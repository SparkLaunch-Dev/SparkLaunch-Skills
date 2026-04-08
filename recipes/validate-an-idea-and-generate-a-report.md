---
id: recipe-validation-001
title: Validate An Idea And Generate A Report
summary: Create a project-scoped validation record, run analysis, wait for completion when downstream assets depend on it, and return a founder-facing validation summary with optional PDF export.
auth: sparklaunch_jwt_optional, project_scoped_mcp_api_key
surfaces: mcp, rest
outputs: validation_project, analysis_results, validation_report_optional
---

# Validate An Idea And Generate A Report

## When To Use

Use this recipe when the user wants structured market, competitor, and TAM or SAM or SOM analysis for an existing SparkLaunch project.

## Credentials

- Project-scoped MCP API key with `validation.read` and `validation.write`
- Optional SparkLaunch JWT if the caller wants the PDF report export or needs the REST fallback path

## User Prompt

`Validate this startup idea for my current project and give me a concise report with the strongest risks and next actions.`

## Workflow

1. Confirm the MCP key is scoped to the correct SparkLaunch project.
2. Create the validation workspace with `validation.create_project` or `POST /api/validation/projects?token=<JWT>`.
3. Start analysis.
   - MCP: `validation.start_analysis(validation_project_id, sections="all")`
   - REST: `POST /api/validation/projects/{validation_project_id}/analyze?token=<JWT>`
4. Fetch the completed record with `validation.get_project` or `GET /api/validation/projects/{validation_project_id}?token=<JWT>`.
5. If the user wants a downloadable report and a SparkLaunch JWT is available, call `POST /api/validation/projects/{validation_project_id}/report?token=<JWT>`.
6. Summarize the output into a founder-ready report, not raw JSON.

## Path Status

- MCP create + analyze path: `Working with caveats`
- REST create + analyze + poll path: `Verified working`
- PDF export: `Verified working`

## Known-Good Transport

1. Start with MCP if the runtime is healthy.
2. If any post-initialize MCP call returns `Session not found`, reinitialize once and retry once.
3. If it still fails, switch to the REST fallback path below and mark MCP as degraded in the final report.
4. Note the semantic difference: MCP analysis is expected to return completed sections inline, while REST analysis starts an async run that must be polled.
5. If this validation result is a blocking dependency for a larger founder workflow, wait for completion before continuing into naming, brand, QR, or landing work.

## Verified Request Bodies

### MCP Create Call Shape

```json
{
  "business_name": "Nimbus Ops",
  "business_description": "AI operations assistant for busy service teams.",
  "target_market": "US home-service businesses with small dispatch teams.",
  "business_model": "SaaS subscription",
  "unique_value_proposition": "Automates intake, scheduling, and customer follow-up from one workflow."
}
```

### REST Create Body

```json
{
  "business_name": "Nimbus Ops",
  "business_description": "AI operations assistant for busy service teams.",
  "target_market": "US home-service businesses with small dispatch teams.",
  "business_model": "SaaS subscription",
  "unique_value_proposition": "Automates intake, scheduling, and customer follow-up from one workflow.",
  "project_id": 123
}
```

### REST Analyze Body

```json
{
  "deep_research": false
}
```

### REST Analyze Response Excerpt

```json
{
  "status": "analyzing",
  "analysis_run_id": "run_abc123",
  "market_analysis": null,
  "competitor_analysis": null,
  "tam_sam_som": null
}
```

## REST Fallback Path

1. `POST /api/validation/projects?token=<JWT>` with the REST create body.
2. `POST /api/validation/projects/{validation_project_id}/analyze?token=<JWT>` with `{ "deep_research": false }`.
3. Poll `GET /api/validation/projects/{validation_project_id}?token=<JWT>` every 15 seconds.
4. Use an 8-minute timeout for standalone validation work.
5. Use a 20-minute timeout when validation is the blocking first step in a founder workflow.
6. Stop polling early if the project returns completed analysis fields.
7. If still analyzing at timeout, return the `validation_project_id`, `analysis_run_id`, current status, and any report URL that was already generated.

## Output Contract

Return:

- validation project id and status
- strongest market takeaway
- strongest competitor takeaway
- most credible TAM or SAM or SOM signal
- top 3 risks or unknowns
- top 3 downstream next steps
- report download URL if generated
- artifact status label for validation: `platform-generated`, `pending async generation`, or `failed`

## Failure Handling

- If MCP initialize succeeds but tool calls later lose session, stop retrying after one reinit and switch to REST.
- If analysis fails, return the platform's friendly error and note whether the validation workspace was still created.
- If the analysis is still running after timeout, treat it as partial success instead of hard failure.
- If this validation is blocking a larger founder workflow, do not claim downstream artifacts are validated unless the validation actually completed.
- If the report export fails after analysis succeeded, keep the analysis result and mark the PDF as optional follow-up.
- Never expose internal model, stack, or database details in the user-facing recap.

## Troubleshooting

- `Please enter a business name.`: `business_name` is operationally required even if a caller assumed bootstrap data would infer it.
- `Please describe your business.`: `business_description` is missing or empty.
- `Please enter your full name.`: this can be a generic validation wrapper, not a literal founder-name requirement. Re-check request field names, aliases, and content type before changing the workflow.
