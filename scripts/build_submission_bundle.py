"""Build a deterministic, credential-free SparkLaunch submission candidate ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)
EXACT_FILES = (
    Path("README.md"),
    Path("chatgpt-app-submission.json"),
    Path("evals/skill-trigger-cases.json"),
    Path(".agents/plugins/marketplace.json"),
)
DIRECTORIES = (
    Path("plugins/sparklaunch"),
    Path("submission"),
)


def _candidate_files() -> list[Path]:
    files = [ROOT / relative for relative in EXACT_FILES]
    for directory in DIRECTORIES:
        files.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    files = sorted(set(files), key=lambda path: path.relative_to(ROOT).as_posix())
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        raise ValueError(f"Missing submission files: {', '.join(missing)}")
    forbidden = [
        str(path.relative_to(ROOT))
        for path in files
        if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}
    ]
    if forbidden:
        raise ValueError(f"Generated files are not allowed in the bundle: {', '.join(forbidden)}")
    return files


def _plugin_version() -> str:
    manifest = json.loads(
        (ROOT / "plugins/sparklaunch/.codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    version = str(manifest.get("version") or "").strip()
    if not version:
        raise ValueError("Plugin manifest version is required.")
    return version


def build_bundle(output: Path | None = None) -> tuple[Path, str]:
    """Write the deterministic archive and return its path and SHA-256 digest."""
    if output is None:
        output = ROOT / "dist" / f"sparklaunch-chatgpt-candidate-{_plugin_version()}.zip"
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for source in _candidate_files():
            relative = source.relative_to(ROOT).as_posix()
            info = ZipInfo(relative, date_time=FIXED_ZIP_TIME)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
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
