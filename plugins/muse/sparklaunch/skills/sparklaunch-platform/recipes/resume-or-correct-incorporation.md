---
title: Resume Or Correct Incorporation
summary: Resume a safe case version, recover stale writes, repeat invalidated tasks, or request cancellation.
---

# Resume Or Correct Incorporation

SparkLaunch service access begins at age 13. Users below their local age of majority need permission from a parent or legal guardian. Do not ask for age. Service access, Incorporation Package entitlement, and an internal Filing Operations receipt do not prove company formation, authority or capacity to sign, payment authorization or completion, identity-verification completion, regulatory eligibility, or provider eligibility.

## Steps

1. Select the project, verify `effective_permissions`, and call `incorporation.check_entitlement` first.
2. Use `incorporation.start_case` with the original stable `idempotency_key` when resuming the same start intent, then read the current case.
3. On `draft_version_conflict`, read the case again and merge non-address ordinary shared fields into a complete successor draft. Pass exactly one source against the newest `expected_version`: the closed structured `draft` object, or `draft_file` only when the host supplies a supported UTF-8 JSON file reference. Use a key for that new intended version. Never put address or location fields in either input, tool responses, or conversation.
4. On `correction_required`, change only the identified ordinary fields in the successor draft, validate, and repeat only the authorization or participant tasks invalidated for that version.
5. For a replacement Action Center, request a fresh preview and approval. Use each confirmation token exactly once and never transplant a token across versions or arguments.
6. For cancellation, preview `incorporation.cancel_case` with the exact version, bounded reason, and stable key. Confirm only after explicit approval. A queued or uncertain case may enter `manual_review` rather than disappearing.
7. Use returned task-specific timing. Stop automatic retries for `manual_review` or `submission_outcome_uncertain`.

## Filing Boundary

Never call Delaware, NWRA, or CorpTools. Keep private participant fields out of the conversation and direct each person to their own Action Center. Any confirmed final handoff must submit to SparkLaunch Filing Operations. **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing was stopped, completed, or accepted.

Retain identifiers and versions only for internal tool calls; refer to the company, case, tasks, and receipt in human-readable terms.
