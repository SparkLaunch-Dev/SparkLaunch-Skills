---
title: Recover Incorporation Entitlement
summary: Check the authoritative package state and guide safe purchase recovery without creating a case prematurely.
---

# Recover Incorporation Entitlement

## Steps

1. Select the project, verify `effective_permissions`, and call `incorporation.check_entitlement` first.
2. Treat the returned entitlement status as authoritative. Do not treat a browser page, user statement, email, or purchase URL as proof.
3. When missing, present the returned package price, reason, and project-bound purchase action. Do not perform checkout or collect payment data in chat.
4. After the user completes recovery outside the MCP call, call `incorporation.check_entitlement` again. Start a case only when the returned state allows it, using a stable `idempotency_key`.
5. For `payment_pending`, `disputed`, `revoked`, or another blocked state, use the returned task-specific timing and recovery action. Do not blind-retry a write; read the case again after uncertainty.

## Filing Boundary

Never call Delaware, NWRA, or CorpTools. Keep private and payment fields out of the conversation. Any later confirmed action can only submit to SparkLaunch Filing Operations. **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing.
