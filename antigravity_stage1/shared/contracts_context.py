from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SourceRecord:
    source_id: str
    source_family: str
    raw_label: str
    normalized_label: str
    last_updated: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContextBundle:
    client_id: str
    sources: List[SourceRecord]
    notes: List[Dict[str, Any]]
    reports: List[Dict[str, Any]]
    strategy_docs: List[Dict[str, Any]]
    basecamp_data: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "sources": [s.to_dict() for s in self.sources],
            "notes": self.notes,
            "reports": self.reports,
            "strategy_docs": self.strategy_docs,
            "basecamp_data": self.basecamp_data,
        }


@dataclass
class ContextLoadResult:
    bundle: ContextBundle
    missing_sources: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle": self.bundle.to_dict(),
            "missing_sources": self.missing_sources,
            "warnings": self.warnings,
        }
