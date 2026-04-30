---
name: sparklaunch-logo-generation
description: >
  Use when the user needs SparkLaunch AI logo generation through the production
  Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/, specifically
  the crm.generate_logo tool. Do not use for generic branding advice when no MCP
  tool execution is requested.
---

# SparkLaunch Logo Generation

Generate production-ready logo assets through SparkLaunch MCP.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. MCP API keys are user-scoped. One key works for every SparkLaunch project the caller can access; logo generation runs against whichever project is selected per request.
4. Select the target project on every MCP tool call by sending the `X-SparkLaunch-Project-Id: <project_id>` header. Tools that accept an explicit `project_id` argument override the header for that call.
5. Mint the user-scoped key with `POST /api/mcp/auth/api-keys?token=<JWT>`. To create a brand-new SparkLaunch project from an MCP client, call the `projects.create` MCP tool and put the returned id in `X-SparkLaunch-Project-Id` on follow-up calls.
6. Do not ask the user to sign in if they already have (or can create) an API key.
7. Use login URL fallback only when API key creation is unavailable.

## Endpoint and Transport
1. Endpoint: `https://sparklaun.ch/api/mcp/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- store protocol version
- send `notifications/initialized` with the same session headers
- if `initialize` returns `mcp-session-id`, reuse it for `tools/list` and `tools/call`
- if no `mcp-session-id` is returned, treat the runtime as stateless and continue without a session header
4. Treat `initialize` success as necessary but not sufficient. The next tool call can still lose session state.
5. If `Session not found` appears, reinitialize once and retry once.
6. If it repeats and a SparkLaunch JWT is available, switch to the REST fallback: `POST /api/logos/?token=<JWT>` then `POST /api/logos/{logo_id}/generate?token=<JWT>`.
7. If the selected logo will be used in landing pages or QR campaigns, mark it favorite with `POST /api/logos/{logo_id}/favorite?token=<JWT>` before reporting the logo step as complete.

## Standard Workflow
1. Confirm the business name and desired design attributes.
2. Collect optional style/color preferences:
- `prompt_style`: `symbolic`, `geometric`, or `mascot`
- optional `selected_colors` object
3. Call `crm.generate_logo`.
4. If the logo is the chosen launch mark, favorite it before handing control to downstream landing-page or campaign workflows.
5. Return generated outputs to the user.
6. If MCP is degraded, keep the same business name, style, and colors when switching to the REST flow so outputs stay comparable.

## Output Contract
Always report:
- `logo_id`
- `business_name`
- `prompt_style`
- `status`
- `mime_type`
- `image_base64`
- `data_url`
- `is_favorite` when known

## Guardrails
1. Require `logos.write` scope.
2. Never ask the user for workspace IDs, project IDs, or internal ownership IDs.
3. Keep user-facing failures friendly and concise.
4. Treat login URLs as fallback only after API key path is blocked.
5. Do not tell the user a logo is the selected launch logo until it has been favorited or explicitly confirmed through the REST selection route.
