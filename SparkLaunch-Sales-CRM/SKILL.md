---
name: SparkLaunch-Sales-CRM
description: >
  Use when the user wants to test or operate SparkLaunch Sales CRM through the embedded Streamable HTTP MCP
  endpoint at /api/mcp/crm/ (trailing slash required), including migration checks, project-scoped MCP API key
  management, OpenClaw dependency setup, and CRM tool calls such as crm.search_leads, crm.create_lead,
  crm.list_deals, crm.move_deal, crm.log_activity, crm.add_contact_note, and crm.get_dashboard. Do not use for
  generic sales strategy or copywriting with no CRM tool operations.
---

# SparkLaunch Sales CRM

Operate the local SparkLaunch CRM MCP stack safely and verify end-to-end tool behavior from OpenClaw.

## Workflow
1. Confirm local prerequisites:
- Backend API is running (locally on `http://localhost:8000`, production on `https://sparklaun.ch`).
- Embedded MCP endpoint is reachable at `https://sparklaun.ch/api/mcp/crm/` (or `http://localhost:8000/api/mcp/crm/` locally).
2. Reconcile database migration state:
- Run `alembic -c alembic.ini current` and `alembic -c alembic.ini heads`.
- If not at head, run `alembic -c alembic.ini upgrade head`.
- If upgrade fails from legacy `mcp_crm_01` because tables already exist, run `alembic -c alembic.ini stamp head`.
3. Check authentication status:
- `GET /api/mcp/auth/status` — if unauthenticated, present the login URL to the user.
- `GET /api/mcp/auth/login-url` — returns the login URL and step-by-step instructions.
4. Bootstrap auth with API keys:
- `POST /api/auth/login` with email and password to obtain a JWT.
- `POST /api/mcp/projects/{project_id}/api-keys` with Authorization: Bearer JWT.
5. Configure OpenClaw to target `https://sparklaun.ch/api/mcp/crm/` and provide the API key token as bearer auth.
6. Run integration checks:
- `python -m pytest tests/test_crm_mcp_integration.py -q`
7. Run CRM smoke tests in safe order:
- Read first (`crm.get_dashboard`, `crm.search_leads`).
- Write next (`crm.create_lead`, `crm.log_activity`, `crm.add_contact_note`, `crm.move_deal`).
- Read again to verify persisted changes.
8. Summarize outcomes with explicit record IDs and fields changed.

See concrete local commands and test prompts in:
- [references/local-mcp-testing.md](references/local-mcp-testing.md)

## Rules
1. Infer tenant from auth token context; never ask for workspace/user IDs when unnecessary.
2. Perform duplicate checks before creating leads:
- `crm.search_leads(query="<email or company/name>")`
3. Require explicit confirmation for bulk or destructive actions.
4. If entitlement or scope checks fail, stop and explain the exact missing scope/plan capability.
5. **On MCP `401` or `403` — this is your #1 priority recovery action:**
- The 401/403 JSON body already contains `login_url`, `auth_help`, and `mcp_endpoint`.
- **Immediately** present the `login_url` from the error body to the user: **"You need to sign in first. Please open this link: {login_url}"**
- Do NOT just report "FAIL" or "Unauthorized". Always surface the login URL.
- Do NOT attempt to open URLs on the host machine or start a browser from the terminal.
- Wait for the user to confirm they have signed in.
- Then help them create a project MCP API key via `POST /api/mcp/projects/{project_id}/api-keys`.
- Set MCP bearer token to the new key and retry the original request once.
6. For raw Streamable HTTP calls, send `Accept: application/json, text/event-stream` and complete `initialize` then `notifications/initialized`.
7. Report concrete output, not assumptions. Include record IDs in final summaries.
8. Use this MCP server URL by default unless the user provides a different one: `https://sparklaun.ch/api/mcp/crm/` (locally: `http://localhost:8000/api/mcp/crm/`).

## 401 Recovery Template (MANDATORY)
**You MUST follow this flow whenever any MCP call returns 401 or 403. Never just report the error.**

The 401/403 response body looks like:
```json
{
  "error": "invalid_token",
  "error_description": "Authentication required",
  "login_url": "https://sparklaun.ch/?login=1",
  "mcp_endpoint": "https://sparklaun.ch/api/mcp/crm/",
  "auth_help": "Please sign in at https://sparklaun.ch/?login=1 ..."
}
```

Recovery steps:
1. **Read `login_url` from the 401 response body** (it's already there — no extra API call needed).
2. **Present the login URL to the user**: "You need to sign in first. Please open this link in your browser: **{login_url}**"
3. **Wait** for the user to confirm they have signed in.
4. `GET /api/mcp/auth/status?token={JWT}` — confirm authentication and list available projects.
5. `POST /api/mcp/projects/{project_id}/api-keys` — create a fresh MCP API key with required scopes.
6. Update MCP bearer token to the new API key token.
7. Retry the original MCP request once.

**Critical**: Never skip step 2. The user must be told where to sign in.

## Tool Map
- `crm.get_dashboard(view)` for quick connectivity and tenancy checks.
- `crm.search_leads(query, status, limit)` for retrieval and duplicate prevention.
- `crm.create_lead(name, email, company)` for lead creation after duplicate check.
- `crm.list_deals(deal_type, status, limit)` for pipeline/deal verification.
- `crm.move_deal(deal_id, stage_id)` for stage transitions.
- `crm.log_activity(activity_type, subject, content, deal_id, person_id)` for timeline logging.
- `crm.add_contact_note(person_id, note)` for appending notes to an existing contact and logging an activity entry.

## Auth Info Endpoints (REST, no MCP auth required)
- `GET /api/mcp/auth/login-url` — Public. Returns `{login_url, mcp_endpoint, auth_type, instructions}`.
- `GET /api/mcp/auth/status?token=JWT` — Returns `{authenticated, login_url, user_id, projects[], message}`.
- `POST /api/mcp/projects/{project_id}/api-keys` — Authenticated (JWT). Creates project-scoped MCP API key.
