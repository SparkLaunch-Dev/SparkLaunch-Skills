import json
import hashlib
from runpy import run_path
from zipfile import ZipFile

import pytest

import scripts.validate_submission as submission_validator
import scripts.generate_submission as submission_generator
from scripts.build_submission_bundle import build_bundle
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
from mcp_oauth_service import MCP_OAUTH_SUPPORTED_SCOPES


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


def test_submission_package_is_complete():
    assert validate() == []
    marketplace = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )
    sparklaunch = next(
        entry for entry in marketplace["plugins"] if entry["name"] == "sparklaunch"
    )
    assert sparklaunch["policy"]["authentication"] == "ON_USE"
    generated = json.loads((ROOT / "chatgpt-app-submission.json").read_text(encoding="utf-8"))
    assert generated == build_submission()
    assert len(generated["tools"]) == 54
    assert "incorporation" in generated["app_info"]["description"].lower()
    assert generated["$schema"] == (
        "https://developers.openai.com/plugins/schemas/"
        "chatgpt-app-submission.v1.json"
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
        f"project {fixture['project_id']}" in case["user_prompt"]
        for case in scoped
    )


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
            "Founder workflows for idea validation, branding, launches, CRM, "
            "and incorporation."
        ),
        "websiteUrl": "https://sparklaun.ch/",
        "remotes": [
            {"type": "streamable-http", "url": CANONICAL_MCP_URL}
        ],
    }
    assert "incorporation" in registry["description"].lower()
    assert len(registry["description"]) <= 100
    application_version = run_path(
        ROOT.parent / "SparkLaunch" / "backend" / "mcp_server_version.py"
    )["SPARKLAUNCH_MCP_SERVER_VERSION"]
    assert version == "1.1.0"
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
        ("$schema", "https://example.com/schema.json", "MCP Registry descriptor must use the pinned official schema"),
        ("name", "com.example/sparklaunch", "MCP Registry descriptor has the wrong server namespace"),
        ("title", "Other", "MCP Registry descriptor must use the SparkLaunch title"),
        ("description", "", "MCP Registry description must contain 1 to 100 characters"),
        ("description", "x" * 101, "MCP Registry description must contain 1 to 100 characters"),
        ("description", 123, "MCP Registry description must contain 1 to 100 characters"),
        ("version", "1.0", "MCP Registry descriptor must use a semantic service version"),
        ("websiteUrl", "https://example.com/", "MCP Registry descriptor has the wrong website URL"),
        ("remotes", [], "MCP Registry descriptor must expose only the canonical remote"),
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


def test_registry_validator_accepts_a_standalone_clone_without_the_application(tmp_path):
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

    assert "Clone the application and skills repositories as sibling directories" in readme
    assert "../SparkLaunch/backend" in readme
    assert "standalone `SparkLaunch-Skills` clone" in readme
    assert "cached by plugin version" in readme


def test_skill_trigger_evaluation_set_covers_every_skill_and_negative_boundaries():
    evaluations = json.loads(
        (ROOT / "evals" / "skill-trigger-cases.json").read_text(encoding="utf-8")
    )
    cases = evaluations["cases"]
    assert len(cases) == 30
    expected_skills = {
        skill
        for case in cases
        for skill in case["expected_skills"]
    }
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
    }
    assert sum(not case["expected_skills"] for case in cases) == 8
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
    covered_tools = {
        tool
        for case in matrix["cases"]
        for tool in case["tools"]
    }
    covered_recipes = {
        recipe
        for case in matrix["cases"]
        for recipe in case["recipes"]
    }

    assert len(matrix["cases"]) == 13
    assert covered_tools == set(submission["tools"])
    assert covered_recipes == {
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
        case["id"]: case for case in matrix["cases"] if case["id"].startswith("E2E-INCORPORATION-")
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
    assert len(MCP_OAUTH_SUPPORTED_SCOPES) == 18
    assert controls["expected_oauth_scope_count"] == len(MCP_OAUTH_SUPPORTED_SCOPES)
    expected_grant_marker = f"expected {len(MCP_OAUTH_SUPPORTED_SCOPES)}-scope grant"
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
        "18 OAuth scopes",
        "Never call Delaware, NWRA, or CorpTools",
        "zero provider calls",
        "submit to SparkLaunch Filing Operations",
        "receipt does not mean",
        "each person to their own Action Center",
    ):
        assert marker in runbook


def test_project_and_validation_guidance_uses_automatic_initial_research():
    project_skill = (ROOT / "sparklaunch-projects" / "SKILL.md").read_text(encoding="utf-8")
    validation_skill = (ROOT / "sparklaunch-idea-validation" / "SKILL.md").read_text(encoding="utf-8")
    validation_recipe = (
        ROOT / "recipes" / "validate-an-idea-and-generate-a-report.md"
    ).read_text(encoding="utf-8")

    for document in (project_skill, validation_skill, validation_recipe):
        assert "automatically" in document
        assert "10-15 minutes" in document
        assert "duplicate" in document
    assert "do not call `validation.create_project` or `validation.start_analysis`" in validation_recipe


def test_landing_recipe_forbids_invented_social_proof():
    launch_recipe = (ROOT / "recipes" / "plan-and-publish-a-launch.md").read_text(
        encoding="utf-8"
    )

    assert "invented testimonials" in launch_recipe
    assert "verified evidence" in launch_recipe


def test_project_guidance_preflights_effective_permissions_before_writes():
    project_skill = (ROOT / "sparklaunch-projects" / "SKILL.md").read_text(encoding="utf-8")
    connect_recipe = (
        ROOT / "recipes" / "connect-sparklaunch-to-chatgpt.md"
    ).read_text(encoding="utf-8")
    launch_recipe = (
        ROOT / "recipes" / "plan-and-publish-a-launch.md"
    ).read_text(encoding="utf-8")

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
        "Validation project id",
        "Selected palette id",
        "Short-lived download reference",
        "Confirmation-gated actions",
    ):
        assert supported in template


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
    assert manifest["version"].startswith("0.3.0+codex.20260820")
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
        "nine",
        "54 tools",
        "18 OAuth scopes",
        "submit to SparkLaunch Filing Operations",
        "receipt does not mean",
        "zero provider calls",
        "private Action Center",
    ):
        assert marker in release_notes
        assert marker in reviewer


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
    with ZipFile(first) as archive:
        names = set(archive.namelist())
        assert "plugins/sparklaunch/.codex-plugin/plugin.json" in names
        assert "plugins/sparklaunch/.mcp.json" in names
        assert "plugins/sparklaunch/LICENSE" in names
        assert "chatgpt-app-submission.json" in names
        assert "evals/skill-trigger-cases.json" in names
        assert "evals/controlled-e2e-matrix.json" in names
        assert "evals/CONTROLLED-E2E.md" in names
        assert "submission/release-notes.md" in names
        assert "submission/reviewer-instructions.md" in names
        assert "submission/reviewer-fixture.json" in names
        assert "plugins/sparklaunch/assets/sparklaunch.png" in names
        assert "plugins/sparklaunch/assets/sparklaunch-small.png" in names
        assert "plugins/sparklaunch/assets/sparklaunch-wordmark-light.png" in names
        assert "plugins/sparklaunch/assets/sparklaunch-wordmark-dark.png" in names
        assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)
