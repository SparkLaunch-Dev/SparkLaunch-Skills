from __future__ import annotations

import base64
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts import build_release_bundles as bundles
from scripts import build_submission_bundle as portal_bundle
from scripts import validate_public_release as gate
from scripts import verify_production_contract as live
from scripts import sync_plugin as sync

ROOT = Path(__file__).resolve().parents[1]


def _unsigned_access_token(payload: dict) -> str:
    def encode(value: dict) -> str:
        raw = json.dumps(value, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return f"{encode({'alg': 'none'})}.{encode(payload)}.signature"


def test_release_archives_are_deterministic_self_contained_and_licensed(tmp_path):
    first = bundles.build_releases(tmp_path / "first")
    second = bundles.build_releases(tmp_path / "second")
    assert first == second
    assert first["schema_version"] == 2
    assert set(first["candidate"]) == {
        "plugin_version",
        "built_at",
        "server_version",
        "tool_count",
        "content_sha256",
    }
    assert first["candidate"]["plugin_version"] == "0.8.1"
    assert first["candidate"]["built_at"] == "2026-09-07T18:56:26Z"
    assert all("+codex" not in asset["file"] for asset in first["assets"])
    assert {asset["host"] for asset in first["assets"]} == set(sync.HOSTS)
    assert len(first["assets"]) == 7
    for asset in first["assets"]:
        raw = (tmp_path / "first" / asset["file"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == asset["sha256"]
        assert raw == (tmp_path / "second" / asset["file"]).read_bytes()
        with ZipFile(tmp_path / "first" / asset["file"]) as archive:
            names = archive.namelist()
            assert len(names) == len(set(names))
            assert bundles.MANIFESTS[asset["host"]] in names
            if asset["host"] in {"openai", "claude", "cursor"}:
                manifest = json.loads(archive.read(bundles.MANIFESTS[asset["host"]]))
                assert manifest["license"] == "Apache-2.0"
            assert all(
                not name.startswith("/")
                and ".." not in Path(name).parts
                and "\\" not in name
                for name in names
            )
            for name in ("LICENSE", "NOTICE"):
                assert archive.read(name) == sync._normalized_content(
                    (ROOT / name).read_bytes()
                )
    assert {
        asset["file"] for asset in first["assets"] if asset["host"] == "gemini"
    } == {
        "darwin.sparklaunch.zip",
        "linux.sparklaunch.zip",
        "win32.sparklaunch.zip",
    }
    assert json.loads(
        (tmp_path / "first/release-manifest.json").read_text(encoding="utf-8")
    ) == first
    checksum_lines = (tmp_path / "first/SHA256SUMS").read_text(
        encoding="utf-8"
    ).splitlines()
    assert checksum_lines == [
        f"{asset['sha256']}  {asset['file']}" for asset in first["assets"]
    ]


def test_release_builder_rejects_drift_and_source_output(monkeypatch, tmp_path):
    monkeypatch.setattr(sync, "sync", lambda **kw: ["drift"])
    with pytest.raises(ValueError, match="validation failed"):
        bundles.build_releases(tmp_path)
    monkeypatch.setattr(sync, "sync", lambda **kw: [])
    with pytest.raises(ValueError, match="source/package"):
        bundles.build_releases(ROOT / "src" / "release")


@pytest.mark.parametrize(
    "built_at",
    ("2026-09-07 00:00:00", "2026-9-7T1:2:3Z"),
)
def test_release_identity_rejects_noncanonical_candidate_build_time(
    monkeypatch, tmp_path, built_at
):
    release_state = tmp_path / "release-state.json"
    release_state.write_text(
        json.dumps(
            {
                "generated_packages": {
                    "version": "0.8.1",
                    "built_at": built_at,
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(bundles, "RELEASE_STATE_PATH", release_state)

    with pytest.raises(ValueError, match="canonical UTC timestamp"):
        bundles.candidate_identity()


def test_release_identity_rejects_release_state_version_drift(monkeypatch, tmp_path):
    release_state = tmp_path / "release-state.json"
    release_state.write_text(
        json.dumps(
            {
                "generated_packages": {
                    "version": "0.8.0",
                    "built_at": "2026-09-07T18:56:26Z",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(bundles, "RELEASE_STATE_PATH", release_state)

    with pytest.raises(ValueError, match="must match the plugin manifest"):
        bundles.candidate_identity()


def test_portal_bundle_rejects_non_numeric_three_part_version(monkeypatch, tmp_path):
    plugin_root = tmp_path / "plugin"
    manifest = plugin_root / ".codex-plugin/plugin.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps({"version": "0.8.1+codex.20260907000000"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(portal_bundle, "PLUGIN_ROOT", plugin_root)

    with pytest.raises(ValueError, match="numeric major.minor.patch"):
        portal_bundle._plugin_version()


def test_portal_bundle_rejects_whitespace_around_version(monkeypatch, tmp_path):
    plugin_root = tmp_path / "plugin"
    manifest = plugin_root / ".codex-plugin/plugin.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"version": " 0.8.1 "}), encoding="utf-8")
    monkeypatch.setattr(portal_bundle, "PLUGIN_ROOT", plugin_root)

    with pytest.raises(ValueError, match="numeric major.minor.patch"):
        portal_bundle._plugin_version()


def test_catalogs_are_generated_from_host_roots():
    assert sync._base_package_version() == "0.8.1"
    for host in ("claude", "cursor"):
        document = json.loads((ROOT / f".{host}-plugin/marketplace.json").read_text())
        entry = document["plugins"][0]
        assert entry["source"] == f"./plugins/{host}/sparklaunch"
        assert entry["version"] == sync._base_package_version()
        assert entry["license"] == "Apache-2.0"


@pytest.mark.parametrize(
    "version",
    (
        "0.8",
        "01.8.1",
        "1\u0662.3.4",
        "0.8.1-rc.1",
        "0.8.1+codex.20260907000000",
        " 0.8.1 ",
    ),
)
def test_package_generation_rejects_non_numeric_three_part_versions(
    monkeypatch, version
):
    manifest_path = (
        sync.ADAPTERS / "openai" / "templates" / ".codex-plugin" / "plugin.json"
    ).resolve()
    original_read_text = Path.read_text

    def read_text(path, *args, **kwargs):
        text = original_read_text(path, *args, **kwargs)
        if path.resolve() == manifest_path:
            manifest = json.loads(text)
            manifest["version"] = version
            return json.dumps(manifest)
        return text

    monkeypatch.setattr(Path, "read_text", read_text)
    with pytest.raises(ValueError, match="numeric major.minor.patch"):
        sync._base_package_version()


def pending_document():
    return json.loads((ROOT / "submission/public-release.json").read_text())


def test_pending_source_validity_is_not_release_acceptance():
    document = pending_document()
    assert gate.validate(document, allow_pending=True) == []
    errors = gate.validate(document)
    assert len(errors) == 6
    assert all("pending" in error for error in errors)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda doc: doc["candidate"].update(content_sha256="0" * 64),
        lambda doc: doc["hosts"]["claude"].update(status="verified"),
        lambda doc: doc["hosts"]["cursor"].update(client_version="pretend"),
        lambda doc: doc["hosts"]["muse"]["checks"].update(oauth_connect="pass"),
        lambda doc: doc["hosts"].pop("gemini"),
        lambda doc: doc["policy_review"].update(status="verified"),
    ],
)
def test_false_and_mismatched_claims_fail_even_in_pending_mode(mutation):
    document = pending_document()
    mutation(document)
    assert gate.validate(document, allow_pending=True)


def verified_document(monkeypatch, tmp_path):
    document = pending_document()
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    identity = document["candidate"]
    monkeypatch.setattr(gate, "candidate_identity", lambda: identity)
    observed = "2026-09-07T20:00:00+00:00"
    now = datetime(2026, 9, 7, 21, tzinfo=timezone.utc)
    (tmp_path / "submission/evidence").mkdir(parents=True)
    records = {"policy": document["policy_review"], **document["hosts"]}
    for label, record in records.items():
        fields = (
            ("sparkclose_classification", "platform_guidelines", "reviewer_access")
            if label == "policy"
            else gate.CHECKS
        )
        report = {
            "candidate": identity,
            "observed_at": observed,
            "surface": label,
            "results": {
                check: {
                    "status": (
                        "not_applicable"
                        if check in gate.NOT_APPLICABLE_CHECKS.get(label, frozenset())
                        else "pass"
                    ),
                    "observation": "Synthetic unit-test fixture; not real acceptance evidence.",
                }
                for check in fields
            },
        }
        raw = json.dumps(report).encode()
        path = f"submission/evidence/{label}.json"
        (tmp_path / path).write_bytes(raw)
        record.update(
            status="verified",
            observed_at=observed,
            evidence_path=path,
            evidence_sha256=hashlib.sha256(raw).hexdigest(),
        )
        record["reviewer" if label == "policy" else "client_version"] = "unit-test-only"
        if label != "policy":
            not_applicable = gate.NOT_APPLICABLE_CHECKS.get(label, frozenset())
            record["checks"] = {
                check: "not_applicable" if check in not_applicable else "pass"
                for check in gate.CHECKS
            }
    return document, now


@pytest.mark.parametrize(
    "mutation",
    (
        lambda doc: doc["hosts"]["muse"]["checks"].update(oauth_connect="pass"),
        lambda doc: doc["hosts"]["muse"]["checks"].update(install="not_applicable"),
        lambda doc: doc["hosts"]["openai"]["checks"].update(
            oauth_connect="not_applicable"
        ),
        lambda doc: doc["hosts"]["muse"].update(not_applicable_reason=""),
    ),
)
def test_not_applicable_checks_are_narrowly_scoped_to_muse(mutation):
    document = pending_document()
    mutation(document)

    assert gate.validate(document, allow_pending=True)


def test_verified_evidence_requires_fresh_bound_complete_reports(monkeypatch, tmp_path):
    document, now = verified_document(monkeypatch, tmp_path)
    assert gate.validate(document, now=now) == []
    (tmp_path / "submission/evidence/claude.json").write_text("{}")
    assert any(
        "claude: evidence" in error for error in gate.validate(document, now=now)
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("observed_at", "2020-01-01T00:00:00Z"),
        ("observed_at", "2099-01-01T00:00:00Z"),
        ("observed_at", "2026-09-07T04:00:00"),
        ("evidence_path", "../outside.json"),
        ("evidence_path", "contracts/tools.snapshot.json"),
        ("evidence_sha256", "0" * 64),
        ("client_version", ""),
    ],
)
def test_verified_host_evidence_rejects_staleness_traversal_and_tampering(
    monkeypatch, tmp_path, field, value
):
    document, now = verified_document(monkeypatch, tmp_path)
    document["hosts"]["claude"][field] = value
    assert gate.validate(document, now=now)


def transport_fixture(monkeypatch, *, mismatch=None, paginate=False):
    snapshot = live.load_snapshot()
    scopes = sorted(live.required_scopes(snapshot))
    descriptors = [
        copy.deepcopy(entry["descriptor"]) for entry in snapshot["tools"].values()
    ]
    if mismatch == "schema":
        descriptors[0]["inputSchema"]["description"] = "changed"
    if mismatch == "scope":
        scopes.pop()
    calls = []
    token = _unsigned_access_token(
        {"exp": int(datetime.now(timezone.utc).timestamp()) + 15 * 60}
    )
    monkeypatch.setenv("SPARKLAUNCH_MCP_ACCESS_TOKEN", token)

    def transport(url, *, body=None, headers=None):
        calls.append((url, body))
        if url.endswith("oauth-authorization-server"):
            return {
                "issuer": live.ORIGIN,
                "scopes_supported": scopes + ["openid", "email"],
                "userinfo_endpoint": live.ORIGIN + "/api/mcp/oauth/userinfo",
            }, {}
        if "oauth-protected-resource" in url:
            return {
                "resource": live.ENDPOINT,
                "authorization_servers": [live.ORIGIN],
                "scopes_supported": scopes,
            }, {}
        assert headers["Authorization"] == "Bearer " + token
        method = body["method"]
        assert method in {"initialize", "notifications/initialized", "tools/list"}
        if method == "notifications/initialized":
            return None, {}
        if method == "initialize":
            result = {
                "serverInfo": {"version": snapshot["server_version"]},
                "protocolVersion": live.PROTOCOL,
            }
        else:
            result = {"tools": descriptors}
            if paginate:
                result = (
                    {"tools": descriptors[:50], "nextCursor": "next"}
                    if not body["params"]
                    else {"tools": descriptors[50:]}
                )
        return {"id": body["id"], "result": result}, {}

    return transport, calls


@pytest.mark.parametrize("paginate", [False, True])
def test_live_probe_only_reads_and_compares_the_full_contract(monkeypatch, paginate):
    transport, calls = transport_fixture(monkeypatch, paginate=paginate)
    result = live.verify(transport=transport)
    assert result["schema_version"] == 2
    assert set(result["candidate"]) == {
        "plugin_version",
        "built_at",
        "server_version",
        "tool_count",
        "content_sha256",
    }
    assert result["verification"] == "authenticated_full_contract"
    assert result["business_tool_calls"] == 0
    assert os.environ["SPARKLAUNCH_MCP_ACCESS_TOKEN"] not in json.dumps(result)
    assert len(result["descriptor_sha256"]) == 64
    assert len(calls) == (6 if paginate else 5)


@pytest.mark.parametrize("mismatch", ["scope", "schema"])
def test_live_probe_rejects_scope_or_full_schema_mismatch(monkeypatch, mismatch):
    transport, _ = transport_fixture(monkeypatch, mismatch=mismatch)
    with pytest.raises(live.VerificationError, match="differ"):
        live.verify(transport=transport)


def test_public_probe_never_claims_authenticated_acceptance(monkeypatch):
    transport, calls = transport_fixture(monkeypatch)
    result = live.verify(public_only=True, transport=transport)
    assert result["schema_version"] == 2
    assert result["candidate"]["built_at"] == "2026-09-07T18:56:26Z"
    assert result["verification"] == "public_metadata_only"
    assert len(calls) == 2


def test_live_probe_requires_oauth_and_rejects_duplicate_tools(monkeypatch):
    transport, _ = transport_fixture(monkeypatch)
    monkeypatch.delenv("SPARKLAUNCH_MCP_ACCESS_TOKEN")
    with pytest.raises(live.VerificationError, match="short-lived, unexpired OAuth"):
        live.verify(transport=transport)
    snapshot = live.load_snapshot()
    descriptors = [entry["descriptor"] for entry in snapshot["tools"].values()]
    with pytest.raises(live.VerificationError, match="duplicate"):
        live.compare_descriptors(snapshot, descriptors + descriptors[:1])


@pytest.mark.parametrize(
    "token",
    (
        "test.access.signature",
        _unsigned_access_token({}),
        _unsigned_access_token({"exp": "4102444800"}),
        _unsigned_access_token({"exp": float("nan")}),
        _unsigned_access_token({"exp": 10**1000}),
    ),
)
def test_live_probe_rejects_malformed_access_token_expiry(token):
    now = datetime(2026, 9, 7, tzinfo=timezone.utc)
    with pytest.raises(live.VerificationError, match="short-lived, unexpired"):
        live._validate_access_token(token, now=now)


@pytest.mark.parametrize("seconds", (-1, 31 * 60 + 1))
def test_live_probe_rejects_expired_or_long_lived_access_token(seconds):
    now = datetime(2026, 9, 7, tzinfo=timezone.utc)
    token = _unsigned_access_token({"exp": int(now.timestamp()) + seconds})

    with pytest.raises(live.VerificationError, match="short-lived, unexpired"):
        live._validate_access_token(token, now=now)


def test_live_probe_accepts_backend_length_access_token():
    now = datetime(2026, 9, 7, tzinfo=timezone.utc)
    token = _unsigned_access_token({"exp": int(now.timestamp()) + 30 * 60})

    live._validate_access_token(token, now=now)


def test_live_probe_does_not_follow_redirects():
    with pytest.raises(live.VerificationError, match="redirected"):
        live.NoRedirect().redirect_request(
            None, None, 302, None, None, "https://attacker.invalid"
        )


def test_native_evidence_cannot_predate_the_candidate_build():
    now = datetime(2026, 9, 7, 5, tzinfo=timezone.utc)
    build = datetime(2026, 9, 7, tzinfo=timezone.utc)
    assert not gate._fresh("2026-09-06T23:59:59Z", now, build)
    assert gate._fresh("2026-09-07T04:00:00Z", now, build)


def test_release_version_cannot_supply_an_output_path(monkeypatch, tmp_path):
    monkeypatch.setattr(sync, "sync", lambda **kw: [])
    monkeypatch.setattr(bundles, "candidate_identity", lambda: {})
    monkeypatch.setattr(sync, "_base_package_version", lambda: "../../source")
    with pytest.raises(ValueError, match="major.minor.patch"):
        bundles.build_releases(tmp_path)


@pytest.mark.parametrize(
    ("status", "extra_field", "should_fail"),
    [
        ("local_placeholder", False, True),
        ("provisioned", False, False),
        ("provisioned", True, True),
    ],
)
def test_publication_cli_requires_a_provisioned_reviewer(
    monkeypatch, tmp_path, status, extra_field, should_fail, capsys
):
    (tmp_path / "submission").mkdir()
    (tmp_path / "submission/public-release.json").write_text("{}")
    fixture = {
        "status": status,
        "project_id": 42,
        "incorporation_data": "synthetic_only",
        "provider_calls_allowed": False,
    }
    if extra_field:
        fixture["unexpected"] = "value"
    (tmp_path / "submission/reviewer-fixture.json").write_text(json.dumps(fixture))
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "validate", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        gate, "verify", lambda: {"verification": "authenticated_full_contract"}
    )
    monkeypatch.setattr("sys.argv", ["validate_public_release.py", "--live"])
    assert gate.main() == int(should_fail)
    output = capsys.readouterr().out
    assert ("provider-disabled reviewer fixture is required" in output) == should_fail


def test_publishing_workflows_require_shared_readiness_and_main():
    for name in ("publish-mcp-registry.yml", "publish-plugin-release.yml"):
        workflow = (ROOT / ".github/workflows" / name).read_text()
        assert "needs: readiness" in workflow
        assert "refs/heads/main" in workflow
        assert "./.github/workflows/release-readiness.yml" in workflow
        assert "validate_portal_prerequisites.py" in workflow
        assert "validate_public_release.py --live" in workflow
        assert "--allow-pending" not in workflow
        assert workflow.index("environment: public-release") < workflow.index(
            "validate_public_release.py --live"
        )
    plugin_workflow = (
        ROOT / ".github/workflows/publish-plugin-release.yml"
    ).read_text()
    assert 'tag="${version}"' in plugin_workflow
    assert "plugins-v${version}" not in plugin_workflow
    assert "Publish immutable" not in plugin_workflow
    assert 'gh api --method POST "repos/${GITHUB_REPOSITORY}/git/refs"' in plugin_workflow
    assert '-f ref="refs/tags/${tag}" -f sha="$GITHUB_SHA"' in plugin_workflow
    assert 'gh release create "$tag" --verify-tag' in plugin_workflow
    assert "could not be created at the reviewed commit" in plugin_workflow
    assert "--notes-file submission/github-release-notes.md" in plugin_workflow
    github_notes = (ROOT / "submission/github-release-notes.md").read_text()
    assert "Apache-2.0" in github_notes
    assert "Release Candidate" not in github_notes
    assert "has not been deployed" not in github_notes
    assert "remain unverified" not in github_notes
    assert "skills-only package" in github_notes
    assert "does not claim protected-tool parity for Muse" in github_notes
    workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text()
    assert "validate_portal_prerequisites.py\n" in workflow
    assert "validate_public_release.py --live" in workflow
    assert "--allow-pending" not in workflow
    assert workflow.index("build_submission_bundle.py") < workflow.index(
        "python -m pytest"
    )
