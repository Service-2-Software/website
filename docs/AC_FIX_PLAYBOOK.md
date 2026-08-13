# ActiveCampaign fix playbook

Run this once either:

1. `/api/3` returns 200 (clear the Developer IP allowlist), then
   `python3 scripts/provision_ac_campaigns.py && python3 scripts/scrub_ac_automations.py`, **or**
2. Someone is logged into
   https://service2software.activehosted.com/admin/ **in the agent browser**
   and follows the UI steps below.

Order matters. Do not skip step 1 — everything downstream depends on the
candidate form keeping the fields the site posts.

---

## 1. Repair form fields (required first)

### Form 11 — Military Application

Add these custom fields (clone types from form 16 if unsure):

| Field | ID | Type | Required |
| --- | --- | --- | --- |
| Website Source | 36 | text / hidden | no |
| Newsletter Opt-In | 37 | text | no |
| SMS Opt-In | 38 | text | no |
| Journey Segment | 39 | text | no |

Keep existing: Branch (5), How Far From Separation (32), phone, email, name.

Save. Confirm the public embed
`https://service2software.activehosted.com/f/11` contains
`field[36]`…`field[39]`.

### Form 13 — Home Page Group

Add **Website Source (36)**. Save. Confirm `/f/13` declares it.

Via API (when unblocked): `python3 scripts/provision_ac_campaigns.py`
clones these from form 16 and fails if the write does not stick.

---

## 2. Candidate apply automation

Open **Website - Candidate Journey - Applied / No Call** (or rename the
current form-11 trigger automation to that).

**Trigger:** Submits form → Military Application (11), runs once.

**Steps:**

1. If/Else on `ETS_WINDOW` (32):
   - `More than 12 months` **or** `6-12 months`
     → add `cand-ets-gt12` / `cand-ets-6-12` as appropriate  
     → add `cand-journey-6-12-nobook`  
     → Send **`S2S · Candidate · 6-12mo no book`**
   - `3-6 months`
     → add `cand-ets-3-6` + `cand-journey-3-6-nobook`  
     → Send **`S2S · Candidate · 3-6mo no book`**
   - `Less than 3 months`
     → add `cand-ets-lt3` + `cand-journey-lt3-nobook`  
     → Send **`S2S · Candidate · <3mo no book`**
   - `Already separated`
     → add `cand-ets-separated` + `cand-journey-separated-onedone`  
     → Send **`S2S · Candidate · Separated one-and-done`**  
     → **End. No Calendly. No wait-and-nudge.**
2. If `NEWSLETTER_OPTIN` = `Yes` → add `optin-newsletter` (optional: subscribe Home Page Group).
3. If `SMS_OPTIN` = `Yes` **and** phone not blank → add `optin-sms`.
4. For non-separated only: Wait 1 day; if Patrick Calendly tag still missing → send book nudge once.

**Critical:** Remove any unconditional Send of
`S2S · Candidate · Book your intro call` / message that currently fires for every submit. That is what the live test caught.

---

## 3. Candidate booked automation

Open **Website - Candidate — Booked Call**.

**Trigger:** Tag added → `calendly-integration-S2S_Discovery_Call_w/_Patrick`.

1. Add `cand-call-booked` + `website-servicemember-booked`.
2. Remove matching `*-nobook` journey tag.
3. If/Else on `ETS_WINDOW`:
   - 6–12 / >12 → add `cand-journey-6-12-booked` → Send **`S2S · Candidate · 6-12mo booked`**
   - 3–6 → add `cand-journey-3-6-booked` → Send **`S2S · Candidate · 3-6mo booked`**
   - <3 **or** Already separated → add `cand-journey-ineligible-timing` → Send **`S2S · Candidate · Ineligible — timing`** (no Calendly link in body)

Do **not** Send `cand-journey-lt3-booked` / campaign 47 — that duplicate is retired.

---

## 4. Partner apply automation

Open **Inquiry / No Call (#2)** (or whatever currently triggers on form 16).
Rename to **Website - Partner Journey - Inquiry / No Call**.

**Trigger:** Submits form → Partner Inquiry (16).

1. If/Else on `HIRING_ROLES` (34):
   - `SDR / BDR` **or** `Account Executive`
     → `partner-roles-sdr-ae` + `partner-journey-sdr-ae-nobook`  
     → Send **`S2S · Partner · SDR/AE no book`**
   - `Customer Success`
     → `partner-roles-cs` + `partner-journey-cs-nobook`  
     → Send **`S2S · Partner · CS no book`**
   - `Multiple / Other`
     → `partner-roles-other` + `partner-journey-other-nobook`  
     → Send **`S2S · Partner · Other no book`**
2. Opt-ins same as candidate (newsletter / SMS).
3. **Repoint every Send step** at the provisioned `S2S · Partner · …` campaigns.
   The live test received a subject that is not in this repo — those hand-edited
   campaigns must stop being the Send targets.

---

## 5. Partner booked automation

**Website - Partner — Booked Call**

**Trigger:** Tag → `calendly-integration-S2S_Initial_Call_with_David`.

Swap nobook → booked journey tags by role; Send the matching
`S2S · Partner · … booked` campaign.

---

## 6. Newsletter + SMS + post-call

Confirm these are Active and wired as named:

| Automation | Trigger | Send / action |
| --- | --- | --- |
| Newsletter - Welcome | Form 13 / list 4 | `S2S · Newsletter · Welcome` from warmed newsletter sender |
| Candidate SMS — Applied / No Call | Form 11 + SMS gate | Twilio SMS (consent + phone) |
| Candidate SMS — Call Booked | Patrick Calendly tag + SMS gate | booked SMS |
| Website - Partner SMS Consent / Nudge | Form 16 + SMS gate | see EMAIL_CAMPAIGNS.md |
| Website - Partner SMS Call Booked | David Calendly tag + SMS gate | booked SMS |
| Website - Candidate — Initial Call Completed | Tag `cand-initial-call-completed` | `S2S · Candidate · Post-call Pre-Core portal` |

Delete or permanently deactivate **Automation 4** if it is still the unnamed stub.

---

## 7. Cleanup

1. Archive AC **message 49** and **campaign 47** (`cand-journey-lt3-booked` retired duplicate).
2. Reconcile senders: delivered partner/newsletter mail came from
   `ceo@service2software.org` while the manifest says `david@` / `dave@`.
   Pick one set and make the campaign From address match.
3. Delete the eight `Scrub … @emalupe.com` test contacts (and their SF leads).

---

## 8. Verify

```bash
python3 scripts/scrub_ac_automations.py --json /tmp/scrub.json
# Must report 0 errors on ac-forms once forms are repaired.
# API tier still skips if /api/3 is blocked.

python3 scripts/ac_live_journey_test.py --wait 1500
# Expect PASS on all six scenarios.
```

Manual extras after live test:

1. Book a Patrick Calendly slot on a 6–12 mo test lead → booked campaign.
2. Book a Patrick slot on a <3 mo lead → ineligible-timing (not a Calendly push).
3. Apply tag `cand-initial-call-completed` → Pre-Core portal email.
4. Book a David Calendly slot on an SDR partner → SDR/AE booked campaign.
