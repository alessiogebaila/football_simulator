"""
Enhanced Football Simulator Demo
This demonstrates the new features including players, statistics, and ML-based predictions
"""

from enhanced_football_simulator import *
from tournament import *
try:
    from bayesian_simulator import *
    BAYESIAN_AVAILABLE = True
except ImportError:
    BAYESIAN_AVAILABLE = False
    print("⚠️  Bayesian simulator not available. Some features may be limited.")
import time

def demo_single_match():
    """Demonstrate a single match with all new features"""
    print("🎮 DEMO: Single Match with Enhanced Features")
    print("=" * 60)
    
    # Create teams with players
    mci, fcb, predictor = create_teams_with_players()
    
    # Show team comparisons
    print(f"\n📊 TEAM COMPARISON:")
    print(f"{'Metric':<25} {'Man City':<15} {'Barcelona'}")
    print("-" * 55)
    print(f"{'Squad Value (€M)':<25} {mci.get_squad_value():<15.1f} {fcb.get_squad_value():.1f}")
    print(f"{'Team Strength':<25} {mci.get_team_strength():<15.1f} {fcb.get_team_strength():.1f}")
    print(f"{'Team Chemistry':<25} {mci.team_chemistry:<15} {fcb.team_chemistry}")
    print(f"{'Manager Rating':<25} {mci.manager_rating:<15} {fcb.manager_rating}")
    
    # Show star players
    print(f"\n⭐ STAR PLAYERS:")
    mci_stars = sorted(mci.players, key=lambda p: p.stats.overall_rating, reverse=True)[:3]
    fcb_stars = sorted(fcb.players, key=lambda p: p.stats.overall_rating, reverse=True)[:3]
    
    print(f"\n{mci.team_name}:")
    for player in mci_stars:
        print(f"  {player.stats.name} ({player.stats.position}) - {player.stats.overall_rating} OVR, €{player.stats.market_value}M")
    
    print(f"\n{fcb.team_name}:")
    for player in fcb_stars:
        print(f"  {player.stats.name} ({player.stats.position}) - {player.stats.overall_rating} OVR, €{player.stats.market_value}M")
    
    input("\nPress Enter to start the match...")
    
    # Create and start match
    match = Match(mci, fcb, predictor)
    match.start()
    winner = match.winner()
    
    print(f"\n🎯 MATCH COMPLETED!")
    return winner

def demo_ml_predictions():
    """Demonstrate the ML prediction system"""
    print("\n🤖 DEMO: Machine Learning Predictions")
    print("=" * 60)
    
    # Create various team matchups
    teams = create_world_class_teams()
    predictor = MatchPredictor()
    
    print("📈 Analyzing different matchups...")
    
    matchups = [
        (teams[0], teams[1]),  # Man City vs Real Madrid
        (teams[2], teams[3]),  # Barcelona vs PSG
        (teams[4], teams[5]),  # Bayern vs Arsenal
        (teams[6], teams[7]),  # Liverpool vs Inter
    ]
    
    for home_team, away_team in matchups:
        predictions = predictor.predict_match_outcome(home_team, away_team)
        
        print(f"\n⚔️  {home_team.team_name} vs {away_team.team_name}")
        print(f"   Home Win: {predictions.get('home_win', 0)*100:.1f}%")
        print(f"   Draw:     {predictions.get('draw', 0)*100:.1f}%")
        print(f"   Away Win: {predictions.get('away_win', 0)*100:.1f}%")
        
        # Show key factors
        home_strength = home_team.get_team_strength()
        away_strength = away_team.get_team_strength()
        home_value = home_team.get_squad_value()
        away_value = away_team.get_squad_value()
        
        print(f"   Strength: {home_strength:.1f} vs {away_strength:.1f}")
        print(f"   Value: €{home_value:.1f}M vs €{away_value:.1f}M")

def demo_player_statistics():
    """Demonstrate player statistics and performance"""
    print("\n📊 DEMO: Player Statistics & Performance")
    print("=" * 60)
    
    # Create team
    mci, _, _ = create_teams_with_players()
    
    print(f"🔍 ANALYZING {mci.team_name} SQUAD:")
    print(f"Total Players: {len(mci.players)}")
    print(f"Squad Value: €{mci.get_squad_value():.1f}M")
    
    # Group players by position
    positions = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
    for player in mci.players:
        positions[player.stats.position].append(player)
    
    for pos, players in positions.items():
        if players:
            print(f"\n{pos} ({len(players)} players):")
            for player in sorted(players, key=lambda p: p.stats.overall_rating, reverse=True):
                performance = player.get_match_performance()
                print(f"  {player.stats.name:<20} OVR:{player.stats.overall_rating:2d} "
                      f"Form:{player.stats.form}/10 Performance:{performance:.1f} "
                      f"Value:€{player.stats.market_value}M Age:{player.stats.age}")
    
    # Show key stats for top players
    top_players = sorted(mci.players, key=lambda p: p.stats.overall_rating, reverse=True)[:5]
    
    print(f"\n🌟 TOP 5 PLAYERS DETAILED STATS:")
    print(f"{'Name':<20} {'PAC':<3} {'SHO':<3} {'PAS':<3} {'DRI':<3} {'DEF':<3} {'PHY':<3}")
    print("-" * 60)
    for player in top_players:
        s = player.stats
        print(f"{s.name:<20} {s.pace:<3} {s.shooting:<3} {s.passing:<3} "
              f"{s.dribbling:<3} {s.defending:<3} {s.physical:<3}")

def main_demo():
    """Main demo function"""
    print("🚀 ENHANCED FOOTBALL SIMULATOR")
    print("Features: Players, Statistics, Machine Learning, Realistic Odds")
    if BAYESIAN_AVAILABLE:
        print("🧠 Bayesian Learning: ENABLED")
    else:
        print("🧠 Bayesian Learning: DISABLED (install pymc for full features)")
    print("=" * 70)
    
    while True:
        print(f"\n📋 DEMO OPTIONS:")
        print("1. 🎮 Single Match Demo (with all features)")
        print("2. 🤖 Machine Learning Predictions Demo")
        print("3. 📊 Player Statistics Demo")
        print("4. 🏆 Full Tournament Demo")
        if BAYESIAN_AVAILABLE:
            print("5. 🧠 Bayesian Learning Tournament")
            print("6. ❌ Exit")
        else:
            print("5. ❌ Exit")
        
        max_choice = 6 if BAYESIAN_AVAILABLE else 5
        choice = input(f"\nSelect option (1-{max_choice}): ").strip()
        
        if choice == "1":
            demo_single_match()
        elif choice == "2":
            demo_ml_predictions()
        elif choice == "3":
            demo_player_statistics()
        elif choice == "4":
            print("\n🏆 STARTING FULL TOURNAMENT...")
            teams = create_world_class_teams()
            tournament = Tournament("Enhanced Champions League", teams, "knockout")
            tournament.start_tournament()
        elif choice == "5" and BAYESIAN_AVAILABLE:
            print("\n🧠 STARTING BAYESIAN TOURNAMENT...")
            demo_bayesian_system()
        elif choice == "5" and not BAYESIAN_AVAILABLE:
            print("👋 Thanks for trying the Enhanced Football Simulator!")
            break
        elif choice == "6" and BAYESIAN_AVAILABLE:
            print("👋 Thanks for trying the Enhanced Football Simulator!")
            break
        else:
            print(f"❌ Invalid option. Please choose 1-{max_choice}.")
        
        if choice in ["1", "2", "3", "4"] or (choice == "5" and BAYESIAN_AVAILABLE):
            input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main_demo()
