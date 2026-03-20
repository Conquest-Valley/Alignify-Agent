from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from antigravity_stage1.shared.contracts_runtime import Build1State, create_call_run
from antigravity_stage1.shared.snapshot import open_run_snapshot
from antigravity_stage2.shared.memory_loader import load_client_memory
from antigravity_stage2.shared.workspace_loader import load_client_workspace
from antigravity_stage2.shared.context_loader import build_context_bundle
try:
    from antigravity_stage3.shared.stage3_runner import run_stage3
except ImportError:  # pragma: no cover
    from antigravity_stage3_clean.shared.stage3_runner import run_stage3

try:
    from antigravity_stage4.shared.stage4_runner import run_stage4
except ImportError:  # pragma: no cover
    from antigravity_stage4_clean.shared.stage4_runner import run_stage4
from antigravity_stage1.shared.state_machine import transition_call_state
from antigravity_stage6.shared.stage6_runner import run_stage6


def _sample_win_ranked_list():
    return {
        'wins': [
            {
                'win_id': 'win_exec_001',
                'type': 'execution',
                'category': 'SEO / Copy',
                'headline': 'Service area page rollout moved into active launch for Dallas and Fort Worth.',
                'description': 'The revised page set is now in active rollout and maps directly to the quarter launch goal.',
                'strategic_goal_alignment': 'launch revised service area pages',
                'client_relevance_score': 92,
                'freshness_window': 'current',
                'evidence_refs': [
                    {
                        'source_type': 'Basecamp',
                        'source_ref': 'src_sample_basecamp',
                        'source_timestamp_or_window': 'current',
                        'observation': 'service area page rollout for Dallas and Fort Worth',
                        'confidence': 'high',
                    }
                ],
                'confidence': 'high',
            },
            {
                'win_id': 'win_perf_001',
                'type': 'performance',
                'category': 'Analytics / Tracking',
                'headline': 'Qualified form submissions improved from service intent pages.',
                'description': 'GA4 indicates a month over month improvement in qualified submissions after launch and tracking cleanup.',
                'strategic_goal_alignment': 'increase qualified leads from local service pages',
                'client_relevance_score': 88,
                'freshness_window': '2026-02-01 to 2026-02-29',
                'evidence_refs': [
                    {
                        'source_type': 'GA4',
                        'source_ref': 'src_sample_ga4',
                        'source_timestamp_or_window': '2026-02-01 to 2026-02-29',
                        'observation': 'Qualified form submissions up 12 percent from service intent pages.',
                        'confidence': 'high',
                    }
                ],
                'confidence': 'high',
            },
        ]
    }


def _sample_downturn_assessment():
    return {
        'findings': [
            {
                'issue': 'Traffic remained soft in non priority areas.',
                'metric': 'sessions',
                'observed_change': 'flat to down slightly',
                'candidate_cause': 'targeting shifted toward higher intent service pages instead of broad traffic growth',
                'support_level': 'partial',
                'evidence_refs': [
                    {
                        'source_type': 'GA4',
                        'source_ref': 'src_sample_ga4',
                        'source_timestamp_or_window': '2026-02-01 to 2026-02-29',
                        'observation': 'Calls from organic landing pages up 9 percent month over month.',
                        'confidence': 'medium',
                    }
                ],
                'confidence': 'medium',
                'needs_human_input': False,
            }
        ]
    }


def _sample_ambiguity_list():
    return {
        'items': [
            {
                'topic': 'Review widget launch timing',
                'why_unclear': 'Legal approval is still open in Basecamp and producer notes caution against overpromising timing.',
                'missing_source': 'explicit client approval confirmation',
                'risk_if_assumed': 'Could overstate launch readiness on the call.',
                'recommended_input': 'Confirm the latest client legal review status before stating a launch date.',
                'highlight_priority': 'high',
            }
        ]
    }


def main() -> None:
    call_run = create_call_run(
        client_id='sample_client',
        dp_id='dp_001',
        scheduled_at='2026-03-20T15:00:00+00:00',
        p0_instruction='Lead with launch progress and clear approvals needed.',
    )
    snapshot = open_run_snapshot(call_run.call_run_id, call_run.client_id)
    workspace = load_client_workspace('sample_client')
    memory = load_client_memory(workspace, manifest=snapshot)
    context = build_context_bundle(
        call_run,
        workspace,
        manifest=snapshot,
        p0_steering=['Lead with launch progress and clear approvals needed.'],
    )
    stage3 = run_stage3(call_run, context, memory, manifest=snapshot)
    stage4 = run_stage4(
        call_run,
        context,
        stage3['strategy_summary'],
        stage3['narrative_summary_lite'],
        manifest=snapshot,
    )
    ok, reason = transition_call_state(call_run, Build1State.WINS_RANKED.value)
    assert ok, reason
    ok, reason = transition_call_state(call_run, Build1State.DOWNTURNS_EXPLAINED.value)
    assert ok, reason
    ok, reason = transition_call_state(call_run, Build1State.AMBIGUITIES_FLAGGED.value)
    assert ok, reason

    stage6 = run_stage6(
        call_run,
        workspace,
        stage3['strategy_summary'],
        stage4['campaign_status_matrix'],
        stage4['commitment_audit_lite'],
        _sample_win_ranked_list(),
        _sample_downturn_assessment(),
        _sample_ambiguity_list(),
        manifest=snapshot,
    )

    agenda_draft = stage6['agenda_draft']
    section_names = [section['section_name'] for section in agenda_draft['content_sections']]
    assert 'Meeting Summary / Recommended talk track' in section_names
    assert 'Pending Approvals' in section_names
    assert 'Analytics / Tracking' in section_names
    assert 'Workstream sections by campaign category' in section_names
    assert 'Wins / Highlights' in section_names
    assert 'Input Required' in section_names
    assert agenda_draft['rendered_location'] == workspace['template_ref']
    assert call_run.current_state == Build1State.AGENDA_RENDERED.value
    assert 'Review widget launch timing' in stage6['agenda_preview']
    assert any(event.event_type == 'agenda_rendered' for event in snapshot.snapshot_events)
    print('Stage 6 smoke test passed.')


if __name__ == '__main__':
    main()
