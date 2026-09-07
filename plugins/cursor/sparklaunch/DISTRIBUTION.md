# Cursor distribution boundary

This adapter generates an Agent Plugins 1.0 package licensed under Apache-2.0. The separately hosted SparkLaunch service and backend remain proprietary. See LICENSE and NOTICE for the repository/service and trademark boundaries.

Cursor's public Marketplace requires plugins to be open source. Apache-2.0 satisfies this source-license prerequisite; it does not establish Marketplace review or approval. The repository generates `.cursor-plugin/marketplace.json` pointing to this package for multi-plugin repository discovery. Submit the reviewed Git revision through Cursor's publishing flow only after the release gates pass.

The generated package must contain root `plugin.json`, root `mcp.json`, `skills/`, `LICENSE`, and this notice. Its MCP configuration follows the Agent Plugins 1.0 schemas and relies on the client-managed OAuth flow. Do not add bearer tokens, client secrets, static OAuth credentials, or authorization headers to the package.

For local validation, copy or link the generated package to `~/.cursor/plugins/local/sparklaunch`, restart Cursor or run **Developer: Reload Window**, and confirm the plugin and MCP server in **Customize**. Inspect **MCP Logs** for connection failures. A private or team rollout still requires the applicable Cursor administrator settings and a separately governed distribution decision.
