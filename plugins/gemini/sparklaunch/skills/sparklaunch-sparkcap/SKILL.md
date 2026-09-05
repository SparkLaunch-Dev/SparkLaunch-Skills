---
name: sparklaunch-sparkcap
description: >
  Use when a connected SparkLaunch user wants to manage SparkCap planning cap
  tables or stakeholders, inspect ownership and plan usage, or model dilution,
  fundraising, and hiring through cap_table tools. Do not use for generic equity
  advice without SparkLaunch data or for executing legal securities workflows.
---

# SparkCap

Manage planning cap tables and model ownership using the connected SparkLaunch app.

## Connection and project

<!-- sparklaunch:connection:start -->
1. Use the OAuth connection managed by Gemini CLI. Never request or accept access tokens, refresh tokens, API keys, client secrets, authorization codes, or transport headers.
2. If the SparkLaunch tools are absent, stop before planning or claiming execution. Ask the user to link or enable the SparkLaunch extension, restart Gemini CLI, and verify the server with `/mcp`.
3. If a protected action returns an OAuth challenge, ask the user to run `/mcp auth sparklaunch`, then retry only after Gemini CLI reports success. Never use a pasted token as a fallback.
4. If authorization is expired or revoked, stop before any write, ask the user to run `/mcp auth sparklaunch` again, and check the target before retrying an uncertain operation.
<!-- sparklaunch:connection:end -->

Use `projects.list` to select an accessible project and `projects.get` to inspect
`effective_permissions`. Pass its explicit `project_id` to every SparkCap call.
Keep project, table, stakeholder identifiers and version values only as internal tool-call state.
Never show identifier/version values, labels, or columns to the
user; use project, cap-table, and stakeholder names.

## Select the supported operation

| Intent | Tools | Permission |
| --- | --- | --- |
| Find tables and read ownership | `cap_table.list`, `cap_table.get` | `cap_table.read` |
| Inspect table and stakeholder limits | `cap_table.get_usage` | `cap_table.read` |
| Create or edit a planning table | `cap_table.create`, `cap_table.update` | `cap_table.write` |
| Add or change planning stakeholders | `cap_table.create_stakeholder`, `cap_table.update_stakeholder` | `cap_table.write` |
| Remove a stakeholder or table | `cap_table.delete_stakeholder`, `cap_table.delete` | `cap_table.write` |
| Preview dilution and a proposed round | `cap_table.dilution_preview`, `cap_table.simulate_raise` | `cap_table.read` |
| Model fully diluted ownership | `cap_table.fully_diluted` | `cap_table.model`, Startup+ |
| Model engineering-hire equity/runway | `cap_table.hiring_impact` | `cap_table.scenarios`, Growth+ |

Page through `cap_table.list` when necessary; do not interpret the first page as
the complete inventory. `cap_table.get` includes stakeholders, current ownership
summary, and the opaque `version`. Usage limits of `-1` mean unlimited. A plan or
project-role denial does not mean the OAuth connection needs to be restarted.

## Save a planning change

1. Use current readback and the user's requested changes. Check usage before
   creating a table or stakeholder. Request only missing ordinary planning data.
2. Use one stable `idempotency_key` for each exact write. Creating an empty draft
   needs no extra server confirmation. All writes to an existing table require
   the latest `version` as `expected_version` and an exact confirmation preview.
3. On `confirmation_required`, show the preview's named target, before/after
   changes, and effect. Wait for explicit approval, then resubmit the same
   arguments and idempotency key with the returned `confirmation_token`.
4. On stale version, read the table again and review a newly prepared change;
   do not automatically force the original edit onto changed ownership data.
5. An uncertain write requires readback and, where appropriate, same-key retry.
   Never issue a fresh key merely because the response was lost. Read the table
   after success; list tables after deletion or uncertain creation.

Stakeholder changes are patches: omit fields that should remain unchanged.
Use whole-share counts. Monetary inputs are whole USD, and `discount_rate` is a
fraction (`0.20` is 20%). Vesting dates use `YYYY-MM-DD`; vesting durations use
months. Dedicated address, signature, identity, execution-status, and freeform
note inputs are not supported through this skill. Do not request sensitive
identity, address, banking, tax, or signature data in the conversation.

Deleting a table also removes associated records and stops existing shared
access. Include that effect in the confirmation. Planning edits do not issue
securities, execute a SAFE/note, sign documents, or establish an official ledger.

## Model and explain

For a priced raise, obtain a positive raise amount and pre-money valuation.
For a SAFE/note, obtain a positive raise amount and valuation cap; make any
discount explicit. Fully diluted calculations may use the existing service's
default conversion valuation; state the valuation actually returned.

Model tools return `saved: false`. Explain assumptions and compare current with
projected ownership, keeping modeled results separate from saved holdings,
executed financing, signed grants, and official records. Hiring uses the
existing stage/level benchmarks, not a company-specific salary forecast. Do not
present these planning calculations as legal, tax, or investment advice.

For official-ledger administration, migration review, signatures, proof/wallet
work, compliance, exports, or public sharing, direct the user to the selected
cap table in SparkLaunch. Those actions are not exposed by these tools. Never
substitute hidden REST calls or claim that a handoff completed the workflow.

## Output

Report the named cap table, what was saved or modeled, key ownership changes,
assumptions, and any needed first-party action. Omit internal references,
private diagnostics, dedicated addresses, and share tokens.
