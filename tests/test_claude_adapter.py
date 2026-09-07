from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path, PurePosixPath

import pytest


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_ROOT = ROOT / "adapters" / "claude"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_claude_adapter_contract_is_safe_and_builder_consumable() -> None:
    adapter = _load_json(ADAPTER_ROOT / "adapter.json")

    assert adapter["host"] == "claude"
    assert adapter["format"] == "claude-code-plugin"
    assert adapter["package_path"] == "plugins/claude/sparklaunch"
    assert adapter["connection_fragment"] == "connection.md"

    destinations = set()
    for item in adapter["static_files"]:
        source = ADAPTER_ROOT / item["source"]
        destination = PurePosixPath(item["destination"])
        assert source.is_file()
        assert not destination.is_absolute()
        assert ".." not in destination.parts
        assert item["destination"] not in destinations
        destinations.add(item["destination"])

    assert destinations == {
        ".claude-plugin/plugin.json",
        ".mcp.json",
        "DISTRIBUTION.md",
    }

    manifest = _load_json(ADAPTER_ROOT / "templates" / "plugin.json")
    assert manifest["$schema"] == "https://json.schemastore.org/claude-code-plugin-manifest.json"
    assert manifest["name"] == "sparklaunch"
    assert manifest["version"] == "0.8.1"
    assert manifest["license"] == "Apache-2.0"
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"

    mcp = _load_json(ADAPTER_ROOT / "templates" / ".mcp.json")
    assert set(mcp) == {"mcpServers"}
    assert set(mcp["mcpServers"]) == {"sparklaunch"}
    server = mcp["mcpServers"]["sparklaunch"]
    assert server == {
        "type": "http",
        "url": "https://sparklaun.ch/api/mcp/",
    }

    serialized = json.dumps({"manifest": manifest, "mcp": mcp}).lower()
    for forbidden in ("authorization", "bearer ", "clientsecret", "client_secret", "access_token"):
        assert forbidden not in serialized


def test_claude_connection_and_distribution_text_are_truthful() -> None:
    connection = (ADAPTER_ROOT / "connection.md").read_text(encoding="utf-8")
    distribution = (ADAPTER_ROOT / "DISTRIBUTION.md").read_text(encoding="utf-8")

    assert [line.split(".", 1)[0] for line in connection.splitlines()] == ["1", "2", "3", "4"]
    assert "Claude Code" in connection
    assert "`/mcp`" in connection
    assert "Never ask the user for credentials" in connection
    assert "stop before any write" in connection
    assert "proprietary" in distribution.lower()
    assert "Apache-2.0" in distribution
    assert "does not claim public listing" in distribution.lower()
    assert "claude plugin validate" in distribution


@pytest.mark.skipif(shutil.which("claude") is None, reason="Claude Code is not installed")
def test_claude_template_passes_native_strict_validation(tmp_path: Path) -> None:
    manifest = _load_json(ADAPTER_ROOT / "templates" / "plugin.json")

    manifest_dir = tmp_path / ".claude-plugin"
    skill_dir = tmp_path / "skills" / "sparklaunch-adapter-test"
    manifest_dir.mkdir(parents=True)
    skill_dir.mkdir(parents=True)
    (manifest_dir / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    shutil.copy2(ADAPTER_ROOT / "templates" / ".mcp.json", tmp_path / ".mcp.json")
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: sparklaunch-adapter-test\n"
        "description: Validate the generated Claude Code adapter layout.\n"
        "---\n\n"
        "# SparkLaunch adapter test\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["claude", "plugin", "validate", str(tmp_path), "--strict"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
