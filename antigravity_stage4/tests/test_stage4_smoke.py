from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from antigravity_stage1.shared.contracts_runtime import Build1State, create_call_run
from antigravity_stage1.shared.snapshot import open_run_snapshot
from antigravity_stage2.shared.context_loader import build_context_bundle
from antigravity_stage2.shared.memory_loader import load_client_memory
from antigravity_stage2.shared.workspace_loader import load_client_workspace
from antigravity_stage3.shared.stage3_runner import run_stage3
from antigravity_stage4.shared.stage4_runner import run_stage4


def main() -> None:
    call_run = create_call_run(
        client_id='sample_client',
        dp_id='dp_001',
        scheduled_at='2026-03-20T15:00:00+00:00',
        p0_instruction='Lead with launch progress.',
    )
    snapshot = open_run_snapshot(call_run.call_run_id, call_run.client_id)
    workspace = load_client_workspace('sample_client')
    memory = load_client_memory(workspace, manifest=snapshot)
    context = build_context_bundle(
        call_run,
        workspace,
        manifest=snapshot,
        p0_steering=['Lead with launch progress and tracking cleanup.'],
    )
    stage3 = run_stage3(call_run, context, memory, manifest=snapshot)
    stage4 = run_stage4(
        call_run,
        context,
        stage3['strategy_summary'],
        stage3['narrative_summary_lite'],
        manifest=snapshot,
    )

    matrix = stage4['campaign_status_matrix']
    commitments = stage4['commitment_audit_lite']
    categories = {item['category']: item for item in matrix['categories']}

    assert 'Analytics / Tracking' in categories
    assert 'SEO / Copy' in categories
    assert 'Web Development' in categories
    assert any('call tracking audit' in item.lower() for item in categories['Analytics / Tracking']['completed_since_last_call'])
    assert any('service area page rollout' in item.lower() for item in categories['SEO / Copy']['in_progress'])
    assert any('review widget deployment' in item.lower() for item in categories['Web Development']['blocked'])
    assert any('review widget deployment' in item.lower() for item in categories['Web Development']['waiting_on_client'])
    assert categories['SEO / Copy']['quarterly_alignment_score'] >= 60
    assert commitments['commitments']
    statuses = {item['status'] for item in commitments['commitments']}
    assert 'active' in statuses or 'completed' in statuses
    assert call_run.current_state == Build1State.COMMITMENTS_RECONCILED.value
    assert any(event.event_type == 'campaign_status_built' for event in snapshot.snapshot_events)
    assert any(event.event_type == 'commitments_reconciled' for event in snapshot.snapshot_events)
    print('Stage 4 smoke test passed.')


if __name__ == '__main__':
    main()
