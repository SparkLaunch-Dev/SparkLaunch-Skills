# Cursor distribution boundary

This adapter generates an Agent Plugins 1.0 package for local testing and authorized private or team distribution. SparkLaunch remains proprietary software under `LicenseRef-SparkLaunch-Proprietary`; generating or locally installing this package does not grant an open-source license.

Cursor's public Marketplace requires plugins to be open source. The current SparkLaunch license therefore blocks public Marketplace submission unless the owner makes a separate, explicit licensing decision. Do not submit this package publicly or describe it as Marketplace-listed, reviewed, or approved.

The generated package must contain root `plugin.json`, root `mcp.json`, `skills/`, `LICENSE`, and this notice. Its MCP configuration follows the Agent Plugins 1.0 schemas and relies on the client-managed OAuth flow. Do not add bearer tokens, client secrets, static OAuth credentials, or authorization headers to the package.

For local validation, copy or link the generated package to `~/.cursor/plugins/local/sparklaunch`, restart Cursor or run **Developer: Reload Window**, and confirm the plugin and MCP server in **Customize**. Inspect **MCP Logs** for connection failures. A private or team rollout still requires the applicable Cursor administrator settings and a separately governed distribution decision.
