# Live audit follow-up — October 13, 2026

This observation preserves proof boundaries for public candidate 0.11.2,
content SHA256 `1d16380a3e3f0d42a3e57b355264c040e56c695b1a11b435289c2b7ccc7a4407`.
The existing private App is a separate full-endpoint test; it is not this public
candidate's native acceptance record.

| Check | Observation | Acceptance boundary |
|---|---|---|
| Existing private App/account | Same App, private audience and primary connected account; cleanup release 1.0.9, twelve skills, 85 files, no diagnostic files. | Account UI preservation verified. No reconnect, permission expansion or replacement App. |
| Read-only native Chat | A fresh ordinary Chat with SparkLaunch Test reports success and 25 accessible active projects; follow-up reports one completed page. | Chat response observed; raw tool trace not captured. No project details retained or business writes requested. |
| App endpoint | Settings display `https://sparklaun.ch/api/mcp/` and no URL editor. | Full endpoint only. The public `/api/mcp/chatgpt/` is not configured in this private App. |
| Public discovery | `verify_production_contract.py --chatgpt --public-only` passes: 33 business scopes, public OAuth metadata, zero business calls. | `public_metadata_only`; `endpoint_verified: false`. Service identity and all 121 descriptors remain unverified. |
| HTTP reachability | Health returns 200; unauthenticated restricted initialization returns 401/Bearer `projects.read` challenge. | Does not prove a deployed catalog or exact backend revision. |
| Official Inspector OAuth | Inspector 2.10.1 requests native public-client registration, S256 flow and `projects.read`; server returns 400 `invalid_redirect_uri` for `http://127.0.0.1:6274/oauth/callback`. | No consent, grant, access token or authenticated scan. Preserve guard; prepare narrow compatibility repair. |
| Skill logos | Stored 24 PNGs match canonical assets. A newly created diagnostic skill also displays a generic badge. | Product acceptance FAIL; host internal cause unknown. Probe removed. |

## Remaining acceptance

- Owner-deployed backend, followed by authenticated full 138-tool and restricted
  121-tool comparisons, direct excluded-call denial and current server identity.
- Supported migration of the existing App endpoint or public developer-preview
  access without creating a duplicate plugin; then fresh public-candidate native
  account/tool tests, including applicable desktop/mobile acceptance.
- OpenAI importer/rendering resolution for skill logos; source parity alone is
  insufficient.
- Secure owner rotation of the reviewer password, approved-store/portal sync,
  then fresh synthetic-project isolation, entitlements and all eight test cases.
- Owner demo recording using `submission/demo-script.md`, verified hosted playback,
  and final candidate-bound portal/policy readiness evidence before submission.

Local screenshot crops are ignored under `dist/audit-2026-10-13/`:
`chat-read.png`, `new-skill-icon-probe.png`, `private-restored.png`.
No demo URL, credential, signed archive link or private project contents are
included here. No backend deployment or plugin publication occurred in this run.

The isolated backend compatibility fix adds only exact `/oauth/callback` under
the existing opt-in loopback flag. The full OAuth/CIMD/deployment suites pass
159 local tests; lint passes. This is implementation evidence, not hosted
registration, consent or public-catalog acceptance. The local Inspector session
was stopped after the failed registration; its temporary local launch credential
was removed, and no delegated OAuth credentials were obtained or retained.
