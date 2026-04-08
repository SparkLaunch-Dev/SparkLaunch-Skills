# SparkLaunch Agent Recipes

This catalog stores prompt-ready workflows for agents operating against SparkLaunch. Use these recipes when you want a repeatable sequence with explicit auth, transport, tool order, and output expectations.

Prefer the canonical MCP runtime at `/api/mcp/` whenever the tool exists there. Use authenticated SparkLaunch app APIs only for steps that do not yet have MCP parity.

Treat the recipes as operational playbooks, not product promises. Each recipe should distinguish what is verified working, what works with caveats, and what can fall back to REST or manual artifact creation.

## How To Use

1. Match the user request to the closest recipe.
2. Confirm the required credentials before starting.
3. Execute the workflow in the documented order.
4. Return the documented report shape instead of a loose status dump.
5. If a step fails, preserve partial outputs and continue only when the recipe explicitly allows it.

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
| [bootstrap-a-project-and-mcp-key.md](./bootstrap-a-project-and-mcp-key.md) | Create a new SparkLaunch project and mint the first scoped MCP key. | JWT control plane + MCP |
| [validate-an-idea-and-generate-a-report.md](./validate-an-idea-and-generate-a-report.md) | Create a validation project, run analysis, and return a founder-facing summary. | MCP + JWT report export |
| [create-a-brand-foundation.md](./create-a-brand-foundation.md) | Generate business names, check domains, choose a palette, and generate a logo. | JWT app APIs + MCP |
| [plan-and-publish-a-launch.md](./plan-and-publish-a-launch.md) | Generate a GTM plan, create a landing page, save AI content, and publish it. | JWT app APIs + MCP |
| [start-a-business-from-an-idea.md](./start-a-business-from-an-idea.md) | Run the full founder bootstrap from idea to validation, brand assets, GTM, landing page, and final report. | JWT control plane + JWT app APIs + MCP |
| [review-launch-signals-and-follow-up.md](./review-launch-signals-and-follow-up.md) | Review landing performance, capture leads, and turn signals into CRM and campaigns follow-up. | MCP |

## Current Boundary Notes

- `/api/mcp/` is the canonical MCP runtime.
- `POST /api/mcp/auth/bootstrap/project?token=<JWT>` is the control-plane bootstrap path for new projects.
- Business naming and GTM planning still use authenticated SparkLaunch app APIs today.
- Validation has both MCP and REST paths, but the REST path is asynchronous and requires polling.
- Landing-page draft persistence requires `PATCH /api/landing-pages/projects/{project_id}/versions/draft?token=<JWT>` even when content came from MCP.
- Palette and logo generation can fall back to authenticated REST if MCP session handling is unstable.
- User-facing failures should stay concise and helpful. SparkLaunch routes backend diagnostics to the support Slack channel for MCP, validation, business naming, GTM, landing pages, and domain-checking flows.

## Shared Report Template

- [templates/founder-workflow-report.md](./templates/founder-workflow-report.md)
