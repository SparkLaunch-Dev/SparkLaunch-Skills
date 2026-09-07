from __future__ import annotations

import copy
import json
from datetime import datetime, timezone

import pytest

from scripts import verify_reviewer_fixture as reviewer

NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)
ENVELOPE = {
    "environment": "production",
    "status": "provisioned",
    "role": "reviewer",
    "tags": ["disposable", "production", "chatgpt-review"],
    "delete_after": "2026-09-11",
    "user_id": 7,
    "project_id": 99,
    "email": "synthetic@example.invalid",
    "password": "unit-test-password",
}
LOGIN = {
    "access_token": "unit-test-token",
    "user": {
        "id": 7,
        "is_active": True,
        "analytics_excluded": True,
    },
}
PROJECTS = [
    {
        "id": 99,
        "user_id": 7,
        "is_archived": False,
        "effective_plan": "growth",
        "incorporate_package_purchased": True,
    }
]


def probe(secret=None, login=None, projects=None, detail=None):
    calls = []

    def transport(url, **kwargs):
        calls.append((url, kwargs))
        if len(calls) == 1:
            response = LOGIN if login is None else login
        elif len(calls) == 2:
            response = PROJECTS if projects is None else projects
        else:
            response = PROJECTS[0] if detail is None else detail
        return copy.deepcopy(response), {}

    result = reviewer.verify(
        json.dumps(ENVELOPE if secret is None else secret), transport=transport, now=NOW
    )
    return result, calls


def test_reviewer_preflight_is_bounded_and_does_not_emit_credentials():
    result, calls = probe()
    assert result["blockers"] == []
    assert result["verification"] == "reviewer_account_preflight"
    assert [url for url, _ in calls] == [
        reviewer.ORIGIN + "/api/auth/login",
        reviewer.ORIGIN + "/api/projects/",
        reviewer.ORIGIN + "/api/projects/99",
    ]
    assert calls[1][1] == {"headers": {"Authorization": "Bearer unit-test-token"}}
    assert calls[2][1] == calls[1][1]
    for sensitive in (ENVELOPE["email"], ENVELOPE["password"], LOGIN["access_token"]):
        assert sensitive not in json.dumps(result)


@pytest.mark.parametrize(
    "change",
    [
        {"delete_after": "2026-09-07"},
        {"delete_after": "nonsense"},
        {"environment": "staging"},
        {"status": "disabled"},
        {"role": "admin"},
        {"tags": []},
        {"tags": [None, {}]},
        {"user_id": True},
        {"project_id": 0},
        {"email": ""},
        {"password": None},
    ],
)
def test_bad_envelope_never_attempts_login(change):
    secret = {**ENVELOPE, **change}

    def never(*args, **kwargs):
        pytest.fail("Invalid envelope must not make a network request")

    with pytest.raises(reviewer.VerificationError, match="metadata"):
        reviewer.verify(json.dumps(secret), transport=never, now=NOW)


@pytest.mark.parametrize("raw", ["", "x" * 16385, "[]", "null", "{", "true"])
def test_malformed_envelope_is_safe(raw):
    with pytest.raises(reviewer.VerificationError):
        reviewer.validate_envelope(raw, today=NOW.date())


@pytest.mark.parametrize(
    "login",
    [
        None,
        {},
        {"user": {}},
        {**LOGIN, "access_token": "bad\nheader"},
        {**LOGIN, "user": {**LOGIN["user"], "id": 8}},
        {**LOGIN, "user": {**LOGIN["user"], "is_active": False}},
    ],
)
def test_wrong_login_does_not_fetch_projects(login):
    calls = []

    def transport(*args, **kwargs):
        calls.append(args)
        assert len(calls) == 1
        return login, {}

    with pytest.raises(reviewer.VerificationError):
        reviewer.verify(json.dumps(ENVELOPE), transport=transport, now=NOW)


@pytest.mark.parametrize(
    "projects",
    [
        [],
        PROJECTS * 2,
        {"items": PROJECTS},
        [[PROJECTS[0]]],
        [{**PROJECTS[0], "id": 100}],
        [{**PROJECTS[0], "user_id": 8}],
        [{**PROJECTS[0], "is_archived": True}],
    ],
)
def test_reviewer_project_boundary_is_exact(projects):
    with pytest.raises(reviewer.VerificationError, match="exactly"):
        probe(projects=projects)


def test_setup_gaps_are_not_reported_as_acceptance():
    result, _ = probe(
        login={**LOGIN, "user": {**LOGIN["user"], "analytics_excluded": False}},
        detail={
            **PROJECTS[0],
            "effective_plan": "free",
            "incorporate_package_purchased": False,
        },
    )
    assert result["blockers"] == [
        "analytics_excluded",
        "growth_access",
        "incorporation_entitlement",
    ]
    assert "release-evidence promotion" in result["proof_boundary"]


def test_plan_access_comes_from_detail_not_stored_or_list_plan():
    result, _ = probe(projects=[{**PROJECTS[0], "effective_plan": None}])
    assert result["checks"]["growth_access"] is True
    result, _ = probe(detail={**PROJECTS[0], "plan": "growth", "effective_plan": None})
    assert result["checks"]["growth_access"] is False


@pytest.mark.parametrize(
    "detail",
    [
        [],
        {},
        {**PROJECTS[0], "id": 100},
        {**PROJECTS[0], "id": True},
        {**PROJECTS[0], "user_id": 8},
        {**PROJECTS[0], "is_archived": True},
    ],
)
def test_detail_identity_must_match_verified_project(detail):
    with pytest.raises(reviewer.VerificationError, match="detail identity"):
        probe(detail=detail)


def test_main_removes_envelope_from_process_environment(monkeypatch, capsys):
    monkeypatch.setenv("SPARKLAUNCH_REVIEWER_SECRET_JSON", json.dumps(ENVELOPE))

    def verify(raw):
        assert json.loads(raw) == ENVELOPE
        assert "SPARKLAUNCH_REVIEWER_SECRET_JSON" not in reviewer.os.environ
        return {"blockers": []}

    monkeypatch.setattr(reviewer, "verify", verify)
    assert reviewer.main() == 0
    assert ENVELOPE["password"] not in capsys.readouterr().out
