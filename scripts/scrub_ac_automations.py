#!/usr/bin/env python3
"""
Scrub the S2S ActiveCampaign setup: journeys, campaigns, forms, and assets.

Runs in three tiers and never stops at the first blocker, because the tier that
usually fails (authenticated API) is not the tier that finds most defects:

  offline  repo contract   — journey map vs manifest vs provision state vs templates
  public   unauthenticated — live AC form field declarations, asset and link health
  live     authenticated   — automation status, Send-step mapping, tag inventory

The public tier matters most in practice: ActiveCampaign silently discards any
`field[N]` posted to a form that does not declare that field, so comparing what
the website posts against what each live form embed declares catches broken
journeys that look fine everywhere else.

    python3 scripts/scrub_ac_automations.py [--json report.json]

Exit code is non-zero when any ERROR-severity finding is present.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field as dc_field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "emails" / "templates"
MANIFEST_PATH = TEMPLATES / "manifest.json"
STATE_PATH = ROOT / "emails" / "ac-provision-state.json"
JOURNEY_PATH = ROOT / "emails" / "journey-map.json"
SITE_PATH = ROOT / "index.html"

WORDMARK = "94ef5e12-7838-4f52-9808-7f50811e72eb.png"
AC_PUBLIC = "https://service2software.activehosted.com"

EXPECTED_SENDERS = {
    "candidate": "recruiting@service2software.org",
    "newsletter": "dave@service2software.org",
    "partner": "david@service2software.org",
}

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"


@dataclass
class Report:
    findings: list[dict] = dc_field(default_factory=list)
    facts: dict = dc_field(default_factory=dict)

    def add(self, severity: str, area: str, message: str) -> None:
        self.findings.append({"severity": severity, "area": area, "message": message})

    def errors(self) -> list[dict]:
        return [f for f in self.findings if f["severity"] == ERROR]


def http(url: str, method: str = "GET", timeout: int = 25, token: str | None = None):
    headers = {"User-Agent": "S2S-AC-Scrub/2.0", "Accept": "*/*"}
    if token:
        headers["Api-Token"] = token
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # noqa: BLE001 - network shape varies; the caller only needs a code
        return 0, str(e).encode()


# --------------------------------------------------------------------------
# offline tier
# --------------------------------------------------------------------------


def load() -> tuple[list[dict], dict, dict, str]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    journey = json.loads(JOURNEY_PATH.read_text(encoding="utf-8"))
    site = SITE_PATH.read_text(encoding="utf-8", errors="replace")
    return manifest, state, journey, site


def template_key(entry: dict) -> str:
    return entry.get("template") or entry["tag"]


def check_provision_state(rep: Report, manifest: list[dict], state: dict) -> None:
    keys = {m["key"] for m in manifest}
    messages, campaigns = set(state["messages"]), set(state["campaigns"])

    for missing in sorted(keys - messages):
        rep.add(ERROR, "state", f"{missing} has no provisioned AC message")
    for missing in sorted(keys - campaigns):
        rep.add(ERROR, "state", f"{missing} has no provisioned AC campaign")

    retired = set(state.get("retired") or {})
    for orphan in sorted((messages | campaigns) - keys - retired):
        rep.add(
            WARN,
            "state",
            f"{orphan} is provisioned in AC but no longer in the manifest — "
            "archive it or add it to the retired block",
        )
    for name, meta in (state.get("retired") or {}).items():
        rep.add(
            INFO,
            "state",
            f"retired {name}: AC message {meta.get('message')} / campaign "
            f"{meta.get('campaign')} still exist — {meta.get('action')}",
        )


def check_manifest_uniqueness(rep: Report, manifest: list[dict]) -> None:
    for label, attr in (("subject", "subject"), ("campaign name", "name")):
        seen: dict[str, str] = {}
        for entry in manifest:
            value = entry[attr]
            if value in seen:
                rep.add(
                    ERROR,
                    "templates",
                    f"duplicate {label} {value!r} on {seen[value]} and {entry['key']}",
                )
            seen[value] = entry["key"]

    bodies: dict[str, str] = {}
    for entry in manifest:
        body = (TEMPLATES / entry["file"]).read_text(encoding="utf-8")
        if body in bodies:
            rep.add(
                ERROR,
                "templates",
                f"{entry['key']} is byte-identical to {bodies[body]} — "
                "two campaigns sending the same email",
            )
        bodies[body] = entry["key"]


REQUIRED_JOURNEY_SECTIONS = (
    "fields",
    "forms",
    "candidate_journeys",
    "partner_journeys",
    "newsletter",
    "sms",
    "calendly",
    "bucket_tags",
    "post_call",
)


def check_contract_shape(rep: Report, journey: dict) -> bool:
    missing = [s for s in REQUIRED_JOURNEY_SECTIONS if s not in journey]
    for section in missing:
        rep.add(
            ERROR,
            "journey-map",
            f"journey-map.json has no {section!r} section — that part of the setup "
            "cannot be verified automatically",
        )
    return not missing


def check_journey_wiring(rep: Report, manifest: list[dict], state: dict, journey: dict) -> None:
    by_key = {m["key"]: m for m in manifest}
    branches = [
        *journey["candidate_journeys"].items(),
        *journey["partner_journeys"].items(),
        ("post_call", {**journey["post_call"], "tag": journey["post_call"]["tag"]}),
        (
            "newsletter_welcome",
            {**journey["newsletter"]["welcome"], "tag": journey["newsletter"]["optin_tag"]},
        ),
    ]

    for jid, branch in branches:
        key = template_key(branch)
        entry = by_key.get(key)
        if not entry:
            rep.add(ERROR, "journeys", f"branch {jid} → template {key} does not exist")
            continue
        if branch.get("campaign") and branch["campaign"] != entry["name"]:
            rep.add(
                ERROR,
                "journeys",
                f"branch {jid} campaign name {branch['campaign']!r} does not match "
                f"manifest {entry['name']!r}",
            )
        if not branch.get("campaign"):
            rep.add(
                ERROR,
                "journeys",
                f"branch {jid} has no campaign — the Send step cannot be verified",
            )
        if key not in state["campaigns"]:
            rep.add(ERROR, "journeys", f"branch {jid} → {key} is not provisioned in AC")

    covered = {template_key(b) for _, b in branches}
    for entry in manifest:
        if entry["key"] not in covered and entry.get("tag"):
            rep.add(
                WARN,
                "journeys",
                f"{entry['key']} is tag-triggered but no journey-map branch references it",
            )


def check_branch_coverage(rep: Report, journey: dict, site: str) -> None:
    def options(field_id: str) -> list[str]:
        match = re.search(
            r'<select[^>]*name="field\[' + field_id + r'\]"[^>]*>(.*?)</select>', site, re.S
        )
        if not match:
            return []
        return [o for o in re.findall(r'<option[^>]*value="([^"]*)"', match.group(1)) if o]

    ets_options = options("32")
    role_options = options("34")
    rep.facts["site_ets_options"] = ets_options
    rep.facts["site_role_options"] = role_options

    for answer in ets_options:
        for booked in (True, False):
            hit = [
                b
                for b in journey["candidate_journeys"].values()
                if answer in b["ets"] and b["booked"] in (booked, None)
            ]
            if not hit:
                state = "booked" if booked else "no book"
                rep.add(ERROR, "coverage", f"ETS {answer!r} ({state}) has no candidate branch")

    for role in role_options:
        for booked in (True, False):
            hit = [
                b
                for b in journey["partner_journeys"].values()
                if role in b["roles"] and b["booked"] is booked
            ]
            if not hit:
                state = "booked" if booked else "no book"
                rep.add(ERROR, "coverage", f"role {role!r} ({state}) has no partner branch")

    buckets = journey["bucket_tags"]
    for answer in ets_options:
        if answer not in buckets["candidate_ets"]:
            rep.add(WARN, "coverage", f"ETS {answer!r} has no bucket tag")
    for role in role_options:
        if role not in buckets["partner_roles"]:
            rep.add(WARN, "coverage", f"role {role!r} has no bucket tag")


def check_templates(rep: Report, manifest: list[dict]) -> None:
    for entry in manifest:
        path = TEMPLATES / entry["file"]
        if not path.exists():
            rep.add(ERROR, "templates", f"{entry['key']} template file missing: {entry['file']}")
            continue
        html = path.read_text(encoding="utf-8")
        header = html[:3000]
        if WORDMARK not in html:
            rep.add(ERROR, "wordmark", f"{entry['key']} has no PNG wordmark")
        elif WORDMARK not in header:
            rep.add(WARN, "wordmark", f"{entry['key']} has the wordmark but not in the header")
        if not re.search(r"<img[^>]+" + re.escape(WORDMARK), html):
            rep.add(ERROR, "wordmark", f"{entry['key']} references the wordmark outside an <img>")
        if 'alt="SERVICE 2 SOFTWARE"' not in html:
            rep.add(WARN, "wordmark", f"{entry['key']} wordmark has no alt text")
        if "%UNSUBSCRIBELINK%" not in html:
            rep.add(ERROR, "templates", f"{entry['key']} has no unsubscribe link")

        expected = EXPECTED_SENDERS.get(entry["journey"])
        if expected and entry["fromemail"] != expected:
            rep.add(
                WARN,
                "senders",
                f"{entry['key']} sends from {entry['fromemail']} "
                f"(expected {expected} for {entry['journey']})",
            )


def check_templates_match_generators(rep: Report) -> None:
    """Templates are generated; drift means the committed HTML is stale."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["cp", "-r", str(TEMPLATES), tmp], check=True, capture_output=True
        )
        result = subprocess.run(
            [sys.executable, "build_templates.py"],
            cwd=ROOT / "emails",
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            rep.add(ERROR, "templates", f"build_templates.py failed: {result.stderr[-300:]}")
            return
        diff = subprocess.run(
            ["diff", "-rq", f"{tmp}/templates", str(TEMPLATES)],
            capture_output=True,
            text=True,
        )
        if diff.stdout.strip():
            rep.add(
                ERROR,
                "templates",
                "committed templates differ from generators: "
                + "; ".join(diff.stdout.strip().splitlines()),
            )


def check_site_wiring(rep: Report, journey: dict, site: str) -> dict:
    posted: dict[str, set[str]] = {}
    for block in re.finditer(r"<form[^>]*>(.*?)</form>", site, re.S):
        body = block.group(1)
        form_id = re.search(r'name="f" value="(\d+)"', body)
        if not form_id:
            continue
        posted.setdefault(form_id.group(1), set()).update(
            re.findall(r'name="field\[(\d+)\]', body)
        )

    for form_id, spec in journey["forms"].items():
        actual = posted.get(form_id)
        if actual is None:
            rep.add(ERROR, "site", f"no site form posts to AC form {form_id} ({spec['name']})")
            continue
        expected = set(spec["posted_by_site"])
        if actual != expected:
            rep.add(
                ERROR,
                "site",
                f"site form {form_id} posts {sorted(actual)} but journey map declares "
                f"{sorted(expected)}",
            )

    known_tags = {b["tag"] for b in journey["candidate_journeys"].values()} | {
        b["tag"] for b in journey["partner_journeys"].values()
    }
    for tag in set(re.findall(r"'((?:cand|partner)-journey-[a-z0-9-]+)'", site)):
        if tag not in known_tags:
            rep.add(ERROR, "site", f"site assigns unknown journey segment {tag!r}")

    rep.facts["site_posted_fields"] = {k: sorted(v) for k, v in posted.items()}
    return {k: sorted(v) for k, v in posted.items()}


# --------------------------------------------------------------------------
# public tier
# --------------------------------------------------------------------------


def check_live_forms(rep: Report, journey: dict, posted: dict) -> None:
    """The check that catches silently-dropped journey fields.

    ActiveCampaign discards `field[N]` values posted to a form that does not
    declare field N, so anything the site posts must appear in the form embed.
    """
    for form_id, spec in journey["forms"].items():
        code, body = http(f"{AC_PUBLIC}/f/{form_id}")
        if code != 200:
            rep.add(ERROR, "ac-forms", f"form {form_id} embed unreachable: HTTP {code}")
            continue
        html = body.decode("utf-8", "replace")
        declared = set(re.findall(r'name="field\[(\d+)\]', html))
        rep.facts.setdefault("ac_form_declared_fields", {})[form_id] = sorted(declared, key=int)

        dropped = [f for f in posted.get(form_id, []) if f not in declared]
        if dropped:
            names = {v: k for k, v in journey["fields"].items()}
            pretty = ", ".join(f"field[{f}] {names.get(f, '?')}" for f in dropped)
            rep.add(
                ERROR,
                "ac-forms",
                f"AC form {form_id} ({spec['name']}) does not declare {pretty} — "
                "the website posts these and ActiveCampaign drops them",
            )


def check_public_assets(rep: Report, journey: dict, manifest: list[dict]) -> None:
    urls = {f"{AC_PUBLIC}/content/pkjoam/2026/07/27/{WORDMARK}"}
    for side in journey["calendly"].values():
        urls.add(side["url"])
    for entry in manifest:
        html = (TEMPLATES / entry["file"]).read_text(encoding="utf-8")
        for href in re.findall(r'href="(https?://[^"%]+)"', html):
            urls.add(href.rstrip("/"))

    for url in sorted(urls):
        code, _ = http(url)
        if code not in (200, 301, 302, 403):
            rep.add(WARN, "links", f"{url} → HTTP {code}")
        elif code == 403:
            rep.add(INFO, "links", f"{url} → HTTP 403 (bot protection, likely fine in mail)")
    rep.facts["checked_urls"] = len(urls)


# --------------------------------------------------------------------------
# live tier
# --------------------------------------------------------------------------


def probe_api(rep: Report, base: str, token: str) -> bool:
    """Tell an auth failure apart from an edge block before reporting a blocker."""
    real, _ = http(f"{base}/api/3/users/me", token=token)
    if real == 200:
        return True

    bogus_path, _ = http(f"{base}/api/3/zzz-does-not-exist", token=token)
    no_token, _ = http(f"{base}/api/3/users/me")
    public, _ = http(f"{AC_PUBLIC}/proc.php")
    rep.facts["api_probe"] = {
        "authenticated": real,
        "nonexistent_path": bogus_path,
        "unauthenticated": no_token,
        "public_proc_php": public,
    }

    if real == 403 and bogus_path == 403:
        rep.add(
            ERROR,
            "api",
            "ActiveCampaign API is blocked at the edge, not rejecting the key: a "
            f"nonexistent path returns {bogus_path} instead of 404, so requests never "
            "reach the application. Public endpoints from the same host still work "
            f"(proc.php → {public}). Automation, tag, and enrollment checks are skipped.",
        )
    else:
        rep.add(ERROR, "api", f"ActiveCampaign API unavailable: HTTP {real}")
    return False


def api_get(base: str, token: str, path: str, params: dict | None = None):
    url = f"{base}/api/3/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    code, body = http(url, token=token)
    if code != 200:
        return code, {}
    try:
        return code, json.loads(body.decode())
    except json.JSONDecodeError:
        return code, {}


def check_live(rep: Report, base: str, token: str, manifest: list[dict], state: dict, journey: dict) -> None:
    code, data = api_get(base, token, "automations", {"limit": 100})
    automations = data.get("automations", [])
    rep.facts["automations"] = [
        {"id": a.get("id"), "name": a.get("name"), "status": a.get("status"), "entered": a.get("entered")}
        for a in automations
    ]
    for auto in automations:
        if str(auto.get("status")) != "1":
            rep.add(WARN, "automations", f"automation {auto.get('name')!r} is not active")
        elif not int(auto.get("entered") or 0):
            rep.add(
                WARN,
                "automations",
                f"automation {auto.get('name')!r} is active but nobody has ever entered it",
            )

    for entry in manifest:
        mid = state["messages"].get(entry["key"])
        code, data = api_get(base, token, f"messages/{mid}")
        if code != 200:
            rep.add(ERROR, "messages", f"{entry['key']} message {mid} unreadable: {code}")
            continue
        html = (data.get("message") or {}).get("html") or ""
        if WORDMARK not in html:
            rep.add(ERROR, "wordmark", f"live AC message {mid} ({entry['key']}) has no PNG wordmark")

    needed = {b["tag"] for b in journey["candidate_journeys"].values()}
    needed |= {b["tag"] for b in journey["partner_journeys"].values()}
    needed |= {journey["post_call"]["tag"], journey["newsletter"]["optin_tag"], journey["sms"]["optin_tag"]}
    needed |= {side["tag"] for side in journey["calendly"].values()}
    for side in journey["calendly"].values():
        needed |= set(side["adds_tags"])
    needed |= set(journey["bucket_tags"]["candidate_ets"].values())
    needed |= set(journey["bucket_tags"]["partner_roles"].values())

    code, data = api_get(base, token, "tags", {"limit": 200})
    have = {t.get("tag") for t in data.get("tags", [])}
    for tag in sorted(needed - have):
        rep.add(ERROR, "tags", f"tag {tag!r} does not exist in ActiveCampaign")


# --------------------------------------------------------------------------


def main() -> int:
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="", help="write the full report here")
    ap.add_argument("--skip-links", action="store_true")
    args = ap.parse_args()

    rep = Report()
    manifest, state, journey, site = load()
    rep.facts["templates"] = len(manifest)

    check_provision_state(rep, manifest, state)
    check_manifest_uniqueness(rep, manifest)
    check_templates(rep, manifest)
    check_templates_match_generators(rep)

    if check_contract_shape(rep, journey):
        check_journey_wiring(rep, manifest, state, journey)
        check_branch_coverage(rep, journey, site)
        posted = check_site_wiring(rep, journey, site)
        check_live_forms(rep, journey, posted)
        if not args.skip_links:
            check_public_assets(rep, journey, manifest)

    base = (os.environ.get("ACTIVECAMPAIGN_API_URL") or "").strip().rstrip("/")
    token = (os.environ.get("ACTIVECAMPAIGN_API_KEY") or "").strip()
    if not base or not token:
        rep.add(ERROR, "api", "ACTIVECAMPAIGN_API_URL / ACTIVECAMPAIGN_API_KEY are not set")
    elif probe_api(rep, base, token):
        check_live(rep, base, token, manifest, state, journey)

    order = {ERROR: 0, WARN: 1, INFO: 2}
    for finding in sorted(rep.findings, key=lambda f: (order[f["severity"]], f["area"])):
        print(f"{finding['severity']:5} [{finding['area']}] {finding['message']}")

    counts = {s: sum(1 for f in rep.findings if f["severity"] == s) for s in (ERROR, WARN, INFO)}
    print(f"\n{counts[ERROR]} errors, {counts[WARN]} warnings, {counts[INFO]} notes")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"findings": rep.findings, "facts": rep.facts}, indent=2), encoding="utf-8"
        )
        print(f"wrote {args.json}")

    return 1 if rep.errors() else 0


if __name__ == "__main__":
    raise SystemExit(main())
