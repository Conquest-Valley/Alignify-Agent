from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from antigravity_stage1.shared.contracts_runtime_v2 import Build1StateV2
from antigravity_stage1.shared.snapshot import append_snapshot_event
from antigravity_stage1.shared.state_machine_v2 import transition_call_state_v2
from antigravity_stage4.shared.stage4_runtime_v2 import run_stage4_v2


def _iter_loaded_lines(stage4: Dict[str, Any]):
    loaded_sources = stage4.get("stage3", {}).get("stage2", {}).get("context", {}).get("all_loaded_sources", [])
    for entry in loaded_sources:
        source_ref = entry.get("target", {}).get("source_ref", "unknown_source")
        content = entry.get("content", "")
        for raw_line in str(content).splitlines():
            line = raw_line.strip().rstrip(".")
            if line:
                yield source_ref, line


def _score_win(*, strategic_alignment: float, client_relevance: float, freshness: float, credibility: float, clarity: float) -> float:
    return round(
        (0.30 * strategic_alignment)
        + (0.30 * client_relevance)
        + (0.15 * freshness)
        + (0.15 * credibility)
        + (0.10 * clarity),
        4,
    )


def _match_strategy(text: str, strategy_summary: Dict[str, Any]) -> str:
    lowered = text.lower()
    for priority in strategy_summary.get("current_quarter_priorities", []):
        tokens = [token for token in re.findall(r"[a-z0-9]+", priority.lower()) if len(token) > 3]
        if any(token in lowered for token in tokens):
            return priority
    goals = strategy_summary.get("north_star_goals", [])
    return goals[0] if goals else "General strategic progress"


def _build_win_candidates(stage4: Dict[str, Any]) -> List[Dict[str, Any]]:
    strategy_summary = stage4.get("stage3", {}).get("strategy_summary", {})
    campaign_status_matrix = stage4.get("campaign_status_matrix", {})
    wins: List[Dict[str, Any]] = []

    for category in campaign_status_matrix.get("categories", []):
        category_name = category.get("category", "General")
        for task in category.get("completed_since_last_call", []):
            alignment = _match_strategy(task, strategy_summary)
            wins.append(
                {
                    "win_id": f"exec_{len(wins)+1}",
                    "type": "execution",
                    "category": category_name,
                    "headline": f"Completed: {task}",
                    "description": f"Completed since last call in {category_name}: {task}",
                    "strategic_goal_alignment": alignment,
                    "client_relevance_score": 0.82,
                    "freshness_window": "current",
                    "evidence_refs": [{"source_ref": (category.get("source_refs") or ["basecamp_unknown"])[0], "observation": task}],
                    "confidence": "medium",
                    "score": _score_win(0.85, 0.82, 0.90, 0.75, 0.90),
                }
            )
        if category.get("quarterly_alignment_score", 0) >= 70 and category.get("alignment_notes"):
            note = category["alignment_notes"][0]
            wins.append(
                {
                    "win_id": f"strat_{len(wins)+1}",
                    "type": "strategic",
                    "category": category_name,
                    "headline": f"{category_name} work is aligned to current quarter priorities",
                    "description": note,
                    "strategic_goal_alignment": note,
                    "client_relevance_score": 0.76,
                    "freshness_window": "current",
                    "evidence_refs": [{"source_ref": (category.get("source_refs") or ["basecamp_unknown"])[0], "observation": note}],
                    "confidence": "medium",
                    "score": _score_win(0.90, 0.76, 0.90, 0.70, 0.80),
                }
            )

    for source_ref, line in _iter_loaded_lines(stage4):
        lowered = line.lower()
        if any(token in lowered for token in ["up", "improved", "increase", "increased", "lift"]):
            if any(token in lowered for token in ["traffic", "click", "lead", "call", "conversion", "form", "position"]):
                alignment = _match_strategy(line, strategy_summary)
                wins.append(
                    {
                        "win_id": f"perf_{len(wins)+1}",
                        "type": "performance",
                        "category": "Performance",
                        "headline": line,
                        "description": line,
                        "strategic_goal_alignment": alignment,
                        "client_relevance_score": 0.80,
                        "freshness_window": "current_reporting_window",
                        "evidence_refs": [{"source_ref": source_ref, "observation": line}],
                        "confidence": "medium",
                        "score": _score_win(0.78, 0.80, 0.90, 0.65, 0.85),
                    }
                )

    wins.sort(key=lambda item: item["score"], reverse=True)
    return wins[:8]


def _build_downturn_assessment(stage4: Dict[str, Any]) -> Dict[str, Any]:
    campaign_status_matrix = stage4.get("campaign_status_matrix", {})
    narrative_summary = stage4.get("stage3", {}).get("narrative_summary_lite", {})
    findings: List[Dict[str, Any]] = []

    blocked_text = " ".join(
        task.lower()
        for category in campaign_status_matrix.get("categories", [])
        for task in category.get("blocked", []) + category.get("waiting_on_client", [])
    )
    unresolved_text = " ".join(item.lower() for item in narrative_summary.get("unresolved_topics", []))

    for source_ref, line in _iter_loaded_lines(stage4):
        lowered = line.lower()
        if not any(token in lowered for token in ["down", "declin", "drop", "flat", "stagn"]):
            continue
        support_level = "unsupported"
        likely_cause = "No supported causal explanation found in current execution or narrative sources."
        if any(token in blocked_text for token in ["approval", "tracking", "launch", "client"]):
            support_level = "partially_supported"
            likely_cause = "Negative movement may be tied to blocked, approval dependent, or delayed execution work."
        elif any(token in unresolved_text for token in ["approval", "delay", "timing", "legal"]):
            support_level = "partially_supported"
            likely_cause = "Recent unresolved issues may be contributing, but evidence is still incomplete."
        findings.append(
            {
                "issue": line,
                "metric": line,
                "observed_change": line,
                "likely_cause": likely_cause,
                "evidence_refs": [{"source_ref": source_ref, "observation": line}],
                "confidence": "medium" if support_level == "partially_supported" else "low",
                "support_level": support_level,
                "needs_human_input": support_level != "supported",
            }
        )
    return {"findings": findings}


def _build_ambiguity_list(stage4: Dict[str, Any], downturns: Dict[str, Any]) -> Dict[str, Any]:
    stage3 = stage4.get("stage3", {})
    campaign_status_matrix = stage4.get("campaign_status_matrix", {})
    items: List[Dict[str, Any]] = list(stage3.get("ambiguity_candidates", []))

    for category in campaign_status_matrix.get("categories", []):
        if category.get("waiting_on_client"):
            items.append(
                {
                    "topic": f"Pending approval in {category.get('category', 'workstream')}",
                    "why_unclear": "Client dependent or approval dependent work is still open.",
                    "missing_source": "Confirmed approval status or due date",
                    "risk_if_assumed": "The agenda may overpromise delivery timing.",
                    "recommended_input": "Confirm approval owner, status, and expected timing.",
                    "highlight_priority": "high",
                }
            )

    for finding in downturns.get("findings", []):
        if finding.get("needs_human_input"):
            items.append(
                {
                    "topic": finding.get("metric", "Downturn explanation"),
                    "why_unclear": finding.get("likely_cause", "Cause is not yet supported."),
                    "missing_source": "Stronger causal evidence or manual context",
                    "risk_if_assumed": "Weak performance could be explained incorrectly.",
                    "recommended_input": "Validate whether there is a known explanation worth stating.",
                    "highlight_priority": "high" if finding.get("support_level") == "unsupported" else "medium",
                }
            )

    deduped: List[Dict[str, Any]] = []
    seen = set()
    for item in items:
        key = (item.get("topic"), item.get("why_unclear"))
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return {"items": deduped}


def run_stage5_v2(
    call_run,
    client_id: str,
    *,
    registry_path: Optional[str] = None,
    manifest=None,
    p0_steering: Optional[list[str]] = None,
) -> Dict[str, Any]:
    stage4 = run_stage4_v2(
        call_run,
        client_id,
        registry_path=registry_path,
        manifest=manifest,
        p0_steering=p0_steering,
    )

    if stage4.get("paused_for_human_input"):
        return {
            "stage4": stage4,
            "paused_for_human_input": True,
            "win_ranked_list": {"wins": []},
            "downturn_assessment_lite": {"findings": []},
            "ambiguity_list": {"items": stage4.get("stage3", {}).get("ambiguity_candidates", [])},
        }

    win_ranked_list = {"wins": _build_win_candidates(stage4)}
    allowed, reason = transition_call_state_v2(call_run, Build1StateV2.WINS_RANKED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, "wins_ranked", "Stage 5 ranked performance, execution, and strategic wins")

    downturn_assessment_lite = _build_downturn_assessment(stage4)
    allowed, reason = transition_call_state_v2(call_run, Build1StateV2.DOWNTURNS_EXPLAINED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, "downturns_explained", "Stage 5 assessed negative or flat signals")

    ambiguity_list = _build_ambiguity_list(stage4, downturn_assessment_lite)
    allowed, reason = transition_call_state_v2(call_run, Build1StateV2.AMBIGUITIES_FLAGGED.value)
    if not allowed:
        raise ValueError(reason)
    if manifest is not None:
        append_snapshot_event(manifest, "ambiguities_flagged", "Stage 5 flagged unresolved ambiguity and input required items")

    return {
        "stage4": stage4,
        "paused_for_human_input": False,
        "win_ranked_list": win_ranked_list,
        "downturn_assessment_lite": downturn_assessment_lite,
        "ambiguity_list": ambiguity_list,
    }
