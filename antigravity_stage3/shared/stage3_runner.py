from __future__ import annotations

from typing import Any, Dict, List, Optional

from antigravity_stage1.shared.contracts_runtime import Build1State
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine import transition_call_state

from .narrative import extract_narrative_continuity
from .prioritization import detect_context_conflicts, prioritize_context_sources, resolve_or_flag_conflicts
from .strategy import extract_strategy_summary


def run_stage3(
    call_run,
    context_bundle: Dict[str, Any],
    client_memory: Dict[str, Any],
    *,
    manifest=None,
) -> Dict[str, Any]:
    prioritized = prioritize_context_sources(context_bundle)
    raw_conflicts = detect_context_conflicts(prioritized)
    conflict_resolution = resolve_or_flag_conflicts(raw_conflicts)
    strategy_summary = extract_strategy_summary(context_bundle, client_memory)
    narrative_summary = extract_narrative_continuity(context_bundle, client_memory)

    ambiguity_candidates: List[Dict[str, str]] = []
    for record in conflict_resolution.conflicts:
        if record.resolution == 'flagged_for_input_required':
            ambiguity_candidates.append(
                {
                    'topic': record.topic,
                    'why_unclear': record.reason,
                    'missing_source': 'higher confidence confirmation needed',
                    'risk_if_assumed': 'Could distort meeting framing or strategy interpretation',
                    'recommended_input': 'DP should confirm which source reflects the current state',
                    'highlight_priority': 'high',
                }
            )

    if manifest is not None:
        append_snapshot_event(manifest, 'context_prioritized', f'Prioritized {len(prioritized)} context entries')
        append_snapshot_event(manifest, 'strategy_summary_extracted', f"Extracted {len(strategy_summary['current_quarter_priorities'])} quarterly priorities")
        append_snapshot_event(manifest, 'narrative_continuity_extracted', f"Extracted {len(narrative_summary['recurring_themes'])} recurring themes")
        if conflict_resolution.conflicts:
            append_snapshot_event(manifest, 'context_conflicts_logged', f'Recorded {len(conflict_resolution.conflicts)} conflict records')

    allowed, reason = transition_call_state(call_run, Build1State.STRATEGY_EXTRACTED.value)
    if not allowed:
        raise ValueError(reason)

    return {
        'prioritized_context': prioritized,
        'strategy_summary': strategy_summary,
        'narrative_summary_lite': narrative_summary,
        'context_conflict_resolution': conflict_resolution.to_dict(),
        'ambiguity_candidates': ambiguity_candidates,
    }
