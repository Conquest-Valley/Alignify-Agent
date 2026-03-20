# Antigravity Stage 5

Stage 5 is the value detection and risk interpretation layer for Build 1.

It consumes outputs from:
- antigravity_stage1
- antigravity_stage2
- antigravity_stage3
- antigravity_stage4

It produces:
- WinRankedList
- DownturnAssessmentLite
- AmbiguityList

Core functions:
- extract_performance_win_candidates
- extract_execution_win_candidates
- extract_strategic_win_candidates
- rank_win_candidates
- detect_negative_or_flat_signals
- generate_downturn_candidates
- classify_downturn_support
- build_ambiguity_list
- run_stage5
