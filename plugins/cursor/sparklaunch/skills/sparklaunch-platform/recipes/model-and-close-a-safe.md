---
title: Model and close a SAFE
summary: Save a SAFE model, prepare a reviewed unsigned agreement, and close an evidenced investment.
---

# Model and close a SAFE

Use `sparklaunch-sparkclose`. Follow the [shared rules](./README.md#shared-rules)
for host-managed OAuth, project selection, privacy and confirmed writes.

1. Select the project and inspect effective permissions. Review
   `sparkclose.readiness`; readiness is not legal approval or a completed closing.
2. Find the cap table and use `sparkclose.model_safe` with the founder's proposed
   USD post-money cap allocations. Explain existing exposure, inclusion filters,
   priced-round and pool assumptions. Do not claim issued shares.
3. If requested, save a confirmed snapshot with `sparkclose.save_scenario` using
   the source version just modeled. Preserve old snapshots and disclose staleness.
4. With complete company-reviewed agreement text and selected same-project
   investor deal and private packet, use `sparkclose.preview_agreement`, then
   confirm `sparkclose.prepare_agreement` with identical inputs and its returned
   version. This saves an unsigned draft. If content or explicit review is
   unavailable, use `sparkclose.open_workflow`. Signing and external signed-SAFE
   import happen in SparkLaunch; opening a link completes neither action.
5. Find the resulting investment with `sparkclose.list_investments` and
   `sparkclose.get_investment`. Record approval only after company review of the
   selected evidence. Record receipts only after company confirmation of money
   received, then reconcile. No tool transfers money or verifies bank settlement.
6. Before changing an existing investment, read its current version. For every
   write use one stable
   idempotency key. Present the returned confirmation preview by human-readable
   names; wait for approval and replay the identical arguments/key with the
   confirmation token. On changed evidence, start a fresh read and review.
7. With all service gates satisfied and the separate close permission available,
   confirm `sparkclose.close_investment` for that single investment. Do not
   equate signing, funding and closing or close the rest of the round implicitly.
8. Read back the outcome and destination update statuses. Retry incomplete
   updates through `sparkclose.retry_updates` after confirmation. Preserve the
   existing events and verify relevant SparkCap, SparkRoom and investor records
   through their read tools when available. Report remaining verification gaps.

Use the first-party workflow for corrections. Never cancel a signed investment,
collect banking credentials, infer document review from titles or expose internal
identifiers, source versions, hashes, private documents or signer details.

Retain identifiers and versions only for internal tool calls. Use human-readable names in every report and confirmation.

If an effective permission is absent, do not infer a plan restriction. An
`insufficient_scope` response requires reconnecting SparkLaunch through the host
and approving the requested permissions. Saving requires SparkClose read, model
and write access; preparation requires read and write. A confirmed plan or role
denial has its own entitlement or membership remedy.
