import pandas as pd
import os

def update_market_values():
    """
    Update the market_value_eur column for the first 330 rows with values from the improved CSV
    """
    # Read both CSV files
    main_csv = 'real_transfermarkt_squads.csv'
    improved_csv = 'real_transfermarkt_squads_improved.csv'
    
    print("Reading CSV files...")
    df_main = pd.read_csv(main_csv)
    df_improved = pd.read_csv(improved_csv)
    
    print(f"Main CSV has {len(df_main)} rows")
    print(f"Improved CSV has {len(df_improved)} rows")
    
    # Create a mapping from player_name + club to market value from improved CSV
    # Convert market_value_mil_eur to market_value_eur (multiply by 1,000,000)
    value_mapping = {}
    for _, row in df_improved.iterrows():
        key = (row['player_name'], row['club'])
        # Convert from millions to actual value
        value_mapping[key] = row['market_value_mil_eur'] * 1_000_000
    
    print(f"Created mapping for {len(value_mapping)} players")
    
    # Update the first 330 rows
    updated_count = 0
    for i in range(min(330, len(df_main))):
        player_name = df_main.loc[i, 'player_name']
        club = df_main.loc[i, 'club']
        key = (player_name, club)
        
        if key in value_mapping:
            old_value = df_main.loc[i, 'market_value_eur']
            new_value = value_mapping[key]
            df_main.loc[i, 'market_value_eur'] = new_value
            updated_count += 1
            
            if updated_count <= 10:  # Show first 10 updates
                print(f"Updated {player_name} ({club}): {old_value:,.0f} → {new_value:,.0f}")
    
    print(f"\nUpdated {updated_count} players in the first 330 rows")
    
    # Save the updated file
    backup_file = 'real_transfermarkt_squads_backup.csv'
    print(f"Creating backup as {backup_file}")
    df_main.to_csv(backup_file, index=False)
    
    print(f"Saving updated data to {main_csv}")
    df_main.to_csv(main_csv, index=False)
    
    print("Market values update completed!")
    
    # Show some statistics
    print("\nMarket value statistics for first 330 rows:")
    first_330 = df_main.head(330)
    print(f"Min value: €{first_330['market_value_eur'].min():,.0f}")
    print(f"Max value: €{first_330['market_value_eur'].max():,.0f}")
    print(f"Mean value: €{first_330['market_value_eur'].mean():,.0f}")
    print(f"Values = 1M: {(first_330['market_value_eur'] == 1_000_000).sum()}")

if __name__ == "__main__":
    update_market_values()
