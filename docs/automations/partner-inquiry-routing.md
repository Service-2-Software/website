# Automation: Partner inquiry routing

**Create at:** Cursor Automations → New

| Setting | Value |
| --- | --- |
| Name | S2S — Partner inquiry routing |
| Trigger | Webhook (preferred) **or** Scheduled every 1 hour |
| Repository | No repository |
| Tools | ActiveCampaign MCP, Salesforce MCP, Send to Slack |
| Visibility | Team Owned |

## Instructions (paste into the automation prompt)

```text
You route Service 2 Software partner / employer inquiries from ActiveCampaign into Salesforce
and notify the partnerships channel.

Context (live AC account):
- Website Partner Inquiry = form id 12. List: Website Partners (id 6).
- Fields: COMPANY (id 35), HIRING_ROLES (id 34).
- Prefer existing tags:
  src-home-partner / src-companies-page, journey-partner, Type: Partner,
  partner-roles-sdr-ae | partner-roles-cs | partner-roles-other,
  Role: SDR-AE | Role: CS | Role: Other,
  Stage: Booked | Stage: No-Book, synced-to-salesforce / created-from-salesforce-* .

On each run:
1. Resolve contact from webhook, or find AC contacts from the last 2 hours on list 6
   / Type: Partner / journey-partner.
2. Ensure Type: Partner, journey-partner, and role tags from HIRING_ROLES
   (SDR/BDR or Account Executive → partner-roles-sdr-ae + Role: SDR-AE;
    Customer Success → partner-roles-cs + Role: CS;
    Multiple/Other → partner-roles-other + Role: Other).
3. Salesforce:
   - Upsert Account by COMPANY when present.
   - Upsert Lead/Contact by email; link to Account when possible.
   - LeadSource = "Website - Partner". Store HIRING_ROLES on Hiring_Roles__c (or nearest).
   - Do not change Opportunity stages.
   - Tag synced-to-salesforce after successful write if missing.
4. Slack: one message per new inquiry (name, email, company, roles, SF ids).
   Prefix "High priority partner" when role is Account Executive or Multiple/Other.
5. Idempotent: skip Slack if this email was already notified in the last 24 hours
   (Memories keyed by email if enabled).
6. Stop clearly on MCP auth errors. Never dump secrets.
```

## ActiveCampaign companion

On form **Partner Inquiry** submit (if not already):

1. Add to list Website Partners
2. Apply `Type: Partner`, `journey-partner`, page source + role tags
3. Webhook → this Cursor automation URL
