# Claude Code distribution boundary

This adapter generates a Claude Code plugin licensed under Apache-2.0. The separately hosted SparkLaunch service and backend remain proprietary. This adapter does not claim public listing, review, approval, or publication in Anthropic's directory.

The generated package must contain `.claude-plugin/plugin.json`, `.mcp.json`, `skills/`, `LICENSE`, and this notice. It connects directly to `https://sparklaun.ch/api/mcp/` and relies on Claude Code's browser-based MCP OAuth discovery. Do not add bearer tokens, client secrets, or authorization headers to the package.

Validate a generated package with:

```text
claude plugin validate plugins/claude/sparklaunch --strict
```

For local development, launch Claude Code with the generated package through its `--plugin-dir` option. The repository generates a root `.claude-plugin/marketplace.json` pointing to this package. After the reviewed release is available, install from the Git repository (not a raw JSON URL):

```text
/plugin marketplace add SparkLaunch-Dev/SparkLaunch-Skills
/plugin install sparklaunch@sparklaunch-skills
```

Refresh the marketplace and update the installed plugin with Claude's plugin manager when a new version is released. Organization policies still apply. The Claude.ai remote-connector directory is a separate submission using the same MCP endpoint; it does not install this Claude Code skill package.
