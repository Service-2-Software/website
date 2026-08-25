# Salesforce → ActiveCampaign: Initial Call Completed

Bridges `Lead.Initial_Call_Completed__c` to ActiveCampaign field
`INITIAL_CALL_COMPLETED` (id **41**) **without** the ActiveCampaign for
Salesforce app. AC automation **18** then sends the Pre-Core portal email
(once `cand-precore-email-sent` is wired as the resend guard).

```
Lead.Initial_Call_Completed__c = true
        ↓  record-triggered Flow (async)
Apex ActiveCampaignInitialCallAction
        ↓  Named Credential callout
AC field 41 = true  (stored as ||true||)
        ↓
Automation 18 → Pre-Core email → tag cand-precore-email-sent
```

> **Status (2026-08-18):** live in **production** (`prod`) and the
> **`s2s-flowdev2` sandbox**. Flipping a Lead’s `Initial_Call_Completed__c` to
> true sets AC field 41 to `||true||` and the Pre-Core email sends once.
> Re-triggering does **not** resend. Note: a production deploy of the Flow
> leaves it **Draft** until activated via Tooling API (see §1).

## 1. Deploy Apex + Flow

The tracked manifest deploys the Apex + Flow but **not** the Named Credential
(the key must not live in the repo). From `salesforce/` with
[Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli):

```bash
cd salesforce
# sandbox (already done):
sf project deploy start --manifest manifest/package.xml --target-org s2s-flowdev2 \
  --test-level RunSpecifiedTests --tests ActiveCampaignInitialCallActionTest

# production:
sf project deploy start --manifest manifest/package.xml --target-org prod \
  --test-level RunSpecifiedTests --tests ActiveCampaignInitialCallActionTest

# Production deploys the Flow as Draft — activate version 1:
DEF_ID=$(sf api request rest "/services/data/v67.0/tooling/query/?q=SELECT+Id+FROM+FlowDefinition+WHERE+DeveloperName='Lead_Initial_Call_Completed_to_AC'" --target-org prod | python3 -c "import sys,json;print(json.load(sys.stdin)['records'][0]['Id'])")
sf api request rest "/services/data/v67.0/tooling/sobjects/FlowDefinition/$DEF_ID" --target-org prod --method PATCH --body '{"Metadata":{"activeVersionNumber":1}}'
```

Or activate in Setup → Flows → **Lead Initial Call Completed to AC** → Activate.

Do **not** `--source-dir force-app`: that would try to deploy the password-less
`ActiveCampaign_API.namedCredential-meta.xml` and fail (“A password is required”).

## 2. Create the Named Credential with the API key (per org)

The Named Credential can’t be committed with its password. Create it once per
org, either in the UI or by deploying a one-off metadata file from **outside**
the repo with the key injected from `.env`:

```bash
# scratch copy outside the repo, key pulled from .env, then deleted
python3 - <<'PY'
from pathlib import Path
import html, os
env={}
for line in Path('.env').read_text(encoding='utf-8-sig').splitlines():
    if '=' in line and not line.strip().startswith('#'):
        k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
d=Path('/tmp/ac_nc/force-app/main/default/namedCredentials'); d.mkdir(parents=True,exist_ok=True)
Path('/tmp/ac_nc/sfdx-project.json').write_text('{"packageDirectories":[{"path":"force-app","default":true}],"sourceApiVersion":"62.0"}')
(d/'ActiveCampaign_API.namedCredential-meta.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <allowMergeFieldsInBody>false</allowMergeFieldsInBody>
    <allowMergeFieldsInHeader>true</allowMergeFieldsInHeader>
    <generateAuthorizationHeader>false</generateAuthorizationHeader>
    <label>ActiveCampaign API</label>
    <endpoint>{html.escape(env["ACTIVECAMPAIGN_API_URL"].rstrip("/"))}/api/3</endpoint>
    <principalType>NamedUser</principalType>
    <protocol>Password</protocol>
    <username>api</username>
    <password>{html.escape(env["ACTIVECAMPAIGN_API_KEY"])}</password>
</NamedCredential>''')
print('wrote temp NC')
PY
sf project deploy start --source-dir /tmp/ac_nc/force-app --target-org s2s-flowdev2 --test-level NoTestRun
rm -rf /tmp/ac_nc
```

UI equivalent — Setup → **Named Credentials** → **ActiveCampaign API**:

| Setting | Value |
| --- | --- |
| URL | `https://service2software.api-us1.com/api/3` |
| Identity Type | Named Principal |
| Authentication Protocol | Password Authentication |
| Username | `api` (dummy; unused) |
| Password | ActiveCampaign API key (same as `ACTIVECAMPAIGN_API_KEY`) |
| Generate Authorization Header | **Unchecked** |
| Allow Merge Fields in HTTP Header | **Checked** |

Apex sends `Api-Token: {!$Credential.Password}`.

## 3. Flow (shipped as metadata)

`Lead_Initial_Call_Completed_to_AC` deploys with the package — no manual
building required. It is a record-triggered (create/update, after-save) Lead
flow with:

- Entry: `Initial_Call_Completed__c = TRUE AND NOT ISBLANK(Email)`, only when
  the record newly meets the criteria
- An **AsyncAfterCommit** scheduled path (required for the callout) that calls
  Apex `ActiveCampaignInitialCallAction` with `leadId = $Record.Id`

To edit it in the UI: Setup → Flows → **Lead Initial Call Completed to AC**.

## 4. AC automation 18 (done)

Automation **Website - Candidate — Initial Call Completed** (18) now triggers on
**Contact field changes → Initial Call Completed = `||true||`** and sends
`S2S · Candidate · Post-call Pre-Core portal`. Verified: contact entered and the
email sent.

**Re-send protection:** ActiveCampaign will not send a one-time campaign to a
contact who already received it, so re-flipping the field does not resend
(verified — `send_amt` stayed at 1). The provisioned tag `cand-precore-email-sent`
(id 89) is available if you want an explicit belt-and-suspenders If/Else guard;
add it in the UI before the Send and apply it after (API cannot edit automation
graphs).

## 5. Test

### A. Payload only (this repo, no SF)

```bash
set -a && source .env && set +a
python3 scripts/sf_ac_set_initial_call_completed.py allie@service2software.org
```

### B. End-to-end (passed in `s2s-flowdev2` 2026-08-17 and **prod** 2026-08-18)

1. AC contact `allie@service2software.org` exists (id 132).
2. Set the Lead’s `Initial_Call_Completed__c` = true (false→true if already true).
3. AC field 41 becomes `||true||` (~25s later, via async Flow → Apex).
4. Pre-Core email “create your Pre-Core portal account” sends once (campaign 90).
5. Re-triggering the field does not resend (`send_amt` stays at 1).

## Classes

| Class | Role |
| --- | --- |
| `ActiveCampaignService` | HTTP GET contact + upsert field 41 |
| `ActiveCampaignInitialCallAction` | `@InvocableMethod` for Flow |
| `ActiveCampaignInitialCallActionTest` | HttpCalloutMock coverage |

## Notes

- Contact must already exist in AC (same email as the Lead). This path does not create contacts.
- Only `true` is written (Pre-Core send). Clearing the SF checkbox does not clear AC.
- Prior routing guidance avoided the AC managed package and broad Apex→AC usage; this is a **single, explicit** callout scoped to Initial Call Completed.
