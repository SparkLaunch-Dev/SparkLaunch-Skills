---
name: sparklaunch-sales-crm
description: >
  Use when a connected SparkLaunch user needs CRM lead, contact, activity,
  deal, dashboard, or business-card operations through the crm.* tools. Do not
  use for generic sales strategy without a SparkLaunch CRM operation.
---

# SparkLaunch Sales CRM

Operate private SparkLaunch CRM data with explicit project selection and write safeguards.

## Connection And Scope

1. Use the OAuth connection managed by ChatGPT. Never request credentials or authorization headers.
2. If the required SparkLaunch actions are absent from this conversation, stop before planning or claiming execution and say: **SparkLaunch isn't loaded in this conversation. Start a new ChatGPT conversation, select SparkLaunch, and send your request again. If ChatGPT asks you to connect, complete the SparkLaunch permission screen.**
3. If a loaded action returns an OAuth challenge, ask the user to connect or reconnect SparkLaunch, then retry only after it succeeds.
4. Resolve the target with `projects.list`, then pass `project_id` to every CRM tool.
5. Start with the narrowest useful read: `crm.get_dashboard`, `crm.search_leads`, `crm.get_lead_workspace`, `crm.search_contacts`, or `crm.get_contact_workspace`.

## Writes

- Create or correct records with `crm.create_lead`, `crm.update_lead`, or `crm.update_contact`.
- Append relationship context with `crm.add_lead_note`, `crm.add_contact_note`, or `crm.log_activity`.
- Change pipeline state with `crm.move_deal`.
- Refresh AI guidance only with explicit user intent via `crm.refresh_contact_summary`.
- Delete a saved card only with explicit user intent via `crm.delete_business_card`.
- For `crm.ingest_business_card`, pass the ChatGPT file attachment as `business_card_file`; never convert it to base64 or paste a data URL.

Every write requires one stable `idempotency_key`. Destructive tools first return a confirmation preview; show it and wait for explicit approval before repeating the exact call with the returned `confirmation_token`. Do not automatically retry uncertain writes.

## Data Quality

1. Search for duplicates before `crm.create_lead`.
2. Use only real email addresses. Omit unknown emails instead of fabricating placeholders.
3. Put labels in `tags`; keep human context and provenance in `message` or a note.
4. Set `lead_type` to `lead`, `contact`, or `investor` from evidence.
5. Set `source` to the real acquisition source, not the MCP transport.
6. Prefer workspace payloads as the source of truth because they include profile, notes, summary state, attachments, and timeline context.

## Verification And Output

Re-read the affected lead, contact, or dashboard after important writes. Report the entity id, source-of-truth read, actions actually completed, changed fields, summary warnings, and justified next step. Never expose personal data beyond what the user requested.
