---
name: sparklaunch-idea-validation
description: >
  Use when a connected SparkLaunch user needs to create, analyze, list, or
  inspect idea-validation projects with validation.create_project,
  validation.start_analysis, validation.list_projects, or validation.get_project.
---

# SparkLaunch Idea Validation

Create and review private market, competitor, and TAM/SAM/SOM analysis.

## Rules

<!-- sparklaunch:connection:start -->
1. Use the SparkLaunch MCP connection supplied by Claude Code. Never ask the user for credentials, access tokens, refresh tokens, or authorization headers.
2. If the SparkLaunch tools are absent, stop before planning or claiming execution and say: **SparkLaunch isn't available in this Claude Code session. Confirm that the SparkLaunch plugin is installed and enabled, run `/mcp`, and complete the SparkLaunch browser sign-in if prompted. Then reload plugins or start a new Claude Code session and send the request again.**
3. If a SparkLaunch tool returns an OAuth challenge, ask the user to authenticate or re-authenticate from `/mcp`, then retry only after the connection succeeds.
4. If authorization is expired or revoked, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Re-authenticate SparkLaunch from `/mcp`, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
<!-- sparklaunch:connection:end -->
5. Resolve the target with `projects.list`, then pass `project_id` to every validation tool. Use `projects.get` to confirm `effective_permissions` includes `validation.write` before an additional validation write; explain a plan or role limitation without requesting OAuth reconnection.
6. A newly created SparkLaunch business project automatically queues one included Idea Validation workspace and analysis. Do not create or start a duplicate initial run.
7. `validation.create_project` and `validation.start_analysis` are for an explicitly requested additional or narrowed validation workspace; they are writes and require a distinct stable `idempotency_key` for each exact mutation.
8. Keep the parent SparkLaunch `project_id` and the returned validation workspace `validation_project_id` as separate identifiers. Every `validation.get_project` call requires both.
9. `validation.start_analysis` accepts work into a background queue and returns before research finishes. Poll the returned `validation_project_id`; do not treat the accepted response as completed research.
10. Do not retry an uncertain write with a new key. Re-read with `validation.get_project` instead. A retryable error correlation id is for support and does not prove whether a write persisted.
11. Retain project/workspace identifiers and versions only as internal tool-call state. Never repeat them to the user or include identifier/version labels or columns; refer to the business and validation workspace by their human-readable names.

## Workflow

1. Gather business name, description, target market, business model, and value proposition.
2. If the business project was just created, poll `validation.list_projects(project_id=...)` about once per minute for up to 20 minutes until its automatic validation workspace appears. Retain the returned item `id` as `validation_project_id`, then poll `validation.get_project(project_id=..., validation_project_id=...)` until it is terminal. Research normally takes 10-15 minutes.
3. If the user explicitly requested an additional or narrowed validation, call `validation.create_project`, retain `validation_project.id`, then call `validation.start_analysis` with that `validation_project_id` and `sections="all"` unless the user chose a narrower section.
4. After `validation.start_analysis` returns `analyzing`, poll `validation.get_project` at the returned cadence until status is `completed`, `partial`, or `failed`. A transport timeout does not prove failure; read back before reusing the original key and never retry with a new key.
5. Wait for completed results before calling the idea validated, then translate results into the narrowest credible wedge, promising signals, and remaining proof gaps.

The supported sections are `all`, `market`, `competitor`, and `tam_sam_som`.

## Output

Report the business name, validation status, sections generated, market and competitor findings, TAM/SAM/SOM method and figures, cited sources returned by the tool, citation retrieval timestamps, any freshness warning, recommended wedge, and unresolved evidence gaps. Never invent citations or claim completion from a queued, analyzing, or partial state.
