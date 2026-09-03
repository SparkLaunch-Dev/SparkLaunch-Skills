import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "adapters" / "gemini"
MCP_URL = "https://sparklaun.ch/api/mcp/"


def test_gemini_manifest_uses_native_streamable_http_contract() -> None:
    manifest = json.loads((ADAPTER / "gemini-extension.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "sparklaunch"
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", manifest["version"])
    assert manifest["contextFileName"] == "GEMINI.md"
    assert set(manifest["mcpServers"]) == {"sparklaunch"}

    server = manifest["mcpServers"]["sparklaunch"]
    assert server == {"httpUrl": MCP_URL}
    assert "url" not in server
    assert "command" not in server
    assert "trust" not in server
    assert "headers" not in server


def test_gemini_recovery_uses_client_oauth_without_credentials() -> None:
    context = (ADAPTER / "GEMINI.md").read_text(encoding="utf-8")
    connection = (ADAPTER / "connection.md").read_text(encoding="utf-8")
    readme = (ADAPTER / "README.md").read_text(encoding="utf-8")
    combined = "\n".join((context, connection, readme))

    assert "/mcp auth sparklaunch" in context
    assert "stop before any write" in combined.lower()
    assert "never ask" in combined.lower()
    assert "gemini extensions validate" in readme
    assert "gemini extensions link" in readme
    assert "\n/mcp\n" in readme
    assert "gemini mcp list" in readme
    assert "Authorization:" not in combined
    assert "Bearer " not in combined
    assert "${SPARKLAUNCH" not in combined
    assert "%SPARKLAUNCH" not in combined
    assert "<token>" not in combined.lower()


def test_gemini_adapter_contains_only_builder_inputs() -> None:
    assert {path.name for path in ADAPTER.iterdir()} == {
        "GEMINI.md",
        "README.md",
        "adapter.json",
        "connection.md",
        "gemini-extension.json",
    }
