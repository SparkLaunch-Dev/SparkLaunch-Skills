# Public release runbook

One source generates five host packages. No workflow below changes the proprietary
SparkLaunch backend license. Generated client code is Apache-2.0 with the owner's
approval; trademark and hosted-service boundaries are in NOTICE.

## Build and verify

```text
python scripts/sync_plugin.py
python scripts/generate_submission.py --check
python scripts/validate_host_packages.py
python scripts/validate_submission.py
python scripts/build_submission_bundle.py
python scripts/build_release_bundles.py
python scripts/validate_portal_prerequisites.py --allow-pending
python scripts/validate_public_release.py --allow-pending
python -m pytest -q
```

`dist/release/` contains one archive per host (three identical platform-named
Gemini archives so its installer can select correctly from a multi-host release),
`release-manifest.json` and `SHA256SUMS`. Each archive is self-contained with the
host's entry point at its root. The manifest binds the package version, full
generated-content fingerprint and MCP snapshot. Identical source produces identical
bytes on Windows and Linux. Bump the package version after any published content
change; never replace an existing release/tag or rely on a cached old install.

## Production and native acceptance

1. Land and deploy the reviewed backend revision through SparkLaunch's deployment
   process. Apply its required migrations before serving that revision. Verify
   every deployment target, health and migration head; do not infer deployment
   from the Skills repository's tool snapshot or a previous deployment statement.
2. Run `python scripts/verify_production_contract.py --public-only`. It checks the
   canonical issuer/resource, all 29 business scopes and UserInfo discovery with
   the two optional identity scopes. It executes no business tool.
3. Obtain a short-lived delegated MCP OAuth access token using the normal browser
   consent flow. Provide it securely as `SPARKLAUNCH_MCP_ACCESS_TOKEN` in the
   verifier's process environment. Never paste it into chat, arguments, package
   files, logs or evidence. Run `python scripts/verify_production_contract.py`.
   It follows no redirects, sends only initialize/initialized/tools-list, handles
   bounded pagination, and compares every complete descriptor with the snapshot.
   No bearer value, user data, response body or session identifier is reported.
4. Use a dedicated synthetic reviewer project with all required entitlements. Bind
   the real reviewer fixture via the existing submission generator, regenerate,
   rebuild and update candidate digests. Do not reuse project 42 as a claimed real
   reviewer environment. Never run a customer mutation to satisfy acceptance.
   Run `python scripts/verify_reviewer_fixture.py` with the approved secret-store
   envelope supplied only in its process environment as
   `SPARKLAUNCH_REVIEWER_SECRET_JSON`. It checks metadata expiry/isolation before
   login and reads the single project's calculated plan, analytics exclusion and
   incorporation entitlement. It never creates a grant, calls a business tool,
   changes entitlements or promotes evidence. Clear the environment afterward.
   A pass is account setup only; sample content, ongoing credential availability,
   native workflows and candidate binding still require verification.
5. For each host, perform all eight checks below on the exact candidate. Static
   trigger/E2E JSON coverage is a test plan, not model execution evidence. Run the
   direct, indirect, incomplete and negative trigger cases in the real host and
   record actual skill/tool selection and safe-stop behavior.

| Check | Required observation |
|---|---|
| install | Fresh client install discovers all 12 skills and the intended MCP server; record client version and artifact digest. |
| skill_selection | Execute every case in `evals/skill-trigger-cases.json`; record selected skill/tools, expected versus actual, and failures. |
| oauth_connect | Browser PKCE flow returns to the correct host; authenticated discovery and project read succeed. |
| scope_escalation | Begin with projects.read; a second permission prompts for consent and only the approved scopes are usable. |
| refresh | Observe refresh after token expiry; no secret copying or duplicate connection grant is needed. |
| disconnect | Revoke in SparkLaunch Profile; old access/refresh fail, then a new host-initiated connection succeeds. |
| safe_write | Run the synthetic E2E matrix, including preview/no-mutation, explicit confirmation, same-key replay, stale-version and unauthorized-project denial. No signing, money movement, external filing, outreach or public publish. |
| file_handoff | Verify permitted file references and first-party business-card import; no arbitrary URL, data URL, raw credentials or unsupported attachment workaround. |

For OpenAI, test ChatGPT and Codex separately within the `openai` report; also verify
UserInfo in a domain-restricted workspace using a mailbox with verified ownership.
Claude Code skill installation is distinct from the Claude.ai connector directory.
Gemini CLI requires an eligible supported account; this is not proof for Gemini web
or Antigravity. Muse protected MCP stays disabled until its currently supported
OAuth lifecycle (or a separately reviewed trusted bridge) is verified. A skills-only
install cannot pass Muse's protected connection checks, so those six checks remain
explicitly `not_applicable` with a concrete reason. Muse install and skill selection
remain required and cannot use that status. Other hosts cannot use it at all.

## Evidence format and policy review

`submission/public-release.json` deliberately starts pending. When results exist,
create a sanitized JSON report under `submission/evidence/` containing exactly
`candidate`, `observed_at` (UTC), `surface` (host name or `policy`), and `results`.
Each applicable result contains `status: "pass"` and a concrete `observation`; use
the eight matrix keys for hosts. Muse's six protected-MCP results instead contain
`status: "not_applicable"` and observations explaining the disabled boundary, matching
the ledger's `not_applicable_reason`. The policy report instead contains
`sparkclose_classification`, `platform_guidelines`, and `reviewer_access`.
Record client version or policy reviewer, observation time, report path, normalized
UTF-8/LF SHA-256, and matching check results in the ledger. The report and ledger must
bind to the exact `candidate_identity()` emitted by the release builder. Reports
must be no more than seven days old when publishing. Preserve older evidence as
historical reports; a changed candidate resets acceptance, not history.

Read [the SparkClose policy review brief](sparkclose-policy-review.md). Do not mark
the policy review passed based on this implementation's existence or this brief.
A reviewer must resolve the concrete classification and any requested surface
changes. Do not silently classify all financial planning as prohibited, or assert
marketplace approval on the publisher's behalf.

## Publishing and installation

Both publishing workflows are manual, main-only and depend on the shared strict
readiness workflow. That workflow runs all tests, builds the exact artifacts,
requires current portal/deployment/reviewer/demo records, requires all applicable
native acceptance and policy reports, and makes a fresh authenticated production scan.
After the protected publish job begins, it rebuilds the candidate and repeats both
strict evidence validators immediately before the external write so an approval delay
cannot reuse expired evidence or an earlier production observation.
`--allow-pending` is never allowed in a publishing path. Configure the
`public-release` GitHub environment with required reviewers. Supply the short-lived
OAuth token as the workflow's protected secret immediately before the run, then
remove it afterward; do not provision a long-lived static bearer workaround.
Do not use untrusted pull-request workflows with that secret.

After release gates pass, `Publish versioned plugin assets` creates
the exact numeric `<MAJOR.MINOR.PATCH>` tag at the reviewed commit, with checksums
and release metadata. The tag matches `gemini-extension.json` for update discovery.
It refuses to overwrite an existing release. `Publish to MCP Registry` separately
publishes the service version in `server.json` through the pinned Registry publisher.
Neither job submits to a host directory or claims vendor approval.

- OpenAI: upload the plugin ZIP, bind the reviewer account, scan the deployed
  endpoint, inspect all imported descriptors, run the demo and test cases, submit
  for review, then publish only the approved snapshot. Changes require rescanning.
- Claude: use the generated root marketplace catalog from the Git repository:
  `/plugin marketplace add SparkLaunch-Dev/SparkLaunch-Skills`, then
  `/plugin install sparklaunch@sparklaunch-skills`. Validate the plugin and catalog
  with `claude plugin validate <path> --strict`. Submit the Claude.ai MCP connector
  separately if directory distribution is desired.
- Cursor: submit the public repository through Cursor's publisher flow. The generated
  `.cursor-plugin/marketplace.json` points to the Apache-2.0 package. Native local
  testing remains required; license eligibility alone is not approval.
- Gemini CLI: publish the platform-named archives before directing users to
  `gemini extensions install https://github.com/SparkLaunch-Dev/SparkLaunch-Skills`.
  Add `gemini-cli-extension` to existing repository topics only when the released
  extension is ready for gallery indexing. Update with `gemini extensions update sparklaunch`.
- Muse: distribute the skills archive only with its explicit protected-MCP limitation
  until supported OAuth can be enabled safely. Do not advertise full five-host parity.

Sources checked 2026-09-07: [OpenAI submission](https://developers.openai.com/plugins/deploy/submission),
[Claude marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[Cursor format](https://prod.cursor.com/docs/reference/plugins),
[Gemini releases](https://geminicli.com/docs/extensions/releasing/).

## Current operator handoff

See `observations/2026-09-07-release-follow-up.json`. The existing synthetic reviewer
passed all six account setup checks after the owner's narrow non-billing approval.
Do not extend its 2026-09-11 retention automatically. Arrange owner-approved access
that lasts through ongoing review, as the portal requires.

A stored reviewer credential appeared in browser inspection output. The owner
must rotate it before further reviewer use, synchronize the approved private
credential store and portal, then repeat the preflight. Never retain its value in
source or evidence. When inspecting the Testing page, do not emit an unfiltered
accessibility tree or screenshot; the credentials are rendered as plain text.

The portal's domain warning is still unresolved. The local UserInfo implementation
is not proof that OpenAI accepts its discovery metadata. After the matching
deployment, verify the portal's metadata detection and an actually verified mailbox
in a domain-restricted workspace. Do not mark the synthetic account's unverified
email as verified or claim a full OIDC provider without implementing its contract.
