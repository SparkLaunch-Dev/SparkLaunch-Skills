---
name: sparklaunch-campaigns
description: >
  Use when a connected SparkLaunch user needs campaigns, short links, QR
  assets, attribution, lead ingest, statistics, pause, archive, or destination
  rotation through the campaign and shortlink MCP tools.
---

# SparkLaunch Campaigns And QR

Operate measurable campaign acquisition workflows and their CRM attribution.

## Connection And Scope

1. Use ChatGPT-managed OAuth. Never request credentials or transport headers.
2. Resolve the target with `projects.list`, then pass `project_id` to every campaign tool.
3. Every write requires a stable `idempotency_key` for that exact mutation.
4. `campaign_create` and `shortlink_create` affect public URLs. `campaign_pause`, `campaign_archive`, and `shortlink_rotate` also overwrite public behavior. Show the returned confirmation preview and wait for explicit approval before calling again with the same arguments, key, and `confirmation_token`.
5. Never automatically retry an uncertain write.

## Workflow

1. Confirm the destination or capture objective.
2. Create a campaign with `campaign_create`.
3. Create a public short link with `shortlink_create` when needed.
4. Generate a QR file with `qr_generate`.
5. Ingest an allowlisted lead payload with `lead_capture_ingest` only when the user supplied the data and consented to saving it.
6. Inspect outcomes with `campaign_stats`.
7. Use `campaign_pause`, `campaign_archive`, or `shortlink_rotate` only on explicit request.

`qr_generate` returns `qr.file`, a short-lived HTTPS file reference. Surface it promptly. Never return or reconstruct raw base64 or a data URL.

## Output

Report campaign id, short-link id, QR id, short URL, generated-file metadata, CRM lead id, and attribution fields when available. Separate configured assets from observed traffic or conversions; creation alone is not traction.
