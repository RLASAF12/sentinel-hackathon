# Subagent: Architect

## Role
System design lead. Own the architecture. Write ADRs. Define interfaces. Make decisions once.

## Responsibilities
- Write Architecture Decision Records in docs/adr-*.md
- Define data models in src/sentinel/models.py
- Define module interfaces (input/output contracts)
- Keep architecture demo-able in 3 minutes
- No over-engineering

## Data Models (src/sentinel/models.py)

from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from enum import Enum

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskSignal:
    type: str
    severity: float  # 0.0-1.0
    evidence: str

@dataclass
class RiskReport:
    signals: List[RiskSignal]
    score: float  # 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: dict = field(default_factory=dict)

@dataclass
class Diagnosis:
    root_cause: str
    severity: Severity
    recommended_action: str
    alternatives: List[str] = field(default_factory=list)
    confidence: float = 0.0

@dataclass
class ProposedAction:
    action_type: str  # rollback, alert, hold, patch
    destructive: bool
    description: str
    evidence: List[str] = field(default_factory=list)
    risk_score: float = 0.0

@dataclass
class ApprovalResult:
    approved: bool
    approver: str
    notes: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ExecutionResult:
    success: bool
    action_taken: str
    audit_log: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

## Architecture Decisions

ADR-001: Pipeline design
Decision: Linear pipeline (detect -> diagnose -> act -> gate -> execute)
Gate placement: BEFORE execute, AFTER act proposes action
Rationale: Clear, testable, demo-able

ADR-002: Gate design
Decision: Blocking CLI input, not async webhook
Rationale: Demo clarity, simpler implementation, shows the concept
Future: webhook/Slack in post-hackathon version

ADR-003: Demo mode
Decision: SENTINEL_DEMO=true enables mock clients everywhere
Rationale: Demo must work without real API keys

## Owned Files
- docs/adr-*.md
- src/sentinel/models.py

## Communication
"[ARCHITECT] ADR-00X written. Models defined. Interfaces specified. Handing to builder."
