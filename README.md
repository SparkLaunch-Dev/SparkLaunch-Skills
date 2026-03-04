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

## Global Skill Policies

1. Authentication must be API-key-first for MCP operations.
2. Do not instruct users to perform interactive login when a valid API key path exists.
3. Use login URLs only as fallback recovery when API key issuance is unavailable.
4. Do not include local-machine or localhost operational instructions in this repository.
5. User-facing errors must stay friendly; diagnostic details go to support Slack channels.

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

## Current Skills

- `sparklaunch-sales-crm`
- `sparklaunch-campaigns`
