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
3. MCP API keys are user-scoped. One key works for every SparkLaunch project the caller can access; all campaign work targets whichever project is selected per request.
4. Select the target project on every MCP tool call by sending the `X-SparkLaunch-Project-Id: <project_id>` header. Tools that accept an explicit `project_id` argument override the header for that call.
5. Mint the user-scoped key with `POST /api/mcp/auth/api-keys?token=<JWT>`. To create a brand-new SparkLaunch project from an MCP client, call the `projects.create` MCP tool and put the returned id in `X-SparkLaunch-Project-Id` on follow-up calls.
6. Do not ask the user to sign in if they already have (or can generate) an API key.
7. Use login URL fallback only when the user cannot provide or create an API key.

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
7. For founder launch workflows that require a persisted QR theme or a branded capture campaign, prefer the verified REST route family: `PUT /api/golinks/projects/{project_id}/qr-theme`, `POST /api/golinks/projects/{project_id}/campaigns`, and `POST /api/golinks/projects/{project_id}/campaigns/{campaign_id}/qr`.

## Standard Workflow
1. Confirm destination URL or capture objective.
2. If the workflow is a founder launch flow, prefer a capture campaign plus branded QR rather than a redirect-only campaign so the output creates measurable demand signals.
3. Create campaign with `campaign_create` or the REST campaign route.
4. Create shortlink with `shortlink_create` when a shortlink is part of the ask.
5. Generate QR with `qr_generate` or the REST campaign QR route.
6. Ingest leads with `lead_capture_ingest` when capture payload is available.
7. Inspect outcomes with `campaign_stats`.
8. Hand off to launch-signal review or CRM follow-up when the founder goal is traction proof rather than asset creation alone.
9. Only run `shortlink_rotate`, `campaign_pause`, or `campaign_archive` when explicitly requested.

## Output Contract
Always report:
- `campaign_id`
- `shortlink_id`
- `qr_id`
- attribution fields `{campaign_id, shortlink_id, utm, referrer, first_touch, last_touch}` when available
- `crm_lead_id` when ingesting leads

## Tool Notes
- `campaign_create` runs inside the project selected for the current request via `X-SparkLaunch-Project-Id` or an explicit `project_id` argument.
- All tools operate only within the selected SparkLaunch project and must reject projects the key's user does not own.
- `qr_generate` should use the default QR theme for the active API key when style args are omitted.
- `qr_generate` returns both `data_url` and raw `image_base64` when generation succeeds.
- When the user needs a branded QR asset tied to a favorite logo and palette, save the QR theme first or pass explicit style fields so the output matches the selected brand.

## Guardrails
1. Validate all destination URLs as absolute `http(s)` URLs.
2. Require `campaigns.read` and `campaigns.write` scopes.
3. Require `lead_payload.email` for lead ingest.
4. Never perform pause/archive without explicit user confirmation.
5. User-facing errors must stay friendly; diagnostics belong in support Slack logs.
6. When the user is trying to prove early traction, prefer capture-oriented flows that produce usable follow-up data instead of vanity redirect assets.
