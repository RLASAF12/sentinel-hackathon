# W5 — Content Chain

## Trigger
Say "Run W5" after W4 is submitted.

## Purpose
Polish the repo and prepare post-hackathon content. Day 5 buffer.

## Steps

### 1. README Final Polish (content-positioning)
The README is your landing page for judges. Non-negotiable items:
- Hero: project name + tagline + 1-line pitch
- Architecture diagram (Mermaid or ASCII art)
- "The Differentiator" section: explain the gate clearly
- Quick start: 3 commands to get running
- Google Cloud section: what GCP components, where used
- MCP section: which server, which tools
- Responsible AI: why the gate matters, audit log
- Demo video link

Tone check: specific, confident, no buzzwords.

### 2. LinkedIn Post (content-positioning)
Create docs/linkedin-post-draft.md using the template in agents/content-positioning.md.

Format:
- Hook: "Just shipped [X] for [hackathon]"
- 3 things built
- The key differentiator (the gate)
- Repo + demo link
- Tags: #GoogleCloud #AI #Hackathon #MCP #AgentDevelopment

### 3. Fix Any Issues (builder)
- All tests passing?
- Demo runs cleanly?
- Cloud Run URL responding?
- Any TODOs in src/ that should be done?

### 4. Tag the Release
Create GitHub release v1.0.0-hackathon:
- Go to https://github.com/RLASAF12/sentinel-hackathon/releases/new
- Tag: v1.0.0-hackathon
- Title: Sentinel — Google Cloud Rapid Agent Hackathon
- Body: Devpost link + demo video link + one-line description

## Done When
- [ ] README is stellar
- [ ] LinkedIn draft exists in docs/
- [ ] All tests pass
- [ ] Release v1.0.0-hackathon tagged

## Final Word
The gate is the differentiator. No one else built that. You shipped.
