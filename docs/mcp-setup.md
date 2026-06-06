# MCP Setup — GitLab MCP (primary)

Sentinel's ACT phase talks to GitLab through the **official GitLab MCP server**
via the Model Context Protocol Python SDK (`mcp`).

## Install the GitLab MCP server

```bash
npm install -g @gitlab/mcp-server
# or run on demand:
npx @gitlab/mcp-server
```

## Environment

```bash
export GITLAB_TOKEN=<personal access token, api scope>
export GITLAB_URL=https://gitlab.com   # or your self-hosted instance
```

## Tools Sentinel wraps (`src/mcp/client.py`)

| Method | MCP tool | Destructive | Gated |
|--------|----------|-------------|-------|
| `get_diff(project_id, mr_iid)` | `get_merge_request_diff` | no | no |
| `create_comment(project_id, mr_iid, body)` | `create_merge_request_note` | no | no |
| `get_pipeline(project_id, pipeline_id)` | `get_pipeline` | no | no |
| `cancel_pipeline(project_id, pipeline_id)` | `cancel_pipeline` | **yes** | **yes** |

`cancel_pipeline` is the only destructive tool and is **always** routed through
the risk gate before it runs.

## Demo mode (no token needed)

```bash
export SENTINEL_DEMO=true
```

`get_mcp_client()` returns `MockGitLabMCPClient`, which serves a canned diff and
logs `[DEMO MCP]` actions instead of calling GitLab. This lets the full pipeline
and the demo recording run with zero credentials.

## Fallback

GitHub MCP is the documented fallback if GitLab MCP is unavailable; the client
interface (`get_diff` / `create_comment` / `get_pipeline` / `cancel_pipeline`)
is intentionally provider-agnostic.
