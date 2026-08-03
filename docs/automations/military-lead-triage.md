# Automation: Military lead triage

**Create at:** [cursor.com/automations/new](https://cursor.com/automations/new)

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

Context:
- Website Military Application posts to ActiveCampaign form f=11.
- Custom fields: Branch = field[5], ETS window = field[32].
- Marketing source of truth is ActiveCampaign; Salesforce owns pipeline/ops.

On each run:
1. If a webhook payload is present, use that contact email / ActiveCampaign contact id.
   Otherwise, list ActiveCampaign contacts created or tagged in the last 2 hours that
   look like military applicants (form Military Application, or tag "Source: Website Military",
   or presence of Branch / ETS custom fields).
2. For each contact, ensure ActiveCampaign tags:
   - "Source: Website Military"
   - Branch tag from field[5] if present (e.g. "Branch: US Army")
   - ETS urgency tag from field[32]:
     - "ETS: <3 months" or "Already separated" → also tag "Priority: Hot"
     - "3-6 months" → "Priority: Warm"
     - else → "Priority: Nurture"
3. In Salesforce, find Lead (or Contact) by email.
   - If missing: create Lead with LeadSource = "Website - Military", map Branch and ETS
     to the org's custom fields (Branch_of_Service__c / ETS_Window__c or nearest match).
     Set Status to New / Applied.
   - If present: update Branch/ETS if blank or changed; do not overwrite owner.
4. Do not create duplicates. Prefer update-by-email.
5. If Slack is enabled, post one short summary of contacts processed (name, email, branch,
   ETS, SF record id). Skip Slack if nothing changed.
6. Never print API keys. If MCP auth fails, stop and report the error clearly.
7. Be conservative: if a custom field API name is unknown, describe_object / list fields
   first; do not invent destructive updates.
```

## ActiveCampaign companion

Automation on form **Military Application** submit:

1. Tag `Source: Website Military`
2. Webhook → this Cursor automation URL (include contact id + email)
3. Start existing nurture sequence
