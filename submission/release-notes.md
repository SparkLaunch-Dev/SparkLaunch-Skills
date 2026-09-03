# SparkLaunch 0.5.0+codex.20260902140918 ChatGPT Candidate

Status: the previously observed production MCP service is deployed and official MCP Registry version `1.0.0` is published. This candidate describes application service version `1.4.0`; its deployment, immutable Registry publication, and marketplace availability require separate approval and evidence. The retained successful production scan covers the prior 59-tool deployed revision and is stale for this 61-tool candidate. This ChatGPT submission bundle has not yet been submitted or approved by ChatGPT.

## Reviewer-visible changes

- Classify collaborator invitation email delivery as destructive and open-world, requiring exact one-time confirmation because a sent message cannot be recalled.
- Remove raw CRM/project location inputs and outputs from the submitted MCP boundary. ChatGPT business-card ingestion excludes physical addresses from extraction and storage while web/mobile retain their existing address-capable defaults.
- Keep incorporation `draft_file` attachments address-free and move participant plus company business/mailing address entry to authenticated sparklaun.ch Action Center tasks.
- Build a portal upload containing only the SparkLaunch plugin, with `.codex-plugin/plugin.json` at the archive root; keep internal submission evidence outside that upload.
- Expose nine concise founder-workflow skills through one connected SparkLaunch MCP server.
- Generate review metadata from the application-owned registry of 61 tools covering projects, general project tasks, owner-confirmed collaborator invitations, idea validation, palettes, logos, campaigns, QR files, landing pages, analytics, CRM, and incorporation.
- Add `crm.prepare_business_card_import` and `crm.get_business_card_import` for a portable, first-party business-card handoff: preparation creates no contact or attachment, import requires an authenticated explicit **Upload and import** action, and status readback returns no image or contact data.
- Add `projects.invite_collaborator` as an owner/admin-only, idempotent, confirmation-bound email invitation that uses the canonical acceptance workflow and reports invitation persistence separately from delivery.
- Add `tasks.list`, `tasks.create`, `tasks.update`, and `tasks.delete` for project-isolated general tasks with accepted-member email assignment, optimistic versions, idempotency, exact overwrite/delete confirmation, and stale mobile-state cleanup. CRM and GTM tasks remain outside this generic contract.
- Add eight incorporation tools with explicit `project_id` arguments and the application-owned `incorporation.read`, `incorporation.write`, and `incorporation.submit` permissions within the expected 18 OAuth scopes.
- Check entitlement before starting, resuming, or reporting on an incorporation case. Missing access returns safe package recovery guidance without checkout or payment collection.
- Coordinate ordinary shared company data separately from private Action Center work. Each participant completes only their own identity/Veriff, compliance, consent, and signature tasks; another participant's private data or Action Center URL is never returned in conversation.
- Use exact draft versions, stable idempotency keys, readback after uncertain writes, and exact one-time confirmation previews for Action Center preparation, internal submission, and cancellation.
- Use task-specific incorporation timing instead of the unrelated Idea Validation estimate.
- Limit the final connected action to **submit to SparkLaunch Filing Operations**. The exact receipt warning is: **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing, registered-agent acceptance, formation, certificate issuance, or provider-production proof.
- Add 30 skill-trigger cases and 13 controlled E2E cases. The five incorporation scenarios require synthetic data and zero provider calls to Delaware, NWRA, CorpTools, email, filing, or registered-agent adapters.
- Preserve generated logo and QR assets as expiring HTTPS file references rather than raw base64 or data URLs.
- Keep identifiers and concurrency versions as internal tool-call state while all user-facing skill, recipe, confirmation, table, and handoff language uses human-readable names or descriptions.
- Rebuild the portal candidate deterministically with canonical/mirror parity and a bundled proprietary license; record its digest in the separate readiness evidence.

## Compatibility

- Clients that sent inline CRM/project locations or address-bearing incorporation drafts must migrate to the location-safe schemas, the non-address incorporation `draft_file`, and protected Action Center address tasks.
- The public ChatGPT skills and reviewer workflow use OAuth and the canonical `https://sparklaun.ch/api/mcp/` endpoint only.
- OAuth scopes are the maximum connection authority; project membership, role, plan, entitlement, case version, participant readiness, and confirmation still gate each action.

## Review boundaries

- The candidate does not add a custom widget, direct provider integration, external filing action, payment collector, identity-document collector, or participant impersonation path.
- The local SparkLaunch public-policy sources now set a minimum age of 13, require parent or legal-guardian permission below the applicable age of majority, and preserve workflow-, provider-, and jurisdiction-specific legal-capacity requirements. Deployment and live observation of the updated public policies remain required.
- Package validation and controlled local E2E do not prove deployment, production email delivery, Registry `1.4.0` publication, marketplace activation, external filing, conversion, or retention.
- Reviewer credentials, confirmation tokens, private participant values, provider session details, and signed file references must remain outside this repository.
- Future production deployment, Registry publication, ChatGPT submission, and any separately enabled external Filing Operations action each require explicit approval and fresh evidence.
