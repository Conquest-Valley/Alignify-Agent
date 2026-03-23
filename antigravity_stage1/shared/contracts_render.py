from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class AgendaSection:
    section_key: str
    display_label: str
    body_lines: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: str = "medium"
    is_required: bool = True
    is_suppressed: bool = False
    suppression_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VisualEvidenceItem:
    visual_ref: str
    visual_type: str
    title: str
    rationale: str
    source_ref: str
    inserted_as: str = "link"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrainstormState:
    brainstorm_due: bool
    meetings_since_brainstorm: int
    last_brainstorm_date: str | None
    should_render_section: bool
    rationale: str
    suggested_topics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgendaDraft:
    call_run_id: str
    client_id: str
    sections: List[AgendaSection] = field(default_factory=list)
    visual_evidence: List[VisualEvidenceItem] = field(default_factory=list)
    brainstorm_state: BrainstormState | None = None
    rendered_location: str = ""
    draft_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_run_id": self.call_run_id,
            "client_id": self.client_id,
            "sections": [item.to_dict() for item in self.sections],
            "visual_evidence": [item.to_dict() for item in self.visual_evidence],
            "brainstorm_state": None if self.brainstorm_state is None else self.brainstorm_state.to_dict(),
            "rendered_location": self.rendered_location,
            "draft_version": self.draft_version,
        }


def should_render_visuals(current_count: int, max_visuals: int = 3) -> bool:
    return current_count < max_visuals


def make_suppressed_section(section_key: str, display_label: str, reason: str) -> AgendaSection:
    return AgendaSection(
        section_key=section_key,
        display_label=display_label,
        body_lines=[],
        evidence_refs=[],
        confidence="low",
        is_required=False,
        is_suppressed=True,
        suppression_reason=reason,
    )
