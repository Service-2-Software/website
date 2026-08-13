# Email / automation flow scrub

Last run: **2026-08-12** (UTC) on branch `cursor/email-scrub-full-2b72`.  
Full machine log: `/opt/cursor/artifacts/email_flow_scrub_2026-08-12.log` (cloud artifact).

## Verdict

| Layer | Status |
| --- | --- |
| Website → AC form wiring | **PASS** (5/5 paths) |
| Journey JS (ETS / roles / separated / SMS) | **PASS** |
| Source email templates (27) + PNG header + links | **PASS** |
| Public AC form embeds + live `proc.php` posts | **PASS** (5/5 HTTP 200) |
| Authenticated AC API (automations, tags, enrollment, delivery) | **BLOCKED** — Cloudflare **403** |
| AC browser UI (automation canvas) | **PARTIAL** — user Desktop browser logged in; cloud agent browser still session-expired |

Static and public integration look healthy. Live automation list is **partially** known from the user’s Automations screenshot; canvas triggers / If/Else / Send mappings still need capture.

## Live automations (from user Desktop browser screenshots 2026-08-12)

Merged from two Automations list crops (names as shown in AC UI):

| Automation | Status | Maps to expected |
| --- | --- | --- |
| Website - Candidate Journey - Applied / No Call | **Active** | Candidate apply / ETS / separated email |
| Website - Candidate — Booked Call | **Active** | Patrick Calendly booked (+ timing-ineligible?) |
| Website - Candidate — Initial Call Completed | **Active** | Post-call Pre-Core portal |
| Candidate SMS — Applied / No Call | **Active** | Candidate SMS apply |
| Candidate SMS — Call Booked / Website - Candidate SMS — Call Booked | **Active** | Candidate SMS booked (same journey; verify not duplicate rows) |
| Inquiry / No Call (#2) | *(seen; confirm Active)* | Likely Partner apply / no-call email — **open to confirm Form 16** |
| Website - Partner — Booked Call | **Active** | David Calendly booked |
| Website - Partner SMS Consent / Nudge | **Active** | Partner SMS inquiry / no call |
| Website - Partner SMS Call Booked | **Active** | Partner SMS booked |
| Newsletter - Welcome | **Active** | Newsletter welcome |
| Automation 4 | **Inactive** | Stub — identify / rename / delete |

### Coverage vs expected journeys

| Expected journey | Present in list? |
| --- | --- |
| Candidate Applied / No Call (email) | **Yes** — Active |
| Candidate Booked Call (email) | **Yes** — Active |
| Candidate Initial Call Completed | **Yes** — Active |
| Partner Inquiry / No Call (email) | **Likely** — `Inquiry / No Call (#2)` (confirm) |
| Partner Booked Call (email) | **Yes** — Active |
| Newsletter Welcome | **Yes** — Active |
| Candidate SMS Applied / No Call | **Yes** — Active |
| Candidate SMS Call Booked | **Yes** — Active |
| Partner SMS Inquiry / No Call | **Yes** — Active (`Consent / Nudge`) |
| Partner SMS Call Booked | **Yes** — Active |

### Still need from canvases (Edit → screenshot)

For each Active automation: trigger, If/Else (`ETS_WINDOW` / `HIRING_ROLES` / `SMS_OPTIN` + phone), Wait steps, Send → campaign name, and that timing-ineligible + separated paths exist on the candidate canvases.

## What passed

### Site forms → ActiveCampaign

| Site path | AC form | `WEBSITE_SOURCE` |
| --- | --- | --- |
| Home candidate | **11** Military Application | `home-candidate` |
| Military page | **11** | `military-page` |
| Home partner | **16** Partner Inquiry | `home-partner` |
| Companies page | **16** | `companies-page` |
| Newsletter | **13** Home Page Group | `newsletter` |

Live posts to `service2software.activehosted.com/proc.php` returned **HTTP 200** for all five (test emails `ac-scrub+…@example.com`). Partner forms include phone + explicit SMS consent; candidates include ETS/branch/opt-ins/journey segment.

### Templates

- 27 unique keys in `emails/templates/manifest.json`
- Each key has message + campaign IDs in `emails/ac-provision-state.json`
- Journey map tags align with templates (including timing-ineligible + Pre-Core post-call)
- PNG wordmark header + unsubscribe present on all source templates
- Calendly, CloudFront deep links, and Pre-Core portal URLs returned HTTP 200

## What is blocked

Authenticated calls to:

- `https://service2software.api-us1.com/api/3/*`
- `https://service2software.activehosted.com/admin/api.php?api_key=…`

return **HTTP 403** from **Cloudflare** (empty body). Public form embeds and `proc.php` still work.

Observed from this cloud VM egress IP: **`52.73.250.138`**.

`ACTIVECAMPAIGN_API_URL` and `ACTIVECAMPAIGN_API_KEY` **are present** in the environment (key length 72). This is not a missing-secret problem — it is an **API WAF / IP block** (or equivalent) on authenticated routes.

Cloud **agent** browser automation still hits **“Your session has expired.”** The user’s Cursor Desktop Simple Browser *is* logged in (Automations list visible) — that session is **not** shared with the agent’s remote Chrome, so the agent cannot click through canvases itself.

Partial automation names/statuses were taken from the user’s screenshot (see table above). This scrub still could **not**:

1. List the **full** automations page (rows below the fold)  
2. Inspect triggers (form / tag / list) on each canvas  
3. Inspect If/Else on `ETS_WINDOW`, `HIRING_ROLES`, `SMS_OPTIN`  
4. Map Send steps → campaign/message IDs vs provision state  
5. Confirm post-submit list membership, fieldValues, tags  
6. Confirm ContactAutomation enrollment  
7. Confirm email/SMS delivery logs  
8. Identify what **Automation 4** (Inactive) actually is  

## How to unblock (pick one)

### A. Fix API access (preferred)

1. In ActiveCampaign: **Settings → Developer** → confirm the key is valid (or **Generate new key**).  
2. Cursor Cloud Secrets as **Environment variables**:  
   - `ACTIVECAMPAIGN_API_URL` = `https://service2software.api-us1.com`  
   - `ACTIVECAMPAIGN_API_KEY` = that key  
3. Start a **new** agent run.  
4. If API still returns **403** from Cloudflare: ask ActiveCampaign support to allowlist egress IP **`52.73.250.138`** (or your cloud agent IP range) for API access. Public form posts already succeed from this IP.

### B. Browser session for canvas audit

Keep ActiveCampaign logged in **in the agent’s remote browser** (not only on your laptop). Session timeouts invalidate UI audits quickly.

## Manual smoke checklist (until API works)

Use these after flipping automations **Active**:

1. Submit home candidate (6–12 months) → expect Website Candidates + book-nudge email.  
2. Submit already-separated candidate → one-and-done email, **no** Calendly.  
3. Book Patrick Calendly → booked / timing-ineligible branch as appropriate.  
4. Submit partner (SDR) with phone + SMS opt-in → Website Partners + email; SMS only if SMS automation is Active.  
5. Newsletter signup → Welcome series.  
6. Tag `cand-initial-call-completed` → Pre-Core portal email.

See [`EMAIL_CAMPAIGNS.md`](EMAIL_CAMPAIGNS.md) for full automation recipes.
