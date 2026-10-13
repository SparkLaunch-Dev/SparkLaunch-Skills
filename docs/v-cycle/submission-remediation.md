# ChatGPT submission remediation

Effective request: October 12, 2026. Prepare the existing SparkLaunch plugin for
eventual public review, fix the twelve skill logos, and update the owner's
existing private test installation. The owner supplies the demo recording.
The owner selected planning/private records for SparkClose and all available
countries. Submission, publication, unrelated work, and expanded permissions
are outside this change.

## Requirements and traceability

All requirements are Must and in scope. Each row states its acceptance boundary,
implementation, and matching verification; unrun hosted checks remain open.

| ID / parent | Atomic requirement and acceptance | Implementation | Verification |
|---|---|---|---|
| PRD-SUBFIX-001 / user | The candidate shall support private testing and preparation for public review without submitting or publishing. | Existing App identities, separate archive | T-ACCEPT-SUBFIX: private release and portal status inspection |
| PROD-SUBFIX-001 / PRD-SUBFIX-001 | Each skill shall display the SparkLaunch logo in the private ChatGPT installation. | `agents/openai.yaml` and packaged images | T-ICON-SUBFIX: file resolution plus actual saved UI inspection |
| PROD-SUBFIX-002 / PRD-SUBFIX-001 | The public candidate shall exclude SparkClose signing and investment finalization. | Server-controlled public MCP surface, matching package instructions | T-BOUNDARY-SUBFIX: discovery excludes tools and direct calls cannot execute them |
| ARCH-SUBFIX-001 / PROD-SUBFIX-002 | Public filtering shall be enforced by the server, independently of client claims and skill text. | Separate server-selected endpoint/profile | T-BOUNDARY-SUBFIX: omitted tools remain unavailable even to an authorized full-scope caller |
| SYS-SUBFIX-001 / PRD-SUBFIX-001 | The ZIP shall contain supported review and publication metadata including five positive cases, three negative cases, release notes, and explicit unrestricted countries. | Portable manifest projection | T-METADATA-SUBFIX: inspect built ZIP, counts, types, and negative validation |
| SYS-SUBFIX-002 / PRD-SUBFIX-001 | Preparation shall preserve existing private App binding, audience, presentation, and account connection. | Guarded version overlay | T-PRIVATE-SUBFIX: source readback, same IDs, private audience, account UI |
| SYS-SUBFIX-003 / PRD-SUBFIX-001 | Release evidence shall distinguish current candidate proof from historical results and owner-dependent checks. | Readiness records and runbooks | T-GATES-SUBFIX: strict gates reject pending demo/access/runtime evidence |
| IMPL-SUBFIX-001 / SYS-SUBFIX-001 | The builder shall reject malformed review fields and keep credentials and registered App references out of the public upload. | Builder/validators | T-METADATA-SUBFIX: valid projection and malformed field/archive regression tests |
| IMPL-SUBFIX-002 / PROD-SUBFIX-001 | Skill image references shall resolve to real packaged SparkLaunch image assets. | Canonical skills and generated OpenAI package | T-ICON-SUBFIX: all twelve paths/files; hosted rendering is separate proof |
| IMPL-SUBFIX-003 / IMPL-SUBFIX-001 | The builder shall reject sensitive values in every projected public metadata string before creating or overwriting an archive. | Recursive use of existing sensitive-text checks | T-SECRET-SUBFIX: credential assignments and credential-bearing URLs in commerce, release notes, demo URL and all case text; no output archive on rejection |
| IMPL-SUBFIX-004 / SYS-SUBFIX-003, ARCH-SUBFIX-001 | The live release gate shall verify both the full host contract and the restricted ChatGPT contract, rejecting a failure in either surface. | Explicit verifier modes in shared release CLI and runbook | T-LIVE-SUBFIX: exact endpoint/descriptors, both CLI calls, restricted failure with full success |

October 12 follow-up: the owner requested review of Copilot's five findings
before merging, asked for a recording script, and retained backend deployment.
The findings identify unscanned free-form metadata, an unwired restricted live
verifier, an incorrect icon-restoration claim and two stale version records.
All are applicable to the catalog groups above; no new infrastructure, provider
workflow, performance target, consent expansion or migration is introduced.
Update the existing privacy and evidence requirements rather than relaxing any
submission gate. The demo script is guidance only, with all eight source prompts
checked for parity; recording and hosted playback remain separate acceptance.
The candidate fingerprint includes the shared sensitive-text validator and live
release verifiers, so changing these safety gates invalidates prior evidence.

## Architecture and rollout

Canonical skills live in `src/skills`, host differences in `adapters`; generated
packages are rebuilt with `sync_plugin.py`. The accepted Codex-format public archive imports supported
metadata under `extensions.com.openai`, retains presentation metadata, and strips
registered App bindings. The private update preserves its App-owned manifest
configuration and overlays only skills/support files plus a version bump.

The main SparkLaunch checkout contains unrelated changes, including additive
account-profile work. Preserve that state and add only the public tool boundary.
The legacy/full MCP route remains compatible. A public route uses the same auth,
authorization, and execution guards but does not register excluded tools. No
client-provided host header grants access or changes the profile.

Rollback restores previous package metadata/private release or removes the new
public mount; no database migration or authorization expansion is required.

## Requirements catalog

1. Product: applicable; reviewer readiness, truthful listing, private testing.
2. Functional: applicable; metadata import, icon display, endpoint discovery and
   call denial, existing OAuth/account behavior preservation.
3. Architecture/quality: applicable; shared source, host adapters, unchanged
   account binding and backend guards. Accessibility follows the host's image
   rendering; no new custom UI. English listing and unrestricted availability
   are explicit; no invented translations.
4. Performance: N/A new targets; bounded catalog filtering and static packaging
   within existing limits, no new workers or external services.
5. Security/privacy: applicable; excluded execution capabilities, credential
   isolation, no consent expansion, separate reviewer account and secure access.
6. Data/compatibility: applicable; versioned artifacts, historical evidence,
   legacy/full endpoint compatibility; no customer-data migration.
7. Verification: applicable; builder regressions, authorization/call boundary,
   generated parity, private UI, runtime/portal and reviewer checks.

## Gaps

| ID | Requirement | Evidence / impact | Disposition |
|---|---|---|---|
| SUBFIX-G1 | PROD-SUBFIX-001 | Existing valid YAML/images show generic badges in the cloud UI. | Diagnose importer/rendering; do not claim fixed from files alone. |
| SUBFIX-G2 | SYS-SUBFIX-003 | Demo recording and verified hosted URL are owner supplied. | Open; leave absent until provided and verified. |
| SUBFIX-G3 | SYS-SUBFIX-003 | Reviewer fixture, credential rotation/retention and current deployment scans are not verified. | Resolve independent preparation; obtain secure owner action where required. |
| SUBFIX-G4 | PRD-SUBFIX-001 | Desktop action loading and native mobile testing remain separate host acceptance. | Verify available environments; explicitly retain unavailable checks. |

## Evidence

Implementation and verification results are recorded below as work completes.

October 13 live follow-up plans T-ICON-CREATE-SUBFIX against PROD-SUBFIX-001:
compare one temporary, non-implicit icon-only skill with the twelve existing
skills in the same private App. Preserve the App identity, connection, audience,
permissions, existing source and image bytes; remove the probe after inspection.
The current owned 1.0.7 archive contains 85 files and all 24 PNGs are byte-identical
to canonical assets at 192x192 and 1024x1024. This experiment distinguishes
existing-skill update caching from a creation/import rendering failure. It is not
permission to replace the App or register another plugin. Verify the probe's
visible icon, then read back cleanup with exactly twelve skills and no probe files.
Public release metadata and its candidate identity remain unchanged.

T-ICON-CREATE-SUBFIX result: FAIL for visible skill logos. The 1.0.8 creation
probe displays its imported metadata but the generic badge. Cleanup readback and
fresh UI confirm 1.0.9, 85 files, twelve skills and zero probe files, with the same
App identity/audience/account. This narrows the diagnosis beyond existing-skill
update caching; it is not a host fix. See `docs/chatgpt-skill-icon-import.md`.

October 13 live connection follow-up: native ordinary Chat reports a successful
read of 25 accessible active projects. Raw tool results were not captured, and
the private App still points to the full `/api/mcp/` endpoint. Public-only
metadata discovery passes for 33 business scopes, while unauthenticated
`/api/mcp/chatgpt/` initialization returns 401. Neither observation proves the
authenticated 121-tool public contract. Official Inspector 2.10.1 fails DCR with
`invalid_redirect_uri` for its exact native `/oauth/callback`; a narrow backend
compatibility repair is being prepared separately. Owner retains deployment.

- T-SECRET-SUBFIX / T-LIVE-SUBFIX: full package regression **412 passed, 6
  skipped** in 108.83 seconds. Credential assignment, direct/nested URL, demo URL
  and positive/negative case regressions reject values before archive creation
  and preserve existing output. Synthetic live transports prove the restricted
  endpoint and 121 descriptors; CLI tests require both full and restricted modes
  and reject a restricted failure after a full pass. No real authenticated scan
  is claimed. Focused Ruff, all package validators and pending-mode evidence
  consistency pass. Rebuilt ZIP equality and current identity are recorded in
  `submission/local-release-verification.md`.

- T-METADATA-SUBFIX: supported manifest metadata and restricted instructions pass
  the package tests. The ZIP contains five positive and three negative cases,
  explicit unrestricted countries, release notes and commerce disclosure.
  Demo URL remains absent. The dedicated project reference is bound with
  `pending_preflight` status; this is not reviewer-access proof.
- T-BOUNDARY-SUBFIX: 244 backend checks passed in the isolated checkout, including
  actual HTTP bearer challenges, 121-tool discovery, direct denial of all nine
  excluded SparkClose calls with a full-scope test principal, account-profile
  isolation/consent, OAuth and existing full-route behavior. Both exported
  snapshots match that isolated source. No production deployment is claimed.
- T-GATES-SUBFIX: pending-mode consistency passes; strict gates continue to reject
  missing deployment/authenticated scans, reviewer verification and demo evidence.
  The 90-day secret-metadata renewal was read back, with the same account/project
  and rotation-required flag. Preflight refuses that flagged credential before login.
- T-ICON-SUBFIX: source metadata, square images and twelve-folder asset parity
  pass. PNG sizes, SVG, alternate contained paths and both upload methods still
  render generic badges. Product acceptance FAIL; see `docs/chatgpt-skill-icon-import.md`.
- T-ACCEPT-SUBFIX / T-PRIVATE-SUBFIX: private App identity, audience, account
  connection and all twelve skills remain intact. Desktop action loading and
  actual mobile workflow acceptance remain unverified, separate from browser UI.

The isolated backend branch contains only related MCP/profile work; the original
checkout's unrelated edits are preserved. Deployment, portal setup after demo,
credential rotation and native acceptance remain operational follow-up. The ZIP
is a prepared draft and is not ready for submission.
