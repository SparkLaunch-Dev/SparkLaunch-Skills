"""Check public repository text without printing sensitive values."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

try:
    from scripts.validate_portal_prerequisites import sensitive_text_findings
except ModuleNotFoundError:
    from validate_portal_prerequisites import sensitive_text_findings


ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS_PATH = ROOT / "contracts/public-safety-exceptions.json"


def line_digest(line: str) -> str:
    return hashlib.sha256(line.strip().encode("utf-8")).hexdigest()


def validate_files(root: Path, paths: list[str], exceptions: dict) -> list[str]:
    """Only reviewed exact synthetic lines may bypass a matching category."""
    errors = []
    for name in paths:
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            errors.append(f"{name}: linked public file requires review")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError:
            errors.append(f"{name}: public file could not be read")
            continue
        allowed = exceptions.get(name, {})
        for number, line in enumerate(text.splitlines(), 1):
            findings = set(sensitive_text_findings(line))
            findings -= set(allowed.get(line_digest(line), []))
            if findings:
                errors.append(f"{name}:{number}: " + ", ".join(sorted(findings)))
        if name == "submission/reviewer-fixture.json":
            policy = json.loads(text)
            if "project_id" in policy or "user_id" in policy:
                errors.append(f"{name}: private reviewer identifiers are prohibited")
    return errors


def main() -> int:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            check=True, capture_output=True,
        )
        paths = sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})
        exceptions = json.loads(EXCEPTIONS_PATH.read_text(encoding="utf-8"))
        if (
            not isinstance(exceptions, dict)
            or set(exceptions) != {"schema_version", "reason", "files"}
            or exceptions["schema_version"] != 1
            or not isinstance(exceptions["files"], dict)
        ):
            raise ValueError("Invalid exception schema")
        errors = validate_files(ROOT, paths, exceptions["files"])
    except (OSError, ValueError, TypeError, AttributeError, subprocess.SubprocessError):
        print("Public repository check failed; file inventory or reviewed exceptions are invalid")
        return 1
    print("\n".join(errors) if errors else f"Public repository text checked across {len(paths)} files")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
