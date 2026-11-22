"""
CERCOS - Pilot Experiments (SYNTHETIC DATA - method validation only)
=====================================================================
Purpose : Show, with reproducible code, that (a) multi-criteria (TOPSIS) charger
          selection behaves differently from "nearest charger", (b) TOPSIS rank
          stability / rank-reversal can be measured, (c) queueing (M/M/c, M/G/c)
          gives non-linear waits.
IMPORTANT: Station attributes below are SIMULATED. Results demonstrate the
          METHOD, not real-world effect sizes. Phase-1 field data replaces them.
Run     : python 01_cercos_pilot_experiments.py     (seeded -> reproducible)
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------- weights (from CERCOS docs)
# order: distance(detour), cost, wait, speed, rating, safety
MODES = {
    "Cheapest":      [0.10, 0.50, 0.10, 0.10, 0.05, 0.15],
    "Fastest":       [0.10, 0.05, 0.25, 0.45, 0.05, 0.10],
    "Shortest":      [0.45, 0.05, 0.25, 0.10, 0.05, 0.10],
    "HighestRated":  [0.10, 0.10, 0.10, 0.10, 0.50, 0.10],
    "BatterySafe":   [0.10, 0.05, 0.05, 0.10, 0.05, 0.65],
    "Balanced":      [0.20, 0.20, 0.20, 0.15, 0.10, 0.15],
}
BENEFIT = np.array([0, 0, 0, 1, 1, 1], dtype=bool)  # distance,cost,wait = cost-type

def topsis(X, w, benefit=BENEFIT):
    X = np.asarray(X, float)
    norm = np.sqrt((X ** 2).sum(0)); norm[norm == 0] = 1
    V = X / norm * w
    ideal = np.where(benefit, V.max(0), V.min(0))
    anti = np.where(benefit, V.min(0), V.max(0))
    sp = np.sqrt(((V - ideal) ** 2).sum(1)); sm = np.sqrt(((V - anti) ** 2).sum(1))
    return sm / (sp + sm + 1e-12)

def wsm_minmax(X, w, benefit=BENEFIT):
    X = np.asarray(X, float); mn, mx = X.min(0), X.max(0); rng = np.where(mx - mn == 0, 1, mx - mn)
    N = np.where(benefit, (X - mn) / rng, (mx - X) / rng)
    return N @ w

def wsm_anchored(X, w, bounds, benefit=BENEFIT):
    """Fixed, domain-anchored bounds -> independent of the candidate set (no rank reversal)."""
    lo, hi = bounds[:, 0], bounds[:, 1]
    Xc = np.clip(X, lo, hi)
    N = np.where(benefit, (Xc - lo) / (hi - lo), (hi - Xc) / (hi - lo))
    return N @ w

# ---------------------------------------------------------------- queueing
def erlang_c(c, a):
    """P(wait>0) for M/M/c with offered load a=lambda/mu (a<c)."""
    if a >= c: return 1.0
    s = sum(a ** k / math.factorial(k) for k in range(c))
    t = a ** c / (math.factorial(c) * (1 - a / c))
    return t / (s + t)

def mmc_wq(lam, mu, c):
    """Mean wait in queue (hours). lam, mu per hour."""
    a = lam / mu
    if a >= c: return float("inf")
    return erlang_c(c, a) / (c * mu - lam)

# ================================================================= EXPERIMENT 1
# Synthetic 180 km corridor, 10 stations, 20,000 trips by a 40 kWh E4W (50 kW DC acceptance)
L, N_ST, N_TRIPS = 180.0, 10, 20000
CAP, CONS, V_ACCEPT, SPEED_DETOUR, VOT = 40.0, 0.150, 50.0, 40.0, 120.0  # kWh, kWh/km, kW, km/h, Rs/h

def make_corridor():
    pos = np.sort(RNG.uniform(5, L - 5, N_ST))
    detour = RNG.uniform(0.2, 6.0, N_ST)
    power = RNG.choice([7.4, 25, 30, 60, 120], N_ST, p=[.25, .2, .2, .25, .1])
    tariff = np.clip(10 + 0.07 * power + RNG.normal(0, 2.5, N_ST), 9, 26)
    rating = np.clip(RNG.normal(3.9, 0.5, N_ST), 2.5, 4.9)
    conn = RNG.integers(2, 7, N_ST)
    rho = RNG.uniform(0.15, 0.9, N_ST)
    return pos, detour, power, tariff, rating, conn, rho

def simulate():
    res = {k: [] for k in ["Nearest", "CheapestOnly", "FastestOnly"] + [f"TOPSIS-{m}" for m in MODES]}
    infeasible = 0
    for _ in range(N_TRIPS):
        pos, det, pw, tar, rat, cn, rho = make_corridor()
        soc0 = RNG.uniform(0.15, 0.45)
        cons_true = CONS * RNG.normal(1.0, 0.12)          # real consumption deviates from model
        e0 = soc0 * CAP
        reach_pred = (e0 - 0.08 * CAP) / CONS             # planner's reach (8% reserve)
        ok = np.where(pos + det <= reach_pred)[0]
        if len(ok) == 0: infeasible += 1; continue
        eff_p = np.minimum(pw, V_ACCEPT)
        mu = 1.0 / ((0.35 * CAP) / eff_p)                  # sessions/h per connector (35% top-up avg)
        lam = rho * cn * mu
        wq_true = np.array([mmc_wq(l, m, c) for l, m, c in zip(lam, mu, cn)]) * 60  # min
        wq_pred = wq_true * RNG.lognormal(0, 0.35, N_ST)   # imperfect prediction
        arr_soc_pred = (e0 - (pos + det) * CONS) / CAP * 100
        # decision matrix over reachable stations: detour, cost, wait, speed, rating, safety
        X = np.c_[det, tar, wq_pred, eff_p, rat, arr_soc_pred][ok]
        choices = {
            "Nearest": ok[np.argmin(pos[ok] + det[ok])],
            "CheapestOnly": ok[np.argmin(tar[ok])],
            "FastestOnly": ok[np.argmax(eff_p[ok])],
        }
        for m, w in MODES.items():
            choices[f"TOPSIS-{m}"] = ok[np.argmax(topsis(X, np.array(w)))]
        for name, i in choices.items():
            # realised outcome
            e_arr = e0 - (pos[i] + det[i]) * cons_true
            stranded = e_arr < 0.02 * CAP
            rem = L - pos[i]
            need = max(0.0, rem * cons_true * 1.10 + 0.10 * CAP - max(e_arr, 0))
            need = min(need, 0.8 * CAP - max(e_arr, 0)) if need > 0.8 * CAP - max(e_arr, 0) else need
            wait = (RNG.exponential(1.0 / max((cn[i] * mu[i] - lam[i]), 1e-6)) * 60
                    if RNG.random() < erlang_c(cn[i], lam[i] / mu[i]) else 0.0)
            t_ch = need / eff_p[i] * 60
            t_det = 2 * det[i] / SPEED_DETOUR * 60
            time = wait + t_ch + t_det
            cost = need * tar[i]
            res[name].append((time, cost, wait, float(stranded), cost + time / 60 * VOT))
    return {k: np.array(v) for k, v in res.items()}, infeasible

R, infeasible = simulate()
base = R["Nearest"]
rows = []
for k, a in R.items():
    d = a[:, 4] - base[:, 4]
    se = d.std(ddof=1) / math.sqrt(len(d))
    rows.append(dict(policy=k, mean_time_min=a[:, 0].mean(), p90_time_min=np.percentile(a[:, 0], 90),
                     mean_cost_inr=a[:, 1].mean(), mean_wait_min=a[:, 2].mean(),
                     stranding_pct=100 * a[:, 3].mean(), gen_cost_inr=a[:, 4].mean(),
                     delta_gen_cost_vs_nearest=d.mean(), ci95=1.96 * se))

# ================================================================= EXPERIMENT 2  rank stability + reversal
def random_matrix(m=6):
    return np.c_[RNG.uniform(0.2, 8, m), RNG.uniform(9, 26, m), RNG.uniform(0, 40, m),
                 RNG.choice([7.4, 25, 30, 50], m), RNG.uniform(2.5, 4.9, m), RNG.uniform(3, 45, m)]

W = np.array(MODES["Balanced"])
stab = []
for _ in range(300):                                     # 300 random decision problems
    X = random_matrix(); win = np.argmax(topsis(X, W)); same = 0
    for _ in range(200):
        w2 = RNG.dirichlet(W * 40); same += (np.argmax(topsis(X, w2)) == win)
    stab.append(same / 200)
stab = np.array(stab)

BOUNDS = np.array([[0, 10], [8, 28], [0, 60], [3.3, 60], [1, 5], [0, 100]], float)
rev = {"TOPSIS (vector norm)": 0, "WSM (min-max)": 0, "WSM (anchored bounds)": 0}
T = 4000
for _ in range(T):
    X = random_matrix(5)
    clone = X[RNG.integers(len(X))] * np.array([1.15, 1.10, 1.3, 0.85, 0.9, 0.9])  # a dominated copy
    X2 = np.vstack([X, clone])
    for name, f in [("TOPSIS (vector norm)", lambda M: topsis(M, W)),
                    ("WSM (min-max)", lambda M: wsm_minmax(M, W)),
                    ("WSM (anchored bounds)", lambda M: wsm_anchored(M, W, BOUNDS))]:
        if np.argmax(f(X)) != np.argmax(f(X2)[:len(X)]) : rev[name] += 1
rev = {k: 100 * v / T for k, v in rev.items()}

# ================================================================= EXPERIMENT 3  queueing
rho_grid = np.linspace(0.05, 0.97, 60)
queue_curves = {}
for c in [1, 2, 4, 8]:
    mu = 1.0  # per hour -> time unit = mean service time
    queue_curves[c] = [mmc_wq(r * c * mu, mu, c) for r in rho_grid]  # in service-times
scv_table = {}
for scv in [0.5, 1.0, 2.0]:
    scv_table[str(scv)] = [(1 + scv) / 2 * mmc_wq(0.85 * c * 1.0, 1.0, c) for c in [1, 2, 4]]

# ================================================================= FIGURES
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
names = [r["policy"] for r in rows]; col = ["#9aa" if n in ("Nearest", "CheapestOnly", "FastestOnly") else "#2a7" for n in names]
ax[0].barh(names, [r["gen_cost_inr"] for r in rows], color=col); ax[0].set_title("Generalised cost per stop (Rs)\n(charging cost + time x Rs120/h)"); ax[0].invert_yaxis()
ax[1].barh(names, [r["stranding_pct"] for r in rows], color=col); ax[1].set_title("Stranding rate (%)"); ax[1].invert_yaxis()
ax[2].barh(names, [r["mean_wait_min"] for r in rows], color=col); ax[2].set_title("Mean queue wait (min)"); ax[2].invert_yaxis()
fig.suptitle("Exp 1 - Nearest vs single-criterion vs TOPSIS (SYNTHETIC 180 km corridor, 20k trips)", y=1.02); fig.tight_layout()
fig.savefig("figures/fig1_policy_comparison.png", dpi=150, bbox_inches="tight"); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].hist(stab * 100, bins=20, color="#27a"); ax[0].set_xlabel("% of weight perturbations keeping the same #1 station"); ax[0].set_ylabel("decision problems"); ax[0].set_title("Exp 2a - TOPSIS winner stability\n(Dirichlet noise on Balanced weights)")
ax[1].bar(list(rev), list(rev.values()), color=["#c53", "#c53", "#2a7"]); ax[1].set_ylabel("% problems where #1 changes\nafter adding a DOMINATED station"); ax[1].set_title("Exp 2b - Rank-reversal rate"); plt.setp(ax[1].get_xticklabels(), rotation=15)
fig.tight_layout(); fig.savefig("figures/fig2_rank_stability.png", dpi=150, bbox_inches="tight"); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 4.2))
for c, y in queue_curves.items(): ax.plot(rho_grid, y, label=f"c={c} connectors")
ax.set_ylim(0, 6); ax.set_xlabel("utilisation rho"); ax.set_ylabel("mean wait (x mean service time)"); ax.set_title("Exp 3 - M/M/c waiting is highly non-linear"); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig("figures/fig3_queueing.png", dpi=150); plt.close(fig)

out = dict(note="SYNTHETIC DATA - validates method, not real-world effect size",
           trips_simulated=N_TRIPS, infeasible_trips_no_reachable_station=infeasible,
           policy_table=rows,
           topsis_winner_stability=dict(mean_pct=100 * stab.mean(), p10_pct=100 * np.percentile(stab, 10), p50_pct=100 * np.percentile(stab, 50)),
           rank_reversal_pct=rev,
           mm_c_wait_in_service_times_at_rho_0_85=scv_table)
json.dump(out, open("results.json", "w"), indent=2)
print(json.dumps(out, indent=2))
