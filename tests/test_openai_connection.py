"""Connected-account wiring and portal export regressions (ACCT requirements)."""

import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts.build_submission_bundle import build_bundle, portal_bundle_layout_errors
from scripts.openai_connection import APPS_CONFIG, native_connection_errors
from scripts.sync_plugin import ROOT
from scripts.validate_host_packages import validate


@pytest.mark.parametrize(
    "apps",
    [{}, {"apps": {}}, {"apps": {"sparklaunch": {"id": "asdk_app_wrong"}}},
     {"apps": {**APPS_CONFIG["apps"], "duplicate": APPS_CONFIG["apps"]["sparklaunch"]}}],
)
def test_acct_contract_001_rejects_missing_wrong_or_duplicate_app(apps):
    assert native_connection_errors({"apps": "./.app.json"}, apps) == [
        "native SparkLaunch must bind exactly the registered SparkLaunch App"
    ]


def test_acct_sec_001_rejects_duplicate_native_mcp_declaration():
    assert native_connection_errors(
        {"apps": "./.app.json", "mcpServers": "./.mcp.json"}, APPS_CONFIG
    ) == ["native SparkLaunch must not declare a duplicate raw MCP server"]


def test_acct_contract_001_host_validator_rejects_wrong_app(monkeypatch):
    target = ROOT / "plugins/sparklaunch/.app.json"
    original = Path.read_text

    def read_text(path, *args, **kwargs):
        if path == target:
            return json.dumps({"apps": {"sparklaunch": {"id": "asdk_app_wrong"}}})
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    assert "native SparkLaunch must bind exactly the registered SparkLaunch App" in validate()


def test_acct_contract_002_public_zip_contains_only_mcp_connection(tmp_path):
    native = ROOT / "plugins/sparklaunch"
    before = (native / ".codex-plugin/plugin.json").read_bytes()
    assert (native / ".app.json").is_file()
    assert not (native / ".mcp.json").exists()
    assert not (native / "mcp.json").exists()
    first, first_digest = build_bundle(tmp_path / "first.zip")
    second, second_digest = build_bundle(tmp_path / "second.zip")
    assert first_digest == second_digest
    assert first.read_bytes() == second.read_bytes()
    assert portal_bundle_layout_errors(first) == []
    with ZipFile(first) as archive:
        assert ".app.json" not in archive.namelist()
        assert "mcp/portal.json" not in archive.namelist()
        manifest = json.loads(archive.read(".codex-plugin/plugin.json"))
        assert "apps" not in manifest
        assert manifest["mcpServers"] == "./.mcp.json"
        assert json.loads(archive.read(".mcp.json")) == json.loads(
            (native / "mcp/portal.json").read_text()
        )
        assert len([p for p in archive.namelist() if p.endswith("/SKILL.md")]) == 12
    assert (native / ".codex-plugin/plugin.json").read_bytes() == before


def test_acct_contract_002_layout_validator_rejects_app_references(tmp_path):
    bundle, _ = build_bundle(tmp_path / "good.zip")
    with ZipFile(bundle) as archive:
        content = {name: archive.read(name) for name in archive.namelist()}
    manifest = json.loads(content[".codex-plugin/plugin.json"])
    manifest["apps"] = "./.app.json"
    content[".codex-plugin/plugin.json"] = json.dumps(manifest).encode()
    invalid = tmp_path / "invalid.zip"
    with ZipFile(invalid, "w") as archive:
        for name, data in content.items():
            archive.writestr(name, data)
    assert "portal plugin ZIP must not declare registered App references" in portal_bundle_layout_errors(invalid)
