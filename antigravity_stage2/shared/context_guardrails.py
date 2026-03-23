from __future__ import annotations

from typing import Dict, List


def summarize_context_health(context_bundle: Dict[str, object]) -> Dict[str, object]:
    missing_sources = list(context_bundle.get("missing_sources", []))
    warnings = list(context_bundle.get("warnings", []))
    loaded_count = len(list(context_bundle.get("all_loaded_sources", [])))

    status = "healthy"
    if missing_sources:
        status = "degraded"
    if len(missing_sources) >= 3:
        status = "needs_human_input"

    return {
        "status": status,
        "loaded_source_count": loaded_count,
        "missing_sources": missing_sources,
        "warnings": warnings,
        "should_pause": status == "needs_human_input",
    }


def build_input_required_notes(context_health: Dict[str, object]) -> List[str]:
    notes: List[str] = []
    missing_sources = list(context_health.get("missing_sources", []))
    warnings = list(context_health.get("warnings", []))

    if missing_sources:
        notes.append("Missing sources: " + ", ".join(sorted(set(str(item) for item in missing_sources))))
    if warnings:
        notes.append("Context warnings: " + ", ".join(sorted(set(str(item) for item in warnings))))
    if context_health.get("should_pause"):
        notes.append("Context load should pause for human input before downstream reasoning.")
    return notes
