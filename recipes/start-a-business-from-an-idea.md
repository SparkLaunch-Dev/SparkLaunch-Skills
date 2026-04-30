---
id: recipe-founder-001
title: Start A Business From An Idea
summary: Bootstrap a project, wait for validation to finish, generate name and brand assets, create a branded QR campaign, publish a landing page, and return a comprehensive founder report plus asset bundle focused on credibility and investability.
auth: sparklaunch_jwt, user_scoped_mcp_api_key
surfaces: rest, mcp
outputs: project, validation, business_name_shortlist, domain_check, palette, logo, qr_campaign, landing_page, founder_report, founder_bundle
---

# Start A Business From An Idea

## When To Use

Use this recipe when the user says some version of: `I want to start a business and here is my idea: {idea}` and expects SparkLaunch to turn that into a real project, validated positioning, saved brand assets, a shareable landing page, and founder-ready deliverables.

## Credentials

- SparkLaunch JWT for REST routes (validation, business-name, branding, logo, QR campaign, landing page) and for minting the MCP key
- One user-scoped MCP API key. Mint it once per user with `POST /api/mcp/auth/api-keys?token=<JWT>` (see [create-a-user-scoped-mcp-key.md](./create-a-user-scoped-mcp-key.md)); the same key works for every SparkLaunch project this user owns or collaborates on
- Send `X-SparkLaunch-Project-Id: <project_id>` on every `/api/mcp/` tool call to target this project

## User Prompt

`I'd like to start a business and here is my idea: {idea}. Create the project, validate it, make a name, make a color palette, make a logo, make a QR campaign, make a landing page, and give me a report and asset bundle when you're done.`

## Path Status

| Step | Status | Notes |
| --- | --- | --- |
| Project bootstrap | Verified working | Use the JWT control-plane bootstrap route. |
| MCP runtime initialization | Working with caveats | `initialize` can succeed even when later tool calls lose session. |
| Validation via REST | Verified working | Async; treat it as blocking for founder workflows and poll until complete. |
| Validation via MCP | Working with caveats | Fast when healthy, but still do not continue until the validation record is complete. |
| Business naming | Working with caveats | Payloads are stricter than the optimistic recipe suggested. |
| Domain availability check | Verified working | Use it to score the recommended final name. |
| Palette generation | Working with caveats | MCP works when healthy; REST fallback is verified. Favorite the chosen palette. |
| Logo generation | Working with caveats | MCP works when healthy; REST fallback is verified. Favorite the chosen logo. |
| QR campaign create + QR theme + QR generate | Verified working | Use REST for founder workflows because it persists theme and branded QR outputs. |
| Landing create + draft patch + publish | Verified working | This is the known-good landing path. |
| Landing auto-generate content | Environment-dependent | If unavailable, patch manual draft content and continue. |
| Founder PDF + asset zip bundle | Working with caveats | Assemble locally from actual SparkLaunch outputs; never claim files exist until they are written. |

## Known-Good Transport

1. Bootstrap the project with REST before any runtime tool calls.
2. If MCP is healthy, use MCP for scoped runtime steps that are stable there.
3. If a post-initialize MCP request returns `Session not found`, reinitialize once and retry once.
4. If the retry also fails, mark MCP as degraded in the final report and switch to the documented REST fallback for that step.
5. Do not keep retrying a broken MCP session beyond that point.

## Workflow

1. Ensure the caller has a user-scoped MCP API key, then create the SparkLaunch project.
   - If the caller does not already have one, mint a user-scoped MCP API key with `POST /api/mcp/auth/api-keys?token=<JWT>` (only required once per user).
   - Initialize the MCP session against `/api/mcp/` (`initialize`, then `notifications/initialized`).
   - Create the SparkLaunch project by calling the `projects.create` MCP tool with the project name, one-liner, business description, industry, and stage. Record the returned `project_id`.
   - Send `X-SparkLaunch-Project-Id: <project_id>` on every subsequent MCP tool call in this recipe.
3. Create the validation project and start analysis.
   - Prefer the REST path in founder workflows because the validation record and report export are part of the final deliverable set.
   - `POST /api/validation/projects?token=<JWT>`
   - `POST /api/validation/projects/{validation_project_id}/analyze?token=<JWT>`
   - Poll `GET /api/validation/projects/{validation_project_id}?token=<JWT>` until the project is complete.
   - Optional PDF export after completion: `POST /api/validation/projects/{validation_project_id}/report?token=<JWT>`
4. Do not continue to naming, palette, logo, QR, or landing until validation has completed unless the user explicitly approves a faster partial run.
5. Generate business names.
   - `POST /api/business-names/projects?token=<JWT>`
   - `POST /api/business-names/projects/{business_name_project_id}/generate?token=<JWT>`
   - Check the strongest candidates with `POST /api/domains/check-for-name`
   - Pick a recommended final name and report whether the primary domain candidates are available.
   - Optional PDF export: `POST /api/business-names/projects/{business_name_project_id}/report?token=<JWT>`
6. Generate and persist the color palette.
   - Try `branding.generate_palette(description=...)` if MCP is healthy.
   - If using REST fallback, call `POST /api/branding/generate-palettes`, then explicitly save the selected palette with `POST /api/branding/save-palette?token=<JWT>`.
   - Mark the selected palette as favorite with `POST /api/branding/palettes/{palette_id}/favorite?token=<JWT>&project_id={project_id}`.
7. Generate and persist the logo.
   - Try `crm.generate_logo(...)` if MCP is healthy.
   - If using REST fallback, call `POST /api/logos/?token=<JWT>` then `POST /api/logos/{logo_id}/generate?token=<JWT>`.
   - Mark the selected logo as favorite with `POST /api/logos/{logo_id}/favorite?token=<JWT>`.
8. Create a branded QR campaign instead of a separate go-to-market planning step.
   - Persist the QR theme with `PUT /api/golinks/projects/{project_id}/qr-theme?token=<JWT>`.
   - Create the campaign with `POST /api/golinks/projects/{project_id}/campaigns?token=<JWT>`.
   - Generate the branded QR asset with `POST /api/golinks/projects/{project_id}/campaigns/{campaign_id}/qr?token=<JWT>`.
   - Prefer a capture-mode campaign that produces measurable demand signals.
9. Create the landing page.
   - `landing.create_project` or `POST /api/landing-pages/projects?token=<JWT>`
   - `landing.generate_content` or `POST /api/landing-pages/generate-content?token=<JWT>`
   - Persist the generated or manual content with `PATCH /api/landing-pages/projects/{landing_project_id}/versions/draft?token=<JWT>`
   - Include `logo_url` and `favicon_url` in the draft payload when a favorite logo exists.
   - Publish with `landing.publish` or `POST /api/landing-pages/projects/{landing_project_id}/publish?token=<JWT>`
   - Confirm the live state with `landing.get_project` or `GET /api/landing-pages/projects/{landing_project_id}?token=<JWT>`
10. Assemble the founder deliverables.
   - Download the validation PDF if created.
   - Download the business-name PDF if created.
   - Download the chosen palette image with `GET /api/branding/palettes/{palette_id}/download?token=<JWT>`.
   - Download the favorite logo with `GET /api/logos/{logo_id}/download?token=<JWT>`.
   - Save the QR image payload and landing-page content JSON.
   - Build a comprehensive founder report from the actual SparkLaunch outputs, explicitly separating what is already credible from what still needs proof before stronger launch or investor outreach, then export it to PDF when local rendering is available.
   - Bundle the report plus the downloaded assets into a `.zip` file.
11. Produce the final founder report using [templates/founder-workflow-report.md](./templates/founder-workflow-report.md).

## Verified Request Bodies

### Example `projects.create` MCP Tool Call Arguments

```json
{
  "name": "Nimbus Ops",
  "one_liner": "AI operations assistant for busy service teams.",
  "business_description": "Nimbus Ops helps service businesses automate intake, scheduling, and customer follow-up.",
  "industry": "operations software",
  "stage": "idea"
}
```

The returned `project_id` goes into the `X-SparkLaunch-Project-Id` header on every follow-up MCP tool call in this recipe.

### Example User-Scoped MCP Key Mint Body

```json
{
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
    "landing.write",
    "campaigns.read",
    "campaigns.write"
  ]
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

### Verified Validation Analyze Body

```json
{
  "deep_research": false
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

### Verified Domain Check Body

```json
{
  "business_name": "Nimbus Ops",
  "tlds": [".com", ".ai", ".co", ".io"]
}
```

### Verified Palette REST Fallback Fields

- `POST /api/branding/generate-palettes`
- multipart form data:
  - `generation_method=description`
  - `prompt=credible modern operations software brand for busy service teams`
  - `token=<JWT>`
  - optional `project_id=123`

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

### Verified QR Theme Body

```json
{
  "module_style": "rounded",
  "eye_style": "match",
  "fg_color": "#0F4C81",
  "bg_color": "#FFFFFF",
  "include_logo": true,
  "logo_id": 456
}
```

### Verified QR Campaign Body

```json
{
  "campaign_slug": "nimbus-ops-launch",
  "slug_mode": "project_name",
  "name": "Nimbus Ops Launch QR",
  "objective": "waitlist_growth",
  "campaign_mode": "capture",
  "default_post_verify_destination": "success",
  "headline": "Get early access to Nimbus Ops",
  "subheadline": "Join the waitlist for AI-assisted intake, scheduling, and follow-up.",
  "consent_text": "I agree to receive early-access and launch updates from Nimbus Ops.",
  "cta_text": "Join the waitlist",
  "utm_defaults": {
    "utm_source": "offline",
    "utm_medium": "qr",
    "utm_campaign": "launch"
  }
}
```

### Verified Campaign QR Body

```json
{
  "format": "png",
  "size": 512,
  "include_logo": true,
  "logo_id": 456,
  "module_style": "rounded",
  "eye_style": "match",
  "fg_color": "#0F4C81",
  "bg_color": "#FFFFFF"
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
  "palette_id": 789,
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
    },
    "logo_url": "data:image/png;base64,<favorite-logo-base64>",
    "favicon_url": "data:image/png;base64,<favorite-logo-base64>"
  },
  "assets_manifest": []
}
```

## Verified Working Path

1. Mint a user-scoped MCP key once per user with `POST /api/mcp/auth/api-keys?token=<JWT>`, then create the SparkLaunch project with the `projects.create` MCP tool and reuse the returned project id in the `X-SparkLaunch-Project-Id` header on every follow-up MCP call.
2. Run validation and wait for completion before continuing.
3. Run naming through the JWT business-name routes and record domain availability for the recommended final name.
4. Generate the palette, ensure it is saved, and mark it favorite.
5. Generate the logo and mark it favorite.
6. Create a branded QR theme, capture campaign, and QR asset through the GoLinks routes.
7. Create the landing project, patch draft content with the favorite logo, publish, and re-read final state.
8. Download or capture all completed SparkLaunch outputs, assemble the comprehensive founder report, export it to PDF when possible, and create the zip bundle.

## REST Fallback Order

1. Validation: `POST /api/validation/projects` -> `POST /analyze` -> `GET /projects/{id}` poll -> optional `POST /report`
2. Palette: `POST /api/branding/generate-palettes` -> `POST /api/branding/save-palette` -> `POST /api/branding/palettes/{palette_id}/favorite`
3. Logo: `POST /api/logos/?token=<JWT>` -> `POST /api/logos/{logo_id}/generate?token=<JWT>` -> `POST /api/logos/{logo_id}/favorite?token=<JWT>`
4. Landing content: if `landing.generate_content` is unavailable, patch manual `content_json` directly into the draft and publish

## Async Handling

1. Poll REST validation every 15 seconds for up to 20 minutes in the founder workflow.
2. Do not continue downstream work until validation is complete unless the user explicitly approves a partial run.
3. If validation is still `analyzing` at timeout, return the project id, `analysis_run_id`, current status, and any export URL already available.
4. In that partial case, stop before naming, palette, logo, QR campaign, or landing unless the user explicitly approves proceeding without completed validation.

## Credible Framing Rule

Always choose the narrowest plausible wedge before generating names, brand direction, QR messaging, or landing copy. Prefer concrete, believable positioning over hype. If the original idea is unusual, frame the first launch around the most credible user and use case rather than the broadest imaginable category.

## Report And Bundle Rules

1. Only report an artifact as completed if it was persisted or read back from SparkLaunch, or if the local founder PDF/zip file was actually written.
2. Every artifact in the report must carry both a status label and a source label.
3. Include raw SparkLaunch URLs or IDs for validation, naming, palette, logo, QR campaign, QR image, and landing assets when available.
4. The Founder report PDF should summarize the actual SparkLaunch outputs, not imagined outcomes.
5. The `.zip` bundle should contain, when available:
   - founder report PDF
   - founder report markdown or HTML source
   - validation PDF
   - business-name PDF
   - domain check JSON or markdown summary
   - palette PNG
   - logo PNG
   - QR PNG or SVG
   - landing content JSON
   - landing page URLs manifest

## Output Contract

Return a single founder-ready report with these sections:

- Executive summary
- Platform status
- Project created
- Validation summary
- Recommended business name and domain signal
- Selected palette and favorite status
- Selected logo and favorite status
- QR campaign and QR asset summary
- Landing page status
- Investment readiness snapshot
- Risks and open questions
- Recommended next 7-day actions
- Artifact inventory with source and status labels
- Founder PDF path or URL if created
- Asset zip path or URL if created

## Failure Handling

- If MCP initialize succeeds but tool calls later lose session, stop retrying after one reinit and switch to REST for that step.
- If validation remains `analyzing` after timeout, treat it as partial success and stop the founder workflow before downstream generation unless the user explicitly approves continuing.
- If the assets are created but the proof story is still weak, say so directly instead of presenting the startup as ready for investor outreach.
- If naming succeeds but the preferred domain is not available, report that clearly and either recommend the next-best available candidate or keep the current working name with a domain warning.
- If palette generation succeeds but no palette is saved or favorited, do not claim it is ready for landing-page use. Save it first or label the palette step incomplete.
- If logo generation succeeds but favorite selection fails, do not claim the landing page is brand-complete. Report the logo as generated but not selected.
- If QR campaign creation fails, continue with the landing page only if the user approved a no-QR launch path; otherwise stop with a partial founder report.
- If landing content generation returns `404` or another deployment mismatch, draft the page manually and continue through draft patch plus publish.
- If the local founder PDF or zip bundle cannot be created, return the markdown report plus the raw SparkLaunch artifact URLs and mark the file-assembly step `failed`.

## Troubleshooting

- `Session not found` after MCP initialize: likely deployment/session instability; reinitialize once, then switch to REST fallback.
- `Please enter your full name.`: likely generic validation wrapping; re-check request field names, aliases, and content type before changing the workflow.
- Validation still `analyzing` after several minutes: keep polling up to the founder timeout; treat validation as blocking for the full founder workflow.
- No palette appears in the project: MCP generation can save automatically, but REST fallback requires explicit save and favorite steps.
- Logo exists but landing page did not use it: mark the logo favorite, then patch `logo_url` and `favicon_url` into the landing draft.
- QR campaign created without brand styling: save QR theme first or pass explicit QR style fields when generating the campaign QR.
