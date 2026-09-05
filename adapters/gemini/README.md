# SparkLaunch Gemini CLI adapter

This adapter is the Gemini-specific input to the repository's host-package builder. The generated package contains this manifest and context file plus the eleven canonical SparkLaunch skills.

## Local verification with Gemini CLI

After the repository's static adapter tests pass, validate an emitted package with the installed client before linking it:

```text
gemini extensions validate <generated-package-directory>
gemini extensions link <generated-package-directory>
gemini extensions list
```

Restart Gemini CLI after linking. In the interactive client, verify the extension and protected connection:

```text
/extensions list
/mcp
/mcp auth sparklaunch
```

From the shell, inspect configured MCP servers with:

```text
gemini mcp list
```

The manifest intentionally uses `httpUrl`, which selects Streamable HTTP. Gemini CLI performs OAuth discovery after the protected endpoint returns an authentication challenge and stores its own tokens. The package contains no credentials and must never ask the user to paste one.

Live linking, OAuth, refresh, revocation, tool discovery, and tool execution require Gemini CLI and a real SparkLaunch test account. Static validation alone does not prove those outcomes.

## Gemini CLI availability boundary

Google's [June 18 Gemini CLI notice](https://github.com/google-gemini/gemini-cli/discussions/28017) says that Gemini CLI stopped serving requests for individual Free, Google AI Pro, and Ultra accounts; those tiers moved to Antigravity CLI. The [original transition announcement](https://github.com/google-gemini/gemini-cli/discussions/27274) says Gemini CLI remains supported for Gemini Code Assist Standard or Enterprise, Google Cloud, and paid Gemini or Gemini Enterprise Agent Platform API-key access. This adapter is therefore a package for supported enterprise/API-key use of the legacy Gemini CLI, not an Antigravity plugin. Antigravity packaging and live compatibility require a separately governed follow-up.

Command references: [Gemini CLI extension reference](https://geminicli.com/docs/extensions/reference/) and [Gemini CLI command reference](https://geminicli.com/docs/cli/cli-reference/).
