from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

import jsonschema

from antigravity_stage1.shared.contracts_runtime import create_call_run
from antigravity_stage1.shared.state_machine import transition_call_state
from antigravity_stage1.shared.evidence import create_evidence_ref, assess_confidence_band
from antigravity_stage1.shared.freshness import assess_source_freshness
from antigravity_stage1.shared.taxonomy import normalize_category_alias
from antigravity_stage1.shared.snapshot import open_run_snapshot, register_source, register_reporting_window
from antigravity_stage1.shared.validation import validate_section_requirements


def load_schema(name: str):
    return json.loads((ROOT / "schemas" / name).read_text())


def main():
    call_run = create_call_run(
        client_id="client_abc",
        dp_id="dp_123",
        scheduled_at="2026-03-20T15:00:00+00:00",
        p0_instruction="Lead with GBP wins",
    )
    jsonschema.validate(call_run.to_dict(), load_schema("call_run.schema.json"))

    ok, msg = transition_call_state(call_run, "context_loaded")
    assert ok, msg

    evidence = create_evidence_ref(
        source_type="Basecamp",
        source_ref="task_12345",
        source_timestamp_or_window="current",
        observation="Homepage CRO staging complete",
        confidence="high",
    )
    jsonschema.validate(evidence.to_dict(), load_schema("evidence_ref.schema.json"))
    assert assess_confidence_band([evidence]) == "medium"

    freshness = assess_source_freshness(
        source_ref="ga4_main",
        source_class="ga4",
        reporting_window="Last 30 days",
    )
    jsonschema.validate(freshness.to_dict(), load_schema("freshness_assessment.schema.json"))
    assert freshness.freshness_status == "fresh"

    assert normalize_category_alias("PPC") == "Paid Media"
    assert normalize_category_alias("Dev") == "Web Development"

    snapshot = open_run_snapshot(call_run.call_run_id, call_run.client_id)
    register_source(snapshot, "doc_quarterly_q2")
    register_reporting_window(snapshot, "ga4_main", "Last 30 days")
    jsonschema.validate(snapshot.to_dict(), load_schema("run_snapshot_manifest.schema.json"))

    report = validate_section_requirements(
        call_run.call_run_id,
        {
            "Meeting Summary": {
                "must_include_strategy_anchor": True,
                "must_include_current_truth_anchor": True,
            },
            "Pending Approvals": {
                "must_have_evidence": True,
            },
            "Wins / Highlights": {
                "must_have_evidence": True,
                "must_have_strategic_relevance": True,
            },
            "Input Required": {
                "must_exist_when_unresolved_low_confidence_conflict_present": True,
            },
        },
    )
    jsonschema.validate(report.to_dict(), load_schema("section_validation_report.schema.json"))
    assert report.overall_valid is True

    print("Stage 1 smoke test passed.")


if __name__ == "__main__":
    main()
