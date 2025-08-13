"""
Bayesian Football Simulator
Integrates Bayesian inference with the enhanced football simulator for realistic team strength updates
"""

import numpy as np
try:
    import pymc as pm
    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False
    print("⚠️  PyMC not available. Using simplified Bayesian updates.")
    print("   To install PyMC, run: pip install pymc")

import warnings
warnings.filterwarnings("ignore")
from enhanced_football_simulator import *
from tournament import Tournament, create_world_class_teams
import pandas as pd
from typing import List, Dict, Tuple, Optional
import pickle
import os

class BayesianMatchPredictor:
    """Enhanced match predictor using Bayesian inference to update team strengths"""
    
    def __init__(self, teams: List[Team]):
        self.teams = teams
        self.n_teams = len(teams)
        self.team_index = {team.team_name: i for i, team in enumerate(teams)}
        self.team_names = [team.team_name for team in teams]
        
        # Initialize Bayesian parameters
        self.attack_strength = np.zeros(self.n_teams)
        self.defense_strength = np.zeros(self.n_teams)
        self.home_advantage = 0.3
        
        # Match history for Bayesian updates
        self.match_history = []
        self.is_trained = False
        
        # Performance tracking
        self.team_performance_history = {team.team_name: [] for team in teams}
        
    def initialize_priors_from_teams(self):
        """Initialize Bayesian priors based on team squad values and ratings"""
        print("🧠 Initializing Bayesian priors from team data...")
        
        # Calculate initial strengths based on squad value and team strength
        squad_values = [team.get_squad_value() for team in self.teams]
        team_strengths = [team.get_team_strength() for team in self.teams]
        
        # Normalize to get relative strengths
        avg_value = np.mean(squad_values)
        avg_strength = np.mean(team_strengths)
        
        for i, team in enumerate(self.teams):
            # Attack strength based on forward/midfield quality
            forwards = [p for p in team.players if p.stats.position in ['FWD', 'MID']]
            attack_rating = np.mean([p.stats.shooting + p.stats.pace for p in forwards]) if forwards else 70
            self.attack_strength[i] = (attack_rating - 75) / 20  # Normalize around 0
            
            # Defense strength based on defensive players
            defenders = [p for p in team.players if p.stats.position in ['DEF', 'GK']]
            defense_rating = np.mean([p.stats.defending + p.stats.physical for p in defenders]) if defenders else 70
            self.defense_strength[i] = (defense_rating - 75) / 20  # Normalize around 0
            
            # Adjust for squad value
            value_factor = (team.get_squad_value() - avg_value) / avg_value * 0.2
            self.attack_strength[i] += value_factor
            self.defense_strength[i] += value_factor
        
        print(f"✅ Initial attack strengths: {dict(zip(self.team_names, self.attack_strength.round(2)))}")
        print(f"✅ Initial defense strengths: {dict(zip(self.team_names, self.defense_strength.round(2)))}")
    
    def predict_goals_bayesian(self, home_team: str, away_team: str) -> Tuple[int, int]:
        """Predict goals using Bayesian model with Poisson distribution"""
        i_home = self.team_index[home_team]
        i_away = self.team_index[away_team]
        
        # Calculate expected goals using current Bayesian estimates
        lambda_home = np.exp(self.home_advantage + self.attack_strength[i_home] - self.defense_strength[i_away])
        lambda_away = np.exp(self.attack_strength[i_away] - self.defense_strength[i_home])
        
        # Ensure reasonable bounds
        lambda_home = np.clip(lambda_home, 0.3, 4.0)
        lambda_away = np.clip(lambda_away, 0.3, 4.0)
        
        # Sample goals from Poisson distribution
        goals_home = np.random.poisson(lambda_home)
        goals_away = np.random.poisson(lambda_away)
        
        return goals_home, goals_away, lambda_home, lambda_away
    
    def get_match_probabilities(self, home_team: str, away_team: str) -> Dict[str, float]:
        """Calculate match outcome probabilities using Bayesian model"""
        i_home = self.team_index[home_team]
        i_away = self.team_index[away_team]
        
        # Calculate expected goals
        lambda_home = np.exp(self.home_advantage + self.attack_strength[i_home] - self.defense_strength[i_away])
        lambda_away = np.exp(self.attack_strength[i_away] - self.defense_strength[i_home])
        
        # Ensure reasonable bounds
        lambda_home = np.clip(lambda_home, 0.3, 4.0)
        lambda_away = np.clip(lambda_away, 0.3, 4.0)
        
        # Monte Carlo simulation to estimate probabilities
        n_simulations = 1000
        home_wins = 0
        draws = 0
        away_wins = 0
        
        for _ in range(n_simulations):
            goals_home = np.random.poisson(lambda_home)
            goals_away = np.random.poisson(lambda_away)
            
            if goals_home > goals_away:
                home_wins += 1
            elif goals_home == goals_away:
                draws += 1
            else:
                away_wins += 1
        
        return {
            'home_win': home_wins / n_simulations,
            'draw': draws / n_simulations,
            'away_win': away_wins / n_simulations,
            'expected_goals_home': lambda_home,
            'expected_goals_away': lambda_away
        }
    
    def update_strengths_bayesian(self):
        """Update team strengths using Bayesian inference on match history"""
        if len(self.match_history) < 2:
            return
        
        print(f"\n🧠 Updating Bayesian model with {len(self.match_history)} matches...")
        
        if PYMC_AVAILABLE:
            try:
                with pm.Model() as model:
                    # Priors for team strengths
                    attack = pm.Normal("attack", mu=0, sigma=0.5, shape=self.n_teams)
                    defense = pm.Normal("defense", mu=0, sigma=0.5, shape=self.n_teams)
                    home_adv = pm.Normal("home_adv", mu=0.3, sigma=0.1)
                    
                    # Expected goals for each match
                    home_exp = []
                    away_exp = []
                    
                    for home_team, away_team, goals_home, goals_away in self.match_history:
                        i_home = self.team_index[home_team]
                        i_away = self.team_index[away_team]
                        
                        home_lambda = pm.math.exp(home_adv + attack[i_home] - defense[i_away])
                        away_lambda = pm.math.exp(attack[i_away] - defense[i_home])
                        
                        home_exp.append(home_lambda)
                        away_exp.append(away_lambda)
                    
                    # Likelihood
                    observed_home_goals = [r[2] for r in self.match_history]
                    observed_away_goals = [r[3] for r in self.match_history]
                    
                    pm.Poisson("home_goals", mu=home_exp, observed=observed_home_goals)
                    pm.Poisson("away_goals", mu=away_exp, observed=observed_away_goals)
                    
                    # Sample posterior
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        trace = pm.sample(500, tune=250, cores=1, progressbar=False, 
                                        return_inferencedata=True, random_seed=42)
                
                # Update strengths with posterior means
                self.attack_strength = trace.posterior["attack"].mean(dim=("chain", "draw")).values
                self.defense_strength = trace.posterior["defense"].mean(dim=("chain", "draw")).values
                self.home_advantage = float(trace.posterior["home_adv"].mean(dim=("chain", "draw")).values)
                
                print(f"✅ Updated attack strengths: {dict(zip(self.team_names, self.attack_strength.round(2)))}")
                print(f"✅ Updated defense strengths: {dict(zip(self.team_names, self.defense_strength.round(2)))}")
                print(f"✅ Updated home advantage: {self.home_advantage:.3f}")
                
                self.is_trained = True
                
            except Exception as e:
                print(f"⚠️  PyMC Bayesian update failed: {e}")
                self._update_strengths_simplified()
        else:
            self._update_strengths_simplified()
    
    def _update_strengths_simplified(self):
        """Simplified Bayesian update without PyMC"""
        print("🔄 Using simplified Bayesian update...")
        
        # Calculate team performance from match history
        team_goals_for = {team: 0 for team in self.team_names}
        team_goals_against = {team: 0 for team in self.team_names}
        team_matches = {team: 0 for team in self.team_names}
        
        for home_team, away_team, goals_home, goals_away in self.match_history:
            team_goals_for[home_team] += goals_home
            team_goals_against[home_team] += goals_away
            team_goals_for[away_team] += goals_away
            team_goals_against[away_team] += goals_home
            team_matches[home_team] += 1
            team_matches[away_team] += 1
        
        # Update strengths based on performance
        for i, team_name in enumerate(self.team_names):
            if team_matches[team_name] > 0:
                # Attack strength based on goals scored
                goals_per_match = team_goals_for[team_name] / team_matches[team_name]
                self.attack_strength[i] = 0.7 * self.attack_strength[i] + 0.3 * (goals_per_match - 1.5)
                
                # Defense strength based on goals conceded (negative is better)
                goals_conceded_per_match = team_goals_against[team_name] / team_matches[team_name]
                self.defense_strength[i] = 0.7 * self.defense_strength[i] + 0.3 * (1.5 - goals_conceded_per_match)
        
        print(f"✅ Updated attack strengths: {dict(zip(self.team_names, self.attack_strength.round(2)))}")
        print(f"✅ Updated defense strengths: {dict(zip(self.team_names, self.defense_strength.round(2)))}")
        
        self.is_trained = True
    
    def add_match_result(self, home_team: str, away_team: str, goals_home: int, goals_away: int):
        """Add match result to history and update strengths"""
        self.match_history.append((home_team, away_team, goals_home, goals_away))
        
        # Track performance for each team
        home_performance = goals_home - goals_away
        away_performance = goals_away - goals_home
        
        self.team_performance_history[home_team].append(home_performance)
        self.team_performance_history[away_team].append(away_performance)
        
        # Update Bayesian model every few matches
        if len(self.match_history) % 3 == 0:  # Update every 3 matches
            self.update_strengths_bayesian()
    
    def get_team_form(self, team_name: str, last_n_matches: int = 5) -> float:
        """Get team's recent form based on Bayesian performance"""
        if team_name not in self.team_performance_history:
            return 0.0
        
        recent_performances = self.team_performance_history[team_name][-last_n_matches:]
        if not recent_performances:
            return 0.0
        
        return np.mean(recent_performances)
    
    def display_current_rankings(self):
        """Display current team rankings based on Bayesian strengths"""
        print(f"\n📊 CURRENT BAYESIAN TEAM RANKINGS")
        print("=" * 60)
        
        # Calculate overall strength (attack + defense)
        overall_strength = self.attack_strength - self.defense_strength
        
        # Sort teams by overall strength
        team_rankings = [(self.team_names[i], overall_strength[i], 
                         self.attack_strength[i], self.defense_strength[i]) 
                        for i in range(self.n_teams)]
        team_rankings.sort(key=lambda x: x[1], reverse=True)
        
        print(f"{'Rank':<4} {'Team':<20} {'Overall':<8} {'Attack':<8} {'Defense':<8} {'Form':<6}")
        print("-" * 60)
        
        for rank, (team_name, overall, attack, defense) in enumerate(team_rankings, 1):
            form = self.get_team_form(team_name)
            print(f"{rank:<4} {team_name:<20} {overall:7.2f} {attack:7.2f} {defense:7.2f} {form:5.1f}")


class BayesianMatch(Match):
    """Enhanced Match class that uses Bayesian predictions"""
    
    def __init__(self, home_team: Team, away_team: Team, bayesian_predictor: BayesianMatchPredictor):
        self.home_team = home_team
        self.away_team = away_team
        self.score = Score()
        self.minute = 0
        self.match_stats = MatchStats()
        self.bayesian_predictor = bayesian_predictor
        self.is_home_game = True
        
        # Ensure teams have starting elevens
        self.home_team.select_starting_eleven()
        self.away_team.select_starting_eleven()
        
        # Get Bayesian predictions
        self.predictions = self.bayesian_predictor.get_match_probabilities(
            home_team.team_name, away_team.team_name
        )
        
        # Get expected goals from Bayesian model
        self.expected_goals_home = self.predictions['expected_goals_home']
        self.expected_goals_away = self.predictions['expected_goals_away']

    def display_pre_match_info(self):
        """Display enhanced pre-match analysis with Bayesian predictions"""
        print(f"\n{'='*60}")
        print(f"BAYESIAN MATCH PREVIEW: {self.home_team} vs {self.away_team}")
        print(f"{'='*60}")
        
        # Team strengths
        home_strength = self.home_team.get_team_strength()
        away_strength = self.away_team.get_team_strength()
        print(f"Squad Strength: {self.home_team.team_name}: {home_strength:.1f} | {self.away_team.team_name}: {away_strength:.1f}")
        
        # Bayesian strengths
        i_home = self.bayesian_predictor.team_index[self.home_team.team_name]
        i_away = self.bayesian_predictor.team_index[self.away_team.team_name]
        
        bayesian_attack_home = self.bayesian_predictor.attack_strength[i_home]
        bayesian_defense_home = self.bayesian_predictor.defense_strength[i_home]
        bayesian_attack_away = self.bayesian_predictor.attack_strength[i_away]
        bayesian_defense_away = self.bayesian_predictor.defense_strength[i_away]
        
        print(f"Bayesian Attack: {self.home_team.team_name}: {bayesian_attack_home:.2f} | {self.away_team.team_name}: {bayesian_attack_away:.2f}")
        print(f"Bayesian Defense: {self.home_team.team_name}: {bayesian_defense_home:.2f} | {self.away_team.team_name}: {bayesian_defense_away:.2f}")
        
        # Expected goals
        print(f"Expected Goals: {self.home_team.team_name}: {self.expected_goals_home:.2f} | {self.away_team.team_name}: {self.expected_goals_away:.2f}")
        
        # Squad values
        home_value = self.home_team.get_squad_value()
        away_value = self.away_team.get_squad_value()
        print(f"Squad Value: {self.home_team.team_name}: €{home_value:.1f}M | {self.away_team.team_name}: €{away_value:.1f}M")
        
        # Recent form
        home_form = self.bayesian_predictor.get_team_form(self.home_team.team_name)
        away_form = self.bayesian_predictor.get_team_form(self.away_team.team_name)
        print(f"Recent Form: {self.home_team.team_name}: {home_form:+.1f} | {self.away_team.team_name}: {away_form:+.1f}")
        
        # Predictions
        print(f"\n🧠 BAYESIAN PREDICTIONS:")
        print(f"Home Win ({self.home_team.team_name}): {self.predictions['home_win']*100:.1f}%")
        print(f"Draw: {self.predictions['draw']*100:.1f}%")
        print(f"Away Win ({self.away_team.team_name}): {self.predictions['away_win']*100:.1f}%")
        
        print(f"\n{'='*60}")

    def simulate_realistic_score(self):
        """Generate a realistic final score using Bayesian prediction"""
        # Use Bayesian model to predict goals
        goals_home, goals_away, _, _ = self.bayesian_predictor.predict_goals_bayesian(
            self.home_team.team_name, self.away_team.team_name
        )
        
        # Update the actual score
        self.score._home_goals = goals_home
        self.score._away_goals = goals_away
        
        # Generate goal events for each goal
        total_goals = goals_home + goals_away
        if total_goals > 0:
            # Distribute goals across the match
            for goal in range(total_goals):
                minute = np.random.randint(1, 91)
                
                if goal < goals_home:
                    # Home team goal
                    potential_scorers = [p for p in self.home_team.starting_eleven 
                                       if p.stats.position in ['FWD', 'MID']]
                    if potential_scorers:
                        weights = [p.stats.shooting + p.get_match_performance() * 0.1 for p in potential_scorers]
                        scorer = np.random.choice(potential_scorers, p=np.array(weights)/sum(weights))
                        self.score.goal_scorers.append((minute, scorer, 'home'))
                        scorer.goals_scored += 1
                else:
                    # Away team goal
                    potential_scorers = [p for p in self.away_team.starting_eleven 
                                       if p.stats.position in ['FWD', 'MID']]
                    if potential_scorers:
                        weights = [p.stats.shooting + p.get_match_performance() * 0.1 for p in potential_scorers]
                        scorer = np.random.choice(potential_scorers, p=np.array(weights)/sum(weights))
                        self.score.goal_scorers.append((minute, scorer, 'away'))
                        scorer.goals_scored += 1
        
        return goals_home, goals_away

    def start(self):
        """Start the match with Bayesian prediction"""
        self.display_pre_match_info()
        
        print(f"\n🏟️  KICK OFF! {self.home_team} vs {self.away_team}")
        
        # Simulate the match using Bayesian model
        goals_home, goals_away = self.simulate_realistic_score()
        
        print(f"\n⚽ MATCH SIMULATION COMPLETE!")
        print(f"📊 Final Score: {self.home_team} {goals_home} - {goals_away} {self.away_team}")
        
        # Display goal scorers
        if self.score.goal_scorers:
            print(f"\n⚽ GOAL SCORERS:")
            for minute, scorer, team_type in sorted(self.score.goal_scorers, key=lambda x: x[0]):
                team_name = self.home_team.team_name if team_type == 'home' else self.away_team.team_name
                print(f"  {minute}' {scorer.stats.name} ({team_name})")
        
        # Add result to Bayesian history
        self.bayesian_predictor.add_match_result(
            self.home_team.team_name, self.away_team.team_name, 
            goals_home, goals_away
        )

    def winner(self):
        """Determine match winner"""
        if self.score._home_goals > self.score._away_goals:
            print(f"🏆 Victory for {self.home_team}!")
            return self.home_team
        elif self.score._home_goals < self.score._away_goals:
            print(f"🏆 Victory for {self.away_team}!")
            return self.away_team
        else:
            print("⚖️  Match ended in a draw! Going to penalty shootout...")
            return self.penalty_shootout()


class BayesianTournament(Tournament):
    """Tournament class with Bayesian learning"""
    
    def __init__(self, name: str, teams: List[Team], tournament_type: str = "knockout"):
        super().__init__(name, teams, tournament_type)
        self.bayesian_predictor = BayesianMatchPredictor(teams)
        self.bayesian_predictor.initialize_priors_from_teams()
        
    def create_match(self, home_team: Team, away_team: Team) -> BayesianMatch:
        """Create a Bayesian match"""
        return BayesianMatch(home_team, away_team, self.bayesian_predictor)
    
    def run_knockout_tournament(self):
        """Run tournament with Bayesian updates"""
        remaining_teams = self.teams.copy()
        
        while len(remaining_teams) > 1:
            print(f"\n🔥 ROUND {self.current_round}")
            print("=" * 40)
            
            if len(remaining_teams) == 2:
                print("🏆 FINAL MATCH!")
            elif len(remaining_teams) == 4:
                print("🥉 SEMI-FINALS!")
            elif len(remaining_teams) == 8:
                print("🥈 QUARTER-FINALS!")
            
            # Display current Bayesian rankings before round
            if self.current_round > 1:
                self.bayesian_predictor.display_current_rankings()
            
            next_round_teams = []
            
            # Pair teams for matches
            for i in range(0, len(remaining_teams), 2):
                if i + 1 < len(remaining_teams):
                    home_team = remaining_teams[i]
                    away_team = remaining_teams[i + 1]
                    
                    print(f"\n⚔️  {home_team.team_name} vs {away_team.team_name}")
                    
                    # Create and play Bayesian match
                    match = self.create_match(home_team, away_team)
                    match.start()
                    winner = match.winner()
                    
                    if winner:
                        next_round_teams.append(winner)
                        self.matches_played.append(match)
                        self.update_tournament_stats(match)
                    
                    print("\n" + "="*60)
                    
                    # Pause between matches
                    input("Press Enter to continue to next match...")
                else:
                    # Odd number of teams, this team gets a bye
                    next_round_teams.append(remaining_teams[i])
                    print(f"🎫 {remaining_teams[i].team_name} receives a bye to the next round!")
            
            remaining_teams = next_round_teams
            self.current_round += 1
        
        # Tournament winner
        if remaining_teams:
            champion = remaining_teams[0]
            
            # Final Bayesian rankings
            print(f"\n🏆 TOURNAMENT COMPLETED!")
            self.bayesian_predictor.display_current_rankings()
            
            self.display_tournament_summary(champion)


def demo_bayesian_system():
    """Demonstrate the Bayesian learning system"""
    print("🧠 BAYESIAN FOOTBALL SIMULATOR DEMO")
    print("=" * 50)
    
    # Create a smaller tournament for demo
    teams = create_world_class_teams()[:4]  # Use first 4 teams
    
    print(f"🏆 Creating tournament with {len(teams)} teams:")
    for team in teams:
        print(f"  - {team.team_name}")
    
    # Create Bayesian tournament
    tournament = BayesianTournament("Bayesian Demo Cup", teams, "knockout")
    
    print(f"\n🎯 This tournament will:")
    print("✅ Use Bayesian inference to update team strengths after each match")
    print("✅ Predict realistic scores using Poisson distribution")
    print("✅ Show how team rankings evolve based on performance")
    print("✅ Display expected goals and win probabilities")
    
    input("\nPress Enter to start the Bayesian tournament...")
    
    # Start tournament
    tournament.start_tournament()


if __name__ == "__main__":
    demo_bayesian_system()
