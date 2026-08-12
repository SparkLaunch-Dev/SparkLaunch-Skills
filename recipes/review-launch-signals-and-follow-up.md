---
title: Review Launch Signals And Follow Up
summary: Compare measured campaign and landing-page evidence with CRM context before taking a follow-up action.
---

# Review Launch Signals And Follow Up

## Steps

1. Resolve the selected `project_id` and identify the campaign and landing page.
2. Read `campaign_stats` for the requested window.
3. Read `landing.get_analytics` and `landing.get_leads` for the same period where possible.
4. Use `crm.search_leads`, `crm.get_lead_workspace`, `crm.search_contacts`, or `crm.get_dashboard` to ground follow-up in persisted CRM state.
5. Separate configured links/pages, observed views/clicks, captured submissions, persisted CRM records, and actual conversion outcomes.
6. Recommend the narrowest next action supported by that evidence.
7. Perform a CRM write only when the user requests it. Use a stable idempotency key and complete any returned confirmation flow exactly.
8. Re-read the affected workspace to verify persistence.

## Output

Report the analysis window, campaign events, landing views/clicks/submissions, lead records reviewed, CRM actions completed, data gaps, and recommended follow-up. Never infer conversion, revenue, or retention from traffic alone.
