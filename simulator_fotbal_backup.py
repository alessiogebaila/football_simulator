import time
import random

class Team:
    def __init__(self, name):
        self.team_name = name

    def __str__(self):
        return f"{self.team_name}"

class Score:
    def __init__(self, home = 0, away = 0):
        self._home_goals = home
        self._away_goals = away
        self.scoring_minutes = []

    def __str__(self):
        return f"{self._home_goals} - {self._away_goals}"

    def home_goal(self, minute):
        self._home_goals += 1
        self.scoring_minutes.append(minute)

    def away_goal(self, minute):
        self._away_goals += 1
        self.scoring_minutes.append(minute)

class Match:
    
    DURATION1 = 9 + random.randint(1, 10) / 10
    DURATION2=3

    def __init__(self, home_team, away_team, score):
        self.home_team = home_team
        self.away_team = away_team
        self.score = score
        self.minute = 0

    def __str__(self):
        return f" {self.home_team} {self.score} {self.away_team} "

    def start(self):
        self.start_time = time.time()
        print("A inceput meciul!Vizionare placuta!")
        print(self)
        self.trigger_event()
        
    def trigger_event(self):

        self.last_time = time.time()
        self.sleep_time = random.randint(0, 90) / 10
        #print(sleep_time)
        
        if self.sleep_time + time.time() > self.start_time + Match.DURATION1:
            print("Meciul s-a incheiat cu scorul", self,"!")
            return

        for i in range(int(self.sleep_time)):
            time.sleep(1)
            print(self.current_minute())

        time.sleep(self.sleep_time - int(self.sleep_time))
        print(self.current_minute())

        # time.sleep(self.sleep_time)        
        event = random.choice([self.inscriere, self.cartonas_colorat])
        event()

        print(self)
        self.trigger_event()


    def inscriere(self):
        events = [self.score.home_goal, self.score.away_goal]
        scoring_event = random.choice(events)

        print(f"GOOOOOOOOOOOOOOOOOOL in minutul", f'{self.current_minute()}\'')
        scoring_event(self.current_minute())


    def current_minute(self):
        minute = time.time() - self.start_time
        return int(minute * 10)
    

    def cartonas_colorat(self):
        teams = [self.home_team, self.away_team]
        orange_card_team = random.choice(teams)
        print(f"Cartonas {random.choice(['rosu', 'galben'])} pentru ", orange_card_team, f'{self.current_minute()}\'')

    def winner(self):
        if self.score._home_goals > self.score._away_goals:
            print(f"Victorie pentru ", f"{self.home_team}\n")
            return self.home_team
        
        elif self.score._home_goals < self.score._away_goals:
            print(f"Victorie pentru ", f"{self.away_team}\n")
            return self.away_team
        else:
            print("Meciul s-a terminat la egalitate,urmeaza penaltyuri!")
    
            self.penaltyShootout()
            
        
    def penaltyShootout(self):

        penalty_home1=random.randint(0,1)
        print(f"{penalty_home1} - 0")
        time.sleep(1)

        penalty_away1=random.randint(0,1)
        print(f"{penalty_home1} - {penalty_away1}")
        time.sleep(1)
        
        penalty_home2=random.randint(0,1)
        print(f"{penalty_home1+penalty_home2} - {penalty_away1}")
        time.sleep(1)

        penalty_away2=random.randint(0,1)
        print(f"{penalty_home1+penalty_home2} - {penalty_away1+penalty_away2}")
        time.sleep(1)

        penalty_home3=random.randint(0,1)
        print(f"{penalty_home1+penalty_home2+penalty_home3} - {penalty_away1+penalty_away2}")
        time.sleep(1)

        penalty_away3=random.randint(0,1)
        print(f"{penalty_home1+penalty_home2+penalty_home3} - {penalty_away1+penalty_away2+penalty_away3}")
        time.sleep(1)

        penalty_home4=random.randint(0,1)
        print(f"{penalty_home1+penalty_home2+penalty_home3+penalty_home4} - {penalty_away1+penalty_away2+penalty_away3}")
        time.sleep(1)

        penalty_away4=random.randint(0,1)
        print(f"{penalty_home1+penalty_home2+penalty_home3+penalty_home4} - {penalty_away1+penalty_away2+penalty_away3+penalty_away4}")
        time.sleep(1)


        penalty_home5=random.randint(0,1)
        print(f"{penalty_home1+penalty_home2+penalty_home3+penalty_home4+penalty_home5} - {penalty_away1+penalty_away2+penalty_away3+penalty_away4}")
        time.sleep(1)

        penalty_away5=random.randint(0,1)
        print(f"{penalty_home1+penalty_home2+penalty_home3+penalty_home4+penalty_home5} - {penalty_away1+penalty_away2+penalty_away3+penalty_away4+penalty_away5}")
        time.sleep(1)

        penalty_home = penalty_home1 + penalty_home2 + penalty_home3 + penalty_home4 + penalty_home5
        penalty_away = penalty_away1 + penalty_away2 + penalty_away3 + penalty_away4 + penalty_away5

       
        
        print(f"Rezultat penalty-uri: {self.home_team} {penalty_home} - {penalty_away} {self.away_team}")

        if penalty_home>penalty_away:
            self.score._home_goals+=1
            penalty_winner=self.home_team
            return penalty_winner
        elif penalty_home<penalty_away:
            self.score._away_goals+=1
            penalty_winner=self.away_team
            return penalty_winner
        else:
            print("Egalitate la penaltyuri,continuam!")
            return self.penaltyShootout()
        

            



MCI= Team("Manchester City")
FLU= Team("Fluminense")

FCB=Team("FC Barcelona")
RMA=Team("Real Madrid CF")

FRA=Team("Equipe de France")
ARG=Team("Seleccion Argentina")

RO=Team("Echipa Nationala a Romaniei")
BEL=Team("Belgium")

FCSB=Team("FCSB")
FCD=Team("FC Dinamo Bucuresti")


BAY=Team("Bayern Munchen")
BVB=Team("Borussia Dortumund")

score= Score()

match1= Match(MCI,FLU,score)
match1.start()
match1.winner()

match2=Match(FCB,RMA,score)
match2.start()
match2.winner()

match3=Match(FRA,ARG,score)
match3.start()
match3.winner()

match4=Match(RO,BEL,score)
match4.start()
match4.winner()

match5=Match(FCSB,FCD,score)
match5.start()
match5.winner()

match6=Match(BAY,BVB,score)
match6.start()
match6.winner()

winner1 = match1.winner()
winner2 = match2.winner()

if winner1 and winner2:
    match7 = Match(winner1, winner2, Score())
    match7.start()
    match7.winner()

winner3 = match3.winner()
winner4 = match4.winner()

if winner3 and winner4:
    match8=Match(winner3,winner4,Score())
    match8.start()
    match7.winner()
    
winner5 = match5.winner()
winner6 = match6.winner()

if winner5 and winner6:
    match9=Match(winner5,winner6,Score())
    match9.start()
    match9.winner()

winner7=match7.winner()
winner9=match9.winner()

if winner7 and winner9:
    match10=Match(winner7,winner9,Score())
    match10.start()
    match10.winner()

winner8=match8.winner()
winner10=match10.winner()

if winner8 and winner10:
    match11=Match(winner8,winner10,Score())
    match11.start()
    match11.winner()

winner11=match11.winner()
print(f'{winner11} a castigat turneul.FELICITARI!CAMPIONII,CAMPIONII,OLE,OLE,OLEEEEEEEEEEEEEEEEEEEEE')




