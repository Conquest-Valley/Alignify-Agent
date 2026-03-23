from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

from .mcp_types import MCPContextLoad, MCPLoadedSource, MCPSourceTarget
from .source_registry import read_descriptor_content, get_source_descriptor


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def fetch_via_mcp_stub(target: MCPSourceTarget) -> Tuple[str, List[str]]:
    """
    Placeholder MCP execution layer.
    This is where real MCP calls will be wired.
    For now, we fallback to descriptor reading to preserve functionality.
    """
    warnings: List[str] = []

    try:
        descriptor = get_source_descriptor(target.source_ref)
        content = read_descriptor_content(descriptor)
        warnings.append("mcp_stub_fallback_used")
        return content, warnings
    except Exception as e:
        return "", [f"fetch_failed:{str(e)}"]


def fetch_targets(targets: List[MCPSourceTarget]) -> MCPContextLoad:
    context = MCPContextLoad()

    for target in targets:
        content, warnings = fetch_via_mcp_stub(target)

        if not content:
            context.missing_sources.append(target.source_ref)
            continue

        context.loaded_sources.append(
            MCPLoadedSource(
                target=target,
                content=content,
                loaded_at=_now_iso(),
                last_updated=None,
                warnings=warnings,
            )
        )

        context.warnings.extend(warnings)

    return context
