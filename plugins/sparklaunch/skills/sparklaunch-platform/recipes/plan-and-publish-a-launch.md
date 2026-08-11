---
id: recipe-launch-001
title: Plan And Publish A Launch
summary: Create a branded QR capture campaign, generate landing-page content, save the draft, and publish a traction-oriented project landing page.
auth: sparklaunch_jwt, user_scoped_mcp_api_key
surfaces: rest, mcp
outputs: qr_campaign, qr_asset, landing_project, landing_draft, published_url
---

# Plan And Publish A Launch

## When To Use

Use this recipe when the user has a project and wants to move from brand assets into a public landing page plus a shareable QR-driven launch asset.

## Credentials

- SparkLaunch JWT for QR theme persistence, QR campaign create, QR generation, and landing-page draft persistence
- User-scoped MCP API key with `landing.read`, `landing.write`, `campaigns.read`, and `campaigns.write` (one key works across all of the caller's projects; see [create-a-user-scoped-mcp-key.md](./create-a-user-scoped-mcp-key.md))
- Send `X-SparkLaunch-Project-Id: <project_id>` on every `/api/mcp/` tool call to target this project

## User Prompt

`Build me a launch path for this project: create a branded QR campaign and publish a landing page I can start sharing.`

## Workflow

1. Confirm that the project already has a selected palette and logo, or create/favorite them first.
2. Confirm the primary conversion event the user wants to measure: waitlist sign-up, demo request, or newsletter signup.
3. Persist the QR theme with `PUT /api/golinks/projects/{project_id}/qr-theme?token=<JWT>`.
4. Create the capture campaign with `POST /api/golinks/projects/{project_id}/campaigns?token=<JWT>`.
5. Generate the branded QR asset with `POST /api/golinks/projects/{project_id}/campaigns/{campaign_id}/qr?token=<JWT>`.
6. Create the landing project with `landing.create_project` or `POST /api/landing-pages/projects?token=<JWT>`.
7. Generate structured landing content with `landing.generate_content` or `POST /api/landing-pages/generate-content?token=<JWT>`.
8. Persist the generated or manual content into the landing draft with `PATCH /api/landing-pages/projects/{landing_project_id}/versions/draft?token=<JWT>`.
9. Include `logo_url` and `favicon_url` in the draft payload when a favorite logo exists.
10. Publish the landing page with `landing.publish` or `POST /api/landing-pages/projects/{landing_project_id}/publish?token=<JWT>`.
11. Fetch the final published state with `landing.get_project` or `GET /api/landing-pages/projects/{landing_project_id}?token=<JWT>`.

## Path Status

- QR theme save: `Verified working`
- QR campaign create + QR generate: `Verified working`
- Landing create + draft patch + publish: `Verified working`
- Landing auto-generate content route: `Environment-dependent`
- Manual draft patch without generated content: `Manual fallback allowed`

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

## Known-Good Execution Order

1. Confirm or set the favorite palette and favorite logo first.
2. Choose a CTA path that creates measurable demand signals instead of a brochure-only page.
3. Save the QR theme before generating the campaign QR asset.
4. Create the QR campaign and generate the QR image.
5. Create the landing project.
6. If `landing.generate_content` works, patch the returned content into the draft.
7. If `landing.generate_content` is unavailable or returns `404`, write a manual `content_json` draft and continue.
8. Publish only after a successful draft patch.
9. Report the page as live only after a publish response or follow-up fetch confirms the production URL.

## Output Contract

Return:

- QR campaign id and public URL
- QR image data or saved file path
- landing project id
- preview URL
- production URL if published
- primary conversion goal
- publish status
- artifact status labels for the QR campaign, QR asset, and landing page

## Failure Handling

- If QR theme save fails, do not claim the QR asset is brand-complete even if campaign creation later succeeds.
- If QR campaign create fails, preserve the landing-page work and report QR as blocked instead of inventing a manual campaign record.
- If landing content generation succeeds but draft persistence fails, keep the generated content in the response so the user can retry the save step without regenerating.
- If publish fails, return the preview URL and draft status instead of pretending the page is live.
- If the page is live but the CTA path or signal capture is unclear, mark the launch as published but not yet traction-ready.

## Troubleshooting

- QR generation without a logo: verify the logo was favorited or pass `logo_id` explicitly in the QR request.
- Landing generate `404`: treat the generate route as deployment-mismatched and continue with a manual draft patch.
- Landing page missing the brand mark: patch `logo_url` and `favicon_url` into the draft payload before publish.
