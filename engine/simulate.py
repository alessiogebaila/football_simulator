"""Monte Carlo match simulation on top of a Dixon-Coles score matrix.

Score-derived markets (1X2, exact score, totals, BTTS) come straight from the
analytic score matrix - it is exact, so no sampling noise. Monte Carlo is used
for the secondary markets (corners, fouls, cards) where outcomes correlate
with the run of play.
"""
from __future__ import annotations

import numpy as np

from .config import N_SIMS


def score_markets(matrix: np.ndarray) -> dict:
    """1X2, totals, BTTS and most likely scorelines from the score matrix."""
    home_win = float(np.tril(matrix, -1).sum())
    draw = float(np.trace(matrix))
    away_win = float(np.triu(matrix, 1).sum())

    n = matrix.shape[0]
    totals = {}
    goals_grid = np.add.outer(np.arange(n), np.arange(n))
    for line in (1.5, 2.5, 3.5):
        totals[f"over_{line}"] = float(matrix[goals_grid > line].sum())
        totals[f"under_{line}"] = float(matrix[goals_grid < line].sum())

    btts = float(matrix[1:, 1:].sum())

    flat = [
        {"score": f"{h}-{a}", "probability": round(float(matrix[h, a]), 4)}
        for h in range(min(6, n))
        for a in range(min(6, n))
    ]
    flat.sort(key=lambda s: -s["probability"])

    return {
        "home_win": round(home_win, 4),
        "draw": round(draw, 4),
        "away_win": round(away_win, 4),
        "totals": {k: round(v, 4) for k, v in totals.items()},
        "btts_yes": round(btts, 4),
        "btts_no": round(1 - btts, 4),
        "top_scorelines": flat[:8],
    }


def _neg_binomial(rng: np.random.Generator, mean: float, dispersion: float, size: int) -> np.ndarray:
    """Sample counts with variance = mean * dispersion (Poisson if ~1)."""
    if mean <= 0:
        return np.zeros(size)
    if dispersion <= 1.01:
        return rng.poisson(mean, size)
    p = 1.0 / dispersion
    r = mean * p / (1 - p)
    return rng.negative_binomial(r, p, size)


def monte_carlo(
    lam: float,
    mu: float,
    home_corners_exp: float,
    away_corners_exp: float,
    home_fouls_exp: float,
    away_fouls_exp: float,
    home_yellows_exp: float,
    away_yellows_exp: float,
    n_sims: int = N_SIMS,
    seed: int | None = None,
) -> dict:
    """Simulate secondary markets, correlating them with attacking dominance."""
    rng = np.random.default_rng(seed)

    hg = rng.poisson(lam, n_sims)
    ag = rng.poisson(mu, n_sims)

    # Corner counts scale mildly with each side's share of attacking output.
    dominance = lam / max(lam + mu, 1e-9)
    hc = _neg_binomial(rng, home_corners_exp * (0.8 + 0.4 * dominance), 1.6, n_sims)
    ac = _neg_binomial(rng, away_corners_exp * (0.8 + 0.4 * (1 - dominance)), 1.6, n_sims)

    hf = _neg_binomial(rng, home_fouls_exp, 1.3, n_sims)
    af = _neg_binomial(rng, away_fouls_exp, 1.3, n_sims)
    hy = rng.poisson(home_yellows_exp, n_sims)
    ay = rng.poisson(away_yellows_exp, n_sims)

    tc = hc + ac
    return {
        "n_sims": n_sims,
        "corners": {
            "home_avg": round(float(hc.mean()), 2),
            "away_avg": round(float(ac.mean()), 2),
            "total_avg": round(float(tc.mean()), 2),
            "over_8_5": round(float((tc > 8.5).mean()), 4),
            "over_9_5": round(float((tc > 9.5).mean()), 4),
            "over_10_5": round(float((tc > 10.5).mean()), 4),
        },
        "fouls": {
            "home_avg": round(float(hf.mean()), 2),
            "away_avg": round(float(af.mean()), 2),
            "total_avg": round(float((hf + af).mean()), 2),
        },
        "cards": {
            "home_yellows_avg": round(float(hy.mean()), 2),
            "away_yellows_avg": round(float(ay.mean()), 2),
            "total_yellows_avg": round(float((hy + ay).mean()), 2),
            "over_3_5_yellows": round(float(((hy + ay) > 3.5).mean()), 4),
        },
        "sampled_goal_check": {
            "home_xg_realised": round(float(hg.mean()), 2),
            "away_xg_realised": round(float(ag.mean()), 2),
        },
    }


def remove_overround(odds: dict[str, float]) -> dict[str, float]:
    """Convert bookmaker odds to fair probabilities (proportional de-vig)."""
    implied = {k: 1.0 / v for k, v in odds.items() if v and v > 1.0}
    total = sum(implied.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in implied.items()}
