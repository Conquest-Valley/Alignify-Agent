from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Tuple

from antigravity_stage1.shared.contracts_runtime import Build1State, ManualOverrideLog, OverrideEntry, utc_now_iso
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine import transition_call_state
from antigravity_stage1.shared.validation import validate_section_requirements


def validate_claim_evidence(section: Dict[str, Any]) -> Dict[str, Any]:
    evidence_refs = section.get('evidence_refs', []) or []
    has_evidence = len(evidence_refs) > 0
    return {
        'section_name': section.get('section_name', 'Unknown section'),
        'has_evidence': has_evidence,
        'evidence_count': len(evidence_refs),
        'missing_evidence': not has_evidence,
    }


def validate_claim_freshness(
    section: Dict[str, Any],
    freshness_by_source: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    freshness_by_source = freshness_by_source or {}
    stale_refs: List[str] = []
    unknown_refs: List[str] = []
    for evidence in section.get('evidence_refs', []) or []:
        source_ref = evidence.get('source_ref')
        if not source_ref:
            unknown_refs.append('missing_source_ref')
            continue
        assessment = freshness_by_source.get(source_ref)
        if assessment is None:
            continue
        status = assessment.get('freshness_status', 'unknown')
        if status == 'stale':
            stale_refs.append(source_ref)
        elif status == 'unknown':
            unknown_refs.append(source_ref)
    freshness_ok = len(stale_refs) == 0
    return {
        'section_name': section.get('section_name', 'Unknown section'),
        'freshness_ok': freshness_ok,
        'stale_refs': stale_refs,
        'unknown_refs': unknown_refs,
    }


def _build_section_inputs(
    agenda_draft: Dict[str, Any],
    section_context: Optional[Dict[str, Dict[str, bool]]] = None,
) -> Dict[str, Dict[str, bool]]:
    section_context = deepcopy(section_context or {})
    for section in agenda_draft.get('content_sections', []):
        name = section.get('section_name', 'Unknown section')
        section_context.setdefault(name, {})
        section_context[name].setdefault('must_have_evidence', len(section.get('evidence_refs', []) or []) > 0)
        section_context[name].setdefault('must_have_strategic_relevance', 'strategy' in (section.get('content', '').lower()))
    return section_context


def validate_section_readiness(
    call_run_id: str,
    agenda_draft: Dict[str, Any],
    section_context: Optional[Dict[str, Dict[str, bool]]] = None,
):
    section_inputs = _build_section_inputs(agenda_draft, section_context)
    return validate_section_requirements(call_run_id, section_inputs)


def downgrade_or_remove_unsupported_claims(
    agenda_draft: Dict[str, Any],
    freshness_by_source: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    downgraded = deepcopy(agenda_draft)
    corrections: List[Dict[str, Any]] = []
    corrected_sections: List[Dict[str, Any]] = []

    for section in downgraded.get('content_sections', []):
        evidence_check = validate_claim_evidence(section)
        freshness_check = validate_claim_freshness(section, freshness_by_source)
        if evidence_check['missing_evidence'] or not freshness_check['freshness_ok']:
            original_content = section.get('content', '')
            input_required_note = 'Input Required: supporting evidence is missing or stale for this section.'
            section['content'] = input_required_note
            section['confidence'] = 'low'
            section['evidence_refs'] = []
            corrections.append(
                {
                    'section_name': section.get('section_name', 'Unknown section'),
                    'reason': 'missing_evidence_or_stale_freshness',
                    'original_content': original_content,
                    'corrected_content': input_required_note,
                }
            )
        corrected_sections.append(section)

    downgraded['content_sections'] = corrected_sections
    downgraded['validation_status'] = 'corrected' if corrections else 'passed'
    return downgraded, corrections


def finalize_run_snapshot(
    manifest,
    *,
    strategy_ref: Optional[str] = None,
    template_ref: Optional[str] = None,
    validation_version: str = 'v1',
):
    if strategy_ref:
        manifest.quarterly_strategy_ref_used = strategy_ref
    if template_ref:
        manifest.template_ref_used = template_ref
    manifest.validation_version = validation_version
    append_snapshot_event(manifest, 'snapshot_finalized', 'Stage 7 finalized validation metadata for DP review')
    return manifest


def capture_manual_override(
    log: ManualOverrideLog,
    *,
    section: str,
    original_text: str,
    edited_text: str,
    reason_code: str,
) -> ManualOverrideLog:
    log.overrides.append(
        OverrideEntry(
            section=section,
            original_text=original_text,
            edited_text=edited_text,
            reason_code=reason_code,
            timestamp=utc_now_iso(),
        )
    )
    return log


def mark_awaiting_dp_review(call_run) -> None:
    ok, reason = transition_call_state(call_run, Build1State.AWAITING_DP_PRE_CALL_REVIEW.value)
    if not ok:
        raise ValueError(reason)


def run_stage7(
    call_run,
    agenda_draft: Dict[str, Any],
    *,
    manifest=None,
    section_context: Optional[Dict[str, Dict[str, bool]]] = None,
    freshness_by_source: Optional[Dict[str, Dict[str, Any]]] = None,
    manual_edits: Optional[List[Dict[str, str]]] = None,
    strategy_ref: Optional[str] = None,
    template_ref: Optional[str] = None,
    validation_version: str = 'v1',
) -> Dict[str, Any]:
    corrected_agenda, corrections = downgrade_or_remove_unsupported_claims(
        agenda_draft,
        freshness_by_source=freshness_by_source,
    )
    validation_report = validate_section_readiness(
        call_run.call_run_id,
        corrected_agenda,
        section_context=section_context,
    )

    override_log = ManualOverrideLog(call_run_id=call_run.call_run_id, dp_id=call_run.dp_id)
    for edit in manual_edits or []:
        capture_manual_override(
            override_log,
            section=edit['section'],
            original_text=edit.get('original_text', ''),
            edited_text=edit.get('edited_text', ''),
            reason_code=edit.get('reason_code', 'dp_edit'),
        )

    if manifest is not None:
        finalize_run_snapshot(
            manifest,
            strategy_ref=strategy_ref,
            template_ref=template_ref or corrected_agenda.get('rendered_location'),
            validation_version=validation_version,
        )
        append_snapshot_event(manifest, 'validation_completed', f"Stage 7 corrections: {len(corrections)}")
        if override_log.overrides:
            append_snapshot_event(manifest, 'manual_overrides_captured', f"Overrides captured: {len(override_log.overrides)}")

    corrected_agenda['validation_status'] = 'passed' if validation_report.overall_valid and not corrections else 'needs_review'
    mark_awaiting_dp_review(call_run)
    if manifest is not None:
        append_snapshot_event(manifest, 'awaiting_dp_pre_call_review', 'Run paused for DP review')

    return {
        'agenda_draft': corrected_agenda,
        'validation_report': validation_report.to_dict(),
        'manual_override_log': override_log.to_dict(),
        'corrections': corrections,
        'review_state': call_run.current_state,
    }
