---
name: sparklaunch-platform
description: >
  Use when a connected SparkLaunch user wants a broad founder workflow spanning
  project setup, idea validation, branding, launch assets, campaigns, landing
  pages, CRM, SparkRoom, SparkCap, SparkClose, or incorporation and the first task is choosing the right
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

## Connected-App Rules

<!-- sparklaunch:connection:start -->
1. Protected SparkLaunch MCP tools are not activated by this Muse Code package because Muse Code does not document the OAuth lifecycle SparkLaunch requires. Never request or accept bearer tokens, API keys, client secrets, authorization codes, or transport headers.
2. If SparkLaunch tools are absent, treat that as the package's intentional protected-auth boundary, not as a completed connection or a server failure. The skills may still provide non-tool planning that the user explicitly requests.
3. If a workflow needs a protected tool, stop before any write and explain that OAuth discovery, secure token storage, refresh, and revocation are not yet supported by this adapter. Never enable the example server with static credentials as a workaround.
4. If an authorization or credential error appears, stop. Do not ask the user to paste anything into Muse settings, headers, the conversation, or repository files.
<!-- sparklaunch:connection:end -->
5. Use `projects.list` to discover accessible projects. Pass the selected `project_id` argument to every project-scoped tool; do not depend on legacy project headers.
6. Before proposing or confirming a write, use `projects.get` and verify `effective_permissions` contains the required permission. A project plan or role can further restrict execution; explain that restriction instead of asking the user to reconnect.
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
