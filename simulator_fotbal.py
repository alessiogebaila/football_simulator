import tkinter as tk
from tkinter import ttk, font, messagebox
import time
import random

class Team:
    def __init__(self, name):
        self.team_name = name

    def __str__(self):
        return f"{self.team_name}"

class Score:
    def __init__(self, home=0, away=0):
        self._home_goals = home
        self._away_goals = away
        self.scoring_minutes = []
        self.yellow_cards = {"home": [], "away": []}
        self.red_cards = {"home": [], "away": []}
        self.events = []  # To store all match events

    def __str__(self):
        return f"{self._home_goals} - {self._away_goals}"

    def home_goal(self, minute):
        self._home_goals += 1
        self.scoring_minutes.append(minute)
        self.events.append({"type": "goal", "team": "home", "minute": minute})

    def away_goal(self, minute):
        self._away_goals += 1
        self.scoring_minutes.append(minute)
        self.events.append({"type": "goal", "team": "away", "minute": minute})
    
    def yellow_card(self, team, minute):
        if team == "home":
            self.yellow_cards["home"].append(minute)
        else:
            self.yellow_cards["away"].append(minute)
        self.events.append({"type": "yellow_card", "team": team, "minute": minute})
    
    def red_card(self, team, minute):
        if team == "home":
            self.red_cards["home"].append(minute)
        else:
            self.red_cards["away"].append(minute)
        self.events.append({"type": "red_card", "team": team, "minute": minute})

class Match:
    def __init__(self, home_team, away_team, score=None):
        self.home_team = home_team
        self.away_team = away_team
        self.score = score if score else Score()
        self.minute = 0
        self.events = []
        self.is_running = False
        self.paused = False
        
        # Create formations for the teams (simplified)
        self.home_formation = self._generate_formation("4-3-3")
        self.away_formation = self._generate_formation("4-4-2")
    
    def _generate_formation(self, formation_type):
        """Generate a simple formation with positions"""
        if formation_type == "4-3-3":
            return {
                "GK": {"x": 0.1, "y": 0.5},
                "DEF": [
                    {"x": 0.2, "y": 0.2},
                    {"x": 0.2, "y": 0.4},
                    {"x": 0.2, "y": 0.6},
                    {"x": 0.2, "y": 0.8}
                ],
                "MID": [
                    {"x": 0.4, "y": 0.3},
                    {"x": 0.4, "y": 0.5},
                    {"x": 0.4, "y": 0.7}
                ],
                "FWD": [
                    {"x": 0.7, "y": 0.3},
                    {"x": 0.7, "y": 0.5},
                    {"x": 0.7, "y": 0.7}
                ]
            }
        elif formation_type == "4-4-2":
            return {
                "GK": {"x": 0.1, "y": 0.5},
                "DEF": [
                    {"x": 0.2, "y": 0.2},
                    {"x": 0.2, "y": 0.4},
                    {"x": 0.2, "y": 0.6},
                    {"x": 0.2, "y": 0.8}
                ],
                "MID": [
                    {"x": 0.4, "y": 0.2},
                    {"x": 0.4, "y": 0.4},
                    {"x": 0.4, "y": 0.6},
                    {"x": 0.4, "y": 0.8}
                ],
                "FWD": [
                    {"x": 0.7, "y": 0.35},
                    {"x": 0.7, "y": 0.65}
                ]
            }
        else:
            # Default 4-4-2
            return self._generate_formation("4-4-2")

    def __str__(self):
        return f"{self.home_team} {self.score} {self.away_team}"

    def start(self, gui_callback=None):
        self.is_running = True
        self.start_time = time.time()
        
        if gui_callback:
            self.gui_callback = gui_callback
        
        self.trigger_event()

    def stop(self):
        self.is_running = False
    
    def pause(self):
        self.paused = True
    
    def resume(self):
        self.paused = False
        
    def trigger_event(self):
        if not self.is_running or self.paused:
            return
        
        # Update current minute
        self.minute = self.current_minute()
        
        # Check if match is over
        if self.minute >= 90:
            self.is_running = False
            if hasattr(self, 'gui_callback'):
                self.gui_callback(self, "match_ended")
            return
        
        # Random event generation
        sleep_time = random.randint(3, 15)
        
        # Randomly decide if an event will occur
        if random.random() < 0.3:  # 30% chance of an event
            event_type = random.choices(
                ["goal", "yellow_card", "red_card", "none"],
                weights=[0.2, 0.15, 0.05, 0.6]
            )[0]
            
            if event_type == "goal":
                scoring_team = random.choice(["home", "away"])
                if scoring_team == "home":
                    self.score.home_goal(self.minute)
                else:
                    self.score.away_goal(self.minute)
                
                if hasattr(self, 'gui_callback'):
                    self.gui_callback(self, "goal", {"team": scoring_team, "minute": self.minute})
            
            elif event_type == "yellow_card":
                card_team = random.choice(["home", "away"])
                self.score.yellow_card(card_team, self.minute)
                
                if hasattr(self, 'gui_callback'):
                    self.gui_callback(self, "yellow_card", {"team": card_team, "minute": self.minute})
            
            elif event_type == "red_card":
                card_team = random.choice(["home", "away"])
                self.score.red_card(card_team, self.minute)
                
                if hasattr(self, 'gui_callback'):
                    self.gui_callback(self, "red_card", {"team": card_team, "minute": self.minute})
        
        # Update GUI if available
        if hasattr(self, 'gui_callback'):
            self.gui_callback(self, "update", {"minute": self.minute})
        
        # Schedule next event
        if hasattr(self, 'root'):
            self.root.after(sleep_time * 100, self.trigger_event)

    def current_minute(self):
        elapsed = time.time() - self.start_time
        # 90 minutes in 90 seconds (fast simulation)
        return min(90, int(elapsed))

    def winner(self):
        if self.score._home_goals > self.score._away_goals:
            return self.home_team
        elif self.score._home_goals < self.score._away_goals:
            return self.away_team
        else:
            return None  # Draw

    def penaltyShootout(self):
        penalty_home = 0
        penalty_away = 0
        
        for i in range(5):
            penalty_home += random.randint(0, 1)
            penalty_away += random.randint(0, 1)
            
            # Could add this to events for GUI display
            if hasattr(self, 'gui_callback'):
                self.gui_callback(self, "penalty", {
                    "round": i+1, 
                    "home_score": penalty_home,
                    "away_score": penalty_away
                })
        
        if penalty_home > penalty_away:
            return self.home_team
        elif penalty_home < penalty_away:
            return self.away_team
        else:
            # Sudden death
            return self.penaltyShootout()  # Simplified - in real implementation would need to prevent infinite recursion


class FootballSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Football Match Simulator")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2c3e50")
        
        # Available teams
        self.teams = [
            Team("Manchester City"),
            Team("Fluminense"),
            Team("FC Barcelona"),
            Team("Real Madrid CF"),
            Team("Equipe de France"),
            Team("Seleccion Argentina"),
            Team("Echipa Nationala a Romaniei"),
            Team("Belgium"),
            Team("FCSB"),
            Team("FC Dinamo Bucuresti"),
            Team("Bayern Munchen"),
            Team("Borussia Dortmund")
        ]
        
        self.match = None
        self.create_widgets()
    
    def create_widgets(self):
        # Use a grid layout with 3 columns
        self.root.grid_columnconfigure(0, weight=1)  # Left column
        self.root.grid_columnconfigure(1, weight=2)  # Middle column
        self.root.grid_columnconfigure(2, weight=1)  # Right column
        
        # Create a custom font for headers
        header_font = font.Font(family="Arial", size=14, weight="bold")
        
        # Left side - Team Selection
        left_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10, bd=2, relief=tk.RAISED)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        tk.Label(left_frame, text="Team Selection", font=header_font, bg="#34495e", fg="white").pack(pady=10)
        
        # Home team
        tk.Label(left_frame, text="Home Team", bg="#34495e", fg="white").pack(anchor='w', pady=5)
        self.home_team_var = tk.StringVar()
        home_team_dropdown = ttk.Combobox(left_frame, textvariable=self.home_team_var, state="readonly", width=25)
        home_team_dropdown['values'] = [team.team_name for team in self.teams]
        home_team_dropdown.pack(pady=5)
        
        # Away team
        tk.Label(left_frame, text="Away Team", bg="#34495e", fg="white").pack(anchor='w', pady=5)
        self.away_team_var = tk.StringVar()
        away_team_dropdown = ttk.Combobox(left_frame, textvariable=self.away_team_var, state="readonly", width=25)
        away_team_dropdown['values'] = [team.team_name for team in self.teams]
        away_team_dropdown.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(left_frame, bg="#34495e")
        btn_frame.pack(pady=20, fill=tk.X)
        
        self.start_btn = tk.Button(btn_frame, text="Start Match", bg="#2ecc71", fg="white", 
                                  padx=10, pady=5, command=self.start_match)
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.reset_btn = tk.Button(btn_frame, text="Reset", bg="#e74c3c", fg="white", 
                                  padx=10, pady=5, command=self.reset_match)
        self.reset_btn.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
        
        # Middle - Score and minute
        middle_frame = tk.Frame(self.root, bg="#2c3e50", padx=10, pady=10)
        middle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Score display
        score_frame = tk.Frame(middle_frame, bg="#2c3e50", padx=20, pady=20)
        score_frame.pack(pady=20)
        
        # Home team name
        self.home_team_label = tk.Label(score_frame, text="Home Team", font=("Arial", 16), 
                                       bg="#2c3e50", fg="white")
        self.home_team_label.grid(row=0, column=0, padx=20)
        
        # Score
        self.score_label = tk.Label(score_frame, text="0 - 0", font=("Arial", 32, "bold"), 
                                   bg="#2c3e50", fg="#f1c40f")
        self.score_label.grid(row=1, column=0, columnspan=3, pady=15)
        
        # Away team name
        self.away_team_label = tk.Label(score_frame, text="Away Team", font=("Arial", 16), 
                                       bg="#2c3e50", fg="white")
        self.away_team_label.grid(row=0, column=2, padx=20)
        
        # Minute display
        minute_frame = tk.Frame(middle_frame, bg="#34495e", padx=10, pady=5, bd=1, relief=tk.RAISED)
        minute_frame.pack(fill=tk.X)
        
        self.minute_label = tk.Label(minute_frame, text="Minute: 0'", font=("Arial", 14), 
                                    bg="#34495e", fg="white")
        self.minute_label.pack(pady=5)
        
        # Right side - Match Events
        right_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10, bd=2, relief=tk.RAISED)
        right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        tk.Label(right_frame, text="Match Events", font=header_font, bg="#34495e", fg="white").pack(pady=10)
        
        # Events list with scrollbar
        events_frame = tk.Frame(right_frame, bg="#34495e")
        events_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(events_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.events_listbox = tk.Listbox(events_frame, bg="#2c3e50", fg="white", 
                                        selectbackground="#3498db", height=15, 
                                        yscrollcommand=scrollbar.set)
        self.events_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.events_listbox.yview)
        
        # Football field visualization
        field_frame = tk.Frame(self.root, bg="#27ae60", padx=10, pady=10, bd=2, relief=tk.RAISED)
        field_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        
        self.field_canvas = tk.Canvas(field_frame, bg="#27ae60", width=980, height=250)
        self.field_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw field markings
        self.draw_field()
        
    def draw_field(self):
        canvas = self.field_canvas
        width = 980
        height = 250
        
        # Field outline
        canvas.create_rectangle(10, 10, width-10, height-10, outline="white")
        
        # Center line
        canvas.create_line(width/2, 10, width/2, height-10, fill="white")
        
        # Center circle
        canvas.create_oval(width/2-40, height/2-40, width/2+40, height/2+40, outline="white")
        canvas.create_oval(width/2-3, height/2-3, width/2+3, height/2+3, fill="white")
        
        # Penalty areas
        # Left
        canvas.create_rectangle(10, height/2-70, 120, height/2+70, outline="white")
        canvas.create_rectangle(10, height/2-30, 60, height/2+30, outline="white")
        # Right
        canvas.create_rectangle(width-120, height/2-70, width-10, height/2+70, outline="white")
        canvas.create_rectangle(width-60, height/2-30, width-10, height/2+30, outline="white")
        
    def update_field(self):
        if not self.match:
            return
        
        # Clear previous players
        self.field_canvas.delete("players")
        
        # Draw home team (left side)
        self.draw_formation(self.match.home_formation, True)
        
        # Draw away team (right side)
        self.draw_formation(self.match.away_formation, False)
    
    def draw_formation(self, formation, is_home_team):
        canvas = self.field_canvas
        width = 980
        height = 250
        
        # Colors for home and away teams
        color = "#3498db" if is_home_team else "#e74c3c"
        
        # X-coordinate offset for home/away team
        x_offset = 0 if is_home_team else width
        x_factor = 1 if is_home_team else -1  # Direction factor
        
        # Draw goalkeeper
        gk = formation["GK"]
        x = x_offset + x_factor * gk["x"] * width
        y = gk["y"] * height
        canvas.create_oval(x-7, y-7, x+7, y+7, fill=color, tags="players")
        canvas.create_text(x, y+15, text="GK", fill="white", font=("Arial", 8), tags="players")
        
        # Draw defenders
        for def_pos in formation["DEF"]:
            x = x_offset + x_factor * def_pos["x"] * width
            y = def_pos["y"] * height
            canvas.create_oval(x-7, y-7, x+7, y+7, fill=color, tags="players")
            canvas.create_text(x, y+15, text="DEF", fill="white", font=("Arial", 8), tags="players")
        
        # Draw midfielders
        for mid_pos in formation["MID"]:
            x = x_offset + x_factor * mid_pos["x"] * width
            y = mid_pos["y"] * height
            canvas.create_oval(x-7, y-7, x+7, y+7, fill=color, tags="players")
            canvas.create_text(x, y+15, text="MID", fill="white", font=("Arial", 8), tags="players")
        
        # Draw forwards
        for fwd_pos in formation["FWD"]:
            x = x_offset + x_factor * fwd_pos["x"] * width
            y = fwd_pos["y"] * height
            canvas.create_oval(x-7, y-7, x+7, y+7, fill=color, tags="players")
            canvas.create_text(x, y+15, text="FWD", fill="white", font=("Arial", 8), tags="players")
    
    def update_match(self, match, event_type, data=None):
        """Update the GUI based on match events"""
        
        # Update score
        self.score_label.config(text=f"{match.score}")
        
        # Update minute
        if data and "minute" in data:
            self.minute_label.config(text=f"Minute: {data['minute']}'")
        
        # Handle different event types
        if event_type == "goal":
            team_str = "Home" if data["team"] == "home" else "Away"
            event_text = f"{data['minute']}' ⚽ GOAL! {team_str} team"
            self.events_listbox.insert(0, event_text)
        
        elif event_type == "yellow_card":
            team_str = "Home" if data["team"] == "home" else "Away"
            # Use a rectangle for yellow card (displayed as rectangle emoji)
            event_text = f"{data['minute']}' 🟨 Yellow card - {team_str} team"
            self.events_listbox.insert(0, event_text)
        
        elif event_type == "red_card":
            team_str = "Home" if data["team"] == "home" else "Away"
            # Use a rectangle for red card (displayed as rectangle emoji)
            event_text = f"{data['minute']}' 🟥 Red card - {team_str} team"
            self.events_listbox.insert(0, event_text)
        
        elif event_type == "match_ended":
            event_text = f"90' ⏱️ Match ended: {match}"
            self.events_listbox.insert(0, event_text)
            
            if match.winner():
                winner_text = f"Winner: {match.winner()}"
                self.events_listbox.insert(0, winner_text)
            else:
                self.events_listbox.insert(0, "Match ended in a draw")
            
            self.start_btn.config(text="Start Match", state=tk.NORMAL)
        
        # Update field visualization
        self.update_field()
        
    def start_match(self):
        home_team_name = self.home_team_var.get()
        away_team_name = self.away_team_var.get()
        
        if not home_team_name or not away_team_name:
            messagebox.showwarning("Warning", "Please select both teams")
            return
        
        if home_team_name == away_team_name:
            messagebox.showwarning("Warning", "Please select different teams")
            return
        
        # Find team objects
        home_team = next((team for team in self.teams if team.team_name == home_team_name), None)
        away_team = next((team for team in self.teams if team.team_name == away_team_name), None)
        
        if not home_team or not away_team:
            return
        
        # Update labels
        self.home_team_label.config(text=home_team_name)
        self.away_team_label.config(text=away_team_name)
        
        # Clear previous events
        self.events_listbox.delete(0, tk.END)
        
        # Create and start match
        self.match = Match(home_team, away_team)
        self.match.root = self.root
        
        # Update the button
        self.start_btn.config(text="Simulating...", state=tk.DISABLED)
        
        # Add starting event
        self.events_listbox.insert(0, "0' 🏁 Match started")
        
        # Update field before starting
        self.update_field()
        
        # Start the match simulation
        self.match.start(self.update_match)
    
    def reset_match(self):
        if self.match and self.match.is_running:
            self.match.stop()
        
        # Reset score and minute
        self.score_label.config(text="0 - 0")
        self.minute_label.config(text="Minute: 0'")
        
        # Reset team labels
        self.home_team_label.config(text="Home Team")
        self.away_team_label.config(text="Away Team")
        
        # Clear events
        self.events_listbox.delete(0, tk.END)
        
        # Reset button
        self.start_btn.config(text="Start Match", state=tk.NORMAL)
        
        # Clear field
        self.field_canvas.delete("players")


def main():
    root = tk.Tk()
    app = FootballSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()




