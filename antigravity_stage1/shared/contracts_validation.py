from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ValidationStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    CONTINUITY_ONLY = "continuity_only"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass
class EvidenceCheck:
    claim_ref: str
    evidence_refs: List[str]
    confidence: str
    validation_status: str
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FreshnessCheck:
    source_ref: str
    freshness_status: str
    evaluated_at: str
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SectionValidationResult:
    section_key: str
    status: str
    evidence_checks: List[EvidenceCheck] = field(default_factory=list)
    freshness_checks: List[FreshnessCheck] = field(default_factory=list)
    requires_intervention: bool = False
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_key": self.section_key,
            "status": self.status,
            "evidence_checks": [item.to_dict() for item in self.evidence_checks],
            "freshness_checks": [item.to_dict() for item in self.freshness_checks],
            "requires_intervention": self.requires_intervention,
            "notes": self.notes,
        }


@dataclass
class InterventionRecord:
    section_key: str
    original_text: str
    edited_text: str
    reason: str
    editor: str
    original_confidence: str
    revised_confidence: str
    timestamp: str
    resolved_validation_issue: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    call_run_id: str
    section_results: List[SectionValidationResult] = field(default_factory=list)
    interventions: List[InterventionRecord] = field(default_factory=list)
    overall_status: str = ValidationStatus.PASS.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_run_id": self.call_run_id,
            "section_results": [item.to_dict() for item in self.section_results],
            "interventions": [item.to_dict() for item in self.interventions],
            "overall_status": self.overall_status,
        }


def determine_overall_status(section_results: List[SectionValidationResult]) -> str:
    if any(s.status == ValidationStatus.FAIL.value for s in section_results):
        return ValidationStatus.FAIL.value
    if any(s.status == ValidationStatus.WARNING.value for s in section_results):
        return ValidationStatus.WARNING.value
    return ValidationStatus.PASS.value
