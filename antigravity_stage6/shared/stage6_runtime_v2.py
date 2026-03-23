from __future__ import annotations

from typing import Any, Dict, List, Optional

from antigravity_stage1.shared.contracts_runtime_v2 import Build1StateV2
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine_v2 import transition_call_state_v2
from antigravity_stage2.shared.template_resolver import resolve_template_ref
from antigravity_stage5.shared.stage5_runtime_v2 import run_stage5_v2


def _section(key: str, label: str, lines: List[str], *, evidence_refs=None, confidence: str = "medium", suppressed: bool = False, suppression_reason: str = "") -> Dict[str, Any]:
    return {
        "section_key": key,
        "display_label": label,
        "body_lines": lines,
        "evidence_refs": evidence_refs or [],
        "confidence": confidence,
        "is_required": True,
        "is_suppressed": suppressed,
        "suppression_reason": suppression_reason,
    }


def _header_lines(call_run, workspace: Dict[str, Any], template_ref: str) -> List[str]:
    return [
        f"Client: {workspace.get('client_name', workspace.get('client_id', 'Unknown client'))}",
        f"Call run: {call_run.call_run_id}",
        f"Scheduled at: {call_run.scheduled_at}",
        f"DP: {call_run.dp_id}",
        f"Template ref: {template_ref or workspace.get('template_ref', 'not_resolved')}",
    ]


def _meeting_summary_lines(stage5: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    strategy = stage5.get("stage4", {}).get("stage3", {}).get("strategy_summary", {})
    priorities = strategy.get("current_quarter_priorities", [])[:2]
    if priorities:
        lines.append("Primary quarter focus: " + "; ".join(priorities))
    top_win = (stage5.get("win_ranked_list", {}).get("wins") or [{}])[0]
    if top_win.get("headline"):
        lines.append("Lead value proof: " + top_win["headline"])
    blocked_categories = [
        item.get("category")
        for item in stage5.get("stage4", {}).get("campaign_status_matrix", {}).get("categories", [])
        if item.get("blocked") or item.get("waiting_on_client")
    ]
    if blocked_categories:
        lines.append("Risk to cover: " + ", ".join(sorted(set(filter(None, blocked_categories)))))
    downturns = stage5.get("downturn_assessment_lite", {}).get("findings", [])
    supported = [item for item in downturns if item.get("support_level") == "partially_supported"]
    if supported:
        lines.append("Context for weaker performance: " + supported[0].get("likely_cause", "review current performance context"))
    if not lines:
        lines.append("Lead with execution progress and clarify any open approvals before promising outcomes.")
    return lines


def _pending_approvals_lines(stage5: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    for category in stage5.get("stage4", {}).get("campaign_status_matrix", {}).get("categories", []):
        for item in category.get("waiting_on_client", []):
            lines.append(f"{category.get('category', 'General')}: {item}")
    for commitment in stage5.get("stage4", {}).get("commitment_audit_lite", {}).get("commitments", []):
        if commitment.get("status") == "blocked" and commitment.get("matched_basecamp_task"):
            lines.append("Prior promise still blocked: " + commitment["matched_basecamp_task"])
    return lines


def _workstream_lines(stage5: Dict[str, Any]) -> List[str]:
    blocks: List[str] = []
    for category in stage5.get("stage4", {}).get("campaign_status_matrix", {}).get("categories", []):
        parts: List[str] = []
        if category.get("completed_since_last_call"):
            parts.append("Completed: " + "; ".join(category["completed_since_last_call"]))
        if category.get("in_progress"):
            parts.append("In progress: " + "; ".join(category["in_progress"]))
        if category.get("blocked"):
            parts.append("Blocked: " + "; ".join(category["blocked"]))
        if category.get("queued_next"):
            parts.append("Queued next: " + "; ".join(category["queued_next"]))
        if parts:
            blocks.append(f"{category.get('category', 'General')}: " + " | ".join(parts))
    return blocks or ["No classified workstream movement available yet."]


def _wins_lines(stage5: Dict[str, Any]) -> List[str]:
    wins = stage5.get("win_ranked_list", {}).get("wins", [])
    if not wins:
        return ["No strong supported wins yet. Use execution progress as the lead proof of movement."]
    return [(item.get("headline") or item.get("description") or "Supported win") for item in wins[:5]]


def _in_progress_lines(stage5: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    for category in stage5.get("stage4", {}).get("campaign_status_matrix", {}).get("categories", []):
        for item in category.get("in_progress", []):
            lines.append(f"{category.get('category', 'General')}: {item}")
    return lines or ["No active workstream items were available in the current source pull."]


def _next_up_lines(stage5: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    for category in stage5.get("stage4", {}).get("campaign_status_matrix", {}).get("categories", []):
        for item in category.get("queued_next", []):
            lines.append(f"{category.get('category', 'General')}: {item}")
    return lines or ["No queued next items were available in the current source pull."]


def _input_required_lines(stage5: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    for item in stage5.get("ambiguity_list", {}).get("items", []):
        lines.append(f"{item.get('topic')}: {item.get('recommended_input')} ({item.get('why_unclear')})")
    for finding in stage5.get("downturn_assessment_lite", {}).get("findings", []):
        if finding.get("needs_human_input") or finding.get("support_level") == "unsupported":
            lines.append(f"{finding.get('issue')}: confirm cause before stating it as fact")
    return lines or ["No unresolved input required items were generated for this run."]


def _discussion_lines(stage5: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    strategy = stage5.get("stage4", {}).get("stage3", {}).get("strategy_summary", {})
    if strategy.get("current_quarter_priorities"):
        lines.append("Confirm next sprint priorities against the active quarter plan.")
    blocked_categories = [
        item.get("category")
        for item in stage5.get("stage4", {}).get("campaign_status_matrix", {}).get("categories", [])
        if item.get("blocked")
    ]
    if blocked_categories:
        lines.append("Resolve blockers in: " + ", ".join(sorted(set(filter(None, blocked_categories)))))
    if stage5.get("ambiguity_list", {}).get("items"):
        lines.append("Collect answers for highlighted Input Required items before the recap is finalized.")
    return lines or ["Confirm next approvals and sequencing for the coming sprint."]


def _render_preview(sections: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for section in sections:
        if section.get("is_suppressed"):
            continue
        lines = section.get("body_lines", [])
        body = "\n".join(f"- {line}" for line in lines) if lines else ""
        parts.append(f"## {section['display_label']}\n{body}".strip())
    return "\n\n".join(parts)


def run_stage6_v2(
    call_run,
    client_id: str,
    *,
    registry_path: Optional[str] = None,
    manifest=None,
    p0_steering: Optional[list[str]] = None,
) -> Dict[str, Any]:
    stage5 = run_stage5_v2(
        call_run,
        client_id,
        registry_path=registry_path,
        manifest=manifest,
        p0_steering=p0_steering,
    )

    if stage5.get("paused_for_human_input"):
        return {
            "stage5": stage5,
            "paused_for_human_input": True,
            "agenda_draft": None,
            "agenda_preview": None,
        }

    workspace = stage5.get("stage4", {}).get("stage3", {}).get("stage2", {}).get("workspace", {})
    template_payload = resolve_template_ref(workspace, registry_path=registry_path, manifest=manifest)

    sections = [
        _section("header_call_metadata", "Header and Call Metadata", _header_lines(call_run, workspace, template_payload.get("template_ref", "")), confidence="high"),
        _section("meeting_summary_recommended_talk_track", "Meeting Summary / Recommended Talk Track", _meeting_summary_lines(stage5)),
        _section("pending_approvals", "Pending Approvals", _pending_approvals_lines(stage5), suppressed=not bool(_pending_approvals_lines(stage5)), suppression_reason="No pending approvals found."),
        _section("workstream_sections", "Workstream Sections by Campaign Category", _workstream_lines(stage5)),
        _section("wins_highlights", "Wins / Highlights", _wins_lines(stage5)),
        _section("in_progress", "In Progress", _in_progress_lines(stage5)),
        _section("in_queue_next_up", "In Queue / Next Up", _next_up_lines(stage5)),
        _section("input_required", "Input Required", _input_required_lines(stage5), confidence="low"),
        _section("discussion_points_next_decisions", "Discussion Points and Next Decisions", _discussion_lines(stage5)),
    ]

    visible_sections = [s for s in sections if not s.get("is_suppressed")]
    agenda_preview = _render_preview(visible_sections)
    agenda_draft = {
        "type": "pre_call_agenda",
        "call_run_id": call_run.call_run_id,
        "client_id": client_id,
        "content_sections": visible_sections,
        "confidence": "medium",
        "approved": False,
        "rendered_location": template_payload.get("template_ref", "local_preview"),
        "validation_status": "pending_stage7_validation",
        "template_used": template_payload.get("template_content") or "default_template_structure",
    }

    allowed, reason = transition_call_state_v2(call_run, Build1StateV2.AGENDA_RENDERED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, "agenda_rendered", "Stage 6 composed the reviewable pre call agenda draft")

    return {
        "stage5": stage5,
        "paused_for_human_input": False,
        "agenda_draft": agenda_draft,
        "agenda_preview": agenda_preview,
    }
