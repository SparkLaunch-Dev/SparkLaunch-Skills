"""Read the checked-in, runtime-derived SparkLaunch MCP tool contract snapshot."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "contracts" / "tools.snapshot.json"


@dataclass(frozen=True)
class ToolContractSnapshot:
    title: str
    description: str
    required_scope: str
    project_scoped: bool
    read_only: bool
    open_world: bool
    destructive: bool
    idempotent: bool
    privacy_class: str
    success_required: tuple[str, ...]
    descriptor: dict[str, Any]


def load_snapshot(path: Path = SNAPSHOT_PATH) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema_version") != 1:
        raise ValueError("tool contract snapshot must use schema_version 1")
    if not isinstance(document.get("server_version"), str):
        raise ValueError("tool contract snapshot must include server_version")
    tools = document.get("tools")
    if not isinstance(tools, dict) or not tools:
        raise ValueError("tool contract snapshot must include a non-empty tools object")
    if document.get("tool_count") != len(tools):
        raise ValueError("tool contract snapshot tool_count does not match its tools object")
    return document


def load_tool_contracts(path: Path = SNAPSHOT_PATH) -> dict[str, ToolContractSnapshot]:
    document = load_snapshot(path)
    contracts: dict[str, ToolContractSnapshot] = {}
    for name, entry in document["tools"].items():
        if not isinstance(name, str) or not isinstance(entry, dict):
            raise ValueError("tool contract snapshot contains an invalid tool entry")
        contract = entry.get("contract")
        descriptor = entry.get("descriptor")
        if not isinstance(contract, dict) or not isinstance(descriptor, dict):
            raise ValueError(f"snapshot tool {name} must include contract and descriptor objects")
        if descriptor.get("name") != name:
            raise ValueError(f"snapshot descriptor name mismatch for {name}")
        contracts[name] = ToolContractSnapshot(
            title=str(contract["title"]),
            description=str(contract["description"]),
            required_scope=str(contract["required_scope"]),
            project_scoped=bool(contract["project_scoped"]),
            read_only=bool(contract["read_only"]),
            open_world=bool(contract["open_world"]),
            destructive=bool(contract["destructive"]),
            idempotent=bool(contract["idempotent"]),
            privacy_class=str(contract["privacy_class"]),
            success_required=tuple(str(value) for value in contract["success_required"]),
            descriptor=descriptor,
        )
    return contracts
