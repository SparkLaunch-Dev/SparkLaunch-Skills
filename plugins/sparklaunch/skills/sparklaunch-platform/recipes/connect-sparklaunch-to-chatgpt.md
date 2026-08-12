---
title: Connect SparkLaunch to ChatGPT
summary: Connect with OAuth, list accessible projects, and select an explicit project for scoped work.
---

# Connect SparkLaunch To ChatGPT

## Outcome

Establish the user-managed SparkLaunch connection and select a project without collecting credentials in chat.

## Steps

1. Invoke `projects.list`.
2. If SparkLaunch returns an OAuth challenge, ask the user to connect or reconnect the app and wait for completion.
3. Call `projects.list` again. It returns every project accessible to the connected user.
4. If there is one clear match, select it. Otherwise present a concise table and ask the user to choose.
5. Pass the selected `project_id` argument to every project-scoped tool in the rest of the workflow.
6. If the user needs a new project, call `projects.create` with a stable `idempotency_key`, then retain its returned project id.

## Guardrails

- Never request or display credentials, OAuth codes, refresh tokens, or authorization headers.
- Never depend on a legacy project-selection HTTP header.
- Never invent a project id or expose internal user/workspace ids.
- A successful connection does not prove access to a particular project; `projects.list` is the source of truth.

## Completion Evidence

Report the connected state, selected `project_id`, project name, status, and plan. If connection or project access is still unresolved, name that blocker instead of continuing with scoped writes.
