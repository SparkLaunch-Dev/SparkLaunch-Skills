# SparkLaunch 0.2.0 ChatGPT Candidate

Status: local production candidate; not yet deployed or submitted.

## Reviewer-visible changes

- Load SparkLaunch tools before connection and start OAuth authorization code with PKCE on first use in hosted ChatGPT or Codex desktop instead of collecting credentials in chat.
- Discover, list, create, inspect, and update authorized projects through explicit `project_id` tool arguments.
- Keep `projects.get` compatible with the declared nullable-string contract when the underlying project stores one or more business-model values as JSON.
- Use one canonical MCP endpoint with 46 tools covering projects, idea validation, palettes, logos, campaigns, QR files, landing pages, analytics, leads, and CRM workflows.
- Receive typed results and structured authentication, authorization, validation, conflict, dependency, and internal error outcomes.
- Send only closed, allowlisted nested objects for campaign leads, UTM parameters, logo colors, and ChatGPT-hosted business-card files.
- Retry writes safely with stable idempotency keys and approve public-world, destructive, or overwriting actions through exact one-time confirmation previews.
- Receive generated logos and QR assets through expiring HTTPS file references rather than raw base64 or data URLs.
- Use eight concise founder-workflow skills backed by the same connected SparkLaunch MCP server.
- Display the canonical SparkLaunch launch mark in the MCP entry and all eight individual skill rows, plus the production app icon across light and dark plugin surfaces and reviewer-ready horizontal wordmarks in the submission bundle.
- Rebuild the reviewer candidate deterministically with a bundled proprietary license and recorded archive digest.
- Publish every changed candidate under a new plugin cache version and document the sibling application checkout required for contract generation and full package tests.

## Compatibility

- Existing user-scoped SparkLaunch MCP API keys and legacy runtime aliases remain supported for existing non-ChatGPT clients.
- The public ChatGPT skills and reviewer workflow use OAuth and the canonical `https://sparklaun.ch/api/mcp/` endpoint only.

## Review boundaries

- The candidate does not add a custom widget, MCP resource, prompt, business-name generator, direct QR-theme editor, or arbitrary landing-draft editor.
- Configured links, published pages, observed traffic, captured leads, conversion, revenue, and retention remain separate proof layers.
- Production deployment and the irreversible ChatGPT submission action require separate approval and fresh live evidence.
