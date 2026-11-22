# ATHARVA — Recommendation Engine, Queue Model & Simulation  (8% of the 40%)

**Mission:** deliver a tested, deterministic `recommend()` function that picks the best charging stop for six modes, plus the queue model and the simulation that prove (RQ1, RQ4, RQ5) it works. This is pure Python with no database, so you can start **on day 1** without waiting for anyone.
Your PRs are reviewed by **Yash** (primary) and **Ansh** (secondary). You review **Ansh** (primary) and **Yash** and **Kashish's analysis scripts** (secondary).

## You own
`backend/app/mcdm/` · `backend/app/queue/` · `backend/tests/mcdm/` · `backend/tests/queue/` · `research/` · `config/weights.yaml` · `config/criteria_bounds.yaml` · `docs/ENGINE.md`
You co-sign changes to `contracts/engine_interface.md` with Yash.

## Inputs / Outputs
| You need | From | When |
|---|---|---|
| `contracts/engine_interface.md`, config files | already in the repo | now |
| Census data (kW, tariff, connectors) for realistic inputs | Kashish | W5–W6 |
| BWM weights per segment | Kashish | W6 |
| Observed queue data (λ, μ, SCV inputs) | Kashish | W6 |
| **You deliver** | | |
| `recommend()` + unit tests | Yash (API), Anshuman (explain fields) | **20 Dec** |
| Simulation with field data, queue calibration | Eshwari (report), Kashish | 3 Jan |
| `docs/ENGINE.md` | Eshwari | 10 Jan |

## Task list by week
**W1:** port `research/01_cercos_pilot_experiments.py` into modules under `backend/app/mcdm/`; create the pytest skeleton and fixtures (use your own `backend/requirements.txt` only if Ansh's is not merged yet; otherwise add to it by PR).
**W2:** `range.py` (usable energy, reach with 8% reserve, Wh/km) and `criteria.py` (decision-matrix builder; **effective_kw = min(station kW, vehicle max kW for that connector)**; hard filters: connector compatible, operational, reachable).
**W3:** `wsm_anchored.py` (fixed bounds from `config/criteria_bounds.yaml`), `topsis.py` (baseline), `modes.py` (loads `config/weights.yaml`, per-segment override). Tests: weights sum to 1, ideal station scores 1.0, dominated never wins, **zero rank reversal on 4,000 random problems** for anchored scoring.
**W4:** `queue/queue.py` (Erlang-C M/M/c, Allen–Cunneen M/G/c) with textbook reference values; `explain.py`; `recommend()` returning exactly the structure in `contracts/engine_interface.md`.
**W5:** `simulator.py` and a regression test that reproduces `research/results.json` within tolerance.
**W6:** with Kashish: queue calibration (observed vs predicted wait), BWM weights into `config/weights.yaml` (via PR); low-SoC (10–25%) stress test.
**W7:** re-run simulation with census inputs and survey weights; `docs/ENGINE.md` with formulas, results and limitations.

## Commit trajectory
| Branch | Commits | PR title | Reviewer | Due |
|---|---|---|---|---|
| `feat/engine-port-research` | `refactor(engine): move pilot experiment code into mcdm package` → `test(engine): add pytest skeleton and fixtures` | Engine package skeleton | Yash | 29 Nov |
| `feat/engine-range-criteria` | `feat(engine): add range model with 8 percent reserve` → `feat(engine): add decision-matrix builder with effective kW` → `test(engine): range and criteria tests` | Range + criteria | Yash | 6 Dec |
| `feat/engine-scoring` | `feat(engine): add anchored weighted-sum scoring` → `feat(engine): add TOPSIS baseline` → `feat(engine): load modes and segment overrides` → `test(engine): ideal, dominated, rank-reversal tests` | Scoring + modes | Yash | 13 Dec |
| `feat/queue-model` | `feat(queue): add Erlang-C wait` → `feat(queue): add Allen-Cunneen M/G/c` → `test(queue): reference values` | Queue model | Yash | 20 Dec |
| `feat/engine-recommend` | `feat(engine): add explain contributions` → `feat(engine): add recommend() per engine_interface` → `test(engine): recommend contract test` | recommend() function | Yash | 20 Dec |
| `feat/engine-simulator` | `feat(engine): add seeded simulator` → `test(engine): regression against results.json` | Simulator + regression | Yash | 27 Dec |
| `feat/queue-calibration` | `feat(analysis): calibrate queue model on field data` → `docs(engine): calibration results` | Queue calibration | Yash | 3 Jan |
| `data/survey-weights` | `data(config): add BWM weights per segment` | Survey weights | Yash + Kashish | 3 Jan |
| `docs/engine` | `docs(engine): write ENGINE.md` | Engine documentation | Yash | 10 Jan |

## Definition of Done
- `pytest backend/tests/mcdm backend/tests/queue -q` passes in CI.
- `recommend()` output matches `contracts/engine_interface.md` for 6 modes × 4 segments.
- Anchored scoring has **0.0%** rank reversal on 4,000 problems; TOPSIS baseline still available.
- Erlang-C results match a textbook example; M/G/c with SCV = 1 equals M/M/c.
- Simulator reproduces `results.json` within tolerance; report-ready tables and figures exist.
- Nothing reads a database or the network inside `mcdm/` or `queue/`.

## Antigravity prompt (Planning mode, branch `feat/engine-scoring`, adapt per task)
```
Read AGENTS.md, contracts/engine_interface.md, config/weights.yaml, config/criteria_bounds.yaml and research/01_cercos_pilot_experiments.py.
You work for Atharva. Edit ONLY backend/app/mcdm/, backend/app/queue/, backend/tests/mcdm/, backend/tests/queue/, research/, config/weights.yaml, config/criteria_bounds.yaml, docs/ENGINE.md.
Implement pure functions (no I/O): anchored weighted-sum scoring using fixed bounds, TOPSIS as a baseline, mode/weight loader from YAML with per-segment override, effective_kw = min(station kW, vehicle max kW), hard filters (connector compatible, operational, reachable with 8% reserve).
Write tests first: weights sum to 1; the ideal alternative scores 1.0; a dominated alternative never wins; 4,000 random problems give 0 rank reversals for the anchored method.
Plan first, then implement. Keep commits small as listed in docs/team/atharva.md. Do not edit other folders. Do not push to main.
```

## Report evidence (your half page)
Engine design, formulas, tests (count and results), simulation findings (clearly separated into synthetic and field-based), limitations — with links to merged PRs.
