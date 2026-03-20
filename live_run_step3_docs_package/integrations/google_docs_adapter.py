from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

GOOGLE_DOC_PATTERNS = {
    "document": re.compile(r"docs\.google\.com/document/d/([^/]+)"),
    "spreadsheet": re.compile(r"docs\.google\.com/spreadsheets/d/([^/]+)"),
    "presentation": re.compile(r"docs\.google\.com/presentation/d/([^/]+)"),
    "drive_file": re.compile(r"drive\.google\.com/file/d/([^/]+)"),
}

CLIENT_DOC_FIELDS = [
    "alignment_notes_doc_link",
    "kickoff_doc_link",
    "acct_info_doc_link",
    "client_dosssier_doc_link",
    "client_overview_link",
    "irg_doc_link",
    "initial_strategy_link",
    "current_quarterly_strategy_link",
    "primary_dashboard_ref_optional",
]

SOURCE_INDEX_DOC_TYPES = {
    "prior_report",
    "dashboard",
    "reference_doc",
    "strategy_support",
    "visual_support",
    "prior_call_note",
}


@dataclass
class DocTarget:
    label: str
    source_ref: str
    doc_kind: str
    file_id: Optional[str]
    source_class: str
    source_type: str
    priority: str
    active: bool
    sub_ref_or_tab: Optional[str] = None
    notes: Optional[str] = None


class DocsAdapterError(Exception):
    pass


def _read_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def classify_google_ref(source_ref: str) -> tuple[str, Optional[str]]:
    if not source_ref:
        return ("unknown", None)
    for kind, pattern in GOOGLE_DOC_PATTERNS.items():
        match = pattern.search(source_ref)
        if match:
            return (kind, match.group(1))
    return ("non_google_or_unknown", None)


def _build_target(label: str, source_ref: str, source_class: str, source_type: str, priority: str = "high", active: bool = True, sub_ref_or_tab: Optional[str] = None, notes: Optional[str] = None) -> DocTarget:
    doc_kind, file_id = classify_google_ref(source_ref)
    return DocTarget(
        label=label,
        source_ref=source_ref,
        doc_kind=doc_kind,
        file_id=file_id,
        source_class=source_class,
        source_type=source_type,
        priority=priority,
        active=active,
        sub_ref_or_tab=sub_ref_or_tab,
        notes=notes,
    )


def build_client_doc_targets(client_record: Dict[str, Any]) -> List[DocTarget]:
    targets: List[DocTarget] = []
    for field in CLIENT_DOC_FIELDS:
        value = client_record.get(field)
        if not value:
            continue
        label = field
        source_class = "active_strategy" if field == "current_quarterly_strategy_link" else "foundational_strategy"
        source_type = field.replace("_link", "")
        if field == "alignment_notes_doc_link":
            source_class = "narrative_memory"
        if field == "primary_dashboard_ref_optional":
            source_class = "live_execution_truth"
        targets.append(_build_target(label, value, source_class, source_type))
    return targets


def build_source_index_doc_targets(source_rows: List[Dict[str, Any]]) -> List[DocTarget]:
    targets: List[DocTarget] = []
    for row in source_rows:
        if not row.get("active", True):
            continue
        source_type = row.get("source_type", "")
        if source_type not in SOURCE_INDEX_DOC_TYPES:
            continue
        targets.append(
            _build_target(
                label=row.get("source_label") or source_type,
                source_ref=row.get("source_ref", ""),
                source_class=row.get("source_class", "narrative_memory"),
                source_type=source_type,
                priority=row.get("priority", "medium"),
                active=bool(row.get("active", True)),
                sub_ref_or_tab=row.get("sub_ref_or_tab_optional"),
                notes=row.get("notes_optional"),
            )
        )
    return targets


def build_docs_resolution_plan(client_record_path: str | Path, source_rows_path: str | Path, output_dir: str | Path) -> Dict[str, Any]:
    client_record = _read_json(client_record_path)
    source_rows = _read_json(source_rows_path)

    client_targets = build_client_doc_targets(client_record)
    index_targets = build_source_index_doc_targets(source_rows)

    all_targets = client_targets + index_targets

    alignment_notes_target = next((asdict(t) for t in all_targets if t.label == "alignment_notes_doc_link"), None)
    strategy_targets = [asdict(t) for t in all_targets if t.source_class in {"foundational_strategy", "active_strategy"}]
    report_targets = [asdict(t) for t in all_targets if t.source_type == "prior_report"]

    resolution_plan = {
        "client_name": client_record.get("client_name"),
        "client_id_optional": client_record.get("client_id_optional"),
        "connector_required": "google_docs_drive",
        "connector_runtime_note": "Actual content fetch must be executed through a Google Docs/Drive connector in Antigravity.",
        "targets": [asdict(t) for t in all_targets],
        "alignment_notes_target": alignment_notes_target,
        "strategy_targets": strategy_targets,
        "report_targets": report_targets,
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "docs_targets.json", "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in all_targets], f, indent=2)
    with open(output_dir / "alignment_notes_target.json", "w", encoding="utf-8") as f:
        json.dump(alignment_notes_target, f, indent=2)
    with open(output_dir / "strategy_targets.json", "w", encoding="utf-8") as f:
        json.dump(strategy_targets, f, indent=2)
    with open(output_dir / "report_targets.json", "w", encoding="utf-8") as f:
        json.dump(report_targets, f, indent=2)
    with open(output_dir / "docs_resolution_plan.json", "w", encoding="utf-8") as f:
        json.dump(resolution_plan, f, indent=2)

    return resolution_plan
