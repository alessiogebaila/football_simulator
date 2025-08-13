import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from datetime import datetime

def calculate_age(birth_date_str):
    """Calculate age from birth date string"""
    try:
        # Parse different date formats
        if '(' in birth_date_str:
            # Extract date part before parentheses
            date_part = birth_date_str.split('(')[0].strip()
        else:
            date_part = birth_date_str.strip()
        
        # Try different date formats
        formats = ['%b %d, %Y', '%d %b %Y', '%Y-%m-%d', '%d.%m.%Y']
        
        for fmt in formats:
            try:
                birth_date = datetime.strptime(date_part, fmt)
                today = datetime.now()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                return age
            except ValueError:
                continue
        
        # If no format works, try to extract just the year
        year_match = re.search(r'(\d{4})', date_part)
        if year_match:
            birth_year = int(year_match.group(1))
            current_year = datetime.now().year
            return current_year - birth_year
        
        return None
    except:
        return None

def parse_market_value(value_str):
    """Parse market value from Transfermarkt format"""
    if not value_str or value_str == '-':
        return 0.0
    
    # Remove currency symbols and clean
    clean_value = re.sub(r'[€$£]', '', value_str).strip()
    
    # Handle millions (m)
    if 'm' in clean_value.lower():
        num = re.findall(r'(\d+\.?\d*)', clean_value)
        if num:
            return float(num[0]) * 1_000_000
    
    # Handle thousands (k)
    elif 'k' in clean_value.lower():
        num = re.findall(r'(\d+\.?\d*)', clean_value)
        if num:
            return float(num[0]) * 1_000
    
    # Handle plain numbers
    else:
        num = re.findall(r'(\d+\.?\d*)', clean_value)
        if num:
            return float(num[0])
    
    return 0.0

def scrape_team_squad(team_url, team_name):
    """Scrape squad data from Transfermarkt team page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Scraping {team_name}...")
        response = requests.get(team_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        players = []
        
        # Find the squad table
        squad_table = soup.find('table', {'class': 'items'})
        if not squad_table:
            print(f"No squad table found for {team_name}")
            return players
        
        rows = squad_table.find('tbody').find_all('tr')
        
        for row in rows:
            try:
                # Skip header rows
                if 'thead' in str(row) or not row.find('td'):
                    continue
                
                cells = row.find_all('td')
                if len(cells) < 8:  # Need at least 8 columns for complete data
                    continue
                
                # Extract kit number (first cell)
                kit_number_cell = cells[0]
                kit_number = kit_number_cell.get_text(strip=True) if kit_number_cell else ""
                if not kit_number.isdigit():
                    kit_number = ""
                
                # Extract player name (usually in 2nd or 3rd cell)
                player_name = ""
                name_cell = None
                for cell in cells[1:4]:  # Check cells 1, 2, 3 for name
                    name_link = cell.find('a')
                    if name_link and '/profil/spieler/' in str(name_link.get('href', '')):
                        player_name = name_link.get_text(strip=True)
                        name_cell = cell
                        break
                
                if not player_name:
                    continue
                
                # Extract position
                position = ""
                # Look for position in the cell after name or in a separate position cell
                pos_cells = cells[2:5]  # Check multiple cells for position
                for cell in pos_cells:
                    pos_text = cell.get_text(strip=True)
                    # Common position abbreviations
                    if pos_text in ['GK', 'CB', 'LB', 'RB', 'DM', 'CM', 'AM', 'LW', 'RW', 'CF', 'ST']:
                        position = pos_text
                        break
                    elif any(pos in pos_text for pos in ['Goalkeeper', 'Defender', 'Midfielder', 'Forward', 'Winger']):
                        # Map full position names to abbreviations
                        if 'Goalkeeper' in pos_text:
                            position = 'GK'
                        elif 'Centre-Back' in pos_text or 'Central Defence' in pos_text:
                            position = 'CB'
                        elif 'Left-Back' in pos_text or 'Left Defence' in pos_text:
                            position = 'LB'
                        elif 'Right-Back' in pos_text or 'Right Defence' in pos_text:
                            position = 'RB'
                        elif 'Defensive Midfield' in pos_text:
                            position = 'DM'
                        elif 'Central Midfield' in pos_text:
                            position = 'CM'
                        elif 'Attacking Midfield' in pos_text:
                            position = 'AM'
                        elif 'Left Winger' in pos_text or 'Left Midfield' in pos_text:
                            position = 'LW'
                        elif 'Right Winger' in pos_text or 'Right Midfield' in pos_text:
                            position = 'RW'
                        elif 'Centre-Forward' in pos_text or 'Striker' in pos_text:
                            position = 'CF'
                        break
                
                # Extract birth date and age
                birth_date = ""
                age = None
                for cell in cells[3:7]:  # Look for birth date in these cells
                    cell_text = cell.get_text(strip=True)
                    # Look for date patterns
                    if re.search(r'\b\d{1,2}[\s,]+\d{4}\b|\b\d{4}\b', cell_text):
                        birth_date = cell_text
                        age = calculate_age(birth_date)
                        break
                
                # Extract nationality
                nationality = ""
                for cell in cells[3:8]:  # Look for nationality
                    # Look for country flag images or country names
                    flag_img = cell.find('img')
                    if flag_img and flag_img.get('title'):
                        nationality = flag_img.get('title')
                        break
                    elif flag_img and flag_img.get('alt'):
                        nationality = flag_img.get('alt')
                        break
                
                # Extract market value (usually in the last few cells)
                market_value = 0.0
                for cell in cells[-3:]:  # Check last 3 cells for market value
                    cell_text = cell.get_text(strip=True)
                    if '€' in cell_text or 'm' in cell_text.lower() or 'k' in cell_text.lower():
                        market_value = parse_market_value(cell_text)
                        break
                
                # Create player record
                player = {
                    'kit_number': kit_number,
                    'player_name': player_name,
                    'club': team_name,
                    'position': position or 'Unknown',
                    'age': age if age else 25,  # Default age if not found
                    'market_value_eur': market_value,
                    'nationality': nationality or 'Unknown',
                    'birth_date': birth_date
                }
                
                players.append(player)
                print(f"  Added: {player_name} ({position}) - Age {age} - {nationality} - €{market_value:,.0f}")
                
            except Exception as e:
                print(f"  Error processing row for {team_name}: {e}")
                continue
        
        print(f"Scraped {len(players)} players from {team_name}")
        return players
        
    except Exception as e:
        print(f"Error scraping {team_name}: {e}")
        return []

def main():
    """Main scraping function"""
    
    # Team URLs for the 16 teams
    teams = {
        'Barcelona': 'https://www.transfermarkt.com/fc-barcelona/startseite/verein/131',
        'Real Madrid': 'https://www.transfermarkt.com/real-madrid/startseite/verein/418',
        'Atletico Madrid': 'https://www.transfermarkt.com/atletico-madrid/startseite/verein/13',
        'Manchester City': 'https://www.transfermarkt.com/manchester-city/startseite/verein/281',
        'Liverpool': 'https://www.transfermarkt.com/fc-liverpool/startseite/verein/31',
        'Arsenal': 'https://www.transfermarkt.com/fc-arsenal/startseite/verein/11',
        'Chelsea': 'https://www.transfermarkt.com/fc-chelsea/startseite/verein/631',
        'Manchester United': 'https://www.transfermarkt.com/manchester-united/startseite/verein/985',
        'Tottenham': 'https://www.transfermarkt.com/tottenham-hotspur/startseite/verein/148',
        'PSG': 'https://www.transfermarkt.com/paris-saint-germain/startseite/verein/583',
        'Bayern Munich': 'https://www.transfermarkt.com/fc-bayern-munchen/startseite/verein/27',
        'Borussia Dortmund': 'https://www.transfermarkt.com/borussia-dortmund/startseite/verein/16',
        'Inter Milan': 'https://www.transfermarkt.com/inter-mailand/startseite/verein/46',
        'AC Milan': 'https://www.transfermarkt.com/ac-mailand/startseite/verein/5',
        'Juventus': 'https://www.transfermarkt.com/juventus-turin/startseite/verein/506',
        'Napoli': 'https://www.transfermarkt.com/ssc-neapel/startseite/verein/6195'
    }
    
    all_players = []
    
    for team_name, team_url in teams.items():
        players = scrape_team_squad(team_url, team_name)
        all_players.extend(players)
        
        # Add delay between requests to be respectful
        time.sleep(2)
    
    # Create DataFrame
    df = pd.DataFrame(all_players)
    
    # Reorder columns
    columns_order = ['kit_number', 'player_name', 'club', 'position', 'age', 'market_value_eur', 'nationality', 'birth_date']
    df = df[columns_order]
    
    # Save to CSV
    output_file = 'final_transfermarkt_squads.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n=== SCRAPING COMPLETE ===")
    print(f"Total players scraped: {len(df)}")
    print(f"Teams covered: {len(teams)}")
    print(f"Data saved to: {output_file}")
    
    # Show summary statistics
    print(f"\nSummary by team:")
    team_counts = df['club'].value_counts()
    for team, count in team_counts.items():
        print(f"  {team}: {count} players")
    
    print(f"\nPosition distribution:")
    pos_counts = df['position'].value_counts()
    for pos, count in pos_counts.items():
        print(f"  {pos}: {count} players")
    
    print(f"\nMarket value statistics:")
    print(f"  Total market value: €{df['market_value_eur'].sum():,.0f}")
    print(f"  Average market value: €{df['market_value_eur'].mean():,.0f}")
    print(f"  Highest value: €{df['market_value_eur'].max():,.0f}")
    print(f"  Lowest value: €{df['market_value_eur'].min():,.0f}")
    
    # Show some sample records
    print(f"\nSample records:")
    print(df.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
