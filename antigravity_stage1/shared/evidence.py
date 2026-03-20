from __future__ import annotations

from typing import Iterable

from .contracts_runtime import ConfidenceBand, EvidenceRef


def create_evidence_ref(
    source_type: str,
    source_ref: str,
    source_timestamp_or_window: str,
    observation: str,
    confidence: str,
) -> EvidenceRef:
    if not source_type:
        raise ValueError("source_type is required")
    if not source_ref:
        raise ValueError("source_ref is required")
    if not source_timestamp_or_window:
        raise ValueError("source_timestamp_or_window is required")
    if not observation:
        raise ValueError("observation is required")
    if confidence not in {band.value for band in ConfidenceBand}:
        raise ValueError("confidence must be one of: high, medium, low")
    return EvidenceRef(
        source_type=source_type,
        source_ref=source_ref,
        source_timestamp_or_window=source_timestamp_or_window,
        observation=observation,
        confidence=confidence,
    )


def assess_confidence_band(evidence_refs: Iterable[EvidenceRef], has_contradiction: bool = False) -> str:
    refs = list(evidence_refs)
    if has_contradiction:
        return ConfidenceBand.LOW.value
    if len(refs) >= 2:
        unique_sources = {ref.source_ref for ref in refs}
        if len(unique_sources) >= 2:
            return ConfidenceBand.HIGH.value
    if len(refs) >= 1:
        return ConfidenceBand.MEDIUM.value
    return ConfidenceBand.LOW.value
