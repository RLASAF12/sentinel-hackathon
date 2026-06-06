# Devpost Unknowns — Resolved (W1)

Status: Resolved with working defaults. Re-verify against the live Devpost
page before final submission in W4.

## 1. Track / Category Names

The remote build environment has no confirmed URL to the live Devpost page,
so these are locked from PLAN.md defaults and the rubric in CLAUDE.md.

**Selected tracks (working assumption):**
- **Best Use of Google Cloud** — Gemini 2.0 Flash + Cloud Run
- **Best Use of MCP** — GitLab MCP (official partner integration)

**Action for W4:** Open the Devpost hackathon page, copy the exact track
labels verbatim, and update `docs/submission-draft.md`. Track names must
match Devpost spelling exactly or the submission can be miscategorized.

## 2. GCP Credit Situation

- **Decision:** Use our own GCP account. Not blocking for the build.
- Gemini access via API key (`GEMINI_API_KEY`); Cloud Run deploy in W3.
- Demo mode (`SENTINEL_DEMO=true`) runs the full pipeline with mock clients,
  so a credit/quota issue never blocks the demo recording.

## 3. Open Items to Confirm in W4

- [ ] Exact track names (verbatim from Devpost)
- [ ] Submission deadline (date + timezone)
- [ ] Video length limit (assumed 3:00 — matches demo-script.md)
- [ ] Team member listing requirements
- [ ] Whether public GitHub repo is required (assumed yes)
