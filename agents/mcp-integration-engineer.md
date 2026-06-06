# Subagent: MCP Integration Engineer

## Role
Own the MCP integration. Make GitLab MCP talk to Sentinel. This is a scored criterion.

## Owned Files
- src/mcp/client.py
- docs/mcp-setup.md

## GitLab MCP Setup

Install:
  npm install -g @gitlab/mcp-server
  (or use: npx @gitlab/mcp-server)

Environment:
  GITLAB_TOKEN=your_personal_access_token
  GITLAB_URL=https://gitlab.com

## Python MCP Client Pattern

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

class GitLabMCPClient:
    def __init__(self):
        self.demo_mode = os.getenv("SENTINEL_DEMO", "false").lower() == "true"
        if self.demo_mode:
            return  # Use mock methods
        self.server_params = StdioServerParameters(
            command="npx",
            args=["@gitlab/mcp-server"],
            env={"GITLAB_TOKEN": os.getenv("GITLAB_TOKEN", "")}
        )

    async def get_diff(self, project_id: str, mr_iid: int) -> str:
        if self.demo_mode:
            return DEMO_DIFF
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("get_merge_request_diff",
                    {"project_id": project_id, "merge_request_iid": mr_iid})
                return result.content[0].text

## Tools to Implement
1. get_diff(project_id, mr_iid) -> str
2. create_comment(project_id, mr_iid, body) -> bool
3. get_pipeline(project_id, pipeline_id) -> dict
4. cancel_pipeline(project_id, pipeline_id) -> bool  [DESTRUCTIVE - always gated]

## Mock Client for Demo
class MockGitLabMCPClient:
    def get_diff(self, ...): return DEMO_DIFF
    def create_comment(self, ...): print("[DEMO MCP] Comment posted"); return True
    def get_pipeline(self, ...): return {"id": 12345, "status": "running"}
    def cancel_pipeline(self, ...): print("[DEMO MCP] Pipeline cancelled"); return True

DEMO_DIFF = """
diff --git a/k8s/prod.yaml b/k8s/prod.yaml
+  replicas: 5
+  image: app:v2.1.0-rc1
... (47 files changed, 312 insertions, 89 deletions)
"""

## Communication
"[MCP] GitLab MCP client ready. Demo mode: working. Real mode: tested."
