"""Walk-forward backtesting: Brier score, log loss, calibration, betting ROI.

For each calendar month of the test period the Dixon-Coles model is refit
using only matches strictly before that month (no lookahead), then evaluated
on that month's fixtures. ROI is measured with flat stakes against Bet365
pre-match odds whenever the model's edge exceeds the value threshold.

Usage:
    python -m engine.backtest              # all leagues, last season in DB
    python -m engine.backtest E0 2425      # one league, one season
"""
from __future__ import annotations

import json
import logging
import sys

import numpy as np
import pandas as pd

from .config import LEAGUES, VALUE_EDGE_THRESHOLD
from .features import load_matches
from .models import dixon_coles
from .simulate import remove_overround, score_markets

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("engine.backtest")


def backtest_league(df: pd.DataFrame, league: str, season: str) -> dict | None:
    league_df = df[df["league"] == league]
    test = league_df[league_df["season"] == season]
    if test.empty:
        return None

    months = sorted(test["date"].str[:7].unique())
    records = []

    for month in months:
        month_start = f"{month}-01"
        train = df[(df["league"] == league) & (df["date"] < month_start)]
        if len(train) < 500:
            continue
        model = dixon_coles.fit(train)
        month_matches = test[test["date"].str[:7] == month]

        for r in month_matches.itertuples():
            if r.home not in model.attack or r.away not in model.attack:
                continue  # promoted team with no history yet this month
            markets = score_markets(model.score_matrix(r.home, r.away))
            outcome = "home" if r.home_goals > r.away_goals else (
                "draw" if r.home_goals == r.away_goals else "away")
            records.append({
                "date": r.date, "home": r.home, "away": r.away,
                "p_home": markets["home_win"], "p_draw": markets["draw"],
                "p_away": markets["away_win"], "outcome": outcome,
                "odds_home": r.odds_home, "odds_draw": r.odds_draw, "odds_away": r.odds_away,
            })

    if not records:
        return None
    return _metrics(pd.DataFrame(records), league, season)


def _metrics(res: pd.DataFrame, league: str, season: str) -> dict:
    probs = res[["p_home", "p_draw", "p_away"]].to_numpy()
    onehot = pd.get_dummies(res["outcome"])[["home", "draw", "away"]].to_numpy(dtype=float)

    brier = float(((probs - onehot) ** 2).sum(axis=1).mean())
    p_true = np.clip((probs * onehot).sum(axis=1), 1e-12, 1)
    logloss = float(-np.log(p_true).mean())
    accuracy = float((probs.argmax(axis=1) == onehot.argmax(axis=1)).mean())

    # Calibration: bin the predicted probability of every outcome option
    flat_p = probs.flatten()
    flat_hit = onehot.flatten()
    bins = np.clip((flat_p * 10).astype(int), 0, 9)
    calibration = []
    for b in range(10):
        mask = bins == b
        if mask.sum() >= 20:
            calibration.append({
                "bin": f"{b * 10}-{b * 10 + 10}%",
                "predicted_avg": round(float(flat_p[mask].mean()), 4),
                "observed_freq": round(float(flat_hit[mask].mean()), 4),
                "n": int(mask.sum()),
            })

    # Flat-stake value betting vs Bet365
    staked = returned = bets = wins = 0.0
    for r in res.itertuples():
        odds = {"home": r.odds_home, "draw": r.odds_draw, "away": r.odds_away}
        if any(o is None or pd.isna(o) for o in odds.values()):
            continue
        fair = remove_overround(odds)
        model_p = {"home": r.p_home, "draw": r.p_draw, "away": r.p_away}
        best = max(fair, key=lambda k: model_p[k] - fair[k])
        if model_p[best] - fair[best] > VALUE_EDGE_THRESHOLD:
            bets += 1
            staked += 1
            if r.outcome == best:
                returned += odds[best]
                wins += 1

    roi = (returned - staked) / staked if staked else None
    return {
        "league": LEAGUES.get(league, league),
        "season": season,
        "n_matches": len(res),
        "brier_score": round(brier, 4),
        "log_loss": round(logloss, 4),
        "accuracy": round(accuracy, 4),
        "calibration": calibration,
        "betting": {
            "value_threshold": VALUE_EDGE_THRESHOLD,
            "bets_placed": int(bets),
            "bets_won": int(wins),
            "flat_stake_roi_pct": round(roi * 100, 2) if roi is not None else None,
        },
        "baselines": {
            "brier_uniform": 0.6667,
            "brier_home_draw_away_prior": 0.63,
            "note": "Bookmaker closing odds typically achieve Brier ~0.57-0.60 on top-5 leagues.",
        },
    }


def main() -> None:
    df = load_matches("club")
    args = sys.argv[1:]
    leagues = [args[0]] if args else list(LEAGUES)
    season = args[1] if len(args) > 1 else sorted(df["season"].dropna().unique())[-1]

    results = []
    for league in leagues:
        log.info("Backtesting %s season %s ...", league, season)
        out = backtest_league(df, league, season)
        if out:
            results.append(out)
            log.info(
                "%s: Brier %.4f | log loss %.4f | acc %.1f%% | ROI %s%% on %d bets",
                out["league"], out["brier_score"], out["log_loss"],
                out["accuracy"] * 100,
                out["betting"]["flat_stake_roi_pct"], out["betting"]["bets_placed"],
            )

    out_path = "engine/data/backtest_results.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    log.info("Saved %s", out_path)


if __name__ == "__main__":
    main()
