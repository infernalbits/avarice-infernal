import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Add request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const sportsBettingAPI = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Games
  getGames: (sport = 'americanfootball_nfl') => 
    api.get(`/games?sport=${sport}`),
  
  updateGames: (sport = 'americanfootball_nfl') => 
    api.post('/games/update', { sport }),

  // Predictions
  getPredictions: (sport = 'americanfootball_nfl', minConfidence = 0.65) =>
    api.get(`/predictions?sport=${sport}&min_confidence=${minConfidence}`),

  // Bets
  getBets: (status = 'all', limit = 50) =>
    api.get(`/bets?status=${status}&limit=${limit}`),
  
  placeBet: (betData) =>
    api.post('/bets', betData),

  // Bankroll
  getBankroll: () => api.get('/bankroll'),

  // Performance
  getPerformance: () => api.get('/performance'),

  // Team Stats
  getTeamStats: (sport = 'americanfootball_nfl', team = null) => {
    let url = `/team-stats?sport=${sport}`;
    if (team) url += `&team=${team}`;
    return api.get(url);
  },
};

export default api;
