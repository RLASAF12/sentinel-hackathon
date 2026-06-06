"""MCP client — GitLab MCP (primary) with a demo mock.

The official `mcp` SDK is imported lazily inside the real-mode methods so the
package imports cleanly without the dependency. When SENTINEL_DEMO=true,
get_mcp_client() returns MockGitLabMCPClient with canned responses.

Tools wrapped:
    get_diff(project_id, mr_iid) -> str
    create_comment(project_id, mr_iid, body) -> bool
    get_pipeline(project_id, pipeline_id) -> dict
    cancel_pipeline(project_id, pipeline_id) -> bool   [DESTRUCTIVE]
"""

import logging
import os

logger = logging.getLogger(__name__)

DEMO_DIFF = """diff --git a/k8s/prod.yaml b/k8s/prod.yaml
-  replicas: 3
-  image: app:v2.0.4
+  replicas: 5
+  image: app:v2.1.0-rc1
diff --git a/.env.production b/.env.production
+  FEATURE_FLAG_NEW_BILLING=true
... (47 files changed, 312 insertions(+), 89 deletions(-))
"""


def _demo_mode() -> bool:
    return os.getenv("SENTINEL_DEMO", "false").lower() in ("1", "true", "yes")


def get_mcp_client():
    """Factory: return the mock client in demo mode, else the real one."""
    return MockGitLabMCPClient() if _demo_mode() else GitLabMCPClient()


class MockGitLabMCPClient:
    """Canned GitLab MCP responses for offline demos and tests."""

    name = "MockGitLabMCPClient"

    async def get_diff(self, project_id: str, mr_iid: int) -> str:
        logger.info("[DEMO MCP] get_diff(%s, %s)", project_id, mr_iid)
        return DEMO_DIFF

    async def create_comment(self, project_id: str, mr_iid: int, body: str) -> bool:
        logger.info("[DEMO MCP] Comment posted to MR !%s", mr_iid)
        return True

    async def get_pipeline(self, project_id: str, pipeline_id: str) -> dict:
        logger.info("[DEMO MCP] get_pipeline(%s)", pipeline_id)
        return {"id": pipeline_id, "status": "running"}

    async def cancel_pipeline(self, project_id: str, pipeline_id: str) -> bool:
        logger.info("[DEMO MCP] Pipeline #%s cancelled", pipeline_id)
        return True


class GitLabMCPClient:
    """Real GitLab MCP client over stdio. Requires GITLAB_TOKEN.

    The `mcp` SDK is imported lazily so importing this module never requires it.
    """

    name = "GitLabMCPClient"

    def __init__(self) -> None:
        self._server_params = None

    def _params(self):
        from mcp import StdioServerParameters  # lazy import

        if self._server_params is None:
            self._server_params = StdioServerParameters(
                command="npx",
                args=["@gitlab/mcp-server"],
                env={
                    "GITLAB_TOKEN": os.getenv("GITLAB_TOKEN", ""),
                    "GITLAB_URL": os.getenv("GITLAB_URL", "https://gitlab.com"),
                },
            )
        return self._server_params

    async def _call(self, tool: str, args: dict):
        from mcp import ClientSession  # lazy import
        from mcp.client.stdio import stdio_client  # lazy import

        async with stdio_client(self._params()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool, args)

    async def get_diff(self, project_id: str, mr_iid: int) -> str:
        result = await self._call(
            "get_merge_request_diff",
            {"project_id": project_id, "merge_request_iid": mr_iid},
        )
        return result.content[0].text

    async def create_comment(self, project_id: str, mr_iid: int, body: str) -> bool:
        await self._call(
            "create_merge_request_note",
            {"project_id": project_id, "merge_request_iid": mr_iid, "body": body},
        )
        return True

    async def get_pipeline(self, project_id: str, pipeline_id: str) -> dict:
        result = await self._call(
            "get_pipeline", {"project_id": project_id, "pipeline_id": pipeline_id}
        )
        return {"id": pipeline_id, "raw": result.content[0].text}

    async def cancel_pipeline(self, project_id: str, pipeline_id: str) -> bool:
        await self._call(
            "cancel_pipeline", {"project_id": project_id, "pipeline_id": pipeline_id}
        )
        return True
