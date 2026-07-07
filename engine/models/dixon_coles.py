"""Time-weighted Dixon-Coles (1997) model for scoreline probabilities.

Each team gets an attack and a defence parameter; a global home-advantage
multiplier and the low-score dependence parameter rho complete the model.
Match likelihoods are exponentially down-weighted with age so the fit tracks
current strength rather than five-year-old form.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

from ..config import DC_HALF_LIFE_DAYS, DC_MAX_GOALS


def _tau(hg: np.ndarray, ag: np.ndarray, lam: np.ndarray, mu: np.ndarray, rho: float) -> np.ndarray:
    """Dixon-Coles low-score correction factor."""
    tau = np.ones_like(lam)
    m00 = (hg == 0) & (ag == 0)
    m01 = (hg == 0) & (ag == 1)
    m10 = (hg == 1) & (ag == 0)
    m11 = (hg == 1) & (ag == 1)
    tau[m00] = 1 - lam[m00] * mu[m00] * rho
    tau[m01] = 1 + lam[m01] * rho
    tau[m10] = 1 + mu[m10] * rho
    tau[m11] = 1 - rho
    return np.clip(tau, 1e-10, None)


@dataclass
class DixonColesModel:
    teams: list[str]
    attack: dict[str, float]
    defence: dict[str, float]
    home_adv: float
    rho: float
    league_avg_goals: float

    def rates(self, home: str, away: str, neutral: bool = False) -> tuple[float, float]:
        """Expected goals (Poisson rates) for a fixture."""
        ha = 0.0 if neutral else self.home_adv
        lam = math.exp(self.attack[home] + self.defence[away] + ha)
        mu = math.exp(self.attack[away] + self.defence[home])
        return lam, mu

    def score_matrix(self, home: str, away: str, neutral: bool = False,
                     max_goals: int = DC_MAX_GOALS) -> np.ndarray:
        lam, mu = self.rates(home, away, neutral)
        goals = np.arange(max_goals + 1)
        matrix = np.outer(poisson.pmf(goals, lam), poisson.pmf(goals, mu))
        # Apply rho correction to the 2x2 low-score block
        matrix[0, 0] *= 1 - lam * mu * self.rho
        matrix[0, 1] *= 1 + lam * self.rho
        matrix[1, 0] *= 1 + mu * self.rho
        matrix[1, 1] *= 1 - self.rho
        return matrix / matrix.sum()


def fit(df: pd.DataFrame, as_of: str | None = None) -> DixonColesModel:
    """Fit on a dataframe with columns date, home, away, home_goals, away_goals.

    `as_of` (ISO date) fits using only prior matches - required for honest
    backtesting without lookahead leakage.
    """
    if as_of:
        df = df[df["date"] < as_of]
    df = df.copy()
    teams = sorted(set(df["home"]) | set(df["away"]))
    idx = {t: i for i, t in enumerate(teams)}
    n = len(teams)

    ref_date = pd.to_datetime(as_of if as_of else df["date"].max())
    age_days = (ref_date - pd.to_datetime(df["date"])).dt.days.to_numpy(dtype=float)
    weights = np.exp(-math.log(2) * age_days / DC_HALF_LIFE_DAYS)

    hi = df["home"].map(idx).to_numpy()
    ai = df["away"].map(idx).to_numpy()
    hg = df["home_goals"].to_numpy(dtype=float)
    ag = df["away_goals"].to_numpy(dtype=float)
    neutral = df["neutral"].to_numpy(dtype=float) if "neutral" in df else np.zeros(len(df))

    # Parameters: attack[n], defence[n], home_adv, rho
    x0 = np.concatenate([np.zeros(n), np.zeros(n), [0.25, -0.05]])

    def nll(params: np.ndarray) -> float:
        atk, dfn = params[:n], params[n:2 * n]
        home_adv, rho = params[-2], params[-1]
        lam = np.exp(atk[hi] + dfn[ai] + home_adv * (1 - neutral))
        mu = np.exp(atk[ai] + dfn[hi])
        ll = (
            weights
            * (
                hg * np.log(lam) - lam
                + ag * np.log(mu) - mu
                + np.log(_tau(hg, ag, lam, mu, rho))
            )
        ).sum()
        # Identifiability: attack params sum to zero (soft constraint)
        return -ll + 1000.0 * atk.sum() ** 2

    res = minimize(nll, x0, method="L-BFGS-B", options={"maxiter": 300})
    atk, dfn = res.x[:n], res.x[n:2 * n]
    avg_goals = float((hg.sum() + ag.sum()) / len(df))
    return DixonColesModel(
        teams=teams,
        attack={t: float(atk[idx[t]]) for t in teams},
        defence={t: float(dfn[idx[t]]) for t in teams},
        home_adv=float(res.x[-2]),
        rho=float(res.x[-1]),
        league_avg_goals=avg_goals,
    )
