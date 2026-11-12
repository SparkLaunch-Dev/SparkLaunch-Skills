# Creation-only validation and reviewer rehearsal

Source: the owner's November 12 request to complete offline release preparation
while existing-App migration and authenticated checks remain pending.

## Scope and requirements

The current backend separates `validation.create_project` from
`validation.start_analysis`; creation returns a workspace without scheduling
research. The skill's unconditional create-then-analyze instruction conflicts
with the submitted creation-only case. Reviewer instructions also prohibit
supporting reads that the skills require for permissions and saved-state checks.

| ID / parent | Requirement and acceptance | Verification |
| --- | --- | --- |
| PRD-REHEARSAL-001 / owner | Offline preparation shall make review expectations match the requested action without claiming native execution. | Inspect the submitted cases, packaged skills and pending gates. |
| PROD-REHEARSAL-001 / PRD-REHEARSAL-001 | A workspace-only request shall stop after creation and permitted readback; research shall require an explicit analysis request. | Compare the skill with the separate backend operations; inspect all five generated packages and the public ZIP. |
| PROD-REHEARSAL-002 / PRD-REHEARSAL-001 | Review guidance shall allow necessary project/permission and result-verification reads while prohibiting unrelated writes. | Review the case checklist and reviewer instructions against actual schemas. |
| SYS-REHEARSAL-001 / PRD-REHEARSAL-001 | Changed packaged instructions shall use a new candidate version with matching archive digests and content identity. | Generate 0.11.5, build archives, run pending-mode validators and package tests. |
| SYS-REHEARSAL-002 / PRD-REHEARSAL-001 | Offline work shall create no account connection, provider job, public draft or submission. | Inspect tool activity and retain live gates as pending. |

Architecture: retain the shared canonical skill and existing public projection.
No backend, endpoint, permission or persistence change. Rollback selects the
preserved 0.11.4 candidate; it does not revert business data.

Requirements catalog: product, functional boundaries, shared-package architecture,
privacy, version compatibility and verification are applicable as above.
Performance, UI/accessibility and localization changes are N/A: no runtime or UI
is changed and no new service target is introduced. No sensitive fixture values
belong in the checklist. Tests of wording/package consistency cannot establish
actual model selection or a native workflow pass.

## Verification

| Verification / requirement | Local result |
| --- | --- |
| Backend/source boundary / PROD-REHEARSAL-001 | PASS by inspection: creation and analysis are separate operations; the creation handler returns a workspace without scheduling research. The canonical skill and recipe now stop after creation/readback when analysis was not requested. No runtime change was made. |
| Actual portal archive / PROD-REHEARSAL-001 | PASS: 93 files; the creation-only prompt, concrete synthetic name and no-analysis expectation agree with the packaged skill and recipe. All 24 local Markdown links resolve; 211 known tool references include no excluded or unrecognized operations. |
| Case/schema review / PROD-REHEARSAL-002 | PASS by inspection: the checklist names the actual required inputs and consent scopes, permits supporting reads and rejects unrelated writes. This is preparation, not model execution. |
| Identity and packaging / SYS-REHEARSAL-001 | PASS: five regenerated host packages, native catalogs, portal ZIP, deterministic release assets and matching identity/checksum ledgers. All host/submission/public-text validators and both pending-mode validators pass. |
| Release regressions / SYS-REHEARSAL-001 | PASS on November 12: 61 release-specific tests; full suite **431 passed, 6 Windows symbolic-link privilege skips in 640.09 seconds**. Existing candidate-version expectations were advanced without removing checks. |
| Privacy/access boundary / SYS-REHEARSAL-002 | PASS for this offline work: no account connection, OAuth grant, provider job, draft upload, submission or publication occurred. The owner's request to wait for migration is preserved. |

Focused Ruff and `git diff --check` pass. Native review cases, authenticated
discovery, the recording and the existing-App migration remain NOT VERIFIED by
this change. Static checks cannot establish that a model obeys the boundary;
the actual creation-only case must still pass in the intended host.

Portal ZIP SHA256:
`FAC812AF9CB7E15D7B92E3B64C9CD47FE0A239B751C6859E5EA80B9DD002BFF0`.
Candidate content SHA256:
`5051882629f8cb0293ab6ac1a2bcdcd3911e91f4253f2cb33edbea4eaa2037b6`.
The prior 0.11.4 portal archive is preserved. These are local package identities,
not a deployed service revision, portal upload or native acceptance record.

Compatibility gate: the OpenAI Git package binds the same registered App as the
public submission, while its instructions retain the full-host source. The
post-migration native check must reconcile those instructions with the App's
restricted catalog before distribution. This change preserves the existing
binding and full-host packages; it does not claim that compatibility is verified.
