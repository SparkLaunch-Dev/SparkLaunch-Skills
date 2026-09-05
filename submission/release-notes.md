# SparkLaunch 0.7.0+codex.20260904000000 ChatGPT Candidate

Status: the local service 1.6.0 candidate adds SparkCap and SparkRoom and has not been deployed.
The previous production MCP service is deployed at service 1.4.0 according to the
retained 2026-09-03 evidence; that 61-tool observation does not verify this 86-tool
candidate. The package has not yet been submitted or approved by ChatGPT.
The retained portal prerequisites remain bound to the previous candidate and
intentionally fail current readiness checks. Registry publication and native-host
invocation of the new tools remain unverified.

## Reviewer-visible changes

- Add twelve SparkRoom tools, three OAuth scopes, an eleventh skill and the investor-room recipe. Room assembly uses reviewed pinned library revisions; sharing requires exact confirmation with expiry/use limits. Uploads, password links, invitations and live-source additions remain first-party handoffs.

- Add 13 SparkCap planning tools for cap tables, stakeholders, quota readback, and
  dilution, raise, fully diluted, and hiring models with explicit OAuth scopes.
- Existing-record writes require exact confirmation, an opaque current version,
  idempotency, live authorization, and existing plan limits. Modeling is unsaved.
- Add the portable SparkCap skill and a cap-table/raise recipe for all hosts.
  Advanced legal/official, sharing, and export actions remain first-party handoffs.


- Classify collaborator invitation email delivery as destructive and open-world, requiring exact one-time confirmation because a sent message cannot be recalled.
- Remove raw CRM/project location inputs and outputs from the submitted MCP boundary. ChatGPT business-card ingestion excludes physical addresses from extraction and storage while web/mobile retain their existing address-capable defaults.
- Keep incorporation `draft_file` attachments address-free and move participant plus company business/mailing address entry to authenticated sparklaun.ch Action Center tasks.
- Build a portal upload containing only the SparkLaunch plugin, with `.codex-plugin/plugin.json` at the archive root; keep internal submission evidence outside that upload.
- Expose eleven concise founder-workflow skills through one connected SparkLaunch MCP server.
- Generate review metadata from the application-owned registry of 86 tools covering projects, general project tasks, owner-confirmed collaborator invitations, idea validation, palettes, logos, campaigns, QR files, landing pages, analytics, CRM, SparkCap, SparkRoom, and incorporation.
- Add `crm.prepare_business_card_import` and `crm.get_business_card_import` for a portable, first-party business-card handoff: preparation creates no contact or attachment, import requires an authenticated explicit **Upload and import** action, and status readback returns no image or contact data.
- Add `projects.invite_collaborator` as an owner/admin-only, idempotent, confirmation-bound email invitation that uses the canonical acceptance workflow and reports invitation persistence separately from delivery.
- Add `tasks.list`, `tasks.create`, `tasks.update`, and `tasks.delete` for project-isolated general tasks with accepted-member email assignment, optimistic versions, idempotency, exact overwrite/delete confirmation, and stale mobile-state cleanup. CRM and GTM tasks remain outside this generic contract.
- Add eight incorporation tools with explicit `project_id` arguments and the application-owned `incorporation.read`, `incorporation.write`, and `incorporation.submit` permissions within the expected 25 OAuth scopes.
- Check entitlement before starting, resuming, or reporting on an incorporation case. Missing access returns safe package recovery guidance without checkout or payment collection.
- Coordinate ordinary shared company data separately from private Action Center work. Each participant completes only their own identity/Veriff, compliance, consent, and signature tasks; another participant's private data or Action Center URL is never returned in conversation.
- Use exact draft versions, stable idempotency keys, readback after uncertain writes, and exact one-time confirmation previews for Action Center preparation, internal submission, and cancellation.
- Use task-specific incorporation timing instead of the unrelated Idea Validation estimate.
- Limit the final connected action to **submit to SparkLaunch Filing Operations**. The exact receipt warning is: **Submitted to SparkLaunch Filing Operations. This receipt does not mean the filing has been sent to Delaware or NWRA.** The receipt does not mean external filing, registered-agent acceptance, formation, certificate issuance, or provider-production proof.
- Add 36 skill-trigger cases and 15 controlled E2E cases. The five incorporation scenarios require synthetic data and zero provider calls to Delaware, NWRA, CorpTools, email, filing, or registered-agent adapters.
- Preserve generated logo and QR assets as expiring HTTPS file references rather than raw base64 or data URLs.
- Keep identifiers and concurrency versions as internal tool-call state while all user-facing skill, recipe, confirmation, table, and handoff language uses human-readable names or descriptions.
- Rebuild the portal candidate deterministically with canonical/mirror parity and a bundled proprietary license; record its digest in the separate readiness evidence.

## Compatibility

- Clients that sent inline CRM/project locations or address-bearing incorporation drafts must migrate to the location-safe schemas, the non-address incorporation `draft_file`, and protected Action Center address tasks.
- The public ChatGPT skills and reviewer workflow use OAuth and the canonical `https://sparklaun.ch/api/mcp/` endpoint only.
- OAuth scopes are the maximum connection authority; project membership, role, plan, entitlement, case version, participant readiness, and confirmation still gate each action.

## Review boundaries

- The candidate does not add a custom widget, direct provider integration, external filing action, payment collector, identity-document collector, or participant impersonation path.
- The deployed SparkLaunch public-policy sources set a minimum age of 13, require parent or legal-guardian permission below the applicable age of majority, and preserve workflow-, provider-, and jurisdiction-specific legal-capacity requirements. A dedicated live policy-content observation remains separate from deployment proof.
- Package validation and controlled local E2E do not by themselves prove deployment, production email delivery, Registry publication, marketplace activation, external filing, conversion, or retention. The retained deployment evidence and direct 61-tool inventory support only the prior service 1.4.0 baseline.
- Reviewer credentials, confirmation tokens, private participant values, provider session details, and signed file references must remain outside this repository.
- Any later runtime deployment, Registry publication, ChatGPT submission, and any separately enabled external Filing Operations action each require explicit approval and fresh evidence.
