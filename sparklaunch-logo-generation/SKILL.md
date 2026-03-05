---
name: sparklaunch-logo-generation
description: >
  Use when the user needs SparkLaunch AI logo generation through the production
  Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/server/, specifically
  the crm.generate_logo tool. Do not use for generic branding advice when no MCP
  tool execution is requested.
---

# SparkLaunch Logo Generation

Generate production-ready logo assets through SparkLaunch MCP.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. Do not ask the user to sign in if they already have (or can create) an API key.
4. Use login URL fallback only when API key creation is unavailable.

## Endpoint and Transport
1. Endpoint: `https://sparklaun.ch/api/mcp/server/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- store `mcp-session-id` and protocol version
- send `notifications/initialized` with the same session headers
- reuse that session id for `tools/list` and `tools/call`
4. If `Session not found` appears, reinitialize once and retry once. If it repeats, escalate as session-state infrastructure issue.

## Standard Workflow
1. Confirm the business name and desired design attributes.
2. Collect optional style/color preferences:
- `prompt_style`: `symbolic`, `geometric`, or `mascot`
- optional `selected_colors` object
3. Call `crm.generate_logo`.
4. Return generated outputs to the user.

## Output Contract
Always report:
- `logo_id`
- `business_name`
- `prompt_style`
- `status`
- `mime_type`
- `image_base64`
- `data_url`

## Guardrails
1. Require `logos.write` scope.
2. Never ask the user for workspace IDs, project IDs, or internal ownership IDs.
3. Keep user-facing failures friendly and concise.
4. Treat login URLs as fallback only after API key path is blocked.
