---
name: sparklaunch-sales
description: >
  Use when the user needs to operate SparkLaunch Sales workflows through the production
  Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/server/, including
  crm.get_dashboard, crm.search_leads, crm.create_lead, crm.list_deals,
  crm.move_deal, crm.log_activity, and crm.add_contact_note. Do not use for
  generic sales strategy requests without MCP operations.
---

# SparkLaunch Sales

Operate SparkLaunch Sales tools safely with MCP API keys and predictable MCP workflows.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for MCP calls.
2. API keys are managed in SparkLaunch Profile API key settings.
3. If the user already has a key, never redirect them to a login URL.
4. Use login URL fallback only when user cannot provide or generate an API key.

## Endpoint and Transport
1. Default endpoint: `https://sparklaun.ch/api/mcp/server/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- persist `mcp-session-id` and protocol version
- send `notifications/initialized`
- reuse the same session for `tools/list` and `tools/call`
4. On `Session not found`, re-initialize and retry once; escalate if repeated.

## Standard Workflow
1. Start with read calls (`crm.get_dashboard`, `crm.search_leads`).
2. Perform writes only when requested (`crm.create_lead`, `crm.log_activity`, `crm.add_contact_note`, `crm.move_deal`).
3. Re-read state to verify persisted results.
4. Return concrete IDs and changed fields.

## Guardrails
1. Check for duplicates before creating leads.
2. Stop and explain missing scope/entitlement errors explicitly.
3. Require confirmation for bulk/destructive actions.
4. Never brute-force identifiers or credentials.
5. Keep user-facing errors concise and non-technical; route diagnostics to support Slack logs.
