"""Best-Worst Method (BWM) linear solver implementing Rezaei (2015, 2016) minimax model.

Solves:
    min  xi
    s.t. |w_B - a_Bj * w_j| <= xi  for all j
         |w_j - a_jW * w_W| <= xi  for all j
         sum(w_j) = 1, w_j >= 0
"""
from typing import Any

import numpy as np
from scipy.optimize import linprog

# Standard Rezaei (2015) Consistency Index (CI) table indexed by a_BW in {1..9}
CONSISTENCY_INDEX: dict[int, float] = {
    1: 0.00,
    2: 0.44,
    3: 1.00,
    4: 1.63,
    5: 2.30,
    6: 3.00,
    7: 3.73,
    8: 4.47,
    9: 5.23,
}


def solve_linear_bwm(
    criteria: list[str],
    best_criterion: str,
    worst_criterion: str,
    best_to_others: dict[str, float],
    others_to_worst: dict[str, float],
) -> dict[str, Any]:
    """Compute optimal BWM criteria weights, minimax residual xi*, and consistency ratio."""
    n = len(criteria)
    if best_criterion not in criteria or worst_criterion not in criteria:
        raise ValueError("Best and worst criteria must exist in criteria list.")

    idx_b = criteria.index(best_criterion)
    idx_w = criteria.index(worst_criterion)

    # Decision vector x = [w_0, ..., w_{n-1}, xi] (length n + 1)
    c = np.zeros(n + 1, dtype=float)
    c[-1] = 1.0  # Minimize xi

    a_ub_rows: list[np.ndarray] = []
    b_ub_vals: list[float] = []

    for j, crit in enumerate(criteria):
        a_bj = float(best_to_others.get(crit, 1.0))
        a_jw = float(others_to_worst.get(crit, 1.0))

        # w_B - a_Bj * w_j - xi <= 0  and  -w_B + a_Bj * w_j - xi <= 0
        if j != idx_b:
            r1 = np.zeros(n + 1)
            r1[idx_b] = 1.0
            r1[j] = -a_bj
            r1[-1] = -1.0
            a_ub_rows.append(r1)
            b_ub_vals.append(0.0)

            r2 = np.zeros(n + 1)
            r2[idx_b] = -1.0
            r2[j] = a_bj
            r2[-1] = -1.0
            a_ub_rows.append(r2)
            b_ub_vals.append(0.0)

        # w_j - a_jW * w_W - xi <= 0  and  -w_j + a_jW * w_W - xi <= 0
        if j != idx_w:
            r3 = np.zeros(n + 1)
            r3[j] = 1.0
            r3[idx_w] = -a_jw
            r3[-1] = -1.0
            a_ub_rows.append(r3)
            b_ub_vals.append(0.0)

            r4 = np.zeros(n + 1)
            r4[j] = -1.0
            r4[idx_w] = a_jw
            r4[-1] = -1.0
            a_ub_rows.append(r4)
            b_ub_vals.append(0.0)

    a_eq = np.ones((1, n + 1), dtype=float)
    a_eq[0, -1] = 0.0  # xi not in sum(w) = 1
    b_eq = np.array([1.0], dtype=float)

    bounds = [(0.0, 1.0)] * n + [(0.0, None)]
    res = linprog(
        c=c,
        A_ub=np.array(a_ub_rows, dtype=float),
        b_ub=np.array(b_ub_vals, dtype=float),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"BWM optimization failed: {res.message}")

    weights = {criteria[i]: round(float(res.x[i]), 6) for i in range(n)}
    xi_star = float(res.x[-1])
    a_bw = max(1, min(9, round(float(best_to_others.get(worst_criterion, 1.0)))))
    ci = CONSISTENCY_INDEX.get(a_bw, 1.0)
    cr = round(xi_star / ci, 4) if ci > 0 else 0.0

    return {
        "weights": weights,
        "xi": round(xi_star, 6),
        "consistency_ratio": cr,
    }
