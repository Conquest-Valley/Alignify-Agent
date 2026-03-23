from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    NEEDS_HUMAN_INPUT = "needs_human_input"


class ResolutionStatus(str, Enum):
    CLEAN = "clean"
    REPAIRED = "repaired"
    BLOCKED = "blocked"


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


class CanonicalSectionKey(str, Enum):
    EXECUTIVE_SNAPSHOT = "executive_snapshot"
    BASECAMP_MOVEMENT_SUMMARY = "basecamp_movement_summary"
    WINS_HIGHLIGHTS = "wins_highlights"
    IN_PROGRESS = "in_progress"
    NEXT_UP = "next_up"
    INPUT_REQUIRED = "input_required"
    STRATEGIC_BRAINSTORM = "strategic_brainstorm"
    APPROVALS_DEPENDENCIES = "approvals_dependencies"
    RISKS_WATCHOUTS = "risks_watchouts"


class SourceFamily(str, Enum):
    GOOGLE_WORKSPACE_DOC = "google_workspace_doc"
    GOOGLE_WORKSPACE_SHEET = "google_workspace_sheet"
    GOOGLE_MARKETING_GA4 = "google_marketing_ga4"
    GOOGLE_MARKETING_GSC = "google_marketing_gsc"
    BASECAMP_EXECUTION = "basecamp_execution"
    BASECAMP_MESSAGE = "basecamp_message"
    PRODUCER_NOTE = "producer_note"
    MANUAL_INPUT = "manual_input"
    MCP_UNKNOWN = "mcp_unknown"


@dataclass
class CanonicalSectionDefinition:
    key: str
    display_label: str
    required_for_v2: bool
    human_gate_relevant: bool
    allows_low_confidence_content: bool
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceDescriptor:
    source_ref: str
    source_family: str
    raw_source_label: str
    display_name: str
    source_class: str
    retrieval_method: str
    normalized_from_alias: Optional[str] = None

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
class StageRepairAttempt:
    issue_code: str
    attempted_fix: str
    outcome: str
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StageGateDecision:
    stage_name: str
    from_state: str
    proposed_state: str
    resolution_status: str
    should_continue: bool
    needs_human_input: bool
    user_visible_reason: str
    repair_attempts: List[StageRepairAttempt] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "from_state": self.from_state,
            "proposed_state": self.proposed_state,
            "resolution_status": self.resolution_status,
            "should_continue": self.should_continue,
            "needs_human_input": self.needs_human_input,
            "user_visible_reason": self.user_visible_reason,
            "repair_attempts": [item.to_dict() for item in self.repair_attempts],
        }


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
        created_at=now,
        updated_at=now,
    )


def canonical_section_definitions() -> List[CanonicalSectionDefinition]:
    return [
        CanonicalSectionDefinition(CanonicalSectionKey.EXECUTIVE_SNAPSHOT.value, "Executive Snapshot", True, True, False),
        CanonicalSectionDefinition(CanonicalSectionKey.BASECAMP_MOVEMENT_SUMMARY.value, "Basecamp Movement Summary", True, True, False),
        CanonicalSectionDefinition(CanonicalSectionKey.WINS_HIGHLIGHTS.value, "Wins / Highlights", True, True, False),
        CanonicalSectionDefinition(CanonicalSectionKey.IN_PROGRESS.value, "In Progress", True, True, False),
        CanonicalSectionDefinition(CanonicalSectionKey.NEXT_UP.value, "Next Up", True, True, False),
        CanonicalSectionDefinition(CanonicalSectionKey.INPUT_REQUIRED.value, "Input Required", True, True, True),
        CanonicalSectionDefinition(CanonicalSectionKey.STRATEGIC_BRAINSTORM.value, "Strategic Brainstorm", False, True, True),
        CanonicalSectionDefinition(CanonicalSectionKey.APPROVALS_DEPENDENCIES.value, "Approvals / Dependencies", True, True, False),
        CanonicalSectionDefinition(CanonicalSectionKey.RISKS_WATCHOUTS.value, "Risks / Watchouts", True, True, True),
    ]
