from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Build1StateV2(str, Enum):
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


@dataclass
class CallRunV2:
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


def create_call_run_v2(client_id: str, dp_id: str, scheduled_at: str, p0_instruction: str = "") -> CallRunV2:
    now = utc_now_iso()
    return CallRunV2(
        call_run_id=f"callrun_{uuid4().hex[:12]}",
        client_id=client_id,
        dp_id=dp_id,
        scheduled_at=scheduled_at,
        p0_instruction=p0_instruction,
        current_state=Build1StateV2.PRE_CALL_REQUESTED.value,
        source_refs=[],
        created_at=now,
        updated_at=now,
    )
