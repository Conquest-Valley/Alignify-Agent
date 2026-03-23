from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MCPSourceTarget:
    source_ref: str
    source_family: str
    raw_label: str
    normalized_label: str
    retrieval_mode: str
    location: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MCPLoadedSource:
    target: MCPSourceTarget
    content: str
    loaded_at: str
    last_updated: Optional[str]
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["target"] = self.target.to_dict()
        return payload


@dataclass
class MCPContextLoad:
    loaded_sources: List[MCPLoadedSource] = field(default_factory=list)
    missing_sources: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loaded_sources": [item.to_dict() for item in self.loaded_sources],
            "missing_sources": self.missing_sources,
            "warnings": self.warnings,
        }
