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
3. Use `recipes/recover-incorporation-entitlement.md` when the package is missing, pending, unavailable, or needs purchase recovery.
4. Use `recipes/resume-or-correct-incorporation.md` for an existing case, stale version, correction, invalidated checkpoint, or cancellation.
5. Use `recipes/check-incorporation-status.md` for progress, waiting, receipt, or acceptance questions.

## Connected-App Rules

1. Use the SparkLaunch connection supplied by ChatGPT. Never ask for credentials or authorization headers.
2. If the required SparkLaunch actions are absent, stop and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation, select SparkLaunch, and send your request again. If ChatGPT asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge, ask the user to connect or reconnect SparkLaunch, then retry only after connection succeeds.
4. If authorization is expired or revoked, stop before writes, ask the user to reconnect from the AI Agent, and check the target before retrying any uncertain operation.
5. Use `projects.list` to select an explicit `project_id`. Use `projects.get` and verify `effective_permissions` before a project-scoped write or confirmation.
6. Treat OAuth scope, project role, and commercial entitlement as separate gates. A denial at one gate does not prove failure at another.

## Tool And Scope Contract

| Tool | Required scope | Use |
| --- | --- | --- |
| `incorporation.check_entitlement` | `incorporation.read` | Read package eligibility and recovery guidance. |
| `incorporation.start_case` | `incorporation.write` | Create or resume one entitled case. |
| `incorporation.get_case` | `incorporation.read` | Read safe case and participant progress. |
| `incorporation.update_draft` | `incorporation.write` | Replace the complete ordinary-data draft at an expected version. |
| `incorporation.validate` | `incorporation.read` | Validate one version without changing state. |
| `incorporation.prepare_action_center` | `incorporation.write` | Confirm and lock a version, then prepare private tasks. |
| `incorporation.submit_to_sparklaunch` | `incorporation.submit` | Confirm an internal Filing Operations receipt. |
| `incorporation.cancel_case` | `incorporation.write` | Confirm cancellation or supervised review. |

## Required Sequence

1. Always check entitlement first with `incorporation.check_entitlement`, including before resuming or checking a known case. Do not treat a purchase page, user statement, or browser success as entitlement evidence.
2. If entitled, call `incorporation.start_case` with one stable `idempotency_key` for that exact start intent. Retain the returned `case_id` and `version`.
3. Read the current case before editing. Call `incorporation.update_draft` with the complete ordinary-data draft, current `expected_version`, and a stable `idempotency_key` for that replacement.
4. Call `incorporation.validate` for the exact saved version. Resolve blocking errors without echoing rejected or private values.
5. Call `incorporation.prepare_action_center` without a confirmation token to obtain the exact preview. Show it and wait for explicit approval. Then repeat the same arguments and key with the returned token.
6. Direct each person to their own Action Center. Poll safe case status only at a bounded cadence appropriate to the returned task-specific guidance.
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

Report the selected project, entitlement state, case id, safe status, current version, blockers, participant progress, confirmation-gated actions, receipt id when present, and returned next action. Separate local/internal receipt evidence from external filing, acceptance, formation, Registry publication, deployment, conversion, and retention.
