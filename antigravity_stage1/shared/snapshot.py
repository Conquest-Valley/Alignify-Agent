from __future__ import annotations

from .contracts_runtime import (
    RunSnapshotManifest,
    SnapshotEvent,
    SnapshotTimestamp,
    SnapshotWindow,
    utc_now_iso,
)


def open_run_snapshot(call_run_id: str, client_id: str, agenda_version: str = "v1", validation_version: str = "v1") -> RunSnapshotManifest:
    manifest = RunSnapshotManifest(
        call_run_id=call_run_id,
        client_id=client_id,
        agenda_version=agenda_version,
        validation_version=validation_version,
    )
    manifest.snapshot_events.append(
        SnapshotEvent(
            event_type="run_initialized",
            event_at=utc_now_iso(),
            details="Snapshot opened",
        )
    )
    return manifest


def append_snapshot_event(manifest: RunSnapshotManifest, event_type: str, details: str) -> None:
    manifest.snapshot_events.append(
        SnapshotEvent(event_type=event_type, event_at=utc_now_iso(), details=details)
    )


def register_source(manifest: RunSnapshotManifest, source_ref: str) -> None:
    if source_ref not in manifest.retrieved_source_refs:
        manifest.retrieved_source_refs.append(source_ref)
    manifest.retrieval_timestamps.append(SnapshotTimestamp(source_ref=source_ref, retrieved_at=utc_now_iso()))
    append_snapshot_event(manifest, "source_registered", f"Registered source: {source_ref}")


def register_reporting_window(manifest: RunSnapshotManifest, source_ref: str, window_label: str) -> None:
    manifest.reporting_windows.append(SnapshotWindow(source_ref=source_ref, window_label=window_label))
    append_snapshot_event(manifest, "reporting_window_registered", f"{source_ref} -> {window_label}")
