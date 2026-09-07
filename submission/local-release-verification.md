# Local public-release verification — 2026-09-07

This records local implementation proof and separately labeled operational
observations. It does not satisfy any native OAuth, policy approval, candidate
deployment, review, publication or customer acceptance gate.

## Candidate

- Client/plugin: `0.8.1+codex.20260907000000`; MCP contract: `1.7.0`, 100 tools,
  29 business permissions, 12 skills.
- Apache-2.0 approved by the repository owner for this repository only. Backend
  licensing and hosted-service terms remain unchanged.
- 460 deterministic generated files, including canonical-generated Claude and
  Cursor catalogs and LICENSE/NOTICE in every package.
- Seven release archives covering five hosts; Gemini receives identical archives
  named for Windows, Linux and macOS so its installer can select its own asset.
- OpenAI ZIP SHA-256:
  `E07DBC7879F159E14AA08E48242EAF4117A832A076204AA592756D298D81ADB8`.

## Observed checks

- Final package suite: 327 passed; six symbolic-link tests skipped because this Windows
  session lacks symlink-creation privileges. Those tests remain enabled in Linux CI.
- The new bounded reviewer preflight has 40 passing tests. Lint, formatting checks
  for the new files, generated-package parity and pending-evidence validation pass.
- Final focused release-tool rerun after hardening: 30 passed.
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
