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
5. Call `landing.generate_content` without `landing_project_id` with its own stable key and present the structured copy as an unsaved preview.
6. If the user approves the copy direction, call `landing.generate_content` with the selected `landing_project_id` and a new stable key. Show the private-draft replacement preview, wait for approval, complete the confirmed call, and verify `saved_to_draft=true` plus the returned preview URL.
7. Ask for publish approval. Call `landing.publish` once to obtain the exact landing name, slug, preview URL, and public destination, then repeat the same arguments and key with the returned confirmation token only after approval.
8. Verify with `landing.get_project` before sharing the production URL.
9. Record the primary conversion goal so later analytics are interpretable.

## Guardrails

- Do not auto-confirm public actions.
- Before presenting a write or confirmation, use `projects.get` and verify that `effective_permissions` contains the required permission. Explain a plan/role limitation without asking the user to reconnect.
- Do not retry an uncertain write with a new key.
- The tool can replace a landing draft with complete generated content, but it does not expose arbitrary field-level draft patches or direct QR-theme changes; do not claim those narrower settings were persisted.
- Never expose raw QR base64 or a data URL.
- Generated landing copy must not contain invented testimonials, customer identities, adoption counts, or performance claims. Leave social proof empty until the user supplies verified evidence.

## Completion Evidence

Report campaign, short-link, QR, and landing ids; short and production URLs; file metadata; confirmed publish status; and the conversion goal. Configuration is not evidence of traffic or conversion.
