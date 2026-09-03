---
name: sparklaunch-color-palettes
description: >
  Use when a connected SparkLaunch user needs to generate or inspect project
  color palettes with branding.generate_palette, branding.list_palettes, or
  branding.get_palette. Do not use for generic color advice without a tool call.
---

# SparkLaunch Color Palettes

Generate and inspect private brand palettes through the connected SparkLaunch app.

## Rules

<!-- sparklaunch:connection:start -->
1. Protected SparkLaunch MCP tools are not activated by this Muse Code package because Muse Code does not document the OAuth lifecycle SparkLaunch requires. Never request or accept bearer tokens, API keys, client secrets, authorization codes, or transport headers.
2. If SparkLaunch tools are absent, treat that as the package's intentional protected-auth boundary, not as a completed connection or a server failure. The skills may still provide non-tool planning that the user explicitly requests.
3. If a workflow needs a protected tool, stop before any write and explain that OAuth discovery, secure token storage, refresh, and revocation are not yet supported by this adapter. Never enable the example server with static credentials as a workaround.
4. If an authorization or credential error appears, stop. Do not ask the user to paste anything into Muse settings, headers, the conversation, or repository files.
<!-- sparklaunch:connection:end -->
5. Use `projects.list` when needed, then pass the selected `project_id` to every palette tool. Use `projects.get` to confirm `effective_permissions` includes `branding.write` before generation; explain a plan or role limitation without requesting OAuth reconnection.
6. `branding.generate_palette` is a write and requires a stable `idempotency_key`. Do not retry with a new key after an uncertain result.
7. Use `branding.list_palettes` or `branding.get_palette` to verify saved results.
8. Retain project and palette identifiers only as internal tool-call state. Never repeat them to the user or include identifier/version labels or columns; refer to palettes by name and colors.

## Workflow

1. Confirm the business, audience, desired feeling, and any color constraints.
2. Call `branding.generate_palette` with a concrete prompt and explicit project id.
3. Present the generated options, including primary, secondary, accent, neutral-light, and neutral-dark colors.
4. Use the saved palette id in downstream planning; do not claim favorite status because the current connected tool set does not change favorites.

## Output

Report the palette name, description, creation time, and each color's hex value and feeling. State whether the result was newly generated or retrieved.
