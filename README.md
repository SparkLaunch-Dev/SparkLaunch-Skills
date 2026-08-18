# SparkLaunch Skills

This repository contains the canonical skills, recipes, and installable plugin package for the connected SparkLaunch ChatGPT experience.

## User Experience

SparkLaunch helps founders select or create a business project, validate an idea, generate brand assets, publish measurable launch surfaces, review campaign and landing-page signals, and operate private CRM workflows.

The default broad workflow is:

1. Connect SparkLaunch and select an accessible project, or create one with a complete business description.
2. When a project is created, wait for its automatically queued Idea Validation research to complete (normally 10-15 minutes).
3. Generate palette and logo options.
4. Create a campaign, QR file, and landing page.
5. Review observed signals and grounded CRM context.

## Shared Safety Contract

1. Authentication is OAuth-connected and managed by the host. It starts on the first protected SparkLaunch action in a conversation where the connector is loaded; skills never request credentials, OAuth codes, or transport headers. If required actions are absent, the skill stops and directs the user to open a new ChatGPT conversation with SparkLaunch selected instead of misreporting connector absence as an OAuth challenge. If a loaded connection is expired or revoked, the skill stops before writes, asks the user to reconnect from the AI Agent, and retries only after reconnection succeeds and any uncertain prior result is checked.
2. `projects.list` is the source of truth for accessible projects. Project-scoped tools receive an explicit `project_id` argument.
3. Every write receives one stable `idempotency_key` for the exact intended mutation. Uncertain writes are not repeated with new keys.
4. Before a write or confirmation, the skill checks `projects.get.effective_permissions` when project-scoped authorization applies. Destructive or public-state tools return a one-time confirmation preview only after server-side authorization preflight succeeds. The user must explicitly approve it before the exact call is resubmitted with its confirmation token.
5. Skills do not use query-token REST URLs, compatibility endpoints, legacy project headers, or hidden fallback routes.
6. Generated logo and QR outputs use short-lived HTTPS file references, never raw base64 or data URLs.
7. Configured assets, published state, traffic, conversions, CRM persistence, and revenue are reported as separate proof layers.
8. User-facing errors stay concise. Secrets, private diagnostics, internal ownership IDs, and unnecessary personal data are never surfaced.
9. OAuth scopes are the connection's maximum authorization. The selected project's plan and the user's project role may further restrict a tool; a plan/role denial is not a reason to reconnect OAuth.

## Repository Layout

- `sparklaunch-*/`: canonical skill source
- `recipes/`: multi-tool connected founder workflows
- `plugins/sparklaunch/`: deterministic packaged mirror plus plugin metadata
- `.agents/plugins/marketplace.json`: repository-local install catalog

The canonical skill folders are the only files edited by hand. Run `scripts/sync_plugin.py --write` to update packaged mirrors and `scripts/validate_submission.py` to check encodings, parity, metadata, tool references, and submission artifacts.

## Development And Validation

Clone the application and skills repositories as sibling directories when running the full package tests or regenerating the ChatGPT submission:

```text
parent/
  SparkLaunch/
    backend/
  SparkLaunch-Skills/
```

`scripts/generate_submission.py` imports the canonical MCP tool contracts from `../SparkLaunch/backend`, so `python scripts/generate_submission.py --check` and `python -m pytest tests -q` require that sibling checkout. A standalone `SparkLaunch-Skills` clone can still run `python scripts/validate_submission.py` for package-only validation.

Every published plugin change must also update `plugins/sparklaunch/.codex-plugin/plugin.json` to a new version. Git marketplace installs are cached by plugin version, so publishing changed files under an existing version can leave an older cached package active.

## Official MCP Registry

The root `server.json` publishes the production service as the remote
Streamable HTTP server `io.github.SparkLaunch-Dev/sparklaunch`. The descriptor
version must match `../SparkLaunch/backend/mcp_server_version.py`; bump both for
every new Registry publication because published versions are immutable.

The descriptor intentionally omits `repository`: the public skills repository
is not the private MCP server source, and the official Registry supports a
closed-source server when its remote endpoint is publicly accessible. Validate
and publish from this repository with the latest official publisher:

```text
mcp-publisher validate
mcp-publisher login github
mcp-publisher publish
```

GitHub authentication for the `SparkLaunch-Dev` namespace must use an
organization Owner account. After publication, verify discovery through:

```text
https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.SparkLaunch-Dev/sparklaunch
```

## Current Skills

- `sparklaunch-platform`: broad founder-workflow router
- `sparklaunch-projects`: project discovery and management
- `sparklaunch-idea-validation`: market, competitor, and TAM/SAM/SOM analysis
- `sparklaunch-color-palettes`: palette generation and retrieval
- `sparklaunch-logo-generation`: logo generation and file handoff
- `sparklaunch-campaigns`: campaigns, short links, QR, attribution, and statistics
- `sparklaunch-landing-pages`: landing creation, publishing, analytics, and leads
- `sparklaunch-sales-crm`: lead, contact, deal, activity, and business-card workflows

See [recipes/README.md](./recipes/README.md) for the supported multi-step workflows.
