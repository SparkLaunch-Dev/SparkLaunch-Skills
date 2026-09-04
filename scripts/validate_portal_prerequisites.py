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
RELEASE_STATE_PATH = ROOT / "release-state.json"
EXPECTED_MCP_URL = "https://sparklaun.ch/api/mcp/"
EXPECTED_SCOPE_COUNT = 18
EXPECTED_DEMO_RUNBOOK = Path("submission/demo-recording-runbook.md")
EXPECTED_MCP_PROTOCOL_VERSION = "2025-11-25"
EXPECTED_MCP_SERVER_NAME = "SparkLaunch MCP"
EXPECTED_PRODUCTION_REVISION = "058513ed28b2fadba120d5f4a0e447a723e37ddc"
EXPECTED_PRODUCTION_TAG = "prod-20260902-211542"
EXPECTED_MIGRATION_REVISION = "mcp_portability_01"
# These canonical-JSON digests pin the immutable observations copied from the
# preceding release ledger. New observations belong in new array entries.
HISTORICAL_PUBLIC_READINESS_SHA256 = (
    "2c5184a1b604988144b951e5673cd1aab53490f72b3f4eb4c9c25d8d8854aca8"
)
HISTORICAL_PRODUCTION_DEPLOYMENT_SHA256 = (
    "123d9d99b32f83d5458b7fb9b6a8943c552bfba836972b49b312745b6f389021"
)
HISTORICAL_PORTAL_SCAN_SHA256 = (
    "34a92056b79e0b224aa7c25596cb8885ed0ee42d1c788403897886ad8a4fab51"
)
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
        "historical_public_production_readiness",
        "production_deployment",
        "historical_production_deployments",
        "direct_authenticated_production_scan",
        "authenticated_production_scan",
        "historical_authenticated_production_scans",
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
        "deployed_git_revision",
        "production_tag",
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
        "domain_challenge_http_status",
        "domain_challenge_response_byte_count",
        "domain_challenge_cache_control_no_store",
        "protected_resource_metadata_http_status",
        "authorization_server_metadata_http_status",
        "public_backend_http_status",
        "public_frontend_http_status",
        "client_id_metadata_document_advertised",
    },
    "$.historical_public_production_readiness[]": {
        "status",
        "observed_at",
        "evidence",
        "proof_boundary",
    },
    "$.historical_public_production_readiness[].evidence": {
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
        "production_tag",
        "branch_matches_origin",
        "service_version",
        "migration_revision",
        "migration_status",
        "alembic_current_matches_head_on_all_backend_instances",
        "backend_refresh_successful",
        "frontend_refresh_successful",
        "launch_template_pins_match_refreshes",
        "frontend_revision_proven_by_immutable_launch_template_pin",
        "public_backend_http_status",
        "public_frontend_http_status",
        "all_observed_deployment_targets_match_revision",
        "required_runtime_configuration_verified",
        "proof_boundary",
    },
    "$.historical_production_deployments[]": {
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
    "$.direct_authenticated_production_scan": {
        "status",
        "observed_at",
        "deployed_git_revision",
        "mcp_protocol_version",
        "server_name",
        "server_version",
        "initialize_http_status",
        "initialized_notification_http_status",
        "tools_list_http_status",
        "tool_count",
        "tool_names",
        "exact_candidate_tool_name_set_match",
        "missing_tool_count",
        "extra_tool_count",
        "duplicate_tool_count",
        "output_schema_root_failure_count",
        "annotation_triplet_failure_count",
        "business_card_tools",
        "dynamic_client_registration_advertised",
        "client_id_metadata_document_advertised",
        "tool_calls_executed",
        "sensitive_values_retained",
        "proof_boundary",
    },
    "$.authenticated_production_scan": {
        "status",
        "candidate_expected_tool_count",
        "observed_at",
        "tool_count",
        "portal_result",
        "proof_boundary",
    },
    "$.historical_authenticated_production_scans[]": {
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
    "$.historical_authenticated_production_scans[].latest_runtime_probe": {
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
    "$.historical_authenticated_production_scans[].latest_portal_refresh": {
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
    "instance_refresh_id",
    "autoscaling_group",
    "launch_template_id",
    "launch_template_name",
    "launch_template_pins",
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
        "infrastructure identifier",
        re.compile(r"\blt-[0-9a-f]{8,17}\b", re.IGNORECASE),
    ),
    (
        "infrastructure identifier",
        re.compile(
            r"\b[a-z0-9-]+-(?:backend|frontend)-(?:asg-)?production[0-9a-z-]*\b",
            re.IGNORECASE,
        ),
    ),
    (
        "operational UUID",
        re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-"
            r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
            re.IGNORECASE,
        ),
    ),
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

    def check(record: object, path: str, schema_path: str) -> None:
        if not isinstance(record, dict):
            return
        unexpected = sorted(set(record) - ALLOWED_KEYS[schema_path])
        for key in unexpected:
            errors.append(f"portal prerequisite evidence has unexpected field at {path}.{key}")

    candidate = evidence.get("candidate")
    public = evidence.get("public_production_readiness")
    deployment = evidence.get("production_deployment")
    direct_scan = evidence.get("direct_authenticated_production_scan")
    scan = evidence.get("authenticated_production_scan")

    check(evidence, "$", "$")
    check(candidate, "$.candidate", "$.candidate")
    check(
        public,
        "$.public_production_readiness",
        "$.public_production_readiness",
    )
    check(
        public.get("evidence") if isinstance(public, dict) else None,
        "$.public_production_readiness.evidence",
        "$.public_production_readiness.evidence",
    )
    check(deployment, "$.production_deployment", "$.production_deployment")
    check(
        direct_scan,
        "$.direct_authenticated_production_scan",
        "$.direct_authenticated_production_scan",
    )
    check(scan, "$.authenticated_production_scan", "$.authenticated_production_scan")
    for field in ("reviewer_access", "publisher_identity", "demo_recording"):
        check(evidence.get(field), f"$.{field}", f"$.{field}")

    history_specs = {
        "historical_public_production_readiness": ("evidence",),
        "historical_production_deployments": (),
        "historical_authenticated_production_scans": (
            "latest_runtime_probe",
            "latest_portal_refresh",
        ),
    }
    for field, nested_fields in history_specs.items():
        records = evidence.get(field)
        if not isinstance(records, list):
            continue
        schema_path = f"$.{field}[]"
        for index, record in enumerate(records):
            path = f"$.{field}[{index}]"
            check(record, path, schema_path)
            for nested_field in nested_fields:
                check(
                    record.get(nested_field) if isinstance(record, dict) else None,
                    f"{path}.{nested_field}",
                    f"{schema_path}.{nested_field}",
                )
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
def _canonical_sha256(value: object) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _require_historical_snapshot(
    evidence: dict,
    field: str,
    label: str,
    expected_sha256: str,
    errors: list[str],
) -> None:
    records = evidence.get(field)
    if not isinstance(records, list) or not records:
        errors.append(f"{label} snapshot is missing")
        return
    if len(records) != 1:
        errors.append(f"{label} snapshot must contain exactly one immutable record")
    if _canonical_sha256(records[0]) != expected_sha256:
        errors.append(f"{label} snapshot changed")


def _validate_runtime_evidence(
    evidence: dict,
    candidate: dict,
    expected_tool_count: int,
    expected_tool_names: list[str],
    expected_service_version: str,
    errors: list[str],
) -> None:
    deployment = evidence.get("production_deployment")
    if not isinstance(deployment, dict) or deployment.get("status") != "verified":
        errors.append("production deployment must have a verified observation")
        deployment = {}
    else:
        _require_observation(deployment, "production deployment", errors)
        deployed_revision = str(deployment.get("git_revision") or "")
        if deployed_revision != EXPECTED_PRODUCTION_REVISION:
            errors.append("production deployment revision is stale")
        if candidate.get("deployed_git_revision") != deployed_revision:
            errors.append("candidate and production deployment revisions must match")
        if candidate.get("production_tag") != deployment.get("production_tag"):
            errors.append("candidate and production deployment tags must match")
        if deployment.get("production_tag") != EXPECTED_PRODUCTION_TAG:
            errors.append("production deployment tag is stale")
        if deployment.get("branch_matches_origin") is not True:
            errors.append("verified production deployment must match origin")
        if deployment.get("service_version") != expected_service_version:
            errors.append("production service version must match the contract snapshot")
        migration_revision = str(deployment.get("migration_revision") or "")
        if (
            migration_revision != EXPECTED_MIGRATION_REVISION
            or deployment.get("migration_status") != "applied"
        ):
            errors.append("production deployment must record the applied migration revision")
        if (
            deployment.get("alembic_current_matches_head_on_all_backend_instances")
            is not True
        ):
            errors.append("production Alembic current/head parity must be verified")
        if deployment.get("public_backend_http_status") != 200:
            errors.append("production backend health must return HTTP 200")
        if deployment.get("public_frontend_http_status") != 200:
            errors.append("production frontend must return HTTP 200")

        for field, message in (
            ("backend_refresh_successful", "production backend refresh must be successful"),
            ("frontend_refresh_successful", "production frontend refresh must be successful"),
            (
                "launch_template_pins_match_refreshes",
                "production launch-template pins must match refreshes",
            ),
            (
                "frontend_revision_proven_by_immutable_launch_template_pin",
                "production frontend revision must use an immutable launch-template pin",
            ),
        ):
            if deployment.get(field) is not True:
                errors.append(message)
        if deployment.get("all_observed_deployment_targets_match_revision") is not True:
            errors.append("production deployment targets must match the recorded revision")
        if deployment.get("required_runtime_configuration_verified") is not True:
            errors.append("production deployment runtime configuration must be verified")

    direct_scan = evidence.get("direct_authenticated_production_scan")
    if not isinstance(direct_scan, dict) or direct_scan.get("status") != "verified":
        errors.append("direct authenticated production scan must be verified")
        return
    _require_observation(direct_scan, "direct authenticated production scan", errors)
    if direct_scan.get("deployed_git_revision") != deployment.get("git_revision"):
        errors.append("direct authenticated scan revision must match production")
    if direct_scan.get("mcp_protocol_version") != EXPECTED_MCP_PROTOCOL_VERSION:
        errors.append("direct authenticated scan protocol version is stale")
    if direct_scan.get("server_name") != EXPECTED_MCP_SERVER_NAME:
        errors.append("direct authenticated scan server name is stale")
    if direct_scan.get("server_version") != expected_service_version:
        errors.append("direct authenticated scan server version is stale")
    expected_http_statuses = {
        "initialize_http_status": 200,
        "initialized_notification_http_status": 202,
        "tools_list_http_status": 200,
    }
    for field, expected_status in expected_http_statuses.items():
        if direct_scan.get(field) != expected_status:
            errors.append(f"direct authenticated scan has invalid {field}")
    if direct_scan.get("tool_count") != expected_tool_count:
        errors.append("direct authenticated scan tool count must match the candidate")
    if direct_scan.get("tool_names") != expected_tool_names:
        errors.append("direct authenticated scan tool names must match the snapshot")
    if direct_scan.get("exact_candidate_tool_name_set_match") is not True:
        errors.append("direct authenticated scan must match the candidate tool-name set")
    for count_field in (
        "missing_tool_count",
        "extra_tool_count",
        "duplicate_tool_count",
        "output_schema_root_failure_count",
        "annotation_triplet_failure_count",
        "tool_calls_executed",
    ):
        if direct_scan.get(count_field) != 0:
            errors.append(f"direct authenticated scan has nonzero {count_field}")
    if direct_scan.get("sensitive_values_retained") is not False:
        errors.append("direct authenticated scan must not retain sensitive values")
    if direct_scan.get("dynamic_client_registration_advertised") is not True:
        errors.append("direct authenticated scan must retain DCR advertisement evidence")
    if direct_scan.get("client_id_metadata_document_advertised") is not False:
        errors.append("direct authenticated scan must record CIMD as not advertised")
    if direct_scan.get("business_card_tools") != [
        "crm.delete_business_card",
        "crm.get_business_card_import",
        "crm.ingest_business_card",
        "crm.prepare_business_card_import",
    ]:
        errors.append("direct authenticated scan business-card inventory is incomplete")


def _validate_release_state(
    evidence: dict,
    release_state: dict,
    expected_service_version: str,
    errors: list[str],
) -> None:
    runtime = release_state.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("release state is missing runtime evidence")
        return

    deployment = evidence.get("production_deployment")
    direct_scan = evidence.get("direct_authenticated_production_scan")
    portal_scan = evidence.get("authenticated_production_scan")
    if not isinstance(deployment, dict):
        deployment = {}
    if not isinstance(direct_scan, dict):
        direct_scan = {}
    if not isinstance(portal_scan, dict):
        portal_scan = {}

    expected_runtime = {
        "contract_snapshot_version": expected_service_version,
        "deployment_status": "verified",
        "observed_at": deployment.get("observed_at"),
        "deployed_git_revision": deployment.get("git_revision"),
        "release_tag": deployment.get("production_tag"),
        "service_version": deployment.get("service_version"),
        "migration_revision": deployment.get("migration_revision"),
        "migration_status": "applied_on_all_observed_backend_targets",
        "openai_portal_rescan_status": portal_scan.get("status"),
    }
    for field, expected in expected_runtime.items():
        if runtime.get(field) != expected:
            errors.append(f"release-state runtime has inconsistent {field}")

    release_scan = runtime.get("direct_authenticated_scan")
    if not isinstance(release_scan, dict):
        errors.append("release state is missing direct authenticated scan evidence")
    else:
        release_scan_fields = {
            "status": "status",
            "tool_count": "tool_count",
            "exact_tool_name_set_match": "exact_candidate_tool_name_set_match",
            "output_schema_root_failure_count": "output_schema_root_failure_count",
            "annotation_triplet_failure_count": "annotation_triplet_failure_count",
            "mcp_protocol_version": "mcp_protocol_version",
            "server_name": "server_name",
            "server_version": "server_version",
            "initialize_http_status": "initialize_http_status",
            "initialized_notification_http_status": "initialized_notification_http_status",
            "tools_list_http_status": "tools_list_http_status",
            "tool_calls_executed": "tool_calls_executed",
        }
        for release_field, evidence_field in release_scan_fields.items():
            if release_scan.get(release_field) != direct_scan.get(evidence_field):
                errors.append(
                    f"release-state direct scan has inconsistent {release_field}"
                )

    oauth = runtime.get("oauth")
    if not isinstance(oauth, dict):
        errors.append("release state is missing OAuth evidence")
    else:
        for field in (
            "dynamic_client_registration_advertised",
            "client_id_metadata_document_advertised",
        ):
            if oauth.get(field) != direct_scan.get(field):
                errors.append(f"release-state OAuth evidence has inconsistent {field}")


def validate(*, allow_pending: bool) -> list[str]:
    errors: list[str] = []
    try:
        evidence = _load_json(EVIDENCE_PATH)
        manifest = _load_json(MANIFEST_PATH)
        release_state = _load_json(RELEASE_STATE_PATH)
        snapshot = load_snapshot()
        expected_tool_count = snapshot["tool_count"]
        expected_tool_names = sorted(snapshot["tools"])
        expected_service_version = snapshot["server_version"]
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
    if candidate.get("deployment_status") != "verified":
        errors.append("portal prerequisite candidate deployment must be verified")

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
                "domain_challenge_http_status": 200,
                "domain_challenge_response_byte_count": 43,
                "domain_challenge_cache_control_no_store": True,
                "protected_resource_metadata_http_status": 200,
                "authorization_server_metadata_http_status": 200,
                "public_backend_http_status": 200,
                "public_frontend_http_status": 200,
                "client_id_metadata_document_advertised": False,
            }
            for key, value in expected.items():
                if public_evidence.get(key) != value:
                    errors.append(f"public production readiness has invalid {key}")
            if "domain_challenge" in public_evidence:
                errors.append(
                    "current public readiness must not reuse historical portal verification"
                )

    _require_historical_snapshot(
        evidence,
        "historical_public_production_readiness",
        "historical public-readiness",
        HISTORICAL_PUBLIC_READINESS_SHA256,
        errors,
    )
    _require_historical_snapshot(
        evidence,
        "historical_production_deployments",
        "historical production deployment",
        HISTORICAL_PRODUCTION_DEPLOYMENT_SHA256,
        errors,
    )
    _require_historical_snapshot(
        evidence,
        "historical_authenticated_production_scans",
        "historical authenticated portal scan",
        HISTORICAL_PORTAL_SCAN_SHA256,
        errors,
    )

    _validate_runtime_evidence(
        evidence,
        candidate,
        expected_tool_count,
        expected_tool_names,
        expected_service_version,
        errors,
    )
    errors.extend(_sensitive_evidence_errors(release_state, "$release_state"))
    _validate_release_state(
        evidence,
        release_state,
        expected_service_version,
        errors,
    )

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
        if scan.get("candidate_expected_tool_count") != expected_tool_count:
            errors.append("pending portal scan must record the candidate tool count")
        if scan.get("portal_result") != "pending":
            errors.append("pending portal scan must not claim a successful result")

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
