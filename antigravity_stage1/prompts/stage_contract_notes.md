# Stage 1 Contract Notes

This package is the contract and guardrail layer for Build 1.

Rules:
1. Stage 1 defines schemas, enums, rules, and shared helper functions only.
2. Stage 1 does not fetch live sources.
3. Stage 1 does not perform strategy reasoning.
4. Stage 1 does not compose agenda text.
5. Later stages must import and use these contracts instead of redefining them.

Shared design principles:
- Evidence first
- Never guess
- Weighted context, not blind override
- Typed objects between stages
- Human gate before client facing output
