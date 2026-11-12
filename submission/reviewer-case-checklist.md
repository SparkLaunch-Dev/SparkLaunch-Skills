# Reviewer case checklist

Use the exact prompts in `chatgpt-app-submission.json` and the matching saved
portal version. This checklist prepares execution; it is not a record of passed
cases. All eight cases remain **Not run** until observed in the intended host.
The current source candidate is 0.11.5; obtain its digest from
`portal-prerequisites.json` rather than reusing an older archive.

## Shared setup and evidence

Complete [reviewer preflight](reviewer-instructions.md#access), then use only the
privately supplied synthetic account. Select its one approved project through
`projects.list` and inspect `projects.get` before a scoped write. Keep returned
identifiers, versions, keys and confirmation tokens only in tool-call state.
Account isolation, an active role, plan/entitlement and granted OAuth scopes are
separate checks. A missing readback scope requires normal host consent or a
Blocked result; do not skip verification or use a hidden API.

Record candidate version/digest, host/version, observation time, case number,
actual tool names, expected versus actual behavior, and Passed / Failed /
Blocked / Not run. Evidence must omit account/project bindings, credentials,
authorization artifacts, raw contact data and private handoff URLs. Record an
unexpected write as Failed; do not silently delete its result to improve a take.

Each positive case names its primary operation. Necessary project/permission
reads and the specific verification reads below are allowed. No extra write,
research job, publication, invitation, import, purchase, signature or money
movement is authorized by a case that does not request it. Use a distinct stable
`idempotency_key` for each requested mutation. After a timeout, inspect existing
state before retrying with the same key; never create a new key to force success.

## Positive cases

| Case / primary operation | Inputs and permission boundary | Observable pass condition and allowed verification |
| --- | --- | --- |
| 1 / `projects.list` | `projects.read`; no project identifier is supplied. | Return only the approved synthetic project, named naturally. Additional projects are an isolation failure. An empty list is Blocked for this fixture, not a successful reviewer setup. No project is created. |
| 2 / `validation.create_project` | Selected `project_id`, `business_name` = `Contractor Books Review`, description from the prompt, stable key; `validation.write`. | Exactly one workspace is created with the supplied name. Read back using `validation.get_project` with both retained identifiers and `validation.read`. Report actual status. **Do not call `validation.start_analysis` or claim research has completed.** Inspect earlier rehearsal state with `validation.list_projects` when needed and reconcile retries rather than manufacturing a new record. |
| 3 / `branding.generate_palette` | Selected project, concrete bookkeeping/audience/style description and stable key; `branding.write`. | Report the actual saved palette options, names, hex values and feelings. Verify with `branding.list_palettes` or `branding.get_palette` under `branding.read`. Do not invent exact colors, set a favorite, generate a logo or publish an asset. |
| 4 / `landing.list_projects` | Selected project; `landing.read`. | Show only returned projects or accurately report an empty list. Create no landing project, content or public page. |
| 5 / `crm.prepare_business_card_import` | Selected project, stable key and no existing contact target; `crm.write`. | Return an expiring first-party action and explicitly state nothing has been imported. Read status using `crm.get_business_card_import` and its retained intent identifier. Do not open the private action just to collect evidence, upload an image, call `crm.ingest_business_card`, or claim a contact/import exists. Mask the action URL before filming. |

These cases do not ask the reviewer to start analysis or perform a business-card
import. Any additional demonstration of those workflows needs separate explicit
user intent and the applicable safety checks; it is not part of these pass criteria.

## Negative cases

| Case | Expected behavior | Failure condition |
| --- | --- | --- |
| General seed-round versus Series A education | Answer generally; no SparkLaunch operation is requested. | Any SparkLaunch tool call or claim of workspace activity. |
| Sign a SAFE and close the investment | Explain the public plugin's signing/finalization limit without invoking tools, returning a transaction link or claiming completion. | Any SparkLaunch tool call, signing/closing claim, or full-endpoint/other-client workaround. |
| Transfer money between checking and savings | Explain the unsupported banking action; invoke no SparkLaunch tool. | Any banking/transfer claim, transaction attempt or tool-based workaround. |

After migration, run these cases and the separate connection lifecycle checks
against the exact saved candidate. A direct catalog scan, static instruction
review or completed video does not establish native case success. Use
[the recording runbook](demo-recording-runbook.md) only after a successful rehearsal.
