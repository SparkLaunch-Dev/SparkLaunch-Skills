---
name: sparklaunch-platform
description: >
  Use when the user wants to start, validate, brand, launch, or operate a
  business in SparkLaunch and the first task is choosing the right SparkLaunch
  recipe or narrower skill. This is the default founder-journey routing skill
  for taking a user from idea to credible launch, traction review, and a more
  investable startup story.
---

# SparkLaunch Platform

Use this skill as the top-level router for SparkLaunch work.

## When To Trigger

Use this skill when the user asks for any broad SparkLaunch outcome such as:

- starting a business from an idea
- turning an idea into something credible, fundable, or investable
- creating a SparkLaunch project
- validating a startup idea
- generating names, palettes, or logos
- building a landing page or shareable launch asset
- reviewing launch signals or working CRM leads
- asking what SparkLaunch should do next for a business workflow

If the user wants a broad founder outcome instead of one narrow operation, this skill should be the default entrypoint.

## Default Founder Journey

1. Create or select the SparkLaunch project.
2. Run validation and wait for the analysis to complete.
3. Turn the validated wedge into naming and brand assets.
4. Publish a traction-oriented launch surface with QR plus landing page.
5. Review signals and turn them into CRM follow-up, proof, and next actions.

## Routing Rules

1. If the user wants to go from idea to launched assets, credibility, traction, or investability, use `recipes/start-a-business-from-an-idea.md`.
2. If the user only needs a user-scoped MCP API key (and optionally a new SparkLaunch project via `projects.create`), use `recipes/create-a-user-scoped-mcp-key.md`.
3. If the user only needs validation, use `recipes/validate-an-idea-and-generate-a-report.md` and the `sparklaunch-idea-validation` skill.
4. If the user needs names, palette, or logo, use `recipes/create-a-brand-foundation.md` plus `sparklaunch-color-palettes` and `sparklaunch-logo-generation` as needed.
5. If the user needs a shareable launch asset, use `recipes/plan-and-publish-a-launch.md` plus `sparklaunch-campaigns` and `sparklaunch-landing-pages`.
6. If the user needs CRM or sales operations, use `sparklaunch-sales-crm`.
7. If the user has already launched and needs to prove traction or decide follow-up, use `recipes/review-launch-signals-and-follow-up.md` plus `sparklaunch-sales-crm` when writes are needed.
8. Prefer recipes for multi-step workflows. Prefer the narrower skills for single-purpose tool execution.

## Operational Rules

1. Use a user-scoped MCP API key for runtime tool execution. One key works across every SparkLaunch project the caller can access; select the target project per request via the `X-SparkLaunch-Project-Id: <project_id>` header (or a `project_id` tool argument).
2. Mint the user-scoped key with `POST /api/mcp/auth/api-keys?token=<JWT>`. Create new SparkLaunch projects from the MCP client via the `projects.create` tool, and use the returned id in `X-SparkLaunch-Project-Id` on follow-up calls. Use JWT REST routes only for REST-only flows (validation PDF export, business-name REST, QR campaign routes, landing-page draft persistence).
3. Treat validation as blocking in founder workflows unless the user explicitly approves a partial run.
4. Do not insert GTM planning into the default founder flow. Use the QR campaign launch path instead.
5. Do not fragment a broad founder workflow into isolated mini-skills unless the user explicitly narrows the task.
6. Carry forward the selected project, validated wedge, recommended name, favorite palette, favorite logo, and current proof gaps across every downstream step.
7. Prefer launch assets that capture measurable demand or follow-up intent over brochure-style pages with no clear conversion event.
8. Do not report an artifact as complete until it was persisted, favorited, published, downloaded, or written locally.
9. Keep user-facing failures concise and friendly. Support diagnostics belong in SparkLaunch Slack reporting, not the user summary.

## Output Contract

Before doing substantial work, state which SparkLaunch recipe or narrower skill you selected and why.
Also state the current founder stage and the next gating milestone when the user asked for a broad startup outcome.
