import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Sports,
  Refresh,
  People,
  MonetizationOn,
  Speed,
  Info,
  Visibility
} from '@mui/icons-material';
import { sportsBettingAPI } from '../services/api';
import moment from 'moment';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bankroll, setBankroll] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [selectedSport, setSelectedSport] = useState('americanfootball_nfl');
  const [refreshing, setRefreshing] = useState(false);
  const [liveMarketData, setLiveMarketData] = useState(null);
  const [publicBettingData, setPublicBettingData] = useState(null);

  const sports = [
    { value: 'americanfootball_nfl', label: 'NFL' },
    { value: 'basketball_nba', label: 'NBA' },
    { value: 'soccer_epl', label: 'Premier League' }
  ];

  useEffect(() => {
    loadDashboardData();
  }, [selectedSport]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load main data from existing API endpoints
      const [bankrollRes, performanceRes] = await Promise.all([
        sportsBettingAPI.getBankroll().catch(() => ({ data: generateMockBankroll() })),
        sportsBettingAPI.getPerformance().catch(() => ({ data: generateMockPerformance() }))
      ]);

      setBankroll(bankrollRes.data);
      setPerformance(performanceRes.data);

      // Load SportRadar predictions data
      await loadSportRadarPredictions();
      
      // Load live market data
      await loadLiveMarketData();
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSportRadarPredictions = async () => {
    try {
      const response = await fetch(`/api/sportsradar/games?sport=${selectedSport}&days=7`);
      if (response.ok) {
        const data = await response.json();
        // Convert games to predictions format
        const predictions = data.games.slice(0, 5).map(game => ({
          id: game.id,
          game: {
            home_team: game.home_team?.name || game.home?.name,
            away_team: game.away_team?.name || game.away?.name,
            commence_time: game.scheduled
          },
          prediction: {
            bet_type: 'moneyline',
            predicted_outcome: game.home_team?.name || game.home?.name,
            confidence_score: 0.75,
            probability: 0.65
          }
        }));
        setRecentPredictions(predictions);
      }
    } catch (err) {
      console.error('SportRadar predictions error:', err);
      setRecentPredictions([]);
    }
  };

  const generateMockBankroll = () => ({
    current_balance: 10000,
    starting_balance: 10000,
    total_profit_loss: 0,
    win_rate: 0,
    roi: 0
  });

  const generateMockPerformance = () => ({
    bankroll: {
      current_balance: 10000,
      starting_balance: 10000,
      total_profit_loss: 0
    },
    recent_performance: {
      bets_last_30_days: 0,
      roi_30_days: 0
    },
    prediction_accuracy: {
      accuracy_percentage: 0
    }
  });

  const loadLiveMarketData = async () => {
    try {
      // Simulate live market data - replace with real API calls
      const mockLiveData = generateMockLiveData();
      const mockPublicData = generateMockPublicBetting();
      
      setLiveMarketData(mockLiveData);
      setPublicBettingData(mockPublicData);
    } catch (err) {
      console.error('Live data error:', err);
    }
  };

  const generateMockLiveData = () => ({
    steamMoves: [
      { game: 'Chiefs vs Bills', market: 'spread', direction: 'away', time: '2 min ago', magnitude: 1.5 },
      { game: 'Celtics vs Lakers', market: 'total', direction: 'under', time: '8 min ago', magnitude: 2.0 },
      { game: 'Cowboys vs Eagles', market: 'moneyline', direction: 'home', time: '15 min ago', magnitude: 0.8 }
    ],
    sharpActions: [
      { game: 'Chiefs vs Bills', action: 'Heavy money on Bills +3.5', confidence: 85 },
      { game: 'Celtics vs Lakers', action: 'Pros taking Lakers +5.5', confidence: 78 },
      { game: 'Cowboys vs Eagles', action: 'Sharp under 47.5', confidence: 72 }
    ],
    marketAlerts: [
      { type: 'reverse_line_movement', message: 'Bills +3.5 moving despite 70% public on Chiefs', severity: 'high' },
      { type: 'consensus_opportunity', message: 'Lakers +5.5 - Public vs Sharp disagreement', severity: 'medium' },
      { type: 'steam_move', message: 'Under 47.5 Cowboys/Eagles - 2pt steam move', severity: 'high' }
    ]
  });

  const generateMockPublicBetting = () => ({
    topGames: [
      {
        game: 'Chiefs vs Bills',
        publicSide: 'Chiefs -3.5',
        publicPercent: 72,
        sharpSide: 'Bills +3.5',
        discrepancy: 'High',
        recommendation: 'Fade Public'
      },
      {
        game: 'Celtics vs Lakers',
        publicSide: 'Celtics -5.5',
        publicPercent: 68,
        sharpSide: 'Lakers +5.5',
        discrepancy: 'Medium',
        recommendation: 'Sharp Side'
      },
      {
        game: 'Cowboys vs Eagles',
        publicSide: 'Over 47.5',
        publicPercent: 58,
        sharpSide: 'Under 47.5',
        discrepancy: 'Low',
        recommendation: 'Monitor'
      }
    ]
  });

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await sportsBettingAPI.updateGames(selectedSport);
      await loadDashboardData();
    } catch (err) {
      console.error('Refresh error:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const StatCard = ({ title, value, subtitle, icon, color = 'primary' }) => (
    <Card elevation={2}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box color={`${color}.main`}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const PredictionCard = ({ prediction }) => {
    const { game, prediction: pred } = prediction;
    const confidenceColor = pred.confidence_score >= 0.8 ? 'success' : 
                           pred.confidence_score >= 0.7 ? 'warning' : 'error';

    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="h6">
              {game.away_team} @ {game.home_team}
            </Typography>
            <Chip 
              label={`${(pred.confidence_score * 100).toFixed(1)}%`}
              color={confidenceColor}
              size="small"
            />
          </Box>
          
          <Typography variant="body2" color="textSecondary" gutterBottom>
            {moment(game.commence_time).format('MMM DD, YYYY HH:mm')}
          </Typography>
          
          <Box mt={1}>
            <Typography variant="body1">
              <strong>{pred.bet_type}:</strong> {pred.predicted_outcome}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Probability: {(pred.probability * 100).toFixed(1)}%
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        
        <Box display="flex" gap={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Sport</InputLabel>
            <Select
              value={selectedSport}
              label="Sport"
              onChange={(e) => setSelectedSport(e.target.value)}
            >
              {sports.map((sport) => (
                <MenuItem key={sport.value} value={sport.value}>
                  {sport.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            startIcon={refreshing ? <CircularProgress size={20} /> : <Refresh />}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            Refresh Data
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Bankroll Stats */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Current Bankroll"
            value={`$${bankroll?.current_balance?.toFixed(2) || '0.00'}`}
            subtitle={`Started: $${bankroll?.starting_balance?.toFixed(2) || '0.00'}`}
            icon={<AccountBalance fontSize="large" />}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Profit/Loss"
            value={`$${bankroll?.total_profit_loss?.toFixed(2) || '0.00'}`}
            subtitle={`ROI: ${bankroll?.roi?.toFixed(2) || '0.00'}%`}
            icon={bankroll?.total_profit_loss >= 0 ? 
              <TrendingUp fontSize="large" /> : 
              <TrendingDown fontSize="large" />}
            color={bankroll?.total_profit_loss >= 0 ? 'success' : 'error'}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Win Rate"
            value={`${bankroll?.win_rate?.toFixed(1) || '0.0'}%`}
            subtitle={`${bankroll?.winning_bets || 0}/${bankroll?.total_bets || 0} bets`}
            icon={<Sports fontSize="large" />}
            color={bankroll?.win_rate >= 65 ? 'success' : 'warning'}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Prediction Accuracy"
            value={`${performance?.prediction_accuracy?.accuracy_percentage?.toFixed(1) || '0.0'}%`}
            subtitle={`${performance?.prediction_accuracy?.correct_predictions || 0}/${performance?.prediction_accuracy?.total_predictions || 0} predictions`}
            icon={<TrendingUp fontSize="large" />}
            color={performance?.prediction_accuracy?.accuracy_percentage >= 65 ? 'success' : 'warning'}
          />
        </Grid>

        {/* Recent Predictions */}
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h5" gutterBottom>
              Top Predictions
            </Typography>
            
            {recentPredictions.length > 0 ? (
              recentPredictions.map((prediction, index) => (
                <PredictionCard key={index} prediction={prediction} />
              ))
            ) : (
              <Typography color="textSecondary" textAlign="center" py={4}>
                No high-confidence predictions available
              </Typography>
            )}
          </Paper>

          {/* Live Market Intelligence */}
          {liveMarketData && (
            <Paper elevation={2} sx={{ p: 2 }}>
              <Box display="flex" alignItems="center" mb={2}>
                <Speed color="primary" sx={{ mr: 1 }} />
                <Typography variant="h5">
                  Live Market Intelligence
                </Typography>
              </Box>
              
              {/* Market Alerts */}
              <Box mb={3}>
                <Typography variant="h6" gutterBottom>
                  Market Alerts
                </Typography>
                {liveMarketData.marketAlerts.map((alert, index) => (
                  <Alert 
                    key={index}
                    severity={alert.severity === 'high' ? 'error' : 'warning'}
                    sx={{ mb: 1 }}
                  >
                    {alert.message}
                  </Alert>
                ))}
              </Box>

              {/* Steam Moves */}
              <Box mb={3}>
                <Typography variant="h6" gutterBottom>
                  Recent Steam Moves
                </Typography>
                <Grid container spacing={1}>
                  {liveMarketData.steamMoves.map((move, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Card variant="outlined">
                        <CardContent sx={{ p: 2 }}>
                          <Box display="flex" alignItems="center" mb={1}>
                            <Speed fontSize="small" color="error" />
                            <Typography variant="body2" fontWeight="bold" sx={{ ml: 1 }}>
                              {move.game}
                            </Typography>
                          </Box>
                          <Typography variant="body2">
                            {move.market.toUpperCase()} - {move.direction.toUpperCase()}
                          </Typography>
                          <Box display="flex" justifyContent="space-between" mt={1}>
                            <Typography variant="caption">
                              {move.time}
                            </Typography>
                            <Chip 
                              label={`${move.magnitude}pt`}
                              size="small"
                              color={move.magnitude > 1.0 ? 'error' : 'warning'}
                            />
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>

              {/* Sharp Actions */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  Sharp Money Actions
                </Typography>
                {liveMarketData.sharpActions.map((action, index) => (
                  <Box 
                    key={index}
                    display="flex" 
                    justifyContent="space-between" 
                    alignItems="center"
                    p={2}
                    sx={{ 
                      backgroundColor: 'background.paper',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1
                    }}
                  >
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {action.game}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {action.action}
                      </Typography>
                    </Box>
                    <Chip 
                      label={`${action.confidence}%`}
                      color={action.confidence > 80 ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                ))}
              </Box>
            </Paper>
          )}
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h5" gutterBottom>
              Quick Stats
            </Typography>
            
            <Box mb={2}>
              <Typography variant="body2" color="textSecondary">
                Current Streak
              </Typography>
              <Typography variant="h6" color={bankroll?.current_streak >= 0 ? 'success.main' : 'error.main'}>
                {bankroll?.current_streak > 0 ? `+${bankroll.current_streak}` : bankroll?.current_streak || 0}
              </Typography>
            </Box>

            <Box mb={2}>
              <Typography variant="body2" color="textSecondary">
                Bankroll Growth
              </Typography>
              <Typography variant="h6" color={bankroll?.bankroll_growth >= 0 ? 'success.main' : 'error.main'}>
                {bankroll?.bankroll_growth?.toFixed(2) || '0.00'}%
              </Typography>
            </Box>

            <Box mb={2}>
              <Typography variant="body2" color="textSecondary">
                Total Wagered
              </Typography>
              <Typography variant="h6">
                ${bankroll?.total_wagered?.toFixed(2) || '0.00'}
              </Typography>
            </Box>

            <Box>
              <Typography variant="body2" color="textSecondary">
                Longest Win Streak
              </Typography>
              <Typography variant="h6" color="success.main">
                {bankroll?.longest_winning_streak || 0}
              </Typography>
            </Box>
          </Paper>

          {/* Public vs Sharp Money */}
          {publicBettingData && (
            <Paper elevation={2} sx={{ p: 2 }}>
              <Box display="flex" alignItems="center" mb={2}>
                <People color="primary" sx={{ mr: 1 }} />
                <Typography variant="h5">
                  Public vs Sharp
                </Typography>
              </Box>
              
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Game</TableCell>
                      <TableCell align="center">Public %</TableCell>
                      <TableCell align="center">Sharp Side</TableCell>
                      <TableCell align="center">Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {publicBettingData.topGames.map((game, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="caption" display="block">
                            {game.game}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Box>
                            <Typography variant="body2">
                              {game.publicPercent}%
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={game.publicPercent} 
                              sx={{ height: 4, borderRadius: 2 }}
                              color={game.publicPercent > 70 ? 'error' : 'primary'}
                            />
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <Typography variant="caption">
                            {game.sharpSide}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Chip 
                            label={game.recommendation}
                            size="small"
                            color={
                              game.recommendation === 'Fade Public' ? 'error' :
                              game.recommendation === 'Sharp Side' ? 'success' : 'default'
                            }
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <Box mt={2}>
                <Typography variant="caption" color="textSecondary">
                  🔴 High discrepancy = Fade public | 🟢 Sharp side = Follow pros
                </Typography>
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
