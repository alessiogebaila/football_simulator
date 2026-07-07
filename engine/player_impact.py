"""Lineup-aware team strength adjustment.

Uses the Transfermarkt squad file already in the repo. A confirmed starting XI
is compared against the club's strongest available XI (by market value, the
best public proxy for player quality). Missing key players weaken the relevant
unit: outfield attackers scale the team's own xG, defenders and the keeper
scale the opponent's xG.
"""
from __future__ import annotations

import logging
import math
import unicodedata
from functools import lru_cache
from pathlib import Path

import pandas as pd

log = logging.getLogger("engine.player_impact")

SQUAD_CSV = Path(__file__).resolve().parent.parent / "final_transfermarkt_squads.csv"

ATTACK_POS = {"ST", "CF", "LW", "RW", "CAM", "SS"}
MID_POS = {"CM", "CDM", "LM", "RM"}
DEF_POS = {"CB", "LB", "RB", "LWB", "RWB"}

# How strongly a unit's quality gap moves goals (exponents on the value ratio)
ATTACK_ELASTICITY = 0.35
DEFENCE_ELASTICITY = 0.30
GK_ELASTICITY = 0.15
MAX_SWING = 0.25  # cap total adjustment at +-25%


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).casefold().strip()


@lru_cache(maxsize=1)
def _squads() -> dict[str, pd.DataFrame]:
    if not SQUAD_CSV.exists():
        log.warning("Squad file not found: %s", SQUAD_CSV)
        return {}
    df = pd.read_csv(SQUAD_CSV).dropna(subset=["player_name", "club", "position"])
    df["market_value_eur"] = pd.to_numeric(df["market_value_eur"], errors="coerce").fillna(1e5)
    return {club: g.reset_index(drop=True) for club, g in df.groupby("club")}


def resolve_club(name: str) -> str | None:
    squads = _squads()
    if name in squads:
        return name
    normed = {_norm(c): c for c in squads}
    if _norm(name) in normed:
        return normed[_norm(name)]
    hits = [c for n, c in normed.items() if n in _norm(name) or _norm(name) in n]
    return hits[0] if len(hits) == 1 else None


def _unit(pos: str) -> str:
    if pos == "GK":
        return "gk"
    if pos in DEF_POS:
        return "def"
    if pos in ATTACK_POS:
        return "att"
    return "mid"


def _unit_values(players: pd.DataFrame) -> dict[str, float]:
    """Log-value strength per unit (log tempers superstar outliers)."""
    out = {"gk": 0.0, "def": 0.0, "mid": 0.0, "att": 0.0}
    for r in players.itertuples():
        out[_unit(str(r.position))] += math.log1p(float(r.market_value_eur) / 1e6)
    return out


def _best_xi(squad: pd.DataFrame) -> pd.DataFrame:
    """Strongest plausible XI by market value in a 1-4-3-3-ish shape."""
    squad = squad.sort_values("market_value_eur", ascending=False)
    picks, counts = [], {"gk": 0, "def": 0, "mid": 0, "att": 0}
    limits = {"gk": 1, "def": 4, "mid": 3, "att": 3}
    for idx, r in squad.iterrows():
        u = _unit(str(r["position"]))
        if counts[u] < limits[u]:
            picks.append(idx)
            counts[u] += 1
        if len(picks) == 11:
            break
    return squad.loc[picks]


def lineup_factors(club: str, lineup_names: list[str]) -> dict | None:
    """Compare a confirmed lineup with the club's best XI.

    Returns unit multipliers (own attack; opponent-facing defence/gk) plus the
    key absentees, or None when the club is unknown.
    """
    resolved = resolve_club(club)
    if resolved is None:
        return None
    squad = _squads()[resolved]

    normed_lineup = {_norm(n) for n in lineup_names}
    squad_norm = squad.assign(_n=squad["player_name"].map(_norm))
    chosen = squad_norm[squad_norm["_n"].isin(normed_lineup)]
    # Also match "last name only" entries from the UI
    if len(chosen) < len(lineup_names):
        last = {n.split()[-1] for n in normed_lineup if n}
        chosen = squad_norm[
            squad_norm["_n"].isin(normed_lineup)
            | squad_norm["_n"].str.split().str[-1].isin(last)
        ]
    matched = int(len(chosen))
    if matched < 7:
        return {"matched_players": matched, "reliable": False}

    best = _best_xi(squad)
    best_units = _unit_values(best)
    line_units = _unit_values(chosen)

    def ratio(unit: str, elasticity: float) -> float:
        if best_units[unit] <= 0:
            return 1.0
        raw = (max(line_units[unit], 0.1) / best_units[unit]) ** elasticity
        return max(1 - MAX_SWING, min(raw, 1 + MAX_SWING / 2))

    # Midfield counts half toward attack, half toward defence
    att = ratio("att", ATTACK_ELASTICITY) * ratio("mid", ATTACK_ELASTICITY / 2)
    dfn = ratio("def", DEFENCE_ELASTICITY) * ratio("mid", DEFENCE_ELASTICITY / 2)
    gk = ratio("gk", GK_ELASTICITY)

    missing = best[~best["player_name"].map(_norm).isin(set(chosen["_n"]))]
    absentees = [
        {"name": r.player_name, "position": r.position,
         "market_value_eur": float(r.market_value_eur)}
        for r in missing.itertuples()
    ]

    return {
        "reliable": True,
        "matched_players": matched,
        "attack_factor": round(att, 3),
        "defence_factor": round(dfn, 3),
        "gk_factor": round(gk, 3),
        "key_absentees": sorted(absentees, key=lambda a: -a["market_value_eur"])[:4],
    }


def adjust_rates(lam: float, mu: float,
                 home_factors: dict | None, away_factors: dict | None) -> tuple[float, float]:
    """Apply lineup factors: own attack scales own xG; defence+GK scale opponent xG."""
    if home_factors and home_factors.get("reliable"):
        lam *= home_factors["attack_factor"]
        mu /= max(home_factors["defence_factor"] * home_factors["gk_factor"], 1 - MAX_SWING)
    if away_factors and away_factors.get("reliable"):
        mu *= away_factors["attack_factor"]
        lam /= max(away_factors["defence_factor"] * away_factors["gk_factor"], 1 - MAX_SWING)
    return lam, mu
