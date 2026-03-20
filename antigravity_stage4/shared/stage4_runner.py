from __future__ import annotations

from typing import Any, Dict

from antigravity_stage1.shared.contracts_runtime import Build1State
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine import transition_call_state

from .basecamp_auditor import aggregate_campaign_status_matrix
from .commitment_reconciler import build_commitment_audit_lite


def run_stage4(
    call_run,
    context_bundle: Dict[str, Any],
    strategy_summary: Dict[str, Any],
    narrative_summary_lite: Dict[str, Any],
    *,
    manifest=None,
) -> Dict[str, Any]:
    campaign_status_matrix = aggregate_campaign_status_matrix(context_bundle, strategy_summary)
    allowed, reason = transition_call_state(call_run, Build1State.CAMPAIGN_STATUS_BUILT.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, 'campaign_status_built', 'Stage 4 built campaign status matrix')

    commitment_audit_lite = build_commitment_audit_lite(context_bundle, narrative_summary_lite, campaign_status_matrix)
    allowed, reason = transition_call_state(call_run, Build1State.COMMITMENTS_RECONCILED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, 'commitments_reconciled', 'Stage 4 reconciled prior commitments to Basecamp')

    return {
        'campaign_status_matrix': campaign_status_matrix,
        'commitment_audit_lite': commitment_audit_lite,
    }
