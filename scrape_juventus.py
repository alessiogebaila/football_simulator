import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

def scrape_juventus_squad():
    # Juventus squad URL on Transfermarkt
    url = "https://www.transfermarkt.com/juventus-fc/startseite/verein/506"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("Scraping Juventus squad from Transfermarkt...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the squad table
        squad_table = soup.find('table', {'class': 'items'})
        
        if not squad_table:
            print("Could not find squad table. Trying alternative URL...")
            # Try the squad page directly
            url = "https://www.transfermarkt.com/juventus-fc/kader/verein/506"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            squad_table = soup.find('table', {'class': 'items'})
        
        if not squad_table:
            print("Still could not find squad table. Using manual Juventus data...")
            return create_juventus_manual_data()
        
        players = []
        rows = squad_table.find_all('tr', {'class': ['odd', 'even']})
        
        for row in rows:
            try:
                # Kit number
                kit_cell = row.find('div', {'class': 'rn_nummer'})
                kit_number = kit_cell.text.strip() if kit_cell else ''
                
                # Player name
                name_cell = row.find('td', {'class': 'posrela'})
                if name_cell:
                    name_link = name_cell.find('a')
                    player_name = name_link.text.strip() if name_link else ''
                else:
                    continue
                
                # Position
                position_cell = row.find_all('td')[1] if len(row.find_all('td')) > 1 else None
                position = position_cell.text.strip() if position_cell else 'Unknown'
                
                # Age (birth date)
                age_cell = row.find('td', {'class': 'zentriert'})
                age_text = age_cell.text.strip() if age_cell else ''
                age = extract_age(age_text)
                birth_date = age_text
                
                # Market value
                value_cell = row.find('td', {'class': 'rechts hauptlink'})
                market_value = parse_market_value(value_cell.text.strip() if value_cell else '0')
                
                # Nationality
                nationality_cell = row.find('img', {'class': 'flaggenrahmen'})
                nationality = nationality_cell.get('title', 'Unknown') if nationality_cell else 'Unknown'
                
                if player_name:  # Only add if we have a player name
                    players.append({
                        'kit_number': kit_number,
                        'player_name': player_name,
                        'club': 'Juventus',
                        'position': map_position(position),
                        'age': age,
                        'market_value_eur': market_value,
                        'nationality': nationality,
                        'birth_date': birth_date
                    })
                    
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        return players
        
    except Exception as e:
        print(f"Error scraping Juventus: {e}")
        print("Using manual Juventus data instead...")
        return create_juventus_manual_data()

def create_juventus_manual_data():
    """Create manual Juventus squad data based on current 2024-25 season"""
    return [
        # Goalkeepers
        {'kit_number': '1', 'player_name': 'Wojciech Szczęsny', 'club': 'Juventus', 'position': 'GK', 'age': 34, 'market_value_eur': 8000000.0, 'nationality': 'Poland', 'birth_date': 'Apr 18, 1990 (34)'},
        {'kit_number': '23', 'player_name': 'Carlo Pinsoglio', 'club': 'Juventus', 'position': 'GK', 'age': 34, 'market_value_eur': 200000.0, 'nationality': 'Italy', 'birth_date': 'Mar 16, 1990 (34)'},
        {'kit_number': '36', 'player_name': 'Mattia Perin', 'club': 'Juventus', 'position': 'GK', 'age': 32, 'market_value_eur': 5000000.0, 'nationality': 'Italy', 'birth_date': 'Nov 10, 1992 (32)'},
        
        # Defenders
        {'kit_number': '3', 'player_name': 'Gleison Bremer', 'club': 'Juventus', 'position': 'CB', 'age': 27, 'market_value_eur': 65000000.0, 'nationality': 'Brazil', 'birth_date': 'Mar 18, 1997 (27)'},
        {'kit_number': '4', 'player_name': 'Federico Gatti', 'club': 'Juventus', 'position': 'CB', 'age': 26, 'market_value_eur': 25000000.0, 'nationality': 'Italy', 'birth_date': 'Jun 24, 1998 (26)'},
        {'kit_number': '6', 'player_name': 'Danilo', 'club': 'Juventus', 'position': 'RB', 'age': 33, 'market_value_eur': 4000000.0, 'nationality': 'Brazil', 'birth_date': 'Jul 15, 1991 (33)'},
        {'kit_number': '12', 'player_name': 'Alex Sandro', 'club': 'Juventus', 'position': 'LB', 'age': 33, 'market_value_eur': 8000000.0, 'nationality': 'Brazil', 'birth_date': 'Jan 26, 1991 (33)'},
        {'kit_number': '15', 'player_name': 'Pierre Kalulu', 'club': 'Juventus', 'position': 'CB', 'age': 24, 'market_value_eur': 20000000.0, 'nationality': 'France', 'birth_date': 'Jun 5, 2000 (24)'},
        {'kit_number': '17', 'player_name': 'Andrea Cambiaso', 'club': 'Juventus', 'position': 'LB', 'age': 24, 'market_value_eur': 35000000.0, 'nationality': 'Italy', 'birth_date': 'Feb 1, 2000 (24)'},
        {'kit_number': '27', 'player_name': 'Andrea Cambiaso', 'club': 'Juventus', 'position': 'LB', 'age': 24, 'market_value_eur': 35000000.0, 'nationality': 'Italy', 'birth_date': 'Feb 1, 2000 (24)'},
        {'kit_number': '37', 'player_name': 'Nicolò Savona', 'club': 'Juventus', 'position': 'RB', 'age': 21, 'market_value_eur': 8000000.0, 'nationality': 'Italy', 'birth_date': 'Sep 7, 2003 (21)'},
        
        # Midfielders
        {'kit_number': '5', 'player_name': 'Manuel Locatelli', 'club': 'Juventus', 'position': 'CDM', 'age': 26, 'market_value_eur': 30000000.0, 'nationality': 'Italy', 'birth_date': 'Jan 8, 1998 (26)'},
        {'kit_number': '8', 'player_name': 'Weston McKennie', 'club': 'Juventus', 'position': 'CM', 'age': 26, 'market_value_eur': 25000000.0, 'nationality': 'United States', 'birth_date': 'Aug 28, 1998 (26)'},
        {'kit_number': '16', 'player_name': 'Khéphren Thuram', 'club': 'Juventus', 'position': 'CM', 'age': 23, 'market_value_eur': 35000000.0, 'nationality': 'France', 'birth_date': 'Mar 26, 2001 (23)'},
        {'kit_number': '19', 'player_name': 'Khéphren Thuram', 'club': 'Juventus', 'position': 'CM', 'age': 23, 'market_value_eur': 35000000.0, 'nationality': 'France', 'birth_date': 'Mar 26, 2001 (23)'},
        {'kit_number': '21', 'player_name': 'Niccolò Fagioli', 'club': 'Juventus', 'position': 'CM', 'age': 23, 'market_value_eur': 25000000.0, 'nationality': 'Italy', 'birth_date': 'Feb 12, 2001 (23)'},
        {'kit_number': '26', 'player_name': 'Douglas Luiz', 'club': 'Juventus', 'position': 'CM', 'age': 26, 'market_value_eur': 50000000.0, 'nationality': 'Brazil', 'birth_date': 'May 9, 1998 (26)'},
        
        # Forwards
        {'kit_number': '7', 'player_name': 'Federico Chiesa', 'club': 'Juventus', 'position': 'RW', 'age': 27, 'market_value_eur': 35000000.0, 'nationality': 'Italy', 'birth_date': 'Oct 25, 1997 (27)'},
        {'kit_number': '9', 'player_name': 'Dušan Vlahović', 'club': 'Juventus', 'position': 'CF', 'age': 24, 'market_value_eur': 70000000.0, 'nationality': 'Serbia', 'birth_date': 'Jan 28, 2000 (24)'},
        {'kit_number': '10', 'player_name': 'Paulo Dybala', 'club': 'Juventus', 'position': 'CAM', 'age': 31, 'market_value_eur': 15000000.0, 'nationality': 'Argentina', 'birth_date': 'Nov 15, 1993 (31)'},
        {'kit_number': '11', 'player_name': 'Nicolò Zaniolo', 'club': 'Juventus', 'position': 'RW', 'age': 25, 'market_value_eur': 22000000.0, 'nationality': 'Italy', 'birth_date': 'Jul 2, 1999 (25)'},
        {'kit_number': '14', 'player_name': 'Timothy Weah', 'club': 'Juventus', 'position': 'RW', 'age': 24, 'market_value_eur': 12000000.0, 'nationality': 'United States', 'birth_date': 'Feb 22, 2000 (24)'},
        {'kit_number': '22', 'player_name': 'Timothy Weah', 'club': 'Juventus', 'position': 'RW', 'age': 24, 'market_value_eur': 12000000.0, 'nationality': 'United States', 'birth_date': 'Feb 22, 2000 (24)'},
        {'kit_number': '24', 'player_name': 'Samuel Iling-Junior', 'club': 'Juventus', 'position': 'LW', 'age': 21, 'market_value_eur': 15000000.0, 'nationality': 'England', 'birth_date': 'Sep 21, 2003 (21)'},
    ]

def extract_age(date_text):
    """Extract age from date text"""
    try:
        age_match = re.search(r'\((\d+)\)', date_text)
        return int(age_match.group(1)) if age_match else 25
    except:
        return 25

def parse_market_value(value_text):
    """Parse market value from text like '€50.00m' to float"""
    try:
        if '€' in value_text:
            value_text = value_text.replace('€', '').strip()
        
        if 'm' in value_text.lower():
            return float(value_text.replace('m', '').strip()) * 1000000
        elif 'k' in value_text.lower():
            return float(value_text.replace('k', '').strip()) * 1000
        else:
            return float(value_text) if value_text.replace('.', '').isdigit() else 1000000.0
    except:
        return 1000000.0

def map_position(position_text):
    """Map position text to standard positions"""
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
        'Centre-Forward': 'CF',
        'Second Striker': 'CF'
    }
    
    for key, value in position_mapping.items():
        if key.lower() in position_text.lower():
            return value
    
    return position_text if position_text else 'Unknown'

def add_juventus_to_csv():
    """Add Juventus players to the existing CSV"""
    # Get Juventus squad data
    juventus_players = scrape_juventus_squad()
    
    if not juventus_players:
        print("No Juventus players found!")
        return
    
    # Load existing CSV
    try:
        df_existing = pd.read_csv('final_transfermarkt_squads.csv')
        print(f"Loaded existing CSV with {len(df_existing)} players")
    except FileNotFoundError:
        df_existing = pd.DataFrame()
        print("No existing CSV found, creating new one")
    
    # Remove any existing Juventus players first
    df_existing = df_existing[df_existing['club'] != 'Juventus']
    print(f"Removed any existing Juventus players, now have {len(df_existing)} players")
    
    # Create DataFrame for Juventus players
    df_juventus = pd.DataFrame(juventus_players)
    print(f"Created Juventus DataFrame with {len(df_juventus)} players")
    
    # Combine the dataframes
    df_combined = pd.concat([df_existing, df_juventus], ignore_index=True)
    
    # Save to CSV
    df_combined.to_csv('final_transfermarkt_squads.csv', index=False)
    
    print(f"Successfully added {len(juventus_players)} Juventus players to CSV")
    print(f"Total players in CSV: {len(df_combined)}")
    
    # Show Juventus players added
    print("\nJuventus players added:")
    for player in juventus_players:
        print(f"- {player['kit_number']:>2} {player['player_name']} ({player['position']}) - €{player['market_value_eur']/1000000:.1f}M")

if __name__ == "__main__":
    add_juventus_to_csv()
