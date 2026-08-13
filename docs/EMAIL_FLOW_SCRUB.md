# ActiveCampaign scrub — 2026-08-12

Branch `cursor/ac-email-campaigns-5d2d`. Reproduce with:

```bash
python3 scripts/scrub_ac_automations.py --json /tmp/scrub.json
python3 scripts/ac_live_journey_test.py --wait 1500
```

## Verdict

The authenticated AC API is blocked at the network edge, so automations could
not be read or repaired over `/api/3`. Instead the journeys were driven from
outside: six leads were submitted to the live forms and the resulting emails
were caught in real inboxes.

**Five of six journeys are broken in production.** Candidate ETS branching and
partner role branching are not happening at all, and the already-separated path
sends the one email it is specifically designed never to send.

| Area | Status |
| --- | --- |
| Candidate ETS branches | **BROKEN** — every ETS answer gets one legacy email |
| Already-separated one-and-done | **BROKEN** — receives a Calendly booking push |
| Partner role branches | **BROKEN** — SDR/AE gets the CS email; CS gets nothing |
| Newsletter opt-in on the candidate form | **BROKEN** — consent is discarded |
| Newsletter signup (form 13) | **PASS** |
| PNG wordmark in delivered mail | **PASS** — present in all six |
| Merge tag resolution | **PASS** for named leads; newsletter greeted "Hi ," (fixed) |
| Calendly booked-tag automations | **NOT VERIFIABLE** — needs the API or a real booking |
| Post-call Pre-Core portal automation | **NOT VERIFIABLE** — needs the API to apply the tag |
| Repo contract (map ↔ manifest ↔ state ↔ templates) | **PASS** after the fixes below |

## Live journey test

Six leads posted to `proc.php` with the exact payload the website sends, each to
its own real mailbox, then watched for 25 minutes.

| Scenario | Form | Expected campaign | Actually received |
| --- | --- | --- | --- |
| ETS 6–12 months | 11 | `S2S · Candidate · 6-12mo no book` | `S2S · Candidate · Book your intro call` |
| ETS < 3 months | 11 | `S2S · Candidate · <3mo no book` | `S2S · Candidate · Book your intro call` |
| Already separated | 11 | `S2S · Candidate · Separated one-and-done` | `S2S · Candidate · Book your intro call` |
| Partner SDR / BDR | 16 | `S2S · Partner · SDR/AE no book` | "still time to schedule a hiring call **(CS)**" |
| Partner Customer Success | 16 | `S2S · Partner · CS no book` | **nothing** |
| Newsletter | 13 | `S2S · Newsletter · Welcome` | `S2S · Newsletter · Welcome` |

The Customer Success case was run twice on separate contacts and received
nothing both times.

## Findings

### 1. Candidate ETS branching does not exist — ERROR

All three candidates — 6–12 months, less than 3 months, and already separated —
received the byte-same legacy email, "%FIRSTNAME%, next step: book your
20-minute intro call". None of the seven `cand-journey-*` campaigns that
`docs/EMAIL_CAMPAIGNS.md` §1 specifies were sent to anyone.

The candidate apply automation is sending one unconditional campaign. The
If/Else on `ETS_WINDOW` is either absent or never matches.

### 2. The already-separated path sends a Calendly push — ERROR

This is the most damaging one. Already-separated applicants are supposed to get
`cand-journey-separated-onedone` and, per the spec, **never** a Calendly link.
The website already handles its side correctly: it suppresses the Calendly
popup and shows the one-and-done confirmation. The automation then emails them
"next step: book your 20-minute intro call" anyway, pointing at Patrick's
booking page, and contradicts what the site just told them.

### 3. Partner role branching sends the wrong campaign — ERROR

A lead whose `HIRING_ROLES` is `SDR / BDR` received an email subject-lined
"still time to schedule a hiring call **(CS)**". A lead whose role is
`Customer Success` received nothing at all, across two separate runs.

That subject matches no template in `emails/templates/manifest.json` — the
closest provisioned campaign is `S2S · Partner · CS no book`, whose subject is
"%FIRSTNAME%, schedule a hiring call (Customer Success)". **The partner
automations send hand-edited campaigns that are not the ones this repo
provisions**, so changes to `emails/templates/` do not reach partner leads.

### 4. AC form 11 discards four fields the website posts — ERROR

ActiveCampaign drops any `field[N]` posted to a form that does not declare
field N. Comparing what the site posts against what each live form embed
declares:

| AC form | Site posts | Form declares | Dropped |
| --- | --- | --- | --- |
| 11 Military Application | 5, 32, 36, 37, 38, 39 | 5, 32 | **36, 37, 38, 39** |
| 16 Partner Inquiry | 34, 35, 36, 37, 38, 39 | all | none |
| 13 Home Page Group | 36 | none | **36** |

Form 16 was rebuilt by hand in commit `8645530` and is the only form carrying
the full set. Form 11 never got the same treatment.

Confirmed by controlled experiment rather than inference. Three contacts opted
into the newsletter with `field[37]=Yes`:

- via form 16 → newsletter welcome **arrived**
- via form 13 → newsletter welcome **arrived**
- via form 11 → newsletter welcome **never arrived**

So on the candidate form:

- `JOURNEY_SEGMENT` (39) is lost, which is very likely why finding 1 looks the
  way it does
- `NEWSLETTER_OPTIN` (37) is lost — candidate newsletter consent is silently
  discarded
- `SMS_OPTIN` (38) is lost — **candidate SMS consent is never recorded**, so the
  two active Candidate SMS automations have no consent to gate on
- `WEBSITE_SOURCE` (36) is lost, so candidate attribution is blank

The SMS one is worth separate attention: the consent checkbox is being collected
from users and thrown away, which leaves no record that consent was ever given.

### 5. Partner and newsletter mail sends from an undeclared address — WARN

Delivered partner and newsletter email came from `ceo@service2software.org`.
The manifest declares `david@service2software.org` for partner and
`dave@service2software.org` for newsletter, and the warmed-sender list in
`docs/EMAIL_CAMPAIGNS.md` names neither `ceo@` nor `david@`. Candidate mail
correctly used `recruiting@`.

Minor related inconsistency: `newsletter-welcome` is sent as "David Hester" but
signed by Allie Medawar in the body, and `newsletter-story` is sent from `dave@`
but signed `david@`. Left alone — that is a copy decision, not a wiring bug.

### 6. Duplicate campaign — FIXED

`cand-journey-lt3-booked` built byte-identical output to
`candidate-ineligible-timing` under the same subject, and both were provisioned
as separate AC messages (49 and 69) and campaigns (47 and 72). `journey-map`
only ever referenced the ineligible branch.

It also broke the provisioner's fallback path: `find_message_by_subject` matches
on subject, so if the state file were ever regenerated both keys would collapse
onto one message and both campaigns would send the same body.

Fixed in the repo. **AC message 49 and campaign 47 still exist and must be
archived by hand** — they are recorded under `retired` in
`emails/ac-provision-state.json`.

### 7. Newsletter greeted subscribers "Hi ," — FIXED

Form 13 collects an email address only, so `%FIRSTNAME%` resolved to an empty
string in the delivered welcome email. Both newsletter templates now use a
name-free greeting.

### 8. What passed

- The PNG wordmark rendered in all six delivered emails, and is present in all
  26 source templates inside an `<img>` with alt text.
- Every link in every template resolves (11 unique URLs, including both Calendly
  pages and all three Pre-Core portal URLs).
- `%FIRSTNAME%` resolved correctly for every named lead; no unresolved merge
  tags went out.
- The delivered newsletter welcome matches its repo template apart from AC's
  appended footer, so the provisioning pipeline itself works.
- All five site form paths post to the right AC form with the right
  `WEBSITE_SOURCE`, and the site's journey-segment assignment is correct for
  every ETS answer and role.

## Blocker: the AC API is blocked at the edge, not rejecting the key

Every path under `/api/*` returns HTTP 403 with a zero-byte Cloudflare response:

| Probe | Result |
| --- | --- |
| `GET /api/3/users/me` with the key | 403, empty |
| `GET /api/3/users/me` with no key | 403, empty |
| `GET /api/3/zzz-does-not-exist` | **403, empty** |
| `POST /admin/api.php` (v1) | 403, empty |
| `POST /proc.php` | 200 |
| `GET /f/11`, `/f/16`, `/f/13` | 200 |

The third row is the diagnostic one. A path that does not exist should return
404; it returns the same empty 403 as everything else, so requests are being
refused before they reach ActiveCampaign. This is **not** a bad or missing
key — `ACTIVECAMPAIGN_API_KEY` is present and 72 characters. Public endpoints on
the same host, from the same egress IP, work fine.

Egress IP this run: `13.222.72.142`. Earlier runs saw `52.73.250.138`,
`3.233.180.130`, and `34.233.103.205`, so per-IP allowlisting will not hold.

To unblock, in ActiveCampaign under **Settings → Developer**, check whether API
access is restricted to an IP allowlist, and either clear it or add the cloud
egress range. Regenerating the key alone will not help — the current key is
never being evaluated.

## Fix list

Cannot be done from here while the API is blocked. In dependency order:

1. **Add fields 36, 37, 38, 39 to form 11 and field 36 to form 13.** Nothing
   else in the candidate journey can work until the form stops discarding them.
   Once the API is reachable, `python3 scripts/provision_ac_campaigns.py` does
   this automatically by cloning the definitions from form 16, verifies the
   write stuck, and exits non-zero if it did not.
2. **Rebuild the candidate apply automation** with the If/Else on `ETS_WINDOW`
   from `docs/EMAIL_CAMPAIGNS.md` §1, and confirm the separated branch sends
   `S2S · Candidate · Separated one-and-done` and nothing else.
3. **Repoint the partner automations** at the provisioned
   `S2S · Partner · …` campaigns, and fix the role If/Else so SDR/AE and
   Customer Success reach their own branches.
4. **Reconcile senders** — decide whether partner and newsletter mail should
   come from `ceo@`, and make the manifest and the warmed-sender list agree with
   the answer.
5. **Archive AC message 49 and campaign 47** (the retired duplicate).
6. **Re-run both scripts.** `scrub_ac_automations.py` exits non-zero while any
   error remains, so it can gate a deploy.

Still not verifiable without the API or a real booking, and left for a manual
pass: the two Calendly booked-tag automations, and the post-call Pre-Core portal
automation on `cand-initial-call-completed`.

## Test contacts

Eight contacts named `Scrub …` at `@emalupe.com` were created through the live
forms. They are real deliverable mailboxes, so no bounces were generated, and
the SMS-consent cases used the reserved `+1-555-01xx` fictional range so no
handset could be texted. Delete them before go-live; they will also have synced
to Salesforce.
