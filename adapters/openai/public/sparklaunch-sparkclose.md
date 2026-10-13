---
name: sparklaunch-sparkclose
description: Model SAFE scenarios, save reviewed modeling snapshots, inspect financing readiness, and read private investment metadata in a connected SparkLaunch project. Signing, agreement preparation and investment finalization are unavailable through this public plugin.
---

# SparkClose planning and records

{{CONNECTION}}

Select the project with `projects.list`, inspect `projects.get` permissions and
pass its explicit `project_id` to every scoped tool. Keep identifiers, hashes,
versions and confirmation tokens only as internal tool-call state. Refer to
records by their names in every user-facing report and confirmation.

Use `sparkclose.readiness` for issue metadata, `sparkclose.list_investments` and
`sparkclose.get_investment` for private investment milestones, and
`sparkclose.list_scenarios` and `sparkclose.get_scenario` for saved models.
Paginate inventories and select existing records; never invent identifiers.

Select an existing cap table through `cap_table.list`. Use `sparkclose.model_safe`
for supported USD post-money valuation-cap SAFE exposure estimates. Report the
server's assumptions, inclusion filter, pool dilution, warnings and limits.
Supply priced-round amount and valuation together. A model does not issue shares,
verify legal adequacy or complete a financing.

Save only when requested, using `sparkclose.save_scenario` with the unchanged
model input and its `source_version` as `expected_source_version`. Use one stable
idempotency key for the exact mutation. Show a returned confirmation preview and
wait for explicit approval before replaying the same arguments and key with its
confirmation token. Read back the saved scenario. Disclose stale snapshots;
remodel instead of silently rewriting them. Reconcile uncertain writes before retrying.

Reads require read consent; modeling requires model consent; saving requires
read, model and write consent. If the connection lacks a required permission,
reconnect through ChatGPT and approve the named scope. Distinguish an explicit
plan or role denial from missing OAuth consent. Never call a write to diagnose access.

Agreement preparation, signing, funding evidence changes, cancellation,
reconciliation, investment finalization and recovery of closing updates are
outside this public plugin. For such requests, explain the limit without invoking
a tool, producing a transaction link or claiming completion. Do not use hidden
REST routes, the full MCP endpoint or another client to bypass this boundary.
