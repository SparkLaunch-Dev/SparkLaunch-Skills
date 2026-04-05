---
name: sparklaunch-projects
description: >
  Use when the user needs to view or update the SparkLaunch business project already
  bound to their MCP API key through the production Streamable HTTP endpoint at
  https://sparklaun.ch/api/mcp/, specifically the projects.get, projects.list,
  and projects.update tools. If the user needs to start a brand-new SparkLaunch
  project, use the SparkLaunch app or the MCP auth/bootstrap flow instead of
  runtime project tools. Do not use for generic startup advice when no MCP tool
  execution is requested.
---

# SparkLaunch Projects

View and update the SparkLaunch business project already bound to a project-scoped MCP key.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. MCP API keys are project-scoped; runtime project tools only operate on the SparkLaunch project bound to that key.
4. If the user needs to create a brand-new SparkLaunch project, use the SparkLaunch app or `POST /api/mcp/auth/bootstrap/project` with a site JWT before MCP runtime calls.
5. Do not ask the user to sign in if they already have (or can create) an API key.
6. Use login URL fallback only when API key creation is unavailable.

## Endpoint and Transport
1. Endpoint: `https://sparklaun.ch/api/mcp/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- store `mcp-session-id` and protocol version
- send `notifications/initialized` with the same session headers
- reuse that session id for `tools/list` and `tools/call`
4. If `Session not found` appears, reinitialize once and retry once. If it repeats, escalate as session-state infrastructure issue.

## Available Tools
- `projects.get` - Get details for the project bound to the current API key
- `projects.list` - List the project bound to the current API key
- `projects.update` - Update project name, description, stage, industry, and other fields

`projects.create` is not a valid new-project bootstrap path for project-scoped MCP runtime keys. Do not use it to start a new SparkLaunch project.

## Standard Workflow
1. If the user needs a brand-new SparkLaunch project, stop using runtime tools and direct them to the SparkLaunch app or `POST /api/mcp/auth/bootstrap/project` with a site JWT.
2. If the user wants to inspect the current scoped project, call `projects.list` or `projects.get`.
3. Present the current scoped project summary to the user.
4. To update existing details, call `projects.update` with only the changed fields.
5. Re-read with `projects.get` when the user needs confirmation of the saved state.

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

Note that `projects.list` returns only the project bound to the current MCP API key, not every project the user can access in SparkLaunch.

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
5. Do not use `projects.create` with a project-scoped runtime key; bootstrap new SparkLaunch projects through the separate auth/control-plane flow.
6. Plan changes happen through the payments flow, not project updates.
7. Archived projects are excluded from lists unless explicitly requested.
