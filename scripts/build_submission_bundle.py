"""Build a deterministic SparkLaunch plugin ZIP for the submission portal."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo

try:
    from scripts.chatgpt_surface import CHATGPT_MCP_URL, public_description
    from scripts.generate_submission import build_submission
    from scripts.openai_connection import PORTAL_MCP_PATH
    from scripts.validate_portal_prerequisites import sensitive_text_findings
    from scripts.sync_plugin import (
        PACKAGE_VERSION_RE,
        _lexical_absolute,
        _normalized_content,
        _tree_links,
        expected_files,
    )
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    from chatgpt_surface import CHATGPT_MCP_URL, public_description
    from generate_submission import build_submission
    from openai_connection import PORTAL_MCP_PATH
    from validate_portal_prerequisites import sensitive_text_findings
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
PUBLIC_METADATA_PATH = ROOT / "submission/public-metadata.json"


def _validate_public_text(value: object) -> None:
    """Reject sensitive leaf strings without echoing their values in errors."""
    if isinstance(value, str):
        findings = sensitive_text_findings(value)
        if findings:
            raise ValueError("Public metadata contains sensitive material: " + ", ".join(findings))
    elif isinstance(value, dict):
        for item in value.values():
            _validate_public_text(item)
    elif isinstance(value, list):
        for item in value:
            _validate_public_text(item)


def submission_metadata() -> dict:
    """Project supported metadata into the upload, keeping secure fields out."""
    metadata = json.loads(PUBLIC_METADATA_PATH.read_text(encoding="utf-8"))
    if set(metadata) != {"schema_version", "review", "publication"} or metadata["schema_version"] != 1:
        raise ValueError("Public metadata schema is invalid")
    review, publication = metadata["review"], metadata["publication"]
    if not isinstance(review, dict) or not {"commerce", "commerce_description"} <= set(review) or set(review) - {"commerce", "commerce_description", "demo_recording_url"}:
        raise ValueError("Public review metadata contains unsupported or missing fields")
    if type(review["commerce"]) is not bool or not isinstance(review["commerce_description"], str) or not review["commerce_description"].strip():
        raise ValueError("Public commerce fields are invalid")
    if "demo_recording_url" in review:
        from urllib.parse import urlparse
        if not isinstance(review["demo_recording_url"], str):
            raise ValueError("Demo recording URL must be a string")
        url = urlparse(review["demo_recording_url"])
        if url.scheme != "https" or not url.netloc or url.username or url.password:
            raise ValueError("Demo recording must use a public HTTPS URL without credentials")
    if not isinstance(publication, dict) or set(publication) != {"countries", "release_notes"}:
        raise ValueError("Public publication metadata is invalid")
    if not isinstance(publication["countries"], list) or any(not isinstance(c, str) or re.fullmatch(r"[A-Z]{2}", c) is None for c in publication["countries"]):
        raise ValueError("Countries must be a list of country codes; [] means all countries")
    if not isinstance(publication["release_notes"], str) or not publication["release_notes"].strip():
        raise ValueError("Release notes must be nonempty")
    submission = build_submission()
    cases = {}
    for kind, key, count in (("positive", "test_cases", 5), ("negative", "negative_test_cases", 3)):
        items = submission[key]
        if not isinstance(items, list) or len(items) != count:
            raise ValueError(f"Expected exactly {count} {kind} cases")
        projected = []
        for item in items:
            fields = {"description": item.get("description"), "prompt": item.get("user_prompt")}
            if kind == "positive":
                fields.update(tools_triggered=item.get("tools_triggered"), expected_behavior=item.get("expected_output"))
                if fields["tools_triggered"] not in submission["tools"]:
                    raise ValueError("Review case references an unavailable public tool")
            if any(not isinstance(v, str) or not v.strip() for v in fields.values()):
                raise ValueError("Review case fields must be nonempty strings")
            projected.append(fields)
        cases[kind] = projected
    projected_metadata = {"review": {**review, "test_cases": cases}, "publication": publication}
    _validate_public_text(projected_metadata)
    return projected_metadata


def _public_content(relative: str, content: bytes) -> bytes:
    if relative == ".mcp.json":
        document = json.loads(content)
        document["mcpServers"]["sparklaunch"]["url"] = CHATGPT_MCP_URL
        return (json.dumps(document, indent=2) + "\n").encode("utf-8")
    if relative.endswith(".md") or relative.endswith("agents/openai.yaml"):
        text = content.decode("utf-8")
        if relative == "skills/sparklaunch-sparkclose/SKILL.md":
            connection = re.search(r"<!-- sparklaunch:connection:start -->.*?<!-- sparklaunch:connection:end -->", text, re.DOTALL)
            if connection is None:
                raise ValueError("Public skill requires the canonical connection instructions")
            text = (ROOT / "adapters/openai/public/sparklaunch-sparkclose.md").read_text(encoding="utf-8").replace("{{CONNECTION}}", connection.group())
        elif relative == "skills/sparklaunch-platform/recipes/model-and-close-a-safe.md":
            text = (ROOT / "adapters/openai/public/model-and-close-a-safe.md").read_text(encoding="utf-8")
        text = text.replace("https://sparklaun.ch/api/mcp/", CHATGPT_MCP_URL)
        text = text.replace("Model and close a SAFE", "Model and save a SAFE scenario")
        text = text.replace("Model SAFEs and manage confirmed investment closings", "Model SAFEs and inspect private investment records")
        text = text.replace("model a SAFE and review the steps to close its investment", "model a SAFE and inspect my saved scenarios and private investment records")
        text = public_description(text)
        return text.encode("utf-8")
    return content


def _portal_plugin_name(override: str | None = None) -> str | None:
    """Bind updates to an existing portal record without renaming native packages."""
    if override is None:
        evidence_path = ROOT / "submission" / "portal-prerequisites.json"
        if evidence_path.is_file():
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            override = evidence.get("candidate", {}).get("portal_plugin_name")
    if override is not None and (
        not isinstance(override, str)
        or not 1 <= len(override) <= 64
        or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", override) is None
    ):
        raise ValueError("Portal plugin name must be a lowercase slug of at most 64 characters")
    return override


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
        _portal_path(path)
        for path in _plugin_files()
        if path.relative_to(PLUGIN_ROOT).as_posix() != ".app.json"
    }
    try:
        with ZipFile(bundle) as archive:
            names = archive.namelist()
            manifest = (
                json.loads(archive.read(PLUGIN_MANIFEST))
                if names.count(PLUGIN_MANIFEST) == 1
                else None
            )
    except (OSError, BadZipFile, KeyError, ValueError) as exc:
        return [f"portal plugin ZIP is unreadable: {exc}"]

    errors: list[str] = []
    if manifest is not None:
        if not isinstance(manifest, dict):
            errors.append("portal plugin ZIP manifest must be an object")
        else:
            extensions = manifest.get("extensions") or {}
            openai = extensions.get("com.openai") if isinstance(extensions, dict) else None
            if manifest.get("apps") is not None or (
                isinstance(openai, dict) and openai.get("apps") is not None
            ):
                errors.append("portal plugin ZIP must not declare registered App references")
            if manifest.get("mcpServers") != "./.mcp.json":
                errors.append("portal plugin ZIP must reference ./.mcp.json")
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


def _portal_path(source: Path) -> str:
    relative = source.relative_to(PLUGIN_ROOT).as_posix()
    return ".mcp.json" if relative == PORTAL_MCP_PATH else relative


def build_bundle(output: Path | None = None, *, portal_plugin_name: str | None = None) -> tuple[Path, str]:
    """Write the deterministic portal archive and return its path and digest."""
    sources = _plugin_files()
    metadata = submission_metadata()
    portal_plugin_name = _portal_plugin_name(portal_plugin_name)
    if output is None:
        output = ROOT / "dist" / f"sparklaunch-chatgpt-plugin-{_plugin_version()}.zip"
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sources:
            if source.relative_to(PLUGIN_ROOT).as_posix() == ".app.json":
                continue
            relative = _portal_path(source)
            content = _archive_content(source)
            if relative == PLUGIN_MANIFEST:
                manifest = json.loads(content)
                convert_connection = manifest.get("apps") == "./.app.json"
                if convert_connection:
                    manifest.pop("apps")
                    manifest["mcpServers"] = "./.mcp.json"
                if portal_plugin_name is not None:
                    manifest["name"] = portal_plugin_name
                interface = manifest.get("interface")
                if isinstance(interface, dict) and isinstance(interface.get("longDescription"), str):
                    interface["longDescription"] = public_description(interface["longDescription"])
                manifest["extensions"] = {"com.openai": metadata}
                content = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
            content = _public_content(relative, content)
            info = ZipInfo(relative, date_time=FIXED_ZIP_TIME)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info,
                content,
                compress_type=ZIP_DEFLATED,
                compresslevel=9,
            )
    digest = hashlib.sha256(output.read_bytes()).hexdigest().upper()
    return output, digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional output ZIP path")
    parser.add_argument("--portal-plugin-name", help="Existing portal plugin slug; defaults to candidate evidence binding")
    args = parser.parse_args(argv)
    path, digest = build_bundle(args.output, portal_plugin_name=args.portal_plugin_name)
    print(json.dumps({"path": str(path), "sha256": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
