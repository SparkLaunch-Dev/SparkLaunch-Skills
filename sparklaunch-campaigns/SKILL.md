---
name: sparklaunch-campaigns
description: >
  Use when the user needs to operate SparkLaunch Campaigns + QR/Shortlinks through
  the production Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/campaigns/,
  including campaign_create, shortlink_create, qr_generate, lead_capture_ingest,
  campaign_stats, campaign_pause, campaign_archive, and shortlink_rotate. Do not use
  for generic marketing advice without MCP operations.
---

# SparkLaunch Campaigns + QR

Operate campaign acquisition workflows with reliable attribution wiring into CRM.

## Authentication Policy (Mandatory)
1. Use a project-scoped MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. Do not ask the user to sign in if they already have (or can generate) an API key.
4. Use login URL fallback only when the user cannot provide or create an API key.

## Endpoint and Transport
1. Default endpoint: `https://sparklaun.ch/api/mcp/campaigns/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- store `mcp-session-id` and `protocolVersion`
- send `notifications/initialized` with same session and protocol headers
- use same session id for `tools/list` and `tools/call`
4. If `Session not found` occurs, re-run initialize + notification once and retry. If it still fails, report likely upstream session affinity issue and escalate.

## Standard Workflow
1. Confirm destination URL, objective, and workspace/project context.
2. Create campaign with `campaign_create`.
3. Create shortlink with `shortlink_create` (include UTM params when available).
4. Generate QR with `qr_generate`.
5. Ingest leads with `lead_capture_ingest` when capture payload is available.
6. Inspect outcomes with `campaign_stats`.
7. Only run `shortlink_rotate`, `campaign_pause`, or `campaign_archive` when explicitly requested.

## Output Contract
Always report:
- `campaign_id`
- `shortlink_id`
- `qr_id`
- attribution fields `{campaign_id, shortlink_id, utm, referrer, first_touch, last_touch}` when available
- `crm_lead_id` when ingesting leads

## Tool Notes
- `qr_generate` should use project default QR theme when style args are omitted.
- `qr_generate` returns both `data_url` and raw `image_base64` when generation succeeds.

## Guardrails
1. Validate all destination URLs as absolute `http(s)` URLs.
2. Require `campaigns.read` and `campaigns.write` scopes.
3. Require `lead_payload.email` for lead ingest.
4. Never perform pause/archive without explicit user confirmation.
5. User-facing errors must stay friendly; diagnostics belong in support Slack logs.
