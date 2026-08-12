# SparkLaunch Skills

This repository contains the canonical skills, recipes, and installable plugin package for the connected SparkLaunch ChatGPT experience.

## User Experience

SparkLaunch helps founders select or create a business project, validate an idea, generate brand assets, publish measurable launch surfaces, review campaign and landing-page signals, and operate private CRM workflows.

The default broad workflow is:

1. Connect SparkLaunch and select an accessible project.
2. Complete idea validation.
3. Generate palette and logo options.
4. Create a campaign, QR file, and landing page.
5. Review observed signals and grounded CRM context.

## Shared Safety Contract

1. Authentication is OAuth-connected and managed by ChatGPT. Skills never request credentials, OAuth codes, or transport headers.
2. `projects.list` is the source of truth for accessible projects. Project-scoped tools receive an explicit `project_id` argument.
3. Every write receives one stable `idempotency_key` for the exact intended mutation. Uncertain writes are not repeated with new keys.
4. Destructive or public-state tools return a one-time confirmation preview. The user must explicitly approve it before the exact call is resubmitted with its confirmation token.
5. Skills do not use query-token REST URLs, compatibility endpoints, legacy project headers, or hidden fallback routes.
6. Generated logo and QR outputs use short-lived HTTPS file references, never raw base64 or data URLs.
7. Configured assets, published state, traffic, conversions, CRM persistence, and revenue are reported as separate proof layers.
8. User-facing errors stay concise. Secrets, private diagnostics, internal ownership IDs, and unnecessary personal data are never surfaced.

## Repository Layout

- `sparklaunch-*/`: canonical skill source
- `recipes/`: multi-tool connected founder workflows
- `plugins/sparklaunch/`: deterministic packaged mirror plus plugin metadata
- `.agents/plugins/marketplace.json`: repository-local install catalog

The canonical skill folders are the only files edited by hand. Run `scripts/sync_plugin.py --write` to update packaged mirrors and `scripts/validate_submission.py` to check encodings, parity, metadata, tool references, and submission artifacts.

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
