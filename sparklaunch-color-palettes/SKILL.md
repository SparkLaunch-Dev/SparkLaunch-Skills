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
2. If challenged, ask the user to connect or reconnect SparkLaunch.
3. Use `projects.list` when needed, then pass the selected `project_id` to every palette tool.
4. `branding.generate_palette` is a write and requires a stable `idempotency_key`. Do not retry with a new key after an uncertain result.
5. Use `branding.list_palettes` or `branding.get_palette` to verify saved results.

## Workflow

1. Confirm the business, audience, desired feeling, and any color constraints.
2. Call `branding.generate_palette` with a concrete prompt and explicit project id.
3. Present the generated options, including primary, secondary, accent, neutral-light, and neutral-dark colors.
4. Use the saved palette id in downstream planning; do not claim favorite status because the current ChatGPT tool set does not change favorites.

## Output

Report `palette_id`, name, description, creation time, and each color's hex value and feeling. State whether the result was newly generated or retrieved.
