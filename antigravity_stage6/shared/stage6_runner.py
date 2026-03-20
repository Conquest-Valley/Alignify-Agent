from __future__ import annotations

from typing import Any, Dict, Optional

from antigravity_stage1.shared.contracts_runtime import Build1State
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine import transition_call_state
from antigravity_stage2.shared.template_resolver import resolve_template_ref

from .agenda_composer import render_agenda_draft


def run_stage6(
    call_run,
    workspace_bundle: Dict[str, Any],
    strategy_summary: Dict[str, Any],
    campaign_status_matrix: Dict[str, Any],
    commitment_audit_lite: Dict[str, Any],
    win_ranked_list: Dict[str, Any],
    downturn_assessment_lite: Dict[str, Any],
    ambiguity_list: Dict[str, Any],
    *,
    manifest=None,
    registry_path: Optional[str] = None,
) -> Dict[str, Any]:
    template_payload = resolve_template_ref(workspace_bundle, registry_path=registry_path, manifest=manifest)
    rendered = render_agenda_draft(
        call_run,
        workspace_bundle,
        strategy_summary,
        campaign_status_matrix,
        commitment_audit_lite,
        win_ranked_list,
        downturn_assessment_lite,
        ambiguity_list,
        template_content=template_payload['template_content'],
        template_ref=template_payload['template_ref'],
    )
    allowed, reason = transition_call_state(call_run, Build1State.AGENDA_RENDERED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, 'agenda_rendered', 'Stage 6 composed the reviewable pre call agenda draft')
    return rendered
