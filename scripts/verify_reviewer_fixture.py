"""Preflight an existing disposable reviewer without changing business data.

SPARKLAUNCH_REVIEWER_SECRET_JSON is a process-only credential envelope obtained
through the operator's approved secret store. Never pass credentials as arguments
or save them in evidence. This is not native-host or full release acceptance.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timezone

try:
    from scripts.verify_production_contract import (
        ORIGIN,
        VerificationError,
        request_json,
    )
except ImportError:
    from verify_production_contract import ORIGIN, VerificationError, request_json


def validate_envelope(raw: str, *, today: date) -> dict:
    if not raw or len(raw) > 16384:
        raise VerificationError("A bounded reviewer credential envelope is required")
    try:
        secret = json.loads(raw)
        valid = (
            isinstance(secret, dict)
            and secret.get("environment") == "production"
            and secret.get("status") == "provisioned"
            and secret.get("role") == "reviewer"
            and isinstance(secret.get("tags"), list)
            and {"disposable", "production", "chatgpt-review"}.issubset(secret["tags"])
            and date.fromisoformat(secret["delete_after"]) > today
            and all(
                type(secret.get(key)) is int and secret[key] > 0
                for key in ("user_id", "project_id")
            )
            and all(
                isinstance(secret.get(key), str) and 0 < len(secret[key]) <= 1024
                for key in ("email", "password")
            )
        )
    except (TypeError, ValueError, KeyError):
        valid = False
    if not valid:
        raise VerificationError(
            "Reviewer metadata is invalid, expired or not disposable"
        )
    return secret


def verify(raw: str, *, transport=request_json, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    secret = validate_envelope(raw, today=now.date())
    login, _ = transport(
        ORIGIN + "/api/auth/login",
        body={"email": secret["email"], "password": secret["password"]},
    )
    if not isinstance(login, dict) or not isinstance(login.get("user"), dict):
        raise VerificationError("Reviewer password login did not return an account")
    user = login["user"]
    token = login.get("access_token")
    if (
        type(user.get("id")) is not int
        or user["id"] != secret["user_id"]
        or user.get("is_active") is not True
        or not isinstance(token, str)
        or not 0 < len(token) <= 8192
        or any(character.isspace() for character in token)
        or any(ord(character) < 32 or ord(character) >= 127 for character in token)
    ):
        raise VerificationError(
            "Reviewer identity, active status or login token is invalid"
        )
    projects, _ = transport(
        ORIGIN + "/api/projects/", headers={"Authorization": "Bearer " + token}
    )
    if (
        not isinstance(projects, list)
        or len(projects) != 1
        or not isinstance(projects[0], dict)
        or type(projects[0].get("id")) is not int
        or projects[0]["id"] != secret["project_id"]
        or type(projects[0].get("user_id")) is not int
        or projects[0]["user_id"] != secret["user_id"]
        or projects[0].get("is_archived") is not False
    ):
        raise VerificationError(
            "Reviewer must own exactly its one active disposable project"
        )
    # The list serializer does not calculate effective_plan. Use the read-only
    # detail endpoint; never infer access from a stored marketing/legacy plan.
    project, _ = transport(
        ORIGIN + f"/api/projects/{secret['project_id']}",
        headers={"Authorization": "Bearer " + token},
    )
    if (
        not isinstance(project, dict)
        or type(project.get("id")) is not int
        or project["id"] != secret["project_id"]
        or type(project.get("user_id")) is not int
        or project["user_id"] != secret["user_id"]
        or project.get("is_archived") is not False
    ):
        raise VerificationError("Reviewer project detail identity is invalid")
    checks = {
        "password_login_without_secondary_step": True,
        "active_expected_account": True,
        "one_expected_owned_project": True,
        "analytics_excluded": user.get("analytics_excluded") is True,
        "growth_access": project.get("effective_plan") == "growth",
        "incorporation_entitlement": project.get("incorporate_package_purchased")
        is True,
    }
    return {
        "verification": "reviewer_account_preflight",
        "observed_at": now.isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "blockers": [name for name, passed in checks.items() if not passed],
        "proof_boundary": (
            "Account login and setup only; no OAuth grant, business tool, native host, "
            "fixture-content verification or release-evidence promotion occurred."
        ),
    }


def main() -> int:
    try:
        result = verify(os.environ.pop("SPARKLAUNCH_REVIEWER_SECRET_JSON", ""))
    except VerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return int(bool(result["blockers"]))


if __name__ == "__main__":
    raise SystemExit(main())
