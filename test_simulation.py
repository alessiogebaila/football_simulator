from backend_simple import simulate_match_detailed

print('Testing the enhanced match simulation... (only players in starting eleven can score)')
match = simulate_match_detailed('Manchester City', 'Arsenal')
print(f'Final score: {match.home_team} {match.home_score} - {match.away_score} {match.away_team}')
print('Goal scorers:')
for event in match.events:
    if event.event_type == 'goal':
        print(f'{event.minute}\' - {event.player} for {event.team}')
