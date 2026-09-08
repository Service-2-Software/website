#!/usr/bin/env python3
"""Probe ActiveCampaign connectivity without printing secrets.

Exit codes:
  0  /api/3 authenticated and returned JSON
  1  missing ACTIVECAMPAIGN_API_URL or ACTIVECAMPAIGN_API_KEY
  2  Cloudflare / edge block (empty 403 on /api/3, including a fake path)
  3  API reachable but auth failed (401/403 with an AC JSON body)
  4  unexpected network or HTTP error
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

PUBLIC_HOST = "https://service2software.activehosted.com"
API_PATHS = ("/api/3/users/me", "/api/3/zzz-does-not-exist")
PUBLIC_PATHS = ("/proc.php", "/f/11", "/admin/")


def _request(url: str, token: str | None = None, timeout: int = 15) -> tuple[int, int, str, str, bytes]:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json, text/html;q=0.8")
    req.add_header("User-Agent", "s2s-ac-connect-check/1.0")
    if token:
        req.add_header("Api-Token", token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return (
                resp.status,
                len(body),
                resp.headers.get("server") or "",
                resp.headers.get("content-type") or "",
                body,
            )
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b""
        return (
            exc.code,
            len(body),
            exc.headers.get("server") or "",
            exc.headers.get("content-type") or "",
            body,
        )


def _egress_ip() -> str:
    try:
        status, _n, _s, _c, body = _request("https://api.ipify.org")
        if status == 200:
            return body.decode("utf-8", "replace")
        return f"unavailable (HTTP {status})"
    except Exception as exc:  # noqa: BLE001 — diagnostic only
        return f"unavailable ({type(exc).__name__})"


def main() -> int:
    raw_url = (os.environ.get("ACTIVECAMPAIGN_API_URL") or "").rstrip("/")
    key = os.environ.get("ACTIVECAMPAIGN_API_KEY") or ""

    print("ActiveCampaign connection check")
    print(f"egress_ip={_egress_ip()}")
    print(f"api_url_set={bool(raw_url)} api_key_set={bool(key)} api_key_len={len(key)}")
    if raw_url:
        host = urlparse(raw_url).netloc or "invalid"
        print(f"api_host={host}")

    if not raw_url or not key:
        print("RESULT missing_secrets")
        print("Set ACTIVECAMPAIGN_API_URL and ACTIVECAMPAIGN_API_KEY, then re-run.")
        return 1

    api_results = []
    for path in API_PATHS:
        status, nbytes, server, ctype, body = _request(raw_url + path, token=key)
        snippet = ""
        if body and nbytes < 240:
            snippet = body.decode("utf-8", "replace").replace("\n", " ")
        elif body:
            try:
                parsed = json.loads(body)
                snippet = "json_keys=" + ",".join(list(parsed)[:6])
            except json.JSONDecodeError:
                snippet = "non_json"
        print(f"API {path} status={status} bytes={nbytes} server={server} ctype={ctype} {snippet}")
        api_results.append((path, status, nbytes, server, body))

    for path in PUBLIC_PATHS:
        status, nbytes, server, ctype, _body = _request(PUBLIC_HOST + path)
        print(f"PUB {path} status={status} bytes={nbytes} server={server} ctype={ctype}")

    me_status, me_bytes, me_server, _ctype, me_body = api_results[0][1], api_results[0][2], api_results[0][3], None, api_results[0][4]
    fake_status, fake_bytes = api_results[1][1], api_results[1][2]

    if me_status == 200 and me_bytes > 0:
        print("RESULT ok — /api/3 accepted the key")
        return 0

    edge_block = (
        me_status == 403
        and me_bytes == 0
        and fake_status == 403
        and fake_bytes == 0
        and "cloudflare" in me_server.lower()
    )
    if edge_block:
        print("RESULT waf_blocked")
        print(
            "Cloudflare is rejecting /api/3 before ActiveCampaign sees the key. "
            "A nonexistent path also returns empty 403. Public form hosts still work. "
            "See docs/ACTIVECAMPAIGN_CONNECTION.md."
        )
        return 2

    if me_status in (401, 403) and me_bytes > 0:
        print("RESULT auth_failed — API reached ActiveCampaign but rejected the key")
        return 3

    print(f"RESULT unexpected status={me_status} bytes={me_bytes}")
    return 4


if __name__ == "__main__":
    sys.exit(main())
