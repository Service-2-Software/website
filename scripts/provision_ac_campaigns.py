#!/usr/bin/env python3
"""
Provision ActiveCampaign messages, campaigns, lists, and form routing.

Requires:
  ACTIVECAMPAIGN_API_URL  (e.g. https://service2software.api-us1.com)
  ACTIVECAMPAIGN_API_KEY

Idempotent where possible: reuses lists/tags/messages named with the S2S · prefix.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "emails" / "templates" / "manifest.json"
STATE_PATH = ROOT / "emails" / "ac-provision-state.json"

LISTS = {
    "master-contact-list": {"name": "Master Contact List", "id": None},
    "home-page-group": {"name": "Home Page Group", "id": None},
    "website-candidates": {
        "name": "Website Candidates",
        "stringid": "website-candidates",
        "reminder": "You applied via service2software.org",
    },
    "website-partners": {
        "name": "Website Partners",
        "stringid": "website-partners",
        "reminder": "You requested hiring info via service2software.org",
    },
}

# AC form API accepts a single subscribe-to-list action reliably (multi-list → 500).
# Automations should also add Candidates/Partners to Master Contact List (3).
FORM_ROUTING = {
    "11": {
        "name": "Military Application",
        "lists": ["website-candidates"],
        "submit": "show-thank-you",
    },
    "16": {
        "name": "Partner Inquiry",
        "lists": ["website-partners"],
        "submit": "show-thank-you",
    },
    "13": {
        "name": "Home Page Group",
        "lists": ["home-page-group"],
        "submit": "show-thank-you",
    },
}


def env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v.rstrip("/")


BASE = None
KEY = None


def v3(method: str, path: str, data=None, params=None):
    url = f"{BASE}/api/3/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body = None
    headers = {"Api-Token": KEY, "Accept": "application/json"}
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:1000]


def v1(action: str, post: dict):
    params = {"api_key": KEY, "api_action": action, "api_output": "json"}
    url = f"{BASE}/admin/api.php?" + urllib.parse.urlencode(params)
    body = urllib.parse.urlencode(post, doseq=True).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode())


def ensure_lists(state: dict) -> dict:
    code, data = v3("GET", "lists", params={"limit": 100})
    if code != 200:
        raise SystemExit(f"list fetch failed: {code} {data}")
    by_name = {x["name"]: x for x in data.get("lists", [])}
    by_sid = {x.get("stringid"): x for x in data.get("lists", [])}
    resolved = {}
    for key, spec in LISTS.items():
        existing = by_name.get(spec["name"]) or by_sid.get(spec.get("stringid"))
        if existing:
            resolved[key] = existing["id"]
            print(f"list ok {key} -> {existing['id']}")
            continue
        if key in ("master-contact-list", "home-page-group"):
            raise SystemExit(f"Expected list missing: {spec['name']}")
        code, created = v3(
            "POST",
            "lists",
            {
                "list": {
                    "name": spec["name"],
                    "stringid": spec["stringid"],
                    "sender_url": "https://service2software.org",
                    "sender_reminder": spec["reminder"],
                }
            },
        )
        if code not in (200, 201):
            raise SystemExit(f"create list {key}: {code} {created}")
        resolved[key] = created["list"]["id"]
        print(f"list created {key} -> {resolved[key]}")
    state["lists"] = resolved
    return resolved


def resolve_list_id(lists: dict, token: str) -> str:
    if token.isdigit():
        return token
    return lists[token]


def update_forms(lists: dict) -> None:
    for fid, spec in FORM_ROUTING.items():
        code, data = v3("GET", f"forms/{fid}")
        if code != 200:
            raise SystemExit(f"form {fid} fetch failed: {code} {data}")
        form = data["form"]
        actions = []
        for token in spec["lists"]:
            lid = resolve_list_id(lists, token)
            code, ldata = v3("GET", f"lists/{lid}")
            lname = ldata.get("list", {}).get("name", lid) if code == 200 else lid
            # Reuse existing action id when possible (AC is picky about form updates).
            existing = (form.get("actiondata") or {}).get("actions") or []
            action_id = existing[0]["id"] if existing else str(uuid.uuid4())
            actions.append(
                {
                    "title": "Subscribe to a list",
                    "type": "subscribe-to-list",
                    "id": action_id,
                    "listName": lname,
                    "list": str(lid),
                }
            )
        keep = {
            k: form[k]
            for k in form
            if k
            not in (
                "links",
                "id",
                "cdate",
                "udate",
                "userid",
                "entries",
                "aid",
                "addressid",
                "parentformid",
                "source",
            )
        }
        keep["name"] = spec["name"]
        keep["submit"] = spec["submit"]
        keep["layout"] = form.get("layout") or "inline-form"
        keep["actiondata"] = {"actions": actions}
        code, out = v3("PUT", f"forms/{fid}", {"form": keep})
        if code != 200:
            raise SystemExit(f"form {fid} update failed: {code} {out}")
        print(f"form {fid} lists -> {[a['list'] for a in actions]}")


def find_message_by_subject(subject: str):
    code, data = v3("GET", "messages", params={"limit": 100})
    if code != 200:
        return None
    for m in data.get("messages", []):
        if m.get("subject") == subject and m.get("fromemail"):
            return m
    return None


def upsert_messages_and_campaigns(lists: dict, state: dict) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    state.setdefault("messages", {})
    state.setdefault("campaigns", {})

    for item in manifest:
        html = (ROOT / "emails" / "templates" / item["file"]).read_text(encoding="utf-8")
        text = (
            f"{item['subject']}\n\n"
            "Service 2 Software — Veteran Talent · SkillBridge Careers\n"
            "https://service2software.org\n"
        )
        existing_id = state["messages"].get(item["key"])
        msg_payload = {
            "message": {
                "fromname": item["fromname"],
                "fromemail": item["fromemail"],
                "reply2": item["reply2"],
                "subject": item["subject"],
                "html": html,
                "text": text,
            }
        }
        if existing_id:
            code, out = v3("PUT", f"messages/{existing_id}", msg_payload)
            if code == 200:
                mid = existing_id
                print(f"message updated {item['key']} -> {mid}")
            else:
                print(f"message update failed {item['key']}: {code}; recreating")
                existing_id = None
        if not existing_id:
            # try match by subject
            found = find_message_by_subject(item["subject"])
            if found:
                mid = found["id"]
                code, out = v3("PUT", f"messages/{mid}", msg_payload)
                print(f"message matched/updated {item['key']} -> {mid} ({code})")
            else:
                code, out = v3("POST", "messages", msg_payload)
                if code not in (200, 201):
                    raise SystemExit(f"message create {item['key']}: {code} {out}")
                mid = out["message"]["id"]
                print(f"message created {item['key']} -> {mid}")
        state["messages"][item["key"]] = str(mid)

        # Campaign via v1 (draft)
        if item["key"] in state["campaigns"]:
            print(f"campaign exists {item['key']} -> {state['campaigns'][item['key']]}")
            continue
        list_id = resolve_list_id(lists, item["list"])
        camp = v1(
            "campaign_create",
            {
                "type": "single",
                "name": item["name"],
                "sdate": "2030-01-01 12:00:00",  # placeholder; automations own send time
                "status": 0,  # draft
                "public": 1,
                "tracklinks": "all",
                "trackreads": 1,
                "htmlunsub": 1,
                f"p[{list_id}]": list_id,
                f"m[{mid}]": 100,
            },
        )
        if not camp.get("result_code"):
            raise SystemExit(f"campaign_create {item['key']}: {camp}")
        cid = str(camp["id"])
        state["campaigns"][item["key"]] = cid
        print(f"campaign created {item['key']} -> {cid}")


def add_website_source_to_forms() -> None:
    """Ensure forms include WEBSITE_SOURCE field (id 36) in cfields when possible."""
    for fid in ("11", "16", "13"):
        code, data = v3("GET", f"forms/{fid}")
        if code != 200:
            print(f"skip cfields form {fid}: {code}")
            continue
        form = data["form"]
        cfields = form.get("cfields") or []
        if isinstance(cfields, str):
            try:
                cfields = json.loads(cfields)
            except json.JSONDecodeError:
                cfields = []
        ids = {str(x.get("id")) for x in cfields if isinstance(x, dict)}
        if "36" in ids:
            print(f"form {fid} already has WEBSITE_SOURCE")
            continue
        cfields.append(
            {
                "type": "hidden",
                "header": "Website Source",
                "id": "36",
                "required": False,
                "default_value": "",
            }
        )
        payload = {
            "form": {
                "name": form.get("name"),
                "submit": form.get("submit") or "show-thank-you",
                "layout": form.get("layout") or "inline-form",
                "actiondata": form.get("actiondata") or {},
                "cfields": cfields,
            }
        }
        code, out = v3("PUT", f"forms/{fid}", payload)
        # Optional — website already posts field[36]; AC may reject cfields mutation.
        print(f"form {fid} cfields update -> {code} (site posts field[36] regardless)")


def main() -> None:
    global BASE, KEY
    BASE = env("ACTIVECAMPAIGN_API_URL")
    KEY = env("ACTIVECAMPAIGN_API_KEY")

    if not MANIFEST.exists():
        raise SystemExit("Run emails/build_templates.py first")

    state = {}
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    lists = ensure_lists(state)
    update_forms(lists)
    add_website_source_to_forms()
    upsert_messages_and_campaigns(lists, state)

    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print("wrote", STATE_PATH)
    print("DONE — finish automation wiring in AC UI (see docs/EMAIL_CAMPAIGNS.md)")


if __name__ == "__main__":
    main()
