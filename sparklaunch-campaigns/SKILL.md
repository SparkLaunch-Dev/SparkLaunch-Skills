---
name: sparklaunch-campaigns
description: >
  Use when the user needs to operate SparkLaunch Campaigns + QR/Shortlinks through
  the production Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/,
  including campaign_create, shortlink_create, qr_generate, lead_capture_ingest,
  campaign_stats, campaign_pause, campaign_archive, and shortlink_rotate. Do not use
  for generic marketing advice without MCP operations.
---

# SparkLaunch Campaigns + QR

Operate campaign acquisition workflows with reliable attribution wiring into CRM.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. MCP API keys are project-scoped; all campaign work stays inside the SparkLaunch project bound to that key.
4. If the user needs a new SparkLaunch project first, use the SparkLaunch app or `POST /api/mcp/auth/bootstrap/project` with a site JWT before MCP runtime calls.
5. Do not ask the user to sign in if they already have (or can generate) an API key.
6. Use login URL fallback only when the user cannot provide or create an API key.

## Endpoint and Transport
1. Default endpoint: `https://sparklaun.ch/api/mcp/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- store `protocolVersion`
- send `notifications/initialized` with same session and protocol headers
- if `initialize` returns `mcp-session-id`, reuse it for `tools/list` and `tools/call`
- if no `mcp-session-id` is returned, treat the runtime as stateless and continue without a session header
4. Treat `initialize` success as necessary but not sufficient. The next tool call can still lose session state.
5. If `Session not found` occurs, re-run initialize + notification once and retry.
6. If it still fails, mark MCP as degraded, preserve any read results already collected, and stop instead of looping retries.

## Standard Workflow
1. Confirm destination URL and objective.
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
- `campaign_create` automatically uses API key scope.
- All tools operate only within the SparkLaunch project bound to the current MCP API key.
- `qr_generate` should use the default QR theme for the active API key when style args are omitted.
- `qr_generate` returns both `data_url` and raw `image_base64` when generation succeeds.

## Guardrails
1. Validate all destination URLs as absolute `http(s)` URLs.
2. Require `campaigns.read` and `campaigns.write` scopes.
3. Require `lead_payload.email` for lead ingest.
4. Never perform pause/archive without explicit user confirmation.
5. User-facing errors must stay friendly; diagnostics belong in support Slack logs.
