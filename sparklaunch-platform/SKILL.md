---
name: sparklaunch-platform
description: >
  Use when the user wants to start, validate, brand, launch, or operate a
  business in SparkLaunch and the first task is choosing the right SparkLaunch
  recipe or narrower skill. This is the broad routing skill for founder
  workflows, project bootstrap, idea validation, brand creation, QR campaign
  launch, landing pages, and CRM follow-up.
---

# SparkLaunch Platform

Use this skill as the top-level router for SparkLaunch work.

## When To Trigger

Use this skill when the user asks for any broad SparkLaunch outcome such as:

- starting a business from an idea
- creating a SparkLaunch project
- validating a startup idea
- generating names, palettes, or logos
- building a landing page or shareable launch asset
- reviewing launch signals or working CRM leads
- asking what SparkLaunch should do next for a business workflow

## Routing Rules

1. If the user wants to go from idea to launched assets, use `recipes/start-a-business-from-an-idea.md`.
2. If the user only needs a new project and MCP key, use `recipes/bootstrap-a-project-and-mcp-key.md`.
3. If the user only needs validation, use `recipes/validate-an-idea-and-generate-a-report.md` and the `sparklaunch-idea-validation` skill.
4. If the user needs names, palette, or logo, use `recipes/create-a-brand-foundation.md` plus `sparklaunch-color-palettes` and `sparklaunch-logo-generation` as needed.
5. If the user needs a shareable launch asset, use `recipes/plan-and-publish-a-launch.md` plus `sparklaunch-campaigns` and `sparklaunch-landing-pages`.
6. If the user needs CRM or sales operations, use `sparklaunch-sales-crm`.
7. Prefer recipes for multi-step workflows. Prefer the narrower skills for single-purpose tool execution.

## Operational Rules

1. Use project-scoped MCP runtime auth for runtime tool execution.
2. Use the JWT control-plane bootstrap flow for new SparkLaunch projects and REST-only routes.
3. Treat validation as blocking in founder workflows unless the user explicitly approves a partial run.
4. Do not insert GTM planning into the default founder flow. Use the QR campaign launch path instead.
5. Do not report an artifact as complete until it was persisted, favorited, published, downloaded, or written locally.
6. Keep user-facing failures concise and friendly. Support diagnostics belong in SparkLaunch Slack reporting, not the user summary.

## Output Contract

Before doing substantial work, state which SparkLaunch recipe or narrower skill you selected and why.
