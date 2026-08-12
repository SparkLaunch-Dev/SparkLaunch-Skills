---
name: sparklaunch-logo-generation
description: >
  Use when a connected SparkLaunch user wants to generate a private logo asset
  with crm.generate_logo. Do not use for generic branding advice without a
  SparkLaunch logo operation.
---

# SparkLaunch Logo Generation

Generate a logo and return its short-lived file reference through the connected app.

## Rules

1. Use ChatGPT-managed OAuth. Never ask for credentials or transport headers.
2. Resolve the project with `projects.list`, then pass `project_id` to `crm.generate_logo`.
3. Collect business name, design attributes, `prompt_style` (`symbolic`, `geometric`, or `mascot`), and optional selected colors.
4. Supply a stable `idempotency_key`; never automatically repeat an uncertain generation with a new key.
5. The result contains `logo.file` with a short-lived HTTPS download URL. Do not request, return, or reconstruct raw base64 or data URLs.

## Workflow

1. Confirm the design brief.
2. Call `crm.generate_logo` once for the exact brief.
3. Report the saved logo record and surface the returned file promptly before its URL expires.
4. Do not claim the logo was favorited; favorite selection is outside the current ChatGPT tool set.

## Output

Report `logo_id`, business name, prompt style, status, and the file name, MIME type, size, URL lifetime, and download reference.
