"""Prediction orchestrator: strengths -> xG -> markets -> value bets.

Club fixtures within one league use that league's Dixon-Coles fit directly.
Cross-league fixtures (e.g. Champions League pairings) combine each team's
own-league parameters with a fixed league-strength offset and are flagged with
lower confidence: the five domestic datasets never play each other, so
cross-league strength is a prior, not an estimate.
"""
from __future__ import annotations

import json
import math
from datetime import date

import pandas as pd

from . import player_impact
from .config import LEAGUES, VALUE_EDGE_THRESHOLD
from .db import get_conn
from .features import build_elo, load_matches, recent_form, team_tendencies
from .models import dixon_coles
from .models import ensemble as ensemble_model
from .simulate import monte_carlo, remove_overround, score_markets

# Dixon-Coles vs calibrated GBM weight in the blended 1X2
DC_BLEND_WEIGHT = 0.55

# Log-goal-space league strength priors (roughly UEFA-coefficient shaped).
LEAGUE_STRENGTH = {"E0": 0.10, "SP1": 0.04, "I1": 0.02, "D1": 0.00, "F1": -0.08}

# League-average fallbacks when a team has no stats history
DEFAULTS = {"corners": 5.0, "fouls": 11.5, "yellows": 2.0}

# App/common team names -> football-data.co.uk names
TEAM_ALIASES = {
    "manchester city": "Man City",
    "manchester united": "Man United",
    "ac milan": "Milan",
    "inter milan": "Inter",
    "internazionale": "Inter",
    "psg": "Paris SG",
    "paris saint-germain": "Paris SG",
    "atletico madrid": "Ath Madrid",
    "atlético madrid": "Ath Madrid",
    "bayern": "Bayern Munich",
    "fc bayern munich": "Bayern Munich",
    "borussia dortmund": "Dortmund",
    "tottenham hotspur": "Tottenham",
    "as roma": "Roma",
    "fc barcelona": "Barcelona",
    "newcastle united": "Newcastle",
    "bayer leverkusen": "Leverkusen",
}


def resolve_team(name: str, known_teams: set[str]) -> str | None:
    """Map an app-side team name onto a football-data.co.uk team name."""
    if name in known_teams:
        return name
    alias = TEAM_ALIASES.get(name.casefold())
    if alias and alias in known_teams:
        return alias
    lowered = {t.casefold(): t for t in known_teams}
    if name.casefold() in lowered:
        return lowered[name.casefold()]
    # Last resort: unique substring match ("Real Madrid CF" -> "Real Madrid")
    hits = [t for low, t in lowered.items() if low in name.casefold() or name.casefold() in low]
    return hits[0] if len(hits) == 1 else None

_cache: dict = {}


def _club_models() -> tuple[dict, pd.DataFrame]:
    if "club" not in _cache:
        df = load_matches("club")
        models = {
            code: dixon_coles.fit(df[df["league"] == code])
            for code in LEAGUES
            if not df[df["league"] == code].empty
        }
        _cache["club"] = (models, df)
    return _cache["club"]


def _intl_model() -> tuple[dixon_coles.DixonColesModel, pd.DataFrame]:
    if "intl" not in _cache:
        df = load_matches("international")
        _cache["intl"] = (dixon_coles.fit(df), df)
    return _cache["intl"]


def _elo(scope: str):
    key = f"elo-{scope}"
    if key not in _cache:
        _cache[key] = build_elo(scope, persist=True)
    return _cache[key]


def invalidate_cache() -> None:
    _cache.clear()


def team_league(team: str, models: dict) -> str | None:
    for code, model in models.items():
        if team in model.teams:
            return code
    return None


def list_teams() -> dict:
    models, _ = _club_models()
    intl, _ = _intl_model()
    return {
        "club": {LEAGUES[c]: sorted(m.teams) for c, m in models.items()},
        "international": sorted(intl.teams),
    }


def _club_rates(home: str, away: str, neutral: bool) -> tuple[float, float, dict]:
    models, _ = _club_models()
    known = {t for m in models.values() for t in m.teams}
    resolved_home, resolved_away = resolve_team(home, known), resolve_team(away, known)
    if resolved_home is None or resolved_away is None:
        missing = home if resolved_home is None else away
        raise KeyError(f"Team '{missing}' not found in club match data")
    home, away = resolved_home, resolved_away
    hl, al = team_league(home, models), team_league(away, models)

    if hl == al:
        lam, mu = models[hl].rates(home, away, neutral)
        return lam, mu, {"cross_league": False, "league": LEAGUES[hl]}

    mh, ma = models[hl], models[al]
    strength_gap = LEAGUE_STRENGTH[hl] - LEAGUE_STRENGTH[al]
    home_adv = 0.0 if neutral else (mh.home_adv + ma.home_adv) / 2
    lam = math.exp(mh.attack[home] + ma.defence[away] + home_adv + strength_gap)
    mu = math.exp(ma.attack[away] + mh.defence[home] - strength_gap)
    return lam, mu, {
        "cross_league": True,
        "league": f"{LEAGUES[hl]} vs {LEAGUES[al]}",
        "league_strength_gap": round(strength_gap, 3),
    }


def _ensemble_features(df, home: str, away: str, elo) -> dict:
    """Pre-match features matching engine.models.ensemble.FEATURES."""
    feats = {
        "elo_diff": elo.get(home) - elo.get(away),
        "elo_expected_home": elo.expected_home(home, away),
    }
    for side, team in (("home", home), ("away", away)):
        form = recent_form(df, team, n=5)
        n = max(form.get("matches", 0), 1)
        feats[f"{side}_ppg5"] = form.get("ppg", 1.1)
        feats[f"{side}_gd5"] = (form.get("goals_for", 0) - form.get("goals_against", 0)) / n
        feats[f"{side}_xgp5"] = form.get("xg_for_avg", 1.2)
        mask = (df["home"] == team) | (df["away"] == team)
        feats[f"{side}_played"] = min(int(mask.sum()), 200)
    return feats


def _reweight_matrix(matrix, target: dict):
    """Scale the H/D/A regions of the score matrix to match blended 1X2."""
    import numpy as np

    current = {
        "home": np.tril(matrix, -1).sum(),
        "draw": np.trace(matrix),
        "away": np.triu(matrix, 1).sum(),
    }
    out = matrix.copy()
    n = matrix.shape[0]
    tri_low = np.tril(np.ones((n, n)), -1).astype(bool)
    tri_up = np.triu(np.ones((n, n)), 1).astype(bool)
    eye = np.eye(n, dtype=bool)
    for region, key in ((tri_low, "home"), (eye, "draw"), (tri_up, "away")):
        if current[key] > 1e-12:
            out[region] *= target[key] / current[key]
    return out / out.sum()


def predict_match(
    home: str,
    away: str,
    scope: str = "club",
    neutral: bool = False,
    bookmaker_odds: dict | None = None,
    home_lineup: list[str] | None = None,
    away_lineup: list[str] | None = None,
) -> dict:
    """Full probabilistic prediction for one fixture."""
    if scope == "international":
        model, df = _intl_model()
        resolved = [resolve_team(t, set(model.teams)) for t in (home, away)]
        for original, res in zip((home, away), resolved):
            if res is None:
                raise KeyError(f"Team '{original}' not found in international match data")
        home, away = resolved
        lam, mu = model.rates(home, away, neutral)
        context = {"cross_league": False, "league": "International"}
        rho = model.rho
    else:
        models, df = _club_models()
        known = {t for m in models.values() for t in m.teams}
        home = resolve_team(home, known) or home
        away = resolve_team(away, known) or away
        lam, mu, context = _club_rates(home, away, neutral)
        rho = models[team_league(home, models)].rho

    # Confirmed-lineup adjustment (club squads only)
    lineup_info = {}
    home_factors = away_factors = None
    if scope == "club":
        if home_lineup:
            home_factors = player_impact.lineup_factors(home, home_lineup)
            lineup_info["home"] = home_factors
        if away_lineup:
            away_factors = player_impact.lineup_factors(away, away_lineup)
            lineup_info["away"] = away_factors
        lam, mu = player_impact.adjust_rates(lam, mu, home_factors, away_factors)

    # Cap rates to a sane range; extreme mismatches otherwise explode
    lam, mu = min(lam, 4.5), min(mu, 4.5)

    # Score matrix with DC low-score correction
    import numpy as np
    from scipy.stats import poisson

    goals = np.arange(11)
    matrix = np.outer(poisson.pmf(goals, lam), poisson.pmf(goals, mu))
    matrix[0, 0] *= 1 - lam * mu * rho
    matrix[0, 1] *= 1 + lam * rho
    matrix[1, 0] *= 1 + mu * rho
    matrix[1, 1] *= 1 - rho
    matrix /= matrix.sum()

    markets = score_markets(matrix)

    # Blend calibrated GBM ensemble with Dixon-Coles (club scope only)
    elo = _elo(scope)
    ensemble_probs = None
    if scope == "club":
        ensemble_probs = ensemble_model.predict_proba(
            _ensemble_features(df, home, away, elo)
        )
    if ensemble_probs:
        blended = {
            "home": DC_BLEND_WEIGHT * markets["home_win"] + (1 - DC_BLEND_WEIGHT) * ensemble_probs["home"],
            "draw": DC_BLEND_WEIGHT * markets["draw"] + (1 - DC_BLEND_WEIGHT) * ensemble_probs["draw"],
            "away": DC_BLEND_WEIGHT * markets["away_win"] + (1 - DC_BLEND_WEIGHT) * ensemble_probs["away"],
        }
        total = sum(blended.values())
        blended = {k: v / total for k, v in blended.items()}
        matrix = _reweight_matrix(matrix, blended)
        markets = score_markets(matrix)

    # Form, momentum, tendencies
    home_form = recent_form(df, home)
    away_form = recent_form(df, away)
    home_tend = team_tendencies(df, home)
    away_tend = team_tendencies(df, away)

    mc = monte_carlo(
        lam, mu,
        home_tend.get("corners_for") or DEFAULTS["corners"],
        away_tend.get("corners_for") or DEFAULTS["corners"],
        home_tend.get("fouls") or DEFAULTS["fouls"],
        away_tend.get("fouls") or DEFAULTS["fouls"],
        home_tend.get("yellows") or DEFAULTS["yellows"],
        away_tend.get("yellows") or DEFAULTS["yellows"],
    )

    # Elo context (independent strength check on the DC estimate)
    elo_home, elo_away = elo.get(home), elo.get(away)
    elo_exp = elo.expected_home(home, away, neutral)

    # Confidence: agreement between Elo and DC, data volume, cross-league penalty
    dc_home_noloss = markets["home_win"] / max(markets["home_win"] + markets["away_win"], 1e-9)
    agreement = 1.0 - min(abs(elo_exp - dc_home_noloss) * 2.0, 1.0)
    data_score = min((home_form.get("matches", 0) + away_form.get("matches", 0)) / 20.0, 1.0)
    confidence = 0.5 * agreement + 0.35 * data_score + 0.15
    if context.get("cross_league"):
        confidence *= 0.75
    confidence = round(min(confidence, 0.95), 2)

    warnings = []
    if context.get("cross_league"):
        warnings.append(
            "Cross-league fixture: relative league strength is a prior, not "
            "estimated from head-to-head data."
        )
    if home_form.get("matches", 0) < 5 or away_form.get("matches", 0) < 5:
        warnings.append("Limited recent match data for at least one team.")
    lineups_applied = bool(
        (home_factors or {}).get("reliable") and (away_factors or {}).get("reliable")
    )
    if lineups_applied:
        confidence = round(min(confidence + 0.03, 0.97), 2)
    else:
        warnings.append("Lineups not confirmed: player-availability adjustment not applied.")
    for side, factors in (("home", home_factors), ("away", away_factors)):
        if factors and not factors.get("reliable"):
            warnings.append(
                f"Could not match enough {side} lineup names to squad data "
                f"({factors.get('matched_players', 0)}/11) - lineup ignored."
            )
    if ensemble_probs is None and scope == "club":
        warnings.append(
            "GBM ensemble not trained (run: python -m engine.models.ensemble) - "
            "Dixon-Coles only."
        )

    result = {
        "match": f"{home} vs {away}",
        "scope": scope,
        "as_of": date.today().isoformat(),
        "context": context,
        "predicted_xg": {"home": round(lam, 2), "away": round(mu, 2)},
        "xg_uncertainty": {
            "home_range": [round(max(lam - 0.35, 0.1), 2), round(lam + 0.35, 2)],
            "away_range": [round(max(mu - 0.35, 0.1), 2), round(mu + 0.35, 2)],
        },
        "probabilities": markets,
        "secondary_markets": mc,
        "elo": {
            "home": round(elo_home), "away": round(elo_away),
            "home_expected_score": round(elo_exp, 3),
        },
        "model_components": {
            "dixon_coles_weight": DC_BLEND_WEIGHT if ensemble_probs else 1.0,
            "ensemble_1x2": ensemble_probs,
            "lineups_applied": lineups_applied,
        },
        "lineup_analysis": lineup_info or None,
        "form": {"home": home_form, "away": away_form},
        "key_reasons": _key_reasons(home, away, lam, mu, elo_home, elo_away,
                                    home_form, away_form, neutral, context),
        "confidence": confidence,
        "warnings": warnings,
        "disclaimer": (
            "Probabilistic estimate, not a guarantee. If you bet, bet only what "
            "you can afford to lose - and be aware most bettors lose long-term."
        ),
    }

    for side_team, factors in ((home, home_factors), (away, away_factors)):
        if factors and factors.get("reliable") and factors.get("key_absentees"):
            names = ", ".join(a["name"] for a in factors["key_absentees"][:2])
            result["key_reasons"].append(f"{side_team} missing key players: {names}.")

    if bookmaker_odds:
        result["value_analysis"] = value_analysis(markets, bookmaker_odds)

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO predictions (scope, home, away, payload) VALUES (?,?,?,?)",
            (scope, home, away, json.dumps(result)),
        )
    return result


def _key_reasons(home, away, lam, mu, elo_home, elo_away,
                 home_form, away_form, neutral, context) -> list[str]:
    reasons = []
    edge = lam - mu
    if abs(edge) < 0.25:
        reasons.append("Evenly matched on attack/defence strength - high draw likelihood.")
    else:
        stronger = home if edge > 0 else away
        reasons.append(f"{stronger} rated stronger on Dixon-Coles attack/defence parameters "
                       f"(xG edge {abs(edge):.2f}).")
    if abs(elo_home - elo_away) > 80:
        leader = home if elo_home > elo_away else away
        reasons.append(f"{leader} leads Elo by {abs(elo_home - elo_away):.0f} points.")
    for team, form in ((home, home_form), (away, away_form)):
        fs = form.get("form_string", "")
        if fs.count("W") >= 4:
            reasons.append(f"{team} in strong form ({fs}).")
        elif fs.count("L") >= 4:
            reasons.append(f"{team} in poor form ({fs}).")
    if neutral:
        reasons.append("Neutral venue: no home advantage applied.")
    elif not context.get("cross_league"):
        reasons.append("Standard home advantage applied.")
    return reasons


def value_analysis(markets: dict, odds: dict) -> dict:
    """Compare model probabilities with bookmaker odds; flag meaningful edges."""
    out = {"fair_probabilities": {}, "value_bets": []}
    trio = {k: odds[k] for k in ("home", "draw", "away") if odds.get(k)}
    if len(trio) == 3:
        fair = remove_overround(trio)
        out["fair_probabilities"] = {k: round(v, 4) for k, v in fair.items()}
        model_p = {"home": markets["home_win"], "draw": markets["draw"], "away": markets["away_win"]}
        for key, fair_p in fair.items():
            edge = model_p[key] - fair_p
            if edge > VALUE_EDGE_THRESHOLD:
                out["value_bets"].append({
                    "market": f"1X2 {key}",
                    "bookmaker_odds": trio[key],
                    "model_probability": round(model_p[key], 4),
                    "market_fair_probability": round(fair_p, 4),
                    "edge": round(edge, 4),
                    "expected_value_pct": round((model_p[key] * trio[key] - 1) * 100, 2),
                    "kelly_fraction": round(
                        max((model_p[key] * trio[key] - 1) / (trio[key] - 1), 0) * 0.25, 4
                    ),  # quarter-Kelly
                })
    if not out["value_bets"]:
        out["note"] = "No edge above threshold - the market price looks efficient here."
    return out
