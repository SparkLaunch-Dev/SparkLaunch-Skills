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

<!-- sparklaunch:connection:start -->
1. Use the standards-based OAuth connection managed by the current host. Never request or accept credentials, bearer tokens, authorization codes, client secrets, or transport headers.
2. If the required SparkLaunch actions are absent, stop before planning or claiming execution. Explain that SparkLaunch is not loaded in this session and direct the user to install or enable this package using the current host's documented flow, then start a fresh session.
3. If a loaded action returns an OAuth challenge, use the current host's documented connect or reconnect flow and retry only after the host reports success. Never use a pasted token as a fallback.
4. If authorization is expired or revoked, stop before any write, reconnect through the current host, and check the target before retrying an uncertain operation.
<!-- sparklaunch:connection:end -->
5. Resolve the target with `projects.list`, then pass `project_id` to every CRM tool. Use `projects.get` to confirm `effective_permissions` includes the required CRM permission before proposing or confirming a write; explain a plan or role limitation without requesting OAuth reconnection.
6. Start with the narrowest useful read: `crm.get_dashboard`, `crm.search_leads`, `crm.get_lead_workspace`, `crm.search_contacts`, or `crm.get_contact_workspace`.
7. Retain project, CRM record, activity, attachment, and concurrency identifiers/versions only as internal tool-call state. Never repeat them to the user or include identifier/version labels or columns; refer to people and records by human-readable name, organization, or title.

## Writes

- Create or correct records with `crm.create_lead`, `crm.update_lead`, or `crm.update_contact`.
- Append relationship context with `crm.add_lead_note`, `crm.add_contact_note`, or `crm.log_activity`.
- Change pipeline state with `crm.move_deal`.
- Refresh AI guidance only with explicit user intent via `crm.refresh_contact_summary`.
- Delete a saved card only with explicit user intent via `crm.delete_business_card`.
- For `crm.ingest_business_card`, pass `business_card_file` only when the current host supplies a server-accepted short-lived HTTPS file reference. Never convert an image to base64, paste a data URL, or pass an arbitrary URL.
- If the host cannot supply that reference and the first-party handoff tools are available, call `crm.prepare_business_card_import` with one stable idempotency key and give the user its expiring SparkLaunch action link. Make clear that preparation imported nothing. The user must sign in, review the bound project/contact, choose the image, and select **Upload and import** on SparkLaunch. After they return, use `crm.get_business_card_import` for readback; report success only when it returns `completed`. Do not display the intent, person, activity, project, or version identifiers.
- If neither the approved file reference nor the first-party handoff is available, explain that business-card image ingestion is unavailable in this host. Use a manual CRM write only when the user supplies the non-address fields and explicitly asks to save them.
- Do not ask for, pass, extract, display, or summarize raw street, city, region, or postal-address values. MCP reads omit saved CRM address fields, and MCP writes never change them. This boundary applies to every connected-agent host; users may continue address work in the SparkLaunch web or mobile app.
- If the user asks to read, add, update, or extract an address, do not call a CRM tool for that request. Say: **SparkLaunch's connected-agent tools can't collect, update, extract, or display physical addresses. Please add or review the address in the SparkLaunch web or mobile app.**

Every write requires one stable `idempotency_key`. Destructive tools first return a confirmation preview; show it and wait for explicit approval before repeating the exact call with the returned `confirmation_token`. Do not automatically retry uncertain writes.

## Data Quality

1. Search for duplicates before `crm.create_lead`.
2. Use only real email addresses. Omit unknown emails instead of fabricating placeholders.
3. Put labels in `tags`; keep human context and provenance in `message` or a note.
4. Set `lead_type` to `lead`, `contact`, or `investor` from evidence.
5. Set `source` to the real acquisition source, not the MCP transport.
6. Prefer workspace payloads as the source of truth because they include profile, notes, summary state, attachments, and timeline context.

## Verification And Output

Re-read the affected lead, contact, or dashboard after important writes. Report the human-readable record, source-of-truth read, actions actually completed, changed fields, summary warnings, and justified next step. Never expose personal data beyond what the user requested.
