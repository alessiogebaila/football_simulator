"""Engine configuration: leagues, seasons, paths, model constants."""
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent
DATA_DIR = ENGINE_DIR / "data"
DB_PATH = DATA_DIR / "engine.db"

# football-data.co.uk league codes -> display names
LEAGUES = {
    "E0": "Premier League",
    "SP1": "La Liga",
    "I1": "Serie A",
    "D1": "Bundesliga",
    "F1": "Ligue 1",
}

# Seasons to ingest, football-data.co.uk folder codes ("1718" = 2017/18).
# ~9 seasons is enough signal for club Elo + Dixon-Coles without stale data.
SEASONS = ["1718", "1819", "1920", "2021", "2122", "2223", "2324", "2425", "2526"]

FOOTBALL_DATA_URL = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"

# International results (martj42 dataset, 1872->today, updated regularly)
INTERNATIONAL_RESULTS_URL = (
    "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
)
# Only recent internationals are modelled; older eras aren't representative.
INTERNATIONAL_MIN_DATE = "2010-01-01"
# Competitive tournaments we actually predict for.
INTERNATIONAL_TOURNAMENTS = (
    "FIFA World Cup",
    "FIFA World Cup qualification",
    "UEFA Euro",
    "UEFA Euro qualification",
    "UEFA Nations League",
    "Copa América",
    "Copa América qualification",
    "Friendly",
)

# --- Elo constants ---
ELO_START = 1500.0
ELO_K_CLUB = 20.0
ELO_K_INTERNATIONAL = 30.0
ELO_HOME_ADV = 60.0  # Elo points of home advantage
ELO_FRIENDLY_DAMP = 0.5  # friendlies move international ratings half as much

# --- Dixon-Coles ---
DC_HALF_LIFE_DAYS = 390.0  # time-decay half-life for match weights
DC_MAX_GOALS = 10  # truncation for the score matrix

# --- Monte Carlo ---
N_SIMS = 50_000

# --- Value bets ---
# Minimum model-vs-market edge (in probability points after removing the
# bookmaker overround) before a bet is flagged as value.
VALUE_EDGE_THRESHOLD = 0.03
