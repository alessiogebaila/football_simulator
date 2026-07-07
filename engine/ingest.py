"""Data ingestion: football-data.co.uk club CSVs + martj42 international results.

Usage:
    python -m engine.ingest            # ingest everything
    python -m engine.ingest --clubs    # club leagues only
    python -m engine.ingest --intl     # internationals only
"""
import io
import logging
import sys

import pandas as pd
import requests

from .config import (
    FOOTBALL_DATA_URL,
    INTERNATIONAL_MIN_DATE,
    INTERNATIONAL_RESULTS_URL,
    INTERNATIONAL_TOURNAMENTS,
    LEAGUES,
    SEASONS,
)
from .db import get_conn

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("engine.ingest")

# football-data.co.uk column -> our column
CLUB_COLUMNS = {
    "HS": "home_shots", "AS": "away_shots",
    "HST": "home_shots_target", "AST": "away_shots_target",
    "HC": "home_corners", "AC": "away_corners",
    "HF": "home_fouls", "AF": "away_fouls",
    "HY": "home_yellows", "AY": "away_yellows",
    "HR": "home_reds", "AR": "away_reds",
    "B365H": "odds_home", "B365D": "odds_draw", "B365A": "odds_away",
    "B365>2.5": "odds_over25", "B365<2.5": "odds_under25",
}

UPSERT_SQL = """
INSERT OR REPLACE INTO matches (
    scope, league, season, date, home, away, home_goals, away_goals,
    home_shots, away_shots, home_shots_target, away_shots_target,
    home_corners, away_corners, home_fouls, away_fouls,
    home_yellows, away_yellows, home_reds, away_reds,
    odds_home, odds_draw, odds_away, odds_over25, odds_under25, neutral
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""


def _fetch_csv(url: str) -> pd.DataFrame | None:
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return pd.read_csv(io.StringIO(resp.text), on_bad_lines="skip", encoding_errors="replace")
    except Exception as exc:  # noqa: BLE001 - ingest keeps going on partial failures
        log.warning("Failed to fetch %s: %s", url, exc)
        return None


def _val(row: pd.Series, col: str):
    v = row.get(col)
    return None if v is None or pd.isna(v) else v


def ingest_clubs() -> int:
    total = 0
    with get_conn() as conn:
        for season in SEASONS:
            for code, name in LEAGUES.items():
                df = _fetch_csv(FOOTBALL_DATA_URL.format(season=season, league=code))
                if df is None or df.empty or "FTHG" not in df.columns:
                    continue
                df = df.dropna(subset=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"])
                dates = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)
                rows = []
                for (_, row), date in zip(df.iterrows(), dates):
                    rows.append((
                        "club", code, season, date.strftime("%Y-%m-%d"),
                        str(row["HomeTeam"]).strip(), str(row["AwayTeam"]).strip(),
                        int(row["FTHG"]), int(row["FTAG"]),
                        *[_val(row, src) for src in CLUB_COLUMNS],
                        0,
                    ))
                conn.executemany(UPSERT_SQL, rows)
                total += len(rows)
                log.info("%s %s (%s): %d matches", name, season, code, len(rows))
    return total


def ingest_internationals() -> int:
    df = _fetch_csv(INTERNATIONAL_RESULTS_URL)
    if df is None:
        return 0
    df = df.dropna(subset=["home_score", "away_score"])
    df = df[df["date"] >= INTERNATIONAL_MIN_DATE]
    df = df[df["tournament"].isin(INTERNATIONAL_TOURNAMENTS)]
    rows = [
        (
            "international", str(r.tournament), None, str(r.date),
            str(r.home_team).strip(), str(r.away_team).strip(),
            int(r.home_score), int(r.away_score),
            *([None] * 17),
            1 if bool(r.neutral) else 0,
        )
        for r in df.itertuples()
    ]
    with get_conn() as conn:
        conn.executemany(UPSERT_SQL, rows)
    log.info("Internationals since %s: %d matches", INTERNATIONAL_MIN_DATE, len(rows))
    return len(rows)


def main() -> None:
    args = set(sys.argv[1:])
    n = 0
    if not args or "--clubs" in args:
        n += ingest_clubs()
    if not args or "--intl" in args:
        n += ingest_internationals()
    log.info("Ingest complete: %d matches upserted", n)


if __name__ == "__main__":
    main()
