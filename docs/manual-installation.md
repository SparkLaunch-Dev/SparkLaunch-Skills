# Manual skill installation

Install the complete generated skill directories for your host. A skill can
contain `SKILL.md`, assets, references, agent metadata and recipes; keep those
files together. Copying only `SKILL.md` or taking a directory from `src/skills/`
can omit dependencies that generation adds from `src/recipes/`.

| Host | Complete generated source | Installation route |
| --- | --- | --- |
| ChatGPT / Codex | `plugins/sparklaunch/` | Use the plugin catalog and [connection guide](../adapters/openai/connection.md); the registered App must be available. |
| Claude Code | `plugins/claude/sparklaunch/` | Follow the [plugin installation guide](../adapters/claude/DISTRIBUTION.md). |
| Cursor | `plugins/cursor/sparklaunch/` | Copy the complete package using the [local plugin guide](../adapters/cursor/DISTRIBUTION.md). |
| Gemini CLI | `plugins/gemini/sparklaunch/` | Follow [extension setup and account eligibility](../adapters/gemini/README.md). |
| Muse Code | Each directory inside `plugins/muse/sparklaunch/skills/` | Validate and install each complete directory using the [Muse guide](../adapters/muse/README.md). |

Individual skill installation does not install a remote connection. Use a host's
documented skill installer only when it supports local skill directories and
preserves the entire directory. For full founder journeys, install all twelve
skills together: the platform skill routes to narrower skills. Do not infer
support for an unlisted AI client, Claude web, Gemini web or Antigravity from a
different client's package.

Let the host manage SparkLaunch sign-in and permission consent. Never paste
credentials or authorization headers into skills or settings. Muse's protected
MCP connection remains disabled; installing its skills does not enable tools.
The public ChatGPT upload is prepared separately from the App-bound native Git
package; do not upload the native archive to the submission portal.

After installing, start a fresh session and verify the intended skills are
discovered. For hosts with supported OAuth, connect through their account
controls and run only `projects.list` to check accessible projects. An empty list
is a valid result. Installation verification must not create a project, publish,
send an invitation, purchase anything or change customer data.

Record the package version or source revision and distinguish installed, loaded
and authenticated states. A missing App, missing scopes and project role/plan
restrictions require different remedies; use the returned error and connection
guide rather than substituting static credentials.
