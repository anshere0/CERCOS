"""
CERCOS - Advanced Research Experiment 02: Heterogeneous Fleet & Power Acceptance
================================================================================
Investigates:
1. Fleet Heterogeneity: Performance across MP's real fleet mix:
   E2W (49.6%), E3W (47.6%), E4W (2.8%).
2. The Acceptance Bottleneck: Eff_kW = min(station_kW, vehicle_accept_kW)
   and its impact on generalized trip cost and tariff inefficiency.
3. Queuing Non-Linearities: M/G/c Allen-Cunneen queue estimation with SCV.
4. Benchmarking: Nearest vs Greedy vs CERCOS (Anchored WSM & TOPSIS).

Reproducible seed: 101
"""
import json, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(101)

# Fleet definitions based on MP commercial registrations
FLEET = {
    "E2W": {
        "share": 0.496,
        "cap": 3.5,            # kWh battery capacity
        "cons": 0.038,         # kWh/km
        "max_accept": 3.3,     # kW max onboard charge acceptance (AC)
        "vot": 60.0,           # INR/hour value of time
        "allowed_plugs": ["Type2", "LECCS", "Socket"],
        "range_full": 3.5 / 0.038 # ~92 km
    },
    "E3W": {
        "share": 0.476,
        "cap": 8.0,            # kWh battery capacity (e-rickshaw / cargo)
        "cons": 0.085,         # kWh/km
        "max_accept": 4.5,     # kW max onboard charge acceptance
        "vot": 90.0,           # INR/hour
        "allowed_plugs": ["Bharat_DC001", "Bharat_AC001", "Socket", "Type2"],
        "range_full": 8.0 / 0.085 # ~94 km
    },
    "E4W": {
        "share": 0.028,
        "cap": 40.0,           # kWh (cab / passenger car)
        "cons": 0.150,         # kWh/km
        "max_accept": 50.0,    # kW DC fast charge
        "vot": 160.0,          # INR/hour
        "allowed_plugs": ["CCS2", "Type2"],
        "range_full": 40.0 / 0.150 # ~266 km
    }
}

MODES = {
    "Balanced":     [0.20, 0.20, 0.20, 0.15, 0.10, 0.15],
    "Cheapest":     [0.10, 0.50, 0.10, 0.10, 0.05, 0.15],
    "Fastest":      [0.10, 0.05, 0.25, 0.45, 0.05, 0.10],
    "BatterySafe":  [0.10, 0.05, 0.05, 0.10, 0.05, 0.65],
}
BENEFIT = np.array([0, 0, 0, 1, 1, 1], dtype=bool)  # Detour, Cost, Wait = cost-type (0)

# Anchored bounds: detour [0, 8], cost [8, 26], wait [0, 45], eff_p [1, 60], rating [1, 5], soc [0, 100]
BOUNDS = np.array([[0, 8], [8, 26], [0, 45], [1.0, 60.0], [1.0, 5.0], [0.0, 100.0]], float)

def topsis(X, w, benefit=BENEFIT):
    X = np.asarray(X, float)
    norm = np.sqrt((X ** 2).sum(0))
    norm[norm == 0] = 1.0
    V = (X / norm) * w
    ideal = np.where(benefit, V.max(0), V.min(0))
    anti = np.where(benefit, V.min(0), V.max(0))
    sp = np.sqrt(((V - ideal) ** 2).sum(1))
    sm = np.sqrt(((V - anti) ** 2).sum(1))
    denom = sp + sm + 1e-12
    return sm / denom

def wsm_anchored(X, w, bounds=BOUNDS, benefit=BENEFIT):
    X = np.asarray(X, float)
    lo, hi = bounds[:, 0], bounds[:, 1]
    Xc = np.clip(X, lo, hi)
    N = np.where(benefit, (Xc - lo) / (hi - lo), (hi - Xc) / (hi - lo))
    return N @ w

def erlang_c(c, a):
    if a >= c: return 1.0
    s = sum(a ** k / math.factorial(k) for k in range(c))
    t = (a ** c) / (math.factorial(c) * (1 - a / c))
    return t / (s + t)

def mgc_wq(lam, mu, c, scv_a=1.0, scv_s=1.2):
    """Allen-Cunneen approximation for M/G/c queue mean wait time (hours)."""
    a = lam / mu
    if a >= c: return 1.5 # saturated fallback cap (hours)
    p_wait = erlang_c(c, a)
    wq_mmc = p_wait / (c * mu - lam)
    return ((scv_a + scv_s) / 2.0) * wq_mmc

# Synthetic corridor: Bhopal - Sehore - Ashta (100 km)
CORRIDOR_KM = 100.0
N_STATIONS = 12
N_TRIPS = 50000

def generate_corridor():
    pos = np.sort(RNG.uniform(4.0, CORRIDOR_KM - 4.0, N_STATIONS))
    detour = RNG.uniform(0.3, 4.5, N_STATIONS)
    # realistic power distribution along highway: 3.3kW, 7.4kW, 25kW, 30kW, 60kW
    st_power = RNG.choice([3.3, 7.4, 25.0, 30.0, 60.0], N_STATIONS, p=[0.25, 0.35, 0.20, 0.15, 0.05])
    tariff = np.clip(10.5 + 0.06 * st_power + RNG.normal(0, 1.8, N_STATIONS), 9.0, 24.0)
    rating = np.clip(RNG.normal(4.1, 0.45, N_STATIONS), 2.8, 4.9)
    conn_count = RNG.integers(2, 6, N_STATIONS)
    utilization = RNG.uniform(0.20, 0.85, N_STATIONS)
    # Available plugs at each station
    plugs = []
    for p in st_power:
        if p <= 3.3: plugs.append(["Socket", "LECCS"])
        elif p <= 7.4: plugs.append(["Type2", "Socket", "LECCS"])
        elif p <= 25.0: plugs.append(["Bharat_DC001", "Type2", "Socket"])
        else: plugs.append(["CCS2", "Type2", "Bharat_DC001"])
    return pos, detour, st_power, tariff, rating, conn_count, utilization, plugs

def run_fleet_experiment():
    print(f"Simulating {N_TRIPS} trips across MP heterogeneous fleet...")
    policies = ["Nearest", "CheapestOnly", "FastestOnly", "CERCOS-TOPSIS", "CERCOS-Anchored"]
    
    # Store per-segment results
    results = {
        seg: {p: {"time": [], "cost": [], "wait": [], "gen_cost": [], "stranded": 0, "bottleneck_kw": []} for p in policies}
        for seg in FLEET
    }
    
    unreachable_trips = 0

    for _ in range(N_TRIPS):
        # Pick vehicle segment according to real registration market share
        seg_name = RNG.choice(["E2W", "E3W", "E4W"], p=[0.496, 0.476, 0.028])
        veh = FLEET[seg_name]
        
        pos, det, st_pw, tar, rat, cn, rho, plugs = generate_corridor()
        
        soc0 = RNG.uniform(0.20, 0.45)
        e0 = soc0 * veh["cap"]
        cons_real = veh["cons"] * RNG.normal(1.0, 0.08)
        
        # Reachable with 8% safety reserve
        max_dist = (e0 - 0.08 * veh["cap"]) / veh["cons"]
        
        # Filter stations by reachability and connector compatibility
        compat_mask = np.array([any(plug in veh["allowed_plugs"] for plug in station_plugs) for station_plugs in plugs])
        reach_mask = (pos + det) <= max_dist
        ok_idx = np.where(reach_mask & compat_mask)[0]
        
        if len(ok_idx) == 0:
            unreachable_trips += 1
            continue
            
        # Physical charge acceptance constraint: Eff_P = min(P_station, P_vehicle)
        eff_p = np.minimum(st_pw[ok_idx], veh["max_accept"])
        bottleneck = st_pw[ok_idx] - eff_p # power wasted/unusable
        
        # Queue model per station (M/G/c)
        service_hours = (0.40 * veh["cap"]) / np.maximum(eff_p, 1.0)
        mu = 1.0 / np.maximum(service_hours, 0.05)
        lam = rho[ok_idx] * cn[ok_idx] * mu
        
        wait_min = np.array([mgc_wq(l, m, c) * 60.0 for l, m, c in zip(lam, mu, cn[ok_idx])])
        wait_min = np.clip(wait_min, 0.0, 60.0)
        
        pred_arr_soc = (e0 - (pos[ok_idx] + det[ok_idx]) * veh["cons"]) / veh["cap"] * 100.0
        
        # Decision matrix: Detour (km), Tariff (INR/kWh), Wait (min), Eff_P (kW), Rating (1-5), Arr_SoC (%)
        X = np.c_[det[ok_idx], tar[ok_idx], wait_min, eff_p, rat[ok_idx], pred_arr_soc]
        
        # Compute choices
        w_balanced = np.array(MODES["Balanced"])
        w_cheap = np.array(MODES["Cheapest"])
        w_fast = np.array(MODES["Fastest"])
        
        c_nearest = ok_idx[np.argmin(pos[ok_idx] + det[ok_idx])]
        c_cheap = ok_idx[np.argmin(tar[ok_idx])]
        c_fast = ok_idx[np.argmax(st_pw[ok_idx])] # naive app picks highest station kW!
        c_topsis = ok_idx[np.argmax(topsis(X, w_balanced))]
        c_anchored = ok_idx[np.argmax(wsm_anchored(X, w_balanced))]
        
        decisions = {
            "Nearest": c_nearest,
            "CheapestOnly": c_cheap,
            "FastestOnly": c_fast,
            "CERCOS-TOPSIS": c_topsis,
            "CERCOS-Anchored": c_anchored
        }
        
        for p_name, st_i in decisions.items():
            # Evaluate real trip outcomes
            dist_to_st = pos[st_i] + det[st_i]
            e_arrival = e0 - dist_to_st * cons_real
            is_stranded = e_arrival < 0.03 * veh["cap"]
            
            # Energy to charge up to 80% SoC or complete remaining corridor
            dist_rem = max(0.0, CORRIDOR_KM - pos[st_i])
            energy_needed = min(veh["cap"] * 0.80 - max(e_arrival, 0.0), dist_rem * cons_real * 1.20)
            energy_needed = max(energy_needed, 0.5)
            
            p_actual = min(st_pw[st_i], veh["max_accept"])
            t_charge_min = (energy_needed / p_actual) * 60.0
            
            # Simulated realization of wait
            p_wait = erlang_c(cn[st_i], rho[st_i] * cn[st_i])
            t_wait_real = RNG.exponential(12.0) if RNG.random() < p_wait else 0.0
            t_detour_min = (2.0 * det[st_i] / 40.0) * 60.0 # 40 km/h access road
            
            total_time_min = t_charge_min + t_wait_real + t_detour_min
            charging_cost_inr = energy_needed * tar[st_i]
            gen_cost_inr = charging_cost_inr + (total_time_min / 60.0) * veh["vot"]
            
            seg_res = results[seg_name][p_name]
            seg_res["time"].append(total_time_min)
            seg_res["cost"].append(charging_cost_inr)
            seg_res["wait"].append(t_wait_real)
            seg_res["gen_cost"].append(gen_cost_inr)
            if is_stranded:
                seg_res["stranded"] += 1
            seg_res["bottleneck_kw"].append(st_pw[st_i] - p_actual)

    # Compute aggregation
    summary = {"n_trips": N_TRIPS, "unreachable_trips": unreachable_trips, "segments": {}}
    
    for seg, p_data in results.items():
        summary["segments"][seg] = {}
        base_gencost = np.mean(p_data["Nearest"]["gen_cost"])
        for p_name, vals in p_data.items():
            gc_mean = float(np.mean(vals["gen_cost"]))
            delta_inr = gc_mean - base_gencost
            pct_saving = (base_gencost - gc_mean) / base_gencost * 100.0 if base_gencost > 0 else 0.0
            summary["segments"][seg][p_name] = {
                "mean_time_min": float(np.mean(vals["time"])),
                "p90_time_min": float(np.percentile(vals["time"], 90)),
                "mean_cost_inr": float(np.mean(vals["cost"])),
                "mean_wait_min": float(np.mean(vals["wait"])),
                "mean_gen_cost_inr": gc_mean,
                "delta_gen_cost_vs_nearest": float(delta_inr),
                "cost_savings_pct": float(pct_saving),
                "stranding_rate_pct": float(vals["stranded"] / len(vals["time"]) * 100.0),
                "avg_unusable_kw": float(np.mean(vals["bottleneck_kw"]))
            }

    # Generate Figures
    os.makedirs("figures", exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    
    # FIG 4: Fleet Segment Performance Breakdown
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=False)
    colors = ["#7f8c8d", "#e67e22", "#e74c3c", "#2980b9", "#27ae60"]
    policies_list = ["Nearest", "CheapestOnly", "FastestOnly", "CERCOS-TOPSIS", "CERCOS-Anchored"]
    
    for idx, (seg, ax) in enumerate(zip(["E2W", "E3W", "E4W"], axes)):
        savings = [summary["segments"][seg][p]["cost_savings_pct"] for p in policies_list]
        bars = ax.bar(policies_list, savings, color=colors, edgecolor="black", alpha=0.85)
        ax.set_title(f"{seg} Vehicles (Share: {FLEET[seg]['share']*100:.1f}%)", fontweight="bold")
        ax.set_ylabel("Generalised Cost Savings vs Nearest (%)")
        ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f"{h:+.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3 if h >= 0 else -10), textcoords="offset points",
                        ha="center", va="bottom", fontsize=9, fontweight="bold")
                        
    fig.suptitle("Fig 4: Generalised Cost Savings across Fleet Segments (50,000 Trips, Bhopal-Ashta Corridor)", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig("figures/fig4_fleet_segment_performance.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # FIG 5: Effective Power Acceptance Bottleneck
    fig, ax = plt.subplots(figsize=(8, 4.5))
    st_kw_levels = [3.3, 7.4, 25.0, 30.0, 60.0]
    x = np.arange(len(st_kw_levels))
    width = 0.25
    
    for i, seg in enumerate(["E2W", "E3W", "E4W"]):
        v_accept = FLEET[seg]["max_accept"]
        actual_power = [min(kw, v_accept) for kw in st_kw_levels]
        ax.bar(x + (i - 1) * width, actual_power, width, label=f"{seg} (Max Accept: {v_accept} kW)")
        
    ax.set_xlabel("Advertised Station Charger Power (kW)", fontweight="bold")
    ax.set_ylabel("Effective Accepted Power (kW)", fontweight="bold")
    ax.set_title("Fig 5: Onboard Acceptance Bottleneck: Station kW vs Real Charging Draw", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{kw} kW" for kw in st_kw_levels])
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    fig.tight_layout()
    fig.savefig("figures/fig5_effective_power_bottleneck.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    with open("results_fleet_experiment.json", "w") as f:
        json.dump(summary, f, indent=2)
        
    print("Experiment 02 complete. Results saved to results_fleet_experiment.json and figures/.")
    return summary

if __name__ == "__main__":
    run_fleet_experiment()
