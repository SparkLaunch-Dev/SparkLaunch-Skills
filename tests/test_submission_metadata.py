"""T-METADATA-SUBFIX: supported review fields and server surface agree in the ZIP."""

import json
from zipfile import ZipFile

import pytest

from scripts import build_submission_bundle as bundle
from scripts.chatgpt_surface import CHATGPT_MCP_URL, CHATGPT_SPARKCLOSE_TOOLS
from scripts.generate_submission import build_submission
from scripts.tool_contract_snapshot import CHATGPT_SNAPSHOT_PATH, load_snapshot


def test_zip_imports_supported_review_publication_and_the_restricted_surface(tmp_path):
    path, _ = bundle.build_bundle(tmp_path / "candidate.zip")
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read(bundle.PLUGIN_MANIFEST))
        openai = manifest["extensions"]["com.openai"]
        review = openai["review"]
        assert len(review["test_cases"]["positive"]) == 5
        assert len(review["test_cases"]["negative"]) == 3
        for case in review["test_cases"]["positive"]:
            assert set(case) == {"description", "prompt", "tools_triggered", "expected_behavior"}
            assert all(isinstance(v, str) and v.strip() for v in case.values())
        assert openai["publication"]["countries"] == []
        assert openai["publication"]["release_notes"]
        assert "demo_recording_url" not in review  # Owner-supplied, not fabricated.
        assert ".app.json" not in archive.namelist()
        assert "apps" not in manifest
        assert json.loads(archive.read(".mcp.json"))["mcpServers"]["sparklaunch"]["url"] == CHATGPT_MCP_URL
        names = set(load_snapshot(CHATGPT_SNAPSHOT_PATH)["tools"])
        assert set(build_submission()["tools"]) == names
        assert {n for n in names if n.startswith("sparkclose.")} == CHATGPT_SPARKCLOSE_TOOLS
        excluded = {"sparkclose." + n for n in ("close_investment", "open_workflow", "prepare_agreement", "preview_agreement", "record_approval", "record_receipt", "reconcile_funding", "retry_updates", "cancel_unsigned")}
        for name in archive.namelist():
            if name.endswith((".md", ".yaml")):
                text = archive.read(name).decode("utf-8")
                assert not any(n in text for n in excluded), name


@pytest.mark.parametrize("change", [
    {"countries": "all"}, {"countries": ["USA"]}, {"release_notes": ""},
    {"password": "not-a-real-secret"},
])
def test_invalid_or_sensitive_publication_fields_fail_before_archive_creation(monkeypatch, tmp_path, change):
    source = json.loads(bundle.PUBLIC_METADATA_PATH.read_text(encoding="utf-8"))
    source["publication"].update(change)
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps(source), encoding="utf-8")
    monkeypatch.setattr(bundle, "PUBLIC_METADATA_PATH", metadata)
    target = tmp_path / "rejected.zip"
    with pytest.raises(ValueError):
        bundle.build_bundle(target)
    assert not target.exists()


def test_public_snapshot_matches_the_server_allowlist_when_backend_available():
    backend = bundle.ROOT.parent / "SparkLaunch/backend/mcp_chatgpt_tools.json"
    if not backend.exists():
        pytest.skip("Sibling backend unavailable; run export --surface chatgpt --check there")
    assert set(json.loads(backend.read_text(encoding="utf-8"))["tools"]) == set(load_snapshot(CHATGPT_SNAPSHOT_PATH)["tools"])
