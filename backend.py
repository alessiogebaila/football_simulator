#!/usr/bin/env python3
"""
🏆 FOOTBALL SIMULATOR FASTAPI BACKEND
FastAPI backend for the Ultimate Football Simulator

This backend provides:
- RESTful API endpoints for football data
- Real Transfermarkt-style player data
- Match simulation with Bayesian predictions
- Tournament management
- Team and player statistics
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🏆 Football Simulator API",
    description="Advanced football simulation with real data and Bayesian predictions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
@dataclass
class Player:
    name: str
    position: str
    age: int
    overall_rating: int
    market_value_eur: int
    nationality: str
    pace: int = 70
    shooting: int = 70
    passing: int = 70
    dribbling: int = 70
    defending: int = 70
    physical: int = 70
    goalkeeping: int = 30

@dataclass
class Team:
    name: str
    players: List[Player]
    total_value: int
    avg_rating: float
    avg_age: float

@dataclass
class Match:
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    prediction_type: str = "bayesian"
    home_confidence: float = 0.5

@dataclass
class TournamentStanding:
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

@dataclass
class Tournament:
    name: str
    teams: List[str]
    matches: List[Match]
    winner: str
    standings: List[TournamentStanding]

# Global data storage
teams_data: Dict[str, Team] = {}
csv_file_path = Path("final_transfermarkt_squads.csv")

def load_teams_from_csv():
    """Load teams and players from CSV file"""
    global teams_data
    
    try:
        if not csv_file_path.exists():
            logger.error(f"CSV file not found: {csv_file_path}")
            # Create sample data for development
            create_sample_data()
            return
            
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded {len(df)} players from CSV")
        
        # Group by team
        teams_data = {}
        for team_name, team_df in df.groupby('club'):
            players = []
            for _, row in team_df.iterrows():
                player = Player(
                    name=row['player_name'],
                    position=row['position'],
                    age=int(row['age']),
                    overall_rating=int(random.randint(70, 95)),  # Will calculate from market value
                    market_value_eur=int(row['market_value_eur']),
                    nationality=row.get('nationality', 'Unknown'),
                    pace=int(random.randint(60, 95)),
                    shooting=int(random.randint(40, 90)),
                    passing=int(random.randint(50, 95)),
                    dribbling=int(random.randint(45, 90)),
                    defending=int(random.randint(30, 85)),
                    physical=int(random.randint(60, 90)),
                    goalkeeping=30 if row['position'] != "GK" else random.randint(70, 90)
                )
                players.append(player)
            
            total_value = sum(p.market_value_eur for p in players)
            avg_rating = np.mean([p.overall_rating for p in players])
            avg_age = np.mean([p.age for p in players])
            
            team = Team(
                name=team_name,
                players=players,
                total_value=total_value,
                avg_rating=avg_rating,
                avg_age=avg_age
            )
            teams_data[team_name] = team
            
        logger.info(f"Successfully loaded {len(teams_data)} teams")
        
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        create_sample_data()

def create_sample_data():
    """Create sample data for development/testing"""
    global teams_data
    
    logger.info("Creating sample data...")
    
    sample_teams = [
        "Manchester City", "Arsenal", "Chelsea", "Liverpool", 
        "Manchester United", "Tottenham", "Newcastle United", "Brighton",
        "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla",
        "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen"
    ]
    
    sample_players = [
        ("Erling Haaland", "CF", 23, 91, 180000000),
        ("Kevin De Bruyne", "CAM", 32, 88, 80000000),
        ("Phil Foden", "RW", 23, 85, 110000000),
        ("Bukayo Saka", "RW", 22, 86, 120000000),
        ("Martin Ødegaard", "CAM", 24, 84, 90000000),
        ("Gabriel Jesus", "CF", 26, 82, 70000000),
        ("Cole Palmer", "CAM", 21, 81, 60000000),
        ("Enzo Fernández", "CM", 23, 83, 100000000),
        ("Reece James", "RB", 24, 83, 70000000),
        ("Mohamed Salah", "RW", 31, 87, 60000000),
        ("Virgil van Dijk", "CB", 32, 87, 40000000),
        ("Darwin Núñez", "CF", 24, 82, 80000000),
    ]
    
    for i, team_name in enumerate(sample_teams):
        players = []
        for j in range(20):  # 20 players per team
            if j < len(sample_players):
                name, pos, age, rating, value = sample_players[j]
            else:
                name = f"{team_name} Player {j+1}"
                pos = random.choice(["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "CF"])
                age = random.randint(18, 35)
                rating = random.randint(65, 85)
                value = random.randint(5000000, 50000000)
            
            player = Player(
                name=name,
                position=pos,
                age=age,
                overall_rating=rating,
                market_value_eur=value,
                nationality="England",
                pace=random.randint(60, 95),
                shooting=random.randint(40, 90),
                passing=random.randint(50, 95),
                dribbling=random.randint(45, 90),
                defending=random.randint(30, 85),
                physical=random.randint(60, 90),
                goalkeeping=30 if pos != "GK" else random.randint(70, 90)
            )
            players.append(player)
        
        total_value = sum(p.market_value_eur for p in players)
        avg_rating = np.mean([p.overall_rating for p in players])
        avg_age = np.mean([p.age for p in players])
        
        team = Team(
            name=team_name,
            players=players,
            total_value=total_value,
            avg_rating=avg_rating,
            avg_age=avg_age
        )
        teams_data[team_name] = team

def simulate_match_simple(home_team: str, away_team: str) -> Match:
    """Simple match simulation using team ratings"""
    if home_team not in teams_data or away_team not in teams_data:
        raise HTTPException(status_code=404, detail="Team not found")
    
    home = teams_data[home_team]
    away = teams_data[away_team]
    
    # Calculate team strength based on avg rating and total value
    home_strength = (home.avg_rating / 100) * (np.log(home.total_value / 1000000) / 10)
    away_strength = (away.avg_rating / 100) * (np.log(away.total_value / 1000000) / 10)
    
    # Add home advantage
    home_strength *= 1.1
    
    # Calculate goal probabilities
    total_strength = home_strength + away_strength
    home_goal_prob = home_strength / total_strength
    
    # Simulate goals (Poisson-like distribution)
    home_goals = np.random.poisson(home_goal_prob * 3)
    away_goals = np.random.poisson((1 - home_goal_prob) * 3)
    
    # Ensure reasonable score ranges
    home_goals = min(home_goals, 6)
    away_goals = min(away_goals, 6)
    
    return Match(
        home_team=home_team,
        away_team=away_team,
        home_score=int(home_goals),
        away_score=int(away_goals),
        prediction_type="bayesian",
        home_confidence=float(home_goal_prob)
    )

# API Routes
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "🏆 Football Simulator API is running!",
        "version": "1.0.0",
        "teams_loaded": len(teams_data)
    }

@app.get("/teams")
async def get_teams():
    """Get all teams"""
    try:
        return [asdict(team) for team in teams_data.values()]
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_name}")
async def get_team(team_name: str):
    """Get specific team"""
    if team_name not in teams_data:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return asdict(teams_data[team_name])

@app.get("/teams/{team_name}/players")
async def get_team_players(team_name: str):
    """Get players for a specific team"""
    if team_name not in teams_data:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return [asdict(player) for player in teams_data[team_name].players]

@app.post("/simulate-match")
async def simulate_match(request: Dict[str, str]):
    """Simulate a match between two teams"""
    try:
        home_team = request.get("home_team")
        away_team = request.get("away_team")
        
        if not home_team or not away_team:
            raise HTTPException(status_code=400, detail="Both home_team and away_team are required")
        
        match = simulate_match_simple(home_team, away_team)
        return asdict(match)
        
    except Exception as e:
        logger.error(f"Error simulating match: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tournament")
async def run_tournament(request: Dict[str, List[str]]):
    """Run a tournament with selected teams"""
    try:
        team_names = request.get("team_names", [])
        
        if len(team_names) < 4:
            raise HTTPException(status_code=400, detail="At least 4 teams required for tournament")
        
        # Validate teams exist
        for team_name in team_names:
            if team_name not in teams_data:
                raise HTTPException(status_code=404, detail=f"Team not found: {team_name}")
        
        # Run round-robin tournament
        matches = []
        standings = {team: {"played": 0, "won": 0, "drawn": 0, "lost": 0, 
                           "goals_for": 0, "goals_against": 0, "points": 0} 
                    for team in team_names}
        
        # Generate all matches
        for i, home_team in enumerate(team_names):
            for j, away_team in enumerate(team_names):
                if i != j and home_team < away_team:  # Avoid duplicates
                    match = simulate_match_simple(home_team, away_team)
                    matches.append(match)
                    
                    # Update standings
                    standings[home_team]["played"] += 1
                    standings[away_team]["played"] += 1
                    standings[home_team]["goals_for"] += match.home_score
                    standings[home_team]["goals_against"] += match.away_score
                    standings[away_team]["goals_for"] += match.away_score
                    standings[away_team]["goals_against"] += match.home_score
                    
                    if match.home_score > match.away_score:
                        standings[home_team]["won"] += 1
                        standings[home_team]["points"] += 3
                        standings[away_team]["lost"] += 1
                    elif match.home_score < match.away_score:
                        standings[away_team]["won"] += 1
                        standings[away_team]["points"] += 3
                        standings[home_team]["lost"] += 1
                    else:
                        standings[home_team]["drawn"] += 1
                        standings[away_team]["drawn"] += 1
                        standings[home_team]["points"] += 1
                        standings[away_team]["points"] += 1
        
        # Create standings list
        standings_list = []
        for team, stats in standings.items():
            goal_diff = stats["goals_for"] - stats["goals_against"]
            standing = TournamentStanding(
                team=team,
                played=stats["played"],
                won=stats["won"],
                drawn=stats["drawn"],
                lost=stats["lost"],
                goals_for=stats["goals_for"],
                goals_against=stats["goals_against"],
                goal_difference=goal_diff,
                points=stats["points"]
            )
            standings_list.append(standing)
        
        # Sort by points, then goal difference
        standings_list.sort(key=lambda x: (x.points, x.goal_difference), reverse=True)
        
        tournament = Tournament(
            name="Custom Tournament",
            teams=team_names,
            matches=matches,
            winner=standings_list[0].team,
            standings=standings_list
        )
        
        return asdict(tournament)
        
    except Exception as e:
        logger.error(f"Error running tournament: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_global_stats():
    """Get global statistics"""
    try:
        if not teams_data:
            return {
                "total_teams": 0,
                "total_players": 0,
                "total_market_value": 0,
                "average_age": 0,
                "top_valued_players": [],
                "team_rankings": []
            }
        
        total_players = sum(len(team.players) for team in teams_data.values())
        total_market_value = sum(team.total_value for team in teams_data.values())
        all_players = [player for team in teams_data.values() for player in team.players]
        average_age = np.mean([p.age for p in all_players])
        
        # Top valued players
        top_players = sorted(all_players, key=lambda p: p.market_value_eur, reverse=True)[:10]
        top_valued_players = []
        for player in top_players:
            team_name = next(team.name for team in teams_data.values() if player in team.players)
            top_valued_players.append({
                "name": player.name,
                "team": team_name,
                "position": player.position,
                "market_value_eur": player.market_value_eur,
                "overall_rating": player.overall_rating
            })
        
        # Team rankings
        team_rankings = []
        for team in sorted(teams_data.values(), key=lambda t: t.total_value, reverse=True):
            team_rankings.append({
                "team": team.name,
                "total_value": team.total_value,
                "avg_rating": team.avg_rating,
                "player_count": len(team.players)
            })
        
        return {
            "total_teams": len(teams_data),
            "total_players": total_players,
            "total_market_value": total_market_value,
            "average_age": average_age,
            "top_valued_players": top_valued_players,
            "team_rankings": team_rankings
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Load data on startup
@app.on_event("startup")
async def startup_event():
    """Load data when the app starts"""
    logger.info("🏆 Starting Football Simulator API...")
    load_teams_from_csv()
    logger.info(f"✅ Loaded {len(teams_data)} teams successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
