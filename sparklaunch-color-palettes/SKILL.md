---
name: sparklaunch-color-palettes
description: >
  Use when the user needs to generate or manage AI color palettes through the
  production Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/server/,
  specifically the branding.generate_palette, branding.list_palettes, and
  branding.get_palette tools. Do not use for generic color or design advice
  when no MCP tool execution is requested.
---

# SparkLaunch Color Palettes

Generate and manage AI-powered brand color palettes through SparkLaunch MCP.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. Do not ask the user to sign in if they already have (or can create) an API key.
4. Use login URL fallback only when API key creation is unavailable.

## Endpoint and Transport
1. Endpoint: `https://sparklaun.ch/api/mcp/server/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- store `mcp-session-id` and protocol version
- send `notifications/initialized` with the same session headers
- reuse that session id for `tools/list` and `tools/call`
4. If `Session not found` appears, reinitialize once and retry once. If it repeats, escalate as session-state infrastructure issue.

## Available Tools
- `branding.generate_palette` - Generate 3 AI color palettes from a text description
- `branding.list_palettes` - List saved palettes in the project
- `branding.get_palette` - Get a specific palette by ID

## Standard Workflow
1. Confirm the brand description or aesthetic the user wants.
2. Call `branding.generate_palette` with a descriptive prompt.
3. Present the 3 generated palettes with color swatches (hex codes and feelings).
4. If the user wants to see saved palettes, call `branding.list_palettes`.
5. If the user wants details on a specific palette, call `branding.get_palette`.

## Output Contract
Always report for generated palettes:
- `palette_id`
- `name`
- `description`
- `colors` (each with `hex` and `feeling`)
- `created_at`

For each color in a palette, display:
- Color name (primary, secondary, accent, neutral_light, neutral_dark)
- Hex code
- Mood/feeling descriptor

## Palette Limits
- Free plan: 5 AI-generated palettes per project
- Startup/Growth/Fundraise Pro: Unlimited
- Custom (user-created) palettes do not count toward limits

## Guardrails
1. Require `branding.write` scope for generation, `branding.read` for listing/viewing.
2. Never ask the user for workspace IDs, project IDs, or internal ownership IDs.
3. Keep user-facing failures friendly and concise.
4. Treat login URLs as fallback only after API key path is blocked.
5. When palette limit is reached, clearly communicate the limit and suggest upgrading.
