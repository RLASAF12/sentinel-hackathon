"""MCP client — connects to the GitLab MCP server (GitHub MCP as fallback).

W1 stub. Real MCP wiring + mock client land in W3 (mcp-integration-engineer).
The `mcp` SDK is imported lazily so the skeleton imports without the dep.
"""

import logging
import os

logger = logging.getLogger(__name__)


class MCPClient:
    """Thin wrapper over an MCP session exposing the tools Sentinel needs.

    Stub: methods are placeholders. In demo mode (SENTINEL_DEMO=true) the real
    implementation will route to a mock that returns canned responses.
    """

    def __init__(self, demo: bool | None = None) -> None:
        self.demo = (
            demo
            if demo is not None
            else os.getenv("SENTINEL_DEMO", "").lower() in ("1", "true", "yes")
        )

    async def rollback_pipeline(self, pipeline_id: str) -> dict:
        """Roll back / cancel a pipeline. Stub returns a placeholder result."""
        logger.info("MCPClient.rollback_pipeline stub; W3 will implement.")
        return {"ok": False, "stub": True, "pipeline_id": pipeline_id}

    async def alert_team(self, message: str) -> dict:
        """Notify the team via MCP. Stub returns a placeholder result."""
        logger.info("MCPClient.alert_team stub; W3 will implement.")
        return {"ok": False, "stub": True, "message": message}
