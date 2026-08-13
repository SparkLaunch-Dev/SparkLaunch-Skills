---
title: Connect SparkLaunch to ChatGPT
summary: Connect with OAuth, list accessible projects, and select an explicit project for scoped work.
---

# Connect SparkLaunch To ChatGPT

## Outcome

Establish the user-managed SparkLaunch connection and select a project without collecting credentials in chat.

## Steps

1. Confirm `projects.list` is callable in the current conversation.
2. If the action is absent, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation, select SparkLaunch, and send your request again. If ChatGPT asks you to connect, complete the SparkLaunch permission screen.**
3. If a new conversation still lacks SparkLaunch actions, tell the user to disable and re-enable or reinstall the SparkLaunch plugin, then open another new conversation. Do not misreport connector absence as an OAuth failure.
4. Invoke `projects.list`.
5. If the loaded action returns an OAuth challenge, ask the user to connect or reconnect the app and wait for completion.
6. Call `projects.list` again. It returns every project accessible to the connected user.
7. If there is one clear match, select it. Otherwise present a concise table and ask the user to choose.
8. Pass the selected `project_id` argument to every project-scoped tool in the rest of the workflow.
9. If the user needs a new project, call `projects.create` with a stable `idempotency_key`, then retain its returned project id.

## Guardrails

- Never request or display credentials, OAuth codes, refresh tokens, or authorization headers.
- Never depend on a legacy project-selection HTTP header.
- Never invent a project id or expose internal user/workspace ids.
- A successful connection does not prove access to a particular project; `projects.list` is the source of truth.
- An active SparkLaunch grant does not prove that ChatGPT loaded the connector into this conversation.

## Completion Evidence

Report the connected state, selected `project_id`, project name, status, and plan. If connection or project access is still unresolved, name that blocker instead of continuing with scoped writes.
