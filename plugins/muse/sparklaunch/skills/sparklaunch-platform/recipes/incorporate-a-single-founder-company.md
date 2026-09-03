---
title: Incorporate A Single-Founder Company
summary: Prepare one entitled founder's supported company case and internal Filing Operations receipt.
---

# Incorporate A Single-Founder Company

SparkLaunch service access begins at age 13. Users below their local age of majority need permission from a parent or legal guardian. Do not ask for age. Service access, Incorporation Package entitlement, and an internal Filing Operations receipt do not prove company formation, authority or capacity to sign, payment authorization or completion, identity-verification completion, regulatory eligibility, or provider eligibility.

## Steps

1. Select the project, verify `effective_permissions`, and call `incorporation.check_entitlement` first.
2. If entitled, call `incorporation.start_case` with one stable `idempotency_key`; retain `case_id` and `version`.
3. Read the case, then prepare the complete non-address ordinary-data draft. Pass exactly one source at the current `expected_version`: the closed structured `draft` object on any MCP host, or `draft_file` only when the host supplies a supported UTF-8 JSON file reference. Never put address or location fields in either input, tool responses, or conversation. The founder may hold the required founder and governance roles.
4. Validate the exact version and correct blocking ordinary fields without collecting private task data in chat.
5. Preview `incorporation.prepare_action_center`, wait for explicit approval, and use its confirmation token exactly once with unchanged arguments and key.
6. Direct the founder to their own Action Center for their address, private information, Veriff, consent, company business/mailing addresses when assigned, and signatures. Use returned task-specific timing and bounded status readback.
7. At `ready_to_submit`, preview and explicitly confirm `incorporation.submit_to_sparklaunch` to submit to SparkLaunch Filing Operations.
8. Retain the internal receipt. If a response is uncertain, read the case again before reusing the original key.

## Filing Boundary

Never call Delaware, NWRA, or CorpTools. Keep private fields out of the conversation. Say: **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing or formation.

Retain identifiers and versions only for internal tool calls; refer to the company, case, tasks, and receipt in human-readable terms.
