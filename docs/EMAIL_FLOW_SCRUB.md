# Email / automation flow scrub

Last run: **2026-08-12** (UTC) on branch `cursor/ac-email-scrub-27b5` (base: `cursor/ac-email-campaigns-5d2d`).  
Secrets present: `ACTIVECAMPAIGN_API_URL`, `ACTIVECAMPAIGN_API_KEY` (key length 72).  
Enrollment artifact: `/opt/cursor/artifacts/ac_enrollment_tests_2026-08-12.json`.

## Verdict

| Check | Status |
| --- | --- |
| (1) Automation status / trigger / Send→campaign mapping | **BLOCKED** — API Cloudflare 403; AC UI session expired |
| (2) Candidate ETS + partner role branch → campaigns | **Source PASS** (journey-map ↔ templates ↔ provision IDs). **Live canvas unverified** |
| (3) Calendly booked-tag automations | **UNVERIFIED** (names previously seen Active in UI screenshots) |
| (4) Post-call Pre-Core on `cand-initial-call-completed` | **UNVERIFIED** (automation previously listed Active; Send mapping not inspected) |
| (5) Newsletter + SMS automations | **UNVERIFIED** (list previously Active; Form 11 gap below) |
| (6) PNG wordmark header on all emails | **PASS** on all 27 source templates + live PNG URL HTTP 200 |
| Test contact enrollment via `proc.php` | **PASS** (11/11 → thank-you 302). Tag/automation enrollment needs API |

**Bottom line:** Keys are in env, but authenticated AC API (`/api/3/*` and `admin/api.php`) is still hard-blocked by Cloudflare from this cloud egress (empty 403). Public form posts and content CDN work. No live automation canvas or ContactAutomation confirmation was possible this run; nothing could be fixed via API.

## Blocker: API WAF (not missing secrets)

| Probe | Result |
| --- | --- |
| `GET /api/3/automations` with `Api-Token` | **403** Cloudflare, 0-byte body |
| Same without auth | **403** |
| v1 `admin/api.php?api_action=…` | **403** |
| `POST …/proc.php` (forms) | **302** thank-you (contact created) |
| Wordmark PNG under `/content/…` | **200** |
| AC admin UI (agent browser) | Login / “session has expired” |
| Active Campaign MCP | Tool discovery **error** (unavailable) |

Egress IP is **not stable** across probes in this environment (observed `3.233.180.130`, then `34.233.103.205`; prior scrub saw `52.73.250.138`). Single-IP allowlisting will keep failing as agents rotate.

### Unblock options

1. Ask ActiveCampaign support to allowlist **AWS us-east / Cursor cloud egress ASN** for API (or provide a stable egress proxy and allowlist that).
2. Log into AC in the **agent remote browser** long enough to screenshot each automation canvas (trigger, If/Else, Send).
3. Re-run `python3 scripts/scrub_ac_automations.py` once `/api/3` returns 200 — it verifies automations, campaigns, tags, wordmarks in live messages, and test-contact enrollment.

## What passed (static + public)

### Templates / provision / journey map

- 27 manifest keys; matching message + campaign IDs in `emails/ac-provision-state.json`.
- All journey-map candidate + partner tags resolve to templates and campaign names in `docs/EMAIL_CAMPAIGNS.md`.
- Post-call: tag `cand-initial-call-completed` → campaign `S2S · Candidate · Post-call Pre-Core portal` (message 56 / campaign 54 in state).
- Every `emails/templates/*.html` includes PNG wordmark  
  `…/94ef5e12-7838-4f52-9808-7f50811e72eb.png` and unsubscribe.
- Calendly (Patrick + David) and Pre-Core portal URLs returned HTTP 200.

### Website journey routing

Site JS sets `field[39]` (`JOURNEY_SEGMENT`) correctly:

| Audience | Input | Segment tag |
| --- | --- | --- |
| Candidate | 6–12 / >12 mo | `cand-journey-6-12-nobook` |
| Candidate | 3–6 mo | `cand-journey-3-6-nobook` |
| Candidate | &lt;3 mo | `cand-journey-lt3-nobook` |
| Candidate | Already separated | `cand-journey-separated-onedone` (no Calendly) |
| Partner | SDR/BDR or AE | `partner-journey-sdr-ae-nobook` |
| Partner | CS | `partner-journey-cs-nobook` |
| Partner | Multiple / Other | `partner-journey-other-nobook` |

Unchecked newsletter/SMS checkboxes are disabled before post (blank opt-in not sent).

### Enrollment test contacts (2026-08-12)

All posts returned thank-you redirects (`proc.php` → `f/thankyou.php?id=…`). Emails use `ac-scrub+…@example.com`:

| Segment | Example local-part suffix |
| --- | --- |
| Candidate ETS ×5 | `cand-6-12`, `cand-gt12`, `cand-3-6`, `cand-lt3`, `cand-sep` |
| Partner roles ×4 | `partner-sdr`, `partner-ae`, `partner-cs`, `partner-other` |
| Newsletter | `nl-…` |
| Partner no SMS | `partner-nosms-…` |

**Cannot confirm** list membership, tags, ContactAutomation, or sends without API.

## Issues found

### P0 — Cannot scrub or fix live automations via API

Cloudflare blocks `/api/3` from cloud agents. Fixes that need API (activate automations, remap Send steps, add form fields, tag test contacts) are blocked.

### P1 — Form 11 (Military Application) missing opt-in / journey / source fields in AC form UI

Public form HTML field inventory:

| Form | Fields present in AC form |
| --- | --- |
| **11** Military Application | `email`, `phone`, `field[5]` branch, `field[32]` ETS only |
| **16** Partner Inquiry | `email`, `phone`, `field[34–39]` (roles, company, source, newsletter, SMS, journey) |
| **13** Newsletter | `email`, `phone` |

Website still **posts** `field[36–39]` (and opt-ins) on candidate forms. Prior smoke tests suggested custom fields can stick when list relations exist, but Form 11’s native definition does not include newsletter / SMS / journey / source — unlike Form 16.  
`scripts/provision_ac_campaigns.py` now attempts to add those cfields when API works.

### P1 — Live canvas mapping still unverified

From earlier Desktop screenshots (prior scrub), these names appeared **Active**:

- Website - Candidate Journey - Applied / No Call  
- Website - Candidate — Booked Call  
- Website - Candidate — Initial Call Completed  
- Website - Partner — Booked Call / Inquiry / No Call (#2)  
- Newsletter - Welcome  
- Candidate + Partner SMS variants  

Still unknown without canvas capture:

1. Triggers (form 11/16/13 vs Calendly tags vs `cand-initial-call-completed`)
2. If/Else on `ETS_WINDOW` / `HIRING_ROLES` / `SMS_OPTIN` + phone
3. Send steps → exact `S2S · …` campaign IDs vs `ac-provision-state.json`
4. Timing-ineligible path (`cand-journey-ineligible-timing` / campaign 72) on booked flow
5. Whether inactive **Automation 4** is a stub to delete

### P2 — Orphan `cand-journey-lt3-booked` campaign

Journey map routes **&lt;3 mo + booked** and **separated + booked** to **Ineligible — timing**, not `cand-journey-lt3-booked`. Template + campaign IDs still exist in provision state (message 49 / campaign 47). Risk: an automation Send step still pointing at the lt3-booked campaign instead of ineligible-timing.

### P2 — Rotating egress IP

Do not treat one IP allowlist as durable for Cursor cloud agents.

## Manual checklist once API or UI works

1. Run `python3 scripts/scrub_ac_automations.py` (expects API 200).  
2. Confirm Form 11 has fields 36–39 (or re-run provision).  
3. Open each Website-* automation canvas; match Send campaigns to state IDs.  
4. Tag one scrub contact with Patrick Calendly tag + `cand-initial-call-completed`; confirm booked + Pre-Core emails.  
5. Partner SMS: consent + phone → nudge; no consent → no SMS.  
6. Delete or rename inactive **Automation 4** if still a stub.

See [`EMAIL_CAMPAIGNS.md`](EMAIL_CAMPAIGNS.md) for intended recipes.
