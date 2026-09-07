# SparkLaunch Connected-Agent Packages

This repository builds SparkLaunch skills and native MCP package metadata for ChatGPT/Codex, Claude Code, Cursor, Gemini CLI, and Muse Code from one hand-edited source tree.

SparkLaunch helps founders select or create a business project, validate an idea, generate brand assets, publish measurable launch surfaces, review campaign and landing-page signals, operate private CRM workflows, and prepare entitlement-gated incorporation cases with person-specific Action Center tasks.

## Host Support

| Host | Generated package | Protected MCP status | Distribution boundary |
| --- | --- | --- | --- |
| ChatGPT and Codex | `plugins/sparklaunch/` | Host-managed OAuth; existing ChatGPT submission and Codex metadata retained | Local candidate; not submitted or approved by this change |
| Claude Code | `plugins/claude/sparklaunch/` | Browser-based MCP OAuth through Claude Code | Native manifest and catalog validation passed; public catalog candidate, not directory-listed |
| Cursor | `plugins/cursor/sparklaunch/` | Client-managed MCP OAuth | Apache-2.0 package and catalog candidate; native acceptance and Marketplace review pending |
| Gemini CLI | `plugins/gemini/sparklaunch/` | `/mcp auth sparklaunch` through Gemini CLI | Enterprise/API-key-supported legacy-CLI candidate; individual Free/Pro/Ultra access moved to Antigravity CLI in June 2026; live proof remains pending |
| Muse Code | `plugins/muse/sparklaunch/` | Disabled by design: Muse does not document the OAuth lifecycle SparkLaunch requires | Skills are packageable; protected tool parity is not claimed |

Google's [June 18, 2026 Gemini CLI notice](https://github.com/google-gemini/gemini-cli/discussions/28017) is the source for the individual-account transition in this table. The Gemini adapter remains distinct from an Antigravity plugin.

All enabled packages connect to the same Streamable HTTP endpoint:

```text
https://sparklaun.ch/api/mcp/
```

No package contains a bearer token, API key, client secret, authorization code, or static authorization header. Never add one as a workaround.

## Repository Layout

- `src/skills/`: canonical, host-neutral skill source edited by hand
- `src/recipes/`: canonical multi-tool founder workflows edited by hand
- `adapters/`: native host manifests, connection recovery fragments, and distribution notes
- `contracts/tools.snapshot.json`: checked-in, runtime-derived 100-tool descriptors and input/output schemas
- `plugins/`: deterministic generated packages for all five hosts
- `sparklaunch-*/` and `recipes/`: generated OpenAI-compatible legacy mirrors retained for existing consumers
- `submission/`: ChatGPT review candidate evidence and portal-only gates
- `release-state.json`: explicit local-candidate, Registry, runtime, and distribution boundaries

Do not edit generated files under `plugins/`, the top-level `sparklaunch-*` folders, or the top-level `recipes/` folder. Edit `src/` or `adapters/`, then rebuild.

## Build And Validate

Build every package and compatibility mirror:

```text
python scripts/sync_plugin.py --write
```

Run standalone validation without the application repository:

```text
python scripts/sync_plugin.py
python scripts/generate_submission.py --check
python scripts/validate_host_packages.py
python scripts/validate_submission.py
python -m pytest tests/test_host_packages.py tests/test_claude_adapter.py tests/test_cursor_adapter.py tests/test_gemini_adapter.py tests/test_muse_adapter.py -q
```

The checked-in tool snapshot makes a standalone `SparkLaunch-Skills` clone self-contained for package and ChatGPT submission validation. Clone the application and skills repositories as sibling directories when the MCP runtime contract changes, then refresh the snapshot from the isolated test-mode exporter. The default runtime source is `../SparkLaunch/backend`:

```text
parent/
  SparkLaunch/
    backend/
  SparkLaunch-Skills/
```

```text
python scripts/export_tool_contract_snapshot.py
python scripts/export_tool_contract_snapshot.py --check
python scripts/generate_submission.py
```

The exporter constructs the sibling runtime against a temporary SQLite database and records the resulting descriptors. It does not deploy the server or call a hosted SparkLaunch environment.

## SparkClose candidate

The local 0.8.1 package and service 1.7.0 candidate include 100 tools, 29 scopes and twelve skills. SparkClose adds fourteen SAFE modeling, investment, evidence, closing, recovery and first-party handoff tools. Signing and agreement review remain in SparkLaunch. Package validation does not prove deployment, publication or native-host execution.

## Earlier SparkRoom candidate

The local 0.7.0 package and service 1.6.0 candidate include 86 tools, 25 scopes and eleven skills. SparkRoom adds twelve room, document-selection, share-control and usage tools plus its skill and recipe. Effective Growth access is required. The previous 1.4.0 / 61-tool production evidence remains historical; deployment and native-host execution of this candidate are unverified.

## Earlier SparkCap candidate

The local 0.6.0 package and service 1.5.0 candidate add 13 SparkCap planning tools,
four selectable permissions, and a tenth skill. Advanced official-ledger,
signature, proof, migration, compliance, sharing, and export workflows remain
first-party application handoffs. The retained portal prerequisites and direct
production scans describe the previous 1.4.0 / 61-tool candidate. They fail the
current readiness check by design until fresh deployment and live scans exist.

## Portable Inputs

`incorporation.update_draft` accepts exactly one of two address-free sources:

- a closed structured `draft` object, portable across MCP hosts; or
- `draft_file`, only when the current host supplies a server-supported UTF-8 JSON file reference.

The same 256 KiB serialized limit, nested extra-field rejection, address-field rejection, expected-version check, and idempotency contract apply to both paths.

`crm.ingest_business_card` remains intentionally narrow. It accepts only a server-approved short-lived HTTPS host file reference; callers must not substitute arbitrary URLs, base64, or data URLs.

For hosts without supported attachment metadata, `crm.prepare_business_card_import` creates an expiring first-party handoff without importing anything. The founder signs in to SparkLaunch and explicitly chooses **Upload and import**; `crm.get_business_card_import` then reports safe status. The page, not the agent, supplies the single bounded image directly to the CRM ingestion path after current user/project access is rechecked. Service `1.4.0` and both handoff descriptors are live; the direct production probe matched the candidate's 61-name tool set and checked every listed tool's output-schema root and annotation triplet. It did not retain a full-descriptor hash, and native-host plus end-to-end import execution remain unverified.

OAuth portability has the same evidence boundary. Existing DCR is the production-verified registration path. Service `1.4.0` includes feature-gated Client ID Metadata Document support with bounded-fetch, SSRF, redirect, persistence/cache, and DCR-regression controls; the implementation and migration are deployed, but current production metadata does not advertise CIMD, so the gate remains off and no live CIMD flow is claimed.

## Shared Safety Contract

1. Authentication is managed by the host. Skills never collect credentials or transport headers.
2. `projects.list` is the source of truth for accessible projects, and project-scoped tools receive an explicit `project_id`.
3. Every write uses one stable `idempotency_key` for the exact mutation. An uncertain write is read back before any retry.
4. Project plan, project role, OAuth scope, and commercial entitlement are separate gates.
5. Destructive or public-state tools expose truthful annotations and use the runtime's governed preview/confirmation or version/idempotency boundary.
6. Generated files use short-lived HTTPS references, never raw base64 or data URLs.
7. Identifiers and concurrency versions remain opaque tool-call state; user-facing output uses human-readable names.
8. Configured assets, published state, traffic, conversion, CRM persistence, formation status, deployment, and marketplace publication are separate proof layers.

## ChatGPT Candidate And MCP Registry

Build the ChatGPT portal ZIP with:

```text
python scripts/build_submission_bundle.py
```

Portal-only prerequisites remain in `submission/portal-prerequisites.json`. Run `python scripts/validate_portal_prerequisites.py --allow-pending` after building the deterministic ZIP to validate the local candidate and its explicit evidence boundaries. That mode permits named external gates to remain pending; running the validator without the flag is the strict readiness check. The retained production revision, migration, 18-scope OAuth discovery, and 61-tool direct scan are historical baseline evidence for service `1.4.0`, not proof of the local `1.7.0` / 100-tool / 29-scope candidate. Candidate deployment, OpenAI portal Scan Tools, full live-descriptor equality, ChatGPT review, native-host execution, and publication remain unverified.

The root `server.json` is the MCP Registry descriptor for `io.github.SparkLaunch-Dev/sparklaunch`. Registry candidate version, last-known published version, runtime snapshot version, and publication status are recorded separately in `release-state.json`. Publishing an immutable Registry version requires its dedicated approved workflow and is not performed by package generation.

## Current Skills

- `sparklaunch-platform`: broad founder-workflow router
- `sparklaunch-projects`: project discovery and management
- `sparklaunch-idea-validation`: market, competitor, and TAM/SAM/SOM analysis
- `sparklaunch-color-palettes`: palette generation and retrieval
- `sparklaunch-logo-generation`: logo generation and file handoff
- `sparklaunch-campaigns`: campaigns, short links, QR, attribution, and statistics
- `sparklaunch-landing-pages`: landing creation, publishing, analytics, and leads
- `sparklaunch-sales-crm`: lead, contact, deal, activity, and supported business-card workflows
- `sparklaunch-sparkroom`: investor room preparation, pinned document selection, controlled sharing and usage summaries
- `sparklaunch-sparkcap`: cap-table and stakeholder planning, ownership, dilution, raise and hiring models
- `sparklaunch-sparkclose`: SAFE modeling, investment evidence, closing, recovery, and first-party signing handoffs
- `sparklaunch-incorporation`: entitlement, address-free case preparation, private participant tasks, corrections, status, and internal Filing Operations submission

## Support, Security, And License

- Support: [support@sparklaun.ch](mailto:support@sparklaun.ch)
- Security reports: [SECURITY.md](./SECURITY.md)
- Privacy: [SparkLaunch Privacy Policy](https://sparklaun.ch/privacy-policy)
- Terms: [SparkLaunch Terms and Conditions](https://sparklaun.ch/terms-and-conditions)
- License: [Apache License 2.0](./LICENSE), with [NOTICE](./NOTICE)

This public skills/plugin repository is Apache-2.0 with the owner's explicit approval. The separately hosted SparkLaunch service and backend remain proprietary; service terms, account permissions and trademark rights are unchanged.

## Public release process

The `0.8.1` release candidate adds Apache-2.0 licensing, generated Claude/Cursor
catalogs, deterministic five-host archives and fail-closed publication checks.
Run `python scripts/build_release_bundles.py` to create the archives, release
manifest and SHA-256 checksums under `dist/release/`.

See [the public-release runbook](submission/public-release-runbook.md) for native
acceptance, production matching, reviewer evidence, installation and publishing.
`--allow-pending` is a source-validation mode only. Both publishing workflows
require strict evidence and a fresh authenticated full-descriptor comparison.

Installed agent packages may be cached by plugin version. Any published package-content change therefore requires a new governed version; rebuilding a local candidate does not publish or invalidate an existing cache.
