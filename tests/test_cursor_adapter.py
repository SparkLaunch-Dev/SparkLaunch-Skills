from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_ROOT = ROOT / "adapters" / "cursor"
PLUGIN_NAME_PATTERN = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_cursor_adapter_conforms_to_agent_plugins_1_0_shape() -> None:
    adapter = _load_json(ADAPTER_ROOT / "adapter.json")

    assert adapter["host"] == "cursor"
    assert adapter["format"] == "agent-plugins-1.0.0"
    assert adapter["package_path"] == "plugins/cursor/sparklaunch"
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

    assert destinations == {"plugin.json", "mcp.json", "DISTRIBUTION.md", "README.md"}

    manifest = _load_json(ADAPTER_ROOT / "templates" / "plugin.json")
    assert manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert manifest["version"] == "0.8.1"
    assert manifest["license"] == "Apache-2.0"
    assert PLUGIN_NAME_PATTERN.fullmatch(manifest["name"])
    assert set(manifest) <= {
        "$schema",
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "extensions",
    }
    assert set(manifest["author"]) <= {"name", "email", "url"}

    mcp = _load_json(ADAPTER_ROOT / "templates" / "mcp.json")
    assert mcp["$schema"] == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
    assert set(mcp) == {"$schema", "mcpServers"}
    assert set(mcp["mcpServers"]) == {"sparklaunch"}
    server = mcp["mcpServers"]["sparklaunch"]
    assert server == {
        "type": "streamable-http",
        "url": "https://sparklaun.ch/api/mcp/",
    }

    serialized = json.dumps({"manifest": manifest, "mcp": mcp}).lower()
    for forbidden in ("authorization", "bearer ", "clientsecret", "client_secret", "access_token"):
        assert forbidden not in serialized


def test_cursor_connection_and_distribution_text_are_truthful() -> None:
    connection = (ADAPTER_ROOT / "connection.md").read_text(encoding="utf-8")
    distribution = (ADAPTER_ROOT / "DISTRIBUTION.md").read_text(encoding="utf-8")

    assert [line.split(".", 1)[0] for line in connection.splitlines()] == ["1", "2", "3", "4"]
    assert "Cursor" in connection
    assert "Customize" in connection
    assert "Never ask the user for credentials" in connection
    assert "stop before any write" in connection
    assert "proprietary" in distribution.lower()
    assert "public Marketplace requires plugins to be open source" in distribution
    assert "Apache-2.0" in distribution
    assert "~/.cursor/plugins/local/sparklaunch" in distribution
