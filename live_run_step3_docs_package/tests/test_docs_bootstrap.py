from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from live_run_step3_docs_package.integrations.google_docs_adapter import build_docs_resolution_plan


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        client = {
            "client_id_optional": "mbda-can",
            "client_name": "My Baby Donor Agency",
            "alignment_notes_doc_link": "https://docs.google.com/document/d/ALIGN123/edit",
            "kickoff_doc_link": "https://docs.google.com/document/d/KICK123/edit",
            "acct_info_doc_link": "https://docs.google.com/document/d/ACCT123/edit",
            "client_dosssier_doc_link": "https://docs.google.com/document/d/DOS123/edit",
            "client_overview_link": "https://docs.google.com/document/d/OVR123/edit",
            "irg_doc_link": "https://docs.google.com/document/d/IRG123/edit",
            "initial_strategy_link": "https://docs.google.com/document/d/INIT123/edit",
            "current_quarterly_strategy_link": "https://docs.google.com/document/d/QTR123/edit",
            "primary_dashboard_ref_optional": "https://docs.google.com/spreadsheets/d/DASH123/edit",
        }
        sources = [
            {
                "source_type": "prior_report",
                "source_class": "narrative_memory",
                "source_label": "April report",
                "source_ref": "https://docs.google.com/document/d/RPT123/edit",
                "sub_ref_or_tab_optional": "April 2026",
                "priority": "high",
                "active": True,
            }
        ]
        client_path = tmp_path / "stage2_client_record.json"
        source_path = tmp_path / "source_rows.json"
        out_path = tmp_path / "out"
        client_path.write_text(json.dumps(client), encoding="utf-8")
        source_path.write_text(json.dumps(sources), encoding="utf-8")

        plan = build_docs_resolution_plan(client_path, source_path, out_path)
        assert plan["alignment_notes_target"]["file_id"] == "ALIGN123"
        assert len(plan["strategy_targets"]) >= 2
        assert len(plan["report_targets"]) == 1
        assert (out_path / "docs_targets.json").exists()
        assert (out_path / "docs_resolution_plan.json").exists()

    print("Step 3 docs smoke test passed.")


if __name__ == "__main__":
    main()
