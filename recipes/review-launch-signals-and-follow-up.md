---
id: recipe-signals-001
title: Review Launch Signals And Follow Up
summary: Pull landing-page performance, review leads, and convert the strongest signals into campaign or CRM actions.
auth: project_scoped_mcp_api_key
surfaces: mcp
outputs: analytics_summary, leads_review, crm_follow_up, campaign_follow_up_optional
---

# Review Launch Signals And Follow Up

## When To Use

Use this recipe after a landing page or campaign has been running and the user wants concrete follow-up actions instead of raw metrics.

## Credentials

- Project-scoped MCP API key with `landing.read`
- Optional `crm.write` and `campaigns.write` when follow-up actions should be created

## User Prompt

`Review the latest launch signals for this project and tell me what needs follow-up right now.`

## Workflow

1. Identify the active landing project with `landing.list_projects` or `landing.get_project`.
2. Pull analytics with `landing.get_analytics`.
3. Pull leads with `landing.get_leads`.
4. If campaigns are part of the workflow, pull campaign performance with `campaign_stats`.
5. Rank the highest-signal leads or experiments.
6. If authorized and useful:
   - create CRM leads with `crm.create_lead`
   - add follow-up notes with `crm.add_lead_note`
   - pause or archive weak campaigns with `campaign_pause` or `campaign_archive`

## Output Contract

Return:

- date window reviewed
- top metrics or trend shifts
- highest-priority leads
- recommended next actions
- any CRM or campaign changes actually made

## Failure Handling

- Keep read-only analysis separate from write actions so a failed CRM write does not erase the signal review.
- If a write scope is missing, return the recommendation without pretending the follow-up was completed.
