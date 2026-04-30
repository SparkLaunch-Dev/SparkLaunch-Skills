---
name: sparklaunch-idea-validation
description: >
  Use when the user needs to validate a startup idea through the production
  Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/, specifically
  the validation.create_project, validation.start_analysis, validation.get_project,
  and validation.list_projects tools. Do not use for generic business advice
  when no MCP tool execution is requested.
---

# SparkLaunch Idea Validation

Validate startup ideas with AI-powered market analysis, competitor analysis, and TAM/SAM/SOM sizing.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. MCP API keys are user-scoped. One key works for every SparkLaunch project the caller can access; validation reads and analysis runs target whichever project is selected per request.
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
6. If it repeats and a SparkLaunch JWT is available, switch to the REST fallback: `POST /api/validation/projects`, `POST /api/validation/projects/{id}/analyze`, then poll `GET /api/validation/projects/{id}`.
7. When using REST fallback, explain that the analysis becomes asynchronous and may remain `analyzing` for several minutes.
8. REST analyze does not take `sections='all'`; use an empty body or `{ "deep_research": false }`.

## Available Tools
- `validation.create_project` - Create a validation project inside the SparkLaunch project selected for the current request
- `validation.start_analysis` - Run AI analysis (market, competitor, TAM/SAM/SOM)
- `validation.get_project` - Get a validation project with results
- `validation.list_projects` - List validation projects in the selected SparkLaunch project

## Standard Workflow
1. Gather the business idea details from the user:
   - Business name (required)
   - Business description (required)
   - Target market (optional but recommended)
   - Business model (optional)
   - Unique value proposition (optional)
2. Call `validation.create_project` to create the validation project.
3. Call `validation.start_analysis` with sections='all' to run full analysis.
4. Present the results organized by section:
   - **Market Analysis**: Market size, target audience, trends, opportunities, challenges
   - **Competitor Analysis**: Direct/indirect competitors, advantages, market gaps
   - **TAM/SAM/SOM**: Total addressable, serviceable, and obtainable market sizing
5. Translate the result into founder-facing guidance:
   - the narrowest credible wedge
   - what appears most promising
   - what still needs proof before launch or investor outreach
6. If the user wants to see previously created projects, call `validation.list_projects`.
7. If MCP is degraded, use the REST fallback instead of abandoning the workflow when JWT auth is available.
8. In founder workflows, treat validation as blocking. Wait for completion before moving into naming, brand, QR, or landing work unless the user explicitly approves a partial run.

## Output Contract
For created projects, report:
- `validation_project_id`
- `business_name`
- `status`

For analysis results, present clearly:
- Market size estimates with sources
- Key competitors with strengths/weaknesses
- TAM/SAM/SOM figures with methodology
- Citations and data sources
- Recommended wedge for the first launch
- Top proof gaps that still block a stronger investability story

## Analysis Sections
The `sections` parameter for `validation.start_analysis` accepts:
- `all` - Run market analysis, competitor analysis, and TAM/SAM/SOM (default)
- `market` - Market analysis only
- `competitor` - Competitor analysis only
- `tam_sam_som` - TAM/SAM/SOM sizing only

## Validation Project Limits
- Free plan: 3 validation projects per project
- Startup/Growth/Fundraise Pro: Unlimited

## Guardrails
1. Require `validation.write` scope for project creation and analysis, `validation.read` for viewing.
2. Never ask the user for workspace IDs, project IDs, or internal ownership IDs.
3. Keep user-facing failures friendly and concise.
4. Treat login URLs as fallback only after API key path is blocked.
5. When project limit is reached, clearly communicate the limit and suggest upgrading.
6. Analysis may take some time to complete. Communicate this expectation to the user.
7. If a validation route returns `Please enter your full name.`, treat it as a likely generic validation wrapper and re-check request fields before changing the user-facing guidance.
8. Do not describe downstream assets as validated unless the validation project actually completed.
