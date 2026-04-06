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

## Path Status

| Step | Status | Notes |
| --- | --- | --- |
| Project bootstrap | Verified working | Use the JWT control plane bootstrap route. |
| MCP runtime initialization | Working with caveats | `initialize` can succeed even when later tool calls lose session. |
| Validation via MCP | Working with caveats | Fast when healthy. |
| Validation via REST | Verified working | Async; poll until complete or timeout. |
| Business naming | Working with caveats | Payloads are stricter than the optimistic recipe suggested. |
| Palette via MCP | Working with caveats | Switch to REST fallback after one session retry. |
| Logo via MCP | Working with caveats | Switch to REST fallback after one session retry. |
| GTM plan | Working with caveats | Requires a fuller `inputs` body than the old recipe implied. |
| Landing create + draft patch + publish | Verified working | This is the known-good landing path. |
| Landing auto-generate content | Environment-dependent | Route exists in platform contracts, but some deployments may still need manual draft content. |

## Known-Good Transport

1. Bootstrap the project with REST before any runtime tool calls.
2. If MCP is healthy, use MCP for scoped runtime steps.
3. If a post-initialize MCP request returns `Session not found`, reinitialize once and retry once.
4. If the retry also fails, mark MCP as degraded in the final report and switch to the documented REST fallback for that step.
5. Do not keep retrying a broken MCP session beyond that point.

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

## Verified Request Bodies

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

### Verified Validation Create Body

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

### Verified Business Naming Body

```json
{
  "project_name": "Nimbus Ops Naming Sprint",
  "business_description": "AI operations assistant for busy service teams.",
  "industry": "operations software",
  "target_audience": "Owners and operators at home-service companies",
  "keywords": "automation, dispatch, scheduling, customer follow-up",
  "style_preferences": "credible, modern, efficient, not playful",
  "project_id": 123
}
```

### Verified Palette REST Fallback Fields

- `POST /api/branding/generate-palettes`
- multipart form data:
  - `generation_method=description`
  - `prompt=credible modern operations software brand for busy service teams`
  - `token=<JWT>`
  - optional `project_id=123`

### Verified Logo REST Fallback Body

```json
{
  "business_name": "Nimbus Ops",
  "attributes": "credible, modern, efficient, not playful",
  "prompt_style": "symbolic",
  "selected_colors": {
    "primary": "#0F4C81",
    "secondary": "#5FA8D3",
    "accent": "#F4B942"
  },
  "project_id": 123
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

### Verified Landing Create Body

```json
{
  "name": "Nimbus Ops Launch Page",
  "template_type": "saas",
  "product_name": "Nimbus Ops",
  "one_liner": "AI operations assistant for busy service teams.",
  "target_icp": "Owners and operators at home-service companies with small dispatch teams.",
  "cta_type": "waitlist",
  "project_id": 123
}
```

### Environment-Dependent Landing Generate Body

```json
{
  "product_name": "Nimbus Ops",
  "one_liner": "AI operations assistant for busy service teams.",
  "template_type": "saas",
  "cta_type": "waitlist",
  "project_id": 123
}
```

### Verified Landing Draft Patch Shape

```json
{
  "content_json": {
    "hero": {
      "headline": "Dispatch less. Follow up faster.",
      "subheadline": "Nimbus Ops automates intake, scheduling, and customer follow-up for busy service teams.",
      "cta_text": "Join the waitlist"
    }
  },
  "assets_manifest": {}
}
```

## Verified Working Path

1. Create the project with `POST /api/mcp/auth/bootstrap/project?token=<JWT>` and mint the first MCP key.
2. Try validation over MCP first; if the runtime degrades, switch to REST create + async analyze + poll.
3. Run naming through the JWT business-name routes using the fuller request body.
4. Try palette and logo over MCP if healthy; otherwise use the documented REST fallbacks.
5. Create the GTM plan through REST with a complete `inputs` body.
6. Create the landing project, patch draft content, publish, and fetch final state.
7. Return the founder report with artifact statuses and source labels.

## REST Fallback Order

1. Validation: `POST /api/validation/projects` -> `POST /analyze` -> `GET /projects/{id}` poll -> optional `POST /report`
2. Palette: `POST /api/branding/generate-palettes` -> `POST /api/branding/save-palette`
3. Logo: `POST /api/logos/?token=<JWT>` -> `POST /api/logos/{logo_id}/generate?token=<JWT>`
4. Landing content: if `landing.generate_content` is unavailable, patch manual `content_json` directly into the draft and publish

## Async Handling

1. Poll REST validation every 10 seconds for up to 8 minutes.
2. If still `analyzing` at timeout, return the project id, `analysis_run_id`, current status, and any export URL already available.
3. Do not block the entire founder report forever on an async validation run.

## Credible Framing Rule

Always choose the narrowest plausible wedge before generating names, GTM, or landing copy. Prefer concrete, believable positioning over hype. If the original idea is unusual, frame the first launch around the most credible user and use case rather than the broadest imaginable category.

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
  Include ids, URLs, report links, source labels, and status labels for every generated asset

## Failure Handling

- This recipe is allowed to complete partially.
- If MCP initialize succeeds but later tool calls fail with `Session not found`, switch to REST fallback and mark MCP degraded.
- If validation fails, stop the downstream brand, GTM, and landing work unless the user explicitly asks to continue without research.
- If validation is still analyzing at timeout, return a partial founder report and mark validation as `pending async generation`.
- If naming fails, preserve the current working name from bootstrap only when the user approved speed over completeness.
- If GTM fails, generate a manual GTM summary from project context and label it `manual fallback`.
- If landing content generation fails, write manual draft content and continue if the page can still be published credibly.
- If landing publish fails, keep the preview or draft state, include the generated content summary, and report the publish failure without pretending the page is live.
- Never expose internal traces or secret-bearing diagnostics. SparkLaunch already routes platform diagnostics to support Slack for these surfaces.

## Troubleshooting

- `Session not found` after successful `initialize`: likely runtime session instability. Reinitialize once, then stop using MCP for the affected step.
- `Please enter your full name.` during business naming or validation: likely generic validation wrapping. Re-check the request body keys and content type before assuming a literal founder-name field is missing.
- Validation stuck in `analyzing`: treat as partial completion, return `analysis_run_id`, and tell the user it is still running.
- GTM generic `400`: the payload is usually under-specified. Re-check `goal`, `project_id`, and the completeness of `inputs`.
- Landing generate `404`: continue with manual draft patch plus publish flow instead of failing the whole recipe.
