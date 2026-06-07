# MCP Setup — GitLab

Sentinel drives a GitLab MCP server with a Personal Access Token (`api` scope).
Two backends are supported, selected by `SENTINEL_GITLAB_MCP`:

## Default — PAT-based GitLab MCP (`stdio`, works on any plan)

```bash
npm install -g @zereight/mcp-gitlab    # or run on demand via npx

export GITLAB_TOKEN=<personal access token, api scope>
export GITLAB_URL=https://gitlab.com   # or your self-hosted instance
export USE_PIPELINE=true               # expose CI/CD pipeline tools
export SENTINEL_GITLAB_MCP=stdio
```

The agent launches the server over stdio and exposes a filtered tool set (see
`GITLAB_TOOL_FILTER` in `src/sentinel/agent.py`).

## Official GitLab MCP (`http`, requires GitLab Duo)

GitLab's official MCP server is served at `https://<instance>/api/v4/mcp` and
authenticated with `Authorization: Bearer <PAT>`. It requires a paid GitLab Duo
plan (returns 404 on Free). To use it:

```bash
export SENTINEL_GITLAB_MCP=http
```

## Tools (reads free, destructive gated)

| MCP tool | Destructive | Gated |
|----------|-------------|-------|
| `get_pipeline`, `list_pipelines`, `list_pipeline_jobs`, `get_merge_request` | no | no |
| `cancel_pipeline` | **yes** | **yes** |
| `create_merge_request`, `create_merge_request_note` | **yes** | **yes** |

Destructive tools are always routed through the human risk-gate before they run.

## Notes

- In TLS-intercepting environments, forward the CA bundle to the Node server
  (`NODE_EXTRA_CA_CERTS`); the agent does this automatically when the variable
  is set.
- Offline mode (`SENTINEL_DEMO=true`) uses `MockGitLabMCPClient` so the flow runs
  with no token — useful for tests and local development.
