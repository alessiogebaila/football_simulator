import axios from 'axios';
import { 
  Team, 
  Player, 
  Match, 
  TeamAnalysis, 
  Tournament, 
  GlobalStats, 
  MatchPredictionRequest 
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

export const footballApi = {
  // Health check
  async getHealth() {
    const response = await api.get('/');
    return response.data;
  },

  // Teams
  async getTeams(): Promise<Team[]> {
    const response = await api.get('/teams');
    return response.data;
  },

  async getTeam(teamName: string): Promise<Team> {
    const response = await api.get(`/teams/${encodeURIComponent(teamName)}`);
    return response.data;
  },

  async getTeamPlayers(teamName: string): Promise<Player[]> {
    const response = await api.get(`/teams/${encodeURIComponent(teamName)}/players`);
    return response.data;
  },

  async getStartingEleven(teamName: string): Promise<{ formation: string; players: Player[] }> {
    const response = await api.get(`/teams/${encodeURIComponent(teamName)}/starting-eleven`);
    return response.data;
  },

  // Match prediction and simulation
  async predictMatch(request: MatchPredictionRequest): Promise<Match> {
    const response = await api.post('/predict-match', request);
    return response.data;
  },

  async simulateMatch(homeTeam: string, awayTeam: string, type: string = 'detailed'): Promise<Match> {
    const response = await api.post('/simulate-match', {
      home_team: homeTeam,
      away_team: awayTeam,
      type: type
    });
    return response.data;
  },

  async simulateLiveMatch(homeTeam: string, awayTeam: string, speed: number = 1): Promise<Match> {
    const response = await api.post('/simulate-live-match', {
      home_team: homeTeam,
      away_team: awayTeam,
      speed: speed
    });
    return response.data;
  },

  // Team analysis
  async getTeamAnalysis(teamName: string): Promise<TeamAnalysis> {
    const response = await api.get(`/team-analysis/${encodeURIComponent(teamName)}`);
    return response.data;
  },

  // Tournament
  async getTournamentStatus(): Promise<any> {
    const response = await api.get('/tournament-status');
    return response.data;
  },

  async runTournament(teamNames: string[]): Promise<Tournament> {
    const response = await api.post('/tournament', { team_names: teamNames });
    return response.data;
  },

  async createTournament(teamNames: string[]): Promise<any> {
    const response = await api.post('/create-tournament', teamNames);
    return response.data;
  },

  // Statistics
  async getGlobalStats(): Promise<GlobalStats> {
    const response = await api.get('/stats');
    return response.data;
  },

  // --- Real-data prediction engine (/engine) ---
  async getEngineTeams(): Promise<{ club: Record<string, string[]>; international: string[] }> {
    const response = await api.get('/engine/teams');
    return response.data;
  },

  async getEnginePrediction(request: {
    home_team: string;
    away_team: string;
    scope: 'club' | 'international';
    neutral?: boolean;
    bookmaker_odds?: { home?: number; draw?: number; away?: number };
    home_lineup?: string[];
    away_lineup?: string[];
  }): Promise<any> {
    // Model fitting on first call can take ~30s; give it room
    const response = await api.post('/engine/predict', request, { timeout: 120000 });
    return response.data;
  },

  async getEngineBacktest(): Promise<any[]> {
    const response = await api.get('/engine/backtest');
    return response.data;
  },
};

export default footballApi;
