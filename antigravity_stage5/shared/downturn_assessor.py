from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

from antigravity_stage1.shared.evidence import create_evidence_ref


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


def detect_negative_or_flat_signals(context_bundle: Dict[str, Any]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    for source_ref, line in _iter_live_lines(context_bundle):
        lowered = line.lower()
        if any(token in lowered for token in ['down', 'declin', 'drop', 'flat', 'stagn']):
            metric_match = re.match(r'([A-Za-z0-9 +/\-]+?)\s+(down|declined|flat|dropped)', line, flags=re.IGNORECASE)
            metric = metric_match.group(1).strip() if metric_match else 'performance signal'
            findings.append({'source_ref': source_ref, 'line': line, 'metric': metric})
    return findings


def classify_downturn_support(signal: Dict[str, str], campaign_status_matrix: Dict[str, Any], narrative_summary_lite: Dict[str, Any]) -> tuple[str, str]:
    line = signal['line'].lower()
    blocked_text = ' '.join(
        task.lower()
        for category in campaign_status_matrix.get('categories', [])
        for task in category.get('blocked', []) + category.get('waiting_on_client', [])
    )
    unresolved = ' '.join(item.lower() for item in narrative_summary_lite.get('unresolved_topics', []))
    if any(token in blocked_text for token in ['approval', 'tracking', 'launch']) and any(token in line for token in ['lead', 'call', 'traffic', 'click']):
        return 'partial', 'Negative movement may be tied to blocked or pending implementation work.'
    if any(token in unresolved for token in ['approval', 'delay', 'legal']) and any(token in line for token in ['lead', 'call', 'traffic', 'click']):
        return 'partial', 'Recent unresolved issues may be contributing, but evidence is still incomplete.'
    return 'unsupported', 'No supported causal explanation found in current execution or narrative sources.'


def generate_downturn_candidates(
    context_bundle: Dict[str, Any],
    campaign_status_matrix: Dict[str, Any],
    narrative_summary_lite: Dict[str, Any],
) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    for signal in detect_negative_or_flat_signals(context_bundle):
        support_level, explanation = classify_downturn_support(signal, campaign_status_matrix, narrative_summary_lite)
        confidence = 'medium' if support_level == 'partial' else 'low'
        findings.append(
            {
                'issue': signal['line'],
                'metric': signal['metric'],
                'observed_change': signal['line'],
                'candidate_cause': explanation,
                'support_level': support_level,
                'evidence_refs': [
                    create_evidence_ref(
                        source_type='Reporting',
                        source_ref=signal['source_ref'],
                        source_timestamp_or_window='current_reporting_window',
                        observation=signal['line'],
                        confidence=confidence,
                    ).to_dict()
                ],
                'confidence': confidence,
                'needs_human_input': support_level != 'supported',
            }
        )
    return {'findings': findings}
