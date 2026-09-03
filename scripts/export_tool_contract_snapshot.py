"""Export a deterministic MCP tool descriptor snapshot from the sibling runtime."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKEND = ROOT.parent / "SparkLaunch" / "backend"
OUTPUT = ROOT / "contracts" / "tools.snapshot.json"


def _isolate_import_environment(database_path: Path) -> None:
    database_url = f"sqlite:///{database_path.as_posix()}"
    os.environ.update(
        {
            "DATABASE_URL": database_url,
            "DATABASE_READ_URL": database_url,
            "JWT_SECRET_KEY": "tool-contract-snapshot-only",
            "ENABLE_MCP_SERVER": "false",
            "ENVIRONMENT": "test",
            "APP_ENV": "test",
            "SPARKLAUNCH_ENV": "test",
            "FORMATION_EXTERNAL_ACTIONS_ENABLED": "false",
            "FORMATION_FILING_OPERATIONS_WORKER": "false",
        }
    )


def build_snapshot(backend: Path = DEFAULT_BACKEND) -> dict[str, object]:
    backend = backend.resolve()
    if not (backend / "mcp_server.py").is_file():
        raise ValueError(f"SparkLaunch backend not found: {backend}")
    with tempfile.TemporaryDirectory(prefix="sparklaunch-contract-snapshot-") as directory:
        _isolate_import_environment(Path(directory) / "snapshot.db")
        sys.path.insert(0, str(backend))
        try:
            from mcp_server import create_mcp_server
            from mcp_server_version import SPARKLAUNCH_MCP_SERVER_VERSION
            from mcp_tool_contracts import MCP_TOOL_CONTRACTS

            descriptors = asyncio.run(
                create_mcp_server(streamable_http_path="/").list_tools()
            )
        finally:
            database_module = sys.modules.get("database")
            if database_module is not None:
                database_module.engine.dispose()
                read_engine = getattr(database_module, "read_engine", None)
                if read_engine is not None:
                    read_engine.dispose()
            if sys.path and sys.path[0] == str(backend):
                sys.path.pop(0)

    descriptor_by_name = {tool.name: tool for tool in descriptors}
    if set(descriptor_by_name) != set(MCP_TOOL_CONTRACTS):
        raise ValueError("runtime descriptors do not match MCP_TOOL_CONTRACTS")
    tools: dict[str, object] = {}
    for name in sorted(MCP_TOOL_CONTRACTS):
        contract = MCP_TOOL_CONTRACTS[name]
        tools[name] = {
            "contract": {
                "title": contract.title,
                "description": contract.description,
                "required_scope": contract.required_scope,
                "project_scoped": contract.project_scoped,
                "read_only": contract.read_only,
                "open_world": contract.open_world,
                "destructive": contract.destructive,
                "idempotent": contract.idempotent,
                "privacy_class": contract.privacy_class,
                "success_required": list(contract.success_required),
            },
            "descriptor": descriptor_by_name[name].model_dump(
                by_alias=True, exclude_none=True
            ),
        }
    return {
        "schema_version": 1,
        "server_version": SPARKLAUNCH_MCP_SERVER_VERSION,
        "tool_count": len(tools),
        "tools": tools,
    }


def _serialized(backend: Path) -> str:
    return json.dumps(build_snapshot(backend), indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", type=Path, default=DEFAULT_BACKEND)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        expected = _serialized(args.backend)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        print(f"Unable to export runtime contracts: {exc}", file=sys.stderr)
        return 1
    if args.check:
        try:
            current = OUTPUT.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(f"Tool contract snapshot is missing or unreadable: {exc}", file=sys.stderr)
            return 1
        if current != expected:
            print(
                "Tool contract snapshot is stale; run scripts/export_tool_contract_snapshot.py.",
                file=sys.stderr,
            )
            return 1
        print("Tool contract snapshot matches the sibling runtime.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
