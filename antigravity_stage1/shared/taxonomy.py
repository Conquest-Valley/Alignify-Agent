from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "validation" / "taxonomy.json"
TAXONOMY = json.loads(TAXONOMY_PATH.read_text())
_alias_lookup: Dict[str, str] = {
    item["alias"].strip().lower(): item["canonical_category"]
    for item in TAXONOMY["default_aliases"]
}
_canonical_lookup: Dict[str, str] = {
    item.strip().lower(): item
    for item in TAXONOMY["canonical_categories"]
}


def normalize_category_alias(raw_label: str) -> Optional[str]:
    if not raw_label:
        return None
    cleaned = raw_label.strip().lower()
    if cleaned in _canonical_lookup:
        return _canonical_lookup[cleaned]
    return _alias_lookup.get(cleaned)
