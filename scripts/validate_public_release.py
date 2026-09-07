"""Fail-closed release gate; static coverage is never native-client evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

try:
    from scripts.build_release_bundles import candidate_identity
    from scripts.sync_plugin import (
        ROOT,
        HOSTS,
        _assert_no_link_components,
        _portable_relative_path,
    )
    from scripts.validate_portal_prerequisites import (
        sensitive_text_findings,
        _candidate_build_time,
    )
    from scripts.verify_production_contract import verify, VerificationError
except ImportError:
    from build_release_bundles import candidate_identity
    from sync_plugin import (
        ROOT,
        HOSTS,
        _assert_no_link_components,
        _portable_relative_path,
    )
    from validate_portal_prerequisites import (
        sensitive_text_findings,
        _candidate_build_time,
    )
    from verify_production_contract import verify, VerificationError

CHECKS = (
    "install",
    "skill_selection",
    "oauth_connect",
    "scope_escalation",
    "refresh",
    "disconnect",
    "safe_write",
    "file_handoff",
)
MAX_AGE = timedelta(days=7)


def _fresh(value: object, now: datetime, minimum: datetime | None = None) -> bool:
    try:
        observed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return (
            observed.tzinfo is not None
            and timedelta(0) <= now - observed <= MAX_AGE
            and (minimum is None or observed >= minimum)
        )
    except (ValueError, TypeError):
        return False


def validate(
    document: dict, *, allow_pending: bool = False, now: datetime | None = None
) -> list[str]:
    now = now or datetime.now(timezone.utc)
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["Public-release evidence must be an object"]
    if (
        set(document) != {"schema_version", "candidate", "policy_review", "hosts"}
        or document.get("schema_version") != 1
    ):
        errors.append("Public-release evidence schema is invalid")
    if document.get("candidate") != candidate_identity():
        errors.append("Public-release evidence is bound to different candidate content")
    if sensitive_text_findings(json.dumps(document)):
        errors.append("Public-release evidence contains sensitive material")
    policy = document.get("policy_review")
    if not isinstance(policy, dict) or set(policy) != {
        "status",
        "reviewer",
        "observed_at",
        "evidence_path",
        "evidence_sha256",
    }:
        errors.append("Policy review record is invalid")
    else:
        errors.extend(
            _record_errors(
                policy,
                "policy",
                allow_pending=allow_pending,
                now=now,
                candidate=document.get("candidate"),
            )
        )
    hosts = document.get("hosts")
    if not isinstance(hosts, dict) or set(hosts) != set(HOSTS):
        return errors + ["Native-host evidence must enumerate all five hosts"]
    for host, record in hosts.items():
        if not isinstance(record, dict) or set(record) != {
            "status",
            "client_version",
            "observed_at",
            "evidence_path",
            "evidence_sha256",
            "checks",
        }:
            errors.append(f"{host}: native-host evidence schema is invalid")
            continue
        checks = record["checks"]
        if (
            not isinstance(checks, dict)
            or set(checks) != set(CHECKS)
            or any(
                not isinstance(value, str) or value not in {"pending", "pass", "fail"}
                for value in checks.values()
            )
        ):
            errors.append(f"{host}: native check matrix is invalid")
        if record["status"] == "verified" and (
            not isinstance(checks, dict)
            or any(checks.get(check) != "pass" for check in CHECKS)
        ):
            errors.append(
                f"{host}: verified status requires every native check to pass"
            )
        if (
            record["status"] == "pending"
            and isinstance(checks, dict)
            and any(value != "pending" for value in checks.values())
        ):
            errors.append(
                f"{host}: partial observations belong in an evidence report, not a pending acceptance claim"
            )
        errors.extend(
            _record_errors(
                record,
                host,
                allow_pending=allow_pending,
                now=now,
                candidate=document.get("candidate"),
            )
        )
    return errors


def _record_errors(
    record: dict, label: str, *, allow_pending: bool, now: datetime, candidate: dict
) -> list[str]:
    if record.get("status") == "pending":
        retained = any(
            record.get(key) is not None
            for key in (
                "observed_at",
                "evidence_path",
                "evidence_sha256",
                "client_version",
                "reviewer",
            )
        )
        errors = []
        if retained:
            errors.append(f"{label}: pending record retains verified claims")
        if not allow_pending:
            errors.append(f"{label}: acceptance evidence is pending")
        return errors
    if record.get("status") != "verified":
        return [f"{label}: status must be pending or verified"]
    errors = []
    build_errors: list[str] = []
    build_time = _candidate_build_time(
        candidate if isinstance(candidate, dict) else {}, build_errors
    )
    if build_errors or not _fresh(record.get("observed_at"), now, build_time):
        errors.append(
            f"{label}: evidence must follow the candidate build and be within the past seven days"
        )
    identity_field = "reviewer" if label == "policy" else "client_version"
    if (
        not isinstance(record.get(identity_field), str)
        or not record[identity_field].strip()
    ):
        errors.append(f"{label}: {identity_field} is required")
    digest = record.get("evidence_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        errors.append(f"{label}: evidence digest is invalid")
    try:
        relative = _portable_relative_path(
            record.get("evidence_path"), label="evidence"
        )
        path = ROOT / relative
        if (
            not path.is_relative_to(ROOT / "submission/evidence")
            or path.suffix != ".json"
        ):
            raise ValueError("Evidence must be a JSON report under submission/evidence")
        _assert_no_link_components(ROOT, path, label="evidence")
        raw = path.read_bytes()
        if len(raw) > 256 * 1024:
            raise ValueError("Evidence exceeds the size limit")
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if hashlib.sha256(text.encode()).hexdigest() != digest:
            errors.append(f"{label}: evidence file digest differs")
        report = json.loads(text)
        if sensitive_text_findings(text):
            errors.append(f"{label}: evidence file contains sensitive material")
        expected_keys = {"candidate", "observed_at", "surface", "results"}
        if (
            not isinstance(report, dict)
            or set(report) != expected_keys
            or report.get("candidate") != candidate
            or report.get("observed_at") != record.get("observed_at")
            or report.get("surface") != label
        ):
            errors.append(f"{label}: evidence report identity/schema differs")
        results = report.get("results") if isinstance(report, dict) else None
        required = (
            ("sparkclose_classification", "platform_guidelines", "reviewer_access")
            if label == "policy"
            else CHECKS
        )
        if not isinstance(results, dict) or set(results) != set(required):
            errors.append(f"{label}: evidence report results are incomplete")
        else:
            for check in required:
                result = results[check]
                if (
                    not isinstance(result, dict)
                    or set(result) != {"status", "observation"}
                    or result.get("status") != "pass"
                    or not isinstance(result.get("observation"), str)
                    or len(result["observation"].strip()) < 20
                ):
                    errors.append(
                        f"{label}: {check} needs a passing result and a concrete observation"
                    )
    except (OSError, ValueError, UnicodeError):
        errors.append(f"{label}: evidence file is missing, unsafe, or malformed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="Source/PR validation only; not a publication gate",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Require a fresh authenticated full-contract production comparison",
    )
    args = parser.parse_args()
    if args.allow_pending and args.live:
        parser.error("--live and --allow-pending cannot be combined")
    try:
        document = json.loads(
            (ROOT / "submission/public-release.json").read_text(encoding="utf-8")
        )
        errors = validate(document, allow_pending=args.allow_pending)
        if not args.allow_pending:
            fixture = json.loads(
                (ROOT / "submission/reviewer-fixture.json").read_text(encoding="utf-8")
            )
            if (
                fixture.get("status") != "provisioned"
                or type(fixture.get("project_id")) is not int
                or fixture["project_id"] <= 0
                or fixture.get("incorporation_data") != "synthetic_only"
                or fixture.get("provider_calls_allowed") is not False
            ):
                errors.append(
                    "A provisioned, synthetic, provider-disabled reviewer fixture is required"
                )
        if args.live:
            try:
                result = verify()
                if result.get("verification") != "authenticated_full_contract":
                    errors.append("Live release verification was not authenticated")
            except VerificationError as exc:
                errors.append(str(exc))
        if not args.allow_pending and not args.live:
            errors.append(
                "Publication requires --live; recorded evidence alone is insufficient"
            )
    except (OSError, ValueError, TypeError, KeyError):
        errors = [
            "Public-release validation failed: malformed evidence or runtime response"
        ]
    print(
        "\n".join(errors)
        if errors
        else "Public-release evidence validated"
        + (
            " (pending mode; not publishable)"
            if args.allow_pending
            else " with fresh authenticated production equality"
        )
    )
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
