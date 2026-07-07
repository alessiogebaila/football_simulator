"""Feature engineering: Elo ratings and recent-form summaries."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

from .config import (
    ELO_FRIENDLY_DAMP,
    ELO_HOME_ADV,
    ELO_K_CLUB,
    ELO_K_INTERNATIONAL,
    ELO_START,
)
from .db import get_conn


@dataclass
class EloBook:
    """Incremental Elo ratings over a chronological match stream."""

    scope: str = "club"
    ratings: dict[str, float] = field(default_factory=dict)
    played: dict[str, int] = field(default_factory=dict)

    def get(self, team: str) -> float:
        return self.ratings.get(team, ELO_START)

    def expected_home(self, home: str, away: str, neutral: bool = False) -> float:
        adv = 0.0 if neutral else ELO_HOME_ADV
        return 1.0 / (1.0 + 10 ** ((self.get(away) - self.get(home) - adv) / 400.0))

    def update(self, home: str, away: str, hg: int, ag: int,
               neutral: bool = False, friendly: bool = False) -> None:
        exp_home = self.expected_home(home, away, neutral)
        result = 1.0 if hg > ag else (0.5 if hg == ag else 0.0)
        k = ELO_K_CLUB if self.scope == "club" else ELO_K_INTERNATIONAL
        if friendly:
            k *= ELO_FRIENDLY_DAMP
        # Goal-margin multiplier (FiveThirtyEight-style): bigger wins move
        # ratings more, tempered when the favourite wins as expected.
        margin = abs(hg - ag)
        adv = 0.0 if neutral else ELO_HOME_ADV
        if result == 1.0:
            winner_diff = self.get(home) + adv - self.get(away)
        elif result == 0.0:
            winner_diff = self.get(away) - self.get(home) - adv
        else:
            winner_diff = 0.0
        mult = math.log(max(margin, 1) + 1.0) * (2.2 / (max(winner_diff, 0.0) * 0.001 + 2.2))
        delta = k * mult * (result - exp_home)
        self.ratings[home] = self.get(home) + delta
        self.ratings[away] = self.get(away) - delta
        self.played[home] = self.played.get(home, 0) + 1
        self.played[away] = self.played.get(away, 0) + 1


def load_matches(scope: str) -> pd.DataFrame:
    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM matches WHERE scope = ? ORDER BY date", conn, params=(scope,)
        )
    return df


def build_elo(scope: str = "club", persist: bool = True) -> EloBook:
    """Replay all stored matches chronologically to produce current Elo ratings."""
    df = load_matches(scope)
    book = EloBook(scope=scope)
    for r in df.itertuples():
        book.update(
            r.home, r.away, r.home_goals, r.away_goals,
            neutral=bool(r.neutral), friendly=(r.league == "Friendly"),
        )
    if persist and not df.empty:
        last_dates = {}
        for r in df.itertuples():
            last_dates[r.home] = r.date
            last_dates[r.away] = r.date
        with get_conn() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO elo_ratings VALUES (?,?,?,?,?)",
                [
                    (scope, team, rating, book.played.get(team, 0), last_dates.get(team))
                    for team, rating in book.ratings.items()
                ],
            )
    return book


def recent_form(df: pd.DataFrame, team: str, n: int = 10) -> dict:
    """Summarise a team's last n matches: results, goals, shots-based xG proxy."""
    mask = (df["home"] == team) | (df["away"] == team)
    recent = df[mask].tail(n)
    if recent.empty:
        return {"matches": 0}

    pts, gf, ga, xg_for, xg_against = [], 0, 0, [], []
    for r in recent.itertuples():
        is_home = r.home == team
        goals_for = r.home_goals if is_home else r.away_goals
        goals_against = r.away_goals if is_home else r.home_goals
        gf += goals_for
        ga += goals_against
        pts.append(3 if goals_for > goals_against else (1 if goals_for == goals_against else 0))
        # Shots-on-target based xG proxy (~0.30 xG per SoT, ~0.03 per off-target shot)
        st_for = r.home_shots_target if is_home else r.away_shots_target
        st_ag = r.away_shots_target if is_home else r.home_shots_target
        s_for = r.home_shots if is_home else r.away_shots
        s_ag = r.away_shots if is_home else r.home_shots
        if st_for is not None and s_for is not None and not pd.isna(st_for) and not pd.isna(s_for):
            xg_for.append(0.30 * st_for + 0.03 * (s_for - st_for))
            xg_against.append(0.30 * st_ag + 0.03 * (s_ag - st_ag))

    out = {
        "matches": len(recent),
        "points": sum(pts),
        "ppg": round(sum(pts) / len(recent), 2),
        "goals_for": int(gf),
        "goals_against": int(ga),
        "form_string": "".join("W" if p == 3 else ("D" if p == 1 else "L") for p in pts),
    }
    if xg_for:
        out["xg_for_avg"] = round(sum(xg_for) / len(xg_for), 2)
        out["xg_against_avg"] = round(sum(xg_against) / len(xg_against), 2)
    return out


def team_tendencies(df: pd.DataFrame, team: str, n: int = 30) -> dict:
    """Per-match averages for corners, fouls and cards (for/against) over last n."""
    mask = (df["home"] == team) | (df["away"] == team)
    recent = df[mask].tail(n)
    stats = {"corners_for": [], "corners_against": [], "fouls": [], "yellows": [], "reds": []}
    for r in recent.itertuples():
        is_home = r.home == team
        pairs = {
            "corners_for": r.home_corners if is_home else r.away_corners,
            "corners_against": r.away_corners if is_home else r.home_corners,
            "fouls": r.home_fouls if is_home else r.away_fouls,
            "yellows": r.home_yellows if is_home else r.away_yellows,
            "reds": r.home_reds if is_home else r.away_reds,
        }
        for key, val in pairs.items():
            if val is not None and not pd.isna(val):
                stats[key].append(float(val))
    return {k: (round(sum(v) / len(v), 2) if v else None) for k, v in stats.items()}
