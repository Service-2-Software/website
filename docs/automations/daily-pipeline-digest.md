# Automation: Daily pipeline digest

**Create at:** [cursor.com/automations/new](https://cursor.com/automations/new)

| Setting | Value |
| --- | --- |
| Name | S2S — Daily AC + SF pipeline digest |
| Trigger | Scheduled — weekdays 09:00 America/Chicago (adjust as needed) |
| Repository | No repository |
| Tools | ActiveCampaign MCP, Salesforce MCP, Send to Slack |
| Visibility | Team Owned |

## Instructions (paste into the automation prompt)

```text
Produce a weekday morning digest for Service 2 Software ops.

Pull (last 24 hours unless noted):
1. ActiveCampaign
   - New military applicants (form 11 / tag Source: Website Military)
   - New partner inquiries (form 12 / tag Source: Website Partner)
   - Newsletter signups (form 13) — count only
2. Salesforce
   - New Leads with LeadSource containing "Website"
   - Open Leads owned by the team that have no activity in 7+ days (cap at 10)
   - Any Leads with Priority Hot / ETS <3 months if those fields/tags exist

Post one Slack message with sections:
- Military applicants (count + up to 5 bullets: name, branch, ETS)
- Partner inquiries (count + up to 5 bullets: company, roles)
- Newsletter signups (count)
- Salesforce stale leads needing follow-up (up to 5)
- Exceptions: AC contacts from website forms in the last 48h missing a matching SF Lead/Contact

If volumes are zero, still post a one-line "quiet day" message.
Do not invent numbers. If a query fails, say which system failed.
```
