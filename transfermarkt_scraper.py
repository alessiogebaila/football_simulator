#!/usr/bin/env python3
"""
🌐 TRANSFERMARKT REAL DATA SCRAPER
Scrapes actual squad data from Transfermarkt for realistic tournaments

Teams included:
- Real Madrid, Atletico Madrid, Barcelona
- Man City, Liverpool, Arsenal, Chelsea, Man United, Tottenham  
- PSG, Bayern Munich, Borussia Dortmund
- Inter, Napoli, Juventus, AC Milan
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class ScrapedPlayer:
    """Player data scraped from Transfermarkt"""
    name: str
    position: str
    age: int
    market_value_eur: int
    nationality: str
    club: str
    shirt_number: Optional[int] = None
    contract_expires: Optional[str] = None

class TransfermarktScraper:
    """Scraper for Transfermarkt squad data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Club URLs on Transfermarkt (these are the actual club IDs)
        self.club_urls = {
            # Spanish Clubs
            'Real Madrid': 'https://www.transfermarkt.com/real-madrid/kader/verein/418',
            'Atletico Madrid': 'https://www.transfermarkt.com/atletico-madrid/kader/verein/13',
            'Barcelona': 'https://www.transfermarkt.com/fc-barcelona/kader/verein/131',
            
            # English Clubs
            'Manchester City': 'https://www.transfermarkt.com/manchester-city/kader/verein/281',
            'Liverpool': 'https://www.transfermarkt.com/fc-liverpool/kader/verein/31',
            'Arsenal': 'https://www.transfermarkt.com/fc-arsenal/kader/verein/11',
            'Chelsea': 'https://www.transfermarkt.com/fc-chelsea/kader/verein/631',
            'Manchester United': 'https://www.transfermarkt.com/manchester-united/kader/verein/985',
            'Tottenham': 'https://www.transfermarkt.com/tottenham-hotspur/kader/verein/148',
            
            # French Club
            'PSG': 'https://www.transfermarkt.com/paris-saint-germain/kader/verein/583',
            
            # German Clubs
            'Bayern Munich': 'https://www.transfermarkt.com/fc-bayern-munchen/kader/verein/27',
            'Borussia Dortmund': 'https://www.transfermarkt.com/borussia-dortmund/kader/verein/16',
            
            # Italian Clubs
            'Inter': 'https://www.transfermarkt.com/inter-mailand/kader/verein/46',
            'Napoli': 'https://www.transfermarkt.com/ssc-neapel/kader/verein/6195',
            'Juventus': 'https://www.transfermarkt.com/juventus-turin/kader/verein/506',
            'AC Milan': 'https://www.transfermarkt.com/ac-mailand/kader/verein/5'
        }
    
    def parse_market_value(self, value_str: str) -> int:
        """Parse market value string to integer in EUR"""
        if not value_str or value_str == '-':
            return 0
        
        # Remove currency symbols and spaces
        value_str = value_str.replace('€', '').replace(',', '').replace('.', '').strip()
        
        # Handle millions (m) and thousands (k)
        if 'm' in value_str.lower():
            value = float(value_str.lower().replace('m', ''))
            return int(value * 1_000_000)
        elif 'k' in value_str.lower():
            value = float(value_str.lower().replace('k', ''))
            return int(value * 1_000)
        else:
            try:
                return int(value_str)
            except:
                return 0
    
    def scrape_squad(self, club_name: str) -> List[ScrapedPlayer]:
        """Scrape squad data for a specific club"""
        if club_name not in self.club_urls:
            print(f"❌ Club {club_name} not found in URLs")
            return []
        
        url = self.club_urls[club_name]
        print(f"🔍 Scraping {club_name} squad from Transfermarkt...")
        
        try:
            # Add delay to be respectful
            time.sleep(2)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the squad table
            players = []
            
            # Look for the main squad table
            squad_table = soup.find('table', {'class': 'items'})
            if not squad_table:
                print(f"⚠️ Could not find squad table for {club_name}")
                return []
            
            # Parse each player row
            rows = squad_table.find('tbody').find_all('tr')
            
            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 6:
                        continue
                    
                    # Extract player data
                    shirt_number_cell = cells[0]
                    shirt_number = None
                    if shirt_number_cell.text.strip().isdigit():
                        shirt_number = int(shirt_number_cell.text.strip())
                    
                    # Player name
                    name_cell = cells[1]
                    name_link = name_cell.find('a')
                    if name_link:
                        player_name = name_link.text.strip()
                    else:
                        continue
                    
                    # Position
                    position_cell = cells[2]
                    position = position_cell.text.strip()
                    
                    # Age
                    age_cell = cells[3]
                    age_text = age_cell.text.strip()
                    age = int(age_text) if age_text.isdigit() else 25
                    
                    # Nationality
                    nationality_cell = cells[4]
                    nationality_img = nationality_cell.find('img')
                    nationality = nationality_img.get('title', 'Unknown') if nationality_img else 'Unknown'
                    
                    # Market Value
                    value_cell = cells[5]
                    value_text = value_cell.text.strip()
                    market_value = self.parse_market_value(value_text)
                    
                    player = ScrapedPlayer(
                        name=player_name,
                        position=position,
                        age=age,
                        market_value_eur=market_value,
                        nationality=nationality,
                        club=club_name,
                        shirt_number=shirt_number
                    )
                    
                    players.append(player)
                    
                except Exception as e:
                    print(f"⚠️ Error parsing player row: {e}")
                    continue
            
            print(f"✅ Scraped {len(players)} players from {club_name}")
            return players
            
        except requests.RequestException as e:
            print(f"❌ Network error scraping {club_name}: {e}")
            return []
        except Exception as e:
            print(f"❌ Error scraping {club_name}: {e}")
            return []
    
    def scrape_all_clubs(self) -> Dict[str, List[ScrapedPlayer]]:
        """Scrape all club squads"""
        all_squads = {}
        
        print("🌐 Starting Transfermarkt scraping for all clubs...")
        print("⏰ This may take a few minutes to be respectful to the server...")
        
        for club_name in self.club_urls.keys():
            squad = self.scrape_squad(club_name)
            if squad:
                all_squads[club_name] = squad
            
            # Respectful delay between requests
            time.sleep(3)
        
        return all_squads
    
    def save_squads_to_json(self, squads: Dict[str, List[ScrapedPlayer]], filename: str = 'transfermarkt_squads.json'):
        """Save scraped squads to JSON file"""
        # Convert to serializable format
        squads_data = {}
        for club, players in squads.items():
            squads_data[club] = []
            for player in players:
                squads_data[club].append({
                    'name': player.name,
                    'position': player.position,
                    'age': player.age,
                    'market_value_eur': player.market_value_eur,
                    'nationality': player.nationality,
                    'club': player.club,
                    'shirt_number': player.shirt_number
                })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(squads_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved squad data to {filename}")
    
    def load_squads_from_json(self, filename: str = 'transfermarkt_squads.json') -> Dict[str, List[ScrapedPlayer]]:
        """Load squads from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                squads_data = json.load(f)
            
            squads = {}
            for club, players_data in squads_data.items():
                squads[club] = []
                for player_data in players_data:
                    player = ScrapedPlayer(**player_data)
                    squads[club].append(player)
            
            print(f"📂 Loaded squad data from {filename}")
            return squads
            
        except FileNotFoundError:
            print(f"📂 No saved data found at {filename}")
            return {}
        except Exception as e:
            print(f"❌ Error loading squads: {e}")
            return {}


def convert_to_simulator_format(scraped_squads: Dict[str, List[ScrapedPlayer]]) -> List[Dict]:
    """Convert scraped data to simulator format"""
    simulator_players = []
    
    # Position mapping
    position_mapping = {
        'Goalkeeper': 'GK',
        'Centre-Back': 'CB',
        'Left-Back': 'LB',
        'Right-Back': 'RB',
        'Defensive Midfield': 'CDM',
        'Central Midfield': 'CM',
        'Attacking Midfield': 'CAM',
        'Left Midfield': 'LM',
        'Right Midfield': 'RM',
        'Left Winger': 'LW',
        'Right Winger': 'RW',
        'Centre-Forward': 'ST',
        'Second Striker': 'CF'
    }
    
    for club, players in scraped_squads.items():
        for player in players:
            # Map position
            mapped_position = position_mapping.get(player.position, player.position[:3])
            
            # Calculate ratings based on market value and position
            base_rating = min(99, max(60, 65 + (player.market_value_eur / 2_000_000)))
            
            # Position-specific adjustments
            if mapped_position == 'GK':
                pace = max(30, base_rating - 20)
                shooting = max(20, base_rating - 40)
                passing = max(60, base_rating - 10)
                dribbling = max(40, base_rating - 20)
                defending = min(99, base_rating + 5)
                physical = min(99, base_rating)
            elif mapped_position in ['CB', 'LB', 'RB']:
                pace = max(50, base_rating - 10)
                shooting = max(30, base_rating - 25)
                passing = max(60, base_rating - 5)
                dribbling = max(50, base_rating - 15)
                defending = min(99, base_rating + 10)
                physical = min(99, base_rating + 5)
            elif mapped_position in ['CDM', 'CM']:
                pace = max(60, base_rating - 5)
                shooting = max(50, base_rating - 10)
                passing = min(99, base_rating + 5)
                dribbling = max(70, base_rating)
                defending = max(60, base_rating - 5)
                physical = max(70, base_rating)
            elif mapped_position in ['CAM', 'LM', 'RM', 'LW', 'RW']:
                pace = min(99, base_rating + 5)
                shooting = max(60, base_rating)
                passing = min(99, base_rating + 5)
                dribbling = min(99, base_rating + 10)
                defending = max(30, base_rating - 25)
                physical = max(60, base_rating - 5)
            else:  # Strikers
                pace = min(99, base_rating + 3)
                shooting = min(99, base_rating + 15)
                passing = max(60, base_rating - 5)
                dribbling = min(99, base_rating + 5)
                defending = max(20, base_rating - 30)
                physical = min(99, base_rating + 5)
            
            # Add some randomness
            noise = np.random.normal(0, 3)
            pace = max(20, min(99, int(pace + noise)))
            shooting = max(20, min(99, int(shooting + noise)))
            passing = max(20, min(99, int(passing + noise)))
            dribbling = max(20, min(99, int(dribbling + noise)))
            defending = max(20, min(99, int(defending + noise)))
            physical = max(20, min(99, int(physical + noise)))
            
            simulator_player = {
                'player_name': player.name,
                'club': player.club,
                'position': mapped_position,
                'market_value_eur': player.market_value_eur,
                'age': player.age,
                'nationality': player.nationality,
                'shirt_number': player.shirt_number,
                'pace': pace,
                'shooting': shooting,
                'passing': passing,
                'dribbling': dribbling,
                'defending': defending,
                'physical': physical,
                'goals_current_season': max(0, int(np.random.poisson(3 if mapped_position in ['ST', 'CF'] else 1))),
                'assists_current_season': max(0, int(np.random.poisson(2 if mapped_position in ['CAM', 'LW', 'RW'] else 1))),
                'minutes_played': max(500, int(np.random.normal(2000, 500)))
            }
            
            simulator_players.append(simulator_player)
    
    return simulator_players


def main():
    """Main function to scrape Transfermarkt data"""
    scraper = TransfermarktScraper()
    
    print("🌐 TRANSFERMARKT REAL DATA SCRAPER")
    print("="*50)
    print("This will scrape current squad data for 16 top European clubs")
    print("⚠️ Please be patient - this respects rate limits")
    print("="*50)
    
    while True:
        print("\n🎮 CHOOSE AN OPTION:")
        print("1. 🔍 Scrape fresh data from Transfermarkt (takes ~5 minutes)")
        print("2. 📂 Load previously scraped data")
        print("3. 📊 Show available clubs")
        print("4. 🏆 Generate simulator data file")
        print("5. 🎯 Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            # Fresh scrape
            print("\n🔍 Starting fresh scrape...")
            squads = scraper.scrape_all_clubs()
            
            if squads:
                scraper.save_squads_to_json(squads)
                
                # Show summary
                total_players = sum(len(players) for players in squads.values())
                total_value = sum(sum(p.market_value_eur for p in players) for players in squads.values())
                
                print(f"\n📊 SCRAPING SUMMARY:")
                print(f"  🏈 Clubs: {len(squads)}")
                print(f"  👥 Total Players: {total_players}")
                print(f"  💰 Total Squad Value: €{total_value/1_000_000:.0f}M")
                
                for club, players in squads.items():
                    club_value = sum(p.market_value_eur for p in players)
                    print(f"    {club}: {len(players)} players, €{club_value/1_000_000:.0f}M")
            else:
                print("❌ No data was scraped successfully")
        
        elif choice == '2':
            # Load saved data
            squads = scraper.load_squads_from_json()
            
            if squads:
                total_players = sum(len(players) for players in squads.values())
                total_value = sum(sum(p.market_value_eur for p in players) for players in squads.values())
                
                print(f"\n📊 LOADED DATA SUMMARY:")
                print(f"  🏈 Clubs: {len(squads)}")
                print(f"  👥 Total Players: {total_players}")
                print(f"  💰 Total Squad Value: €{total_value/1_000_000:.0f}M")
                
                for club, players in squads.items():
                    club_value = sum(p.market_value_eur for p in players)
                    most_valuable = max(players, key=lambda p: p.market_value_eur)
                    print(f"    {club}: {len(players)} players, €{club_value/1_000_000:.0f}M")
                    print(f"      💎 Most valuable: {most_valuable.name} (€{most_valuable.market_value_eur/1_000_000:.0f}M)")
        
        elif choice == '3':
            # Show clubs
            print(f"\n🏈 AVAILABLE CLUBS ({len(scraper.club_urls)}):")
            for i, club in enumerate(scraper.club_urls.keys(), 1):
                print(f"  {i:2d}. {club}")
        
        elif choice == '4':
            # Generate simulator file
            squads = scraper.load_squads_from_json()
            
            if not squads:
                print("❌ No squad data available. Please scrape first!")
                continue
            
            print("\n🏆 Converting to simulator format...")
            simulator_data = convert_to_simulator_format(squads)
            
            # Save to Python file
            with open('real_transfermarkt_data.py', 'w', encoding='utf-8') as f:
                f.write('#!/usr/bin/env python3\n')
                f.write('"""\n')
                f.write('🌐 REAL TRANSFERMARKT DATA\n')
                f.write('Scraped from transfermarkt.com for realistic tournaments\n')
                f.write('"""\n\n')
                f.write('REAL_TRANSFERMARKT_DATA = [\n')
                
                for player in simulator_data:
                    f.write('    {\n')
                    for key, value in player.items():
                        if isinstance(value, str):
                            f.write(f'        "{key}": "{value}",\n')
                        else:
                            f.write(f'        "{key}": {value},\n')
                    f.write('    },\n')
                
                f.write(']\n')
            
            print(f"✅ Generated real_transfermarkt_data.py with {len(simulator_data)} players!")
            print("🎮 You can now use this in your ultimate simulator!")
        
        elif choice == '5':
            print("\n👋 Goodbye! Happy simulating! ⚽")
            break
        
        else:
            print("❌ Invalid choice! Please enter 1-5.")


if __name__ == "__main__":
    main()
