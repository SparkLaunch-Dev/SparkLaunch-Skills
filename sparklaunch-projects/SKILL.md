---
name: sparklaunch-projects
description: >
  Use when a connected SparkLaunch user needs to list, create, inspect, or
  update business projects; invite a project collaborator; or list, add,
  update, assign, complete, cancel, or delete general project tasks with the
  projects.* or tasks.* actions. Do not use for generic startup advice without
  a project or task operation.
---

# SparkLaunch Projects

Manage the user's accessible SparkLaunch projects through the connected app.

## Connection And Scope

1. Use the OAuth connection managed by ChatGPT. Never request credentials or bearer tokens.
2. If the required SparkLaunch actions are absent from this conversation, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation, select SparkLaunch, and send your request again. If ChatGPT asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge, ask the user to connect or reconnect SparkLaunch, then retry only after it succeeds.
4. If a loaded action reports an expired or revoked authorization, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Reconnect SparkLaunch from this AI Agent, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
5. `projects.list` and `projects.create` are user-level tools and do not take `project_id`.
6. Pass an explicit `project_id` to `projects.get`, `projects.update`, `projects.invite_collaborator`, and every `tasks.*` action. Do not ask for workspace or user IDs.

## Tools

- `projects.list`: list every project accessible to the connected user.
- `projects.create`: create a private SparkLaunch project.
- `projects.get`: retrieve one accessible project.
- `projects.update`: overwrite supplied fields on one accessible project.
- `projects.invite_collaborator`: create or reissue one email invitation for an Editor or Owner; only a project owner/admin may confirm it, and access begins only after acceptance.
- `tasks.list`: list private general project tasks and their current versions.
- `tasks.create`: add a private general project task and optionally assign it to an accepted project member by email.
- `tasks.update`: update details or lifecycle status, assign/unassign, complete, or cancel a general task using its current version and exact confirmation.
- `tasks.delete`: permanently delete a general task using its current version and exact confirmation.

## Workflow

1. Call `projects.list` when the target project is not already unambiguous.
2. If creating a project, require a useful business description, call `projects.create` with the known name and business fields, then retain the returned project id. Project creation automatically queues the included Idea Validation research.
3. Tell the user that the automatic research normally takes 10-15 minutes. Poll `validation.list_projects` with the returned project id at a bounded cadence (about once per minute, for up to 20 minutes). Do not create or start a duplicate initial run with `validation.create_project` or `validation.start_analysis`.
4. Call `projects.get` with that explicit id before edits when the current state matters. Its `effective_permissions` are the plan/role/token intersection for that project; if the required permission is absent, explain the plan/role boundary before proposing or confirming the write.
5. For `projects.update`, use a stable `idempotency_key`. The first call returns a confirmation preview; show it and wait for explicit approval before retrying with the same arguments, key, and `confirmation_token`.
6. For `projects.invite_collaborator`, normalize and verify the intended email and Editor/Owner role, use a stable `idempotency_key`, and show the exact project/email/role confirmation preview. Wait for explicit approval before retrying with the same arguments, key, and `confirmation_token`. Never describe the recipient as a collaborator until the returned status is `accepted`; `invited` means acceptance is still pending. Report `delivery_status` separately because a persisted invitation does not prove email delivery.
7. Re-read with `projects.get` to verify important project-field updates.
8. For task work, call `tasks.list` first unless the exact task and current `version` were just returned. These actions manage general project tasks only; do not use them as aliases for CRM or GTM tasks.
9. For `tasks.create`, use a stable `idempotency_key`. If assigning immediately, pass the active project owner or accepted collaborator's email. A pending invitation is not assignable and task assignment never grants project access.
10. For `tasks.update`, pass the exact current `task_id` and `expected_version`, plus only the intended fields. Use `clear_description`, `clear_due_at`, or `unassign` for explicit removal. Show the before/after confirmation preview and wait for approval before retrying with unchanged arguments, key, and token. Re-list after a stale-version response.
11. For `tasks.delete`, show the exact task confirmation preview and wait for approval. Retry only with the unchanged task id, current version, key, and token, then use `tasks.list` to verify absence.

Never change subscription plans through project updates. Never automatically repeat an uncertain write or confirm an invitation, task overwrite, or task deletion on the user's behalf.

## Output

For each project, report `project_id`, `name`, `status`, and `plan`. Include stage, industry, description, entity type, state, and timestamps when present. For invitations, report the project, normalized email, requested role, invitation status, delivery status, and acceptance requirement. For tasks, report `task_id`, title, status, priority, due time, assignee, and version. Present lists as a concise table.
