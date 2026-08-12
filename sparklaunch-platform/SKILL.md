---
name: sparklaunch-platform
description: >
  Use when a connected SparkLaunch user wants a broad founder workflow spanning
  project setup, idea validation, branding, launch assets, campaigns, landing
  pages, or CRM and the first task is choosing the right SparkLaunch recipe or
  narrower skill.
---

# SparkLaunch Platform

Route broad founder outcomes to the smallest complete SparkLaunch workflow.

## Routing

1. For an idea-to-launch journey, use `recipes/start-a-business-from-an-idea.md`.
2. For connection or project selection, use `recipes/connect-sparklaunch-to-chatgpt.md` and `sparklaunch-projects`.
3. For validation only, use `recipes/validate-an-idea-and-generate-a-report.md` and `sparklaunch-idea-validation`.
4. For palette or logo work, use `recipes/create-a-brand-foundation.md` and the matching branding skills.
5. For campaigns, QR, or landing pages, use `recipes/plan-and-publish-a-launch.md` with `sparklaunch-campaigns` and `sparklaunch-landing-pages`.
6. For leads, contacts, deals, or follow-up, use `sparklaunch-sales-crm`.
7. For post-launch evidence, use `recipes/review-launch-signals-and-follow-up.md`.

## Connected-App Rules

1. Use the SparkLaunch connection supplied by ChatGPT. Never ask for credentials or authorization headers.
2. If a tool returns an OAuth challenge, ask the user to connect or reconnect SparkLaunch, then retry only after connection succeeds.
3. Use `projects.list` to discover accessible projects. Pass the selected `project_id` argument to every project-scoped tool; do not depend on legacy project headers.
4. For each write, create one stable `idempotency_key` for that exact intended mutation. Never retry a write with a new key after an uncertain result.
5. When a tool returns `confirmation_required`, show the exact preview and wait for explicit approval. Then call the same tool with the same arguments, same idempotency key, and returned confirmation token.
6. Never expose secrets, raw base64, data URLs, internal ownership IDs, or support diagnostics.

## Founder Journey

1. Select or create the SparkLaunch project.
2. Complete idea validation before claiming the idea is validated.
3. Generate the selected brand assets.
4. Create a measurable campaign or landing-page surface.
5. Review analytics and CRM context before recommending follow-up.

Carry forward the selected project, validated wedge, brand choices, published URLs, and unresolved proof gaps. Do not report an artifact as complete until the tool result confirms it was created, generated, or published.

## Output

Before substantial work, name the selected recipe or narrower skill, the current founder stage, and the next gating milestone.
