# Review a SparkCap cap table and model a raise

Use `sparklaunch-sparkcap` for planning cap tables, stakeholders, and modeled
ownership changes. Follow its host-managed OAuth, permission, privacy,
confirmation, and idempotency rules.

Retain identifiers and versions only for internal tool calls; use human-readable
names and omit identifier/version labels or columns from user-facing output.

1. Select an accessible project using `projects.list`; inspect its
   `effective_permissions` with `projects.get`.
2. Use `cap_table.list` with pagination and `cap_table.get` to select and read
   the intended planning table. Use names in conversation and retain identifiers
   and versions only as opaque internal tool-call state.
3. If a saved correction is requested, check `cap_table.get_usage`, prepare the
   appropriate write with a stable `idempotency_key` and current `expected_version`,
   show the returned `confirmation_required` preview, and wait for approval.
   Submit the same arguments/key with its confirmation token; read back success.
4. Collect raise amount and pre-money valuation for a priced round, or raise
   amount and valuation cap for a SAFE/note. Use whole USD and fractional
   discounts. Call `cap_table.simulate_raise` with the explicit project/table.
5. Compare actual current ownership with the returned unsaved projection.
   Use `cap_table.fully_diluted` only when `cap_table.model` is available.
6. State assumptions and explain that `saved: false` does not record financing,
   issue securities, or establish an official ledger. The result is a planning
   model, not legal, tax, or investment advice.

For stale or uncertain writes, use current readback and the skill's exact-key
recovery. Do not expose credentials, addresses, signatures, share tokens, or
private diagnostics. Advanced official, signature, sharing, and export work
continues in the first-party SparkLaunch cap-table workspace.
