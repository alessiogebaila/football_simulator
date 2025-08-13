import pandas as pd

df = pd.read_csv('real_transfermarkt_squads.csv')
first_330 = df.head(330)

print(f"Total rows in CSV: {len(df)}")
print(f"Rows in first 330 with value = 1M: {(first_330['market_value_eur'] == 1_000_000).sum()}")
print(f"Min value in first 330: €{first_330['market_value_eur'].min():,.0f}")
print(f"Max value in first 330: €{first_330['market_value_eur'].max():,.0f}")
print(f"Mean value in first 330: €{first_330['market_value_eur'].mean():,.0f}")

# Check some high-value players
high_value = first_330[first_330['market_value_eur'] > 100_000_000]
print(f"\nPlayers with value > 100M in first 330 rows:")
for _, player in high_value.iterrows():
    print(f"  {player['player_name']} ({player['club']}): €{player['market_value_eur']:,.0f}")
