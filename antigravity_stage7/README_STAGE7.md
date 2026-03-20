# Antigravity Stage 7

Stage 7 is the final Build 1 gate layer.

It validates evidence coverage and section readiness for the pre call agenda,
finalizes the run snapshot, captures optional manual overrides, and moves the
run into `awaiting_dp_pre_call_review`.

## Core functions
- `validate_claim_evidence()`
- `validate_claim_freshness()`
- `validate_section_readiness()`
- `downgrade_or_remove_unsupported_claims()`
- `finalize_run_snapshot()`
- `capture_manual_override()`
- `mark_awaiting_dp_review()`
- `run_stage7()`
