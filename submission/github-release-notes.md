# SparkLaunch plugin packages

This release contains deterministic, checksummed SparkLaunch packages for OpenAI,
Claude, Cursor, Gemini CLI, and Muse Code, generated from one canonical skills and
MCP contract source.

- Package twelve founder-workflow skills with the service 1.11.0 snapshot of
  138 full-host tools and 121 public ChatGPT tools. The public SparkClose profile
  supports planning and private records rather than investment execution.
- Keep validation workspace creation separate from explicitly requested research;
  creation-only requests stop after creation and saved-state verification.
- Include self-contained host archives, Apache-2.0 licensing, NOTICE, and a
  release manifest with SHA-256 checksums.
- Keep authentication on the canonical SparkLaunch OAuth resource, with separate
  full-host and public ChatGPT MCP profiles;
  package publication does not grant account, project, plan, or workflow access.
- Treat Muse Code as a skills-only package: its protected MCP configuration remains
  disabled because Muse does not yet document the required OAuth lifecycle, so this
  release does not claim protected-tool parity for Muse.
- Preserve vendor-review boundaries: a GitHub release does not by itself mean a
  host directory, marketplace, or OpenAI submission has been approved.

The publishing workflow permits this release only from `main` after strict
candidate, production-contract, native-host, reviewer, policy, and artifact gates
pass. See the bundled release manifest and checksums for the exact candidate.
