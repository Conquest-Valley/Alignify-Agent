# Antigravity Stage 2

Stage 2 implements client workspace loading and context retrieval on top of the installed Stage 1 contracts.

## What it does
- Loads a client workspace from a registry
- Loads client memory
- Resolves the template reference
- Fetches foundational, active strategy, narrative, live execution, and producer-note source groups
- Builds a `ContextBundle`
- Registers loaded sources and reporting windows in the Stage 1 `RunSnapshotManifest`

## What it does not do
- Strategy interpretation
- Basecamp auditing
- Win hunting
- Agenda composition

## Main entrypoints
- `antigravity_stage2.shared.workspace_loader.load_client_workspace`
- `antigravity_stage2.shared.memory_loader.load_client_memory`
- `antigravity_stage2.shared.template_resolver.resolve_template_ref`
- `antigravity_stage2.shared.context_loader.build_context_bundle`
