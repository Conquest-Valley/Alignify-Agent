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

    strategy = stage3['strategy_summary']
    narrative = stage3['narrative_summary_lite']
    conflicts = stage3['context_conflict_resolution']['conflicts']

    assert strategy['active_benchmark_period'] == 'Q1 2026'
    assert 'launch revised service area pages' in strategy['current_quarter_priorities'][0].lower()
    assert any(item['workstream'] == 'Analytics / Tracking' for item in strategy['workstream_goal_map'])
    assert any('lead quality' in signal.lower() or 'qualified leads' in signal.lower() for signal in strategy['client_value_signals'])
    assert narrative['prior_promises']
    assert any('approval' in topic.lower() for topic in narrative['unresolved_topics'])
    assert any('launch progress' in theme.lower() for theme in narrative['recurring_themes'])
    assert isinstance(conflicts, list)
    assert call_run.current_state == Build1State.STRATEGY_EXTRACTED.value
    assert any(event.event_type == 'strategy_summary_extracted' for event in snapshot.snapshot_events)
    print('Stage 3 smoke test passed.')


if __name__ == '__main__':
    main()
