# ruff: noqa: E402

import json
import hashlib
import os
import sys
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile

import pytest


BACKEND = Path(
    os.environ.get(
        "SPARKLAUNCH_BACKEND",
        Path(__file__).resolve().parents[2] / "SparkLaunch" / "backend",
    )
).resolve()
BACKEND_AVAILABLE = BACKEND.is_dir()
if BACKEND_AVAILABLE:
    sys.path.insert(0, str(BACKEND))
    from incorporation_contracts import parse_incorporation_draft
    from incorporation_validation import validate_incorporation_draft

import scripts.generate_submission as submission_generator
import scripts.validate_portal_prerequisites as portal_prerequisite_validator
import scripts.validate_submission as submission_validator
from scripts.build_submission_bundle import build_bundle, portal_bundle_layout_errors
from scripts.generate_submission import (
    MCP_TOOL_CONTRACTS,
    ROOT,
    build_submission,
    main as generate_submission,
)
from scripts.sync_plugin import SKILLS, expected_pairs, sync
from scripts.validate_submission import (
    CANONICAL_MCP_URL,
    REGISTRY_SCHEMA_URL,
    REGISTRY_SERVER_NAME,
    _load_json,
    _validate_registry_descriptor,
    validate,
)


def _validate_with_text_replaced(monkeypatch, path, old, new):
    original_read_text = Path.read_text
    target = path.resolve()

    def read_text(candidate, *args, **kwargs):
        text = original_read_text(candidate, *args, **kwargs)
        if candidate.resolve() == target:
            assert old in text
            return text.replace(old, new, 1)
        return text

    monkeypatch.setattr(Path, "read_text", read_text)
    return validate()


def _validate_with_bytes_replaced(monkeypatch, path, old, new):
    original_read_bytes = Path.read_bytes
    target = path.resolve()

    def read_bytes(candidate, *args, **kwargs):
        raw = original_read_bytes(candidate, *args, **kwargs)
        if candidate.resolve() == target:
            text = raw.decode("utf-8")
            assert old in text
            return text.replace(old, new, 1).encode("utf-8")
        return raw

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    return validate()


def _validate_portal_evidence(
    monkeypatch,
    tmp_path,
    evidence,
    release_state=None,
    *,
    allow_pending=True,
):
    evidence_path = tmp_path / "portal-prerequisites.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    monkeypatch.setattr(
        portal_prerequisite_validator,
        "EVIDENCE_PATH",
        evidence_path,
    )
    if release_state is not None:
        release_state_path = tmp_path / "release-state.json"
        release_state_path.write_text(json.dumps(release_state), encoding="utf-8")
        monkeypatch.setattr(
            portal_prerequisite_validator,
            "RELEASE_STATE_PATH",
            release_state_path,
        )
    return portal_prerequisite_validator.validate(allow_pending=allow_pending)


def _replace_nested_value(value, path, replacement):
    target = value
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement


def _promote_candidate_evidence(evidence, release_state):
    candidate = evidence["candidate"]
    plugin_version = candidate["plugin_version"]
    service_version = candidate["service_version"]
    tool_count = candidate["expected_tool_count"]
    scope_count = candidate["expected_oauth_scope_count"]
    revision = "a" * 40

    public = json.loads(
        json.dumps(evidence["historical_public_production_readiness"][-1])
    )
    public.update(
        {
            "status": "verified",
            "candidate_plugin_version": plugin_version,
            "candidate_service_version": service_version,
            "candidate_expected_oauth_scope_count": scope_count,
            "observed_at": "2026-09-06T20:01:00Z",
        }
    )
    public["evidence"]["oauth_scope_count"] = scope_count
    evidence["public_production_readiness"] = public

    deployment = json.loads(
        json.dumps(evidence["historical_production_deployments"][-1])
    )
    deployment.update(
        {
            "status": "verified",
            "candidate_plugin_version": plugin_version,
            "candidate_service_version": service_version,
            "candidate_expected_tool_count": tool_count,
            "observed_at": "2026-09-06T20:00:00Z",
            "git_revision": revision,
            "production_tag": "prod-candidate-test",
            "service_version": service_version,
        }
    )
    evidence["production_deployment"] = deployment

    direct_scan = json.loads(
        json.dumps(evidence["historical_direct_authenticated_production_scans"][-1])
    )
    direct_scan.update(
        {
            "status": "verified",
            "candidate_plugin_version": plugin_version,
            "candidate_service_version": service_version,
            "candidate_expected_tool_count": tool_count,
            "observed_at": "2026-09-06T20:02:00Z",
            "deployed_git_revision": revision,
            "server_version": service_version,
            "tool_count": tool_count,
            "tool_names": sorted(MCP_TOOL_CONTRACTS),
        }
    )
    evidence["direct_authenticated_production_scan"] = direct_scan

    evidence["authenticated_production_scan"].update(
        {
            "status": "verified",
            "observed_at": "2026-09-06T20:03:00Z",
            "tool_count": tool_count,
            "portal_result": "successful",
        }
    )
    evidence["demo_recording"].update(
        {
            "status": "verified",
            "url": "https://demo.sparklaun.ch/reviewer-demo",
            "observed_at": "2026-09-06T20:04:00Z",
            "reviewer_access_verified": True,
        }
    )

    release_candidate = release_state["runtime"]["candidate"]
    release_candidate.update(
        {
            "deployment_status": "verified",
            "direct_authenticated_scan_status": "verified",
            "openai_portal_rescan_status": "verified",
        }
    )
    baseline = release_state["runtime"]["last_verified_production"]
    baseline.update(
        {
            "observed_at": deployment["observed_at"],
            "deployed_git_revision": revision,
            "release_tag": deployment["production_tag"],
            "service_version": service_version,
            "migration_revision": deployment["migration_revision"],
            "migration_status": "applied_on_all_observed_backend_targets",
        }
    )
    release_scan = baseline["direct_authenticated_scan"]
    for release_field, evidence_field in {
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
    }.items():
        release_scan[release_field] = direct_scan[evidence_field]
    baseline["oauth"].update(
        {
            "scope_count": scope_count,
            "dynamic_client_registration_advertised": direct_scan[
                "dynamic_client_registration_advertised"
            ],
            "client_id_metadata_document_advertised": direct_scan[
                "client_id_metadata_document_advertised"
            ],
        }
    )
    return evidence, release_state


def test_packaged_skills_are_exact_deterministic_mirrors():
    assert SKILLS == (
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
    assert len(expected_pairs()) > 40
    assert sync(write=False) == []


def test_every_skill_distinguishes_connector_absence_from_oauth():
    required = (
        "SparkLaunch isn't loaded in this conversation.",
        "Start a new ChatGPT conversation",
        "OAuth challenge",
        "expired or revoked",
        "effective_permissions",
    )
    for skill in SKILLS:
        canonical = (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
        assert all(marker in canonical for marker in required), skill

    recipe = (ROOT / "recipes" / "connect-sparklaunch-to-chatgpt.md").read_text(
        encoding="utf-8"
    )
    assert all(marker in recipe for marker in required)
    assert "disable and re-enable or reinstall" in recipe


def test_every_skill_and_recipe_keeps_internal_references_out_of_user_output():
    for skill in SKILLS:
        canonical = (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
        assert "only as internal tool-call state" in canonical, skill

    recipe_contract = "Retain identifiers and versions only for internal tool calls"
    for recipe in (ROOT / "recipes").rglob("*.md"):
        text = recipe.read_text(encoding="utf-8")
        if recipe.name == "README.md":
            assert "only as internal tool-call state" in text
        else:
            assert recipe_contract in text, recipe.name

    project_skill = (ROOT / "sparklaunch-projects" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "report `project_id`" not in project_skill
    assert "report `task_id`" not in project_skill
    assert "identifier or version columns" in project_skill


def test_validator_rejects_a_skill_without_the_user_output_contract(monkeypatch):
    skill = SKILLS[0]

    errors = _validate_with_text_replaced(
        monkeypatch,
        ROOT / skill / "SKILL.md",
        "only as internal tool-call state",
        "only as opaque runtime state",
    )

    assert errors == [
        f"skill must keep identifiers and versions out of user-facing output: {skill}"
    ]


def test_validator_rejects_recipe_readme_without_the_user_output_contract(monkeypatch):
    errors = _validate_with_text_replaced(
        monkeypatch,
        ROOT / "recipes" / "README.md",
        "only as internal tool-call state",
        "only as opaque runtime state",
    )

    assert errors == [
        "recipe must keep identifiers and versions out of user-facing output: "
        f"{Path('recipes') / 'README.md'}"
    ]


def test_validator_rejects_an_ordinary_recipe_without_the_user_output_contract(
    monkeypatch,
):
    recipe = ROOT / "recipes" / "connect-sparklaunch-to-chatgpt.md"

    errors = _validate_with_text_replaced(
        monkeypatch,
        recipe,
        "Retain identifiers and versions only for internal tool calls",
        "Retain identifiers and versions only as opaque runtime state",
    )

    assert errors == [
        "recipe must keep identifiers and versions out of user-facing output: "
        f"{recipe.relative_to(ROOT)}"
    ]


def test_validator_rejects_positive_submission_output_without_user_friendly_presentation(
    monkeypatch,
):
    errors = _validate_with_text_replaced(
        monkeypatch,
        ROOT / "chatgpt-app-submission.json",
        "without exposing internal identifiers or versions",
        "while exposing internal identifiers and versions",
    )

    assert errors == [
        "positive submission case must require user-friendly record presentation"
    ]


def test_submission_package_is_complete():
    assert validate() == []
    marketplace = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
    )
    sparklaunch = next(
        entry for entry in marketplace["plugins"] if entry["name"] == "sparklaunch"
    )
    assert sparklaunch["policy"]["authentication"] == "ON_USE"
    generated = json.loads(
        (ROOT / "chatgpt-app-submission.json").read_text(encoding="utf-8")
    )
    assert generated == build_submission()
    assert len(generated["tools"]) == len(MCP_TOOL_CONTRACTS)
    invite = generated["tools"]["projects.invite_collaborator"]
    assert invite["annotations"] == {
        "readOnlyHint": False,
        "openWorldHint": True,
        "destructiveHint": True,
    }
    assert "external recipient" in invite["justifications"]["open_world_justification"]
    assert (
        "irreversible sent message"
        in invite["justifications"]["destructive_justification"]
    )
    assert "incorporation" in generated["app_info"]["description"].lower()
    assert generated["$schema"] == (
        "https://developers.openai.com/plugins/schemas/chatgpt-app-submission.v1.json"
    )
    assert all(
        case["tools_triggered"] in generated["tools"]
        for case in generated["test_cases"]
    )
    assert generate_submission(["--check"]) == 0
    fixture = json.loads(
        (ROOT / "submission" / "reviewer-fixture.json").read_text(encoding="utf-8")
    )
    assert fixture["status"] in {"local_placeholder", "provisioned"}
    assert isinstance(fixture["project_id"], int)
    assert fixture["project_id"] > 0
    if fixture["status"] == "local_placeholder":
        assert fixture["project_id"] == 42
    assert fixture["incorporation_data"] == "synthetic_only"
    assert fixture["provider_calls_allowed"] is False
    scoped = [
        case
        for case in generated["test_cases"]
        if case["tools_triggered"] != "projects.list"
    ]
    assert len(scoped) == 4
    assert all(
        f"project {fixture['project_id']}" in case["user_prompt"] for case in scoped
    )


@pytest.mark.skipif(
    not BACKEND_AVAILABLE,
    reason="requires the sibling SparkLaunch runtime contract",
)
def test_packaged_synthetic_incorporation_draft_matches_runtime_contract():
    path = (
        ROOT
        / "sparklaunch-incorporation"
        / "references"
        / "synthetic-single-founder-draft.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    parsed = parse_incorporation_draft(payload)
    validation = validate_incorporation_draft(parsed)

    assert parsed.company_name == "Example Launch Labs, Inc."
    assert str(parsed.company_contact_email).endswith("@example.com")
    assert parsed.business_address is None
    assert all(founder.address is None for founder in parsed.founders)
    assert validation.blocking_errors == []
    serialized = json.dumps(payload).lower()
    for forbidden in (
        '"address"',
        '"addresses"',
        '"business_address"',
        '"mailing_address"',
        '"city"',
        '"state_or_region"',
        '"postal_code"',
    ):
        assert forbidden not in serialized


def test_reviewer_project_regeneration_preserves_incorporation_safety_controls(
    tmp_path, monkeypatch
):
    fixture_path = tmp_path / "submission" / "reviewer-fixture.json"
    fixture_path.parent.mkdir()
    monkeypatch.setattr(submission_generator, "ROOT", tmp_path)
    monkeypatch.setattr(submission_generator, "REVIEWER_FIXTURE_PATH", fixture_path)

    assert submission_generator.main(["--reviewer-project-id", "123"]) == 0
    assert json.loads(fixture_path.read_text(encoding="utf-8")) == {
        "status": "provisioned",
        "project_id": 123,
        "incorporation_data": "synthetic_only",
        "provider_calls_allowed": False,
    }


def test_mcp_registry_descriptor_matches_the_public_remote_and_application_version():
    registry = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    version = registry.pop("version")

    assert registry == {
        "$schema": REGISTRY_SCHEMA_URL,
        "name": REGISTRY_SERVER_NAME,
        "title": "SparkLaunch",
        "description": (
            "Founder tools for launch, CRM, incorporation, SparkCap, SparkRoom, and SparkClose."
        ),
        "websiteUrl": "https://sparklaun.ch/",
        "remotes": [{"type": "streamable-http", "url": CANONICAL_MCP_URL}],
    }
    assert "incorporation" in registry["description"].lower()
    assert len(registry["description"]) <= 100
    assert version == "1.7.0"
    if BACKEND_AVAILABLE:
        application_version = run_path(BACKEND / "mcp_server_version.py")[
            "SPARKLAUNCH_MCP_SERVER_VERSION"
        ]
        assert version == application_version


def test_incorporation_tools_and_scopes_match_the_runtime_contract():
    expected = {
        "incorporation.check_entitlement": "incorporation.read",
        "incorporation.start_case": "incorporation.write",
        "incorporation.get_case": "incorporation.read",
        "incorporation.update_draft": "incorporation.write",
        "incorporation.validate": "incorporation.read",
        "incorporation.prepare_action_center": "incorporation.write",
        "incorporation.submit_to_sparklaunch": "incorporation.submit",
        "incorporation.cancel_case": "incorporation.write",
    }

    assert {
        name: contract.required_scope
        for name, contract in MCP_TOOL_CONTRACTS.items()
        if name.startswith("incorporation.")
    } == expected


def test_incorporation_skill_is_private_and_never_calls_filing_providers():
    skill = (ROOT / "sparklaunch-incorporation" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    recipes = [
        (ROOT / "recipes" / name).read_text(encoding="utf-8")
        for name in (
            "incorporate-a-single-founder-company.md",
            "incorporate-with-collaborators.md",
            "recover-incorporation-entitlement.md",
            "resume-or-correct-incorporation.md",
            "check-incorporation-status.md",
        )
    ]

    for marker in (
        "check entitlement first",
        "stable `idempotency_key`",
        "Read the case again",
        "exactly once",
        "private fields out of the conversation",
        "their own Action Center",
        "task-specific",
        "submit to SparkLaunch Filing Operations",
        "Never call Delaware, NWRA, or CorpTools",
        "receipt does not mean",
    ):
        assert marker in skill

    for document in (skill, *recipes):
        assert "submit to SparkLaunch Filing Operations" in document
        assert "Never call Delaware, NWRA, or CorpTools" in document
        assert "receipt does not mean" in document
        assert "private" in document.lower()
        assert "https://corp.delaware.gov" not in document
        assert "nwregisteredagent.com" not in document
        assert "corptools.com" not in document


def test_incorporation_service_access_and_legal_capacity_boundary_is_packaged():
    documents = (
        ROOT / "sparklaunch-incorporation" / "SKILL.md",
        ROOT / "recipes" / "incorporate-a-single-founder-company.md",
        ROOT / "recipes" / "incorporate-with-collaborators.md",
        ROOT / "recipes" / "resume-or-correct-incorporation.md",
        ROOT
        / "plugins"
        / "sparklaunch"
        / "skills"
        / "sparklaunch-incorporation"
        / "SKILL.md",
        ROOT
        / "plugins"
        / "sparklaunch"
        / "skills"
        / "sparklaunch-platform"
        / "recipes"
        / "incorporate-a-single-founder-company.md",
        ROOT
        / "plugins"
        / "sparklaunch"
        / "skills"
        / "sparklaunch-platform"
        / "recipes"
        / "incorporate-with-collaborators.md",
        ROOT
        / "plugins"
        / "sparklaunch"
        / "skills"
        / "sparklaunch-platform"
        / "recipes"
        / "resume-or-correct-incorporation.md",
        ROOT / "submission" / "reviewer-instructions.md",
    )
    markers = (
        "service access begins at age 13",
        "below their local age of majority",
        "parent or legal guardian",
        "Do not ask for age.",
        "do not prove company formation",
        "capacity to sign",
        "payment authorization or completion",
        "identity-verification completion",
        "regulatory eligibility",
        "provider eligibility",
    )

    for path in documents:
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            assert marker in text, f"{path}: missing {marker!r}"

    canonical_skill = documents[0].read_text(encoding="utf-8")
    packaged_skill = documents[4].read_text(encoding="utf-8")
    for skill in (canonical_skill, packaged_skill):
        assert (
            "Read package access and entitlement state without price, purchase links, "
            "checkout actions, or purchasing instructions."
        ) in skill
        assert "Purchasing is unavailable through this connected agent package" in skill
        assert "package eligibility" not in skill.lower()


@pytest.mark.parametrize("payload", ["null", "[]", "[{}]", '"sparklaunch"'])
def test_json_loader_rejects_non_object_documents(tmp_path, monkeypatch, payload):
    monkeypatch.setattr(submission_validator, "ROOT", tmp_path)
    descriptor_path = tmp_path / "server.json"
    descriptor_path.write_text(payload, encoding="utf-8")
    errors = []

    assert _load_json(descriptor_path, errors) is None
    assert errors == ["JSON object required: server.json"]


def test_json_loader_rejects_malformed_documents(tmp_path, monkeypatch):
    monkeypatch.setattr(submission_validator, "ROOT", tmp_path)
    descriptor_path = tmp_path / "server.json"
    descriptor_path.write_text("{", encoding="utf-8")
    errors = []

    assert _load_json(descriptor_path, errors) is None
    assert len(errors) == 1
    assert errors[0].startswith("invalid JSON server.json:")


def test_registry_validator_rejects_an_empty_descriptor(tmp_path):
    errors = []

    _validate_registry_descriptor({}, tmp_path / "missing-version.py", errors)

    assert "MCP Registry descriptor fields are incomplete or unexpected" in errors
    assert "MCP Registry descriptor must use the pinned official schema" in errors
    assert "MCP Registry descriptor has the wrong server namespace" in errors
    assert "MCP Registry descriptor must use a semantic service version" in errors
    assert "MCP Registry descriptor must expose only the canonical remote" in errors


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        (
            "$schema",
            "https://example.com/schema.json",
            "MCP Registry descriptor must use the pinned official schema",
        ),
        (
            "name",
            "com.example/sparklaunch",
            "MCP Registry descriptor has the wrong server namespace",
        ),
        ("title", "Other", "MCP Registry descriptor must use the SparkLaunch title"),
        (
            "description",
            "",
            "MCP Registry description must contain 1 to 100 characters",
        ),
        (
            "description",
            "x" * 101,
            "MCP Registry description must contain 1 to 100 characters",
        ),
        (
            "description",
            123,
            "MCP Registry description must contain 1 to 100 characters",
        ),
        (
            "version",
            "1.0",
            "MCP Registry descriptor must use a semantic service version",
        ),
        (
            "websiteUrl",
            "https://example.com/",
            "MCP Registry descriptor has the wrong website URL",
        ),
        (
            "remotes",
            [],
            "MCP Registry descriptor must expose only the canonical remote",
        ),
    ],
)
def test_registry_validator_rejects_invalid_fields(
    tmp_path,
    field,
    value,
    expected_error,
):
    registry = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    registry[field] = value
    errors = []

    _validate_registry_descriptor(registry, tmp_path / "missing-version.py", errors)

    assert expected_error in errors


@pytest.mark.parametrize("description", ["x", "x" * 100])
def test_registry_validator_accepts_description_boundaries(tmp_path, description):
    registry = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    registry["description"] = description
    errors = []

    _validate_registry_descriptor(registry, tmp_path / "missing-version.py", errors)

    assert errors == []


@pytest.mark.parametrize(
    "version",
    ["0.0.0", "1.0.0-alpha.1", "1.0.0+build.5", "1.0.0-alpha+build"],
)
def test_registry_validator_accepts_semantic_versions(tmp_path, version):
    registry = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    registry["version"] = version
    errors = []

    _validate_registry_descriptor(registry, tmp_path / "missing-version.py", errors)

    assert errors == []


@pytest.mark.parametrize(
    "version",
    ["01.0.0", "1.01.0", "1.0.01", "1.0.0-.", "1.0.0-alpha..1", "1.0.0-01"],
)
def test_registry_validator_rejects_invalid_semantic_versions(tmp_path, version):
    registry = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    registry["version"] = version
    errors = []

    _validate_registry_descriptor(registry, tmp_path / "missing-version.py", errors)

    assert "MCP Registry descriptor must use a semantic service version" in errors


def test_registry_validator_accepts_a_standalone_clone_without_the_application(
    tmp_path,
):
    registry = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    errors = []

    _validate_registry_descriptor(registry, tmp_path / "missing-version.py", errors)

    assert errors == []


@pytest.mark.parametrize(
    ("application_version", "expected_error"),
    [
        (
            'SPARKLAUNCH_MCP_SERVER_VERSION = "2.0.0"',
            "MCP Registry version does not match the SparkLaunch application",
        ),
        (
            "SPARKLAUNCH_MCP_SERVER_VERSION = get_version()",
            "SparkLaunch application MCP version is unreadable",
        ),
    ],
)
def test_registry_validator_rejects_an_invalid_application_version(
    tmp_path,
    application_version,
    expected_error,
):
    registry = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    application_version_path = tmp_path / "mcp_server_version.py"
    application_version_path.write_text(application_version, encoding="utf-8")
    errors = []

    _validate_registry_descriptor(registry, application_version_path, errors)

    assert expected_error in errors


def test_registry_validator_rejects_an_invalid_utf8_application_version(tmp_path):
    registry = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    application_version_path = tmp_path / "mcp_server_version.py"
    application_version_path.write_bytes(b"\xff\xfe")
    errors = []

    _validate_registry_descriptor(registry, application_version_path, errors)

    assert len(errors) == 1
    assert errors[0].startswith("SparkLaunch application MCP version is unreadable:")


def test_readme_documents_cross_repository_validation_and_cache_versioning():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert (
        "Clone the application and skills repositories as sibling directories" in readme
    )
    assert "../SparkLaunch/backend" in readme
    assert "standalone `SparkLaunch-Skills` clone" in readme
    assert "cached by plugin version" in readme


def test_skill_trigger_evaluation_set_covers_every_skill_and_negative_boundaries():
    evaluations = json.loads(
        (ROOT / "evals" / "skill-trigger-cases.json").read_text(encoding="utf-8")
    )
    cases = evaluations["cases"]
    assert len(cases) == 39
    expected_skills = {skill for case in cases for skill in case["expected_skills"]}
    assert expected_skills == {
        "sparklaunch-campaigns",
        "sparklaunch-color-palettes",
        "sparklaunch-idea-validation",
        "sparklaunch-landing-pages",
        "sparklaunch-logo-generation",
        "sparklaunch-platform",
        "sparklaunch-projects",
        "sparklaunch-sales-crm",
        "sparklaunch-incorporation",
        "sparklaunch-sparkcap",
        "sparklaunch-sparkroom",
        "sparklaunch-sparkclose",
    }
    assert sum(not case["expected_skills"] for case in cases) == 11
    assert next(
        case for case in cases if case["id"] == "negative-generic-safe-advice"
    )["expected_skills"] == []
    incorporation_cases = {
        case["id"]: case["expected_skills"]
        for case in cases
        if case["id"].startswith("incorporation-")
    }
    assert incorporation_cases == {
        "incorporation-general": ["sparklaunch-incorporation"],
        "incorporation-missing-plan": ["sparklaunch-incorporation"],
        "incorporation-collaborators": ["sparklaunch-incorporation"],
        "incorporation-resume-status": ["sparklaunch-incorporation"],
        "incorporation-correction-conflict": ["sparklaunch-incorporation"],
        "incorporation-negative-stays-projects": ["sparklaunch-projects"],
    }


def test_controlled_e2e_matrix_covers_every_tool_and_recipe():
    matrix = json.loads(
        (ROOT / "evals" / "controlled-e2e-matrix.json").read_text(encoding="utf-8")
    )
    submission = json.loads(
        (ROOT / "chatgpt-app-submission.json").read_text(encoding="utf-8")
    )
    covered_tools = {tool for case in matrix["cases"] for tool in case["tools"]}
    covered_recipes = {recipe for case in matrix["cases"] for recipe in case["recipes"]}

    assert len(matrix["cases"]) == 16
    assert covered_tools == set(submission["tools"])
    assert covered_recipes == {
        "model-and-close-a-safe.md",
        "prepare-and-share-an-investor-room.md",
        "review-cap-table-and-model-a-raise.md",
        "connect-sparklaunch-to-chatgpt.md",
        "validate-an-idea-and-generate-a-report.md",
        "create-a-brand-foundation.md",
        "plan-and-publish-a-launch.md",
        "review-launch-signals-and-follow-up.md",
        "start-a-business-from-an-idea.md",
        "incorporate-a-single-founder-company.md",
        "incorporate-with-collaborators.md",
        "recover-incorporation-entitlement.md",
        "resume-or-correct-incorporation.md",
        "check-incorporation-status.md",
    }
    incorporation_cases = {
        case["id"]: case
        for case in matrix["cases"]
        if case["id"].startswith("E2E-INCORPORATION-")
    }
    assert set(incorporation_cases) == {
        "E2E-INCORPORATION-MISSING-ENTITLEMENT",
        "E2E-INCORPORATION-SINGLE-FOUNDER",
        "E2E-INCORPORATION-MULTI-PARTICIPANT",
        "E2E-INCORPORATION-CORRECTION-RESUME",
        "E2E-INCORPORATION-INTERNAL-SUBMISSION",
    }
    assert all(
        "real provider" not in case["live_level"]
        for case in incorporation_cases.values()
    )
    controls = matrix["controls"]
    assert controls["automatic_validation_typical_minutes"] == "10-15"
    assert controls["automatic_validation_poll_seconds"] >= 60
    assert controls["automatic_validation_timeout_minutes"] >= 20
    expected_scopes = {
        contract.required_scope for contract in MCP_TOOL_CONTRACTS.values()
    }
    assert len(expected_scopes) == 29
    assert controls["expected_oauth_scope_count"] == len(expected_scopes)
    expected_grant_marker = f"expected {len(expected_scopes)}-scope grant"
    assert any(expected_grant_marker in case["expected"] for case in matrix["cases"])
    assert "15-scope" not in json.dumps(matrix)
    assert controls["preflight_effective_permissions"] is True
    assert controls["open_and_cancel_disconnect_dialog"] is True
    assert controls["never_auto_confirm"] is True
    assert controls["never_perform_real_outreach"] is True
    assert controls["never_retry_uncertain_write_with_new_key"] is True
    assert controls["never_call_delaware_nwra_or_corptools"] is True
    assert controls["incorporation_submission_is_internal_only"] is True


def test_controlled_e2e_runbook_preserves_the_incorporation_provider_barrier():
    runbook = (ROOT / "evals" / "CONTROLLED-E2E.md").read_text(encoding="utf-8")

    for marker in (
        "29 OAuth scopes",
        "Never call Delaware, NWRA, or CorpTools",
        "zero provider calls",
        "submit to SparkLaunch Filing Operations",
        "receipt does not mean",
        "each person to their own Action Center",
    ):
        assert marker in runbook


def test_project_and_validation_guidance_uses_automatic_initial_research():
    project_skill = (ROOT / "sparklaunch-projects" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    validation_skill = (ROOT / "sparklaunch-idea-validation" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    validation_recipe = (
        ROOT / "recipes" / "validate-an-idea-and-generate-a-report.md"
    ).read_text(encoding="utf-8")

    for document in (project_skill, validation_skill, validation_recipe):
        assert "automatically" in document
        assert "10-15 minutes" in document
        assert "duplicate" in document
    assert (
        "do not call `validation.create_project` or `validation.start_analysis`"
        in validation_recipe
    )


def test_landing_recipe_forbids_invented_social_proof():
    launch_recipe = (ROOT / "recipes" / "plan-and-publish-a-launch.md").read_text(
        encoding="utf-8"
    )

    assert "invented testimonials" in launch_recipe
    assert "verified evidence" in launch_recipe


def test_project_guidance_preflights_effective_permissions_before_writes():
    project_skill = (ROOT / "sparklaunch-projects" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    connect_recipe = (ROOT / "recipes" / "connect-sparklaunch-to-chatgpt.md").read_text(
        encoding="utf-8"
    )
    launch_recipe = (ROOT / "recipes" / "plan-and-publish-a-launch.md").read_text(
        encoding="utf-8"
    )

    for document in (project_skill, connect_recipe, launch_recipe):
        assert "effective_permissions" in document
    assert "do not propose or confirm a write" in connect_recipe


def test_logo_guidance_documents_the_selected_colors_transport_shape():
    logo_skill = (ROOT / "sparklaunch-logo-generation" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    brand_recipe = (ROOT / "recipes" / "create-a-brand-foundation.md").read_text(
        encoding="utf-8"
    )

    for document in (logo_skill, brand_recipe):
        assert "`selected_colors`" in document
        assert '`{"hex":"#6E4E3A","feeling":"grounded"}`' in document
        assert "never pass an array" in document.lower()
        assert "`neutral_light` to `background`" in document
        assert "`neutral_dark` to `foreground`" in document


def test_connection_recipe_classifies_bare_oauth_403_without_reusing_the_url():
    recipe = (ROOT / "recipes" / "connect-sparklaunch-to-chatgpt.md").read_text(
        encoding="utf-8"
    )

    assert "only `403 Forbidden`" in recipe
    assert "start a fresh connection" in recipe
    assert "not proof that the account is connected, expired, or revoked" in recipe


def test_founder_report_template_only_requests_supported_tool_evidence():
    template = (
        ROOT / "recipes" / "templates" / "founder-workflow-report.md"
    ).read_text(encoding="utf-8")

    for unsupported in (
        "Recommended business name",
        "MCP key created",
        "Naming And Domain",
        "Favorite status",
        "Founder report PDF",
        "Asset zip",
    ):
        assert unsupported not in template
    for supported in (
        "Effective permissions",
        "Project name",
        "Palette name",
        "Short-lived download reference",
        "Confirmation-gated actions",
    ):
        assert supported in template
    for internal_label in (
        "Project id:",
        "Validation project id:",
        "Selected palette id:",
        "Logo id:",
        "Campaign id",
        "QR id",
        "Landing project id:",
    ):
        assert internal_label not in template


def test_reviewer_documents_are_credential_free_and_candidate_bounded():
    release_notes = (ROOT / "submission" / "release-notes.md").read_text(
        encoding="utf-8"
    )
    reviewer = (ROOT / "submission" / "reviewer-instructions.md").read_text(
        encoding="utf-8"
    )
    manifest = json.loads(
        (ROOT / "plugins" / "sparklaunch" / ".codex-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    fixture = json.loads(
        (ROOT / "submission" / "reviewer-fixture.json").read_text(encoding="utf-8")
    )
    assert manifest["version"].startswith("0.8.0+codex.20260906")
    assert manifest["version"] != "0.2.1+codex.20260817230400"
    assert manifest["version"] in release_notes
    assert manifest["version"] in reviewer
    assert "production MCP service is deployed" in release_notes
    assert "has not yet been submitted or approved by ChatGPT" in release_notes
    assert f"project `{fixture['project_id']}`" in reviewer
    assert "supplied through the approved private reviewer channel" in reviewer
    assert "must never be added to this file" in reviewer
    assert "support@sparklaun.ch" in reviewer
    assert "plugins/sparklaunch/assets/sparklaunch.png" in reviewer
    assert "sparklaunch-wordmark-light.png" in reviewer
    assert "sparklaunch-wordmark-dark.png" in reviewer
    for marker in (
        "twelve",
        f"{len(MCP_TOOL_CONTRACTS)} tools",
        "29 OAuth scopes",
        "submit to SparkLaunch Filing Operations",
        "receipt does not mean",
        "zero provider calls",
        "private Action Center",
    ):
        assert marker in release_notes
        assert marker in reviewer


@pytest.mark.parametrize(
    ("relative_path", "injected", "category"),
    (
        (
            "submission/release-notes.md",
            "Authorization: Bearer synthetic-review-secret",
            "authorization header",
        ),
        (
            "submission/reviewer-instructions.md",
            "client_secret=synthetic-review-secret",
            "secret assignment",
        ),
        (
            "submission/demo-recording-runbook.md",
            "-----BEGIN PRIVATE KEY-----",
            "private key",
        ),
        (
            "submission/demo-recording-runbook.md",
            "eyJabcdefgh.abcdefgh.abcdefgh",
            "JWT",
        ),
        (
            "submission/demo-recording-runbook.md",
            "https://downloads.example.com/demo?X-Amz-Signature=synthetic",
            "credential-bearing URL",
        ),
    ),
)
def test_reviewer_markdown_rejects_injected_sensitive_material(
    monkeypatch,
    relative_path,
    injected,
    category,
):
    path = ROOT / relative_path
    marker = path.read_text(encoding="utf-8").splitlines()[0]

    errors = _validate_with_bytes_replaced(
        monkeypatch,
        path,
        marker,
        f"{marker}\n{injected}",
    )

    assert (
        f"reviewer-facing Markdown contains {category}: "
        f"{path.relative_to(ROOT)}"
    ) in errors


@pytest.mark.parametrize(
    "url",
    (
        "https://downloads.example.com/demo#access_token=synthetic",
        (
            "https://downloads.example.com/redirect?target="
            "https%3A%2F%2Fvideo.example.com%2Fdemo%23session_id%3Dsynthetic"
        ),
    ),
)
def test_reviewer_markdown_url_scan_follows_fragments_and_nested_urls(url):
    assert "credential-bearing URL" in (
        portal_prerequisite_validator.sensitive_text_findings(url)
    )


def test_reviewer_markdown_url_scan_allows_benign_key_substrings():
    url = "https://downloads.example.com/demo?design=minimal&codec=av1&monkey=capuchin"

    assert portal_prerequisite_validator.sensitive_text_findings(url) == []
    assert portal_prerequisite_validator._is_https_url(url) is True


def test_portal_prerequisites_are_credential_free_and_pending_gates_fail_closed():
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    runbook = (ROOT / "submission" / "demo-recording-runbook.md").read_text(
        encoding="utf-8"
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )

    assert evidence["schema_version"] == 3
    assert evidence["candidate"]["plugin_version"] == ("0.8.0+codex.20260906000000")
    assert evidence["candidate"]["service_version"] == "1.7.0"
    assert evidence["candidate"]["expected_tool_count"] == 100
    assert len(MCP_TOOL_CONTRACTS) == 100
    assert evidence["candidate"]["expected_oauth_scope_count"] == 29
    deployed_revision = "058513ed28b2fadba120d5f4a0e447a723e37ddc"
    historical_revision = "867ac0360949a81966d194ab2aaaa774e377d597"
    assert evidence["public_production_readiness"]["status"] == "pending"
    assert evidence["production_deployment"]["status"] == "pending"
    assert evidence["direct_authenticated_production_scan"]["status"] == "pending"
    current_public = evidence["historical_public_production_readiness"][-1]["evidence"]
    assert "domain_challenge" not in current_public
    assert current_public["domain_challenge_http_status"] == 200
    assert current_public["domain_challenge_response_byte_count"] == 43
    assert current_public["domain_challenge_cache_control_no_store"] is True
    assert evidence["authenticated_production_scan"]["status"] == "pending"
    assert (
        evidence["authenticated_production_scan"]["candidate_expected_tool_count"] == 100
    )
    assert evidence["authenticated_production_scan"]["portal_result"] == "pending"
    deployment = evidence["historical_production_deployments"][-1]
    assert deployment["git_revision"] == deployed_revision
    assert deployment["service_version"] == "1.4.0"
    assert deployment["migration_revision"] == ("mcp_portability_01")
    assert deployment["alembic_current_matches_head_on_all_backend_instances"] is True
    assert {
        deployment["git_revision"]
        for deployment in evidence["historical_production_deployments"]
    } == {historical_revision, deployed_revision}
    historical_scan = evidence["historical_authenticated_production_scans"][0]
    assert historical_scan["historical_result_status"] == "verified"
    assert historical_scan["tool_count"] == 59
    assert historical_scan["candidate_contract_status"] == "stale"
    assert (
        historical_scan["latest_runtime_probe"]["deployed_git_revision"]
        == historical_revision
    )
    assert (
        portal_prerequisite_validator._canonical_sha256(
            evidence["historical_candidates"][0]
        )
        == portal_prerequisite_validator.HISTORICAL_CANDIDATE_SHA256S[0]
    )
    assert (
        portal_prerequisite_validator._canonical_sha256(
            evidence["historical_public_production_readiness"][0]
        )
        == portal_prerequisite_validator.HISTORICAL_PUBLIC_READINESS_SHA256S[0]
    )
    assert (
        portal_prerequisite_validator._canonical_sha256(
            evidence["historical_public_production_readiness"][1]
        )
        == portal_prerequisite_validator.HISTORICAL_PUBLIC_READINESS_SHA256S[1]
    )
    assert (
        portal_prerequisite_validator._canonical_sha256(
            evidence["historical_production_deployments"][0]
        )
        == portal_prerequisite_validator.HISTORICAL_PRODUCTION_DEPLOYMENT_SHA256S[0]
    )
    assert (
        portal_prerequisite_validator._canonical_sha256(
            evidence["historical_production_deployments"][1]
        )
        == portal_prerequisite_validator.HISTORICAL_PRODUCTION_DEPLOYMENT_SHA256S[1]
    )
    assert (
        portal_prerequisite_validator._canonical_sha256(
            evidence["historical_direct_authenticated_production_scans"][0]
        )
        == portal_prerequisite_validator.HISTORICAL_DIRECT_SCAN_SHA256S[0]
    )
    assert (
        portal_prerequisite_validator._canonical_sha256(historical_scan)
        == portal_prerequisite_validator.HISTORICAL_PORTAL_SCAN_SHA256S[0]
    )
    historical_pending_scan = evidence["historical_authenticated_production_scans"][1]
    assert historical_pending_scan == {
        "status": "pending",
        "candidate_expected_tool_count": 61,
        "portal_result": "pending",
        "proof_boundary": (
            "A fresh OpenAI portal OAuth Scan Tools pass against the deployed 61-tool "
            "candidate remains pending. The separate direct authenticated production "
            "scan does not replace this portal gate, and the prior 59-tool portal "
            "observation is preserved under historical_authenticated_production_scans."
        ),
    }
    assert (
        portal_prerequisite_validator._canonical_sha256(historical_pending_scan)
        == portal_prerequisite_validator.HISTORICAL_PORTAL_SCAN_SHA256S[1]
    )
    assert deployment["backend_refresh_successful"] is True
    assert deployment["frontend_refresh_successful"] is True
    assert deployment["launch_template_pins_match_refreshes"] is True
    assert (
        deployment["frontend_revision_proven_by_immutable_launch_template_pin"] is True
    )
    assert deployment["all_observed_deployment_targets_match_revision"] is True
    assert deployment["required_runtime_configuration_verified"] is True
    direct_scan = evidence["historical_direct_authenticated_production_scans"][0]
    assert direct_scan["status"] == "verified"
    assert direct_scan["deployed_git_revision"] == deployed_revision
    assert direct_scan["mcp_protocol_version"] == "2025-11-25"
    assert direct_scan["server_name"] == "SparkLaunch MCP"
    assert direct_scan["server_version"] == "1.4.0"
    assert direct_scan["initialize_http_status"] == 200
    assert direct_scan["initialized_notification_http_status"] == 202
    assert direct_scan["tools_list_http_status"] == 200
    assert direct_scan["tool_count"] == 61
    assert direct_scan["tool_names"] == sorted(
        name
        for name in MCP_TOOL_CONTRACTS
        if not name.startswith(("cap_table.", "sparkroom.", "sparkclose."))
    )
    assert direct_scan["exact_candidate_tool_name_set_match"] is True
    assert direct_scan["output_schema_root_failure_count"] == 0
    assert direct_scan["annotation_triplet_failure_count"] == 0
    assert direct_scan["tool_calls_executed"] == 0
    assert direct_scan["sensitive_values_retained"] is False
    release_scan = release_state["runtime"]["last_verified_production"][
        "direct_authenticated_scan"
    ]
    assert "exact_contract_match" not in release_scan
    assert release_scan["exact_tool_name_set_match"] is True
    assert release_scan["output_schema_root_failure_count"] == 0
    assert release_scan["annotation_triplet_failure_count"] == 0
    assert release_scan["initialize_http_status"] == 200
    assert release_scan["initialized_notification_http_status"] == 202
    assert release_scan["tools_list_http_status"] == 200
    assert release_scan["mcp_protocol_version"] == "2025-11-25"
    assert release_scan["server_name"] == "SparkLaunch MCP"
    assert release_scan["server_version"] == "1.4.0"
    assert evidence["reviewer_access"]["status"] == "verified"
    assert evidence["reviewer_access"]["project_isolation_verified"] is True
    assert evidence["reviewer_access"]["reviewer_materials_configured"] is True
    assert (
        evidence["reviewer_access"]["reviewer_materials_stored_outside_repository"]
        is True
    )
    assert evidence["publisher_identity"]["status"] == "verified"
    assert evidence["publisher_identity"]["organization_and_project_match"] is True
    assert evidence["demo_recording"]["status"] == "pending"
    assert "hosted ChatGPT first and Codex second" in runbook
    assert release_state["runtime"]["candidate"]["deployment_status"] == (
        "not_verified_for_candidate"
    )
    assert portal_prerequisite_validator.validate(allow_pending=True) == []
    strict_errors = portal_prerequisite_validator.validate(allow_pending=False)
    assert {
        "external portal gate is still pending: public_production_readiness",
        "external portal gate is still pending: production_deployment",
        "external portal gate is still pending: direct_authenticated_production_scan",
        "external portal gate is still pending: authenticated_production_scan",
        "external portal gate is still pending: demo_recording",
    }.issubset(strict_errors)


@pytest.mark.parametrize(
    ("path", "replacement", "expected_error"),
    (
        (
            ("candidate", "plugin_version"),
            "0.6.0",
            "portal prerequisite plugin version does not match the plugin manifest",
        ),
        (
            ("candidate", "service_version"),
            "1.5.0",
            "portal prerequisite service version must match the contract snapshot",
        ),
        (
            ("candidate", "expected_tool_count"),
            85,
            "portal prerequisite evidence tool count must match the contract snapshot",
        ),
        (
            ("candidate", "expected_oauth_scope_count"),
            24,
            "portal prerequisite evidence OAuth scope count must match the contract snapshot",
        ),
        (
            ("candidate", "bundle_sha256"),
            "0" * 64,
            "portal prerequisite candidate bundle digest does not match",
        ),
    ),
)
def test_portal_prerequisite_validator_rejects_candidate_identity_drift(
    monkeypatch,
    tmp_path,
    path,
    replacement,
    expected_error,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    _replace_nested_value(evidence, path, replacement)

    assert expected_error in _validate_portal_evidence(monkeypatch, tmp_path, evidence)


@pytest.mark.parametrize(
    ("path", "replacement", "expected_error"),
    (
        (
            ("historical_candidates", 0, "expected_tool_count"),
            60,
            "historical candidate snapshot changed",
        ),
        (
            (
                "historical_public_production_readiness",
                0,
                "evidence",
                "oauth_scope_count",
            ),
            17,
            "historical public-readiness snapshot changed",
        ),
        (
            (
                "historical_production_deployments",
                1,
                "required_runtime_configuration_verified",
            ),
            False,
            "historical production deployment snapshot changed",
        ),
        (
            (
                "historical_direct_authenticated_production_scans",
                0,
                "tool_count",
            ),
            60,
            "historical direct authenticated production scan snapshot changed",
        ),
        (
            (
                "historical_authenticated_production_scans",
                0,
                "latest_portal_refresh",
                "annotation_justification_field_count",
            ),
            176,
            "historical authenticated portal scan snapshot changed",
        ),
    ),
)
def test_portal_prerequisite_validator_rejects_historical_evidence_changes(
    monkeypatch,
    tmp_path,
    path,
    replacement,
    expected_error,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    _replace_nested_value(evidence, path, replacement)
    assert expected_error in _validate_portal_evidence(monkeypatch, tmp_path, evidence)


@pytest.mark.parametrize(
    ("path", "replacement", "expected_error"),
    (
        (
            ("public_production_readiness", "candidate_expected_oauth_scope_count"),
            24,
            "public production readiness has inconsistent candidate_expected_oauth_scope_count",
        ),
        (
            ("production_deployment", "candidate_plugin_version"),
            "0.6.0",
            "production deployment has inconsistent candidate_plugin_version",
        ),
        (
            ("direct_authenticated_production_scan", "candidate_service_version"),
            "1.5.0",
            "direct authenticated production scan has inconsistent candidate_service_version",
        ),
        (
            ("production_deployment", "status"),
            "pending",
            "production deployment is pending but contains verified field observed_at",
        ),
        (
            ("production_deployment", "observed_at"),
            "",
            "production deployment is verified but has no observation time",
        ),
        (
            ("production_deployment", "git_revision"),
            "not-a-sha",
            "production deployment revision must be a full Git SHA",
        ),
        (
            ("production_deployment", "production_tag"),
            "",
            "production deployment tag is missing",
        ),
        (
            ("production_deployment", "branch_matches_origin"),
            False,
            "verified production deployment must match origin",
        ),
        (
            ("production_deployment", "service_version"),
            "1.3.0",
            "production service version must match the contract snapshot",
        ),
        (
            ("production_deployment", "migration_status"),
            "pending",
            "production deployment must record the applied migration revision",
        ),
        (
            (
                "production_deployment",
                "alembic_current_matches_head_on_all_backend_instances",
            ),
            False,
            "production Alembic current/head parity must be verified",
        ),
        (
            ("production_deployment", "public_backend_http_status"),
            503,
            "production backend health must return HTTP 200",
        ),
        (
            ("production_deployment", "public_frontend_http_status"),
            503,
            "production frontend must return HTTP 200",
        ),
        (
            (
                "production_deployment",
                "all_observed_deployment_targets_match_revision",
            ),
            False,
            "production deployment targets must match the recorded revision",
        ),
        (
            ("production_deployment", "backend_refresh_successful"),
            False,
            "production backend refresh must be successful",
        ),
        (
            ("production_deployment", "frontend_refresh_successful"),
            False,
            "production frontend refresh must be successful",
        ),
        (
            ("production_deployment", "launch_template_pins_match_refreshes"),
            False,
            "production launch-template pins must match refreshes",
        ),
        (
            (
                "production_deployment",
                "frontend_revision_proven_by_immutable_launch_template_pin",
            ),
            False,
            "production frontend revision must use an immutable launch-template pin",
        ),
        (
            ("production_deployment", "required_runtime_configuration_verified"),
            False,
            "production deployment runtime configuration must be verified",
        ),
        (
            ("direct_authenticated_production_scan", "status"),
            "pending",
            "direct authenticated production scan is pending but contains verified field observed_at",
        ),
        (
            ("direct_authenticated_production_scan", "observed_at"),
            "",
            "direct authenticated production scan is verified but has no observation time",
        ),
        (
            ("direct_authenticated_production_scan", "deployed_git_revision"),
            "0" * 40,
            "direct authenticated scan revision must match production",
        ),
        (
            ("direct_authenticated_production_scan", "initialize_http_status"),
            201,
            "direct authenticated scan has invalid initialize_http_status",
        ),
        (
            ("direct_authenticated_production_scan", "mcp_protocol_version"),
            "2025-03-26",
            "direct authenticated scan protocol version is stale",
        ),
        (
            ("direct_authenticated_production_scan", "server_name"),
            "Other MCP",
            "direct authenticated scan server name is stale",
        ),
        (
            ("direct_authenticated_production_scan", "server_version"),
            "1.3.0",
            "direct authenticated scan server version is stale",
        ),
        (
            (
                "direct_authenticated_production_scan",
                "initialized_notification_http_status",
            ),
            200,
            "direct authenticated scan has invalid initialized_notification_http_status",
        ),
        (
            ("direct_authenticated_production_scan", "tools_list_http_status"),
            503,
            "direct authenticated scan has invalid tools_list_http_status",
        ),
        (
            ("direct_authenticated_production_scan", "tool_count"),
            60,
            "direct authenticated scan tool count must match the candidate",
        ),
        (
            ("direct_authenticated_production_scan", "tool_names"),
            [],
            "direct authenticated scan tool names must match the snapshot",
        ),
        (
            (
                "direct_authenticated_production_scan",
                "exact_candidate_tool_name_set_match",
            ),
            False,
            "direct authenticated scan must match the candidate tool-name set",
        ),
        (
            ("direct_authenticated_production_scan", "missing_tool_count"),
            1,
            "direct authenticated scan has nonzero missing_tool_count",
        ),
        (
            ("direct_authenticated_production_scan", "extra_tool_count"),
            1,
            "direct authenticated scan has nonzero extra_tool_count",
        ),
        (
            ("direct_authenticated_production_scan", "duplicate_tool_count"),
            1,
            "direct authenticated scan has nonzero duplicate_tool_count",
        ),
        (
            (
                "direct_authenticated_production_scan",
                "output_schema_root_failure_count",
            ),
            1,
            "direct authenticated scan has nonzero output_schema_root_failure_count",
        ),
        (
            (
                "direct_authenticated_production_scan",
                "annotation_triplet_failure_count",
            ),
            1,
            "direct authenticated scan has nonzero annotation_triplet_failure_count",
        ),
        (
            ("direct_authenticated_production_scan", "tool_calls_executed"),
            1,
            "direct authenticated scan has nonzero tool_calls_executed",
        ),
        (
            ("direct_authenticated_production_scan", "sensitive_values_retained"),
            True,
            "direct authenticated scan must not retain sensitive values",
        ),
        (
            (
                "direct_authenticated_production_scan",
                "dynamic_client_registration_advertised",
            ),
            False,
            "direct authenticated scan must retain DCR advertisement evidence",
        ),
        (
            (
                "direct_authenticated_production_scan",
                "client_id_metadata_document_advertised",
            ),
            True,
            "direct authenticated scan must record CIMD as not advertised",
        ),
        (
            ("direct_authenticated_production_scan", "business_card_tools"),
            [],
            "direct authenticated scan business-card inventory is incomplete",
        ),
        (
            (
                "public_production_readiness",
                "evidence",
                "authorization_server_metadata_http_status",
            ),
            503,
            "public production readiness has invalid authorization_server_metadata_http_status",
        ),
        (
            ("public_production_readiness", "evidence", "domain_challenge"),
            "verified_by_openai_portal",
            "current public readiness must not reuse historical portal verification",
        ),
    ),
)
def test_portal_prerequisite_validator_rejects_incomplete_current_proof(
    monkeypatch,
    tmp_path,
    path,
    replacement,
    expected_error,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    evidence, release_state = _promote_candidate_evidence(evidence, release_state)
    _replace_nested_value(evidence, path, replacement)
    assert expected_error in _validate_portal_evidence(
        monkeypatch, tmp_path, evidence, release_state
    )


def test_portal_prerequisite_validator_accepts_fully_verified_candidate(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    evidence, release_state = _promote_candidate_evidence(evidence, release_state)

    assert (
        _validate_portal_evidence(
            monkeypatch,
            tmp_path,
            evidence,
            release_state,
            allow_pending=False,
        )
        == []
    )


@pytest.mark.parametrize(
    ("field", "observed_at", "expected_error"),
    (
        (
            "public_production_readiness",
            "2026-09-03T04:41:12Z",
            "public production readiness observation must be newer than its historical baseline",
        ),
        (
            "production_deployment",
            "2026-09-03T04:47:05Z",
            "production deployment observation must be newer than its historical baseline",
        ),
        (
            "direct_authenticated_production_scan",
            "2026-09-03T04:43:24Z",
            "direct authenticated production scan observation must be newer than its historical baseline",
        ),
        (
            "authenticated_production_scan",
            "2026-09-01T18:53:55Z",
            "authenticated production scan observation must be newer than its historical baseline",
        ),
    ),
)
def test_portal_prerequisite_validator_rejects_reused_historical_observations(
    monkeypatch,
    tmp_path,
    field,
    observed_at,
    expected_error,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    evidence, release_state = _promote_candidate_evidence(evidence, release_state)
    evidence[field]["observed_at"] = observed_at

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
        allow_pending=False,
    )

    assert expected_error in errors


def test_portal_prerequisite_validator_rejects_invalid_or_prebuild_observations(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    evidence, release_state = _promote_candidate_evidence(evidence, release_state)
    evidence["public_production_readiness"]["observed_at"] = "not-a-time"
    evidence["production_deployment"]["observed_at"] = "2026-09-03T23:59:59Z"
    evidence["demo_recording"]["observed_at"] = "2026-09-03T23:59:59Z"

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
        allow_pending=False,
    )

    assert "public production readiness has an invalid UTC observation time" in errors
    assert "production deployment observation predates the candidate build" in errors
    assert "demo recording observation predates the candidate build" in errors


def test_portal_prerequisite_validator_requires_exact_candidate_bundle_path(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    manifest = ROOT / "plugins" / "sparklaunch" / ".codex-plugin" / "plugin.json"
    evidence["candidate"]["bundle_path"] = manifest.relative_to(ROOT).as_posix()
    evidence["candidate"]["bundle_sha256"] = hashlib.sha256(
        manifest.read_bytes()
    ).hexdigest()

    errors = _validate_portal_evidence(monkeypatch, tmp_path, evidence)

    assert "portal prerequisite candidate bundle path is invalid" in errors


def test_portal_prerequisite_validator_requires_exact_demo_runbook(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    evidence["demo_recording"]["runbook"] = "README.md"

    errors = _validate_portal_evidence(monkeypatch, tmp_path, evidence)

    assert "demo recording runbook is missing" in errors


@pytest.mark.parametrize(
    ("old", "new", "expected_error"),
    (
        (
            "exactly 100 tools",
            "exactly 61 tools",
            "demo recording runbook has stale tool count",
        ),
        (
            "service `1.7.0`",
            "service `1.4.0`",
            "demo recording runbook has stale service version",
        ),
        (
            "29 OAuth scopes",
            "18 OAuth scopes",
            "demo recording runbook has stale OAuth scope count",
        ),
        (
            "**Review SparkCap.**",
            "**Review old cap table.**",
            "demo recording runbook has stale SparkCap walkthrough",
        ),
        (
            "**Review SparkRoom.**",
            "**Review old room.**",
            "demo recording runbook has stale SparkRoom walkthrough",
        ),
        (
            "**Review SparkClose.**",
            "**Review old SAFE workflow.**",
            "demo recording runbook has stale SparkClose walkthrough",
        ),
    ),
)
def test_portal_prerequisite_validator_rejects_stale_demo_runbook(
    monkeypatch,
    old,
    new,
    expected_error,
):
    original_read_text = Path.read_text
    runbook_path = (
        ROOT / portal_prerequisite_validator.EXPECTED_DEMO_RUNBOOK
    ).resolve()

    def read_text(path, *args, **kwargs):
        text = original_read_text(path, *args, **kwargs)
        if path.resolve() == runbook_path:
            assert old in text
            return text.replace(old, new, 1)
        return text

    monkeypatch.setattr(Path, "read_text", read_text)

    errors = portal_prerequisite_validator.validate(allow_pending=True)

    assert expected_error in errors


def test_portal_prerequisite_validator_rejects_new_sensitive_history_fields(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    evidence["historical_authenticated_production_scans"][0]["client_secret"] = (
        "not-a-real-secret"
    )

    errors = _validate_portal_evidence(monkeypatch, tmp_path, evidence)

    assert any("sensitive field" in error for error in errors)
    assert all("not-a-real-secret" not in error for error in errors)


def test_portal_prerequisite_validator_rejects_extra_historical_records(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    evidence["historical_production_deployments"].append({})

    errors = _validate_portal_evidence(monkeypatch, tmp_path, evidence)

    assert (
        "historical production deployment snapshot must contain exactly 2 immutable records"
        in errors
    )


@pytest.mark.parametrize(
    ("path", "replacement", "expected_error"),
    (
        (
            ("runtime", "last_verified_production", "deployed_git_revision"),
            "0" * 40,
            "release-state production baseline has inconsistent deployed_git_revision",
        ),
        (
            (
                "runtime",
                "last_verified_production",
                "direct_authenticated_scan",
                "tool_count",
            ),
            60,
            "release-state baseline direct scan has inconsistent tool_count",
        ),
        (
            (
                "runtime",
                "last_verified_production",
                "oauth",
                "dynamic_client_registration_advertised",
            ),
            False,
            "release-state baseline OAuth has inconsistent dynamic_client_registration_advertised",
        ),
    ),
)
def test_portal_prerequisite_validator_cross_checks_release_state(
    monkeypatch,
    tmp_path,
    path,
    replacement,
    expected_error,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    _replace_nested_value(release_state, path, replacement)

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
    )

    assert expected_error in errors


@pytest.mark.parametrize(
    ("path", "replacement", "expected_error"),
    (
        (
            ("generated_packages", "status"),
            "published",
            "release-state generated packages has inconsistent status",
        ),
        (
            ("generated_packages", "hosts"),
            ["openai"],
            "release-state generated packages has inconsistent hosts",
        ),
        (
            ("mcp_registry", "publication_status"),
            "published",
            "release-state Registry has inconsistent publication_status",
        ),
        (
            ("mcp_registry", "live_refresh_status"),
            "verified",
            "release-state Registry has inconsistent live_refresh_status",
        ),
        (
            ("distribution", "openai"),
            "publicly_published",
            "release-state distribution has inconsistent openai",
        ),
    ),
)
def test_portal_prerequisite_validator_rejects_false_release_claims(
    monkeypatch,
    tmp_path,
    path,
    replacement,
    expected_error,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    _replace_nested_value(release_state, path, replacement)

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
    )

    assert expected_error in errors


def test_portal_prerequisite_validator_rejects_extra_release_state_fields(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    release_state["generated_packages"]["publication_url"] = (
        "https://demo.sparklaun.ch/release"
    )

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
    )

    assert (
        "release state has unexpected field at "
        "$release_state.generated_packages.publication_url" in errors
    )


def test_release_state_production_baseline_switches_atomically(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    promoted_evidence = json.loads(json.dumps(evidence))
    promoted_release_state = json.loads(json.dumps(release_state))
    promoted_evidence, _ = _promote_candidate_evidence(
        promoted_evidence,
        promoted_release_state,
    )
    evidence["production_deployment"] = promoted_evidence["production_deployment"]
    release_state["runtime"]["candidate"]["deployment_status"] = "verified"

    assert (
        _validate_portal_evidence(
            monkeypatch,
            tmp_path,
            evidence,
            release_state,
        )
        == []
    )

    release_state["runtime"]["last_verified_production"]["service_version"] = "1.7.0"
    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
    )
    assert (
        "release-state production baseline has inconsistent service_version" in errors
    )


def test_public_readiness_alone_cannot_verify_a_new_undeployed_candidate(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    promoted_evidence = json.loads(json.dumps(evidence))
    promoted_release_state = json.loads(json.dumps(release_state))
    promoted_evidence, _ = _promote_candidate_evidence(
        promoted_evidence,
        promoted_release_state,
    )
    evidence["public_production_readiness"] = promoted_evidence[
        "public_production_readiness"
    ]

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
    )

    assert (
        "public production readiness requires a verified candidate deployment" in errors
    )


@pytest.mark.parametrize(
    ("field", "expected_error"),
    (
        (
            "reviewer_access",
            "reviewer access is pending but contains verified field observed_at",
        ),
        (
            "publisher_identity",
            "publisher identity is pending but contains verified field observed_at",
        ),
    ),
)
def test_pending_identity_gates_cannot_retain_verified_proof(
    monkeypatch,
    tmp_path,
    field,
    expected_error,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    evidence[field]["status"] = "pending"

    errors = _validate_portal_evidence(monkeypatch, tmp_path, evidence)

    assert expected_error in errors


def test_pending_demo_cannot_retain_verified_proof(monkeypatch, tmp_path):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    evidence["demo_recording"].update(
        {
            "url": "https://demo.sparklaun.ch/demo",
            "observed_at": "2026-09-06T20:04:00Z",
            "reviewer_access_verified": True,
        }
    )

    errors = _validate_portal_evidence(monkeypatch, tmp_path, evidence)

    assert "pending demo recording must not contain a URL" in errors
    assert "pending demo recording must not contain an observation time" in errors
    assert "pending demo recording must not claim reviewer access" in errors


@pytest.mark.parametrize(
    ("field", "label"),
    (
        ("production_deployment", "candidate deployment"),
        ("authenticated_production_scan", "authenticated production scan"),
        ("reviewer_access", "reviewer access"),
        ("publisher_identity", "publisher identity"),
    ),
)
def test_verified_demo_requires_verified_recording_prerequisites(
    monkeypatch,
    tmp_path,
    field,
    label,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(
            encoding="utf-8"
        )
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    evidence, release_state = _promote_candidate_evidence(evidence, release_state)
    evidence[field]["status"] = "pending"

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
    )

    assert f"verified demo recording requires verified {label}" in errors


@pytest.mark.parametrize(
    ("field", "label"),
    (
        ("authenticated_production_scan", "authenticated production scan"),
        ("reviewer_access", "reviewer access"),
        ("publisher_identity", "publisher identity"),
    ),
)
def test_verified_demo_must_postdate_recording_prerequisites(
    monkeypatch,
    tmp_path,
    field,
    label,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(
            encoding="utf-8"
        )
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    evidence, release_state = _promote_candidate_evidence(evidence, release_state)
    evidence[field]["observed_at"] = "2026-09-06T20:05:00Z"

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
    )

    assert (
        f"demo recording observation must be later than {label} observation"
        in errors
    )


@pytest.mark.parametrize(
    ("url", "expected"),
    (
        ("https://demo.sparklaun.ch/demo", True),
        ("https://demo.sparklaun.ch/demo?v=public-id", True),
        ("https://8.8.8.8/demo", True),
        ("http://demo.sparklaun.ch/demo", False),
        ("https://:443", False),
        ("https://localhost/demo", False),
        ("https://internal/demo", False),
        ("https://service.internal/demo", False),
        ("https://127.0.0.1/demo", False),
        ("https://127.1/demo", False),
        ("https://2130706433/demo", False),
        ("https://0x7f.0.0.1/demo", False),
        ("https://10.0.0.1/demo", False),
        ("https://exa mple.com/demo", False),
        ("https://demo.sparklaun.ch:0/demo", False),
        ("https://demo.sparklaun.ch/demo?token=supersecretvalue", False),
        ("https://demo.sparklaun.ch/demo?signature=supersecretvalue", False),
        ("https://demo.sparklaun.ch/demo?password=supersecretvalue", False),
        ("https://demo.sparklaun.ch/demo?passphrase=supersecretvalue", False),
        ("https://demo.sparklaun.ch/demo?passcode=supersecretvalue", False),
        ("https://demo.sparklaun.ch/demo?pwd=supersecretvalue", False),
        ("https://demo.sparklaun.ch/demo?session_id=supersecretvalue", False),
        (
            "https://demo.sparklaun.ch/demo?target="
            "https%3A%2F%2Fvideo.example.com%2Fwatch%23access_token%3Dsecret",
            False,
        ),
        (
            "https://demo.sparklaun.ch/demo?design=minimal&codec=av1&monkey=capuchin",
            True,
        ),
    ),
)
def test_demo_url_must_be_credential_free_and_public(url, expected):
    assert portal_prerequisite_validator._is_https_url(url) is expected


def test_portal_prerequisite_cli_defaults_to_strict(capsys):
    assert portal_prerequisite_validator.main([]) == 1
    strict_output = capsys.readouterr().out
    assert (
        "external portal gate is still pending: production_deployment" in strict_output
    )

    assert portal_prerequisite_validator.main(["--allow-pending"]) == 0
    assert capsys.readouterr().out.strip() == (
        "ChatGPT portal prerequisite evidence passed."
    )


def test_portal_scan_alone_cannot_verify_a_new_undeployed_candidate(
    monkeypatch,
    tmp_path,
):
    evidence = json.loads(
        (ROOT / "submission" / "portal-prerequisites.json").read_text(encoding="utf-8")
    )
    release_state = json.loads(
        (ROOT / "release-state.json").read_text(encoding="utf-8")
    )
    evidence["authenticated_production_scan"].update(
        {
            "status": "verified",
            "observed_at": "2026-09-04T22:30:00Z",
            "tool_count": len(MCP_TOOL_CONTRACTS),
            "portal_result": "successful",
        }
    )
    release_state["runtime"]["candidate"]["openai_portal_rescan_status"] = "verified"

    errors = _validate_portal_evidence(
        monkeypatch,
        tmp_path,
        evidence,
        release_state,
    )
    assert (
        "verified authenticated production scan requires a verified candidate deployment"
        in errors
    )
    assert (
        "verified authenticated production scan requires a verified direct authenticated scan"
        in errors
    )


def test_public_repository_has_license_and_security_guidance():
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")

    assert "Proprietary" in license_text
    assert "support@sparklaun.ch" in security
    assert "Do not open a public issue" in security


def test_plugin_brand_assets_are_canonical_and_theme_ready():
    manifest = json.loads(
        (ROOT / "plugins" / "sparklaunch" / ".codex-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    interface = manifest["interface"]
    assert interface["composerIcon"] == "./assets/sparklaunch-small.png"
    assert interface["logo"] == "./assets/sparklaunch.png"
    assert interface["logoDark"] == "./assets/sparklaunch.png"

    assets = ROOT / "plugins" / "sparklaunch" / "assets"
    for name in (
        "sparklaunch-small.png",
        "sparklaunch.png",
        "sparklaunch-wordmark-light.png",
        "sparklaunch-wordmark-dark.png",
    ):
        assert (assets / name).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    expected_small = (assets / "sparklaunch-small.png").read_bytes()
    expected_large = (assets / "sparklaunch.png").read_bytes()
    for skill in SKILLS:
        skill_assets = ROOT / skill / "assets"
        assert (skill_assets / "sparklaunch-small.png").read_bytes() == expected_small
        assert (skill_assets / "sparklaunch.png").read_bytes() == expected_large


def test_submission_bundle_is_complete_and_deterministic(tmp_path):
    first, first_digest = build_bundle(tmp_path / "first.zip")
    second, second_digest = build_bundle(tmp_path / "second.zip")

    assert first_digest == second_digest
    assert first_digest == hashlib.sha256(first.read_bytes()).hexdigest().upper()
    assert portal_bundle_layout_errors(first) == []
    with ZipFile(first) as archive:
        names = set(archive.namelist())
        plugin_root = ROOT / "plugins" / "sparklaunch"
        expected_names = {
            path.relative_to(plugin_root).as_posix()
            for path in plugin_root.rglob("*")
            if path.is_file()
        }
        assert names == expected_names
        assert ".codex-plugin/plugin.json" in names
        assert ".mcp.json" in names
        assert "LICENSE" in names
        assert "assets/sparklaunch.png" in names
        assert "assets/sparklaunch-small.png" in names
        assert "assets/sparklaunch-wordmark-light.png" in names
        assert "assets/sparklaunch-wordmark-dark.png" in names
        assert "skills/sparklaunch-platform/SKILL.md" in names
        assert not any(name.startswith("plugins/sparklaunch/") for name in names)
        assert "chatgpt-app-submission.json" not in names
        assert not any(name.startswith(("evals/", "submission/")) for name in names)
        assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)


def test_clean_checkout_builds_candidate_before_portal_validation(
    tmp_path,
    monkeypatch,
):
    workflow = (ROOT / ".github/workflows/validate-host-packages.yml").read_text(
        encoding="utf-8"
    )
    build_command = "python scripts/build_submission_bundle.py"
    validation_command = (
        "python scripts/validate_portal_prerequisites.py --allow-pending"
    )
    assert workflow.index(build_command) < workflow.index(validation_command)

    clean_root = tmp_path / "clean-checkout"
    evidence_target = clean_root / "submission/portal-prerequisites.json"
    manifest_target = clean_root / "plugins/sparklaunch/.codex-plugin/plugin.json"
    runbook_target = clean_root / "submission/demo-recording-runbook.md"
    evidence_target.parent.mkdir(parents=True)
    manifest_target.parent.mkdir(parents=True)
    evidence_target.write_bytes(
        (ROOT / "submission/portal-prerequisites.json").read_bytes()
    )
    manifest_target.write_bytes(
        (ROOT / "plugins/sparklaunch/.codex-plugin/plugin.json").read_bytes()
    )
    runbook_target.write_bytes(
        (ROOT / "submission/demo-recording-runbook.md").read_bytes()
    )

    evidence = json.loads(evidence_target.read_text(encoding="utf-8"))
    bundle_target = clean_root / evidence["candidate"]["bundle_path"]
    assert not bundle_target.exists()
    _bundle, digest = build_bundle(bundle_target)
    assert digest == evidence["candidate"]["bundle_sha256"]

    monkeypatch.setattr(portal_prerequisite_validator, "ROOT", clean_root)
    monkeypatch.setattr(
        portal_prerequisite_validator,
        "EVIDENCE_PATH",
        evidence_target,
    )
    monkeypatch.setattr(
        portal_prerequisite_validator,
        "MANIFEST_PATH",
        manifest_target,
    )
    errors = portal_prerequisite_validator.validate(allow_pending=True)
    assert errors == []


def test_portal_bundle_layout_validation_rejects_nested_plugin_root(tmp_path):
    bundle = tmp_path / "nested.zip"
    with ZipFile(bundle, "w") as archive:
        archive.writestr("plugins/sparklaunch/.codex-plugin/plugin.json", "{}")

    errors = portal_bundle_layout_errors(bundle)

    assert any(
        "exactly one root .codex-plugin/plugin.json" in error for error in errors
    )
    assert any("non-plugin files" in error for error in errors)
