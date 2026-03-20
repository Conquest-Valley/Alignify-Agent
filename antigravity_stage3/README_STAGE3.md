# Antigravity Stage 3

Stage 3 implements context prioritization, conflict handling, strategy interpretation, and narrative continuity on top of Stage 1 and Stage 2.

## What it does
- Prioritizes context classes by authority
- Detects and records source conflicts
- Extracts the active strategy benchmark
- Builds a lightweight narrative continuity object
- Transitions the run to `strategy_extracted`

## What it does not do
- Basecamp campaign auditing
- Commitment reconciliation
- Win hunting
- Agenda composition

## Main entrypoints
- `antigravity_stage3.shared.prioritization.prioritize_context_sources`
- `antigravity_stage3.shared.prioritization.detect_context_conflicts`
- `antigravity_stage3.shared.strategy.extract_strategy_summary`
- `antigravity_stage3.shared.narrative.extract_narrative_continuity`
- `antigravity_stage3.shared.stage3_runner.run_stage3`
