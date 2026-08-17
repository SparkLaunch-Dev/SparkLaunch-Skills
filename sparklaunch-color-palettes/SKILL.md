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

1. Use ChatGPT-managed OAuth. Never ask for credentials or transport headers.
2. If the required SparkLaunch actions are absent from this conversation, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation, select SparkLaunch, and send your request again. If ChatGPT asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge, ask the user to connect or reconnect SparkLaunch, then retry only after it succeeds.
4. If a loaded action reports an expired or revoked authorization, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Reconnect SparkLaunch from this AI Agent, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
5. Use `projects.list` when needed, then pass the selected `project_id` to every palette tool. Use `projects.get` to confirm `effective_permissions` includes `branding.write` before generation; explain a plan or role limitation without requesting OAuth reconnection.
6. `branding.generate_palette` is a write and requires a stable `idempotency_key`. Do not retry with a new key after an uncertain result.
7. Use `branding.list_palettes` or `branding.get_palette` to verify saved results.

## Workflow

1. Confirm the business, audience, desired feeling, and any color constraints.
2. Call `branding.generate_palette` with a concrete prompt and explicit project id.
3. Present the generated options, including primary, secondary, accent, neutral-light, and neutral-dark colors.
4. Use the saved palette id in downstream planning; do not claim favorite status because the current ChatGPT tool set does not change favorites.

## Output

Report `palette_id`, name, description, creation time, and each color's hex value and feeling. State whether the result was newly generated or retrieved.
