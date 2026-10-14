# Deployed follow-up — October 14, 2026

This observation concerns local public candidate 0.11.3, content SHA256
`a7d6b43a704a8b2fb7407f04d787dc6f63f57660e794a22c913084b7d7fb8777`.
The existing private Test App and existing public draft retain their identities,
connections and full-root MCP URL. Neither is the restricted public endpoint's
native acceptance record.

| Check | Current result | Proof boundary |
|---|---|---|
| Public OAuth discovery | Canonical issuer/resource, 33 business scopes and UserInfo identity metadata pass. | Discovery is separate from native-host acceptance. |
| Authenticated full catalog | All 138 complete descriptors exactly match; MCP service 1.11.0; SHA256 `7d71812bbebea12242ca8e8c2565a3f1557871ba2fe9b099709f65f3a56f2514`. | Verified twice; latest direct comparison at 2026-10-14T18:04:25.895226Z. No business tool calls in the catalog verifier. |
| Authenticated public catalog | All 121 complete descriptors exactly match; MCP service 1.11.0; SHA256 `ffdf78d081cc02c914fe8858e4c19a653b5cd386d66f97380c29a2a1e295fda7`. | Verified twice; latest direct comparison at 2026-10-14T18:04:30.920600Z. No business tool calls in the catalog verifier. |
| Native public-client OAuth | Exact loopback `/oauth/callback`, S256 PKCE, state validation, normal reviewer consent and validated reviewer UserInfo succeed. | Standard audit client only; not ChatGPT-native acceptance. |
| Reviewer browser sign-in | Ordinary first-party email/password login reaches the synthetic fixture's LaunchPad. | Browser sign-in is separately verified; no business write. |
| Reviewer setup | All seven read-only preflight checks pass at 2026-10-14T17:03:54.408825Z. | Regular active user, single owned project, analytics exclusion, Growth and incorporation entitlement; no content or native scenario acceptance. |
| Existing private App profile | `get_profile` requests reauthentication for `openid` and `email`. | The current primary connection lacks identity consent; it was preserved. |
| Existing private App endpoint | Full `/api/mcp/`; no URL editor in Manage App. | Restricted native acceptance cannot be inferred from full-root tests. |
| Existing public draft endpoint | Full `/api/mcp/`; MCP actions contains only Reconnect. No preview control is exposed. | Supported existing-App migration is unresolved. Draft remains not submitted and not published. |
| Temporary audit lifecycle | Refresh preserves reviewer identity. The replacement grant is revoked; UserInfo access then returns 401 and refresh returns 400. Both owned listeners are closed and the reviewer browser is signed out. | Immediate refresh, not access-expiry proof. No native ChatGPT disconnect was performed. |
| Excluded-call verification | All seventeen exact omitted names, including nine SparkClose and eight validation names, return `unsupported_tool`, `isError:true`, `retryable:false`, and no OAuth challenge. Arguments are empty objects only. | Direct restricted-endpoint denial before business execution. No signing, finalization, provider call or business mutation. |
| Public reviewer reads | Profile identity and the single fixture-project listing pass their guards; project detail returns structured data. | The supplementary combined role/grant assertion is not verified: the helper incorrectly expected `Owner` while the documented backend owner role is `owner`. Corrected for future runs; no extra grant was created. Raw helper status preserves that failure. |
| Host skill badges | Owner reports the same generic badges on other approved skills and elects to keep the report as a draft. Canonical SparkLaunch assets remain packaged. | Intended host badge design is unconfirmed; no additional icon probe or support escalation. |

The temporary audit client is a standard OAuth public client, not another ChatGPT
App or plugin. Its callback is bound only to loopback; authorization material
stays in process memory and HTTP request logging is disabled. The approved
encrypted fixture is read without retaining credentials. No backend deployment,
customer mutation, provider action, signing, filing or publication was performed.

Credential-free local evidence is ignored under `dist/audit-2026-10-14/`:
`reviewer-preflight.json`, `read-only-consent.png` and
`public-mcp-no-editor.png`, `audit-revocation.png` and `reviewer-signed-out.png`.
The MCP screenshot records the existing public URL and the Reconnect-only menu.
The latest repeated full and public catalog observations
are preserved in `2026-10-14-full-contract.json` and
`2026-10-14-public-contract.json` beside this file. The raw audit result is
`2026-10-14-oauth-audit.json`; its separate supplementary assertion remains
failed. `2026-10-14-public-boundary.json` binds the independently verified
catalog, seventeen-denial and lifecycle outcomes to the candidate and the
canonical JSON evidence digest (sorted keys, compact separators, UTF-8).
This binding survives Git's line-ending conversion. Publication, complete
reviewer cases and native acceptance
gates remain pending.

OpenAI's current [submission guide](https://developers.openai.com/plugins/deploy/submission#update-your-published-plugin)
explicitly directs existing MCP server URL changes to support and says the
current update flow does not support them. This corroborates the observed UI
limitation. It does not establish that support has migrated either App.

The updated OpenAI migration/icon support report remains unsent at the owner's
explicit request. The existing-App URL migration remains blocked on OpenAI's
supported workflow. Related icon
research is recorded in the October 13 observation; it does not establish an
internal cause or a supported endpoint migration.
