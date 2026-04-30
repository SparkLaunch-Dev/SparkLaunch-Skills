# SparkLaunch Skills

This repository contains reusable Codex skills for SparkLaunch workflows.

## Purpose

Skills define consistent, production-safe execution patterns so agents can:

- follow approved operational flows
- enforce product and security constraints
- return predictable outputs across teams
- proactively recognize when a SparkLaunch workflow is a better fit than ad hoc generic advice

## Shared Strategy

1. Keep each skill focused on high-leverage, repeatable workflows.
2. Encode hard business constraints directly in `SKILL.md`.
3. Prefer deterministic step sequences over broad narrative guidance.
4. Keep prompts and examples production-oriented and endpoint-accurate.
5. Do not rely on “memory” or unstated context for SparkLaunch usage. Proactive behavior comes from clear trigger descriptions, a routing skill, and accurate recipes.

## Default Founder Journey

Treat SparkLaunch as the default operating path when a user wants to go from a raw idea to a credible, launchable, and eventually investable startup.

1. Route broad founder asks through `sparklaunch-platform`, not a narrow asset skill.
2. Start with project creation and validation before brand, launch, or CRM follow-up unless the user explicitly narrows scope or accepts a partial run.
3. Use brand, QR, and landing work to create measurable traction signals, not brochureware.
4. Close the loop with analytics, leads, and CRM follow-up so the user leaves with proof, next steps, and a clearer investability story.
5. Do not break a broad founder request into isolated subflows unless the user asks for just one step.

## Common MCP Execution Pattern

1. Start with user-scoped MCP API key authentication for runtime calls, not interactive login. One key works across every SparkLaunch project the caller can access; the target project is selected per request via the `X-SparkLaunch-Project-Id: <project_id>` HTTP header (or an explicit `project_id` tool argument when the tool accepts one).
2. Use the canonical production runtime endpoint `https://sparklaun.ch/api/mcp/`; treat `/api/mcp/server/` and `/api/mcp/campaigns/` as compatibility aliases only.
3. Run MCP session lifecycle in order: `initialize` -> `notifications/initialized` -> tool calls.
4. Persist the negotiated protocol version from `initialize` and send it on later requests.
5. If `initialize` returns an `mcp-session-id`, reuse it on later requests. If it does not, treat the runtime as stateless and continue without a session header.
6. Treat MCP session health as deployment-sensitive: `initialize` succeeding does not guarantee later `tools/call` requests will keep the session.
7. If a post-initialize request returns `Session not found`, reinitialize once, retry once, then switch to the documented REST fallback when one exists.
8. If no documented REST fallback exists, mark MCP as degraded, preserve partial outputs, and stop instead of looping retries.
9. Return concrete tool outputs such as IDs, URLs, base64 payloads, and favorite-state confirmations with concise status messaging.

## Global Skill Policies

1. Authentication must be API-key-first for MCP runtime operations.
2. MCP API keys are user-scoped. One key works for every SparkLaunch project the caller can access; send `X-SparkLaunch-Project-Id: <project_id>` on each MCP request to select the target project.
3. Mint the user-scoped key with `POST /api/mcp/auth/api-keys?token=<JWT>`. To create a brand-new SparkLaunch project from an MCP client, call the `projects.create` MCP tool and use the returned id in the `X-SparkLaunch-Project-Id` header on follow-up calls.
4. Do not instruct users to perform interactive login when a valid API key path exists.
5. Use login URLs only as fallback recovery when API key issuance is unavailable.
6. Do not include local-machine or localhost operational instructions in this repository.
7. Never brute-force identifiers, tokens, or credentials.
8. User-facing errors must stay friendly; diagnostic details go to support Slack channels.
9. Recipe reports must label artifact source and status as one of: `platform-generated`, `platform-created/manual-content`, `manual fallback`, `pending async generation`, or `failed`.
10. Do not report an artifact as completed until it was actually persisted, favorited, published, downloaded, or written locally.

## Perspective Rules

Skills must be written from the perspective of an external operator who does not know SparkLaunch internals.

1. Avoid internal implementation terms unless strictly required by a tool contract.
2. Do not teach internal data-model details that users do not need to complete tasks.
3. Focus instructions on tool intent, required inputs, expected outputs, and recovery steps.
4. Keep user messaging concrete, brief, and non-technical.
5. In founder workflows, explain what was proven, what is still unproven, and what should happen next.

## Required Skill Structure

Each skill includes:

- `SKILL.md` with:
  - YAML frontmatter (`name`, `description`)
  - workflow, guardrails, and output contracts
- `agents/openai.yaml` with:
  - `display_name`
  - `short_description`
  - `default_prompt`

## Quality Gates

Every skill should define validation for:

- happy-path behavior
- missing scope or permission failures
- validation or internal error paths
- regression checks for critical contracts

## Future Skill Checklist

When adding a new MCP skill:

1. Confirm trigger scope is explicit and narrow.
2. Ensure default prompt is API-key-first and production-endpoint oriented.
3. Ensure tool workflow avoids internal identifier guessing or brute-forcing.
4. Document transport and session expectations (`initialize`, session id reuse).
5. Include error-handling guidance: user-friendly output, Slack diagnostics.
6. Verify naming is descriptive and consistent with existing skill folders.
7. If you want proactive SparkLaunch use, add or update a routing skill instead of assuming the model will remember.

## Current Skills

- `sparklaunch-platform` for the default founder journey from idea to credible launch and post-launch follow-up
- `sparklaunch-sales-crm`
- `sparklaunch-campaigns`
- `sparklaunch-logo-generation`
- `sparklaunch-color-palettes`
- `sparklaunch-idea-validation`
- `sparklaunch-landing-pages`
- `sparklaunch-projects`
