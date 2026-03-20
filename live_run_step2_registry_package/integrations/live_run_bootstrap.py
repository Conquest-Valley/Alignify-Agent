
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .registry_adapter import build_live_run_payload, write_live_run_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build live run artifacts from the client registry workbook.")
    parser.add_argument("--workbook", required=True, help="Path to the Google Sheet workbook exported as .xlsx")
    parser.add_argument("--client", required=True, help="Client selector: client_id_optional or client_name")
    parser.add_argument("--output-dir", default="live_run_outputs", help="Directory where normalized artifacts will be written")
    args = parser.parse_args()

    payload = build_live_run_payload(args.workbook, args.client)
    output_files = write_live_run_artifacts(payload, args.output_dir)

    print("Live run registry bootstrap complete.")
    print(f"Client: {payload['client_id']}")
    print("Artifacts:")
    for name, path in output_files.items():
        print(f"- {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
