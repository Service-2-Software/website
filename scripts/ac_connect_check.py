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

import http.client
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


class _RecordingHTTPSConnection(http.client.HTTPSConnection):
    """Capture the exact bytes written to the socket for the request head."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_request = b""

    def send(self, data):  # noqa: ANN001 — matches http.client signature
        if isinstance(data, (bytes, bytearray)):
            self.raw_request += bytes(data)
        super().send(data)


def _wire_probe(url: str, headers: dict[str, str], timeout: int = 15) -> dict:
    """GET `url` with exactly `headers` and report what went on the wire.

    Uses http.client directly (no urllib proxy handling, no extra headers
    besides the Host / Accept-Encoding http.client itself adds) so the
    measured request head is byte-accurate.
    """
    parsed = urlparse(url)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    conn = _RecordingHTTPSConnection(parsed.netloc, timeout=timeout)
    try:
        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()
        body = resp.read()
        resp_headers = {k.lower(): v for k, v in resp.getheaders()}
        status = resp.status
    finally:
        raw = conn.raw_request
        conn.close()
    head = raw.split(b"\r\n\r\n", 1)[0]
    lines = head.decode("latin-1").split("\r\n")
    sent_names = [line.split(":", 1)[0] for line in lines[1:] if ":" in line]
    return {
        "request_line": lines[0] if lines else "",
        "sent_header_names": sent_names,
        "sent_head_bytes": len(head) + 4,  # request line + headers + CRLFCRLF
        "status": status,
        "body_bytes": len(body),
        "body": body,
        "resp_headers": resp_headers,
    }


def _print_wire_probe(name: str, url: str, headers: dict[str, str]) -> dict | None:
    lower = {k.lower(): v for k, v in headers.items()}
    auth = lower.get("authorization")
    auth_scheme = auth.split(" ", 1)[0] if auth else None
    try:
        result = _wire_probe(url, headers)
    except Exception as exc:  # noqa: BLE001 — diagnostic only
        print(f"PROBE {name} failed: {type(exc).__name__}: {exc}")
        return None
    rh = result["resp_headers"]
    print(f"PROBE {name} {result['request_line']}")
    print(f"  sent_header_names={','.join(result['sent_header_names'])}")
    print(f"  sent_head_bytes={result['sent_head_bytes']}")
    print(
        f"  api_token_sent={'api-token' in lower} "
        f"authorization_sent={auth is not None} "
        f"authorization_scheme={auth_scheme}"
    )
    print(
        f"  resp status={result['status']} body_bytes={result['body_bytes']} "
        f"server={rh.get('server', '')} ctype={rh.get('content-type', '')} "
        f"cf_ray={rh.get('cf-ray', '')} cf_cache_status={rh.get('cf-cache-status', '')}"
    )
    if result["body"] and result["body_bytes"] < 240:
        print(f"  body_snippet={result['body'].decode('utf-8', 'replace')!r}")
    return result


def _run_header_diagnostics(raw_url: str, key: str) -> None:
    """Measure exactly what this runtime sends, without printing the key."""
    print("-- header diagnostics (ticket 11476413) --")
    redacted = f"len={len(key)} first2={key[:2]} last2={key[-2:]}"
    print(f"api_key_redacted {redacted}")

    proxy_env = [
        n
        for n in os.environ
        if n.lower() in ("http_proxy", "https_proxy", "all_proxy", "no_proxy")
    ]
    print(f"proxy_env_vars_set={proxy_env or 'none'}")
    print(f"urllib_detected_proxies={sorted(urllib.request.getproxies()) or 'none'}")

    base_headers = {
        "Accept": "application/json, text/html;q=0.8",
        "User-Agent": "s2s-ac-connect-check/1.0",
    }
    me_url = raw_url + "/api/3/users/me"
    fake_url = raw_url + "/api/3/zzz-does-not-exist"

    _print_wire_probe("api-token", me_url, {**base_headers, "Api-Token": key})
    _print_wire_probe(
        "bearer", me_url, {**base_headers, "Authorization": f"Bearer {key}"}
    )
    _print_wire_probe("no-auth", me_url, dict(base_headers))
    _print_wire_probe("api-token-fake-path", fake_url, {**base_headers, "Api-Token": key})

    # Echo probe: send the same header shape (dummy token of identical
    # length — NEVER the real key) to a third-party echo service to see
    # what an origin actually receives, i.e. whether any proxy between
    # this runtime and the internet adds or rewrites headers.
    dummy = "x" * len(key)
    try:
        result = _wire_probe(
            "https://httpbin.org/headers", {**base_headers, "Api-Token": dummy}
        )
        if result["status"] == 200:
            received = json.loads(result["body"]).get("headers", {})
            names = sorted(received)
            token_len = len(received.get("Api-Token", ""))
            print(f"ECHO httpbin received_header_names={','.join(names)}")
            print(f"ECHO httpbin api_token_received_len={token_len} (dummy sent)")
        else:
            print(f"ECHO httpbin unavailable status={result['status']}")
    except Exception as exc:  # noqa: BLE001 — diagnostic only
        print(f"ECHO httpbin failed: {type(exc).__name__}")


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
    egress = _egress_ip()
    print(f"egress_ip={egress}")
    for known in ("54.236.202.137", "44.216.155.73"):
        print(f"egress_matches_{known}={egress == known}")
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

    _run_header_diagnostics(raw_url, key)

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
