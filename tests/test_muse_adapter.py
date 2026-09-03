import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "adapters" / "muse"
MCP_URL = "https://sparklaun.ch/api/mcp/"


def test_muse_settings_example_is_disabled_and_fail_soft() -> None:
    settings = json.loads((ADAPTER / "settings.example.json").read_text(encoding="utf-8"))

    assert settings["schema_version"] == 1
    assert set(settings) == {"schema_version", "mcp_servers"}
    assert set(settings["mcp_servers"]) == {"sparklaunch"}

    server = settings["mcp_servers"]["sparklaunch"]
    assert server == {
        "transport": "streamable_http",
        "url": MCP_URL,
        "headers": {},
        "enabled": False,
        "mode": "optional",
    }


def test_muse_package_states_the_protected_oauth_boundary() -> None:
    connection = (ADAPTER / "connection.md").read_text(encoding="utf-8")
    readme = (ADAPTER / "README.md").read_text(encoding="utf-8")
    combined = "\n".join((connection, readme)).lower()

    assert "not activated" in combined
    assert "does not document" in combined
    assert "disabled and optional" in combined
    assert "do not paste" in combined
    assert "stop before any write" in combined
    assert "marketplace installation" in combined
    assert "muse skills validate" in readme
    assert "muse skills list" in readme


def test_muse_adapter_contains_no_static_secret_path() -> None:
    settings_text = (ADAPTER / "settings.example.json").read_text(encoding="utf-8")
    settings = json.loads(settings_text)
    combined_text = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(ADAPTER.iterdir())
    )

    assert settings["mcp_servers"]["sparklaunch"]["headers"] == {}
    assert "Authorization" not in settings_text
    assert "Bearer " not in settings_text
    assert "${SPARKLAUNCH" not in combined_text
    assert "%SPARKLAUNCH" not in combined_text
    assert "<token>" not in combined_text.lower()
    assert {path.name for path in ADAPTER.iterdir()} == {
        "README.md",
        "adapter.json",
        "connection.md",
        "settings.example.json",
    }
