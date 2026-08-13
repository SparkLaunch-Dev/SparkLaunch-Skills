---
name: sparklaunch-landing-pages
description: >
  Use when a connected SparkLaunch user needs to create, generate, publish,
  inspect, or measure landing pages with the landing.* tools. Do not use for
  generic web design advice without a SparkLaunch landing-page operation.
---

# SparkLaunch Landing Pages

Create and operate conversion-focused SparkLaunch landing pages.

## Connection And Scope

1. Use ChatGPT-managed OAuth. Never request credentials or transport headers.
2. If the required SparkLaunch actions are absent from this conversation, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation, select SparkLaunch, and send your request again. If ChatGPT asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge, ask the user to connect or reconnect SparkLaunch, then retry only after it succeeds.
4. Resolve the project with `projects.list`, then pass `project_id` to every landing tool.
5. Use stable, unique `idempotency_key` values for `landing.create_project` and `landing.generate_content`.
6. `landing.publish` changes public internet state. Its first call returns a confirmation preview; show it and wait for explicit approval before repeating the exact call with the same key and returned `confirmation_token`.
7. Never automatically retry an uncertain publish.

## Workflow

1. Gather product name, one-liner, target customer, template type, CTA type, and desired proof signal.
2. Call `landing.create_project`.
3. Call `landing.generate_content` for structured copy.
4. Present the result and confirm the user wants it published.
5. Call `landing.publish` through the confirmation flow.
6. Verify the public state with `landing.get_project` before sharing the production URL.
7. Use `landing.get_analytics` and `landing.get_leads` for evidence-backed follow-up.

Template types: `saas`, `marketplace`, `ai_tool`, `waitlist`. CTA types: `waitlist`, `book_call`, `newsletter`.

The current ChatGPT tool set does not expose direct draft-patch, logo-selection, or favorite-selection actions. Do not claim those changes were made.

## Output

For projects, report id, name, slug, status, template, CTA, preview URL, production URL, and publish time when present. For analytics, report views, clicks, submissions, time window, and trend data. For leads, reveal only the records the user requested.
