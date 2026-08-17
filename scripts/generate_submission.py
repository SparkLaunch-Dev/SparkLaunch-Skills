"""Generate the review-facing ChatGPT app submission from runtime contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT.parent / "SparkLaunch" / "backend"
if not BACKEND.is_dir():
    raise SystemExit(
        "SparkLaunch backend not found beside the skills repository. Clone "
        "SparkLaunch and SparkLaunch-Skills as sibling directories before running "
        f"submission generation or the full test suite. Expected: {BACKEND}"
    )
sys.path.insert(0, str(BACKEND))

from mcp_tool_contracts import MCP_TOOL_CONTRACTS  # noqa: E402


REVIEWER_FIXTURE_PATH = ROOT / "submission" / "reviewer-fixture.json"


def _reviewer_project_id() -> int:
    fixture = json.loads(REVIEWER_FIXTURE_PATH.read_text(encoding="utf-8"))
    project_id = fixture.get("project_id")
    if not isinstance(project_id, int) or project_id <= 0:
        raise ValueError("reviewer-fixture.json must contain a positive integer project_id")
    return project_id


def _tool_entry(name, contract):
    if contract.read_only:
        read_reason = contract.description
    else:
        read_reason = (
            f"{contract.description.rstrip('.')} and therefore changes SparkLaunch state."
        )
    if contract.open_world:
        open_reason = "This can change a publicly reachable URL or other public internet state."
    else:
        open_reason = "This operates within private SparkLaunch data and does not change a public or third-party system."
    if contract.destructive:
        destructive_reason = "This can delete or overwrite existing state and requires an exact one-time confirmation before execution."
    else:
        destructive_reason = "This does not delete, revoke, or overwrite an existing user-selected record."
    return {
        "annotations": {
            "readOnlyHint": contract.read_only,
            "openWorldHint": contract.open_world,
            "destructiveHint": contract.destructive,
        },
        "justifications": {
            "read_only_justification": read_reason,
            "open_world_justification": open_reason,
            "destructive_justification": destructive_reason,
        },
    }


def build_submission(reviewer_project_id: int | None = None):
    project_id = reviewer_project_id or _reviewer_project_id()
    return {
        "$schema": "https://developers.openai.com/plugins/schemas/chatgpt-app-submission.v1.json",
        "schema_version": 1,
        "app_info": {
            "display_name": "SparkLaunch",
            "subtitle": "Build and operate a startup",
            "description": "SparkLaunch helps founders select or create a business project, validate an idea, generate brand assets, publish measurable campaigns and landing pages, inspect performance, and operate private CRM workflows.",
            "category": "BUSINESS",
        },
        "tools": {
            name: _tool_entry(name, contract)
            for name, contract in sorted(MCP_TOOL_CONTRACTS.items())
        },
        "test_cases": [
            {
                "description": "List the connected user's accessible projects before scoped work.",
                "user_prompt": "Show me the SparkLaunch projects I can access so I can choose one.",
                "file_attachment_urls": None,
                "tools_triggered": "projects.list",
                "expected_output": "Returns a concise list of accessible projects with ids, names, status, and plan.",
                "expected_output_url": None,
            },
            {
                "description": "Create a private idea-validation workspace in a selected project.",
                "user_prompt": f"Create a validation project for an AI bookkeeping assistant for independent contractors in project {project_id}.",
                "file_attachment_urls": None,
                "tools_triggered": "validation.create_project",
                "expected_output": "Creates one validation record in the selected project and reports its id and status.",
                "expected_output_url": None,
            },
            {
                "description": "Generate saved brand palette options from a concrete brief.",
                "user_prompt": f"Generate a trustworthy, modern color palette for my contractor bookkeeping product in project {project_id}.",
                "file_attachment_urls": None,
                "tools_triggered": "branding.generate_palette",
                "expected_output": "Returns saved palette options with ids, names, hex values, and feeling labels.",
                "expected_output_url": None,
            },
            {
                "description": "List private landing-page projects without requiring seeded records.",
                "user_prompt": f"List the landing-page projects in SparkLaunch project {project_id}.",
                "file_attachment_urls": None,
                "tools_triggered": "landing.list_projects",
                "expected_output": "Returns the landing-page projects visible in the selected SparkLaunch project without changing them.",
                "expected_output_url": None,
            },
            {
                "description": "Search private CRM leads without creating or updating records.",
                "user_prompt": f"Find leads mentioning bookkeeping in project {project_id} and show at most 10.",
                "file_attachment_urls": None,
                "tools_triggered": "crm.search_leads",
                "expected_output": "Returns matching private leads and a result count without modifying CRM data.",
                "expected_output_url": None,
            },
        ],
        "negative_test_cases": [
            {
                "description": "Do not trigger for general startup education with no SparkLaunch operation.",
                "user_prompt": "What is the difference between a seed round and a Series A?",
                "file_attachment_urls": None,
                "tools_triggered": None,
                "expected_output": "Answers generally without invoking SparkLaunch because no connected workspace action was requested.",
                "expected_output_url": None,
            },
            {
                "description": "Do not trigger for unrelated calendar management.",
                "user_prompt": "Move my meeting tomorrow from 2 PM to 3 PM.",
                "file_attachment_urls": None,
                "tools_triggered": None,
                "expected_output": "Does not invoke SparkLaunch because calendar management is outside its supported workflows.",
                "expected_output_url": None,
            },
            {
                "description": "Do not trigger for unsupported financial transactions.",
                "user_prompt": "Transfer $500 from my checking account to savings.",
                "file_attachment_urls": None,
                "tools_triggered": None,
                "expected_output": "Does not invoke SparkLaunch because it cannot access bank accounts or transfer funds.",
                "expected_output_url": None,
            },
        ],
    }


def _serialized_submission(reviewer_project_id: int | None = None) -> str:
    return json.dumps(build_submission(reviewer_project_id), indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail without writing when chatgpt-app-submission.json is stale.",
    )
    parser.add_argument(
        "--reviewer-project-id",
        type=int,
        help="Bind scoped positive prompts to a provisioned disposable reviewer project.",
    )
    args = parser.parse_args(argv)
    if args.reviewer_project_id is not None and args.reviewer_project_id <= 0:
        parser.error("--reviewer-project-id must be a positive integer")
    output = ROOT / "chatgpt-app-submission.json"
    expected = _serialized_submission(args.reviewer_project_id)
    if args.check:
        try:
            current = output.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(f"Submission import is missing or unreadable: {exc}", file=sys.stderr)
            return 1
        if current != expected:
            print(
                "chatgpt-app-submission.json is stale; run scripts/generate_submission.py.",
                file=sys.stderr,
            )
            return 1
        print(
            f"Validated {output.name} against {len(MCP_TOOL_CONTRACTS)} runtime tools."
        )
        return 0
    if args.reviewer_project_id is not None:
        REVIEWER_FIXTURE_PATH.write_text(
            json.dumps(
                {"status": "provisioned", "project_id": args.reviewer_project_id},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    output.write_text(expected, encoding="utf-8")
    print(f"Wrote {output.name} with {len(MCP_TOOL_CONTRACTS)} tools.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
