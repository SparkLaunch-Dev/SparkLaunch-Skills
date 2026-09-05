import json

from scripts.generate_submission import MCP_TOOL_CONTRACTS, build_submission
from scripts.sync_plugin import HOSTS, ROOT, SKILLS, sync
from scripts.validate_host_packages import PACKAGE_ROOTS, validate


def test_all_host_packages_are_current_and_valid() -> None:
    assert HOSTS == ("openai", "claude", "cursor", "gemini", "muse")
    assert sync(write=False) == []
    assert validate() == []


def test_checked_in_contract_supports_standalone_submission_generation() -> None:
    assert set(build_submission()["tools"]) == set(MCP_TOOL_CONTRACTS)
    snapshot = json.loads(
        (ROOT / "contracts" / "tools.snapshot.json").read_text(encoding="utf-8")
    )
    assert snapshot["tool_count"] == len(MCP_TOOL_CONTRACTS)
    assert snapshot["server_version"] == "1.6.0"
    assert {
        "crm.prepare_business_card_import",
        "crm.get_business_card_import",
    } <= set(MCP_TOOL_CONTRACTS)
    draft_update = build_submission()["tools"]["incorporation.update_draft"]
    assert draft_update["annotations"]["destructiveHint"] is True
    assert "expected version" in draft_update["justifications"]["destructive_justification"]
    assert "rather than a one-time confirmation" in draft_update["justifications"][
        "destructive_justification"
    ]


def test_business_card_handoff_contract_is_portable_and_truthful() -> None:
    prepare = MCP_TOOL_CONTRACTS["crm.prepare_business_card_import"]
    status = MCP_TOOL_CONTRACTS["crm.get_business_card_import"]
    submission = build_submission()["tools"]

    assert prepare.required_scope == "crm.write"
    assert status.required_scope == "crm.write"
    assert prepare.read_only is False
    assert status.read_only is True
    assert prepare.open_world is False
    assert status.open_world is False
    assert prepare.destructive is False
    assert status.destructive is False
    assert set(prepare.descriptor["inputSchema"]["properties"]) == {
        "idempotency_key",
        "person_id",
        "project_id",
    }
    assert set(status.descriptor["inputSchema"]["properties"]) == {
        "import_intent_id",
        "project_id",
    }
    assert "outputSchema" in prepare.descriptor
    assert "outputSchema" in status.descriptor
    assert submission["crm.prepare_business_card_import"]["annotations"] == {
        "readOnlyHint": False,
        "openWorldHint": False,
        "destructiveHint": False,
    }
    assert submission["crm.get_business_card_import"]["annotations"] == {
        "readOnlyHint": True,
        "openWorldHint": False,
        "destructiveHint": False,
    }


def test_incorporation_recipe_links_resolve_inside_every_skill_package() -> None:
    names = {
        "incorporate-a-single-founder-company.md",
        "incorporate-with-collaborators.md",
        "recover-incorporation-entitlement.md",
        "resume-or-correct-incorporation.md",
        "check-incorporation-status.md",
    }
    for package in PACKAGE_ROOTS.values():
        recipe_root = package / "skills" / "sparklaunch-incorporation" / "recipes"
        assert {path.name for path in recipe_root.glob("*.md")} == names


def test_non_openai_packages_do_not_leak_openai_agent_metadata() -> None:
    for host in HOSTS:
        if host == "openai":
            continue
        for skill in SKILLS:
            assert not (
                PACKAGE_ROOTS[host] / "skills" / skill / "agents" / "openai.yaml"
            ).exists()


def test_muse_package_is_explicitly_fail_closed_for_protected_mcp() -> None:
    settings = json.loads(
        (PACKAGE_ROOTS["muse"] / "settings.example.json").read_text(encoding="utf-8")
    )
    server = settings["mcp_servers"]["sparklaunch"]
    assert server["enabled"] is False
    assert server["headers"] == {}
    for skill_path in (PACKAGE_ROOTS["muse"] / "skills").glob("*/SKILL.md"):
        assert "Protected SparkLaunch MCP tools are not activated" in skill_path.read_text(
            encoding="utf-8"
        )
