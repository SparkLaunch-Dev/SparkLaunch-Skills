---
id: recipe-brand-001
title: Create A Brand Foundation
summary: Generate a naming shortlist, pressure-test domains, create and persist a favorite palette, and generate and favorite a logo for the active business concept.
auth: sparklaunch_jwt, user_scoped_mcp_api_key
surfaces: rest, mcp
outputs: business_name_project, domain_check, palette, logo
---

# Create A Brand Foundation

## When To Use

Use this recipe when the user wants to turn a rough startup brief into a name shortlist, domain signal, palette direction, and first-pass logo.

## Credentials

- SparkLaunch JWT for business naming, domain checks, palette save/favorite, logo favorite, and optional business-name report export
- User-scoped MCP API key with `branding.read`, `branding.write`, and `logos.write` (one key works across all of the caller's projects; see [create-a-user-scoped-mcp-key.md](./create-a-user-scoped-mcp-key.md))
- Send `X-SparkLaunch-Project-Id: <project_id>` on every `/api/mcp/` tool call to target this project

## User Prompt

`Create a brand foundation for this startup: generate names, check domains, make a palette, save the right one, and give me a first logo direction.`

## Workflow

1. Create a business-name project with `POST /api/business-names/projects?token=<JWT>`.
2. Generate the naming shortlist with `POST /api/business-names/projects/{business_name_project_id}/generate?token=<JWT>`.
3. Check the strongest 3 to 5 candidates with `POST /api/domains/check-for-name`.
4. Choose one recommended name, explicitly noting whether the decision is based on brand fit, domain availability, or both.
5. Generate palettes with `branding.generate_palette` when MCP is healthy.
6. If using REST fallback, call `POST /api/branding/generate-palettes`, then explicitly save the selected palette with `POST /api/branding/save-palette?token=<JWT>`.
7. Mark the chosen palette favorite with `POST /api/branding/palettes/{palette_id}/favorite?token=<JWT>&project_id={project_id}`.
8. Generate the logo with `crm.generate_logo` or the REST logo flow.
9. Mark the chosen logo favorite with `POST /api/logos/{logo_id}/favorite?token=<JWT>`.
10. Optionally create a business-name PDF report with `POST /api/business-names/projects/{business_name_project_id}/report?token=<JWT>`.

## Path Status

- Business-name project create + generate: `Working with caveats`
- Domain check: `Verified working`
- Palette generation via MCP: `Working with caveats`
- Palette generation via REST fallback: `Verified working`
- Palette save + favorite: `Verified working`
- Logo generation via MCP: `Working with caveats`
- Logo generation via REST fallback: `Verified working`
- Logo favorite: `Verified working`
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

### Verified Palette Save Body

```json
{
  "palette_data": {
    "name": "Signal Current",
    "description": "Credible and modern B2B software palette",
    "colors": {
      "primary": { "hex": "#0F4C81", "feeling": "trustworthy" },
      "secondary": { "hex": "#5FA8D3", "feeling": "approachable" },
      "accent": { "hex": "#F4B942", "feeling": "energetic" },
      "neutral_light": { "hex": "#F5F7FA", "feeling": "clean" },
      "neutral_dark": { "hex": "#1E293B", "feeling": "grounded" }
    }
  },
  "generation_method": "description",
  "prompt": "credible modern operations software brand for busy service teams",
  "project_id": 123
}
```

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
  "color_palette_id": 789,
  "project_id": 123
}
```

## Operating Notes

1. Treat naming payload fields as stricter than the current public recipe implies. In practice, `project_name` and `business_description` should both be present.
2. If the first naming request fails with a generic validation message, confirm field names and aliases before changing strategy.
3. If MCP is degraded after initialization, skip straight to the documented REST fallback for palettes or logos instead of repeating MCP retries.
4. Keep a credible framing layer. Prefer the narrowest plausible market wedge and a believable promise over hype.
5. A generated palette is not ready for downstream use until it is saved or confirmed persisted and then marked favorite.
6. A generated logo is not the selected launch logo until it is favorited.
7. If there is no completed validation yet, label the brand recommendation as pre-validation or route back to validation before presenting the identity as strongly grounded.

## Output Contract

Return:

- business-name project id
- generated name shortlist
- recommended final name with domain-check result
- selected palette id, hex values, and favorite status
- logo id, image delivery fields, and favorite status
- business-name report URL if generated
- artifact status labels for naming, palette, and logo

## Failure Handling

- Naming and domain steps can fail independently; keep successful outputs instead of restarting the whole recipe.
- If naming fails, preserve the current working business name from bootstrap or validation only if the user approved continuing without a generated shortlist.
- If palette generation succeeds but save or favorite fails, do not claim the palette is ready for landing or QR usage.
- If palette generation succeeds but logo generation fails, preserve the chosen palette and retry through the REST logo path before falling back to a manual logo concept.
- If both platform palette paths fail, provide a manual palette direction labeled `manual fallback`.
- Keep the user-safe platform error text intact and note that SparkLaunch already routed diagnostics to support.

## Troubleshooting

- `Please enter your full name.`: likely generic validation wrapping. Re-check the business-name payload shape before assuming a founder-name field is needed.
- Empty or generic name list: tighten `industry`, `target_audience`, `keywords`, and `style_preferences` rather than blindly regenerating.
- Palette MCP session errors: use the multipart REST fallback, save the selected palette explicitly, then favorite it.
- Logo was generated but not used later: favorite the logo before passing control to landing-page or QR workflows.
