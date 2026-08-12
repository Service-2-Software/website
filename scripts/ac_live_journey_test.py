#!/usr/bin/env python3
"""
Drive real leads through the live ActiveCampaign journeys and catch the emails.

The authenticated AC API is unreachable from cloud/CI egress (see
docs/EMAIL_FLOW_SCRUB.md), so automation enrollment cannot be read back over
`/api/3`. This script proves the journeys from the outside instead: it posts the
exact payload the website posts to `proc.php`, then watches a disposable inbox
per scenario and reports which campaign actually arrived.

Every recipient is a real, deliverable mailbox, so this does not generate bounces.
The SMS-consent cases use the reserved +1-555-01xx fictional range so no real
handset can be texted.

    python3 scripts/ac_live_journey_test.py --wait 900
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mailtm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "emails" / "templates" / "manifest.json"
PROC = "https://service2software.activehosted.com/proc.php"
WORDMARK = "94ef5e12-7838-4f52-9808-7f50811e72eb.png"

# Reserved fictional range (NANP 555-01xx) — unroutable, cannot reach a person.
TEST_PHONE = "+15555550199"

BASE_11 = {"u": "11", "f": "11", "s": "", "c": "0", "m": "0", "act": "sub", "v": "2"}
BASE_16 = {"u": "16", "f": "16", "s": "", "c": "0", "m": "0", "act": "sub", "v": "2"}
BASE_13 = {"u": "13", "f": "13", "s": "", "c": "0", "m": "0", "act": "sub", "v": "2"}

SCENARIOS = [
    {
        "label": "cand-6-12",
        "form": "11",
        "base": BASE_11,
        "fullname": "Scrub Candidate SixTwelve",
        "phone": TEST_PHONE,
        "fields": {
            "5": "US Army",
            "32": "6-12 months",
            "36": "scrub-candidate",
            "37": "Yes",
            "38": "Yes",
            "39": "cand-journey-6-12-nobook",
        },
        # Newsletter opt-in is the observable probe for whether form 11 keeps field[37].
        "expect": ["cand-journey-6-12-nobook"],
        "may_also": ["newsletter-welcome"],
    },
    {
        "label": "cand-lt3",
        "form": "11",
        "base": BASE_11,
        "fullname": "Scrub Candidate LessThree",
        "fields": {
            "5": "US Navy",
            "32": "Less than 3 months",
            "36": "scrub-candidate",
            "39": "cand-journey-lt3-nobook",
        },
        "expect": ["cand-journey-lt3-nobook"],
    },
    {
        "label": "cand-separated",
        "form": "11",
        "base": BASE_11,
        "fullname": "Scrub Candidate Separated",
        "fields": {
            "5": "US Air Force",
            "32": "Already separated",
            "36": "scrub-candidate",
            "39": "cand-journey-separated-onedone",
        },
        "expect": ["cand-journey-separated-onedone"],
        "forbid": [
            "cand-journey-6-12-nobook",
            "cand-journey-3-6-nobook",
            "cand-journey-lt3-nobook",
            "candidate-book-nudge",
        ],
    },
    {
        "label": "partner-sdr",
        "form": "16",
        "base": BASE_16,
        "fullname": "Scrub Partner SdrAe",
        "phone": TEST_PHONE,
        "fields": {
            "34": "SDR / BDR",
            "35": "S2S Scrub Co",
            "36": "scrub-partner",
            "37": "Yes",
            "38": "Yes",
            "39": "partner-journey-sdr-ae-nobook",
        },
        "expect": ["partner-journey-sdr-ae-nobook"],
        "may_also": ["newsletter-welcome"],
    },
    {
        "label": "partner-cs",
        "form": "16",
        "base": BASE_16,
        "fullname": "Scrub Partner CustomerSuccess",
        "fields": {
            "34": "Customer Success",
            "35": "S2S Scrub Co",
            "36": "scrub-partner",
            "39": "partner-journey-cs-nobook",
        },
        "expect": ["partner-journey-cs-nobook"],
    },
    {
        "label": "newsletter",
        "form": "13",
        "base": BASE_13,
        "fields": {"36": "scrub-newsletter"},
        "expect": ["newsletter-welcome"],
    },
]


def post_form(scenario: dict, email: str) -> tuple[int, str]:
    payload = dict(scenario["base"])
    payload["email"] = email
    if scenario.get("fullname"):
        payload["fullname"] = scenario["fullname"]
    if scenario.get("phone"):
        payload["phone"] = scenario["phone"]
    for fid, value in scenario["fields"].items():
        payload[f"field[{fid}]"] = value
    body = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(
        PROC,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (S2S-journey-test)",
            "Referer": "https://service2software.org/",
        },
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
    try:
        with opener.open(req, timeout=45) as resp:
            return resp.status, resp.geturl()
    except urllib.error.HTTPError as e:
        return e.code, ""


def classify(subject: str, manifest: list[dict]) -> str | None:
    subject = (subject or "").strip()
    # AC resolves %FIRSTNAME%, so compare on the static tail of each subject.
    for entry in manifest:
        tmpl = entry["subject"]
        pattern = "^" + "".join(
            ".*" if part.startswith("%") else re.escape(part)
            for part in re.split(r"(%[A-Z_]+%)", tmpl)
        ) + "$"
        if re.match(pattern, subject, re.I):
            return entry["key"]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait", type=int, default=900, help="seconds to watch inboxes")
    ap.add_argument("--poll", type=int, default=20, help="seconds between polls")
    ap.add_argument("--out", default="/tmp/ac_live_journey_test.json")
    ap.add_argument("--only", default="", help="comma-separated scenario labels")
    ap.add_argument(
        "--dump-dir",
        default="",
        help="save each delivered body here to diff live copy against emails/templates/",
    )
    args = ap.parse_args()
    dump_dir = Path(args.dump_dir) if args.dump_dir else None
    if dump_dir:
        dump_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    wanted = {s.strip() for s in args.only.split(",") if s.strip()}
    scenarios = [s for s in SCENARIOS if not wanted or s["label"] in wanted]

    dom = mailtm.domain()
    print(f"disposable domain: {dom}\n")

    runs = []
    for scenario in scenarios:
        inbox = mailtm.Inbox(scenario["label"], dom)
        status, final = post_form(scenario, inbox.address)
        print(f"POST form {scenario['form']:>2} {scenario['label']:<16} {inbox.address} -> {status}")
        runs.append({"scenario": scenario, "inbox": inbox, "post_status": status, "post_url": final, "received": {}})
        time.sleep(2)

    print(f"\nwatching {len(runs)} inboxes for {args.wait}s ...")
    deadline = time.time() + args.wait
    while time.time() < deadline:
        time.sleep(args.poll)
        new = 0
        for run in runs:
            for msg in run["inbox"].messages():
                mid = msg["id"]
                if mid in run["received"]:
                    continue
                full = run["inbox"].message(mid)
                subject = full.get("subject") or msg.get("subject") or ""
                html = " ".join(full.get("html") or [])
                key = classify(subject, manifest)
                run["received"][mid] = {
                    "subject": subject,
                    "from": (full.get("from") or {}).get("address"),
                    "key": key,
                    "wordmark": WORDMARK in html,
                    "unresolved_tags": sorted(set(re.findall(r"%[A-Z_]+%", html))),
                    "at": time.strftime("%H:%M:%SZ", time.gmtime()),
                }
                if dump_dir:
                    name = f"{run['scenario']['label']}--{key or 'unmapped'}.html"
                    (dump_dir / name).write_text(html, encoding="utf-8")
                    run["received"][mid]["saved_as"] = name
                new += 1
                print(
                    f"  [{run['scenario']['label']}] {key or 'UNMAPPED'} "
                    f"from={run['received'][mid]['from']} wordmark={run['received'][mid]['wordmark']} "
                    f"| {subject}"
                )
        if new == 0:
            remaining = int(deadline - time.time())
            print(f"  ... no new mail ({remaining}s left)", flush=True)

    print("\n=== RESULT ===")
    report, failures = [], []
    for run in runs:
        scenario = run["scenario"]
        got = {v["key"] for v in run["received"].values() if v["key"]}
        unmapped = [v["subject"] for v in run["received"].values() if not v["key"]]
        missing = [k for k in scenario["expect"] if k not in got]
        forbidden = [k for k in scenario.get("forbid", []) if k in got]
        no_wordmark = [v["key"] or v["subject"] for v in run["received"].values() if not v["wordmark"]]
        leftover = sorted({t for v in run["received"].values() for t in v["unresolved_tags"]})

        status = "PASS"
        if missing or forbidden or no_wordmark or leftover:
            status = "FAIL"
            failures.append(scenario["label"])
        elif not run["received"]:
            status = "FAIL"
            failures.append(scenario["label"])

        print(f"{status:5} {scenario['label']:<16} received={sorted(got) or list(unmapped) or 'NOTHING'}")
        if missing:
            print(f"        missing expected: {missing}")
        if forbidden:
            print(f"        WRONG BRANCH sent: {forbidden}")
        if no_wordmark:
            print(f"        missing PNG wordmark: {no_wordmark}")
        if leftover:
            print(f"        unresolved merge tags: {leftover}")
        if unmapped:
            print(f"        unmapped subjects: {unmapped}")

        report.append(
            {
                "label": scenario["label"],
                "form": scenario["form"],
                "address": run["inbox"].address,
                "post_status": run["post_status"],
                "expected": scenario["expect"],
                "received": list(run["received"].values()),
                "status": status,
            }
        )

    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
