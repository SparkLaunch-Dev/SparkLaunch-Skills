"""Validate credential-free evidence for the external ChatGPT portal gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

try:
    from scripts.tool_contract_snapshot import load_snapshot
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    from tool_contract_snapshot import load_snapshot


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "submission" / "portal-prerequisites.json"
MANIFEST_PATH = ROOT / "plugins" / "sparklaunch" / ".codex-plugin" / "plugin.json"
EXPECTED_MCP_URL = "https://sparklaun.ch/api/mcp/"
EXPECTED_SCOPE_COUNT = 18
EXPECTED_DEMO_RUNBOOK = Path("submission/demo-recording-runbook.md")
EXTERNAL_GATES = (
    "authenticated_production_scan",
    "reviewer_access",
    "publisher_identity",
    "demo_recording",
)
ALLOWED_KEYS = {
    "$": {
        "schema_version",
        "candidate",
        "public_production_readiness",
        "production_deployment",
        "authenticated_production_scan",
        "reviewer_access",
        "publisher_identity",
        "demo_recording",
    },
    "$.candidate": {
        "plugin_version",
        "production_mcp_url",
        "expected_tool_count",
        "expected_oauth_scope_count",
        "bundle_path",
        "bundle_sha256",
        "deployment_status",
    },
    "$.public_production_readiness": {
        "status",
        "observed_at",
        "evidence",
        "proof_boundary",
    },
    "$.public_production_readiness.evidence": {
        "oauth_scope_count",
        "pkce",
        "dynamic_client_registration",
        "mcp_authentication_challenge",
        "domain_challenge",
    },
    "$.production_deployment": {
        "status",
        "observed_at",
        "git_revision",
        "branch_matches_origin",
        "public_backend_http_status",
        "public_frontend_http_status",
        "all_observed_deployment_targets_match_revision",
        "required_runtime_configuration_verified",
        "proof_boundary",
    },
    "$.authenticated_production_scan": {
        "status",
        "historical_result_status",
        "candidate_contract_status",
        "candidate_expected_tool_count",
        "observed_at",
        "tool_count",
        "portal_result",
        "latest_runtime_probe",
        "latest_portal_refresh",
        "proof_boundary",
    },
    "$.authenticated_production_scan.latest_runtime_probe": {
        "status",
        "observed_at",
        "deployed_git_revision",
        "oauth_flow_verified",
        "mcp_session_verified",
        "tool_count",
        "reviewer_project_count",
        "incorporation_purchase_supported_in_chatgpt",
        "temporary_grant_revoked",
    },
    "$.authenticated_production_scan.latest_portal_refresh": {
        "status",
        "observed_at",
        "oauth_permissions_granted",
        "tool_count",
        "annotation_justification_field_count",
        "scan_or_annotation_errors",
        "invite_collaborator_read_only",
        "invite_collaborator_open_world",
        "invite_collaborator_destructive",
        "commerce_purchase_link_claim",
    },
    "$.reviewer_access": {
        "status",
        "observed_at",
        "project_isolation_verified",
        "reviewer_materials_configured",
        "reviewer_materials_stored_outside_repository",
        "portal_positive_test_case_count",
        "portal_negative_test_case_count",
        "proof_boundary",
    },
    "$.publisher_identity": {
        "status",
        "observed_at",
        "organization_and_project_match",
        "proof_boundary",
    },
    "$.demo_recording": {
        "status",
        "url",
        "observed_at",
        "reviewer_access_verified",
        "runbook",
        "proof_boundary",
    },
}
SENSITIVE_KEY_PARTS = {
    "password",
    "passphrase",
    "credential",
    "credentials",
    "secret",
    "api_key",
    "private_key",
    "access_token",
    "refresh_token",
    "bearer_token",
    "authorization_code",
    "recovery_code",
    "session_cookie",
    "auth_cookie",
    "seed_phrase",
    "mnemonic",
}
FORBIDDEN_OPERATIONAL_KEYS = {
    "instances",
    "instance_id",
    "project_id",
    "reviewer_project_id",
    "password_login_without_secondary_authentication",
    "login_without_mfa_or_secondary_confirmation",
    "private_channel",
    "portal_test_credentials_populated",
    "verified_identity_label",
    "apps_management_write_access",
    "oauth_state_length",
}
SENSITIVE_VALUE_PATTERNS = (
    (
        "authorization header",
        re.compile(r"\bauthorization\s*[:=]\s*(?:bearer|basic)\s+\S+", re.IGNORECASE),
    ),
    (
        "secret assignment",
        re.compile(
            r"\b(?:api[_-]?key|client[_-]?secret|password|access[_-]?token|"
            r"refresh[_-]?token)\s*[:=]\s*\S+",
            re.IGNORECASE,
        ),
    ),
    (
        "private key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "JWT",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    ),
    (
        "provider token",
        re.compile(
            r"\b(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|"
            r"github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
            r"AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{20,})\b"
        ),
    ),
    ("URL userinfo", re.compile(r"https?://[^/\s:@]+:[^/\s@]+@", re.IGNORECASE)),
    ("infrastructure identifier", re.compile(r"\bi-[0-9a-f]{8,17}\b", re.IGNORECASE)),
    (
        "numbered reviewer project",
        re.compile(r"\b(?:reviewer|disposable)\s+project\s+`?#?\d+`?\b", re.IGNORECASE),
    ),
)


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def _is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return (
        parsed.scheme == "https"
        and bool(parsed.netloc)
        and parsed.username is None
        and parsed.password is None
        and not parsed.fragment
    )


def _require_observation(record: dict, label: str, errors: list[str]) -> None:
    if not str(record.get("observed_at") or "").strip():
        errors.append(f"{label} is verified but has no observation time")


def _is_regular_repository_file(path: Path) -> bool:
    absolute = Path(path.absolute())
    try:
        absolute.relative_to(ROOT)
        return absolute.is_file() and absolute.resolve(strict=True) == absolute
    except (OSError, ValueError):
        return False


def _normalize_key(value: object) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(value))
    return re.sub(r"[^a-z0-9]+", "_", text.casefold()).strip("_")


def _schema_errors(evidence: dict) -> list[str]:
    errors: list[str] = []
    records: dict[str, object] = {
        "$": evidence,
        "$.candidate": evidence.get("candidate"),
        "$.public_production_readiness": evidence.get("public_production_readiness"),
        "$.production_deployment": evidence.get("production_deployment"),
        "$.authenticated_production_scan": evidence.get("authenticated_production_scan"),
        "$.reviewer_access": evidence.get("reviewer_access"),
        "$.publisher_identity": evidence.get("publisher_identity"),
        "$.demo_recording": evidence.get("demo_recording"),
    }
    public = records["$.public_production_readiness"]
    scan = records["$.authenticated_production_scan"]
    records["$.public_production_readiness.evidence"] = (
        public.get("evidence") if isinstance(public, dict) else None
    )
    records["$.authenticated_production_scan.latest_runtime_probe"] = (
        scan.get("latest_runtime_probe") if isinstance(scan, dict) else None
    )
    records["$.authenticated_production_scan.latest_portal_refresh"] = (
        scan.get("latest_portal_refresh") if isinstance(scan, dict) else None
    )
    for path, allowed in ALLOWED_KEYS.items():
        record = records[path]
        if not isinstance(record, dict):
            continue
        unexpected = sorted(set(record) - allowed)
        for key in unexpected:
            errors.append(f"portal prerequisite evidence has unexpected field at {path}.{key}")
    return errors


def _sensitive_evidence_errors(value: object, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = _normalize_key(key)
            key_path = f"{path}.{key}"
            if normalized in FORBIDDEN_OPERATIONAL_KEYS or any(
                part in normalized for part in SENSITIVE_KEY_PARTS
            ):
                errors.append(
                    f"portal prerequisite evidence contains a sensitive field at {key_path}"
                )
            errors.extend(_sensitive_evidence_errors(item, key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_sensitive_evidence_errors(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        for category, pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                errors.append(
                    f"portal prerequisite evidence contains {category} at {path}"
                )
    return errors


def validate(*, allow_pending: bool) -> list[str]:
    errors: list[str] = []
    try:
        evidence = _load_json(EVIDENCE_PATH)
        manifest = _load_json(MANIFEST_PATH)
        expected_tool_count = load_snapshot()["tool_count"]
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]

    errors.extend(_schema_errors(evidence))
    errors.extend(_sensitive_evidence_errors(evidence))

    if evidence.get("schema_version") != 2:
        errors.append("portal prerequisite evidence schema_version must be 2")

    candidate = evidence.get("candidate")
    if not isinstance(candidate, dict):
        errors.append("portal prerequisite evidence is missing candidate metadata")
        candidate = {}
    if candidate.get("plugin_version") != manifest.get("version"):
        errors.append("portal prerequisite plugin version does not match the plugin manifest")
    if candidate.get("production_mcp_url") != EXPECTED_MCP_URL:
        errors.append("portal prerequisite evidence must use the canonical production MCP URL")
    if candidate.get("expected_tool_count") != expected_tool_count:
        errors.append(
            "portal prerequisite evidence tool count must match the contract snapshot"
        )
    if candidate.get("expected_oauth_scope_count") != EXPECTED_SCOPE_COUNT:
        errors.append("portal prerequisite evidence must expect exactly 18 OAuth scopes")

    bundle_relative = Path(str(candidate.get("bundle_path") or ""))
    expected_bundle_relative = Path(
        "dist"
    ) / f"sparklaunch-chatgpt-plugin-{manifest.get('version')}.zip"
    if (
        bundle_relative.is_absolute()
        or "\\" in str(candidate.get("bundle_path") or "")
        or ".." in bundle_relative.parts
        or bundle_relative != expected_bundle_relative
    ):
        errors.append("portal prerequisite candidate bundle path is invalid")
        bundle_path = ROOT / expected_bundle_relative
    else:
        bundle_path = ROOT / bundle_relative
    if not _is_regular_repository_file(bundle_path):
        errors.append("portal prerequisite candidate bundle does not exist")
    else:
        digest = hashlib.sha256(bundle_path.read_bytes()).hexdigest().upper()
        if digest != str(candidate.get("bundle_sha256") or "").upper():
            errors.append("portal prerequisite candidate bundle digest does not match")

    public = evidence.get("public_production_readiness")
    if not isinstance(public, dict) or public.get("status") != "verified":
        errors.append("public production readiness must have a verified observation")
    else:
        _require_observation(public, "public production readiness", errors)
        public_evidence = public.get("evidence")
        if not isinstance(public_evidence, dict):
            errors.append("public production readiness is missing bounded evidence")
        else:
            expected = {
                "oauth_scope_count": EXPECTED_SCOPE_COUNT,
                "pkce": "S256",
                "dynamic_client_registration": True,
                "mcp_authentication_challenge": "valid",
                "domain_challenge": "verified_by_openai_portal",
            }
            for key, value in expected.items():
                if public_evidence.get(key) != value:
                    errors.append(f"public production readiness has invalid {key}")

    deployment = evidence.get("production_deployment")
    if not isinstance(deployment, dict) or deployment.get("status") != "verified":
        errors.append("production deployment must have a verified observation")
    else:
        _require_observation(deployment, "production deployment", errors)
        if deployment.get("all_observed_deployment_targets_match_revision") is not True:
            errors.append("production deployment targets must match the recorded revision")
        if deployment.get("required_runtime_configuration_verified") is not True:
            errors.append("production deployment runtime configuration must be verified")

    scan = evidence.get("authenticated_production_scan")
    if isinstance(scan, dict) and scan.get("status") == "verified":
        _require_observation(scan, "authenticated production scan", errors)
        if scan.get("tool_count") != expected_tool_count:
            errors.append(
                "verified authenticated production scan must match the candidate tool count"
            )
        if scan.get("portal_result") != "successful":
            errors.append("verified authenticated production scan must report a successful portal result")
    elif isinstance(scan, dict) and scan.get("status") == "pending":
        historical_count = scan.get("tool_count")
        if scan.get("historical_result_status") == "verified":
            _require_observation(scan, "historical authenticated production scan", errors)
            if not isinstance(historical_count, int) or historical_count <= 0:
                errors.append(
                    "historical authenticated production scan must retain its tool count"
                )
            if scan.get("portal_result") != "successful":
                errors.append(
                    "historical authenticated production scan must retain its portal result"
                )
        if historical_count != expected_tool_count:
            if scan.get("candidate_contract_status") != "stale":
                errors.append(
                    "a historical production scan with a different tool count must be marked stale"
                )
            if scan.get("candidate_expected_tool_count") != expected_tool_count:
                errors.append(
                    "a stale production scan must record the current candidate tool count"
                )
    if isinstance(scan, dict):
        runtime_probe = scan.get("latest_runtime_probe")
        if isinstance(runtime_probe, dict) and runtime_probe.get("status") == "verified":
            _require_observation(runtime_probe, "latest runtime probe", errors)
            if runtime_probe.get("oauth_flow_verified") is not True:
                errors.append("latest runtime probe must verify the OAuth flow")
            if runtime_probe.get("mcp_session_verified") is not True:
                errors.append("latest runtime probe must verify the MCP session")
            if runtime_probe.get("reviewer_project_count") != 1:
                errors.append("latest runtime probe must verify one isolated reviewer project")

    reviewer = evidence.get("reviewer_access")
    if isinstance(reviewer, dict) and reviewer.get("status") == "verified":
        _require_observation(reviewer, "reviewer access", errors)
        if reviewer.get("project_isolation_verified") is not True:
            errors.append("verified reviewer access must prove disposable-project isolation")
        if reviewer.get("reviewer_materials_configured") is not True:
            errors.append("verified reviewer access must have configured review materials")
        if reviewer.get("reviewer_materials_stored_outside_repository") is not True:
            errors.append("reviewer materials must be stored outside the repository")
        if reviewer.get("portal_positive_test_case_count") != 5:
            errors.append("reviewer access must retain five positive portal test cases")
        if reviewer.get("portal_negative_test_case_count") != 3:
            errors.append("reviewer access must retain three negative portal test cases")

    publisher = evidence.get("publisher_identity")
    if isinstance(publisher, dict) and publisher.get("status") == "verified":
        _require_observation(publisher, "publisher identity", errors)
        if publisher.get("organization_and_project_match") is not True:
            errors.append("verified publisher identity must match the submission organization and project")

    demo = evidence.get("demo_recording")
    if isinstance(demo, dict) and demo.get("status") == "verified":
        _require_observation(demo, "demo recording", errors)
        if not _is_https_url(demo.get("url")):
            errors.append("verified demo recording must have a credential-free HTTPS URL")
        if demo.get("reviewer_access_verified") is not True:
            errors.append("verified demo recording URL must be tested without reviewer sign-in")
    if (
        not isinstance(demo, dict)
        or demo.get("runbook") != EXPECTED_DEMO_RUNBOOK.as_posix()
        or not _is_regular_repository_file(ROOT / EXPECTED_DEMO_RUNBOOK)
    ):
        errors.append("demo recording runbook is missing")

    for gate in EXTERNAL_GATES:
        record = evidence.get(gate)
        if not isinstance(record, dict) or record.get("status") not in {"pending", "verified"}:
            errors.append(f"{gate} status must be pending or verified")
        elif not allow_pending and record.get("status") != "verified":
            errors.append(f"external portal gate is still pending: {gate}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="Validate structure and safe evidence while permitting external gates to remain pending.",
    )
    args = parser.parse_args(argv)
    errors = validate(allow_pending=args.allow_pending)
    if errors:
        print("\n".join(errors))
        return 1
    print("ChatGPT portal prerequisite evidence passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
