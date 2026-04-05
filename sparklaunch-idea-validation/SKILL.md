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
3. MCP API keys are project-scoped; validation reads and analysis runs stay inside the SparkLaunch project bound to that key.
4. If the user needs a new SparkLaunch project first, use the SparkLaunch app or `POST /api/mcp/auth/bootstrap/project` with a site JWT before MCP runtime calls.
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
- `validation.create_project` - Create a validation project inside the SparkLaunch project already bound to the MCP API key
- `validation.start_analysis` - Run AI analysis (market, competitor, TAM/SAM/SOM)
- `validation.get_project` - Get a validation project with results
- `validation.list_projects` - List validation projects in the current project

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
5. If the user wants to see previously created projects, call `validation.list_projects`.

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
