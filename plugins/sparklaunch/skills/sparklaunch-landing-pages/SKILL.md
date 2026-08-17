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
4. If a loaded action reports an expired or revoked authorization, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Reconnect SparkLaunch from this AI Agent, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
5. Resolve the project with `projects.list`, then pass `project_id` to every landing tool. Use `projects.get` to confirm `effective_permissions` includes `landing.write` before proposing or confirming a write; explain a plan or role limitation without requesting OAuth reconnection.
6. Use stable, unique `idempotency_key` values for `landing.create_project` and `landing.generate_content`. A generation call without `landing_project_id` returns an unsaved preview. To replace the selected private draft, repeat the generation intent with `landing_project_id` through its confirmation preview and verify `saved_to_draft=true`.
7. `landing.publish` changes public internet state. Its first call returns a confirmation preview naming the landing page, slug, preview URL, and exact public destination; show it and wait for explicit approval before repeating the exact call with the same key and returned `confirmation_token`.
8. Never automatically retry an uncertain publish.

## Workflow

1. Gather product name, one-liner, target customer, template type, CTA type, and desired proof signal.
2. Call `landing.create_project`.
3. Call `landing.generate_content` without `landing_project_id` to create an unsaved structured-copy preview and present it to the user.
4. If the user wants that direction saved, call `landing.generate_content` with the selected `landing_project_id`, show the draft-replacement preview, and wait for approval before the confirmed call. Verify `saved_to_draft=true` and retain the returned draft version and preview URL.
5. Review the saved draft preview, then ask whether the user wants the exact public destination published.
6. Call `landing.publish` through its separate public-state confirmation flow.
7. Verify the public state with `landing.get_project` before sharing the production URL.
8. Use `landing.get_analytics` and `landing.get_leads` for evidence-backed follow-up.

Template types: `saas`, `marketplace`, `ai_tool`, `waitlist`. CTA types: `waitlist`, `book_call`, `newsletter`.

The tool can replace a draft only with the complete content returned by `landing.generate_content`; it does not expose arbitrary field-level draft patches, logo selection, or favorite selection. Do not claim those narrower changes were made.

## Output

For projects, report id, name, slug, status, template, CTA, preview URL, production URL, and publish time when present. For analytics, report views, clicks, submissions, time window, and trend data. For leads, reveal only the records the user requested.
