---
name: sparklaunch-incorporation
description: >
  Use when a connected SparkLaunch user wants to check an Incorporation Package,
  start or resume a Delaware C-corporation case, prepare ordinary formation data,
  coordinate founder or collaborator Action Center tasks, recover from a version
  conflict, check status, cancel an unfiled case, or submit an authorized case to
  internal SparkLaunch Filing Operations.
---

# SparkLaunch Incorporation

Guide a resumable incorporation case through the connected SparkLaunch tools. Keep shared ordinary company data in the case and every person's sensitive work in their authenticated Action Center.

## Route The Request

1. Use `recipes/incorporate-a-single-founder-company.md` for one founder holding the required governance roles.
2. Use `recipes/incorporate-with-collaborators.md` when multiple founders, collaborators, or task-scoped participants are involved.
3. Use `recipes/recover-incorporation-entitlement.md` when the package is missing, pending, or unavailable and the user needs a safe entitlement readback.
4. Use `recipes/resume-or-correct-incorporation.md` for an existing case, stale version, correction, invalidated checkpoint, or cancellation.
5. Use `recipes/check-incorporation-status.md` for progress, waiting, receipt, or acceptance questions.

## Connected-App Rules

<!-- sparklaunch:connection:start -->
1. Use the OAuth connection managed by ChatGPT or Codex. Never request credentials, bearer tokens, authorization codes, client secrets, or transport headers.
2. If the required SparkLaunch actions are absent, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation with SparkLaunch selected, or enable the SparkLaunch plugin and start a new Codex task. If it is still absent, disable and re-enable or reinstall the SparkLaunch plugin, then start another fresh session. If the host asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge or `insufficient_scope`, ask the user to connect or reconnect SparkLaunch through the host and approve the named missing permissions, then retry only after it succeeds. Existing connections may lack access to newly added tools; a missing grant is not evidence of a plan restriction. Never ask the user to paste a token.
4. If a loaded action reports an expired or revoked authorization, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Reconnect SparkLaunch through the host, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
<!-- sparklaunch:connection:end -->
5. Use `projects.list` to select an explicit `project_id`. Use `projects.get` and verify `effective_permissions` before a project-scoped write or confirmation.
6. Treat OAuth scope, project role, and commercial entitlement as separate gates. A denial at one gate does not prove failure at another.
7. Retain project, case, participant, task, receipt, and version values only as internal tool-call state. Never repeat them to the user or include identifier/version labels, parenthetical references, or columns; refer to the company, case, person, task, and receipt in human-readable terms.

## Service Access And Legal Capacity

SparkLaunch service access begins at age 13. Users below their local age of majority need permission from a parent or legal guardian. Do not ask for age. Service access, Incorporation Package entitlement, and an internal Filing Operations receipt do not prove company formation, authority or capacity to sign, payment authorization or completion, identity-verification completion, regulatory eligibility, or provider eligibility.

## Tool And Scope Contract

| Tool | Required scope | Use |
| --- | --- | --- |
| `incorporation.check_entitlement` | `incorporation.read` | Read package access and entitlement state without price, purchase links, checkout actions, or purchasing instructions. |
| `incorporation.start_case` | `incorporation.write` | Create or resume one entitled case. |
| `incorporation.get_case` | `incorporation.read` | Read safe case and participant progress. |
| `incorporation.update_draft` | `incorporation.write` | Replace the complete non-address ordinary-data draft from exactly one source: a closed structured `draft` object or a supported `draft_file` reference, at an expected version. |
| `incorporation.validate` | `incorporation.read` | Validate one version without changing state. |
| `incorporation.prepare_action_center` | `incorporation.write` | Confirm and lock a version, then prepare private tasks. |
| `incorporation.submit_to_sparklaunch` | `incorporation.submit` | Confirm an internal Filing Operations receipt. |
| `incorporation.cancel_case` | `incorporation.write` | Confirm cancellation or supervised review. |

## Required Sequence

1. Always check entitlement first with `incorporation.check_entitlement`, including before resuming or checking a known case. Do not treat a purchase page, user statement, or browser success as entitlement evidence. Purchasing is unavailable through this connected agent package: never provide a price, purchase link, checkout action, or purchasing instructions. SparkLaunch web and mobile retain their separate first-party account workflows.
2. If entitled, call `incorporation.start_case` with one stable `idempotency_key` for that exact start intent. Retain the returned `case_id` and `version`.
3. Before a draft replacement, read [`references/draft-file-format.md`](./references/draft-file-format.md) completely. Read the current case, then prepare the complete non-address ordinary-data draft. Pass exactly one source: use the closed structured `draft` object on any MCP host, or use `draft_file` only when the host supplies a server-supported UTF-8 JSON file reference. Include the current `expected_version` and one stable `idempotency_key` for that replacement. Never include address or location fields in either input, tool responses, or conversation.
4. Call `incorporation.validate` for the exact saved version. Resolve blocking errors without echoing rejected or private values.
5. Call `incorporation.prepare_action_center` without a confirmation token to obtain the exact preview. Show it and wait for explicit approval. Then repeat the same arguments and key with the returned token.
6. Direct each person to their own authenticated Action Center on sparklaun.ch. Each participant enters their own address with private profile and identity work there. Because the connected-agent draft omits company addresses, the filing signer also completes the protected company business-address task and may add a distinct mailing address. Poll safe case status only at a bounded cadence appropriate to the returned task-specific guidance.
7. When the exact locked version is `ready_to_submit`, call `incorporation.submit_to_sparklaunch` for its preview. After explicit approval, repeat the same arguments and key with the returned token to submit to SparkLaunch Filing Operations.
8. Retain the receipt and use `incorporation.get_case` for bounded status readback.

## Idempotency And Recovery

- Give each exact write one stable `idempotency_key`; do not reuse it for different arguments.
- Read the case again after an uncertain write. Reuse the original arguments and original key only when readback shows a retry is needed.
- Use each confirmation token exactly once, with the same tool arguments and idempotency key that produced its preview. An expired or changed preview requires a new preview and approval.
- On `draft_version_conflict`, read the current case, merge only ordinary shared data, and create a complete successor draft against the latest version. Never overwrite newer work.
- On `manual_review`, `submission_outcome_uncertain`, or a queued cancellation, stop automatic retries and follow the returned safe recovery action.

## Participant Privacy

- Keep private fields out of the conversation: never ask for or display SSN/TIN values, identity documents, biometrics, payment credentials, signatures, private attestations, provider URLs or tokens, invitation tokens, or checkpoint locators.
- Keep raw physical locations out of connected-agent tool inputs, attachments, tool responses, and conversational text. Required participant, company business, and mailing addresses are entered only in the authenticated SparkLaunch Action Center on sparklaun.ch.
- A project collaborator may prepare ordinary shared company data. Collaboration access does not authorize completing another person's tasks or final submission.
- Every founder, officer, director, incorporator, signer, or responsible party completes only their own profile, identity/Veriff, compliance, consent, and signature work in their own Action Center.
- Show only safe participant display name, role, status, and next action. Never expose another person's private task evidence or Action Center URL.
- A participant-only invitation does not grant project collaboration or filing authority. The project owner retains final submission authority.

## Timing And Status

Use task-specific timing from each result. Do not reuse the unrelated Idea Validation 10–15 minute estimate. When timing is unavailable, say it varies and report the last update plus returned next action.

- For `human_action_required`, tell each person to use their own Action Center and use bounded readback.
- For `identity_resubmission_required`, direct only the affected person to their private task.
- For `manual_review`, stop automatic retries and wait for SparkLaunch guidance.
- For `correction_required`, update the identified ordinary fields, revalidate, and repeat only invalidated authorization or participant work.
- For `submitted_to_sparklaunch`, retain the receipt and check status without claiming external filing.

## Filing Boundary

Never call Delaware, NWRA, or CorpTools. Never instruct the user or another agent to invoke a provider endpoint, email a filing, or run a background provider process.

Use this exact success wording:

> Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.

The receipt does not mean external filing, registered-agent acceptance, formation, certificate issuance, or provider-production proof. It records one durable internal SparkLaunch Filing Operations handoff only.

## Completion Evidence

Report the selected project name, entitlement state, safe status, blockers, participant progress, confirmation-gated actions, whether an internal receipt exists, and the returned next action. Separate local/internal receipt evidence from external filing, acceptance, formation, Registry publication, deployment, conversion, and retention.
