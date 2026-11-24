# Weekly log — Atharva (Recommendation Engine, Queue Models & Simulation Engineer)

## Week 1 (15 Jan – 21 Jan)
- **Hours:** 7
- **Done:** Structured the recommendation engine package skeleton under `backend/app/mcdm/` and `backend/app/queue/`. Ported pilot experiment algorithms from `research/01_cercos_pilot_experiments.py` into pure functions with zero I/O. Created pytest fixtures in `backend/tests/conftest.py` with multi-segment vehicle specs and candidate stations. (Branch: `feat/engine-port-research`)
- **In progress:** EV range and physical power bottleneck modeling.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Implement battery consumption model with mandatory 8.0% reserve constraint and connector-aware power bottleneck rule.
- **Supervisor signature date (record book):** 21 Jan 2026

## Week 2 (22 Jan – 28 Jan)
- **Hours:** 8
- **Done:** Implemented `backend/app/mcdm/range.py` with multi-factor energy consumption modeling (speed drag penalty, cabin climate control, payload mass, road gradient) and strict 8% safety reserve reachability calculations. Implemented `backend/app/mcdm/criteria.py` enforcing the physical charging bottleneck $P_{\text{eff}} = \min(P_{\text{station}}, P_{\text{vehicle}})$ and candidate admissibility filters. Authored unit test suites in `test_range.py` and `test_criteria.py` (7 tests passing). (Branch: `feat/engine-range-criteria`)
- **In progress:** Domain-anchored MCDM scoring and decision modes.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Implement fixed-bound domain-anchored WSM normalisation to prevent rank reversal, and load mode weight profiles.
- **Supervisor signature date (record book):** 28 Jan 2026

## Week 3 (29 Jan – 04 Feb)
- **Hours:** 8
- **Done:** Implemented `backend/app/mcdm/wsm_anchored.py` using domain-anchored bounds from `config/criteria_bounds.yaml` to ensure candidate-set independence. Implemented `backend/app/mcdm/topsis.py` preserving vector-normalized TOPSIS and min-max WSM as comparative research baselines. Implemented `backend/app/mcdm/modes.py` loading the 6 operational driver modes and segment overrides from `config/weights.yaml`. Authored unit tests in `test_scoring.py` and `test_modes.py` (8 tests passing). (Branch: `feat/engine-scoring`)
- **In progress:** Closed-form queueing delay models.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Implement Erlang-C multi-server waiting times and Allen-Cunneen approximation for general service time distributions.
- **Supervisor signature date (record book):** 04 Feb 2026

## Week 4 (05 Feb – 11 Feb)
- **Hours:** 8
- **Done:** Implemented analytical queue models in `backend/app/queue/queue.py`: Erlang-C ($M/M/c$) for probability of waiting and expected delay, and the Allen-Cunneen ($M/G/c$) approximation incorporating arrival and service time squared coefficients of variation ($C_a^2, C_s^2$). Validated against textbook analytical reference values ($M/M/1$ and $M/M/2$) and saturation boundaries in `test_queue.py` (9 tests passing). (Branch: `feat/queue-model`)
- **In progress:** Recommendation orchestration and explainability accounting.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Build `recommend()` entry point conforming to `contracts/engine_interface.md` and per-criterion contribution notes.
- **Supervisor signature date (record book):** 11 Feb 2026

## Week 5 (12 Feb – 18 Feb)
- **Hours:** 8
- **Done:** Implemented `backend/app/mcdm/explain.py` calculating per-criterion contribution points ($w_j \cdot N_j$) and natural language reasoning notes. Implemented deterministic `recommend()` in `backend/app/mcdm/recommend.py` conforming strictly to `contracts/engine_interface.md` and returning Pydantic v2 `RecommendResult`. Verified contracts across all 6 modes and 4 vehicle segments in `test_recommend.py` (4 tests passing). (Branch: `feat/engine-recommend`)
- **In progress:** Seeded corridor simulator and rank reversal stress testing.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Port 20,000-trip synthetic corridor simulation and validate rank stability across 4,000 random problems.
- **Supervisor signature date (record book):** 18 Feb 2026

## Week 6 (19 Feb – 25 Feb)
- **Hours:** 9
- **Done:** Developed modular seeded simulation engine in `backend/app/mcdm/simulator.py` reproducing `research/results.json` pilot experiment benchmarks within confidence intervals. Executed 4,000-problem rank reversal stress test verifying strictly 0.0% rank reversal for anchored WSM vs 7.8% for TOPSIS. Authored comprehensive technical documentation and oral examination defense guide in `docs/ENGINE.md`. Authored regression tests in `test_rank_reversal.py` and `test_simulator.py`. (Branch: `feat/engine-scoring`, PR #8)
- **In progress:** Peer code review and API handover with Yash.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Support Yash with API integration and collaborate with Kashish on survey BWM weight integration.
- **Supervisor signature date (record book):** 25 Feb 2026
