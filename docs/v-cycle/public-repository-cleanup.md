# Public repository cleanup

Date: 2026-09-08. Scope: repository presentation, contributor onboarding, local-file
exclusions, and correction of stale local candidate checksums. Source: the owner's
request to prepare the repository for public viewing with zero loss of performance
or quality.

## First-pass baseline and design

The working tree already contains an unreleased 0.9.0 / service 1.8.0 candidate.
Its 468 generated files across five hosts validate against 107 tools. Existing
uncommitted work is the baseline, not the previous Git commit. A private temporary
snapshot records every tracked and visible untracked file hash before this change.

Keep canonical skills, recipes, adapters, contracts, generated packages, scripts,
tests, dependencies, licenses, and publication workflows unchanged. Move the old
skill-loop record from `.codex/skill-runs/` into `evals/archive/` byte for byte;
ignore future local runs. Move detailed compatibility and historical release prose
out of the README into linked documents. Preserve the public safety and release
boundaries. No runtime or API architecture changes are needed. No package version
change is needed because the generated content stays identical. Reverting these
documentation and ignore-file changes requires no migration or deployment.

## Requirements and verification

All requirements below are in scope and required. Verification uses Windows,
Python 3.12, the existing suite, deterministic package builds, Git file checks,
and a standalone copy with the pinned development dependencies.

| ID | Parent / rationale | Requirement and acceptance | Verification | Status |
| --- | --- | --- | --- | --- |
| PRD-PUBLIC-001 | Owner request | The repository shall give a public reader a clear introduction, host entry points, source map, contribution path, and honest release status. | T-ACCEPT-001: review README and contributor guide; resolve all new local links. | PASS: reviewed; 72 local links resolve. |
| PROD-PUBLIC-001 | PRD-PUBLIC-001 | Documentation shall preserve the current monthly operating-cycle work and retain earlier release and compatibility information in linked pages. | T-DOC-001: compare relocated text against the starting README and current release metadata. | PASS: host, portable-input, earlier-candidate, and safety prose retained; current candidate matches release metadata. |
| ARCH-PUBLIC-001 | PRD-PUBLIC-001; zero regression | The cleanup shall preserve every canonical and generated package input and every generated output byte. | T-PERF-001: baseline file hashes and before/after deterministic archive hashes must match. This verifies unchanged shipped behavior and payload, not live latency. | PASS: 468 generated files, seven archives, and candidate identity unchanged. |
| SYS-PUBLIC-001 | ARCH-PUBLIC-001 | The existing validation suite shall pass without weakening checks or claiming external acceptance. | T-SYS-001: run the CI command sequence and full suite; strict readiness must continue rejecting pending external gates. | PASS: both local environments pass; strict gates remain closed. |
| SYS-PUBLIC-002 | PRD-PUBLIC-001; public hygiene | Local credentials, environments, caches, and future agent run output shall be excluded from ordinary Git additions while source and generated packages remain visible. | T-SEC-001: check representative excluded and included paths with Git; scan repository text for credential patterns without printing values. | PASS: 14 excluded paths and 11 distributable paths checked; current text matches are synthetic fixtures/tests. |
| IMPL-PUBLIC-001 | PROD-PUBLIC-001 | Historical evaluation records shall be retained byte for byte in a documented archive. | T-ARCHIVE-001: compare all 13 source/destination hashes and confirm no remaining consumers reference the old directory. | PASS: 13 exact hashes; no build or test consumer depended on the old path. |
| IMPL-PUBLIC-002 | SYS-PUBLIC-001 | Local candidate checksum records shall match the built candidate while all historical observations and pending external statuses remain unchanged. | T-CONTRACT-001: update only the two current digests and their human-readable copy; pending validators pass and historical records remain exact. | PASS: reversing only each digest substitution reconstructs its baseline file hash, allowing Git newline normalization. |

## Requirements-catalog disposition

| Group | Disposition |
| --- | --- |
| Product context and outcomes | Applicable: public introduction and contributor onboarding, PRD/PROD-PUBLIC-001. |
| Functional requirements | Preservation only: no skill, tool, authentication, or workflow changes, ARCH-PUBLIC-001. |
| Architecture and technical quality | Applicable: canonical/generated ownership, portable contribution instructions, retained evidence. UI, localization, and deployment architecture are unchanged. |
| Performance and scalability | Applicable: zero payload or executable change, T-PERF-001. A live performance benchmark would not measure a changed runtime because none is being changed. |
| Security, privacy, and compliance | Applicable: local-file exclusions, credential-pattern review, unchanged safety contracts and licensing. No new personal data or compliance claims. |
| Data, compatibility, and migration | Applicable: exact archive preservation and candidate/historical evidence separation. No production migration or API/schema change. |
| Verification and acceptance | Applicable: link review, hash comparisons, existing tests and validators. Hosted behavior and publication are outside this local cleanup. |

## Gaps and decisions

| ID | Evidence / impact | Resolution | Status |
| --- | --- | --- | --- |
| GAP-PUBLIC-001 | Baseline portal validation rejects a stale ZIP digest; public-release validation rejects a stale candidate content digest. | Rebound only local candidate digests to the unchanged deterministic build. All six baseline test failures are resolved and external acceptance remains pending. | Closed |
| GAP-PUBLIC-002 | A new environment with only `requirements-dev.txt` cannot collect optional backend tests when the sibling backend exists without its dependencies. | Verified a standalone working-tree copy with pinned dependencies and the original workspace with backend dependencies. CONTRIBUTING documents the distinction. | Closed |
| GAP-PUBLIC-003 | Standalone pytest warns about the pre-existing optional pytest-asyncio setting. | Preserve test configuration and report the warning; no asynchronous tests or plugin behavior are changed. | Known, non-blocking |
| ASSUMPTION-PUBLIC-001 | Cleanup authorization concerns this working tree. | Prepare a local, reviewable change without publishing or rewriting Git history. | Applied |

## First-pass results

Validation ran on 2026-09-08 using Python 3.12.8 on Windows. The baseline suite
reported 357 passed, 6 failed, and 6 skipped; all failures traced to the two stale
candidate checksums. No code, tests, dependency versions, or test configuration
were changed to resolve them.

| Evidence | Result |
| --- | --- |
| Baseline preservation | Of 646 starting files, only README, `.gitignore`, and the three explicitly scoped checksum-bearing documents changed; all 13 relocated evaluation files match their original hashes. |
| Package and contract checks | Both environments pass `sync_plugin.py`, `generate_submission.py --check`, `validate_host_packages.py`, `validate_submission.py`, both deterministic builders, and both readiness validators with `--allow-pending`. |
| Existing workspace suite | `python -m pytest -q -ra`: 363 passed, 6 skipped in 71.78 seconds. Skips require Windows symbolic-link privileges. |
| Standalone source copy | Same command with Python 3.12.8, pytest 9.1.1, and PyYAML 6.0.3: 362 passed, 7 skipped, 1 warning in 111.14 seconds. Includes the same six symlink skips, one optional sibling-backend test, and the existing optional pytest-asyncio configuration warning. |
| Strict readiness | Portal and public-release validators continue rejecting pending production, reviewer, native-host, policy, and publication evidence. |
| Documentation and hygiene | 72 local links resolve; 14 ignore examples and 11 included-path examples pass; `git diff --check` passes. |
| Current credential-pattern review | 471 text files scanned using existing repository sensitive-text patterns. Matches occur only in synthetic incorporation fixture identifiers and deliberate security test inputs. This is a pattern review, not a claim of exhaustive security certification. |
| Reachable-history pattern review | 762 unique text blobs across 62 locally reachable commits checked for private keys, JWTs, provider tokens, authorization headers, and URL credentials. Flagged history contains deliberate security tests and explicit documentation placeholders only. No history rewrite was needed. |

The unchanged candidate content identity is
`81e13d7b228a9ffbb0195a6405eb03050db926566403fd565bdca73407361163`.
The unchanged OpenAI/portal archive SHA-256 is
`EB2B39F4322B727D78F1786E211D55163FD1D4152698CE95C1BDAD8AEBF40F0D`.
All seven host archive hashes match the pre-cleanup release manifest. The complete
validation commands are in [CONTRIBUTING.md](../../CONTRIBUTING.md); detailed run
logs and the baseline hash manifest were retained outside the repository for this
local session.

All in-scope requirements are satisfied. The optional standalone configuration
warning remains documented. Local source/package checks do not establish
production deployment, hosted latency, directory approval, or native-client
acceptance. No release was published and no Git history was rewritten.

## Package-only layout follow-up

The owner explicitly removed the historical-compatibility requirement on
2026-09-08: the plugin has not been submitted and should have a clean layout.
This supersedes the first-pass requirement to retain generated root skill and
recipe copies. Keep canonical source in `src/` and generated host packages in
`plugins/`; retain the native host catalogs in their required discovery locations.

The starting state has 468 generated files. The generator and submission validator
still consume root mirrors. The sibling application's recipe tests and two active
documentation links also refer to root recipes; these will point at the packaged
OpenAI recipe catalog. Historical records will retain their original paths.

| ID | Parent / priority | Requirement and acceptance | Verification | Status |
| --- | --- | --- | --- | --- |
| PRD-LAYOUT-001 | Owner clarification / Must | The repository shall contain no root `sparklaunch-*` skill directories or root `recipes/` mirror. | T-LAYOUT-001: inspect root and generated output plan after rebuild. | PASS: 13 root directories and 77 duplicate files removed; rebuild does not recreate them. |
| ARCH-LAYOUT-001 | PRD-LAYOUT-001 / Must | Generation shall use only canonical source and host adapters and emit host packages plus native catalogs. | T-LAYOUT-002: regression test restricts managed roots and output paths; duplicate-target and file-safety tests remain active. | PASS: 391 generated files; new layout test and existing duplicate-target checks pass. |
| SYS-LAYOUT-001 | Original zero-loss requirement / Must | Every canonical file and installable host package shall retain its exact pre-change bytes. | T-LAYOUT-003: source/package hash comparison and seven archive checksum comparisons. | PASS: 497 source/adapter/contract/package files and all seven archives match baseline hashes. |
| IMPL-LAYOUT-001 | ARCH-LAYOUT-001 / Must | Submission validation and existing behavioral tests shall use canonical source or actual packaged files after root copies are removed. | T-LAYOUT-004: full package suite, including negative safety-contract tests, passes. | PASS: 364 passed, 6 Windows symlink skips; standalone suite passes. |
| IMPL-LAYOUT-002 | PRD-LAYOUT-001 / Must | The sibling application's active recipe consumers shall resolve the packaged recipe catalog without losing checks. | T-LAYOUT-005: its existing five recipe tests pass with default paths; active guide links resolve. | PASS: five tests; all three sibling-file changes are limited to the recipe catalog path. |
| SYS-LAYOUT-002 | ARCH-LAYOUT-001 / Must | Local candidate evidence shall bind to the reduced generated file set while preserving package identity fields and all external readiness states. | T-LAYOUT-006: refresh only the aggregate content digest; pending validators pass and strict validators remain closed. | PASS: JSON comparison proves only the aggregate digest changed; strict gates still reject missing evidence. |

Catalog disposition: product, architecture, compatibility, security, and verification
apply through the requirements above. Functional behavior and performance are
preservation constraints verified with identical source, package bytes, and archive
payloads. No API, authentication, dependency, UI, accessibility, localization,
production-data, migration, or deployment change applies.

The archive checksums should stay unchanged, while the aggregate candidate content
digest changes because it includes every generated path, including the removed
root mirrors. This is expected and does not justify changing runtime versions or
promoting pending release evidence. The baseline and copies of removed files are
retained outside the repository for local recovery. Reverting the generator and
restoring those copies requires no production migration.

### Follow-up verification

- `python scripts/sync_plugin.py --write` and the complete package-validation
  sequence in CONTRIBUTING pass with 391 outputs. Source, adapters, contracts,
  package files, native catalogs, seven host ZIPs, and the portal ZIP retain their
  pre-change bytes.
- Final workspace run: `python -m pytest -q -ra` reports **364 passed, 6 skipped
  in 42.78 seconds**. The skips are the existing Windows symbolic-link privilege
  cases. The full run found one multiline fixture path missed by the initial
  migration; it was corrected, its focused runtime-contract test passed, and the
  complete suite then passed.
- Standalone source-copy run with pinned development dependencies: **363 passed,
  7 skipped, 1 warning in 46.62 seconds**. The extra skip is the optional sibling
  runtime-contract test; the warning is the existing optional pytest-asyncio
  setting. The backend-capable workspace verifies that optional contract.
- Sibling application command:
  `node scripts/run-backend-pytest.cjs ../tests/test_agent_recipes.py -q --tb=short`:
  **5 passed in 1.34 seconds**. Its README and AGENTS guidance also resolve the
  packaged recipe path; no application runtime code changed.
- Ruff passes for both changed scripts and both changed test modules. Whitespace
  checks pass in both repositories. Current public documentation links resolve.
- Both strict release validators still exit 1 for their named external gates.
  The portal archive digest and all historical observations remain unchanged.
  Only `submission/public-release.json`'s aggregate content digest changed to
  `13ef6b3fd962fe9e898e0b160df59510ba35e82240fa2c8305affa59c959c867`.

All six follow-up requirements are satisfied. There is no unresolved regression.
The 77 removed files (1,054,727 bytes) remain in an external local recovery backup.
Changes are local and uncommitted; deployment and publication were not performed.

### Public metadata and local dot folders

The follow-up folder review keeps `.agents/plugins/marketplace.json`,
`.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json`, and `.github/`
tracked as package-discovery and repository-workflow metadata. The root `.codex/`
is now entirely ignored, including temporary output; its former run records remain
pending deletions at the old paths, with the reviewed evaluation archive retained
under `evals/archive/`. Both test/lint cache directories are already ignored and
contain no tracked files. `.git/` is Git's local database and is never part of the
committed tree. Verification checks the ignore rules, tracked-file inventory, and
continued visibility of all host catalogs and packaged `.codex-plugin` manifests.
