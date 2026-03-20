from __future__ import annotations

from typing import Any, Dict, Optional

from antigravity_stage1.shared.snapshot import register_source, append_snapshot_event

from .source_registry import get_source_descriptor, read_descriptor_content


def resolve_template_ref(workspace_bundle: Dict[str, Any], registry_path: Optional[str] = None, manifest=None) -> Dict[str, Any]:
    descriptor = get_source_descriptor(workspace_bundle['template_ref'], registry_path)
    content = read_descriptor_content(descriptor, registry_path)
    if manifest is not None:
        register_source(manifest, workspace_bundle['template_ref'])
        append_snapshot_event(manifest, 'template_resolved', f"Resolved template: {workspace_bundle['template_ref']}")
    return {
        'template_ref': workspace_bundle['template_ref'],
        'template_label': descriptor.get('label', workspace_bundle['template_ref']),
        'template_content': content,
    }
