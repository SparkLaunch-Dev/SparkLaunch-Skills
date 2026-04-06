---
name: sparklaunch-landing-pages
description: >
  Use when the user needs to create, publish, or manage AI-powered landing pages
  through the production Streamable HTTP endpoint at https://sparklaun.ch/api/mcp/,
  specifically the landing.create_project, landing.generate_content, landing.publish,
  landing.get_project, landing.list_projects, landing.get_analytics, and
  landing.get_leads tools. Do not use for generic web design advice when no MCP
  tool execution is requested.
---

# SparkLaunch Landing Pages

Create, publish, and manage AI-powered startup landing pages through SparkLaunch MCP.

## Authentication Policy (Mandatory)
1. Use an MCP API key as bearer auth for all MCP calls.
2. API keys must come from SparkLaunch Profile API key management.
3. MCP API keys are project-scoped; landing-page reads and writes stay inside the SparkLaunch project bound to that key.
4. If the user needs a new SparkLaunch project first, use the SparkLaunch app or `POST /api/mcp/auth/bootstrap/project` with a site JWT before MCP runtime calls.
5. Do not ask the user to sign in if they already have (or can create) an API key.
6. Use login URL fallback only when API key creation is unavailable.

## Endpoint and Transport
1. Endpoint: `https://sparklaun.ch/api/mcp/`.
2. Required headers: `Authorization: Bearer <MCP_API_KEY>`, `Accept: application/json`, `Content-Type: application/json`.
3. Session lifecycle:
- call `initialize`
- store `mcp-session-id` and protocol version
- send `notifications/initialized` with the same session headers
- reuse that session id for `tools/list` and `tools/call`
4. Treat `initialize` success as necessary but not sufficient. The next tool call can still lose session state.
5. If `Session not found` appears, reinitialize once and retry once.
6. If it repeats and a SparkLaunch JWT is available, switch to the REST landing flow instead of looping MCP retries.

## Available Tools
- `landing.create_project` - Create a landing-page project inside the SparkLaunch project already bound to the MCP API key
- `landing.generate_content` - Generate AI-powered landing page content (hero, features, FAQ, etc.)
- `landing.publish` - Publish a landing page project to its live subdomain URL
- `landing.get_project` - Get a landing page project with status, URLs, and lead count
- `landing.list_projects` - List landing page projects in the current SparkLaunch project
- `landing.get_analytics` - Get analytics summary (views, clicks, submissions)
- `landing.get_leads` - Get captured leads for a landing page

## Standard Workflow
1. Gather landing page details from the user:
   - Product name (required)
   - One-liner description (required)
   - Template type: `saas`, `marketplace`, `ai_tool`, or `waitlist`
   - CTA type: `waitlist`, `book_call`, or `newsletter`
   - Target ICP (optional)
2. Call `landing.create_project` to create the landing page project.
3. Call `landing.generate_content` to produce AI-powered copy when the route is available and the runtime is healthy.
4. Persist generated or manual content through `PATCH /api/landing-pages/projects/{project_id}/versions/draft?token=<JWT>` before publish.
5. Present the draft content to the user for review.
6. When ready, call `landing.publish` or the REST publish route to make the page live.
7. Share the production URL with the user.
8. Use `landing.get_analytics` and `landing.get_leads` to monitor performance.

## Output Contract
For created projects, always report:
- `landing_project_id`
- `name`
- `slug`
- `status`
- `preview_url`
- `template_type`
- `cta_type`

For published projects, additionally report:
- `production_url`
- `published_at`

For generated content, present sections clearly:
- Hero (headline, subheadline, CTA text)
- Features (title, description, icon per feature)
- Social proof / testimonials
- FAQ items
- CTA section
- Footer

For analytics, present:
- Total views, clicks, and submissions
- Views by day (trend data)

## Template Types
- `saas` - B2B/SaaS software (professional, enterprise-friendly)
- `marketplace` - Two-sided marketplace (community, discovery)
- `ai_tool` - AI/technology product (innovation, automation)
- `waitlist` - Pre-launch (exclusivity, anticipation)

## CTA Types
- `waitlist` - Email capture for early access
- `book_call` - Schedule a demo call
- `newsletter` - Newsletter subscription

## Landing Page Limits
- Free plan: 1 project, 1 published, 200 leads
- Startup plan: 5 projects, 3 published, 1000 leads
- Growth plan: Unlimited projects and leads

## Guardrails
1. Require `landing.write` scope for creation/publishing/content generation, `landing.read` for viewing.
2. Never ask the user for workspace IDs, project IDs, or internal ownership IDs.
3. Keep user-facing failures friendly and concise.
4. Treat login URLs as fallback only after API key path is blocked.
5. When project or publish limit is reached, clearly communicate and suggest upgrading.
6. Content generation returns content, not a guaranteed saved draft. Persist the draft explicitly before publish.
7. If the content-generation route is unavailable on a deployment, create manual draft content and continue with draft patch plus publish.
