---
name: sparklaunch-campaigns
description: >
  Use when the user needs to test, operate, or automate SparkLaunch Campaigns + QR/Shortlinks through the
  Streamable HTTP MCP endpoint at /api/mcp/campaigns/ (trailing slash required), including campaign_create,
  shortlink_create, qr_generate, lead_capture_ingest, campaign_stats, campaign_pause, campaign_archive, and
  shortlink_rotate. Also use for Campaigns MCP auth recovery via /api/mcp/auth/login-url?service=campaigns and
  /api/mcp/auth/status?service=campaigns, project-scoped MCP API key setup, migration checks, and attribution
  verification into CRM lead inbox records. Do not use for generic marketing advice with no MCP operations.
---

# SparkLaunch Campaigns MCP

Operate the SparkLaunch Campaigns MCP stack safely and verify end-to-end growth wiring (campaign -> shortlink -> QR -> lead -> CRM).

## Workflow
1. Confirm backend and MCP endpoint availability:
- Backend API is running (`http://localhost:8000` locally or `https://sparklaun.ch`).
- Campaigns MCP endpoint is reachable at `/api/mcp/campaigns/` (trailing slash required).
2. Reconcile migration state before testing:
- Run `alembic -c alembic.ini current` and `alembic -c alembic.ini heads`.
- If behind head, run `alembic -c alembic.ini upgrade head`.
3. Check auth status for Campaigns MCP:
- `GET /api/mcp/auth/login-url?service=campaigns`
- `GET /api/mcp/auth/status?service=campaigns`
4. Bootstrap auth if needed:
- `POST /api/auth/login` for JWT.
- `POST /api/mcp/projects/{project_id}/api-keys` with JWT bearer token.
5. Configure MCP client:
- Endpoint: `https://sparklaun.ch/api/mcp/campaigns/` (local: `http://localhost:8000/api/mcp/campaigns/`).
- Bearer token: project-scoped MCP API key (`slk_mcp_...`).
- Required scopes on the key: `campaigns.read` and `campaigns.write`.
6. Execute tools in safe order:
- Start with `campaign_create`.
- Then `shortlink_create`.
- Then `qr_generate`.
- Then `lead_capture_ingest`.
- Then read checks with `campaign_stats`.
- Use `shortlink_rotate`, `campaign_pause`, and `campaign_archive` only when requested.
7. Summarize with explicit IDs and attribution fields:
- `campaign_id`, `shortlink_id`, `qr_id`, `crm_lead_id`.

See concrete local commands in:
- [references/local-mcp-testing.md](references/local-mcp-testing.md)

## Rules
1. Treat MCP token context as source of truth for project scope.
2. Ensure `owner_workspace_id` matches token project context.
3. Validate destinations as absolute `http(s)` URLs before create/rotate operations.
4. Require explicit user confirmation before pause/archive operations.
5. Treat vanity domains as unsupported unless the backend explicitly enables them.
6. Require `lead_payload.email` for ingest; reject empty or malformed emails.
7. Always report concrete IDs and changed fields after write tools.
8. On any MCP 401/403, run the mandatory recovery flow below immediately.

## 401/403 Recovery (Mandatory)
1. Read `login_url` from the MCP error body.
2. Show the exact link to the user:
- `You need to sign in first. Please open this link: {login_url}`
3. Do not only report "Unauthorized" or "FAIL".
4. Wait for user confirmation they signed in.
5. Check auth with `GET /api/mcp/auth/status?service=campaigns`.
6. Create a fresh key with `POST /api/mcp/projects/{project_id}/api-keys`.
7. Retry the original MCP request once.

## Tool Map
- `campaign_create(name, objective, destination_url, owner_workspace_id, tags[])`
- `shortlink_create(campaign_id, destination_url, slug?, utm_params?, vanity_domain?)`
- `qr_generate(shortlink_id, format, size, foreground_color?, background?, module_style?, eye_style?, include_logo?, use_project_theme?)`
- `lead_capture_ingest(campaign_id, lead_payload)`
- `campaign_stats(campaign_id, window)`
- `campaign_pause(campaign_id)`
- `campaign_archive(campaign_id)`
- `shortlink_rotate(shortlink_id, destination_url, utm_params?)`

`qr_generate` notes:
- Defaults to `use_project_theme=true` so project QR settings are applied when style inputs are omitted.
- Response includes `data_url` plus raw `image_base64`.
