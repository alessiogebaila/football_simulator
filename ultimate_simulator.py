#!/usr/bin/env python3
"""
🏆 ULTIMATE FOOTBALL SIMULATOR
Enhanced with Real Data + Advanced Bayesian Learning + ML

This version includes:
- Real Transfermarkt-style player data
- Advanced Bayesian inference (with PyMC when available)
- Machine Learning predictions
- Interactive tournament simulation
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import random
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Try to import PyMC for advanced Bayesian modeling
try:
    import pymc as pm
    import pytensor.tensor as pt
    PYMC_AVAILABLE = True
    print("🧠 Advanced PyMC Bayesian modeling available!")
except ImportError:
    PYMC_AVAILABLE = False
    print("📊 Using simplified Bayesian modeling (PyMC not available)")

from enhanced_football_simulator import Player, Team, Match, Tournament, MatchPredictor

class AdvancedBayesianPredictor:
    """Advanced Bayesian match predictor with PyMC integration"""
    
    def __init__(self):
        self.team_strengths = {}
        self.match_history = []
        self.pymc_model = None
        
    def initialize_team_strength(self, team: Team):
        """Initialize team strength with enhanced priors"""
        if team.name not in self.team_strengths:
            # Calculate based on squad value and player ratings
            squad_value = sum(p.market_value_eur for p in team.players)
            avg_rating = np.mean([p.overall_rating for p in team.players])
            
            # Enhanced prior based on real data
            base_strength = np.log(squad_value / 10_000_000) * 0.3 + avg_rating * 0.02
            self.team_strengths[team.name] = {
                'attack': max(0.1, base_strength + np.random.normal(0, 0.2)),
                'defense': max(0.1, base_strength + np.random.normal(0, 0.2)),
                'confidence': 1.0,
                'form': 1.0
            }
    
    def predict_match_advanced(self, home_team: Team, away_team: Team) -> Tuple[int, int]:
        """Advanced match prediction using PyMC or simplified Bayesian"""
        self.initialize_team_strength(home_team)
        self.initialize_team_strength(away_team)
        
        if PYMC_AVAILABLE:
            return self._predict_with_pymc(home_team, away_team)
        else:
            return self._predict_simplified_bayesian(home_team, away_team)
    
    def _predict_with_pymc(self, home_team: Team, away_team: Team) -> Tuple[int, int]:
        """Advanced PyMC-based prediction"""
        try:
            home_strength = self.team_strengths[home_team.name]
            away_strength = self.team_strengths[away_team.name]
            
            with pm.Model() as match_model:
                # Home advantage
                home_advantage = pm.Normal('home_advantage', mu=0.3, sigma=0.1)
                
                # Team attack and defense strengths
                home_attack = pm.Normal('home_attack', 
                                      mu=home_strength['attack'], 
                                      sigma=0.2)
                away_attack = pm.Normal('away_attack', 
                                      mu=away_strength['attack'], 
                                      sigma=0.2)
                
                home_defense = pm.Normal('home_defense', 
                                       mu=home_strength['defense'], 
                                       sigma=0.2)
                away_defense = pm.Normal('away_defense', 
                                       mu=away_strength['defense'], 
                                       sigma=0.2)
                
                # Expected goals calculation
                home_expected_goals = pm.math.exp(home_attack - away_defense + home_advantage)
                away_expected_goals = pm.math.exp(away_attack - home_defense)
                
                # Poisson distribution for goals
                home_goals = pm.Poisson('home_goals', mu=home_expected_goals)
                away_goals = pm.Poisson('away_goals', mu=away_expected_goals)
                
                # Sample from the model
                with match_model:
                    trace = pm.sample(100, tune=50, cores=1, 
                                    progressbar=False, random_seed=42)
                    
                # Get predictions
                home_prediction = int(np.mean(trace.posterior['home_goals']))
                away_prediction = int(np.mean(trace.posterior['away_goals']))
                
                return max(0, home_prediction), max(0, away_prediction)
                
        except Exception as e:
            print(f"⚠️ PyMC prediction failed: {e}")
            return self._predict_simplified_bayesian(home_team, away_team)
    
    def _predict_simplified_bayesian(self, home_team: Team, away_team: Team) -> Tuple[int, int]:
        """Simplified Bayesian prediction (fallback)"""
        home_strength = self.team_strengths[home_team.name]
        away_strength = self.team_strengths[away_team.name]
        
        # Calculate expected goals using Poisson-like approach
        home_attack_power = home_strength['attack'] * home_strength['form']
        away_defense_power = away_strength['defense']
        home_expected = max(0.1, (home_attack_power / away_defense_power) * 1.3)  # Home advantage
        
        away_attack_power = away_strength['attack'] * away_strength['form']
        home_defense_power = home_strength['defense']
        away_expected = max(0.1, away_attack_power / home_defense_power)
        
        # Sample from Poisson-like distribution
        home_goals = max(0, int(np.random.poisson(home_expected)))
        away_goals = max(0, int(np.random.poisson(away_expected)))
        
        return home_goals, away_goals
    
    def update_from_match_result(self, match: Match):
        """Update team strengths based on match results"""
        home_name = match.home_team.name
        away_name = match.away_team.name
        
        # Learning rate
        lr = 0.1
        
        # Expected vs actual performance
        expected_home_goals = self.team_strengths[home_name]['attack'] * 1.3
        expected_away_goals = self.team_strengths[away_name]['attack']
        
        goal_diff_home = match.home_score - expected_home_goals
        goal_diff_away = match.away_score - expected_away_goals
        
        # Update attack and defense based on performance
        self.team_strengths[home_name]['attack'] += lr * goal_diff_home * 0.5
        self.team_strengths[home_name]['defense'] -= lr * goal_diff_away * 0.5
        
        self.team_strengths[away_name]['attack'] += lr * goal_diff_away * 0.5
        self.team_strengths[away_name]['defense'] -= lr * goal_diff_home * 0.5
        
        # Update form and confidence
        if match.home_score > match.away_score:
            self.team_strengths[home_name]['confidence'] *= 1.05
            self.team_strengths[away_name]['confidence'] *= 0.98
        elif match.away_score > match.home_score:
            self.team_strengths[away_name]['confidence'] *= 1.05
            self.team_strengths[home_name]['confidence'] *= 0.98
        
        # Clip values to reasonable ranges
        for team_name in [home_name, away_name]:
            for stat in ['attack', 'defense']:
                self.team_strengths[team_name][stat] = np.clip(
                    self.team_strengths[team_name][stat], 0.1, 3.0
                )
            self.team_strengths[team_name]['confidence'] = np.clip(
                self.team_strengths[team_name]['confidence'], 0.5, 2.0
            )


class UltimateTournament(Tournament):
    """Ultimate tournament with advanced Bayesian learning"""
    
    def __init__(self, name: str, teams: List[Team]):
        super().__init__(name, teams)
        self.advanced_predictor = AdvancedBayesianPredictor()
        self.ml_predictor = MatchPredictor()
        
        # Train ML model on historical data
        self._train_ml_model()
    
    def _train_ml_model(self):
        """Train ML model with enhanced features"""
        features = []
        results = []
        
        # Generate synthetic training data based on real squad values
        for _ in range(1000):
            team1, team2 = random.sample(self.teams, 2)
            
            # Enhanced features
            feature_vector = [
                sum(p.market_value_eur for p in team1.players) / 1_000_000,  # Squad value
                sum(p.market_value_eur for p in team2.players) / 1_000_000,
                np.mean([p.overall_rating for p in team1.players]),  # Avg rating
                np.mean([p.overall_rating for p in team2.players]),
                len(team1.players),  # Squad depth
                len(team2.players),
                sum(p.age for p in team1.players) / len(team1.players),  # Avg age
                sum(p.age for p in team2.players) / len(team2.players),
            ]
            
            features.append(feature_vector)
            
            # Simulate realistic result based on squad strength
            strength_diff = feature_vector[0] - feature_vector[1]
            result_prob = 1 / (1 + np.exp(-strength_diff * 0.01))
            results.append(1 if random.random() < result_prob else 0)
        
        self.ml_predictor.train(features, results)
    
    def predict_match_ultimate(self, home_team: Team, away_team: Team) -> Tuple[int, int]:
        """Ultimate prediction combining all methods"""
        # Get predictions from different models
        bayesian_prediction = self.advanced_predictor.predict_match_advanced(home_team, away_team)
        
        # ML prediction for result confidence
        ml_features = [
            sum(p.market_value_eur for p in home_team.players) / 1_000_000,
            sum(p.market_value_eur for p in away_team.players) / 1_000_000,
            np.mean([p.overall_rating for p in home_team.players]),
            np.mean([p.overall_rating for p in away_team.players]),
            len(home_team.players),
            len(away_team.players),
            sum(p.age for p in home_team.players) / len(home_team.players),
            sum(p.age for p in away_team.players) / len(away_team.players),
        ]
        
        ml_confidence = self.ml_predictor.predict_probability([ml_features])[0]
        
        # Weighted combination
        home_goals, away_goals = bayesian_prediction
        
        # Adjust based on ML confidence
        if ml_confidence > 0.7:  # High confidence in home win
            home_goals = max(home_goals, away_goals + 1)
        elif ml_confidence < 0.3:  # High confidence in away win
            away_goals = max(away_goals, home_goals + 1)
        
        return home_goals, away_goals
    
    def simulate_match(self, home_team: Team, away_team: Team) -> Match:
        """Simulate match with ultimate prediction"""
        home_score, away_score = self.predict_match_ultimate(home_team, away_team)
        match = Match(home_team, away_team, home_score, away_score)
        
        # Update Bayesian model
        self.advanced_predictor.update_from_match_result(match)
        
        return match
    
    def print_advanced_analysis(self):
        """Print advanced tournament analysis"""
        print("\n" + "="*60)
        print("🧠 ADVANCED BAYESIAN ANALYSIS")
        print("="*60)
        
        for team_name, strengths in self.advanced_predictor.team_strengths.items():
            print(f"\n{team_name}:")
            print(f"  🏈 Attack Strength: {strengths['attack']:.2f}")
            print(f"  🛡️  Defense Strength: {strengths['defense']:.2f}")
            print(f"  💪 Confidence: {strengths['confidence']:.2f}")
            print(f"  📈 Form: {strengths['form']:.2f}")


def create_player_from_csv_data(player_row) -> Player:
    """Create a Player object from CSV data"""
    # Calculate overall rating based on market value and age
    market_value_millions = player_row['market_value_eur'] / 1_000_000
    age = player_row['age']
    
    # Rating calculation: higher market value = higher rating, with age factor
    base_rating = min(99, max(50, 50 + np.log(market_value_millions + 1) * 8))
    
    # Age factor: peak at 25-28, decline after 30
    if age <= 20:
        age_factor = 0.85 + (age - 16) * 0.03  # Young potential
    elif age <= 28:
        age_factor = 1.0  # Peak years
    elif age <= 32:
        age_factor = 1.0 - (age - 28) * 0.05  # Slow decline
    else:
        age_factor = 0.8 - (age - 32) * 0.03  # Faster decline
    
    overall_rating = int(base_rating * age_factor)
    
    # Position-specific attributes
    position = player_row['position']
    if position == 'GK':
        attributes = {
            'pace': random.randint(30, 60),
            'shooting': random.randint(10, 30),
            'passing': random.randint(40, 80),
            'dribbling': random.randint(20, 50),
            'defending': random.randint(10, 30),
            'physical': random.randint(60, 90),
            'goalkeeping': random.randint(70, 95)
        }
    elif position in ['CB', 'LB', 'RB']:
        attributes = {
            'pace': random.randint(40, 85),
            'shooting': random.randint(20, 60),
            'passing': random.randint(50, 85),
            'dribbling': random.randint(30, 70),
            'defending': random.randint(70, 95),
            'physical': random.randint(70, 95),
            'goalkeeping': random.randint(5, 15)
        }
    elif position in ['CDM', 'CM', 'CAM']:
        attributes = {
            'pace': random.randint(50, 85),
            'shooting': random.randint(40, 90),
            'passing': random.randint(70, 95),
            'dribbling': random.randint(60, 90),
            'defending': random.randint(30, 80),
            'physical': random.randint(50, 85),
            'goalkeeping': random.randint(5, 15)
        }
    elif position in ['LW', 'RW']:
        attributes = {
            'pace': random.randint(70, 95),
            'shooting': random.randint(60, 90),
            'passing': random.randint(50, 85),
            'dribbling': random.randint(70, 95),
            'defending': random.randint(20, 50),
            'physical': random.randint(40, 80),
            'goalkeeping': random.randint(5, 15)
        }
    else:  # CF
        attributes = {
            'pace': random.randint(60, 90),
            'shooting': random.randint(75, 95),
            'passing': random.randint(50, 80),
            'dribbling': random.randint(60, 90),
            'defending': random.randint(15, 40),
            'physical': random.randint(70, 95),
            'goalkeeping': random.randint(5, 15)
        }
    
    return Player(
        name=player_row['player_name'],
        position=position,
        age=age,
        overall_rating=overall_rating,
        market_value_eur=player_row['market_value_eur'],
        nationality=player_row['nationality'],
        **attributes
    )


def create_ultimate_teams() -> List[Team]:
    """Create teams with real CSV data from final_transfermarkt_squads.csv"""
    try:
        # Load the CSV file
        df = pd.read_csv('final_transfermarkt_squads.csv')
        print(f"📊 Loaded {len(df)} players from CSV file")
        
        teams = []
        teams_data = df.groupby('club')
        
        for club_name, club_players in teams_data:
            team = Team(club_name)
            
            for _, player_row in club_players.iterrows():
                try:
                    player = create_player_from_csv_data(player_row)
                    team.add_player(player)
                except Exception as e:
                    print(f"⚠️ Error creating player {player_row.get('player_name', 'Unknown')}: {e}")
                    continue
            
            if len(team.players) > 0:  # Only add teams with players
                teams.append(team)
                print(f"✅ Created team {club_name} with {len(team.players)} players")
        
        print(f"🏆 Successfully created {len(teams)} teams from CSV data")
        return teams
        
    except FileNotFoundError:
        print("❌ Error: final_transfermarkt_squads.csv not found!")
        print("Please make sure the CSV file is in the current directory.")
        return []
    except Exception as e:
        print(f"❌ Error loading CSV data: {e}")
        return []


def main():
    """Main function for ultimate football simulator"""
    print("🏆" + "="*60 + "🏆")
    print("  ULTIMATE FOOTBALL SIMULATOR")
    print("  Real Data + Advanced Bayesian + Machine Learning")
    if PYMC_AVAILABLE:
        print("  🧠 Powered by PyMC Advanced Bayesian Modeling")
    else:
        print("  📊 Simplified Bayesian Modeling (PyMC not available)")
    print("🏆" + "="*60 + "🏆")
    
    # Create teams with real data
    teams = create_ultimate_teams()
    
    if not teams:
        print("❌ No teams could be loaded! Please check your CSV file.")
        return
    
    print(f"\n📊 Loaded {len(teams)} teams with real Transfermarkt data:")
    total_value = 0
    for team in teams:
        team_value = sum(p.market_value_eur for p in team.players)
        total_value += team_value
        print(f"  {team.name}: {len(team.players)} players, €{team_value/1_000_000:.0f}M value")
    
    print(f"\n💰 Total Squad Values: €{total_value/1_000_000:.0f} million")
    
    while True:
        print("\n" + "="*50)
        print("🎮 CHOOSE YOUR SIMULATION:")
        print("="*50)
        print("1. 🏆 Full Tournament (4 teams, complete season)")
        print("2. ⚡ Quick Match (any 2 teams)")
        print("3. 📊 Team Analysis & Statistics")
        print("4. 🧠 Advanced Bayesian Learning Demo")
        print("5. 📈 ML vs Bayesian Comparison")
        print("6. 🎯 Exit")
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                # Full tournament
                print(f"\n🏆 Starting Ultimate Champions League with {len(teams)} teams!")
                tournament = UltimateTournament("Ultimate Champions League", teams)
                tournament.start_tournament()
                tournament.print_advanced_analysis()
                
            elif choice == '2':
                # Quick match
                print("\n⚡ QUICK MATCH")
                print("Available teams:")
                for i, team in enumerate(teams, 1):
                    print(f"  {i}. {team.name}")
                
                try:
                    team1_idx = int(input("Select home team (number): ")) - 1
                    team2_idx = int(input("Select away team (number): ")) - 1
                    
                    if 0 <= team1_idx < len(teams) and 0 <= team2_idx < len(teams) and team1_idx != team2_idx:
                        home_team = teams[team1_idx]
                        away_team = teams[team2_idx]
                        
                        predictor = AdvancedBayesianPredictor()
                        home_goals, away_goals = predictor.predict_match_advanced(home_team, away_team)
                        
                        print(f"\n🎯 MATCH PREDICTION:")
                        print(f"  {home_team.name} {home_goals} - {away_goals} {away_team.name}")
                        
                        # Show detailed analysis
                        predictor.initialize_team_strength(home_team)
                        predictor.initialize_team_strength(away_team)
                        home_str = predictor.team_strengths[home_team.name]
                        away_str = predictor.team_strengths[away_team.name]
                        
                        print(f"\n📊 TEAM ANALYSIS:")
                        print(f"  {home_team.name}: Attack {home_str['attack']:.2f}, Defense {home_str['defense']:.2f}")
                        print(f"  {away_team.name}: Attack {away_str['attack']:.2f}, Defense {away_str['defense']:.2f}")
                    else:
                        print("❌ Invalid team selection!")
                except ValueError:
                    print("❌ Please enter valid numbers!")
            
            elif choice == '3':
                # Team analysis
                print("\n📊 TEAM ANALYSIS")
                for team in teams:
                    print(f"\n{'='*40}")
                    print(f"🏈 {team.name}")
                    print(f"{'='*40}")
                    
                    team_value = sum(p.market_value_eur for p in team.players)
                    avg_age = sum(p.age for p in team.players) / len(team.players)
                    avg_rating = np.mean([p.overall_rating for p in team.players])
                    
                    print(f"💰 Squad Value: €{team_value/1_000_000:.1f}M")
                    print(f"👥 Players: {len(team.players)}")
                    print(f"📊 Average Rating: {avg_rating:.1f}")
                    print(f"🎂 Average Age: {avg_age:.1f}")
                    
                    # Top 3 most valuable players
                    top_players = sorted(team.players, key=lambda p: p.market_value_eur, reverse=True)[:3]
                    print(f"⭐ Top Players:")
                    for i, player in enumerate(top_players, 1):
                        print(f"  {i}. {player.name} - €{player.market_value_eur/1_000_000:.1f}M")
            
            elif choice == '4':
                # Advanced Bayesian demo
                print("\n🧠 ADVANCED BAYESIAN LEARNING DEMO")
                predictor = AdvancedBayesianPredictor()
                
                # Show initial predictions
                team1, team2 = teams[0], teams[1]
                print(f"\n📊 Initial prediction: {team1.name} vs {team2.name}")
                initial_pred = predictor.predict_match_advanced(team1, team2)
                print(f"  Prediction: {team1.name} {initial_pred[0]} - {initial_pred[1]} {team2.name}")
                
                # Simulate some matches and show learning
                print(f"\n🎮 Simulating matches and learning...")
                for i in range(5):
                    home_goals, away_goals = predictor.predict_match_advanced(team1, team2)
                    match = Match(team1, team2, home_goals, away_goals)
                    predictor.update_from_match_result(match)
                    print(f"  Match {i+1}: {team1.name} {home_goals} - {away_goals} {team2.name}")
                
                # Show updated prediction
                print(f"\n📈 After learning - New prediction:")
                final_pred = predictor.predict_match_advanced(team1, team2)
                print(f"  Prediction: {team1.name} {final_pred[0]} - {final_pred[1]} {team2.name}")
                
                # Show team strength evolution
                print(f"\n🧠 Team Strength Evolution:")
                for team_name in [team1.name, team2.name]:
                    strengths = predictor.team_strengths[team_name]
                    print(f"  {team_name}:")
                    print(f"    Attack: {strengths['attack']:.3f}")
                    print(f"    Defense: {strengths['defense']:.3f}")
                    print(f"    Confidence: {strengths['confidence']:.3f}")
            
            elif choice == '5':
                # ML vs Bayesian comparison
                print("\n📈 ML vs BAYESIAN COMPARISON")
                tournament = UltimateTournament("Comparison Test", teams[:2])
                
                team1, team2 = teams[0], teams[1]
                print(f"\nComparing predictions for: {team1.name} vs {team2.name}")
                
                # Bayesian prediction
                bayesian_pred = tournament.advanced_predictor.predict_match_advanced(team1, team2)
                print(f"🧠 Bayesian: {team1.name} {bayesian_pred[0]} - {bayesian_pred[1]} {team2.name}")
                
                # Ultimate prediction (combined)
                ultimate_pred = tournament.predict_match_ultimate(team1, team2)
                print(f"🎯 Ultimate: {team1.name} {ultimate_pred[0]} - {ultimate_pred[1]} {team2.name}")
                
                # Show reasoning
                ml_features = [
                    sum(p.market_value_eur for p in team1.players) / 1_000_000,
                    sum(p.market_value_eur for p in team2.players) / 1_000_000,
                    np.mean([p.overall_rating for p in team1.players]),
                    np.mean([p.overall_rating for p in team2.players]),
                    len(team1.players), len(team2.players),
                    sum(p.age for p in team1.players) / len(team1.players),
                    sum(p.age for p in team2.players) / len(team2.players),
                ]
                
                ml_confidence = tournament.ml_predictor.predict_probability([ml_features])[0]
                print(f"\n📊 Analysis:")
                print(f"  ML Confidence in {team1.name} win: {ml_confidence:.1%}")
                print(f"  Squad Value Ratio: {ml_features[0]/ml_features[1]:.2f}")
                print(f"  Rating Difference: {ml_features[2] - ml_features[3]:.1f}")
            
            elif choice == '6':
                print("\n👋 Thanks for using the Ultimate Football Simulator!")
                print("🏆 May the best team win! ⚽")
                break
            
            else:
                print("❌ Invalid choice! Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
