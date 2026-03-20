from __future__ import annotations

from typing import Any, Dict, List, Sequence

from antigravity_stage1.shared.evidence import assess_confidence_band, create_evidence_ref

THEME_RULES = {
    'launch progress': ['launch', 'rollout', 'service area page', 'template'],
    'tracking cleanup': ['tracking', 'attribution', 'event naming', 'call tracking', 'untagged'],
    'approval delays': ['approval', 'legal', 'awaiting'],
    'gbp momentum': ['gbp', 'google business profile', 'review', 'posting'],
}


def _flatten(values: Sequence[str]) -> str:
    return '\n'.join(value for value in values if value)


def _extract_theme_hits(text: str) -> List[str]:
    normalized = text.lower()
    hits: List[str] = []
    for label, keywords in THEME_RULES.items():
        if any(keyword in normalized for keyword in keywords):
            hits.append(label)
    return hits


def extract_prior_promises(narrative_texts: Sequence[str]) -> List[str]:
    promises: List[str] = []
    for line in _flatten(narrative_texts).splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if 'committed to' in lowered:
            promises.append(stripped.split('committed to', 1)[1].strip().rstrip('.'))
    return promises


def extract_unresolved_themes(narrative_texts: Sequence[str], producer_notes: Sequence[str], client_memory: Dict[str, Any]) -> List[str]:
    unresolved: List[str] = []
    combined_lines = _flatten(narrative_texts + list(producer_notes)).splitlines()
    for line in combined_lines:
        lowered = line.lower().strip()
        if any(word in lowered for word in ['blocked', 'awaiting', 'untagged', 'careful not to overpromise']):
            unresolved.append(line.strip().rstrip('.'))
    for concern in client_memory.get('recurring_concerns', []):
        if concern not in unresolved:
            unresolved.append(concern)
    return unresolved


def extract_narrative_continuity(context_bundle: Dict[str, Any], client_memory: Dict[str, Any]) -> Dict[str, Any]:
    narrative_texts = context_bundle.get('narrative_memory', [])
    producer_notes = context_bundle.get('producer_notes', [])
    combined = _flatten(narrative_texts + producer_notes)

    recurring_themes: List[str] = []
    for theme in _extract_theme_hits(combined):
        if theme not in recurring_themes:
            recurring_themes.append(theme)
    for concern in client_memory.get('recurring_concerns', []):
        if concern not in recurring_themes:
            recurring_themes.append(concern)

    prior_promises = extract_prior_promises(narrative_texts)
    unresolved_topics = extract_unresolved_themes(narrative_texts, producer_notes, client_memory)

    prior_resonant_wins: List[str] = []
    for line in _flatten(narrative_texts).splitlines():
        lowered = line.lower().strip()
        if 'improved' in lowered or 'up ' in lowered:
            cleaned = line.strip().rstrip('.')
            if cleaned not in prior_resonant_wins:
                prior_resonant_wins.append(cleaned)

    continuity_risks: List[str] = []
    for line in _flatten(producer_notes).splitlines():
        lowered = line.lower().strip()
        if 'careful' in lowered or 'do not overpromise' in lowered or 'overpromise' in lowered:
            continuity_risks.append(line.strip().rstrip('.'))
    for blocker in client_memory.get('recurring_blockers', []):
        if blocker not in continuity_risks:
            continuity_risks.append(blocker)

    evidence_refs = []
    if narrative_texts:
        evidence_refs.append(
            create_evidence_ref(
                source_type='context_bundle',
                source_ref='narrative_memory',
                source_timestamp_or_window='current_run',
                observation=f'Loaded {len(narrative_texts)} narrative memory texts',
                confidence='medium',
            )
        )
    if producer_notes:
        evidence_refs.append(
            create_evidence_ref(
                source_type='context_bundle',
                source_ref='producer_notes',
                source_timestamp_or_window='current_run',
                observation=f'Loaded {len(producer_notes)} producer note texts',
                confidence='medium',
            )
        )
    confidence = assess_confidence_band(evidence_refs, has_contradiction=False)

    source_refs = []
    for entry in context_bundle.get('provenance_map', []):
        key = entry.get('context_key', '')
        if key.startswith('narrative_memory') or key.startswith('producer_notes'):
            source_refs.extend(entry.get('source_refs', []))

    return {
        'recurring_themes': recurring_themes,
        'prior_promises': prior_promises,
        'unresolved_topics': unresolved_topics,
        'prior_resonant_wins': prior_resonant_wins,
        'continuity_risks': continuity_risks,
        'source_refs': sorted(set(source_refs)),
        'confidence': confidence,
    }
