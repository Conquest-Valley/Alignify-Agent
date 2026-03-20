from __future__ import annotations

from typing import Any, Dict, List


def build_ambiguity_list(
    context_conflict_resolution: Dict[str, Any],
    campaign_status_matrix: Dict[str, Any],
    downturn_assessment_lite: Dict[str, Any],
    narrative_summary_lite: Dict[str, Any],
) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []

    for conflict in context_conflict_resolution.get('conflicts', []):
        if conflict.get('resolution') == 'flagged_for_input_required':
            items.append(
                {
                    'topic': conflict.get('topic', 'Context conflict'),
                    'why_unclear': conflict.get('reason', 'Sources conflict and cannot be safely reconciled.'),
                    'missing_source': conflict.get('lower_priority_source', 'clarification needed'),
                    'risk_if_assumed': 'Agenda may overstate or misframe the account status.',
                    'recommended_input': 'DP should confirm which framing is appropriate for the call.',
                    'highlight_priority': 'high',
                }
            )

    for category in campaign_status_matrix.get('categories', []):
        if category.get('waiting_on_client'):
            items.append(
                {
                    'topic': f"Pending approval in {category['category']}",
                    'why_unclear': 'Client dependent or approval dependent work is still open.',
                    'missing_source': 'Confirmed approval status or due date',
                    'risk_if_assumed': 'The agenda may overpromise delivery timing.',
                    'recommended_input': 'Confirm approval owner, status, and expected timing.',
                    'highlight_priority': 'high',
                }
            )

    for finding in downturn_assessment_lite.get('findings', []):
        if finding.get('needs_human_input'):
            items.append(
                {
                    'topic': finding.get('metric', 'Downturn explanation'),
                    'why_unclear': finding.get('candidate_cause', 'Cause is not yet supported.'),
                    'missing_source': 'Stronger causal evidence or manual context',
                    'risk_if_assumed': 'Weak performance could be explained incorrectly.',
                    'recommended_input': 'DP should validate whether there is a known explanation worth stating.',
                    'highlight_priority': 'high' if finding.get('support_level') == 'unsupported' else 'medium',
                }
            )

    for unresolved in narrative_summary_lite.get('unresolved_topics', []):
        lowered = unresolved.lower()
        if any(token in lowered for token in ['approval', 'delay', 'timing']):
            items.append(
                {
                    'topic': unresolved,
                    'why_unclear': 'Recent call history shows this topic is still unresolved.',
                    'missing_source': 'Current owner, status, or ETA',
                    'risk_if_assumed': 'The call may gloss over a repeated blocker.',
                    'recommended_input': 'Surface this explicitly and confirm next step ownership.',
                    'highlight_priority': 'medium',
                }
            )

    deduped: List[Dict[str, Any]] = []
    seen = set()
    for item in items:
        key = (item['topic'], item['why_unclear'])
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return {'items': deduped}
