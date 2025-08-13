#!/usr/bin/env python3
"""
🏆 FOOTBALL SIMULATOR API
FastAPI backend for the Ultimate Football Simulator
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import random
from dataclasses import asdict
import asyncio
import uvicorn

# Import our existing simulator components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_football_simulator import Player, Team, Match, Tournament
from ultimate_simulator import (
    AdvancedBayesianPredictor, 
    UltimateTournament, 
    create_player_from_csv_data,
    create_ultimate_teams
)

app = FastAPI(
    title="Ultimate Football Simulator API",
    description="Advanced football simulation with Bayesian learning and ML",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class PlayerResponse(BaseModel):
    name: str
    position: str
    age: int
    overall_rating: int
    market_value_eur: int
    nationality: str
    pace: int
    shooting: int
    passing: int
    dribbling: int
    defending: int
    physical: int
    goalkeeping: int

class TeamResponse(BaseModel):
    name: str
    players: List[PlayerResponse]
    total_value: int
    avg_rating: float
    avg_age: float

class MatchResponse(BaseModel):
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    prediction_type: str
    home_confidence: float

class TournamentResponse(BaseModel):
    name: str
    teams: List[str]
    matches: List[MatchResponse]
    standings: List[Dict[str, any]]

class MatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    prediction_type: str = "ultimate"  # "bayesian", "ml", "ultimate"

# Global variables to store data
teams_data: List[Team] = []
predictor = AdvancedBayesianPredictor()
tournament: Optional[UltimateTournament] = None

def player_to_response(player: Player) -> PlayerResponse:
    """Convert Player object to API response"""
    return PlayerResponse(
        name=player.name,
        position=player.position,
        age=player.age,
        overall_rating=player.overall_rating,
        market_value_eur=player.market_value_eur,
        nationality=player.nationality,
        pace=player.pace,
        shooting=player.shooting,
        passing=player.passing,
        dribbling=player.dribbling,
        defending=player.defending,
        physical=player.physical,
        goalkeeping=player.goalkeeping
    )

def team_to_response(team: Team) -> TeamResponse:
    """Convert Team object to API response"""
    total_value = sum(p.market_value_eur for p in team.players)
    avg_rating = np.mean([p.overall_rating for p in team.players])
    avg_age = np.mean([p.age for p in team.players])
    
    return TeamResponse(
        name=team.name,
        players=[player_to_response(p) for p in team.players],
        total_value=total_value,
        avg_rating=round(avg_rating, 1),
        avg_age=round(avg_age, 1)
    )

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    global teams_data, predictor, tournament
    
    print("🚀 Loading football data...")
    teams_data = create_ultimate_teams()
    predictor = AdvancedBayesianPredictor()
    
    if teams_data:
        tournament = UltimateTournament("API Tournament", teams_data)
        print(f"✅ Loaded {len(teams_data)} teams successfully!")
    else:
        print("❌ Failed to load teams data")

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "🏆 Ultimate Football Simulator API",
        "status": "active",
        "teams_loaded": len(teams_data),
        "version": "1.0.0"
    }

@app.get("/teams", response_model=List[TeamResponse])
async def get_teams():
    """Get all teams with their players"""
    if not teams_data:
        raise HTTPException(status_code=500, detail="Teams data not loaded")
    
    return [team_to_response(team) for team in teams_data]

@app.get("/teams/{team_name}", response_model=TeamResponse)
async def get_team(team_name: str):
    """Get specific team details"""
    team = next((t for t in teams_data if t.name.lower() == team_name.lower()), None)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
    
    return team_to_response(team)

@app.get("/teams/{team_name}/players", response_model=List[PlayerResponse])
async def get_team_players(team_name: str):
    """Get all players for a specific team"""
    team = next((t for t in teams_data if t.name.lower() == team_name.lower()), None)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
    
    return [player_to_response(p) for p in team.players]

@app.post("/predict-match", response_model=MatchResponse)
async def predict_match(request: MatchPredictionRequest):
    """Predict match result between two teams"""
    global predictor, tournament
    
    # Find teams
    home_team = next((t for t in teams_data if t.name.lower() == request.home_team.lower()), None)
    away_team = next((t for t in teams_data if t.name.lower() == request.away_team.lower()), None)
    
    if not home_team:
        raise HTTPException(status_code=404, detail=f"Home team '{request.home_team}' not found")
    if not away_team:
        raise HTTPException(status_code=404, detail=f"Away team '{request.away_team}' not found")
    
    # Get prediction based on type
    if request.prediction_type == "bayesian":
        home_score, away_score = predictor.predict_match_advanced(home_team, away_team)
        prediction_type = "🧠 Bayesian"
    elif request.prediction_type == "ultimate" and tournament:
        home_score, away_score = tournament.predict_match_ultimate(home_team, away_team)
        prediction_type = "🎯 Ultimate AI"
    else:
        home_score, away_score = predictor.predict_match_advanced(home_team, away_team)
        prediction_type = "📊 Standard"
    
    # Calculate confidence (simplified)
    goal_diff = abs(home_score - away_score)
    confidence = min(0.9, 0.5 + goal_diff * 0.1)
    
    return MatchResponse(
        home_team=home_team.name,
        away_team=away_team.name,
        home_score=home_score,
        away_score=away_score,
        prediction_type=prediction_type,
        home_confidence=confidence
    )

@app.post("/simulate-match", response_model=MatchResponse)
async def simulate_match(request: MatchPredictionRequest):
    """Simulate a match and update team strengths"""
    global predictor, tournament
    
    # Find teams
    home_team = next((t for t in teams_data if t.name.lower() == request.home_team.lower()), None)
    away_team = next((t for t in teams_data if t.name.lower() == request.away_team.lower()), None)
    
    if not home_team or not away_team:
        raise HTTPException(status_code=404, detail="One or both teams not found")
    
    # Simulate match
    if tournament:
        match = tournament.simulate_match(home_team, away_team)
    else:
        home_score, away_score = predictor.predict_match_advanced(home_team, away_team)
        match = Match(home_team, away_team, home_score, away_score)
        predictor.update_from_match_result(match)
    
    return MatchResponse(
        home_team=match.home_team.name,
        away_team=match.away_team.name,
        home_score=match.home_score,
        away_score=match.away_score,
        prediction_type="🎮 Simulated",
        home_confidence=0.8
    )

@app.get("/team-analysis/{team_name}")
async def get_team_analysis(team_name: str):
    """Get detailed team analysis"""
    team = next((t for t in teams_data if t.name.lower() == team_name.lower()), None)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
    
    # Calculate team statistics
    total_value = sum(p.market_value_eur for p in team.players)
    avg_rating = np.mean([p.overall_rating for p in team.players])
    avg_age = np.mean([p.age for p in team.players])
    
    # Position breakdown
    positions = {}
    for player in team.players:
        positions[player.position] = positions.get(player.position, 0) + 1
    
    # Top players by value
    top_players = sorted(team.players, key=lambda p: p.market_value_eur, reverse=True)[:5]
    
    # Get team strength from predictor
    predictor.initialize_team_strength(team)
    strengths = predictor.team_strengths.get(team.name, {})
    
    return {
        "team_name": team.name,
        "total_value": total_value,
        "avg_rating": round(avg_rating, 1),
        "avg_age": round(avg_age, 1),
        "squad_size": len(team.players),
        "positions": positions,
        "top_players": [
            {
                "name": p.name,
                "position": p.position,
                "rating": p.overall_rating,
                "value": p.market_value_eur,
                "age": p.age
            } for p in top_players
        ],
        "strengths": {
            "attack": round(strengths.get('attack', 1.0), 2),
            "defense": round(strengths.get('defense', 1.0), 2),
            "confidence": round(strengths.get('confidence', 1.0), 2),
            "form": round(strengths.get('form', 1.0), 2)
        }
    }

@app.get("/tournament-status")
async def get_tournament_status():
    """Get current tournament status"""
    if not tournament:
        return {"status": "No active tournament"}
    
    return {
        "name": tournament.name,
        "teams": [team.name for team in tournament.teams],
        "total_teams": len(tournament.teams),
        "matches_played": len(tournament.matches),
        "status": "active"
    }

@app.post("/create-tournament")
async def create_tournament(team_names: List[str]):
    """Create a new tournament with selected teams"""
    global tournament
    
    if len(team_names) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 teams for tournament")
    
    # Find selected teams
    selected_teams = []
    for name in team_names:
        team = next((t for t in teams_data if t.name.lower() == name.lower()), None)
        if team:
            selected_teams.append(team)
        else:
            raise HTTPException(status_code=404, detail=f"Team '{name}' not found")
    
    tournament = UltimateTournament(f"Custom Tournament ({len(selected_teams)} teams)", selected_teams)
    
    return {
        "message": f"Tournament created with {len(selected_teams)} teams",
        "teams": [team.name for team in selected_teams]
    }

@app.get("/stats")
async def get_stats():
    """Get overall statistics"""
    if not teams_data:
        raise HTTPException(status_code=500, detail="No data available")
    
    total_players = sum(len(team.players) for team in teams_data)
    total_value = sum(sum(p.market_value_eur for p in team.players) for team in teams_data)
    avg_team_value = total_value / len(teams_data)
    
    # Most valuable player
    all_players = [p for team in teams_data for p in team.players]
    most_valuable = max(all_players, key=lambda p: p.market_value_eur)
    
    # Average ratings by position
    position_ratings = {}
    for player in all_players:
        if player.position not in position_ratings:
            position_ratings[player.position] = []
        position_ratings[player.position].append(player.overall_rating)
    
    avg_by_position = {
        pos: round(np.mean(ratings), 1) 
        for pos, ratings in position_ratings.items()
    }
    
    return {
        "total_teams": len(teams_data),
        "total_players": total_players,
        "total_value": total_value,
        "avg_team_value": round(avg_team_value),
        "most_valuable_player": {
            "name": most_valuable.name,
            "team": next(t.name for t in teams_data if most_valuable in t.players),
            "value": most_valuable.market_value_eur,
            "position": most_valuable.position
        },
        "avg_rating_by_position": avg_by_position
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
