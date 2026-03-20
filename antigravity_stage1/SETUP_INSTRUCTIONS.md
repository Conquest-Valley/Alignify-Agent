# Click by click setup instructions for Stage 1

These steps assume you are putting Stage 1 into an Antigravity project folder on your machine.

## Part 1. Get the files into your project
1. Download the Stage 1 zip.
2. Unzip it.
3. Open the unzipped folder.
4. Copy the folder named `antigravity_stage1`.
5. Open your Antigravity project folder.
6. Paste `antigravity_stage1` into your project.

After pasting, you should see these folders inside `antigravity_stage1`:
- schemas
- validation
- run_state
- artifacts
- prompts
- shared
- tests

## Part 2. Open the project in your code editor
1. Open VS Code.
2. Click `File`.
3. Click `Open Folder`.
4. Pick your Antigravity project folder.
5. In the left sidebar, click the `antigravity_stage1` folder.

## Part 3. Create the Python environment
1. In VS Code, click `Terminal`.
2. Click `New Terminal`.
3. In the terminal, type this exactly and press Enter:

   python3 -m venv .venv

4. Activate it.

   On Mac or Linux:

   source .venv/bin/activate

   On Windows PowerShell:

   .venv\Scripts\Activate.ps1

5. Install the package requirements:

   pip install -r antigravity_stage1/requirements.txt

## Part 4. Run the smoke test
1. In the same terminal, run:

   python antigravity_stage1/tests/test_stage1_smoke.py

2. If everything is correct, you should see:

   Stage 1 smoke test passed.

## Part 5. What to do if the smoke test fails
1. Make sure your terminal is in the project root folder.
2. Make sure the virtual environment is activated.
3. Make sure you installed requirements.
4. Run the test again.

## Part 6. How to use Stage 1 in later stages
Later stage files should import from `antigravity_stage1/shared` instead of rewriting rules.

Examples:

   from antigravity_stage1.shared.contracts_runtime import create_call_run
   from antigravity_stage1.shared.state_machine import transition_call_state
   from antigravity_stage1.shared.evidence import create_evidence_ref
   from antigravity_stage1.shared.freshness import assess_source_freshness
   from antigravity_stage1.shared.taxonomy import normalize_category_alias
   from antigravity_stage1.shared.validation import validate_section_requirements
   from antigravity_stage1.shared.snapshot import open_run_snapshot, register_source

## Part 7. What gets built next
After Stage 1 is working, Stage 2 should plug into these contracts for:
- client workspace loading
- context retrieval
- snapshot source registration
- provenance tracking
