import json
import hashlib
from zipfile import ZipFile

from scripts.build_submission_bundle import build_bundle
from scripts.generate_submission import ROOT, build_submission, main as generate_submission
from scripts.sync_plugin import expected_pairs, sync
from scripts.validate_submission import validate


def test_packaged_skills_are_exact_deterministic_mirrors():
    assert len(expected_pairs()) > 40
    assert sync(write=False) == []


def test_submission_package_is_complete():
    assert validate() == []
    generated = json.loads((ROOT / "chatgpt-app-submission.json").read_text(encoding="utf-8"))
    assert generated == build_submission()
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
        assert "submission/release-notes.md" in names
        assert "submission/reviewer-instructions.md" in names
        assert "submission/reviewer-fixture.json" in names
        assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)
