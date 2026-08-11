---
id: recipe-user-mcp-key-001
title: Create A User-Scoped MCP API Key
summary: Mint a single user-scoped MCP API key that works across every SparkLaunch project the caller can access, and select a target project per request via the 'X-SparkLaunch-Project-Id' header.
auth: sparklaunch_jwt, user_scoped_mcp_api_key
surfaces: rest, mcp
outputs: mcp_api_key, mcp_session_ready
---

# Create A User-Scoped MCP API Key

## When To Use

Use this recipe the first time a SparkLaunch user wants an MCP client (Claude Desktop, IDE, custom agent) to call `/api/mcp/`. Minting the key is a one-time, per-user setup step. Once the caller has a key, the same key works for every project they own or collaborate on. Targeting a specific project is a per-request concern solved by a single HTTP header.

## Credentials

- SparkLaunch JWT (from the web login)
- No existing MCP key is required; this recipe creates one

## User Prompt

`Set up MCP for SparkLaunch. Give me a single key I can use across all of my projects.`

## Workflow

1. Confirm the caller has a SparkLaunch JWT.
2. List accessible projects with `GET /api/mcp/auth/status?token=<JWT>`. Use this to confirm which projects the user can target.
3. Mint the MCP API key with `POST /api/mcp/auth/api-keys?token=<JWT>`. Body:
   ```json
   {
     "name": "Claude Desktop",
     "scopes": [
       "projects.read",
       "projects.write",
       "validation.read",
       "validation.write",
       "branding.read",
       "branding.write",
       "logos.write",
       "landing.read",
       "landing.write",
       "campaigns.read",
       "campaigns.write",
       "crm.read",
       "crm.write"
     ]
   }
   ```
   Recommended scopes cover the full founder workflow. Trim the list if the user only needs a subset.
4. Capture:
   - `id` (for later revocation)
   - `token` (the raw `slk_mcp_…` secret — shown only once)
   - `scopes`
5. Initialize the MCP session against `/api/mcp/`:
   - `initialize`
   - `notifications/initialized`
6. For every subsequent tool call, send the target project via the `X-SparkLaunch-Project-Id: <project_id>` header. The same key is reused for every project; the header determines which project the request applies to.
7. To create a new SparkLaunch project from the MCP client, call the `projects.create` tool. Then send the returned project id in the header on follow-up calls.

## Path Status

- User-scoped API key mint: `Verified working`
- MCP runtime session init with a user-scoped key: `Verified working`
- Per-request project header routing: `Verified working`

## Known-Good Transport

1. Treat `POST /api/mcp/auth/api-keys?token=<JWT>` as the only source of truth for minting MCP keys. There is no per-project key mint endpoint.
2. Use MCP `initialize` only to verify that the new key is accepted. Do not treat failure there as a setup failure; reinitialize once and continue.
3. Always attach `X-SparkLaunch-Project-Id` on tool calls that operate on project data. Tools that accept an explicit `project_id` argument override the header for that single call.
4. Reuse the key for every project. Never create a new key per project.

### Example Mint Response Excerpt

```json
{
  "id": 42,
  "name": "Claude Desktop",
  "prefix": "slk_mcp_AbCdEf",
  "token": "slk_mcp_secret_value",
  "scopes": [
    "projects.read",
    "projects.write",
    "validation.read",
    "validation.write",
    "branding.read",
    "branding.write",
    "logos.write",
    "landing.read",
    "landing.write",
    "campaigns.read",
    "campaigns.write",
    "crm.read",
    "crm.write"
  ]
}
```

### Example MCP Request Headers

```
Authorization: Bearer slk_mcp_secret_value
X-SparkLaunch-Project-Id: 123
```

### Example `projects.create` Tool Call

```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tools/call",
  "params": {
    "name": "projects.create",
    "arguments": {
      "name": "Nimbus Ops",
      "one_liner": "AI operations assistant for busy service teams.",
      "business_description": "Nimbus Ops helps service businesses automate intake, scheduling, and customer follow-up.",
      "industry": "operations software",
      "stage": "idea"
    }
  }
}
```

The returned `project_id` is the value to send in `X-SparkLaunch-Project-Id` on subsequent calls.

## Output Contract

Return:

- MCP API key id, prefix, and raw token (shown to the user once so they can paste it into their client)
- Canonical MCP runtime URL: `/api/mcp/`
- Instruction: use `Authorization: Bearer <token>` on every request, and set `X-SparkLaunch-Project-Id: <project_id>` to select the target project
- Whether MCP session initialization succeeded

## Failure Handling

- If JWT auth fails, stop immediately and ask for a fresh login token.
- If key creation returns a user-facing 4xx, relay the platform message without adding stack traces.
- If key creation returns a 5xx, tell the user key creation failed and that support diagnostics were already routed by SparkLaunch.
- If key creation succeeds but MCP session initialization fails, still return the key. Mark the runtime as degraded rather than reporting the entire setup as failed.
- Do not fabricate a key when creation fails.
- To revoke a lost or compromised key, call `POST /api/mcp/auth/api-keys/{id}/revoke?token=<JWT>`.
