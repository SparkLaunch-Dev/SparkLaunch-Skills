"""Deterministically mirror canonical SparkLaunch skills into the plugin bundle."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SKILLS = ROOT / "plugins" / "sparklaunch" / "skills"
SKILLS = (
    "sparklaunch-platform",
    "sparklaunch-projects",
    "sparklaunch-idea-validation",
    "sparklaunch-color-palettes",
    "sparklaunch-logo-generation",
    "sparklaunch-campaigns",
    "sparklaunch-landing-pages",
    "sparklaunch-sales-crm",
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_pairs() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for skill in SKILLS:
        source_root = ROOT / skill
        for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
            pairs.append((source, PLUGIN_SKILLS / skill / source.relative_to(source_root)))
    recipes = ROOT / "recipes"
    for source in sorted(path for path in recipes.rglob("*") if path.is_file()):
        pairs.append(
            (
                source,
                PLUGIN_SKILLS / "sparklaunch-platform" / "recipes" / source.relative_to(recipes),
            )
        )
    return pairs


def sync(*, write: bool) -> list[str]:
    errors: list[str] = []
    for source, target in expected_pairs():
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if not target.is_file():
            errors.append(f"missing packaged file: {target.relative_to(ROOT)}")
        elif _digest(source) != _digest(target):
            errors.append(f"packaged file differs: {target.relative_to(ROOT)}")

    expected = {target.resolve() for _, target in expected_pairs()}
    actual = {
        path.resolve()
        for skill in SKILLS
        for path in (PLUGIN_SKILLS / skill).rglob("*")
        if path.is_file()
    }
    for extra in sorted(actual - expected):
        errors.append(f"unexpected packaged file: {extra.relative_to(ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="overwrite mirrors from canonical source")
    args = parser.parse_args()
    errors = sync(write=args.write)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Validated {len(expected_pairs())} canonical-to-plugin file mirrors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
