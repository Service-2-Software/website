# Automation: Military lead triage

**Create at:** Cursor Automations → New

| Setting | Value |
| --- | --- |
| Name | S2S — Military lead triage |
| Trigger | Webhook (preferred) **or** Scheduled every 1 hour |
| Repository | No repository |
| Tools | ActiveCampaign MCP, Salesforce MCP, Send to Slack (optional) |
| Visibility | Team Owned (ops) or Private while testing |

## Instructions (paste into the automation prompt)

```text
You triage new Service 2 Software military applicants from ActiveCampaign into Salesforce.

Context (live AC account):
- Website Military Application = form id 11. List: Website Candidates (id 5).
- Fields: BRANCH (id 5), ETS_WINDOW (id 32).
- Prefer existing tags — do not invent parallel ones:
  src-military-page / src-home-candidate, journey-candidate, Type: Candidate,
  cand-ets-gt12 | cand-ets-6-12 | cand-ets-3-6 | cand-ets-lt3 | cand-ets-separated,
  Tenure: Under 3mo | Tenure: 3-6mo | Tenure: 6-12mo | Tenure: Separated,
  Stage: Booked | Stage: No-Book, synced-to-salesforce / created-from-salesforce-* .

On each run:
1. If a webhook payload is present, use that contact email / ActiveCampaign contact id.
   Otherwise, find contacts created/updated in the last 2 hours on list 5 or with
   Type: Candidate / journey-candidate / src-military-page / src-home-candidate.
2. Ensure tags match ETS_WINDOW (map to cand-ets-* and Tenure:*). Ensure
   Type: Candidate and journey-candidate. Do not remove booking tags.
3. Salesforce:
   - Find Lead or Contact by email.
   - If missing AND not tagged synced-to-salesforce: create Lead with
     LeadSource = "Website - Military", map BRANCH → Branch_of_Service__c (or nearest),
     ETS_WINDOW → ETS_Window__c (or nearest). Status = New / Applied.
   - If present: fill blank Branch/ETS only; never overwrite owner or closed stages.
   - After successful SF write, tag AC contact synced-to-salesforce if absent.
4. No duplicates. Prefer update-by-email. Cap creates at 25/run.
5. Optional Slack: one summary (name, email, branch, ETS, SF id). Skip if nothing changed.
6. Never print API keys. On MCP auth failure, stop with a clear error.
7. If custom field API names are unknown, describe the object first.
```

## ActiveCampaign companion

On form **Military Application** submit (if not already):

1. Add to list Website Candidates
2. Apply `Type: Candidate`, `journey-candidate`, page source tag, ETS tags
3. Webhook → this Cursor automation URL (contact id + email)
