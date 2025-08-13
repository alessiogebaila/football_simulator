#!/usr/bin/env python3
"""
🏆 TACTICAL FORMATION SYSTEM
Automatically selects best starting XI based on team formations and market values

Formations supported:
- 4-2-3-1 (Barcelona, PSG, Arsenal)
- 4-3-3 (Real Madrid, Liverpool, Bayern Munich)
- 4-1-4-1 (Manchester City, Chelsea)
- 3-5-2 (Atletico Madrid, Inter Milan)
- 4-2-3-1 (Manchester United, Tottenham, AC Milan, Juventus, Napoli)
- 4-3-3 (Borussia Dortmund)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enhanced_football_simulator import Player, PlayerStats, Team
import random

@dataclass
class FormationPosition:
    """Represents a position in a formation"""
    position: str
    priority: int  # 1 = most important, higher = less important
    alternatives: List[str]  # Alternative positions that can play here

class TacticalFormation:
    """Represents a team's tactical formation"""
    
    def __init__(self, name: str, positions: List[FormationPosition]):
        self.name = name
        self.positions = positions
    
    def get_starting_xi_positions(self) -> List[str]:
        """Get the 11 starting positions in order of importance"""
        sorted_positions = sorted(self.positions, key=lambda x: x.priority)
        return [pos.position for pos in sorted_positions[:11]]

# Define all formations
FORMATIONS = {
    'Barcelona': TacticalFormation('4-2-3-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('CM', 6, ['DM']),
        FormationPosition('CM', 7, ['DM']),
        FormationPosition('AM', 8, ['CM', 'LW', 'RW']),
        FormationPosition('LW', 9, ['AM', 'CF']),
        FormationPosition('RW', 10, ['AM', 'CF']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Real Madrid': TacticalFormation('4-3-1-2', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('CM', 6, ['DM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('CM', 8, ['DM', 'AM']),
        FormationPosition('AM', 9, ['CM']),  # Attacking midfielder behind strikers
        FormationPosition('CF', 10, ['ST']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Atletico Madrid': TacticalFormation('4-4-2', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('RM', 6, ['RW', 'CM']),  # Right midfielder
        FormationPosition('CM', 7, ['DM']),
        FormationPosition('CM', 8, ['DM']),
        FormationPosition('LM', 9, ['LW', 'CM']),  # Left midfielder
        FormationPosition('CF', 10, ['ST']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Manchester City': TacticalFormation('4-3-3', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('CM', 8, ['DM', 'AM']),
        FormationPosition('LW', 9, ['CF', 'AM']),
        FormationPosition('CF', 10, ['ST']),
        FormationPosition('RW', 11, ['CF', 'AM']),
    ]),
    
    'Liverpool': TacticalFormation('4-2-3-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('AM', 8, ['CM', 'LW', 'RW']),
        FormationPosition('LW', 9, ['AM']),
        FormationPosition('RW', 10, ['AM']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Arsenal': TacticalFormation('4-2-3-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('AM', 8, ['CM', 'LW', 'RW']),
        FormationPosition('LW', 9, ['AM']),
        FormationPosition('RW', 10, ['AM']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Chelsea': TacticalFormation('4-1-4-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('AM', 8, ['CM', 'LW', 'RW']),
        FormationPosition('LW', 9, ['AM']),
        FormationPosition('RW', 10, ['AM']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Manchester United': TacticalFormation('3-4-2-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('CB', 2, []),
        FormationPosition('CB', 3, []),
        FormationPosition('CB', 4, []),
        FormationPosition('LM', 5, ['LB', 'LW']),  # Left midfielder/wing-back
        FormationPosition('CM', 6, ['DM']),
        FormationPosition('CM', 7, ['DM']),
        FormationPosition('RM', 8, ['RB', 'RW']),  # Right midfielder/wing-back
        FormationPosition('AM', 9, ['CM']),  # Attacking midfielder
        FormationPosition('AM', 10, ['CM']),  # Second attacking midfielder
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Tottenham': TacticalFormation('4-3-3', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('CM', 8, ['DM', 'AM']),
        FormationPosition('LW', 9, ['CF']),
        FormationPosition('CF', 10, ['ST']),
        FormationPosition('RW', 11, ['CF']),
    ]),
    
    'PSG': TacticalFormation('4-3-3', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('CM', 8, ['DM', 'AM']),
        FormationPosition('LW', 9, ['CF', 'AM']),
        FormationPosition('CF', 10, ['ST']),
        FormationPosition('RW', 11, ['CF', 'AM']),
    ]),
    
    'Bayern Munich': TacticalFormation('4-2-3-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('AM', 8, ['CM', 'LW', 'RW']),
        FormationPosition('LW', 9, ['AM']),
        FormationPosition('RW', 10, ['AM']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Borussia Dortmund': TacticalFormation('3-4-2-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('CB', 2, []),
        FormationPosition('CB', 3, []),
        FormationPosition('CB', 4, []),
        FormationPosition('LM', 5, ['LB', 'LW']),  # Left midfielder/wing-back
        FormationPosition('CM', 6, ['DM']),
        FormationPosition('CM', 7, ['DM']),
        FormationPosition('RM', 8, ['RB', 'RW']),  # Right midfielder/wing-back
        FormationPosition('AM', 9, ['CM']),  # Attacking midfielder
        FormationPosition('AM', 10, ['CM']),  # Second attacking midfielder
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Inter Milan': TacticalFormation('3-5-2', [
        FormationPosition('GK', 1, []),
        FormationPosition('CB', 2, []),
        FormationPosition('CB', 3, []),
        FormationPosition('CB', 4, []),
        FormationPosition('LB', 5, ['LW']),  # Wing-back
        FormationPosition('RB', 6, ['RW']),  # Wing-back
        FormationPosition('DM', 7, ['CM']),
        FormationPosition('CM', 8, ['DM', 'AM']),
        FormationPosition('AM', 9, ['CM']),
        FormationPosition('CF', 10, ['ST']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'AC Milan': TacticalFormation('4-2-3-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('AM', 8, ['CM', 'LW', 'RW']),
        FormationPosition('LW', 9, ['AM']),
        FormationPosition('RW', 10, ['AM']),
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Juventus': TacticalFormation('3-4-2-1', [
        FormationPosition('GK', 1, []),
        FormationPosition('CB', 2, []),
        FormationPosition('CB', 3, []),
        FormationPosition('CB', 4, []),
        FormationPosition('LM', 5, ['LB', 'LW']),  # Left midfielder/wing-back
        FormationPosition('CM', 6, ['DM']),
        FormationPosition('CM', 7, ['DM']),
        FormationPosition('RM', 8, ['RB', 'RW']),  # Right midfielder/wing-back
        FormationPosition('AM', 9, ['CM']),  # Attacking midfielder
        FormationPosition('AM', 10, ['CM']),  # Second attacking midfielder
        FormationPosition('CF', 11, ['ST']),
    ]),
    
    'Napoli': TacticalFormation('4-3-3', [
        FormationPosition('GK', 1, []),
        FormationPosition('RB', 2, ['CB']),
        FormationPosition('CB', 3, ['RB', 'LB']),
        FormationPosition('CB', 4, ['RB', 'LB']),
        FormationPosition('LB', 5, ['CB']),
        FormationPosition('DM', 6, ['CM']),
        FormationPosition('CM', 7, ['DM', 'AM']),
        FormationPosition('CM', 8, ['DM', 'AM']),
        FormationPosition('LW', 9, ['CF']),
        FormationPosition('CF', 10, ['ST']),
        FormationPosition('RW', 11, ['CF']),
    ]),
}

class TacticalManager:
    """Manages tactical formations and squad selection"""
    
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.suspended_players = set()  # Players who are suspended
        self.injured_players = set()    # Players who are injured
        
        # Check if we have the new column name, otherwise use old one
        if 'market_value_mil_eur' in self.df.columns:
            self.value_column = 'market_value_mil_eur'
            # Values are already in millions, no conversion needed
        else:
            self.value_column = 'market_value_eur'
            # Fix market value issues (some have billions instead of millions)
            self.df[self.value_column] = self.df[self.value_column].apply(self._fix_market_value)
        
        # Normalize position names
        self.df['position'] = self.df['position'].apply(self._normalize_position)
    
    def _fix_market_value(self, value: int) -> int:
        """Fix market values that are too high (billions instead of millions)"""
        if value > 1_000_000_000:  # If more than 1 billion
            return min(value // 1000, 200_000_000)  # Convert and cap at 200M
        return max(value, 1_000_000)  # Minimum 1M value
    
    def _normalize_position(self, position: str) -> str:
        """Normalize position names to standard format"""
        if pd.isna(position) or position == 'Unknown':
            return 'Unknown'
        
        position = position.upper().strip()
        
        # Position mapping
        position_map = {
            'ST': 'CF', 'STRIKER': 'CF', 'CENTRE-FORWARD': 'CF',
            'CAM': 'AM', 'ATTACKING MIDFIELDER': 'AM', 'TREQUARTISTA': 'AM',
            'CDM': 'DM', 'DEFENSIVE MIDFIELDER': 'DM', 'HOLDING MIDFIELDER': 'DM',
            'LWB': 'LB', 'LEFT WING-BACK': 'LB',
            'RWB': 'RB', 'RIGHT WING-BACK': 'RB',
            'CENTRE-BACK': 'CB', 'CENTRAL DEFENDER': 'CB',
            'GOALKEEPER': 'GK', 'KEEPER': 'GK',
            'CENTRAL MIDFIELDER': 'CM', 'BOX-TO-BOX': 'CM',
            'LEFT WINGER': 'LW', 'RIGHT WINGER': 'RW',
            'LEFT-BACK': 'LB', 'RIGHT-BACK': 'RB',
            # Special formations mapping
            'RM': 'RW', 'RIGHT MIDFIELDER': 'RW',  # RM maps to RW
            'LM': 'LW', 'LEFT MIDFIELDER': 'LW',   # LM maps to LW
        }
        
        return position_map.get(position, position)
    
    def set_injuries_and_suspensions(self, team_name: str, injured: List[str] = None, suspended: List[str] = None):
        """Set injured and suspended players for a team"""
        if injured:
            self.injured_players.update(injured)
        if suspended:
            self.suspended_players.update(suspended)
    
    def get_available_players(self, team_name: str, position: str) -> List[Dict]:
        """Get available players for a specific position, sorted by market value"""
        team_players = self.df[self.df['club'] == team_name].copy()
        
        # Filter out injured and suspended players
        available_players = team_players[
            ~team_players['player_name'].isin(self.injured_players) &
            ~team_players['player_name'].isin(self.suspended_players)
        ]
        
        # Filter by position
        position_players = available_players[available_players['position'] == position]
        
        # Sort by market value (descending)
        if self.value_column == 'market_value_mil_eur':
            # Values are in millions, display as is
            position_players = position_players.sort_values(self.value_column, ascending=False)
        else:
            # Values are in full euros, sort normally
            position_players = position_players.sort_values(self.value_column, ascending=False)
        
        return position_players.to_dict('records')
    
    def find_best_player_for_position(self, team_name: str, formation_pos: FormationPosition) -> Optional[Dict]:
        """Find the best available player for a formation position"""
        # Try primary position first
        players = self.get_available_players(team_name, formation_pos.position)
        if players:
            return players[0]  # Best player in primary position
        
        # Try alternative positions
        for alt_position in formation_pos.alternatives:
            players = self.get_available_players(team_name, alt_position)
            if players:
                return players[0]  # Best player in alternative position
        
        return None
    
    def select_starting_xi(self, team_name: str) -> Tuple[List[Dict], str]:
        """Select the best starting XI based on team's formation"""
        if team_name not in FORMATIONS:
            raise ValueError(f"Formation not defined for {team_name}")
        
        formation = FORMATIONS[team_name]
        starting_xi = []
        used_players = set()
        
        print(f"\n🏗️ Building {team_name} lineup ({formation.name}):")
        print("=" * 50)
        
        for i, formation_pos in enumerate(formation.positions[:11]):
            # Find best available player for this position
            team_players = self.df[self.df['club'] == team_name].copy()
            available_players = team_players[
                ~team_players['player_name'].isin(self.injured_players) &
                ~team_players['player_name'].isin(self.suspended_players) &
                ~team_players['player_name'].isin(used_players)
            ]
            
            # Try primary position first
            position_players = available_players[available_players['position'] == formation_pos.position]
            position_players = position_players.sort_values('market_value_eur', ascending=False)
            
            selected_player = None
            
            if not position_players.empty:
                selected_player = position_players.iloc[0].to_dict()
            else:
                # Try alternative positions
                for alt_position in formation_pos.alternatives:
                    alt_players = available_players[available_players['position'] == alt_position]
                    alt_players = alt_players.sort_values(self.value_column, ascending=False)
                    if not alt_players.empty:
                        selected_player = alt_players.iloc[0].to_dict()
                        break
            
            if selected_player:
                starting_xi.append(selected_player)
                used_players.add(selected_player['player_name'])
                # Display value based on column type
                if self.value_column == 'market_value_mil_eur':
                    value_display = f"€{selected_player[self.value_column]:.1f}M"
                else:
                    value_display = f"€{selected_player[self.value_column]/1_000_000:.1f}M"
                print(f"  {formation_pos.position:2s}: {selected_player['player_name']:20s} ({value_display})")
            else:
                print(f"  {formation_pos.position:2s}: NO PLAYER AVAILABLE")
        
        # Calculate total squad value
        if self.value_column == 'market_value_mil_eur':
            total_value = sum(p[self.value_column] for p in starting_xi)
            print(f"\n💰 Total Starting XI Value: €{total_value:.1f}M")
        else:
            total_value = sum(p[self.value_column] for p in starting_xi)
            print(f"\n💰 Total Starting XI Value: €{total_value/1_000_000:.1f}M")
        
        return starting_xi, formation.name
    
    def get_bench_players(self, team_name: str, starting_xi: List[Dict], num_subs: int = 7) -> List[Dict]:
        """Get the best bench players (substitutes)"""
        used_players = {p['player_name'] for p in starting_xi}
        
        team_players = self.df[self.df['club'] == team_name].copy()
        available_players = team_players[
            ~team_players['player_name'].isin(self.injured_players) &
            ~team_players['player_name'].isin(self.suspended_players) &
            ~team_players['player_name'].isin(used_players)
        ]
        
        # Sort by market value and take best available
        bench_players = available_players.sort_values(self.value_column, ascending=False)
        return bench_players.head(num_subs).to_dict('records')
    
    def print_full_squad(self, team_name: str):
        """Print complete squad with starting XI and bench"""
        print(f"\n🏆 {team_name.upper()} SQUAD SELECTION")
        print("=" * 60)
        
        starting_xi, formation_name = self.select_starting_xi(team_name)
        bench = self.get_bench_players(team_name, starting_xi)
        
        print(f"\n📋 BENCH ({len(bench)} players):")
        print("-" * 30)
        for i, player in enumerate(bench, 1):
            if self.value_column == 'market_value_mil_eur':
                value_display = f"€{player[self.value_column]:.1f}M"
            else:
                value_display = f"€{player[self.value_column]/1_000_000:.1f}M"
            print(f"  {i:2d}. {player['player_name']:20s} ({player['position']}) - {value_display}")
        
        # Squad statistics
        all_players = starting_xi + bench
        avg_age = sum(p['age'] for p in all_players) / len(all_players)
        
        if self.value_column == 'market_value_mil_eur':
            total_squad_value = sum(p[self.value_column] for p in all_players)
            starting_xi_value = sum(p[self.value_column] for p in starting_xi)
            print(f"\n📊 SQUAD STATISTICS:")
            print(f"  Formation: {formation_name}")
            print(f"  Total Squad Value: €{total_squad_value:.1f}M")
            print(f"  Starting XI Value: €{starting_xi_value:.1f}M")
        else:
            total_squad_value = sum(p[self.value_column] for p in all_players)
            starting_xi_value = sum(p[self.value_column] for p in starting_xi)
            print(f"\n📊 SQUAD STATISTICS:")
            print(f"  Formation: {formation_name}")
            print(f"  Total Squad Value: €{total_squad_value/1_000_000:.1f}M")
            print(f"  Starting XI Value: €{starting_xi_value/1_000_000:.1f}M")
        print(f"  Average Age: {avg_age:.1f} years")
        print(f"  Squad Size: {len(all_players)} players")
        
        return starting_xi, bench
    
    def convert_to_enhanced_team(self, team_name: str) -> Team:
        """Convert CSV data to enhanced Team object with tactical formation"""
        starting_xi, bench = self.print_full_squad(team_name)
        all_squad_players = starting_xi + bench
        
        team = Team(team_name)
        team.formation = FORMATIONS[team_name].name
        team.starting_xi = []
        
        for player_data in all_squad_players:
            # Create PlayerStats
            stats = PlayerStats(
                pace=random.randint(60, 95),
                shooting=random.randint(40, 95) if player_data['position'] in ['CF', 'ST', 'LW', 'RW', 'AM'] else random.randint(20, 70),
                passing=random.randint(50, 95) if player_data['position'] in ['CM', 'AM', 'DM'] else random.randint(40, 85),
                dribbling=random.randint(50, 95) if player_data['position'] in ['LW', 'RW', 'AM', 'CF'] else random.randint(30, 80),
                defending=random.randint(70, 95) if player_data['position'] in ['CB', 'LB', 'RB', 'DM'] else random.randint(20, 60),
                physical=random.randint(60, 95)
            )
            
            # Create Player
            player_market_value = player_data[self.value_column]
            if self.value_column == 'market_value_mil_eur':
                # Convert millions to full euros for Player object
                player_market_value = int(player_market_value * 1_000_000)
            
            player = Player(
                name=player_data['player_name'],
                age=player_data['age'],
                position=player_data['position'],
                stats=stats,
                market_value_eur=player_market_value
            )
            
            team.add_player(player)
            
            # Mark starting XI
            if player_data in starting_xi:
                team.starting_xi.append(player)
        
        return team


def main():
    """Main function to demonstrate tactical formations"""
    print("🏆" + "="*60 + "🏆")
    print("  TACTICAL FORMATION SYSTEM")
    print("  Automatic Starting XI Selection Based on Market Value")
    print("🏆" + "="*60 + "🏆")
    
    # Try to use the improved CSV first, fallback to original
    csv_files = ['real_transfermarkt_squads_improved.csv', 'real_transfermarkt_squads.csv']
    csv_file = None
    
    for file in csv_files:
        try:
            import os
            if os.path.exists(file):
                csv_file = file
                break
        except:
            continue
    
    if csv_file is None:
        print("❌ No CSV file found! Please run the scraper first.")
        return
    
    print(f"📊 Using data from: {csv_file}")
    manager = TacticalManager(csv_file)
    
    print(f"\n📋 Available teams:")
    teams = manager.df['club'].unique()
    for i, team in enumerate(teams, 1):
        if team in FORMATIONS:
            print(f"  {i:2d}. {team} ({FORMATIONS[team].name})")
    
    while True:
        print(f"\n" + "="*50)
        print("🎮 TACTICAL MANAGER OPTIONS:")
        print("="*50)
        print("1. 📋 Show squad for specific team")
        print("2. ⚽ Compare starting XIs")
        print("3. 🚑 Set injuries/suspensions")
        print("4. 🏆 Generate all teams for tournament")
        print("5. 🎯 Exit")
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                print(f"\nAvailable teams:")
                valid_teams = [team for team in teams if team in FORMATIONS]
                for i, team in enumerate(valid_teams, 1):
                    print(f"  {i}. {team}")
                
                try:
                    team_idx = int(input("Select team number: ")) - 1
                    if 0 <= team_idx < len(valid_teams):
                        selected_team = valid_teams[team_idx]
                        manager.print_full_squad(selected_team)
                    else:
                        print("❌ Invalid team selection!")
                except ValueError:
                    print("❌ Please enter a valid number!")
            
            elif choice == '2':
                print(f"\nSelect 2 teams to compare:")
                valid_teams = [team for team in teams if team in FORMATIONS]
                for i, team in enumerate(valid_teams, 1):
                    print(f"  {i}. {team}")
                
                try:
                    team1_idx = int(input("First team: ")) - 1
                    team2_idx = int(input("Second team: ")) - 1
                    
                    if 0 <= team1_idx < len(valid_teams) and 0 <= team2_idx < len(valid_teams):
                        team1 = valid_teams[team1_idx]
                        team2 = valid_teams[team2_idx]
                        
                        print(f"\n🆚 {team1} vs {team2}")
                        print("=" * 60)
                        
                        xi1, formation1 = manager.select_starting_xi(team1)
                        xi2, formation2 = manager.select_starting_xi(team2)
                        
                        value1 = sum(p['market_value_eur'] for p in xi1) / 1_000_000
                        value2 = sum(p['market_value_eur'] for p in xi2) / 1_000_000
                        
                        print(f"\n📊 COMPARISON:")
                        print(f"  {team1} ({formation1}): €{value1:.1f}M")
                        print(f"  {team2} ({formation2}): €{value2:.1f}M")
                        
                        if value1 > value2:
                            print(f"  💰 {team1} has the more valuable starting XI!")
                        elif value2 > value1:
                            print(f"  💰 {team2} has the more valuable starting XI!")
                        else:
                            print(f"  🤝 Both teams have equally valuable starting XIs!")
                    
                    else:
                        print("❌ Invalid team selection!")
                except ValueError:
                    print("❌ Please enter valid numbers!")
            
            elif choice == '3':
                print(f"\nSet injuries and suspensions:")
                valid_teams = [team for team in teams if team in FORMATIONS]
                for i, team in enumerate(valid_teams, 1):
                    print(f"  {i}. {team}")
                
                try:
                    team_idx = int(input("Select team: ")) - 1
                    if 0 <= team_idx < len(valid_teams):
                        selected_team = valid_teams[team_idx]
                        
                        # Show team players
                        team_players = manager.df[manager.df['club'] == selected_team]['player_name'].tolist()
                        print(f"\n{selected_team} players:")
                        for i, player in enumerate(team_players, 1):
                            print(f"  {i:2d}. {player}")
                        
                        injured_input = input("\nEnter injured player names (comma-separated, or press Enter for none): ")
                        suspended_input = input("Enter suspended player names (comma-separated, or press Enter for none): ")
                        
                        injured = [name.strip() for name in injured_input.split(',') if name.strip()]
                        suspended = [name.strip() for name in suspended_input.split(',') if name.strip()]
                        
                        manager.set_injuries_and_suspensions(selected_team, injured, suspended)
                        
                        if injured or suspended:
                            print(f"\n✅ Updated injury/suspension list:")
                            if injured:
                                print(f"  🚑 Injured: {', '.join(injured)}")
                            if suspended:
                                print(f"  🔴 Suspended: {', '.join(suspended)}")
                            
                            # Show updated squad
                            manager.print_full_squad(selected_team)
                        else:
                            print(f"\n✅ No injuries or suspensions set.")
                    
                    else:
                        print("❌ Invalid team selection!")
                except ValueError:
                    print("❌ Please enter a valid number!")
            
            elif choice == '4':
                print(f"\n🏆 Generating all teams for tournament...")
                enhanced_teams = []
                
                valid_teams = [team for team in teams if team in FORMATIONS]
                for team_name in valid_teams:
                    enhanced_team = manager.convert_to_enhanced_team(team_name)
                    enhanced_teams.append(enhanced_team)
                
                print(f"\n✅ Generated {len(enhanced_teams)} teams ready for tournament!")
                print(f"📊 Teams with formations:")
                
                total_value = 0
                for team in enhanced_teams:
                    team_value = sum(p.market_value_eur for p in team.starting_xi)
                    total_value += team_value
                    print(f"  {team.name:20s} ({team.formation}): €{team_value/1_000_000:.1f}M")
                
                print(f"\n💰 Total tournament value: €{total_value/1_000_000:.0f}M")
                print(f"🎮 Teams are ready for your Ultimate Football Simulator!")
                
                return enhanced_teams
            
            elif choice == '5':
                print("\n👋 Thanks for using the Tactical Formation System!")
                break
            
            else:
                print("❌ Invalid choice! Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
