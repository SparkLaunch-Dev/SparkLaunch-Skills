---
title: Check Incorporation Status
summary: Read safe case, participant, internal receipt, correction, and acceptance progress.
---

# Check Incorporation Status

## Steps

1. Select the project, verify `effective_permissions`, and call `incorporation.check_entitlement` first.
2. Call `incorporation.get_case` with the known `case_id`. If the case is unknown but entitlement allows it, use `incorporation.start_case` with the stable `idempotency_key` for the original start intent.
3. Report status, current version, last update, blockers, warnings, safe participant progress, and returned next action. Keep private fields out of the conversation.
4. For human work, direct each person to their own Action Center. Use returned task-specific timing and bounded readback; do not reuse the Idea Validation estimate.
5. For `manual_review` or an uncertain outcome, stop automatic retries. For `correction_required`, route to `resume-or-correct-incorporation.md`.
6. For `submitted_to_sparklaunch`, retain the receipt and continue bounded readback without claiming provider transmission or formation.

## Filing Boundary

Never call Delaware, NWRA, or CorpTools. A later owner-approved action may submit to SparkLaunch Filing Operations. Say: **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing, acceptance, certificate issuance, or company formation.
