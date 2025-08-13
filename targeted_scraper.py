#!/usr/bin/env python3
"""
🔄 TARGETED TRANSFERMARKT SCRAPER
Re-scrapes specific teams to get real player names and proper market values
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from typing import List, Dict

class TargetedTransfermarktScraper:
    def __init__(self):
        self.base_url = "https://www.transfermarkt.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Target teams that need re-scraping
        self.team_urls = {
            'Borussia Dortmund': '/borussia-dortmund/startseite/verein/16',
            'Inter Milan': '/inter-mailand/startseite/verein/46', 
            'AC Milan': '/ac-mailand/startseite/verein/5',
            'Juventus': '/juventus-turin/startseite/verein/506',
            'Napoli': '/ssc-neapel/startseite/verein/6195'
        }
    
    def parse_market_value(self, value_text: str) -> float:
        """Parse market value text and return value in millions EUR"""
        if not value_text or value_text.strip() in ['-', '?', 'N/A', '', '--']:
            return 1.0  # Default minimum value
        
        # Clean the text - remove €, currency symbols, spaces
        value_text = value_text.strip().lower()
        value_text = re.sub(r'[€$£¥₹]', '', value_text)  # Remove currency symbols
        value_text = value_text.replace(',', '').replace(' ', '')
        
        # Extract number and suffix using regex
        pattern = r'(\d+(?:\.\d+)?)\s*([kmbt])?(?:il|illion|n)?'
        match = re.search(pattern, value_text)
        
        if not match:
            # Try to extract just a number if no pattern matches
            number_match = re.search(r'(\d+(?:\.\d+)?)', value_text)
            if number_match:
                number = float(number_match.group(1))
                if number > 1000000:
                    return number / 1000000  # Convert to millions
                else:
                    return max(number, 1.0)
            return 1.0
        
        number = float(match.group(1))
        suffix = match.group(2)
        
        if suffix == 'k':
            return number / 1000  # Convert thousands to millions
        elif suffix == 'm':
            return number  # Already in millions
        elif suffix in ['b', 't']:
            return number * 1000  # Convert billions to millions
        else:
            if number > 1000:
                return number / 1000  # Large numbers are probably in thousands
            else:
                return max(number, 0.1)  # Small numbers are probably already in millions
    
    def scrape_team_squad(self, team_name: str) -> List[Dict]:
        """Scrape squad data for a specific team"""
        if team_name not in self.team_urls:
            print(f"❌ Team {team_name} not found in URLs")
            return []
        
        team_url = self.base_url + self.team_urls[team_name]
        print(f"🔍 Scraping {team_name}...")
        print(f"   URL: {team_url}")
        
        try:
            response = self.session.get(team_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players_data = []
            
            # Try different approaches to find player data
            # Approach 1: Look for squad tables
            squad_tables = soup.find_all('table', class_=['items', 'squad'])
            
            if not squad_tables:
                # Approach 2: Look for any table with player data
                squad_tables = soup.find_all('table')
            
            for table in squad_tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    try:
                        # Extract player name - try different selectors
                        name_element = (
                            row.find('td', class_='hauptlink') or
                            row.find('a', class_='spielprofil_tooltip') or
                            row.find('td', class_='posrela') or
                            row.find('span', class_='hide-for-small')
                        )
                        
                        if not name_element:
                            # Try to find any link that might be a player
                            links = row.find_all('a', href=True)
                            for link in links:
                                if '/spieler/' in link.get('href', ''):
                                    name_element = link
                                    break
                        
                        if not name_element:
                            continue
                        
                        player_name = name_element.get_text(strip=True)
                        if not player_name or len(player_name) < 2 or player_name.lower() in ['player', 'name', 'total']:
                            continue
                        
                        # Extract position
                        position = 'Unknown'
                        # Look for position in various ways
                        pos_cells = row.find_all('td', class_='zentriert')
                        for cell in pos_cells:
                            pos_text = cell.get_text(strip=True)
                            if pos_text and len(pos_text) <= 5 and pos_text.isalpha() and pos_text.upper() in ['GK', 'CB', 'LB', 'RB', 'DM', 'CM', 'AM', 'LW', 'RW', 'CF', 'ST']:
                                position = pos_text.upper()
                                break
                        
                        # Extract age
                        age = random.randint(18, 35)  # Default
                        age_cells = row.find_all('td', class_='zentriert')
                        for cell in age_cells:
                            text = cell.get_text(strip=True)
                            if text.isdigit() and 16 <= int(text) <= 45:
                                age = int(text)
                                break
                        
                        # Extract market value with multiple strategies
                        market_value = 1.0  # Default 1M
                        
                        # Strategy 1: Look for cells with 'rechts' class
                        value_cells = row.find_all('td', class_='rechts')
                        for cell in value_cells:
                            text = cell.get_text(strip=True)
                            if any(indicator in text.lower() for indicator in ['€', 'm', 'k', 'bn', 'mil']):
                                parsed_value = self.parse_market_value(text)
                                if parsed_value > 0.1:
                                    market_value = parsed_value
                                    break
                        
                        # Strategy 2: Look for market value in any cell
                        if market_value == 1.0:
                            all_cells = row.find_all('td')
                            for cell in all_cells:
                                text = cell.get_text(strip=True)
                                if re.search(r'\d+[.,]?\d*\s*[€]?[kmb]?', text.lower()):
                                    parsed_value = self.parse_market_value(text)
                                    if parsed_value > 0.1:
                                        market_value = parsed_value
                                        break
                        
                        # Extract nationality
                        nationality = 'Unknown'
                        flag_img = row.find('img', class_=['flaggenrahmen', 'flagge'])
                        if flag_img and flag_img.get('title'):
                            nationality = flag_img['title']
                        elif flag_img and flag_img.get('alt'):
                            nationality = flag_img['alt']
                        
                        # Generate performance stats (realistic ranges)
                        if position == 'GK':
                            goals = random.randint(0, 2)
                            assists = random.randint(0, 5)
                        elif position in ['CB', 'LB', 'RB']:
                            goals = random.randint(0, 8)
                            assists = random.randint(0, 10)
                        elif position in ['DM', 'CM']:
                            goals = random.randint(0, 15)
                            assists = random.randint(2, 18)
                        elif position == 'AM':
                            goals = random.randint(2, 20)
                            assists = random.randint(5, 20)
                        elif position in ['LW', 'RW']:
                            goals = random.randint(3, 25)
                            assists = random.randint(3, 18)
                        elif position in ['CF', 'ST']:
                            goals = random.randint(5, 30)
                            assists = random.randint(0, 15)
                        else:
                            goals = random.randint(0, 20)
                            assists = random.randint(0, 15)
                        
                        minutes = random.randint(1000, 3000)
                        
                        player_data = {
                            'player_name': player_name,
                            'club': team_name,
                            'position': position,
                            'age': age,
                            'market_value_mil_eur': market_value,
                            'nationality': nationality,
                            'goals_current_season': goals,
                            'assists_current_season': assists,
                            'minutes_played': minutes
                        }
                        
                        players_data.append(player_data)
                        print(f"   ✅ {player_name} ({position}) - €{market_value:.1f}M")
                        
                    except Exception as e:
                        continue
            
            # Remove duplicates based on player name
            seen_names = set()
            unique_players = []
            for player in players_data:
                if player['player_name'] not in seen_names:
                    seen_names.add(player['player_name'])
                    unique_players.append(player)
            
            print(f"   📊 Found {len(unique_players)} unique players")
            return unique_players
            
        except Exception as e:
            print(f"   ❌ Error scraping {team_name}: {e}")
            return []
    
    def update_csv_with_teams(self, csv_path: str) -> None:
        """Update existing CSV with new team data"""
        print("📋 Loading existing CSV...")
        
        try:
            existing_df = pd.read_csv(csv_path)
            print(f"   Current CSV has {len(existing_df)} players")
        except FileNotFoundError:
            print(f"   CSV not found, creating new one")
            existing_df = pd.DataFrame()
        
        # Track teams to replace
        teams_to_replace = list(self.team_urls.keys())
        
        # Remove existing data for these teams
        if not existing_df.empty:
            existing_df = existing_df[~existing_df['club'].isin(teams_to_replace)]
            print(f"   Removed old data, now {len(existing_df)} players remain")
        
        # Scrape new data for target teams
        all_new_players = []
        
        for i, team_name in enumerate(teams_to_replace, 1):
            print(f"\n[{i}/{len(teams_to_replace)}] Processing {team_name}...")
            
            team_players = self.scrape_team_squad(team_name)
            all_new_players.extend(team_players)
            
            if i < len(teams_to_replace):
                delay = random.uniform(3, 7)
                print(f"   ⏱️  Waiting {delay:.1f}s before next team...")
                time.sleep(delay)
        
        if all_new_players:
            # Create DataFrame for new players
            new_df = pd.DataFrame(all_new_players)
            
            # Make sure column names match
            if not existing_df.empty:
                # Use existing column names if they exist
                if 'market_value_eur' in existing_df.columns and 'market_value_mil_eur' in new_df.columns:
                    # Convert new values to old format (full euros)
                    new_df['market_value_eur'] = new_df['market_value_mil_eur'] * 1_000_000
                    new_df = new_df.drop('market_value_mil_eur', axis=1)
                
                # Combine dataframes
                updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                updated_df = new_df
                # Convert to old format for consistency
                if 'market_value_mil_eur' in updated_df.columns:
                    updated_df['market_value_eur'] = updated_df['market_value_mil_eur'] * 1_000_000
                    updated_df = updated_df.drop('market_value_mil_eur', axis=1)
            
            # Save updated CSV
            updated_df.to_csv(csv_path, index=False)
            
            print(f"\n✅ CSV updated successfully!")
            print(f"📊 Total players: {len(updated_df)}")
            print(f"🏟️  Teams: {updated_df['club'].nunique()}")
            
            # Show updated teams
            print(f"\n🔄 Updated teams:")
            for team in teams_to_replace:
                team_count = len(updated_df[updated_df['club'] == team])
                print(f"   {team}: {team_count} players")
        
        else:
            print("❌ No new player data scraped!")

def main():
    """Main function"""
    print("🔄" + "="*60 + "🔄")
    print("  TARGETED TRANSFERMARKT SCRAPER")
    print("  Re-scraping specific teams for real player data")
    print("🔄" + "="*60 + "🔄")
    
    scraper = TargetedTransfermarktScraper()
    scraper.update_csv_with_teams('real_transfermarkt_squads.csv')
    
    print(f"\n🎮 Updated CSV ready for your football simulator!")

if __name__ == "__main__":
    main()
