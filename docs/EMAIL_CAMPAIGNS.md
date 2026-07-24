# Email campaigns — journeys, tags, Calendly, Salesforce

Brooke-format templates: [`emails/templates/`](../emails/templates/)  
Journey map: [`emails/journey-map.json`](../emails/journey-map.json)  
Rebuild + provision:

```bash
export ACTIVECAMPAIGN_API_URL=https://service2software.api-us1.com
export ACTIVECAMPAIGN_API_KEY=...   # never commit
python3 emails/build_templates.py
python3 scripts/provision_ac_campaigns.py
```

## Website behavior (shipped)

| CTA | Behavior |
| --- | --- |
| Homepage / nav **Apply Now** | Scrolls to **Get In The Fight**, opens **Transitioning Service Member** form |
| Homepage **Hire Military Talent** | Scrolls to **Get In The Fight**, opens **Company Looking to Hire** form |
| **Already separated** ETS | No Calendly popup; confirmation copy only; `JOURNEY_SEGMENT=cand-journey-separated-onedone` |
| **Not you? Change selection** | Styled in red |
| Opt-ins on all lead forms | `field[37]` Newsletter, `field[38]` SMS (legal), `field[39]` Journey Segment |

## Custom fields

| ID | Perstag | Use |
| --- | --- | --- |
| 32 | `ETS_WINDOW` | Candidate separation window |
| 34 | `HIRING_ROLES` | Partner roles |
| 36 | `WEBSITE_SOURCE` | Which CTA/page |
| 37 | `NEWSLETTER_OPTIN` | `Yes` if checked |
| 38 | `SMS_OPTIN` | `Yes` if checked |
| 39 | `JOURNEY_SEGMENT` | Initial nobook/separated segment (set in browser) |
| 31 | `INITIAL_CALL_DATETIME` | Calendly start time |

## 1. Candidate journeys (ETS × booking)

On apply, site sets `JOURNEY_SEGMENT` to the **nobook** (or separated) tag name.  
When Patrick’s Calendly tag is added, AC automation should **swap** to the matching **booked** journey tag.

| ID | ETS answer | Booked? | Tag | Campaign |
| --- | --- | --- | --- | --- |
| 1a | 6–12 mo **or** More than 12 mo | Yes | `cand-journey-6-12-booked` | `S2S · Candidate · 6-12mo booked` |
| 1b | 3–6 months | Yes | `cand-journey-3-6-booked` | `S2S · Candidate · 3-6mo booked` |
| 1c | Less than 3 months | Yes | `cand-journey-lt3-booked` | `S2S · Candidate · <3mo booked` |
| 1d | 6–12 mo **or** More than 12 mo | No | `cand-journey-6-12-nobook` | `S2S · Candidate · 6-12mo no book` |
| 1e | 3–6 months | No | `cand-journey-3-6-nobook` | `S2S · Candidate · 3-6mo no book` |
| 1f | Less than 3 months | No | `cand-journey-lt3-nobook` | `S2S · Candidate · <3mo no book` |
| — | Already separated | N/A | `cand-journey-separated-onedone` | `S2S · Candidate · Separated one-and-done` (**no Calendly**) |

Also create/apply bucket tags on form submit (via AC If/Else on `ETS_WINDOW`):  
`cand-ets-gt12`, `cand-ets-6-12`, `cand-ets-3-6`, `cand-ets-lt3`, `cand-ets-separated`.

### Candidate automations to build in AC UI

1. **Apply (form Military Application / list Website Candidates)**  
   - If/Else on `ETS_WINDOW` → Add matching `cand-ets-*` tag + `cand-journey-*-nobook` (or separated one-done)  
   - If `NEWSLETTER_OPTIN = Yes` → tag `optin-newsletter` (+ subscribe Home Page Group if desired)  
   - If `SMS_OPTIN = Yes` → tag `optin-sms`  
   - If **not** separated → Send matching **nobook** campaign; Wait 1 day; if still no Patrick Calendly tag → nudge once  
   - If **separated** → Send **Separated one-and-done** only (never Calendly)

2. **Booked (tag `calendly-integration-S2S_Discovery_Call_w/_Patrick`)**  
   - Add `cand-call-booked` + `website-servicemember-booked`  
   - Remove matching `*-nobook` journey tag; add matching `*-booked` journey tag (If/Else on `ETS_WINDOW`)  
   - Send matching **booked** campaign (uses `%INITIAL_CALL_DATETIME%`)

## 2. Partner journeys (roles × booking)

| ID | Roles answer | Booked? | Tag | Campaign |
| --- | --- | --- | --- | --- |
| 2a | SDR/BDR **and/or** Account Executive | Yes | `partner-journey-sdr-ae-booked` | `S2S · Partner · SDR/AE booked` |
| 2b | Customer Success | Yes | `partner-journey-cs-booked` | `S2S · Partner · CS booked` |
| 2c | Multiple / Other | Yes | `partner-journey-other-booked` | `S2S · Partner · Other booked` |
| 2a | SDR/BDR **and/or** AE | No | `partner-journey-sdr-ae-nobook` | `S2S · Partner · SDR/AE no book` |
| 2b | Customer Success | No | `partner-journey-cs-nobook` | `S2S · Partner · CS no book` |
| 2c | Multiple / Other | No | `partner-journey-other-nobook` | `S2S · Partner · Other no book` |

Role bucket tags: `partner-roles-sdr-ae`, `partner-roles-cs`, `partner-roles-other`.

### Partner automations

1. **Apply (form Partner Inquiry)** → role tags + `partner-journey-*-nobook` + opt-in tags → send matching nobook campaign  
2. **Booked (tag `calendly-integration-S2S_Initial_Call_with_David`)** → `partner-call-booked` / `website-partner-booked` → swap to `*-booked` journey tag → send booked campaign

## 3. Newsletter / SMS opt-in

Checkboxes on candidate + partner forms post:

- `field[37]=Yes` → automation adds `optin-newsletter` (and optionally list **Home Page Group**)  
- `field[38]=Yes` → automation adds `optin-sms` (Twilio / compliance — only text if tagged)

Newsletter welcome sender: **dave@service2software.org**.  
Candidate journey senders: **recruiting@service2software.org**.

## 4. Calendly + Salesforce (your checklist)

| Task | Owner | Detail |
| --- | --- | --- |
| Map Calendly start → `INITIAL_CALL_DATETIME` (31) | AC/Calendly settings | Required for booked emails |
| Calendly → Salesforce sync | Ops | Critical dependency called out with Dave |
| Salesforce routing | AC Salesforce connector | List 5 / candidate tags → Recruiting/Patrick; List 6 / partner tags → David; newsletter-only → no sales Lead |
| Wire automations above | AC UI | API cannot create automation graphs |
| Test leads per ETS + role | Pre go-live | Confirm correct journey tag + email |
| SMS campaign resubmit | After site live | Twilio may block until portal URL is live |

## Sending addresses (warmed)

- `recruiting@` — candidate journeys  
- `dave@service2software.org` — newsletter  
- `info@` / `support@` — portal/general (not these marketing journeys)

## Manual AC steps (cannot be done via API)

1. Build candidate + partner automations from the tables above (If/Else on fields/tags → Send matching `S2S · …` campaign).  
2. Confirm Calendly field map + SF sync.  
3. Activate automations after a test lead per segment.  
4. Dave: revise copy in Claude using Brock/Brooke template against the provisioned HTML.
