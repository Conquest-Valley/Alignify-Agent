from __future__ import annotations

from typing import Any, Dict, Optional

from antigravity_stage1.shared.contracts_runtime import Build1State
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine import transition_call_state
from antigravity_stage2.shared.stage2_runtime_v2 import run_stage2_v2

from .stage3_runner import run_stage3


def run_stage3_v2(
    call_run,
    client_id: str,
    *,
    registry_path: Optional[str] = None,
    manifest=None,
    p0_steering: Optional[list[str]] = None,
) -> Dict[str, Any]:
    stage2 = run_stage2_v2(
        call_run,
        client_id,
        registry_path=registry_path,
        manifest=manifest,
        p0_steering=p0_steering,
    )

    context_health = stage2["context_health"]
    if context_health.get("should_pause"):
        if manifest is not None:
            append_snapshot_event(
                manifest,
                "context_pause_for_human_input",
                "Stage 3 skipped because Stage 2 context health required human input.",
            )
        allowed, reason = transition_call_state(call_run, Build1State.NEEDS_HUMAN_INPUT.value)
        if not allowed:
            raise ValueError(reason)
        return {
            "stage2": stage2,
            "paused_for_human_input": True,
            "pause_reason": "Stage 2 context health requires human input before strategy reasoning.",
            "strategy_summary": None,
            "narrative_summary_lite": None,
            "context_conflict_resolution": {"conflicts": []},
            "ambiguity_candidates": [
                {
                    "topic": "context_load",
                    "why_unclear": "Critical or numerous sources were missing during Stage 2 retrieval.",
                    "missing_source": ", ".join(context_health.get("missing_sources", [])) or "multiple sources",
                    "risk_if_assumed": "Strategy reasoning could be distorted by incomplete context.",
                    "recommended_input": "Review Stage 2 context health and repair or confirm the missing sources.",
                    "highlight_priority": "high",
                }
            ],
        }

    stage3 = run_stage3(
        call_run,
        stage2["context"],
        stage2["memory"],
        manifest=manifest,
    )

    return {
        "stage2": stage2,
        "paused_for_human_input": False,
        **stage3,
    }
