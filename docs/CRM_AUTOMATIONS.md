# Salesforce + ActiveCampaign automations (S2S)

Playbook for running CRM/marketing automations with **Cursor Automations** +
**MCP**, built around the lead forms already wired on this site.

## What exists today

Website forms POST to ActiveCampaign (`service2software.activehosted.com/proc.php`).
No API keys are embedded in the HTML — only public form IDs.

| Site form | AC form | `u` / `f` | Custom fields |
| --- | --- | --- | --- |
| Military Application | Military Application | 11 | `field[5]` Branch, `field[32]` ETS window |
| Partner Inquiry | Partner Inquiry | 12 | `field[35]` Company, `field[34]` Hiring roles |
| Newsletter | Home Page Group | 13 | — |

After military/partner submits, the site opens a Calendly gate. Lead/CRM data
continues to flow into ActiveCampaign separately from GA4 analytics.

## Target architecture

```text
Website forms ──► ActiveCampaign (source of truth for marketing)
                        │
                        │  Cursor Automation (webhook / schedule)
                        │  + AC MCP + Salesforce MCP
                        ▼
                 Salesforce (ops / pipeline / SkillBridge tracking)
                        │
                        ▼
              Slack digest / follow-up tasks
```

**Recommended ownership**

| System | Owns |
| --- | --- |
| ActiveCampaign | Nurture sequences, tags, lists, email |
| Salesforce | Candidate/partner pipeline stages, ownership, reporting |
| Cursor Automations | Sync checks, triage, digests, exception handling |

Native AC↔Salesforce sync (Zapier / native connector / middleware) can still
handle the bulk create/update path. Cursor Automations are best for **judgment
work**: scoring, routing, drafting outreach, flagging bad data, weekly digests.

## Prerequisites

1. **ActiveCampaign API access**  
   Settings → Developer → API URL + Key for `service2software`.

2. **Salesforce org access**  
   Authenticate the Salesforce CLI (`sf org login web -a s2s-prod`) or enable
   Salesforce hosted MCP + External Client App (OAuth PKCE). Prefer a
   least-privilege integration user.

3. **Cursor MCP** (Desktop / Cloud Agent environment)  
   Copy [`.cursor/mcp.json.example`](../.cursor/mcp.json.example) to
   `.cursor/mcp.json` (gitignored — never commit keys) **or** configure the same
   servers in Cursor Settings → Tools & MCP / Cloud Agent environment secrets.

   - **Salesforce:** official `@salesforce/mcp` (DX MCP). Auth an org first:
     `sf org login web -a s2s-prod`, then point `--orgs` at that alias.
     Alternative: Salesforce hosted MCP + External Client App (OAuth PKCE).
   - **ActiveCampaign:** community MCP `@marcelocorrea/mcp-active-campaign`
     (API v3). Set `ACTIVECAMPAIGN_ACCOUNT_URL` to your AC API base
     (`https://YOUR_ACCOUNT.api-us1.com`, no trailing `/api/3`) and
     `ACTIVECAMPAIGN_API_KEY` from AC → Settings → Developer. Prefer injecting
     these via Cursor / Cloud Agent secrets (env names
     `ACTIVECAMPAIGN_API_URL` + `ACTIVECAMPAIGN_API_KEY`). Or use
     ActiveCampaign’s remote/hosted MCP if your plan exposes one.

4. **Cursor Automations**  
   Create at [cursor.com/automations/new](https://cursor.com/automations/new).
   Enable the Salesforce + ActiveCampaign MCP tools on each automation.
   For lead-event workflows, use a **Webhook** trigger and point an AC
   automation webhook at the Cursor endpoint after save.

## Field mapping (AC → Salesforce)

Suggested Salesforce objects (adjust to your org schema):

### Military Application → Lead (or custom Candidate)

| ActiveCampaign | Salesforce |
| --- | --- |
| Email | `Email` |
| First / Last name | `FirstName` / `LastName` |
| Branch (`field[5]`) | `Branch_of_Service__c` (or equivalent) |
| ETS window (`field[32]`) | `ETS_Window__c` |
| Form = Military Application | `LeadSource = Website - Military` |
| — | `Status = New` / custom stage `Applied` |

### Partner Inquiry → Lead + Account (or Opportunity)

| ActiveCampaign | Salesforce |
| --- | --- |
| Email | Contact / Lead `Email` |
| Name | Contact / Lead name |
| Company (`field[35]`) | `Company` / Account `Name` |
| Hiring roles (`field[34]`) | `Hiring_Roles__c` |
| Form = Partner Inquiry | `LeadSource = Website - Partner` |

### Newsletter

Keep in ActiveCampaign only unless you need Salesforce marketing sync. Tag:
`Newsletter - Home Page Group`.

## Automations to create

Ready-to-paste prompts live in [`docs/automations/`](./automations/):

| Automation | Trigger | Repo | Purpose |
| --- | --- | --- | --- |
| [Military lead triage](./automations/military-lead-triage.md) | Webhook (AC) or hourly | No repo | Score + tag new military applicants; create/update SF Lead |
| [Partner inquiry routing](./automations/partner-inquiry-routing.md) | Webhook (AC) or hourly | No repo | Route partner leads; create SF Lead/Account; Slack notify |
| [Daily pipeline digest](./automations/daily-pipeline-digest.md) | Schedule (weekdays 9am) | No repo | Slack summary of AC + SF pipeline |
| [AC ↔ SF sync health](./automations/ac-sf-sync-health.md) | Schedule (daily) | This website repo optional | Find AC contacts missing in SF (last 48h) |

## ActiveCampaign native setup (recommended companion)

Inside ActiveCampaign, create automations that fire on form submit:

1. **Military Application submitted** → Tag `Source: Website Military` → Add to
   list → Webhook to Cursor (military triage) → Start nurture.
2. **Partner Inquiry submitted** → Tag `Source: Website Partner` → Webhook to
   Cursor (partner routing) → Notify partner-ops list.
3. **Newsletter subscribe** → Add to Home Page Group → Welcome series only.

Keep webhooks idempotent: include contact email + AC contact id in the payload.

## Security

- Store `ACTIVECAMPAIGN_API_KEY` and Salesforce OAuth secrets in Cursor /
  environment secret stores — never in `index.html` or committed JSON.
- Use a Salesforce integration user with CRUD only on Lead/Contact/Account
  fields needed for these flows.
- Webhook endpoints from Cursor Automations require the automation API key on
  POST; do not publish that key.
- Public AC form posts remain `mode: 'no-cors'` to `proc.php` (opaque by design).

## Activation checklist

- [ ] Salesforce CLI auth (`s2s-prod`) or hosted MCP External Client App
- [ ] ActiveCampaign API URL + key in Cursor MCP / cloud secrets
- [ ] MCP servers show Connected in Cursor Settings
- [ ] Create the four Cursor Automations from `docs/automations/`
- [ ] Wire AC form-submit automations → Cursor webhook URLs
- [ ] Dry-run with a test contact; confirm SF Lead + AC tags + Slack message
- [ ] Restrict automation visibility (Private or Team Owned as appropriate)
