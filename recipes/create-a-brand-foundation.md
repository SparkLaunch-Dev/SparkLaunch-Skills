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

## Path Status

- Business-name project create + generate: `Working with caveats`
- Domain check: `Verified working`
- Palette generation via MCP: `Working with caveats`
- Palette generation via REST fallback: `Verified working`
- Logo generation via MCP: `Working with caveats`
- Logo generation via REST fallback: `Verified working`
- Manual brand recommendation: `Manual fallback allowed`

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

### Example Naming Generate Response Excerpt

```json
{
  "project_id": 456,
  "status": "completed",
  "generated_names": [
    "Nimbus Ops",
    "DispatchPilot",
    "FieldCurrent"
  ]
}
```

### Example Domain Check Body

```json
{
  "business_name": "Nimbus Ops",
  "tlds": [".com", ".ai", ".co", ".io"]
}
```

### Verified Palette REST Fallback

Use `POST /api/branding/generate-palettes` as multipart form data with:

- `generation_method`: `description`
- `prompt`: concise aesthetic brief
- `token`: SparkLaunch JWT
- optional `project_id`

Save the chosen result with `POST /api/branding/save-palette?token=<JWT>`.

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

## Operating Notes

1. Treat naming payload fields as stricter than the current public recipe implies. In practice, `project_name` and `business_description` should both be present.
2. If the first naming request fails with a generic validation message, confirm field names and aliases before changing strategy.
3. If MCP is degraded after initialization, skip straight to the documented REST fallback for palettes or logos instead of repeating MCP retries.
4. Keep a credible framing layer. Prefer the narrowest plausible market wedge and a believable promise over hype.

## Output Contract

Return:

- business-name project id
- generated name shortlist
- recommended final name with domain-check result
- selected palette id and hex values
- logo id and image delivery fields
- business-name report URL if generated
- artifact status labels for naming, palette, and logo

## Failure Handling

- Naming and domain steps can fail independently; keep successful outputs instead of restarting the whole recipe.
- If naming fails, preserve the current working business name from bootstrap or validation only if the user approved continuing without a generated shortlist.
- If palette generation succeeds but logo generation fails, preserve the chosen palette and retry through the REST logo path before falling back to a manual logo concept.
- If both platform palette paths fail, provide a manual palette direction labeled `manual fallback`.
- Keep the user-safe platform error text intact and note that SparkLaunch already routed diagnostics to support.

## Troubleshooting

- `Please enter your full name.`: likely generic validation wrapping. Re-check the business-name payload shape before assuming a founder-name field is needed.
- Empty or generic name list: tighten `industry`, `target_audience`, `keywords`, and `style_preferences` rather than blindly regenerating.
- Palette MCP session errors: use the multipart REST fallback and save the selected palette explicitly.
