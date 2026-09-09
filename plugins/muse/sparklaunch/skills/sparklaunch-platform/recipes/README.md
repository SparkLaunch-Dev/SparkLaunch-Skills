# SparkLaunch Connected-Agent Recipes

These recipes compose the connected SparkLaunch MCP tools into founder workflows.

| Recipe | Use it for |
| --- | --- |
| [run-monthly-founder-close.md](./run-monthly-founder-close.md) | Review monthly evidence, author investor/board reports, refresh a room and maintain recurring obligations |
| [model-and-close-a-safe.md](./model-and-close-a-safe.md) | Model SAFE exposure, confirm funding evidence and close one signed investment |
| [review-cap-table-and-model-a-raise.md](./review-cap-table-and-model-a-raise.md) | Inspect SparkCap ownership, confirm planning edits, and model an unsaved raise |
| [connect-sparklaunch.md](./connect-sparklaunch.md) | Host-managed OAuth connection, accessible-project discovery, and project selection |
| [validate-an-idea-and-generate-a-report.md](./validate-an-idea-and-generate-a-report.md) | Create and complete a private idea-validation analysis |
| [create-a-brand-foundation.md](./create-a-brand-foundation.md) | Generate saved palette and logo options |
| [plan-and-publish-a-launch.md](./plan-and-publish-a-launch.md) | Create a confirmed campaign, QR file, and landing-page launch surface |
| [review-launch-signals-and-follow-up.md](./review-launch-signals-and-follow-up.md) | Separate measured signals from configured assets and prepare grounded CRM follow-up |
| [start-a-business-from-an-idea.md](./start-a-business-from-an-idea.md) | Run the full connected founder journey |
| [incorporate-a-single-founder-company.md](./incorporate-a-single-founder-company.md) | Prepare a single-founder company case and internal Filing Operations receipt |
| [incorporate-with-collaborators.md](./incorporate-with-collaborators.md) | Coordinate shared company data and separate private tasks for multiple people |
| [recover-incorporation-entitlement.md](./recover-incorporation-entitlement.md) | Recover a missing or pending Incorporation Package safely |
| [resume-or-correct-incorporation.md](./resume-or-correct-incorporation.md) | Resume a case, resolve a version conflict, correct a successor version, or cancel |
| [check-incorporation-status.md](./check-incorporation-status.md) | Read safe case, participant, receipt, and acceptance progress |
| [prepare-and-share-an-investor-room.md](./prepare-and-share-an-investor-room.md) | Prepare reviewed room contents and create or revoke bounded investor access |

## Shared Rules

1. Use standards-based OAuth managed by the current host; never collect credentials in the conversation or configuration files.
2. Discover projects with `projects.list` and pass an explicit `project_id` to scoped tools.
3. Give each exact write one stable `idempotency_key`. Never retry uncertain writes with a new key.
4. For `confirmation_required`, show the exact preview and wait for explicit approval before resubmitting the same arguments, key, and token.
5. Do not use hidden REST routes, query-token URLs, or legacy project headers as fallback behavior.
6. Keep configured assets, published state, observed traffic, conversions, and CRM persistence as separate proof layers.
7. Do not expose secrets, raw base64, data URLs, private diagnostics, or more personal data than requested.
8. Project creation automatically queues its included Idea Validation research. Allow 10-15 minutes, poll at a bounded cadence, and do not create a duplicate initial validation workspace.
9. OAuth scopes are maximum connection permissions; project plan and role restrictions can still deny a tool and should not be described as a reconnection problem.
10. Incorporation starts with entitlement readback. Keep personal tasks in each participant's own Action Center, and never equate an internal SparkLaunch Filing Operations receipt with Delaware, NWRA, or CorpTools activity.
11. Retain identifiers and concurrency versions only as internal tool-call state. Never repeat them to the user, place them in parentheses, label them, or include them as table/report columns. Use human-readable project and record names or descriptions instead.
