# SparkLaunch ChatGPT Recipes

These recipes compose the connected SparkLaunch MCP tools into founder workflows.

| Recipe | Use it for |
| --- | --- |
| [connect-sparklaunch-to-chatgpt.md](./connect-sparklaunch-to-chatgpt.md) | OAuth connection, accessible-project discovery, and project selection |
| [validate-an-idea-and-generate-a-report.md](./validate-an-idea-and-generate-a-report.md) | Create and complete a private idea-validation analysis |
| [create-a-brand-foundation.md](./create-a-brand-foundation.md) | Generate saved palette and logo options |
| [plan-and-publish-a-launch.md](./plan-and-publish-a-launch.md) | Create a confirmed campaign, QR file, and landing-page launch surface |
| [review-launch-signals-and-follow-up.md](./review-launch-signals-and-follow-up.md) | Separate measured signals from configured assets and prepare grounded CRM follow-up |
| [start-a-business-from-an-idea.md](./start-a-business-from-an-idea.md) | Run the full connected founder journey |

## Shared Rules

1. Use ChatGPT-managed OAuth; never collect credentials in the conversation.
2. Discover projects with `projects.list` and pass an explicit `project_id` to scoped tools.
3. Give each exact write one stable `idempotency_key`. Never retry uncertain writes with a new key.
4. For `confirmation_required`, show the exact preview and wait for explicit approval before resubmitting the same arguments, key, and token.
5. Do not use hidden REST routes, query-token URLs, or legacy project headers as fallback behavior.
6. Keep configured assets, published state, observed traffic, conversions, and CRM persistence as separate proof layers.
7. Do not expose secrets, raw base64, data URLs, private diagnostics, or more personal data than requested.
