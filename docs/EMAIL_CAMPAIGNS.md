# Email campaigns — ActiveCampaign + Calendly + Salesforce

Brooke-format HTML templates live in [`emails/templates/`](../emails/templates/).  
Rebuild with `python3 emails/build_templates.py`.  
Provision messages/campaigns/lists into ActiveCampaign with:

```bash
export ACTIVECAMPAIGN_API_URL=https://service2software.api-us1.com
export ACTIVECAMPAIGN_API_KEY=...   # never commit
python3 emails/build_templates.py
python3 scripts/provision_ac_campaigns.py
```

State file (message/campaign IDs): `emails/ac-provision-state.json`.

## Website → ActiveCampaign entry points

| Site CTA / form | AC form | List | `field[36]` WEBSITE_SOURCE |
| --- | --- | --- | --- |
| Home → Candidate | 11 Military Application | Website Candidates (5) | `home-candidate` |
| Military page Apply | 11 | Website Candidates (5) | `military-page` |
| Home → Partner | 12 Partner Inquiry | Website Partners (6) | `home-partner` |
| Companies page Inquire | 12 | Website Partners (6) | `companies-page` |
| Newsletter | 13 Home Page Group | Home Page Group (4) | `newsletter` |

Automations should also subscribe Candidates/Partners onto **Master Contact List (3)** if you still want a single omnibus list.

Email validation runs client-side before the AC `proc.php` post.

## Campaign series (automations)

ActiveCampaign’s API cannot create automations (405). Messages + draft campaigns are provisioned; wire these automations once in the AC UI (**Automations → Create**). Use the provisioned campaign/message names (`S2S · …`).

### A. Candidate journey (form 11 / list Website Candidates)

1. **Trigger:** Submits form *Military Application* **or** Subscribes to *Website Candidates*
2. **Immediate:** Send `S2S · Candidate · Book your intro call`
3. **Wait 1 day** → If contact does **not** have Calendly tag  
   `calendly-integration-S2S_Discovery_Call_w/_Patrick`  
   (or `call-booked-candidate`) → resend book nudge once
4. **Trigger (separate automation):** Tag added  
   `calendly-integration-S2S_Discovery_Call_w/_Patrick`  
   → Send `S2S · Candidate · Booking confirmation`  
   (uses `%INITIAL_CALL_DATETIME%` — field 31)
5. **Wait until 24h before** call (or 1 day after booking) → Send `S2S · Candidate · Call reminder`
6. **Wait 2 days after form** (if still engaged) → Send `S2S · Candidate · What SkillBridge looks like`

### B. Partner journey (form 12 / list Website Partners)

1. **Trigger:** Submits *Partner Inquiry* **or** Subscribes to *Website Partners*
2. **Immediate:** Send `S2S · Partner · Schedule hiring call`
3. **Trigger:** Tag  
   `calendly-integration-S2S_Initial_Call_with_David`  
   → Send `S2S · Partner · Booking confirmation`
4. Reminder + nurture: `S2S · Partner · Call reminder`, `S2S · Partner · How hiring works`

### C. Newsletter (form 13 / list Home Page Group)

1. **Trigger:** Submits *Home Page Group* / subscribes to list 4  
2. Immediate → `S2S · Newsletter · Welcome`  
3. Wait 2–3 days → `S2S · Newsletter · Story & mission`  
4. Wait 2–3 days → `S2S · Newsletter · What we offer`  

Replace the inactive “3-Email Welcome Sequence” (automation 7) content with these Brooke-format campaigns, or turn that automation off and use this series.

## Calendly wiring

Native AC↔Calendly integration is already tagging contacts:

| Calendly event | AC tag (existing) | Confirmation email |
| --- | --- | --- |
| Patrick initial / discovery call | `calendly-integration-S2S_Discovery_Call_w/_Patrick` | Candidate booking confirmation |
| David hiring call | `calendly-integration-S2S_Initial_Call_with_David` | Partner booking confirmation |
| CEO intro / about | `calendly-integration-S2S_CEO_Intro_Call` | Optional — About “Get Involved” |

**Required in Calendly → ActiveCampaign field mapping:**  
map event start time → contact field **Initial Call Datetime** (`INITIAL_CALL_DATETIME`, field id **31**).  
Confirm under ActiveCampaign → *Settings → Integrations → Calendly* (or the Calendly AC app settings).

Site Calendly URLs (unchanged):

- Candidates: `calendly.com/patrick-service2software/initial-call-with-service-2-software`
- Partners: `calendly.com/davidhester/s2s-hiring`
- About: `calendly.com/davidhester/30minutes`

## Salesforce routing

AC Salesforce connection `ActiveCamp.USA36` is active (`connections` id 1).  
Configure sync rules in **AC → Salesforce** so website leads land on the right pipeline:

| Signal | Salesforce routing |
| --- | --- |
| List *Website Candidates* or `WEBSITE_SOURCE` starts with `home-candidate` / `military-page` | Lead — Recruiting pipeline; Lead Source = `Website - Candidate`; Owner = Patrick Gilroy |
| List *Website Partners* or source `home-partner` / `companies-page` | Lead — Partner/Sales pipeline; Lead Source = `Website - Partner`; Owner = David Hester |
| List *Home Page Group* only | Marketing contact / campaign member — **do not** create a sales Lead unless they later apply or inquire |
| Calendly booked tags | Update Lead Status (e.g. `Intro Call Booked`) and sync `INITIAL_CALL_DATETIME` |

Ensure these contact fields sync to Salesforce:  
`WEBSITE_SOURCE`, `BRANCH`, `ETS_WINDOW`, `COMPANY`, `HIRING_ROLES`, `INITIAL_CALL_DATETIME`, phone, email, full name.

Existing SF bridge tags (`created-from-salesforce-lead`, `added-to-salesforce`, etc.) remain owned by the native connector.

## Tags created for journeys

`src-home-candidate`, `src-home-partner`, `src-military-page`, `src-companies-page`, `src-newsletter`, `src-about-involved`, `journey-candidate`, `journey-partner`, `journey-newsletter`, `call-booked-candidate`, `call-booked-partner`, `awaiting-calendly-candidate`, `awaiting-calendly-partner`.

Form actions cannot add tags via API (AC returns 500). Prefer **list + WEBSITE_SOURCE** for automation conditions; optionally add “Add tag” actions manually on forms 11/12/13 in the AC form builder.

## Already provisioned in ActiveCampaign

| Resource | IDs / notes |
| --- | --- |
| Lists | Website Candidates **5**, Website Partners **6** (+ Master **3**, Home Page Group **4**) |
| Custom field | `WEBSITE_SOURCE` field **36**; `INITIAL_CALL_DATETIME` field **31** |
| Forms | **11** → list 5; **12** → list 6; **13** → list 4 |
| Messages + draft campaigns | See `emails/ac-provision-state.json` (keys `candidate-*`, `partner-*`, `newsletter-*`) |
| Newsletter automation **7** | Existing send messages **14/15/16** overwritten with Brooke HTML |
| Candidate automation **3** | Send message updated to Brooke “book your intro call”; **change trigger from form 7 → form 11** in UI |

## Manual checklist (finish wiring)

1. **Automations → Candidate Application - COMPLETE (3):** change start trigger to form *Military Application* (11) or “Subscribes to Website Candidates”; activate if inactive.
2. **Create Partner journey automation** (API cannot create automations): trigger form 12 / list 6 → partner nudge + Calendly confirmation series.
3. **Create Calendly confirmation automations** for tags `calendly-integration-S2S_Discovery_Call_w/_Patrick` and `calendly-integration-S2S_Initial_Call_with_David` using campaigns in `ac-provision-state.json`.
4. Confirm Calendly → `INITIAL_CALL_DATETIME` field mapping.
5. Confirm Salesforce lead routing for lists 5/6 (see table above).
6. Smoke test: home candidate form → list 5 + `WEBSITE_SOURCE=home-candidate` → book Patrick Calendly → confirmation with datetime.
