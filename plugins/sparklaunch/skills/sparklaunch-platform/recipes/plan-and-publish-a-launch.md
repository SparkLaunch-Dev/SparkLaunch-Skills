---
title: Plan And Publish A Launch
summary: Create confirmed public campaign surfaces, a QR file, and a measurable landing page.
---

# Plan And Publish A Launch

## Inputs

- Selected `project_id`
- Valid absolute destination URL or capture objective
- Campaign name and attribution parameters
- Landing-page product brief, audience, template, and CTA

## Steps

1. Call `campaign_create` with a stable idempotency key. Show its public-state confirmation preview and wait for explicit approval before the confirmed call.
2. When needed, call `shortlink_create` through the same two-step confirmation pattern with its own stable key.
3. Call `qr_generate` with a separate stable key, then surface `qr.file` before its download URL expires.
4. Call `landing.create_project` with its own stable key.
5. Call `landing.generate_content` with its own stable key and present the structured copy.
6. Ask for publish approval. Call `landing.publish` once to obtain the exact preview, then repeat the same arguments and key with the returned confirmation token only after approval.
7. Verify with `landing.get_project` before sharing the production URL.
8. Record the primary conversion goal so later analytics are interpretable.

## Guardrails

- Do not auto-confirm public actions.
- Do not retry an uncertain write with a new key.
- The current ChatGPT tool set does not expose direct QR-theme or landing-draft patch operations; do not claim those settings were persisted.
- Never expose raw QR base64 or a data URL.

## Completion Evidence

Report campaign, short-link, QR, and landing ids; short and production URLs; file metadata; confirmed publish status; and the conversion goal. Configuration is not evidence of traffic or conversion.
