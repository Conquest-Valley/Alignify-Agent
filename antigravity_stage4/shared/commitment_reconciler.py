from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid4

from antigravity_stage1.shared.evidence import assess_confidence_band, create_evidence_ref

STOPWORDS = {
    'the', 'a', 'an', 'for', 'and', 'to', 'of', 'in', 'on', 'with', 'from', 'up', 'by',
    'is', 'are', 'be', 'was', 'were', 'this', 'that', 'it', 'as', 'or', 'at', 'into',
    'before', 'next', 'call', 'team', 'client'
}


def _tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r'[a-z0-9]+', text.lower()) if token not in STOPWORDS]


def _extract_prior_call_date(context_bundle: Dict[str, Any]) -> Optional[str]:
    for text in context_bundle.get('narrative_memory', []):
        match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if match:
            return match.group(1)
    return None


def extract_commitments_from_notes(narrative_summary_lite: Dict[str, Any]) -> List[str]:
    promises = narrative_summary_lite.get('prior_promises', [])
    expanded: List[str] = []
    for promise in promises:
        parts = re.split(r'\band\b', promise, flags=re.IGNORECASE)
        for part in parts:
            cleaned = part.strip().strip('. ')
            if cleaned:
                expanded.append(cleaned)
    return expanded


def _flatten_campaign_tasks(campaign_status_matrix: Dict[str, Any]) -> List[Dict[str, str]]:
    tasks: List[Dict[str, str]] = []
    for category in campaign_status_matrix.get('categories', []):
        for bucket in ['completed_since_last_call', 'in_progress', 'blocked', 'waiting_on_client', 'queued_next']:
            for task in category.get(bucket, []):
                tasks.append(
                    {
                        'category': category['category'],
                        'bucket': bucket,
                        'task_text': task,
                        'source_ref': (category.get('source_refs') or ['unknown'])[0],
                    }
                )
    return tasks


def match_commitments_to_tasks(commitments: Sequence[str], campaign_status_matrix: Dict[str, Any]) -> List[Dict[str, Any]]:
    flattened_tasks = _flatten_campaign_tasks(campaign_status_matrix)
    matches: List[Dict[str, Any]] = []

    for commitment in commitments:
        commitment_tokens = set(_tokenize(commitment))
        best_match: Optional[Dict[str, str]] = None
        best_overlap = 0
        for task in flattened_tasks:
            overlap = len(commitment_tokens & set(_tokenize(task['task_text'])))
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = task
        matches.append(
            {
                'commitment_text': commitment,
                'matched_task': best_match,
                'overlap': best_overlap,
            }
        )
    return matches


def classify_commitment_state(match_record: Dict[str, Any]) -> str:
    task = match_record.get('matched_task')
    overlap = match_record.get('overlap', 0)
    if not task or overlap == 0:
        return 'unmatched'
    bucket = task['bucket']
    if bucket == 'completed_since_last_call':
        return 'completed'
    if bucket == 'in_progress':
        return 'active'
    if bucket == 'blocked' or bucket == 'waiting_on_client':
        return 'blocked'
    if bucket == 'queued_next':
        return 'stale'
    return 'unmatched'


def build_commitment_audit_lite(
    context_bundle: Dict[str, Any],
    narrative_summary_lite: Dict[str, Any],
    campaign_status_matrix: Dict[str, Any],
) -> Dict[str, Any]:
    commitments = extract_commitments_from_notes(narrative_summary_lite)
    matched = match_commitments_to_tasks(commitments, campaign_status_matrix)
    source_call_date = _extract_prior_call_date(context_bundle)

    audit_items: List[Dict[str, Any]] = []
    for match in matched:
        state = classify_commitment_state(match)
        task = match.get('matched_task')
        evidence_refs = []
        if task:
            evidence_refs.append(
                create_evidence_ref(
                    source_type='Basecamp',
                    source_ref=task['source_ref'],
                    source_timestamp_or_window='current',
                    observation=f"{task['bucket']}: {task['task_text']}",
                    confidence='high' if state in {'completed', 'active'} else 'medium',
                )
            )
        confidence = assess_confidence_band(evidence_refs, has_contradiction=False)
        audit_items.append(
            {
                'commitment_id': f'commit_{uuid4().hex[:10]}',
                'source_call_date': source_call_date,
                'commitment_text': match['commitment_text'],
                'owner': 'agency',
                'due_date': None,
                'matched_basecamp_task': task['task_text'] if task else None,
                'status': state,
                'evidence_refs': [ref.to_dict() for ref in evidence_refs],
                'confidence': confidence,
            }
        )
    return {'commitments': audit_items}
