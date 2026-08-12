#!/usr/bin/env python3
"""
Scrub ActiveCampaign automations, campaigns, tags, and test enrollment.

Requires:
  ACTIVECAMPAIGN_API_URL
  ACTIVECAMPAIGN_API_KEY

Exits non-zero if API is unreachable or required journeys are missing/miswired.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "emails" / "ac-provision-state.json"
JOURNEY_PATH = ROOT / "emails" / "journey-map.json"
MANIFEST_PATH = ROOT / "emails" / "templates" / "manifest.json"
WORDMARK = "94ef5e12-7838-4f52-9808-7f50811e72eb.png"

EXPECTED_AUTOMATION_HINTS = [
    ("candidate", "applied", "no call"),
    ("candidate", "booked"),
    ("initial call completed",),
    ("partner", "booked"),
    ("inquiry", "no call"),
    ("newsletter",),
    ("sms",),
]

CALENDLY_TAGS = [
    "calendly-integration-S2S_Discovery_Call_w/_Patrick",
    "calendly-integration-S2S_Initial_Call_with_David",
]

POST_CALL_TAG = "cand-initial-call-completed"


def env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v.rstrip("/")


BASE = env("ACTIVECAMPAIGN_API_URL")
KEY = env("ACTIVECAMPAIGN_API_KEY")


def v3(method: str, path: str, data=None, params=None):
    url = f"{BASE}/api/3/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body = None
    headers = {"Api-Token": KEY, "Accept": "application/json", "User-Agent": "S2S-AC-Scrub/1.0"}
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:2000]


def paginate(path: str, key: str, params=None):
    params = dict(params or {})
    params.setdefault("limit", 100)
    offset = 0
    out = []
    while True:
        params["offset"] = offset
        code, data = v3("GET", path, params=params)
        if code != 200:
            raise SystemExit(f"GET {path} failed: {code} {data}")
        batch = data.get(key) or []
        out.extend(batch)
        total = int((data.get("meta") or {}).get("total") or 0)
        offset += len(batch)
        if not batch or (total and offset >= total):
            break
    return out


def check_api() -> None:
    code, data = v3("GET", "users/me")
    if code == 403:
        raise SystemExit(
            "ActiveCampaign API returned Cloudflare/WAF 403. "
            "Public forms may still work; authenticated /api/3 is blocked from this egress. "
            f"URL={BASE}"
        )
    if code != 200:
        raise SystemExit(f"API auth failed: {code} {data}")
    print(f"API OK as user {(data.get('user') or {}).get('email') or data.get('user')}")


def scrub_automations(report: dict) -> None:
    autos = paginate("automations", "automations")
    report["automations"] = [
        {
            "id": a.get("id"),
            "name": a.get("name"),
            "status": a.get("status"),
            "entered": a.get("entered"),
            "completed": a.get("completed"),
        }
        for a in sorted(autos, key=lambda x: int(x.get("id") or 0))
    ]
    print(f"\nAutomations ({len(autos)}):")
    for a in report["automations"]:
        print(f"  [{a['status']}] id={a['id']} entered={a['entered']} {a['name']}")

    # AC Classic API does not expose full automation graphs (If/Else + Send).
    # We can only inventory status/names here and flag missing name hints.
    names_l = " | ".join((a.get("name") or "").lower() for a in autos)
    missing = []
    for hint in EXPECTED_AUTOMATION_HINTS:
        if not all(h in names_l for h in hint):
            missing.append(" + ".join(hint))
    report["missing_automation_name_hints"] = missing
    if missing:
        print("WARN missing automation name hints:", missing)
    else:
        print("All expected automation name hints present (status/canvas still need UI review).")


def scrub_campaigns_and_wordmarks(report: dict) -> None:
    state = json.loads(STATE_PATH.read_text())
    journey = json.loads(JOURNEY_PATH.read_text())
    manifest = {e["key"]: e for e in json.loads(MANIFEST_PATH.read_text())}
    issues = []

    print("\nCampaigns / messages vs journey map:")
    for jid, j in {**journey["candidate_journeys"], **{f"p-{k}": v for k, v in journey["partner_journeys"].items()}}.items():
        tag = j["tag"]
        key = {
            "cand-journey-ineligible-timing": "candidate-ineligible-timing",
        }.get(tag, tag)
        mid = state["messages"].get(key)
        cid = state["campaigns"].get(key)
        if not mid or not cid:
            issues.append(f"missing state ids for {key}")
            continue
        code, msg = v3("GET", f"messages/{mid}")
        if code != 200:
            issues.append(f"message {key} id={mid} fetch {code}")
            continue
        html = (msg.get("message") or {}).get("html") or ""
        has_wm = WORDMARK in html
        print(f"  {'OK' if has_wm else 'NO WM'} {key} message={mid} campaign={cid}")
        if not has_wm:
            issues.append(f"live message missing PNG wordmark: {key} ({mid})")

    pc = journey["post_call"]
    key = pc["template"]
    mid = state["messages"].get(key)
    code, msg = v3("GET", f"messages/{mid}")
    html = ((msg.get("message") or {}).get("html") or "") if code == 200 else ""
    print(f"  post_call message={mid} wordmark={WORDMARK in html}")
    if WORDMARK not in html:
        issues.append(f"post-call message missing wordmark: {mid}")

    # Orphan risk
    if "cand-journey-lt3-booked" in state["campaigns"]:
        issues.append(
            "orphan campaign cand-journey-lt3-booked still provisioned; "
            "booked lt3 should use candidate-ineligible-timing per journey-map"
        )

    report["campaign_issues"] = issues
    for i in issues:
        print("!", i)


def scrub_tags(report: dict) -> None:
    tags = paginate("tags", "tags")
    by_name = {t.get("tag"): t for t in tags}
    needed = set()
    journey = json.loads(JOURNEY_PATH.read_text())
    for j in journey["candidate_journeys"].values():
        needed.add(j["tag"])
    for j in journey["partner_journeys"].values():
        needed.add(j["tag"])
    needed.update(CALENDLY_TAGS)
    needed.add(POST_CALL_TAG)
    needed.update(
        {
            "optin-newsletter",
            "optin-sms",
            "cand-call-booked",
            "partner-call-booked",
            "cand-ets-gt12",
            "cand-ets-6-12",
            "cand-ets-3-6",
            "cand-ets-lt3",
            "cand-ets-separated",
            "partner-roles-sdr-ae",
            "partner-roles-cs",
            "partner-roles-other",
        }
    )
    missing = sorted(n for n in needed if n not in by_name)
    report["missing_tags"] = missing
    print(f"\nTags: {len(tags)} total; missing required: {missing or 'none'}")


def find_contact(email: str):
    code, data = v3("GET", "contacts", params={"email": email})
    if code != 200:
        return None
    contacts = data.get("contacts") or []
    return contacts[0] if contacts else None


def enroll_smoke(report: dict) -> None:
    """Create one candidate + one partner via API and report tags/automations after a short wait."""
    ts = int(time.time())
    results = []
    cases = [
        {
            "email": f"ac-scrub+api-cand-{ts}@example.com",
            "firstName": "ApiCand",
            "lastName": "Scrub",
            "fields": [
                {"field": "32", "value": "6-12 months"},
                {"field": "36", "value": "scrub-api"},
                {"field": "37", "value": "Yes"},
                {"field": "39", "value": "cand-journey-6-12-nobook"},
            ],
            "list": "5",
        },
        {
            "email": f"ac-scrub+api-partner-{ts}@example.com",
            "firstName": "ApiPartner",
            "lastName": "Scrub",
            "phone": "+15555550199",
            "fields": [
                {"field": "34", "value": "SDR / BDR"},
                {"field": "35", "value": "Scrub Co"},
                {"field": "36", "value": "scrub-api"},
                {"field": "38", "value": "Yes"},
                {"field": "39", "value": "partner-journey-sdr-ae-nobook"},
            ],
            "list": "6",
        },
    ]
    for case in cases:
        payload = {
            "contact": {
                "email": case["email"],
                "firstName": case["firstName"],
                "lastName": case["lastName"],
                "phone": case.get("phone", ""),
                "fieldValues": case["fields"],
            }
        }
        code, data = v3("POST", "contact/sync", payload)
        ok = code in (200, 201)
        cid = ((data.get("contact") or {}).get("id")) if isinstance(data, dict) else None
        if ok and cid and case.get("list"):
            v3(
                "POST",
                "contactLists",
                {"contactList": {"list": case["list"], "contact": cid, "status": 1}},
            )
        results.append({"email": case["email"], "http": code, "contact_id": cid, "ok": ok})
        print(f"sync {case['email']} -> {code} id={cid}")

    time.sleep(3)
    for r in results:
        c = find_contact(r["email"])
        if not c:
            r["found"] = False
            continue
        r["found"] = True
        cid = c["id"]
        code, tags = v3("GET", f"contacts/{cid}/contactTags")
        r["tags"] = tags.get("contactTags") if code == 200 else code
        code, autos = v3("GET", "contactAutomations", params={"filters[contact]": cid})
        r["automations"] = autos.get("contactAutomations") if code == 200 else code
        print(f"  contact {cid} tags={r['tags']} automations={r['automations']}")

    report["enrollment"] = results


def main() -> None:
    report = {"base": BASE}
    print("=== AC automation scrub ===")
    check_api()
    scrub_automations(report)
    scrub_campaigns_and_wordmarks(report)
    scrub_tags(report)
    enroll_smoke(report)

    out = Path("/tmp/ac_automation_scrub_report.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nwrote", out)

    hard_fail = bool(report.get("campaign_issues")) or bool(report.get("missing_tags"))
    # Missing automation name hints are warnings — canvases may use different titles.
    if hard_fail:
        raise SystemExit(1)
    print("SCRUB OK (still open canvases in AC UI to confirm If/Else + Send mappings)")


if __name__ == "__main__":
    main()
