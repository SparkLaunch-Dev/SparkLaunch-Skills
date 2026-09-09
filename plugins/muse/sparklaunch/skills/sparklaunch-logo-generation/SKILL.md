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
1. Protected SparkLaunch MCP tools are not activated by this Muse Code package because Muse Code does not document the OAuth lifecycle SparkLaunch requires. Never request or accept bearer tokens, API keys, client secrets, authorization codes, or transport headers.
2. If SparkLaunch tools are absent, treat that as the package's intentional protected-auth boundary, not as a completed connection or a server failure. The skills may still provide non-tool planning that the user explicitly requests.
3. If a workflow needs a protected tool, stop before any write and explain that OAuth discovery, secure token storage, refresh, and revocation are not yet supported by this adapter. Never enable the example server with static credentials as a workaround.
4. If an authorization or credential error appears, stop. Do not ask the user to paste anything into Muse settings, headers, the conversation, or repository files.
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
