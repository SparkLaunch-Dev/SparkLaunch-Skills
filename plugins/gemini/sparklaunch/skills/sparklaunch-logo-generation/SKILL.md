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

<!-- sparklaunch:connection:start -->
1. Use the OAuth connection managed by Gemini CLI. Never request or accept access tokens, refresh tokens, API keys, client secrets, authorization codes, or transport headers.
2. If the SparkLaunch tools are absent, stop before planning or claiming execution. Ask the user to link or enable the SparkLaunch extension, restart Gemini CLI, and verify the server with `/mcp`.
3. If a protected action returns an OAuth challenge, ask the user to run `/mcp auth sparklaunch`, then retry only after Gemini CLI reports success. Never use a pasted token as a fallback.
4. If authorization is expired or revoked, stop before any write, ask the user to run `/mcp auth sparklaunch` again, and check the target before retrying an uncertain operation.
<!-- sparklaunch:connection:end -->
5. Resolve the project with `projects.list`, then pass `project_id` to `crm.generate_logo`. Use `projects.get` to confirm `effective_permissions` includes `logos.write` before generation; explain a plan or role limitation without requesting OAuth reconnection.
6. Collect business name, design attributes, `prompt_style` (`symbolic`, `geometric`, or `mascot`), and optional selected colors.
7. When supplying `selected_colors`, pass an object keyed only by `primary`, `secondary`, `accent`, `background`, `foreground`, or `neutral`. Each included role is an object such as `{"hex":"#6E4E3A","feeling":"grounded"}`. Never pass an array. To reuse a generated palette, map `neutral_light` to `background` and `neutral_dark` to `foreground`; omit any role that is unknown.
8. Supply a stable `idempotency_key`; never automatically repeat an uncertain generation with a new key.
9. The result contains `logo.file` with a short-lived HTTPS download URL. Do not request, return, or reconstruct raw base64 or data URLs.
10. Retain project and logo identifiers only as internal tool-call state. Never repeat them to the user or include identifier/version labels or columns; refer to the logo by business name and design description.

## Workflow

1. Confirm the design brief.
2. Call `crm.generate_logo` once for the exact brief.
3. Report the saved logo record and surface the returned file promptly before its URL expires.
4. Do not claim the logo was favorited; favorite selection is outside the current connected tool set.

## Output

Report the business name, prompt style, status, and the file name, MIME type, size, URL lifetime, and download reference.
