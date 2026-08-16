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
2. If the required SparkLaunch actions are absent from this conversation, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation, select SparkLaunch, and send your request again. If ChatGPT asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge, ask the user to connect or reconnect SparkLaunch, then retry only after it succeeds.
4. `projects.list` and `projects.create` are user-level tools and do not take `project_id`.
5. Pass an explicit `project_id` to `projects.get` and `projects.update`. Do not ask for workspace or user IDs.

## Tools

- `projects.list`: list every project accessible to the connected user.
- `projects.create`: create a private SparkLaunch project.
- `projects.get`: retrieve one accessible project.
- `projects.update`: overwrite supplied fields on one accessible project.

## Workflow

1. Call `projects.list` when the target project is not already unambiguous.
2. If creating a project, require a useful business description, call `projects.create` with the known name and business fields, then retain the returned project id. Project creation automatically queues the included Idea Validation research.
3. Tell the user that the automatic research normally takes 10-15 minutes. Poll `validation.list_projects` with the returned project id at a bounded cadence (about once per minute, for up to 20 minutes). Do not create or start a duplicate initial run with `validation.create_project` or `validation.start_analysis`.
4. Call `projects.get` with that explicit id before edits when the current state matters. Its `effective_permissions` are the plan/role/token intersection for that project; if the required permission is absent, explain the plan/role boundary before proposing or confirming the write.
5. For `projects.update`, use a stable `idempotency_key`. The first call returns a confirmation preview; show it and wait for explicit approval before retrying with the same arguments, key, and `confirmation_token`.
6. Re-read with `projects.get` to verify important updates.

Never change subscription plans through project updates. Never automatically repeat an uncertain write.

## Output

For each project, report `project_id`, `name`, `status`, and `plan`. Include stage, industry, description, entity type, state, and timestamps when present. Present lists as a concise table.
