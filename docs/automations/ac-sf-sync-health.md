# Automation: ActiveCampaign ↔ Salesforce sync health

**Create at:** [cursor.com/automations/new](https://cursor.com/automations/new)

| Setting | Value |
| --- | --- |
| Name | S2S — AC ↔ SF sync health |
| Trigger | Scheduled — daily 07:30 America/Chicago |
| Repository | No repository (or this website repo if you want docs updates) |
| Tools | ActiveCampaign MCP, Salesforce MCP, Send to Slack |
| Visibility | Team Owned |

## Instructions (paste into the automation prompt)

```text
You are a sync health checker for Service 2 Software. Do not mass-create records unless
gaps are clear and low-risk; prefer reporting.

Scope: contacts associated with website forms in the last 48 hours
(Military Application f=11, Partner Inquiry f=12, tags Source: Website Military / Partner).

Steps:
1. List matching ActiveCampaign contacts (email required).
2. For each email, query Salesforce Lead OR Contact by email.
3. Classify:
   - Synced: SF record exists with matching LeadSource or recent create
   - Missing in SF: no Lead/Contact
   - Partial: SF exists but Branch / ETS / Company / Hiring roles blank while AC has values
4. Auto-fix only "Missing in SF" when email + name are present:
   - Create Lead with correct LeadSource and mapped custom fields
   - Cap auto-creates at 25 per run; if more, report overflow and stop creating
5. For "Partial", update blank SF fields from AC values only (never overwrite non-blank).
6. Slack a compact report: synced count, created count, partial-fixed count, overflow,
   and up to 10 example emails for any failures.

Safety:
- Never delete Salesforce or ActiveCampaign records.
- Never change Opportunity stage or Campaign membership.
- If MCP tools are unauthorized, abort with a clear auth error.
```

## Notes

This automation is a safety net when Zapier/native sync lags. If you later enable a
reliable native AC→SF connector, keep this as a **report-only** job (remove step 4).
