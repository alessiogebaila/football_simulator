export interface Player {
  name: string;
  position: string;
  age: number;
  overall_rating: number;
  market_value_eur: number;
  nationality: string;
  kit_number: string;
  pace: number;
  shooting: number;
  passing: number;
  dribbling: number;
  defending: number;
  physical: number;
  goalkeeping: number;
}

export interface Team {
  name: string;
  players: Player[];
  total_value: number;
  avg_rating: number;
  avg_age: number;
}

export interface MatchEvent {
  minute: number;
  event_type: string;
  team: string;
  player: string;
  description: string;
}

export interface MatchStats {
  possession_home: number;
  possession_away: number;
  shots_home: number;
  shots_away: number;
  shots_on_target_home: number;
  shots_on_target_away: number;
  corners_home: number;
  corners_away: number;
  fouls_home: number;
  fouls_away: number;
  yellow_cards_home: number;
  yellow_cards_away: number;
  red_cards_home: number;
  red_cards_away: number;
}

export interface Match {
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  prediction_type: string;
  home_confidence: number;
  events?: MatchEvent[];
  stats?: MatchStats;
  status?: string;
  current_minute?: number;
}

export interface TeamAnalysis {
  team_name: string;
  total_value: number;
  avg_rating: number;
  avg_age: number;
  squad_size: number;
  positions: Record<string, number>;
  top_players: Array<{
    name: string;
    position: string;
    rating: number;
    value: number;
    age: number;
  }>;
  strengths: {
    attack: number;
    defense: number;
    confidence: number;
    form: number;
  };
}

export interface Tournament {
  name: string;
  teams: string[];
  matches: Match[];
  winner: string;
  standings: Array<{
    team: string;
    played: number;
    won: number;
    drawn: number;
    lost: number;
    goals_for: number;
    goals_against: number;
    goal_difference: number;
    points: number;
    wins: number;
    draws: number;
    losses: number;
  }>;
}

export interface GlobalStats {
  total_teams: number;
  total_players: number;
  total_market_value: number;
  average_age: number;
  top_valued_players: Array<{
    name: string;
    team: string;
    position: string;
    market_value_eur: number;
    overall_rating: number;
  }>;
  team_rankings: Array<{
    team: string;
    total_value: number;
    avg_rating: number;
    player_count: number;
  }>;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export type PredictionType = 'bayesian' | 'ml' | 'ultimate';

export interface MatchPredictionRequest {
  home_team: string;
  away_team: string;
  prediction_type: PredictionType;
}
