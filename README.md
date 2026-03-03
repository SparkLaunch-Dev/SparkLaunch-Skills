# SparkLaunch Skills

This repository contains reusable Codex skills for SparkLaunch product and operations workflows.

## Purpose

Skills provide consistent, high-quality execution patterns so agents can:

- follow approved workflows
- enforce product and security constraints
- produce predictable outputs across teams

## Core Strategy

1. Keep skills focused on repeatable, high-leverage workflows.
2. Encode business constraints directly in the skill instructions.
3. Prefer clear operational sequences over broad narrative guidance.
4. Standardize response quality, error handling, and reporting expectations.

## Skill Design Principles

1. Be explicit about when a skill should trigger.
2. Keep `SKILL.md` concise and task-oriented.
3. Use `references/` for detailed material that should only be loaded when needed.
4. Avoid redundant content across skills; define shared conventions here.
5. Keep each skill deterministic where possible (clear order of operations and required outputs).

## Required Skill Structure

Each skill should include:

- `SKILL.md` with:
  - YAML frontmatter: `name`, `description`
  - workflow and guardrails
  - output expectations
- `agents/openai.yaml` with UI metadata (`display_name`, `short_description`, `default_prompt`)

Optional:

- `references/` for deeper runbooks, schemas, or domain context
- `assets/` for templates and reusable artifacts

## Trigger and Scope Rules

Each skill must define:

- what requests should trigger it
- what requests should not trigger it
- the exact boundary of responsibility

If a request spans multiple skills, apply the minimal set needed to complete the task.

## Quality and UX Standards

Skills should enforce:

- user-friendly messaging
- consistent naming and terminology
- stable IDs and output fields for automation
- concise summaries with actionable next steps

## Error Handling Standards

All skill-guided implementations should align with SparkLaunch policy:

- users receive friendly, non-technical error messages
- full diagnostics are sent to support Slack channels
- internal details (stack traces, secrets, raw infra errors) are never user-facing

## Testing and Validation Standards

Every skill should define the required validation surface:

- happy-path behavior
- permission/scope failures
- validation and internal error paths
- regression checks for key contracts

Use repository-defined linting, type checks, and test suites as quality gates.

## Documentation Standards

Skills should document:

- architecture intent
- data contracts
- scope and entitlement expectations
- change checklist / definition of done

Avoid environment-specific or machine-specific instructions in this repository-level guide.

## Current Skills

- `sparklaunch-sales-crm`
- `sparklaunch-campaigns`
