from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .mcp_types import MCPSourceTarget
from .source_registry import get_client_record, get_source_descriptor


SOURCE_FAMILY_ALIASES = {
    "google_doc": "google_workspace_doc",
    "google_sheet": "google_workspace_sheet",
    "ga4": "google_marketing_ga4",
    "gsc": "google_marketing_gsc",
    "basecamp": "basecamp_execution",
    "basecamp_message": "basecamp_message",
    "producer_note": "producer_note",
}


GROUP_TO_WORKSPACE_KEYS = {
    "foundational_strategy": ("strategy_doc_refs", "overview_doc_refs"),
    "active_strategy": ("quarterly_strategy_ref",),
    "narrative_memory": ("prior_report_refs", "prior_call_note_refs"),
    "live_execution_truth": ("basecamp_refs", "reporting_refs"),
    "producer_notes": ("producer_note_refs",),
}


def normalize_source_family(raw_family: Optional[str], descriptor: Dict[str, Any]) -> str:
    candidate = raw_family or descriptor.get("source_family") or descriptor.get("source_class") or descriptor.get("kind") or "mcp_unknown"
    return SOURCE_FAMILY_ALIASES.get(candidate, candidate)


def descriptor_to_target(source_ref: str, descriptor: Dict[str, Any]) -> MCPSourceTarget:
    raw_label = descriptor.get("label") or descriptor.get("title") or descriptor.get("name") or source_ref
    normalized_label = descriptor.get("normalized_label") or raw_label
    retrieval_mode = descriptor.get("retrieval_mode") or descriptor.get("kind") or "registry_fallback"
    location = descriptor.get("location") or descriptor.get("external_ref") or source_ref
    return MCPSourceTarget(
        source_ref=source_ref,
        source_family=normalize_source_family(descriptor.get("source_family"), descriptor),
        raw_label=raw_label,
        normalized_label=normalized_label,
        retrieval_mode=retrieval_mode,
        location=location,
        metadata={
            "reporting_window": descriptor.get("reporting_window"),
            "version_identified": descriptor.get("version_identified", False),
            "matches_active_benchmark_period": descriptor.get("matches_active_benchmark_period", False),
            "run_bounded": descriptor.get("run_bounded", False),
            "current_run_fetch": descriptor.get("current_run_fetch", False),
            "source_class": descriptor.get("source_class", "other"),
        },
    )


def _ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    return [str(value)]


def resolve_group_source_refs(workspace_bundle: Dict[str, Any], group_name: str) -> List[str]:
    refs: List[str] = []
    for key in GROUP_TO_WORKSPACE_KEYS[group_name]:
        refs.extend(_ensure_list(workspace_bundle.get(key)))
    return refs


def resolve_group_targets(workspace_bundle: Dict[str, Any], group_name: str, registry_path: Optional[str] = None) -> List[MCPSourceTarget]:
    targets: List[MCPSourceTarget] = []
    for source_ref in resolve_group_source_refs(workspace_bundle, group_name):
        descriptor = get_source_descriptor(source_ref, registry_path)
        targets.append(descriptor_to_target(source_ref, descriptor))
    return targets


def resolve_workspace_bundle(client_id: str, registry_path: Optional[str] = None) -> Dict[str, Any]:
    record = get_client_record(client_id, registry_path)
    workspace_bundle = dict(record)
    workspace_bundle.setdefault("client_id", client_id)
    return workspace_bundle


def resolve_all_targets(workspace_bundle: Dict[str, Any], registry_path: Optional[str] = None) -> Dict[str, List[MCPSourceTarget]]:
    return {
        group_name: resolve_group_targets(workspace_bundle, group_name, registry_path)
        for group_name in GROUP_TO_WORKSPACE_KEYS
    }
