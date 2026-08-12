"""Validate the canonical skills and ChatGPT/Codex submission package."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

try:
    from scripts.build_submission_bundle import build_bundle
    from scripts.sync_plugin import ROOT, SKILLS, sync
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    from build_submission_bundle import build_bundle
    from sync_plugin import ROOT, SKILLS, sync


FORBIDDEN = {
    "API-key guidance": re.compile(r"\b(?:MCP\s+)?API[- ]key\b", re.IGNORECASE),
    "query-token URL": re.compile(r"\?token=", re.IGNORECASE),
    "legacy project header": re.compile(r"X-SparkLaunch-Project-Id", re.IGNORECASE),
    "raw image field": re.compile(r"\b(?:image_base64|data_url)\b"),
}

CANONICAL_MCP_URL = "https://sparklaun.ch/api/mcp/"
EXPECTED_ANNOTATIONS = {"readOnlyHint", "openWorldHint", "destructiveHint"}
EXPECTED_JUSTIFICATIONS = {
    "read_only_justification",
    "open_world_justification",
    "destructive_justification",
}
EXPECTED_PLUGIN_INTERFACE = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "defaultPrompt",
    "brandColor",
    "composerIcon",
    "logo",
    "screenshots",
}


def _load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return None


def validate() -> list[str]:
    errors = sync(write=False)
    text_roots = [ROOT / skill for skill in SKILLS] + [
        ROOT / "recipes",
        ROOT / "plugins" / "sparklaunch",
        ROOT / "submission",
    ]
    text_files = {
        path
        for root in text_roots
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json"}
    }
    for path in sorted(text_files):
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM is not allowed: {path.relative_to(ROOT)}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"not UTF-8: {path.relative_to(ROOT)}: {exc}")
            continue
        for label, pattern in FORBIDDEN.items():
            if pattern.search(text):
                errors.append(f"{label} remains in {path.relative_to(ROOT)}")

    for skill in SKILLS:
        skill_path = ROOT / skill / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not match:
            errors.append(f"invalid frontmatter: {skill}/SKILL.md")
            continue
        data = yaml.safe_load(match.group(1))
        if set(data or {}) != {"name", "description"} or data.get("name") != skill:
            errors.append(f"frontmatter must contain only matching name and description: {skill}")
        agent = yaml.safe_load((ROOT / skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        interface = ((agent or {}).get("interface") or {})
        prompt = interface.get("default_prompt", "")
        if f"${skill}" not in prompt:
            errors.append(f"default prompt must mention ${skill}")
        dependencies = ((agent or {}).get("dependencies") or {}).get("tools") or []
        if len(dependencies) != 1:
            errors.append(f"skill must declare exactly one MCP dependency: {skill}")
        else:
            dependency = dependencies[0]
            expected_dependency = {
                "type": "mcp",
                "value": "sparklaunch",
                "transport": "streamable_http",
                "url": CANONICAL_MCP_URL,
            }
            for key, value in expected_dependency.items():
                if dependency.get(key) != value:
                    errors.append(f"invalid {key} MCP dependency for {skill}")
            if not str(dependency.get("description", "")).strip():
                errors.append(f"MCP dependency description is required: {skill}")
            if set(dependency) != {*expected_dependency, "description"}:
                errors.append(f"unexpected MCP dependency fields: {skill}")
        if ((agent or {}).get("policy") or {}).get("allow_implicit_invocation") is not True:
            errors.append(f"implicit invocation must be enabled: {skill}")
        for icon_key in ("icon_small", "icon_large"):
            icon = str(interface.get(icon_key, ""))
            if not icon.startswith("./") or not (ROOT / skill / icon[2:]).is_file():
                errors.append(f"missing {icon_key} asset: {skill}")

    plugin = ROOT / "plugins" / "sparklaunch"
    manifest = _load_json(plugin / ".codex-plugin" / "plugin.json", errors)
    if manifest:
        for key in ("name", "version", "description", "homepage", "repository", "license"):
            if not str(manifest.get(key, "")).strip():
                errors.append(f"plugin manifest missing {key}")
        author = manifest.get("author") or {}
        for key in ("name", "email", "url"):
            if not str(author.get(key, "")).strip():
                errors.append(f"plugin author missing {key}")
        interface = manifest.get("interface") or {}
        missing_interface = EXPECTED_PLUGIN_INTERFACE.difference(interface)
        if missing_interface:
            errors.append(
                "plugin interface missing fields: " + ", ".join(sorted(missing_interface))
            )
        for key in ("privacyPolicyURL", "termsOfServiceURL"):
            if not str(interface.get(key, "")).startswith("https://"):
                errors.append(f"plugin interface missing secure {key}")
        prompts = interface.get("defaultPrompt") or []
        if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
            errors.append("plugin defaultPrompt must contain one to three prompts")
        elif any(not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 128 for prompt in prompts):
            errors.append("plugin defaultPrompt entries must be non-empty and at most 128 characters")
        for key in ("composerIcon", "logo"):
            relative = str(interface.get(key, ""))
            if not relative.startswith("./") or not (plugin / relative[2:]).is_file():
                errors.append(f"plugin {key} must reference an included asset")
        if "TODO" in json.dumps(manifest):
            errors.append("plugin manifest contains a TODO placeholder")
        if manifest.get("mcpServers") != "./.mcp.json":
            errors.append("plugin manifest must reference ./.mcp.json")
    mcp = _load_json(plugin / ".mcp.json", errors)
    endpoint = (((mcp or {}).get("mcpServers") or {}).get("sparklaunch") or {}).get("url")
    if endpoint != CANONICAL_MCP_URL:
        errors.append("plugin MCP mapping must use the canonical production endpoint")
    if set((mcp or {}).get("mcpServers") or {}) != {"sparklaunch"}:
        errors.append("plugin MCP mapping must contain only the sparklaunch server")

    marketplace = _load_json(ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    entries = (marketplace or {}).get("plugins") or []
    matching_entries = [entry for entry in entries if entry.get("name") == "sparklaunch"]
    if len(matching_entries) != 1:
        errors.append("marketplace must contain exactly one sparklaunch plugin entry")
    else:
        entry = matching_entries[0]
        if entry.get("source") != {"source": "local", "path": "./plugins/sparklaunch"}:
            errors.append("marketplace sparklaunch source is invalid")
        if entry.get("policy") != {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        }:
            errors.append("marketplace sparklaunch policy is invalid")
        if entry.get("category") != "Productivity":
            errors.append("marketplace sparklaunch category is invalid")

    submission = _load_json(ROOT / "chatgpt-app-submission.json", errors)
    if submission:
        if submission.get("schema_version") != 1:
            errors.append("submission schema_version must be 1")
        if len(submission.get("test_cases") or []) != 5:
            errors.append("submission must contain exactly five positive test cases")
        if len(submission.get("negative_test_cases") or []) != 3:
            errors.append("submission must contain exactly three negative test cases")
        if len(submission.get("tools") or {}) != 46:
            errors.append("submission must cover all 46 MCP tools")
        for tool_name, tool in (submission.get("tools") or {}).items():
            annotations = tool.get("annotations") or {}
            if set(annotations) != EXPECTED_ANNOTATIONS or not all(
                isinstance(value, bool) for value in annotations.values()
            ):
                errors.append(f"submission annotations are incomplete: {tool_name}")
            justifications = tool.get("justifications") or {}
            if set(justifications) != EXPECTED_JUSTIFICATIONS or any(
                not isinstance(value, str) or not value.strip()
                for value in justifications.values()
            ):
                errors.append(f"submission justifications are incomplete: {tool_name}")
        for case in submission.get("test_cases") or []:
            if case.get("tools_triggered") not in (submission.get("tools") or {}):
                errors.append("positive submission case references an unknown tool")
        for case in submission.get("negative_test_cases") or []:
            if case.get("tools_triggered") is not None:
                errors.append("negative submission cases must not trigger a tool")

    evaluations = _load_json(ROOT / "evals" / "skill-trigger-cases.json", errors)
    cases = (evaluations or {}).get("cases") or []
    if (evaluations or {}).get("schema_version") != 1:
        errors.append("skill trigger evaluations schema_version must be 1")
    case_ids: set[str] = set()
    positive_counts = {skill: 0 for skill in SKILLS}
    negative_count = 0
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            errors.append("skill trigger evaluation ids must be unique non-empty strings")
        else:
            case_ids.add(case_id)
        if not str(case.get("prompt", "")).strip() or not str(case.get("rationale", "")).strip():
            errors.append(f"skill trigger evaluation is incomplete: {case_id}")
        expected = case.get("expected_skills")
        if not isinstance(expected, list) or any(skill not in SKILLS for skill in expected):
            errors.append(f"skill trigger evaluation has unknown expected skill: {case_id}")
            continue
        if not expected:
            negative_count += 1
        for skill in set(expected):
            positive_counts[skill] += 1
    for skill, count in positive_counts.items():
        if count < 2:
            errors.append(f"skill trigger evaluations need two positive cases: {skill}")
    if negative_count < len(SKILLS):
        errors.append("skill trigger evaluations need at least one negative case per skill")

    release_notes_path = ROOT / "submission" / "release-notes.md"
    reviewer_path = ROOT / "submission" / "reviewer-instructions.md"
    reviewer_fixture = _load_json(
        ROOT / "submission" / "reviewer-fixture.json", errors
    )
    if reviewer_fixture:
        fixture_status = reviewer_fixture.get("status")
        fixture_project_id = reviewer_fixture.get("project_id")
        if fixture_status not in {"local_placeholder", "provisioned"}:
            errors.append("reviewer fixture status must be local_placeholder or provisioned")
        if not isinstance(fixture_project_id, int) or fixture_project_id <= 0:
            errors.append("reviewer fixture project_id must be a positive integer")
        else:
            scoped_cases = [
                case
                for case in (submission or {}).get("test_cases", [])
                if case.get("tools_triggered") != "projects.list"
            ]
            if len(scoped_cases) != 4 or any(
                f"project {fixture_project_id}" not in str(case.get("user_prompt", ""))
                for case in scoped_cases
            ):
                errors.append("scoped submission prompts do not match the reviewer fixture")
    try:
        release_notes = release_notes_path.read_text(encoding="utf-8")
        reviewer = reviewer_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"submission reviewer documentation is missing or invalid: {exc}")
    else:
        for marker in ("0.2.0", "46 tools", "OAuth", "project_id", "idempotency", "file references"):
            if marker not in release_notes:
                errors.append(f"release notes missing marker: {marker}")
        for marker in (
            CANONICAL_MCP_URL,
            "projects.list",
            "confirmation preview",
            "five positive prompts",
            "three negative prompts",
            "privacy-policy",
            "terms-and-conditions",
        ):
            if marker not in reviewer:
                errors.append(f"reviewer instructions missing marker: {marker}")
        if (reviewer_fixture or {}).get("status") == "local_placeholder" and "--reviewer-project-id" not in reviewer:
            errors.append("reviewer instructions must explain how to replace the local fixture")

    license_path = ROOT / "plugins" / "sparklaunch" / "LICENSE"
    try:
        license_text = license_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"plugin LICENSE is missing or invalid: {exc}")
    else:
        if "Proprietary" not in license_text:
            errors.append("plugin LICENSE does not match the manifest")

    try:
        with tempfile.TemporaryDirectory() as directory:
            bundle, _digest = build_bundle(Path(directory) / "candidate.zip")
            if not bundle.is_file() or bundle.stat().st_size <= 0:
                errors.append("submission bundle was not created")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"submission bundle is not buildable: {exc}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(errors))
        return 1
    print("SparkLaunch skills and submission package validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
