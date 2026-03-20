from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from .contracts_runtime import Build1State, CallRun, utc_now_iso


RULES_PATH = Path(__file__).resolve().parent.parent / "validation" / "state_transition_rules.json"
_rules: Dict[str, List[str]] = json.loads(RULES_PATH.read_text())["allowed_transitions"]


def is_transition_allowed(current_state: str, proposed_next_state: str) -> bool:
    return proposed_next_state in _rules.get(current_state, [])


def transition_call_state(call_run: CallRun, proposed_next_state: str) -> Tuple[bool, str]:
    if not is_transition_allowed(call_run.current_state, proposed_next_state):
        return False, f"Illegal transition from {call_run.current_state} to {proposed_next_state}"
    call_run.current_state = proposed_next_state
    call_run.updated_at = utc_now_iso()
    return True, "ok"
