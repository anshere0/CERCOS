# P2 — Recommendation engine (TDD)
Implement `backend/app/mcdm/`:
- `range.py`: usable energy, reach with 8% reserve, consumption = base Wh/km * factors (speed, load, AC use, gradient optional).
- `criteria.py`: build the decision matrix [detour_km, cost, wait_min, effective_kw, rating, arrival_soc_pct]; effective_kw = min(station, vehicle accept).
- `topsis.py` (vector norm, baseline), `wsm_anchored.py` (fixed bounds from config), `modes.py` (weights.yaml, per-segment override).
- `queue.py`: Erlang-C M/M/c and Allen-Cunneen M/G/c wait estimate; inputs lambda, mean service time, SCV, c.
- `explain.py`: per-criterion contribution so the UI can say "chosen because cheaper by Rs X and 6 min shorter wait".
- `simulator.py`: port research/01 experiment into reusable code (seeded) for regression tests.
Hard filters: connector compatible, operational, reachable. Return top-3 with scores, ETA, cost estimate, arrival SoC, provenance and confidence.
Tests: ideal=1.0, dominated never wins, weights sum to 1, zero rank reversal (4000 random problems) for anchored scoring, Erlang-C reference values, range sanity for 3 vehicles.
Acceptance: `pytest backend/tests/mcdm -q` green; docs/ENGINE.md with formulas.
