<!-- sparklaunch:connection:start -->
1. Protected SparkLaunch MCP tools are not activated by this Muse Code package because Muse Code does not document the OAuth lifecycle SparkLaunch requires. Never request or accept bearer tokens, API keys, client secrets, authorization codes, or transport headers.
2. If SparkLaunch tools are absent, treat that as the package's intentional protected-auth boundary, not as a completed connection or a server failure. The skills may still provide non-tool planning that the user explicitly requests.
3. If a workflow needs a protected tool, stop before any write and explain that OAuth discovery, secure token storage, refresh, and revocation are not yet supported by this adapter. Never enable the example server with static credentials as a workaround.
4. If an authorization or credential error appears, stop. Do not ask the user to paste anything into Muse settings, headers, the conversation, or repository files.
<!-- sparklaunch:connection:end -->
