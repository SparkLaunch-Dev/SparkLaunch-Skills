# Claude Code distribution boundary

This adapter generates a Claude Code plugin for local testing and authorized private distribution. SparkLaunch remains proprietary software under `LicenseRef-SparkLaunch-Proprietary`; generating this package does not grant an open-source license or publish it to an Anthropic directory or marketplace.

The generated package must contain `.claude-plugin/plugin.json`, `.mcp.json`, `skills/`, `LICENSE`, and this notice. It connects directly to `https://sparklaun.ch/api/mcp/` and relies on Claude Code's browser-based MCP OAuth discovery. Do not add bearer tokens, client secrets, or authorization headers to the package.

Validate a generated package with:

```text
claude plugin validate plugins/claude/sparklaunch --strict
```

For local development, launch Claude Code with the generated package through its `--plugin-dir` option. Private marketplace or organization distribution requires a separately governed marketplace catalog and access policy. This adapter does not claim public listing, review, approval, or publication.
