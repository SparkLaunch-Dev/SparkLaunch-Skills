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

1. Use ChatGPT-managed OAuth. Never request credentials or authorization headers.
2. If the required SparkLaunch actions are absent from this conversation, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation, select SparkLaunch, and send your request again. If ChatGPT asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge, ask the user to connect or reconnect SparkLaunch, then retry only after it succeeds.
4. Resolve the target with `projects.list`, then pass `project_id` to every validation tool.
5. `validation.create_project` and `validation.start_analysis` are writes; use a distinct stable `idempotency_key` for each exact mutation.
6. Do not retry an uncertain write with a new key. Re-read with `validation.get_project` instead.

## Workflow

1. Gather business name, description, target market, business model, and value proposition.
2. Call `validation.create_project`.
3. Call `validation.start_analysis` with `sections="all"` unless the user chose a narrower section.
4. Re-read with `validation.get_project` and wait for completed results before calling the idea validated.
5. Translate results into the narrowest credible wedge, promising signals, and remaining proof gaps.

The supported sections are `all`, `market`, `competitor`, and `tam_sam_som`.

## Output

Report the validation project id, business name, status, sections generated, market and competitor findings, TAM/SAM/SOM method and figures, cited sources returned by the tool, recommended wedge, and unresolved evidence gaps. Never invent citations or claim completion from a queued or partial state.
