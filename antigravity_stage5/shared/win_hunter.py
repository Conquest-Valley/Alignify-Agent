from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence
from uuid import uuid4

from antigravity_stage1.shared.evidence import assess_confidence_band, create_evidence_ref

@dataclass
class WinCandidate:
    type: str
    category: str
    headline: str
    description: str
    strategic_goal_alignment: str
    client_relevance_score: float
    freshness_window: str
    evidence_refs: List[Dict[str, Any]]
    confidence: str
    score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'win_id': f'win_{uuid4().hex[:10]}',
            'type': self.type,
            'category': self.category,
            'headline': self.headline,
            'description': self.description,
            'strategic_goal_alignment': self.strategic_goal_alignment,
            'client_relevance_score': round(self.client_relevance_score, 2),
            'freshness_window': self.freshness_window,
            'evidence_refs': self.evidence_refs,
            'confidence': self.confidence,
        }


def _collect_live_source_refs(context_bundle: Dict[str, Any]) -> List[str]:
    refs: List[str] = []
    for entry in context_bundle.get('provenance_map', []):
        if str(entry.get('context_key', '')).startswith('live_execution_truth'):
            refs.extend(entry.get('source_refs', []))
    return refs


def _iter_live_lines(context_bundle: Dict[str, Any]) -> Iterable[tuple[str, str]]:
    refs = _collect_live_source_refs(context_bundle)
    texts = context_bundle.get('live_execution_truth', [])
    for idx, text in enumerate(texts):
        source_ref = refs[idx] if idx < len(refs) else f'live_source_{idx}'
        for line in text.splitlines():
            line = line.strip().rstrip('.')
            if line:
                yield source_ref, line


def _line_category(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ['gbp', 'business profile', 'maps']):
        return 'Local SEO / GBP'
    if any(token in lowered for token in ['call tracking', 'tracking', 'attribution', 'event naming']):
        return 'Analytics / Tracking'
    if any(token in lowered for token in ['landing page', 'service area page', 'service intent', 'clicks', 'position']):
        return 'SEO / Copy'
    return 'Strategy'


def _match_strategy(text: str, strategy_summary: Dict[str, Any]) -> str:
    lowered = text.lower()
    for priority in strategy_summary.get('current_quarter_priorities', []):
        p = priority.lower()
        tokens = [token for token in re.findall(r'[a-z0-9]+', p) if len(token) > 3]
        if any(token in lowered for token in tokens):
            return priority
    success_defs = strategy_summary.get('success_definitions', [])
    if success_defs:
        return success_defs[0]
    goals = strategy_summary.get('north_star_goals', [])
    return goals[0] if goals else 'General strategic progress'


def _estimate_relevance(text: str, strategy_summary: Dict[str, Any], value_signals: Sequence[str]) -> float:
    lowered = text.lower()
    score = 0.45
    if any(token in lowered for token in ['qualified', 'lead', 'call', 'conversion', 'form']):
        score += 0.25
    if any(token in lowered for token in ['launch', 'live', 'complete', 'completed', 'resolved', 'improved', 'up']):
        score += 0.15
    if any(signal.lower().split()[0] in lowered for signal in value_signals if signal):
        score += 0.1
    return min(score, 0.98)


def _build_score(candidate: WinCandidate) -> float:
    confidence_weight = {'high': 1.0, 'medium': 0.7, 'low': 0.3}[candidate.confidence]
    evidence_strength = min(len(candidate.evidence_refs) / 2, 1.0)
    freshness = 1.0 if '2026' in candidate.freshness_window or 'current' in candidate.freshness_window else 0.7
    explainability = 1.0 if len(candidate.description) < 180 else 0.8
    strategic_alignment = 1.0 if candidate.strategic_goal_alignment else 0.5
    return round(
        0.35 * strategic_alignment
        + 0.30 * candidate.client_relevance_score
        + 0.20 * evidence_strength * confidence_weight
        + 0.10 * freshness
        + 0.05 * explainability,
        4,
    )


def extract_performance_win_candidates(context_bundle: Dict[str, Any], strategy_summary: Dict[str, Any]) -> List[WinCandidate]:
    candidates: List[WinCandidate] = []
    value_signals = strategy_summary.get('client_value_signals', [])
    for source_ref, line in _iter_live_lines(context_bundle):
        lowered = line.lower()
        if not any(token in lowered for token in ['up', 'improved', 'increase', 'increased']):
            continue
        if any(token in lowered for token in ['click', 'position', 'form', 'calls', 'qualified']):
            evidence = [
                create_evidence_ref(
                    source_type='Reporting',
                    source_ref=source_ref,
                    source_timestamp_or_window='current_reporting_window',
                    observation=line,
                    confidence='high',
                ).to_dict()
            ]
            relevance = _estimate_relevance(line, strategy_summary, value_signals)
            alignment = _match_strategy(line, strategy_summary)
            candidate = WinCandidate(
                type='performance',
                category=_line_category(line),
                headline=line,
                description=line,
                strategic_goal_alignment=alignment,
                client_relevance_score=relevance,
                freshness_window='current_reporting_window',
                evidence_refs=evidence,
                confidence=assess_confidence_band([], has_contradiction=False),
                score=0.0,
            )
            candidate.confidence = 'medium'
            candidate.score = _build_score(candidate)
            candidates.append(candidate)
    return candidates


def extract_execution_win_candidates(campaign_status_matrix: Dict[str, Any], strategy_summary: Dict[str, Any]) -> List[WinCandidate]:
    candidates: List[WinCandidate] = []
    for category in campaign_status_matrix.get('categories', []):
        source_ref = (category.get('source_refs') or ['basecamp_unknown'])[0]
        for task in category.get('completed_since_last_call', []):
            evidence = [
                create_evidence_ref(
                    source_type='Basecamp',
                    source_ref=source_ref,
                    source_timestamp_or_window='current',
                    observation=f"completed_since_last_call: {task}",
                    confidence='high',
                ).to_dict()
            ]
            alignment = _match_strategy(task, strategy_summary)
            candidate = WinCandidate(
                type='execution',
                category=category['category'],
                headline=f"Completed: {task}",
                description=f"Completed since last call: {task}",
                strategic_goal_alignment=alignment,
                client_relevance_score=0.82 if category['category'] != 'Approvals / Client Dependencies' else 0.68,
                freshness_window='current',
                evidence_refs=evidence,
                confidence='medium',
                score=0.0,
            )
            candidate.score = _build_score(candidate)
            candidates.append(candidate)
        for task in category.get('in_progress', []):
            if category.get('quarterly_alignment_score', 0) < 60:
                continue
            evidence = [
                create_evidence_ref(
                    source_type='Basecamp',
                    source_ref=source_ref,
                    source_timestamp_or_window='current',
                    observation=f"in_progress: {task}",
                    confidence='medium',
                ).to_dict()
            ]
            alignment = _match_strategy(task, strategy_summary)
            candidate = WinCandidate(
                type='execution',
                category=category['category'],
                headline=f"In motion: {task}",
                description=f"Visible progress is underway: {task}",
                strategic_goal_alignment=alignment,
                client_relevance_score=0.73,
                freshness_window='current',
                evidence_refs=evidence,
                confidence='medium',
                score=0.0,
            )
            candidate.score = _build_score(candidate)
            candidates.append(candidate)
    return candidates


def extract_strategic_win_candidates(campaign_status_matrix: Dict[str, Any], strategy_summary: Dict[str, Any]) -> List[WinCandidate]:
    candidates: List[WinCandidate] = []
    for category in campaign_status_matrix.get('categories', []):
        alignment_score = category.get('quarterly_alignment_score', 0)
        if alignment_score < 70:
            continue
        alignment_notes = category.get('alignment_notes') or []
        if not alignment_notes:
            continue
        source_ref = (category.get('source_refs') or ['basecamp_unknown'])[0]
        note = alignment_notes[0]
        evidence = [
            create_evidence_ref(
                source_type='Basecamp',
                source_ref=source_ref,
                source_timestamp_or_window='current',
                observation=note,
                confidence='medium',
            ).to_dict()
        ]
        candidate = WinCandidate(
            type='strategic',
            category=category['category'],
            headline=f"{category['category']} work is aligned to quarter priorities",
            description=note,
            strategic_goal_alignment=note,
            client_relevance_score=0.76,
            freshness_window='current',
            evidence_refs=evidence,
            confidence='medium',
            score=0.0,
        )
        candidate.score = _build_score(candidate)
        candidates.append(candidate)
    return candidates


def rank_win_candidates(*candidate_groups: Sequence[WinCandidate], limit: int = 8) -> Dict[str, Any]:
    candidates: List[WinCandidate] = []
    for group in candidate_groups:
        candidates.extend(group)
    candidates.sort(key=lambda item: item.score, reverse=True)
    return {'wins': [candidate.to_dict() for candidate in candidates[:limit]]}
