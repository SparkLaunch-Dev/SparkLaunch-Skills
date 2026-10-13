# Local public-release verification

This records local implementation proof and separately labeled operational
observations. It does not satisfy any native OAuth, policy approval, candidate
deployment, review, publication or customer acceptance gate.

## Current candidate: reviewer setup hardening, 0.11.3 — 2026-10-13

The candidate retains service **1.11.0**, **138 full-host tools**, **121 public
ChatGPT tools**, **33 business scopes** and **12 skills**. Reviewer preflight now
requires a regular-user account before project reads and participates in the
candidate fingerprint. Password rotation, seven setup checks and an outside
project denial were verified against the same isolated synthetic fixture.
Native private App reads, synthetic task creation/readback, confirmation preview
and Markdown file retrieval succeeded. Details are in
[the live audit](observations/2026-10-13-live-audit.md).

The rotated credentials were saved to the existing OpenAI reviewer fields after
owner approval and reopened with a masked password. The encrypted store's sync
metadata was updated and read back. No plaintext password is retained in evidence.

Restricted endpoint migration, native
reviewer scenarios, profile/refresh/disconnect/mobile acceptance and rendered
skill logos remain pending. The public draft is still 0.11.0. No public draft
upload, submission, publication or backend deployment is claimed.

Local verification: **416 passed, 6 skipped** in 406.00 seconds; six Windows
symlink-privilege skips remain enabled in Linux CI. Focused Ruff, all host and
submission validators, generated parity and pending-mode evidence consistency
pass. Candidate built at `2026-10-13T20:53:45Z`; content SHA256
`a7d6b43a704a8b2fb7407f04d787dc6f63f57660e794a22c913084b7d7fb8777`.
Portal ZIP `dist/sparklaunch-chatgpt-plugin-0.11.3.zip` SHA256
`3F379ADD1F1F9E88D36D1B02A4D42A0564EB55EA8977C465059F8B0EB2B48A14`.
The prepared archive remains local and unsubmitted.

## Historical candidate: restricted ChatGPT review preparation, 0.11.2 — 2026-10-12

Service **1.11.0**, **138 full-host tools**, **121 public ChatGPT tools**,
**33 business scopes**, **12 skills**. The native package preserves its registered
App binding; the public portal ZIP uses the restricted MCP endpoint and excludes
App references. SparkClose is limited to planning and private records. See
[submission remediation](../docs/v-cycle/submission-remediation.md).

Baseline candidate verification before the Copilot follow-up:

- Package suite: **384 passed, 6 skipped** (Windows symlink privileges).
- Isolated backend MCP/profile/OAuth selection: **244 passed**.
- Prepared portal ZIP `dist/sparklaunch-chatgpt-plugin-0.11.2.zip`, SHA-256
  `5E3D0580201A78CE37996D05124ED00B38EDE3878FED34CC8C52CB044957EF54`.

The digest above identifies the baseline artifact; metadata corrections change
the rebuilt ZIP. Deployment, restricted authenticated scans, reviewer password
rotation/preflight, actual recording/playback and native acceptance remain pending.
Valid logo assets are preserved, but private ChatGPT skill icons still display
generic badges. No submission or publication is claimed.

Copilot follow-up verification — 2026-10-12:

- Full package suite: **412 passed, 6 skipped** in 108.83 seconds; output at
  `dist/copilot-review-tests.txt` (local, ignored).
- Sensitive metadata tests reject credential assignments and credential-bearing
  URLs across supported review/publication strings and projected cases before
  archive creation, preserve any existing archive, and omit values from errors.
- Live-verifier tests prove restricted endpoint/descriptor equality, reject the
  full catalog at the restricted endpoint, and reject a restricted failure even
  when the full surface passes. These are synthetic transport tests, not live scans.
- Five-host/submission validators, focused Ruff, diff whitespace checks and both
  pending-aware evidence validators: **PASS**. Strict publication is still pending.
- Replacement ZIP `dist/sparklaunch-chatgpt-plugin-0.11.2.zip`, SHA-256
  `982F834AFB0B045F58ADD05D7CFC832BA2516ED806B89E00DF34F2EF95F3C277`.
  A separate rebuild matched byte-for-byte. Seven host release archives rebuilt.
- Candidate built at `2026-10-13T04:39:29Z`; content SHA-256
  `1d16380a3e3f0d42a3e57b355264c040e56c695b1a11b435289c2b7ccc7a4407`.
- [Demo script](demo-script.md): all five positive and three negative source
  prompts match. Recording, safe playback and a hosted URL remain owner follow-up.

## Historical local candidate: connected accounts, 0.11.1 — 2026-10-12

The native Git package binds the existing registered SparkLaunch App, preserves
all twelve skills, and no longer registers a second raw MCP connection. The
public portal ZIP converts this binding to the unchanged accepted MCP endpoint
and excludes App references. Verification and the public activation blocker are
recorded in [connected accounts](../docs/v-cycle/connected-accounts.md).

- Full package suite: **377 passed, 6 skipped** (Windows symlink privileges).
- Generator, contract consumer, five-host/submission validators, focused Ruff
  and pending-aware release-record checks: **PASS**.
- Portal ZIP SHA-256:
  `AECD024FCF724E1828E6B4CDE2B73FFE285CF6E130E37EBCF72EA032CB1F2F12`.

This version has not been uploaded, submitted, published or installed. The
registered App remains an unpublished draft, and personal ChatGPT returns
Plugin not found. The public-only OAuth discovery check passed with 33 advertised
scopes and zero business tool calls; authentication and account UI are unverified.

## Historical local candidate: ChatGPT reviewed operations, 0.11.0

Service **1.10.0**, **129 tools**, **33 scopes**, **12 skills**. Fixes the OpenAI
MCP wrapper and support URL and replaces two generic founder executors with 22
individually named operations. Native clients must rediscover the tool contract.
Canonical services, REST, persistence, authorization, exact confirmation and
idempotency remain unchanged.

- Backend selection: **125 passed, 4 PostgreSQL cases deselected**.
- Full package regression suite: **369 passed, 6 skipped** in 416.42 seconds.
  The six symbolic-link cases require Windows symlink-creation privileges and
  remain enabled in Linux CI.
- Focused Python lint: **PASS** in both repositories.
- Five-host and submission validators, seven deterministic release archives,
  and pending-aware portal/public-release consistency checks: **PASS**.
  Both repository diffs passed `git diff --check`.
- Deterministic portal ZIP:
  `dist/sparklaunch-chatgpt-plugin-0.11.0.zip`, SHA-256
  `6DD264947B4202BCE16AFE8F4FC65E869BDC04E71EB5820BF610C66EE77D9F76`.
- Candidate content SHA-256:
  `c97e2281c4792952e7010abef76eb1bc2aac626a8b1215679f8dc72e89476a27`.
- The existing portal requires its public legacy app slug in the ZIP manifest.
  Only that name is overridden; native packages retain `sparklaunch`.
- OpenAI accepted draft **0.11.0** and all **12 skills passed** its checks.
  Review status is **Not submitted**; publication is **Not published**.

The fresh legacy MCP scan failed because authorization was unavailable; its
59-tool display is retained review data. The packaged server reports Connection
unknown without a connection control. The portal also flags category confirmation
and incomplete review information. Matching backend deployment, a fresh 129-tool
scan, hosted acceptance and reviewer/demo prerequisites remain unverified.
See [portal observation](observations/2026-10-01-chatgpt-submission.md) and the
application's `docs/v-cycle/chatgpt-submission-operations.md` for exact boundaries.

No backend deployment, tool execution through the portal, final submission or
publication was performed. No credentials or customer records were changed.

## Historical local candidate: SparkClose preparation, 0.10.0

Date: 2026-09-08. Local candidate only; service 1.9.0, 109 tools, 33 scopes.

Adds reviewed unsigned agreement preview/preparation, preserves canonical SAFE
calculation and execution gates, and makes missing connection consent distinct
from project plan/role access. Source skills and all five host packages have
been regenerated. Backend verification is recorded in the application repository
at `docs/v-cycle/sparkclose-connected-preparation.md`.

- Package regression suite: **364 passed, 6 skipped** (Windows/Python 3.12).
- Backend regression suite: **216 passed, 2 PostgreSQL cases deselected**.
- Runtime snapshot equality; generated submission; 391 generated files across
  five hosts; host/submission validators; pending-aware portal/public release
  validation; and all seven deterministic release archives: **PASS**.
- Candidate content SHA-256:
  `55a52d11e8483e294e869063bae7c552ef0aed8ebc60b8c44052ff67720f6df5`.
- Portal ZIP: `dist/sparklaunch-chatgpt-plugin-0.10.0.zip`, SHA-256
  `31263A09929114C50BE4F63CB8AC49E32489C05A608C03C7B25C18BF82418043`.

Live ChatGPT consent, deployment and draft-preparation acceptance remain
**NOT VERIFIED**. No customer financing records or real agreements were changed.
The prior 0.9.0 local candidate below is historical, not evidence for this build.

## Historical local candidate: Monthly Founder Close, 0.9.0

The 2026-09-07 implementation adds seven typed tools and four separately
consented permissions for monthly reporting, reviewed SparkRoom additions,
obligations and approved internal operations. The AI host authors investor and
board reports; SparkLaunch stores exact revisions and approvals and exports safe
PDFs through Company Library. The recurring state lives in SparkLaunch.

- Plugin 0.9.0; service contract 1.8.0; 107 tools, 33 scopes, twelve skills.
- New canonical recipe: `src/recipes/run-monthly-founder-close.md`, included in
  the platform skill for all five generated host packages. There are 391
  deterministic generated files across host packages and native catalogs.
- Runtime snapshot parity, generated-package parity, submission generation,
  host/submission validators, and pending-mode portal/public-release evidence
  checks pass. Pending mode explicitly does not establish publishability.
- Package-only layout follow-up: 364 passed, 6 skipped in 42.78s. The six
  symbolic-link cases require Windows symlink-creation privileges and remain
  enabled in Linux CI. Standalone and sibling checks are recorded in
  `docs/v-cycle/public-repository-cleanup.md`.
- The new backend slice has 311 combined passing regression tests, plus isolated
  PostgreSQL migration, concurrent command/dispatch and source-lock proofs.
  The final frontend suite has 48 passing tests and desktop/Pixel 7 two-period
  browser journeys. Storage is stubbed and browser APIs are synthetic.
- OpenAI ZIP: `dist/sparklaunch-chatgpt-plugin-0.9.0.zip`, SHA-256
  `EB2B39F4322B727D78F1786E211D55163FD1D4152698CE95C1BDAD8AEBF40F0D`.
  All-host archives and checksums are in `dist/release/`.
- New tools honor current effective subscriptions and revoked authority even on
  replay. Legacy API keys also require exact confirmation. Assignee names and
  occurrence dates remain visible in operations previews; room audiences omit
  private identities and credentials from MCP output.

No production deployment, client installation, OAuth/native-host run,
marketplace submission, delivery or founder acceptance occurred for 0.9.0.
Historical candidate records are preserved below and in the immutable release
ledger; their observations cannot satisfy this changed candidate's gates.

## Historical candidate: 0.8.1

- Client/plugin: `0.8.1`; MCP contract: `1.7.0`, 100 tools,
  29 business permissions, 12 skills.
- Apache-2.0 approved by the repository owner for this repository only. Backend
  licensing and hosted-service terms remain unchanged.
- 462 deterministic generated files, including canonical-generated Claude and
  Cursor catalogs and LICENSE/NOTICE in every package.
- Seven release archives covering five hosts; Gemini receives identical archives
  named for Windows, Linux and macOS so its installer can select its own asset.
- OpenAI ZIP SHA-256:
  `72D4F4893D86D7BA198FA0A0E8345017CCFB6F476441E847EA43D6BC943B982F`.
- The icon follow-up adds a transparent #F1F5F9 1024px dark-directory mark and a
  dedicated transparent 48px composer icon. Package references and candidate
  digests were refreshed; earlier installation observations remain historical,
  not acceptance for this changed candidate. Portal icons have not been uploaded.

## Observed checks

- Final package suite after release hardening: 363 passed; six symbolic-link tests skipped because this Windows
  session lacks symlink-creation privileges. Those tests remain enabled in Linux CI.
- The new bounded reviewer preflight has 40 passing tests. Python lint,
  generated-package parity and pending-evidence validation pass.
- Final focused public-release/submission/safety rerun after hardening: 294 passed;
  six symbolic-link tests skipped for the same Windows privilege boundary.
- Claude Code 2.1.207: generated plugin and root marketplace catalog both passed
  native strict validation. A fresh isolated local catalog/plugin installation also
  succeeded and discovered all 12 skills and one MCP server. The model account is
  not signed in; OAuth/model-driven selection remain untested.
- Gemini CLI 0.58.0: generated extension passed native `extensions validate` using
  the pinned official npm package. A fresh isolated local extension installation
  succeeded and discovered all 12 skills and one MCP server. No normal user
  configuration was changed, and no OAuth or model request occurred.
- Sibling backend: 134 OAuth/CIMD tests, 39 auth/deployment/schema tests and 126
  MCP/SparkCap/SparkRoom/SparkClose regression tests passed. UserInfo returns only
  consented claims and reuses the active grant boundary. Consent-page tests: 14
  passed; frontend typecheck and lint passed.
- Source snapshot still matches the sibling runtime. Deterministic archive tests
  compare complete contents and bytes across repeated builds, including license
  parity, safe archive paths and Gemini asset selection.
- Strict public-release check correctly refuses publication for six pending
  policy/native records, an unprovisioned reviewer fixture, and the live four-scope
  production mismatch. Pending/source mode does not bypass strict publication.

## Not completed

Production still omits `sparkclose.read`, `sparkclose.model`, `sparkclose.write` and
`sparkclose.close`. Its older deployment cannot close this candidate's proof gates.
No deployment, registry publish, GitHub release or marketplace submission occurred.

Cursor and Muse binaries are unavailable on this machine. Meta's current Muse
[configuration](https://dev.meta.ai/docs/muse-code/configuration) and
[MCP documentation](https://dev.meta.ai/docs/muse-code/extending#mcp) were read
successfully in a fresh browser tab. They document HTTP/static headers and stdio,
but do not establish a protected OAuth lifecycle. The Muse adapter therefore
remains disabled for protected MCP. Do not replace this limitation with a static token.

The synthetic reviewer now has owner-approved non-billing Growth/incorporation
access and analytics exclusion. Exactly one user and one project changed; billing,
paid-at and unverified-mailbox state were preserved. All six account preflight
checks passed. This does not prove fixture content or native workflows. A stored
reviewer credential appeared in portal inspection output: owner rotation and
private store/portal synchronization are required before further reviewer use.
The unchanged 2026-09-11 retention date is not a long-term review-access commitment.

Both live backend instances still report revision
`0916f9fa16e55ebbf3ad84fe3e07232461553181` and migration
`formation_consent_actor_01`; the candidate requires `sparkclose_safe_01`.
The OpenAI draft still shows 59 tools, a stale fifth positive test, an empty demo
URL and the enterprise-domain restriction warning. No portal changes were saved.

The remaining gates are a reviewed matching backend deployment, reviewer credential
rotation/retention and candidate fixture binding, native host/auth/selection/write/file walkthroughs, SparkClose policy
classification, current ChatGPT rescan/demo and public host review/publication.
Follow [the release runbook](public-release-runbook.md); do not mark observations
that have not occurred as verified to make a workflow pass.
