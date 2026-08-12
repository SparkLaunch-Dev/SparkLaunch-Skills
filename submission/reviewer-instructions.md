# SparkLaunch ChatGPT Reviewer Instructions

These instructions apply to the SparkLaunch 0.2.0 candidate and the canonical MCP endpoint `https://sparklaun.ch/api/mcp/`.

## Access

1. Use the synthetic reviewer account supplied through the approved private reviewer channel. Credentials and authorization artifacts must never be added to this file, a prompt, a screenshot, or retained evidence.
2. Connect SparkLaunch from ChatGPT. The connection must start the SparkLaunch OAuth consent flow and must not ask for a long-lived credential, JWT, authorization code, PKCE verifier, or custom header.
3. Approve only the scopes shown for the planned scenarios. Reconnect if ChatGPT reports an OAuth challenge or insufficient scope.
4. Invoke `projects.list`, select the disposable reviewer project, and pass its explicit `project_id` to every scoped operation.

The checked-in positive prompts use project `42` as a deterministic local fixture. Before the final import is uploaded, run `python scripts/generate_submission.py --reviewer-project-id <actual-id>` and then rebuild the bundle. This updates `submission/reviewer-fixture.json` and all four scoped prompts together; do not assume project `42` exists in the reviewer account.

## Positive review

Run the five positive prompts in `chatgpt-app-submission.json`. Confirm that each invokes only its exact declared tool and that persisted state belongs to the disposable reviewer project.

Also exercise these safety boundaries:

1. Repeat one private write with its original idempotency key and confirm no duplicate record is created.
2. Request a public or destructive operation. Verify ChatGPT shows the exact server confirmation preview, then decline once before approving a disposable action with the same arguments, key, and confirmation token.
3. Generate a logo or QR asset and verify the result is an expiring HTTPS file reference with no raw base64, data URL, bucket path, or credential.
4. Read a synthetic CRM contact or lead and verify the response contains only the fields needed for the requested workflow.
5. Revoke or disconnect SparkLaunch and confirm another MCP call requires authorization.

## Negative review

Run all three negative prompts in `chatgpt-app-submission.json`. SparkLaunch must not trigger for generic startup education, unrelated calendar management, or financial transactions.

Do not approve or infer unsupported behavior. The candidate has no banking access, calendar management, arbitrary internet browsing, custom widget, business-name generation, direct QR-theme editing, or arbitrary landing-draft editing.

## Expected evidence

Record the candidate revision, package digest, observation time, exact scenario outcome, and any discrepancy without retaining credentials, authorization artifacts, private customer data, or raw uploaded/generated files. Distinguish configured state, persisted state, published state, observed traffic, captured leads, and actual conversion.

## Support and legal

- Support: `support@sparklaun.ch` and `https://sparklaun.ch/help`
- Privacy: `https://sparklaun.ch/privacy-policy`
- Terms: `https://sparklaun.ch/terms-and-conditions`

Stop review and contact support if OAuth redirects to an unregistered host, a project outside the reviewer account becomes visible, a write cannot be safely reconciled, or a credential/private diagnostic appears in output.
