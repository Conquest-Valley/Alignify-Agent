from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from .google_docs_adapter import CLIENT_DOC_FIELDS, build_docs_resolution_plan
except ImportError:  # pragma: no cover - direct script execution
    from google_docs_adapter import CLIENT_DOC_FIELDS, build_docs_resolution_plan


def _load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected a JSON object at {path}, got {type(payload).__name__}.")
    return payload


def _validate_client_row_payload(payload: dict[str, Any], path: Path) -> None:
    doc_fields_present = [field for field in CLIENT_DOC_FIELDS if payload.get(field)]
    if doc_fields_present:
        return

    expected = ", ".join(CLIENT_DOC_FIELDS)
    raise SystemExit(
        "Step 3 expects the enriched client_row JSON from the prior stage, not the compact stage2 client record. "
        f"Checked file: {path}. No supported doc fields were found. Expected one or more of: {expected}."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the step 3 docs resolution plan from the enriched client_row handoff."
    )
    parser.add_argument("--client-row", required=True, help="Path to client_row.json from the prior stage.")
    parser.add_argument("--source-rows", required=True, help="Path to source_rows.json.")
    parser.add_argument("--output-dir", required=True, help="Directory for output artifacts.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    client_row_path = Path(args.client_row)
    source_rows_path = Path(args.source_rows)
    output_dir = Path(args.output_dir)

    client_payload = _load_json_object(client_row_path)
    _validate_client_row_payload(client_payload, client_row_path)

    plan = build_docs_resolution_plan(client_row_path, source_rows_path, output_dir)
    print(
        json.dumps(
            {
                "status": "ok",
                "client_row": str(client_row_path),
                "source_rows": str(source_rows_path),
                "output_dir": str(output_dir),
                "alignment_notes_target": plan.get("alignment_notes_target"),
                "strategy_target_count": len(plan.get("strategy_targets", [])),
                "report_target_count": len(plan.get("report_targets", [])),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
