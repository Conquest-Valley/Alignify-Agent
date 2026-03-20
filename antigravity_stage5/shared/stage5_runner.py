from __future__ import annotations

from typing import Any, Dict

from antigravity_stage1.shared.contracts_runtime import Build1State
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine import transition_call_state

from .ambiguity_detector import build_ambiguity_list
from .downturn_assessor import generate_downturn_candidates
from .win_hunter import (
    extract_execution_win_candidates,
    extract_performance_win_candidates,
    extract_strategic_win_candidates,
    rank_win_candidates,
)


def run_stage5(
    call_run,
    context_bundle: Dict[str, Any],
    strategy_summary: Dict[str, Any],
    narrative_summary_lite: Dict[str, Any],
    context_conflict_resolution: Dict[str, Any],
    campaign_status_matrix: Dict[str, Any],
    commitment_audit_lite: Dict[str, Any],
    *,
    manifest=None,
) -> Dict[str, Any]:
    performance = extract_performance_win_candidates(context_bundle, strategy_summary)
    execution = extract_execution_win_candidates(campaign_status_matrix, strategy_summary)
    strategic = extract_strategic_win_candidates(campaign_status_matrix, strategy_summary)
    wins = rank_win_candidates(performance, execution, strategic)

    allowed, reason = transition_call_state(call_run, Build1State.WINS_RANKED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, 'wins_ranked', 'Stage 5 ranked performance, execution, and strategic wins')

    downturns = generate_downturn_candidates(context_bundle, campaign_status_matrix, narrative_summary_lite)
    allowed, reason = transition_call_state(call_run, Build1State.DOWNTURNS_EXPLAINED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, 'downturns_explained', 'Stage 5 assessed negative or flat signals')

    ambiguities = build_ambiguity_list(context_conflict_resolution, campaign_status_matrix, downturns, narrative_summary_lite)
    allowed, reason = transition_call_state(call_run, Build1State.AMBIGUITIES_FLAGGED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, 'ambiguities_flagged', 'Stage 5 flagged unresolved ambiguity and input required items')

    return {
        'win_ranked_list': wins,
        'downturn_assessment_lite': downturns,
        'ambiguity_list': ambiguities,
    }
