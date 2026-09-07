import json

import scripts.validate_host_packages as host_package_validator
from scripts.generate_submission import MCP_TOOL_CONTRACTS, build_submission
from scripts.sync_plugin import HOSTS, ROOT, SKILLS, sync
from scripts.validate_host_packages import (
    EXPECTED_DESCRIPTOR_SCOPE_SETS,
    PACKAGE_ROOTS,
    _descriptor_scope_set_errors,
    _exact_oauth2_scope_set,
    _expected_descriptor_scope_set,
    validate,
)


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
    assert snapshot["server_version"] == "1.7.0"
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


def test_compound_descriptor_scope_sets_are_exact() -> None:
    expected_by_tool = {
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
        "sparkroom.add_documents": frozenset(
            {"sparkroom.read", "sparkroom.write"}
        ),
        "sparkroom.update_item": frozenset({"sparkroom.read", "sparkroom.write"}),
        "sparkroom.remove_item": frozenset({"sparkroom.read", "sparkroom.write"}),
        "sparkroom.create_share_link": frozenset(
            {"sparkroom.read", "sparkroom.share"}
        ),
        "sparkroom.revoke_share_link": frozenset(
            {"sparkroom.read", "sparkroom.share"}
        ),
    }
    primary_by_tool = {
        "sparkclose.cancel_unsigned": "sparkclose.write",
        "sparkclose.close_investment": "sparkclose.close",
        "sparkclose.reconcile_funding": "sparkclose.write",
        "sparkclose.record_approval": "sparkclose.write",
        "sparkclose.record_receipt": "sparkclose.write",
        "sparkclose.retry_updates": "sparkclose.write",
        "sparkclose.save_scenario": "sparkclose.write",
        "sparkroom.update": "sparkroom.write",
        "sparkroom.add_documents": "sparkroom.write",
        "sparkroom.update_item": "sparkroom.write",
        "sparkroom.remove_item": "sparkroom.write",
        "sparkroom.create_share_link": "sparkroom.share",
        "sparkroom.revoke_share_link": "sparkroom.share",
    }

    assert EXPECTED_DESCRIPTOR_SCOPE_SETS == expected_by_tool
    for name, expected in expected_by_tool.items():
        primary = primary_by_tool[name]
        contract = {"required_scope": primary}
        schemes = [{"type": "oauth2", "scopes": sorted(expected)}]
        descriptor = {"securitySchemes": schemes, "_meta": {"securitySchemes": schemes}}

        assert _expected_descriptor_scope_set(name, contract) == expected
        assert _exact_oauth2_scope_set(descriptor) == expected
        assert _descriptor_scope_set_errors(name, contract, descriptor) == []

        primary_only = [{"type": "oauth2", "scopes": [primary]}]
        missing_secondary = {
            "securitySchemes": primary_only,
            "_meta": {"securitySchemes": primary_only},
        }
        unexpected_extra_scopes = [*sorted(expected), "projects.read"]
        unexpected_extra = {
            "securitySchemes": [
                {"type": "oauth2", "scopes": unexpected_extra_scopes}
            ],
            "_meta": {
                "securitySchemes": [
                    {"type": "oauth2", "scopes": unexpected_extra_scopes}
                ]
            },
        }
        assert len(
            _descriptor_scope_set_errors(name, contract, missing_secondary)
        ) == 2
        assert len(_descriptor_scope_set_errors(name, contract, unexpected_extra)) == 2

        split_schemes = [
            {"type": "oauth2", "scopes": [scope]} for scope in sorted(expected)
        ]
        split_across_alternatives = {
            "securitySchemes": split_schemes,
            "_meta": {"securitySchemes": split_schemes},
        }
        assert len(
            _descriptor_scope_set_errors(name, contract, split_across_alternatives)
        ) == 2


def test_descriptor_scope_sets_require_a_nonempty_primary_scope_and_membership() -> None:
    empty_schemes = [{"type": "oauth2", "scopes": []}]
    empty_descriptor = {
        "securitySchemes": empty_schemes,
        "_meta": {"securitySchemes": empty_schemes},
    }
    for missing_primary in ({}, {"required_scope": ""}, {"required_scope": "   "}):
        assert any(
            "required_scope must be nonempty" in error
            for error in _descriptor_scope_set_errors(
                "projects.list", missing_primary, empty_descriptor
            )
        )

    expected = EXPECTED_DESCRIPTOR_SCOPE_SETS["sparkroom.update"]
    schemes = [{"type": "oauth2", "scopes": sorted(expected)}]
    descriptor = {
        "securitySchemes": schemes,
        "_meta": {"securitySchemes": schemes},
    }
    errors = _descriptor_scope_set_errors(
        "sparkroom.update",
        {"required_scope": "projects.read"},
        descriptor,
    )
    assert any("does not include required_scope" in error for error in errors)


def test_snapshot_requires_every_compound_scope_override_tool(monkeypatch) -> None:
    snapshot = json.loads(
        (ROOT / "contracts" / "tools.snapshot.json").read_text(encoding="utf-8")
    )
    missing_name = "sparkroom.update"
    del snapshot["tools"][missing_name]
    monkeypatch.setattr(host_package_validator, "load_snapshot", lambda: snapshot)
    errors: list[str] = []

    host_package_validator._validate_snapshot_and_release(
        errors,
        {
            "openai": json.loads(
                (
                    PACKAGE_ROOTS["openai"]
                    / ".codex-plugin"
                    / "plugin.json"
                ).read_text(encoding="utf-8")
            )["version"]
        },
    )

    assert (
        "snapshot is missing tool with an expected descriptor scope set: "
        f"{missing_name}"
    ) in errors


def test_canonical_sharing_guidance_conditions_existing_access() -> None:
    room_skill = (
        ROOT / "src" / "skills" / "sparklaunch-sparkroom" / "SKILL.md"
    ).read_text(encoding="utf-8")
    room_recipe = (
        ROOT / "src" / "recipes" / "prepare-and-share-an-investor-room.md"
    ).read_text(encoding="utf-8")
    cap_skill = (
        ROOT / "src" / "skills" / "sparklaunch-sparkcap" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert (
        "Any existing room links may expose additions\n"
        "according to their current permissions."
    ) in room_skill
    assert (
        "Any existing room links may expose additions\n"
        "   according to their current permissions."
    ) in room_recipe
    assert "Any other links are unaffected; prior\ndownloads, if any" in room_skill
    assert "Any other links are unaffected; prior\n   downloads, if any" in room_recipe
    assert (
        "Any existing SparkCap or SparkRoom shares can reflect saved table and "
        "stakeholder\nchanges immediately."
    ) in cap_skill
    assert "any\nexisting SparkCap links stop working" in cap_skill
    assert "any shared SparkRoom live-cap-table\nitems stop exposing it" in cap_skill

    combined = "\n".join((room_skill, room_recipe, cap_skill))
    for stale in (
        "Adding a document makes it available to existing room viewers.",
        "Existing viewers can access the additions.",
        "Other links remain usable and previously downloaded copies",
        "Other links and old downloads persist.",
        "stops existing shared access",
    ):
        assert stale not in combined


def test_platform_routes_new_workflows_to_packaged_recipe_paths() -> None:
    platform = (
        ROOT / "src" / "skills" / "sparklaunch-platform" / "SKILL.md"
    ).read_text(encoding="utf-8")
    routing = platform.split("## Routing", 1)[1].split("## Connected-App Rules", 1)[0]

    for name in (
        "review-cap-table-and-model-a-raise.md",
        "prepare-and-share-an-investor-room.md",
        "model-and-close-a-safe.md",
    ):
        reference = f"`recipes/{name}`"
        assert routing.count(reference) == 1
        assert platform.count(reference) == 1
        assert routing.count(name) == 1
        assert platform.count(name) == 1
        assert (ROOT / "src" / "recipes" / name).is_file()


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
