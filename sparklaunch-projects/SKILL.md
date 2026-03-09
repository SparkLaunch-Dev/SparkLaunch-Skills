---
name: sparklaunch-projects
description: >
  Use when the user needs to create, view, update, or list their business projects
  through the production Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/server/,
  specifically the projects.create, projects.get, projects.list, and projects.update
  tools. Do not use for generic startup advice when no MCP tool execution is requested.
---

# SparkLaunch Projects

Create, view, update, and manage SparkLaunch business projects through MCP.

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

## Available Tools
- `projects.create` - Create a new business project with name, description, and metadata
- `projects.get` - Get project details (defaults to current API key project)
- `projects.list` - List all business projects for the authenticated user
- `projects.update` - Update project name, description, stage, industry, and other fields

## Standard Workflow
1. If the user wants to see existing projects, call `projects.list`.
2. If they need details on a specific project, call `projects.get` with the project ID.
3. To create a new project, gather:
   - Project name (required)
   - Description (recommended)
   - Business description, location, model (optional)
   - Entity type and state (optional, for future incorporation)
   - Stage: idea, mvp, pre_seed, seed, series_a (optional)
   - Industry: tech, healthcare, fintech, etc. (optional)
   - One-liner (optional)
4. Call `projects.create` with the gathered details.
5. Present the created project summary to the user.
6. To update existing details, call `projects.update` with only the changed fields.

## Output Contract
For created or retrieved projects, always report:
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
1. Require `projects.write` scope for creation/updates, `projects.read` for viewing.
2. Never ask the user for workspace IDs, internal user IDs, or database identifiers.
3. Keep user-facing failures friendly and concise.
4. Treat login URLs as fallback only after API key path is blocked.
5. Plan changes happen through the payments flow, not project updates.
6. Archived projects are excluded from lists unless explicitly requested.
