---
title: Check Incorporation Entitlement
summary: Check the authoritative package state without exposing or facilitating a purchase through the connected agent.
---

# Check Incorporation Entitlement

## Steps

1. Select the project, verify `effective_permissions`, and call `incorporation.check_entitlement` first.
2. Treat the returned entitlement status as authoritative. Do not treat a browser page, user statement, email, or purchase result as proof.
3. When access is missing, state only the returned reason and that purchasing is unavailable through the connected agent package. Do not provide a price, purchase link, checkout action, purchasing instructions, or collect payment data.
4. SparkLaunch web and mobile retain their separate first-party account and purchase workflows. Do not open, invoke, or describe those workflows from the connected agent.
5. If the account state later changes, call `incorporation.check_entitlement` again. Start a case only when the returned state allows it, using a stable `idempotency_key`.
6. For `payment_pending`, `disputed`, `revoked`, or another blocked state, use only the returned task-specific timing. Do not blind-retry a write; read the case again after uncertainty.

## Filing Boundary

Never call Delaware, NWRA, or CorpTools. Keep private and payment fields out of the conversation. Any later confirmed action can only submit to SparkLaunch Filing Operations. **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing.

Retain identifiers and versions only for internal tool calls; refer to the project, entitlement, case, and receipt in human-readable terms.
