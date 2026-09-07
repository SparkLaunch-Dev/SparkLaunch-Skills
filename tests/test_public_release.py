from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts import build_release_bundles as bundles
from scripts import validate_public_release as gate
from scripts import verify_production_contract as live
from scripts import sync_plugin as sync

ROOT = Path(__file__).resolve().parents[1]


def test_release_archives_are_deterministic_self_contained_and_licensed(tmp_path):
    first = bundles.build_releases(tmp_path / "first")
    second = bundles.build_releases(tmp_path / "second")
    assert first == second
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


def test_release_builder_rejects_drift_and_source_output(monkeypatch, tmp_path):
    monkeypatch.setattr(sync, "sync", lambda **kw: ["drift"])
    with pytest.raises(ValueError, match="validation failed"):
        bundles.build_releases(tmp_path)
    monkeypatch.setattr(sync, "sync", lambda **kw: [])
    with pytest.raises(ValueError, match="source/package"):
        bundles.build_releases(ROOT / "src" / "release")


def test_catalogs_are_generated_from_host_roots():
    for host in ("claude", "cursor"):
        document = json.loads((ROOT / f".{host}-plugin/marketplace.json").read_text())
        entry = document["plugins"][0]
        assert entry["source"] == f"./plugins/{host}/sparklaunch"
        assert entry["version"] == sync._base_package_version()
        assert entry["license"] == "Apache-2.0"


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
    observed = "2026-09-07T04:00:00+00:00"
    now = datetime(2026, 9, 7, 5, tzinfo=timezone.utc)
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
                    "status": "pass",
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
            record["checks"] = dict.fromkeys(gate.CHECKS, "pass")
    return document, now


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
    monkeypatch.setenv("SPARKLAUNCH_MCP_ACCESS_TOKEN", "test.access.signature")

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
        assert headers["Authorization"] == "Bearer test.access.signature"
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
    assert result["verification"] == "authenticated_full_contract"
    assert result["business_tool_calls"] == 0
    assert "test.access.signature" not in json.dumps(result)
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
    assert result["verification"] == "public_metadata_only"
    assert len(calls) == 2


def test_live_probe_requires_oauth_and_rejects_duplicate_tools(monkeypatch):
    transport, _ = transport_fixture(monkeypatch)
    monkeypatch.delenv("SPARKLAUNCH_MCP_ACCESS_TOKEN")
    with pytest.raises(live.VerificationError, match="short-lived OAuth"):
        live.verify(transport=transport)
    snapshot = live.load_snapshot()
    descriptors = [entry["descriptor"] for entry in snapshot["tools"].values()]
    with pytest.raises(live.VerificationError, match="duplicate"):
        live.compare_descriptors(snapshot, descriptors + descriptors[:1])


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


@pytest.mark.parametrize("status", ["local_placeholder", "provisioned"])
def test_publication_cli_requires_a_provisioned_reviewer(
    monkeypatch, tmp_path, status, capsys
):
    (tmp_path / "submission").mkdir()
    (tmp_path / "submission/public-release.json").write_text("{}")
    (tmp_path / "submission/reviewer-fixture.json").write_text(
        json.dumps(
            {
                "status": status,
                "project_id": 42,
                "incorporation_data": "synthetic_only",
                "provider_calls_allowed": False,
            }
        )
    )
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "validate", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        gate, "verify", lambda: {"verification": "authenticated_full_contract"}
    )
    monkeypatch.setattr("sys.argv", ["validate_public_release.py", "--live"])
    assert gate.main() == (1 if status == "local_placeholder" else 0)
    output = capsys.readouterr().out
    assert ("provider-disabled reviewer fixture is required" in output) == (
        status == "local_placeholder"
    )


def test_publishing_workflows_require_shared_readiness_and_main():
    for name in ("publish-mcp-registry.yml", "publish-plugin-release.yml"):
        workflow = (ROOT / ".github/workflows" / name).read_text()
        assert "needs: readiness" in workflow
        assert "refs/heads/main" in workflow
        assert "./.github/workflows/release-readiness.yml" in workflow
    workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text()
    assert "validate_portal_prerequisites.py\n" in workflow
    assert "validate_public_release.py --live" in workflow
    assert "--allow-pending" not in workflow
    assert workflow.index("build_submission_bundle.py") < workflow.index(
        "python -m pytest"
    )
