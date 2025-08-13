import pandas as pd
import re

# Load the CSV file
df = pd.read_csv('final_transfermarkt_squads.csv')

# Create a mapping of known player positions based on real-world knowledge
# This includes defenders, midfielders, and attackers not already marked
position_mapping = {
    # Barcelona defenders
    'Pau Cubarsí': 'CB',
    'Ronald Araujo': 'CB', 
    'Eric García': 'CB',
    'Andreas Christensen': 'CB',
    'Alejandro Balde': 'LB',
    'Gerard Martín': 'LB',
    'Jules Koundé': 'RB',
    'Héctor Fort': 'RB',
    
    # Barcelona midfielders
    'Marc Casadó': 'CDM',
    'Marc Bernal': 'CM',
    'Oriol Romeu': 'CDM',
    'Pedri': 'CM',
    'Gavi': 'CM',
    'Frenkie de Jong': 'CM',
    'Dani Olmo': 'CAM',
    'Fermín López': 'CM',
    
    # Real Madrid defenders
    'Dean Huijsen': 'CB',
    'Raúl Asencio': 'CB',
    'Éder Militão': 'CB',
    'Antonio Rüdiger': 'CB',
    'David Alaba': 'CB',
    'Álvaro Carreras': 'LB',
    'Fran García': 'LB',
    'Ferland Mendy': 'LB',
    'Trent Alexander-Arnold': 'RB',
    'Daniel Carvajal': 'RB',
    
    # Real Madrid midfielders
    'Aurélien Tchouaméni': 'CDM',
    'Federico Valverde': 'CM',
    'Eduardo Camavinga': 'CM',
    'Dani Ceballos': 'CM',
    'Jude Bellingham': 'CAM',
    'Arda Güler': 'CAM',
    
    # Atletico Madrid defenders
    'Robin Le Normand': 'CB',
    'Dávid Hancko': 'CB',
    'José María Giménez': 'CB',
    'Clément Lenglet': 'CB',
    'Matteo Ruggeri': 'LB',
    'Javi Galán': 'LB',
    'Nahuel Molina': 'RB',
    'Marc Pubill': 'RB',
    
    # Atletico Madrid midfielders
    'Pablo Barrios': 'CM',
    'Conor Gallagher': 'CM',
    'Johnny Cardoso': 'CDM',
    'Koke': 'CM',
    'Marcos Llorente': 'CM',
    'Thiago Almada': 'CAM',
    'Antoine Griezmann': 'CAM',
    
    # Manchester City defenders
    'Rúben Dias': 'CB',
    'Abdukodir Khusanov': 'CB',
    'Manuel Akanji': 'CB',
    'John Stones': 'CB',
    'Nathan Aké': 'CB',
    'Callum Doyle': 'LB',
    'Josko Gvardiol': 'LB',
    'Rayan Aït-Nouri': 'LB',
    'Nico O\'Reilly': 'CM',
    'Josh Wilson-Esbrand': 'LB',
    'Rico Lewis': 'RB',
    'Issa Kaboré': 'RB',
    
    # Manchester City midfielders
    'Rodri': 'CDM',
    'Kalvin Phillips': 'CDM',
    'Tijjani Reijnders': 'CM',
    'Nico González': 'CM',
    'Matheus Nunes': 'CM',
    'Mateo Kovacic': 'CM',
    'Sverre Nypan': 'CM',
    'İlkay Gündoğan': 'CM',
    'Bernardo Silva': 'CAM',
    'James McAtee': 'CAM',
    'Claudio Echeverri': 'CAM',
    
    # Liverpool defenders
    'Ibrahima Konaté': 'CB',
    'Virgil van Dijk': 'CB',
    'Joe Gomez': 'CB',
    'Rhys Williams': 'CB',
    'Milos Kerkez': 'LB',
    'Konstantinos Tsimikas': 'LB',
    'Andrew Robertson': 'LB',
    'Jeremie Frimpong': 'RB',
    'Conor Bradley': 'RB',
    'Calvin Ramsay': 'RB',
    
    # Liverpool midfielders
    'Ryan Gravenberch': 'CM',
    'Stefan Bajcetic': 'CDM',
    'Wataru Endo': 'CDM',
    'Alexis Mac Allister': 'CM',
    'Curtis Jones': 'CM',
    'Trey Nyoni': 'CM',
    'Florian Wirtz': 'CAM',
    'Dominik Szoboszlai': 'CAM',
    'Harvey Elliott': 'CAM',
    
    # Arsenal defenders
    'William Saliba': 'CB',
    'Gabriel Magalhães': 'CB',
    'Cristhian Mosquera': 'CB',
    'Jakub Kiwior': 'CB',
    'Myles Lewis-Skelly': 'LB',
    'Riccardo Calafiori': 'LB',
    'Oleksandr Zinchenko': 'LB',
    'Jurrien Timber': 'RB',
    'Ben White': 'RB',
    
    # Arsenal midfielders
    'Martín Zubimendi': 'CDM',
    'Christian Nørgaard': 'CDM',
    'Declan Rice': 'CDM',
    'Mikel Merino': 'CM',
    'Albert Sambi Lokonga': 'CM',
    'Martin Ødegaard': 'CAM',
    'Fábio Vieira': 'CAM',
    
    # Chelsea defenders
    'Levi Colwill': 'CB',
    'Renato Veiga': 'CB',
    'Trevoh Chalobah': 'CB',
    'Wesley Fofana': 'CB',
    'Axel Disasi': 'CB',
    'Benoît Badiashile': 'CB',
    'Tosin Adarabioyo': 'CB',
    'Aarón Anselmino': 'CB',
    'Marc Cucurella': 'LB',
    'Jorrel Hato': 'LB',
    'Ben Chilwell': 'LB',
    'Malo Gusto': 'RB',
    'Reece James': 'RB',
    'Alfie Gilchrist': 'RB',
    'Josh Acheampong': 'RB',
    
    # Chelsea midfielders
    'Moisés Caicedo': 'CDM',
    'Roméo Lavia': 'CDM',
    'Dário Essugo': 'CM',
    'Enzo Fernández': 'CM',
    'Andrey Santos': 'CM',
    'Carney Chukwuemeka': 'CM',
    'Cole Palmer': 'CAM',
    
    # Manchester United defenders
    'Leny Yoro': 'CB',
    'Lisandro Martínez': 'CB',
    'Matthijs de Ligt': 'CB',
    'Harry Maguire': 'CB',
    'Ayden Heaven': 'CB',
    'Tyler Fredricson': 'CB',
    'Patrick Dorgu': 'LB',
    'Luke Shaw': 'LB',
    'Tyrell Malacia': 'LB',
    'Harry Amass': 'LB',
    'Diego León': 'LB',
    'Diogo Dalot': 'RB',
    'Noussair Mazraoui': 'RB',
    
    # Manchester United midfielders
    'Manuel Ugarte': 'CDM',
    'Casemiro': 'CDM',
    'Toby Collyer': 'CM',
    'Kobbie Mainoo': 'CM',
    'Bruno Fernandes': 'CAM',
    'Mason Mount': 'CAM',
    'Matheus Cunha': 'CAM',
    
    # Tottenham defenders
    'Cristian Romero': 'CB',
    'Micky van de Ven': 'CB',
    'Radu Drăgușin': 'CB',
    'Kevin Danso': 'CB',
    'Luka Vuskovic': 'CB',
    'Ben Davies': 'LB',
    'Kota Takai': 'LB',
    'Destiny Udogie': 'LB',
    'Djed Spence': 'RB',
    'Pedro Porro': 'RB',
    'Archie Gray': 'RB',
    
    # Tottenham midfielders
    'João Palhinha': 'CDM',
    'Rodrigo Bentancur': 'CDM',
    'Yves Bissouma': 'CDM',
    'Lucas Bergvall': 'CM',
    'Pape Matar Sarr': 'CM',
    'Dejan Kulusevski': 'CAM',
    'James Maddison': 'CAM',
    
    # PSG defenders
    'Willian Pacho': 'CB',
    'Marquinhos': 'CB',
    'Lucas Beraldo': 'CB',
    'Presnel Kimpembe': 'CB',
    'Nuno Mendes': 'LB',
    'Lucas Hernández': 'LB',
    'Achraf Hakimi': 'RB',
    'Nordi Mukiele': 'RB',
    
    # PSG midfielders
    'Vitinha': 'CM',
    'João Neves': 'CM',
    'Warren Zaïre-Emery': 'CM',
    'Fabián Ruiz': 'CM',
    'Carlos Soler': 'CM',
    'Senny Mayulu': 'CM',
    'Renato Sanches': 'CM',
    'Marco Asensio': 'CAM',
    
    # Bayern Munich defenders
    'Dayot Upamecano': 'CB',
    'Min-jae Kim': 'CB',
    'Jonathan Tah': 'CB',
    'Hiroki Ito': 'CB',
    'Alphonso Davies': 'LB',
    'Raphaël Guerreiro': 'LB',
    'Josip Stanisic': 'RB',
    'Konrad Laimer': 'RB',
    'Sacha Boey': 'RB',
    
    # Bayern Munich midfielders
    'Aleksandar Pavlovic': 'CDM',
    'Joshua Kimmich': 'CDM',
    'Tom Bischof': 'CM',
    'Leon Goretzka': 'CM',
    'Jamal Musiala': 'CAM',
    'Paul Wanner': 'CAM',
    'Lennart Karl': 'CM',
    
    # Borussia Dortmund defenders
    'Nico Schlotterbeck': 'CB',
    'Waldemar Anton': 'CB',
    'Niklas Süle': 'CB',
    'Filippo Mané': 'CB',
    'Daniel Svensson': 'LB',
    'Ramy Bensebaini': 'LB',
    'Almugera Kabar': 'LB',
    'Yan Couto': 'RB',
    'Julian Ryerson': 'RB',
    
    # Borussia Dortmund midfielders
    'Emre Can': 'CDM',
    'Salih Özcan': 'CDM',
    'Felix Nmecha': 'CM',
    'Jobe Bellingham': 'CM',
    'Marcel Sabitzer': 'CM',
    'Pascal Groß': 'CM',
    'Julian Brandt': 'CAM',
    'Giovanni Reyna': 'CAM',
    
    # Inter Milan defenders
    'Alessandro Bastoni': 'CB',
    'Yann Bisseck': 'CB',
    'Benjamin Pavard': 'CB',
    'Stefan de Vrij': 'CB',
    'Tomás Palacios': 'CB',
    'Francesco Acerbi': 'CB',
    'Federico Dimarco': 'LB',
    'Carlos Augusto': 'LB',
    'Denzel Dumfries': 'RB',
    'Matteo Darmian': 'RB',
    
    # Inter Milan midfielders
    'Hakan Çalhanoğlu': 'CDM',
    'Petar Sučić': 'CM',
    'Kristjan Asllani': 'CM',
    'Nicolò Barella': 'CM',
    'Davide Frattesi': 'CM',
    'Piotr Zieliński': 'CM',
    'Henrikh Mkhitaryan': 'CAM',
    'Luis Henrique': 'CAM',
    'Nicola Zalewski': 'CAM',
    'Sebastiano Esposito': 'CAM',
    
    # AC Milan defenders
    'Fikayo Tomori': 'CB',
    'Malick Thiaw': 'CB',
    'Strahinja Pavlović': 'CB',
    'Matteo Gabbia': 'CB',
    'Pervis Estupiñán': 'LB',
    'Davide Bartesaghi': 'LB',
    'Álex Jiménez': 'RB',
    'Filippo Terracciano': 'RB',
    
    # AC Milan midfielders
    'Ardon Jashari': 'CDM',
    'Samuele Ricci': 'CDM',
    'Youssouf Fofana': 'CDM',
    'Ismaël Bennacer': 'CM',
    'Yacine Adli': 'CM',
    'Yunus Musah': 'CM',
    'Ruben Loftus-Cheek': 'CM',
    'Warren Bondo': 'CM',
    'Luka Modrić': 'CAM',
    
    # Napoli defenders
    'Alessandro Buongiorno': 'CB',
    'Sam Beukema': 'CB',
    'Amir Rrahmani': 'CB',
    'Luca Marianucci': 'CB',
    'Juan Jesus': 'CB',
    'Nosa Edward Obaretin': 'CB',
    'Mathías Olivera': 'LB',
    'Leonardo Spinazzola': 'LB',
    'Giovanni Di Lorenzo': 'RB',
    'Alessandro Zanoli': 'RB',
    'Pasquale Mazzocchi': 'RB',
    
    # Napoli midfielders
    'Stanislav Lobotka': 'CDM',
    'Billy Gilmour': 'CDM',
    'Scott McTominay': 'CM',
    'Frank Anguissa': 'CM',
    'Luis Hasa': 'CM',
    'Coli Saco': 'CM',
    'Kevin De Bruyne': 'CAM',
    'Antonio Vergara': 'CAM',
    'Giacomo Raspadori': 'CAM',
}

# Function to update positions
def update_positions():
    updated_count = 0
    
    for index, row in df.iterrows():
        if row['position'] == 'Unknown':
            player_name = row['player_name']
            if player_name in position_mapping:
                df.at[index, 'position'] = position_mapping[player_name]
                updated_count += 1
                print(f"Updated {player_name}: Unknown -> {position_mapping[player_name]}")
    
    return updated_count

# Update the positions
print("Updating player positions...")
updates = update_positions()

# Save the updated CSV
df.to_csv('final_transfermarkt_squads.csv', index=False)

print(f"\nPosition update complete!")
print(f"Total positions updated: {updates}")

# Show remaining Unknown positions
remaining_unknown = df[df['position'] == 'Unknown']
print(f"Remaining Unknown positions: {len(remaining_unknown)}")

if len(remaining_unknown) > 0:
    print("\nPlayers still with Unknown positions:")
    for _, row in remaining_unknown.iterrows():
        print(f"- {row['player_name']} ({row['club']})")
