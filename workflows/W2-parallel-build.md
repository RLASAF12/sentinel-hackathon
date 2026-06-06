# W2 — Parallel Build

## Trigger
Say "Run W2" in Claude Code after W1 is complete.

## Purpose
Build the core Sentinel modules in parallel. Ship working code, no placeholders.

## Prerequisite
W1 must be complete (skeleton exists, ADR-001 written).

## Parallel Streams

### Stream A: Detection Engine (architect + builder)
**File**: src/sentinel/detect.py

Implement:
```python
class RiskDetector:
    def scan(self, context: dict) -> RiskReport:
        # Scan for: high-churn files, missing tests, config changes,
        # large diffs, breaking API changes
        # Return: RiskReport(signals=[], score=0.0-1.0, evidence=[])
```

Risk signals to detect:
- Files changed > threshold (default: 20)
- Test coverage dropped
- Config/env files modified
- Breaking change patterns in diff
- Deployment to production (not staging)

### Stream B: Diagnosis Engine (builder)
**File**: src/sentinel/diagnose.py

Implement:
```python
class GeminiDiagnoser:
    def __init__(self, api_key: str):
        # Init Gemini 2.0 Flash client
    
    def diagnose(self, risk_report: RiskReport, diff: str) -> Diagnosis:
        # Send to Gemini: risk signals + code diff
        # Get: root cause, severity, recommended action
        # Return: Diagnosis(root_cause=str, severity=str, action=str)
```

Gemini prompt template:
- Context: deployment risk signals found
- Evidence: code diff, risk signals
- Task: identify root cause and recommend action
- Output format: structured JSON

### Stream C: Risk Gate (safeguard-risk-engineer)
**File**: src/sentinel/gate.py

Implement:
```python
class RiskGate:
    def request_approval(self, action: ProposedAction) -> ApprovalRequest:
        # Present: what, why, risk score, alternatives
        # Wait for: human input (Y/N/details)
        # Log: decision with timestamp
        # Return: ApprovalResult(approved=bool, approver=str, notes=str)
```

Gate display format:
```
SENTINEL RISK GATE
==================
Action:   [rollback production deploy]
Risk:     HIGH (0.87)
Reason:   3 critical signals detected
Evidence: [list]

Proposed alternative: [delay + notify team]

APPROVE? (y/n/details):
```

## Integration Test
After both streams done:
```bash
python -c "
from sentinel.detect import RiskDetector
from sentinel.diagnose import GeminiDiagnoser
from sentinel.gate import RiskGate
print('All imports OK')
"
```

## Done When
- [ ] detect.py: RiskDetector.scan() returns RiskReport
- [ ] diagnose.py: GeminiDiagnoser.diagnose() returns Diagnosis
- [ ] gate.py: RiskGate.request_approval() works in CLI
- [ ] All unit tests pass
- [ ] python -m sentinel.main --demo runs (can use mock data)

## Hand Off
When done, say: "W2 complete. Ready for W3."
