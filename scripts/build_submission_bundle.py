"""Build a deterministic SparkLaunch plugin ZIP for the submission portal."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo

try:
    from scripts.sync_plugin import (
        PACKAGE_VERSION_RE,
        _lexical_absolute,
        _normalized_content,
        _tree_links,
        expected_files,
    )
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    from sync_plugin import (
        PACKAGE_VERSION_RE,
        _lexical_absolute,
        _normalized_content,
        _tree_links,
        expected_files,
    )


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "sparklaunch"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)
PLUGIN_MANIFEST = ".codex-plugin/plugin.json"


def _expected_plugin_content() -> dict[Path, bytes]:
    plugin_root = _lexical_absolute(PLUGIN_ROOT)
    planned: dict[Path, bytes] = {}
    for item in expected_files():
        target = _lexical_absolute(item.target)
        if target.is_relative_to(plugin_root):
            planned[target] = item.content
    return planned


def _plugin_files() -> list[Path]:
    links = _tree_links(PLUGIN_ROOT)
    if links:
        displayed = ", ".join(
            path.relative_to(PLUGIN_ROOT).as_posix()
            if path != PLUGIN_ROOT
            else "."
            for path in links
        )
        raise ValueError(
            "symbolic links or junctions are not allowed in the plugin bundle: "
            + displayed
        )
    if not PLUGIN_ROOT.is_dir():
        raise ValueError(f"Plugin root is missing: {PLUGIN_ROOT.relative_to(ROOT)}")
    manifest = PLUGIN_ROOT / PLUGIN_MANIFEST
    if not manifest.is_file():
        raise ValueError(f"Plugin manifest is missing: {manifest.relative_to(ROOT)}")
    files = sorted(
        (path for path in PLUGIN_ROOT.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(PLUGIN_ROOT).as_posix(),
    )
    forbidden = [
        str(path.relative_to(PLUGIN_ROOT))
        for path in files
        if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}
    ]
    if forbidden:
        raise ValueError(f"Generated files are not allowed in the bundle: {', '.join(forbidden)}")
    expected = _expected_plugin_content()
    actual = {_lexical_absolute(path): path for path in files}
    missing = sorted(set(expected) - set(actual), key=lambda path: path.as_posix())
    unexpected = sorted(set(actual) - set(expected), key=lambda path: path.as_posix())
    if missing:
        raise ValueError(
            "Plugin bundle is missing generated files: "
            + ", ".join(path.relative_to(_lexical_absolute(PLUGIN_ROOT)).as_posix() for path in missing)
        )
    if unexpected:
        raise ValueError(
            "Plugin bundle contains unexpected files: "
            + ", ".join(path.relative_to(_lexical_absolute(PLUGIN_ROOT)).as_posix() for path in unexpected)
        )
    differing = [
        path
        for absolute, path in actual.items()
        if _normalized_content(path.read_bytes()) != _normalized_content(expected[absolute])
    ]
    if differing:
        raise ValueError(
            "Plugin bundle contains files that differ from the generated plan: "
            + ", ".join(path.relative_to(PLUGIN_ROOT).as_posix() for path in differing)
        )
    return files


def portal_bundle_layout_errors(bundle: Path) -> list[str]:
    """Return portal-layout errors for a built SparkLaunch plugin archive."""
    expected = {
        path.relative_to(PLUGIN_ROOT).as_posix()
        for path in _plugin_files()
    }
    try:
        with ZipFile(bundle) as archive:
            names = archive.namelist()
    except (OSError, BadZipFile) as exc:
        return [f"portal plugin ZIP is unreadable: {exc}"]

    errors: list[str] = []
    if names.count(PLUGIN_MANIFEST) != 1:
        errors.append(f"portal plugin ZIP must contain exactly one root {PLUGIN_MANIFEST}")
    if len(names) != len(set(names)):
        errors.append("portal plugin ZIP contains duplicate entries")

    unsafe = [
        name
        for name in names
        if name.startswith(("/", "\\"))
        or "\\" in name
        or ".." in Path(name).parts
    ]
    if unsafe:
        errors.append("portal plugin ZIP contains unsafe entry paths")

    actual = set(names)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        errors.append("portal plugin ZIP is missing files: " + ", ".join(missing))
    if unexpected:
        errors.append("portal plugin ZIP contains non-plugin files: " + ", ".join(unexpected))
    return errors


def _plugin_version() -> str:
    manifest = json.loads(
        (PLUGIN_ROOT / PLUGIN_MANIFEST).read_text(encoding="utf-8")
    )
    version = manifest.get("version")
    if not isinstance(version, str) or PACKAGE_VERSION_RE.fullmatch(version) is None:
        raise ValueError("Plugin version must be numeric major.minor.patch")
    return version


def _archive_content(source: Path) -> bytes:
    return _normalized_content(source.read_bytes())


def build_bundle(output: Path | None = None) -> tuple[Path, str]:
    """Write the deterministic portal archive and return its path and digest."""
    sources = _plugin_files()
    if output is None:
        output = ROOT / "dist" / f"sparklaunch-chatgpt-plugin-{_plugin_version()}.zip"
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sources:
            relative = source.relative_to(PLUGIN_ROOT).as_posix()
            info = ZipInfo(relative, date_time=FIXED_ZIP_TIME)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info,
                _archive_content(source),
                compress_type=ZIP_DEFLATED,
                compresslevel=9,
            )
    digest = hashlib.sha256(output.read_bytes()).hexdigest().upper()
    return output, digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional output ZIP path")
    args = parser.parse_args(argv)
    path, digest = build_bundle(args.output)
    print(json.dumps({"path": str(path), "sha256": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
