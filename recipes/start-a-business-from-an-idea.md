---
title: Start A Business From An Idea
summary: Run the connected project, validation, brand, launch, measurement, and CRM workflow without skipping proof gates.
---

# Start A Business From An Idea

## Sequence

1. Connect and select or create the project with [connect-sparklaunch-to-chatgpt.md](./connect-sparklaunch-to-chatgpt.md).
2. Complete [validate-an-idea-and-generate-a-report.md](./validate-an-idea-and-generate-a-report.md). Treat validation as blocking unless the user explicitly accepts a partial run.
3. Generate palette and logo options with [create-a-brand-foundation.md](./create-a-brand-foundation.md).
4. Create the campaign, QR file, and landing-page surface with [plan-and-publish-a-launch.md](./plan-and-publish-a-launch.md).
5. Review measured signals and CRM context with [review-launch-signals-and-follow-up.md](./review-launch-signals-and-follow-up.md).

## State To Carry Forward

- SparkLaunch `project_id`
- Validation project id, final status, recommended wedge, and proof gaps
- Selected palette and logo record ids
- Campaign, short-link, QR, and landing-page ids
- Published URL and primary conversion goal
- Analytics window, observed events, saved leads, and next approved action

## Gates

- Do not call the concept validated until completed validation results exist.
- Do not call an asset published until a follow-up read confirms the public URL.
- Do not call configured tracking traction; require observed analytics or captured leads.
- Do not perform public/destructive actions until the user approves the exact confirmation preview.
- Never repeat an uncertain write with a new idempotency key.

## Final Handoff

Summarize what was actually persisted, what is public, what was measured, what remains unproven, and the single next action most likely to reduce the biggest proof gap.
