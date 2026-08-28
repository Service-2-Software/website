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
