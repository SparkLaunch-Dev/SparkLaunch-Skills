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
1. Use the OAuth connection managed by ChatGPT or Codex. Never request credentials, bearer tokens, authorization codes, client secrets, or transport headers.
2. If the required SparkLaunch actions are absent, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation with SparkLaunch selected, or enable the SparkLaunch plugin and start a new Codex task. If it is still absent, disable and re-enable or reinstall the SparkLaunch plugin, then start another fresh session. If the host asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge or `insufficient_scope`, ask the user to connect or reconnect SparkLaunch through the host and approve the named missing permissions, then retry only after it succeeds. Existing connections may lack access to newly added tools; a missing grant is not evidence of a plan restriction. Never ask the user to paste a token.
4. If a loaded action reports an expired or revoked authorization, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Reconnect SparkLaunch through the host, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
<!-- sparklaunch:connection:end -->
5. Resolve the project with `projects.list`, then pass `project_id` to `crm.generate_logo`. Use `projects.get` to confirm `effective_permissions` includes `logos.write` before generation; if required access is missing from the connection_permissions list, reconnect through the host and approve it. Explain an explicit plan or role denial using its stated remedy; do not infer that denial from effective permissions alone.
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
