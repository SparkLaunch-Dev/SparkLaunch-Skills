---
name: sparklaunch-platform
description: >
  Use when a connected SparkLaunch user wants a broad founder workflow spanning
  project setup, idea validation, branding, launch assets, campaigns, landing
  pages, CRM, SparkRoom, SparkCap, SparkClose, monthly reporting, obligations, or incorporation and the first task is choosing the right
  SparkLaunch recipe or narrower skill.
---

# SparkLaunch Platform

Route broad founder outcomes to the smallest complete SparkLaunch workflow.

## Routing

1. For an idea-to-launch journey, use `recipes/start-a-business-from-an-idea.md`.
2. For connection or project selection, use `recipes/connect-sparklaunch.md` and `sparklaunch-projects`.
3. For validation only, use `recipes/validate-an-idea-and-generate-a-report.md` and `sparklaunch-idea-validation`.
4. For palette or logo work, use `recipes/create-a-brand-foundation.md` and the matching branding skills.
5. For campaigns, QR, or landing pages, use `recipes/plan-and-publish-a-launch.md` with `sparklaunch-campaigns` and `sparklaunch-landing-pages`.
6. For leads, contacts, deals, or follow-up, use `sparklaunch-sales-crm`.
7. For post-launch evidence, use `recipes/review-launch-signals-and-follow-up.md`.
8. For cap tables, stakeholder planning, ownership, dilution, fundraising models, or hiring impact, use `sparklaunch-sparkcap` and `recipes/review-cap-table-and-model-a-raise.md`.
9. For investor rooms, selected library documents, room share links, or usage summaries, use `sparklaunch-sparkroom` and `recipes/prepare-and-share-an-investor-room.md`. SparkRoom requires effective Growth access; uploads and password sharing continue in SparkLaunch.
10. For SAFE modeling, saved dilution scenarios, funding evidence, or investment closings, use `sparklaunch-sparkclose` and `recipes/model-and-close-a-safe.md`.
11. For an Incorporation Package, formation case, participant Action Center, correction, cancellation, or internal Filing Operations receipt, use `sparklaunch-incorporation` and its matching incorporation recipe.
12. For a Monthly Founder Close, investor update, board package, reviewed room refresh, ongoing obligations or post-close reporting, use `recipes/run-monthly-founder-close.md`. The AI host drafts; SparkLaunch persists evidence, exact approvals and recurring work. Check the new reporting/operations permissions before accessing private report contents.

## Connected-App Rules

<!-- sparklaunch:connection:start -->
1. Use the SparkLaunch MCP connection supplied by Claude Code. Never ask the user for credentials, access tokens, refresh tokens, or authorization headers.
2. If the SparkLaunch tools are absent, stop before planning or claiming execution and say: **SparkLaunch isn't available in this Claude Code session. Confirm that the SparkLaunch plugin is installed and enabled, run `/mcp`, and complete the SparkLaunch browser sign-in if prompted. Then reload plugins or start a new Claude Code session and send the request again.**
3. If a SparkLaunch tool returns an OAuth challenge, ask the user to authenticate or re-authenticate from `/mcp`, then retry only after the connection succeeds.
4. If authorization is expired or revoked, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Re-authenticate SparkLaunch from `/mcp`, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
<!-- sparklaunch:connection:end -->
5. Use `projects.list` to discover accessible projects. Pass the selected `project_id` argument to every project-scoped tool; do not depend on legacy project headers.
6. Before proposing or confirming a write, use `projects.get` and verify `effective_permissions` contains the required permission. If the `connection_permissions` list lacks required access, reconnect through the host and approve it. A project plan or role can also restrict execution; explain an explicit denial using its stated remedy. Do not infer a plan restriction from the effective list alone.
7. For each write, create one stable `idempotency_key` for that exact intended mutation. Never retry a write with a new key after an uncertain result.
8. When a tool returns `confirmation_required`, show the exact preview and wait for explicit approval. Then call the same tool with the same arguments, same idempotency key, and returned confirmation token.
9. Never expose secrets, raw base64, data URLs, internal ownership IDs, or support diagnostics.
10. Retain record identifiers and concurrency versions only as internal tool-call state. In every user-facing message, table, confirmation, and handoff, identify records by human-readable names or descriptions and omit identifier/version values, labels, parenthetical references, and columns.

## Founder Journey

1. Select a SparkLaunch project, or create one and retain its returned id.
2. For a newly created project, wait for the automatically queued Idea Validation research (normally 10-15 minutes) rather than creating a duplicate validation run. Complete validation before claiming the idea is validated.
3. Generate the selected brand assets.
4. Create a measurable campaign or landing-page surface.
5. Review analytics and CRM context before recommending follow-up.

Carry forward the selected project, validated wedge, brand choices, published URLs, and unresolved proof gaps. Do not report an artifact as complete until the tool result confirms it was created, generated, or published.

## Output

Before substantial work, name the selected recipe or narrower skill, the current founder stage, and the next gating milestone.
