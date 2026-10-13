# Private ChatGPT skill icon rendering

Observed October 12, 2026 in the owner's existing App-backed private test plugin.
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

Private screenshots and source readback are retained under the ignored
`dist/connection-evidence/` directory, outside public release artifacts.
