# Host compatibility and portable inputs

These are the repository's recorded adapter contracts and evidence boundaries,
collected from the README during the September 8, 2026 cleanup. They are not a
fresh live-client or production audit. Check [release-state.json](../release-state.json)
and the [release runbook](../submission/public-release-runbook.md) for candidate
identity and acceptance requirements. Package paths below are relative to the
repository root.

## Host support

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

## Portable inputs

`incorporation.update_draft` accepts exactly one of two address-free sources:

- a closed structured `draft` object, portable across MCP hosts; or
- `draft_file`, only when the current host supplies a server-supported UTF-8 JSON file reference.

The same 256 KiB serialized limit, nested extra-field rejection, address-field rejection, expected-version check, and idempotency contract apply to both paths.

`crm.ingest_business_card` remains intentionally narrow. It accepts only a server-approved short-lived HTTPS host file reference; callers must not substitute arbitrary URLs, base64, or data URLs.

For hosts without supported attachment metadata, `crm.prepare_business_card_import` creates an expiring first-party handoff without importing anything. The founder signs in to SparkLaunch and explicitly chooses **Upload and import**; `crm.get_business_card_import` then reports safe status. The page, not the agent, supplies the single bounded image directly to the CRM ingestion path after current user/project access is rechecked. Service `1.4.0` and both handoff descriptors are live; the direct production probe matched the candidate's 61-name tool set and checked every listed tool's output-schema root and annotation triplet. It did not retain a full-descriptor hash, and native-host plus end-to-end import execution remain unverified.

OAuth portability has the same evidence boundary. Existing DCR is the production-verified registration path. Service `1.4.0` includes feature-gated Client ID Metadata Document support with bounded-fetch, SSRF, redirect, persistence/cache, and DCR-regression controls; the implementation and migration are deployed, but current production metadata does not advertise CIMD, so the gate remains off and no live CIMD flow is claimed.

Return to the [project overview](../README.md) or [contributor guide](../CONTRIBUTING.md).
