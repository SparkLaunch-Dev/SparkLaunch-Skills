# Private ChatGPT skill icon rendering

Observed October 12–13, 2026 in the owner's existing App-backed private test plugin.
The App/header logo displays correctly. All twelve skill rows display the generic
colored cube despite packaged SparkLaunch icons.

The source uses the documented `interface.icon_small` and `icon_large` fields in
each `agents/openai.yaml`. The paths resolve to valid square PNGs, and all twelve
small/large PNGs match the canonical SparkLaunch assets. The importer accepts
changed skill display descriptions, demonstrating that it reads the YAML.

Checks performed without changing identity, audience, connection or permissions:

- Re-imported metadata and all PNG assets, with normalized relative paths.
- Checked asset resolution at skill root, package root and YAML-directory root.
- Re-imported the complete package through ChatGPT's native ZIP upload UI.
- Checked an existing 48-pixel SparkLaunch PNG and the existing SparkLaunch SVG.

All checks retained generic badges. The final private update restores the
canonical metadata and removes temporary probe files. Source/package validation
does not prove UI rendering, and this issue remains unresolved. Current evidence
points to the private-plugin importer or renderer; its internal cause is unverified.

The supported metadata contract is documented in
[OpenAI's skill agent metadata reference](https://developers.openai.com/plugins/deploy/submission-errors#skill-agent-metadata-errors).
No custom icon editor is exposed on the App-backed skill dialogs. Do not add
unsupported frontmatter keys, change App identity, or create another plugin to
conceal the issue. An OpenAI host fix or a supported importer repair is required
before the logo acceptance requirement can be marked passed.

## Creation probe — October 13

Downloaded the owner's stored 1.0.7 archive and inspected its actual gzip/tar
contents: 85 files, twelve `SKILL.md` files and 24 real PNGs. All image bytes
match `src/skills/<skill>/assets/`; small/large images are 192x192 and 1024x1024.
The assets meet the documented size, format and contained relative-path contract.

Added one temporary `sl-icon-probe` skill to the same private App through an
App-preserving overlay. Its only instruction was an explicitly invoked icon
diagnostic, implicit invocation was disabled, and it used copies of the same
canonical PNGs with `./assets/` paths in `agents/openai.yaml`. Version 1.0.8
rendered thirteen skills and the diagnostic's correct display name/description,
but both the new skill and the existing skills retained generic badges. This
rules out an issue confined to updating previously imported skills. It does not
identify the host's internal failure or prove a public submission behaves alike.

Removed all four diagnostic files with a guarded overlay and restored the two
manifests at version 1.0.9. Fresh source readback contains 85 files, exactly twelve
skills and zero probe paths. The UI confirms twelve skills/version 1.0.9. App
identity, private audience and connected account were preserved. The App/header
rocket still renders; skill-logo acceptance remains FAIL.

For an owner-authorized OpenAI support report, provide this reproduction, the
metadata reference above and the sanitized screenshots. Do not send an owned
archive URL, OAuth state/code, account credentials or customer project contents.
No support message has been sent.

Private screenshots and source readback are retained under the ignored
`dist/connection-evidence/` directory, outside public release artifacts.
October 13 crops are in `dist/audit-2026-10-13/new-skill-icon-probe.png` and
`private-restored.png`; these ignored local files are not public review evidence.

## Current DOM diagnosis — October 13

The restored 1.0.9 skill row contains no `img` element. It renders a 24x24 generic
SVG with fills `#FFD400`, `#F75858`, `#8166E1`, `#BDAAFF`, and `#FFA43D`.
The current screenshot `dist/audit-2026-10-13/skill-icons-still-generic.png`
confirms the correct App/header rocket beside generic skill badges. This is
direct rendering evidence, not an inference from source validation.

A concrete support report is staged locally at
`dist/audit-2026-10-13/openai-support-report.md`. It requests a supported icon
repair and migration of the existing App's full MCP URL to the reviewed endpoint
while preserving App/account identity. Sending it requires the owner's explicit
authorization. No support response or resolution is claimed.

## Online reports — October 13

Two original reports in OpenAI's Codex repository remain open:

- [Issue 16307](https://github.com/openai/codex/issues/16307), opened March 31:
  Windows users report generic skill icons despite valid `icon_small` metadata;
  subsequent probes find resolved image paths.
- [Issue 40224](https://github.com/openai/codex/issues/40224), opened August 23:
  the desktop picker reporter finds loaded image metadata but generic icons,
  across PNG and SVG assets and after reloads.

These are related desktop reports, not confirmation of the same internal defect
on our web plugin page. The similarity and our direct generic-SVG observation
support a host rendering diagnosis. Neither report documents a shipped repair.
The packaged images already meet the official metadata contract. Do not repeat
unsupported packaging variants or modify a signed desktop bundle.

The owner requested this research before any support contact; the report remains
unsent. Official [refresh instructions](https://developers.openai.com/plugins/deploy/connect-chatgpt#refresh-metadata)
describe refreshing an existing connection's metadata, without documenting an
existing-App URL editor. A
[developer discussion](https://community.openai.com/t/clarification-on-mcp-server-url-and-versioning-during-chatgpt-app-update-submission/1379705)
says URLs can differ between submitted app versions, but gives no verified
migration procedure for our current App-backed private installation.
