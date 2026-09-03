# SparkLaunch ChatGPT Reviewer Instructions

These instructions apply to the SparkLaunch `0.5.0+codex.20260902140918` candidate and the canonical MCP endpoint `https://sparklaun.ch/api/mcp/`. The portal ZIP contains nine skills, and the generated submission import declares 61 tools under the expected 18 OAuth scopes; before review, the exact deployed runtime must be scanned and observed to expose the same 61-tool contract. The retained 59-tool production scan predates this candidate and is marked stale, not rewritten. The repository's internal reviewer evidence contains 30 trigger cases and 13 controlled E2E cases; those evidence files are intentionally excluded from the portal ZIP.

## Access

1. Use the synthetic reviewer account supplied through the approved private reviewer channel. Credentials and authorization artifacts must never be added to this file, a prompt, a screenshot, or retained evidence.
2. Invoke `projects.list` from hosted ChatGPT or Codex desktop. First protected use starts SparkLaunch OAuth; it must not ask for a long-lived credential, JWT, authorization code, PKCE verifier, or custom header.
3. Approve only the scopes shown for the planned scenarios. The incorporation tools use application-owned `incorporation.read`, `incorporation.write`, and `incorporation.submit` scopes. Reconnect only for an actual OAuth challenge or missing requested scope, not for a project role, plan, entitlement, case, or version denial.
4. Invoke `projects.list`, select the disposable reviewer project, and pass its explicit `project_id` to every scoped operation. Verify `projects.get.effective_permissions` before writes or confirmations.
5. For `projects.invite_collaborator`, use only a synthetic `example.com` recipient and stop at the exact project/email/role confirmation preview. Do not confirm it during review; no email or collaborator membership should be created.
6. For general task coverage, use `tasks.create` with synthetic private content and a stable idempotency key, verify it with `tasks.list`, and use only an active owner or accepted collaborator email for assignment. Stop `tasks.update` and `tasks.delete` at their exact version-bound confirmation previews unless a disposable mutation is explicitly approved.

The checked-in five positive prompts use local placeholder project `42`, recorded in `submission/reviewer-fixture.json`. The fixture permits synthetic incorporation data only and sets `provider_calls_allowed` to false. Before final import, bind the approved disposable reviewer project with `python scripts/generate_submission.py --reviewer-project-id <actual-id>` and rebuild the bundle; never hand-edit generated tool schemas or prompts.

### Environment binding

Staging credentials and reviewer projects are provisioned outside this package and stored only in the approved private credential channel. Do not replace a production reviewer fixture with a staging id. Bind the import only after the matching application service, disposable reviewer account, feature gate, and entitlement have been separately approved and provisioned.

### Brand assets

- Upload `plugins/sparklaunch/assets/sparklaunch.png` as the square app logo.
- Use `plugins/sparklaunch/assets/sparklaunch-wordmark-light.png` on light surfaces and `plugins/sparklaunch/assets/sparklaunch-wordmark-dark.png` on dark surfaces.
- Do not substitute generated artwork, stretch a wordmark, or crop the app logo.

## Positive review

Run the five positive prompts in `chatgpt-app-submission.json`. Confirm each invokes only its declared tool and that persisted state belongs to the disposable reviewer project.

Also exercise these boundaries:

0. In every user-visible response, table, confirmation, and handoff, verify records are named naturally and no identifier/version values, labels, parenthetical references, or columns appear. Confirm follow-up tool calls still use the exact retained internal state.
1. Repeat one private write with its original idempotency key and confirm no duplicate record is created.
2. Request a public, destructive, or overwrite operation. Verify the exact confirmation preview, decline once, then approve only a disposable action with unchanged arguments, key, and token.
3. Generate a logo or QR asset and verify the result is an expiring HTTPS file reference with no raw base64, data URL, bucket path, or credential.
4. Read a synthetic CRM contact or lead and verify only requested private fields are returned.
5. Revoke or disconnect SparkLaunch and confirm another protected call starts authorization again.
6. Create and read back one synthetic general project task. Verify a pending invitation or outsider cannot be assigned, an old version cannot be updated or deleted, and task overwrite/delete require exact confirmation.
7. For the portable business-card flow, call `crm.prepare_business_card_import` and verify it creates only an expiring SparkLaunch action link. Sign in on the first-party page, use one synthetic PNG/JPEG/WebP image no larger than 10 MiB, and import only by explicitly choosing **Upload and import**. Then use `crm.get_business_card_import` for status readback. Do not send image bytes, arbitrary URLs, base64, data URLs, addresses, or private contact data through MCP, and do not claim an import before the page reports completion.

## Controlled incorporation review

Run the five incorporation scenarios only when the matching service version and synthetic entitlement are explicitly available. Otherwise record the scenario as externally blocked instead of working around the gate.

SparkLaunch service access begins at age 13. Users below their local age of majority need permission from a parent or legal guardian. Do not ask for age. Service access, Incorporation Package entitlement, and an internal Filing Operations receipt do not prove company formation, authority or capacity to sign, payment authorization or completion, identity-verification completion, regulatory eligibility, or provider eligibility.

1. Check entitlement first. Missing access must return `purchase_supported_in_chatgpt:false` and no price, purchase URL, checkout action, purchasing instructions, case creation, email, or provider activity.
2. Use synthetic ordinary company and participant data only. Extract `skills/sparklaunch-incorporation/references/synthetic-single-founder-draft.json` from the portal ZIP, attach it through the host file interface, and pass it as `draft_file`. The fixture intentionally contains no address fields. The packaged `draft-file-format.md` reference describes the complete non-address file contract. Never enter addresses, SSN/TIN values, identity documents, biometrics, signatures, payment data, private attestations, invitation tokens, provider sessions, or private Action Center URLs in chat. Complete address tasks only on the authenticated sparklaun.ch Action Center.
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
