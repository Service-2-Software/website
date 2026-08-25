#!/usr/bin/env python3
"""
Mirror of the Salesforce ActiveCampaignInitialCallAction callout.

Sets AC INITIAL_CALL_COMPLETED (field 41) to true for a contact email.
Used to validate the payload without deploying Apex.

    set -a && source .env && set +a
    python3 scripts/sf_ac_set_initial_call_completed.py allie@service2software.org
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

FIELD_ID = "41"
TRUE_VALUE = "true"


def env(name: str) -> str:
    value = (os.environ.get(name) or "").strip()
    if not value:
        raise SystemExit(f"Missing {name}")
    return value.rstrip("/")


def api(method: str, path: str, data=None, params=None):
    base = env("ACTIVECAMPAIGN_API_URL")
    key = env("ACTIVECAMPAIGN_API_KEY")
    url = f"{base}/api/3/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body = None
    headers = {"Api-Token": key, "Accept": "application/json"}
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:500]}") from e


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: sf_ac_set_initial_call_completed.py <email>")
    email = sys.argv[1].strip()

    code, data = api("GET", "contacts", params={"email": email})
    contacts = data.get("contacts") or []
    if not contacts:
        raise SystemExit(f"No ActiveCampaign contact for {email}")
    contact_id = str(contacts[0]["id"])

    code, data = api("GET", f"contacts/{contact_id}/fieldValues")
    existing = next(
        (v for v in data.get("fieldValues", []) if str(v.get("field")) == FIELD_ID),
        None,
    )
    payload = {
        "fieldValue": {
            "contact": contact_id,
            "field": FIELD_ID,
            "value": TRUE_VALUE,
        }
    }
    if existing:
        code, out = api("PUT", f"fieldValues/{existing['id']}", payload)
        action = "updated"
    else:
        code, out = api("POST", "fieldValues", payload)
        action = "created"

    stored = (out.get("fieldValue") or {}).get("value")
    print(
        f"{action} contact={contact_id} field={FIELD_ID} "
        f"http={code} stored={stored!r}"
    )
    print(
        "Next: confirm automation 18 is triggered on field change + guard tag, "
        "then check allie's inbox for Pre-Core."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
