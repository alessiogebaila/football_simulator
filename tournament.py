from enhanced_football_simulator import *
import json
from typing import List, Dict

class Tournament:
    def __init__(self, name: str, teams: List[Team], tournament_type: str = "knockout"):
        self.name = name
        self.teams = teams
        self.tournament_type = tournament_type
        self.predictor = MatchPredictor()
        self.matches_played = []
        self.current_round = 1
        self.tournament_stats = {
            'total_goals': 0,
            'total_cards': 0,
            'top_scorers': {},
            'top_assisters': {}
        }
        
    def start_tournament(self):
        print(f"\n🏆 WELCOME TO {self.name.upper()}")
        print("=" * 60)
        print(f"🌟 {len(self.teams)} teams competing for glory!")
        
        # Display teams and their squad values
        print(f"\n📋 PARTICIPATING TEAMS:")
        teams_with_values = [(team, team.get_squad_value()) for team in self.teams]
        teams_with_values.sort(key=lambda x: x[1], reverse=True)
        
        for i, (team, value) in enumerate(teams_with_values, 1):
            print(f"{i:2d}. {team.team_name:<25} - €{value:.1f}M")
        
        if self.tournament_type == "knockout":
            self.run_knockout_tournament()
        else:
            print("Only knockout tournaments are currently supported.")
    
    def run_knockout_tournament(self):
        remaining_teams = self.teams.copy()
        
        while len(remaining_teams) > 1:
            print(f"\n🔥 ROUND {self.current_round}")
            print("=" * 40)
            
            if len(remaining_teams) == 2:
                print("🏆 FINAL MATCH!")
            elif len(remaining_teams) == 4:
                print("🥉 SEMI-FINALS!")
            elif len(remaining_teams) == 8:
                print("🥈 QUARTER-FINALS!")
            
            next_round_teams = []
            
            # Pair teams for matches
            for i in range(0, len(remaining_teams), 2):
                if i + 1 < len(remaining_teams):
                    home_team = remaining_teams[i]
                    away_team = remaining_teams[i + 1]
                    
                    print(f"\n⚔️  {home_team.team_name} vs {away_team.team_name}")
                    
                    # Create and play match
                    match = Match(home_team, away_team, self.predictor)
                    match.start()
                    winner = match.winner()
                    
                    if winner:
                        next_round_teams.append(winner)
                        self.matches_played.append(match)
                        self.update_tournament_stats(match)
                    
                    print("\n" + "="*60)
                    
                    # Pause between matches
                    input("Press Enter to continue to next match...")
                else:
                    # Odd number of teams, this team gets a bye
                    next_round_teams.append(remaining_teams[i])
                    print(f"🎫 {remaining_teams[i].team_name} receives a bye to the next round!")
            
            remaining_teams = next_round_teams
            self.current_round += 1
        
        # Tournament winner
        if remaining_teams:
            champion = remaining_teams[0]
            self.display_tournament_summary(champion)
    
    def update_tournament_stats(self, match: Match):
        """Update tournament statistics"""
        self.tournament_stats['total_goals'] += match.score._home_goals + match.score._away_goals
        self.tournament_stats['total_cards'] += (
            match.match_stats.yellow_cards_home + match.match_stats.yellow_cards_away +
            match.match_stats.red_cards_home + match.match_stats.red_cards_away
        )
        
        # Update goal scorers
        for minute, scorer, team in match.score.goal_scorers:
            player_name = scorer.stats.name
            if player_name not in self.tournament_stats['top_scorers']:
                self.tournament_stats['top_scorers'][player_name] = 0
            self.tournament_stats['top_scorers'][player_name] += 1
        
        # Update assist providers
        for minute, assister, team in match.score.assist_providers:
            player_name = assister.stats.name
            if player_name not in self.tournament_stats['top_assisters']:
                self.tournament_stats['top_assisters'][player_name] = 0
            self.tournament_stats['top_assisters'][player_name] += 1
    
    def display_tournament_summary(self, champion: Team):
        """Display final tournament summary"""
        print(f"\n🎊 TOURNAMENT COMPLETED! 🎊")
        print("=" * 60)
        print(f"🏆 CHAMPION: {champion.team_name.upper()}")
        print(f"🌟 Squad Value: €{champion.get_squad_value():.1f}M")
        print(f"💪 Team Strength: {champion.get_team_strength():.1f}")
        
        print(f"\n📊 TOURNAMENT STATISTICS:")
        print(f"🥅 Total Goals Scored: {self.tournament_stats['total_goals']}")
        print(f"🟨 Total Cards: {self.tournament_stats['total_cards']}")
        print(f"⚽ Matches Played: {len(self.matches_played)}")
        
        # Top scorers
        if self.tournament_stats['top_scorers']:
            print(f"\n⚽ TOP SCORERS:")
            top_scorers = sorted(self.tournament_stats['top_scorers'].items(), 
                               key=lambda x: x[1], reverse=True)[:5]
            for i, (player, goals) in enumerate(top_scorers, 1):
                print(f"{i}. {player}: {goals} goals")
        
        # Top assisters
        if self.tournament_stats['top_assisters']:
            print(f"\n👏 TOP ASSISTERS:")
            top_assisters = sorted(self.tournament_stats['top_assisters'].items(), 
                                 key=lambda x: x[1], reverse=True)[:5]
            for i, (player, assists) in enumerate(top_assisters, 1):
                print(f"{i}. {player}: {assists} assists")
        
        print(f"\n🎉 CONGRATULATIONS TO {champion.team_name}!")
        print("🏆 CHAMPIONS! CHAMPIONS! OLE, OLE, OLEEEEEEE!")


def create_world_class_teams():
    """Create multiple world-class teams for the tournament"""
    
    teams = []
    
    # Manchester City (already created in main file)
    mci = Team("Manchester City", "England")
    mci_players = [
        PlayerStats("Erling Haaland", "FWD", 91, 89, 92, 65, 80, 45, 88, 180.0, 24, 9),
        PlayerStats("Kevin De Bruyne", "MID", 89, 68, 86, 93, 87, 64, 78, 100.0, 32, 8),
        PlayerStats("Rodri", "MID", 87, 62, 75, 90, 81, 84, 82, 90.0, 27, 8),
        PlayerStats("Ruben Dias", "DEF", 86, 61, 48, 71, 70, 91, 85, 75.0, 26, 8),
        PlayerStats("Ederson", "GK", 85, 87, 75, 85, 82, 62, 86, 40.0, 30, 7),
        PlayerStats("Jack Grealish", "MID", 84, 82, 74, 86, 90, 52, 71, 70.0, 28, 7),
        PlayerStats("John Stones", "DEF", 83, 70, 58, 83, 75, 88, 81, 55.0, 29, 7),
        PlayerStats("Bernardo Silva", "MID", 86, 75, 82, 89, 91, 61, 73, 80.0, 29, 8),
        PlayerStats("Nathan Ake", "DEF", 82, 78, 55, 76, 73, 86, 79, 45.0, 28, 7),
        PlayerStats("Kyle Walker", "DEF", 81, 91, 52, 68, 71, 82, 77, 35.0, 33, 6),
        PlayerStats("Julian Alvarez", "FWD", 83, 83, 85, 81, 86, 55, 76, 75.0, 24, 8)
    ]
    for player_stats in mci_players:
        mci.add_player(Player(player_stats))
    teams.append(mci)
    
    # Real Madrid
    real_madrid = Team("Real Madrid", "Spain")
    real_players = [
        PlayerStats("Kylian Mbappe", "FWD", 93, 97, 89, 80, 92, 36, 77, 200.0, 25, 9),
        PlayerStats("Vinicius Jr", "FWD", 89, 95, 83, 85, 90, 29, 73, 150.0, 23, 9),
        PlayerStats("Jude Bellingham", "MID", 87, 78, 82, 86, 84, 78, 84, 130.0, 20, 9),
        PlayerStats("Luka Modric", "MID", 85, 72, 81, 95, 90, 72, 65, 15.0, 38, 8),
        PlayerStats("Thibaut Courtois", "GK", 87, 48, 75, 84, 88, 67, 90, 35.0, 31, 8),
        PlayerStats("Antonio Rudiger", "DEF", 84, 82, 55, 76, 74, 89, 86, 45.0, 30, 7),
        PlayerStats("Federico Valverde", "MID", 85, 87, 84, 88, 82, 78, 89, 100.0, 25, 8),
        PlayerStats("Eder Militao", "DEF", 83, 85, 51, 73, 71, 87, 83, 60.0, 25, 7),
        PlayerStats("Dani Carvajal", "DEF", 81, 84, 62, 81, 75, 84, 78, 20.0, 32, 7),
        PlayerStats("Aurelien Tchouameni", "MID", 82, 76, 73, 83, 78, 85, 87, 80.0, 24, 7),
        PlayerStats("Rodrygo", "FWD", 84, 91, 85, 86, 89, 35, 70, 90.0, 23, 8)
    ]
    for player_stats in real_players:
        real_madrid.add_player(Player(player_stats))
    teams.append(real_madrid)
    
    # FC Barcelona
    barcelona = Team("FC Barcelona", "Spain")
    barca_players = [
        PlayerStats("Robert Lewandowski", "FWD", 89, 78, 91, 79, 85, 44, 82, 50.0, 35, 8),
        PlayerStats("Pedri", "MID", 85, 74, 76, 89, 90, 59, 68, 80.0, 21, 9),
        PlayerStats("Gavi", "MID", 82, 81, 73, 86, 88, 64, 72, 90.0, 19, 8),
        PlayerStats("Ronald Araujo", "DEF", 83, 82, 51, 73, 71, 89, 86, 70.0, 24, 7),
        PlayerStats("Marc-Andre ter Stegen", "GK", 84, 68, 79, 88, 84, 58, 83, 30.0, 31, 7),
        PlayerStats("Frenkie de Jong", "MID", 84, 76, 77, 87, 89, 72, 79, 85.0, 26, 7),
        PlayerStats("Jules Kounde", "DEF", 82, 85, 56, 75, 74, 87, 78, 60.0, 24, 7),
        PlayerStats("Raphinha", "FWD", 81, 86, 80, 83, 88, 38, 74, 65.0, 26, 7),
        PlayerStats("Lamine Yamal", "FWD", 79, 88, 78, 82, 91, 32, 65, 120.0, 17, 9),
        PlayerStats("Alejandro Balde", "DEF", 78, 89, 61, 78, 76, 79, 74, 40.0, 20, 8),
        PlayerStats("Ferran Torres", "FWD", 80, 83, 82, 81, 85, 45, 71, 55.0, 24, 6)
    ]
    for player_stats in barca_players:
        barcelona.add_player(Player(player_stats))
    teams.append(barcelona)
    
    # PSG
    psg = Team("Paris Saint-Germain", "France")
    psg_players = [
        PlayerStats("Ousmane Dembele", "FWD", 86, 94, 84, 82, 91, 38, 71, 60.0, 27, 8),
        PlayerStats("Marco Verratti", "MID", 85, 68, 79, 92, 89, 77, 63, 55.0, 31, 8),
        PlayerStats("Marquinhos", "DEF", 86, 76, 67, 84, 78, 90, 82, 70.0, 30, 8),
        PlayerStats("Gianluigi Donnarumma", "GK", 85, 61, 72, 83, 89, 64, 90, 35.0, 25, 8),
        PlayerStats("Hakimi", "DEF", 84, 94, 71, 79, 82, 80, 81, 65.0, 25, 8),
        PlayerStats("Warren Zaire-Emery", "MID", 78, 79, 74, 85, 86, 71, 73, 50.0, 18, 9),
        PlayerStats("Vitinha", "MID", 81, 73, 80, 88, 87, 68, 74, 40.0, 24, 7),
        PlayerStats("Lucas Hernandez", "DEF", 82, 81, 58, 76, 74, 86, 82, 50.0, 28, 7),
        PlayerStats("Randal Kolo Muani", "FWD", 81, 87, 84, 78, 84, 47, 79, 70.0, 25, 7),
        PlayerStats("Bradley Barcola", "FWD", 79, 92, 79, 80, 89, 35, 68, 45.0, 22, 8),
        PlayerStats("Milan Skriniar", "DEF", 83, 68, 59, 77, 73, 88, 83, 40.0, 29, 7)
    ]
    for player_stats in psg_players:
        psg.add_player(Player(player_stats))
    teams.append(psg)
    
    # Bayern Munich
    bayern = Team("Bayern Munich", "Germany")
    bayern_players = [
        PlayerStats("Harry Kane", "FWD", 90, 68, 93, 83, 82, 47, 82, 120.0, 30, 9),
        PlayerStats("Jamal Musiala", "MID", 86, 86, 81, 89, 92, 64, 71, 100.0, 21, 9),
        PlayerStats("Joshua Kimmich", "MID", 87, 70, 82, 91, 81, 84, 73, 75.0, 29, 8),
        PlayerStats("Manuel Neuer", "GK", 85, 67, 79, 86, 91, 59, 81, 15.0, 38, 7),
        PlayerStats("Alphonso Davies", "DEF", 84, 96, 64, 82, 85, 79, 78, 60.0, 23, 8),
        PlayerStats("Kim Min-jae", "DEF", 83, 74, 54, 75, 72, 88, 85, 50.0, 27, 7),
        PlayerStats("Leon Goretzka", "MID", 82, 73, 80, 84, 82, 78, 86, 35.0, 29, 7),
        PlayerStats("Serge Gnabry", "FWD", 83, 89, 85, 84, 87, 42, 74, 55.0, 28, 7),
        PlayerStats("Dayot Upamecano", "DEF", 81, 87, 52, 74, 71, 85, 84, 45.0, 25, 7),
        PlayerStats("Leroy Sane", "FWD", 84, 92, 84, 86, 90, 37, 72, 65.0, 28, 7),
        PlayerStats("Thomas Muller", "FWD", 81, 65, 85, 88, 89, 56, 71, 8.0, 34, 7)
    ]
    for player_stats in bayern_players:
        bayern.add_player(Player(player_stats))
    teams.append(bayern)
    
    # Arsenal
    arsenal = Team("Arsenal", "England")
    arsenal_players = [
        PlayerStats("Bukayo Saka", "FWD", 87, 88, 83, 87, 92, 49, 73, 110.0, 22, 9),
        PlayerStats("Martin Odegaard", "MID", 86, 74, 84, 91, 89, 67, 72, 90.0, 25, 8),
        PlayerStats("William Saliba", "DEF", 84, 79, 56, 78, 75, 88, 81, 80.0, 23, 8),
        PlayerStats("David Raya", "GK", 82, 71, 77, 85, 87, 61, 82, 30.0, 28, 8),
        PlayerStats("Declan Rice", "MID", 84, 71, 76, 86, 82, 85, 84, 105.0, 25, 8),
        PlayerStats("Gabriel Martinelli", "FWD", 83, 91, 81, 84, 89, 41, 72, 70.0, 22, 8),
        PlayerStats("Gabriel Magalhaes", "DEF", 82, 72, 55, 75, 73, 87, 86, 50.0, 26, 7),
        PlayerStats("Kai Havertz", "FWD", 83, 75, 85, 84, 86, 58, 78, 75.0, 24, 7),
        PlayerStats("Ben White", "DEF", 80, 82, 63, 79, 76, 83, 77, 45.0, 26, 7),
        PlayerStats("Thomas Partey", "MID", 81, 74, 77, 84, 81, 82, 82, 40.0, 30, 6),
        PlayerStats("Gabriel Jesus", "FWD", 82, 85, 84, 83, 87, 45, 75, 50.0, 27, 7)
    ]
    for player_stats in arsenal_players:
        arsenal.add_player(Player(player_stats))
    teams.append(arsenal)
    
    # Liverpool
    liverpool = Team("Liverpool", "England")
    liverpool_players = [
        PlayerStats("Mohamed Salah", "FWD", 89, 90, 91, 81, 90, 45, 75, 70.0, 32, 8),
        PlayerStats("Virgil van Dijk", "DEF", 87, 77, 60, 91, 88, 92, 86, 40.0, 32, 8),
        PlayerStats("Alisson", "GK", 87, 72, 78, 87, 90, 65, 85, 45.0, 31, 8),
        PlayerStats("Sadio Mane", "FWD", 86, 94, 84, 86, 91, 44, 77, 60.0, 31, 7),
        PlayerStats("Jordan Henderson", "MID", 79, 68, 74, 88, 82, 78, 77, 15.0, 33, 6),
        PlayerStats("Andy Robertson", "DEF", 83, 87, 68, 84, 82, 82, 79, 35.0, 30, 7),
        PlayerStats("Fabinho", "MID", 83, 69, 75, 86, 79, 87, 84, 40.0, 30, 7),
        PlayerStats("Diogo Jota", "FWD", 84, 85, 86, 82, 87, 48, 76, 65.0, 27, 8),
        PlayerStats("Trent Alexander-Arnold", "DEF", 84, 76, 71, 93, 87, 78, 72, 70.0, 25, 7),
        PlayerStats("Luis Diaz", "FWD", 82, 92, 82, 85, 91, 38, 71, 75.0, 27, 8),
        PlayerStats("Darwin Nunez", "FWD", 81, 91, 83, 76, 83, 49, 82, 80.0, 24, 7)
    ]
    for player_stats in liverpool_players:
        liverpool.add_player(Player(player_stats))
    teams.append(liverpool)
    
    # Inter Milan
    inter = Team("Inter Milan", "Italy")
    inter_players = [
        PlayerStats("Lautaro Martinez", "FWD", 87, 82, 89, 81, 84, 56, 78, 90.0, 26, 8),
        PlayerStats("Alessandro Bastoni", "DEF", 84, 78, 67, 87, 83, 86, 77, 70.0, 24, 8),
        PlayerStats("Nicolo Barella", "MID", 85, 80, 82, 87, 88, 76, 77, 80.0, 27, 8),
        PlayerStats("Yann Sommer", "GK", 83, 65, 75, 84, 88, 62, 79, 8.0, 35, 7),
        PlayerStats("Marcus Thuram", "FWD", 83, 87, 84, 79, 85, 51, 81, 60.0, 26, 8),
        PlayerStats("Hakan Calhanoglu", "MID", 82, 71, 85, 90, 86, 72, 74, 25.0, 30, 7),
        PlayerStats("Milan Skriniar", "DEF", 83, 68, 59, 77, 73, 88, 83, 40.0, 29, 7),
        PlayerStats("Federico Dimarco", "DEF", 80, 84, 73, 86, 84, 79, 75, 35.0, 26, 8),
        PlayerStats("Denzel Dumfries", "DEF", 80, 88, 69, 76, 78, 81, 84, 30.0, 27, 7),
        PlayerStats("Henrikh Mkhitaryan", "MID", 79, 72, 80, 87, 87, 70, 68, 10.0, 35, 6),
        PlayerStats("Edin Dzeko", "FWD", 78, 65, 85, 78, 79, 55, 78, 5.0, 37, 6)
    ]
    for player_stats in inter_players:
        inter.add_player(Player(player_stats))
    teams.append(inter)
    
    return teams

if __name__ == "__main__":
    # Create tournament with 8 world-class teams
    teams = create_world_class_teams()
    
    # Create tournament
    tournament = Tournament("Champions League Elite", teams, "knockout")
    
    # Start the tournament
    tournament.start_tournament()
