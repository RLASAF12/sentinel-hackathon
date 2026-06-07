"""Data models for the Sentinel pipeline.

These dataclasses are the contracts that flow through
detect -> diagnose -> act -> gate -> execute. Kept dependency-free
(stdlib only) so every module can import them without pulling in heavy SDKs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class Severity(Enum):
    """Coarse severity bucket used by diagnosis and the gate display."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskSignal:
    """A single risk indicator found during the detect phase."""

    type: str
    severity: float  # 0.0-1.0
    evidence: str


@dataclass
class RiskReport:
    """Aggregate output of the detect phase."""

    signals: List[RiskSignal]
    score: float  # 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: dict = field(default_factory=dict)


@dataclass
class Diagnosis:
    """Root-cause analysis produced by Gemini in the diagnose phase."""

    root_cause: str
    severity: Severity
    recommended_action: str
    alternatives: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ProposedAction:
    """An action the agent wants to take. If destructive, it must pass the gate."""

    action_type: str  # rollback, alert, hold, patch
    destructive: bool
    description: str
    evidence: List[str] = field(default_factory=list)
    risk_score: float = 0.0


@dataclass
class ApprovalResult:
    """Outcome of a human decision at the risk gate."""

    approved: bool
    approver: str
    notes: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExecutionResult:
    """Result of executing (or discarding) a proposed action."""

    success: bool
    action_taken: str
    audit_log: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SentinelResult:
    """End-to-end result of one Sentinel run, returned by main.run_sentinel."""

    report: RiskReport
    diagnosis: Diagnosis
    action: ProposedAction
    approval: ApprovalResult
    execution: ExecutionResult
