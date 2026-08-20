# Controlled SparkLaunch Plugin E2E Runbook

Use this runbook for repeatable ChatGPT-plugin and MCP checks without confusing package validity, authorization, persistence, public state, or business outcomes.

## Evidence levels

1. **Descriptor:** the installed plugin exposes the expected skills, recipes, tool schemas, OAuth scopes, annotations, and confirmation controls.
2. **Authenticated transport:** a protected read succeeds through the installed host and production MCP endpoint.
3. **Private persistence:** a synthetic private write is read back with the returned record id.
4. **Confirmation boundary:** a public, destructive, or overwrite action returns its exact preview and makes no change before approval.
5. **Confirmed mutation:** execute only after the user approves that exact preview; then read back the affected record.
6. **Observed outcome:** analytics, captured leads, conversion, revenue, and retention remain separate evidence and are never inferred from configuration.

## Fixture and timing controls

- Create one clearly named private QA project with a useful synthetic business description and one stable idempotency key.
- Project creation must automatically queue the included Idea Validation research. Poll `validation.list_projects` about once per minute for up to 20 minutes; a typical run takes 10-15 minutes. Do not call the manual create/start tools for the initial validation.
- If a long write loses its response, use readback with the returned parent identifiers. Never retry with a different idempotency key.
- Use `example.com` addresses and explicit synthetic labels for CRM and incorporation fixtures. Never perform outreach.
- Keep public/destructive tools at preview level unless the user approves the exact preview. An expired preview requires a new preview and new approval.
- In SparkLaunch Profile, verify each grant's readable permissions, open its Disconnect confirmation, and cancel. Revoke only with explicit user approval; precise authorization timestamps must distinguish duplicate client grants.
- When no connected tool can delete a private fixture, retain it with the QA label and record that limitation instead of using a hidden API.

## Permission variants

Run the matrix with a grant containing the expected 18 OAuth scopes, then call `projects.get` and evaluate `effective_permissions` for the selected project's plan, the user's role, and any token restriction. OAuth authorization is only the maximum connection boundary. A project-plan or role denial must not prompt an OAuth reconnect. A least-privilege OAuth variant may be run separately, but it must use a separate labeled connection and be disconnected only with explicit user approval.

## Incorporation isolation controls

- Run only with synthetic ordinary company and participant data. Keep SSN/TIN values, identity documents, biometrics, signatures, private attestations, payment data, invitation tokens, and private Action Center URLs out of prompts and retained evidence.
- Check entitlement before every incorporation scenario. A purchase URL or user statement is not entitlement proof, and the missing-entitlement case must not perform checkout.
- Direct each person to their own Action Center. Collaborators see only safe participant status and cannot complete another person's private work.
- Use stable idempotency keys, exact version guards, and each confirmation token once. Read the case after an uncertain write before deciding whether the original call needs replay.
- Never call Delaware, NWRA, or CorpTools. Block email, provider, worker, registered-agent, and filing adapters, and require zero provider calls for all five incorporation cases.
- The confirmed MCP action can only **submit to SparkLaunch Filing Operations**. Preserve the exact warning: **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing, provider acceptance, formation, or certificate issuance.
- Use task-specific timing returned by the case. Never apply the Idea Validation 10–15 minute estimate to identity, participant, compliance, operator, or filing work.

## Result vocabulary

- `PASS`: the declared live behavior and readback both succeeded.
- `PASS_PREVIEW`: confirmation appeared and no mutation was executed.
- `PASS_DENIED`: the intended OAuth, plan, role, ownership, or input boundary rejected the call with accurate guidance.
- `BLOCKED_EXTERNAL`: host version, deployment, maintenance, quota, or another external prerequisite prevented live proof.
- `FAIL_CONTRACT`: tool input/output did not match its descriptor.
- `FAIL_UX`: the operation may be technically bounded but the user guidance is misleading, unsafe, or unusable.

Record host and plugin versions, the redacted fixture ids, start/end timestamps, exact evidence level, discrepancies, and follow-up owner. Never store OAuth codes, access tokens, refresh tokens, confirmation tokens, or signed download URLs.
