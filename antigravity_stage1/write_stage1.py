from pathlib import Path
import json
import textwrap

root = Path('/mnt/data/antigravity_stage1')

files = {}

# JSON Schema helpers
schema_base = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
}

def dump_json(obj):
    return json.dumps(obj, indent=2) + "\n"

confidence_enum = ["high", "medium", "low"]
campaign_categories = [
  "Strategy",
  "SEO / Copy",
  "Local SEO / GBP",
  "Web Development",
  "CRO",
  "Analytics / Tracking",
  "Link Building / Authority",
  "Paid Media",
  "Social / Community",
  "Email / CRM",
  "Approvals / Client Dependencies",
  "Internal Blockers"
]

build1_states = [
  "scheduled",
  "pre_call_requested",
  "context_loaded",
  "strategy_extracted",
  "campaign_status_built",
  "commitments_reconciled",
  "wins_ranked",
  "downturns_explained",
  "ambiguities_flagged",
  "agenda_rendered",
  "awaiting_dp_pre_call_review"
]

# Shared defs via local references for schema files

def string_array(min_items=0):
    out = {"type": "array", "items": {"type": "string"}}
    if min_items:
        out["minItems"] = min_items
    return out

iso_datetime = {"type": "string", "format": "date-time"}
iso_date = {"type": ["string", "null"], "format": "date"}

schemas = {}

schemas['call_run.schema.json'] = {
    **schema_base,
    "title": "CallRun",
    "required": [
        "call_run_id", "client_id", "dp_id", "scheduled_at", "p0_instruction",
        "current_state", "source_refs", "created_at", "updated_at"
    ],
    "properties": {
        "call_run_id": {"type": "string", "minLength": 1},
        "client_id": {"type": "string", "minLength": 1},
        "dp_id": {"type": "string", "minLength": 1},
        "scheduled_at": iso_datetime,
        "p0_instruction": {"type": "string"},
        "current_state": {"type": "string", "enum": build1_states},
        "source_refs": string_array(),
        "created_at": iso_datetime,
        "updated_at": iso_datetime,
    }
}

schemas['client_memory.schema.json'] = {
    **schema_base,
    "title": "ClientMemory",
    "required": [
        "client_id", "client_name", "industry", "service_mix", "north_star_goals",
        "preferred_language_style", "what_counts_as_a_win", "recurring_concerns",
        "recurring_blockers", "sensitive_topics", "approval_patterns",
        "known_reporting_caveats", "preferred_workstream_order", "sentiment_markers",
        "last_updated"
    ],
    "properties": {
        "client_id": {"type": "string"},
        "client_name": {"type": "string"},
        "industry": {"type": "string"},
        "service_mix": string_array(),
        "north_star_goals": string_array(1),
        "preferred_language_style": {"type": "string"},
        "what_counts_as_a_win": string_array(),
        "recurring_concerns": string_array(),
        "recurring_blockers": string_array(),
        "sensitive_topics": string_array(),
        "approval_patterns": string_array(),
        "known_reporting_caveats": string_array(),
        "preferred_workstream_order": string_array(),
        "sentiment_markers": string_array(),
        "last_updated": iso_datetime,
    }
}

schemas['client_workspace_bundle.schema.json'] = {
    **schema_base,
    "title": "ClientWorkspaceBundle",
    "required": [
        "client_id", "client_name", "strategy_doc_refs", "quarterly_strategy_ref",
        "overview_doc_refs", "prior_report_refs", "prior_call_note_refs", "basecamp_refs",
        "reporting_refs", "producer_note_refs", "template_ref", "memory_ref"
    ],
    "properties": {
        "client_id": {"type": "string"},
        "client_name": {"type": "string"},
        "strategy_doc_refs": string_array(),
        "quarterly_strategy_ref": {"type": "string"},
        "overview_doc_refs": string_array(),
        "prior_report_refs": string_array(),
        "prior_call_note_refs": string_array(),
        "basecamp_refs": string_array(),
        "reporting_refs": string_array(),
        "producer_note_refs": string_array(),
        "template_ref": {"type": "string"},
        "memory_ref": {"type": "string"},
    }
}

schemas['context_bundle.schema.json'] = {
    **schema_base,
    "title": "ContextBundle",
    "required": [
        "p0_steering", "foundational_strategy", "active_strategy", "narrative_memory",
        "live_execution_truth", "producer_notes", "provenance_map"
    ],
    "properties": {
        "p0_steering": string_array(),
        "foundational_strategy": string_array(),
        "active_strategy": string_array(),
        "narrative_memory": string_array(),
        "live_execution_truth": string_array(),
        "producer_notes": string_array(),
        "provenance_map": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["context_key", "source_refs"],
                "properties": {
                    "context_key": {"type": "string"},
                    "source_refs": string_array(),
                },
            },
        },
    }
}

schemas['strategy_summary.schema.json'] = {
    **schema_base,
    "title": "StrategySummary",
    "required": [
        "north_star_goals", "current_quarter_priorities", "success_definitions",
        "workstream_goal_map", "client_value_signals", "active_benchmark_period",
        "source_refs", "confidence"
    ],
    "properties": {
        "north_star_goals": string_array(1),
        "current_quarter_priorities": string_array(1),
        "success_definitions": string_array(),
        "workstream_goal_map": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["workstream", "goal"],
                "properties": {
                    "workstream": {"type": "string"},
                    "goal": {"type": "string"},
                },
            },
        },
        "client_value_signals": string_array(),
        "active_benchmark_period": {"type": "string"},
        "source_refs": string_array(1),
        "confidence": {"type": "string", "enum": confidence_enum},
    }
}

schemas['narrative_summary_lite.schema.json'] = {
    **schema_base,
    "title": "NarrativeSummaryLite",
    "required": [
        "recurring_themes", "prior_promises", "unresolved_topics", "prior_resonant_wins",
        "continuity_risks", "source_refs", "confidence"
    ],
    "properties": {
        "recurring_themes": string_array(),
        "prior_promises": string_array(),
        "unresolved_topics": string_array(),
        "prior_resonant_wins": string_array(),
        "continuity_risks": string_array(),
        "source_refs": string_array(),
        "confidence": {"type": "string", "enum": confidence_enum},
    }
}

schemas['campaign_status_matrix.schema.json'] = {
    **schema_base,
    "title": "CampaignStatusMatrix",
    "required": ["categories"],
    "properties": {
        "categories": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "category", "completed_since_last_call", "in_progress", "blocked",
                    "waiting_on_client", "queued_next", "risk_level",
                    "quarterly_alignment_score", "alignment_notes", "source_refs"
                ],
                "properties": {
                    "category": {"type": "string", "enum": campaign_categories},
                    "completed_since_last_call": string_array(),
                    "in_progress": string_array(),
                    "blocked": string_array(),
                    "waiting_on_client": string_array(),
                    "queued_next": string_array(),
                    "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
                    "quarterly_alignment_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "alignment_notes": string_array(),
                    "source_refs": string_array(),
                },
            },
        }
    }
}

schemas['commitment_audit_lite.schema.json'] = {
    **schema_base,
    "title": "CommitmentAuditLite",
    "required": ["commitments"],
    "properties": {
        "commitments": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "commitment_id", "source_call_date", "commitment_text", "owner",
                    "due_date", "matched_basecamp_task", "status", "evidence_refs", "confidence"
                ],
                "properties": {
                    "commitment_id": {"type": "string"},
                    "source_call_date": {"type": "string", "format": "date"},
                    "commitment_text": {"type": "string"},
                    "owner": {"type": "string"},
                    "due_date": iso_date,
                    "matched_basecamp_task": {"type": ["string", "null"]},
                    "status": {"type": "string", "enum": ["completed", "active", "blocked", "stale", "unmatched"]},
                    "evidence_refs": string_array(),
                    "confidence": {"type": "string", "enum": confidence_enum},
                },
            },
        }
    }
}

schemas['win_ranked_list.schema.json'] = {
    **schema_base,
    "title": "WinRankedList",
    "required": ["wins"],
    "properties": {
        "wins": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "win_id", "type", "category", "headline", "description",
                    "strategic_goal_alignment", "client_relevance_score", "freshness_window",
                    "evidence_refs", "confidence"
                ],
                "properties": {
                    "win_id": {"type": "string"},
                    "type": {"type": "string", "enum": ["performance", "execution", "strategic"]},
                    "category": {"type": "string", "enum": campaign_categories},
                    "headline": {"type": "string"},
                    "description": {"type": "string"},
                    "strategic_goal_alignment": {"type": "string"},
                    "client_relevance_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "freshness_window": {"type": "string"},
                    "evidence_refs": string_array(),
                    "confidence": {"type": "string", "enum": confidence_enum},
                },
            },
        }
    }
}

schemas['downturn_assessment_lite.schema.json'] = {
    **schema_base,
    "title": "DownturnAssessmentLite",
    "required": ["findings"],
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "issue", "metric", "observed_change", "candidate_cause", "support_level",
                    "evidence_refs", "confidence", "needs_human_input"
                ],
                "properties": {
                    "issue": {"type": "string"},
                    "metric": {"type": "string"},
                    "observed_change": {"type": "string"},
                    "candidate_cause": {"type": "string"},
                    "support_level": {"type": "string", "enum": ["supported", "partial", "unsupported"]},
                    "evidence_refs": string_array(),
                    "confidence": {"type": "string", "enum": confidence_enum},
                    "needs_human_input": {"type": "boolean"},
                },
            },
        }
    }
}

schemas['ambiguity_list.schema.json'] = {
    **schema_base,
    "title": "AmbiguityList",
    "required": ["items"],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "topic", "why_unclear", "missing_source", "risk_if_assumed",
                    "recommended_input", "highlight_priority"
                ],
                "properties": {
                    "topic": {"type": "string"},
                    "why_unclear": {"type": "string"},
                    "missing_source": {"type": "string"},
                    "risk_if_assumed": {"type": "string"},
                    "recommended_input": {"type": "string"},
                    "highlight_priority": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            },
        }
    }
}

schemas['agenda_draft.schema.json'] = {
    **schema_base,
    "title": "AgendaDraft",
    "required": [
        "type", "call_run_id", "content_sections", "evidence_refs", "confidence", "approved",
        "rendered_location"
    ],
    "properties": {
        "type": {"type": "string", "const": "pre_call_agenda"},
        "call_run_id": {"type": "string"},
        "content_sections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["section_name", "content", "evidence_refs", "confidence"],
                "properties": {
                    "section_name": {"type": "string"},
                    "content": {"type": "string"},
                    "evidence_refs": string_array(),
                    "confidence": {"type": "string", "enum": confidence_enum},
                },
            },
        },
        "evidence_refs": string_array(),
        "confidence": {"type": "string", "enum": confidence_enum},
        "approved": {"type": "boolean"},
        "rendered_location": {"type": ["string", "null"]},
    }
}

schemas['evidence_ref.schema.json'] = {
    **schema_base,
    "title": "EvidenceRef",
    "required": ["source_type", "source_ref", "source_timestamp_or_window", "observation", "confidence"],
    "properties": {
        "source_type": {"type": "string"},
        "source_ref": {"type": "string"},
        "source_timestamp_or_window": {"type": "string"},
        "observation": {"type": "string"},
        "confidence": {"type": "string", "enum": confidence_enum},
    }
}

schemas['run_snapshot_manifest.schema.json'] = {
    **schema_base,
    "title": "RunSnapshotManifest",
    "required": [
        "call_run_id", "client_id", "retrieved_source_refs", "retrieval_timestamps", "reporting_windows",
        "prior_call_date_used", "quarterly_strategy_ref_used", "template_ref_used", "agenda_version",
        "validation_version", "snapshot_events"
    ],
    "properties": {
        "call_run_id": {"type": "string"},
        "client_id": {"type": "string"},
        "retrieved_source_refs": string_array(),
        "retrieval_timestamps": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["source_ref", "retrieved_at"],
                "properties": {
                    "source_ref": {"type": "string"},
                    "retrieved_at": iso_datetime,
                },
            },
        },
        "reporting_windows": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["source_ref", "window_label"],
                "properties": {
                    "source_ref": {"type": "string"},
                    "window_label": {"type": "string"},
                },
            },
        },
        "prior_call_date_used": iso_date,
        "quarterly_strategy_ref_used": {"type": ["string", "null"]},
        "template_ref_used": {"type": ["string", "null"]},
        "agenda_version": {"type": "string"},
        "validation_version": {"type": "string"},
        "snapshot_events": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["event_type", "event_at", "details"],
                "properties": {
                    "event_type": {"type": "string"},
                    "event_at": iso_datetime,
                    "details": {"type": "string"},
                },
            },
        },
    }
}

schemas['freshness_assessment.schema.json'] = {
    **schema_base,
    "title": "FreshnessAssessment",
    "required": ["source_ref", "source_class", "freshness_status", "reason"],
    "properties": {
        "source_ref": {"type": "string"},
        "source_class": {"type": "string", "enum": ["strategy", "quarterly_strategy", "prior_note", "prior_report", "basecamp", "ga4", "gsc", "producer_note", "other"]},
        "freshness_status": {"type": "string", "enum": ["fresh", "acceptable_for_continuity", "stale", "unknown"]},
        "reason": {"type": "string"},
    }
}

schemas['section_validation_report.schema.json'] = {
    **schema_base,
    "title": "SectionValidationReport",
    "required": ["call_run_id", "sections", "overall_valid"],
    "properties": {
        "call_run_id": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["section_name", "is_valid", "checks_passed", "checks_failed", "required_follow_up"],
                "properties": {
                    "section_name": {"type": "string"},
                    "is_valid": {"type": "boolean"},
                    "checks_passed": string_array(),
                    "checks_failed": string_array(),
                    "required_follow_up": string_array(),
                },
            },
        },
        "overall_valid": {"type": "boolean"},
    }
}

schemas['manual_override_log.schema.json'] = {
    **schema_base,
    "title": "ManualOverrideLog",
    "required": ["call_run_id", "dp_id", "overrides"],
    "properties": {
        "call_run_id": {"type": "string"},
        "dp_id": {"type": "string"},
        "overrides": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["section", "original_text", "edited_text", "reason_code", "timestamp"],
                "properties": {
                    "section": {"type": "string"},
                    "original_text": {"type": "string"},
                    "edited_text": {"type": "string"},
                    "reason_code": {"type": "string"},
                    "timestamp": iso_datetime,
                },
            },
        },
    }
}

schemas['category_alias_map.schema.json'] = {
    **schema_base,
    "title": "CategoryAliasMap",
    "required": ["aliases"],
    "properties": {
        "aliases": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["alias", "canonical_category"],
                "properties": {
                    "alias": {"type": "string"},
                    "canonical_category": {"type": "string", "enum": campaign_categories},
                },
            },
        }
    }
}

schemas['context_conflict_resolution.schema.json'] = {
    **schema_base,
    "title": "ContextConflictResolution",
    "required": ["conflicts"],
    "properties": {
        "conflicts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["topic", "higher_priority_source", "lower_priority_source", "resolution", "reason"],
                "properties": {
                    "topic": {"type": "string"},
                    "higher_priority_source": {"type": "string"},
                    "lower_priority_source": {"type": "string"},
                    "resolution": {"type": "string", "enum": ["resolved", "flagged_for_input_required"]},
                    "reason": {"type": "string"},
                },
            },
        }
    }
}

for name, schema in schemas.items():
    files[f'schemas/{name}'] = dump_json(schema)

# validation and run_state files
files['validation/confidence_rules.json'] = dump_json({
    "bands": confidence_enum,
    "scoring_guide": {
        "high": {
            "minimum_evidence_count": 2,
            "source_agreement_required": True,
            "contradiction_allowed": False
        },
        "medium": {
            "minimum_evidence_count": 1,
            "source_agreement_required": False,
            "contradiction_allowed": False
        },
        "low": {
            "minimum_evidence_count": 0,
            "source_agreement_required": False,
            "contradiction_allowed": True
        }
    }
})

files['validation/freshness_rules.json'] = dump_json({
    "strategy": "acceptable_if_version_identified",
    "quarterly_strategy": "must_match_active_benchmark_period",
    "prior_report": "continuity_only",
    "prior_note": "continuity_only",
    "basecamp": "current_run_fetch_only",
    "ga4": "explicit_reporting_window_required",
    "gsc": "explicit_reporting_window_required",
    "producer_note": "run_bounded_only",
    "other": "unknown_until_classified"
})

files['validation/section_rules.json'] = dump_json({
    "Meeting Summary": [
        "must_include_strategy_anchor",
        "must_include_current_truth_anchor"
    ],
    "Pending Approvals": [
        "must_have_evidence"
    ],
    "Wins / Highlights": [
        "must_have_evidence",
        "must_have_strategic_relevance"
    ],
    "Input Required": [
        "must_exist_when_unresolved_low_confidence_conflict_present"
    ]
})

# state transitions allowed map
allowed_transitions = {
    "scheduled": ["pre_call_requested"],
    "pre_call_requested": ["context_loaded"],
    "context_loaded": ["strategy_extracted"],
    "strategy_extracted": ["campaign_status_built"],
    "campaign_status_built": ["commitments_reconciled", "wins_ranked"],
    "commitments_reconciled": ["wins_ranked"],
    "wins_ranked": ["downturns_explained", "ambiguities_flagged"],
    "downturns_explained": ["ambiguities_flagged"],
    "ambiguities_flagged": ["agenda_rendered"],
    "agenda_rendered": ["awaiting_dp_pre_call_review"],
    "awaiting_dp_pre_call_review": []
}
files['validation/state_transition_rules.json'] = dump_json({"allowed_transitions": allowed_transitions})

files['validation/taxonomy.json'] = dump_json({
    "canonical_categories": campaign_categories,
    "default_aliases": [
        {"alias": "ppc", "canonical_category": "Paid Media"},
        {"alias": "paid search", "canonical_category": "Paid Media"},
        {"alias": "dev", "canonical_category": "Web Development"},
        {"alias": "development", "canonical_category": "Web Development"},
        {"alias": "tracking", "canonical_category": "Analytics / Tracking"},
        {"alias": "analytics", "canonical_category": "Analytics / Tracking"},
        {"alias": "content", "canonical_category": "SEO / Copy"},
        {"alias": "seo", "canonical_category": "SEO / Copy"},
        {"alias": "gbp", "canonical_category": "Local SEO / GBP"},
        {"alias": "approvals", "canonical_category": "Approvals / Client Dependencies"}
    ]
})

files['run_state/build1_states.json'] = dump_json(build1_states)
files['run_state/snapshot_event_types.json'] = dump_json([
    "run_initialized",
    "source_registered",
    "reporting_window_registered",
    "validation_version_set",
    "agenda_render_attempted",
    "manual_override_recorded",
    "snapshot_finalized"
])

# prompts notes
files['prompts/stage_contract_notes.md'] = textwrap.dedent('''
    # Stage 1 Contract Notes

    This package is the contract and guardrail layer for Build 1.

    Rules:
    1. Stage 1 defines schemas, enums, rules, and shared helper functions only.
    2. Stage 1 does not fetch live sources.
    3. Stage 1 does not perform strategy reasoning.
    4. Stage 1 does not compose agenda text.
    5. Later stages must import and use these contracts instead of redefining them.

    Shared design principles:
    - Evidence first
    - Never guess
    - Weighted context, not blind override
    - Typed objects between stages
    - Human gate before client facing output
''').lstrip()

# Python shared modules
files['shared/__init__.py'] = textwrap.dedent('''
    from .contracts_runtime import *
    from .state_machine import *
    from .evidence import *
    from .freshness import *
    from .taxonomy import *
    from .validation import *
    from .snapshot import *
''').lstrip()

files['shared/contracts_runtime.py'] = textwrap.dedent('''
    from __future__ import annotations

    from dataclasses import dataclass, field, asdict
    from datetime import datetime, timezone
    from enum import Enum
    from typing import Any, Dict, List, Optional
    from uuid import uuid4


    def utc_now_iso() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


    class ConfidenceBand(str, Enum):
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"


    class Build1State(str, Enum):
        SCHEDULED = "scheduled"
        PRE_CALL_REQUESTED = "pre_call_requested"
        CONTEXT_LOADED = "context_loaded"
        STRATEGY_EXTRACTED = "strategy_extracted"
        CAMPAIGN_STATUS_BUILT = "campaign_status_built"
        COMMITMENTS_RECONCILED = "commitments_reconciled"
        WINS_RANKED = "wins_ranked"
        DOWNTURNS_EXPLAINED = "downturns_explained"
        AMBIGUITIES_FLAGGED = "ambiguities_flagged"
        AGENDA_RENDERED = "agenda_rendered"
        AWAITING_DP_PRE_CALL_REVIEW = "awaiting_dp_pre_call_review"


    class CampaignCategory(str, Enum):
        STRATEGY = "Strategy"
        SEO_COPY = "SEO / Copy"
        LOCAL_SEO_GBP = "Local SEO / GBP"
        WEB_DEVELOPMENT = "Web Development"
        CRO = "CRO"
        ANALYTICS_TRACKING = "Analytics / Tracking"
        LINK_BUILDING_AUTHORITY = "Link Building / Authority"
        PAID_MEDIA = "Paid Media"
        SOCIAL_COMMUNITY = "Social / Community"
        EMAIL_CRM = "Email / CRM"
        APPROVALS_CLIENT_DEPENDENCIES = "Approvals / Client Dependencies"
        INTERNAL_BLOCKERS = "Internal Blockers"


    @dataclass
    class EvidenceRef:
        source_type: str
        source_ref: str
        source_timestamp_or_window: str
        observation: str
        confidence: str

        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)


    @dataclass
    class CallRun:
        call_run_id: str
        client_id: str
        dp_id: str
        scheduled_at: str
        p0_instruction: str
        current_state: str
        source_refs: List[str] = field(default_factory=list)
        created_at: str = field(default_factory=utc_now_iso)
        updated_at: str = field(default_factory=utc_now_iso)

        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)


    @dataclass
    class FreshnessAssessment:
        source_ref: str
        source_class: str
        freshness_status: str
        reason: str

        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)


    @dataclass
    class SnapshotTimestamp:
        source_ref: str
        retrieved_at: str


    @dataclass
    class SnapshotWindow:
        source_ref: str
        window_label: str


    @dataclass
    class SnapshotEvent:
        event_type: str
        event_at: str
        details: str


    @dataclass
    class RunSnapshotManifest:
        call_run_id: str
        client_id: str
        retrieved_source_refs: List[str] = field(default_factory=list)
        retrieval_timestamps: List[SnapshotTimestamp] = field(default_factory=list)
        reporting_windows: List[SnapshotWindow] = field(default_factory=list)
        prior_call_date_used: Optional[str] = None
        quarterly_strategy_ref_used: Optional[str] = None
        template_ref_used: Optional[str] = None
        agenda_version: str = "v1"
        validation_version: str = "v1"
        snapshot_events: List[SnapshotEvent] = field(default_factory=list)

        def to_dict(self) -> Dict[str, Any]:
            return {
                "call_run_id": self.call_run_id,
                "client_id": self.client_id,
                "retrieved_source_refs": self.retrieved_source_refs,
                "retrieval_timestamps": [asdict(item) for item in self.retrieval_timestamps],
                "reporting_windows": [asdict(item) for item in self.reporting_windows],
                "prior_call_date_used": self.prior_call_date_used,
                "quarterly_strategy_ref_used": self.quarterly_strategy_ref_used,
                "template_ref_used": self.template_ref_used,
                "agenda_version": self.agenda_version,
                "validation_version": self.validation_version,
                "snapshot_events": [asdict(item) for item in self.snapshot_events],
            }


    @dataclass
    class SectionCheckResult:
        section_name: str
        is_valid: bool
        checks_passed: List[str] = field(default_factory=list)
        checks_failed: List[str] = field(default_factory=list)
        required_follow_up: List[str] = field(default_factory=list)


    @dataclass
    class SectionValidationReport:
        call_run_id: str
        sections: List[SectionCheckResult]
        overall_valid: bool

        def to_dict(self) -> Dict[str, Any]:
            return {
                "call_run_id": self.call_run_id,
                "sections": [asdict(item) for item in self.sections],
                "overall_valid": self.overall_valid,
            }


    @dataclass
    class OverrideEntry:
        section: str
        original_text: str
        edited_text: str
        reason_code: str
        timestamp: str


    @dataclass
    class ManualOverrideLog:
        call_run_id: str
        dp_id: str
        overrides: List[OverrideEntry] = field(default_factory=list)

        def to_dict(self) -> Dict[str, Any]:
            return {
                "call_run_id": self.call_run_id,
                "dp_id": self.dp_id,
                "overrides": [asdict(item) for item in self.overrides],
            }


    @dataclass
    class ConflictRecord:
        topic: str
        higher_priority_source: str
        lower_priority_source: str
        resolution: str
        reason: str


    @dataclass
    class ContextConflictResolution:
        conflicts: List[ConflictRecord] = field(default_factory=list)

        def to_dict(self) -> Dict[str, Any]:
            return {"conflicts": [asdict(item) for item in self.conflicts]}


    def create_call_run(client_id: str, dp_id: str, scheduled_at: str, p0_instruction: str = "") -> CallRun:
        if not client_id:
            raise ValueError("client_id is required")
        if not dp_id:
            raise ValueError("dp_id is required")
        if not scheduled_at:
            raise ValueError("scheduled_at is required")
        now = utc_now_iso()
        return CallRun(
            call_run_id=f"callrun_{uuid4().hex[:12]}",
            client_id=client_id,
            dp_id=dp_id,
            scheduled_at=scheduled_at,
            p0_instruction=p0_instruction,
            current_state=Build1State.PRE_CALL_REQUESTED.value,
            source_refs=[],
            created_at=now,
            updated_at=now,
        )
''').lstrip()

files['shared/state_machine.py'] = textwrap.dedent('''
    from __future__ import annotations

    import json
    from pathlib import Path
    from typing import Dict, List, Tuple

    from .contracts_runtime import Build1State, CallRun, utc_now_iso


    RULES_PATH = Path(__file__).resolve().parent.parent / "validation" / "state_transition_rules.json"
    _rules: Dict[str, List[str]] = json.loads(RULES_PATH.read_text())["allowed_transitions"]


    def is_transition_allowed(current_state: str, proposed_next_state: str) -> bool:
        return proposed_next_state in _rules.get(current_state, [])


    def transition_call_state(call_run: CallRun, proposed_next_state: str) -> Tuple[bool, str]:
        if not is_transition_allowed(call_run.current_state, proposed_next_state):
            return False, f"Illegal transition from {call_run.current_state} to {proposed_next_state}"
        call_run.current_state = proposed_next_state
        call_run.updated_at = utc_now_iso()
        return True, "ok"
''').lstrip()

files['shared/evidence.py'] = textwrap.dedent('''
    from __future__ import annotations

    from typing import Iterable

    from .contracts_runtime import ConfidenceBand, EvidenceRef


    def create_evidence_ref(
        source_type: str,
        source_ref: str,
        source_timestamp_or_window: str,
        observation: str,
        confidence: str,
    ) -> EvidenceRef:
        if not source_type:
            raise ValueError("source_type is required")
        if not source_ref:
            raise ValueError("source_ref is required")
        if not source_timestamp_or_window:
            raise ValueError("source_timestamp_or_window is required")
        if not observation:
            raise ValueError("observation is required")
        if confidence not in {band.value for band in ConfidenceBand}:
            raise ValueError("confidence must be one of: high, medium, low")
        return EvidenceRef(
            source_type=source_type,
            source_ref=source_ref,
            source_timestamp_or_window=source_timestamp_or_window,
            observation=observation,
            confidence=confidence,
        )


    def assess_confidence_band(evidence_refs: Iterable[EvidenceRef], has_contradiction: bool = False) -> str:
        refs = list(evidence_refs)
        if has_contradiction:
            return ConfidenceBand.LOW.value
        if len(refs) >= 2:
            unique_sources = {ref.source_ref for ref in refs}
            if len(unique_sources) >= 2:
                return ConfidenceBand.HIGH.value
        if len(refs) >= 1:
            return ConfidenceBand.MEDIUM.value
        return ConfidenceBand.LOW.value
''').lstrip()

files['shared/freshness.py'] = textwrap.dedent('''
    from __future__ import annotations

    import json
    from pathlib import Path
    from typing import Optional

    from .contracts_runtime import FreshnessAssessment


    RULES_PATH = Path(__file__).resolve().parent.parent / "validation" / "freshness_rules.json"
    RULES = json.loads(RULES_PATH.read_text())


    def assess_source_freshness(
        source_ref: str,
        source_class: str,
        *,
        version_identified: bool = False,
        matches_active_benchmark_period: bool = False,
        reporting_window: Optional[str] = None,
        run_bounded: bool = False,
        current_run_fetch: bool = False,
    ) -> FreshnessAssessment:
        rule = RULES.get(source_class, RULES["other"])

        if source_class == "strategy":
            if version_identified:
                return FreshnessAssessment(source_ref, source_class, "acceptable_for_continuity", "Version identified strategy source")
            return FreshnessAssessment(source_ref, source_class, "unknown", "Strategy source missing version metadata")

        if source_class == "quarterly_strategy":
            if matches_active_benchmark_period:
                return FreshnessAssessment(source_ref, source_class, "fresh", "Quarterly strategy matches active benchmark period")
            return FreshnessAssessment(source_ref, source_class, "stale", "Quarterly strategy does not match active benchmark period")

        if source_class in {"prior_note", "prior_report"}:
            return FreshnessAssessment(source_ref, source_class, "acceptable_for_continuity", "Continuity only source")

        if source_class == "basecamp":
            if current_run_fetch:
                return FreshnessAssessment(source_ref, source_class, "fresh", "Fetched during current run")
            return FreshnessAssessment(source_ref, source_class, "stale", "Basecamp source must be fetched during current run")

        if source_class in {"ga4", "gsc"}:
            if reporting_window:
                return FreshnessAssessment(source_ref, source_class, "fresh", f"Reporting window supplied: {reporting_window}")
            return FreshnessAssessment(source_ref, source_class, "unknown", "Explicit reporting window required")

        if source_class == "producer_note":
            if run_bounded:
                return FreshnessAssessment(source_ref, source_class, "fresh", "Producer note is active for current run")
            return FreshnessAssessment(source_ref, source_class, "stale", "Producer notes must be run bounded")

        return FreshnessAssessment(source_ref, source_class, "unknown", f"Rule applied: {rule}")
''').lstrip()

files['shared/taxonomy.py'] = textwrap.dedent('''
    from __future__ import annotations

    import json
    from pathlib import Path
    from typing import Dict, Optional


    TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "validation" / "taxonomy.json"
    TAXONOMY = json.loads(TAXONOMY_PATH.read_text())
    _alias_lookup: Dict[str, str] = {
        item["alias"].strip().lower(): item["canonical_category"]
        for item in TAXONOMY["default_aliases"]
    }
    _canonical_lookup: Dict[str, str] = {
        item.strip().lower(): item
        for item in TAXONOMY["canonical_categories"]
    }


    def normalize_category_alias(raw_label: str) -> Optional[str]:
        if not raw_label:
            return None
        cleaned = raw_label.strip().lower()
        if cleaned in _canonical_lookup:
            return _canonical_lookup[cleaned]
        return _alias_lookup.get(cleaned)
''').lstrip()

files['shared/validation.py'] = textwrap.dedent('''
    from __future__ import annotations

    import json
    from pathlib import Path
    from typing import Dict, List

    from .contracts_runtime import SectionCheckResult, SectionValidationReport


    SECTION_RULES_PATH = Path(__file__).resolve().parent.parent / "validation" / "section_rules.json"
    SECTION_RULES: Dict[str, List[str]] = json.loads(SECTION_RULES_PATH.read_text())


    def validate_section_requirements(call_run_id: str, section_inputs: Dict[str, Dict[str, bool]]) -> SectionValidationReport:
        results: List[SectionCheckResult] = []
        overall_valid = True

        for section_name, rules in SECTION_RULES.items():
            provided = section_inputs.get(section_name, {})
            passed: List[str] = []
            failed: List[str] = []
            follow_up: List[str] = []

            for rule in rules:
                if provided.get(rule, False):
                    passed.append(rule)
                else:
                    failed.append(rule)
                    follow_up.append(f"Resolve rule: {rule}")

            is_valid = len(failed) == 0
            overall_valid = overall_valid and is_valid
            results.append(
                SectionCheckResult(
                    section_name=section_name,
                    is_valid=is_valid,
                    checks_passed=passed,
                    checks_failed=failed,
                    required_follow_up=follow_up,
                )
            )

        return SectionValidationReport(call_run_id=call_run_id, sections=results, overall_valid=overall_valid)
''').lstrip()

files['shared/snapshot.py'] = textwrap.dedent('''
    from __future__ import annotations

    from .contracts_runtime import (
        RunSnapshotManifest,
        SnapshotEvent,
        SnapshotTimestamp,
        SnapshotWindow,
        utc_now_iso,
    )


    def open_run_snapshot(call_run_id: str, client_id: str, agenda_version: str = "v1", validation_version: str = "v1") -> RunSnapshotManifest:
        manifest = RunSnapshotManifest(
            call_run_id=call_run_id,
            client_id=client_id,
            agenda_version=agenda_version,
            validation_version=validation_version,
        )
        manifest.snapshot_events.append(
            SnapshotEvent(
                event_type="run_initialized",
                event_at=utc_now_iso(),
                details="Snapshot opened",
            )
        )
        return manifest


    def append_snapshot_event(manifest: RunSnapshotManifest, event_type: str, details: str) -> None:
        manifest.snapshot_events.append(
            SnapshotEvent(event_type=event_type, event_at=utc_now_iso(), details=details)
        )


    def register_source(manifest: RunSnapshotManifest, source_ref: str) -> None:
        if source_ref not in manifest.retrieved_source_refs:
            manifest.retrieved_source_refs.append(source_ref)
        manifest.retrieval_timestamps.append(SnapshotTimestamp(source_ref=source_ref, retrieved_at=utc_now_iso()))
        append_snapshot_event(manifest, "source_registered", f"Registered source: {source_ref}")


    def register_reporting_window(manifest: RunSnapshotManifest, source_ref: str, window_label: str) -> None:
        manifest.reporting_windows.append(SnapshotWindow(source_ref=source_ref, window_label=window_label))
        append_snapshot_event(manifest, "reporting_window_registered", f"{source_ref} -> {window_label}")
''').lstrip()

files['requirements.txt'] = 'jsonschema==4.25.1\n'

files['README_STAGE1.md'] = textwrap.dedent('''
    # Antigravity Strategic Assistant
    ## Stage 1 package

    This package contains the Stage 1 contract and guardrail layer for Build 1.

    Included:
    - JSON Schemas for all Stage 1 objects
    - Validation rule files
    - Run state files
    - Shared Python helpers
    - Sample objects
    - Smoke test

    ## What Stage 1 does
    - Defines typed objects
    - Defines allowed state transitions
    - Defines evidence, confidence, freshness, taxonomy, snapshot, and section validation helpers

    ## What Stage 1 does not do
    - No source fetching
    - No strategy reasoning
    - No Basecamp auditing
    - No agenda writing

    ## Quick start
    1. Create a Python virtual environment.
    2. Install requirements.
    3. Run the smoke test.

    See `SETUP_INSTRUCTIONS.md` for the full click by click walkthrough.
''').lstrip()

files['SETUP_INSTRUCTIONS.md'] = textwrap.dedent('''
    # Click by click setup instructions for Stage 1

    These steps assume you are putting Stage 1 into an Antigravity project folder on your machine.

    ## Part 1. Get the files into your project
    1. Download the Stage 1 zip.
    2. Unzip it.
    3. Open the unzipped folder.
    4. Copy the folder named `antigravity_stage1`.
    5. Open your Antigravity project folder.
    6. Paste `antigravity_stage1` into your project.

    After pasting, you should see these folders inside `antigravity_stage1`:
    - schemas
    - validation
    - run_state
    - artifacts
    - prompts
    - shared
    - tests

    ## Part 2. Open the project in your code editor
    1. Open VS Code.
    2. Click `File`.
    3. Click `Open Folder`.
    4. Pick your Antigravity project folder.
    5. In the left sidebar, click the `antigravity_stage1` folder.

    ## Part 3. Create the Python environment
    1. In VS Code, click `Terminal`.
    2. Click `New Terminal`.
    3. In the terminal, type this exactly and press Enter:

       python3 -m venv .venv

    4. Activate it.

       On Mac or Linux:

       source .venv/bin/activate

       On Windows PowerShell:

       .venv\\Scripts\\Activate.ps1

    5. Install the package requirements:

       pip install -r antigravity_stage1/requirements.txt

    ## Part 4. Run the smoke test
    1. In the same terminal, run:

       python antigravity_stage1/tests/test_stage1_smoke.py

    2. If everything is correct, you should see:

       Stage 1 smoke test passed.

    ## Part 5. What to do if the smoke test fails
    1. Make sure your terminal is in the project root folder.
    2. Make sure the virtual environment is activated.
    3. Make sure you installed requirements.
    4. Run the test again.

    ## Part 6. How to use Stage 1 in later stages
    Later stage files should import from `antigravity_stage1/shared` instead of rewriting rules.

    Examples:

       from antigravity_stage1.shared.contracts_runtime import create_call_run
       from antigravity_stage1.shared.state_machine import transition_call_state
       from antigravity_stage1.shared.evidence import create_evidence_ref
       from antigravity_stage1.shared.freshness import assess_source_freshness
       from antigravity_stage1.shared.taxonomy import normalize_category_alias
       from antigravity_stage1.shared.validation import validate_section_requirements
       from antigravity_stage1.shared.snapshot import open_run_snapshot, register_source

    ## Part 7. What gets built next
    After Stage 1 is working, Stage 2 should plug into these contracts for:
    - client workspace loading
    - context retrieval
    - snapshot source registration
    - provenance tracking
''').lstrip()

# sample objects
files['artifacts/sample_objects/sample_call_run.json'] = dump_json({
    "call_run_id": "callrun_demo123",
    "client_id": "client_abc",
    "dp_id": "dp_xyz",
    "scheduled_at": "2026-03-20T15:00:00+00:00",
    "p0_instruction": "Emphasize approvals needed for homepage launch.",
    "current_state": "pre_call_requested",
    "source_refs": [],
    "created_at": "2026-03-13T12:00:00+00:00",
    "updated_at": "2026-03-13T12:00:00+00:00"
})

files['artifacts/sample_objects/sample_run_snapshot_manifest.json'] = dump_json({
    "call_run_id": "callrun_demo123",
    "client_id": "client_abc",
    "retrieved_source_refs": ["doc_quarterly_q2", "basecamp_board_1"],
    "retrieval_timestamps": [
        {"source_ref": "doc_quarterly_q2", "retrieved_at": "2026-03-13T12:01:00+00:00"}
    ],
    "reporting_windows": [
        {"source_ref": "ga4_main", "window_label": "Last 30 days"}
    ],
    "prior_call_date_used": "2026-02-27",
    "quarterly_strategy_ref_used": "doc_quarterly_q2",
    "template_ref_used": "gdoc_template_123",
    "agenda_version": "v1",
    "validation_version": "v1",
    "snapshot_events": [
        {"event_type": "run_initialized", "event_at": "2026-03-13T12:00:00+00:00", "details": "Snapshot opened"}
    ]
})

files['artifacts/sample_objects/sample_evidence_ref.json'] = dump_json({
    "source_type": "Basecamp",
    "source_ref": "task_12345",
    "source_timestamp_or_window": "current",
    "observation": "Homepage CRO staging complete",
    "confidence": "high"
})

files['artifacts/sample_objects/sample_section_validation_report.json'] = dump_json({
    "call_run_id": "callrun_demo123",
    "sections": [
        {
            "section_name": "Meeting Summary",
            "is_valid": True,
            "checks_passed": ["must_include_strategy_anchor", "must_include_current_truth_anchor"],
            "checks_failed": [],
            "required_follow_up": []
        }
    ],
    "overall_valid": True
})

files['tests/test_stage1_smoke.py'] = textwrap.dedent('''
    from pathlib import Path
    import json
    import sys

    ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT.parent))

    import jsonschema

    from antigravity_stage1.shared.contracts_runtime import create_call_run
    from antigravity_stage1.shared.state_machine import transition_call_state
    from antigravity_stage1.shared.evidence import create_evidence_ref, assess_confidence_band
    from antigravity_stage1.shared.freshness import assess_source_freshness
    from antigravity_stage1.shared.taxonomy import normalize_category_alias
    from antigravity_stage1.shared.snapshot import open_run_snapshot, register_source, register_reporting_window
    from antigravity_stage1.shared.validation import validate_section_requirements


    def load_schema(name: str):
        return json.loads((ROOT / "schemas" / name).read_text())


    def main():
        call_run = create_call_run(
            client_id="client_abc",
            dp_id="dp_123",
            scheduled_at="2026-03-20T15:00:00+00:00",
            p0_instruction="Lead with GBP wins",
        )
        jsonschema.validate(call_run.to_dict(), load_schema("call_run.schema.json"))

        ok, msg = transition_call_state(call_run, "context_loaded")
        assert ok, msg

        evidence = create_evidence_ref(
            source_type="Basecamp",
            source_ref="task_12345",
            source_timestamp_or_window="current",
            observation="Homepage CRO staging complete",
            confidence="high",
        )
        jsonschema.validate(evidence.to_dict(), load_schema("evidence_ref.schema.json"))
        assert assess_confidence_band([evidence]) == "medium"

        freshness = assess_source_freshness(
            source_ref="ga4_main",
            source_class="ga4",
            reporting_window="Last 30 days",
        )
        jsonschema.validate(freshness.to_dict(), load_schema("freshness_assessment.schema.json"))
        assert freshness.freshness_status == "fresh"

        assert normalize_category_alias("PPC") == "Paid Media"
        assert normalize_category_alias("Dev") == "Web Development"

        snapshot = open_run_snapshot(call_run.call_run_id, call_run.client_id)
        register_source(snapshot, "doc_quarterly_q2")
        register_reporting_window(snapshot, "ga4_main", "Last 30 days")
        jsonschema.validate(snapshot.to_dict(), load_schema("run_snapshot_manifest.schema.json"))

        report = validate_section_requirements(
            call_run.call_run_id,
            {
                "Meeting Summary": {
                    "must_include_strategy_anchor": True,
                    "must_include_current_truth_anchor": True,
                },
                "Pending Approvals": {
                    "must_have_evidence": True,
                },
                "Wins / Highlights": {
                    "must_have_evidence": True,
                    "must_have_strategic_relevance": True,
                },
                "Input Required": {
                    "must_exist_when_unresolved_low_confidence_conflict_present": True,
                },
            },
        )
        jsonschema.validate(report.to_dict(), load_schema("section_validation_report.schema.json"))
        assert report.overall_valid is True

        print("Stage 1 smoke test passed.")


    if __name__ == "__main__":
        main()
''').lstrip()

for rel_path, content in files.items():
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

print(f"Wrote {len(files)} files to {root}")
