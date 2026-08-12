---
name: sparklaunch-projects
description: >
  Use when a connected SparkLaunch user needs to list, create, inspect, or
  update business projects with projects.list, projects.create, projects.get,
  or projects.update. Do not use for generic startup advice without a project
  operation.
---

# SparkLaunch Projects

Manage the user's accessible SparkLaunch projects through the connected app.

## Connection And Scope

1. Use the OAuth connection managed by ChatGPT. Never request credentials or bearer tokens.
2. On an OAuth challenge, ask the user to connect or reconnect SparkLaunch.
3. `projects.list` and `projects.create` are user-level tools and do not take `project_id`.
4. Pass an explicit `project_id` to `projects.get` and `projects.update`. Do not ask for workspace or user IDs.

## Tools

- `projects.list`: list every project accessible to the connected user.
- `projects.create`: create a private SparkLaunch project.
- `projects.get`: retrieve one accessible project.
- `projects.update`: overwrite supplied fields on one accessible project.

## Workflow

1. Call `projects.list` when the target project is not already unambiguous.
2. If creating a project, call `projects.create` with the known name and business fields, then retain the returned project id.
3. Call `projects.get` with that explicit id before edits when the current state matters.
4. For `projects.update`, use a stable `idempotency_key`. The first call returns a confirmation preview; show it and wait for explicit approval before retrying with the same arguments, key, and `confirmation_token`.
5. Re-read with `projects.get` to verify important updates.

Never change subscription plans through project updates. Never automatically repeat an uncertain write.

## Output

For each project, report `project_id`, `name`, `status`, and `plan`. Include stage, industry, description, entity type, state, and timestamps when present. Present lists as a concise table.
