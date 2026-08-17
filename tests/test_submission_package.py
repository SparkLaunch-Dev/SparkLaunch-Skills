import json
import hashlib
from zipfile import ZipFile

from scripts.build_submission_bundle import build_bundle
from scripts.generate_submission import ROOT, build_submission, main as generate_submission
from scripts.sync_plugin import SKILLS, expected_pairs, sync
from scripts.validate_submission import validate


def test_packaged_skills_are_exact_deterministic_mirrors():
    assert len(expected_pairs()) > 40
    assert sync(write=False) == []


def test_every_skill_distinguishes_connector_absence_from_oauth():
    required = (
        "SparkLaunch isn't loaded in this conversation.",
        "Start a new ChatGPT conversation",
        "OAuth challenge",
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
    }
    assert sum(not case["expected_skills"] for case in cases) == 8


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

    assert covered_tools == set(submission["tools"])
    assert covered_recipes == {
        "connect-sparklaunch-to-chatgpt.md",
        "validate-an-idea-and-generate-a-report.md",
        "create-a-brand-foundation.md",
        "plan-and-publish-a-launch.md",
        "review-launch-signals-and-follow-up.md",
        "start-a-business-from-an-idea.md",
    }
    controls = matrix["controls"]
    assert controls["automatic_validation_typical_minutes"] == "10-15"
    assert controls["automatic_validation_poll_seconds"] >= 60
    assert controls["automatic_validation_timeout_minutes"] >= 20
    assert controls["expected_oauth_scope_count"] == 15
    assert controls["preflight_effective_permissions"] is True
    assert controls["open_and_cancel_disconnect_dialog"] is True
    assert controls["never_auto_confirm"] is True
    assert controls["never_perform_real_outreach"] is True
    assert controls["never_retry_uncertain_write_with_new_key"] is True


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


def test_reviewer_documents_are_credential_free_and_candidate_bounded():
    release_notes = (ROOT / "submission" / "release-notes.md").read_text(
        encoding="utf-8"
    )
    reviewer = (ROOT / "submission" / "reviewer-instructions.md").read_text(
        encoding="utf-8"
    )
    assert "not yet deployed or submitted" in release_notes
    assert "Production deployment" in release_notes
    assert "supplied through the approved private reviewer channel" in reviewer
    assert "must never be added to this file" in reviewer
    assert "support@sparklaun.ch" in reviewer
    assert "plugins/sparklaunch/assets/sparklaunch.png" in reviewer
    assert "sparklaunch-wordmark-light.png" in reviewer
    assert "sparklaunch-wordmark-dark.png" in reviewer


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
