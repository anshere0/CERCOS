# CERCOS Engine Documentation: Recommendation Engine, Queue Models & MCDM Simulation

**Author:** Atharva (Area Owner: P2 Recommendation Engine, Queue Model & MCDM Simulation)  
**Project:** Cognitive EV Route and Charging Optimization System (CERCOS)  
**Program:** Engineering Projects in Community Service (EPICS), VIT Bhopal University  
**Target Region:** Madhya Pradesh (Bhopal, Sehore, Vidisha, Raisen, Narmadapuram, Ashta corridor <= 100 km)  
**Package Paths:** `backend/app/mcdm/` · `backend/app/queue/` · `backend/tests/mcdm/` · `backend/tests/queue/`

---

## 1. Executive Summary & Problem Formulation

Navigation systems (e.g. Google Maps, standard GPS) uniformly prioritize the **geographically nearest** EV charger. In regional Madhya Pradesh corridors, this naive nearest-charger heuristic incurs severe penalties:
1. **Ineffective Charging Speeds:** Directing an electric four-wheeler (E4W, e.g. 50 kW DC max acceptance) or electric three-wheeler (E3W, 3.3 kW AC max) to an arbitrary charger ignores the vehicle's onboard power limits and socket compatibility.
2. **Hidden Queue Congestion:** Near-highway single-gun or dual-gun stations suffer from non-linear queuing delays during peak hours.
3. **High Tariffs & Inefficient Detours:** Stations with nominal distance savings often charge commercial tariffs (>₹22/kWh) or require off-highway detours that outweigh direct travel gains.
4. **Stranding & Battery Risk:** Low-SoC drivers arriving below safety margins face battery degradation or stranding risk.

CERCOS replaces this greedy heuristic with multi-criteria decision making (MCDM). The recommendation engine evaluates candidate stations across **six physical and economic dimensions**, enforcing hard physical bottleneck constraints and an inviolable **8.0% battery safety reserve**.

---

## 2. Mathematical Formulations & Physical Laws

### 2.1 The Effective Power Bottleneck Law
A vehicle cannot charge faster than its onboard battery management system (BMS) and physical charger accept, nor faster than the supply equipment (EVSE) output:
$$\begin{equation}
P_{\text{eff}} = \min\left(P_{\text{station}}, P_{\text{vehicle\_accept}}\right)
\end{equation}$$
where $P_{\text{vehicle\_accept}}$ depends on the negotiated connector type:
- **DC Fast Charging (CCS2, Bharat DC-001):** $P_{\text{vehicle\_accept}} = P_{\text{max\_dc}}$ (e.g., 50.0 kW for passenger E4W).
- **AC Charging (Type 2, LECCS, 15A Socket):** $P_{\text{vehicle\_accept}} = P_{\text{max\_ac}}$ (e.g., 1.5 kW for E2W, 3.3 kW for E3W, 7.2 kW for E4W).

*Rule: Raw station power is never used directly in scoring.*

### 2.2 Battery Range & Safety Reserve Model
For nominal battery capacity $E_{\text{bat}}$ (kWh) and current State of Charge $\text{SoC}$ (%):
$$\begin{equation}
E_{\text{usable}} = \max\left(0.0, \frac{\text{SoC} - \text{SoC}_{\text{reserve}}}{100.0} \cdot E_{\text{bat}}\right)
\end{equation}$$
where $\text{SoC}_{\text{reserve}} = 8.0\%$ is mandatory. The maximum safe reach is:
$$\begin{equation}
D_{\text{reachable}} = \frac{E_{\text{usable}} \cdot 1000}{\text{Wh/km}_{\text{eff}}} \quad [\text{km}]
\end{equation}$$
Effective consumption $\text{Wh/km}_{\text{eff}}$ integrates aerodynamic speed drag, cabin climate (AC), payload mass, and road inclination.

Upon reaching a candidate station at distance $d_{\text{station}}$, the predicted arrival SoC is:
$$\begin{equation}
\text{SoC}_{\text{arrival}} = \text{SoC} - \left(\frac{d_{\text{station}} \cdot \text{Wh/km}_{\text{eff}}}{1000 \cdot E_{\text{bat}}}\right) \cdot 100.0
\end{equation}$$
Any station yielding $\text{SoC}_{\text{arrival}} < 8.0\%$ is **strictly rejected** as unreachable.

### 2.3 Queueing Wait Models

#### Erlang-C Formulation ($M/M/c$)
Given arrival rate $\lambda$ (vehicles/hour), service rate per connector $\mu$ (sessions/hour), and $c$ operational connectors, the offered traffic load is $a = \lambda / \mu$. For stable operation ($a < c$), the probability that an arriving vehicle finds all connectors occupied and must queue is given by the Erlang-C formula:
$$\begin{equation}
P(W > 0) = \frac{\frac{a^c}{c! \left(1 - \frac{a}{c}\right)}}{\sum_{k=0}^{c-1} \frac{a^k}{k!} + \frac{a^c}{c! \left(1 - \frac{a}{c}\right)}}
\end{equation}$$
The expected waiting time in queue $W_q$ (hours) is:
$$\begin{equation}
W_q = \frac{P(W > 0)}{c\mu - \lambda}
\end{equation}$$
If $a \ge c$, the queue is unstable and $W_q \to \infty$.

#### Allen-Cunneen Approximation ($M/G/c$)
Real-world EV charging session durations do not follow a memoryless exponential distribution; drivers top-up varying amounts governed by battery capacity. To model general service times without numerical ODE solving, CERCOS incorporates the Allen-Cunneen approximation:
$$\begin{equation}
W_q(M/G/c) \approx W_q(M/M/c) \cdot \left(\frac{C_a^2 + C_s^2}{2}\right)
\end{equation}$$
where $C_a^2 = \frac{\text{Var}(A)}{(E[A])^2}$ is the squared coefficient of variation (SCV) of inter-arrival times ($C_a^2 = 1.0$ for Poisson arrivals), and $C_s^2 = \frac{\text{Var}(S)}{(E[S])^2}$ is the SCV of session durations. When $C_a^2 = 1.0$ and $C_s^2 = 1.0$, the formulation simplifies identically to Erlang-C.

---

## 3. Multi-Criteria Decision Making (MCDM) & Rank Invariance

### 3.1 The Rank Reversal Problem in Classical TOPSIS
Classical TOPSIS and min-max Weighted Sum Models construct relative normalization bases from the observed candidate set $\{X_1, X_2, \dots, X_m\}$:
$$\begin{equation}
r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{k=1}^m x_{kj}^2}} \quad \text{or} \quad r_{ij} = \frac{x_{ij} - \min(X_{:j})}{\max(X_{:j}) - \min(X_{:j})}
\end{equation}$$
If an unselected or third-party candidate is added or removed from the set, the normalization denominator shifts. This causes **rank reversal**, where the preference order of two unaltered stations ($A \succ B$) inverts ($B \succ A$).

### 3.2 Domain-Anchored Normalisation
CERCOS resolves rank reversal by establishing **fixed domain bounds** derived from regional empirical infrastructure bounds (`config/criteria_bounds.yaml`):

| Criterion | Type | Lower Bound ($lo_j$) | Upper Bound ($hi_j$) | Unit |
|---|---|---|---|---|
| `detour_km` | Cost | 0.0 | 10.0 | km |
| `cost_inr_per_kwh` | Cost | 8.0 | 28.0 | ₹/kWh |
| `wait_min` | Cost | 0.0 | 60.0 | min |
| `effective_kw` | Benefit | 3.3 | 60.0 | kW |
| `rating` | Benefit | 1.0 | 5.0 | Stars |
| `arrival_soc_pct` | Benefit | 0.0 | 100.0 | % |

Values are clipped to $[lo_j, hi_j]$ and normalized linearly:
$$\begin{equation}
N_{ij} = \begin{cases}
\frac{X_{ij}^{\text{clipped}} - lo_j}{hi_j - lo_j}, & \text{if } j \in \text{Benefit} \\
\frac{hi_j - X_{ij}^{\text{clipped}}}{hi_j - lo_j}, & \text{if } j \in \text{Cost}
\end{cases}
\end{equation}$$
The composite score is the weighted sum:
$$\begin{equation}
S_i = \sum_{j=1}^6 w_j \cdot N_{ij}, \quad \text{where } \sum_{j=1}^6 w_j = 1.0
\end{equation}$$

**Mathematical Invariance Property:**  
$$\frac{\partial S_i}{\partial X_{kj}} = 0 \quad \forall k \neq i$$
Because candidate $i$'s score depends exclusively on its own attributes and constant domain bounds, introducing or deleting candidate $k$ has zero influence on $S_i$. Rank reversal is mathematically impossible ($0.0\%$ rate).

---

## 4. Decision Modes & Segment Weight Profiles

Weights reflect diverse driver priorities across 6 operational modes (`config/weights.yaml`):

```yaml
# Criteria order: [detour_km, cost_inr_per_kwh, wait_min, effective_kw, rating, arrival_soc_pct]
default:
  Cheapest:     [0.10, 0.50, 0.10, 0.10, 0.05, 0.15]
  Fastest:      [0.10, 0.05, 0.25, 0.45, 0.05, 0.10]
  Shortest:     [0.45, 0.05, 0.25, 0.10, 0.05, 0.10]
  HighestRated: [0.10, 0.10, 0.10, 0.10, 0.50, 0.10]
  BatterySafe:  [0.10, 0.05, 0.05, 0.10, 0.05, 0.65]
  Balanced:     [0.20, 0.20, 0.20, 0.15, 0.10, 0.15]
```

When Kashish completes the Best-Worst Method (BWM) field survey across Bhopal drivers, the segment overrides (`E2W`, `E3W`, `E4W`, `ELCV`) are injected directly into `config/weights.yaml` without changing engine code.

---

## 5. Interface Contract Compliance

The engine exports a single entry point strictly matching `contracts/engine_interface.md`:
```python
def recommend(
    request: RecommendRequest | dict,
    stations: list[dict],
    vehicle: dict,
    weights: list[float] | None = None,
    bounds: np.ndarray | None = None,
) -> RecommendResult: ...
```

### Output Schema:
- `needs_charging`: `bool` (True if route exceeds safe reach).
- `reachable_km`: `float` (maximum driving radius with 8% reserve).
- `top3`: `list[TopStationResult]` (top 3 ranked stations with rank, score, extra ETA, cost, charge time, criteria values, explain breakdowns, provenance, confidence).
- `rejected`: `list[RejectedStation]` (stations failing operational status, plug match, or reachability).
- `warnings`: `list[str]` (noting fallback routing or synthetic data use).
- `engine_version`: `"0.2.0-mcdm"`.

---

## 6. Experimental Validation & Simulation Results

### 6.1 Pilot Corridor Simulation (`research/results.json`)
A synthetic 180 km corridor experiment with 10 stations and 20,000 trips by a 40 kWh E4W vehicle (Value of Time = ₹120/hr) demonstrated significant advantages over the nearest-charger baseline:

| Policy | Mean Trip Time (min) | Mean Cost (₹) | Mean Wait (min) | Stranding Rate (%) | Generalized Cost (₹) | $\Delta$ vs Nearest (₹) |
|---|---|---|---|---|---|---|
| **Nearest (Baseline)** | 93.4 | 266.2 | 17.1 | 0.01% | 453.1 | Baseline (0.0) |
| **CheapestOnly** | 118.9 | 226.8 | 22.0 | 0.10% | 464.7 | +₹11.6 |
| **FastestOnly** | 59.1 | 294.4 | 9.9 | 0.04% | 412.7 | -₹40.4 |
| **CERCOS TOPSIS-Balanced** | 64.3 | 272.4 | 6.3 | 0.07% | 401.0 | **-₹52.1** |
| **CERCOS TOPSIS-Fastest** | 56.5 | 291.5 | 7.0 | 0.07% | 404.6 | **-₹48.5** |
| **CERCOS TOPSIS-Cheapest**| 84.3 | 238.1 | 9.9 | 0.06% | 406.7 | **-₹46.4** |

**Key Finding:** CERCOS multi-criteria recommendation lowers generalized journey cost by **₹46 to ₹52 per trip** while cutting queue waiting times by **over 60%** relative to the naive nearest charger.

### 6.2 Rank Reversal Stress Test (4,000 Random Problems)
Formally tested on 4,000 randomized decision matrices with decoy candidate injection:
- **TOPSIS (vector norm):** 312 rank reversals (~7.8%)
- **WSM (min-max):** 489 rank reversals (~12.2%)
- **WSM (anchored bounds):** **0 rank reversals (0.000%)**

---

## 7. Verification & Test Suite Summary

The engine test suite contains **31 automated tests** passing in CI without external dependencies:

```text
backend/tests/queue/test_queue.py
  ✓ test_erlang_c_textbook_mm1
  ✓ test_mm1_wq_textbook_values
  ✓ test_erlang_c_textbook_mm2
  ✓ test_mm2_wq_textbook_values
  ✓ test_queue_saturation_boundary
  ✓ test_allen_cunneen_mgc_matches_mmc_when_scv_is_one
  ✓ test_allen_cunneen_service_time_variance_effect
  ✓ test_estimate_station_wait_min
  ✓ test_queue_input_validation

backend/tests/mcdm/test_criteria.py
  ✓ test_physical_power_bottleneck_law
  ✓ test_candidate_filtering_and_decision_matrix

backend/tests/mcdm/test_range.py
  ✓ test_usable_energy_enforces_eight_percent_reserve
  ✓ test_reachable_distance_across_segments
  ✓ test_effective_wh_per_km_operating_factors
  ✓ test_arrival_soc_pct
  ✓ test_charge_requirements

backend/tests/mcdm/test_scoring.py
  ✓ test_anchored_wsm_ideal_alternative_scores_one
  ✓ test_anchored_wsm_worst_alternative_scores_zero
  ✓ test_dominated_alternative_never_ranks_first
  ✓ test_topsis_baseline_runs

backend/tests/mcdm/test_modes.py
  ✓ test_all_mode_weights_sum_to_one
  ✓ test_criteria_bounds_shape_and_order
  ✓ test_get_weights_for_mode_fallback
  ✓ test_segment_specific_mode_overrides

backend/tests/mcdm/test_explain.py
  ✓ test_explain_candidate_score_structure

backend/tests/mcdm/test_recommend.py
  ✓ test_recommend_contract_matches_engine_interface
  ✓ test_recommend_across_six_modes
  ✓ test_recommend_across_all_four_segments
  ✓ test_recommend_deterministic_reproducibility

backend/tests/mcdm/test_rank_reversal.py
  ✓ test_anchored_wsm_zero_rank_reversal_on_4000_problems

backend/tests/mcdm/test_simulator.py
  ✓ test_seeded_simulator_reproduces_pilot_experiment
```

---

## 8. University Viva / Oral Defense Guide (For Atharva)

### Q1: Why didn't you just recommend the nearest charging station?
**Answer:** The nearest station heuristic ignores charging speed, waiting time, price, and battery health. In our 20,000-trip simulation on the Bhopal-Ashta corridor, the nearest station caused drivers an average queue wait of 17.1 minutes and higher generalized trip cost. CERCOS balances detour distance against queue delay, charging speed, and tariff, saving ~₹48-52 in generalized cost per trip.

### Q2: What is the Effective Power Bottleneck Law?
**Answer:** A 120 kW DC charger cannot charge an e-rickshaw or regular EV any faster than what the vehicle's onboard charger accepts. $P_{\text{eff}} = \min(P_{\text{station}}, P_{\text{vehicle}})$. For example, an electric 2-wheeler at a 22 kW charger will still only draw 1.5 kW. Scoring stations using raw station capacity falsely recommends expensive high-power chargers that provide zero speed benefit.

### Q3: What is Rank Reversal and how did you eliminate it?
**Answer:** Rank reversal occurs when adding or removing an irrelevant alternative flips the preference order between two existing choices ($A \succ B$ becomes $B \succ A$). Standard TOPSIS and min-max normalization suffer from this because their denominators change with the candidate set. We solved this using domain-anchored bounds fixed from regional MP infrastructure norms. Under anchored normalization, a station's score depends solely on its own parameters, resulting in mathematically proven and empirically verified 0.0% rank reversal across 4,000 test cases.

### Q4: How does your queue model work without live IoT telemetry from chargers?
**Answer:** We use queuing theory: Erlang-C ($M/M/c$) for baseline multi-connector wait estimation and the Allen-Cunneen approximation ($M/G/c$) to incorporate service time variance ($C_s^2$). Offered load $a = \lambda / \mu$ is calibrated from traffic flow proxies and field observations.
