from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .contracts_runtime import SectionCheckResult, SectionValidationReport


SECTION_RULES_PATH = Path(__file__).resolve().parent.parent / "validation" / "section_rules.json"
SECTION_RULES: Dict[str, List[str]] = json.loads(SECTION_RULES_PATH.read_text())


def validate_section_requirements(call_run_id: str, section_inputs: Dict[str, Dict[str, bool]]) -> SectionValidationReport:
    results: List[SectionCheckResult] = []
    overall_valid = True

    for section_name, rules in SECTION_RULES.items():
        provided = section_inputs.get(section_name, {})
        passed: List[str] = []
        failed: List[str] = []
        follow_up: List[str] = []

        for rule in rules:
            if provided.get(rule, False):
                passed.append(rule)
            else:
                failed.append(rule)
                follow_up.append(f"Resolve rule: {rule}")

        is_valid = len(failed) == 0
        overall_valid = overall_valid and is_valid
        results.append(
            SectionCheckResult(
                section_name=section_name,
                is_valid=is_valid,
                checks_passed=passed,
                checks_failed=failed,
                required_follow_up=follow_up,
            )
        )

    return SectionValidationReport(call_run_id=call_run_id, sections=results, overall_valid=overall_valid)
