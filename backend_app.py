#!/usr/bin/env python3
"""
🏆 FOOTBALL SIMULATOR BACKEND API
FastAPI backend for the Ultimate Football Simulator

Features:
- RESTful API endpoints
- Real Transfermarkt data integration
- Advanced Bayesian predictions
- WebSocket for real-time match updates
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import json
import asyncio
from datetime import datetime
import uvicorn

# Import our existing simulator components
from ultimate_simulator import (
    create_ultimate_teams, 
    AdvancedBayesianPredictor, 
    UltimateTournament,
    create_player_from_csv_data
)
from enhanced_football_simulator import Player, Team, Match

# Initialize FastAPI app
app = FastAPI(
    title="Ultimate Football Simulator API",
    description="Advanced football simulation with Bayesian learning and ML",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class PlayerResponse(BaseModel):
    name: str
    position: str
    age: int
    overall_rating: int
    market_value_eur: float
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
    total_value: float
    avg_rating: float
    avg_age: float
    player_count: int

class MatchRequest(BaseModel):
    home_team: str
    away_team: str

class MatchResponse(BaseModel):
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    home_strength: Dict[str, float]
    away_strength: Dict[str, float]
    prediction_method: str
    timestamp: str

class TournamentRequest(BaseModel):
    name: str
    team_names: List[str]

class TournamentResponse(BaseModel):
    name: str
    teams: List[str]
    matches: List[MatchResponse]
    standings: List[Dict[str, Any]]
    winner: Optional[str] = None

# Global variables
teams_data: List[Team] = []
predictor = AdvancedBayesianPredictor()
active_connections: List[WebSocket] = []

# Initialize data on startup
@app.on_event("startup")
async def startup_event():
    global teams_data
    print("🚀 Starting Football Simulator API...")
    teams_data = create_ultimate_teams()
    print(f"✅ Loaded {len(teams_data)} teams")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# Helper functions
def team_to_response(team: Team) -> TeamResponse:
    """Convert Team object to API response"""
    players = [
        PlayerResponse(
            name=p.name,
            position=p.position,
            age=p.age,
            overall_rating=p.overall_rating,
            market_value_eur=p.market_value_eur,
            nationality=p.nationality,
            pace=p.pace,
            shooting=p.shooting,
            passing=p.passing,
            dribbling=p.dribbling,
            defending=p.defending,
            physical=p.physical,
            goalkeeping=p.goalkeeping
        ) for p in team.players
    ]
    
    total_value = sum(p.market_value_eur for p in team.players)
    avg_rating = np.mean([p.overall_rating for p in team.players])
    avg_age = sum(p.age for p in team.players) / len(team.players)
    
    return TeamResponse(
        name=team.name,
        players=players,
        total_value=total_value,
        avg_rating=avg_rating,
        avg_age=avg_age,
        player_count=len(team.players)
    )

def find_team_by_name(name: str) -> Optional[Team]:
    """Find team by name"""
    for team in teams_data:
        if team.name.lower() == name.lower():
            return team
    return None

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🏆 Ultimate Football Simulator API",
        "version": "1.0.0",
        "teams_loaded": len(teams_data),
        "endpoints": {
            "teams": "/teams",
            "match": "/match",
            "tournament": "/tournament",
            "websocket": "/ws"
        }
    }

@app.get("/teams", response_model=List[TeamResponse])
async def get_teams():
    """Get all available teams"""
    if not teams_data:
        raise HTTPException(status_code=500, detail="Teams data not loaded")
    
    return [team_to_response(team) for team in teams_data]

@app.get("/teams/{team_name}", response_model=TeamResponse)
async def get_team(team_name: str):
    """Get specific team details"""
    team = find_team_by_name(team_name)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
    
    return team_to_response(team)

@app.post("/match", response_model=MatchResponse)
async def simulate_match(match_request: MatchRequest):
    """Simulate a match between two teams"""
    home_team = find_team_by_name(match_request.home_team)
    away_team = find_team_by_name(match_request.away_team)
    
    if not home_team:
        raise HTTPException(status_code=404, detail=f"Home team '{match_request.home_team}' not found")
    if not away_team:
        raise HTTPException(status_code=404, detail=f"Away team '{match_request.away_team}' not found")
    
    # Predict match
    home_score, away_score = predictor.predict_match_advanced(home_team, away_team)
    
    # Get team strengths
    predictor.initialize_team_strength(home_team)
    predictor.initialize_team_strength(away_team)
    home_strength = predictor.team_strengths[home_team.name]
    away_strength = predictor.team_strengths[away_team.name]
    
    # Create match object and update predictor
    match = Match(home_team, away_team, home_score, away_score)
    predictor.update_from_match_result(match)
    
    response = MatchResponse(
        home_team=home_team.name,
        away_team=away_team.name,
        home_score=home_score,
        away_score=away_score,
        home_strength=home_strength,
        away_strength=away_strength,
        prediction_method="Advanced Bayesian",
        timestamp=datetime.now().isoformat()
    )
    
    # Broadcast to WebSocket clients
    await manager.broadcast(json.dumps({
        "type": "match_result",
        "data": response.dict()
    }))
    
    return response

@app.post("/tournament", response_model=TournamentResponse)
async def simulate_tournament(tournament_request: TournamentRequest):
    """Simulate a full tournament"""
    # Find teams
    tournament_teams = []
    for team_name in tournament_request.team_names:
        team = find_team_by_name(team_name)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
        tournament_teams.append(team)
    
    if len(tournament_teams) < 2:
        raise HTTPException(status_code=400, detail="Tournament needs at least 2 teams")
    
    # Create tournament
    tournament = UltimateTournament(tournament_request.name, tournament_teams)
    
    # Simulate matches
    matches = []
    standings = {}
    
    # Initialize standings
    for team in tournament_teams:
        standings[team.name] = {
            "team": team.name,
            "played": 0,
            "won": 0,
            "drawn": 0,
            "lost": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0
        }
    
    # Play round-robin tournament
    for i, home_team in enumerate(tournament_teams):
        for j, away_team in enumerate(tournament_teams):
            if i != j:
                match = tournament.simulate_match(home_team, away_team)
                
                # Update standings
                standings[home_team.name]["played"] += 1
                standings[away_team.name]["played"] += 1
                standings[home_team.name]["goals_for"] += match.home_score
                standings[home_team.name]["goals_against"] += match.away_score
                standings[away_team.name]["goals_for"] += match.away_score
                standings[away_team.name]["goals_against"] += match.home_score
                
                if match.home_score > match.away_score:
                    standings[home_team.name]["won"] += 1
                    standings[home_team.name]["points"] += 3
                    standings[away_team.name]["lost"] += 1
                elif match.away_score > match.home_score:
                    standings[away_team.name]["won"] += 1
                    standings[away_team.name]["points"] += 3
                    standings[home_team.name]["lost"] += 1
                else:
                    standings[home_team.name]["drawn"] += 1
                    standings[away_team.name]["drawn"] += 1
                    standings[home_team.name]["points"] += 1
                    standings[away_team.name]["points"] += 1
                
                # Calculate goal difference
                for team_name in standings:
                    standings[team_name]["goal_difference"] = (
                        standings[team_name]["goals_for"] - 
                        standings[team_name]["goals_against"]
                    )
                
                # Add match to results
                match_response = MatchResponse(
                    home_team=home_team.name,
                    away_team=away_team.name,
                    home_score=match.home_score,
                    away_score=match.away_score,
                    home_strength=tournament.advanced_predictor.team_strengths[home_team.name],
                    away_strength=tournament.advanced_predictor.team_strengths[away_team.name],
                    prediction_method="Ultimate Bayesian + ML",
                    timestamp=datetime.now().isoformat()
                )
                matches.append(match_response)
    
    # Sort standings by points, then goal difference
    sorted_standings = sorted(
        standings.values(), 
        key=lambda x: (x["points"], x["goal_difference"]), 
        reverse=True
    )
    
    winner = sorted_standings[0]["team"] if sorted_standings else None
    
    response = TournamentResponse(
        name=tournament_request.name,
        teams=[team.name for team in tournament_teams],
        matches=matches,
        standings=sorted_standings,
        winner=winner
    )
    
    # Broadcast tournament result
    await manager.broadcast(json.dumps({
        "type": "tournament_complete",
        "data": response.dict()
    }))
    
    return response

@app.get("/stats")
async def get_stats():
    """Get overall statistics"""
    if not teams_data:
        return {"error": "No teams loaded"}
    
    total_players = sum(len(team.players) for team in teams_data)
    total_value = sum(sum(p.market_value_eur for p in team.players) for team in teams_data)
    avg_team_value = total_value / len(teams_data)
    
    # Position distribution
    positions = {}
    for team in teams_data:
        for player in team.players:
            positions[player.position] = positions.get(player.position, 0) + 1
    
    # Top teams by value
    team_values = [
        {
            "name": team.name,
            "value": sum(p.market_value_eur for p in team.players),
            "players": len(team.players)
        }
        for team in teams_data
    ]
    team_values.sort(key=lambda x: x["value"], reverse=True)
    
    return {
        "total_teams": len(teams_data),
        "total_players": total_players,
        "total_value": total_value,
        "avg_team_value": avg_team_value,
        "position_distribution": positions,
        "top_teams": team_values[:10]
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "teams_loaded": len(teams_data),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Football Simulator Backend...")
    uvicorn.run(
        "backend_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
