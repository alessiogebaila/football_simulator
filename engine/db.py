"""SQLite storage for matches, ratings and predictions."""
import sqlite3
from contextlib import contextmanager

from .config import DATA_DIR, DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT NOT NULL,              -- 'club' | 'international'
    league TEXT NOT NULL,             -- league code or tournament name
    season TEXT,                      -- club only, e.g. '2324'
    date TEXT NOT NULL,               -- ISO yyyy-mm-dd
    home TEXT NOT NULL,
    away TEXT NOT NULL,
    home_goals INTEGER NOT NULL,
    away_goals INTEGER NOT NULL,
    -- match stats (club data, nullable)
    home_shots INTEGER, away_shots INTEGER,
    home_shots_target INTEGER, away_shots_target INTEGER,
    home_corners INTEGER, away_corners INTEGER,
    home_fouls INTEGER, away_fouls INTEGER,
    home_yellows INTEGER, away_yellows INTEGER,
    home_reds INTEGER, away_reds INTEGER,
    -- closing-ish odds (Bet365 pre-match, nullable)
    odds_home REAL, odds_draw REAL, odds_away REAL,
    odds_over25 REAL, odds_under25 REAL,
    neutral INTEGER DEFAULT 0,        -- international neutral venue
    UNIQUE(scope, league, date, home, away)
);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date);
CREATE INDEX IF NOT EXISTS idx_matches_team ON matches(home, away);

CREATE TABLE IF NOT EXISTS elo_ratings (
    scope TEXT NOT NULL,
    team TEXT NOT NULL,
    rating REAL NOT NULL,
    matches_played INTEGER NOT NULL,
    last_match_date TEXT,
    PRIMARY KEY (scope, team)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    scope TEXT NOT NULL,
    home TEXT NOT NULL,
    away TEXT NOT NULL,
    payload TEXT NOT NULL             -- full prediction JSON
);
"""


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextmanager
def get_conn():
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()
