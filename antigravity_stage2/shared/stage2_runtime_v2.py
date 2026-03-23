from __future__ import annotations

from typing import Any, Dict, Optional

from .workspace_loader import load_client_workspace
from .memory_loader import load_client_memory
from .context_loader_v2 import build_context_bundle_v2
from .context_guardrails import summarize_context_health, build_input_required_notes


def run_stage2_v2(
    call_run,
    client_id: str,
    *,
    registry_path: Optional[str] = None,
    manifest=None,
    p0_steering: Optional[list[str]] = None,
) -> Dict[str, Any]:
    workspace = load_client_workspace(client_id, registry_path)
    memory = load_client_memory(workspace, registry_path=registry_path, manifest=manifest)
    context = build_context_bundle_v2(
        call_run,
        workspace,
        registry_path=registry_path,
        manifest=manifest,
        p0_steering=p0_steering,
    )
    context_health = summarize_context_health(context)
    input_required_notes = build_input_required_notes(context_health)

    return {
        "workspace": workspace,
        "memory": memory,
        "context": context,
        "context_health": context_health,
        "input_required_notes": input_required_notes,
    }
