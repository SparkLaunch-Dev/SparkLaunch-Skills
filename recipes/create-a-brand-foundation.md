---
title: Create A Brand Foundation
summary: Generate saved palette and logo options for a selected SparkLaunch project.
---

# Create A Brand Foundation

## Inputs

- Selected `project_id`
- Confirmed business name
- Audience, positioning, desired feeling, and constraints
- Optional palette or logo style preferences

## Steps

1. If the project is not selected, use [connect-sparklaunch-to-chatgpt.md](./connect-sparklaunch-to-chatgpt.md).
2. Call `branding.generate_palette` with a stable idempotency key.
3. Present the saved options and retain the selected palette id.
4. Call `crm.generate_logo` with the chosen business name, attributes, prompt style, optional colors, and a different stable idempotency key.
5. Surface the returned `logo.file` download reference promptly because it expires.
6. Verify saved records with `branding.get_palette` or `branding.list_palettes` when needed.

## Guardrails

- The current ChatGPT tool set does not generate business names or set favorite palette/logo status. Do not claim those actions occurred.
- Never request or reconstruct raw base64 or data URLs.
- A generated option is not automatically the user's selected brand; record the choice explicitly in the handoff.

## Completion Evidence

Report the project id, selected palette id and colors, logo id and status, short-lived file metadata, and any selection step still requiring user judgment.
