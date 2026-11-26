# Member Contribution Report — Kashish

**Role:** Field Research, Ethics Governance, BWM Preference Modeling & Queue Statistics Lead  
**Phase-I Allocation:** 6% of Total Project (40% Phase-I Scope)  
**Primary Owned Paths:** `docs/FIELD_PROTOCOL.md`, `docs/ETHICS.md`, `docs/FIELD_FORMS.md`, `analysis/bwm_weights.py`, `analysis/queue_stats.py`, `backend/tests/etl/test_analysis_p3.py` (BWM & queue tests)

---

## 1. Key Deliverables Completed

1. **Field Survey Protocol & Data Collection Ethics (`docs/FIELD_PROTOCOL.md`, `docs/ETHICS.md`, `docs/FIELD_FORMS.md`)**
   - Authored standardized Standard Operating Procedures (SOPs) for on-ground charging station hardware audits, peak-window (`07-10`, `12-15`, `18-21`) queue timing observations, and structured EV driver interviews within 100 km of VIT Bhopal.
   - Established strict **Research Ethics & Privacy Governance**: mandatory verbal consent check prior to logging, strict zero-PII policy (no driver names, phone numbers, or faces photographed), equipment-only photography rules, and explicit coverage mandates for E2W/e-rickshaw (E3W) operators.

2. **Best-Worst Method (BWM) Preference Solver (`analysis/bwm_weights.py`)**
   - Implemented Rezaei's (2015) linear Best-Worst Method optimization model using `scipy.optimize.linprog` to solve $2n - 3$ pairwise driver criterion comparisons (detour, cost, wait time, speed, rating, battery safety).
   - Computes optimal driver weights $w_j$, minimax residual $\xi^*$, and consistency ratios per respondent, plus vehicle-segment geometric mean aggregation.
   - Verified mathematically against Rezaei's published worked benchmark in `backend/tests/etl/test_analysis_p3.py` (`test_bwm_solver_rezaei_worked_example`).

3. **Empirical Queue Telemetry Estimator (`analysis/queue_stats.py`)**
   - Built statistical estimator converting 15-minute manual charger observation counts into empirical arrival rates ($\lambda$), service completion rates ($\mu$), utilization ($\rho = \lambda / (c\mu)$), and Squared Coefficients of Variation ($C_a^2, C_s^2$) needed to calibrate Atharva's Allen-Cunneen $M/G/c$ queue model without live CPO telemetry.
   - Verified via unit tests in `test_queue_stats_computations`.

---

## 2. Pull Requests & Verification Evidence
- **Merged PR:** PR `#3` (`docs/field-protocol-ethics` — commits `c3a9554`/`e5b7e35`, `09bf91c`/`a68f99c`, `87377c0`/`0fe11f3`, merge commit `b1c1358`).
- **Verification Status:** P3 BWM & queue analysis unit tests passing inside the `74/74` backend pytest suite with `scipy` dependency verified in CI.
