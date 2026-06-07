# Sentinel — ~3-Minute Demo Script

Format: screen recording of the hosted web UI + the live GitLab pipelines page.
Everything below is **real**: real Gemini 3, a real GitLab pipeline, a real cancel.

- Sentinel: https://sentinel-258340350085.us-central1.run.app
- GitLab pipelines: https://gitlab.com/harelasaf7-group/sentinel-demo-target/-/pipelines

Before recording, trigger a running pipeline so there's a live target:

```bash
curl -s -X POST -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/82983615/pipeline?ref=main" >/dev/null
```

---

## [0:00] Cold open
Camera on the Sentinel page.
> "AI agents that act are dangerous without a brake. Sentinel is the brake —
> the agent that knows when *not* to ship."

## [0:15] Detect + Diagnose (Gemini 3)
Click **Review the pending deployment**. As the panels render:
> "Sentinel reads a live GitLab pipeline through its MCP server and asks Gemini 3
> to assess the blast radius."
Point at the risk score and Gemini 3's root cause.

## [0:40] The gate — the money shot
Stop on the red **SENTINEL RISK GATE** panel. Let it breathe 2–3s.
> "It wants to cancel the deploy. But it won't. It stops and asks a human. The AI
> cannot proceed alone — and every decision is logged."

## [1:05] Deny → HOLD (the brake works)
Click **Deny**. Show "HELD — pipeline left running."
Switch to the GitLab pipelines tab, reload:
> "I said no. The pipeline is still running. Nothing happened to production."

## [1:40] Approve → real effect
Back in Sentinel, run again and click **Approve**. Show "Cancelled pipeline … via GitLab."
Switch to the GitLab tab, reload:
> "This time I approve — and the pipeline is cancelled, for real, through the
> GitLab MCP server. The agent acted only because a human said go."

## [2:20] Audit trail
Point at the audit entry (approver, timestamp, gitlab_status).
> "Approve or deny, it's the same append-only record. Fully auditable."

## [2:40] Close
> "Gemini 3 for the reasoning, Google ADK for the agent, GitLab's MCP server for
> the action — and a human gate so it never ships on its own. Sentinel."

---

## After recording
- Upload to YouTube (unlisted) or Loom; note the URL for Devpost.
- Thumbnail: the gate panel (scripts/shots/sentinel-03-gate-hero.png).
