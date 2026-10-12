# Connected-account inspection — 2026-10-12

The user selected repair of the existing public/Git SparkLaunch plugin and
declined a private replacement.

SayForward's live Plugin Creator source binds a registered App in `.app.json`.
SparkLaunch's 0.11.0 Git package instead declares only `.mcp.json`, matching
the supplied screenshot's MCP servers section and absent account controls.

The live SparkLaunch Developer Portal, in the SparkLaunch organization, identifies
the existing App as `asdk_app_6a963bde250881918591112eac13b307` and plugin as
`plugin_asdk_app_6a963bde250881918591112eac13b307`. Its endpoint is
`https://sparklaun.ch/api/mcp/`; Authentication shows Authorized and Domain
verified. These badges coexist with Complete MCP setup, Not published,
Not submitted, and Draft. Displayed tools are Not live. Personal ChatGPT's
plugin page lookup reports Plugin not found. The App is therefore not proven
available to the Git package's intended audience.

Connect account reached SparkLaunch sign-in and the existing business Google
account selector. After selecting the existing account, the popup closed.
No authorization approval was clicked. A fresh portal read still reports
Complete MCP setup; grant outcome and authenticated tool discovery are unknown.
No business tool was executed and no package was uploaded or submitted.

The public-only verifier passed at `2026-10-12T21:48:14.482683+00:00`, reporting
33 advertised scopes and zero business tool calls. It does not prove a token,
the complete authenticated catalog, deployed service identity or App activation.

The 0.11.1 local candidate restores the native App binding and emits the accepted
MCP configuration only in the public portal ZIP. Tests and the release gate are
recorded in [connected accounts](../../docs/v-cycle/connected-accounts.md).
Local screenshot: `dist/connection-evidence/sparklaunch-portal.png` (ignored
artifact, not part of the upload). Public activation and fresh native connected
account acceptance remain required before merging or releasing the candidate.
