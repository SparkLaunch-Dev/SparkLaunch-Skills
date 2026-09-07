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
4. Use `sparkclose.open_workflow` for complete agreement review, preparation,
   signatures or external signed-SAFE import. The user performs these actions
   in SparkLaunch; the handoff itself has completed none of them.
5. Find the resulting investment with `sparkclose.list_investments` and
   `sparkclose.get_investment`. Record approval only after company review of the
   selected evidence. Record receipts only after company confirmation of money
   received, then reconcile. No tool transfers money or verifies bank settlement.
6. Before every write, read its current investment version and use one stable
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
