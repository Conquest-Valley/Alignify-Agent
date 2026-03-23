from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class WinType(str, Enum):
    PERFORMANCE = "performance"
    EXECUTION = "execution"
    STRATEGIC = "strategic"


class ExplanationSupport(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNSUPPORTED = "unsupported"


class AmbiguityPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class WinCandidate:
    win_id: str
    type: str
    category: str
    headline: str
    description: str
    strategic_goal_alignment: str
    client_relevance_score: float
    freshness_window: str
    evidence_refs: List[str] = field(default_factory=list)
    confidence: str = "medium"
    clarity_score: float = 0.0
    explainability_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WinRankedList:
    wins: List[WinCandidate] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"wins": [item.to_dict() for item in self.wins]}


@dataclass
class DownturnFinding:
    issue: str
    metric: str
    observed_change: str
    likely_cause: str
    evidence_refs: List[str] = field(default_factory=list)
    confidence: str = "medium"
    support_level: str = ExplanationSupport.PARTIALLY_SUPPORTED.value
    needs_human_input: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DownturnAssessmentLite:
    findings: List[DownturnFinding] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"findings": [item.to_dict() for item in self.findings]}


@dataclass
class AmbiguityItem:
    topic: str
    why_unclear: str
    missing_source: str
    risk_if_assumed: str
    recommended_input: str
    highlight_priority: str = AmbiguityPriority.MEDIUM.value
    related_evidence_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AmbiguityList:
    items: List[AmbiguityItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"items": [item.to_dict() for item in self.items]}


@dataclass
class ValueSignal:
    signal_ref: str
    signal_type: str
    category: str
    summary: str
    strategic_alignment_score: float
    client_relevance_score: float
    freshness_score: float
    credibility_score: float
    evidence_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def rank_score(*, strategic_alignment: float, client_relevance: float, freshness: float, credibility: float, clarity: float) -> float:
    return round(
        (0.30 * float(strategic_alignment))
        + (0.30 * float(client_relevance))
        + (0.15 * float(freshness))
        + (0.15 * float(credibility))
        + (0.10 * float(clarity)),
        4,
    )


def should_force_input_required(*, support_level: str, confidence: str) -> bool:
    return support_level == ExplanationSupport.UNSUPPORTED.value or confidence == "low"
