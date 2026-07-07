"""Gradient-boosting ensemble member with isotonic calibration.

A HistGradientBoostingClassifier (sklearn's LightGBM-style trees) predicts
1X2 from leak-free pre-match features built by replaying history in date
order: Elo, recent points/goals form and a shots-based xG proxy. Probabilities
are calibrated per class with isotonic regression fit on a held-out season,
then blended with Dixon-Coles at predict time.

Train:  python -m engine.models.ensemble
"""
from __future__ import annotations

import logging
# Security note: pickle is required to persist sklearn estimators. The file at
# MODEL_PATH is produced and consumed exclusively by this module on the local
# machine - never load an ensemble.pkl obtained from an untrusted source.
import pickle
import sys
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression

from ..config import DATA_DIR
from ..features import EloBook, load_matches

log = logging.getLogger("engine.ensemble")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

MODEL_PATH = DATA_DIR / "ensemble.pkl"

FEATURES = [
    "elo_diff", "elo_expected_home",
    "home_ppg5", "away_ppg5", "home_gd5", "away_gd5",
    "home_xgp5", "away_xgp5", "home_played", "away_played",
]

OUTCOMES = ["home", "draw", "away"]  # class order used throughout


class _FormTracker:
    """Rolling last-5 form per team, updated as history is replayed."""

    def __init__(self) -> None:
        self.results: dict[str, deque] = defaultdict(lambda: deque(maxlen=5))
        self.played: dict[str, int] = defaultdict(int)

    def features(self, team: str) -> tuple[float, float, float]:
        rows = self.results[team]
        if not rows:
            return 1.1, 0.0, 1.2  # league-average priors for unseen teams
        pts = sum(r[0] for r in rows) / len(rows)
        gd = sum(r[1] for r in rows) / len(rows)
        xgp_vals = [r[2] for r in rows if r[2] is not None]
        xgp = sum(xgp_vals) / len(xgp_vals) if xgp_vals else 1.2
        return pts, gd, xgp

    def update(self, team: str, gf: int, ga: int, xg_proxy: float | None) -> None:
        pts = 3 if gf > ga else (1 if gf == ga else 0)
        self.results[team].append((pts, gf - ga, xg_proxy))
        self.played[team] += 1


def _xg_proxy(shots, shots_target) -> float | None:
    if shots is None or shots_target is None or pd.isna(shots) or pd.isna(shots_target):
        return None
    return 0.30 * shots_target + 0.03 * (max(shots - shots_target, 0))


def build_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Replay matches chronologically; every row's features precede kickoff."""
    elo = EloBook(scope="club")
    form = _FormTracker()
    rows = []
    for r in df.itertuples():
        rows.append({
            "date": r.date, "season": r.season,
            "elo_diff": elo.get(r.home) - elo.get(r.away),
            "elo_expected_home": elo.expected_home(r.home, r.away),
            "home_ppg5": form.features(r.home)[0], "away_ppg5": form.features(r.away)[0],
            "home_gd5": form.features(r.home)[1], "away_gd5": form.features(r.away)[1],
            "home_xgp5": form.features(r.home)[2], "away_xgp5": form.features(r.away)[2],
            "home_played": min(form.played[r.home], 200), "away_played": min(form.played[r.away], 200),
            "outcome": 0 if r.home_goals > r.away_goals else (1 if r.home_goals == r.away_goals else 2),
        })
        elo.update(r.home, r.away, r.home_goals, r.away_goals)
        form.update(r.home, r.home_goals, r.away_goals,
                    _xg_proxy(r.home_shots, r.home_shots_target))
        form.update(r.away, r.away_goals, r.home_goals,
                    _xg_proxy(r.away_shots, r.away_shots_target))
    return pd.DataFrame(rows)


def train() -> dict:
    df = load_matches("club")
    frame = build_training_frame(df)
    seasons = sorted(frame["season"].dropna().unique())
    calib_season, test_season = seasons[-2], seasons[-1]

    train_mask = ~frame["season"].isin([calib_season, test_season])
    calib_mask = frame["season"] == calib_season
    test_mask = frame["season"] == test_season

    X = frame[FEATURES].to_numpy()
    y = frame["outcome"].to_numpy()

    clf = HistGradientBoostingClassifier(
        max_iter=400, learning_rate=0.06, max_depth=4,
        l2_regularization=1.0, random_state=42,
    )
    clf.fit(X[train_mask.to_numpy()], y[train_mask.to_numpy()])

    # Per-class isotonic calibration on the held-out calibration season
    raw_calib = clf.predict_proba(X[calib_mask.to_numpy()])
    y_calib = y[calib_mask.to_numpy()]
    calibrators = []
    for k in range(3):
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.01, y_max=0.97)
        iso.fit(raw_calib[:, k], (y_calib == k).astype(float))
        calibrators.append(iso)

    # Report on the untouched test season
    raw_test = clf.predict_proba(X[test_mask.to_numpy()])
    cal_test = _apply_calibration(raw_test, calibrators)
    y_test = y[test_mask.to_numpy()]
    onehot = np.eye(3)[y_test]
    metrics = {
        "test_season": test_season,
        "n_test": int(test_mask.sum()),
        "brier_raw": round(float(((raw_test - onehot) ** 2).sum(1).mean()), 4),
        "brier_calibrated": round(float(((cal_test - onehot) ** 2).sum(1).mean()), 4),
        "log_loss_calibrated": round(float(-np.log(
            np.clip((cal_test * onehot).sum(1), 1e-12, 1)).mean()), 4),
        "accuracy": round(float((cal_test.argmax(1) == y_test).mean()), 4),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as fh:
        pickle.dump({"clf": clf, "calibrators": calibrators,
                     "features": FEATURES, "metrics": metrics}, fh)
    log.info("Ensemble trained. Test-season metrics: %s", metrics)
    return metrics


def _apply_calibration(raw: np.ndarray, calibrators) -> np.ndarray:
    cal = np.column_stack([calibrators[k].predict(raw[:, k]) for k in range(3)])
    return cal / cal.sum(axis=1, keepdims=True)


_loaded: dict = {}


def predict_proba(features: dict) -> dict[str, float] | None:
    """Calibrated 1X2 probabilities, or None if no trained model exists."""
    if "bundle" not in _loaded:
        if not MODEL_PATH.exists():
            return None
        with open(MODEL_PATH, "rb") as fh:
            _loaded["bundle"] = pickle.load(fh)
    bundle = _loaded["bundle"]
    x = np.array([[features[f] for f in bundle["features"]]])
    raw = bundle["clf"].predict_proba(x)
    cal = _apply_calibration(raw, bundle["calibrators"])[0]
    return dict(zip(OUTCOMES, (round(float(p), 4) for p in cal)))


if __name__ == "__main__":
    train()
