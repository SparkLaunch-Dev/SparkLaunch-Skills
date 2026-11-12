"""T-METADATA-SUBFIX: supported review fields and server surface agree in the ZIP."""

import copy
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
        dependency = archive.read("skills/sparklaunch-sparkclose/agents/openai.yaml").decode()
        assert "SAFE planning and private-record tools" in dependency
        native = (bundle.PLUGIN_ROOT / "skills/sparklaunch-sparkclose/agents/openai.yaml").read_text()
        assert "SAFE modeling and closing tools" in native
        excluded = {"sparkclose." + n for n in ("close_investment", "open_workflow", "prepare_agreement", "preview_agreement", "record_approval", "record_receipt", "reconcile_funding", "retry_updates", "cancel_unsigned")}
        for name in archive.namelist():
            if name.endswith((".md", ".yaml")):
                text = archive.read(name).decode("utf-8")
                assert not any(n in text for n in excluded), name
                from scripts.chatgpt_surface import public_scope_findings
                assert public_scope_findings(text) == [], name


def test_public_projection_keeps_full_host_operations_and_rejects_unhandled_claims():
    from scripts.chatgpt_surface import public_description, public_scope_findings
    routing = (bundle.ROOT / "src/skills/sparklaunch-platform/SKILL.md").read_text()
    catalog = (bundle.ROOT / "src/recipes/README.md").read_text()
    assert "investment closings" in routing
    assert "close one signed investment" in catalog
    assert public_scope_findings(public_description(routing + catalog)) == []
    with pytest.raises(ValueError, match="excluded capability"):
        bundle._public_content("skills/example/SKILL.md", b"Close a signed investment for the user.")


@pytest.mark.parametrize("existing", [False, True])
def test_unhandled_public_claim_does_not_create_or_replace_archive(tmp_path, monkeypatch, existing):
    original = bundle._archive_content

    def content(source):
        data = original(source)
        if source.relative_to(bundle.PLUGIN_ROOT).as_posix() == "skills/sparklaunch-platform/SKILL.md":
            return data + b"\nClose a signed investment for the user.\n"
        return data

    monkeypatch.setattr(bundle, "_archive_content", content)
    path = tmp_path / "candidate.zip"
    if existing:
        path.write_bytes(b"preceding archive")
    with pytest.raises(ValueError, match="excluded capability"):
        bundle.build_bundle(path)
    if existing:
        assert path.read_bytes() == b"preceding archive"
    else:
        assert not path.exists()


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


@pytest.mark.parametrize("section,field", [
    ("review", "commerce_description"), ("publication", "release_notes"),
])
@pytest.mark.parametrize("payload", [
    "password=synthetic-secret", "https://example.com/video?access_token=synthetic-secret",
    "https://example.com/video?redirect=https%3A%2F%2Fexample.com%2F%3Ftoken%3Dsynthetic-secret",
])
@pytest.mark.parametrize("existing_archive", [False, True])
def test_sensitive_metadata_text_cannot_create_or_overwrite_an_archive(
    monkeypatch, tmp_path, section, field, payload, existing_archive,
):
    source = json.loads(bundle.PUBLIC_METADATA_PATH.read_text(encoding="utf-8"))
    source[section][field] = payload
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps(source), encoding="utf-8")
    monkeypatch.setattr(bundle, "PUBLIC_METADATA_PATH", metadata)
    target = tmp_path / "rejected.zip"
    if existing_archive:
        target.write_bytes(b"previous archive")
    with pytest.raises(ValueError, match="sensitive material") as error:
        bundle.build_bundle(target)
    assert "synthetic-secret" not in str(error.value)
    if existing_archive:
        assert target.read_bytes() == b"previous archive"
    else:
        assert not target.exists()


@pytest.mark.parametrize("url", [
    "https://example.com/video?token=synthetic-secret",
    "https://example.com/video#access_token=synthetic-secret",
])
def test_credential_bearing_demo_url_is_rejected(monkeypatch, tmp_path, url):
    source = json.loads(bundle.PUBLIC_METADATA_PATH.read_text(encoding="utf-8"))
    source["review"]["demo_recording_url"] = url
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps(source), encoding="utf-8")
    monkeypatch.setattr(bundle, "PUBLIC_METADATA_PATH", metadata)
    target = tmp_path / "rejected.zip"
    with pytest.raises(ValueError, match="sensitive material"):
        bundle.build_bundle(target)
    assert not target.exists()


@pytest.mark.parametrize("kind,field", [
    ("test_cases", "description"), ("test_cases", "user_prompt"),
    ("test_cases", "expected_output"), ("negative_test_cases", "description"),
    ("negative_test_cases", "user_prompt"),
])
@pytest.mark.parametrize("payload", [
    "password=synthetic-secret", "https://example.com/action?token=synthetic-secret",
])
def test_sensitive_projected_review_cases_are_rejected(monkeypatch, tmp_path, kind, field, payload):
    submission = copy.deepcopy(build_submission())
    submission[kind][0][field] = payload
    monkeypatch.setattr(bundle, "build_submission", lambda: submission)
    target = tmp_path / "rejected.zip"
    with pytest.raises(ValueError, match="sensitive material") as error:
        bundle.build_bundle(target)
    assert "synthetic-secret" not in str(error.value)
    assert not target.exists()
