from __future__ import annotations

import argparse
from pathlib import Path

from .google_docs_adapter import build_docs_resolution_plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Build docs target manifest for a live client run.")
    parser.add_argument("--client-record", required=True, help="Path to stage2_client_record.json")
    parser.add_argument("--source-rows", required=True, help="Path to source_rows.json")
    parser.add_argument("--output-dir", required=True, help="Directory to write docs target artifacts")
    args = parser.parse_args()

    plan = build_docs_resolution_plan(args.client_record, args.source_rows, args.output_dir)

    print("Step 3 docs bootstrap complete.")
    print(f"Client: {plan.get('client_id_optional') or plan.get('client_name')}")
    print("Artifacts:")
    print(f"- docs_targets: {Path(args.output_dir) / 'docs_targets.json'}")
    print(f"- alignment_notes_target: {Path(args.output_dir) / 'alignment_notes_target.json'}")
    print(f"- strategy_targets: {Path(args.output_dir) / 'strategy_targets.json'}")
    print(f"- report_targets: {Path(args.output_dir) / 'report_targets.json'}")
    print(f"- docs_resolution_plan: {Path(args.output_dir) / 'docs_resolution_plan.json'}")


if __name__ == "__main__":
    main()
