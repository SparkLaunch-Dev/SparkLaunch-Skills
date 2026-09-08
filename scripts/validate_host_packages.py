"""Standalone validation for cross-host packages and the checked-in MCP contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.sync_plugin import HOSTS, ROOT, SKILLS, sync
    from scripts.tool_contract_snapshot import load_snapshot
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    from sync_plugin import HOSTS, ROOT, SKILLS, sync
    from tool_contract_snapshot import load_snapshot


CANONICAL_MCP_URL = "https://sparklaun.ch/api/mcp/"
PACKAGE_ROOTS = {
    "openai": ROOT / "plugins" / "sparklaunch",
    "claude": ROOT / "plugins" / "claude" / "sparklaunch",
    "cursor": ROOT / "plugins" / "cursor" / "sparklaunch",
    "gemini": ROOT / "plugins" / "gemini" / "sparklaunch",
    "muse": ROOT / "plugins" / "muse" / "sparklaunch",
}
HOST_MARKERS = {
    "openai": "Start a new ChatGPT conversation",
    "claude": "Claude Code session",
    "cursor": "Cursor session",
    "gemini": "/mcp auth sparklaunch",
    "muse": "Protected SparkLaunch MCP tools are not activated",
}
RECIPE_REFERENCE = re.compile(r"recipes/([A-Za-z0-9_.-]+\.md)")
EXPECTED_DESCRIPTOR_SCOPE_SETS: dict[str, frozenset[str]] = {
    "founder_close.command": frozenset({"founder_close.read", "founder_close.write"}),
    "founder_close.refresh_room": frozenset(
        {"founder_close.read", "founder_close.write", "sparkroom.read", "sparkroom.write"}
    ),
    "founder_close.room_review": frozenset({"founder_close.read", "sparkroom.read"}),
    "founder_ops.command": frozenset({"founder_ops.read", "founder_ops.write"}),
    "sparkclose.cancel_unsigned": frozenset(
        {"sparkclose.read", "sparkclose.write"}
    ),
    "sparkclose.close_investment": frozenset(
        {"sparkclose.close", "sparkclose.read"}
    ),
    "sparkclose.reconcile_funding": frozenset(
        {"sparkclose.read", "sparkclose.write"}
    ),
    "sparkclose.record_approval": frozenset(
        {"sparkclose.read", "sparkclose.write"}
    ),
    "sparkclose.record_receipt": frozenset(
        {"sparkclose.read", "sparkclose.write"}
    ),
    "sparkclose.retry_updates": frozenset(
        {"sparkclose.read", "sparkclose.write"}
    ),
    "sparkclose.save_scenario": frozenset(
        {"sparkclose.model", "sparkclose.read", "sparkclose.write"}
    ),
    "sparkroom.update": frozenset({"sparkroom.read", "sparkroom.write"}),
    "sparkroom.add_documents": frozenset({"sparkroom.read", "sparkroom.write"}),
    "sparkroom.update_item": frozenset({"sparkroom.read", "sparkroom.write"}),
    "sparkroom.remove_item": frozenset({"sparkroom.read", "sparkroom.write"}),
    "sparkroom.create_share_link": frozenset(
        {"sparkroom.read", "sparkroom.share"}
    ),
    "sparkroom.revoke_share_link": frozenset(
        {"sparkroom.read", "sparkroom.share"}
    ),
}


def _json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"JSON object required: {path.relative_to(ROOT)}")
        return {}
    return value


def _exact_oauth2_scope_set(descriptor: dict[str, Any]) -> frozenset[str] | None:
    schemes = descriptor.get("securitySchemes")
    if not isinstance(schemes, list) or len(schemes) != 1:
        return None
    scheme = schemes[0]
    if not isinstance(scheme, dict) or scheme.get("type") != "oauth2":
        return None
    scopes = scheme.get("scopes")
    if (
        not isinstance(scopes, list)
        or not all(isinstance(scope, str) for scope in scopes)
        or len(scopes) != len(set(scopes))
    ):
        return None
    return frozenset(scopes)


def _expected_descriptor_scope_set(
    name: str, contract: dict[str, Any]
) -> frozenset[str]:
    configured = EXPECTED_DESCRIPTOR_SCOPE_SETS.get(name)
    if configured is not None:
        return configured
    required_scope = contract.get("required_scope")
    if isinstance(required_scope, str):
        return frozenset({required_scope})
    return frozenset()


def _descriptor_scope_set_errors(
    name: str, contract: dict[str, Any], descriptor: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    required_scope = contract.get("required_scope")
    expected_scopes = _expected_descriptor_scope_set(name, contract)
    if not isinstance(required_scope, str) or not required_scope.strip():
        errors.append(f"snapshot contract required_scope must be nonempty: {name}")
    elif required_scope not in expected_scopes:
        errors.append(
            "snapshot expected descriptor scope set does not include required_scope: "
            f"{name} ({required_scope})"
        )
    metadata = descriptor.get("_meta")
    locations = {
        "descriptor": _exact_oauth2_scope_set(descriptor),
        "descriptor _meta": _exact_oauth2_scope_set(
            metadata if isinstance(metadata, dict) else {}
        ),
    }
    errors.extend(
        (
            f"snapshot {location} security scope set mismatch: "
            f"{name} (expected {sorted(expected_scopes)}, "
            f"got {sorted(advertised_scopes) if advertised_scopes else advertised_scopes})"
        )
        for location, advertised_scopes in locations.items()
        if advertised_scopes != expected_scopes
    )
    return errors


def _validate_manifest_contracts(errors: list[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    openai = _json(PACKAGE_ROOTS["openai"] / ".codex-plugin" / "plugin.json", errors)
    versions["openai"] = str(openai.get("version", ""))
    openai_mcp = _json(PACKAGE_ROOTS["openai"] / ".mcp.json", errors)
    if openai_mcp != {
        "sparklaunch": {
            "type": "http",
            "url": CANONICAL_MCP_URL,
            "oauth_resource": CANONICAL_MCP_URL,
        }
    }:
        errors.append("OpenAI MCP config must use the direct Codex server map")

    claude = _json(
        PACKAGE_ROOTS["claude"] / ".claude-plugin" / "plugin.json", errors
    )
    versions["claude"] = str(claude.get("version", ""))
    claude_mcp = _json(PACKAGE_ROOTS["claude"] / ".mcp.json", errors)
    if claude_mcp != {
        "mcpServers": {"sparklaunch": {"type": "http", "url": CANONICAL_MCP_URL}}
    }:
        errors.append("Claude MCP config does not match the native HTTP contract")

    cursor = _json(PACKAGE_ROOTS["cursor"] / "plugin.json", errors)
    versions["cursor"] = str(cursor.get("version", ""))
    cursor_mcp = _json(PACKAGE_ROOTS["cursor"] / "mcp.json", errors)
    cursor_server = ((cursor_mcp.get("mcpServers") or {}).get("sparklaunch") or {})
    if cursor_mcp.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        errors.append("Cursor MCP config must use the Agent Plugins 1.0 schema")
    if cursor_server != {"type": "streamable-http", "url": CANONICAL_MCP_URL}:
        errors.append("Cursor MCP config must use native Streamable HTTP")

    gemini = _json(PACKAGE_ROOTS["gemini"] / "gemini-extension.json", errors)
    versions["gemini"] = str(gemini.get("version", ""))
    gemini_server = ((gemini.get("mcpServers") or {}).get("sparklaunch") or {})
    if gemini_server != {"httpUrl": CANONICAL_MCP_URL}:
        errors.append("Gemini manifest must use httpUrl for Streamable HTTP")
    if gemini.get("contextFileName") != "GEMINI.md":
        errors.append("Gemini manifest must bind GEMINI.md")

    muse = _json(PACKAGE_ROOTS["muse"] / "settings.example.json", errors)
    muse_server = ((muse.get("mcp_servers") or {}).get("sparklaunch") or {})
    if muse.get("schema_version") != 1:
        errors.append("Muse settings example must use schema_version 1")
    if muse_server != {
        "transport": "streamable_http",
        "url": CANONICAL_MCP_URL,
        "headers": {},
        "enabled": False,
        "mode": "optional",
    }:
        errors.append("Muse protected server example must remain disabled and credential-free")
    versions["muse"] = versions["openai"].split("+", 1)[0]
    return versions


def _validate_skills(errors: list[str]) -> None:
    for host in HOSTS:
        root = PACKAGE_ROOTS[host]
        skill_root = root / "skills"
        actual_skills = {path.name for path in skill_root.iterdir() if path.is_dir()}
        if actual_skills != set(SKILLS):
            errors.append(f"{host} package must contain exactly the configured canonical skills")
            continue
        for skill in SKILLS:
            directory = skill_root / skill
            text = (directory / "SKILL.md").read_text(encoding="utf-8")
            if HOST_MARKERS[host] not in text:
                errors.append(f"{host}/{skill} is missing host-specific connection recovery")
            if "only as internal tool-call state" not in text:
                errors.append(f"{host}/{skill} lost the user-output privacy boundary")
            if host != "openai" and (directory / "agents" / "openai.yaml").exists():
                errors.append(f"{host}/{skill} must not package OpenAI-only agent metadata")
            for recipe_name in RECIPE_REFERENCE.findall(text):
                if not (directory / "recipes" / recipe_name).is_file():
                    errors.append(
                        f"{host}/{skill} references missing recipes/{recipe_name}"
                    )
        platform_recipes = skill_root / "sparklaunch-platform" / "recipes"
        if not (platform_recipes / "connect-sparklaunch.md").is_file():
            errors.append(f"{host} package is missing the host-neutral connection recipe")


def _validate_snapshot_and_release(errors: list[str], versions: dict[str, str]) -> None:
    try:
        snapshot = load_snapshot()
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid tool contract snapshot: {exc}")
        return
    tools = snapshot["tools"]
    for name in sorted(set(EXPECTED_DESCRIPTOR_SCOPE_SETS) - set(tools)):
        errors.append(
            f"snapshot is missing tool with an expected descriptor scope set: {name}"
        )
    for name, entry in tools.items():
        descriptor = entry.get("descriptor") or {}
        contract = entry.get("contract") or {}
        if descriptor.get("name") != name:
            errors.append(f"snapshot descriptor name mismatch: {name}")
        if not isinstance(descriptor.get("inputSchema"), dict):
            errors.append(f"snapshot descriptor is missing inputSchema: {name}")
        if not isinstance(descriptor.get("outputSchema"), dict):
            errors.append(f"snapshot descriptor is missing outputSchema: {name}")
        errors.extend(_descriptor_scope_set_errors(name, contract, descriptor))

    registry = _json(ROOT / "server.json", errors)
    if snapshot.get("server_version") != registry.get("version"):
        errors.append("snapshot server version must match the Registry candidate descriptor")
    release = _json(ROOT / "release-state.json", errors)
    generated = release.get("generated_packages") or {}
    registry_state = release.get("mcp_registry") or {}
    runtime_state = release.get("runtime") or {}
    if generated.get("version") != versions.get("openai"):
        errors.append("release state package version does not match OpenAI package")
    if set(generated.get("hosts") or []) != set(HOSTS):
        errors.append("release state must name every generated host package")
    if registry_state.get("candidate_descriptor_version") != registry.get("version"):
        errors.append("release state Registry candidate version is stale")
    if runtime_state.get("contract_snapshot_version") != snapshot.get("server_version"):
        errors.append("release state contract snapshot version is stale")
    base = versions.get("openai", "").split("+", 1)[0]
    for host in ("claude", "cursor", "gemini", "muse"):
        if versions.get(host) != base:
            errors.append(f"{host} package version must match the OpenAI base version")


def validate() -> list[str]:
    errors = sync(write=False)
    versions = _validate_manifest_contracts(errors)
    _validate_skills(errors)
    _validate_snapshot_and_release(errors, versions)
    root_license = (ROOT / "LICENSE").read_bytes()
    for host, package in PACKAGE_ROOTS.items():
        if (package / "LICENSE").read_bytes() != root_license:
            errors.append(f"{host} package license differs from the repository license")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(errors))
        return 1
    print("All five generated host packages and the contract snapshot are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
