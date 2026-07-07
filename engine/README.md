# Football Prediction Engine

A probabilistic match-prediction engine built on **free, real data**: 9 seasons of
top-5 European league matches (football-data.co.uk, including Bet365 odds and match
stats) and all competitive internationals since 2010 (martj42 dataset) for World
Cup / Euro / Copa América fixtures.

## Architecture

```
football-data.co.uk CSVs ─┐
                          ├─> ingest.py ─> SQLite (engine/data/engine.db)
international results ────┘                    │
                                               ▼
                    features.py: Elo ratings (margin-aware, home-adv,
                                 friendly damping) + rolling form + tendencies
                                               │
                                               ▼
                    models/dixon_coles.py: time-weighted Dixon-Coles MLE
                    (attack/defence per team, home advantage, rho low-score
                    correction, 390-day half-life decay)
                                               │
                                               ▼
                    simulate.py: analytic score matrix -> 1X2 / exact scores /
                    totals / BTTS; 50k Monte Carlo sims -> corners, fouls, cards
                                               │
                                               ▼
                    predict.py: orchestration, Elo cross-check confidence,
                    key reasons, value-bet detection vs de-vigged odds
                                               │
                                               ▼
                    api.py: FastAPI router mounted at /engine
```

## Usage

```bash
# 1. Ingest/refresh data (re-run weekly; it upserts)
python -m engine.ingest

# 2. Backtest (walk-forward, no lookahead; writes engine/data/backtest_results.json)
python -m engine.backtest            # all leagues, latest season
python -m engine.backtest I1 2425    # one league/season

# 3. Predict from Python
from engine import predict
p = predict.predict_match("Juventus", "Inter", scope="club",
                          bookmaker_odds={"home": 2.9, "draw": 3.1, "away": 2.5})

# 4. Or over HTTP (backend_simple.py mounts the router)
POST /engine/predict
{"home_team": "Argentina", "away_team": "France",
 "scope": "international", "neutral": true}
GET /engine/teams      # valid team names per league
GET /engine/backtest   # stored backtest metrics
GET /engine/status
```

Team names follow football-data.co.uk ("Man City", "Paris SG", "Milan");
`predict.resolve_team` maps common aliases automatically.

## Output

Every prediction returns: predicted xG per team with uncertainty range, 1X2
probabilities, top scorelines, over/under 1.5/2.5/3.5, BTTS, expected corners /
fouls / cards (with over-lines), Elo context, recent form, key reasons,
confidence score, warnings, and — when bookmaker odds are supplied — de-vigged
market probabilities, model edge, EV% and quarter-Kelly stake for any flagged
value bet (edge threshold: 3 probability points).

## Backtest results (season 2025/26, walk-forward monthly refits)

| League | Brier | Log loss | Accuracy | Flat-stake ROI |
|---|---|---|---|---|
| Premier League | 0.616 | 1.026 | 47.2% | -8.5% (271 bets) |
| La Liga | 0.583 | 0.981 | 52.2% | -8.1% (221) |
| Serie A | 0.589 | 0.988 | 52.9% | +12.5% (237) |
| Bundesliga | 0.575 | 0.974 | 55.2% | -4.4% (196) |
| Ligue 1 | 0.599 | 1.000 | 51.8% | -15.4% (192) |

Read this honestly: Brier is close to, but not better than, bookmaker closing
odds (~0.57–0.60). Aggregate betting ROI is **negative** — the Serie A number is
within variance, not proof of an edge. This is the expected result for a
Dixon-Coles baseline against sharp markets and it is why the engine separates
"most likely result" from "value bet" and demands a statistical edge threshold.

## Known limitations / roadmap

1. **Cross-league fixtures** use fixed league-strength priors (no inter-league
   matches in the data) — confidence is automatically reduced.
2. **No confirmed-lineup adjustment yet** (free data has no injury feeds).
   Planned: player-impact layer using the existing squad market values, and
   optionally API-Football for live lineups/injuries.
3. **No GBM ensemble / calibration layer yet.** Planned: LightGBM on
   Elo+form+DC features with isotonic calibration, blended with DC.
4. Corners/fouls/cards use team tendencies + negative-binomial dispersion, not
   event-level data. StatsBomb Open Data integration is the planned upgrade.

## Responsible gambling

This engine outputs probabilities, never certainties. Its own backtest shows a
negative aggregate ROI against real bookmaker prices. Never bet money you
cannot afford to lose; if betting stops being fun, seek help (e.g. BeGambleAware).
