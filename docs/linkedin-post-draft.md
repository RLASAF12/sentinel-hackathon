# LinkedIn Post — Draft

> Replace `[demo link]` once the video is uploaded. Confirm the repo is public
> before posting. Tone: builder to builder, no buzzwords.

---

## Draft A — primary

Just shipped **Sentinel** at the Google Cloud Rapid Agent Hackathon.

The concept: an AI agent that knows when **not** to ship.

Most deployment agents race to fix prod on their own. Sentinel does the
analysis — then stops and asks a human before doing anything destructive.

3 things built in 5 days:
1. Multi-agent risk detection — Google ADK + 7 subagents scan a deploy for
   file churn, config changes, coverage drops, and prod targets.
2. Gemini 2.0 Flash diagnosis — turns raw risk signals into a root cause and a
   recommended action.
3. A human approval gate — before any destructive action (rollback, cancel),
   Sentinel shows you what, why, the risk score, and the alternatives. You
   decide. Every decision is logged to an append-only audit trail.

That gate is the differentiator. Almost no one builds it. It's the line between
AI *assistance* and AI *autonomy over production* — and engineers want the
former.

Repo: https://github.com/RLASAF12/sentinel-hackathon
Demo: [demo link]

#GoogleCloud #AI #Hackathon #MCP #AgentDevelopment #Python #BuildInPublic

---

## Draft B — shorter / punchier

We gave an AI agent power over production deploys — then made it ask permission.

That's Sentinel, my Google Cloud Rapid Agent Hackathon build: it detects deploy
risk, diagnoses the root cause with Gemini 2.0 Flash, proposes a fix through the
GitLab MCP server, and then **halts at a human gate** before anything
destructive runs. Approve, hold, or inspect — every call logged.

AI suggests. You decide.

Repo: https://github.com/RLASAF12/sentinel-hackathon
Demo: [demo link]

#GoogleCloud #AI #Hackathon #MCP #AgentDevelopment #Python #BuildInPublic

---

## Posting checklist
- [ ] Repo is public
- [ ] Demo video uploaded; `[demo link]` replaced
- [ ] Screenshot/GIF of the risk gate attached (the money shot)
- [ ] Devpost submission link added (optional)
