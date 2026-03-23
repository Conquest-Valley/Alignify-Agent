from __future__ import annotations

from typing import Tuple

from .contracts_runtime_v2 import Build1StateV2, CallRunV2, utc_now_iso


_ALLOWED_TRANSITIONS = {
    Build1StateV2.SCHEDULED.value: {Build1StateV2.PRE_CALL_REQUESTED.value},
    Build1StateV2.PRE_CALL_REQUESTED.value: {
        Build1StateV2.CONTEXT_LOADED.value,
        Build1StateV2.NEEDS_HUMAN_INPUT.value,
    },
    Build1StateV2.CONTEXT_LOADED.value: {
        Build1StateV2.STRATEGY_EXTRACTED.value,
        Build1StateV2.NEEDS_HUMAN_INPUT.value,
    },
    Build1StateV2.STRATEGY_EXTRACTED.value: {Build1StateV2.CAMPAIGN_STATUS_BUILT.value},
    Build1StateV2.CAMPAIGN_STATUS_BUILT.value: {
        Build1StateV2.COMMITMENTS_RECONCILED.value,
        Build1StateV2.WINS_RANKED.value,
    },
    Build1StateV2.COMMITMENTS_RECONCILED.value: {Build1StateV2.WINS_RANKED.value},
    Build1StateV2.WINS_RANKED.value: {
        Build1StateV2.DOWNTURNS_EXPLAINED.value,
        Build1StateV2.AMBIGUITIES_FLAGGED.value,
    },
    Build1StateV2.DOWNTURNS_EXPLAINED.value: {Build1StateV2.AMBIGUITIES_FLAGGED.value},
    Build1StateV2.AMBIGUITIES_FLAGGED.value: {Build1StateV2.AGENDA_RENDERED.value},
    Build1StateV2.AGENDA_RENDERED.value: {Build1StateV2.AWAITING_DP_PRE_CALL_REVIEW.value},
    Build1StateV2.AWAITING_DP_PRE_CALL_REVIEW.value: set(),
    Build1StateV2.NEEDS_HUMAN_INPUT.value: set(),
}


def is_transition_allowed_v2(current_state: str, proposed_next_state: str) -> bool:
    return proposed_next_state in _ALLOWED_TRANSITIONS.get(current_state, set())


def transition_call_state_v2(call_run: CallRunV2, proposed_next_state: str) -> Tuple[bool, str]:
    if not is_transition_allowed_v2(call_run.current_state, proposed_next_state):
        return False, f"Illegal transition from {call_run.current_state} to {proposed_next_state}"
    call_run.current_state = proposed_next_state
    call_run.updated_at = utc_now_iso()
    return True, "ok"
