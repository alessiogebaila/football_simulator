"""
Transfermarkt Data Integration
This module shows how to integrate real football data (Transfermarkt-style) into the simulator
"""

import pandas as pd
import numpy as np
from enhanced_football_simulator import PlayerStats, Player, Team
from typing import List, Dict, Optional

# Sample Transfermarkt-style dataset
TRANSFERMARKT_DATA = {
    'player_name': [
        # Manchester City
        'Erling Haaland', 'Kevin De Bruyne', 'Rodri', 'Ruben Dias', 'Ederson',
        'Jack Grealish', 'Bernardo Silva', 'Kyle Walker', 'John Stones', 'Julian Alvarez', 'Nathan Ake',
        
        # Real Madrid
        'Kylian Mbappe', 'Vinicius Jr', 'Jude Bellingham', 'Luka Modric', 'Thibaut Courtois',
        'Antonio Rudiger', 'Federico Valverde', 'Eder Militao', 'Dani Carvajal', 'Aurelien Tchouameni', 'Rodrygo',
        
        # Barcelona
        'Robert Lewandowski', 'Pedri', 'Gavi', 'Frenkie de Jong', 'Marc-Andre ter Stegen',
        'Ronald Araujo', 'Jules Kounde', 'Raphinha', 'Lamine Yamal', 'Alejandro Balde', 'Ferran Torres',
        
        # Bayern Munich  
        'Harry Kane', 'Jamal Musiala', 'Joshua Kimmich', 'Manuel Neuer', 'Alphonso Davies',
        'Kim Min-jae', 'Leon Goretzka', 'Serge Gnabry', 'Dayot Upamecano', 'Leroy Sane', 'Thomas Muller'
    ],
    
    'club': [
        # Manchester City
        'Manchester City', 'Manchester City', 'Manchester City', 'Manchester City', 'Manchester City',
        'Manchester City', 'Manchester City', 'Manchester City', 'Manchester City', 'Manchester City', 'Manchester City',
        
        # Real Madrid
        'Real Madrid', 'Real Madrid', 'Real Madrid', 'Real Madrid', 'Real Madrid',
        'Real Madrid', 'Real Madrid', 'Real Madrid', 'Real Madrid', 'Real Madrid', 'Real Madrid',
        
        # Barcelona
        'FC Barcelona', 'FC Barcelona', 'FC Barcelona', 'FC Barcelona', 'FC Barcelona',
        'FC Barcelona', 'FC Barcelona', 'FC Barcelona', 'FC Barcelona', 'FC Barcelona', 'FC Barcelona',
        
        # Bayern Munich
        'Bayern Munich', 'Bayern Munich', 'Bayern Munich', 'Bayern Munich', 'Bayern Munich',
        'Bayern Munich', 'Bayern Munich', 'Bayern Munich', 'Bayern Munich', 'Bayern Munich', 'Bayern Munich'
    ],
    
    'position': [
        # Manchester City
        'Centre-Forward', 'Attacking Midfield', 'Defensive Midfield', 'Centre-Back', 'Goalkeeper',
        'Left Winger', 'Attacking Midfield', 'Right-Back', 'Centre-Back', 'Centre-Forward', 'Centre-Back',
        
        # Real Madrid
        'Left Winger', 'Left Winger', 'Central Midfield', 'Central Midfield', 'Goalkeeper',
        'Centre-Back', 'Central Midfield', 'Centre-Back', 'Right-Back', 'Defensive Midfield', 'Right Winger',
        
        # Barcelona
        'Centre-Forward', 'Central Midfield', 'Central Midfield', 'Central Midfield', 'Goalkeeper',
        'Centre-Back', 'Centre-Back', 'Right Winger', 'Right Winger', 'Left-Back', 'Centre-Forward',
        
        # Bayern Munich
        'Centre-Forward', 'Attacking Midfield', 'Defensive Midfield', 'Goalkeeper', 'Left-Back',
        'Centre-Back', 'Central Midfield', 'Right Winger', 'Centre-Back', 'Left Winger', 'Attacking Midfield'
    ],
    
    'market_value_eur': [
        # Manchester City
        180000000, 100000000, 90000000, 75000000, 40000000,
        70000000, 80000000, 35000000, 55000000, 75000000, 45000000,
        
        # Real Madrid
        200000000, 150000000, 130000000, 15000000, 35000000,
        45000000, 100000000, 60000000, 20000000, 80000000, 90000000,
        
        # Barcelona
        50000000, 80000000, 90000000, 85000000, 30000000,
        70000000, 60000000, 65000000, 120000000, 40000000, 55000000,
        
        # Bayern Munich
        120000000, 100000000, 75000000, 15000000, 60000000,
        50000000, 35000000, 55000000, 45000000, 65000000, 8000000
    ],
    
    'age': [
        # Manchester City
        24, 32, 27, 26, 30, 28, 29, 33, 29, 24, 28,
        
        # Real Madrid
        25, 23, 20, 38, 31, 30, 25, 25, 32, 24, 23,
        
        # Barcelona
        35, 21, 19, 26, 31, 24, 24, 26, 17, 20, 24,
        
        # Bayern Munich
        30, 21, 29, 38, 23, 27, 29, 28, 25, 28, 34
    ],
    
    'goals_current_season': [
        # Manchester City
        38, 6, 2, 1, 0, 3, 8, 0, 2, 11, 1,
        
        # Real Madrid
        44, 24, 23, 1, 0, 2, 12, 5, 2, 8, 17,
        
        # Barcelona
        26, 2, 5, 3, 0, 1, 2, 12, 7, 1, 8,
        
        # Bayern Munich
        44, 12, 7, 0, 3, 3, 5, 8, 2, 11, 8
    ],
    
    'assists_current_season': [
        # Manchester City
        8, 18, 9, 2, 1, 11, 15, 8, 3, 5, 2,
        
        # Real Madrid
        8, 9, 13, 8, 0, 4, 8, 1, 6, 4, 9,
        
        # Barcelona
        8, 8, 10, 5, 0, 3, 1, 10, 11, 4, 3,
        
        # Bayern Munich
        12, 8, 15, 0, 13, 2, 3, 6, 1, 8, 12
    ],
    
    'minutes_played': [
        # Manchester City
        3420, 2890, 3100, 2950, 3240, 2100, 2800, 2600, 2400, 1800, 2200,
        
        # Real Madrid
        3650, 3200, 3500, 1200, 1800, 2900, 3000, 2700, 2300, 2600, 2100,
        
        # Barcelona
        2800, 2400, 2100, 2200, 2700, 2500, 2300, 2000, 1500, 1800, 1600,
        
        # Bayern Munich
        3100, 2800, 2900, 1800, 2600, 2400, 2000, 2200, 2100, 2300, 1400
    ]
}

# Position mapping from Transfermarkt to our system
POSITION_MAPPING = {
    'Goalkeeper': 'GK',
    'Centre-Back': 'DEF', 
    'Left-Back': 'DEF',
    'Right-Back': 'DEF',
    'Defensive Midfield': 'MID',
    'Central Midfield': 'MID',
    'Attacking Midfield': 'MID',
    'Left Winger': 'FWD',
    'Right Winger': 'FWD',
    'Centre-Forward': 'FWD'
}

def load_transfermarkt_data() -> pd.DataFrame:
    """Load Transfermarkt-style data into a pandas DataFrame"""
    df = pd.DataFrame(TRANSFERMARKT_DATA)
    
    # Add some calculated fields
    df['goals_per_90'] = (df['goals_current_season'] * 90) / df['minutes_played']
    df['assists_per_90'] = (df['assists_current_season'] * 90) / df['minutes_played']
    df['market_value_millions'] = df['market_value_eur'] / 1000000
    
    # Map positions
    df['position_short'] = df['position'].map(POSITION_MAPPING)
    
    return df

def calculate_player_ratings_from_transfermarkt(row: pd.Series) -> Dict[str, int]:
    """Calculate FIFA-style ratings from Transfermarkt data"""
    
    # Base ratings by position
    base_ratings = {
        'GK': {'pace': 40, 'shooting': 20, 'passing': 60, 'dribbling': 30, 'defending': 50, 'physical': 60},
        'DEF': {'pace': 65, 'shooting': 35, 'passing': 65, 'dribbling': 55, 'defending': 80, 'physical': 75},
        'MID': {'pace': 70, 'shooting': 65, 'passing': 80, 'dribbling': 75, 'defending': 60, 'physical': 70},
        'FWD': {'pace': 85, 'shooting': 85, 'passing': 70, 'dribbling': 85, 'defending': 35, 'physical': 75}
    }
    
    position = row['position_short']
    ratings = base_ratings.get(position, base_ratings['MID']).copy()
    
    # Adjust based on performance
    goals_per_90 = row['goals_per_90']
    assists_per_90 = row['assists_per_90']
    market_value = row['market_value_millions']
    age = row['age']
    
    # Performance adjustments
    if position in ['FWD', 'MID']:
        ratings['shooting'] += min(int(goals_per_90 * 15), 20)
        ratings['passing'] += min(int(assists_per_90 * 10), 15)
        ratings['dribbling'] += min(int((goals_per_90 + assists_per_90) * 5), 15)
    
    # Market value adjustments (higher value = better overall)
    value_factor = min(market_value / 50, 2.0)  # Max 2x boost for €50M+ players
    for stat in ratings:
        ratings[stat] = int(ratings[stat] * (0.8 + 0.2 * value_factor))
    
    # Age adjustments
    if age < 23:  # Young players get potential boost
        for stat in ['pace', 'dribbling']:
            ratings[stat] += 5
    elif age > 32:  # Older players lose some pace/physical
        ratings['pace'] = max(ratings['pace'] - 10, 30)
        ratings['physical'] = max(ratings['physical'] - 5, 50)
        ratings['passing'] += 5  # But gain experience
    
    # Ensure ratings are within bounds
    for stat in ratings:
        ratings[stat] = max(30, min(99, ratings[stat]))
    
    return ratings

def calculate_overall_rating(ratings: Dict[str, int], position: str) -> int:
    """Calculate overall rating based on position importance"""
    
    weights = {
        'GK': {'pace': 0.05, 'shooting': 0.0, 'passing': 0.15, 'dribbling': 0.1, 'defending': 0.35, 'physical': 0.35},
        'DEF': {'pace': 0.15, 'shooting': 0.05, 'passing': 0.2, 'dribbling': 0.1, 'defending': 0.35, 'physical': 0.15},
        'MID': {'pace': 0.15, 'shooting': 0.2, 'passing': 0.3, 'dribbling': 0.2, 'defending': 0.1, 'physical': 0.05},
        'FWD': {'pace': 0.2, 'shooting': 0.35, 'passing': 0.15, 'dribbling': 0.25, 'defending': 0.0, 'physical': 0.05}
    }
    
    position_weights = weights.get(position, weights['MID'])
    overall = sum(ratings[stat] * weight for stat, weight in position_weights.items())
    
    return int(overall)

def create_player_from_transfermarkt(row: pd.Series) -> Player:
    """Create a Player object from Transfermarkt data"""
    
    # Calculate ratings
    ratings = calculate_player_ratings_from_transfermarkt(row)
    overall = calculate_overall_rating(ratings, row['position_short'])
    
    # Calculate form based on recent performance
    expected_goals_for_value = row['market_value_millions'] / 20  # Very rough estimate
    actual_performance = row['goals_per_90'] + row['assists_per_90']
    form = max(1, min(10, int(5 + (actual_performance - expected_goals_for_value) * 2)))
    
    # Create PlayerStats
    player_stats = PlayerStats(
        name=row['player_name'],
        position=row['position_short'],
        overall_rating=overall,
        pace=ratings['pace'],
        shooting=ratings['shooting'],
        passing=ratings['passing'],
        dribbling=ratings['dribbling'],
        defending=ratings['defending'],
        physical=ratings['physical'],
        market_value=row['market_value_millions'],
        age=row['age'],
        form=form
    )
    
    # Create Player and add current season stats
    player = Player(player_stats)
    player.goals_scored = row['goals_current_season']
    player.assists = row['assists_current_season']
    player.minutes_played = row['minutes_played']
    
    return player

def create_teams_from_transfermarkt() -> List[Team]:
    """Create teams using Transfermarkt data"""
    
    df = load_transfermarkt_data()
    teams = []
    
    # Group by club
    for club_name in df['club'].unique():
        club_players = df[df['club'] == club_name]
        
        # Create team
        team = Team(club_name)
        
        # Add players
        for _, player_row in club_players.iterrows():
            player = create_player_from_transfermarkt(player_row)
            team.add_player(player)
        
        # Set team chemistry based on squad value and diversity
        avg_value = club_players['market_value_millions'].mean()
        team.team_chemistry = min(100, int(70 + (avg_value / 10)))  # Higher value teams have better chemistry
        team.manager_rating = min(100, int(75 + (avg_value / 15)))   # Better managers for expensive squads
        
        teams.append(team)
    
    return teams

def display_transfermarkt_summary():
    """Display summary of Transfermarkt data integration"""
    
    df = load_transfermarkt_data()
    teams = create_teams_from_transfermarkt()
    
    print("📊 TRANSFERMARKT DATA INTEGRATION SUMMARY")
    print("=" * 60)
    
    print(f"📈 Data Statistics:")
    print(f"  Total Players: {len(df)}")
    print(f"  Total Teams: {len(teams)}")
    print(f"  Total Market Value: €{df['market_value_millions'].sum():.1f}M")
    print(f"  Average Market Value: €{df['market_value_millions'].mean():.1f}M")
    print(f"  Most Valuable Player: {df.loc[df['market_value_millions'].idxmax(), 'player_name']} (€{df['market_value_millions'].max():.1f}M)")
    
    print(f"\n🏆 Teams Overview:")
    for team in sorted(teams, key=lambda t: t.get_squad_value(), reverse=True):
        squad_value = team.get_squad_value()
        avg_age = np.mean([p.stats.age for p in team.players])
        print(f"  {team.team_name:<15} - €{squad_value:.1f}M (Avg Age: {avg_age:.1f})")
    
    print(f"\n⚽ Top Scorers This Season:")
    top_scorers = df.nlargest(5, 'goals_current_season')[['player_name', 'club', 'goals_current_season', 'market_value_millions']]
    for _, player in top_scorers.iterrows():
        print(f"  {player['player_name']:<20} ({player['club']:<15}) - {player['goals_current_season']} goals (€{player['market_value_millions']:.1f}M)")
    
    print(f"\n👏 Top Assisters This Season:")
    top_assisters = df.nlargest(5, 'assists_current_season')[['player_name', 'club', 'assists_current_season', 'market_value_millions']]
    for _, player in top_assisters.iterrows():
        print(f"  {player['player_name']:<20} ({player['club']:<15}) - {player['assists_current_season']} assists (€{player['market_value_millions']:.1f}M)")

def save_transfermarkt_csv():
    """Save the Transfermarkt dataset as CSV for future use"""
    df = load_transfermarkt_data()
    df.to_csv('transfermarkt_data.csv', index=False)
    print("✅ Transfermarkt data saved to 'transfermarkt_data.csv'")
    
    # Also save additional analysis
    analysis = {
        'team_values': df.groupby('club')['market_value_millions'].sum().sort_values(ascending=False),
        'position_values': df.groupby('position_short')['market_value_millions'].mean().sort_values(ascending=False),
        'age_performance': df.groupby(pd.cut(df['age'], bins=[16, 23, 28, 35, 40]))['goals_per_90'].mean()
    }
    
    print("\n📈 QUICK ANALYSIS:")
    print("Team Values:", analysis['team_values'].to_dict())
    print("Position Average Values:", analysis['position_values'].to_dict())

if __name__ == "__main__":
    print("🏆 TRANSFERMARKT DATA INTEGRATION DEMO")
    print("=" * 50)
    
    # Display summary
    display_transfermarkt_summary()
    
    # Save data
    save_transfermarkt_csv()
    
    print(f"\n💡 Integration Benefits:")
    print("✅ Real player performance data")
    print("✅ Market value-based team strength")
    print("✅ Age and form calculations")
    print("✅ Current season statistics")
    print("✅ Position-appropriate ratings")
    
    print(f"\n🔧 How to Use:")
    print("1. Replace sample data with real Transfermarkt CSV")
    print("2. Update create_teams_from_transfermarkt() in your tournament")
    print("3. Players will have realistic ratings based on actual performance")
    print("4. Market values influence team chemistry and manager ratings")
