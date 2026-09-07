# Public release readiness: 2026-09-07

Status: local package/release and UserInfo implementation verified; publication and native acceptance remain gated.

## Intent and boundaries

PRD-REL-001: One canonical skills and MCP contract source shall produce installable,
versioned packages for OpenAI, Claude, Cursor, Gemini CLI, and Muse Code. The user's
release audit and request to fix all gaps are the authority. The user explicitly
approved Apache-2.0 for this repository only; the sibling backend/service remains
proprietary. Do not manufacture host, deployment, reviewer, policy, or publication proof.

## Requirements and traceability

| Requirement | Parent | Implementation | Verification / expected result |
|---|---|---|---|
| PROD-REL-001: Apply Apache-2.0 consistently to source and generated client packages, preserving service and trademark boundaries. | PRD-REL-001 | LICENSE, NOTICE, manifests, docs | T-REL-LICENSE: all packages include exact license/notice, manifests use SPDX identifier |
| PROD-REL-002: Build deterministic self-contained archives for every host, with manifests at the archive root, digests, candidate identity and no credentials. | PRD-REL-001 | release bundle builder and CI | T-REL-BUNDLE: byte-identical rebuild, safe paths, no extra files, all five layouts validated |
| PROD-REL-003: Publish install catalogs from the same adapter/version source and document host-specific installation/update boundaries. | PRD-REL-001 | generated catalogs, release guide | T-REL-CATALOG: canonical parity plus native Claude strict validation |
| SYS-REL-001: Registry and public artifact publishing shall fail closed unless candidate identity, live full descriptors/scopes and host evidence agree. | PROD-REL-002 | release readiness validator, workflows | T-REL-GATE: pending/stale/malformed/mismatched evidence and non-main refs rejected |
| SYS-REL-002: Native evidence shall distinguish install, skill selection, OAuth lifecycle, safe writes and file handoffs from static coverage. | PROD-REL-003 | candidate-bound evidence schema/runbook | T-REL-HOST: missing, stale and falsely complete results rejected; real client checks recorded separately |
| SYS-REL-003: Authenticated live verification shall use a short-lived environment-provided OAuth token, follow no credential-bearing redirects and execute no business tool calls. | SYS-REL-001 | production contract verifier | T-REL-LIVE: initialize/list only, pagination bounded, full descriptor equality, safe sanitized failures |
| SYS-REL-004: SparkClose review classification and ChatGPT portal readiness shall remain explicit release gates. | SYS-REL-001 | evidence ledger and submission docs | T-REL-POLICY: unreviewed classification, demo or reviewer fixture cannot become a public approval claim |
| SYS-REL-005: Workspace-domain identity and Muse protected OAuth shall be supported only with verified identity/consent and a documented secure host lifecycle. | PRD-REL-001 | runtime assessment and host adapter | T-REL-AUTH: verified email only, minimal scopes, revocation; unsupported host cannot advertise protected parity |
| SYS-REL-006: Reviewer preflight shall validate a current disposable credential envelope before login and verify identity, one-project isolation, analytics exclusion and the detail endpoint's calculated Growth access without changing business data or printing credentials. | SYS-REL-004 | scripts/verify_reviewer_fixture.py | T-REL-REVIEWER: malformed/expired metadata makes zero requests; mismatched accounts stop; stored/list plan is not entitlement proof; missing setup is reported without promoting release evidence |
| SYS-REL-007: Owner-approved reviewer setup shall affect only the verified disposable account/project, preserve null billing/payment and email-verification fields, and stop on conflicting ownership or subscription state. | SYS-REL-006 | Guarded operator transaction; no application bypass | T-REL-SETUP: locked-row preconditions, exact row counts, post-transaction account preflight; no Stripe/provider/filing calls |

## Requirements catalog disposition

| Group | Disposition / rationale |
|---|---|
| Product context/outcomes | Applicable: five-host public distribution and explicit proof layers above. |
| Functional | Applicable: packaging, install/update, evidence state transitions, live auth checks; no new founder workflow. |
| Architecture/technical quality | Applicable: canonical generation, deterministic builds, versioned release gates. UI/accessibility/localization N/A: no UI changes planned. |
| Performance/scalability | Applicable: bounded network response sizes, timeouts and pagination. Load/throughput targets N/A for small release tooling. |
| Security/privacy/compliance | Applicable: Apache approval, no backend relicensing, token redaction, supply-chain integrity, policy review and least-privilege OAuth. |
| Data/compatibility/migration | Applicable: exact candidate hashes and schema versioning; preserve historical evidence. Production data migration only through the backend's reviewed deployment workflow. |
| Verification/acceptance | Applicable: positive/negative unit tests, deterministic integration checks, actual native/production observations. Unavailable external proof is NOT VERIFIED. |

## Acceptance evidence

T-REL-LICENSE, T-REL-BUNDLE, T-REL-CATALOG and T-REL-GATE passed locally. T-REL-HOST
and T-REL-LIVE negative/positive synthetic validator tests passed; actual native
workflows and full authenticated production equality remain NOT VERIFIED.
T-REL-POLICY correctly refuses pending review; the technical classification brief
does not approve public distribution. T-REL-AUTH passes for the sibling UserInfo
implementation and remains NOT VERIFIED for Muse protected OAuth and live workspace
domain enforcement. The readonly live probe fails on four missing business scopes.

See `submission/local-release-verification.md` for test counts, native validator
versions, bundle digest and exact remaining external gates. The code-simplifier
pass separated catalog generation and explicit error handling and formatted only
the new release tooling; it did not expand product behavior or weaken acceptance.

## Follow-up: effective production and reviewer baseline

Observed 2026-09-07: both live backend targets report revision
`0916f9fa16e55ebbf3ad84fe3e07232461553181`, migration
`formation_consent_actor_01`, and an active service. This revision precedes
SparkClose MCP registration. Public metadata still lacks its four permissions.
The retained disposable reviewer credential is current through 2026-09-11;
password login succeeds and only its expected project is visible. Its analytics
exclusion was false before the approved setup. T-REL-REVIEWER automates this account-only preflight;
successful login does not prove entitlement completeness, native OAuth, fixture
contents, policy acceptance or candidate deployment. No production mutation is
part of this verifier. Deployment remains held until the uncommitted backend
changes have a reviewed PR. Fresh browser tabs recovered portal/documentation
access after the original tab's repeated CDP timeouts.

The owner subsequently approved non-billing Growth/incorporation access and
analytics exclusion for the existing synthetic reviewer only. Read-only database
preflight found a regular active user, exactly one owned project, null subscription
lifecycle, no Stripe customer/subscription, a free project, and no incorporation
entitlement. The project-level legacy plan fallback is the existing supported
mechanism for this no-subscription account. The operator transaction must lock
both rows and recheck those preconditions, change only analytics exclusion and
project entitlement fields, leave paid-at and verified-email timestamps unchanged,
and report row counts. The retained fixture expires 2026-09-11; no customer plan
or recurring billing subscription is part of this authorization.

T-REL-SETUP completed: the first guard query failed before writes and rolled back;
the corrected query reads the real collaborator association table. The successful
atomic transaction changed exactly one user and one project, preserved all billing,
paid-at and email-verification fields, and made zero provider calls. All six live
preflight checks passed at 2026-09-07T05:31:59Z. The verifier reads project detail for
the server-calculated effective plan because the list serializer leaves it null;
it never equates a stored plan with access. Forty focused verifier tests passed.

Fresh isolated Claude Code 2.1.207 and Gemini CLI 0.58.0 installs each discovered
twelve skills and one MCP server. These are installation observations only, not
OAuth or model-driven acceptance. Claude has no signed-in model account; Cursor
and Muse binaries were unavailable. Muse's current official configuration and MCP
pages were read successfully, but they did not establish protected OAuth lifecycle
support. Its disabled adapter remains unchanged.

The OpenAI draft still contains 59 tools, a stale fifth positive test, an empty demo
recording URL and an enterprise-domain restriction warning. No draft values were
changed and no scan or publication occurred. A stored disposable reviewer credential
appeared in portal inspection output. Owner rotation is now required, followed by
private credential-store/portal synchronization and a fresh preflight. Reviewer
acceptance has been reset to pending; historical evidence is preserved separately.
The fixed 2026-09-11 fixture retention also needs an owner-approved ongoing-review
plan. Account provisioning does not resolve these independent gates.

See `submission/observations/2026-09-07-release-follow-up.json` for sanitized partial
observations. The V-cycle skill kept account requirements, guarded changes and
proof boundaries explicit; the code-simplifier pass kept the verifier small and
separated list isolation from authoritative detail access.

Final local regression: 327 passed, six Windows symlink-privilege skips. The four
tests that assumed historical reviewer approval was permanently current now use
explicit synthetic positive fixtures or assert the live pending state. Both strict
release commands still exit nonzero for real outstanding gates; pending mode and
all five generated package validators pass. Candidate and archive digests are
unchanged because no canonical skills, manifests or generated prompts changed in
this follow-up.
