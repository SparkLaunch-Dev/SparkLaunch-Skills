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
1. Protected SparkLaunch MCP tools are not activated by this Muse Code package because Muse Code does not document the OAuth lifecycle SparkLaunch requires. Never request or accept bearer tokens, API keys, client secrets, authorization codes, or transport headers.
2. If SparkLaunch tools are absent, treat that as the package's intentional protected-auth boundary, not as a completed connection or a server failure. The skills may still provide non-tool planning that the user explicitly requests.
3. If a workflow needs a protected tool, stop before any write and explain that OAuth discovery, secure token storage, refresh, and revocation are not yet supported by this adapter. Never enable the example server with static credentials as a workaround.
4. If an authorization or credential error appears, stop. Do not ask the user to paste anything into Muse settings, headers, the conversation, or repository files.
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
