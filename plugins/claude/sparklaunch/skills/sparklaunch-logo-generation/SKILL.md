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
1. Use the SparkLaunch MCP connection supplied by Claude Code. Never ask the user for credentials, access tokens, refresh tokens, or authorization headers.
2. If the SparkLaunch tools are absent, stop before planning or claiming execution and say: **SparkLaunch isn't available in this Claude Code session. Confirm that the SparkLaunch plugin is installed and enabled, run `/mcp`, and complete the SparkLaunch browser sign-in if prompted. Then reload plugins or start a new Claude Code session and send the request again.**
3. If a SparkLaunch tool returns an OAuth challenge, ask the user to authenticate or re-authenticate from `/mcp`, then retry only after the connection succeeds.
4. If authorization is expired or revoked, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Re-authenticate SparkLaunch from `/mcp`, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
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
