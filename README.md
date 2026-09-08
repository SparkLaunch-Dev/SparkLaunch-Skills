# SparkLaunch for AI agents

SparkLaunch helps founders validate ideas, build a brand, launch landing pages,
manage customer relationships, prepare fundraising materials, and organize company
operations through a connected AI assistant.

This repository provides twelve skills and native MCP package metadata for
ChatGPT/Codex, Claude Code, Cursor, Gemini CLI, and Muse Code. One canonical source
tree generates every host package and native catalog.

[Workflow recipes](src/recipes/README.md) · [Contributing](CONTRIBUTING.md) ·
[Release status](release-state.json) · [Security](SECURITY.md)

## Get started

Choose your host and follow its setup guide. Protected tools use a SparkLaunch
account and host-managed OAuth. Available actions depend on the selected project,
your role, granted permissions, and plan or purchased entitlement.

| Host | Package | Setup and compatibility |
| --- | --- | --- |
| ChatGPT / Codex | [OpenAI package](plugins/sparklaunch/) | [Connection guide](adapters/openai/connection.md) and [release runbook](submission/public-release-runbook.md) |
| Claude Code | [Claude package](plugins/claude/sparklaunch/) | [Local setup and installation](adapters/claude/DISTRIBUTION.md) |
| Cursor | [Cursor package](plugins/cursor/sparklaunch/) | [Local setup and distribution](adapters/cursor/DISTRIBUTION.md) |
| Gemini CLI | [Gemini package](plugins/gemini/sparklaunch/) | [Setup and account compatibility](adapters/gemini/README.md) |
| Muse Code | [Muse skills](plugins/muse/sparklaunch/) | [Skill installation](adapters/muse/README.md); protected MCP is disabled in this adapter |

Enabled packages use the same Streamable HTTP endpoint:

```text
https://sparklaun.ch/api/mcp/
```

The packages contain no credentials. Use your host's sign-in flow; do not paste
bearer tokens, API keys, client secrets, or authorization headers into skills or
MCP configuration. See [host compatibility and portable inputs](docs/compatibility.md)
for attachment handling and OAuth evidence boundaries.

## What you can do

| Skill | Workflows |
| --- | --- |
| [Platform](src/skills/sparklaunch-platform/SKILL.md) | Route a founder journey across tools, including monthly reporting and operations. |
| [Projects](src/skills/sparklaunch-projects/SKILL.md) | Find, select, and manage accessible business projects. |
| [Idea validation](src/skills/sparklaunch-idea-validation/SKILL.md) | Explore markets, competitors, and TAM/SAM/SOM. |
| [Color palettes](src/skills/sparklaunch-color-palettes/SKILL.md) | Generate and retrieve brand palettes. |
| [Logos](src/skills/sparklaunch-logo-generation/SKILL.md) | Generate logos and hand off the files. |
| [Campaigns](src/skills/sparklaunch-campaigns/SKILL.md) | Create campaigns, short links, QR codes, attribution, and statistics. |
| [Landing pages](src/skills/sparklaunch-landing-pages/SKILL.md) | Create and publish pages, then inspect analytics and leads. |
| [Sales CRM](src/skills/sparklaunch-sales-crm/SKILL.md) | Manage leads, contacts, deals, activities, and supported business-card imports. |
| [SparkCap](src/skills/sparklaunch-sparkcap/SKILL.md) | Model ownership, dilution, raises, and hiring plans. |
| [SparkRoom](src/skills/sparklaunch-sparkroom/SKILL.md) | Prepare investor rooms, select document revisions, control sharing, and review usage. |
| [SparkClose](src/skills/sparklaunch-sparkclose/SKILL.md) | Model SAFEs and manage investment evidence, closing workflows, and signing handoffs. |
| [Incorporation](src/skills/sparklaunch-incorporation/SKILL.md) | Prepare eligible cases, private participant tasks, corrections, status checks, and internal Filing Operations submissions. |

The [recipe catalog](src/recipes/README.md) connects these skills into complete
workflows. Capabilities listed here describe the local candidate; availability in
a hosted environment depends on its deployed version and permissions.

## Release status

The working-tree candidate is **0.9.0**, with a service **1.8.0** snapshot of
**107 tools**, **33 OAuth scopes**, and **12 skills**. Its monthly operating cycle
adds seven reporting and operations tools and a platform recipe: the host authors
investor and board reports while SparkLaunch persists source snapshots, exact
approvals, private PDF publication, reviewed room refreshes, and obligations.
Existing grants require new consent, and the backend requires additive Founder
Close/Operations migrations.

Deployment, hosted package consumption, native-host acceptance, marketplace
publication, and real-user outcomes remain unverified for this candidate. The
retained service 1.4.0 / 61-tool production observations are historical evidence.
See [release state](release-state.json), [local verification](submission/local-release-verification.md),
and [earlier candidate notes](docs/release-history.md) for the details.

## Develop and validate

Use Python 3.12. A standalone `SparkLaunch-Skills` clone can validate packages
using the checked-in tool snapshot:

```sh
python -m pip install -r requirements-dev.txt
python scripts/sync_plugin.py
python scripts/generate_submission.py --check
python scripts/validate_host_packages.py
python scripts/validate_submission.py
python scripts/build_submission_bundle.py
python scripts/build_release_bundles.py
python scripts/validate_portal_prerequisites.py --allow-pending
python scripts/validate_public_release.py --allow-pending
python -m pytest -q
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup and the complete
source-editing workflow. Edit `src/` or `adapters/`, then regenerate with
`python scripts/sync_plugin.py --write`. Keep generated packages under `plugins/`
checked in; each host needs its self-contained files.

Clone the application and skills repositories as sibling directories when changing
the runtime contract. The exporter defaults to `../SparkLaunch/backend` and needs
that repository's development dependencies; it uses a temporary local database.
The public standalone checks above do not require the application repository.

Installed packages may be cached by plugin version. Published package-content
changes require a new governed version; rebuilding locally does not publish or
invalidate an existing cache. `--allow-pending` verifies source consistency while
preserving external gates. Follow the [release runbook](submission/public-release-runbook.md)
for strict readiness checks, native acceptance, and publishing.

## Repository map

| Path | Purpose |
| --- | --- |
| [`src/skills/`](src/skills/) and [`src/recipes/`](src/recipes/) | Canonical skill instructions and founder workflows. |
| [`adapters/`](adapters/) | Host manifests, connection guides, assets, and distribution notes. |
| [`contracts/tools.snapshot.json`](contracts/tools.snapshot.json) | Runtime-derived tool descriptors and input/output schemas. |
| [`plugins/`](plugins/) | Generated, self-contained packages for each host. |
| [`scripts/`](scripts/) and [`tests/`](tests/) | Deterministic builds, validators, and regression tests. |
| [`evals/`](evals/README.md) | Trigger cases, controlled workflow reviews, and archived evaluations. |
| [`docs/`](docs/) | Compatibility notes, release history, and design/verification records. |
| [`submission/`](submission/) | Reviewer guidance and recorded release evidence. |
| [`release-state.json`](release-state.json) and [`server.json`](server.json) | Candidate/distribution status and the MCP Registry descriptor. |

## Shared safety contract

1. Authentication is managed by the host. Skills never collect credentials or transport headers.
2. `projects.list` is the source of truth for accessible projects, and project-scoped tools receive an explicit `project_id`.
3. Every write uses one stable `idempotency_key` for the exact mutation. An uncertain write is read back before any retry.
4. Project plan, project role, OAuth scope, and commercial entitlement are separate gates.
5. Destructive or public-state tools expose truthful annotations and use the runtime's governed preview/confirmation or version/idempotency boundary.
6. Generated files use short-lived HTTPS references, never raw base64 or data URLs.
7. Identifiers and concurrency versions remain opaque tool-call state; user-facing output uses human-readable names.
8. Configured assets, published state, traffic, conversion, CRM persistence, formation status, deployment, and marketplace publication are separate proof layers.

## Support and license

- Support: [support@sparklaun.ch](mailto:support@sparklaun.ch)
- Security reports: [SECURITY.md](SECURITY.md)
- Privacy: [SparkLaunch Privacy Policy](https://sparklaun.ch/privacy-policy)
- Terms: [SparkLaunch Terms and Conditions](https://sparklaun.ch/terms-and-conditions)
- License: [Apache License 2.0](LICENSE), with [NOTICE](NOTICE)

This repository is licensed under Apache-2.0. The separately hosted SparkLaunch
service and backend remain proprietary; service terms, account permissions, and
trademark rights are unchanged.
