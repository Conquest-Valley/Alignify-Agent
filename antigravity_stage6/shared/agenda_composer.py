from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from antigravity_stage1.shared.evidence import assess_confidence_band

SECTION_ORDER = [
    'Header and call metadata',
    'Meeting Summary / Recommended talk track',
    'Pending Approvals',
    'Analytics / Tracking',
    'Top Performing Pages or key performance views',
    'GBP performance if applicable',
    'Workstream sections by campaign category',
    'Wins / Highlights',
    'In Progress',
    'In Queue / Next Up',
    'Input Required',
    'Discussion points and next decisions',
]


def _flatten_evidence_refs(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    flattened: List[Dict[str, Any]] = []
    for item in items:
        for evidence in item.get('evidence_refs', []):
            flattened.append(evidence)
    return flattened


def _build_header_section(call_run, workspace_bundle: Dict[str, Any], template_ref: Optional[str]) -> Dict[str, Any]:
    content = (
        f"Client: {workspace_bundle.get('client_name', workspace_bundle.get('client_id', 'Unknown client'))}\n"
        f"Call run: {call_run.call_run_id}\n"
        f"Scheduled at: {call_run.scheduled_at}\n"
        f"DP: {call_run.dp_id}\n"
        f"Template ref: {template_ref or workspace_bundle.get('template_ref', 'not_resolved')}"
    )
    return {
        'section_name': 'Header and call metadata',
        'content': content,
        'evidence_refs': [],
        'confidence': 'high',
    }


def build_meeting_summary_section(
    strategy_summary: Dict[str, Any],
    campaign_status_matrix: Dict[str, Any],
    win_ranked_list: Dict[str, Any],
    downturn_assessment_lite: Dict[str, Any],
) -> Dict[str, Any]:
    priorities = strategy_summary.get('current_quarter_priorities', [])[:2]
    top_win = (win_ranked_list.get('wins') or [{}])[0]
    blocked_categories = [
        item['category'] for item in campaign_status_matrix.get('categories', []) if item.get('blocked') or item.get('waiting_on_client')
    ]
    supported_downturns = [
        item for item in downturn_assessment_lite.get('findings', []) if item.get('support_level') in {'supported', 'partial'}
    ]

    lines = []
    if priorities:
        lines.append('Primary quarter focus: ' + '; '.join(priorities))
    if top_win.get('headline'):
        lines.append('Lead value proof: ' + top_win['headline'])
    if blocked_categories:
        lines.append('Risk to cover: ' + ', '.join(sorted(set(blocked_categories))))
    if supported_downturns:
        lines.append('Context for weaker performance: ' + supported_downturns[0].get('candidate_cause', 'review current performance context'))
    if not lines:
        lines.append('Lead with execution progress and clarify any open approvals before promising outcomes.')

    evidence = _flatten_evidence_refs([top_win] + supported_downturns)
    return {
        'section_name': 'Meeting Summary / Recommended talk track',
        'content': '\n'.join(f'- {line}' for line in lines),
        'evidence_refs': evidence,
        'confidence': assess_confidence_band([], has_contradiction=False) if not evidence else assess_confidence_band([], False),
    }


def build_pending_approvals_section(campaign_status_matrix: Dict[str, Any], commitment_audit_lite: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    lines: List[str] = []
    evidence: List[Dict[str, Any]] = []
    for category in campaign_status_matrix.get('categories', []):
        for item in category.get('waiting_on_client', []):
            lines.append(f"{category['category']}: {item}")
            if category.get('source_refs'):
                evidence.append({
                    'source_type': 'Basecamp',
                    'source_ref': category['source_refs'][0],
                    'source_timestamp_or_window': 'current',
                    'observation': item,
                    'confidence': category.get('confidence', 'medium'),
                })
    for commitment in commitment_audit_lite.get('commitments', []):
        if commitment.get('status') == 'blocked' and commitment.get('matched_basecamp_task'):
            lines.append('Prior promise still blocked: ' + commitment['matched_basecamp_task'])
            evidence.extend(commitment.get('evidence_refs', []))
    if not lines:
        return None
    return {
        'section_name': 'Pending Approvals',
        'content': '\n'.join(f'- {line}' for line in lines),
        'evidence_refs': evidence,
        'confidence': 'medium' if lines else 'low',
    }


def build_analytics_section(win_ranked_list: Dict[str, Any], downturn_assessment_lite: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    lines: List[str] = []
    evidence: List[Dict[str, Any]] = []
    for win in win_ranked_list.get('wins', []):
        if win.get('type') == 'performance':
            lines.append(win.get('headline') or win.get('description', 'Performance movement detected'))
            evidence.extend(win.get('evidence_refs', []))
    for finding in downturn_assessment_lite.get('findings', []):
        if finding.get('support_level') in {'supported', 'partial'}:
            lines.append(f"Watch item: {finding.get('issue')} due to {finding.get('candidate_cause')}")
            evidence.extend(finding.get('evidence_refs', []))
    if not lines:
        return None
    return {
        'section_name': 'Analytics / Tracking',
        'content': '\n'.join(f'- {line}' for line in lines),
        'evidence_refs': evidence,
        'confidence': 'medium' if lines else 'low',
    }


def build_top_pages_section(win_ranked_list: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    page_lines = []
    evidence = []
    for win in win_ranked_list.get('wins', []):
        headline = (win.get('headline') or '').lower()
        if 'page' in headline or 'gbp' in headline or 'service' in headline:
            page_lines.append(win.get('headline') or win.get('description', 'Relevant page movement'))
            evidence.extend(win.get('evidence_refs', []))
    if not page_lines:
        return None
    return {
        'section_name': 'Top Performing Pages or key performance views',
        'content': '\n'.join(f'- {line}' for line in page_lines[:3]),
        'evidence_refs': evidence,
        'confidence': 'medium',
    }


def build_gbp_section(win_ranked_list: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    gbp_lines = []
    evidence = []
    for win in win_ranked_list.get('wins', []):
        text = ' '.join(filter(None, [win.get('headline'), win.get('description')])).lower()
        if 'gbp' in text or 'google business profile' in text:
            gbp_lines.append(win.get('headline') or win.get('description'))
            evidence.extend(win.get('evidence_refs', []))
    if not gbp_lines:
        return None
    return {
        'section_name': 'GBP performance if applicable',
        'content': '\n'.join(f'- {line}' for line in gbp_lines[:3]),
        'evidence_refs': evidence,
        'confidence': 'medium',
    }


def build_workstream_sections(campaign_status_matrix: Dict[str, Any]) -> Dict[str, Any]:
    blocks: List[str] = []
    evidence: List[Dict[str, Any]] = []
    for category in campaign_status_matrix.get('categories', []):
        parts: List[str] = []
        if category.get('completed_since_last_call'):
            parts.append('Completed: ' + '; '.join(category['completed_since_last_call']))
        if category.get('in_progress'):
            parts.append('In progress: ' + '; '.join(category['in_progress']))
        if category.get('blocked'):
            parts.append('Blocked: ' + '; '.join(category['blocked']))
        if category.get('queued_next'):
            parts.append('Queued next: ' + '; '.join(category['queued_next']))
        if not parts:
            continue
        blocks.append(f"{category['category']}\n  - " + '\n  - '.join(parts))
        if category.get('source_refs'):
            evidence.append({
                'source_type': 'Basecamp',
                'source_ref': category['source_refs'][0],
                'source_timestamp_or_window': 'current',
                'observation': f"Workstream status for {category['category']}",
                'confidence': category.get('confidence', 'medium'),
            })
    if not blocks:
        blocks.append('No classified workstream movement available yet.')
    return {
        'section_name': 'Workstream sections by campaign category',
        'content': '\n\n'.join(blocks),
        'evidence_refs': evidence,
        'confidence': 'medium' if evidence else 'low',
    }


def build_wins_section(win_ranked_list: Dict[str, Any]) -> Dict[str, Any]:
    wins = win_ranked_list.get('wins', [])
    if not wins:
        return {
            'section_name': 'Wins / Highlights',
            'content': '- No strong supported wins yet. Use execution progress as the lead proof of movement.',
            'evidence_refs': [],
            'confidence': 'low',
        }
    lines = []
    evidence = []
    for win in wins[:5]:
        lines.append((win.get('headline') or win.get('description', 'Supported win')).strip())
        evidence.extend(win.get('evidence_refs', []))
    return {
        'section_name': 'Wins / Highlights',
        'content': '\n'.join(f'- {line}' for line in lines),
        'evidence_refs': evidence,
        'confidence': 'medium' if evidence else 'low',
    }


def build_in_progress_section(campaign_status_matrix: Dict[str, Any]) -> Dict[str, Any]:
    lines = []
    evidence = []
    for category in campaign_status_matrix.get('categories', []):
        for item in category.get('in_progress', []):
            lines.append(f"{category['category']}: {item}")
            if category.get('source_refs'):
                evidence.append({
                    'source_type': 'Basecamp',
                    'source_ref': category['source_refs'][0],
                    'source_timestamp_or_window': 'current',
                    'observation': item,
                    'confidence': category.get('confidence', 'medium'),
                })
    if not lines:
        lines.append('No active workstream items were available in the current source pull.')
    return {
        'section_name': 'In Progress',
        'content': '\n'.join(f'- {line}' for line in lines),
        'evidence_refs': evidence,
        'confidence': 'medium' if evidence else 'low',
    }


def build_next_up_section(campaign_status_matrix: Dict[str, Any]) -> Dict[str, Any]:
    lines = []
    evidence = []
    for category in campaign_status_matrix.get('categories', []):
        for item in category.get('queued_next', []):
            lines.append(f"{category['category']}: {item}")
            if category.get('source_refs'):
                evidence.append({
                    'source_type': 'Basecamp',
                    'source_ref': category['source_refs'][0],
                    'source_timestamp_or_window': 'current',
                    'observation': item,
                    'confidence': category.get('confidence', 'medium'),
                })
    if not lines:
        lines.append('No queued next items were available in the current source pull.')
    return {
        'section_name': 'In Queue / Next Up',
        'content': '\n'.join(f'- {line}' for line in lines),
        'evidence_refs': evidence,
        'confidence': 'medium' if evidence else 'low',
    }


def build_input_required_section(
    ambiguity_list: Dict[str, Any],
    downturn_assessment_lite: Dict[str, Any],
) -> Dict[str, Any]:
    lines = []
    for item in ambiguity_list.get('items', []):
        lines.append(f"{item.get('topic')}: {item.get('recommended_input')} ({item.get('why_unclear')})")
    for finding in downturn_assessment_lite.get('findings', []):
        if finding.get('needs_human_input') or finding.get('support_level') == 'unsupported':
            lines.append(f"{finding.get('issue')}: confirm cause before stating it as fact")
    if not lines:
        lines.append('No unresolved input required items were generated for this run.')
    return {
        'section_name': 'Input Required',
        'content': '\n'.join(f'- {line}' for line in lines),
        'evidence_refs': [],
        'confidence': 'low' if lines else 'high',
    }


def build_discussion_points_section(
    strategy_summary: Dict[str, Any],
    campaign_status_matrix: Dict[str, Any],
    ambiguity_list: Dict[str, Any],
) -> Dict[str, Any]:
    lines = []
    if strategy_summary.get('current_quarter_priorities'):
        lines.append('Confirm next sprint priorities against the active quarter plan.')
    blocked_categories = [item['category'] for item in campaign_status_matrix.get('categories', []) if item.get('blocked')]
    if blocked_categories:
        lines.append('Resolve blockers in: ' + ', '.join(sorted(set(blocked_categories))))
    if ambiguity_list.get('items'):
        lines.append('Collect answers for highlighted Input Required items before the recap is finalized.')
    if not lines:
        lines.append('Confirm next approvals and sequencing for the coming sprint.')
    return {
        'section_name': 'Discussion points and next decisions',
        'content': '\n'.join(f'- {line}' for line in lines),
        'evidence_refs': [],
        'confidence': 'medium',
    }


def apply_section_fallback_rules(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for section in sections:
        content = (section.get('content') or '').strip()
        if not content:
            continue
        if section['section_name'] in {'Top Performing Pages or key performance views', 'GBP performance if applicable'}:
            if 'No ' in content or content == '-':
                continue
        filtered.append(section)
    return filtered


def render_agenda_draft(
    call_run,
    workspace_bundle: Dict[str, Any],
    strategy_summary: Dict[str, Any],
    campaign_status_matrix: Dict[str, Any],
    commitment_audit_lite: Dict[str, Any],
    win_ranked_list: Dict[str, Any],
    downturn_assessment_lite: Dict[str, Any],
    ambiguity_list: Dict[str, Any],
    *,
    template_content: Optional[str] = None,
    template_ref: Optional[str] = None,
) -> Dict[str, Any]:
    sections = [
        _build_header_section(call_run, workspace_bundle, template_ref),
        build_meeting_summary_section(strategy_summary, campaign_status_matrix, win_ranked_list, downturn_assessment_lite),
        build_pending_approvals_section(campaign_status_matrix, commitment_audit_lite),
        build_analytics_section(win_ranked_list, downturn_assessment_lite),
        build_top_pages_section(win_ranked_list),
        build_gbp_section(win_ranked_list),
        build_workstream_sections(campaign_status_matrix),
        build_wins_section(win_ranked_list),
        build_in_progress_section(campaign_status_matrix),
        build_next_up_section(campaign_status_matrix),
        build_input_required_section(ambiguity_list, downturn_assessment_lite),
        build_discussion_points_section(strategy_summary, campaign_status_matrix, ambiguity_list),
    ]
    ordered_sections = apply_section_fallback_rules([section for section in sections if section])

    section_lookup = {section['section_name']: section for section in ordered_sections}
    final_sections = [section_lookup[name] for name in SECTION_ORDER if name in section_lookup]

    agenda_evidence: List[Dict[str, Any]] = []
    for section in final_sections:
        agenda_evidence.extend(section.get('evidence_refs', []))

    agenda_draft = {
        'type': 'pre_call_agenda',
        'call_run_id': call_run.call_run_id,
        'content_sections': final_sections,
        'evidence_refs': agenda_evidence,
        'confidence': 'medium' if agenda_evidence else 'low',
        'approved': False,
        'rendered_location': template_ref or 'local_preview',
        'validation_status': 'pending_stage7_validation',
        'template_used': template_content or 'default_template_structure',
    }
    preview = '\n\n'.join([f"## {section['section_name']}\n{section['content']}" for section in final_sections])
    return {'agenda_draft': agenda_draft, 'agenda_preview': preview}
