---
title: Resume Or Correct Incorporation
summary: Resume a safe case version, recover stale writes, repeat invalidated tasks, or request cancellation.
---

# Resume Or Correct Incorporation

## Steps

1. Select the project, verify `effective_permissions`, and call `incorporation.check_entitlement` first.
2. Use `incorporation.start_case` with the original stable `idempotency_key` when resuming the same start intent, then read the current case.
3. On `draft_version_conflict`, read the case again, merge only ordinary shared fields, and replace the complete draft against the newest `expected_version` with a key for that new intended version.
4. On `correction_required`, change only identified ordinary fields, validate, and repeat only the authorization or participant tasks invalidated for the successor version.
5. For a replacement Action Center, request a fresh preview and approval. Use each confirmation token exactly once and never transplant a token across versions or arguments.
6. For cancellation, preview `incorporation.cancel_case` with the exact version, bounded reason, and stable key. Confirm only after explicit approval. A queued or uncertain case may enter `manual_review` rather than disappearing.
7. Use returned task-specific timing. Stop automatic retries for `manual_review` or `submission_outcome_uncertain`.

## Filing Boundary

Never call Delaware, NWRA, or CorpTools. Keep private participant fields out of the conversation and direct each person to their own Action Center. Any confirmed final handoff must submit to SparkLaunch Filing Operations. **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing was stopped, completed, or accepted.
