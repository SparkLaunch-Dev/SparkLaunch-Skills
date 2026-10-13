"""Package-side contract for the server-owned initial ChatGPT surface."""

CHATGPT_MCP_URL = "https://sparklaun.ch/api/mcp/chatgpt/"
CHATGPT_SPARKCLOSE_TOOLS = frozenset({
    "sparkclose.model_safe", "sparkclose.save_scenario", "sparkclose.get_scenario",
    "sparkclose.list_scenarios", "sparkclose.readiness", "sparkclose.get_investment",
    "sparkclose.list_investments",
})


def is_public_tool(name: str) -> bool:
    return not name.startswith("sparkclose.") or name in CHATGPT_SPARKCLOSE_TOOLS


def public_description(text: str) -> str:
    return text.replace("model and close SAFE investments", "model SAFE scenarios and inspect private investment records")
