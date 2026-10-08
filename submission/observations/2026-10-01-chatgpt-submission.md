# ChatGPT draft upload observation — 2026-10-01

Observed through the authenticated SparkLaunch organization browser session.
This is draft/package proof, not deployment, review approval or publication.

- Plugin record: `plugin_asdk_app_6a963bde250881918591112eac13b307`.
- Accepted draft: `appsub_6abeeb6bd57881919f79a2a755500e91`.
- Metadata and skills version: **0.11.0 · Draft**.
- Publication: **Not published**. Review status: **Not submitted**.
- Accepted ZIP: `dist/sparklaunch-chatgpt-plugin-0.11.0.zip`.
- ZIP SHA-256:
  `6DD264947B4202BCE16AFE8F4FC65E869BDC04E71EB5820BF610C66EE77D9F76`.
- All twelve packaged skills display **Checks passed**.
- Website, support, privacy and terms URLs were imported correctly. Support is
  `https://sparklaun.ch/help`.

The existing portal record rejected `name: sparklaunch` and required its legacy
`app-6a963bde250881918591112eac13b307` name. The deterministic portal builder
applies that public name only to the ZIP manifest; native packages keep their
canonical `sparklaunch` identity. The accepted MCP configuration uses the named
`mcpServers` wrapper, HTTP transport and canonical OAuth resource.

The MCP selector exposes both the legacy associated app and the packaged server.
The legacy app retains 59 tools from its previous review. A fresh rescan failed
because scanning authorization was unavailable. The portal explicitly says its
results are retained from the last available review, not this failed attempt.
It requests reconnection, although the authentication badge still says Authorized.
The packaged `sparklaunch` server reports **Complete MCP setup / Connection
unknown** and exposes no connection control in the inspected UI.

A diagnostic upload using a changed MCP entry was rejected because adding,
removing or replacing MCP configurations is unsupported on an existing plugin.
The diagnostic source change was reverted; the local archive digest again equals
the accepted digest above. No new plugin record was created.

Metadata checks also report that the selected **Productivity** category could
not be confirmed. That title matches OpenAI's documented category example, but
the warning remains unresolved; no category-check pass is inferred. Review
information is incomplete. Reviewer credentials, fixtures and demonstration
preparation are audit item 3 and were not modified during this work.

The 1.10.0 / 129-tool backend candidate was not deployed. No OAuth credential or
grant was entered, no tool was executed through the portal, and no final review
submission, legal attestation or publication was performed.

Screenshots are retained in the application repository:

- `reports/chatgpt-submission-0.11.0.jpg`: accepted version, URLs, skill status and
  unresolved metadata/review warnings.
- `reports/chatgpt-mcp-connection-0.11.0.jpg`: packaged server connection unknown.
- `reports/chatgpt-legacy-scan-0.11.0.jpg`: legacy app requests reconnection.

Remaining external proof: matching backend deployment; working portal MCP
connection; fresh scan matching the complete 129-tool inventory; category
confirmation; and the separately scoped reviewer/demo prerequisites.
