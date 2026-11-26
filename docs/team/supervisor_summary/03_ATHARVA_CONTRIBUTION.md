# Member Contribution Report — Atharva

**Role:** Core Algorithms Lead — Recommendation Engine, Queuing Theory & Simulation  
**Phase-I Allocation:** 8% of Total Project (40% Phase-I Scope)  
**Primary Owned Paths:** `backend/app/mcdm/`, `backend/app/queue/`, `backend/tests/mcdm/`, `backend/tests/queue/`, `config/weights.yaml`, `config/criteria_bounds.yaml`, `docs/ENGINE.md`, `research/01_cercos_pilot_experiments.py`

---

## 1. Key Deliverables Completed

1. **Physics-Aware Range & Safety Reserve Model (`backend/app/mcdm/range.py`)**
   - Formulated deterministic energy consumption accounting for speed drag penalties, cabin AC/auxiliary loads, payload mass, and road gradient multipliers.
   - Enforced the mandatory **8.0% State-of-Charge (SoC) safety buffer** when computing reachable range so drivers never get stranded near empty.

2. **Hard Feasibility Filtering & Power Bottleneck Law (`backend/app/mcdm/criteria.py`)**
   - Implemented strict candidate admissibility filters rejecting non-operational stations, connector-incompatible sites (e.g., CCS2 vs LECCS / 15A_Socket), and stations causing arrival SoC below `8.0%`.
   - Enforced the real charging intake law $P_{\text{eff}} = \min(P_{\text{station}}, P_{\text{vehicle}})$, preventing 2W/3W light EVs from overpaying for high-power DC chargers they cannot absorb.

3. **Zero Rank-Reversal Scoring & 6 Driver Modes (`wsm_anchored.py`, `topsis.py`, `modes.py`)**
   - Designed **Domain-Anchored Weighted Sum (WSM)** normalization against fixed physical bounds (`config/criteria_bounds.yaml`) alongside classical TOPSIS and min-max baselines.
   - Proved **0.0% rank reversal** across 4,000 randomized candidate-perturbation stress trials (versus ~7.8%–18.4% in unanchored vector TOPSIS).
   - Configured 6 operational decision modes (`Balanced`, `Cheapest`, `Fastest`, `Shortest`, `HighestRated`, `BatterySafe`) in `config/weights.yaml`.

4. **Analytical Non-Telemetry Queuing Models (`backend/app/queue/queue.py`)**
   - Implemented multi-server **Erlang-C ($M/M/c$)** waiting probabilities and the **Allen-Cunneen ($M/G/c$)** queue waiting time formula incorporating arrival/service variability ($C_a^2, C_s^2$), verified against textbook analytical solutions.

5. **Explainability, Entry Point & Simulator (`explain.py`, `recommend.py`, `simulator.py`, `docs/ENGINE.md`)**
   - Delivered pure, stateless `recommend()` conforming strictly to `contracts/engine_interface.md` with per-criterion weighted contribution breakdowns.
   - Built a seeded simulator reproducing `research/results.json` pilot findings and authored the mathematical reference & viva guide in `docs/ENGINE.md` and weekly logs in `docs/team/logs/atharva.md`.

---

## 2. Pull Requests & Verification Evidence
- **Merged PR:** PR `#8` (`feat/engine-scoring` — commits `9100d93`, `7ae61ef`, `fa85d8a`, `40d808d`, `f1a20ae`).
- **Verification Status:** Dedicated unit & stress suites (`test_range.py`, `test_criteria.py`, `test_scoring.py`, `test_modes.py`, `test_queue.py`, `test_recommend.py`, `test_rank_reversal.py`, `test_simulator.py`) all passing within the `74/74` pytest suite.
