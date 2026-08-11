# SparkLaunch Agent Recipes

This catalog stores prompt-ready workflows for agents operating against SparkLaunch. Use these recipes when you want a repeatable sequence with explicit auth, transport, tool order, and output expectations.

Prefer the canonical MCP runtime at `/api/mcp/` whenever the tool exists there and the transport is healthy. Use authenticated SparkLaunch app APIs for bootstrap, report export, QR campaign routes, and for any workflow step that does not yet have stable MCP parity.

Treat the recipes as operational playbooks, not product promises. Each recipe should distinguish what is verified working, what works with caveats, and what can fall back to REST or manual artifact creation.

## How To Use

1. Match the user request to the closest recipe.
2. Confirm the required credentials before starting.
3. Execute the workflow in the documented order.
4. Return the documented report shape instead of a loose status dump.
5. If a step fails, preserve partial outputs and continue only when the recipe explicitly allows it.
6. Do not report an artifact as completed until it was read back, favorited, published, downloaded, or written locally.

## Default Founder Path

Use the founder path by default when the user is asking for a broad startup outcome rather than one narrow operation.

1. Start with [start-a-business-from-an-idea.md](./start-a-business-from-an-idea.md) when the ask sounds like "help me build this startup", "turn this idea into a business", "make this credible", or "help me get investable".
2. Treat completed validation as the gating signal before naming, brand, QR, or landing work unless the user explicitly accepts a partial run.
3. Use [plan-and-publish-a-launch.md](./plan-and-publish-a-launch.md) to create a measurable public launch surface, not a static brochure page.
4. Use [review-launch-signals-and-follow-up.md](./review-launch-signals-and-follow-up.md) to turn launch activity into proof, follow-up, and CRM action.
5. Prefer one coherent founder report over disconnected status dumps from multiple narrow steps.

## Status Labels

Use these labels inside recipes and final reports:

- `Verified working` - confirmed flow with a documented request and response shape
- `Working with caveats` - usable, but transport, async timing, or schema behavior is brittle
- `Environment-dependent` - route exists in platform contracts but was not stable on every deployment tested
- `Manual fallback allowed` - the platform step may fail without blocking the whole founder outcome

## MCP Transport Reality

1. Start with MCP when the recipe says the tool is available there.
2. Call `initialize`, store the negotiated protocol version, send `notifications/initialized`, and reuse that protocol header on later requests.
3. If `initialize` returns an `mcp-session-id`, reuse it. If it does not, treat the runtime as stateless and continue without a session header.
4. If any later MCP request returns `Session not found`, reinitialize once and retry once.
5. If the retry also fails, mark MCP as degraded in the final report and switch to the recipe's REST fallback path.
6. Do not keep retrying a broken session beyond that point.

## Catalog

| Recipe | Main Use | Surfaces |
| --- | --- | --- |
| [create-a-user-scoped-mcp-key.md](./create-a-user-scoped-mcp-key.md) | Mint a single user-scoped MCP API key and select a project per request with X-SparkLaunch-Project-Id. | JWT control plane + MCP |
| [validate-an-idea-and-generate-a-report.md](./validate-an-idea-and-generate-a-report.md) | Create a validation project, run analysis, wait for completion when needed, and return a founder-facing summary. | MCP + JWT report export |
| [create-a-brand-foundation.md](./create-a-brand-foundation.md) | Generate business names, check domains, persist a favorite palette, and generate a favorite logo. | JWT app APIs + MCP |
| [plan-and-publish-a-launch.md](./plan-and-publish-a-launch.md) | Create a branded QR capture campaign, save landing-page content, and publish it. | JWT app APIs + MCP |
| [start-a-business-from-an-idea.md](./start-a-business-from-an-idea.md) | Run the full founder bootstrap from idea to validation, brand assets, QR campaign, landing page, comprehensive founder report, and asset bundle. | JWT control plane + JWT app APIs + MCP |
| [review-launch-signals-and-follow-up.md](./review-launch-signals-and-follow-up.md) | Review landing performance, capture leads, and turn signals into CRM and campaigns follow-up. | MCP |

## Current Boundary Notes

- `/api/mcp/` is the canonical MCP runtime.
- `POST /api/mcp/auth/api-keys?token=<JWT>` is the user-scoped MCP key mint path. One key works for every SparkLaunch project the caller can access.
- `X-SparkLaunch-Project-Id: <project_id>` is the per-request project selector for every `/api/mcp/` tool call (tools that accept an explicit `project_id` argument override the header for that call).
- The `projects.create` MCP tool is the in-MCP path for creating a new SparkLaunch project; use the returned project id in the `X-SparkLaunch-Project-Id` header on follow-up calls.
- Validation has both MCP and REST paths, but the REST path is asynchronous and requires polling.
- In founder workflows, validation is a blocking dependency by default. Do not continue into naming, brand, QR, or landing work until it completes unless the user explicitly approves a partial run.
- Business naming still uses authenticated SparkLaunch app APIs today.
- Palette generation can use MCP, but downstream launch workflows should explicitly favorite the selected palette.
- Logo generation can use MCP, but downstream launch workflows should explicitly favorite the selected logo.
- Landing-page draft persistence requires `PATCH /api/landing-pages/projects/{project_id}/versions/draft?token=<JWT>` even when content came from MCP.
- Founder launch workflows should use the project-targeted QR campaign routes instead of GTM planning.
- Founder launch workflows should prefer capture-oriented CTAs and assets that create measurable demand signals for follow-up and investability proof.
- User-facing failures should stay concise and helpful. SparkLaunch routes backend diagnostics to the support Slack channel for MCP, validation, business naming, domains, branding, logos, campaigns, and landing-page flows.

## Shared Report Template

- [templates/founder-workflow-report.md](./templates/founder-workflow-report.md)
