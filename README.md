# SparkLaunch Skills

This repository contains reusable Codex skills for SparkLaunch workflows.

## Purpose

Skills define consistent, production-safe execution patterns so agents can:

- follow approved operational flows
- enforce product and security constraints
- return predictable outputs across teams

## Shared Strategy

1. Keep each skill focused on high-leverage, repeatable workflows.
2. Encode hard business constraints directly in `SKILL.md`.
3. Prefer deterministic step sequences over broad narrative guidance.
4. Keep prompts and examples production-oriented and endpoint-accurate.

## Common MCP Execution Pattern

1. Start with project-scoped MCP API key authentication for runtime calls, not interactive login.
2. Use the canonical production runtime endpoint `https://sparklaun.ch/api/mcp/`; treat `/api/mcp/server/` and `/api/mcp/campaigns/` as compatibility aliases only.
3. Run MCP session lifecycle in order: `initialize` -> `notifications/initialized` -> tool calls on the same `mcp-session-id`.
4. If session state fails, reinitialize once, then escalate.
5. Return concrete tool outputs (IDs, URLs, base64 payloads) with concise status messaging.

## Global Skill Policies

1. Authentication must be API-key-first for MCP runtime operations.
2. MCP API keys are project-scoped; do not assume one key can access multiple SparkLaunch projects.
3. New SparkLaunch project bootstrap belongs to the app or the control-plane auth flow (`GET /api/mcp/auth/status`, `POST /api/mcp/auth/bootstrap/project`) with a site JWT, not to runtime tool calls.
4. Do not instruct users to perform interactive login when a valid API key path exists.
5. Use login URLs only as fallback recovery when API key issuance is unavailable.
6. Do not include local-machine or localhost operational instructions in this repository.
7. Never brute-force identifiers, tokens, or credentials.
8. User-facing errors must stay friendly; diagnostic details go to support Slack channels.

## Perspective Rules

Skills must be written from the perspective of an external operator who does not know SparkLaunch internals.

1. Avoid internal implementation terms unless strictly required by a tool contract.
2. Do not teach internal data-model details that users do not need to complete tasks.
3. Focus instructions on tool intent, required inputs, expected outputs, and recovery steps.
4. Keep user messaging concrete, brief, and non-technical.

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
- missing scope/permission failures
- validation/internal error paths
- regression checks for critical contracts

## Future Skill Checklist

When adding a new MCP skill:

1. Confirm trigger scope is explicit and narrow.
2. Ensure default prompt is API-key-first and production-endpoint oriented.
3. Ensure tool workflow avoids internal identifier guessing/brute-forcing.
4. Document transport/session expectations (`initialize`, session id reuse).
5. Include error-handling guidance: user-friendly output, Slack diagnostics.
6. Verify naming is descriptive and consistent with existing skill folders.

## Current Skills

- `sparklaunch-sales` for lead, deal, and CRM contact-workspace operations over the canonical SparkLaunch MCP runtime
- `sparklaunch-campaigns`
- `sparklaunch-logo-generation`
- `sparklaunch-color-palettes`
- `sparklaunch-idea-validation`
- `sparklaunch-landing-pages`
- `sparklaunch-projects`
