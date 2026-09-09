# SparkClose: public-host policy review brief

Status: technical assessment prepared; platform/legal classification NOT APPROVED.
Scope: the sixteen `sparkclose.*` descriptors in the candidate snapshot, plus their
canonical skill, recipe and any first-party workflow links.

## Behavior to classify

The common backend separates unsaved SAFE calculations, saved planning scenarios,
private investment metadata, company-recorded evidence, reviewed unsigned agreement
preparation, first-party signing workflows, receipt reconciliation, and finalization of internal closing
state. The MCP tool does not itself transfer money or issue shares. That fact alone
does not determine whether a tool meaningfully enables a prohibited transaction.

| Surface | Concrete behavior / review question |
|---|---|
| Readiness, lists, reads, unsaved SAFE modeling | Planning and private information. Verify no individualized investment recommendation or transaction execution is implied. |
| Scenario/investment creation and updates | Saves private records with plan, project-role and scope checks. Review the intended downstream financing workflow, not just the absence of payment APIs. |
| Preview/prepare agreement | Accepts complete company-reviewed agreement text, validates selected source records, and saves one unsigned investment draft after exact confirmation. It creates or links an unsigned SAFE instrument but sends no signature request or document. Review this added preparation capability explicitly. |
| Record approval or receipt | Persists company assertions and supporting evidence; does not independently verify board authority, settlement or legal adequacy. Ensure descriptions never claim otherwise. |
| Reconcile funding | Checks company-recorded receipts against expected amounts; not bank verification or money movement. Review whether this operational step falls within the host's restricted-services boundary. |
| Close investment / retry updates / cancel unsigned | Changes consequential internal investment state and may update connected private CRM/document destinations; unsigned cancellation may void internal signature-envelope state. Review these exact side effects. |
| Open workflow | Returns an authenticated first-party workspace link, where review/signing may occur. A handoff is not an automatic exemption from host policy. |

The implementation requires separate permissions, live project access/plan checks,
current-version checks, stable retries and explicit confirmation for consequential
mutations. Those controls protect the operation; they are not policy approval.

## Decision required before public submission

Review against the current [OpenAI plugin guidelines](https://developers.openai.com/plugins/app-guidelines)
and [Claude connector requirements](https://claude.com/docs/connectors/building/submission).
OpenAI names execution of investment trades among restricted financial activities.
Do not equate every financial calculation with trade execution; assess the complete
workflow and first-party handoff rather than an isolated function name.

Record a reasoned approval for the exact surface, or identify which capabilities
must be excluded from a public-host profile. If filtering is required, implement it
server-side on a distinct reviewed endpoint and generate the matching descriptors,
skills, scopes and reviewer cases from the canonical source. Removing skill prose
alone does not remove callable tools. Do not silently fork backend business logic
or pretend a client-declared host identity is an authorization control.

Use only synthetic reviewer data and preserve the differences between model output,
saved records, company assertions, signed documents, bank settlement, securities
issuance, internal close state and customer acceptance in the demonstration.
