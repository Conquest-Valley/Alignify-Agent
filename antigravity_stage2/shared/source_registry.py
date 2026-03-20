from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_PATH = PACKAGE_ROOT / 'data' / 'clients_registry.json'


def load_registry(registry_path: Optional[str] = None) -> Dict[str, Any]:
    path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
    return json.loads(path.read_text())


def get_client_record(client_id: str, registry_path: Optional[str] = None) -> Dict[str, Any]:
    registry = load_registry(registry_path)
    try:
        return registry['clients'][client_id]
    except KeyError as exc:
        raise ValueError(f'Unknown client_id: {client_id}') from exc


def get_source_descriptor(source_ref: str, registry_path: Optional[str] = None) -> Dict[str, Any]:
    registry = load_registry(registry_path)
    try:
        descriptor = registry['sources'][source_ref].copy()
        descriptor['ref'] = source_ref
        return descriptor
    except KeyError as exc:
        raise ValueError(f'Unknown source_ref: {source_ref}') from exc


def iter_source_descriptors(source_refs: Iterable[str], registry_path: Optional[str] = None) -> List[Dict[str, Any]]:
    return [get_source_descriptor(source_ref, registry_path) for source_ref in source_refs]


def read_descriptor_content(descriptor: Dict[str, Any], registry_path: Optional[str] = None) -> str:
    kind = descriptor.get('kind')
    if kind == 'inline':
        return descriptor.get('content', '')
    if kind == 'file':
        location = descriptor.get('location')
        if not location:
            raise ValueError(f"Descriptor {descriptor.get('ref')} is missing location")
        path = PACKAGE_ROOT / location
        return path.read_text()
    if kind == 'external_ref':
        external_ref = descriptor.get('location') or descriptor.get('external_ref') or descriptor.get('ref')
        return f'EXTERNAL_REF::{external_ref}'
    raise ValueError(f"Unsupported source kind: {kind}")
