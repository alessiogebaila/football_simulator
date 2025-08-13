"""
Simple Bayesian Football Match Example
Demonstrates how Bayesian learning improves predictions over time
"""

import numpy as np
from bayesian_simulator import BayesianMatchPredictor, BayesianMatch
from tournament import create_world_class_teams

def simple_bayesian_demo():
    """Run a simple demo showing Bayesian learning in action"""
    print("🧠 SIMPLE BAYESIAN LEARNING DEMO")
    print("=" * 50)
    
    # Create 4 teams
    teams = create_world_class_teams()[:4]
    team_names = [team.team_name for team in teams]
    
    print("🏆 Teams in demo:")
    for i, team in enumerate(teams, 1):
        print(f"  {i}. {team.team_name}")
    
    # Create Bayesian predictor
    predictor = BayesianMatchPredictor(teams)
    predictor.initialize_priors_from_teams()
    
    print(f"\n📊 INITIAL BAYESIAN STRENGTHS:")
    predictor.display_current_rankings()
    
    # Simulate some matches and show how predictions evolve
    matchups = [
        (teams[0], teams[1]),  # Man City vs Real Madrid
        (teams[2], teams[3]),  # Barcelona vs PSG
        (teams[0], teams[2]),  # Man City vs Barcelona
        (teams[1], teams[3]),  # Real Madrid vs PSG
    ]
    
    print(f"\n🎯 SIMULATING MATCHES WITH BAYESIAN LEARNING...")
    
    for i, (home_team, away_team) in enumerate(matchups, 1):
        print(f"\n{'='*60}")
        print(f"MATCH {i}: {home_team.team_name} vs {away_team.team_name}")
        print(f"{'='*60}")
        
        # Get predictions before match
        probs = predictor.get_match_probabilities(home_team.team_name, away_team.team_name)
        print(f"\n📈 PRE-MATCH PREDICTIONS:")
        print(f"Home Win: {probs['home_win']*100:.1f}%")
        print(f"Draw: {probs['draw']*100:.1f}%") 
        print(f"Away Win: {probs['away_win']*100:.1f}%")
        print(f"Expected Goals: {home_team.team_name} {probs['expected_goals_home']:.2f} - {probs['expected_goals_away']:.2f} {away_team.team_name}")
        
        # Simulate match
        goals_home, goals_away, _, _ = predictor.predict_goals_bayesian(
            home_team.team_name, away_team.team_name
        )
        
        print(f"\n⚽ MATCH RESULT: {home_team.team_name} {goals_home} - {goals_away} {away_team.team_name}")
        
        # Add result and update model
        predictor.add_match_result(home_team.team_name, away_team.team_name, goals_home, goals_away)
        
        print(f"\n📊 UPDATED RANKINGS AFTER MATCH {i}:")
        predictor.display_current_rankings()
        
        if i < len(matchups):
            input("\nPress Enter for next match...")
    
    print(f"\n🎉 DEMO COMPLETE!")
    print("Notice how team rankings changed based on actual match results!")
    print("This is the power of Bayesian learning - the model gets smarter over time! 🧠")

def compare_predictions():
    """Compare original vs Bayesian predictions"""
    print("\n🔬 PREDICTION COMPARISON DEMO")
    print("=" * 50)
    
    teams = create_world_class_teams()[:2]
    mci, real = teams[0], teams[1]
    
    print(f"🆚 Comparing predictions for: {mci.team_name} vs {real.team_name}")
    
    # Original ML predictor
    from enhanced_football_simulator import MatchPredictor
    original_predictor = MatchPredictor()
    original_probs = original_predictor.predict_match_outcome(mci, real)
    
    print(f"\n🤖 ORIGINAL ML PREDICTIONS:")
    print(f"Home Win: {original_probs.get('home_win', 0)*100:.1f}%")
    print(f"Draw: {original_probs.get('draw', 0)*100:.1f}%")
    print(f"Away Win: {original_probs.get('away_win', 0)*100:.1f}%")
    
    # Bayesian predictor
    bayesian_predictor = BayesianMatchPredictor([mci, real])
    bayesian_predictor.initialize_priors_from_teams()
    bayesian_probs = bayesian_predictor.get_match_probabilities(mci.team_name, real.team_name)
    
    print(f"\n🧠 BAYESIAN PREDICTIONS:")
    print(f"Home Win: {bayesian_probs['home_win']*100:.1f}%")
    print(f"Draw: {bayesian_probs['draw']*100:.1f}%")
    print(f"Away Win: {bayesian_probs['away_win']*100:.1f}%")
    print(f"Expected Goals: {mci.team_name} {bayesian_probs['expected_goals_home']:.2f} - {bayesian_probs['expected_goals_away']:.2f} {real.team_name}")
    
    print(f"\n💡 KEY DIFFERENCES:")
    print("- Original: Static predictions based on current squad")
    print("- Bayesian: Dynamic predictions that learn from match results")
    print("- Bayesian: Provides expected goals for more detailed analysis")
    print("- Bayesian: Updates team strengths after each match")

if __name__ == "__main__":
    print("🧠 BAYESIAN FOOTBALL SIMULATION EXAMPLES")
    print("=" * 60)
    
    choice = input("Choose demo:\n1. Simple Bayesian Learning\n2. Prediction Comparison\n3. Both\nEnter choice (1-3): ")
    
    if choice in ["1", "3"]:
        simple_bayesian_demo()
    
    if choice in ["2", "3"]:
        compare_predictions()
    
    print(f"\n✨ Try running 'python demo.py' for the full interactive experience!")
