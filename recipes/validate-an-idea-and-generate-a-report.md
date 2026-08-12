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
2. Call `validation.create_project` with a stable idempotency key.
3. Call `validation.start_analysis` with a different stable key and `sections="all"` unless the user narrowed scope.
4. Call `validation.get_project` until the record reports completed results. Do not spin or claim completion from a queued state.
5. Summarize market evidence, competitors, TAM/SAM/SOM methodology, citations returned by the tool, the narrowest credible wedge, and unresolved proof gaps.

## Completion Evidence

Record the SparkLaunch project id, validation project id, final status, sections completed, and evidence-backed recommendation. A locally written summary is not proof that a separate downloadable PDF exists; the current ChatGPT tool set does not generate that PDF.
