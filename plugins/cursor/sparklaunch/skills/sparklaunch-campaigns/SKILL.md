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

<!-- sparklaunch:connection:start -->
1. Use the SparkLaunch MCP connection supplied by Cursor. Never ask the user for credentials, access tokens, refresh tokens, client secrets, or authorization headers.
2. If the SparkLaunch tools are absent, stop before planning or claiming execution and say: **SparkLaunch isn't available in this Cursor session. Open Customize, confirm that the SparkLaunch plugin and MCP server are installed and enabled, and follow Cursor's authentication prompt if shown. Then reload the Cursor window or start a new Agent conversation and send the request again.**
3. If a SparkLaunch tool returns an OAuth challenge, ask the user to complete Cursor's SparkLaunch authentication prompt, then retry only after the connection succeeds.
4. If authorization is expired or revoked, stop before any write and say: **Your SparkLaunch authorization is expired or revoked. Re-authenticate SparkLaunch from Cursor's Customize page, complete the permission screen, and then retry. I will not repeat a write until the connection is restored and any uncertain prior result is checked.**
<!-- sparklaunch:connection:end -->
5. Resolve the target with `projects.list`, then pass `project_id` to every campaign tool. Use `projects.get` to confirm `effective_permissions` includes `campaigns.write` before proposing or confirming a write; explain a plan or role limitation without requesting OAuth reconnection.
6. Every write requires a stable `idempotency_key` for that exact mutation.
7. `campaign_create` and `shortlink_create` affect public URLs. `campaign_pause`, `campaign_archive`, and `shortlink_rotate` also overwrite public behavior. Show the returned confirmation preview and wait for explicit approval before calling again with the same arguments, key, and `confirmation_token`.
8. Never automatically retry an uncertain write.
9. Retain campaign, short-link, QR, lead, and project identifiers and versions only as internal tool-call state. Never repeat them to the user or include identifier/version labels or columns; refer to records by campaign name, destination, short URL, or another human-readable description.

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

Report the campaign name and status, short URL, generated-file metadata, and attribution fields when available. Separate configured assets from observed traffic or conversions; creation alone is not traction.
