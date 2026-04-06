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

## Output Contract

Return:

- GTM plan id and goal
- strongest 3 GTM priorities
- exported markdown path or inline summary if export was requested
- landing project id
- preview URL
- production URL if published
- publish status

## Failure Handling

- If GTM succeeds but landing fails, preserve the GTM plan and report launch-page work as blocked.
- If landing content generation succeeds but draft persistence fails, keep the generated content in the response so the user can retry the save step without regenerating.
- If publish fails, return the preview URL and draft status instead of pretending the page is live.
