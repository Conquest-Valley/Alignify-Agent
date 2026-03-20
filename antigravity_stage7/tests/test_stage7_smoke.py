from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from antigravity_stage1.shared.contracts_runtime import Build1State, create_call_run
from antigravity_stage1.shared.snapshot import open_run_snapshot
from antigravity_stage1.shared.state_machine import transition_call_state
from antigravity_stage7.shared.stage7_runner import run_stage7


def _sample_agenda_draft(call_run_id: str):
    return {
        'type': 'pre_call_agenda',
        'call_run_id': call_run_id,
        'content_sections': [
            {
                'section_name': 'Meeting Summary',
                'content': 'Strategy focus remains lead quality and service page rollout.',
                'evidence_refs': [
                    {
                        'source_type': 'StrategyDoc',
                        'source_ref': 'src_quarterly_strategy_q1',
                        'source_timestamp_or_window': 'Q1 2026',
                        'observation': 'Quarter priority is service page rollout and lead quality.',
                        'confidence': 'high',
                    },
                    {
                        'source_type': 'Basecamp',
                        'source_ref': 'src_basecamp_board',
                        'source_timestamp_or_window': 'current',
                        'observation': 'Service page rollout is active in Basecamp.',
                        'confidence': 'high',
                    },
                ],
                'confidence': 'high',
            },
            {
                'section_name': 'Pending Approvals',
                'content': 'Awaiting legal signoff on the review widget launch.',
                'evidence_refs': [
                    {
                        'source_type': 'Basecamp',
                        'source_ref': 'src_basecamp_board',
                        'source_timestamp_or_window': 'current',
                        'observation': 'Legal signoff is still pending.',
                        'confidence': 'medium',
                    }
                ],
                'confidence': 'medium',
            },
            {
                'section_name': 'Wins / Highlights',
                'content': 'Qualified submissions improved from service intent pages.',
                'evidence_refs': [
                    {
                        'source_type': 'GA4',
                        'source_ref': 'src_ga4_reporting',
                        'source_timestamp_or_window': '2026-02-01 to 2026-02-29',
                        'observation': 'Qualified submissions up 12 percent.',
                        'confidence': 'high',
                    }
                ],
                'confidence': 'high',
            },
            {
                'section_name': 'Input Required',
                'content': 'Confirm the exact client launch date for the review widget.',
                'evidence_refs': [],
                'confidence': 'low',
            },
        ],
        'evidence_refs': [],
        'confidence': 'medium',
        'approved': False,
        'rendered_location': 'gdoc://template/sample-client-call-notes',
        'validation_status': 'pending',
    }


def main() -> None:
    call_run = create_call_run(
        client_id='sample_client',
        dp_id='dp_001',
        scheduled_at='2026-03-20T15:00:00+00:00',
        p0_instruction='Lead with value proof and approvals needed.',
    )
    snapshot = open_run_snapshot(call_run.call_run_id, call_run.client_id)

    transitions = [
        Build1State.CONTEXT_LOADED.value,
        Build1State.STRATEGY_EXTRACTED.value,
        Build1State.CAMPAIGN_STATUS_BUILT.value,
        Build1State.COMMITMENTS_RECONCILED.value,
        Build1State.WINS_RANKED.value,
        Build1State.DOWNTURNS_EXPLAINED.value,
        Build1State.AMBIGUITIES_FLAGGED.value,
        Build1State.AGENDA_RENDERED.value,
    ]
    for next_state in transitions:
        ok, reason = transition_call_state(call_run, next_state)
        assert ok, reason

    agenda_draft = _sample_agenda_draft(call_run.call_run_id)
    section_context = {
        'Meeting Summary': {
            'must_include_strategy_anchor': True,
            'must_include_current_truth_anchor': True,
        },
        'Pending Approvals': {
            'must_have_evidence': True,
        },
        'Wins / Highlights': {
            'must_have_evidence': True,
            'must_have_strategic_relevance': True,
        },
        'Input Required': {
            'must_exist_when_unresolved_low_confidence_conflict_present': True,
        },
    }
    freshness_by_source = {
        'src_quarterly_strategy_q1': {
            'freshness_status': 'fresh',
        },
        'src_basecamp_board': {
            'freshness_status': 'fresh',
        },
        'src_ga4_reporting': {
            'freshness_status': 'fresh',
        },
    }
    manual_edits = [
        {
            'section': 'Meeting Summary',
            'original_text': 'Strategy focus remains lead quality and service page rollout.',
            'edited_text': 'Lead with lead quality improvement, then approvals needed.',
            'reason_code': 'dp_tone_adjustment',
        }
    ]

    result = run_stage7(
        call_run,
        agenda_draft,
        manifest=snapshot,
        section_context=section_context,
        freshness_by_source=freshness_by_source,
        manual_edits=manual_edits,
        strategy_ref='src_quarterly_strategy_q1',
        template_ref='gdoc://template/sample-client-call-notes',
        validation_version='v1',
    )

    assert result['validation_report']['overall_valid'] is True
    assert result['review_state'] == Build1State.AWAITING_DP_PRE_CALL_REVIEW.value
    assert call_run.current_state == Build1State.AWAITING_DP_PRE_CALL_REVIEW.value
    assert result['manual_override_log']['overrides'][0]['reason_code'] == 'dp_tone_adjustment'
    assert snapshot.template_ref_used == 'gdoc://template/sample-client-call-notes'
    assert snapshot.quarterly_strategy_ref_used == 'src_quarterly_strategy_q1'
    assert any(event.event_type == 'snapshot_finalized' for event in snapshot.snapshot_events)
    assert any(event.event_type == 'awaiting_dp_pre_call_review' for event in snapshot.snapshot_events)
    print('Stage 7 smoke test passed.')


if __name__ == '__main__':
    main()
