from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple

from antigravity_stage1.shared.evidence import assess_confidence_band, create_evidence_ref
from antigravity_stage1.shared.taxonomy import normalize_category_alias

STATUS_PREFIX_MAP = {
    'complete': 'completed_since_last_call',
    'completed': 'completed_since_last_call',
    'in progress': 'in_progress',
    'blocked': 'blocked',
    'next': 'queued_next',
    'queued': 'queued_next',
}

CATEGORY_HINTS = {
    'tracking': 'Analytics / Tracking',
    'attribution': 'Analytics / Tracking',
    'analytics': 'Analytics / Tracking',
    'call tracking': 'Analytics / Tracking',
    'event naming': 'Analytics / Tracking',
    'service area page': 'SEO / Copy',
    'page rollout': 'SEO / Copy',
    'seo': 'SEO / Copy',
    'content': 'SEO / Copy',
    'gbp': 'Local SEO / GBP',
    'google business profile': 'Local SEO / GBP',
    'widget': 'Web Development',
    'deployment': 'Web Development',
    'dev': 'Web Development',
    'approval': 'Approvals / Client Dependencies',
    'legal': 'Approvals / Client Dependencies',
}

STOPWORDS = {
    'the', 'a', 'an', 'for', 'and', 'to', 'of', 'in', 'on', 'with', 'from', 'up', 'by',
    'is', 'are', 'be', 'was', 'were', 'this', 'that', 'it', 'as', 'or', 'at', 'into',
    'still', 'next', 'current', 'quarter', 'priority'
}


def _tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r'[a-z0-9]+', text.lower()) if token not in STOPWORDS]


def parse_basecamp_items(basecamp_texts: Iterable[str], basecamp_refs: Iterable[str]) -> List[Dict[str, Any]]:
    refs = list(basecamp_refs)
    items: List[Dict[str, Any]] = []
    for text_index, text in enumerate(basecamp_texts):
        source_ref = refs[text_index] if text_index < len(refs) else f'basecamp_{text_index}'
        for line in text.splitlines():
            stripped = line.strip()
            if ':' not in stripped:
                continue
            prefix, body = stripped.split(':', 1)
            lowered_prefix = prefix.strip().lower()
            status_bucket = STATUS_PREFIX_MAP.get(lowered_prefix)
            if not status_bucket:
                continue
            task_text = body.strip().rstrip('.')
            if not task_text:
                continue
            items.append(
                {
                    'status_bucket': status_bucket,
                    'task_text': task_text,
                    'source_ref': source_ref,
                    'source_type': 'Basecamp',
                }
            )
    return items


def classify_task_category(task_text: str) -> str:
    normalized = normalize_category_alias(task_text)
    if normalized:
        return normalized
    lowered = task_text.lower()
    for hint, category in CATEGORY_HINTS.items():
        if hint in lowered:
            return category
    return 'Strategy'


def detect_blocker_type(task_text: str) -> str:
    lowered = task_text.lower()
    if any(token in lowered for token in ['client', 'approval', 'legal', 'awaiting']):
        return 'client_blocked'
    if any(token in lowered for token in ['internal', 'engineering', 'dependency']):
        return 'agency_blocked'
    return 'none'


def score_quarterly_alignment(task_text: str, strategy_summary: Dict[str, Any]) -> Tuple[int, str]:
    task_tokens = set(_tokenize(task_text))
    best_score = 10
    best_priority = 'No direct quarterly priority match found.'

    for priority in strategy_summary.get('current_quarter_priorities', []):
        priority_tokens = set(_tokenize(priority))
        overlap = len(task_tokens & priority_tokens)
        if overlap >= 3:
            score = 95
        elif overlap == 2:
            score = 80
        elif overlap == 1:
            score = 55
        else:
            score = 10
        if score > best_score:
            best_score = score
            best_priority = f'Aligned to quarter priority: {priority}'

    workstream_goal_map = strategy_summary.get('workstream_goal_map', [])
    category = classify_task_category(task_text)
    for mapping in workstream_goal_map:
        if mapping.get('workstream') == category and best_score < 70:
            best_score = max(best_score, 65)
            best_priority = f'Workstream supports quarter goal: {mapping.get("goal", "")}'
            break

    if best_score <= 20:
        best_priority = 'Weak or unclear quarterly alignment.'

    return best_score, best_priority


def _basecamp_source_refs(context_bundle: Dict[str, Any]) -> List[str]:
    refs: List[str] = []
    for entry in context_bundle.get('provenance_map', []):
        if entry.get('context_key') == 'live_execution_truth[0]':
            refs.extend(entry.get('source_refs', []))
    return refs


def aggregate_campaign_status_matrix(context_bundle: Dict[str, Any], strategy_summary: Dict[str, Any]) -> Dict[str, Any]:
    basecamp_refs = _basecamp_source_refs(context_bundle)
    basecamp_texts = context_bundle.get('live_execution_truth', [])[: len(basecamp_refs) or 1]
    items = parse_basecamp_items(basecamp_texts, basecamp_refs)

    category_map: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            'completed_since_last_call': [],
            'in_progress': [],
            'blocked': [],
            'waiting_on_client': [],
            'queued_next': [],
            'alignment_notes': [],
            'source_refs': [],
            '_scores': [],
            '_evidence': [],
        }
    )
    matched_priority_indexes = set()

    priorities = strategy_summary.get('current_quarter_priorities', [])
    for item in items:
        task_text = item['task_text']
        category = classify_task_category(task_text)
        blocker_type = detect_blocker_type(task_text)
        score, note = score_quarterly_alignment(task_text, strategy_summary)
        bucket = item['status_bucket']

        category_entry = category_map[category]
        category_entry[bucket].append(task_text)
        if blocker_type == 'client_blocked' and task_text not in category_entry['waiting_on_client']:
            category_entry['waiting_on_client'].append(task_text)
        category_entry['alignment_notes'].append(note)
        category_entry['source_refs'].append(item['source_ref'])
        category_entry['_scores'].append(score)
        category_entry['_evidence'].append(
            create_evidence_ref(
                source_type=item['source_type'],
                source_ref=item['source_ref'],
                source_timestamp_or_window='current',
                observation=f'{bucket}: {task_text}',
                confidence='high',
            )
        )
        lowered_task = task_text.lower()
        for idx, priority in enumerate(priorities):
            if len(set(_tokenize(priority)) & set(_tokenize(lowered_task))) >= 1:
                matched_priority_indexes.add(idx)

    if priorities:
        strategy_entry = category_map['Strategy']
        for idx, priority in enumerate(priorities):
            if idx not in matched_priority_indexes:
                strategy_entry['alignment_notes'].append(f'Missing active work mapped to quarter priority: {priority}')
                strategy_entry['_scores'].append(15)

    categories: List[Dict[str, Any]] = []
    for category, entry in category_map.items():
        avg_score = round(sum(entry['_scores']) / len(entry['_scores']), 1) if entry['_scores'] else 0.0
        if entry['blocked']:
            risk_level = 'high' if entry['waiting_on_client'] else 'medium'
        elif entry['queued_next'] and not entry['completed_since_last_call']:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        categories.append(
            {
                'category': category,
                'completed_since_last_call': entry['completed_since_last_call'],
                'in_progress': entry['in_progress'],
                'blocked': entry['blocked'],
                'waiting_on_client': entry['waiting_on_client'],
                'queued_next': entry['queued_next'],
                'risk_level': risk_level,
                'quarterly_alignment_score': avg_score,
                'alignment_notes': sorted(set(entry['alignment_notes'])),
                'source_refs': sorted(set(entry['source_refs'])),
                'confidence': assess_confidence_band(entry['_evidence'], has_contradiction=False),
            }
        )

    categories.sort(key=lambda item: item['category'])
    return {'categories': categories}
