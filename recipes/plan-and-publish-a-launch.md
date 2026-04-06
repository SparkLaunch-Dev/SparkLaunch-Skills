---
id: recipe-launch-001
title: Plan And Publish A Launch
summary: Create a GTM plan, generate landing-page content, save the draft, and publish a project landing page.
auth: sparklaunch_jwt, project_scoped_mcp_api_key
surfaces: rest, mcp
outputs: gtm_plan, landing_project, landing_draft, published_url
---

# Plan And Publish A Launch

## When To Use

Use this recipe when the user has a project and wants to move from strategy into a public landing page.

## Credentials

- SparkLaunch JWT for GTM and landing-page draft persistence
- Project-scoped MCP API key with `landing.read` and `landing.write`

## User Prompt

`Build me a launch plan for this project and publish a landing page I can start sharing.`

## Workflow

1. Pull GTM context with `GET /api/gtm/project-context?project_id={project_id}&token=<JWT>`.
2. Create the GTM plan with `POST /api/gtm/plans?token=<JWT>`.
3. Optionally export the plan with `GET /api/gtm/plans/{gtm_plan_id}/export?format=markdown&token=<JWT>`.
4. Create the landing project with `landing.create_project`.
5. Generate structured landing content with `landing.generate_content`.
6. Persist the generated content into the landing draft with `PATCH /api/landing-pages/projects/{landing_project_id}/versions/draft?token=<JWT>`.
7. Publish the landing page with `landing.publish` or `POST /api/landing-pages/projects/{landing_project_id}/publish?token=<JWT>`.
8. Fetch the final published state with `landing.get_project`.

## Path Status

- GTM plan create: `Working with caveats`
- Landing create + draft patch + publish: `Verified working`
- Landing auto-generate content route: `Environment-dependent`
- Manual draft patch without generated content: `Manual fallback allowed`

### Example GTM Plan Body

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

## Known-Good Execution Order

1. Build or fetch GTM context first.
2. Create the landing project.
3. If `landing.generate_content` works, patch the returned content into the draft.
4. If `landing.generate_content` is unavailable or returns `404`, write a manual `content_json` draft and continue.
5. Publish only after a successful draft patch.

## Output Contract

Return:

- GTM plan id and goal
- strongest 3 GTM priorities
- exported markdown path or inline summary if export was requested
- landing project id
- preview URL
- production URL if published
- publish status
- artifact status labels for GTM and landing page

## Failure Handling

- If GTM fails, provide a manual GTM summary from project context and label it `manual fallback` instead of returning nothing.
- If GTM succeeds but landing fails, preserve the GTM plan and report launch-page work as blocked.
- If landing content generation succeeds but draft persistence fails, keep the generated content in the response so the user can retry the save step without regenerating.
- If publish fails, return the preview URL and draft status instead of pretending the page is live.

## Troubleshooting

- GTM `400` with limited detail: re-check that `project_id`, `goal`, and `inputs` are all present and that the inputs describe a coherent launch stage.
- Landing generate `404`: treat the generate route as deployment-mismatched and continue with a manual draft patch.
- Publish failure after draft save: keep the draft and preview URL in the final report rather than collapsing the whole workflow.
