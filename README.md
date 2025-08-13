# Enhanced Football Simulator 🏆

A sophisticated football tournament simulator with realistic players, statistics, and machine learning-based match predictions.

## 🌟 Key Features

### 🧑‍🤝‍🧑 Player System
- **Detailed Player Stats**: Each player has 7 core attributes (pace, shooting, passing, dribbling, defending, physical)
- **Position-Based Gameplay**: Players are assigned positions (GK, DEF, MID, FWD) that affect their role in matches
- **Market Values**: Realistic player valuations that influence team strength calculations
- **Form & Fitness**: Dynamic performance modifiers that change match by match
- **Age & Development**: Player ages affect their market value and performance

### 📊 Advanced Statistics
- **Match Statistics**: Possession, shots, corners, fouls, cards tracking
- **Player Performance**: Goals, assists, cards, minutes played
- **Tournament Stats**: Top scorers, top assisters, total goals/cards
- **Team Chemistry**: Team cohesion affects overall performance
- **Manager Ratings**: Tactical influence on team performance

### 🤖 Machine Learning Predictions
- **Logistic Regression Model**: Trained on synthetic match data
- **Multiple Factors**: Team strength, squad value, form, home advantage
- **Realistic Odds**: Win/draw/loss probabilities for each match
- **Performance Tracking**: Model learns from team characteristics

### 🏟️ Enhanced Match Simulation
- **Realistic Events**: Goals, cards, substitutions based on player abilities
- **Weighted Outcomes**: Better players more likely to score/assist
- **Dynamic Commentary**: Detailed match reporting with player names
- **Pre-Match Analysis**: Team comparisons, predictions, lineups
- **Post-Match Statistics**: Comprehensive match breakdown

### 🏆 Tournament System
- **Knockout Format**: Elimination-style tournament progression
- **Multiple Teams**: 8 world-class teams with realistic squads
- **Progressive Rounds**: Quarter-finals, semi-finals, final
- **Tournament Statistics**: Overall competition tracking
- **Champion Celebration**: Winner announcement with stats

## 🚀 Quick Start

### Prerequisites
```bash
pip install numpy pandas scikit-learn pymc
```

### Optional Dependencies
- **PyMC**: For advanced Bayesian inference (recommended for most realistic predictions)
- Without PyMC: Falls back to simplified Bayesian updates

## 🧠 **NEW: Bayesian Learning System**

The simulator now includes a sophisticated Bayesian inference system that learns from match results and provides increasingly accurate predictions:

### How It Works
1. **Initial Priors**: Teams start with strength estimates based on squad value and player ratings
2. **Match Learning**: After each match, the system updates team strengths using Bayesian inference
3. **Poisson Prediction**: Goals are predicted using Poisson distribution based on learned attack/defense strengths
4. **Dynamic Rankings**: Team rankings evolve as the tournament progresses

### Key Features
- **Attack/Defense Strengths**: Separate modeling of offensive and defensive capabilities
- **Home Advantage**: Dynamic estimation of home field advantage
- **Form Tracking**: Recent performance influences predictions
- **Expected Goals**: Realistic goal predictions based on team matchups
- **Probability Estimates**: Win/draw/loss probabilities for each match

### Running the Simulator

1. **Demo Mode** (Recommended for first time):
```bash
python demo.py
```

2. **Bayesian Tournament** (Most realistic):
```bash
python bayesian_simulator.py
```

3. **Standard Tournament**:
```bash
python tournament.py
```

4. **Single Enhanced Match**:
```bash
python enhanced_football_simulator.py
```

## 🎮 Demo Options

The demo script provides several ways to explore the simulator:

1. **Single Match Demo**: Experience all new features in one match
2. **ML Predictions Demo**: See how the AI predicts different matchups
3. **Player Statistics Demo**: Explore detailed player data and performance
4. **Full Tournament Demo**: Run a complete 8-team tournament

## 📈 Technical Details

### Player Rating System
- **Overall Rating**: 1-100 scale representing player quality
- **Specialized Stats**: Position-specific attributes for realistic gameplay
- **Performance Calculation**: Dynamic match performance based on multiple factors
- **Market Value**: Reflects real-world player valuations

### Machine Learning Model
- **Algorithm**: Logistic Regression with feature scaling
- **Training Data**: 1000+ synthetic matches with realistic patterns
- **Features**: Team strength, squad value difference, form, home advantage
- **Accuracy**: Calibrated to produce realistic football match probabilities

### Match Simulation Engine
- **Event-Driven**: Realistic timing and frequency of match events
- **Player-Based**: Outcomes determined by individual player abilities
- **Statistical Tracking**: Comprehensive data collection throughout matches
- **Penalty Shootouts**: Skill-based penalty system for draws

## 🌍 Teams Included

The simulator includes 8 world-class teams with realistic squads:

1. **Manchester City** (England)
2. **Real Madrid** (Spain)
3. **FC Barcelona** (Spain)
4. **Paris Saint-Germain** (France)
5. **Bayern Munich** (Germany)
6. **Arsenal** (England)
7. **Liverpool** (England)
8. **Inter Milan** (Italy)

Each team features:
- 11+ realistic players with accurate ratings
- Authentic formations and tactics
- Real market values and player characteristics

## 📊 Sample Output

```
🏆 WELCOME TO ENHANCED CHAMPIONS LEAGUE
============================================================
🌟 8 teams competing for glory!

📋 PARTICIPATING TEAMS:
 1. Real Madrid              - €1185.0M
 2. Manchester City          - €1055.0M
 3. Bayern Munich            - €813.0M
 4. FC Barcelona             - €765.0M
 5. Arsenal                  - €760.0M
 6. Paris Saint-Germain      - €570.0M
 7. Liverpool                - €575.0M
 8. Inter Milan              - €453.0M

🔥 ROUND 1
========================================

⚔️  Manchester City vs Real Madrid

MATCH PREVIEW: Manchester City vs Real Madrid
============================================================
Team Strength: Manchester City: 85.3 | Real Madrid: 87.1
Squad Value: Manchester City: €1055.0M | Real Madrid: €1185.0M

MATCH PREDICTIONS:
Home Win (Manchester City): 35.2%
Draw: 28.1%
Away Win (Real Madrid): 36.7%
```

## 🔧 Customization

### Adding New Players
```python
new_player = PlayerStats(
    name="Your Player",
    position="MID",
    overall_rating=85,
    pace=80,
    shooting=75,
    passing=90,
    dribbling=85,
    defending=70,
    physical=78,
    market_value=50.0,
    age=25,
    form=8
)
team.add_player(Player(new_player))
```

### Modifying Team Characteristics
```python
team.team_chemistry = 90  # 0-100
team.manager_rating = 85  # 0-100
team.home_advantage = 7   # Bonus points
```

### Adjusting ML Model
The machine learning model can be retrained with different parameters by modifying the `generate_training_data()` method in the `MatchPredictor` class.

## 🎯 Future Enhancements

- **Leagues**: Full season simulation with standings
- **Player Development**: Training and progression systems
- **Transfers**: Player trading between teams
- **Weather Conditions**: Environmental factors affecting matches
- **Injuries**: Realistic injury system with recovery times
- **Tactical Systems**: More complex formation and strategy options
- **European Competitions**: Multiple tournament formats

## 📝 Notes

- Match duration is accelerated for simulation purposes (9 seconds = 90 minutes)
- Player stats are inspired by real players but adapted for simulation balance
- The ML model uses synthetic data to ensure fair and unbiased predictions
- All market values are approximate and for simulation purposes only

## 🤝 Contributing

Feel free to enhance the simulator by:
- Adding more realistic player databases
- Improving the ML prediction model
- Creating new tournament formats
- Adding more detailed statistics tracking

Enjoy the enhanced football simulation experience! ⚽🏆
