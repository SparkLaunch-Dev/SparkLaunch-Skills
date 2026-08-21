---
title: Incorporate With Collaborators
summary: Coordinate shared ordinary company data and separate private tasks for multiple people.
---

# Incorporate With Collaborators

## Steps

1. Select the project, verify `effective_permissions`, and call `incorporation.check_entitlement` first.
2. Start or resume one case with a stable `idempotency_key`.
3. Let authorized project collaborators prepare only the shared ordinary-data draft. Replace the complete draft against the current `expected_version` and validate it.
4. Preview and explicitly confirm `incorporation.prepare_action_center` exactly once with unchanged arguments, key, and returned token.
5. Direct each person to their own Action Center. Each founder, officer, director, incorporator, signer, or responsible party supplies only their own private information and completes only their own Veriff, compliance, consent, and signature tasks.
6. Show collaborators only safe names, roles, statuses, and next actions. Participant-only access does not create project collaboration or filing authority.
7. Follow returned task-specific timing and use bounded `incorporation.get_case` readback. On an uncertain write, read the case again before using the original key.
8. Only the authorized owner previews and confirms `incorporation.submit_to_sparklaunch` to submit to SparkLaunch Filing Operations.

## Filing Boundary

Never call Delaware, NWRA, or CorpTools. Keep private fields and private Action Center URLs out of the conversation. Say: **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing or provider acceptance.
