from __future__ import annotations

from typing import Any, Dict

from antigravity_stage1.shared.contracts_runtime_v2 import Build1StateV2
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine_v2 import transition_call_state_v2

from antigravity_stage3.shared.stage3_runtime_v3 import run_stage3_v3

from .basecamp_auditor import aggregate_campaign_status_matrix
from .commitment_reconciler import build_commitment_audit_lite


def run_stage4_v2(
    call_run,
    client_id: str,
    *,
    registry_path=None,
    manifest=None,
    p0_steering=None,
) -> Dict[str, Any]:
    stage3 = run_stage3_v3(
        call_run,
        client_id,
        registry_path=registry_path,
        manifest=manifest,
        p0_steering=p0_steering,
    )

    if stage3.get("paused_for_human_input"):
        return {
            "stage3": stage3,
            "paused_for_human_input": True,
        }

    campaign_status_matrix = aggregate_campaign_status_matrix(
        stage3["stage2"]["context"],
        stage3["strategy_summary"],
    )

    allowed, reason = transition_call_state_v2(
        call_run, Build1StateV2.CAMPAIGN_STATUS_BUILT.value
    )
    if not allowed:
        raise ValueError(reason)

    if manifest is not None:
        append_snapshot_event(
            manifest,
            "campaign_status_built",
            "Stage 4 built campaign status matrix",
        )

    commitment_audit_lite = build_commitment_audit_lite(
        stage3["stage2"]["context"],
        stage3["narrative_summary_lite"],
        campaign_status_matrix,
    )

    allowed, reason = transition_call_state_v2(
        call_run, Build1StateV2.COMMITMENTS_RECONCILED.value
    )
    if not allowed:
        raise ValueError(reason)

    if manifest is not None:
        append_snapshot_event(
            manifest,
            "commitments_reconciled",
            "Stage 4 reconciled prior commitments to Basecamp",
        )

    return {
        "stage3": stage3,
        "paused_for_human_input": False,
        "campaign_status_matrix": campaign_status_matrix,
        "commitment_audit_lite": commitment_audit_lite,
    }
