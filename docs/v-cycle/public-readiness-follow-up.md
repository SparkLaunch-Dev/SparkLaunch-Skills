# Public release audit fixes

This record covers the 0.11.4 preparation and its historical verification. The
subsequent 0.11.5 instruction/rehearsal correction is tracked in
[reviewer-workspace-boundary.md](reviewer-workspace-boundary.md).

Effective request: November 10, 2026. Fix locally actionable findings from the
repository and existing ChatGPT listing audit. This change prepares a candidate;
endpoint migration, account changes, support messages, deployment, review
submission, publication and legal attestations remain separate actions.

## Requirements and verification

All requirements below are Must, in scope, and sourced from the audit and the
owner's follow-up request. Verification uses Python 3.12 and the built archives.

| ID / parent | Atomic requirement and acceptance | Implementation | Verification |
| --- | --- | --- | --- |
| PRD-AUDIT-001 / owner | The candidate shall resolve the local public-readiness findings without claiming hosted acceptance. | Source, documentation and versioned archives | T-ACCEPT-AUDIT: inspect final archives and strict pending gates |
| PROD-AUDIT-001 / PRD-AUDIT-001 | Public ChatGPT descriptions shall advertise only planning and private investment records. | Shared public projection and archive validation | T-CONTRACT-AUDIT: reject closing claims while retaining full-host capabilities |
| PROD-AUDIT-002 / PRD-AUDIT-001 | Public review cases shall select the synthetic project through projects.list without embedding a production identifier. | Reviewer policy and submission generator | T-PRIVACY-AUDIT: generated prompts and archive contain discovery-based selection; reject legacy identifier binding |
| ARCH-AUDIT-001 / PROD-AUDIT-001 | Public projection shall share canonical source and preserve native full-host packages. | Existing adapter/builder boundary | T-CONTRACT-AUDIT: public and native archive comparison |
| SYS-AUDIT-001 / PROD-AUDIT-002 | Public files shall retain only sanitized reviewer and operational evidence. | Private archive of original records; public summaries and hygiene check | T-SEC-AUDIT: all tracked text inspected with explicit synthetic-fixture handling |
| SYS-AUDIT-002 / PRD-AUDIT-001 | New package content shall have a new version and matching fingerprints while external gates remain pending. | Version 0.11.4 and readiness ledgers | T-GATES-AUDIT: deterministic builds, pending consistency, strict rejection |
| IMPL-AUDIT-001 / PROD-AUDIT-002 | The generator shall reject the former identifier-writing option before writing files. | CLI validation | T-PRIVACY-AUDIT: legacy option cannot overwrite source or fixture policy |
| IMPL-AUDIT-002 / SYS-AUDIT-001 | Manual installation instructions shall require complete generated skill directories and host-managed authentication. | Compatibility guide | T-DOC-AUDIT: inspect instructions and resolve local links |
| IMPL-AUDIT-003 / PROD-AUDIT-001 | The prepared listing shall use the supported Business & Operations category for the founder workflow. | OpenAI manifest and catalog | T-DOC-AUDIT: generated metadata parity; portal classification remains separate |

The public reviewer policy records readiness status and selection method only.
Actual account/project identifiers and account access stay in the private
preflight envelope. Provisioning or login is not performed by generation.
Rollback restores the preceding candidate; it does not change service data.

## Requirements catalog

1. Product: applicable; truthful public claims and installable preparation.
2. Functional: applicable; project discovery, generation, validation and failure
   before writes. No remote API or business workflow changes.
3. Architecture and quality: applicable; existing shared source and adapter
   boundary, deterministic builds, Python 3.12. Accessibility/localization N/A:
   no new UI or locale change.
4. Performance: no new latency or throughput target; bounded local file checks.
5. Security and privacy: applicable; minimize public operator data, keep private
   bindings separate, avoid secret-bearing diagnostics. No access expansion.
6. Compatibility and migration: applicable; documented removal of the unsafe
   identifier-writing CLI workflow, version bump, preserved native tool scope.
7. Verification: applicable; focused regressions, generated parity, complete
   package suite, archive inspection and fail-closed readiness checks.

## Gaps and proof boundaries

| Gap | Evidence and impact | Disposition |
| --- | --- | --- |
| AUDIT-G1 | Existing portal draft uses the full endpoint and older package. | Open: supported existing-App migration precedes a matching draft update. |
| AUDIT-G2 | Demo, native account lifecycle and reviewer cases lack current proof. | Open: retain pending states; do not copy historical acceptance to this candidate. |
| AUDIT-G3 | Previously public history retains removed operator details. | No history rewrite or credential changes; preserve originals privately and sanitize the current tree. |

## Results

November 12 pre-landing review extends T-SEC-AUDIT to recognized text files in
unsupported encodings, multiline assignments, and JSON credential values. These
inputs shall fail without disclosing their values; reviewed exact synthetic lines
remain exempt. T-CONTRACT-AUDIT also covers the public SparkClose dependency
description while preserving full-host descriptions. The original November 10
results below are historical; fresh validation is required for this follow-up.

Verified locally on November 10, 2026, with Python 3.12.8:

| Verification / requirements | Result and evidence |
| --- | --- |
| T-CONTRACT-AUDIT / PROD-AUDIT-001, ARCH-AUDIT-001 | PASS: the actual 93-file public ZIP has planning-only routing and summaries, the restricted endpoint and no App references. Native skill files are unchanged. Regressions reject new unsupported claims before creating or replacing an archive. |
| T-PRIVACY-AUDIT / PROD-AUDIT-002, IMPL-AUDIT-001 | PASS: all four scoped cases declare projects.list setup and use the selected reviewer project; the policy has no private identifier. The former identifier-writing option rejects before writes. |
| T-SEC-AUDIT / SYS-AUDIT-001 | PASS: python scripts/validate_public_repository.py checks the 606-file tracked/new inventory. Changed synthetic values and unlisted documents are detected without printing their values. Detailed original operator records are preserved outside the public repository. |
| T-DOC-AUDIT / IMPL-AUDIT-002..003 | PASS: complete-directory manual installation guidance resolves its local links; all eight demo prompts match the generated review cases. The prepared category is Business & Operations. Live listing changes remain pending. |
| T-GATES-AUDIT / SYS-AUDIT-002 | PASS: candidate 0.11.4, aggregate fingerprints and deterministic archive digests match. Both pending-mode validators pass. Strict validators still reject the outstanding external gates and unverified reviewer policy. Safety-rule and exception changes invalidate the aggregate fingerprint. |
| T-ACCEPT-AUDIT / PRD-AUDIT-001 | PASS for local preparation: generated parity, submission generation, five-host validation, public archive inspection, focused Ruff and git diff --check pass. No hosted acceptance is inferred. |
| Complete regression suite | python -m pytest -q -ra: **425 passed, 6 skipped in 607.59 seconds**. The six skips require Windows symbolic-link privileges; those checks remain enabled for Linux CI. |

The historical November 10 public ZIP was `dist/sparklaunch-chatgpt-plugin-0.11.4.zip`, SHA256
`3DFEDC4BF37B4C79D670AAB6CF2425FB2FF0FEA7BF42148F703AFDF852961C4A`.
Archives for all five hosts and their release manifest are retained locally under
`dist/readiness-fixes-2026-11-10/hosts/`. An independent public ZIP rebuild matched
byte-for-byte. Current fingerprints are in the readiness JSON files.

All local requirements above are satisfied. AUDIT-G1 and AUDIT-G2 remain open:
existing-App endpoint migration, matching portal update, current authenticated
discovery, native/reviewer acceptance, demo and policy review are not verified.
An unsent migration request is prepared locally with the existing App identity
and exact endpoints. No public upload, support message, account change,
deployment, submission, publication, Git history rewrite or remote source update
was performed.

## November 12 pre-landing verification

Independent review identified unsupported text encodings, multiline/JSON secret
assignments, a stale SparkClose dependency description and outdated operator
handoff prose. These are corrected within the existing privacy and public-scope
requirements. Full-host skill descriptions and immutable historical JSON are
unchanged. Detailed original handoff records are retained privately.

Fresh Python 3.12 validation: **431 passed, 6 Windows symbolic-link permission
skips in 307.98 seconds**. The nine focused privacy regressions and actual public
ZIP dependency assertions pass. Generated parity, all host/submission validators,
public repository checks, focused Ruff, deterministic builds and both pending-mode
readiness validators pass. Independent code and documentation re-review found no
remaining source-merge blockers. Native-host/publication acceptance remains open.

The current public ZIP SHA256 is
`F40034A3F66B13476A2F9E9214DAB63A4C27B4FDE064E7DB71BDA1726B90ED5A`.
The current candidate fingerprint is recorded in `submission/public-release.json`.
This evidence covers source preparation and pre-landing checks, not plugin
publication or a backend deployment.
