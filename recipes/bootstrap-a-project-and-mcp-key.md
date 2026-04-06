---
id: recipe-bootstrap-001
title: Bootstrap A Project And MCP Key
summary: Create a SparkLaunch project through the JWT control plane and optionally seed the first project-scoped MCP API key.
auth: sparklaunch_jwt, project_scoped_mcp_api_key_optional
surfaces: rest, mcp
outputs: project, mcp_api_key, mcp_session_ready
---

# Bootstrap A Project And MCP Key

## When To Use

Use this recipe when the user needs a brand-new SparkLaunch project before any MCP workflow can begin.

## Credentials

- SparkLaunch JWT
- Optional: no existing MCP key required because this recipe can mint the first one

## User Prompt

`Create a new SparkLaunch project for this business idea and give me a scoped MCP key I can use right away.`

## Workflow

1. Confirm the caller has a SparkLaunch JWT.
2. Discover current projects with `GET /api/mcp/auth/status?token=<JWT>`.
3. If a matching project already exists, stop and ask whether to reuse it instead of creating a duplicate.
4. Create the project with `POST /api/mcp/auth/bootstrap/project?token=<JWT>`.
5. Include `mcp_api_key` in the bootstrap body when the agent should immediately continue into MCP work.
6. Recommended initial scopes for founder-bootstrap flows:
   `projects.read`, `projects.write`, `validation.read`, `validation.write`, `branding.read`, `branding.write`, `logos.write`, `landing.read`, `landing.write`
7. Capture:
   - `project.id`
   - `project.name`
   - `api_key.token` if returned
8. Initialize the MCP session against `/api/mcp/` with the returned key:
   - `initialize`
   - `notifications/initialized`
9. Optionally verify scope and project binding with `projects.get` or `projects.list`.

### Example Bootstrap Body

```json
{
  "name": "Nimbus Ops",
  "one_liner": "AI operations assistant for busy service teams.",
  "business_description": "Nimbus Ops helps service businesses automate intake, scheduling, and customer follow-up.",
  "industry": "operations software",
  "stage": "idea",
  "mcp_api_key": {
    "name": "Founder Bootstrap Key",
    "scopes": [
      "projects.read",
      "projects.write",
      "validation.read",
      "validation.write",
      "branding.read",
      "branding.write",
      "logos.write",
      "landing.read",
      "landing.write"
    ]
  }
}
```

## Output Contract

Return:

- project id and name
- plan tier
- created MCP key prefix and raw token if newly minted
- canonical MCP runtime URL: `/api/mcp/`
- whether MCP session initialization succeeded

## Failure Handling

- If JWT auth fails, stop immediately and ask for a fresh login token.
- If bootstrap returns a user-facing 4xx, relay the platform message without adding stack traces or guessing.
- If bootstrap returns a 5xx, tell the user project creation failed and that support diagnostics were already routed by SparkLaunch.
- Do not fabricate a project or key when creation fails.
