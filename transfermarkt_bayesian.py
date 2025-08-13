"""
Enhanced Bayesian System with Transfermarkt Integration
Combines Bayesian learning with real football data
"""

from bayesian_simulator import BayesianMatchPredictor, BayesianMatch, BayesianTournament
from transfermarkt_integration import create_teams_from_transfermarkt, display_transfermarkt_summary
from enhanced_football_simulator import Team
import numpy as np

class TransfermarktBayesianTournament(BayesianTournament):
    """Tournament using Transfermarkt data with Bayesian learning"""
    
    def __init__(self, name: str = "Transfermarkt Champions League"):
        # Create teams from Transfermarkt data
        teams = create_teams_from_transfermarkt()
        super().__init__(name, teams, "knockout")
        
        # Enhanced Bayesian initialization using real data
        self.initialize_enhanced_priors()
    
    def initialize_enhanced_priors(self):
        """Initialize Bayesian priors using Transfermarkt performance data"""
        print("🧠 Initializing Enhanced Bayesian priors from Transfermarkt data...")
        
        for i, team in enumerate(self.teams):
            # Calculate team performance metrics from actual player data
            team_goals = sum(p.goals_scored for p in team.players)
            team_assists = sum(p.assists for p in team.players)
            team_minutes = sum(p.minutes_played for p in team.players)
            
            # Calculate goals/assists per 90 minutes for the team
            if team_minutes > 0:
                goals_per_90 = (team_goals * 90) / team_minutes
                assists_per_90 = (team_assists * 90) / team_minutes
            else:
                goals_per_90 = assists_per_90 = 0.5
            
            # Attack strength based on actual scoring rate
            self.bayesian_predictor.attack_strength[i] = (goals_per_90 - 1.5) * 0.5
            
            # Defense strength based on squad value (proxy for defensive quality)
            squad_value = team.get_squad_value()
            avg_squad_value = np.mean([t.get_squad_value() for t in self.teams])
            defense_factor = (squad_value - avg_squad_value) / avg_squad_value * 0.3
            self.bayesian_predictor.defense_strength[i] = defense_factor
            
            # Adjust for player ages (younger teams = more pace, older = more experience)
            avg_age = np.mean([p.stats.age for p in team.players])
            if avg_age < 25:
                self.bayesian_predictor.attack_strength[i] += 0.1  # Young attacking pace
            elif avg_age > 30:
                self.bayesian_predictor.defense_strength[i] += 0.1  # Veteran experience
        
        print(f"✅ Enhanced attack strengths: {dict(zip(self.bayesian_predictor.team_names, self.bayesian_predictor.attack_strength.round(2)))}")
        print(f"✅ Enhanced defense strengths: {dict(zip(self.bayesian_predictor.team_names, self.bayesian_predictor.defense_strength.round(2)))}")

    def display_pre_tournament_analysis(self):
        """Display comprehensive pre-tournament analysis"""
        print(f"\n🏆 {self.name.upper()}")
        print("=" * 60)
        
        # Transfermarkt summary
        display_transfermarkt_summary()
        
        # Initial Bayesian rankings
        print(f"\n🧠 INITIAL BAYESIAN PREDICTIONS:")
        self.bayesian_predictor.display_current_rankings()
        
        # Predicted tournament favorites
        attack_ranking = sorted(enumerate(self.bayesian_predictor.attack_strength), 
                              key=lambda x: x[1], reverse=True)
        defense_ranking = sorted(enumerate(self.bayesian_predictor.defense_strength), 
                               key=lambda x: x[1], reverse=True)
        
        print(f"\n🎯 TOURNAMENT PREDICTIONS:")
        print(f"Most likely to score goals:")
        for i, (team_idx, strength) in enumerate(attack_ranking[:3], 1):
            team_name = self.bayesian_predictor.team_names[team_idx]
            print(f"  {i}. {team_name} (Attack: {strength:.2f})")
        
        print(f"\nBest defensive teams:")
        for i, (team_idx, strength) in enumerate(defense_ranking[:3], 1):
            team_name = self.bayesian_predictor.team_names[team_idx]
            print(f"  {i}. {team_name} (Defense: {strength:.2f})")
    
    def start_tournament(self):
        """Start tournament with enhanced analysis"""
        self.display_pre_tournament_analysis()
        
        input("\nPress Enter to start the Transfermarkt Bayesian Tournament...")
        
        # Run the tournament
        self.run_knockout_tournament()

def demo_transfermarkt_bayesian():
    """Complete demo of Transfermarkt + Bayesian system"""
    print("🚀 TRANSFERMARKT + BAYESIAN INTEGRATION DEMO")
    print("=" * 60)
    
    print("🎯 This demo showcases:")
    print("✅ Real player data from Transfermarkt-style dataset")
    print("✅ Market value-based team strengths") 
    print("✅ Performance-based player ratings")
    print("✅ Bayesian learning that adapts during tournament")
    print("✅ Realistic goal predictions using Poisson distribution")
    print("✅ Team rankings that evolve based on actual results")
    
    # Create and run tournament
    tournament = TransfermarktBayesianTournament()
    tournament.start_tournament()

def compare_prediction_systems():
    """Compare different prediction approaches"""
    print("\n🔬 PREDICTION SYSTEM COMPARISON")
    print("=" * 50)
    
    teams = create_teams_from_transfermarkt()[:2]  # First 2 teams
    team1, team2 = teams[0], teams[1]
    
    print(f"🆚 Matchup: {team1.team_name} vs {team2.team_name}")
    
    # 1. Simple squad value comparison
    value1, value2 = team1.get_squad_value(), team2.get_squad_value()
    simple_prob = value1 / (value1 + value2)
    
    print(f"\n💰 Simple Squad Value Method:")
    print(f"  {team1.team_name}: €{value1:.1f}M → {simple_prob*100:.1f}% chance")
    print(f"  {team2.team_name}: €{value2:.1f}M → {(1-simple_prob)*100:.1f}% chance")
    
    # 2. Enhanced ML predictor
    from enhanced_football_simulator import MatchPredictor
    ml_predictor = MatchPredictor()
    ml_probs = ml_predictor.predict_match_outcome(team1, team2)
    
    print(f"\n🤖 Enhanced ML Method:")
    print(f"  Home Win: {ml_probs.get('home_win', 0)*100:.1f}%")
    print(f"  Draw: {ml_probs.get('draw', 0)*100:.1f}%")
    print(f"  Away Win: {ml_probs.get('away_win', 0)*100:.1f}%")
    
    # 3. Bayesian predictor with Transfermarkt data
    bayesian_predictor = BayesianMatchPredictor([team1, team2])
    bayesian_predictor.initialize_priors_from_teams()
    bayesian_probs = bayesian_predictor.get_match_probabilities(team1.team_name, team2.team_name)
    
    print(f"\n🧠 Bayesian + Transfermarkt Method:")
    print(f"  Home Win: {bayesian_probs['home_win']*100:.1f}%")
    print(f"  Draw: {bayesian_probs['draw']*100:.1f}%")
    print(f"  Away Win: {bayesian_probs['away_win']*100:.1f}%")
    print(f"  Expected Goals: {team1.team_name} {bayesian_probs['expected_goals_home']:.2f} - {bayesian_probs['expected_goals_away']:.2f} {team2.team_name}")
    
    print(f"\n💡 Key Differences:")
    print("📊 Simple: Only considers squad values")
    print("🤖 ML: Uses multiple features but static predictions") 
    print("🧠 Bayesian: Learns from results + provides expected goals")

if __name__ == "__main__":
    print("🏆 ENHANCED FOOTBALL SIMULATOR")
    print("Real Data + Machine Learning + Bayesian Inference")
    print("=" * 60)
    
    choice = input("\nChoose demo:\n1. Full Transfermarkt + Bayesian Tournament\n2. Prediction System Comparison\n3. Both\nEnter choice (1-3): ")
    
    if choice in ["1", "3"]:
        demo_transfermarkt_bayesian()
    
    if choice in ["2", "3"]:
        compare_prediction_systems()
    
    print(f"\n✨ You now have the most sophisticated football simulator with:")
    print("🔥 Real player data integration")
    print("🧠 Bayesian learning that improves over time")
    print("📊 Multiple prediction methods")
    print("⚽ Realistic goal generation using Poisson distribution")
    print("📈 Dynamic team rankings based on performance")
