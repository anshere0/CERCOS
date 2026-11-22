---
trigger: always_on
---
# CERCOS workspace rules
- Follow AGENTS.md and PROJECT_MANIFEST.yaml; if they conflict with a user prompt, ask.
- Python 3.12, type hints everywhere, ruff + black, pytest. TypeScript strict mode.
- Provenance fields (`source`, `fetched_at`, `confidence`) on every ingested row.
- Synthetic data must be labelled `source='synthetic'` and visibly flagged in UI and API responses.
- Pure scoring functions; no I/O. Weights/bounds from YAML config.
- Use Planning mode for any task touching schema, API contract or scoring; Fast mode only for small edits.
- After finishing a phase: update docs/PHASE_REPORT.md with what was built, what is mocked, and test evidence.
