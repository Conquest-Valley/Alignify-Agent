from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from .registry_adapter import build_live_run_payload, write_live_run_artifacts
except ImportError:  # pragma: no cover - direct script execution
    from registry_adapter import build_live_run_payload, write_live_run_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build live run registry artifacts from the client workbook with a script-friendly entrypoint."
    )
    parser.add_argument("--workbook", required=True, help="Path to the exported registry workbook (.xlsx).")
    parser.add_argument("--client", required=True, help="Client selector: client_id_optional or client_name.")
    parser.add_argument("--output-dir", default="live_run_outputs", help="Directory for normalized artifacts.")
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print the artifact map as JSON instead of the legacy human-readable summary.",
    )
    return parser


def _build_summary(payload: dict[str, Any], output_files: dict[str, str]) -> dict[str, Any]:
    return {
        "status": "ok",
        "client_id": payload.get("client_id"),
        "client_name": payload.get("client_name"),
        "artifact_count": len(output_files),
        "artifacts": output_files,
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    payload = build_live_run_payload(args.workbook, args.client)
    output_files = write_live_run_artifacts(payload, args.output_dir)
    summary = _build_summary(payload, output_files)

    if args.print_json:
        print(json.dumps(summary, indent=2))
        return 0

    print("Live run registry bootstrap complete.")
    print(f"Client: {summary['client_id']}")
    print("Artifacts:")
    for name, path in output_files.items():
        print(f"- {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
