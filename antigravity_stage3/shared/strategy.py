from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Sequence

from antigravity_stage1.shared.evidence import assess_confidence_band, create_evidence_ref

WORKSTREAM_MAP = {
    'service area': 'SEO / Copy',
    'service page': 'SEO / Copy',
    'tracking': 'Analytics / Tracking',
    'attribution': 'Analytics / Tracking',
    'call attribution': 'Analytics / Tracking',
    'gbp': 'Local SEO / GBP',
    'google business profile': 'Local SEO / GBP',
    'review': 'Local SEO / GBP',
    'launch': 'Web Development',
}


def _flatten_texts(values: Sequence[str]) -> str:
    return '\n'.join(value for value in values if value)


def _extract_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _extract_north_stars(foundational_texts: Sequence[str], client_memory: Dict[str, Any]) -> List[str]:
    results = list(client_memory.get('north_star_goals', []))
    combined = _flatten_texts(foundational_texts)
    match = re.search(r'north star:\s*(.+)', combined, re.IGNORECASE)
    if match:
        candidate = match.group(1).strip().rstrip('.')
        if candidate and candidate not in results:
            results.insert(0, candidate)
    return results


def _extract_quarterly_priorities(active_strategy_texts: Sequence[str]) -> List[str]:
    priorities: List[str] = []
    for line in _extract_lines(_flatten_texts(active_strategy_texts)):
        if re.match(r'quarter priority\s*\d+\s*:', line, re.IGNORECASE):
            priorities.append(line.split(':', 1)[1].strip().rstrip('.'))
    return priorities


def _extract_success_definitions(active_strategy_texts: Sequence[str], client_memory: Dict[str, Any]) -> List[str]:
    successes: List[str] = []
    for line in _extract_lines(_flatten_texts(active_strategy_texts)):
        if line.lower().startswith('success means'):
            if ':' in line:
                cleaned = line.split(':', 1)[1].strip().rstrip('.')
            else:
                cleaned = line[len('Success means'):].strip().rstrip('.')
            if cleaned:
                successes.append(cleaned)
    for item in client_memory.get('what_counts_as_a_win', []):
        if item not in successes:
            successes.append(item)
    return successes


def build_workstream_goal_map(current_quarter_priorities: Sequence[str]) -> List[Dict[str, str]]:
    mappings: List[Dict[str, str]] = []
    for priority in current_quarter_priorities:
        lowered = priority.lower()
        workstream = 'Strategy'
        for needle, mapped in WORKSTREAM_MAP.items():
            if needle in lowered:
                workstream = mapped
                break
        mappings.append({'workstream': workstream, 'goal': priority})
    return mappings


def extract_client_value_signals(foundational_texts: Sequence[str], client_memory: Dict[str, Any]) -> List[str]:
    signals = list(client_memory.get('what_counts_as_a_win', []))
    for line in _extract_lines(_flatten_texts(foundational_texts)):
        if 'values' in line.lower() or 'lead quality' in line.lower():
            cleaned = line.rstrip('.')
            if cleaned not in signals:
                signals.append(cleaned)
    return signals


def _extract_benchmark_period(active_strategy_texts: Sequence[str]) -> str:
    for line in _extract_lines(_flatten_texts(active_strategy_texts)):
        match = re.match(r'(q\d\s+\d{4})', line, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return 'UNKNOWN'


def extract_strategy_summary(
    context_bundle: Dict[str, Any],
    client_memory: Dict[str, Any],
) -> Dict[str, Any]:
    foundational = context_bundle.get('foundational_strategy', [])
    active = context_bundle.get('active_strategy', [])
    north_stars = _extract_north_stars(foundational, client_memory)
    priorities = _extract_quarterly_priorities(active)
    success_definitions = _extract_success_definitions(active, client_memory)
    workstream_goal_map = build_workstream_goal_map(priorities)
    client_value_signals = extract_client_value_signals(foundational, client_memory)
    benchmark = _extract_benchmark_period(active)

    evidence_refs = []
    for source_ref in ['foundational_strategy', 'active_strategy']:
        source_texts = context_bundle.get(source_ref, [])
        if source_texts:
            evidence_refs.append(
                create_evidence_ref(
                    source_type='context_bundle',
                    source_ref=source_ref,
                    source_timestamp_or_window='current_run',
                    observation=f'Loaded {len(source_texts)} text blocks from {source_ref}',
                    confidence='medium',
                )
            )

    confidence = assess_confidence_band(evidence_refs, has_contradiction=False)
    source_refs = []
    for entry in context_bundle.get('provenance_map', []):
        key = entry.get('context_key', '')
        if key.startswith('foundational_strategy') or key.startswith('active_strategy'):
            source_refs.extend(entry.get('source_refs', []))

    return {
        'north_star_goals': north_stars,
        'current_quarter_priorities': priorities,
        'success_definitions': success_definitions,
        'workstream_goal_map': workstream_goal_map,
        'client_value_signals': client_value_signals,
        'active_benchmark_period': benchmark,
        'source_refs': sorted(set(source_refs)),
        'confidence': confidence,
    }
