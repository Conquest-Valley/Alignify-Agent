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
from antigravity_stage5.shared.stage5_runner import run_stage5


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
    stage5 = run_stage5(
        call_run,
        context,
        stage3['strategy_summary'],
        stage3['narrative_summary_lite'],
        stage3['context_conflict_resolution'],
        stage4['campaign_status_matrix'],
        stage4['commitment_audit_lite'],
        manifest=snapshot,
    )

    wins = stage5['win_ranked_list']['wins']
    downturns = stage5['downturn_assessment_lite']['findings']
    ambiguities = stage5['ambiguity_list']['items']

    assert wins, 'Stage 5 should surface wins'
    assert any(win['type'] == 'performance' for win in wins)
    assert any(win['type'] == 'execution' for win in wins)
    assert any('qualified form submissions' in win['headline'].lower() or 'calls from organic' in win['headline'].lower() for win in wins)
    assert isinstance(downturns, list)
    assert ambiguities, 'Stage 5 should surface at least one ambiguity from waiting_on_client or unresolved topics'
    assert any('approval' in item['topic'].lower() or 'approval' in item['why_unclear'].lower() for item in ambiguities)
    assert call_run.current_state == Build1State.AMBIGUITIES_FLAGGED.value
    assert any(event.event_type == 'wins_ranked' for event in snapshot.snapshot_events)
    assert any(event.event_type == 'downturns_explained' for event in snapshot.snapshot_events)
    assert any(event.event_type == 'ambiguities_flagged' for event in snapshot.snapshot_events)
    print('Stage 5 smoke test passed.')


if __name__ == '__main__':
    main()
