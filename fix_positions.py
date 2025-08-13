import pandas as pd
import re

def infer_positions():
    """
    Infer player positions based on player names and common football position patterns
    """
    
    # Read the main CSV
    df = pd.read_csv('real_transfermarkt_squads.csv')
    
    # Common position mappings based on player names and roles
    position_keywords = {
        'GK': ['Keeper', 'Goalkeeper', 'García', 'ter Stegen', 'Peña', 'Szczesny', 'Courtois', 'Lunin', 'González', 
               'Oblak', 'Musso', 'Trafford', 'Ederson', 'Ortega', 'Bettinelli', 'Mamardashvili', 'Alisson', 
               'Woodman', 'Pécsi', 'Raya', 'Arrizabalaga', 'Hein', 'Sánchez', 'Jørgensen', 'Slonina', 
               'Onana', 'Bayındır', 'Heaton', 'Vicario', 'Kinský', 'Austin', 'Donnarumma', 'Chevalier', 
               'Safonov', 'Tenas', 'Marin', 'Urbig', 'Neuer', 'Ulreich', 'Klanac', 'Kobel', 'Meyer', 
               'Drewes', 'Ostrzinski', 'Martínez', 'Sommer', 'Di Gennaro', 'Maignan', 'Terracciano', 
               'Torriani', 'Di Gregorio', 'Perin', 'Pinsoglio', 'Meret', 'Milinković-Savić', 'Contini', 
               'Ferrante'],
        
        'CB': ['Cubarsí', 'Araujo', 'García', 'Christensen', 'Huijsen', 'Asencio', 'Militão', 'Rüdiger', 
               'Alaba', 'Le Normand', 'Hancko', 'Giménez', 'Lenglet', 'Dias', 'Khusanov', 'Akanji', 
               'Stones', 'Aké', 'Doyle', 'Konaté', 'van Dijk', 'Gomez', 'Williams', 'Saliba', 'Magalhães', 
               'Mosquera', 'Kiwior', 'Colwill', 'Veiga', 'Chalobah', 'Fofana', 'Disasi', 'Badiashile', 
               'Adarabioyo', 'Anselmino', 'Yoro', 'Martínez', 'de Ligt', 'Maguire', 'Heaven', 'Fredricson', 
               'Romero', 'van de Ven', 'Drăgușin', 'Danso', 'Vuskovic', 'Davies', 'Takai', 'Pacho', 
               'Marquinhos', 'Beraldo', 'Kimpembe', 'Upamecano', 'Kim', 'Tah', 'Ito', 'Kiala', 
               'Schlotterbeck', 'Anton', 'Süle', 'Mané', 'Bastoni', 'Bisseck', 'Pavard', 'de Vrij', 
               'Palacios', 'Acerbi', 'Tomori', 'Thiaw', 'Pavlović', 'Gabbia', 'Bremer', 'Kalulu', 
               'Gatti', 'Kelly', 'Djaló', 'González', 'Rugani', 'Buongiorno', 'Beukema', 'Rrahmani', 
               'Marianucci', 'Jesus'],
        
        'LB': ['Balde', 'Martín', 'Carreras', 'García', 'Mendy', 'Ruggeri', 'Galán', 'Gvardiol', 
               'Aït-Nouri', 'O\'Reilly', 'Wilson-Esbrand', 'Kerkez', 'Tsimikas', 'Robertson', 
               'Lewis-Skelly', 'Calafiori', 'Zinchenko', 'Cucurella', 'Hato', 'Chilwell', 'Dorgu', 
               'Shaw', 'Malacia', 'Amass', 'León', 'Udogie', 'Spence', 'Mendes', 'Hernández', 
               'Davies', 'Guerreiro', 'Svensson', 'Bensebaini', 'Olivera', 'Spinazzola', 'Estupiñán', 
               'Bartesaghi'],
        
        'RB': ['Koundé', 'Fort', 'Alexander-Arnold', 'Carvajal', 'Molina', 'Pubill', 'Lewis', 'Kaboré', 
               'Frimpong', 'Bradley', 'Ramsay', 'Timber', 'White', 'Gusto', 'James', 'Gilchrist', 
               'Acheampong', 'Dalot', 'Mazraoui', 'Porro', 'Hakimi', 'Mukiele', 'Stanisic', 'Laimer', 
               'Boey', 'Couto', 'Ryerson', 'Dumfries', 'Darmian', 'Jiménez', 'Terracciano', 'Cambiaso', 
               'Cabal', 'Rouhi', 'Savona', 'Mário', 'Di Lorenzo', 'Zanoli', 'Mazzocchi'],
        
        'DM': ['Casadó', 'Bernal', 'Romeu', 'Tchouaméni', 'Rodri', 'Phillips', 'Gravenberch', 'Bajcetic', 
               'Endo', 'Zubimendi', 'Nørgaard', 'Caicedo', 'Lavia', 'Essugo', 'Ugarte', 'Casemiro', 
               'Collyer', 'Gray', 'Palhinha', 'Bentancur', 'Bissouma', 'Pavlovic', 'Kimmich', 'Can', 
               'Özcan', 'Çalhanoğlu', 'Asllani'],
        
        'CM': ['Pedri', 'Gavi', 'de Jong', 'Valverde', 'Camavinga', 'Ceballos', 'Barrios', 'Gallagher', 
               'Cardoso', 'Koke', 'Reijnders', 'González', 'Nunes', 'Kovacic', 'Nypan', 'Gündoğan', 
               'Mac Allister', 'Jones', 'Nyoni', 'Rice', 'Merino', 'Lokonga', 'Fernández', 'Santos', 
               'Chukwuemeka', 'Mainoo', 'Bergvall', 'Sarr', 'Vitinha', 'Neves', 'Zaïre-Emery', 'Ruiz', 
               'Soler', 'Mayulu', 'Sanches', 'Bischof', 'Goretzka', 'Nmecha', 'Bellingham', 'Sabitzer', 
               'Groß', 'Barella', 'Frattesi', 'Zieliński', 'Mkhitaryan', 'Sučić', 'Jashari', 'Ricci', 
               'Fofana', 'Bennacer', 'Adli', 'Musah', 'Loftus-Cheek', 'Bondo', 'Modrić', 'Locatelli', 
               'Melo', 'Thuram', 'Luiz', 'McKennie', 'Miretti', 'Lobotka', 'Gilmour', 'McTominay', 
               'Anguissa', 'Hasa', 'Saco'],
        
        'AM': ['Olmo', 'López', 'Bellingham', 'Güler', 'Llorente', 'Almada', 'Silva', 'McAtee', 
               'Echeverri', 'Wirtz', 'Szoboszlai', 'Elliott', 'Ødegaard', 'Vieira', 'Palmer', 
               'Fernandes', 'Mount', 'Kulusevski', 'Maddison', 'Asensio', 'Musiala', 'Wanner', 
               'Karl', 'Koopmeiners', 'Adžić', 'De Bruyne', 'Vergara'],
        
        'LW': ['Raphinha', 'Rashford', 'Vinicius', 'Baena', 'Doku', 'Grealish', 'Gakpo', 'Martinelli', 
               'Trossard', 'Gittens', 'George', 'Mudryk', 'Garnacho', 'Sancho', 'Gil', 'Solomon', 
               'Kvaratskhelia', 'Barcola', 'Díaz', 'Coman', 'Gnabry', 'Mike', 'Leão', 'Okafor', 
               'Lang', 'Henrique', 'Zalewski'],
        
        'RW': ['Yamal', 'Rodrygo', 'Díaz', 'Simeone', 'Martín', 'Foden', 'Savinho', 'Cherki', 'Bobb', 
               'Salah', 'Chiesa', 'Doak', 'Saka', 'Nwaneri', 'Madueke', 'Nelson', 'Estêvão', 'Neto', 
               'Sterling', 'Mbeumo', 'Diallo', 'Antony', 'Kudus', 'Johnson', 'Odobert', 'Dembélé', 
               'Doué', 'Lee', 'Mbaye', 'Olise', 'Pulisic', 'Saelemaekers', 'Chukwueze', 'Conceição', 
               'González', 'Neres', 'Politano'],
        
        'CF': ['Torres', 'Lewandowski', 'Mbappé', 'Endrick', 'García', 'Griezmann', 'Alvarez', 'Sørloth', 
               'Haaland', 'Marmoush', 'Ekitiké', 'Gyökeres', 'Havertz', 'Jesus', 'Jackson', 'Pedro', 
               'Delap', 'Nkunku', 'Fofana', 'Cunha', 'Sesko', 'Højlund', 'Zirkzee', 'Obi', 'Solanke', 
               'Tel', 'Richarlison', 'Scarlett', 'Ramos', 'Muani', 'Kane', 'Kusi-Asare', 'Guirassy', 
               'Beier', 'Haller', 'Martínez', 'Thuram', 'Esposito', 'Bonny', 'Taremi', 'Gimenez', 
               'David', 'Vlahović', 'Milik', 'Raspadori', 'Lukaku', 'Lucca', 'Ambrosino', 'Cheddira']
    }
    
    # Function to infer position based on player name
    def get_position(player_name):
        # Check each position category
        for position, keywords in position_keywords.items():
            for keyword in keywords:
                if keyword.lower() in player_name.lower():
                    return position
        
        # If no match found, keep as Unknown
        return 'Unknown'
    
    # Count original Unknown positions
    original_unknown = (df['position'] == 'Unknown').sum()
    print(f"Original Unknown positions: {original_unknown}")
    
    # Update positions for Unknown entries only
    unknown_mask = df['position'] == 'Unknown'
    df.loc[unknown_mask, 'position'] = df.loc[unknown_mask, 'player_name'].apply(get_position)
    
    # Count remaining Unknown positions
    remaining_unknown = (df['position'] == 'Unknown').sum()
    updated_count = original_unknown - remaining_unknown
    
    print(f"Updated {updated_count} positions")
    print(f"Remaining Unknown positions: {remaining_unknown}")
    
    # Show position distribution
    print("\nPosition distribution:")
    position_counts = df['position'].value_counts()
    for pos, count in position_counts.items():
        print(f"  {pos}: {count}")
    
    # Save updated CSV
    backup_file = 'real_transfermarkt_squads_positions_backup.csv'
    print(f"\nCreating backup as {backup_file}")
    pd.read_csv('real_transfermarkt_squads.csv').to_csv(backup_file, index=False)
    
    print(f"Saving updated data to real_transfermarkt_squads.csv")
    df.to_csv('real_transfermarkt_squads.csv', index=False)
    
    print("Position update completed!")
    
    # Show some examples of updated positions
    print("\nExamples of updated positions:")
    updated_players = df[unknown_mask & (df['position'] != 'Unknown')].head(10)
    for _, player in updated_players.iterrows():
        print(f"  {player['player_name']} ({player['club']}): {player['position']}")

if __name__ == "__main__":
    infer_positions()
