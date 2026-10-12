"""Registered SparkLaunch App identity shared by native package validators."""

REGISTERED_APP_ID = "asdk_app_6a963bde250881918591112eac13b307"
APPS_CONFIG = {"apps": {"sparklaunch": {"id": REGISTERED_APP_ID}}}
PORTAL_MCP_PATH = "mcp/portal.json"


def native_connection_errors(manifest: dict, apps: dict) -> list[str]:
    errors = []
    if manifest.get("apps") != "./.app.json":
        errors.append("native SparkLaunch manifest must reference ./.app.json")
    if manifest.get("mcpServers") is not None:
        errors.append("native SparkLaunch must not declare a duplicate raw MCP server")
    if apps != APPS_CONFIG:
        errors.append("native SparkLaunch must bind exactly the registered SparkLaunch App")
    return errors
