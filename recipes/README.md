# SparkLaunch Agent Recipes

This catalog stores prompt-ready workflows for agents operating against SparkLaunch. Use these recipes when you want a repeatable sequence with explicit auth, transport, tool order, and output expectations.

Prefer the canonical MCP runtime at `/api/mcp/` whenever the tool exists there. Use authenticated SparkLaunch app APIs only for steps that do not yet have MCP parity.

## How To Use

1. Match the user request to the closest recipe.
2. Confirm the required credentials before starting.
3. Execute the workflow in the documented order.
4. Return the documented report shape instead of a loose status dump.
5. If a step fails, preserve partial outputs and continue only when the recipe explicitly allows it.

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
- Landing-page draft persistence currently requires `PATCH /api/landing-pages/projects/{project_id}/versions/draft?token=<JWT>` after MCP content generation.
- User-facing failures should stay concise and helpful. SparkLaunch routes backend diagnostics to the support Slack channel for MCP, validation, business naming, GTM, landing pages, and domain-checking flows.

## Shared Report Template

- [templates/founder-workflow-report.md](./templates/founder-workflow-report.md)
