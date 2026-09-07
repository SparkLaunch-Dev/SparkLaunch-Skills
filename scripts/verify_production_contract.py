"""Read-only, credential-safe production MCP contract verification.

Only initialize, initialized notification and tools/list are sent. No tool is
executed. The short-lived OAuth access token is read from the environment, never
from an argument, file, or printed response. Redirects are not followed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import urllib.error
import urllib.request

try:
    from scripts.build_release_bundles import candidate_identity
    from scripts.tool_contract_snapshot import load_snapshot
except ImportError:
    from build_release_bundles import candidate_identity
    from tool_contract_snapshot import load_snapshot

ORIGIN = "https://sparklaun.ch"
ENDPOINT = ORIGIN + "/api/mcp/"
PROTOCOL = "2025-11-25"
MAX_BYTES = 8 * 1024 * 1024


class VerificationError(ValueError):
    """A safe diagnostic without server-provided text or credentials."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise VerificationError("Production endpoint redirected; verification stopped")


def request_json(
    url: str, *, body: dict | None = None, headers: dict | None = None
) -> tuple[object, dict]:
    request = urllib.request.Request(
        url,
        data=None if body is None else json.dumps(body).encode(),
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            **(headers or {}),
        },
    )
    try:
        with urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect
        ).open(request, timeout=30) as response:
            raw = response.read(MAX_BYTES + 1)
            response_headers = dict(response.headers.items())
            content_type = response.headers.get_content_type()
    except urllib.error.HTTPError as exc:
        raise VerificationError(
            f"Production request failed (HTTP {exc.code})"
        ) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise VerificationError(
            "Production request failed (network/TLS/timeout)"
        ) from None
    if len(raw) > MAX_BYTES:
        raise VerificationError("Production response exceeded the size limit")
    if not raw:
        return None, response_headers
    try:
        if content_type == "text/event-stream":
            messages = []
            for event in raw.decode("utf-8").replace("\r\n", "\n").split("\n\n"):
                data = "\n".join(
                    line[5:].lstrip(" ")
                    for line in event.splitlines()
                    if line.startswith("data:")
                )
                if data:
                    messages.append(json.loads(data))
            expected_id = (body or {}).get("id")
            matched = [
                item
                for item in messages
                if isinstance(item, dict) and item.get("id") == expected_id
            ]
            if len(matched) != 1:
                raise VerificationError(
                    "MCP stream did not contain one matching response"
                )
            return matched[0], response_headers
        return json.loads(raw), response_headers
    except (UnicodeError, json.JSONDecodeError):
        raise VerificationError("Production response was not valid JSON") from None


def required_scopes(snapshot: dict) -> set[str]:
    return {
        scope
        for entry in snapshot["tools"].values()
        for scheme in entry["descriptor"].get("securitySchemes", [])
        if scheme.get("type") == "oauth2"
        for scope in scheme.get("scopes", [])
    }


def compare_descriptors(snapshot: dict, descriptors: list[dict]) -> None:
    if any(
        not isinstance(item, dict) or not isinstance(item.get("name"), str)
        for item in descriptors
    ):
        raise VerificationError("MCP returned an invalid tool descriptor")
    actual = {item["name"]: item for item in descriptors}
    expected = {name: entry["descriptor"] for name, entry in snapshot["tools"].items()}
    if len(actual) != len(descriptors):
        raise VerificationError("MCP returned duplicate tool names")
    if actual.keys() != expected.keys():
        raise VerificationError(
            f"Production tool set differs: {len(expected.keys() - actual.keys())} missing, "
            f"{len(actual.keys() - expected.keys())} unexpected"
        )
    changed = sum(actual[name] != descriptor for name, descriptor in expected.items())
    if changed:
        raise VerificationError(
            f"Production full descriptors differ for {changed} tools"
        )


def verify(*, public_only: bool = False, transport=request_json) -> dict:
    snapshot = load_snapshot()
    expected_scopes = required_scopes(snapshot)
    # Fixed URLs prevent a supplied evidence document from choosing where a
    # release token is transmitted. Discovery redirects also fail closed.
    resource, _ = transport(ORIGIN + "/.well-known/oauth-protected-resource/api/mcp")
    authorization, _ = transport(ORIGIN + "/.well-known/oauth-authorization-server")
    if not isinstance(resource, dict) or resource.get("resource") != ENDPOINT:
        raise VerificationError(
            "Protected-resource identity does not match the canonical endpoint"
        )
    if not isinstance(authorization, dict) or authorization.get("issuer") != ORIGIN:
        raise VerificationError(
            "Authorization-server issuer does not match the canonical origin"
        )
    if resource.get("authorization_servers") != [ORIGIN]:
        raise VerificationError("Protected-resource authorization server differs")
    for metadata in (resource, authorization):
        live_scopes = set(metadata.get("scopes_supported") or [])
        # Identity scopes may be added independently; business scopes must match.
        if live_scopes - {"openid", "email"} != expected_scopes:
            raise VerificationError(
                f"Production OAuth permissions differ: {len(expected_scopes - live_scopes)} missing, "
                f"{len(live_scopes - expected_scopes - {'openid', 'email'})} unexpected business scopes"
            )
    if authorization.get(
        "userinfo_endpoint"
    ) != ORIGIN + "/api/mcp/oauth/userinfo" or not {"openid", "email"} <= set(
        authorization.get("scopes_supported") or []
    ):
        raise VerificationError(
            "Production UserInfo discovery or identity permissions are missing"
        )
    result = {
        "schema_version": 1,
        "candidate": candidate_identity(),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": ENDPOINT,
        "scope_count": len(expected_scopes),
        "business_tool_calls": 0,
        "verification": "public_metadata_only",
    }
    if public_only:
        return result
    token = os.environ.get("SPARKLAUNCH_MCP_ACCESS_TOKEN", "")
    if not token or not re.fullmatch(
        r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", token
    ):
        raise VerificationError(
            "A short-lived OAuth access token is required in SPARKLAUNCH_MCP_ACCESS_TOKEN"
        )
    headers = {"Authorization": "Bearer " + token}

    def rpc(method: str, params: dict | None, request_id: int) -> tuple[dict, dict]:
        payload, response_headers = transport(
            ENDPOINT,
            body={
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params or {},
            },
            headers=headers,
        )
        if (
            not isinstance(payload, dict)
            or payload.get("id") != request_id
            or "error" in payload
            or not isinstance(payload.get("result"), dict)
        ):
            raise VerificationError(
                "MCP request failed or returned an invalid response"
            )
        return payload["result"], response_headers

    initialized, response_headers = rpc(
        "initialize",
        {
            "protocolVersion": PROTOCOL,
            "capabilities": {},
            "clientInfo": {"name": "sparklaunch-release-verifier", "version": "1.0.0"},
        },
        1,
    )
    if initialized.get("serverInfo", {}).get("version") != snapshot["server_version"]:
        raise VerificationError(
            "Production MCP service version differs from the candidate"
        )
    if initialized.get("protocolVersion") != PROTOCOL:
        raise VerificationError("Production MCP protocol negotiation differs")
    headers["MCP-Protocol-Version"] = PROTOCOL
    session = next(
        (
            value
            for key, value in response_headers.items()
            if key.lower() == "mcp-session-id"
        ),
        None,
    )
    if session:
        if not re.fullmatch(r"[\x21-\x7e]{1,256}", session):
            raise VerificationError("MCP returned an invalid session header")
        headers["Mcp-Session-Id"] = session
    transport(
        ENDPOINT,
        body={"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers=headers,
    )
    descriptors, seen = [], set()
    cursor = None
    for page in range(20):
        listed, _ = rpc("tools/list", {"cursor": cursor} if cursor else {}, page + 2)
        if not isinstance(listed.get("tools"), list):
            raise VerificationError("MCP tools/list did not return a tool array")
        descriptors.extend(listed["tools"])
        cursor = listed.get("nextCursor")
        if not cursor:
            break
        if not isinstance(cursor, str) or len(cursor) > 4096 or cursor in seen:
            raise VerificationError(
                "MCP pagination returned an invalid or repeated cursor"
            )
        seen.add(cursor)
    else:
        raise VerificationError("MCP pagination exceeded the page limit")
    compare_descriptors(snapshot, descriptors)
    result.update(
        verification="authenticated_full_contract",
        descriptor_sha256=hashlib.sha256(
            json.dumps(
                sorted(descriptors, key=lambda item: item["name"]),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Verify only discovery metadata, never sufficient for publication",
    )
    args = parser.parse_args()
    try:
        print(json.dumps(verify(public_only=args.public_only), indent=2))
    except VerificationError as exc:
        print(str(exc))
        return 1
    except (ValueError, KeyError, TypeError):
        # Unexpected schema failures never echo the response or token.
        print("Production verification failed: invalid contract/metadata shape")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
