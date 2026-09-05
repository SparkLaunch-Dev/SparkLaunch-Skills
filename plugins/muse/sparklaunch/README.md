# SparkLaunch Muse Code adapter

Muse Code has no documented third-party plugin manifest. This adapter therefore packages the eleven canonical SparkLaunch skills and a truthful, disabled MCP settings example; it does not claim marketplace installation or protected-tool parity.

## Validate and install the skills

Validate every emitted skill before installing it:

```text
muse skills validate ./skills/sparklaunch-platform
muse skills validate ./skills/sparklaunch-projects
muse skills validate ./skills/sparklaunch-idea-validation
muse skills validate ./skills/sparklaunch-color-palettes
muse skills validate ./skills/sparklaunch-logo-generation
muse skills validate ./skills/sparklaunch-campaigns
muse skills validate ./skills/sparklaunch-landing-pages
muse skills validate ./skills/sparklaunch-sales-crm
muse skills validate ./skills/sparklaunch-incorporation
```

Install a validated skill for one user with `muse skills install ./skills/<skill-id> --scope user`, or commit it to a trusted project's `.agents/skills/<skill-id>/SKILL.md`. Verify discovery with `muse skills list` and inspect an individual skill with `muse skills inspect <skill-id>`.

## Protected MCP boundary

Muse Code's public configuration contract supports `streamable_http` servers and static headers, but it does not document the OAuth discovery, PKCE, secure token storage, refresh, and revocation lifecycle SparkLaunch requires. Do not paste or store a bearer token, API key, client secret, authorization code, or other credential as a workaround.

`settings.example.json` is intentionally fail-soft: the server is disabled and optional, and its headers are empty. It documents the expected endpoint and Muse schema without activating protected access. Do not enable it until Muse provides a standards-based OAuth client flow or a separately reviewed trusted bridge is implemented and tested.

Muse Code user settings live at `~/.config/muse/settings.json` and must include `"schema_version": 1`. Do not overwrite an existing settings file with the example. Merge only reviewed fields after the protected authentication boundary is resolved.

Local static tests can prove the package's file contract. Live skill validation, installation, discovery, and invocation require the Muse Code binary. Protected SparkLaunch tool execution remains unavailable by design in this adapter.
