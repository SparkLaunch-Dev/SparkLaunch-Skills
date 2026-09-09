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
1. Use the OAuth connection managed by Gemini CLI. Never request or accept access tokens, refresh tokens, API keys, client secrets, authorization codes, or transport headers.
2. If the SparkLaunch tools are absent, stop before planning or claiming execution. Ask the user to link or enable the SparkLaunch extension, restart Gemini CLI, and verify the server with `/mcp`.
3. If a protected action returns an OAuth challenge, ask the user to run `/mcp auth sparklaunch`, then retry only after Gemini CLI reports success. Never use a pasted token as a fallback.
4. If authorization is expired or revoked, stop before any write, ask the user to run `/mcp auth sparklaunch` again, and check the target before retrying an uncertain operation.
<!-- sparklaunch:connection:end -->
5. Use `projects.list` when needed, then pass the selected `project_id` to every palette tool. Use `projects.get` to confirm `effective_permissions` includes `branding.write` before generation; if required access is missing from the connection_permissions list, reconnect through the host and approve it. Explain an explicit plan or role denial using its stated remedy; do not infer that denial from effective permissions alone.
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
