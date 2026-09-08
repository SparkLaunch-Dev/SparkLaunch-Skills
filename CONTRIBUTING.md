# Contributing to SparkLaunch

This repository contains the skills, recipes, host adapters, and package tooling
for SparkLaunch. The hosted application and backend are maintained separately.

For security reports, follow [SECURITY.md](SECURITY.md). For other issues, describe
the affected host and package version, what you expected, what happened, and how
to reproduce it with synthetic data.

## Set up a standalone checkout

Use Python 3.12, matching the repository's validation workflow. Create a local
environment from the repository root:

```sh
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or in a POSIX shell:

```sh
. .venv/bin/activate
```

Install the pinned validation dependencies:

```sh
python -m pip install -r requirements-dev.txt
```

The checked-in tool snapshot supports standalone package validation without a
SparkLaunch account or the application repository. If a sibling backend checkout
is present, optional integration tests also import its modules and require its
development dependencies. Use the backend's documented environment for those
checks, or use a standalone skills checkout for the public package checks below.

## Edit the source, then generate packages

| Change | Edit here |
| --- | --- |
| Skill instructions and skill assets | `src/skills/` |
| Founder workflow recipes | `src/recipes/` |
| Host manifests, connection instructions, and distribution notes | `adapters/` |
| Package generation and validation | `scripts/` |
| Contract regression tests and evaluation cases | `tests/` and `evals/` |
| Contributor and compatibility documentation | `README.md`, `CONTRIBUTING.md`, and `docs/` |

`plugins/` and the native host catalogs are generated outputs used for installation.
Skills and recipes are authored only in `src/`; the generator places installable
copies inside each host package. After a source change, regenerate them with:

```sh
python scripts/sync_plugin.py --write
```

Review and include the generated changes alongside their canonical source.
Do not hand-edit generated output or remove duplicate-looking assets: each
host package is self-contained.

## Run the package checks

Run these commands in order from the repository root. This is the same sequence
used by [package validation in CI](.github/workflows/validate-host-packages.yml):

```sh
python scripts/sync_plugin.py
python scripts/generate_submission.py --check
python scripts/validate_host_packages.py
python scripts/validate_submission.py
python scripts/build_submission_bundle.py
python scripts/build_release_bundles.py
python scripts/validate_portal_prerequisites.py --allow-pending
python scripts/validate_public_release.py --allow-pending
python -m pytest -q
git diff --check
```

Builds write archives and checksums to ignored `dist/` output. Build the portal
ZIP before validating its recorded digest. If a package change makes candidate
checksums stale, follow the [release runbook](submission/public-release-runbook.md)
to bind evidence to the new content. Do not copy old native-host or production
observations onto a changed candidate.

`--allow-pending` validates local consistency while leaving named external gates
pending. Passing these checks does not publish a package or prove hosted behavior.
Some filesystem tests skip when Windows lacks symbolic-link creation privileges;
they remain enabled in Linux CI. Native-host acceptance is a separate check.

## Update the runtime contract

This step is needed only when the MCP runtime changes and requires access to the
application repository and its development dependencies. Use sibling checkouts:

```text
parent/
  SparkLaunch/
    backend/
  SparkLaunch-Skills/
```

The default runtime source is `../SparkLaunch/backend`. From the skills checkout,
using the backend-capable Python environment:

```sh
python scripts/export_tool_contract_snapshot.py
python scripts/export_tool_contract_snapshot.py --check
python scripts/generate_submission.py
python scripts/sync_plugin.py --write
```

The exporter constructs the sibling runtime against a temporary SQLite database
and records its descriptors. It does not deploy the server or call a hosted
SparkLaunch environment. Review the snapshot changes and rerun the package checks.

## Prepare a pull request

Keep the change focused and preserve existing local work. Explain the problem,
the resulting behavior, and the checks you ran. Identify any checks you could not
run and distinguish local validation from deployment or native-host acceptance.

Keep credentials, customer data, signed URLs, recordings with private content,
and local agent-session output out of commits. Use synthetic test fixtures.
See the [shared safety contract](README.md#shared-safety-contract) before changing
workflow instructions or tool contracts.

Package content may be cached by plugin version. Published content changes need
a new governed version; a local rebuild does not publish a release or invalidate
an installed cache. Follow the [public release runbook](submission/public-release-runbook.md)
for versioning, acceptance evidence, and publication.

Contributions to this repository use the [Apache License 2.0](LICENSE). The
hosted-service and trademark boundaries are described in [NOTICE](NOTICE).
