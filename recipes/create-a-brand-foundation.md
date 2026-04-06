---
id: recipe-brand-001
title: Create A Brand Foundation
summary: Generate a naming shortlist, pressure-test domains, create color palettes, and generate a logo for the active business concept.
auth: sparklaunch_jwt, project_scoped_mcp_api_key
surfaces: rest, mcp
outputs: business_name_project, domain_check, palette, logo
---

# Create A Brand Foundation

## When To Use

Use this recipe when the user wants to turn a rough startup brief into a name shortlist, palette direction, and first-pass logo.

## Credentials

- SparkLaunch JWT for business naming and optional business-name report export
- Project-scoped MCP API key with `branding.read`, `branding.write`, and `logos.write`

## User Prompt

`Create a brand foundation for this startup: generate names, check domains, make a palette, and give me a first logo direction.`

## Workflow

1. Create a business-name project with `POST /api/business-names/projects?token=<JWT>`.
2. Generate the naming shortlist with `POST /api/business-names/projects/{business_name_project_id}/generate?token=<JWT>`.
3. Check the strongest 3 to 5 candidates with `POST /api/domains/check-for-name`.
4. Choose one recommended name, explicitly noting whether the decision is based on brand fit, domain availability, or both.
5. Generate palettes with `branding.generate_palette`.
6. Pick the strongest palette from the returned options and pass its colors into `crm.generate_logo`.
7. Optionally create a business-name PDF report with `POST /api/business-names/projects/{business_name_project_id}/report?token=<JWT>`.

### Example Business Naming Body

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

### Example Domain Check Body

```json
{
  "business_name": "Nimbus Ops",
  "tlds": [".com", ".ai", ".co", ".io"]
}
```

## Output Contract

Return:

- business-name project id
- generated name shortlist
- recommended final name with domain-check result
- selected palette id and hex values
- logo id and image delivery fields
- business-name report URL if generated

## Failure Handling

- Naming and domain steps can fail independently; keep successful outputs instead of restarting the whole recipe.
- If palette generation succeeds but logo generation fails, preserve the chosen palette and ask whether to retry the logo with a narrower prompt.
- Keep the user-safe platform error text intact and note that SparkLaunch already routed diagnostics to support.
