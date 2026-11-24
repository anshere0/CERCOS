"""TOPSIS and Min-Max WSM scoring baselines for CERCOS.

Preserved as research comparison baselines to demonstrate rank reversal and relative
ranking behavior against the production anchored WSM method.

References:
- Hwang, C.L. & Yoon, K. (1981). Multiple Attribute Decision Making: Methods and Applications.
- CERCOS Pilot Experiment (research/01_cercos_pilot_experiments.py).
"""
import numpy as np

from app.mcdm.criteria import BENEFIT_VECTOR


def topsis(
    X: np.ndarray,
    weights: np.ndarray,
    benefit: np.ndarray = BENEFIT_VECTOR,
) -> np.ndarray:
    """Vector-normalized Technique for Order Preference by Similarity to Ideal Solution (TOPSIS).

    Parameters
    ----------
    X : np.ndarray
        Decision matrix of shape (m, n).
    weights : np.ndarray
        Criteria weight vector of length n.
    benefit : np.ndarray
        Boolean array of length n (True for benefit, False for cost).

    Returns
    -------
    np.ndarray
        Relative closeness to ideal solution C_i in [0.0, 1.0].
    """
    X_arr = np.asarray(X, dtype=float)
    if X_arr.size == 0:
        return np.empty(0, dtype=float)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(1, -1)

    w = np.asarray(weights, dtype=float)

    # 1. Vector normalization
    norm = np.sqrt((X_arr**2).sum(axis=0))
    norm[norm == 0] = 1.0
    V = (X_arr / norm) * w

    # 2. Determine ideal (V+) and anti-ideal (V-) reference points
    ideal = np.where(benefit, V.max(axis=0), V.min(axis=0))
    anti = np.where(benefit, V.min(axis=0), V.max(axis=0))

    # 3. Separation measures
    sp = np.sqrt(((V - ideal) ** 2).sum(axis=1))
    sm = np.sqrt(((V - anti) ** 2).sum(axis=1))

    # 4. Relative closeness
    closeness = sm / (sp + sm + 1e-12)
    return np.clip(closeness, 0.0, 1.0)


def wsm_minmax(
    X: np.ndarray,
    weights: np.ndarray,
    benefit: np.ndarray = BENEFIT_VECTOR,
) -> np.ndarray:
    """Candidate-relative Min-Max Weighted Sum Model baseline.

    Subject to rank reversal when candidate set changes.
    """
    X_arr = np.asarray(X, dtype=float)
    if X_arr.size == 0:
        return np.empty(0, dtype=float)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(1, -1)

    mn = X_arr.min(axis=0)
    mx = X_arr.max(axis=0)
    rng = np.where(mx - mn == 0, 1.0, mx - mn)

    N = np.where(benefit, (X_arr - mn) / rng, (mx - X_arr) / rng)
    w = np.asarray(weights, dtype=float)
    return np.clip(N @ w, 0.0, 1.0)
