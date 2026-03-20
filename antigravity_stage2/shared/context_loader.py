from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from antigravity_stage1.shared.freshness import assess_source_freshness
from antigravity_stage1.shared.snapshot import append_snapshot_event, register_reporting_window, register_source
from antigravity_stage1.shared.state_machine import transition_call_state
from antigravity_stage1.shared.contracts_runtime import Build1State

from .source_registry import get_source_descriptor, read_descriptor_content


def _load_group(
    source_refs: Iterable[str],
    registry_path: Optional[str],
    manifest,
) -> Tuple[List[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
    contents: List[str] = []
    provenance_entries: List[Dict[str, Any]] = []
    loaded_descriptors: List[Dict[str, Any]] = []

    for idx, source_ref in enumerate(source_refs):
        descriptor = get_source_descriptor(source_ref, registry_path)
        content = read_descriptor_content(descriptor, registry_path)
        contents.append(content)
        provenance_entries.append({'context_key': str(idx), 'source_refs': [source_ref]})
        loaded_descriptors.append(descriptor)

        if manifest is not None:
            register_source(manifest, source_ref)
            if descriptor.get('reporting_window'):
                register_reporting_window(manifest, source_ref, descriptor['reporting_window'])

    return contents, provenance_entries, loaded_descriptors


def _build_freshness_records(descriptors: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for descriptor in descriptors:
        freshness = assess_source_freshness(
            descriptor['ref'],
            descriptor.get('source_class', 'other'),
            version_identified=descriptor.get('version_identified', False),
            matches_active_benchmark_period=descriptor.get('matches_active_benchmark_period', False),
            reporting_window=descriptor.get('reporting_window'),
            run_bounded=descriptor.get('run_bounded', False),
            current_run_fetch=descriptor.get('current_run_fetch', False),
        )
        records.append(freshness.to_dict())
    return records


def fetch_foundational_docs(workspace_bundle: Dict[str, Any], registry_path: Optional[str] = None, manifest=None):
    refs = list(workspace_bundle['strategy_doc_refs']) + list(workspace_bundle['overview_doc_refs'])
    return _load_group(refs, registry_path, manifest)


def fetch_active_strategy_docs(workspace_bundle: Dict[str, Any], registry_path: Optional[str] = None, manifest=None):
    return _load_group([workspace_bundle['quarterly_strategy_ref']], registry_path, manifest)


def fetch_narrative_sources(workspace_bundle: Dict[str, Any], registry_path: Optional[str] = None, manifest=None):
    refs = list(workspace_bundle['prior_report_refs']) + list(workspace_bundle['prior_call_note_refs'])
    return _load_group(refs, registry_path, manifest)


def fetch_live_execution_sources(workspace_bundle: Dict[str, Any], registry_path: Optional[str] = None, manifest=None):
    refs = list(workspace_bundle['basecamp_refs']) + list(workspace_bundle['reporting_refs'])
    return _load_group(refs, registry_path, manifest)


def fetch_active_producer_notes(workspace_bundle: Dict[str, Any], registry_path: Optional[str] = None, manifest=None):
    return _load_group(workspace_bundle['producer_note_refs'], registry_path, manifest)


def _namespace_provenance(group_name: str, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    namespaced: List[Dict[str, Any]] = []
    for entry in entries:
        namespaced.append({
            'context_key': f"{group_name}[{entry['context_key']}]",
            'source_refs': entry['source_refs'],
        })
    return namespaced


def record_loaded_sources_in_snapshot(manifest, loaded_descriptors: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    descriptors = list(loaded_descriptors)
    freshness_records = _build_freshness_records(descriptors)
    if manifest is not None:
        append_snapshot_event(
            manifest,
            'context_load_completed',
            f'Registered {len(descriptors)} source descriptors for context loading',
        )
    return freshness_records


def build_context_bundle(
    call_run,
    workspace_bundle: Dict[str, Any],
    *,
    registry_path: Optional[str] = None,
    manifest=None,
    p0_steering: Optional[List[str]] = None,
) -> Dict[str, Any]:
    foundational_texts, foundational_prov, foundational_desc = fetch_foundational_docs(workspace_bundle, registry_path, manifest)
    active_texts, active_prov, active_desc = fetch_active_strategy_docs(workspace_bundle, registry_path, manifest)
    narrative_texts, narrative_prov, narrative_desc = fetch_narrative_sources(workspace_bundle, registry_path, manifest)
    live_texts, live_prov, live_desc = fetch_live_execution_sources(workspace_bundle, registry_path, manifest)
    producer_texts, producer_prov, producer_desc = fetch_active_producer_notes(workspace_bundle, registry_path, manifest)

    all_descriptors = foundational_desc + active_desc + narrative_desc + live_desc + producer_desc
    freshness_records = _build_freshness_records(all_descriptors)

    if manifest is not None:
        append_snapshot_event(manifest, 'context_bundle_built', f'Built context bundle for {workspace_bundle["client_id"]}')
        if workspace_bundle.get('quarterly_strategy_ref'):
            manifest.quarterly_strategy_ref_used = workspace_bundle['quarterly_strategy_ref']
        if workspace_bundle.get('template_ref'):
            manifest.template_ref_used = workspace_bundle['template_ref']
        prior_call_refs = workspace_bundle.get('prior_call_note_refs', [])
        if prior_call_refs:
            manifest.prior_call_date_used = 'latest_available_prior_call_note'

    context_bundle = {
        'p0_steering': list(p0_steering or []),
        'foundational_strategy': foundational_texts,
        'active_strategy': active_texts,
        'narrative_memory': narrative_texts,
        'live_execution_truth': live_texts,
        'producer_notes': producer_texts,
        'provenance_map': (
            _namespace_provenance('foundational_strategy', foundational_prov)
            + _namespace_provenance('active_strategy', active_prov)
            + _namespace_provenance('narrative_memory', narrative_prov)
            + _namespace_provenance('live_execution_truth', live_prov)
            + _namespace_provenance('producer_notes', producer_prov)
        ),
        'freshness_assessments': freshness_records,
    }

    allowed, reason = transition_call_state(call_run, Build1State.CONTEXT_LOADED.value)
    if not allowed:
        raise ValueError(reason)

    return context_bundle
