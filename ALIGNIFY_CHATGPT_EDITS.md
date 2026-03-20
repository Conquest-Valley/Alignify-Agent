# ALIGNIFY_CHATGPT_EDITS

## Purpose

This file is a working landing zone for ChatGPT proposed repo edits when direct multi file surgery is either premature or connector constrained.

The immediate goal is to stabilize the current Alignify Agent shape before deeper V2 implementation work lands.

## Snapshot

- Repository: `Conquest-Valley/Alignify-Agent`
- Baseline branch: `main`
- Observed head during review: `350a45065eb7a53064006ca80a40ad1afa8710a9`

## High level read on current repo shape

The current codebase appears split across multiple operational centers rather than one clearly enforced runtime path.

Key visible anchors:

- `README.md`
- `antigravity_stage3/README_STAGE3.md`
- `antigravity_stage1/shared/contracts_runtime.py`
- `antigravity_stage1/write_stage1.py`
- `live_run_step2_registry_package/integrations/registry_adapter.py`
- `live_run_step2_registry_package/tests/test_registry_bootstrap.py`
- `prompts/dp_profiles/default_dp_notes_profile.md`

That layout strongly suggests integration risk from stage drift, runtime drift, prompt drift, and registry/bootstrap duplication.

## Working diagnosis

Before pushing broader feature work, the repo likely needs a short stabilization pass focused on reducing ambiguity in four areas:

1. **Single runtime path**
   - Choose one canonical execution path for the current product slice.
   - Demote or clearly mark legacy or experimental paths.

2. **Single contract surface**
   - Make one place authoritative for request and response contracts.
   - Remove hidden divergence between prompt assumptions, runtime contracts, and registry adapters.

3. **Single integration boundary**
   - Decide whether the active integration seam lives in the stage folders, the live registry package, or a thin composition layer above them.
   - Avoid parallel orchestration logic.

4. **Single validation path**
   - One smoke test path should prove bootstrap, contract validity, and end to end execution for the current slice.

## Recommended Workstream 0

### 1. Establish a canonical system map

Create a short architecture note that answers:

- What is the current entrypoint?
- What package owns runtime orchestration?
- What package owns registry/bootstrap?
- What package owns contracts and schemas?
- What prompt profile is actually live?

If any answer has two valid candidates, that is the first thing to collapse.

### 2. Freeze or label non canonical paths

Anything not on the primary runtime path should be one of:

- active and canonical
- experimental
- archived
- migration only

Right now the stage based folder structure makes that boundary easy to blur.

### 3. Unify contract ownership

Audit these first:

- `antigravity_stage1/shared/contracts_runtime.py`
- `antigravity_stage1/write_stage1.py`
- `prompts/dp_profiles/default_dp_notes_profile.md`
- any route, handler, or adapter layer that transforms the same payloads again

Target state:

- one canonical input contract
- one canonical internal normalized representation
- one canonical output contract
- explicit adapter transforms only where required

### 4. Unify registry/bootstrap behavior

Audit these first:

- `live_run_step2_registry_package/integrations/registry_adapter.py`
- `live_run_step2_registry_package/tests/test_registry_bootstrap.py`

Target state:

- registry bootstrap is deterministic
- environment requirements are explicit
- test bootstrap matches production bootstrap
- failure modes are surfaced early and with typed errors

### 5. Add one real end to end proof

Minimum acceptable smoke path:

- load config
- bootstrap registry
- load active prompt profile
- execute the primary write or generation path
- validate schema or contract output
- fail loudly on contract mismatch

## Recommended implementation order

### Slice A

Document the canonical runtime path and mark every non canonical path.

### Slice B

Collapse auth, bootstrap, and registry setup into one enforced flow.

### Slice C

Collapse contract normalization and output validation into one path.

### Slice D

Add a single end to end test covering the active flow only.

### Slice E

Remove or quarantine dead paths once the green path is proven.

## Concrete repo tasks

### Task 1: runtime inventory

Produce a file level inventory for:

- stage entrypoints
- live runtime entrypoints
- registry/bootstrap helpers
- prompt selection logic
- contract validation logic

### Task 2: ownership matrix

For each subsystem, assign one owner module:

- entrypoint
- orchestration
- contracts
- prompts
- registry
- validation
- tests

### Task 3: delete or quarantine ambiguity

Where two modules do the same job, choose one and explicitly retire the other.

### Task 4: test the only path that matters

Prefer one truthful end to end test over many shallow tests that each validate a different interpretation of the runtime.

## Completion criteria

Workstream 0 is done when:

- a new contributor can identify the one true runtime path in under five minutes
- bootstrap behavior is the same in local runs and tests
- contracts are defined once and enforced once
- prompt selection is explicit and not accidental
- there is one end to end smoke test for the active product slice
- legacy or experimental paths are clearly labeled and not silently active

## Notes for next ChatGPT pass

The next pass should not start with broad feature work.

It should first:

1. map the actual current entrypoint
2. trace registry/bootstrap from entry to execution
3. trace contract normalization from input to output
4. identify duplicate or stale paths
5. only then patch code

If direct edits are requested later, use this file as the sequencing anchor and update it as decisions become concrete.
