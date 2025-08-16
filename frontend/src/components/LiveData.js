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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Tabs,
  Tab,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  People,
  MonetizationOn,
  Speed,
  Refresh,
  Info,
  Warning
} from '@mui/icons-material';
import { sportsBettingAPI } from '../services/api';

const LiveData = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [liveData, setLiveData] = useState(null);
  const [publicBetting, setPublicBetting] = useState(null);
  const [sharpMoney, setSharpMoney] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    loadLiveData();
    const interval = setInterval(loadLiveData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadLiveData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Simulated API calls - replace with real endpoints
      const [oddsRes, publicRes, sharpRes] = await Promise.all([
        fetch('/api/live-odds').catch(() => ({ json: () => generateMockOdds() })),
        fetch('/api/public-betting').catch(() => ({ json: () => generateMockPublicData() })),
        fetch('/api/sharp-money').catch(() => ({ json: () => generateMockSharpData() }))
      ]);

      const [odds, publicData, sharpData] = await Promise.all([
        oddsRes.json ? oddsRes.json() : generateMockOdds(),
        publicRes.json ? publicRes.json() : generateMockPublicData(),
        sharpRes.json ? sharpRes.json() : generateMockSharpData()
      ]);

      setLiveData(odds);
      setPublicBetting(publicData);
      setSharpMoney(sharpData);
      setLastUpdate(new Date());
    } catch (err) {
      setError('Failed to load live data');
      console.error('Live data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateMockOdds = () => ({
    games: [
      {
        id: 'game1',
        homeTeam: 'Kansas City Chiefs',
        awayTeam: 'Buffalo Bills',
        startTime: '2024-01-21T18:00:00Z',
        odds: {
          moneyline: { home: -140, away: +120 },
          spread: { home: -3.5, away: +3.5, homeOdds: -110, awayOdds: -110 },
          total: { line: 47.5, over: -110, under: -110 }
        },
        consensus: {
          books: 8,
          avgSpread: -3.5,
          avgTotal: 47.5,
          spreadRange: { min: -3, max: -4 },
          totalRange: { min: 47, max: 48 }
        }
      },
      {
        id: 'game2',
        homeTeam: 'Boston Celtics',
        awayTeam: 'LA Lakers',
        startTime: '2024-01-22T20:30:00Z',
        odds: {
          moneyline: { home: -180, away: +155 },
          spread: { home: -5.5, away: +5.5, homeOdds: -110, awayOdds: -110 },
          total: { line: 228.5, over: -105, under: -115 }
        },
        consensus: {
          books: 12,
          avgSpread: -5.5,
          avgTotal: 228.5,
          spreadRange: { min: -5, max: -6 },
          totalRange: { min: 228, max: 229 }
        }
      }
    ]
  });

  const generateMockPublicData = () => ({
    games: [
      {
        gameId: 'game1',
        publicBetting: {
          moneyline: { homePercent: 68, awayPercent: 32 },
          spread: { homePercent: 72, awayPercent: 28 },
          total: { overPercent: 58, underPercent: 42 }
        },
        handle: {
          moneylineHome: 62,
          spreadHome: 55,
          totalOver: 48
        },
        tickets: {
          moneylineHome: 68,
          spreadHome: 72,
          totalOver: 58
        }
      },
      {
        gameId: 'game2',
        publicBetting: {
          moneyline: { homePercent: 75, awayPercent: 25 },
          spread: { homePercent: 80, awayPercent: 20 },
          total: { overPercent: 65, underPercent: 35 }
        },
        handle: {
          moneylineHome: 45,
          spreadHome: 35,
          totalOver: 70
        },
        tickets: {
          moneylineHome: 75,
          spreadHome: 80,
          totalOver: 65
        }
      }
    ]
  });

  const generateMockSharpData = () => ({
    games: [
      {
        gameId: 'game1',
        sharpAction: {
          moneyline: { side: 'away', confidence: 78 },
          spread: { side: 'away', confidence: 65 },
          total: { side: 'under', confidence: 72 }
        },
        steamMoves: [
          { time: '2 hours ago', market: 'spread', direction: 'away', magnitude: 0.5 },
          { time: '45 min ago', market: 'total', direction: 'under', magnitude: 1.0 }
        ],
        lineMovement: {
          spread: { opening: -3, current: -3.5, direction: 'home' },
          total: { opening: 48, current: 47.5, direction: 'under' }
        }
      },
      {
        gameId: 'game2',
        sharpAction: {
          moneyline: { side: 'away', confidence: 82 },
          spread: { side: 'away', confidence: 88 },
          total: { side: 'over', confidence: 60 }
        },
        steamMoves: [
          { time: '3 hours ago', market: 'spread', direction: 'away', magnitude: 1.5 },
          { time: '1 hour ago', market: 'moneyline', direction: 'away', magnitude: 0.8 }
        ],
        lineMovement: {
          spread: { opening: -4.5, current: -5.5, direction: 'home' },
          total: { opening: 229, current: 228.5, direction: 'under' }
        }
      }
    ]
  });

  const PublicBettingCard = ({ game, publicData }) => {
    const gamePublic = publicData?.games?.find(g => g.gameId === game.id);
    if (!gamePublic) return null;

    const { publicBetting, handle, tickets } = gamePublic;

    return (
      <Card elevation={2} sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {game.awayTeam} @ {game.homeTeam}
          </Typography>
          
          <Grid container spacing={2}>
            {/* Moneyline */}
            <Grid item xs={12} md={4}>
              <Box mb={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Moneyline Public %
                </Typography>
                <Box display="flex" alignItems="center" mb={1}>
                  <People fontSize="small" color="primary" />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    Tickets: {publicBetting.moneyline.homePercent}% / {publicBetting.moneyline.awayPercent}%
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center">
                  <MonetizationOn fontSize="small" color="secondary" />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    Handle: {handle.moneylineHome}% / {100 - handle.moneylineHome}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={publicBetting.moneyline.homePercent} 
                  sx={{ mt: 1, height: 8, borderRadius: 4 }}
                />
                {Math.abs(tickets.moneylineHome - handle.moneylineHome) > 10 && (
                  <Chip 
                    label="Sharp Disagreement" 
                    color="warning" 
                    size="small" 
                    sx={{ mt: 1 }}
                  />
                )}
              </Box>
            </Grid>

            {/* Spread */}
            <Grid item xs={12} md={4}>
              <Box mb={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Spread Public %
                </Typography>
                <Box display="flex" alignItems="center" mb={1}>
                  <People fontSize="small" color="primary" />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    Tickets: {publicBetting.spread.homePercent}% / {publicBetting.spread.awayPercent}%
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center">
                  <MonetizationOn fontSize="small" color="secondary" />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    Handle: {handle.spreadHome}% / {100 - handle.spreadHome}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={publicBetting.spread.homePercent} 
                  sx={{ mt: 1, height: 8, borderRadius: 4 }}
                />
                {(publicBetting.spread.homePercent > 75 || publicBetting.spread.homePercent < 25) && (
                  <Chip 
                    label="Contrarian Spot" 
                    color="success" 
                    size="small" 
                    sx={{ mt: 1 }}
                  />
                )}
              </Box>
            </Grid>

            {/* Total */}
            <Grid item xs={12} md={4}>
              <Box mb={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Total Public %
                </Typography>
                <Box display="flex" alignItems="center" mb={1}>
                  <People fontSize="small" color="primary" />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    Tickets: {publicBetting.total.overPercent}% O / {publicBetting.total.underPercent}% U
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center">
                  <MonetizationOn fontSize="small" color="secondary" />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    Handle: {handle.totalOver}% O / {100 - handle.totalOver}% U
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={publicBetting.total.overPercent} 
                  sx={{ mt: 1, height: 8, borderRadius: 4 }}
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const SharpMoneyCard = ({ game, sharpData }) => {
    const gameSharp = sharpData?.games?.find(g => g.gameId === game.id);
    if (!gameSharp) return null;

    const { sharpAction, steamMoves, lineMovement } = gameSharp;

    return (
      <Card elevation={2} sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {game.awayTeam} @ {game.homeTeam}
          </Typography>
          
          <Grid container spacing={2}>
            {/* Sharp Action */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Sharp Money Direction
              </Typography>
              
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Moneyline:</Typography>
                  <Chip 
                    label={`${sharpAction.moneyline.side.toUpperCase()} (${sharpAction.moneyline.confidence}%)`}
                    color={sharpAction.moneyline.confidence > 75 ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
                  <Typography variant="body2">Spread:</Typography>
                  <Chip 
                    label={`${sharpAction.spread.side.toUpperCase()} (${sharpAction.spread.confidence}%)`}
                    color={sharpAction.spread.confidence > 75 ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
                  <Typography variant="body2">Total:</Typography>
                  <Chip 
                    label={`${sharpAction.total.side.toUpperCase()} (${sharpAction.total.confidence}%)`}
                    color={sharpAction.total.confidence > 75 ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
              </Box>
            </Grid>

            {/* Line Movement */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Line Movement
              </Typography>
              
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Spread:</Typography>
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2">
                      {lineMovement.spread.opening} → {lineMovement.spread.current}
                    </Typography>
                    {lineMovement.spread.opening !== lineMovement.spread.current && (
                      lineMovement.spread.direction === 'home' ? 
                        <TrendingUp color="success" fontSize="small" sx={{ ml: 1 }} /> :
                        <TrendingDown color="error" fontSize="small" sx={{ ml: 1 }} />
                    )}
                  </Box>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
                  <Typography variant="body2">Total:</Typography>
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2">
                      {lineMovement.total.opening} → {lineMovement.total.current}
                    </Typography>
                    {lineMovement.total.opening !== lineMovement.total.current && (
                      lineMovement.total.direction === 'over' ? 
                        <TrendingUp color="success" fontSize="small" sx={{ ml: 1 }} /> :
                        <TrendingDown color="error" fontSize="small" sx={{ ml: 1 }} />
                    )}
                  </Box>
                </Box>
              </Box>
            </Grid>
          </Grid>

          {/* Steam Moves */}
          {steamMoves.length > 0 && (
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Recent Steam Moves
              </Typography>
              {steamMoves.map((move, index) => (
                <Chip 
                  key={index}
                  label={`${move.market.toUpperCase()} ${move.direction.toUpperCase()} - ${move.time}`}
                  variant="outlined"
                  size="small"
                  icon={<Speed />}
                  sx={{ mr: 1, mb: 1 }}
                  color={move.magnitude > 1.0 ? 'error' : 'warning'}
                />
              ))}
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  const OddsComparisonTable = ({ games }) => (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Game</TableCell>
            <TableCell align="center">Moneyline</TableCell>
            <TableCell align="center">Spread</TableCell>
            <TableCell align="center">Total</TableCell>
            <TableCell align="center">Consensus</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {games.map((game) => (
            <TableRow key={game.id} hover>
              <TableCell>
                <Box>
                  <Typography variant="body2" fontWeight="bold">
                    {game.awayTeam} @ {game.homeTeam}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {new Date(game.startTime).toLocaleDateString()} {new Date(game.startTime).toLocaleTimeString()}
                  </Typography>
                </Box>
              </TableCell>
              
              <TableCell align="center">
                <Box>
                  <Typography variant="body2">
                    {game.odds.moneyline.home > 0 ? '+' : ''}{game.odds.moneyline.home} / 
                    {game.odds.moneyline.away > 0 ? '+' : ''}{game.odds.moneyline.away}
                  </Typography>
                </Box>
              </TableCell>
              
              <TableCell align="center">
                <Box>
                  <Typography variant="body2">
                    {game.odds.spread.home > 0 ? '+' : ''}{game.odds.spread.home} ({game.odds.spread.homeOdds})
                  </Typography>
                  <Typography variant="body2">
                    {game.odds.spread.away > 0 ? '+' : ''}{game.odds.spread.away} ({game.odds.spread.awayOdds})
                  </Typography>
                </Box>
              </TableCell>
              
              <TableCell align="center">
                <Box>
                  <Typography variant="body2">
                    O{game.odds.total.line} ({game.odds.total.over})
                  </Typography>
                  <Typography variant="body2">
                    U{game.odds.total.line} ({game.odds.total.under})
                  </Typography>
                </Box>
              </TableCell>
              
              <TableCell align="center">
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    {game.consensus.books} books
                  </Typography>
                  <Typography variant="body2">
                    Spread: {game.consensus.spreadRange.min} to {game.consensus.spreadRange.max}
                  </Typography>
                  <Typography variant="body2">
                    Total: {game.consensus.totalRange.min} to {game.consensus.totalRange.max}
                  </Typography>
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

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
          Live Market Data
        </Typography>
        
        <Box display="flex" alignItems="center" gap={2}>
          {lastUpdate && (
            <Typography variant="body2" color="textSecondary">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </Typography>
          )}
          <IconButton onClick={loadLiveData} disabled={loading}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Tabs value={tabValue} onChange={(e, val) => setTabValue(val)} sx={{ mb: 3 }}>
        <Tab label="Live Odds" />
        <Tab label="Public Betting" />
        <Tab label="Sharp Money" />
      </Tabs>

      {tabValue === 0 && liveData && (
        <OddsComparisonTable games={liveData.games} />
      )}

      {tabValue === 1 && (
        <Box>
          {liveData?.games?.map(game => (
            <PublicBettingCard 
              key={game.id} 
              game={game} 
              publicData={publicBetting} 
            />
          ))}
        </Box>
      )}

      {tabValue === 2 && (
        <Box>
          {liveData?.games?.map(game => (
            <SharpMoneyCard 
              key={game.id} 
              game={game} 
              sharpData={sharpMoney} 
            />
          ))}
        </Box>
      )}
    </Box>
  );
};

export default LiveData;
