import pandas as pd

# Load the CSV file
df = pd.read_csv('final_transfermarkt_squads.csv')

# Create a mapping for Juventus players with Unknown positions
juventus_position_mapping = {
    'Manuel Locatelli': 'CDM',
    'Arthur Melo': 'CM',
    'Khéphren Thuram': 'CM',
    'Douglas Luiz': 'CM',
    'Weston McKennie': 'CM',
    'Fabio Miretti': 'CAM',
    'Filip Kostić': 'LW',
    'Teun Koopmeiners': 'CAM',
    'Vasilije Adžić': 'CAM',
    'Kenan Yıldız': 'LW',
    'Francisco Conceição': 'RW',
    'Nico González': 'RW',
}

# Function to update Juventus positions
def update_juventus_positions():
    updated_count = 0
    
    for index, row in df.iterrows():
        if row['club'] == 'Juventus' and row['position'] == 'Unknown':
            player_name = row['player_name']
            if player_name in juventus_position_mapping:
                df.at[index, 'position'] = juventus_position_mapping[player_name]
                updated_count += 1
                print(f"Updated {player_name}: Unknown -> {juventus_position_mapping[player_name]}")
    
    return updated_count

# Update the positions
print("Updating Juventus player positions...")
updates = update_juventus_positions()

# Save the updated CSV
df.to_csv('final_transfermarkt_squads.csv', index=False)

print(f"\nJuventus position update complete!")
print(f"Total positions updated: {updates}")

# Show Juventus squad with positions
juventus_players = df[df['club'] == 'Juventus']
print(f"\n🔵⚪ Updated Juventus Squad ({len(juventus_players)} players):")
print("Kit | Name                 | Pos | Age | Value")
print("-" * 50)

for _, player in juventus_players.iterrows():
    kit = str(player['kit_number']) if pd.notna(player['kit_number']) else '--'
    name = str(player['player_name'])[:18]
    pos = player['position']
    age = player['age']
    value = player['market_value_eur'] / 1000000
    print(f"{kit:>3} | {name:<18} | {pos:>3} | {age:>2} | €{value:>4.1f}M")

# Show position distribution
positions = juventus_players['position'].value_counts()
print(f"\nJuventus position distribution:")
for pos, count in positions.items():
    print(f"  {pos}: {count} players")

print(f"\nRemaining Unknown positions: {len(juventus_players[juventus_players['position'] == 'Unknown'])}")
