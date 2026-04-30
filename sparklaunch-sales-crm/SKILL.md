---
name: sparklaunch-sales-crm
description: >
  Use when the user needs to operate SparkLaunch Sales and CRM workflows through
  the production Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/,
  including crm.get_dashboard, crm.search_leads, crm.create_lead,
  crm.search_contacts, crm.get_contact_workspace, crm.update_contact,
  crm.add_contact_note, crm.add_lead_note, crm.refresh_contact_summary,
  crm.delete_business_card, crm.ingest_business_card, crm.list_deals,
  crm.move_deal, and crm.log_activity. Do not use for generic sales strategy
  requests without MCP operations.
---

# SparkLaunch Sales CRM

Operate SparkLaunch Sales tools safely with MCP API keys and predictable MCP workflows.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for MCP calls.
2. API keys are managed in SparkLaunch Profile API key settings.
3. MCP API keys are user-scoped. One key works for every SparkLaunch project the caller can access; CRM reads and writes target whichever project is selected per request.
4. Select the target project on every MCP tool call by sending the `X-SparkLaunch-Project-Id: <project_id>` header. Tools that accept an explicit `project_id` argument override the header for that call.
5. Mint the user-scoped key with `POST /api/mcp/auth/api-keys?token=<JWT>`. To create a brand-new SparkLaunch project from an MCP client, call the `projects.create` MCP tool and put the returned id in `X-SparkLaunch-Project-Id` on follow-up calls.
6. If the user already has a key, never redirect them to a login URL.
7. Use login URL fallback only when user cannot provide or generate an API key.

## Endpoint and Transport
1. Default endpoint: `https://sparklaun.ch/api/mcp/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- persist protocol version
- send `notifications/initialized`
- if `initialize` returns `mcp-session-id`, reuse it for `tools/list` and `tools/call`
- if no `mcp-session-id` is returned, treat the runtime as stateless and continue without a session header
4. Treat `initialize` success as necessary but not sufficient. The next tool call can still lose session state.
5. On `Session not found`, re-initialize and retry once.
6. If it repeats, mark MCP as degraded, preserve any successful reads or writes already completed, and stop instead of looping retries.

## Standard Workflow
1. Start with the narrowest read call that gives grounded context:
- `crm.get_dashboard` for pipeline status
- `crm.search_leads` for inbox-style lead lookup
- `crm.search_contacts` or `crm.get_contact_workspace` for relationship work
2. Perform writes only when requested:
- `crm.create_lead`, `crm.move_deal`, `crm.log_activity`
- `crm.add_contact_note` for contact workspace note history
- `crm.add_lead_note` when the record is still a lead rather than a contact
- `crm.update_contact` for direct contact correction, including LinkedIn URL plus richer phone/address/website detail
- `crm.delete_business_card` only when the user explicitly wants the saved card removed
- `crm.ingest_business_card` when a base64 business-card image is available for contact creation or enrichment
3. Treat AI summary generation as operator-controlled:
- business-card intake and note updates do not generate summary content
- use `crm.refresh_contact_summary` only when the user explicitly wants refreshed AI guidance
4. Re-read state with `crm.get_contact_workspace`, `crm.get_contact`, or `crm.get_dashboard` to verify persisted results.
5. Return concrete IDs, changed fields, and any summary-warning state.

## Output Contract

Always report:
- the primary entity id touched (`lead_id`, `contact_id`, or `deal_id`)
- the read used as source of truth
- the write actions actually completed
- the next follow-up recommendation when signals or CRM context justify one
- any summary warning or deferred action that still needs operator approval

## Guardrails
1. Check for duplicates before creating leads.
2. Stop and explain missing scope/entitlement errors explicitly.
3. Require confirmation for bulk/destructive actions.
4. Never brute-force identifiers or credentials.
5. Keep user-facing errors concise and non-technical; route diagnostics to support Slack logs.
6. When using contact-workspace tools, prefer the workspace payload as the source of truth because it includes attachments, activity history, summary state, and richer extracted contact detail.
7. When the user is asking for a broad founder workflow rather than a focused CRM operation, route back to `sparklaunch-platform` instead of treating CRM as the entrypoint.
