# Salesforce: assign incoming ActiveCampaign website leads

Spec for a Salesforce agent (Flow or Apex). Do **not** install the paid
ActiveCampaign managed package. Do **not** call the ActiveCampaign API.
Only stamp **Record Type** and **Owner** on Leads that already exist.

Prefer a **before-save record-triggered Flow** on Lead. Use **Apex**
(before-insert / before-update, bulk-safe) only if Flow cannot do the
updates cleanly.

## Goal

When a Lead is created from the Service 2 Software website (via
ActiveCampaign), automatically set:

1. The correct Lead Record Type
2. The correct Owner

## Business rules

Three website audiences. Newsletter must **not** be treated as a sales Lead.

| Audience | How they enter ActiveCampaign | Salesforce outcome |
| --- | --- | --- |
| **Candidate** (transitioning service member) | Form 11, list Website Candidates (5) | Candidate record type. Owner = Patrick Gilroy (Recruiting). |
| **Partner** (company hiring) | Form 16, list Website Partners (6) | Partner / company record type. Owner = David Hester. |
| **Newsletter only** | Form 13, list Home Page Group (4) | Do **not** assign a sales record type or sales owner. Skip, or stamp a non-sales type if one exists. |

## Classification (first match that exists in this org)

Inspect **one real candidate Lead and one real partner Lead** before writing
code. Field API names may differ (`Website_Source__c`, `WebsiteSource__c`,
etc.). Map to whatever is actually populated.

Trust **website source first** when it is present.

Website source values the site posts today (`WEBSITE_SOURCE` / AC field 36):

| Value | Audience |
| --- | --- |
| `home-candidate` | Candidate |
| `military-page` | Candidate |
| `home-partner` | Partner |
| `companies-page` | Partner |
| `newsletter` | Newsletter — do not route to sales |

**Candidate if any of:**

- Website source in `home-candidate`, `military-page`
- ETS / separation window populated (`More than 12 months`, `6-12 months`,
  `3-6 months`, `Less than 3 months`, `Already separated`)
- Branch populated (for example `US Army`)
- AC list / tags indicating Website Candidates

**Partner if any of:**

- Website source in `home-partner`, `companies-page`
- Hiring roles populated (`SDR / BDR`, `Account Executive`,
  `Customer Success`, `Multiple / Other`)
- Company name from the partner form
- AC list / tags indicating Website Partners

**Newsletter / skip if:**

- Website source = `newsletter`
- Email-only, no ETS and no hiring roles
- Came from Home Page Group / newsletter list

If both somehow match: use website source. If source is missing, partner
roles/company imply partner; ETS/branch imply candidate.

v1 does **not** split partner owners by hiring role. All partners go to David.

## Record types and owners

Do **not** hard-code 18-character IDs in a way that breaks sandboxes. Prefer:

- RecordType **DeveloperName** via
  `Schema.SObjectType.Lead.getRecordTypeInfosByDeveloperName()`
- Owner via Custom Metadata or a Hierarchy Custom Setting (User Id or
  Username) so prod vs sandbox can differ

Look up in the org:

- Lead record types for “Candidate / Service member” vs “Partner / Company”
- Usernames for **Patrick Gilroy** and **David Hester** (must be active)

If developer names are unclear, ask Allie Medawar
(`allie@service2software.org`).

## When it should run

- Lead **before insert** (Flow: fast field updates / before save)
- Also **before update** if RecordTypeId is still blank (delayed AC sync)
- **Do not** overwrite RecordTypeId or OwnerId if a human already changed
  them. v1: only stamp when RecordTypeId is null **or** still the
  default/master Lead record type, **and** owner is still the default lead
  owner / integration user.

## What not to do

- Do not install ActiveCampaign for Salesforce
- Do not call the ActiveCampaign API
- Do not create Leads; only assign Leads that already exist
- Do not convert Leads
- Do not sync Calendly or send the Pre-Core email (that stays in AC via tag
  `cand-initial-call-completed`)
- Do not process newsletter-only records as sales Leads

## Apex sketch (if not using Flow)

- `LeadAssignmentTrigger` on Lead (before insert, before update)
- Handler class, bulk-safe, no SOQL/DML inside loops
- Query RecordType once; query assignee Users once (or CMDT)
- Tests ≥ 75%, covering:
  - source `home-candidate` → candidate RT + Patrick
  - source `companies-page` → partner RT + David
  - source `newsletter` → not assigned to Patrick or David
  - existing non-default RecordTypeId is left alone
  - bulk 200 mixed leads

## Discovery (do this first)

1. Open a recent website candidate Lead and a partner Lead. List every
   AC-related field (source, ETS, roles, company, tags).
2. Setup → Object Manager → Lead → Record Types. Note Developer Names.
3. Confirm Patrick and David are active users.
4. Confirm how Leads are created (connector, Zapier, web-to-lead). Assignment
   does not care, as long as classification fields are populated.
5. If website source is **not** on the Lead object, stop and add a custom
   field plus mapping, or classify from ETS vs hiring roles. Do not guess.

## Acceptance

- New candidate website Lead → candidate record type, owned by Patrick,
  without a human clicking
- New partner website Lead → partner record type, owned by David
- Newsletter signup does not land on Patrick or David as a sales Lead
- Tests pass; no hardcoded prod-only IDs that break sandbox
