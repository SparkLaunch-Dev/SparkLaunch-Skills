"""Validate credential-free evidence for the external ChatGPT portal gates."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlparse

try:
    from scripts.sync_plugin import PACKAGE_VERSION_RE
    from scripts.tool_contract_snapshot import load_snapshot
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    from sync_plugin import PACKAGE_VERSION_RE
    from tool_contract_snapshot import load_snapshot


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "submission" / "portal-prerequisites.json"
MANIFEST_PATH = ROOT / "plugins" / "sparklaunch" / ".codex-plugin" / "plugin.json"
RELEASE_STATE_PATH = ROOT / "release-state.json"
EXPECTED_MCP_URL = "https://sparklaun.ch/api/mcp/"
EXPECTED_DEMO_RUNBOOK = Path("submission/demo-recording-runbook.md")
EXPECTED_MCP_PROTOCOL_VERSION = "2025-11-25"
EXPECTED_MCP_SERVER_NAME = "SparkLaunch MCP"
# These canonical-JSON digests pin the immutable observations copied from the
# preceding release ledger. New observations belong in new array entries.
HISTORICAL_CANDIDATE_SHA256S = (
    "5364d6e483e10125a0c6b653d908c03b9bc9fa6348ab68eb46510c8183f914ce",
)
HISTORICAL_PUBLIC_READINESS_SHA256S = (
    "2c5184a1b604988144b951e5673cd1aab53490f72b3f4eb4c9c25d8d8854aca8",
    "d8a6b2ad4068415a291dbde5faf7c76567c399ccb1abfda4a54a5bd790184c0b",
)
HISTORICAL_PRODUCTION_DEPLOYMENT_SHA256S = (
    "123d9d99b32f83d5458b7fb9b6a8943c552bfba836972b49b312745b6f389021",
    "8ee875d9526e432474df6c8ebe393dd4d1fb06879ec2fd42c830268173422835",
)
HISTORICAL_DIRECT_SCAN_SHA256S = (
    "2f158c96b57acf0718241b8289c488c0a21cc89e53c28551e28ff00b9ab35364",
)
HISTORICAL_PORTAL_SCAN_SHA256S = (
    "34a92056b79e0b224aa7c25596cb8885ed0ee42d1c788403897886ad8a4fab51",
    "526c80fecc62504c67218f687c67e519845056f6738e9c8f275038d8c98e678a",
)
EXTERNAL_GATES = (
    "public_production_readiness",
    "production_deployment",
    "direct_authenticated_production_scan",
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
        "historical_candidates",
        "historical_public_production_readiness",
        "production_deployment",
        "historical_production_deployments",
        "direct_authenticated_production_scan",
        "historical_direct_authenticated_production_scans",
        "authenticated_production_scan",
        "historical_authenticated_production_scans",
        "reviewer_access",
        "publisher_identity",
        "demo_recording",
    },
    "$.candidate": {
        "plugin_version",
        "built_at",
        "service_version",
        "production_mcp_url",
        "expected_tool_count",
        "expected_oauth_scope_count",
        "bundle_path",
        "bundle_sha256",
    },
    "$.historical_candidates[]": {
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
        "candidate_plugin_version",
        "candidate_service_version",
        "candidate_expected_oauth_scope_count",
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
        "domain_challenge_http_status",
        "domain_challenge_response_byte_count",
        "domain_challenge_cache_control_no_store",
        "protected_resource_metadata_http_status",
        "authorization_server_metadata_http_status",
        "public_backend_http_status",
        "public_frontend_http_status",
        "client_id_metadata_document_advertised",
    },
    "$.production_deployment": {
        "status",
        "candidate_plugin_version",
        "candidate_service_version",
        "candidate_expected_tool_count",
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
    "$.direct_authenticated_production_scan": {
        "status",
        "candidate_plugin_version",
        "candidate_service_version",
        "candidate_expected_tool_count",
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
    "$.historical_direct_authenticated_production_scans[]": {
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
        "candidate_plugin_version",
        "candidate_service_version",
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
RELEASE_STATE_ALLOWED_KEYS = {
    "$release_state": {
        "schema_version",
        "generated_packages",
        "mcp_registry",
        "runtime",
        "distribution",
    },
    "$release_state.generated_packages": {"version", "built_at", "hosts", "status"},
    "$release_state.mcp_registry": {
        "candidate_descriptor_version",
        "last_known_published_version",
        "last_known_version_basis",
        "live_refresh_status",
        "publication_status",
    },
    "$release_state.runtime": {
        "contract_snapshot_version",
        "candidate",
        "last_verified_production",
    },
    "$release_state.runtime.candidate": {
        "plugin_version",
        "deployment_status",
        "direct_authenticated_scan_status",
        "openai_portal_rescan_status",
        "proof_boundary",
    },
    "$release_state.runtime.last_verified_production": {
        "observed_at",
        "deployed_git_revision",
        "release_tag",
        "service_version",
        "migration_revision",
        "migration_status",
        "direct_authenticated_scan",
        "oauth",
        "proof_boundary",
    },
    "$release_state.runtime.last_verified_production.direct_authenticated_scan": {
        "status",
        "tool_count",
        "exact_tool_name_set_match",
        "output_schema_root_failure_count",
        "annotation_triplet_failure_count",
        "mcp_protocol_version",
        "server_name",
        "server_version",
        "initialize_http_status",
        "initialized_notification_http_status",
        "tools_list_http_status",
        "tool_calls_executed",
    },
    "$release_state.runtime.last_verified_production.oauth": {
        "scope_count",
        "dynamic_client_registration_advertised",
        "client_id_metadata_document_advertised",
    },
    "$release_state.distribution": {"openai", "claude", "cursor", "gemini", "muse"},
}
EXPECTED_PACKAGE_HOSTS = ["openai", "claude", "cursor", "gemini", "muse"]
EXPECTED_REGISTRY_STATE = {
    "last_known_published_version": "1.0.0",
    "last_known_version_basis": (
        "repository release record preceding the 2026-09-02 change"
    ),
    "live_refresh_status": "not_performed_by_this_change",
    "publication_status": "not_performed_by_this_change",
}
EXPECTED_DISTRIBUTION_STATE = {
    "openai": "local_candidate_not_submitted",
    "claude": "local_public_catalog_candidate_not_listed",
    "cursor": "local_open_source_candidate_not_submitted",
    "gemini": "local_candidate",
    "muse": "skills_candidate_protected_mcp_disabled",
}
SENSITIVE_URL_PARAMETER_KEY_COMPONENTS = {
    "auth",
    "code",
    "cookie",
    "credential",
    "key",
    "passcode",
    "passphrase",
    "password",
    "pwd",
    "secret",
    "session",
    "sig",
    "signature",
    "token",
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
URL_CANDIDATE_PATTERN = re.compile(
    r"https?://[^\s<>{}\[\]\"'`]+",
    re.IGNORECASE,
)


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def _is_https_url(value: object) -> bool:
    if not isinstance(value, str) or any(
        character.isspace() or ord(character) == 127 for character in value
    ):
        return False
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        return False
    try:
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return False
    if not hostname or port == 0:
        return False
    normalized_hostname = hostname.rstrip(".").casefold()
    special_suffixes = (
        "localhost",
        ".localhost",
        ".internal",
        ".invalid",
        ".lan",
        ".local",
        ".onion",
        ".test",
    )
    if normalized_hostname == "localhost" or normalized_hostname.endswith(
        special_suffixes
    ):
        return False
    try:
        address = ipaddress.ip_address(normalized_hostname)
    except ValueError:
        labels = normalized_hostname.split(".")
        numeric_label = re.compile(r"(?:0x[0-9a-f]+|0[0-7]+|[0-9]+)")
        if len(labels) < 2 or all(numeric_label.fullmatch(label) for label in labels):
            return False
        try:
            ascii_hostname = normalized_hostname.encode("idna").decode("ascii")
        except UnicodeError:
            return False
        if len(ascii_hostname) > 253 or any(
            not re.fullmatch(
                r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?",
                label,
            )
            for label in ascii_hostname.split(".")
        ):
            return False
    else:
        if not address.is_global:
            return False
    if _url_contains_sensitive_material(parsed):
        return False
    return True


def _url_contains_sensitive_material(parsed: object) -> bool:
    pending = [
        str(component)
        for component in (
            getattr(parsed, "query", ""),
            getattr(parsed, "fragment", ""),
        )
        if component
    ]
    inspected: set[str] = set()
    while pending:
        component = pending.pop()
        for decoded in _decoded_url_component_variants(component):
            if decoded in inspected:
                continue
            inspected.add(decoded)
            if len(inspected) > 64:
                return True
            for key, item in parse_qsl(
                decoded.lstrip("/?#"), keep_blank_values=True
            ):
                key_components = set(filter(None, _normalize_key(key).split("_")))
                if key_components & SENSITIVE_URL_PARAMETER_KEY_COMPONENTS:
                    return True
                for decoded_item in _decoded_url_component_variants(item):
                    if any(
                        pattern.search(decoded_item)
                        for _, pattern in SENSITIVE_VALUE_PATTERNS
                    ):
                        return True
                    nested = urlparse(decoded_item)
                    if nested.query:
                        pending.append(nested.query)
                    if nested.fragment:
                        pending.append(nested.fragment)
    return False


def _decoded_url_component_variants(value: str) -> tuple[str, ...]:
    variants: list[str] = []
    current = value
    for _ in range(3):
        if current in variants:
            break
        variants.append(current)
        decoded = unquote(current)
        if decoded == current:
            break
        current = decoded
    return tuple(variants)


def sensitive_text_findings(value: str) -> list[str]:
    """Return unique sensitive-value categories found in reviewer-facing text."""
    findings = [
        category
        for category, pattern in SENSITIVE_VALUE_PATTERNS
        if pattern.search(value)
    ]
    for candidate in URL_CANDIDATE_PATTERN.findall(value):
        parsed = urlparse(candidate.rstrip(".,;:!?"))
        if _url_contains_sensitive_material(parsed):
            findings.append("credential-bearing URL")
    return list(dict.fromkeys(findings))


def _parse_utc_observation(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        observed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if observed.tzinfo is None or observed.utcoffset() != timezone.utc.utcoffset(
        observed
    ):
        return None
    return observed.astimezone(timezone.utc)


def _require_observation(
    record: dict, label: str, errors: list[str]
) -> datetime | None:
    value = record.get("observed_at")
    if not str(value or "").strip():
        errors.append(f"{label} is verified but has no observation time")
        return None
    observed = _parse_utc_observation(value)
    if observed is None:
        errors.append(f"{label} has an invalid UTC observation time")
    return observed


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
            errors.append(
                f"portal prerequisite evidence has unexpected field at {path}.{key}"
            )

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
        "historical_candidates": (),
        "historical_public_production_readiness": ("evidence",),
        "historical_production_deployments": (),
        "historical_direct_authenticated_production_scans": (),
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


def _release_state_schema_errors(release_state: dict) -> list[str]:
    errors: list[str] = []

    def check(record: object, path: str) -> None:
        if not isinstance(record, dict):
            errors.append(f"release state is missing object at {path}")
            return
        unexpected = sorted(set(record) - RELEASE_STATE_ALLOWED_KEYS[path])
        for key in unexpected:
            errors.append(f"release state has unexpected field at {path}.{key}")

    check(release_state, "$release_state")
    generated = release_state.get("generated_packages")
    registry = release_state.get("mcp_registry")
    runtime = release_state.get("runtime")
    distribution = release_state.get("distribution")
    check(generated, "$release_state.generated_packages")
    check(registry, "$release_state.mcp_registry")
    check(runtime, "$release_state.runtime")
    check(distribution, "$release_state.distribution")
    candidate = runtime.get("candidate") if isinstance(runtime, dict) else None
    baseline = (
        runtime.get("last_verified_production") if isinstance(runtime, dict) else None
    )
    check(candidate, "$release_state.runtime.candidate")
    check(baseline, "$release_state.runtime.last_verified_production")
    release_scan = (
        baseline.get("direct_authenticated_scan")
        if isinstance(baseline, dict)
        else None
    )
    oauth = baseline.get("oauth") if isinstance(baseline, dict) else None
    check(
        release_scan,
        "$release_state.runtime.last_verified_production.direct_authenticated_scan",
    )
    check(oauth, "$release_state.runtime.last_verified_production.oauth")
    return errors


def _candidate_build_time(candidate: dict, errors: list[str]) -> datetime | None:
    version = str(candidate.get("plugin_version") or "")
    if PACKAGE_VERSION_RE.fullmatch(version) is None:
        errors.append("candidate plugin version must be numeric major.minor.patch")
    built_at = _parse_utc_observation(candidate.get("built_at"))
    if built_at is None:
        errors.append("candidate built_at must be a valid UTC timestamp")
    return built_at


def _latest_observation(records: object) -> datetime | None:
    if not isinstance(records, list):
        return None
    observations = [
        observed
        for record in records
        if isinstance(record, dict)
        and (observed := _parse_utc_observation(record.get("observed_at"))) is not None
    ]
    return max(observations, default=None)


def _validate_current_observation_freshness(
    evidence: dict,
    candidate_build_time: datetime | None,
    errors: list[str],
) -> None:
    record_specs = (
        (
            "public_production_readiness",
            "historical_public_production_readiness",
            "public production readiness",
        ),
        (
            "production_deployment",
            "historical_production_deployments",
            "production deployment",
        ),
        (
            "direct_authenticated_production_scan",
            "historical_direct_authenticated_production_scans",
            "direct authenticated production scan",
        ),
        (
            "authenticated_production_scan",
            "historical_authenticated_production_scans",
            "authenticated production scan",
        ),
        ("demo_recording", None, "demo recording"),
    )
    current_times: dict[str, datetime] = {}
    for current_field, history_field, label in record_specs:
        record = evidence.get(current_field)
        if not isinstance(record, dict) or record.get("status") != "verified":
            continue
        observed = _parse_utc_observation(record.get("observed_at"))
        if observed is None:
            continue
        current_times[current_field] = observed
        historical = _latest_observation(
            evidence.get(history_field) if history_field is not None else None
        )
        if historical is not None and observed <= historical:
            errors.append(
                f"{label} observation must be newer than its historical baseline"
            )
        if candidate_build_time is not None and observed < candidate_build_time:
            errors.append(f"{label} observation predates the candidate build")

    deployment_time = current_times.get("production_deployment")
    public_time = current_times.get("public_production_readiness")
    direct_time = current_times.get("direct_authenticated_production_scan")
    portal_time = current_times.get("authenticated_production_scan")
    if (
        public_time is not None
        and deployment_time is not None
        and public_time < deployment_time
    ):
        errors.append(
            "public production readiness observation predates the candidate deployment"
        )
    if (
        direct_time is not None
        and deployment_time is not None
        and direct_time < deployment_time
    ):
        errors.append(
            "direct authenticated production scan observation predates the candidate deployment"
        )
    if (
        portal_time is not None
        and deployment_time is not None
        and portal_time < deployment_time
    ):
        errors.append(
            "authenticated production scan observation predates the candidate deployment"
        )
    if (
        portal_time is not None
        and direct_time is not None
        and portal_time < direct_time
    ):
        errors.append(
            "authenticated production scan observation predates the direct authenticated scan"
        )


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
        for category in sensitive_text_findings(value):
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


def _require_historical_snapshots(
    evidence: dict,
    field: str,
    label: str,
    expected_sha256s: tuple[str, ...],
    errors: list[str],
) -> None:
    records = evidence.get(field)
    if not isinstance(records, list):
        errors.append(f"{label} snapshot is missing")
        return
    if len(records) != len(expected_sha256s):
        errors.append(
            f"{label} snapshot must contain exactly {len(expected_sha256s)} immutable records"
        )
    actual_sha256s = tuple(_canonical_sha256(record) for record in records)
    if actual_sha256s != expected_sha256s:
        errors.append(f"{label} snapshot changed")


def _expected_scope_count(snapshot: dict) -> int:
    scopes: set[str] = set()
    for name, entry in snapshot["tools"].items():
        contract = entry.get("contract") if isinstance(entry, dict) else None
        scope = contract.get("required_scope") if isinstance(contract, dict) else None
        if not isinstance(scope, str) or not scope.strip():
            raise ValueError(f"snapshot tool {name} is missing required_scope")
        scopes.add(scope)
    return len(scopes)


def _validate_candidate_binding(
    record: dict,
    label: str,
    candidate: dict,
    errors: list[str],
    *,
    tool_count: bool = False,
    scope_count: bool = False,
) -> None:
    expected = {
        "candidate_plugin_version": candidate.get("plugin_version"),
        "candidate_service_version": candidate.get("service_version"),
    }
    if tool_count:
        expected["candidate_expected_tool_count"] = candidate.get("expected_tool_count")
    if scope_count:
        expected["candidate_expected_oauth_scope_count"] = candidate.get(
            "expected_oauth_scope_count"
        )
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{label} has inconsistent {field}")
    if not str(record.get("proof_boundary") or "").strip():
        errors.append(f"{label} is missing a proof boundary")


def _validate_pending_record(
    record: dict,
    label: str,
    allowed_fields: set[str],
    errors: list[str],
) -> None:
    for field in sorted(set(record) - allowed_fields):
        errors.append(f"{label} is pending but contains verified field {field}")


def _validate_runtime_evidence(
    evidence: dict,
    candidate: dict,
    expected_tool_count: int,
    expected_tool_names: list[str],
    expected_service_version: str,
    expected_scope_count: int,
    errors: list[str],
) -> None:
    public = evidence.get("public_production_readiness")
    if not isinstance(public, dict):
        errors.append("public production readiness evidence is missing")
        public = {}
    else:
        _validate_candidate_binding(
            public,
            "public production readiness",
            candidate,
            errors,
            scope_count=True,
        )
        if public.get("status") == "pending":
            _validate_pending_record(
                public,
                "public production readiness",
                {
                    "status",
                    "candidate_plugin_version",
                    "candidate_service_version",
                    "candidate_expected_oauth_scope_count",
                    "proof_boundary",
                },
                errors,
            )
        elif public.get("status") == "verified":
            _require_observation(public, "public production readiness", errors)
            deployment_for_public = evidence.get("production_deployment")
            if (
                not isinstance(deployment_for_public, dict)
                or deployment_for_public.get("status") != "verified"
            ):
                errors.append(
                    "public production readiness requires a verified candidate deployment"
                )
            public_evidence = public.get("evidence")
            if not isinstance(public_evidence, dict):
                errors.append("public production readiness is missing bounded evidence")
            else:
                expected_public = {
                    "oauth_scope_count": expected_scope_count,
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
                for key, value in expected_public.items():
                    if public_evidence.get(key) != value:
                        errors.append(f"public production readiness has invalid {key}")
                if "domain_challenge" in public_evidence:
                    errors.append(
                        "current public readiness must not reuse historical portal verification"
                    )
        else:
            errors.append(
                "public production readiness status must be pending or verified"
            )

    deployment = evidence.get("production_deployment")
    if not isinstance(deployment, dict):
        errors.append("production deployment evidence is missing")
        deployment = {}
    else:
        _validate_candidate_binding(
            deployment,
            "production deployment",
            candidate,
            errors,
            tool_count=True,
        )
        if deployment.get("status") == "pending":
            _validate_pending_record(
                deployment,
                "production deployment",
                {
                    "status",
                    "candidate_plugin_version",
                    "candidate_service_version",
                    "candidate_expected_tool_count",
                    "proof_boundary",
                },
                errors,
            )
        elif deployment.get("status") == "verified":
            _require_observation(deployment, "production deployment", errors)
            if not re.fullmatch(
                r"[0-9a-f]{40}", str(deployment.get("git_revision") or "")
            ):
                errors.append("production deployment revision must be a full Git SHA")
            if not str(deployment.get("production_tag") or "").strip():
                errors.append("production deployment tag is missing")
            if deployment.get("branch_matches_origin") is not True:
                errors.append("verified production deployment must match origin")
            if deployment.get("service_version") != expected_service_version:
                errors.append(
                    "production service version must match the contract snapshot"
                )
            if (
                not str(deployment.get("migration_revision") or "").strip()
                or deployment.get("migration_status") != "applied"
            ):
                errors.append(
                    "production deployment must record the applied migration revision"
                )
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
                (
                    "backend_refresh_successful",
                    "production backend refresh must be successful",
                ),
                (
                    "frontend_refresh_successful",
                    "production frontend refresh must be successful",
                ),
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
            if (
                deployment.get("all_observed_deployment_targets_match_revision")
                is not True
            ):
                errors.append(
                    "production deployment targets must match the recorded revision"
                )
            if deployment.get("required_runtime_configuration_verified") is not True:
                errors.append(
                    "production deployment runtime configuration must be verified"
                )
        else:
            errors.append("production deployment status must be pending or verified")

    direct_scan = evidence.get("direct_authenticated_production_scan")
    if not isinstance(direct_scan, dict):
        errors.append("direct authenticated production scan evidence is missing")
        direct_scan = {}
    else:
        _validate_candidate_binding(
            direct_scan,
            "direct authenticated production scan",
            candidate,
            errors,
            tool_count=True,
        )
        if direct_scan.get("status") == "pending":
            _validate_pending_record(
                direct_scan,
                "direct authenticated production scan",
                {
                    "status",
                    "candidate_plugin_version",
                    "candidate_service_version",
                    "candidate_expected_tool_count",
                    "proof_boundary",
                },
                errors,
            )
        elif direct_scan.get("status") == "verified":
            _require_observation(
                direct_scan, "direct authenticated production scan", errors
            )
            if deployment.get("status") != "verified":
                errors.append(
                    "direct authenticated production scan requires a verified candidate deployment"
                )
            if direct_scan.get("deployed_git_revision") != deployment.get(
                "git_revision"
            ):
                errors.append(
                    "direct authenticated scan revision must match production"
                )
            if direct_scan.get("mcp_protocol_version") != EXPECTED_MCP_PROTOCOL_VERSION:
                errors.append("direct authenticated scan protocol version is stale")
            if direct_scan.get("server_name") != EXPECTED_MCP_SERVER_NAME:
                errors.append("direct authenticated scan server name is stale")
            if direct_scan.get("server_version") != expected_service_version:
                errors.append("direct authenticated scan server version is stale")
            for field, expected_status in {
                "initialize_http_status": 200,
                "initialized_notification_http_status": 202,
                "tools_list_http_status": 200,
            }.items():
                if direct_scan.get(field) != expected_status:
                    errors.append(f"direct authenticated scan has invalid {field}")
            if direct_scan.get("tool_count") != expected_tool_count:
                errors.append(
                    "direct authenticated scan tool count must match the candidate"
                )
            if direct_scan.get("tool_names") != expected_tool_names:
                errors.append(
                    "direct authenticated scan tool names must match the snapshot"
                )
            if direct_scan.get("exact_candidate_tool_name_set_match") is not True:
                errors.append(
                    "direct authenticated scan must match the candidate tool-name set"
                )
            for count_field in (
                "missing_tool_count",
                "extra_tool_count",
                "duplicate_tool_count",
                "output_schema_root_failure_count",
                "annotation_triplet_failure_count",
                "tool_calls_executed",
            ):
                if direct_scan.get(count_field) != 0:
                    errors.append(
                        f"direct authenticated scan has nonzero {count_field}"
                    )
            if direct_scan.get("sensitive_values_retained") is not False:
                errors.append(
                    "direct authenticated scan must not retain sensitive values"
                )
            if direct_scan.get("dynamic_client_registration_advertised") is not True:
                errors.append(
                    "direct authenticated scan must retain DCR advertisement evidence"
                )
            if direct_scan.get("client_id_metadata_document_advertised") is not False:
                errors.append(
                    "direct authenticated scan must record CIMD as not advertised"
                )
            if direct_scan.get("business_card_tools") != [
                "crm.delete_business_card",
                "crm.get_business_card_import",
                "crm.ingest_business_card",
                "crm.prepare_business_card_import",
            ]:
                errors.append(
                    "direct authenticated scan business-card inventory is incomplete"
                )
        else:
            errors.append(
                "direct authenticated production scan status must be pending or verified"
            )


def _validate_release_state(
    evidence: dict,
    release_state: dict,
    candidate: dict,
    expected_service_version: str,
    errors: list[str],
) -> None:
    if release_state.get("schema_version") != 3:
        errors.append("release state schema_version must be 3")
    generated = release_state.get("generated_packages")
    if isinstance(generated, dict):
        expected_generated = {
            "version": candidate.get("plugin_version"),
            "built_at": candidate.get("built_at"),
            "hosts": EXPECTED_PACKAGE_HOSTS,
            "status": "local_candidates_only",
        }
        for field, expected in expected_generated.items():
            if generated.get(field) != expected:
                errors.append(
                    f"release-state generated packages has inconsistent {field}"
                )
    registry = release_state.get("mcp_registry")
    if isinstance(registry, dict):
        expected_registry = {
            "candidate_descriptor_version": expected_service_version,
            **EXPECTED_REGISTRY_STATE,
        }
        for field, expected in expected_registry.items():
            if registry.get(field) != expected:
                errors.append(f"release-state Registry has inconsistent {field}")
    distribution = release_state.get("distribution")
    if isinstance(distribution, dict):
        for field, expected in EXPECTED_DISTRIBUTION_STATE.items():
            if distribution.get(field) != expected:
                errors.append(f"release-state distribution has inconsistent {field}")

    runtime = release_state.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("release state is missing runtime evidence")
        return
    if runtime.get("contract_snapshot_version") != expected_service_version:
        errors.append(
            "release-state runtime has inconsistent contract_snapshot_version"
        )

    deployment = evidence.get("production_deployment")
    direct_scan = evidence.get("direct_authenticated_production_scan")
    portal_scan = evidence.get("authenticated_production_scan")
    deployment = deployment if isinstance(deployment, dict) else {}
    direct_scan = direct_scan if isinstance(direct_scan, dict) else {}
    portal_scan = portal_scan if isinstance(portal_scan, dict) else {}
    candidate_state = runtime.get("candidate")
    if not isinstance(candidate_state, dict):
        errors.append("release state is missing candidate runtime status")
    else:
        expected_candidate_state = {
            "plugin_version": candidate.get("plugin_version"),
            "deployment_status": (
                "verified"
                if deployment.get("status") == "verified"
                else "not_verified_for_candidate"
            ),
            "direct_authenticated_scan_status": direct_scan.get("status"),
            "openai_portal_rescan_status": portal_scan.get("status"),
        }
        for field, expected in expected_candidate_state.items():
            if candidate_state.get(field) != expected:
                errors.append(f"release-state candidate has inconsistent {field}")
        if not str(candidate_state.get("proof_boundary") or "").strip():
            errors.append("release-state candidate is missing a proof boundary")

    historical_deployments = evidence.get("historical_production_deployments")
    historical_direct_scans = evidence.get(
        "historical_direct_authenticated_production_scans"
    )
    historical_public = evidence.get("historical_public_production_readiness")
    current_public = evidence.get("public_production_readiness")
    candidate_baseline_is_complete = (
        isinstance(current_public, dict)
        and current_public.get("status") == "verified"
        and deployment.get("status") == "verified"
        and direct_scan.get("status") == "verified"
    )
    if candidate_baseline_is_complete:
        baseline_deployment = deployment
        baseline_direct_scan = direct_scan
        baseline_public = current_public
    else:
        baseline_deployment = (
            historical_deployments[-1]
            if isinstance(historical_deployments, list) and historical_deployments
            else {}
        )
        baseline_direct_scan = (
            historical_direct_scans[-1]
            if isinstance(historical_direct_scans, list) and historical_direct_scans
            else {}
        )
        baseline_public = (
            historical_public[-1]
            if isinstance(historical_public, list) and historical_public
            else {}
        )
    baseline_public_evidence = (
        baseline_public.get("evidence")
        if isinstance(baseline_public, dict)
        and isinstance(baseline_public.get("evidence"), dict)
        else {}
    )
    baseline = runtime.get("last_verified_production")
    if not isinstance(baseline, dict):
        errors.append("release state is missing last verified production evidence")
        return
    expected_baseline = {
        "observed_at": baseline_deployment.get("observed_at"),
        "deployed_git_revision": baseline_deployment.get("git_revision"),
        "release_tag": baseline_deployment.get("production_tag"),
        "service_version": baseline_deployment.get("service_version"),
        "migration_revision": baseline_deployment.get("migration_revision"),
        "migration_status": "applied_on_all_observed_backend_targets",
    }
    for field, expected in expected_baseline.items():
        if baseline.get(field) != expected:
            errors.append(f"release-state production baseline has inconsistent {field}")
    release_scan = baseline.get("direct_authenticated_scan")
    if not isinstance(release_scan, dict):
        errors.append(
            "release state is missing baseline direct authenticated scan evidence"
        )
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
            if release_scan.get(release_field) != baseline_direct_scan.get(
                evidence_field
            ):
                errors.append(
                    f"release-state baseline direct scan has inconsistent {release_field}"
                )
    oauth = baseline.get("oauth")
    if not isinstance(oauth, dict):
        errors.append("release state is missing baseline OAuth evidence")
    else:
        expected_oauth = {
            "scope_count": baseline_public_evidence.get("oauth_scope_count"),
            "dynamic_client_registration_advertised": baseline_direct_scan.get(
                "dynamic_client_registration_advertised"
            ),
            "client_id_metadata_document_advertised": baseline_direct_scan.get(
                "client_id_metadata_document_advertised"
            ),
        }
        for field, expected in expected_oauth.items():
            if oauth.get(field) != expected:
                errors.append(f"release-state baseline OAuth has inconsistent {field}")
    if not str(baseline.get("proof_boundary") or "").strip():
        errors.append("release-state production baseline is missing a proof boundary")


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
        expected_scope_count = _expected_scope_count(snapshot)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]

    errors.extend(_schema_errors(evidence))
    errors.extend(_sensitive_evidence_errors(evidence))
    errors.extend(_release_state_schema_errors(release_state))

    if evidence.get("schema_version") != 4:
        errors.append("portal prerequisite evidence schema_version must be 4")

    candidate = evidence.get("candidate")
    if not isinstance(candidate, dict):
        errors.append("portal prerequisite evidence is missing candidate metadata")
        candidate = {}
    candidate_build_time = _candidate_build_time(candidate, errors)
    if candidate.get("plugin_version") != manifest.get("version"):
        errors.append(
            "portal prerequisite plugin version does not match the plugin manifest"
        )
    if candidate.get("production_mcp_url") != EXPECTED_MCP_URL:
        errors.append(
            "portal prerequisite evidence must use the canonical production MCP URL"
        )
    if candidate.get("expected_tool_count") != expected_tool_count:
        errors.append(
            "portal prerequisite evidence tool count must match the contract snapshot"
        )
    if candidate.get("service_version") != expected_service_version:
        errors.append(
            "portal prerequisite service version must match the contract snapshot"
        )
    if candidate.get("expected_oauth_scope_count") != expected_scope_count:
        errors.append(
            "portal prerequisite evidence OAuth scope count must match the contract snapshot"
        )

    bundle_relative = Path(str(candidate.get("bundle_path") or ""))
    expected_bundle_relative = (
        Path("dist") / f"sparklaunch-chatgpt-plugin-{manifest.get('version')}.zip"
    )
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

    _require_historical_snapshots(
        evidence,
        "historical_candidates",
        "historical candidate",
        HISTORICAL_CANDIDATE_SHA256S,
        errors,
    )
    _require_historical_snapshots(
        evidence,
        "historical_public_production_readiness",
        "historical public-readiness",
        HISTORICAL_PUBLIC_READINESS_SHA256S,
        errors,
    )
    _require_historical_snapshots(
        evidence,
        "historical_production_deployments",
        "historical production deployment",
        HISTORICAL_PRODUCTION_DEPLOYMENT_SHA256S,
        errors,
    )
    _require_historical_snapshots(
        evidence,
        "historical_direct_authenticated_production_scans",
        "historical direct authenticated production scan",
        HISTORICAL_DIRECT_SCAN_SHA256S,
        errors,
    )
    _require_historical_snapshots(
        evidence,
        "historical_authenticated_production_scans",
        "historical authenticated portal scan",
        HISTORICAL_PORTAL_SCAN_SHA256S,
        errors,
    )

    _validate_runtime_evidence(
        evidence,
        candidate,
        expected_tool_count,
        expected_tool_names,
        expected_service_version,
        expected_scope_count,
        errors,
    )
    _validate_current_observation_freshness(
        evidence,
        candidate_build_time,
        errors,
    )

    scan = evidence.get("authenticated_production_scan")
    if isinstance(scan, dict):
        _validate_candidate_binding(
            scan,
            "authenticated production scan",
            candidate,
            errors,
            tool_count=True,
        )
        if scan.get("status") == "verified":
            _require_observation(scan, "authenticated production scan", errors)
            if scan.get("tool_count") != expected_tool_count:
                errors.append(
                    "verified authenticated production scan must match the candidate tool count"
                )
            if scan.get("portal_result") != "successful":
                errors.append(
                    "verified authenticated production scan must report a successful portal result"
                )
            deployment = evidence.get("production_deployment")
            direct_scan = evidence.get("direct_authenticated_production_scan")
            if (
                not isinstance(deployment, dict)
                or deployment.get("status") != "verified"
            ):
                errors.append(
                    "verified authenticated production scan requires a verified candidate deployment"
                )
            if (
                not isinstance(direct_scan, dict)
                or direct_scan.get("status") != "verified"
            ):
                errors.append(
                    "verified authenticated production scan requires a verified direct authenticated scan"
                )
        elif scan.get("status") == "pending":
            _validate_pending_record(
                scan,
                "authenticated production scan",
                {
                    "status",
                    "candidate_plugin_version",
                    "candidate_service_version",
                    "candidate_expected_tool_count",
                    "portal_result",
                    "proof_boundary",
                },
                errors,
            )
            if scan.get("portal_result") != "pending":
                errors.append("pending portal scan must not claim a successful result")
        else:
            errors.append(
                "authenticated production scan status must be pending or verified"
            )
    else:
        errors.append("authenticated production scan evidence is missing")

    errors.extend(_sensitive_evidence_errors(release_state, "$release_state"))
    _validate_release_state(
        evidence,
        release_state,
        candidate,
        expected_service_version,
        errors,
    )

    reviewer = evidence.get("reviewer_access")
    if isinstance(reviewer, dict):
        if reviewer.get("status") == "verified":
            _require_observation(reviewer, "reviewer access", errors)
            if reviewer.get("project_isolation_verified") is not True:
                errors.append(
                    "verified reviewer access must prove disposable-project isolation"
                )
            if reviewer.get("reviewer_materials_configured") is not True:
                errors.append(
                    "verified reviewer access must have configured review materials"
                )
            if reviewer.get("reviewer_materials_stored_outside_repository") is not True:
                errors.append(
                    "reviewer materials must be stored outside the repository"
                )
            if reviewer.get("portal_positive_test_case_count") != 5:
                errors.append(
                    "reviewer access must retain five positive portal test cases"
                )
            if reviewer.get("portal_negative_test_case_count") != 3:
                errors.append(
                    "reviewer access must retain three negative portal test cases"
                )
        elif reviewer.get("status") == "pending":
            _validate_pending_record(
                reviewer,
                "reviewer access",
                {"status", "proof_boundary"},
                errors,
            )
        else:
            errors.append("reviewer access status must be pending or verified")
        if not str(reviewer.get("proof_boundary") or "").strip():
            errors.append("reviewer access is missing a proof boundary")
    else:
        errors.append("reviewer access evidence is missing")

    publisher = evidence.get("publisher_identity")
    if isinstance(publisher, dict):
        if publisher.get("status") == "verified":
            _require_observation(publisher, "publisher identity", errors)
            if publisher.get("organization_and_project_match") is not True:
                errors.append(
                    "verified publisher identity must match the submission organization and project"
                )
        elif publisher.get("status") == "pending":
            _validate_pending_record(
                publisher,
                "publisher identity",
                {"status", "proof_boundary"},
                errors,
            )
        else:
            errors.append("publisher identity status must be pending or verified")
        if not str(publisher.get("proof_boundary") or "").strip():
            errors.append("publisher identity is missing a proof boundary")
    else:
        errors.append("publisher identity evidence is missing")

    demo = evidence.get("demo_recording")
    if isinstance(demo, dict):
        if demo.get("status") == "verified":
            demo_observed = _require_observation(demo, "demo recording", errors)
            if not _is_https_url(demo.get("url")):
                errors.append(
                    "verified demo recording must have a credential-free public HTTPS URL"
                )
            if demo.get("reviewer_access_verified") is not True:
                errors.append(
                    "verified demo recording URL must be tested without reviewer sign-in"
                )
            recording_prerequisites = {
                "production_deployment": "candidate deployment",
                "authenticated_production_scan": "authenticated production scan",
                "reviewer_access": "reviewer access",
                "publisher_identity": "publisher identity",
            }
            for field, label in recording_prerequisites.items():
                prerequisite = evidence.get(field)
                if (
                    not isinstance(prerequisite, dict)
                    or prerequisite.get("status") != "verified"
                ):
                    errors.append(
                        f"verified demo recording requires verified {label}"
                    )
                    continue
                prerequisite_observed = _parse_utc_observation(
                    prerequisite.get("observed_at")
                )
                if (
                    demo_observed is not None
                    and prerequisite_observed is not None
                    and demo_observed <= prerequisite_observed
                ):
                    errors.append(
                        "demo recording observation must be later than "
                        f"{label} observation"
                    )
        elif demo.get("status") == "pending":
            if demo.get("url") is not None:
                errors.append("pending demo recording must not contain a URL")
            if demo.get("observed_at") is not None:
                errors.append(
                    "pending demo recording must not contain an observation time"
                )
            if demo.get("reviewer_access_verified") is not False:
                errors.append("pending demo recording must not claim reviewer access")
        else:
            errors.append("demo recording status must be pending or verified")
        if not str(demo.get("proof_boundary") or "").strip():
            errors.append("demo recording is missing a proof boundary")
    else:
        errors.append("demo recording evidence is missing")
    runbook_path = ROOT / EXPECTED_DEMO_RUNBOOK
    if (
        not isinstance(demo, dict)
        or demo.get("runbook") != EXPECTED_DEMO_RUNBOOK.as_posix()
        or not _is_regular_repository_file(runbook_path)
    ):
        errors.append("demo recording runbook is missing")
    else:
        try:
            runbook = runbook_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append("demo recording runbook is unreadable")
        else:
            required_runbook_markers = {
                f"exactly {expected_tool_count} tools": "tool count",
                f"service `{expected_service_version}`": "service version",
                f"{expected_scope_count} OAuth scopes": "OAuth scope count",
                "**Review SparkCap.**": "SparkCap walkthrough",
                "**Review SparkRoom.**": "SparkRoom walkthrough",
                "**Review SparkClose.**": "SparkClose walkthrough",
            }
            for marker, label in required_runbook_markers.items():
                if marker not in runbook:
                    errors.append(f"demo recording runbook has stale {label}")

    for gate in EXTERNAL_GATES:
        record = evidence.get(gate)
        if not isinstance(record, dict) or record.get("status") not in {
            "pending",
            "verified",
        }:
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
