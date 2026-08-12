"""Minimal mail.tm client used to receive real journey emails during live tests.

ActiveCampaign's authenticated API is unreachable from CI/cloud egress, so the
only way to prove an automation actually fired is to catch the email it sends.
"""

from __future__ import annotations

import json
import secrets
import time
import urllib.error
import urllib.request

API = "https://api.mail.tm"


def _req(method: str, path: str, data=None, token: str | None = None, timeout: int = 30):
    headers = {"Accept": "application/json"}
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]


def _members(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get("hydra:member") or []
    return []


def domain() -> str:
    code, data = _req("GET", "/domains")
    members = _members(data)
    if code != 200 or not members:
        raise RuntimeError(f"mail.tm domains failed: {code} {data}")
    return members[0]["domain"]


class Inbox:
    def __init__(self, label: str, dom: str | None = None):
        self.label = label
        dom = dom or domain()
        self.address = f"s2s-{label}-{secrets.token_hex(3)}@{dom}"
        self.password = secrets.token_urlsafe(18)
        code, data = _req("POST", "/accounts", {"address": self.address, "password": self.password})
        if code not in (200, 201):
            raise RuntimeError(f"mail.tm account create failed: {code} {data}")
        # Token issuance occasionally lags account creation by a beat.
        for attempt in range(6):
            code, data = _req("POST", "/token", {"address": self.address, "password": self.password})
            if code == 200 and isinstance(data, dict) and data.get("token"):
                self.token = data["token"]
                break
            time.sleep(1 + attempt)
        else:
            raise RuntimeError(f"mail.tm token failed: {code} {data}")

    def messages(self) -> list[dict]:
        code, data = _req("GET", "/messages", token=self.token)
        return _members(data) if code == 200 else []

    def message(self, mid: str) -> dict:
        code, data = _req("GET", f"/messages/{mid}", token=self.token)
        return data if code == 200 else {}

    def to_dict(self) -> dict:
        return {"label": self.label, "address": self.address}
