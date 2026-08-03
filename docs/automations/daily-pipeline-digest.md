# Automation: Daily pipeline digest

**Create at:** Cursor Automations → New

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

Pull (last 24 hours unless noted) from ActiveCampaign using existing tags/lists:
1. Candidates: list Website Candidates (5) or Type: Candidate / journey-candidate
   — include BRANCH + ETS_WINDOW; call out cand-ets-lt3 and cand-ets-separated as hot
2. Partners: list Website Partners (6) or Type: Partner / journey-partner
   — include COMPANY + HIRING_ROLES
3. Newsletter: list Home Page Group (4) / src-newsletter / journey-newsletter — count only
4. Booking: Stage: Booked vs Stage: No-Book counts for candidates and partners

Salesforce:
- New Leads with LeadSource containing "Website"
- Open Leads with no activity in 7+ days (cap 10)
- Exceptions: AC contacts tagged Type: Candidate or Type: Partner in last 48h
  that lack synced-to-salesforce AND have no SF Lead/Contact by email

Post one Slack message with sections:
- Military / candidates (count + up to 5 bullets)
- Partners (count + up to 5 bullets)
- Newsletter signups (count)
- Booked vs no-book
- Salesforce stale leads
- Sync exceptions

If volumes are zero, post a one-line quiet-day message.
Do not invent numbers. If a query fails, name the system.
```
