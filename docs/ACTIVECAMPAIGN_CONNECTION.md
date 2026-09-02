# ActiveCampaign connection (Cursor Cloud)

Website lead forms do **not** use the API. They POST to
`https://service2software.activehosted.com/proc.php` (forms 11 / 12 / 13).
That path still works from Cursor Cloud.

Automation, MCP, and campaign scripts need `/api/3`. That path is what
keeps failing.

## What fails

From Cursor Cloud (this environment and prior agents):

| Request | Result |
| --- | --- |
| `GET $ACTIVECAMPAIGN_API_URL/api/3/users/me` with `Api-Token` | HTTP **403**, **0-byte** body, `server: cloudflare` |
| `GET …/api/3/zzz-does-not-exist` (should be 404) | same empty **403** |
| `GET /admin/api.php` (v1) | same empty **403** |
| Active Campaign MCP | tool discovery fails (same block) |
| Admin UI in the agent browser | Cloudflare Turnstile loops; login never completes |
| `GET /f/11`, `GET /proc.php` | **200** |

Secrets are present and look valid (API URL set, key length 72). A
nonexistent `/api/3` path would be 404 if the request reached
ActiveCampaign. Empty 403 on both real and fake paths means Cloudflare
is dropping the request at the edge. This is not a bad key.

Cursor Cloud egress IPs rotate (example from this run: `44.216.155.73`).
Allowlisting a single IP will keep failing.

## Recheck

```bash
python3 scripts/ac_connect_check.py
```

| Exit | Meaning |
| --- | --- |
| 0 | API works — safe to run provision/scrub scripts |
| 1 | Missing `ACTIVECAMPAIGN_API_URL` / `ACTIVECAMPAIGN_API_KEY` |
| 2 | Cloudflare still blocking `/api/3` |
| 3 | API reachable, key rejected — rotate the key |
| 4 | Something else (network / unexpected HTTP) |

The script never prints the token.

## Status (2026-08-28)

| Check | Result |
| --- | --- |
| Laptop `GET /api/3/users/me` | **200** — key is valid |
| Cursor Cloud `/api/3` | still empty Cloudflare **403** |
| ActiveCampaign AI chat | confirmed: not an account setting; infra must whitelist |
| Human support ticket | **11476413** |

When support says the Cloudflare rule is lifted, rerun
`python3 scripts/ac_connect_check.py` from Cursor Cloud. Exit `0` means
API/MCP work can resume.

## Recheck (2026-09-02, ticket 11476413 follow-up)

Support (Danielle) said the 403 is not a Cloudflare WAF block: their app
received the request and returned 403, the empty body is expected on
auth failure, and the request they inspected had ~2.4 KB of headers.
The script now prints wire-level header diagnostics so each rerun
measures this instead of assuming. Results from this run:

| Measurement | Result |
| --- | --- |
| Secrets injected | `ACTIVECAMPAIGN_API_URL` + `ACTIVECAMPAIGN_API_KEY` set, key length 72 |
| Proxy env vars / detected proxies | none — requests go direct |
| `Api-Token` probe (script default) | empty 403, `server: cloudflare`, `cf-ray` logged |
| `Authorization: Bearer <key>` probe | identical empty 403 |
| No auth header at all | identical empty 403 |
| `Api-Token` + nonexistent `/api/3` path | identical empty 403 (not a JSON 404) |
| Request head size (`Api-Token` probe) | **261 bytes** total — 5 headers (`Host`, `Accept-Encoding`, `Accept`, `User-Agent`, `Api-Token`) |
| Header echo (httpbin, dummy token) | origin received exactly the headers sent; nothing added or rewritten in transit |
| `curl` with the minimal laptop headers, from Cursor Cloud | same empty 403 over HTTP/2 |
| Egress IP across 3 runs in ~3 min | `34.232.125.200`, `44.216.155.73`, `184.72.220.21` — rotates per run |

What this rules out:

- **Wrong/missing auth header** — a valid `Api-Token`, a Bearer
  `Authorization`, and no auth at all are indistinguishable (all empty
  403). If the AC app were rejecting bad auth, the valid-token request
  would differ from the no-auth request.
- **Proxy rewriting headers** — no proxy is configured and an external
  echo host receives the request byte-for-byte as sent.
- **Client fingerprint** — `curl` with the exact working laptop headers
  fails identically from Cursor Cloud.
- **The ~2.4 KB request support inspected was not this script** — this
  script's whole request head is 261 bytes. Support likely looked at a
  browser or MCP request. Give them a `cf-ray` id from the script
  output so they inspect the right request.

The only remaining variable versus the working laptop request is the
source network (rotating AWS us-east-1 IPs). The `cf-ray` values in
each script run identify the exact requests for support to look up.

## Unblock (must be done in the AC account, not in this repo)

1. From a laptop, confirm the key works:

   ```bash
   curl -sS -o /tmp/ac-me.json -w "%{http_code}\n" \
     -H "Api-Token: $ACTIVECAMPAIGN_API_KEY" \
     -H "Accept: application/json" \
     "$ACTIVECAMPAIGN_API_URL/api/3/users/me"
   ```

   `200` + JSON means only datacenter / Cursor Cloud IPs are blocked.

2. In ActiveCampaign → **Settings → Developer**, turn off any “lock API
   to these IPs” setting. Cloud agent IPs change every run.

3. Open an ActiveCampaign support ticket: ask them to stop Cloudflare
   from returning empty 403s on `/api/3` from AWS us-east-1 (Cursor
   Cloud). Mention that public `/f/11` and `/proc.php` still return 200.

Until that is done, cloud agents can test public forms only. Campaign
and automation edits have to happen in the AC UI from a normal browser,
or from a local Cursor session whose IP is not blocked.
