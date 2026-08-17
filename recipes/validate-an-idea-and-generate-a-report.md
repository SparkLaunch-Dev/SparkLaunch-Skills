---
title: Validate An Idea And Summarize The Evidence
summary: Create, analyze, and verify a SparkLaunch validation project through the connected app.
---

# Validate An Idea And Summarize The Evidence

## Inputs

- Selected `project_id`
- Business name and description
- Target market, business model, and value proposition when known
- Requested analysis sections, defaulting to `all`

## Steps

1. Use [connect-sparklaunch-to-chatgpt.md](./connect-sparklaunch-to-chatgpt.md) if the project is not selected.
2. If this business project was just created, do not call `validation.create_project` or `validation.start_analysis`: the included Idea Validation research was queued automatically, and either call would create a duplicate initial run.
3. Poll `validation.list_projects(project_id=...)` about once per minute for up to 20 minutes until the automatic workspace appears. Retain the returned item `id` as `validation_project_id`, then poll `validation.get_project(project_id=..., validation_project_id=...)` until it reports completed or failed. A typical run takes 10-15 minutes.
4. Only when the user explicitly requests an additional or narrowed validation workspace, call `validation.create_project` with a stable idempotency key, retain `validation_project.id`, and call `validation.start_analysis` with that `validation_project_id`, the parent `project_id`, a different stable key, and the requested sections.
5. `validation.start_analysis` returns after queue acceptance. Poll readback until status is `completed`, `partial`, or `failed`. If a write loses its transport response, read back with both identifiers before reusing the original key. Do not repeat it with a new idempotency key or infer failure from the transport alone.
6. Summarize market evidence, competitors, TAM/SAM/SOM methodology, citations returned by the tool, the narrowest credible wedge, and unresolved proof gaps.

## Completion Evidence

Record the SparkLaunch project id, validation project id, final status, sections completed, citation retrieval timestamps, freshness warnings, and evidence-backed recommendation. A locally written summary is not proof that a separate downloadable PDF exists; the current ChatGPT tool set does not generate that PDF.
