---
title: Connect SparkLaunch
summary: Connect with host-managed OAuth, list accessible projects, and select an explicit project for scoped work.
---

# Connect SparkLaunch

## Outcome

Establish the user-managed SparkLaunch connection and select a project without collecting credentials in the conversation or configuration files.

## Steps

<!-- sparklaunch:connection:start -->
1. Use the OAuth connection managed by Gemini CLI. Never request or accept access tokens, refresh tokens, API keys, client secrets, authorization codes, or transport headers.
2. If the SparkLaunch tools are absent, stop before planning or claiming execution. Ask the user to link or enable the SparkLaunch extension, restart Gemini CLI, and verify the server with `/mcp`.
3. If a protected action returns an OAuth challenge, ask the user to run `/mcp auth sparklaunch`, then retry only after Gemini CLI reports success. Never use a pasted token as a fallback.
4. If authorization is expired or revoked, stop before any write, ask the user to run `/mcp auth sparklaunch` again, and check the target before retrying an uncertain operation.
<!-- sparklaunch:connection:end -->
5. Invoke `projects.list` after the host reports a usable connection.
6. If the authorization browser shows only `403 Forbidden`, do not reuse, refresh, bookmark, or ask the user to edit that URL; start a fresh connection from the current host. A bare 403 is not proof that the account is connected, expired, or revoked.
7. Call `projects.list` again. It returns every project accessible to the connected user.
8. If there is one clear match, select it. Otherwise present a concise table and ask the user to choose.
9. Call `projects.get` for the selected project and retain its `effective_permissions`. Pass the selected `project_id` argument to every project-scoped tool, and do not propose or confirm a write whose required permission is absent.
   Check `connection_permissions` before diagnosing missing access: a list that
   omits the required scope needs renewed host consent; `null` is an unrestricted
   legacy connection. An absent effective permission alone is not proof of a
   plan restriction. Explain a specific plan or role denial using its stated remedy.
10. If the user needs a new project, require a useful business description, call `projects.create` with a stable `idempotency_key`, then retain its returned project id. Creation automatically queues the included Idea Validation research; tell the user it normally takes 10-15 minutes and do not launch a duplicate initial validation.
11. To review or disconnect grants, direct the user to SparkLaunch **Profile > AI Agent Connections**. Warn that an open agent session may continue to show an expired or revoked connection and that SparkLaunch cannot restart the client-owned authorization automatically. Disconnecting is a separate, explicit user action; do not revoke a grant merely to diagnose a tool failure.

## Guardrails

- Never request or display credentials, OAuth codes, refresh tokens, bearer tokens, client secrets, or authorization headers.
- Never depend on a legacy project-selection HTTP header.
- Never invent a project id or expose internal user/workspace ids.
- A successful connection does not prove access to a particular project; `projects.list` is the source of truth.
- An active SparkLaunch grant does not prove that the current host loaded the MCP server into this session.
- Granted OAuth permissions are the maximum authorization. A selected project's plan or the user's project role may further restrict writes; that is not an OAuth reconnection failure.
- Never retry a mutation merely because reconnection succeeded. Read back the target first and reuse the original idempotency key only when a retry is proven necessary.

## Completion Evidence

Report the connected state, selected project name, status, and plan. If connection or project access is still unresolved, name that blocker instead of continuing with scoped writes. Retain identifiers and versions only for internal tool calls; never show their values or labels to the user.
