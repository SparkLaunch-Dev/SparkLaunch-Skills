---
id: recipe-validation-001
title: Validate An Idea And Generate A Report
summary: Create a project-scoped validation record, run analysis, and return a founder-facing validation summary with optional PDF export.
auth: sparklaunch_jwt_optional, project_scoped_mcp_api_key
surfaces: mcp, rest
outputs: validation_project, analysis_results, validation_report_optional
---

# Validate An Idea And Generate A Report

## When To Use

Use this recipe when the user wants structured market, competitor, and TAM or SAM or SOM analysis for an existing SparkLaunch project.

## Credentials

- Project-scoped MCP API key with `validation.read` and `validation.write`
- Optional SparkLaunch JWT if the caller wants the PDF report export

## User Prompt

`Validate this startup idea for my current project and give me a concise report with the strongest risks and next actions.`

## Workflow

1. Confirm the MCP key is scoped to the correct SparkLaunch project.
2. Create the validation workspace with `validation.create_project`.
3. Run the full analysis with `validation.start_analysis(validation_project_id, sections="all")`.
4. Fetch the completed record with `validation.get_project`.
5. If the user wants a downloadable report and a SparkLaunch JWT is available, call `POST /api/validation/projects/{validation_project_id}/report?token=<JWT>`.
6. Summarize the output into a founder-ready report, not raw JSON.

### Recommended MCP Call Shape

```json
{
  "business_name": "Nimbus Ops",
  "business_description": "AI operations assistant for busy service teams.",
  "target_market": "US home-service businesses with small dispatch teams.",
  "business_model": "SaaS subscription",
  "unique_value_proposition": "Automates intake, scheduling, and customer follow-up from one workflow."
}
```

## Output Contract

Return:

- validation project id and status
- strongest market takeaway
- strongest competitor takeaway
- most credible TAM or SAM or SOM signal
- top 3 risks or unknowns
- top 3 downstream next steps
- report download URL if generated

## Failure Handling

- If analysis fails, return the platform’s friendly error and note whether the validation workspace was still created.
- If the report export fails after analysis succeeded, keep the analysis result and mark the PDF as optional follow-up.
- Never expose internal model, stack, or database details in the user-facing recap.
