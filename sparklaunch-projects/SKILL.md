---
name: sparklaunch-projects
description: >
  Use when the user needs to view, create, or update SparkLaunch business projects
  through the production Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/,
  specifically the projects.get, projects.list, projects.create, and projects.update
  tools. MCP API keys are user-scoped; select the target project per request by
  sending the X-SparkLaunch-Project-Id header. Do not use for generic startup
  advice when no MCP tool execution is requested.
---

# SparkLaunch Projects

View, create, and update SparkLaunch business projects with a user-scoped MCP key. Select the target project on every tool call with the `X-SparkLaunch-Project-Id: <project_id>` header (or a `project_id` tool argument when the tool accepts one).

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. MCP API keys are user-scoped. One key works for every SparkLaunch project the caller can access; the target project is selected per request.
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
4. Treat `initialize` success as necessary but not sufficient. Some deployments may still lose session state on the next request.
5. If `Session not found` appears, reinitialize once and retry once.
6. If it repeats, mark MCP as degraded. Use only the documented control-plane REST routes for bootstrap or auth discovery; otherwise stop instead of looping retries.

## Available Tools
- `projects.get` - Get details for the project selected via `X-SparkLaunch-Project-Id` (or a `project_id` tool argument)
- `projects.list` - List every SparkLaunch project the caller can access with the current user-scoped MCP key
- `projects.create` - Create a brand-new SparkLaunch project from the MCP client. Returns the new `project_id`; use it in `X-SparkLaunch-Project-Id` on follow-up calls
- `projects.update` - Update project name, description, stage, industry, and other fields on the selected project

## Standard Workflow
1. If the user needs a brand-new SparkLaunch project, call `projects.create` with the project name, one-liner, business description, industry, and stage; then send the returned `project_id` in `X-SparkLaunch-Project-Id` on every follow-up call.
2. If the user wants to inspect an existing project, send `X-SparkLaunch-Project-Id: <project_id>` and call `projects.list` or `projects.get`.
3. Present the selected project summary to the user.
4. To update existing details, call `projects.update` with only the changed fields, keeping the same `X-SparkLaunch-Project-Id` header.
5. Re-read with `projects.get` when the user needs confirmation of the saved state.
6. If runtime MCP is degraded, tell the user the key is valid but the runtime session is unstable.

## Output Contract
For retrieved or updated projects, always report:
- `project_id`
- `name`
- `status`
- `plan`

When available, also report:
- `description`
- `business_description`
- `entity_type`
- `state`
- `stage`
- `industry`
- `one_liner`
- `created_at`
- `updated_at`

For project lists, present as a concise table:
- project_id, name, status, plan, stage, industry

Note that `projects.list` returns every SparkLaunch project the caller can access with the current user-scoped MCP key.

## Stages
- `idea` - Early concept stage
- `mvp` - Building minimum viable product
- `pre_seed` - Pre-seed funding stage
- `seed` - Seed funding stage
- `series_a` - Series A and beyond

## Entity Types
- `LLC` - Limited Liability Company
- `C-Corp` - C Corporation (Delaware)
- `S-Corp` - S Corporation
- `Sole Proprietorship`

## Guardrails
1. Require `projects.write` scope for updates, `projects.read` for viewing.
2. Never ask the user for workspace IDs, internal user IDs, or database identifiers.
3. Keep user-facing failures friendly and concise.
4. Treat login URLs as fallback only after API key path is blocked.
5. Use `projects.create` from the MCP client to bootstrap new SparkLaunch projects; record the returned `project_id` and send it in `X-SparkLaunch-Project-Id` on follow-up tool calls.
6. Plan changes happen through the payments flow, not project updates.
7. Archived projects are excluded from lists unless explicitly requested.
