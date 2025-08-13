#!/usr/bin/env python3
"""
📊 CSV SQUAD LOADER
Load squad data from CSV and integrate with Ultimate Football Simulator

This module loads the scraped squad data and creates teams for the simulator.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from enhanced_football_simulator import Player, Team
import random

class SquadLoader:
    """Load and process squad data from CSV"""
    
    def __init__(self, csv_file: str = 'real_transfermarkt_squads.csv'):
        self.csv_file = f"c:\\Users\\Alessio\\OneDrive\\Desktop\\football_simulator\\{csv_file}"
        self.df = None
        self.teams = []
    
    def load_data(self) -> pd.DataFrame:
        """Load squad data from CSV"""
        try:
            self.df = pd.read_csv(self.csv_file, encoding='utf-8')
            print(f"📊 Loaded {len(self.df)} players from {self.csv_file}")
            
            # Clean up data
            self.df = self.clean_data()
            
            return self.df
            
        except FileNotFoundError:
            print(f"❌ File not found: {self.csv_file}")
            return None
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and normalize the loaded data"""
        df = self.df.copy()
        
        print("🧹 Cleaning squad data...")
        
        # Remove players with 'Unknown' or missing names
        df = df[df['player_name'] != 'Player']
        df = df[df['player_name'] != 'Unknown']
        df = df[df['player_name'].notna()]
        
        # Fix market values that are too high (likely parsing errors)
        def fix_market_value(value):
            if value > 1_000_000_000:  # More than 1 billion
                # Likely parsing error, divide by appropriate factor
                if value > 10_000_000_000:  # 10+ billion
                    return int(value / 1000)  # Divide by 1000
                else:  # 1-10 billion
                    return int(value / 100)   # Divide by 100
            elif value < 100_000:  # Less than 100k
                return max(100_000, value)  # Minimum 100k
            return value
        
        df['market_value_eur'] = df['market_value_eur'].apply(fix_market_value)
        
        # Clean positions
        position_mapping = {
            'Unknown': 'CM',  # Default unknown to CM
            'UNKNOWN': 'CM',
            'GK': 'GK',
            'CB': 'CB', 
            'LB': 'LB',
            'RB': 'RB',
            'DM': 'DM',
            'CM': 'CM',
            'AM': 'AM',
            'LW': 'LW',
            'RW': 'RW',
            'CF': 'ST',  # Convert CF to ST
            'ST': 'ST'
        }
        
        df['position'] = df['position'].map(position_mapping).fillna('CM')
        
        # Ensure reasonable age range
        df['age'] = df['age'].clip(16, 45)
        
        # Ensure reasonable stats
        df['goals_current_season'] = df['goals_current_season'].clip(0, 50)
        df['assists_current_season'] = df['assists_current_season'].clip(0, 30)
        df['minutes_played'] = df['minutes_played'].clip(0, 4000)
        
        print(f"✅ Cleaned data: {len(df)} players remaining")
        
        return df
    
    def calculate_player_ratings(self, row) -> Dict[str, float]:
        """Calculate FIFA-style ratings for a player based on position and market value"""
        position = row['position']
        market_value = row['market_value_eur']
        age = row['age']
        
        # Base rating from market value (logarithmic scale)
        if market_value > 0:
            base_rating = min(99, max(60, 50 + np.log10(market_value / 100_000) * 8))
        else:
            base_rating = 65
        
        # Age factor (peak around 26-29)
        age_factor = 1.0
        if age < 20:
            age_factor = 0.85 + (age - 16) * 0.03  # Young players
        elif age > 32:
            age_factor = 1.0 - (age - 32) * 0.02   # Declining players
        
        base_rating *= age_factor
        
        # Position-specific ratings
        ratings = {
            'pace': base_rating,
            'shooting': base_rating,
            'passing': base_rating,
            'dribbling': base_rating,
            'defending': base_rating,
            'physical': base_rating
        }
        
        # Adjust based on position
        if position == 'GK':
            ratings.update({
                'pace': base_rating * 0.6,
                'shooting': base_rating * 0.3,
                'passing': base_rating * 0.7,
                'dribbling': base_rating * 0.4,
                'defending': base_rating * 0.9,
                'physical': base_rating * 0.8
            })
        elif position in ['CB']:
            ratings.update({
                'pace': base_rating * 0.7,
                'shooting': base_rating * 0.4,
                'passing': base_rating * 0.8,
                'dribbling': base_rating * 0.6,
                'defending': base_rating * 1.1,
                'physical': base_rating * 1.0
            })
        elif position in ['LB', 'RB']:
            ratings.update({
                'pace': base_rating * 1.0,
                'shooting': base_rating * 0.6,
                'passing': base_rating * 0.9,
                'dribbling': base_rating * 0.8,
                'defending': base_rating * 0.9,
                'physical': base_rating * 0.8
            })
        elif position in ['DM']:
            ratings.update({
                'pace': base_rating * 0.8,
                'shooting': base_rating * 0.6,
                'passing': base_rating * 1.0,
                'dribbling': base_rating * 0.8,
                'defending': base_rating * 1.0,
                'physical': base_rating * 0.9
            })
        elif position in ['CM']:
            ratings.update({
                'pace': base_rating * 0.9,
                'shooting': base_rating * 0.8,
                'passing': base_rating * 1.0,
                'dribbling': base_rating * 0.9,
                'defending': base_rating * 0.8,
                'physical': base_rating * 0.8
            })
        elif position in ['AM']:
            ratings.update({
                'pace': base_rating * 0.9,
                'shooting': base_rating * 1.0,
                'passing': base_rating * 1.0,
                'dribbling': base_rating * 1.1,
                'defending': base_rating * 0.6,
                'physical': base_rating * 0.7
            })
        elif position in ['LW', 'RW']:
            ratings.update({
                'pace': base_rating * 1.1,
                'shooting': base_rating * 0.9,
                'passing': base_rating * 0.8,
                'dribbling': base_rating * 1.1,
                'defending': base_rating * 0.5,
                'physical': base_rating * 0.7
            })
        elif position in ['ST']:
            ratings.update({
                'pace': base_rating * 0.95,
                'shooting': base_rating * 1.2,
                'passing': base_rating * 0.7,
                'dribbling': base_rating * 0.9,
                'defending': base_rating * 0.4,
                'physical': base_rating * 1.0
            })
        
        # Clip all ratings to reasonable range
        for key in ratings:
            ratings[key] = np.clip(ratings[key], 40, 99)
        
        return ratings
    
    def create_player_from_row(self, row) -> Player:
        """Create a Player object from a DataFrame row"""
        from enhanced_football_simulator import PlayerStats
        
        ratings = self.calculate_player_ratings(row)
        
        # Calculate overall rating as average of key stats
        overall_rating = int(np.mean([
            ratings['pace'], ratings['shooting'], ratings['passing'],
            ratings['dribbling'], ratings['defending'], ratings['physical']
        ]))
        
        # Create PlayerStats object
        player_stats = PlayerStats(
            name=row['player_name'],
            position=row['position'],
            overall_rating=overall_rating,
            pace=int(ratings['pace']),
            shooting=int(ratings['shooting']),
            passing=int(ratings['passing']),
            dribbling=int(ratings['dribbling']),
            defending=int(ratings['defending']),
            physical=int(ratings['physical']),
            market_value=row['market_value_eur'] / 1_000_000,  # Convert to millions
            age=int(row['age']),
            form=random.randint(7, 10)  # Good form for all players
        )
        
        # Create Player object
        player = Player(player_stats)
        
        # Set additional stats
        player.goals_scored = int(row['goals_current_season'])
        player.assists = int(row['assists_current_season'])
        player.minutes_played = int(row['minutes_played'])
        
        return player
    
    def create_teams_from_csv(self) -> List[Team]:
        """Create Team objects from the loaded data"""
        if self.df is None:
            self.load_data()
        
        if self.df is None:
            return []
        
        teams = []
        
        print("🏈 Creating teams from CSV data...")
        
        for club_name, club_players in self.df.groupby('club'):
            team = Team(club_name)
            
            for _, player_row in club_players.iterrows():
                try:
                    player = self.create_player_from_row(player_row)
                    team.add_player(player)
                except Exception as e:
                    print(f"  ⚠️ Error creating player {player_row['player_name']}: {e}")
                    continue
            
            if len(team.players) > 0:
                teams.append(team)
                total_value = sum(p.market_value_eur for p in team.players)
                avg_rating = np.mean([p.overall_rating for p in team.players])
                print(f"  ✅ {club_name}: {len(team.players)} players, €{total_value/1_000_000:.1f}M, avg rating {avg_rating:.1f}")
        
        self.teams = teams
        print(f"\n🎉 Created {len(teams)} teams from CSV data!")
        
        return teams
    
    def get_team_summary(self) -> pd.DataFrame:
        """Get summary statistics for all teams"""
        if not self.teams:
            return pd.DataFrame()
        
        summary_data = []
        
        for team in self.teams:
            total_value = sum(p.market_value_eur for p in team.players)
            avg_age = np.mean([p.age for p in team.players])
            avg_rating = np.mean([p.overall_rating for p in team.players])
            
            # Position counts
            positions = {}
            for player in team.players:
                positions[player.position] = positions.get(player.position, 0) + 1
            
            summary_data.append({
                'Team': team.name,
                'Players': len(team.players),
                'Total_Value_M': total_value / 1_000_000,
                'Avg_Value_M': (total_value / len(team.players)) / 1_000_000,
                'Avg_Age': avg_age,
                'Avg_Rating': avg_rating,
                'GK': positions.get('GK', 0),
                'Defenders': positions.get('CB', 0) + positions.get('LB', 0) + positions.get('RB', 0),
                'Midfielders': positions.get('DM', 0) + positions.get('CM', 0) + positions.get('AM', 0),
                'Forwards': positions.get('LW', 0) + positions.get('RW', 0) + positions.get('ST', 0)
            })
        
        df = pd.DataFrame(summary_data)
        return df.sort_values('Total_Value_M', ascending=False)


def main():
    """Test the squad loader"""
    print("📊" + "="*60 + "📊")
    print("  CSV SQUAD LOADER TEST")
    print("📊" + "="*60 + "📊")
    
    loader = SquadLoader()
    
    # Load and clean data
    df = loader.load_data()
    if df is None:
        return
    
    # Create teams
    teams = loader.create_teams_from_csv()
    
    # Show summary
    summary = loader.get_team_summary()
    print("\n📈 TEAM SUMMARY:")
    print("="*80)
    print(summary.to_string(index=False))
    
    # Show top players by value
    print(f"\n⭐ TOP 10 MOST VALUABLE PLAYERS:")
    print("="*50)
    top_players = df.nlargest(10, 'market_value_eur')[['player_name', 'club', 'position', 'market_value_eur']]
    top_players['Value_M'] = top_players['market_value_eur'] / 1_000_000
    print(top_players[['player_name', 'club', 'position', 'Value_M']].to_string(index=False))
    
    print(f"\n✅ Squad loader test completed!")
    print(f"🎮 Ready to use teams in Ultimate Football Simulator!")


if __name__ == "__main__":
    main()
