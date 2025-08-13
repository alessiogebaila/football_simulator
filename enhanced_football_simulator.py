import time
import random
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
import math

@dataclass
class PlayerStats:
    name: str
    position: str  # GK, DEF, MID, FWD
    overall_rating: int  # 1-100
    pace: int
    shooting: int
    passing: int
    dribbling: int
    defending: int
    physical: int
    market_value: float  # in millions
    age: int
    form: int  # Current form 1-10
    
    def __post_init__(self):
        # Ensure stats are within bounds
        for attr in ['overall_rating', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physical']:
            setattr(self, attr, max(1, min(100, getattr(self, attr))))
        self.form = max(1, min(10, self.form))

class Player:
    def __init__(self, stats: PlayerStats):
        self.stats = stats
        self.goals_scored = 0
        self.assists = 0
        self.yellow_cards = 0
        self.red_cards = 0
        self.minutes_played = 0
        self.is_injured = False
        self.fitness = 100  # 0-100

    def __str__(self):
        return f"{self.stats.name} ({self.stats.position}) - {self.stats.overall_rating}"

    def get_match_performance(self) -> float:
        """Calculate player performance for current match based on form, fitness, and randomness"""
        base_performance = self.stats.overall_rating
        form_modifier = (self.stats.form - 5) * 2  # -8 to +10
        fitness_modifier = (self.fitness - 80) * 0.1  # -8 to +2
        random_modifier = random.uniform(-5, 5)
        
        performance = base_performance + form_modifier + fitness_modifier + random_modifier
        return max(20, min(100, performance))

class Team:
    def __init__(self, name: str, country: str = "Unknown"):
        self.team_name = name
        self.country = country
        self.players: List[Player] = []
        self.formation = "4-4-2"  # Default formation
        self.starting_eleven: List[Player] = []
        self.bench: List[Player] = []
        self.team_chemistry = 75  # 0-100
        self.manager_rating = 75  # 0-100
        self.home_advantage = 5  # Bonus when playing at home
        
    def __str__(self):
        return f"{self.team_name}"
    
    def add_player(self, player: Player):
        self.players.append(player)
    
    def get_team_strength(self) -> float:
        """Calculate overall team strength based on starting eleven"""
        if not self.starting_eleven:
            self.select_starting_eleven()
        
        total_performance = sum(player.get_match_performance() for player in self.starting_eleven)
        avg_performance = total_performance / len(self.starting_eleven)
        
        # Add team chemistry and manager bonuses
        chemistry_bonus = (self.team_chemistry - 50) * 0.2
        manager_bonus = (self.manager_rating - 50) * 0.1
        
        return avg_performance + chemistry_bonus + manager_bonus
    
    def select_starting_eleven(self):
        """Select best 11 players based on position and performance"""
        if len(self.players) < 11:
            self.starting_eleven = self.players[:11]
            return
        
        # Sort players by position and performance
        goalkeepers = [p for p in self.players if p.stats.position == "GK"]
        defenders = [p for p in self.players if p.stats.position == "DEF"]
        midfielders = [p for p in self.players if p.stats.position == "MID"]
        forwards = [p for p in self.players if p.stats.position == "FWD"]
        
        # Sort by performance
        goalkeepers.sort(key=lambda x: x.get_match_performance(), reverse=True)
        defenders.sort(key=lambda x: x.get_match_performance(), reverse=True)
        midfielders.sort(key=lambda x: x.get_match_performance(), reverse=True)
        forwards.sort(key=lambda x: x.get_match_performance(), reverse=True)
        
        # Select starting eleven based on formation (4-4-2)
        starting_eleven = []
        starting_eleven.append(goalkeepers[0] if goalkeepers else None)
        starting_eleven.extend(defenders[:4] if len(defenders) >= 4 else defenders)
        starting_eleven.extend(midfielders[:4] if len(midfielders) >= 4 else midfielders)
        starting_eleven.extend(forwards[:2] if len(forwards) >= 2 else forwards)
        
        # Fill remaining spots with best available players
        used_players = set(starting_eleven)
        remaining_players = [p for p in self.players if p not in used_players]
        remaining_players.sort(key=lambda x: x.get_match_performance(), reverse=True)
        
        while len(starting_eleven) < 11 and remaining_players:
            starting_eleven.append(remaining_players.pop(0))
        
        self.starting_eleven = [p for p in starting_eleven if p is not None]
        self.bench = [p for p in self.players if p not in self.starting_eleven]
    
    def get_squad_value(self) -> float:
        """Calculate total squad market value"""
        return sum(player.stats.market_value for player in self.players)

class MatchStats:
    def __init__(self):
        self.possession_home = 50
        self.possession_away = 50
        self.shots_home = 0
        self.shots_away = 0
        self.shots_on_target_home = 0
        self.shots_on_target_away = 0
        self.corners_home = 0
        self.corners_away = 0
        self.fouls_home = 0
        self.fouls_away = 0
        self.yellow_cards_home = 0
        self.yellow_cards_away = 0
        self.red_cards_home = 0
        self.red_cards_away = 0

class MatchPredictor:
    def __init__(self):
        self.model = LogisticRegression()
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def generate_training_data(self, num_samples=1000):
        """Generate synthetic training data for the ML model"""
        data = []
        
        for _ in range(num_samples):
            # Generate random team strengths
            home_strength = random.uniform(60, 95)
            away_strength = random.uniform(60, 95)
            
            # Home advantage
            home_advantage = random.uniform(3, 7)
            
            # Squad value difference (normalized)
            value_diff = random.uniform(-50, 50)
            
            # Recent form difference
            form_diff = random.uniform(-20, 20)
            
            # Calculate probability based on these factors
            strength_diff = home_strength - away_strength + home_advantage
            total_factor = strength_diff + value_diff * 0.1 + form_diff * 0.1
            
            # Convert to win probability (sigmoid-like function)
            home_win_prob = 1 / (1 + math.exp(-total_factor * 0.1))
            
            # Determine outcome
            rand = random.random()
            if rand < home_win_prob * 0.6:  # Home win
                outcome = 1
            elif rand < home_win_prob * 0.6 + 0.25:  # Draw
                outcome = 0
            else:  # Away win
                outcome = -1
            
            data.append([
                home_strength, away_strength, home_advantage, 
                value_diff, form_diff, outcome
            ])
        
        return np.array(data)
    
    def train_model(self):
        """Train the ML model on synthetic data"""
        data = self.generate_training_data()
        X = data[:, :-1]  # Features
        y = data[:, -1]   # Target (1: home win, 0: draw, -1: away win)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        print("ML model trained successfully!")
    
    def predict_match_outcome(self, home_team: Team, away_team: Team, is_home_game=True) -> Dict[str, float]:
        """Predict match outcome probabilities"""
        if not self.is_trained:
            self.train_model()
        
        # Calculate features
        home_strength = home_team.get_team_strength()
        away_strength = away_team.get_team_strength()
        home_advantage = home_team.home_advantage if is_home_game else 0
        
        # Squad value difference (in millions)
        home_value = home_team.get_squad_value()
        away_value = away_team.get_squad_value()
        value_diff = home_value - away_value
        
        # Form difference (simplified)
        home_form = np.mean([p.stats.form for p in home_team.starting_eleven])
        away_form = np.mean([p.stats.form for p in away_team.starting_eleven])
        form_diff = home_form - away_form
        
        # Prepare features
        features = np.array([[home_strength, away_strength, home_advantage, value_diff, form_diff]])
        features_scaled = self.scaler.transform(features)
        
        # Get probabilities
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Map to outcomes
        classes = self.model.classes_
        prob_dict = {}
        
        for i, cls in enumerate(classes):
            if cls == 1:
                prob_dict['home_win'] = probabilities[i]
            elif cls == 0:
                prob_dict['draw'] = probabilities[i]
            elif cls == -1:
                prob_dict['away_win'] = probabilities[i]
        
        # Ensure all outcomes are present
        if 'home_win' not in prob_dict:
            prob_dict['home_win'] = 0.0
        if 'draw' not in prob_dict:
            prob_dict['draw'] = 0.0
        if 'away_win' not in prob_dict:
            prob_dict['away_win'] = 0.0
        
        return prob_dict

class Score:
    def __init__(self, home=0, away=0):
        self._home_goals = home
        self._away_goals = away
        self.scoring_minutes = []
        self.goal_scorers = []
        self.assist_providers = []

    def __str__(self):
        return f"{self._home_goals} - {self._away_goals}"

    def home_goal(self, minute, scorer=None, assister=None):
        self._home_goals += 1
        self.scoring_minutes.append(minute)
        if scorer:
            self.goal_scorers.append((minute, scorer, 'home'))
            scorer.goals_scored += 1
        if assister:
            self.assist_providers.append((minute, assister, 'home'))
            assister.assists += 1

    def away_goal(self, minute, scorer=None, assister=None):
        self._away_goals += 1
        self.scoring_minutes.append(minute)
        if scorer:
            self.goal_scorers.append((minute, scorer, 'away'))
            scorer.goals_scored += 1
        if assister:
            self.assist_providers.append((minute, assister, 'away'))
            assister.assists += 1

class Match:
    DURATION = 9  # seconds for simulation
    
    def __init__(self, home_team: Team, away_team: Team, predictor: MatchPredictor = None):
        self.home_team = home_team
        self.away_team = away_team
        self.score = Score()
        self.minute = 0
        self.match_stats = MatchStats()
        self.predictor = predictor or MatchPredictor()
        self.is_home_game = True
        
        # Ensure teams have starting elevens
        self.home_team.select_starting_eleven()
        self.away_team.select_starting_eleven()
        
        # Get match predictions
        self.predictions = self.predictor.predict_match_outcome(home_team, away_team, self.is_home_game)

    def __str__(self):
        return f"{self.home_team} {self.score} {self.away_team}"

    def display_pre_match_info(self):
        """Display pre-match analysis and predictions"""
        print(f"\n{'='*60}")
        print(f"MATCH PREVIEW: {self.home_team} vs {self.away_team}")
        print(f"{'='*60}")
        
        # Team strengths
        home_strength = self.home_team.get_team_strength()
        away_strength = self.away_team.get_team_strength()
        print(f"Team Strength: {self.home_team.team_name}: {home_strength:.1f} | {self.away_team.team_name}: {away_strength:.1f}")
        
        # Squad values
        home_value = self.home_team.get_squad_value()
        away_value = self.away_team.get_squad_value()
        print(f"Squad Value: {self.home_team.team_name}: €{home_value:.1f}M | {self.away_team.team_name}: €{away_value:.1f}M")
        
        # Predictions
        print(f"\nMATCH PREDICTIONS:")
        print(f"Home Win ({self.home_team.team_name}): {self.predictions.get('home_win', 0)*100:.1f}%")
        print(f"Draw: {self.predictions.get('draw', 0)*100:.1f}%")
        print(f"Away Win ({self.away_team.team_name}): {self.predictions.get('away_win', 0)*100:.1f}%")
        
        # Starting lineups
        print(f"\nSTARTING LINEUPS:")
        print(f"{self.home_team.team_name}:")
        for player in self.home_team.starting_eleven:
            print(f"  {player.stats.name} ({player.stats.position}) - {player.stats.overall_rating}")
        
        print(f"\n{self.away_team.team_name}:")
        for player in self.away_team.starting_eleven:
            print(f"  {player.stats.name} ({player.stats.position}) - {player.stats.overall_rating}")
        
        print(f"\n{'='*60}")

    def start(self):
        self.display_pre_match_info()
        self.start_time = time.time()
        print(f"\n🏟️  KICK OFF! {self.home_team} vs {self.away_team}")
        print(f"📊 Current Score: {self.score}")
        self.trigger_event()
        
    def trigger_event(self):
        self.last_time = time.time()
        self.sleep_time = random.uniform(0.5, 2.0)
        
        if self.sleep_time + time.time() > self.start_time + Match.DURATION:
            self.end_match()
            return

        time.sleep(self.sleep_time)
        print(f"⏱️  {self.current_minute()}'")

        # Calculate event probabilities based on team strengths
        home_strength = self.home_team.get_team_strength()
        away_strength = self.away_team.get_team_strength()
        
        # Event probabilities
        events = []
        
        # Goal events (more likely for stronger teams)
        goal_prob_home = 0.15 * (home_strength / 80)
        goal_prob_away = 0.15 * (away_strength / 80)
        
        events.extend([self.home_goal] * int(goal_prob_home * 100))
        events.extend([self.away_goal] * int(goal_prob_away * 100))
        
        # Other events
        events.extend([self.card_event] * 10)
        events.extend([self.general_play] * 70)
        
        if events:
            event = random.choice(events)
            event()

        print(f"📊 {self}")
        self.trigger_event()

    def home_goal(self):
        minute = self.current_minute()
        
        # Select random scorer from forwards/midfielders
        potential_scorers = [p for p in self.home_team.starting_eleven 
                           if p.stats.position in ['FWD', 'MID']]
        if not potential_scorers:
            potential_scorers = self.home_team.starting_eleven
        
        # Weight selection by shooting ability
        weights = [p.stats.shooting + p.get_match_performance() * 0.1 for p in potential_scorers]
        scorer = random.choices(potential_scorers, weights=weights)[0]
        
        # Potential assister
        assister = None
        if random.random() < 0.7:  # 70% chance of assist
            potential_assisters = [p for p in self.home_team.starting_eleven 
                                 if p != scorer and p.stats.position in ['MID', 'FWD', 'DEF']]
            if potential_assisters:
                assist_weights = [p.stats.passing for p in potential_assisters]
                assister = random.choices(potential_assisters, weights=assist_weights)[0]
        
        print(f"⚽ GOOOOOAL! {scorer.stats.name} scores for {self.home_team}! {minute}'")
        if assister:
            print(f"👏 Assist by {assister.stats.name}")
        
        self.score.home_goal(minute, scorer, assister)
        self.match_stats.shots_home += 1
        self.match_stats.shots_on_target_home += 1

    def away_goal(self):
        minute = self.current_minute()
        
        # Select random scorer from forwards/midfielders
        potential_scorers = [p for p in self.away_team.starting_eleven 
                           if p.stats.position in ['FWD', 'MID']]
        if not potential_scorers:
            potential_scorers = self.away_team.starting_eleven
        
        # Weight selection by shooting ability
        weights = [p.stats.shooting + p.get_match_performance() * 0.1 for p in potential_scorers]
        scorer = random.choices(potential_scorers, weights=weights)[0]
        
        # Potential assister
        assister = None
        if random.random() < 0.7:  # 70% chance of assist
            potential_assisters = [p for p in self.away_team.starting_eleven 
                                 if p != scorer and p.stats.position in ['MID', 'FWD', 'DEF']]
            if potential_assisters:
                assist_weights = [p.stats.passing for p in potential_assisters]
                assister = random.choices(potential_assisters, weights=assist_weights)[0]
        
        print(f"⚽ GOOOOOAL! {scorer.stats.name} scores for {self.away_team}! {minute}'")
        if assister:
            print(f"👏 Assist by {assister.stats.name}")
        
        self.score.away_goal(minute, scorer, assister)
        self.match_stats.shots_away += 1
        self.match_stats.shots_on_target_away += 1

    def card_event(self):
        teams = [(self.home_team, 'home'), (self.away_team, 'away')]
        team, team_type = random.choice(teams)
        player = random.choice(team.starting_eleven)
        
        card_type = random.choices(['yellow', 'red'], weights=[85, 15])[0]
        minute = self.current_minute()
        
        if card_type == 'yellow':
            player.yellow_cards += 1
            if team_type == 'home':
                self.match_stats.yellow_cards_home += 1
            else:
                self.match_stats.yellow_cards_away += 1
            print(f"🟡 Yellow card for {player.stats.name} ({team.team_name}) {minute}'")
        else:
            player.red_cards += 1
            if team_type == 'home':
                self.match_stats.red_cards_home += 1
            else:
                self.match_stats.red_cards_away += 1
            print(f"🟥 Red card for {player.stats.name} ({team.team_name}) {minute}'")

    def general_play(self):
        """Simulate general play events"""
        events = ['shot_off_target', 'corner', 'foul', 'possession_change']
        event = random.choice(events)
        
        if event == 'shot_off_target':
            team = random.choice([self.home_team, self.away_team])
            if team == self.home_team:
                self.match_stats.shots_home += 1
            else:
                self.match_stats.shots_away += 1
        elif event == 'corner':
            team = random.choice([self.home_team, self.away_team])
            if team == self.home_team:
                self.match_stats.corners_home += 1
            else:
                self.match_stats.corners_away += 1
        elif event == 'foul':
            team = random.choice([self.home_team, self.away_team])
            if team == self.home_team:
                self.match_stats.fouls_home += 1
            else:
                self.match_stats.fouls_away += 1

    def current_minute(self):
        elapsed = time.time() - self.start_time
        return int((elapsed / Match.DURATION) * 90) + 1

    def end_match(self):
        print(f"\n🏁 FULL TIME! Final Score: {self}")
        self.display_match_stats()

    def display_match_stats(self):
        """Display detailed match statistics"""
        print(f"\n📈 MATCH STATISTICS")
        print(f"{'='*50}")
        print(f"{'Statistic':<20} {self.home_team.team_name:<15} {self.away_team.team_name}")
        print(f"{'='*50}")
        print(f"{'Goals':<20} {self.score._home_goals:<15} {self.score._away_goals}")
        print(f"{'Shots':<20} {self.match_stats.shots_home:<15} {self.match_stats.shots_away}")
        print(f"{'Shots on Target':<20} {self.match_stats.shots_on_target_home:<15} {self.match_stats.shots_on_target_away}")
        print(f"{'Corners':<20} {self.match_stats.corners_home:<15} {self.match_stats.corners_away}")
        print(f"{'Fouls':<20} {self.match_stats.fouls_home:<15} {self.match_stats.fouls_away}")
        print(f"{'Yellow Cards':<20} {self.match_stats.yellow_cards_home:<15} {self.match_stats.yellow_cards_away}")
        print(f"{'Red Cards':<20} {self.match_stats.red_cards_home:<15} {self.match_stats.red_cards_away}")
        
        # Goal scorers
        if self.score.goal_scorers:
            print(f"\n⚽ GOAL SCORERS:")
            for minute, scorer, team_type in self.score.goal_scorers:
                team_name = self.home_team.team_name if team_type == 'home' else self.away_team.team_name
                print(f"  {minute}' {scorer.stats.name} ({team_name})")

    def winner(self):
        if self.score._home_goals > self.score._away_goals:
            print(f"🏆 Victory for {self.home_team}!\n")
            return self.home_team
        elif self.score._home_goals < self.score._away_goals:
            print(f"🏆 Victory for {self.away_team}!\n")
            return self.away_team
        else:
            print("⚖️  Match ended in a draw! Going to penalty shootout...")
            return self.penalty_shootout()

    def penalty_shootout(self):
        print(f"\n🥅 PENALTY SHOOTOUT")
        print(f"{self.home_team} vs {self.away_team}")
        print("=" * 40)
        
        home_penalties = 0
        away_penalties = 0
        
        # Standard 5 penalties each
        for i in range(5):
            # Home team penalty
            home_taker = random.choice([p for p in self.home_team.starting_eleven 
                                      if p.stats.position in ['FWD', 'MID']])
            penalty_skill = (home_taker.stats.shooting + home_taker.get_match_performance()) / 2
            if random.random() < (penalty_skill / 100) * 0.8:  # 80% base success rate adjusted by skill
                home_penalties += 1
                print(f"⚽ {home_taker.stats.name} scores for {self.home_team}!")
            else:
                print(f"❌ {home_taker.stats.name} misses for {self.home_team}!")
            
            print(f"Score: {home_penalties} - {away_penalties}")
            time.sleep(1)
            
            # Away team penalty
            away_taker = random.choice([p for p in self.away_team.starting_eleven 
                                      if p.stats.position in ['FWD', 'MID']])
            penalty_skill = (away_taker.stats.shooting + away_taker.get_match_performance()) / 2
            if random.random() < (penalty_skill / 100) * 0.8:
                away_penalties += 1
                print(f"⚽ {away_taker.stats.name} scores for {self.away_team}!")
            else:
                print(f"❌ {away_taker.stats.name} misses for {self.away_team}!")
            
            print(f"Score: {home_penalties} - {away_penalties}")
            time.sleep(1)
            
            # Check if one team has already won
            remaining_penalties = 5 - (i + 1)
            if home_penalties - away_penalties > remaining_penalties:
                break
            elif away_penalties - home_penalties > remaining_penalties:
                break
        
        # Sudden death if tied
        while home_penalties == away_penalties:
            print("\n🔥 SUDDEN DEATH!")
            
            # Home penalty
            home_taker = random.choice(self.home_team.starting_eleven)
            if random.random() < 0.75:
                home_penalties += 1
                print(f"⚽ {home_taker.stats.name} scores for {self.home_team}!")
            else:
                print(f"❌ {home_taker.stats.name} misses for {self.home_team}!")
            
            # Away penalty
            away_taker = random.choice(self.away_team.starting_eleven)
            if random.random() < 0.75:
                away_penalties += 1
                print(f"⚽ {away_taker.stats.name} scores for {self.away_team}!")
            else:
                print(f"❌ {away_taker.stats.name} misses for {self.away_team}!")
            
            print(f"Score: {home_penalties} - {away_penalties}")
            time.sleep(1)
        
        print(f"\n🏁 PENALTY SHOOTOUT RESULT: {self.home_team} {home_penalties} - {away_penalties} {self.away_team}")
        
        if home_penalties > away_penalties:
            print(f"🏆 {self.home_team} wins on penalties!")
            return self.home_team
        else:
            print(f"🏆 {self.away_team} wins on penalties!")
            return self.away_team


def create_sample_players():
    """Create sample players for demonstration"""
    
    # Manchester City players
    mci_players = [
        PlayerStats("Erling Haaland", "FWD", 91, 89, 92, 65, 80, 45, 88, 180.0, 24, 9),
        PlayerStats("Kevin De Bruyne", "MID", 89, 68, 86, 93, 87, 64, 78, 100.0, 32, 8),
        PlayerStats("Rodri", "MID", 87, 62, 75, 90, 81, 84, 82, 90.0, 27, 8),
        PlayerStats("Ruben Dias", "DEF", 86, 61, 48, 71, 70, 91, 85, 75.0, 26, 8),
        PlayerStats("Ederson", "GK", 85, 87, 75, 85, 82, 62, 86, 40.0, 30, 7),
        PlayerStats("Jack Grealish", "MID", 84, 82, 74, 86, 90, 52, 71, 70.0, 28, 7),
        PlayerStats("John Stones", "DEF", 83, 70, 58, 83, 75, 88, 81, 55.0, 29, 7),
        PlayerStats("Bernardo Silva", "MID", 86, 75, 82, 89, 91, 61, 73, 80.0, 29, 8),
        PlayerStats("Nathan Ake", "DEF", 82, 78, 55, 76, 73, 86, 79, 45.0, 28, 7),
        PlayerStats("Kyle Walker", "DEF", 81, 91, 52, 68, 71, 82, 77, 35.0, 33, 6),
        PlayerStats("Julian Alvarez", "FWD", 83, 83, 85, 81, 86, 55, 76, 75.0, 24, 8)
    ]
    
    # FC Barcelona players
    fcb_players = [
        PlayerStats("Robert Lewandowski", "FWD", 89, 78, 91, 79, 85, 44, 82, 50.0, 35, 8),
        PlayerStats("Pedri", "MID", 85, 74, 76, 89, 90, 59, 68, 80.0, 21, 9),
        PlayerStats("Gavi", "MID", 82, 81, 73, 86, 88, 64, 72, 90.0, 19, 8),
        PlayerStats("Ronald Araujo", "DEF", 83, 82, 51, 73, 71, 89, 86, 70.0, 24, 7),
        PlayerStats("Marc-Andre ter Stegen", "GK", 84, 68, 79, 88, 84, 58, 83, 30.0, 31, 7),
        PlayerStats("Frenkie de Jong", "MID", 84, 76, 77, 87, 89, 72, 79, 85.0, 26, 7),
        PlayerStats("Jules Kounde", "DEF", 82, 85, 56, 75, 74, 87, 78, 60.0, 24, 7),
        PlayerStats("Raphinha", "FWD", 81, 86, 80, 83, 88, 38, 74, 65.0, 26, 7),
        PlayerStats("Lamine Yamal", "FWD", 79, 88, 78, 82, 91, 32, 65, 120.0, 17, 9),
        PlayerStats("Alejandro Balde", "DEF", 78, 89, 61, 78, 76, 79, 74, 40.0, 20, 8),
        PlayerStats("Ferran Torres", "FWD", 80, 83, 82, 81, 85, 45, 71, 55.0, 24, 6)
    ]
    
    return mci_players, fcb_players

def create_teams_with_players():
    """Create sample teams with realistic players"""
    
    # Create predictor
    predictor = MatchPredictor()
    
    # Create Manchester City
    mci = Team("Manchester City", "England")
    mci_players, _ = create_sample_players()
    for player_stats in mci_players:
        mci.add_player(Player(player_stats))
    
    # Create FC Barcelona
    fcb = Team("FC Barcelona", "Spain")
    _, fcb_players = create_sample_players()
    for player_stats in fcb_players:
        fcb.add_player(Player(player_stats))
    
    return mci, fcb, predictor

# Example usage
if __name__ == "__main__":
    print("🏟️  ENHANCED FOOTBALL SIMULATOR")
    print("================================")
    
    # Create teams
    mci, fcb, predictor = create_teams_with_players()
    
    # Create and start a match
    match = Match(mci, fcb, predictor)
    match.start()
    
    # Determine winner
    winner = match.winner()
    
    if winner:
        print(f"\n🎉 Tournament continues with {winner}!")
