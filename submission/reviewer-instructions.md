# SparkLaunch ChatGPT Reviewer Instructions

These instructions apply to the SparkLaunch `0.3.0+codex.20260820131503` candidate and the canonical MCP endpoint `https://sparklaun.ch/api/mcp/`. The package contains nine skills, 54 tools, 30 trigger cases, and 13 controlled E2E cases under the expected 18 OAuth scopes.

## Access

1. Use the synthetic reviewer account supplied through the approved private reviewer channel. Credentials and authorization artifacts must never be added to this file, a prompt, a screenshot, or retained evidence.
2. Invoke `projects.list` from hosted ChatGPT or Codex desktop. First protected use starts SparkLaunch OAuth; it must not ask for a long-lived credential, JWT, authorization code, PKCE verifier, or custom header.
3. Approve only the scopes shown for the planned scenarios. The incorporation tools use application-owned `incorporation.read`, `incorporation.write`, and `incorporation.submit` scopes. Reconnect only for an actual OAuth challenge or missing requested scope, not for a project role, plan, entitlement, case, or version denial.
4. Invoke `projects.list`, select the disposable reviewer project, and pass its explicit `project_id` to every scoped operation. Verify `projects.get.effective_permissions` before writes or confirmations.

The checked-in five positive prompts use provisioned reviewer project `99`, recorded in `submission/reviewer-fixture.json`. The fixture permits synthetic incorporation data only and sets `provider_calls_allowed` to false. Before final import, confirm the project still belongs to the approved disposable reviewer account. If it changes, run `python scripts/generate_submission.py --reviewer-project-id <actual-id>` and rebuild the bundle; never hand-edit generated tool schemas or prompts.

### Environment binding

Staging credentials and reviewer projects are provisioned outside this package and stored only in the approved private credential channel. Do not replace a production reviewer fixture with a staging id. Bind the import only after the matching application service, disposable reviewer account, feature gate, and entitlement have been separately approved and provisioned.

### Brand assets

- Upload `plugins/sparklaunch/assets/sparklaunch.png` as the square app logo.
- Use `plugins/sparklaunch/assets/sparklaunch-wordmark-light.png` on light surfaces and `plugins/sparklaunch/assets/sparklaunch-wordmark-dark.png` on dark surfaces.
- Do not substitute generated artwork, stretch a wordmark, or crop the app logo.

## Positive review

Run the five positive prompts in `chatgpt-app-submission.json`. Confirm each invokes only its declared tool and that persisted state belongs to the disposable reviewer project.

Also exercise these boundaries:

1. Repeat one private write with its original idempotency key and confirm no duplicate record is created.
2. Request a public, destructive, or overwrite operation. Verify the exact confirmation preview, decline once, then approve only a disposable action with unchanged arguments, key, and token.
3. Generate a logo or QR asset and verify the result is an expiring HTTPS file reference with no raw base64, data URL, bucket path, or credential.
4. Read a synthetic CRM contact or lead and verify only requested private fields are returned.
5. Revoke or disconnect SparkLaunch and confirm another protected call starts authorization again.

## Controlled incorporation review

Run the five incorporation scenarios only when the matching service version and synthetic entitlement are explicitly available. Otherwise record the scenario as externally blocked instead of working around the gate.

1. Check entitlement first. Missing access must return recovery guidance without checkout, payment, case creation, email, or provider activity.
2. Use synthetic ordinary company and participant data only. Never enter SSN/TIN values, identity documents, biometrics, signatures, payment data, private attestations, invitation tokens, provider sessions, or private Action Center URLs in chat.
3. For multiple participants, direct each person to their own private Action Center. A collaborator sees safe progress only and cannot complete another person's task.
4. Use stable idempotency keys, exact versions, readback after uncertainty, and each confirmation token exactly once.
5. Block every external provider adapter and require zero provider calls. Never call Delaware, NWRA, or CorpTools, and never perform filing, registered-agent, email, identity-provider, or background-worker actions from this review.
6. The confirmed action may only **submit to SparkLaunch Filing Operations**. Require this warning: **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing, registered-agent acceptance, formation, certificate issuance, or provider-production proof.

## Negative review

Run all three negative prompts in `chatgpt-app-submission.json`. SparkLaunch must not trigger for generic startup education, unrelated calendar management, or financial transactions. Also verify the incorporation trigger boundary: a request to add a general project collaborator remains with `sparklaunch-projects`.

Do not approve or infer unsupported behavior. The candidate has no banking access, calendar management, arbitrary internet browsing, direct provider filing tool, participant impersonation, custom widget, business-name generation, direct QR-theme editor, or arbitrary landing-draft editor.

## Expected evidence

Record the candidate revision, package digest, service version, redacted fixture ids, observation time, exact scenario outcome, provider-call counter, and any discrepancy. Do not retain credentials, authorization artifacts, confirmation tokens, private customer data, provider session details, signed URLs, or raw uploaded/generated files. Distinguish package validity, deployment, internal persistence, internal receipt, external filing, provider acceptance, formation, published state, traffic, leads, and conversion.

## Support and legal

- Support: `support@sparklaun.ch` and `https://sparklaun.ch/help`
- Privacy: `https://sparklaun.ch/privacy-policy`
- Terms: `https://sparklaun.ch/terms-and-conditions`

Stop review and contact support if OAuth redirects to an unregistered host, a project outside the reviewer account becomes visible, a private participant value appears, a write cannot be safely reconciled, or any provider call occurs.
