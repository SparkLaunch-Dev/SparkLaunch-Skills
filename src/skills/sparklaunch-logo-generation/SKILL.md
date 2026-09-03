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
1. Use the standards-based OAuth connection managed by the current host. Never request or accept credentials, bearer tokens, authorization codes, client secrets, or transport headers.
2. If the required SparkLaunch actions are absent, stop before planning or claiming execution. Explain that SparkLaunch is not loaded in this session and direct the user to install or enable this package using the current host's documented flow, then start a fresh session.
3. If a loaded action returns an OAuth challenge, use the current host's documented connect or reconnect flow and retry only after the host reports success. Never use a pasted token as a fallback.
4. If authorization is expired or revoked, stop before any write, reconnect through the current host, and check the target before retrying an uncertain operation.
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
