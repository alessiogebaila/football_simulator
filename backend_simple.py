#!/usr/bin/env python3
"""
🏆 FOOTBALL SIMULATOR FASTAPI BACKEND
FastAPI backend for the Ultimate Football Simulator with real data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import logging
from dataclasses import dataclass, asdict, field
import random
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🏆 Football Simulator API",
    description="Advanced football simulation with real transfermarkt data",
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
    kit_number: str = "-"  # Add kit number field
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
class MatchEvent:
    minute: int
    event_type: str  # "goal", "yellow_card", "red_card", "substitution", "corner", "free_kick"
    team: str
    player: str
    description: str
    
@dataclass
class MatchStats:
    possession_home: int
    possession_away: int
    shots_home: int
    shots_away: int
    shots_on_target_home: int
    shots_on_target_away: int
    corners_home: int
    corners_away: int
    fouls_home: int
    fouls_away: int
    yellow_cards_home: int
    yellow_cards_away: int
    red_cards_home: int
    red_cards_away: int

@dataclass
class Match:
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    prediction_type: str = "bayesian"
    home_confidence: float = 0.5
    events: List[MatchEvent] = field(default_factory=list)
    stats: MatchStats = None
    status: str = "FULL TIME"  # "LIVE", "HALF TIME", "FULL TIME"
    current_minute: int = 90

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

def calculate_overall_rating_from_value(market_value: int, age: int, player_name: str = "") -> int:
    """Calculate overall rating based on market value and age (deterministic)"""
    # Create a seed based on market value and player name for consistency
    seed = hash(f"{player_name}_{market_value}_{age}") % 10000
    import random as rand_module
    rand_module.seed(seed)
    
    # Base rating from market value
    if market_value >= 150000000:  # 150M+ (Exceptional talents)
        base_rating = rand_module.randint(92, 97)
    elif market_value >= 100000000:  # 100M+ (World class)
        base_rating = rand_module.randint(89, 95)
    elif market_value >= 80000000:  # 80M+ (Elite)
        base_rating = rand_module.randint(84, 90)
    elif market_value >= 50000000:  # 50M+ (Very good)
        base_rating = rand_module.randint(80, 87)
    elif market_value >= 30000000:  # 30M+ (Good)
        base_rating = rand_module.randint(76, 83)
    elif market_value >= 15000000:  # 15M+ (Decent)
        base_rating = rand_module.randint(72, 80)
    elif market_value >= 5000000:  # 5M+ (Average)
        base_rating = rand_module.randint(68, 76)
    else:
        base_rating = rand_module.randint(60, 70)
    
    # Age-based adjustments (more nuanced for high-value players)
    if market_value >= 80000000:  # High-value players (80M+) - minimal age penalty
        if age <= 18:  # Generational talents like Yamal and Cubarsi
            base_rating = max(85, base_rating - rand_module.randint(0, 2))  # Minimal reduction, min 85
        elif age <= 21:  # Young superstars
            base_rating = max(84, base_rating - rand_module.randint(0, 1))  # Very small reduction
        elif age <= 25:  # Prime development
            pass  # No adjustment
        elif age <= 29:  # Prime years
            base_rating += rand_module.randint(0, 2)  # Small experience boost
        elif age <= 32:  # Experienced veterans
            base_rating = max(82, base_rating - rand_module.randint(0, 1))  # Minimal decline, min 82
        elif age <= 35:  # Older veterans but still valuable
            base_rating = max(80, base_rating - rand_module.randint(0, 2))  # Small decline, min 80
        else:  # Very old but still high-value (legends)
            base_rating = max(77, base_rating - rand_module.randint(1, 3))  # Moderate decline, min 77
    elif market_value >= 50000000:  # Very good players (50M+) - reduced age penalty for veterans
        if age <= 18:  # Young talents
            base_rating = max(81, base_rating - rand_module.randint(0, 2))  # Small reduction, min 81
        elif age <= 21:  # Young players like Gavi
            base_rating = max(83, base_rating - rand_module.randint(0, 1))  # Very small reduction, min 83
        elif age <= 25:  # Prime development
            pass  # No adjustment
        elif age <= 29:  # Prime years
            base_rating += rand_module.randint(0, 2)  # Small experience boost
        elif age <= 32:  # Experienced
            base_rating = max(77, base_rating - rand_module.randint(0, 2))  # Small decline, min 77
        elif age <= 35:  # Older veterans
            base_rating = max(74, base_rating - rand_module.randint(0, 3))  # Moderate decline, min 74
        else:  # Very old
            base_rating = max(70, base_rating - rand_module.randint(1, 4))  # Decline, min 70
    elif market_value >= 30000000:  # Good players (30M+) - reduced age penalty
        if age <= 18:  # Young talents
            base_rating = max(78, base_rating - rand_module.randint(0, 3))  # Small reduction, min 78
        elif age <= 21:  # Young players
            base_rating = max(76, base_rating - rand_module.randint(0, 2))  # Small reduction
        elif age <= 25:  # Prime development
            pass  # No adjustment
        elif age <= 29:  # Prime years
            base_rating += rand_module.randint(0, 2)  # Small experience boost
        elif age <= 32:  # Experienced
            base_rating = max(72, base_rating - rand_module.randint(0, 3))  # Small decline, min 72
        elif age <= 35:  # Older players
            base_rating = max(68, base_rating - rand_module.randint(1, 4))  # Moderate decline, min 68
        else:  # Very old
            base_rating = max(65, base_rating - rand_module.randint(2, 5))  # Decline, min 65
    elif market_value >= 10000000:  # Valuable players (10M+) - good protection for veterans
        if age <= 18:  # Young talents
            base_rating = max(73, base_rating - rand_module.randint(0, 3))  # Small reduction, min 73
        elif age <= 21:  # Young players
            base_rating = max(71, base_rating - rand_module.randint(0, 2))  # Small reduction
        elif age <= 25:  # Prime development
            pass  # No adjustment
        elif age <= 29:  # Prime years
            base_rating += rand_module.randint(0, 2)  # Small experience boost
        elif age <= 32:  # Experienced
            base_rating = max(70, base_rating - rand_module.randint(0, 2))  # Small decline, min 70
        elif age <= 35:  # Older but valuable players
            base_rating = max(65, base_rating - rand_module.randint(1, 3))  # Moderate decline, min 65
        else:  # Very old but still 10M+ (valuable veterans) - realistic for 35+
            base_rating = max(60, base_rating - rand_module.randint(2, 5))  # Age decline, min 60
    else:  # Regular players (under 10M) - normal age adjustments
        if age <= 18:  # Very young players
            base_rating = min(base_rating, 78)  # Cap at 78 for most teenagers
            base_rating -= rand_module.randint(2, 6)  # Reduce for lack of experience
        elif age <= 21:  # Young players
            base_rating = min(base_rating, 83)  # Cap at 83 for very young
            base_rating -= rand_module.randint(1, 4)  # Small reduction
        elif age <= 25:  # Prime development
            pass  # No adjustment, peak potential
        elif age <= 29:  # Prime years
            base_rating += rand_module.randint(0, 3)  # Small boost for experience
        elif age <= 32:  # Experienced
            base_rating += rand_module.randint(0, 2)  # Experience boost
            base_rating -= rand_module.randint(0, 2)  # Physical decline
        else:  # Veteran players (low value)
            base_rating -= rand_module.randint(2, 6)  # Age decline
    
    return max(60, min(95, base_rating))

def generate_position_stats(position: str, overall_rating: int) -> dict:
    """Generate realistic stats based on position and overall rating"""
    base_stats = {
        "pace": overall_rating,
        "shooting": overall_rating,
        "passing": overall_rating,
        "dribbling": overall_rating,
        "defending": overall_rating,
        "physical": overall_rating,
        "goalkeeping": 30
    }
    
    # Position-specific adjustments
    variation = random.randint(-10, 10)
    
    if position == "GK":
        base_stats.update({
            "goalkeeping": min(95, overall_rating + random.randint(0, 10)),
            "defending": max(30, overall_rating - 20),
            "shooting": max(20, overall_rating - 40),
            "dribbling": max(30, overall_rating - 30),
            "pace": max(40, overall_rating - 25)
        })
    elif position in ["CB", "LB", "RB"]:
        base_stats.update({
            "defending": min(95, overall_rating + random.randint(0, 15)),
            "physical": min(95, overall_rating + random.randint(0, 10)),
            "shooting": max(30, overall_rating - 25),
            "dribbling": max(40, overall_rating - 20)
        })
    elif position in ["CDM", "CM"]:
        base_stats.update({
            "passing": min(95, overall_rating + random.randint(0, 15)),
            "defending": min(90, overall_rating + random.randint(-5, 10)),
            "physical": min(90, overall_rating + random.randint(-5, 5))
        })
    elif position in ["CAM", "LW", "RW"]:
        base_stats.update({
            "dribbling": min(95, overall_rating + random.randint(0, 15)),
            "passing": min(95, overall_rating + random.randint(0, 10)),
            "pace": min(95, overall_rating + random.randint(0, 10)),
            "defending": max(20, overall_rating - 30)
        })
    elif position in ["CF", "ST"]:
        base_stats.update({
            "shooting": min(95, overall_rating + random.randint(0, 15)),
            "physical": min(95, overall_rating + random.randint(0, 10)),
            "pace": min(95, overall_rating + random.randint(-5, 10)),
            "defending": max(20, overall_rating - 35)
        })
    
    return base_stats

def load_teams_from_csv():
    """Load teams and players from CSV file"""
    global teams_data
    
    try:
        csv_file_path = Path("final_transfermarkt_squads.csv")
        if not csv_file_path.exists():
            logger.error(f"CSV file not found: {csv_file_path}")
            create_sample_data()
            return
            
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded {len(df)} players from CSV")
        
        # Group by team (club)
        teams_data = {}
        for team_name, team_df in df.groupby('club'):
            players = []
            for _, row in team_df.iterrows():
                market_value = int(row['market_value_eur']) if pd.notna(row['market_value_eur']) else 1000000
                age = int(row['age'])
                overall_rating = calculate_overall_rating_from_value(market_value, age, row['player_name'])
                position_stats = generate_position_stats(row['position'], overall_rating)
                
                # Handle kit number
                kit_number = "-"
                if pd.notna(row['kit_number']) and row['kit_number'] != '':
                    try:
                        kit_number = str(int(float(row['kit_number'])))
                    except (ValueError, TypeError):
                        kit_number = "-"
                
                player = Player(
                    name=row['player_name'],
                    position=row['position'],
                    age=age,
                    overall_rating=overall_rating,
                    market_value_eur=market_value,
                    nationality=row.get('nationality', 'Unknown'),
                    kit_number=kit_number,
                    **position_stats
                )
                players.append(player)
            
            if players:  # Only add teams that have players
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
        
        # Print team names for debugging
        for team_name in sorted(teams_data.keys()):
            logger.info(f"Team: {team_name} ({len(teams_data[team_name].players)} players)")
        
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        create_sample_data()

def create_sample_data():
    """Create sample data for development/testing"""
    global teams_data
    
    logger.info("Creating sample data...")
    
    sample_teams = [
        "Manchester City", "Arsenal", "Chelsea", "Liverpool", 
        "Manchester United", "Tottenham", "Newcastle United", "Brighton"
    ]
    
    for team_name in sample_teams:
        players = []
        for j in range(20):  # 20 players per team
            player = Player(
                name=f"{team_name} Player {j+1}",
                position=random.choice(["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "CF"]),
                age=random.randint(18, 35),
                overall_rating=random.randint(65, 85),
                market_value_eur=random.randint(5000000, 50000000),
                nationality="England",
                pace=random.randint(60, 95),
                shooting=random.randint(40, 90),
                passing=random.randint(50, 95),
                dribbling=random.randint(45, 90),
                defending=random.randint(30, 85),
                physical=random.randint(60, 90),
                goalkeeping=30
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

def simulate_match_detailed(home_team_name: str, away_team_name: str) -> Match:
    """Advanced match simulation with detailed events and statistics"""
    if home_team_name not in teams_data or away_team_name not in teams_data:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Get team data using the new function to ensure we only use starting eleven
    home_team = get_team_starting_eleven(home_team_name)
    away_team = get_team_starting_eleven(away_team_name)
    
    # Get the original team objects for strength calculation
    home = teams_data[home_team_name]
    away = teams_data[away_team_name]
    
    # Calculate team strength based on avg rating and total value
    home_strength = (home.avg_rating / 100) * (np.log(home.total_value / 1000000) / 10)
    away_strength = (away.avg_rating / 100) * (np.log(away.total_value / 1000000) / 10)
    
    # Add home advantage
    home_strength *= 1.1
    
    # Calculate possession percentage
    total_strength = home_strength + away_strength
    home_possession = int((home_strength / total_strength) * 100)
    away_possession = 100 - home_possession
    
    # Initialize match variables
    events = []
    home_score = 0
    away_score = 0
    
    # Generate realistic statistics based on team strength
    shots_home = max(5, int(home_strength * 8 + random.randint(-3, 5)))
    shots_away = max(5, int(away_strength * 8 + random.randint(-3, 5)))
    shots_on_target_home = max(1, int(shots_home * 0.4 + random.randint(-2, 3)))
    shots_on_target_away = max(1, int(shots_away * 0.4 + random.randint(-2, 3)))
    corners_home = max(0, int(home_strength * 6 + random.randint(-2, 4)))
    corners_away = max(0, int(away_strength * 6 + random.randint(-2, 4)))
    fouls_home = max(5, int(15 - home_strength * 2 + random.randint(-3, 5)))
    fouls_away = max(5, int(15 - away_strength * 2 + random.randint(-3, 5)))
    yellow_cards_home = max(0, int(fouls_home / 5 + random.randint(-1, 2)))
    yellow_cards_away = max(0, int(fouls_away / 5 + random.randint(-1, 2)))
    red_cards_home = 1 if random.random() < 0.05 else 0
    red_cards_away = 1 if random.random() < 0.05 else 0
    
    # Only players in the starting eleven can participate in match events
    home_players = home_team["players"]
    away_players = away_team["players"]
    
    # Weight scoring probability by position and overall rating
    home_attackers = [p for p in home_players if p.position in ["ST", "CF", "LW", "RW"]]
    away_attackers = [p for p in away_players if p.position in ["ST", "CF", "LW", "RW"]]
    
    home_midfielders = [p for p in home_players if p.position in ["CAM", "CM", "CDM"]]
    away_midfielders = [p for p in away_players if p.position in ["CAM", "CM", "CDM"]]
    
    # Ensure we have players to choose from (fallback to starting eleven)
    if not home_attackers:
        home_attackers = home_players[:5]
    if not away_attackers:
        away_attackers = away_players[:5]
    if not home_midfielders:
        home_midfielders = home_players[:5]
    if not away_midfielders:
        away_midfielders = away_players[:5]
    
    # Generate goals and key events with improved probabilities
    # Better players should have higher chances of scoring
    goal_probability_home = (home_strength / total_strength) * 0.7  # Increased probability
    goal_probability_away = (away_strength / total_strength) * 0.7  # Increased probability
    
    def select_weighted_scorer(attackers):
        """Select a scorer based on weighted probability (higher overall = higher chance)"""
        if not attackers:
            return None
        
        # Create weights based on overall rating (exponential for more realistic distribution)
        weights = []
        for player in attackers:
            # Players with higher overall get exponentially higher chances
            # 90+ overall: very high chance, 80-89: high chance, 70-79: medium chance, etc.
            base_weight = max(1, player.overall_rating - 60)  # Minimum weight of 1
            # Exponential scaling: 95 overall = ~35^2, 85 overall = ~25^2, 75 overall = ~15^2
            weight = base_weight ** 1.8
            weights.append(weight)
        
        # Weighted random selection
        total_weight = sum(weights)
        random_num = random.random() * total_weight
        
        cumulative_weight = 0
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if random_num <= cumulative_weight:
                return attackers[i]
        
        # Fallback to last player
        return attackers[-1]
    
    # Substitutions, goals, cards and other events will be created and then sorted by minute
    events_by_time = []
    goal_minutes = []
    
    # First half goals (more likely in 15-45 minutes)
    for _ in range(max(0, int(np.random.poisson(goal_probability_home * 2)))):
        minute = random.choice(range(1, 46))
        if minute not in goal_minutes:
            goal_minutes.append(minute)
            events_by_time.append((minute, 'goal', home_team_name, home_attackers))
    
    for _ in range(max(0, int(np.random.poisson(goal_probability_away * 2)))):
        minute = random.choice(range(1, 46))
        if minute not in goal_minutes:
            goal_minutes.append(minute)
            events_by_time.append((minute, 'goal', away_team_name, away_attackers))
    
    # Second half goals (45-90 minutes)
    for _ in range(max(0, int(np.random.poisson(goal_probability_home * 2)))):
        minute = random.choice(range(46, 91))
        if minute not in goal_minutes:
            goal_minutes.append(minute)
            events_by_time.append((minute, 'goal', home_team_name, home_attackers))
    
    for _ in range(max(0, int(np.random.poisson(goal_probability_away * 2)))):
        minute = random.choice(range(46, 91))
        if minute not in goal_minutes:
            goal_minutes.append(minute)
            events_by_time.append((minute, 'goal', away_team_name, away_attackers))
    
    # Add yellow cards to events_by_time
    card_minutes = []
    for _ in range(yellow_cards_home):
        minute = random.randint(1, 90)
        if minute not in card_minutes:
            card_minutes.append(minute)
            events_by_time.append((minute, 'yellow_card', home_team_name, home_players))
    
    for _ in range(yellow_cards_away):
        minute = random.randint(1, 90)
        if minute not in card_minutes:
            card_minutes.append(minute)
            events_by_time.append((minute, 'yellow_card', away_team_name, away_players))
    
    # Add red cards to events_by_time
    for _ in range(red_cards_home):
        minute = random.randint(1, 90)
        events_by_time.append((minute, 'red_card', home_team_name, home_players))
    
    for _ in range(red_cards_away):
        minute = random.randint(1, 90)
        events_by_time.append((minute, 'red_card', away_team_name, away_players))
    
    # Track subbed out players to ensure they don't participate in later events
    substitutions = []
    subbed_out_players = []
    subbed_in_players = []
    
    # Add some substitutions (substitute from starting eleven, bring in bench players)
    for team_name, team_obj, players in [(home_team_name, home, home_players), (away_team_name, away, away_players)]:
        # Create a bench of players not in the starting eleven
        bench_players = [p for p in team_obj.players if p.name not in [player.name for player in players]]
        for _ in range(random.randint(1, 3)):
            minute = random.randint(46, 85)
            if players and bench_players:
                # Ensure we don't sub out already substituted players
                available_players = [p for p in players if p.name not in subbed_out_players]
                if not available_players:
                    continue
                    
                sub_out = random.choice(available_players)
                sub_in = random.choice(bench_players)
                
                # Track substitutions
                subbed_out_players.append(sub_out.name)
                subbed_in_players.append(sub_in.name)
                substitutions.append((minute, sub_out.name, sub_in.name, team_name))
                
                events.append(MatchEvent(
                    minute=minute,
                    event_type="substitution",
                    team=team_name,
                    player=f"{sub_out.name} → {sub_in.name}",
                    description=f"🔄 Substitution: {sub_out.name} off, {sub_in.name} on ({team_name})"
                ))
    
    # Add corner kicks to events_by_time
    for _ in range(corners_home):
        minute = random.randint(1, 90)
        events_by_time.append((minute, 'corner', home_team_name, None))
    
    for _ in range(corners_away):
        minute = random.randint(1, 90)
        events_by_time.append((minute, 'corner', away_team_name, None))
    
    # Now add all substitutions to events_by_time
    for minute, subbed_out, subbed_in, team in substitutions:
        events_by_time.append((minute, 'substitution', team, (subbed_out, subbed_in)))
        
    # Sort all events by minute
    events_by_time.sort(key=lambda x: x[0])
    
    # Process events chronologically to handle substitutions
    active_players_home = {p.name: p for p in home_players}
    active_players_away = {p.name: p for p in away_players}
    bench_players_home = {p.name: p for p in home.players if p.name not in active_players_home}
    bench_players_away = {p.name: p for p in away.players if p.name not in active_players_away}
    
    for minute, event_type, team, data in events_by_time:
        if event_type == 'substitution':
            # Process substitution
            subbed_out, subbed_in = data
            if team == home_team_name:
                if subbed_out in active_players_home:
                    del active_players_home[subbed_out]
                if subbed_in in bench_players_home:
                    active_players_home[subbed_in] = bench_players_home[subbed_in]
                    del bench_players_home[subbed_in]
            else:
                if subbed_out in active_players_away:
                    del active_players_away[subbed_out]
                if subbed_in in bench_players_away:
                    active_players_away[subbed_in] = bench_players_away[subbed_in]
                    del bench_players_away[subbed_in]
            
            # Add event
            events.append(MatchEvent(
                minute=minute,
                event_type="substitution",
                team=team,
                player=f"{subbed_out} → {subbed_in}",
                description=f"� Substitution: {subbed_out} off, {subbed_in} on ({team})"
            ))
        elif event_type == 'goal':
            # Process goal, only active players can score
            team_players = active_players_home.values() if team == home_team_name else active_players_away.values()
            team_attackers = [p for p in team_players if p.position in ["ST", "CF", "LW", "RW", "CAM"]]
            
            if not team_attackers:
                team_attackers = list(team_players)[:3]  # Use any active players if no attackers available
            
            if team_attackers:
                scorer = select_weighted_scorer(team_attackers)
                if scorer:
                    if team == home_team_name:
                        home_score += 1
                    else:
                        away_score += 1
                        
                    events.append(MatchEvent(
                        minute=minute,
                        event_type="goal",
                        team=team,
                        player=scorer.name,
                        description=f"⚽ Goal! {scorer.name} scores for {team}"
                    ))
        
        elif event_type == 'yellow_card' or event_type == 'red_card':
            # Only active players can get cards
            team_players = list(active_players_home.values() if team == home_team_name else active_players_away.values())
            if team_players:
                player = random.choice(team_players)
                card_emoji = "🟨" if event_type == "yellow_card" else "🟥"
                card_text = "Yellow card" if event_type == "yellow_card" else f"Red card! {player.name} is sent off"
                
                events.append(MatchEvent(
                    minute=minute,
                    event_type=event_type,
                    team=team,
                    player=player.name,
                    description=f"{card_emoji} {card_text} for {player.name} ({team})"
                ))
        
        elif event_type == 'corner':
            # Add corner event
            events.append(MatchEvent(
                minute=minute,
                event_type="corner",
                team=team,
                player="",
                description=f"🚩 Corner kick for {team}"
            ))
    
    # Create match statistics
    stats = MatchStats(
        possession_home=home_possession,
        possession_away=away_possession,
        shots_home=shots_home,
        shots_away=shots_away,
        shots_on_target_home=shots_on_target_home,
        shots_on_target_away=shots_on_target_away,
        corners_home=corners_home,
        corners_away=corners_away,
        fouls_home=fouls_home,
        fouls_away=fouls_away,
        yellow_cards_home=yellow_cards_home,
        yellow_cards_away=yellow_cards_away,
        red_cards_home=red_cards_home,
        red_cards_away=red_cards_away
    )
    
    return Match(
        home_team=home_team_name,
        away_team=away_team_name,
        home_score=home_score,
        away_score=away_score,
        prediction_type="advanced_bayesian",
        home_confidence=float(home_strength / total_strength),
        events=events,
        stats=stats,
        status="FULL TIME",
        current_minute=90
    )

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

def get_team_formation(team_name: str) -> str:
    """Get the specific formation for each team"""
    formations = {
        "Real Madrid": "4-3-1-2",
        "PSG": "4-3-3", 
        "Manchester City": "4-3-3",
        "Napoli": "4-3-3",
        "Arsenal": "4-2-3-1",
        "Liverpool": "4-2-3-1",
        "Atletico Madrid": "4-4-2",
        "Bayern Munich": "4-2-3-1",
        "Barcelona": "4-2-3-1",
        "Juventus": "3-4-2-1",
        "Inter": "3-5-2",
        "Inter Milan": "3-5-2",  # Alternative name
        "AC Milan": "4-2-3-1",
        "Borussia Dortmund": "3-4-2-1",
        "Manchester United": "3-4-2-1",
        "Tottenham": "4-3-3",
        "Chelsea": "4-2-3-1"  # Added Chelsea
    }
    
    # Try exact match first, then partial match for variations
    if team_name in formations:
        return formations[team_name]
    
    # Check for partial matches (case-insensitive)
    team_lower = team_name.lower()
    for team_key, formation in formations.items():
        if team_key.lower() in team_lower or team_lower in team_key.lower():
            return formation
    
    # Special handling for common variations
    if 'barcelona' in team_lower or 'barca' in team_lower:
        return "4-2-3-1"
    if 'real madrid' in team_lower or 'madrid' in team_lower:
        return "4-3-1-2"
    if 'manchester city' in team_lower or 'man city' in team_lower:
        return "4-3-3"
    
    # Default formation
    return "4-3-3"

def select_players_by_formation(players: List[Player], formation: str) -> List[Player]:
    """Select starting eleven based on team's specific formation"""
    starting_eleven = []
    
    # Always start with goalkeeper
    goalkeepers = [p for p in players if p.position == "GK"]
    if goalkeepers:
        starting_eleven.append(max(goalkeepers, key=lambda x: x.overall_rating))
    
    # Get available players by position
    center_backs = [p for p in players if p.position == "CB"]
    left_backs = [p for p in players if p.position == "LB"]
    right_backs = [p for p in players if p.position == "RB"]
    cdms = [p for p in players if p.position == "CDM"]
    cms = [p for p in players if p.position == "CM"]
    cams = [p for p in players if p.position == "CAM"]
    left_wings = [p for p in players if p.position == "LW"]
    right_wings = [p for p in players if p.position == "RW"]
    strikers = [p for p in players if p.position in ["ST", "CF"]]
    
    # Sort by overall rating
    center_backs.sort(key=lambda x: x.overall_rating, reverse=True)
    left_backs.sort(key=lambda x: x.overall_rating, reverse=True)
    right_backs.sort(key=lambda x: x.overall_rating, reverse=True)
    cdms.sort(key=lambda x: x.overall_rating, reverse=True)
    cms.sort(key=lambda x: x.overall_rating, reverse=True)
    cams.sort(key=lambda x: x.overall_rating, reverse=True)
    left_wings.sort(key=lambda x: x.overall_rating, reverse=True)
    right_wings.sort(key=lambda x: x.overall_rating, reverse=True)
    strikers.sort(key=lambda x: x.overall_rating, reverse=True)
    
    if formation == "4-3-3":
        # 4 defenders: LB, CB, CB, RB
        if left_backs: starting_eleven.extend(left_backs[:1])
        if center_backs: starting_eleven.extend(center_backs[:2])
        if right_backs: starting_eleven.extend(right_backs[:1])
        
        # 3 midfielders: CDM/CM, CM, CM/CAM
        if cdms: starting_eleven.extend(cdms[:1])
        if cms: starting_eleven.extend(cms[:2])
        
        # 3 forwards: LW, ST, RW
        if left_wings: starting_eleven.extend(left_wings[:1])
        if strikers: starting_eleven.extend(strikers[:1])
        if right_wings: starting_eleven.extend(right_wings[:1])
        
    elif formation == "4-2-3-1":
        # 4 defenders: LB, CB, CB, RB
        if left_backs: starting_eleven.extend(left_backs[:1])
        if center_backs: starting_eleven.extend(center_backs[:2])
        if right_backs: starting_eleven.extend(right_backs[:1])
        
        # 2 defensive midfielders: CDM, CDM (double pivot)
        if cdms: starting_eleven.extend(cdms[:2])
        elif cms: starting_eleven.extend(cms[:2])  # Use CMs if no CDMs available
        
        # 3 attacking midfielders: LW, CAM, RW
        if left_wings: starting_eleven.extend(left_wings[:1])
        if cams: starting_eleven.extend(cams[:1])
        if right_wings: starting_eleven.extend(right_wings[:1])
        
        # 1 striker: CF/ST
        if strikers: starting_eleven.extend(strikers[:1])
        
    elif formation == "4-4-2":
        # 4 defenders: LB, CB, CB, RB
        if left_backs: starting_eleven.extend(left_backs[:1])
        if center_backs: starting_eleven.extend(center_backs[:2])
        if right_backs: starting_eleven.extend(right_backs[:1])
        
        # 4 midfielders: LM, CM, CM, RM (flat midfield line)
        # Use wingers as left/right midfielders, CMs in center
        if left_wings: starting_eleven.extend(left_wings[:1])  # LM
        elif cms: starting_eleven.extend(cms[:1])  # Fallback LM
        if cms: starting_eleven.extend(cms[:2])  # Two central midfielders
        if right_wings: starting_eleven.extend(right_wings[:1])  # RM
        elif cms and len(cms) > 2: starting_eleven.extend(cms[2:3])  # Fallback RM
        
        # 2 strikers: ST, ST
        if strikers: starting_eleven.extend(strikers[:2])
        
    elif formation == "4-3-1-2":
        # 4 defenders: LB, CB, CB, RB
        if left_backs: starting_eleven.extend(left_backs[:1])
        if center_backs: starting_eleven.extend(center_backs[:2])
        if right_backs: starting_eleven.extend(right_backs[:1])
        
        # 3 midfielders: CDM/CM, CM, CM
        if cdms: starting_eleven.extend(cdms[:1])
        if cms: starting_eleven.extend(cms[:2])
        
        # 1 attacking midfielder: CAM
        if cams: starting_eleven.extend(cams[:1])
        
        # 2 strikers: ST, ST
        if strikers: starting_eleven.extend(strikers[:2])
        
    elif formation == "3-4-2-1":
        # 3 defenders: CB, CB, CB
        if center_backs: starting_eleven.extend(center_backs[:3])
        
        # 4 midfielders: LM/LWB, CM, CM, RM/RWB (flat midfield line)
        if left_backs: starting_eleven.extend(left_backs[:1])  # LWB/LM
        elif left_wings: starting_eleven.extend(left_wings[:1])  # LM
        if cms: starting_eleven.extend(cms[:2])  # Two central midfielders
        if right_backs: starting_eleven.extend(right_backs[:1])  # RWB/RM
        elif right_wings: starting_eleven.extend(right_wings[:1])  # RM
        
        # 2 attacking midfielders: CAM, CAM/LW/RW
        if cams: starting_eleven.extend(cams[:1])
        if cams and len(cams) > 1: starting_eleven.extend(cams[1:2])
        elif left_wings and len(left_wings) > 0: starting_eleven.extend(left_wings[:1])
        elif right_wings and len(right_wings) > 0: starting_eleven.extend(right_wings[:1])
        
        # 1 striker: ST
        if strikers: starting_eleven.extend(strikers[:1])
        
    elif formation == "3-5-2":
        # 3 defenders: CB, CB, CB
        if center_backs: starting_eleven.extend(center_backs[:3])
        
        # 5 midfielders: LB/LW, CDM, CM, CM, RB/RW
        if left_backs: starting_eleven.extend(left_backs[:1])
        elif left_wings: starting_eleven.extend(left_wings[:1])
        if cdms: starting_eleven.extend(cdms[:1])
        if cms: starting_eleven.extend(cms[:2])
        if right_backs: starting_eleven.extend(right_backs[:1])
        elif right_wings: starting_eleven.extend(right_wings[:1])
        
        # 2 strikers: ST, ST
        if strikers: starting_eleven.extend(strikers[:2])
    
    # Fill remaining spots with best available players
    if len(starting_eleven) < 11:
        remaining_players = [p for p in players if p not in starting_eleven]
        remaining_players.sort(key=lambda x: x.overall_rating, reverse=True)
        needed = 11 - len(starting_eleven)
        starting_eleven.extend(remaining_players[:needed])
    
    # Ensure exactly 11 players
    starting_eleven = starting_eleven[:11]
    return starting_eleven

def get_team_starting_eleven(team_name: str) -> Dict[str, Any]:
    """Get starting eleven for a specific team with their formation"""
    if team_name not in teams_data:
        raise HTTPException(status_code=404, detail="Team not found")
        
    team = teams_data[team_name]
    formation = get_team_formation(team_name)
    starting_eleven = select_players_by_formation(team.players, formation)
    
    return {
        "name": team_name,
        "formation": formation,
        "players": starting_eleven
    }

@app.get("/teams/{team_name}/starting-eleven")
async def get_starting_eleven(team_name: str):
    """Get starting eleven for a specific team with their formation"""
    if team_name not in teams_data:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams_data[team_name]
    formation = get_team_formation(team_name)
    starting_eleven = select_players_by_formation(team.players, formation)
    
    # Return players with formation info
    result = {
        "formation": formation,
        "players": [asdict(player) for player in starting_eleven]
    }
    
    return result

@app.get("/teams/{team_name}/players")
async def get_team_players(team_name: str):
    """Get players for a specific team"""
    if team_name not in teams_data:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return [asdict(player) for player in teams_data[team_name].players]

@app.post("/simulate-match")
async def simulate_match(request: Dict[str, Any]):
    """Simulate a match between two teams with detailed events"""
    try:
        home_team = request.get("home_team")
        away_team = request.get("away_team")
        simulation_type = request.get("type", "detailed")  # "simple" or "detailed"
        
        if not home_team or not away_team:
            raise HTTPException(status_code=400, detail="Both home_team and away_team are required")
        
        if simulation_type == "simple":
            match = simulate_match_simple(home_team, away_team)
        else:
            match = simulate_match_detailed(home_team, away_team)
            
        return asdict(match)
        
    except Exception as e:
        logger.error(f"Error simulating match: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulate-live-match")
async def simulate_live_match(request: Dict[str, Any]):
    """Simulate a live match with real-time progression"""
    try:
        home_team = request.get("home_team")
        away_team = request.get("away_team")
        speed = request.get("speed", 1)  # Default speed is 1
        
        # Convert speed to int if it's a string
        if isinstance(speed, str):
            try:
                speed = int(speed)
            except ValueError:
                speed = 1
        
        if not home_team or not away_team:
            raise HTTPException(status_code=400, detail="Both home_team and away_team are required")
        
        # Get the full match simulation
        full_match = simulate_match_detailed(home_team, away_team)
        
        # For live simulation, we'll return the full match but mark it as live
        # The frontend can handle the time progression
        full_match.status = "LIVE"
        full_match.current_minute = 0
        
        return asdict(full_match)
        
    except Exception as e:
        logger.error(f"Error simulating live match: {e}")
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

# Load data on startup - manually call it here to avoid event loops
logger.info("🏆 Starting Football Simulator API...")
load_teams_from_csv()
logger.info(f"✅ Loaded {len(teams_data)} teams successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
