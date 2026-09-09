import json
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest

import scripts.build_submission_bundle as submission_bundle
import scripts.export_tool_contract_snapshot as snapshot_exporter
import scripts.sync_plugin as plugin_sync
import scripts.validate_portal_prerequisites as portal_validator
from scripts.tool_contract_snapshot import load_snapshot, load_tool_contracts


def _make_symlink(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symbolic links are unavailable in this environment: {exc}")


def _minimal_bundle_tree(tmp_path: Path, monkeypatch) -> tuple[Path, bytes]:
    root = tmp_path / "repo"
    plugin_root = root / "plugins" / "sparklaunch"
    manifest = plugin_root / ".codex-plugin" / "plugin.json"
    manifest.parent.mkdir(parents=True)
    manifest_content = b'{"version":"1.0.0"}\n'
    manifest.write_bytes(manifest_content)
    monkeypatch.setattr(submission_bundle, "ROOT", root)
    monkeypatch.setattr(submission_bundle, "PLUGIN_ROOT", plugin_root)
    monkeypatch.setattr(
        submission_bundle,
        "expected_files",
        lambda: [SimpleNamespace(target=manifest, content=manifest_content)],
    )
    return plugin_root, manifest_content


@pytest.mark.parametrize("kind", ["file", "directory", "broken"])
def test_bundle_rejects_links_before_creating_archive(tmp_path, monkeypatch, kind):
    plugin_root, _manifest_content = _minimal_bundle_tree(tmp_path, monkeypatch)
    outside = tmp_path / "outside"
    if kind == "directory":
        outside.mkdir()
        link = plugin_root / "linked-directory"
        _make_symlink(link, outside, directory=True)
    else:
        if kind == "file":
            outside.write_text("outside sentinel", encoding="utf-8")
        link = plugin_root / f"{kind}-link"
        _make_symlink(link, outside)
    output = tmp_path / "candidate.zip"

    with pytest.raises(ValueError, match="symbolic links or junctions"):
        submission_bundle.build_bundle(output)

    assert not output.exists()


def test_bundle_rejects_unplanned_files_before_creating_archive(tmp_path, monkeypatch):
    plugin_root, _manifest_content = _minimal_bundle_tree(tmp_path, monkeypatch)
    (plugin_root / "unplanned.txt").write_text("not in generated plan", encoding="utf-8")
    output = tmp_path / "candidate.zip"

    with pytest.raises(ValueError, match="unexpected files"):
        submission_bundle.build_bundle(output)

    assert not output.exists()


def test_bundle_normalizes_text_line_endings(tmp_path, monkeypatch):
    plugin_root, manifest_content = _minimal_bundle_tree(tmp_path, monkeypatch)
    manifest = plugin_root / ".codex-plugin" / "plugin.json"
    crlf_content = manifest_content.replace(b"\n", b"\r\n")
    manifest.write_bytes(crlf_content)
    monkeypatch.setattr(
        submission_bundle,
        "expected_files",
        lambda: [SimpleNamespace(target=manifest, content=manifest_content)],
    )

    output, _digest = submission_bundle.build_bundle(tmp_path / "candidate.zip")

    with ZipFile(output) as archive:
        assert archive.read(".codex-plugin/plugin.json") == manifest_content


def _isolated_sync_roots(tmp_path: Path, monkeypatch) -> Path:
    generated = tmp_path / "generated"
    generated.mkdir()
    for attribute, name in (
        ("SOURCE_SKILLS", "source-skills"),
        ("SOURCE_RECIPES", "source-recipes"),
        ("ADAPTERS", "adapters"),
    ):
        path = tmp_path / name
        path.mkdir()
        monkeypatch.setattr(plugin_sync, attribute, path)
    monkeypatch.setattr(plugin_sync, "ROOT", tmp_path)
    monkeypatch.setattr(plugin_sync, "_generated_roots", lambda: (generated,))
    return generated


def test_sync_write_rejects_generated_link_without_touching_target(tmp_path, monkeypatch):
    generated = _isolated_sync_roots(tmp_path, monkeypatch)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside sentinel", encoding="utf-8")
    link = generated / "unexpected.txt"
    _make_symlink(link, outside)
    planned = False

    def should_not_plan():
        nonlocal planned
        planned = True
        return []

    monkeypatch.setattr(plugin_sync, "expected_files", should_not_plan)

    with pytest.raises(ValueError, match="symbolic links or junctions"):
        plugin_sync.sync(write=True)

    assert planned is False
    assert outside.read_text(encoding="utf-8") == "outside sentinel"
    assert link.is_symlink()


def test_sync_write_removes_only_lexical_in_tree_extra(tmp_path, monkeypatch):
    generated = _isolated_sync_roots(tmp_path, monkeypatch)
    extra = generated / "nested" / "extra.txt"
    extra.parent.mkdir()
    extra.write_text("extra", encoding="utf-8")
    monkeypatch.setattr(plugin_sync, "expected_files", lambda: [])

    assert plugin_sync.sync(write=True) == []

    assert not extra.exists()
    assert generated.exists()


def test_sync_treats_text_line_endings_as_platform_equivalent(tmp_path, monkeypatch):
    generated = _isolated_sync_roots(tmp_path, monkeypatch)
    target = generated / "document.md"
    target.write_bytes(b"one\r\ntwo\r\n")
    expected = plugin_sync.ExpectedFile(
        source=target,
        target=target,
        content=b"one\ntwo\n",
    )
    monkeypatch.setattr(plugin_sync, "expected_files", lambda: [expected])

    assert plugin_sync.sync(write=False) == []


def _write_adapter(tmp_path: Path, monkeypatch, static_file: dict[str, object]) -> None:
    adapters = tmp_path / "adapters"
    root = adapters / "openai"
    (root / "templates").mkdir(parents=True)
    (root / "connection.md").write_text("Connect safely.", encoding="utf-8")
    (root / "templates" / "plugin.json").write_text("{}", encoding="utf-8")
    (root / "adapter.json").write_text(
        json.dumps(
            {
                "host": "openai",
                "package_path": "plugins/sparklaunch",
                "connection_fragment": "connection.md",
                "static_files": [static_file],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(plugin_sync, "ROOT", tmp_path)
    monkeypatch.setattr(plugin_sync, "ADAPTERS", adapters)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source", "../outside.json"),
        ("source", "/outside.json"),
        ("destination", "../../outside.json"),
        ("destination", "/outside.json"),
    ],
)
def test_adapter_static_paths_cannot_escape_roots(tmp_path, monkeypatch, field, value):
    static_file = {
        "source": "templates/plugin.json",
        "destination": "plugin.json",
    }
    static_file[field] = value
    _write_adapter(tmp_path, monkeypatch, static_file)

    with pytest.raises(ValueError, match="portable relative path"):
        plugin_sync._read_adapter("openai")


def test_adapter_static_source_link_cannot_escape_root(tmp_path, monkeypatch):
    _write_adapter(
        tmp_path,
        monkeypatch,
        {"source": "templates/linked.json", "destination": "plugin.json"},
    )
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    _make_symlink(tmp_path / "adapters" / "openai" / "templates" / "linked.json", outside)

    with pytest.raises(ValueError, match="symbolic link or junction"):
        plugin_sync._read_adapter("openai")


def test_adapter_loader_rejects_malformed_json(tmp_path, monkeypatch):
    adapters = tmp_path / "adapters"
    adapter_root = adapters / "openai"
    adapter_root.mkdir(parents=True)
    (adapter_root / "adapter.json").write_text("{", encoding="utf-8")
    monkeypatch.setattr(plugin_sync, "ROOT", tmp_path)
    monkeypatch.setattr(plugin_sync, "ADAPTERS", adapters)

    with pytest.raises(json.JSONDecodeError):
        plugin_sync._read_adapter("openai")


@pytest.mark.parametrize(
    "fragment",
    [
        plugin_sync.CONNECTION_START + "\nmissing end",
        plugin_sync.CONNECTION_END,
        plugin_sync.CONNECTION_START * 2 + plugin_sync.CONNECTION_END,
    ],
)
def test_connection_fragment_rejects_malformed_sentinels(fragment):
    with pytest.raises(ValueError, match="exactly one complete sentinel block"):
        plugin_sync._connection_block(fragment)


def test_generation_keeps_skills_and_recipes_out_of_the_repository_root():
    root = plugin_sync.ROOT
    package_roots = {
        root / "plugins/sparklaunch",
        root / "plugins/claude/sparklaunch",
        root / "plugins/cursor/sparklaunch",
        root / "plugins/gemini/sparklaunch",
        root / "plugins/muse/sparklaunch",
    }
    assert set(plugin_sync._generated_roots()) == package_roots
    catalogs = {
        root / ".claude-plugin" / "marketplace.json",
        root / ".cursor-plugin" / "marketplace.json",
    }
    targets = {item.target for item in plugin_sync.expected_files()}
    assert {
        target for target in targets
        if not any(target.is_relative_to(package) for package in package_roots)
    } == catalogs
    assert not (root / "recipes").exists()
    assert all(not (root / skill).exists() for skill in plugin_sync.SKILLS)


def test_expected_file_plan_rejects_duplicate_targets(monkeypatch, tmp_path):
    duplicate = plugin_sync.ExpectedFile(tmp_path / "source", tmp_path / "target", b"")
    adapter = plugin_sync.Adapter("openai", tmp_path, tmp_path, "", ())
    monkeypatch.setattr(plugin_sync, "_base_package_version", lambda: "1.0.0")
    monkeypatch.setattr(plugin_sync, "_read_adapter", lambda _host: adapter)
    monkeypatch.setattr(
        plugin_sync, "_package_files", lambda *_args, **_kwargs: [duplicate, duplicate]
    )
    monkeypatch.setattr(plugin_sync, "_catalog_files", lambda *_args: [])

    with pytest.raises(ValueError, match="duplicate target files"):
        plugin_sync.expected_files()


@pytest.mark.parametrize(
    "key",
    [
        "clientSecret",
        "api-key",
        "private_key",
        "sessionCookie",
        "reviewer_project_id",
        "instance_id",
        "instance_refresh_id",
        "autoscaling_group",
        "launch_template_id",
        "launch_template_name",
        "launch_template_pins",
        "verified_identity_label",
    ],
)
def test_portal_scan_rejects_nested_sensitive_fields_without_echoing_values(key):
    marker = "do-not-echo-this-value"

    errors = portal_validator._sensitive_evidence_errors({"nested": {key: marker}})

    assert len(errors) == 1
    assert "sensitive field" in errors[0]
    assert marker not in errors[0]


@pytest.mark.parametrize(
    "value",
    [
        "Authorization: " + "Bearer " + "a" * 24,
        "client_" + "secret=" + "b" * 24,
        "-----BEGIN " + "PRIVATE KEY-----",
        "eyJ" + "a" * 10 + "." + "b" * 10 + "." + "c" * 10,
        "sk-" + "d" * 24,
        "https://reviewer:" + "e" * 20 + "@example.com/path",
        "i-" + "0" * 17,
        "lt-" + "0" * 17,
        "example-backend-asg-production",
        "00000000-0000-4000-8000-000000000000",
        "reviewer project " + "99",
    ],
)
def test_portal_scan_rejects_sensitive_values_without_echoing_them(value):
    errors = portal_validator._sensitive_evidence_errors({"note": value})

    assert errors
    assert all(value not in error for error in errors)


def test_portal_schema_rejects_unexpected_operational_fields():
    evidence = {key: {} for key in portal_validator.ALLOWED_KEYS["$"] if key != "schema_version"}
    evidence["schema_version"] = 2
    evidence["reviewer_access"]["private_channel"] = "elsewhere"

    errors = portal_validator._schema_errors(evidence)

    assert errors == [
        "portal prerequisite evidence has unexpected field at $.reviewer_access.private_channel"
    ]


def test_checked_in_portal_evidence_has_no_sensitive_fields():
    evidence = json.loads(portal_validator.EVIDENCE_PATH.read_text(encoding="utf-8"))

    assert portal_validator._schema_errors(evidence) == []
    assert portal_validator._sensitive_evidence_errors(evidence) == []


def test_demo_runbook_keeps_operational_access_details_private():
    runbook = (
        plugin_sync.ROOT / portal_validator.EXPECTED_DEMO_RUNBOOK
    ).read_text(encoding="utf-8").casefold()

    for forbidden in (
        "without mfa",
        "without sms",
        "email confirmation",
        "password login",
        "reviewer project `",
    ):
        assert forbidden not in runbook


def test_portal_validator_cli_reports_validation_failures(monkeypatch, capsys):
    monkeypatch.setattr(portal_validator, "validate", lambda **_kwargs: ["bounded failure"])

    assert portal_validator.main(["--allow-pending"]) == 1
    assert capsys.readouterr().out.strip() == "bounded failure"


def test_portal_repository_file_check_rejects_out_of_tree_files(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    inside = root / "inside.md"
    inside.write_text("inside", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    monkeypatch.setattr(portal_validator, "ROOT", root)

    assert portal_validator._is_regular_repository_file(inside) is True
    assert portal_validator._is_regular_repository_file(outside) is False


def test_portal_repository_file_check_rejects_linked_files(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    linked = root / "linked.md"
    monkeypatch.setattr(portal_validator, "ROOT", root)

    _make_symlink(linked, outside)
    assert portal_validator._is_regular_repository_file(linked) is False


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"schema_version": 2, "server_version": "1", "tool_count": 1, "tools": {}}, "schema_version 1"),
        ({"schema_version": 1, "server_version": "1", "tool_count": 1, "tools": {}}, "non-empty tools"),
        (
            {
                "schema_version": 1,
                "server_version": "1",
                "tool_count": 2,
                "tools": {"one": {}},
            },
            "tool_count does not match",
        ),
    ],
)
def test_snapshot_loader_rejects_invalid_document_shapes(tmp_path, payload, message):
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_snapshot(path)


@pytest.mark.parametrize(
    "entry",
    [
        [],
        {"contract": {}, "descriptor": []},
        {"contract": {}, "descriptor": {"name": "different"}},
    ],
)
def test_snapshot_contract_loader_rejects_invalid_entries(tmp_path, entry):
    path = tmp_path / "snapshot.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "server_version": "1.0.0",
                "tool_count": 1,
                "tools": {"tool.name": entry},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid tool entry|contract and descriptor|name mismatch"):
        load_tool_contracts(path)


def test_snapshot_exporter_fails_cleanly_for_missing_backend(tmp_path, capsys):
    assert snapshot_exporter.main(["--backend", str(tmp_path / "missing")]) == 1
    assert "SparkLaunch backend not found" in capsys.readouterr().err


def test_ci_uses_immutable_actions_and_dependency_versions():
    workflow = (plugin_sync.ROOT / ".github/workflows/validate-host-packages.yml").read_text(
        encoding="utf-8"
    )
    publish = (plugin_sync.ROOT / ".github/workflows/publish-mcp-registry.yml").read_text(
        encoding="utf-8"
    )
    requirements = (plugin_sync.ROOT / "requirements-dev.txt").read_text(encoding="utf-8")

    assert "actions/checkout@v" not in workflow + publish
    assert "actions/setup-python@v" not in workflow
    assert "python -m pip install -r requirements-dev.txt" in workflow
    assert requirements.splitlines() == ["pytest==9.1.1", "PyYAML==6.0.3"]
