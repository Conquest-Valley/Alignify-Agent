from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from antigravity_stage1.shared.contracts_runtime_v2 import Build1StateV2
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine_v2 import transition_call_state_v2
from antigravity_stage6.shared.stage6_runtime_v2 import run_stage6_v2


def _validate_section_evidence(section: Dict[str, Any]) -> Dict[str, Any]:
    evidence_refs = section.get("evidence_refs", []) or []
    return {
        "section_key": section.get("section_key", "unknown_section"),
        "has_evidence": len(evidence_refs) > 0,
        "evidence_count": len(evidence_refs),
        "missing_evidence": len(evidence_refs) == 0,
    }


def _validate_section_confidence(section: Dict[str, Any]) -> Dict[str, Any]:
    confidence = section.get("confidence", "low")
    return {
        "section_key": section.get("section_key", "unknown_section"),
        "confidence": confidence,
        "confidence_ok": confidence in {"high", "medium"},
    }


def _correct_section(section: Dict[str, Any], reason: str) -> Dict[str, Any]:
    corrected = deepcopy(section)
    corrected["body_lines"] = [f"Input Required: {reason}"]
    corrected["confidence"] = "low"
    corrected["evidence_refs"] = []
    return corrected


def _validate_and_correct_agenda(agenda_draft: Dict[str, Any]) -> tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    corrected = deepcopy(agenda_draft)
    section_results: List[Dict[str, Any]] = []
    corrections: List[Dict[str, Any]] = []
    new_sections: List[Dict[str, Any]] = []

    for section in corrected.get("content_sections", []):
        evidence_check = _validate_section_evidence(section)
        confidence_check = _validate_section_confidence(section)
        requires_intervention = False
        notes: List[str] = []

        if section.get("section_key") != "header_call_metadata" and evidence_check["missing_evidence"]:
            requires_intervention = True
            notes.append("missing_evidence")
        if not confidence_check["confidence_ok"]:
            notes.append("low_confidence")

        if requires_intervention:
            original_lines = list(section.get("body_lines", []))
            section = _correct_section(section, "supporting evidence is missing for this section before DP review")
            corrections.append(
                {
                    "section_key": section.get("section_key", "unknown_section"),
                    "reason": "missing_evidence",
                    "original_body_lines": original_lines,
                    "corrected_body_lines": section.get("body_lines", []),
                }
            )

        section_results.append(
            {
                "section_key": section.get("section_key", "unknown_section"),
                "status": "fail" if requires_intervention else ("warning" if notes else "pass"),
                "requires_intervention": requires_intervention,
                "notes": notes,
                "evidence_count": evidence_check["evidence_count"],
                "confidence": section.get("confidence", "low"),
            }
        )
        new_sections.append(section)

    corrected["content_sections"] = new_sections
    corrected["validation_status"] = "needs_review" if corrections else "passed"
    return corrected, section_results, corrections


def _determine_overall_status(section_results: List[Dict[str, Any]]) -> str:
    if any(item.get("status") == "fail" for item in section_results):
        return "fail"
    if any(item.get("status") == "warning" for item in section_results):
        return "warning"
    return "pass"


def _capture_manual_overrides(call_run, manual_edits: Optional[List[Dict[str, str]]]) -> Dict[str, Any]:
    overrides = []
    for edit in manual_edits or []:
        overrides.append(
            {
                "section": edit.get("section", "unknown_section"),
                "original_text": edit.get("original_text", ""),
                "edited_text": edit.get("edited_text", ""),
                "reason_code": edit.get("reason_code", "dp_edit"),
                "timestamp": edit.get("timestamp", "manual"),
                "editor": edit.get("editor", call_run.dp_id),
            }
        )
    return {
        "call_run_id": call_run.call_run_id,
        "dp_id": call_run.dp_id,
        "overrides": overrides,
    }


def run_stage7_v2(
    call_run,
    client_id: str,
    *,
    registry_path: Optional[str] = None,
    manifest=None,
    p0_steering: Optional[list[str]] = None,
    manual_edits: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    stage6 = run_stage6_v2(
        call_run,
        client_id,
        registry_path=registry_path,
        manifest=manifest,
        p0_steering=p0_steering,
    )

    if stage6.get("paused_for_human_input"):
        return {
            "stage6": stage6,
            "paused_for_human_input": True,
            "agenda_draft": None,
            "validation_report": None,
            "manual_override_log": None,
            "corrections": [],
            "review_state": call_run.current_state,
        }

    corrected_agenda, section_results, corrections = _validate_and_correct_agenda(stage6["agenda_draft"])
    overall_status = _determine_overall_status(section_results)
    manual_override_log = _capture_manual_overrides(call_run, manual_edits)

    if manifest is not None:
        append_snapshot_event(manifest, "validation_completed", f"Stage 7 corrections: {len(corrections)}")
        if manual_override_log.get("overrides"):
            append_snapshot_event(manifest, "manual_overrides_captured", f"Overrides captured: {len(manual_override_log['overrides'])}")

    allowed, reason = transition_call_state_v2(call_run, Build1StateV2.AWAITING_DP_PRE_CALL_REVIEW.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, "awaiting_dp_pre_call_review", "Run paused for DP review")

    return {
        "stage6": stage6,
        "paused_for_human_input": False,
        "agenda_draft": corrected_agenda,
        "validation_report": {
            "call_run_id": call_run.call_run_id,
            "section_results": section_results,
            "overall_status": overall_status,
        },
        "manual_override_log": manual_override_log,
        "corrections": corrections,
        "review_state": call_run.current_state,
    }
