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
1. Use the OAuth connection managed by ChatGPT or Codex. Never request credentials, bearer tokens, authorization codes, client secrets, or transport headers.
2. If the required SparkLaunch actions are absent, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation with SparkLaunch selected, or enable the SparkLaunch plugin and start a new Codex task. If it is still absent, disable and re-enable or reinstall the SparkLaunch plugin, then start another fresh session. If the host asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge or `insufficient_scope`, ask the user to connect or reconnect SparkLaunch through the host and approve the named missing permissions, then retry only after it succeeds. Existing connections may lack access to newly added tools; a missing grant is not evidence of a plan restriction. Never ask the user to paste a token.
4. If a loaded action reports an expired or revoked authorization, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Reconnect SparkLaunch through the host, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
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
