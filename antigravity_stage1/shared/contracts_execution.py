from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    WAITING_ON_CLIENT = "waiting_on_client"
    QUEUED_NEXT = "queued_next"
    STALE = "stale"
    GHOST_IN_PROGRESS = "ghost_in_progress"


class BlockerType(str, Enum):
    NONE = "none"
    CLIENT = "client"
    AGENCY = "agency"
    APPROVAL = "approval"
    EXTERNAL = "external"


class CommitmentStatus(str, Enum):
    COMPLETED = "completed"
    ACTIVE = "active"
    BLOCKED = "blocked"
    STALE = "stale"
    UNMATCHED = "unmatched"


@dataclass
class ExecutionSignal:
    task_ref: str
    title: str
    category: str
    status: str
    blocker_type: str
    changed_since_last_call: bool
    approval_required: bool
    approval_received: bool
    comment_activity_count: int
    last_activity_at: Optional[str]
    quarterly_alignment_score: float
    delay_risk_score: float
    ghost_task_risk: bool
    source_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CampaignCategoryStatus:
    category: str
    completed_since_last_call: List[str] = field(default_factory=list)
    in_progress: List[str] = field(default_factory=list)
    blocked: List[str] = field(default_factory=list)
    waiting_on_client: List[str] = field(default_factory=list)
    queued_next: List[str] = field(default_factory=list)
    risk_level: str = "low"
    quarterly_alignment_score: float = 0.0
    alignment_notes: List[str] = field(default_factory=list)
    source_refs: List[str] = field(default_factory=list)
    execution_signals: List[ExecutionSignal] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "completed_since_last_call": self.completed_since_last_call,
            "in_progress": self.in_progress,
            "blocked": self.blocked,
            "waiting_on_client": self.waiting_on_client,
            "queued_next": self.queued_next,
            "risk_level": self.risk_level,
            "quarterly_alignment_score": self.quarterly_alignment_score,
            "alignment_notes": self.alignment_notes,
            "source_refs": self.source_refs,
            "execution_signals": [item.to_dict() for item in self.execution_signals],
        }


@dataclass
class CampaignStatusMatrix:
    categories: List[CampaignCategoryStatus] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"categories": [item.to_dict() for item in self.categories]}


@dataclass
class CommitmentItem:
    commitment_id: str
    source_call_date: str
    commitment_text: str
    owner: str
    due_date: Optional[str]
    matched_basecamp_task: Optional[str]
    status: str
    evidence_refs: List[str] = field(default_factory=list)
    confidence: str = "medium"
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CommitmentAuditLite:
    commitments: List[CommitmentItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"commitments": [item.to_dict() for item in self.commitments]}


@dataclass
class QueuePriorityItem:
    task_ref: str
    title: str
    category: str
    strategic_impact_score: float
    dependency_score: float
    client_value_score: float
    priority_rank: int
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueuePriorityModel:
    items: List[QueuePriorityItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"items": [item.to_dict() for item in self.items]}


def bounded_score(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def compute_risk_level(*, blocker_count: int, waiting_count: int, ghost_count: int, avg_alignment: float) -> str:
    if blocker_count >= 2 or ghost_count >= 2 or avg_alignment < 0.35:
        return "high"
    if blocker_count >= 1 or waiting_count >= 2 or ghost_count >= 1 or avg_alignment < 0.6:
        return "medium"
    return "low"


def infer_execution_status(*, is_complete: bool, is_blocked: bool, waiting_on_client: bool, queued_next: bool, ghost_task_risk: bool) -> str:
    if is_complete:
        return ExecutionStatus.COMPLETED.value
    if waiting_on_client:
        return ExecutionStatus.WAITING_ON_CLIENT.value
    if is_blocked:
        return ExecutionStatus.BLOCKED.value
    if queued_next:
        return ExecutionStatus.QUEUED_NEXT.value
    if ghost_task_risk:
        return ExecutionStatus.GHOST_IN_PROGRESS.value
    return ExecutionStatus.IN_PROGRESS.value
