from __future__ import annotations

from typing import Any, Dict, List, Optional

from antigravity_stage1.shared.state_machine import transition_call_state
from antigravity_stage1.shared.contracts_runtime import Build1State
from antigravity_stage1.shared.snapshot import append_snapshot_event

from .mcp_resolver import resolve_all_targets
from .mcp_fetcher import fetch_targets


def _flatten_loaded_sources(grouped_contexts):
    all_sources = []
    for group_name, ctx in grouped_contexts.items():
        for item in ctx.loaded_sources:
            payload = item.to_dict()
            payload["group"] = group_name
            all_sources.append(payload)
    return all_sources


def build_context_bundle_v2(
    call_run,
    workspace_bundle: Dict[str, Any],
    *,
    registry_path: Optional[str] = None,
    manifest=None,
    p0_steering: Optional[List[str]] = None,
) -> Dict[str, Any]:

    grouped_targets = resolve_all_targets(workspace_bundle, registry_path)

    grouped_contexts = {}
    missing_sources = []
    warnings = []

    for group_name, targets in grouped_targets.items():
        ctx = fetch_targets(targets)
        grouped_contexts[group_name] = ctx
        missing_sources.extend(ctx.missing_sources)
        warnings.extend(ctx.warnings)

    if manifest is not None:
        append_snapshot_event(
            manifest,
            "context_load_completed",
            f"Loaded {len(_flatten_loaded_sources(grouped_contexts))} sources via MCP layer",
        )

    context_bundle = {
        "p0_steering": list(p0_steering or []),
        "grouped_context": {
            group: [item.to_dict() for item in ctx.loaded_sources]
            for group, ctx in grouped_contexts.items()
        },
        "all_loaded_sources": _flatten_loaded_sources(grouped_contexts),
        "missing_sources": list(set(missing_sources)),
        "warnings": list(set(warnings)),
    }

    allowed, reason = transition_call_state(call_run, Build1State.CONTEXT_LOADED.value)
    if not allowed:
        raise ValueError(reason)

    return context_bundle
