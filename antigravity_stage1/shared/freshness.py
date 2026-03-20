from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .contracts_runtime import FreshnessAssessment


RULES_PATH = Path(__file__).resolve().parent.parent / "validation" / "freshness_rules.json"
RULES = json.loads(RULES_PATH.read_text())


def assess_source_freshness(
    source_ref: str,
    source_class: str,
    *,
    version_identified: bool = False,
    matches_active_benchmark_period: bool = False,
    reporting_window: Optional[str] = None,
    run_bounded: bool = False,
    current_run_fetch: bool = False,
) -> FreshnessAssessment:
    rule = RULES.get(source_class, RULES["other"])

    if source_class == "strategy":
        if version_identified:
            return FreshnessAssessment(source_ref, source_class, "acceptable_for_continuity", "Version identified strategy source")
        return FreshnessAssessment(source_ref, source_class, "unknown", "Strategy source missing version metadata")

    if source_class == "quarterly_strategy":
        if matches_active_benchmark_period:
            return FreshnessAssessment(source_ref, source_class, "fresh", "Quarterly strategy matches active benchmark period")
        return FreshnessAssessment(source_ref, source_class, "stale", "Quarterly strategy does not match active benchmark period")

    if source_class in {"prior_note", "prior_report"}:
        return FreshnessAssessment(source_ref, source_class, "acceptable_for_continuity", "Continuity only source")

    if source_class == "basecamp":
        if current_run_fetch:
            return FreshnessAssessment(source_ref, source_class, "fresh", "Fetched during current run")
        return FreshnessAssessment(source_ref, source_class, "stale", "Basecamp source must be fetched during current run")

    if source_class in {"ga4", "gsc"}:
        if reporting_window:
            return FreshnessAssessment(source_ref, source_class, "fresh", f"Reporting window supplied: {reporting_window}")
        return FreshnessAssessment(source_ref, source_class, "unknown", "Explicit reporting window required")

    if source_class == "producer_note":
        if run_bounded:
            return FreshnessAssessment(source_ref, source_class, "fresh", "Producer note is active for current run")
        return FreshnessAssessment(source_ref, source_class, "stale", "Producer notes must be run bounded")

    return FreshnessAssessment(source_ref, source_class, "unknown", f"Rule applied: {rule}")
