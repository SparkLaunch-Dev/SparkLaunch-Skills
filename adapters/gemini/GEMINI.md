# SparkLaunch for Gemini CLI

Use the `sparklaunch` MCP server for connected SparkLaunch projects, validation, branding, launch, CRM, and incorporation workflows. Load the matching skill from `skills/` when one applies.

Preserve the workflow safeguards described by the selected skill:

- Resolve the active project before project-scoped work.
- Preview or summarize material writes before asking for confirmation.
- Reuse idempotency keys when retrying the same write.
- Never expose private CRM, incorporation, or generated-asset data outside the user's requested scope.
- Treat a returned file reference as private unless the tool explicitly says otherwise.

If the SparkLaunch connection is missing or expired, stop before any write and ask the user to run `/mcp auth sparklaunch`. Retry only after Gemini CLI reports that authentication succeeded. Never ask the user to paste an access token, refresh token, API key, client secret, or authorization code into the conversation or extension files.

Do not invent a fallback for host-specific file inputs. Use only input forms advertised by the current SparkLaunch tool schema; otherwise explain that the workflow is unavailable in this host and stop safely.
