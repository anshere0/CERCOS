"""Domain-anchored Weighted Sum Model (WSM) scoring for CERCOS.

Eliminates rank reversal by using fixed, domain-anchored bounds from config/criteria_bounds.yaml
instead of relative candidate min/max bounds.

Mathematical Formulation:
-------------------------
For decision matrix X in R^{m x n}, weight vector w in R^n, and bounds [lo, hi] in R^{n x 2}:

1. Clip values to domain bounds:
       X_c = clip(X, lo, hi)
2. Normalise to [0, 1]:
       N_j = (X_cj - lo_j) / (hi_j - lo_j)     if j is benefit criterion
       N_j = (hi_j - X_cj) / (hi_j - lo_j)     if j is cost criterion
3. Weighted aggregation:
       Score_i = sum_j (w_j * N_ij)

Properties:
- Proven 0.0% rank reversal under candidate addition/deletion.
- The ideal alternative (optimal on all bounds) scores exactly 1.0.
- Scores are absolute, transparent, and computationally O(m * n).
"""
import numpy as np

from app.mcdm.criteria import BENEFIT_VECTOR


def normalize_anchored(
    X: np.ndarray,
    bounds: np.ndarray,
    benefit: np.ndarray = BENEFIT_VECTOR,
) -> np.ndarray:
    """Normalize raw decision matrix using fixed domain-anchored bounds.

    Parameters
    ----------
    X : np.ndarray
        Raw decision matrix of shape (m, n) for m candidates and n criteria.
    bounds : np.ndarray
        Array of shape (n, 2) where bounds[:, 0] = lower bound and bounds[:, 1] = upper bound.
    benefit : np.ndarray
        Boolean array of length n indicating benefit criteria (True) vs cost criteria (False).

    Returns
    -------
    np.ndarray
        Normalized matrix N in [0, 1] of shape (m, n).
    """
    X_arr = np.asarray(X, dtype=float)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(1, -1)

    bounds_arr = np.asarray(bounds, dtype=float)
    lo = bounds_arr[:, 0]
    hi = bounds_arr[:, 1]

    span = hi - lo
    span = np.where(span == 0, 1.0, span)

    Xc = np.clip(X_arr, lo, hi)
    normalized = np.where(benefit, (Xc - lo) / span, (hi - Xc) / span)
    return np.clip(normalized, 0.0, 1.0)


def wsm_anchored(
    X: np.ndarray,
    weights: np.ndarray,
    bounds: np.ndarray,
    benefit: np.ndarray = BENEFIT_VECTOR,
) -> np.ndarray:
    """Compute composite preference scores using domain-anchored Weighted Sum Model.

    Parameters
    ----------
    X : np.ndarray
        Raw decision matrix of shape (m, n).
    weights : np.ndarray
        Criteria weight vector of length n, summing to 1.0.
    bounds : np.ndarray
        Fixed domain bounds of shape (n, 2).
    benefit : np.ndarray, default=BENEFIT_VECTOR
        Boolean indicator vector of length n for benefit vs cost criteria.

    Returns
    -------
    np.ndarray
        Composite score vector of length m with values in [0.0, 1.0].
    """
    X_arr = np.asarray(X, dtype=float)
    if X_arr.size == 0:
        return np.empty(0, dtype=float)

    N = normalize_anchored(X_arr, bounds, benefit)
    w = np.asarray(weights, dtype=float)
    scores = N @ w
    return np.clip(scores, 0.0, 1.0)
