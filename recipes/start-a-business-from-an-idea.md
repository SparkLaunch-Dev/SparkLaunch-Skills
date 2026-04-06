---
id: recipe-founder-001
title: Start A Business From An Idea
summary: Bootstrap a project, validate the idea, generate name and brand assets, create a GTM plan, create and publish a landing page, and return a founder-ready report.
auth: sparklaunch_jwt, project_scoped_mcp_api_key_created_during_recipe
surfaces: rest, mcp
outputs: project, validation, business_name_shortlist, palette, logo, gtm_plan, landing_page, founder_report
---

# Start A Business From An Idea

## When To Use

Use this recipe when the user says some version of: `I want to start a business and here is my idea: {idea}` and expects SparkLaunch to turn that into an actual project plus launch assets.

## Credentials

- SparkLaunch JWT to bootstrap the project and call the current business-name, GTM, validation-report, and landing-draft REST routes
- No existing MCP key is required because this recipe should create one during bootstrap

## User Prompt

`I'd like to start a business and here is my idea: {idea}. Create the project, validate it, make a name, make a color palette, make a logo, make a GTM, make a landing page, and give me a report when you're done.`

## Workflow

1. Bootstrap the SparkLaunch project.
   - Call `POST /api/mcp/auth/bootstrap/project?token=<JWT>`.
   - Include `mcp_api_key` so the same request returns the first scoped MCP token.
   - Recommended scopes:
     `projects.read`, `projects.write`, `validation.read`, `validation.write`, `branding.read`, `branding.write`, `logos.write`, `landing.read`, `landing.write`
2. Initialize the MCP session against `/api/mcp/`.
3. Run idea validation.
   - `validation.create_project`
   - `validation.start_analysis(validation_project_id, sections="all")`
   - `validation.get_project`
   - Optional PDF export: `POST /api/validation/projects/{validation_project_id}/report?token=<JWT>`
4. Generate business names.
   - `POST /api/business-names/projects?token=<JWT>`
   - `POST /api/business-names/projects/{business_name_project_id}/generate?token=<JWT>`
   - Check the strongest candidates with `POST /api/domains/check-for-name`
   - Pick a recommended final name and explain why it won.
   - Optional PDF export: `POST /api/business-names/projects/{business_name_project_id}/report?token=<JWT>`
5. Generate the color palette.
   - `branding.generate_palette(description=...)`
   - Choose one palette and keep its id plus hex values.
6. Generate the logo.
   - `crm.generate_logo(business_name=chosen_name, attributes=..., prompt_style="symbolic", selected_colors={...})`
7. Build the GTM plan.
   - `GET /api/gtm/project-context?project_id={project_id}&token=<JWT>`
   - `POST /api/gtm/plans?token=<JWT>`
   - Optional export: `GET /api/gtm/plans/{gtm_plan_id}/export?format=markdown&token=<JWT>`
8. Create the landing page.
   - `landing.create_project`
   - `landing.generate_content`
   - Persist the generated content with `PATCH /api/landing-pages/projects/{landing_project_id}/versions/draft?token=<JWT>`
   - Publish with `landing.publish`
   - Confirm the live state with `landing.get_project`
9. Produce the final founder report using [templates/founder-workflow-report.md](./templates/founder-workflow-report.md).

### Example Bootstrap Body

```json
{
  "name": "Nimbus Ops",
  "one_liner": "AI operations assistant for busy service teams.",
  "business_description": "Nimbus Ops helps service businesses automate intake, scheduling, and customer follow-up.",
  "industry": "operations software",
  "stage": "idea",
  "mcp_api_key": {
    "name": "Founder Launch Recipe Key",
    "scopes": [
      "projects.read",
      "projects.write",
      "validation.read",
      "validation.write",
      "branding.read",
      "branding.write",
      "logos.write",
      "landing.read",
      "landing.write"
    ]
  }
}
```

### Example GTM Body

```json
{
  "project_id": 123,
  "goal": "launch_mvp",
  "inputs": {
    "product_description": "AI operations assistant for busy service teams.",
    "target_user_hypothesis": "Owners and operators at home-service companies with small dispatch teams.",
    "problem_and_benefit": "Manual intake and scheduling wastes time; the product automates follow-up and routing.",
    "business_model": "SaaS subscription",
    "launch_timeline": "this_month",
    "primary_constraint": "time",
    "stage": "idea",
    "conversion_goal": "email_signups"
  }
}
```

## Output Contract

Return a single founder-ready report with these sections:

- Executive summary
- Project created
- Validation summary
- Recommended business name and domain signal
- Selected palette
- Logo direction
- GTM priorities
- Landing page status
- Risks and open questions
- Recommended next 7-day actions
- Artifact inventory
  Include ids, URLs, and report links for every generated asset

## Failure Handling

- This recipe is allowed to complete partially.
- If validation fails, stop the downstream brand, GTM, and landing work unless the user explicitly asks to continue without research.
- If naming fails, keep validation outputs and explain that brand-generation steps are blocked on a chosen name.
- If GTM fails, still finish the landing page only if the user asked for speed over planning; otherwise stop at brand completion.
- If landing publish fails, keep the preview or draft state, include the generated content summary, and report the publish failure without pretending the page is live.
- Never expose internal traces or secret-bearing diagnostics. SparkLaunch already routes platform diagnostics to support Slack for these surfaces.
