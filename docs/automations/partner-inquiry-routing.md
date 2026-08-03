# Automation: Partner inquiry routing

**Create at:** [cursor.com/automations/new](https://cursor.com/automations/new)

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

Context:
- Website Partner Inquiry posts to ActiveCampaign form f=12.
- Custom fields: Company = field[35], Hiring roles = field[34].
- LeadSource for Salesforce = "Website - Partner".

On each run:
1. Resolve the partner contact from the webhook payload, or find AC contacts from the last
   2 hours with Partner Inquiry / tag "Source: Website Partner".
2. Tag in ActiveCampaign: "Source: Website Partner" and a role tag from field[34]
   (e.g. "Hiring: SDR / BDR").
3. Salesforce:
   - Upsert Account by company name (field[35]) when company is present.
   - Upsert Lead or Contact by email; link to Account when possible.
   - Set LeadSource = "Website - Partner".
   - Store hiring roles on Hiring_Roles__c (or nearest custom field after describe).
   - Do not change existing Opportunity stages; only create a Lead/Contact for new inquiries.
4. Slack: one message per new inquiry with name, email, company, roles, and SF links/ids.
   If the hiring role is "Account Executive" or "Multiple / Other", prefix with "High priority partner".
5. Idempotent: skip Slack if this email was already processed in the last 24 hours (use Memories
   if enabled, keyed by email).
6. Stop clearly on MCP auth errors. Never dump secrets.
```

## ActiveCampaign companion

Automation on form **Partner Inquiry** submit:

1. Tag `Source: Website Partner`
2. Webhook → this Cursor automation URL
3. Notify internal partner list / start partner nurture if you have one
