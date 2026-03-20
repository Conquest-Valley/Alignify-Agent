from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from antigravity_stage1.shared.contracts_runtime import Build1State, create_call_run
from antigravity_stage1.shared.snapshot import open_run_snapshot
from antigravity_stage2.shared.workspace_loader import load_client_workspace
from antigravity_stage2.shared.memory_loader import load_client_memory
from antigravity_stage2.shared.template_resolver import resolve_template_ref
from antigravity_stage2.shared.context_loader import build_context_bundle


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
    template = resolve_template_ref(workspace, manifest=snapshot)
    context = build_context_bundle(
        call_run,
        workspace,
        manifest=snapshot,
        p0_steering=['Lead with launch progress and tracking cleanup.'],
    )

    assert workspace['client_id'] == 'sample_client'
    assert memory['client_name'] == 'Sample Client Co'
    assert 'Alignment Notes Template' in template['template_content']
    assert context['p0_steering'][0].startswith('Lead with launch progress')
    assert len(context['foundational_strategy']) >= 2
    assert len(context['active_strategy']) == 1
    assert len(context['narrative_memory']) >= 2
    assert len(context['live_execution_truth']) >= 3
    assert len(context['producer_notes']) == 1
    assert len(context['provenance_map']) == 10
    assert len(snapshot.retrieved_source_refs) == 12
    assert len(snapshot.reporting_windows) == 2
    assert snapshot.quarterly_strategy_ref_used == workspace['quarterly_strategy_ref']
    assert snapshot.template_ref_used == workspace['template_ref']
    assert call_run.current_state == Build1State.CONTEXT_LOADED.value
    print('Stage 2 smoke test passed.')


if __name__ == '__main__':
    main()
