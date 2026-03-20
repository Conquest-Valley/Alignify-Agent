# Alignment Notes Render Spec

## Purpose
This file defines the hard coded rendering rules for Build 1 pre call agenda generation.

The system must render into the real alignment notes structure, not invent a new format.

## Non negotiable rules
- Facts must come from client sources or live systems, not from style guidance or producer notes.
- Producer notes may influence framing, emphasis, and caution, but cannot create factual claims.
- Unsupported claims must be removed, softened, or moved to Input Required.
- The output must stop at DP review state.
- The system must preserve auditability through source refs and run snapshot data.

## Required section order
1. Header and call metadata
2. Meeting Summary / Recommended talk track
3. Pending Approvals
4. Analytics / Tracking
5. Workstream sections by campaign category
6. Wins / Highlights
7. In Progress
8. In Queue / Next Up
9. Input Required
10. Discussion points and next decisions

## Section intent

### 1. Header and call metadata
Include:
- client name
- DP name if available
- call date
- active quarter label if available

### 2. Meeting Summary / Recommended talk track
Purpose:
- tell the DP what to lead with
- connect current quarter priorities to current truth
- keep it short and useful

Requirements:
- must include at least one strategy anchor
- must include at least one current truth anchor
- must not include unsupported causal claims

### 3. Pending Approvals
Purpose:
- surface anything awaiting client action or signoff

Requirements:
- every approval item must map to Basecamp or a supported source
- if none exist, suppress the section cleanly or include "No pending approvals" depending on DP profile

### 4. Analytics / Tracking
Purpose:
- summarize meaningful movement only

Requirements:
- use explicit time windows when available
- if reporting is missing or weak, state that clearly
- do not over explain weak movement without support

### 5. Workstream sections by campaign category
Purpose:
- show what moved, what is active, what is blocked, and what is next

Rules:
- order sections using DP profile preference if available, otherwise use canonical order
- each workstream section should distinguish completed, in progress, blocked, and waiting on client where relevant
- align commentary to the current quarter when possible

### 6. Wins / Highlights
Purpose:
- surface the client meaningful wins, not vanity items

Requirements:
- every win must have evidence support
- prefer strategic, execution, and performance wins that show forward movement the client will care about
- keep the section concise and lead with the strongest 2 to 4 items

### 7. In Progress
Purpose:
- show meaningful work underway

Requirements:
- focus on items likely to matter on the call
- avoid cluttering with low value task noise

### 8. In Queue / Next Up
Purpose:
- show what is coming next and why it matters

Requirements:
- only include items with reasonable confidence
- if sequencing is unclear, downgrade to Input Required or soften phrasing

### 9. Input Required
Purpose:
- make uncertainty visible instead of hiding it

Requirements:
- must appear whenever unresolved ambiguity, low confidence conflict, or missing source coverage exists
- should be phrased as a concrete need, question, or decision

### 10. Discussion points and next decisions
Purpose:
- help the DP steer the call and capture likely next moves

Requirements:
- should be short and decision oriented
- should connect to current blockers, approvals, or quarter priorities

## Fallback rules
- If there is no strong performance win, emphasize execution movement or resolved blockers.
- If there is no supported downturn explanation, do not speculate. Move the issue to Input Required.
- If a section is irrelevant, suppress it cleanly instead of filling it with weak content.
- If reporting is missing, state the reporting gap rather than pretending certainty.
- If the same point would appear in multiple sections, keep it in the section where it is most actionable.

## Writing rules
- Be direct, clear, and useful.
- Prefer short, evidence grounded bullets or compact prose.
- Avoid generic filler language.
- Do not overstate confidence.
- Preserve the client's actual strategic context and account reality.

## Confidence handling
- High confidence: state normally.
- Medium confidence: use careful phrasing.
- Low confidence: move to Input Required or explicitly frame as unresolved.

## Do not do
- Do not invent KPI explanations.
- Do not treat producer notes as factual proof.
- Do not use cross client examples as evidence.
- Do not skip Input Required when uncertainty exists.
- Do not bypass DP review.
