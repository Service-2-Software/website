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
| 1c | Less than 3 months **or already separated** | Yes / existing booking | `cand-journey-ineligible-timing` | `S2S · Candidate · Ineligible — timing` |
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
   - If `ETS_WINDOW` is **Less than 3 months OR Already separated**: add
     `cand-journey-ineligible-timing` and send **S2S · Candidate · Ineligible — timing**
     (no Calendly link)
   - Otherwise send the matching **booked** campaign (uses `%INITIAL_CALL_DATETIME%`)

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

### Partner SMS automations (Twilio approved)

Both partner forms collect the core AC `phone` field and an unchecked
`SMS_OPTIN` checkbox. If SMS consent is checked, the browser requires a
10–15 digit phone number. Never send when `SMS_OPTIN` is blank.

#### A. `Website - Partner SMS — Inquiry / No Call`

1. Trigger: **Submits form** → `Partner Inquiry` (Form 16), runs once.
2. If/Else (**AND**):
   - `SMS_OPTIN` equals `Yes`
   - Phone is not blank
3. **No** → End.
4. **Yes**:
   - Add `optin-sms`
   - Add `partner-sms-consented`
   - Send SMS:

   > S2S: Thanks for your interest in hiring military talent. Book a call with David: https://calendly.com/davidhester/s2s-hiring Reply STOP to opt out.

   - Add `partner-sms-nudge-sent`
   - Wait 1 day
   - If tag `calendly-integration-S2S_Initial_Call_with_David` exists → End
   - Otherwise send one final SMS:

   > S2S: Still interested in veteran talent? Choose a time with David: https://calendly.com/davidhester/s2s-hiring Reply STOP to opt out.

   - End; do not send more booking nudges.

#### B. `Website - Partner SMS — Call Booked`

1. Trigger: tag `calendly-integration-S2S_Initial_Call_with_David` is added,
   runs once.
2. If/Else (**AND**): `SMS_OPTIN = Yes` and Phone is not blank.
3. **No** → End.
4. **Yes** → Send:

   > S2S: Your hiring call with David is booked for %INITIAL_CALL_DATETIME%. Need another time? https://calendly.com/davidhester/s2s-hiring Reply STOP to opt out.

5. Add `partner-sms-booked-confirmation-sent`; End.

Do not add another reminder if Calendly already sends SMS reminders. AC/Twilio
STOP suppression must remain authoritative: never re-add an opted-out number.

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
| SMS campaign | Approved | Build the consent-gated SMS automations above |

## Sending addresses (warmed)

- `recruiting@` — candidate journeys  
- `dave@service2software.org` — newsletter  
- `info@` / `support@` — portal/general (not these marketing journeys)

## Post–initial-call email (Pre-Core portal)

Source doc: [`docs/pre-core-candidate-portal.md`](pre-core-candidate-portal.md)  
Campaign: **`S2S · Candidate · Post-call Pre-Core portal`**  
Template key: `candidate-post-call-precore-portal`

**When to send:** after the candidate **completes** their initial call with Patrick (not when they only book).

| Step | Action |
| --- | --- |
| 1 | Create/use tag `cand-initial-call-completed` |
| 2 | Apply that tag when the call is done (Salesforce Lead Status sync, or Patrick/recruiter marks complete in AC) |
| 3 | Automation: **Tag is added** `cand-initial-call-completed` → **Send** `S2S · Candidate · Post-call Pre-Core portal` |

Portal links in the email:

- Pre-Core login: https://s2score.service2software.org/candidatelogin  
- Pre-Core home: https://s2score.service2software.org/candidates/leads  
- Core (after acceptance): https://s2score.service2software.org/login  

## Form smoke test (API)

Automated checks (Aug 2026) posted each site form to `proc.php` and verified contacts in AC:

| Form path | List | `WEBSITE_SOURCE` | Journey / extras |
| --- | --- | --- | --- |
| Home candidate | Website Candidates (5) | `home-candidate` | `JOURNEY_SEGMENT` + ETS/Branch |
| Military page | Website Candidates (5) | `military-page` | same |
| Home partner | Website Partners (6) | `home-partner` | roles + company |
| Companies page | Website Partners (6) | `companies-page` | roles + company |
| Newsletter | Home Page Group (4) | `newsletter` | email only |

**Fix applied:** `ETS_WINDOW` (32), `HIRING_ROLES` (34), and `COMPANY` (35) had no list field relations, so those values were dropped on form post. They are now related to lists 3–6.

**Still manual:** Activate automations in AC UI and confirm the actual emails send. `Candidate Journey` (automation 8) is triggered on form 11 but showed `entered=0` / inactive during smoke test — flip it **Active** and submit one real test lead to confirm the send steps.

## Scrub / verify

Full scrub log: [`docs/EMAIL_FLOW_SCRUB.md`](EMAIL_FLOW_SCRUB.md)

```bash
export ACTIVECAMPAIGN_API_URL=https://service2software.api-us1.com
export ACTIVECAMPAIGN_API_KEY=...
python3 scripts/scrub_ac_automations.py
```

**Known gap:** Military Application (form **11**) public HTML only exposes branch + ETS; Partner form **16** includes source / newsletter / SMS / journey fields. Website still posts `field[36–39]` on candidate forms — re-run `provision_ac_campaigns.py` once API access works so form 11 cfields match.

**Orphan risk:** `cand-journey-lt3-booked` remains provisioned, but booked **&lt;3 mo** / separated must Send **Ineligible — timing** (`candidate-ineligible-timing`), not the lt3-booked campaign.

## Manual AC steps (cannot be done via API)

1. Build candidate + partner automations from the tables above (If/Else on fields/tags → Send matching `S2S · …` campaign).  
2. Confirm Calendly field map + SF sync.  
3. Wire **post-call Pre-Core portal** automation on `cand-initial-call-completed`.  
4. Activate automations after a test lead per segment.  
5. Dave: revise copy in Claude using Brock/Brooke template against the provisioned HTML.
