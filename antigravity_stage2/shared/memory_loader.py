from __future__ import annotations

import json
from typing import Any, Dict, Optional

from antigravity_stage1.shared.snapshot import register_source, append_snapshot_event

from .source_registry import get_source_descriptor, read_descriptor_content


REQUIRED_MEMORY_KEYS = {
    'client_id',
    'client_name',
    'industry',
    'service_mix',
    'north_star_goals',
    'preferred_language_style',
    'what_counts_as_a_win',
    'recurring_concerns',
    'recurring_blockers',
    'sensitive_topics',
    'approval_patterns',
    'known_reporting_caveats',
    'preferred_workstream_order',
    'sentiment_markers',
    'last_updated',
}


def load_client_memory(workspace_bundle: Dict[str, Any], registry_path: Optional[str] = None, manifest=None) -> Dict[str, Any]:
    descriptor = get_source_descriptor(workspace_bundle['memory_ref'], registry_path)
    content = read_descriptor_content(descriptor, registry_path)
    if manifest is not None:
        register_source(manifest, workspace_bundle['memory_ref'])
        append_snapshot_event(manifest, 'client_memory_loaded', f"Loaded client memory: {workspace_bundle['memory_ref']}")
    memory = json.loads(content)
    missing = REQUIRED_MEMORY_KEYS - set(memory.keys())
    if missing:
        raise ValueError(f'Client memory missing keys: {sorted(missing)}')
    return memory
