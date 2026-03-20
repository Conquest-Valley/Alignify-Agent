from __future__ import annotations

from typing import Any, Dict, Optional

from .source_registry import get_client_record


REQUIRED_WORKSPACE_KEYS = {
    'client_id',
    'client_name',
    'strategy_doc_refs',
    'quarterly_strategy_ref',
    'overview_doc_refs',
    'prior_report_refs',
    'prior_call_note_refs',
    'basecamp_refs',
    'reporting_refs',
    'producer_note_refs',
    'template_ref',
    'memory_ref',
}


def load_client_workspace(client_id: str, registry_path: Optional[str] = None) -> Dict[str, Any]:
    record = get_client_record(client_id, registry_path)
    missing = REQUIRED_WORKSPACE_KEYS - set(record.keys())
    if missing:
        raise ValueError(f'Workspace record missing keys: {sorted(missing)}')
    return {
        'client_id': record['client_id'],
        'client_name': record['client_name'],
        'strategy_doc_refs': list(record['strategy_doc_refs']),
        'quarterly_strategy_ref': record['quarterly_strategy_ref'],
        'overview_doc_refs': list(record['overview_doc_refs']),
        'prior_report_refs': list(record['prior_report_refs']),
        'prior_call_note_refs': list(record['prior_call_note_refs']),
        'basecamp_refs': list(record['basecamp_refs']),
        'reporting_refs': list(record['reporting_refs']),
        'producer_note_refs': list(record['producer_note_refs']),
        'template_ref': record['template_ref'],
        'memory_ref': record['memory_ref'],
    }
