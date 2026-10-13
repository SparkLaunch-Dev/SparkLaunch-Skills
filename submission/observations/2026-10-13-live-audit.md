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
- Complete reviewer native OAuth, fixture-content and all eight test cases.
  Password rotation, portal synchronization, account setup and outside-project
  denial were verified separately below.
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

## Subsequent native and reviewer verification

The existing private Test App's actual tool results are now available. Project
listing, project/effective-permission reads, private task creation and exact
readback succeeded in a pre-existing controlled synthetic QA project. Task update
returned an exact confirmation preview and was not committed. A private Markdown
export downloaded successfully with HTTP 200 and matched its artifact metadata.
The owner/admin connection and full endpoint remain unchanged; these observations
cannot establish restricted-public or reviewer native acceptance. Sanitized
results are in `2026-10-13-native-smoke.json`.
Repeating task creation with the original key returned the same task/version and
left one audit task. An update with a stale version returned a non-retryable
error directing a fresh task read. Readback confirms pending state and version
were unchanged after the preview and stale request.
The existing App's Refresh tools control was invoked and returned to enabled
state. A subsequent native project read succeeds; the same App, primary account,
permissions and full URL remain visible. No changed catalog/version was captured,
so this is not authenticated descriptor equality or OAuth token-expiry refresh
proof. The latter lifecycle check remains pending.

The owner-approved reviewer password rotation completed against the same account
and single synthetic project, with expiry and entitlements unchanged. The old
password is rejected, the encrypted current version was verified, and all seven
setup checks pass. Preflight now rejects administrator or missing-role identities
before project reads. The regular reviewer was separately denied access to an
outside project. `2026-10-13-reviewer-rotation.json` contains credential-free
evidence. The owner subsequently approved secure portal synchronization. The
rotated credential fields were saved and reopened, with username matching the
approved store and password remaining masked. Store sync metadata was updated
and read back. The same public draft remains unsubmitted/unpublished. New OAuth,
sample content and native review cases remain pending.

The fresh skill DOM renders the generic five-colour SVG rather than an image.
The correct PNGs and metadata are already packaged. A support report is prepared;
host resolution and supported App URL migration remain unresolved. The existing
public draft remains 0.11.0, unsubmitted and unpublished. No duplicate App was
created and no backend deployment was performed.

Online research found two open original reports of valid skill icon metadata
falling back to generic badges:
[Windows issue 16307](https://github.com/openai/codex/issues/16307) and
[desktop picker issue 40224](https://github.com/openai/codex/issues/40224).
They concern desktop surfaces and do not prove this web page has the same code
defect. No shipped repair is documented in those reports. The support report
remains unsent following the owner's request to research first.
