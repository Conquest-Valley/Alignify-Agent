from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class ConfidenceBand(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Build1State(str, Enum):
    SCHEDULED = "scheduled"
    PRE_CALL_REQUESTED = "pre_call_requested"
    CONTEXT_LOADED = "context_loaded"
    STRATEGY_EXTRACTED = "strategy_extracted"
    CAMPAIGN_STATUS_BUILT = "campaign_status_built"
    COMMITMENTS_RECONCILED = "commitments_reconciled"
    WINS_RANKED = "wins_ranked"
    DOWNTURNS_EXPLAINED = "downturns_explained"
    AMBIGUITIES_FLAGGED = "ambiguities_flagged"
    AGENDA_RENDERED = "agenda_rendered"
    AWAITING_DP_PRE_CALL_REVIEW = "awaiting_dp_pre_call_review"


class CampaignCategory(str, Enum):
    STRATEGY = "Strategy"
    SEO_COPY = "SEO / Copy"
    LOCAL_SEO_GBP = "Local SEO / GBP"
    WEB_DEVELOPMENT = "Web Development"
    CRO = "CRO"
    ANALYTICS_TRACKING = "Analytics / Tracking"
    LINK_BUILDING_AUTHORITY = "Link Building / Authority"
    PAID_MEDIA = "Paid Media"
    SOCIAL_COMMUNITY = "Social / Community"
    EMAIL_CRM = "Email / CRM"
    APPROVALS_CLIENT_DEPENDENCIES = "Approvals / Client Dependencies"
    INTERNAL_BLOCKERS = "Internal Blockers"


@dataclass
class EvidenceRef:
    source_type: str
    source_ref: str
    source_timestamp_or_window: str
    observation: str
    confidence: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CallRun:
    call_run_id: str
    client_id: str
    dp_id: str
    scheduled_at: str
    p0_instruction: str
    current_state: str
    source_refs: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FreshnessAssessment:
    source_ref: str
    source_class: str
    freshness_status: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SnapshotTimestamp:
    source_ref: str
    retrieved_at: str


@dataclass
class SnapshotWindow:
    source_ref: str
    window_label: str


@dataclass
class SnapshotEvent:
    event_type: str
    event_at: str
    details: str


@dataclass
class RunSnapshotManifest:
    call_run_id: str
    client_id: str
    retrieved_source_refs: List[str] = field(default_factory=list)
    retrieval_timestamps: List[SnapshotTimestamp] = field(default_factory=list)
    reporting_windows: List[SnapshotWindow] = field(default_factory=list)
    prior_call_date_used: Optional[str] = None
    quarterly_strategy_ref_used: Optional[str] = None
    template_ref_used: Optional[str] = None
    agenda_version: str = "v1"
    validation_version: str = "v1"
    snapshot_events: List[SnapshotEvent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_run_id": self.call_run_id,
            "client_id": self.client_id,
            "retrieved_source_refs": self.retrieved_source_refs,
            "retrieval_timestamps": [asdict(item) for item in self.retrieval_timestamps],
            "reporting_windows": [asdict(item) for item in self.reporting_windows],
            "prior_call_date_used": self.prior_call_date_used,
            "quarterly_strategy_ref_used": self.quarterly_strategy_ref_used,
            "template_ref_used": self.template_ref_used,
            "agenda_version": self.agenda_version,
            "validation_version": self.validation_version,
            "snapshot_events": [asdict(item) for item in self.snapshot_events],
        }


@dataclass
class SectionCheckResult:
    section_name: str
    is_valid: bool
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    required_follow_up: List[str] = field(default_factory=list)


@dataclass
class SectionValidationReport:
    call_run_id: str
    sections: List[SectionCheckResult]
    overall_valid: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_run_id": self.call_run_id,
            "sections": [asdict(item) for item in self.sections],
            "overall_valid": self.overall_valid,
        }


@dataclass
class OverrideEntry:
    section: str
    original_text: str
    edited_text: str
    reason_code: str
    timestamp: str


@dataclass
class ManualOverrideLog:
    call_run_id: str
    dp_id: str
    overrides: List[OverrideEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_run_id": self.call_run_id,
            "dp_id": self.dp_id,
            "overrides": [asdict(item) for item in self.overrides],
        }


@dataclass
class ConflictRecord:
    topic: str
    higher_priority_source: str
    lower_priority_source: str
    resolution: str
    reason: str


@dataclass
class ContextConflictResolution:
    conflicts: List[ConflictRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"conflicts": [asdict(item) for item in self.conflicts]}


def create_call_run(client_id: str, dp_id: str, scheduled_at: str, p0_instruction: str = "") -> CallRun:
    if not client_id:
        raise ValueError("client_id is required")
    if not dp_id:
        raise ValueError("dp_id is required")
    if not scheduled_at:
        raise ValueError("scheduled_at is required")
    now = utc_now_iso()
    return CallRun(
        call_run_id=f"callrun_{uuid4().hex[:12]}",
        client_id=client_id,
        dp_id=dp_id,
        scheduled_at=scheduled_at,
        p0_instruction=p0_instruction,
        current_state=Build1State.PRE_CALL_REQUESTED.value,
        source_refs=[],
        created_at=now,
        updated_at=now,
    )
