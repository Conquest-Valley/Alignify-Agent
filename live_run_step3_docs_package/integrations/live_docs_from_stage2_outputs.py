from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from .google_docs_adapter import CLIENT_DOC_FIELDS, build_docs_resolution_plan
except ImportError:  # pragma: no cover - direct script execution
    from google_docs_adapter import CLIENT_DOC_FIELDS, build_docs_resolution_plan


EXPECTED_STAGE2_FILES = {
    "client_row": "client_row.json",
    "source_rows": "source_rows.json",
    "stage2_client_record": "stage2_client_record.json",
}


def _load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected a JSON object at {path}, got {type(payload).__name__}.")
    return payload


def _find_stage2_dir(base_dir: Path, client_id: str | None) -> Path:
    if client_id:
        candidate = base_dir / client_id
        if candidate.exists():
            return candidate
        raise SystemExit(f"Could not find stage 2 output directory for client '{client_id}' under {base_dir}.")

    if (base_dir / EXPECTED_STAGE2_FILES["client_row"]).exists():
        return base_dir

    child_dirs = sorted(path for path in base_dir.iterdir() if path.is_dir())
    matching = [path for path in child_dirs if (path / EXPECTED_STAGE2_FILES["client_row"]).exists()]
    if len(matching) == 1:
        return matching[0]
    if not matching:
        raise SystemExit(
            f"No stage 2 client output directory found under {base_dir}. Expected {EXPECTED_STAGE2_FILES['client_row']}."
        )
    raise SystemExit(
        "Multiple stage 2 client directories were found. Pass --client-id so the bridge knows which one to use."
    )


def _validate_client_row_payload(payload: dict[str, Any], path: Path) -> None:
    doc_fields_present = [field for field in CLIENT_DOC_FIELDS if payload.get(field)]
    if doc_fields_present:
        return
    expected = ", ".join(CLIENT_DOC_FIELDS)
    raise SystemExit(
        f"Stage 2 output at {path} does not contain any supported document fields. Expected one or more of: {expected}."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run step 3 docs resolution directly from a stage 2 output directory."
    )
    parser.add_argument(
        "--stage2-output-dir",
        required=True,
        help="Root stage 2 output directory. This can be the overall output root or a specific client subdirectory.",
    )
    parser.add_argument(
        "--client-id",
        required=False,
        help="Optional client id when the stage 2 output root contains multiple client subdirectories.",
    )
    parser.add_argument("--output-dir", required=True, help="Directory where step 3 docs artifacts should be written.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    stage2_root = Path(args.stage2_output_dir)
    client_dir = _find_stage2_dir(stage2_root, args.client_id)
    client_row_path = client_dir / EXPECTED_STAGE2_FILES["client_row"]
    source_rows_path = client_dir / EXPECTED_STAGE2_FILES["source_rows"]

    if not client_row_path.exists():
        raise SystemExit(f"Missing stage 2 artifact: {client_row_path}")
    if not source_rows_path.exists():
        raise SystemExit(f"Missing stage 2 artifact: {source_rows_path}")

    client_row = _load_json_object(client_row_path)
    _validate_client_row_payload(client_row, client_row_path)

    plan = build_docs_resolution_plan(client_row_path, source_rows_path, args.output_dir)
    print(
        json.dumps(
            {
                "status": "ok",
                "stage2_client_dir": str(client_dir),
                "client_row": str(client_row_path),
                "source_rows": str(source_rows_path),
                "output_dir": str(args.output_dir),
                "alignment_notes_target": plan.get("alignment_notes_target"),
                "strategy_target_count": len(plan.get("strategy_targets", [])),
                "report_target_count": len(plan.get("report_targets", [])),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
