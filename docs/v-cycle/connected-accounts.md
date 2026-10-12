# SparkLaunch connected accounts

Date: 2026-10-12 (America/Phoenix). Status: local 0.11.1 candidate verified;
public App activation and native acceptance blocked by GAP-001/GAP-003.

The user requires the existing public/Git SparkLaunch plugin to expose the
same account controls as SayForward. A private replacement was explicitly
declined. The clean working tree contains a raw MCP-only OpenAI package.
SayForward's live source instead declares `apps: "./.app.json"` and an
authenticated registered App. SparkLaunch's Developer Portal identifies the
existing integration as `asdk_app_6a963bde250881918591112eac13b307`, backed by
`https://sparklaun.ch/api/mcp/`. Preserve this identity and all twelve skills.

## Requirements and verification

All requirements below are Must and in scope for the local candidate.

| ID | Parent | Atomic requirement and acceptance | Implementation | Verification |
| --- | --- | --- | --- | --- |
| PRD-ACCT-001 | User request | The existing Git plugin shall expose host-managed SparkLaunch account controls once its registered App is available. | OpenAI adapter and registered App | T-ACCEPT-001: fresh Git install displays Apps, Connected accounts and Connect another account; pending public activation. |
| PROD-ACCT-001 | PRD-ACCT-001 | The native package shall reference the verified existing SparkLaunch App exactly once. | `.app.json` and compatibility manifest | T-CONTRACT-001: generated package validation and negative binding tests; no default raw MCP connection. |
| PROD-ACCT-002 | PRD-ACCT-001 | The public portal upload shall preserve the canonical MCP endpoint without App references. | Portal ZIP builder | T-CONTRACT-002: deterministic ZIP, no `.app.json` or non-null apps declarations, canonical endpoint/resource, all skills and assets. |
| ARCH-ACCT-001 | PROD-ACCT-001, PROD-ACCT-002 | The generator shall keep native App wiring and portal MCP wiring as distinct representations of the same service. | Adapter static files; inert `mcp/portal.json` becomes `.mcp.json` only in upload ZIP. | T-CONTRACT-001/002 and existing host-package regression suite. Rollback restores the previous adapter and rebuilds. |
| SYS-ACCT-001 | ARCH-ACCT-001 | Packages shall contain no credentials or duplicate native raw-MCP integration. | Explicit component paths; unchanged OAuth server | T-SEC-001: package inspection and negative tests reject a raw MCP declaration or wrong App binding. |
| IMPL-ACCT-001 | PROD-ACCT-001 | Validators shall reject missing, wrong or duplicate App bindings. | Host/submission validators | T-CONTRACT-001: mutation tests. |
| IMPL-ACCT-002 | PROD-ACCT-002 | The portal builder shall convert native integration metadata without modifying native files. | Builder and layout checks | T-CONTRACT-002: build twice, compare bytes, read both manifests and endpoint config, verify source unchanged. |
| IMPL-ACCT-003 | PROD-ACCT-001 | OpenAI connection instructions shall direct users to host account controls and accurately report an unavailable App. | OpenAI connection fragment | T-COMP-001: generator/validator and text inspection; credentials never requested. |

## Catalog applicability

1. Product context/outcomes: applicable; public/Git identity, account UI and
   twelve skills above. Private replacement, public review submission and new
   business workflows are outside scope.
2. Functional: applicable; host OAuth connection and failure recovery. No
   changes to business CRUD, roles, scopes, data retention or mutations.
3. Architecture/quality: applicable; deterministic generation, native versus
   portal representation, package compatibility and reversible source rollback.
   Accessibility/localization/runtime reliability are N/A: host-owned UI and
   unchanged hosted service.
4. Performance/scalability: N/A; static metadata change; no runtime/load changes.
5. Security/privacy: applicable; verified binding, no tokens, unchanged service
   authorization, no duplicate credential path. No new compliance claims.
6. Data/compatibility/migration: applicable; package patch version, cache refresh,
   preserved service identity and endpoint. No database migration.
7. Verification/acceptance: applicable; contract and package tests plus separate
   real-host acceptance. Local tests cannot prove App availability.

## Conflicts and evidence

| ID | Evidence | Impact / resolution | Status |
| --- | --- | --- | --- |
| GAP-001 | Live Developer Portal: existing App is Draft, Not published, Not submitted; Complete MCP setup finding. Personal ChatGPT lookup returns Plugin not found. | Blocks public/native acceptance. Prepare the source candidate but do not claim account controls restored or publish a broken Git update. Existing App must complete its release process. | Open, blocking external acceptance |
| GAP-002 | Official OpenAI packaging/submission docs forbid App references in public upload ZIPs. | Native Git package uses App binding; ZIP builder converts to the accepted MCP configuration. | Addressed by planned T-CONTRACT-002 |
| GAP-003 | Portal Connect account reached SparkLaunch sign-in, then the existing business Google account selector. The popup subsequently closed; refreshed portal still reports Complete MCP setup. | No authorization approval was clicked; grant outcome and authenticated scan remain unverified. | Not verified |

Sources: live SayForward Plugin Creator source; live SparkLaunch Developer Portal;
user screenshots and public/Git clarification;
[OpenAI package guide](https://developers.openai.com/plugins/build/plugins),
[submission guide](https://developers.openai.com/plugins/deploy/submission),
[multi-account authentication](https://developers.openai.com/plugins/build/auth).
The public-only verifier passed on 2026-10-12 with 33 advertised scopes and
zero business tool calls. This verifies discovery, not authenticated tools.

## Results

Windows/PowerShell, local candidate 0.11.1, 2026-10-12:

- T-CONTRACT-001, T-CONTRACT-002, T-SEC-001, T-COMP-001: PASS. `python -m
  pytest -q` reported **377 passed, 6 skipped** in 125.78 seconds. The six
  existing Windows symlink-privilege skips remain enabled in Linux CI.
- `python scripts/sync_plugin.py`: PASS, 392 generated files across five hosts.
- `python scripts/generate_submission.py --check`, both host/submission
  validators, and focused Ruff checks: PASS.
- Portal and public-release validators with `--allow-pending`: PASS for local
  consistency; public readiness is not asserted.
- Portal ZIP: `dist/sparklaunch-chatgpt-plugin-0.11.1.zip`, SHA-256
  `AECD024FCF724E1828E6B4CDE2B73FFE285CF6E130E37EBCF72EA032CB1F2F12`.
- Native OpenAI archive: `dist/release/sparklaunch-openai-0.11.1.zip`.
- T-ACCEPT-001 and authenticated OAuth acceptance: **NOT VERIFIED**. The
  registered App remains unavailable in personal ChatGPT and unpublished in
  the Developer Portal. A screenshot is retained locally at
  `dist/connection-evidence/sparklaunch-portal.png`.

The existing App must complete MCP setup and become available to its intended
audience before this Git candidate is merged/released. Then perform a fresh
native install, inspect account controls, connect an account, and read projects.
The candidate has not been installed, uploaded, submitted or published.

## Private testing before public submission

The user's follow-up authorizes testing in their ChatGPT account now and
eventual public publication later. Private testing does not require public
submission. The shared App's release gate above does not block a separately
registered account-only test connection to the same MCP service.

| ID | Parent | Requirement / acceptance | Verification |
| --- | --- | --- | --- |
| PROD-ACCT-003 | PRD-ACCT-001 | A private test copy shall use the existing SparkLaunch service and all twelve canonical skills in the requesting user's ChatGPT account. | T-PRIVATE-001: source read confirms USER/PRIVATE scope, exact App identity and all twelve skills; native UI shows connected-account controls. |
| SYS-ACCT-002 | PROD-ACCT-003 | The private test shall preserve public draft identity and use only project reads for functional acceptance. | T-PRIVATE-002: private source/config readback and a native read-only project request; no public submission, writes or credential copying. |
| IMPL-ACCT-004 | PROD-ACCT-003 | The private overlay shall preserve App-owned metadata and binding while adding the generated OpenAI skills. | T-PRIVATE-003: compare root/compatibility manifests with retrieved source, exact skill-file content parity, guarded update and source readback. |

The private connection was created through ChatGPT's supported custom-MCP flow
with USER/PRIVATE scope. Its verified identity and source readback are retained
in ignored local artifacts under `dist/private-test/` and
`dist/private-test-readback.json`. The public draft retains its original identity.
These are distinct host registrations of the same verified service; the private
ID is not substituted into the shared Git package.

Catalog groups 1/2/3/5/6/7 remain applicable to account-only packaging,
OAuth/permission boundaries, identity preservation and native acceptance.
Group 4 remains N/A because there is no hosted runtime or load change.
App-owned presentation is preserved even where it differs from the public
listing. Independent skill packaging preserves the first-party authorization
flow. Private acceptance results
are recorded after readback; they do not constitute public-release acceptance.

Private test results, 2026-10-12:

- T-PRIVATE-001: PASS. Source confirms USER/PRIVATE scope and version **1.0.1**;
  the native page shows **Apps 1** and **Skills 12**. Native settings show
  **Connected accounts**, the owner's account marked **Primary**, and
  **Connect another account**.
- T-PRIVATE-002: PASS for private registration, preservation of the public
  draft, and a read-only native test returning **31 accessible projects**.
  The host displayed the SparkLaunch tool operation and its successful result
  in a new conversation with SparkLaunch Test selected. No write was requested
  or public submission made. Setup selected `projects.read` as its default,
  but the subsequent authorization request advertised broader scopes; the
  effective grant's exact scope set is NOT VERIFIED. This acceptance proves
  functional project access, not a grant restricted to project reads.
- T-PRIVATE-003: PASS. Both manifests, preserved App configuration and all twelve
  saved skill texts were read back against the prepared overlay. The host
  normalized a trailing slash on `skills` and added an empty keyword list; these
  are equivalent representations. Explicit UTF-8 reads preserve Unicode text.
- Private overlay archive:
  `dist/sparklaunch-private-test-skills-1.0.1.zip`, SHA-256
  `d6a9fde85859f4a7d3a79ee936084c49a14f5ec6b89be71954aba8c1e06bf2a0`.

Native evidence is retained locally in
`dist/connection-evidence/private-test-connected-accounts.png` and
`dist/connection-evidence/private-test-project-read.png`. The shared package
continues to have a separate intended-audience acceptance gate for release.
The private copy is ready for account-owner testing; verification of the other
eleven workflows and public-release acceptance remain separate work.
