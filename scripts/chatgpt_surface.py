"""Package-side contract for the server-owned initial ChatGPT surface."""

import re

CHATGPT_MCP_URL = "https://sparklaun.ch/api/mcp/chatgpt/"
CHATGPT_SPARKCLOSE_TOOLS = frozenset({
    "sparkclose.model_safe", "sparkclose.save_scenario", "sparkclose.get_scenario",
    "sparkclose.list_scenarios", "sparkclose.readiness", "sparkclose.get_investment",
    "sparkclose.list_investments",
})


def is_public_tool(name: str) -> bool:
    return not name.startswith("sparkclose.") or name in CHATGPT_SPARKCLOSE_TOOLS


def public_description(text: str) -> str:
    replacements = (
        ("model and close SAFE investments", "model SAFE scenarios and inspect private investment records"),
        ("Model and close a SAFE", "Model and save a SAFE scenario"),
        ("Model SAFEs and manage confirmed investment closings", "Model SAFEs and inspect private investment records"),
        ("model a SAFE and review the steps to close its investment", "model a SAFE and inspect my saved scenarios and private investment records"),
        ("For SAFE modeling, saved dilution scenarios, funding evidence, or investment closings", "For SAFE modeling, saved dilution scenarios, financing readiness, or private investment records"),
        ("Model SAFE exposure, confirm funding evidence and close one signed investment", "Model SAFE exposure and save a private planning scenario"),
    )
    for full, public in replacements:
        text = text.replace(full, public)
    return text


def public_scope_findings(text: str) -> list[str]:
    """Reject unsupported positive claims in public skill/recipe descriptions."""
    pattern = re.compile(
        r"\b(?:investment closings|confirm funding evidence|"
        r"close (?:one|a|an|the) (?:signed )?investment|"
        r"model and close (?:a )?SAFE|prepare (?:a |an |the )?(?:reviewed )?unsigned SAFE agreement)\b",
        re.IGNORECASE,
    )
    return ["excluded investment capability claim"] if pattern.search(text) else []
