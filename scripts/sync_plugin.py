"""Build and validate every SparkLaunch host package from one canonical source tree."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILLS = ROOT / "src" / "skills"
SOURCE_RECIPES = ROOT / "src" / "recipes"
ADAPTERS = ROOT / "adapters"
SKILLS = (
    "sparklaunch-platform",
    "sparklaunch-projects",
    "sparklaunch-idea-validation",
    "sparklaunch-color-palettes",
    "sparklaunch-logo-generation",
    "sparklaunch-campaigns",
    "sparklaunch-landing-pages",
    "sparklaunch-sales-crm",
    "sparklaunch-incorporation",
    "sparklaunch-sparkcap",
    "sparklaunch-sparkroom",
    "sparklaunch-sparkclose",
)
HOSTS = ("openai", "claude", "cursor", "gemini", "muse")
INCORPORATION_RECIPES = (
    "incorporate-a-single-founder-company.md",
    "incorporate-with-collaborators.md",
    "recover-incorporation-entitlement.md",
    "resume-or-correct-incorporation.md",
    "check-incorporation-status.md",
)
CONNECTION_START = "<!-- sparklaunch:connection:start -->"
CONNECTION_END = "<!-- sparklaunch:connection:end -->"
CONNECTION_PATTERN = re.compile(
    re.escape(CONNECTION_START) + r".*?" + re.escape(CONNECTION_END),
    re.DOTALL,
)
PACKAGE_VERSION_RE = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
)


@dataclass(frozen=True)
class ExpectedFile:
    source: Path
    target: Path
    content: bytes


@dataclass(frozen=True)
class Adapter:
    host: str
    root: Path
    package_root: Path
    connection: str
    static_files: tuple[dict[str, Any], ...]


def _is_link_like(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(is_junction and is_junction())


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def _normalized_content(content: bytes) -> bytes:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _assert_contained(
    root: Path,
    candidate: Path,
    *,
    label: str,
    allow_root: bool = False,
) -> Path:
    root_absolute = _lexical_absolute(root)
    candidate_absolute = _lexical_absolute(candidate)
    try:
        relative = candidate_absolute.relative_to(root_absolute)
    except ValueError as exc:
        raise ValueError(f"{label} escapes {root_absolute}") from exc
    if not allow_root and not relative.parts:
        raise ValueError(f"{label} must name a file below {root_absolute}")
    return candidate_absolute


def _assert_no_link_components(root: Path, candidate: Path, *, label: str) -> None:
    root_absolute = _lexical_absolute(root)
    candidate_absolute = _assert_contained(
        root_absolute,
        candidate,
        label=label,
        allow_root=True,
    )
    if _is_link_like(root_absolute):
        raise ValueError(f"{label} contains a symbolic link or junction: {root_absolute}")
    current = root_absolute
    for part in candidate_absolute.relative_to(root_absolute).parts:
        current /= part
        if _is_link_like(current):
            raise ValueError(f"{label} contains a symbolic link or junction: {current}")


def _portable_relative_path(value: object, *, label: str) -> Path:
    text = str(value or "").strip()
    portable = PurePosixPath(text)
    if (
        not text
        or "\\" in text
        or portable.is_absolute()
        or ".." in portable.parts
        or re.match(r"^[A-Za-z]:", text)
    ):
        raise ValueError(f"{label} must be a portable relative path")
    return Path(*portable.parts)


def _configured_path(root: Path, value: object, *, label: str) -> Path:
    candidate = _assert_contained(
        root,
        root / _portable_relative_path(value, label=label),
        label=label,
    )
    _assert_no_link_components(root, candidate, label=label)
    return candidate


def _tree_links(root: Path) -> list[Path]:
    if _is_link_like(root):
        return [root]
    if not root.is_dir():
        return []
    links: list[Path] = []
    for directory, names, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        for name in list(names):
            candidate = parent / name
            if _is_link_like(candidate):
                links.append(candidate)
                names.remove(name)
        for name in files:
            candidate = parent / name
            if _is_link_like(candidate):
                links.append(candidate)
    return sorted(links, key=lambda path: _lexical_absolute(path).as_posix())


def _reject_tree_links(roots: tuple[Path, ...]) -> None:
    links = [link for root in roots for link in _tree_links(root)]
    if links:
        displayed = []
        for link in links:
            try:
                displayed.append(link.relative_to(ROOT).as_posix())
            except ValueError:
                displayed.append(str(link))
        raise ValueError(
            "symbolic links or junctions are not allowed in package trees: "
            + ", ".join(sorted(displayed))
        )


def _tree_files(root: Path, *, label: str) -> list[Path]:
    _reject_tree_links((root,))
    if not root.is_dir():
        raise ValueError(f"{label} is missing: {root}")
    return sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def _read_adapter(host: str) -> Adapter:
    root = _assert_contained(ADAPTERS, ADAPTERS / host, label=f"{host} adapter root")
    _assert_no_link_components(ADAPTERS, root, label=f"{host} adapter root")
    metadata_path = _configured_path(root, "adapter.json", label=f"{host} adapter metadata")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("host") != host:
        raise ValueError(f"adapter host mismatch: {metadata_path.relative_to(ROOT)}")
    plugins_root = _lexical_absolute(ROOT / "plugins")
    package_root = _assert_contained(
        plugins_root,
        ROOT / _portable_relative_path(
            metadata.get("package_path"),
            label=f"{host} adapter package_path",
        ),
        label=f"{host} adapter package_path",
    )
    _assert_no_link_components(ROOT, package_root, label=f"{host} adapter package_path")
    connection_path = _configured_path(
        root,
        metadata.get("connection_fragment"),
        label=f"{host} adapter connection_fragment",
    )
    static_files = metadata.get("static_files") or ()
    if not isinstance(static_files, list):
        raise ValueError(f"{host} adapter static_files must be a list")
    for index, item in enumerate(static_files):
        if not isinstance(item, dict):
            raise ValueError(f"{host} adapter static_files[{index}] must be an object")
        _configured_path(
            root,
            item.get("source"),
            label=f"{host} adapter static_files[{index}].source",
        )
        _configured_path(
            package_root,
            item.get("destination"),
            label=f"{host} adapter static_files[{index}].destination",
        )
    return Adapter(
        host=host,
        root=root,
        package_root=package_root,
        connection=connection_path.read_text(encoding="utf-8").strip(),
        static_files=tuple(static_files),
    )


def _base_package_version() -> str:
    manifest = json.loads(
        (ADAPTERS / "openai" / "templates" / ".codex-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    version = manifest.get("version")
    if not isinstance(version, str) or PACKAGE_VERSION_RE.fullmatch(version) is None:
        raise ValueError("Package version must be numeric major.minor.patch")
    return version


def _connection_block(fragment: str) -> str:
    if CONNECTION_START in fragment or CONNECTION_END in fragment:
        if fragment.count(CONNECTION_START) != 1 or fragment.count(CONNECTION_END) != 1:
            raise ValueError("connection fragment must contain exactly one complete sentinel block")
        return fragment
    return f"{CONNECTION_START}\n{fragment}\n{CONNECTION_END}"


def _render_connection(text: str, adapter: Adapter) -> str:
    matches = CONNECTION_PATTERN.findall(text)
    if len(matches) != 1:
        raise ValueError(
            f"canonical connected-agent document must contain one connection block; found {len(matches)}"
        )
    return CONNECTION_PATTERN.sub(_connection_block(adapter.connection), text, count=1)


def _render_static(source: Path, *, render_version: bool, base_version: str) -> bytes:
    if not render_version:
        return source.read_bytes()
    document = json.loads(source.read_text(encoding="utf-8"))
    document["version"] = base_version
    return (json.dumps(document, indent=2) + "\n").encode("utf-8")


def _append(
    files: list[ExpectedFile],
    *,
    source: Path,
    target: Path,
    content: bytes | None = None,
) -> None:
    _assert_contained(ROOT, source, label="package source")
    _assert_no_link_components(ROOT, source, label="package source")
    _assert_contained(ROOT, target, label="generated package target")
    _assert_no_link_components(ROOT, target, label="generated package target")
    files.append(ExpectedFile(source, target, source.read_bytes() if content is None else content))


def _canonical_skill_files(host: str, adapter: Adapter) -> list[ExpectedFile]:
    files: list[ExpectedFile] = []
    for skill in SKILLS:
        source_root = SOURCE_SKILLS / skill
        for source in _tree_files(source_root, label=f"canonical skill {skill}"):
            relative = source.relative_to(source_root)
            if host != "openai" and relative.as_posix() == "agents/openai.yaml":
                continue
            content = source.read_bytes()
            if relative.as_posix() == "SKILL.md":
                content = _render_connection(source.read_text(encoding="utf-8"), adapter).encode(
                    "utf-8"
                )
            _append(
                files,
                source=source,
                target=adapter.package_root / "skills" / skill / relative,
                content=content,
            )
    return files


def _recipe_files(adapter: Adapter) -> list[ExpectedFile]:
    files: list[ExpectedFile] = []
    rendered_by_name: dict[str, bytes] = {}
    for source in _tree_files(SOURCE_RECIPES, label="canonical recipes"):
        relative = source.relative_to(SOURCE_RECIPES)
        text = source.read_text(encoding="utf-8")
        if CONNECTION_START in text or CONNECTION_END in text:
            text = _render_connection(text, adapter)
        content = text.encode("utf-8")
        rendered_by_name[relative.as_posix()] = content
        _append(
            files,
            source=source,
            target=(
                adapter.package_root
                / "skills"
                / "sparklaunch-platform"
                / "recipes"
                / relative
            ),
            content=content,
        )
    if adapter.host == "openai":
        connection_source = SOURCE_RECIPES / "connect-sparklaunch.md"
        _append(
            files,
            source=connection_source,
            target=(
                adapter.package_root
                / "skills"
                / "sparklaunch-platform"
                / "recipes"
                / "connect-sparklaunch-to-chatgpt.md"
            ),
            content=rendered_by_name["connect-sparklaunch.md"],
        )
    for name in INCORPORATION_RECIPES:
        source = SOURCE_RECIPES / name
        _append(
            files,
            source=source,
            target=(
                adapter.package_root
                / "skills"
                / "sparklaunch-incorporation"
                / "recipes"
                / name
            ),
            content=rendered_by_name[name],
        )
    return files


def _package_files(adapter: Adapter, *, base_version: str) -> list[ExpectedFile]:
    files = _canonical_skill_files(adapter.host, adapter) + _recipe_files(adapter)
    for index, item in enumerate(adapter.static_files):
        source = _configured_path(
            adapter.root,
            item.get("source"),
            label=f"{adapter.host} adapter static_files[{index}].source",
        )
        target = _configured_path(
            adapter.package_root,
            item.get("destination"),
            label=f"{adapter.host} adapter static_files[{index}].destination",
        )
        _append(
            files,
            source=source,
            target=target,
            content=_render_static(
                source,
                render_version=bool(item.get("render_package_version")),
                base_version=base_version,
            ),
        )
    _append(files, source=ROOT / "LICENSE", target=adapter.package_root / "LICENSE")
    _append(files, source=ROOT / "NOTICE", target=adapter.package_root / "NOTICE")
    if adapter.host == "openai":
        asset_root = adapter.root / "assets"
        for source in _tree_files(asset_root, label="OpenAI adapter assets"):
            _append(
                files,
                source=source,
                target=adapter.package_root / "assets" / source.relative_to(asset_root),
            )
    return files


def _catalog_files(adapters: dict[str, Adapter], base_version: str) -> list[ExpectedFile]:
    files: list[ExpectedFile] = []
    for host in ("claude", "cursor"):
        catalog = {
            "name": "sparklaunch-skills",
            "owner": {"name": "SparkLaunch", "email": "support@sparklaun.ch"},
            "metadata": {"description": "SparkLaunch founder workflow plugins."},
            "plugins": [{
                "name": "sparklaunch",
                "source": "./" + adapters[host].package_root.relative_to(ROOT).as_posix(),
                "version": base_version,
                "description": "Connected SparkLaunch founder workflows.",
                "license": "Apache-2.0",
            }],
        }
        _append(
            files, source=adapters[host].root / "adapter.json",
            target=ROOT / f".{host}-plugin" / "marketplace.json",
            content=(json.dumps(catalog, indent=2) + "\n").encode("utf-8"),
        )
    return files


def expected_files() -> list[ExpectedFile]:
    base_version = _base_package_version()
    adapters = {host: _read_adapter(host) for host in HOSTS}
    files: list[ExpectedFile] = []
    for host in HOSTS:
        files.extend(_package_files(adapters[host], base_version=base_version))
    files.extend(_catalog_files(adapters, base_version))
    targets = [_lexical_absolute(item.target) for item in files]
    if len(targets) != len(set(targets)):
        raise ValueError("host package plan contains duplicate target files")
    return files


def _generated_roots() -> tuple[Path, ...]:
    return (
        ROOT / "plugins" / "sparklaunch",
        ROOT / "plugins" / "claude" / "sparklaunch",
        ROOT / "plugins" / "cursor" / "sparklaunch",
        ROOT / "plugins" / "gemini" / "sparklaunch",
        ROOT / "plugins" / "muse" / "sparklaunch",
    )


def _remove_empty_generated_directories() -> None:
    for root in _generated_roots():
        if not root.is_dir():
            continue
        for directory in sorted(
            (
                path
                for path in root.rglob("*")
                if path.is_dir() and not _is_link_like(path)
            ),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            try:
                directory.rmdir()
            except OSError:
                pass


def sync(*, write: bool) -> list[str]:
    generated_roots = _generated_roots()
    _reject_tree_links((SOURCE_SKILLS, SOURCE_RECIPES, ADAPTERS, *generated_roots))
    files = expected_files()
    expected = {_lexical_absolute(item.target) for item in files}
    errors: list[str] = []
    for item in files:
        if write:
            _assert_no_link_components(ROOT, item.target, label="generated package target")
            item.target.parent.mkdir(parents=True, exist_ok=True)
            _assert_no_link_components(ROOT, item.target, label="generated package target")
            item.target.write_bytes(item.content)
        if not item.target.is_file():
            errors.append(f"missing generated file: {item.target.relative_to(ROOT)}")
        elif _normalized_content(item.target.read_bytes()) != _normalized_content(
            item.content
        ):
            errors.append(f"generated file differs: {item.target.relative_to(ROOT)}")

    actual = {
        _lexical_absolute(path): path
        for root in generated_roots
        if root.is_dir()
        for path in root.rglob("*")
        if path.is_file()
    }
    for extra in sorted(set(actual) - expected, key=lambda path: path.as_posix()):
        extra_path = actual[extra]
        if write:
            if not any(
                _lexical_absolute(extra_path).is_relative_to(_lexical_absolute(root))
                for root in generated_roots
            ):
                raise ValueError(f"refusing to remove out-of-tree generated file: {extra_path}")
            extra_path.unlink()
        else:
            errors.append(f"unexpected generated file: {extra_path.relative_to(ROOT)}")
    if write:
        _remove_empty_generated_directories()
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="overwrite generated host packages and catalogs"
    )
    args = parser.parse_args()
    try:
        errors = sync(write=args.write)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(exc)
        return 1
    if errors:
        print("\n".join(errors))
        return 1
    print(
        f"Validated {len(expected_files())} generated files across "
        f"{len(HOSTS)} host packages and native catalogs."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
