"""Build deterministic, self-contained release assets for all five hosts."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

try:
    from scripts import sync_plugin as sync
    from scripts.build_submission_bundle import FIXED_ZIP_TIME
except ImportError:
    import sync_plugin as sync
    from build_submission_bundle import FIXED_ZIP_TIME

ROOT = sync.ROOT
RELEASE_STATE_PATH = ROOT / "release-state.json"
MANIFESTS = {
    "openai": ".codex-plugin/plugin.json",
    "claude": ".claude-plugin/plugin.json",
    "cursor": "plugin.json",
    "gemini": "gemini-extension.json",
    "muse": "settings.example.json",  # A skills package, not an invented plugin manifest.
}


def _candidate_built_at(expected_version: str) -> str:
    release_state = json.loads(RELEASE_STATE_PATH.read_text(encoding="utf-8"))
    generated = release_state.get("generated_packages")
    if not isinstance(generated, dict) or generated.get("version") != expected_version:
        raise ValueError(
            "Release-state package version must match the plugin manifest"
        )
    value = generated.get("built_at")
    if not isinstance(value, str):
        raise ValueError("Candidate built_at must be a canonical UTC timestamp")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValueError(
            "Candidate built_at must be a canonical UTC timestamp"
        ) from exc
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise ValueError("Candidate built_at must be a canonical UTC timestamp")
    return value


def candidate_identity() -> dict:
    """Bind evidence to the complete generated content and full tool snapshot.

    Evidence itself is excluded to avoid a self-referential digest. Newlines are
    normalized identically to ZIP creation so Windows/Linux produce one identity.
    """
    entries = {
        item.target.relative_to(ROOT).as_posix(): hashlib.sha256(
            sync._normalized_content(item.content)
        ).hexdigest()
        for item in sync.expected_files()
    }
    snapshot = json.loads(
        (ROOT / "contracts/tools.snapshot.json").read_text(encoding="utf-8")
    )
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
    entries["contracts/tools.snapshot.json"] = hashlib.sha256(canonical).hexdigest()
    for name in ("chatgpt-app-submission.json", "submission/reviewer-fixture.json"):
        document = json.loads((ROOT / name).read_text(encoding="utf-8"))
        entries[name] = hashlib.sha256(
            json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    version = sync._base_package_version()
    return {
        "plugin_version": version,
        "built_at": _candidate_built_at(version),
        "server_version": snapshot["server_version"],
        "tool_count": snapshot["tool_count"],
        "content_sha256": hashlib.sha256(
            json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def build_releases(output_dir: Path | None = None) -> dict:
    errors = sync.sync(write=False)
    if errors:
        raise ValueError("Generated package validation failed: " + "; ".join(errors))
    output_dir = output_dir or ROOT / "dist/release"
    # Never let an archive overwrite a source or follow an existing symlink.
    absolute = sync._lexical_absolute(output_dir)
    sync._assert_no_link_components(
        Path(absolute.anchor), absolute, label="release output"
    )
    if absolute == ROOT or any(
        absolute.is_relative_to(ROOT / p)
        for p in (
            "src",
            "adapters",
            "plugins",
            "contracts",
            "scripts",
            "tests",
            "submission",
        )
    ):
        raise ValueError("Release output must not be a source/package directory")
    absolute.mkdir(parents=True, exist_ok=True)
    identity = candidate_identity()
    version = sync._base_package_version()
    if sync.PACKAGE_VERSION_RE.fullmatch(version) is None:
        raise ValueError("Release version must be a numeric major.minor.patch")
    assets: list[dict] = []
    planned = sync.expected_files()
    for host in sync.HOSTS:
        package = sync._read_adapter(host).package_root
        content = {
            item.target.relative_to(package).as_posix(): sync._normalized_content(
                item.content
            )
            for item in planned
            if item.target.is_relative_to(package)
        }
        if (
            MANIFESTS[host] not in content
            or not {"LICENSE", "NOTICE"} <= content.keys()
        ):
            raise ValueError(f"{host} package is not self-contained")
        # Gemini must select its own archive from this multi-host release. A
        # generic ZIP would be ambiguous alongside the other four hosts' ZIPs.
        names = (
            [f"{platform}.sparklaunch.zip" for platform in ("darwin", "linux", "win32")]
            if host == "gemini"
            else [f"sparklaunch-{host}-{version}.zip"]
        )
        for name in names:
            path = absolute / name
            sync._assert_no_link_components(absolute, path, label="release archive")
            with ZipFile(
                path, "w", compression=ZIP_DEFLATED, compresslevel=9
            ) as archive:
                for relative, data in sorted(content.items()):
                    info = ZipInfo(relative, date_time=FIXED_ZIP_TIME)
                    info.compress_type = ZIP_DEFLATED
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    archive.writestr(
                        info, data, compress_type=ZIP_DEFLATED, compresslevel=9
                    )
            assets.append(
                {
                    "host": host,
                    "file": name,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    result = {"schema_version": 2, "candidate": identity, "assets": assets}
    for name in ("release-manifest.json", "SHA256SUMS"):
        sync._assert_no_link_components(
            absolute, absolute / name, label="release metadata"
        )
    (absolute / "release-manifest.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (absolute / "SHA256SUMS").write_text(
        "".join(f"{asset['sha256']}  {asset['file']}\n" for asset in assets),
        encoding="utf-8",
        newline="\n",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build_releases(args.output_dir), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Release build failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
