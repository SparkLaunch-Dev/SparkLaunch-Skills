# Founder Close branch integration

Evidence date: 2026-10-07 (America/Phoenix). Status: locally verified; GitHub acceptance pending.

## Baseline and scope

The user requested merging `codex/founder-close-operating-cycle` into `main`
and making main current. Main at `abe7bb7` has the same tree as the previously
merged branch at `f69c7ae`; the local feature branch adds `c8d3021`.
The checkout already contains a merge of that commit with 34 conflicted paths.
A ZIP of the original changed files and merge/index metadata is saved outside
the repository before resolution.

The incoming commit supplies package 0.11.0, service contract 1.10.0, 129 tools,
named Founder Close/Operations writes, and portal package compatibility changes.
Existing release evidence remains bounded to its recorded candidate. Deployment,
native-host acceptance, portal submission, and public releases are outside this
branch integration.

## Requirements and traceability

All requirements below are mandatory and in scope. The user request supplies
the product outcome; CONTRIBUTING.md supplies package and verification rules.

| ID | Parent | Atomic requirement | Target and acceptance | Verification |
|---|---|---|---|---|
| PRD-MERGE-001 | none | Main shall contain the requested branch's latest changes. | The reviewed integrated tree is present on remote main; local main matches remote. | T-ACCEPT-MERGE |
| PROD-MERGE-001 | PRD-MERGE-001 | The integration shall preserve committed work from both branches. | Finish the existing merge without discarding main or the incoming changes; retain the integration history locally while honoring GitHub's linear-history protection. | T-ACCEPT-MERGE |
| ARCH-MERGE-001 | PROD-MERGE-001 | Generated packages shall derive from canonical source and adapters. | Regenerate five hosts; generator check reports no drift. Keep the current incoming public contract instead of restoring obsolete command tools. | T-CONTRACT-MERGE |
| SYS-MERGE-001 | ARCH-MERGE-001 | The integrated candidate shall pass the repository's package validation. | Validators, deterministic archives, pending-evidence checks and existing pytest suite pass; no conflict markers remain. | T-SYS-MERGE |
| IMPL-MERGE-001 | SYS-MERGE-001 | Conflict resolution shall retain the latest contract, versions, recipes and packaging logic. | Canonical paths agree with the incoming commit except documented merge fixes; OpenAI MCP wrapper and portal binding remain covered. | T-UNIT-MERGE, T-CONTRACT-MERGE |

| Verification ID | Repeatable method and environment | Expected result | Evidence/status |
|---|---|---|---|
| T-UNIT-MERGE | Existing package pytest suite, Python 3.12; standalone Linux CI where required | No failures; explain environment-dependent skips | PASS: `python -m pytest -q`: 369 passed, six Windows symlink-privilege skips, 59.50 seconds; Linux CI pending |
| T-CONTRACT-MERGE | `sync_plugin.py`, `generate_submission.py --check`, host and submission validators | Canonical mirrors and 129-tool contract agree | PASS: 391 generated files, five hosts, 129 runtime tools |
| T-SYS-MERGE | Submission/release builders; portal/public validators with `--allow-pending`; `git diff --check`; conflict scan | Valid archives and evidence; pending external gates stay explicit | PASS: seven host archives and portal ZIP built; candidate identity and ZIP digest match their recorded bindings; pending validators passed; conflict markers absent |
| T-ACCEPT-MERGE | GitHub squash-merge readback, fresh fetch, integrated-tree comparison and local/remote main SHA comparison | Latest main and feature changes included; main synchronized | Planned |

## Requirements-catalog disposition

| Group | Disposition | Rationale |
|---|---|---|
| Product context and outcomes | Applicable | PRD-MERGE-001 and PROD-MERGE-001 define branch completion. |
| Functional requirements | Applicable | Preserve incoming workflows and packaging; existing tests validate behavior. |
| Architecture and technical quality | Applicable | ARCH-MERGE-001 keeps canonical source and generated adapters. |
| Performance and scalability | N/A | No runtime performance change or new performance target is requested. |
| Security, privacy and compliance | Applicable | Preserve confirmation/scopes and fail-closed release evidence via existing package tests; no live account/business actions. |
| Data, compatibility and migration | Applicable | Integrate the branch's named-tool contract and package versions; no database migration or production cutover. |
| Verification and acceptance | Applicable | SYS-MERGE-001 plus final remote ancestry/readback. |

## Conflicts and assumptions

| ID | Evidence and impact | Resolution | Status |
|---|---|---|---|
| GAP-MERGE-001 | 34 unresolved paths block the requested merge. Main and the previous feature tree are identical. | Incoming conflicted sections retained; clean merge content preserved; mirrors regenerated. | Resolved |
| GAP-MERGE-002 | Incoming README navigation introduces mojibake in middle-dot separators. | Main's correctly encoded navigation preserved. | Resolved |
| GAP-MERGE-003 | Recorded candidate digests can become stale when resolving or regenerating content. | Actual rebuild exactly matches recorded candidate content and portal ZIP digests; no evidence rebinding needed. | Resolved |
| GAP-MERGE-004 | Main is protected with required pull requests and linear history; merge commits are disabled in repository settings. | Publish the resolved branch for CI and squash the reviewed tree into main. Preserve original commits on the local feature branch; synchronize a clean local main to the authoritative squash commit. | Planned |

## Verification boundary

Local package checks and GitHub CI prove repository integration. They do not
prove service deployment, portal acceptance, installed host behavior, or customer
outcomes. Rollback is a normal revert of the integration, not a history rewrite.
