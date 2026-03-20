from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from antigravity_stage1.shared.contracts_runtime import ContextConflictResolution, ConflictRecord

GROUP_PRIORITY = {
    'p0_steering': 6,
    'active_strategy': 5,
    'live_execution_truth': 4,
    'foundational_strategy': 3,
    'narrative_memory': 2,
    'producer_notes': 1,
}

TOPIC_KEYWORDS = {
    'service_area_pages': ['service area', 'service-area', 'page rollout', 'page templates', 'launch'],
    'tracking': ['tracking', 'attribution', 'event naming', 'call tracking', 'form'],
    'gbp': ['gbp', 'google business profile', 'review widget', 'review acquisition', 'posting'],
    'lead_quality': ['qualified leads', 'qualified calls', 'lead quality'],
    'approval_risk': ['approval', 'legal', 'awaiting client', 'awaiting', 'open'],
}

POSITIVE_MARKERS = ['complete', 'completed', 'up ', 'improved', 'launch', 'rollout', 'fix ', 'fixed', 'cleanup']
BLOCKED_MARKERS = ['blocked', 'awaiting', 'delay', 'stalled', 'open', 'untagged', 'gap', 'careful not to overpromise']
CAUTION_MARKERS = ['be careful', 'do not overpromise', "don't overpromise", 'careful not to overpromise']


def _normalize_text(value: str) -> str:
    return ' '.join(value.lower().split())


def prioritize_context_sources(context_bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    prioritized: List[Dict[str, Any]] = []
    provenance_lookup = {entry['context_key']: entry.get('source_refs', []) for entry in context_bundle.get('provenance_map', [])}

    for group_name, priority in GROUP_PRIORITY.items():
        items = context_bundle.get(group_name, [])
        if not isinstance(items, list):
            continue
        for idx, content in enumerate(items):
            source_refs = provenance_lookup.get(f'{group_name}[{idx}]', [])
            prioritized.append(
                {
                    'group': group_name,
                    'priority': priority,
                    'content': content,
                    'source_refs': source_refs,
                }
            )

    prioritized.sort(key=lambda item: item['priority'], reverse=True)
    return prioritized


def _detect_topic_hits(text: str) -> List[str]:
    normalized = _normalize_text(text)
    hits: List[str] = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            hits.append(topic)
    return hits


def _classify_signal(text: str) -> str:
    normalized = _normalize_text(text)
    if any(marker in normalized for marker in BLOCKED_MARKERS):
        return 'blocked'
    if any(marker in normalized for marker in CAUTION_MARKERS):
        return 'caution'
    if any(marker in normalized for marker in POSITIVE_MARKERS):
        return 'positive'
    return 'neutral'


def detect_context_conflicts(prioritized_context: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_by_topic: Dict[str, List[Dict[str, Any]]] = {}

    for item in prioritized_context:
        topics = _detect_topic_hits(item['content'])
        signal = _classify_signal(item['content'])
        for topic in topics:
            seen_by_topic.setdefault(topic, []).append(
                {
                    'topic': topic,
                    'group': item['group'],
                    'priority': item['priority'],
                    'signal': signal,
                    'content': item['content'],
                    'source_refs': item.get('source_refs', []),
                }
            )

    conflicts: List[Dict[str, Any]] = []
    for topic, entries in seen_by_topic.items():
        entries = sorted(entries, key=lambda entry: entry['priority'], reverse=True)
        blocked_or_caution = [entry for entry in entries if entry['signal'] in {'blocked', 'caution'}]
        positives = [entry for entry in entries if entry['signal'] == 'positive']
        if blocked_or_caution and positives:
            high = blocked_or_caution[0] if blocked_or_caution[0]['priority'] >= positives[0]['priority'] else positives[0]
            low = positives[0] if high in blocked_or_caution else blocked_or_caution[0]
            conflicts.append(
                {
                    'topic': topic,
                    'higher_priority_source': high['group'],
                    'lower_priority_source': low['group'],
                    'higher_signal': high['signal'],
                    'lower_signal': low['signal'],
                    'higher_source_refs': high['source_refs'],
                    'lower_source_refs': low['source_refs'],
                    'reason': f"{high['group']} indicates {high['signal']} while {low['group']} indicates {low['signal']}",
                }
            )
    return conflicts


def resolve_or_flag_conflicts(conflict_records: Iterable[Dict[str, Any]]) -> ContextConflictResolution:
    resolved: List[ConflictRecord] = []
    for record in conflict_records:
        resolution = 'resolved' if record['higher_signal'] in {'blocked', 'caution'} else 'flagged_for_input_required'
        resolved.append(
            ConflictRecord(
                topic=record['topic'],
                higher_priority_source=record['higher_priority_source'],
                lower_priority_source=record['lower_priority_source'],
                resolution=resolution,
                reason=record['reason'],
            )
        )
    return ContextConflictResolution(conflicts=resolved)
