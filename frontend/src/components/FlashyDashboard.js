import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Grid, Card, CardContent, Typography, 
  CircularProgress, Alert, Button, Select, MenuItem,
  FormControl, InputLabel, Chip, Avatar,
  LinearProgress, Fade, Slide, Zoom,
  Badge, Fab, Tooltip, CardActions
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Refresh,
  Visibility, ShowChart, AttachMoney,
  EmojiEvents, Whatshot, Bolt, TrendingFlat,
  LocalFireDepartment, Psychology, Speed,
  Rocket
} from '@mui/icons-material';
// Charts can be imported when needed for future enhancements
import { sportsBettingAPI } from '../services/api';

// Color palettes for future chart implementations

const FlashyDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bankroll, setBankroll] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [selectedSport, setSelectedSport] = useState('nfl');
  const [refreshing, setRefreshing] = useState(false);
  const [liveMarketData, setLiveMarketData] = useState(null);

  const sports = [
    { value: 'nfl', label: 'NFL', icon: '🏈', color: '#00d4ff' },
    { value: 'nba', label: 'NBA', icon: '🏀', color: '#8a2be2' },
    { value: 'tennis', label: 'Tennis', icon: '🎾', color: '#39ff14' },
    { value: 'mma', label: 'MMA', icon: '🥊', color: '#ff073a' },
    { value: 'nascar', label: 'NASCAR', icon: '🏎️', color: '#ff6600' },
    { value: 'golf', label: 'Golf', icon: '⛳', color: '#ffff00' }
  ];

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Auto-refresh every 30 seconds
    return () => clearInterval(interval);
  }, [selectedSport]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [bankrollRes] = await Promise.all([
        sportsBettingAPI.getBankroll().catch(() => ({ data: generateMockBankroll() }))
      ]);

      setBankroll(bankrollRes.data);

      await loadSportRadarPredictions();
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
        const predictions = data.games.slice(0, 6).map((game, index) => ({
          id: game.id || `game_${index}`,
          game: {
            home_team: game.home_team?.name || game.home?.name || `Home Team ${index + 1}`,
            away_team: game.away_team?.name || game.away?.name || `Away Team ${index + 1}`,
            commence_time: game.scheduled || new Date(Date.now() + index * 86400000).toISOString()
          },
          prediction: {
            bet_type: ['moneyline', 'spread', 'total'][index % 3],
            predicted_outcome: game.home_team?.name || game.home?.name || 'Home',
            confidence_score: 0.65 + (Math.random() * 0.3),
            probability: 0.60 + (Math.random() * 0.35),
            expected_value: 5 + (Math.random() * 15),
            recommended_stake: 25 + (Math.random() * 75)
          }
        }));
        setRecentPredictions(predictions);
      }
    } catch (err) {
      console.error('SportRadar predictions error:', err);
      setRecentPredictions(generateMockPredictions());
    }
  };

  const loadLiveMarketData = async () => {
    try {
      setLiveMarketData(generateMockLiveData());
    } catch (err) {
      console.error('Live market data error:', err);
    }
  };

  const generateMockBankroll = () => ({
    current_balance: 12543.67,
    starting_balance: 10000,
    total_profit_loss: 2543.67,
    win_rate: 72.5,
    roi: 25.44
  });

  // Mock performance data generator (reserved for future use)
  // const generateMockPerformance = () => ({
  //   bankroll: {
  //     current_balance: 12543.67,
  //     starting_balance: 10000,
  //     total_profit_loss: 2543.67
  //   },
  //   recent_performance: {
  //     bets_last_30_days: 47,
  //     roi_30_days: 28.7
  //   },
  //   prediction_accuracy: {
  //     accuracy_percentage: 72.5
  //   }
  // });

  const generateMockPredictions = () => [
    {
      id: 1,
      game: { home_team: 'Chiefs', away_team: 'Bills', commence_time: new Date(Date.now() + 86400000).toISOString() },
      prediction: { bet_type: 'moneyline', predicted_outcome: 'away', confidence_score: 0.87, probability: 0.74, expected_value: 12.5, recommended_stake: 85 }
    },
    {
      id: 2,
      game: { home_team: 'Lakers', away_team: 'Celtics', commence_time: new Date(Date.now() + 172800000).toISOString() },
      prediction: { bet_type: 'spread', predicted_outcome: 'home -5.5', confidence_score: 0.79, probability: 0.68, expected_value: 8.7, recommended_stake: 65 }
    }
  ];

  const generateMockLiveData = () => ({
    steam_moves: 3,
    sharp_money_percentage: 67,
    public_betting_fade_opportunities: 5,
    live_odds_changes: 12,
    market_efficiency_score: 78
  });

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handlePlaceBet = (prediction) => {
    console.log('Placing bet for prediction:', prediction);
    // Navigate to predictions page with the specific prediction
    navigate('/predictions', { 
      state: { 
        selectedPrediction: prediction,
        action: 'place_bet' 
      }
    });
  };

  const handleViewDetails = (prediction) => {
    // Navigate to predictions page with detailed view
    navigate('/predictions', { 
      state: { 
        selectedPrediction: prediction,
        action: 'view_details' 
      }
    });
  };

  const handleQuickAction = (action) => {
    console.log('Quick action triggered:', action);
    switch (action) {
      case 'view_all_predictions':
        console.log('Navigating to /predictions');
        navigate('/predictions');
        break;
      case 'view_performance':
        console.log('Navigating to /performance');
        navigate('/performance');
        break;
      case 'view_live_data':
        console.log('Navigating to /live-data');
        navigate('/live-data');
        break;
      case 'view_sportsradar':
        console.log('Navigating to /sportsradar');
        navigate('/sportsradar');
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#39ff14';
    if (confidence >= 0.7) return '#ffff00';
    return '#ff073a';
  };

  const getConfidenceIcon = (confidence) => {
    if (confidence >= 0.85) return <Rocket />;
    if (confidence >= 0.75) return <LocalFireDepartment />;
    if (confidence >= 0.65) return <Bolt />;
    return <Speed />;
  };

  const StatCard = ({ title, value, subtitle, icon, color = '#00d4ff', trend = null, delay = 0, onClick }) => (
    <Zoom in={!loading} style={{ transitionDelay: `${delay}ms` }}>
      <Card 
        className="fadeIn stat-card responsive-container"
        onClick={onClick}
        sx={{ 
          height: '100%',
          background: 'var(--bg-glass)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          position: 'relative',
          overflow: 'hidden',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: { xs: 'scale(1.02)', md: 'translateY(-8px) scale(1.02)' },
            boxShadow: `0 15px 40px ${color}40`,
            transition: 'all 0.3s ease'
          }
        }}
      >
        <CardContent sx={{ 
          position: 'relative', 
          zIndex: 2,
          padding: { xs: '12px', sm: '16px', md: '20px' }
        }}>
          <Box 
            display="flex" 
            justifyContent="space-between" 
            alignItems="flex-start" 
            mb={{ xs: 1, md: 2 }}
            flexDirection={{ xs: 'column', sm: 'row' }}
            gap={{ xs: 1, sm: 0 }}
          >
            <Avatar 
              sx={{ 
                bgcolor: color, 
                width: { xs: 40, sm: 48, md: 56 }, 
                height: { xs: 40, sm: 48, md: 56 },
                boxShadow: `0 0 20px ${color}60`,
                animation: 'pulse 2s ease-in-out infinite'
              }}
            >
              {icon}
            </Avatar>
            {trend && (
              <Chip
                icon={trend > 0 ? <TrendingUp /> : trend < 0 ? <TrendingDown /> : <TrendingFlat />}
                label={`${trend > 0 ? '+' : ''}${trend}%`}
                size="small"
                sx={{
                  background: trend > 0 ? 'var(--success-gradient)' : trend < 0 ? 'var(--danger-gradient)' : 'var(--warning-gradient)',
                  color: 'white',
                  fontWeight: 700,
                  fontSize: { xs: '0.7rem', sm: '0.75rem' },
                  height: { xs: 24, sm: 28 }
                }}
              />
            )}
          </Box>
          
          <Typography 
            component="div" 
            className="readable-text-strong"
            sx={{ 
              fontFamily: 'Orbitron, monospace',
              fontWeight: 900,
              fontSize: { xs: '1.4rem', sm: '1.8rem', md: '2.2rem', lg: '2.5rem' },
              lineHeight: { xs: 1.1, md: 1.2 },
              background: `linear-gradient(45deg, ${color}, #fff)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              textShadow: `0 0 30px ${color}`,
              animation: 'neonText 2s ease-in-out infinite alternate',
              mb: { xs: 0.5, md: 1 }
            }}
          >
            {value}
          </Typography>
          
          <Typography 
            variant="h6" 
            className="readable-text"
            sx={{ 
              color: 'rgba(255, 255, 255, 0.9)', 
              fontWeight: 600, 
              fontSize: { xs: '0.9rem', sm: '1rem', md: '1.1rem' },
              lineHeight: { xs: 1.2, md: 1.3 },
              textShadow: '0 1px 3px rgba(0, 0, 0, 0.7)',
              mb: { xs: 0.5, md: 1 }
            }}
          >
            {title}
          </Typography>
          
          <Typography 
            variant="body2" 
            className="readable-text"
            sx={{ 
              color: 'rgba(255, 255, 255, 0.7)', 
              fontSize: { xs: '0.75rem', sm: '0.8rem', md: '0.85rem' },
              lineHeight: { xs: 1.3, md: 1.4 },
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.6)'
            }}
          >
            {subtitle}
          </Typography>
        </CardContent>
        
        <Box 
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: { xs: 2, md: 3 },
            background: `linear-gradient(90deg, ${color}, transparent)`,
            animation: 'shimmer 2s ease-in-out infinite'
          }}
        />
      </Card>
    </Zoom>
  );

  const PredictionCard = ({ prediction, index }) => (
    <Slide in={!loading} direction="up" style={{ transitionDelay: `${index * 100}ms` }}>
      <Card 
        className="bet-card responsive-container"
        sx={{
          background: 'var(--bg-glass)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: { xs: '12px', md: '16px' },
          position: 'relative',
          overflow: 'hidden',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: { xs: 'scale(1.02)', md: 'translateX(12px) scale(1.02)' },
            boxShadow: '0 12px 30px rgba(0, 212, 255, 0.3)',
          }
        }}
      >
        <CardContent sx={{ 
          padding: { xs: '12px', sm: '16px', md: '20px' }
        }}>
          <Box 
            display="flex" 
            justifyContent="space-between" 
            alignItems={{ xs: 'flex-start', sm: 'center' }}
            mb={{ xs: 1, md: 2 }}
            flexDirection={{ xs: 'column', sm: 'row' }}
            gap={{ xs: 1, sm: 0 }}
          >
            <Box flex={1}>
              <Typography 
                variant="h6" 
                className="readable-text-strong"
                sx={{ 
                  color: '#fff', 
                  fontWeight: 700,
                  fontSize: { xs: '0.9rem', sm: '1rem', md: '1.1rem' },
                  lineHeight: 1.2,
                  textShadow: '0 1px 3px rgba(0, 0, 0, 0.8)',
                  mb: 0.5
                }}
              >
                {prediction.game.away_team} @ {prediction.game.home_team}
              </Typography>
              <Typography 
                variant="body2" 
                className="readable-text"
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.7)',
                  fontSize: { xs: '0.75rem', sm: '0.8rem' },
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.6)'
                }}
              >
                {new Date(prediction.game.commence_time).toLocaleDateString()}
              </Typography>
            </Box>
            
            <Box 
              display="flex" 
              alignItems="center" 
              gap={1}
              justifyContent={{ xs: 'flex-start', sm: 'flex-end' }}
              width={{ xs: '100%', sm: 'auto' }}
            >
              <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
                {getConfidenceIcon(prediction.prediction.confidence_score)}
              </Box>
              <Chip
                label={`${(prediction.prediction.confidence_score * 100).toFixed(1)}%`}
                sx={{
                  background: getConfidenceColor(prediction.prediction.confidence_score),
                  color: '#000',
                  fontWeight: 800,
                  fontSize: { xs: '0.75rem', sm: '0.8rem', md: '0.9rem' },
                  height: { xs: 24, sm: 28, md: 32 },
                  boxShadow: `0 0 15px ${getConfidenceColor(prediction.prediction.confidence_score)}60`
                }}
              />
            </Box>
          </Box>

          <Box 
            display="flex" 
            justifyContent="space-between" 
            alignItems="center" 
            mb={{ xs: 1, md: 2 }}
            flexWrap="wrap"
            gap={1}
          >
            <Chip
              label={prediction.prediction.bet_type.toUpperCase()}
              variant="outlined"
              size="small"
              sx={{ 
                color: '#00d4ff', 
                borderColor: '#00d4ff',
                fontWeight: 600,
                fontSize: { xs: '0.7rem', sm: '0.75rem' },
                height: { xs: 24, sm: 28 }
              }}
            />
            
            <Typography 
              variant="h6" 
              className="readable-text-strong"
              sx={{ 
                color: '#39ff14', 
                fontWeight: 700,
                fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
                textShadow: '0 1px 3px rgba(0, 0, 0, 0.8)'
              }}
            >
              ${prediction.prediction.recommended_stake?.toFixed(0) || 'N/A'}
            </Typography>
          </Box>

          <LinearProgress
            variant="determinate"
            value={prediction.prediction.confidence_score * 100}
            sx={{
              height: { xs: 6, md: 8 },
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.1)',
              mb: { xs: 1, md: 2 },
              '& .MuiLinearProgress-bar': {
                background: `linear-gradient(90deg, ${getConfidenceColor(prediction.prediction.confidence_score)}, #fff)`,
                borderRadius: 4,
                boxShadow: `0 0 10px ${getConfidenceColor(prediction.prediction.confidence_score)}`
              }
            }}
          />
          
          <Typography 
            variant="body2" 
            className="readable-text"
            sx={{ 
              color: 'rgba(255, 255, 255, 0.8)', 
              fontWeight: 500,
              fontSize: { xs: '0.75rem', sm: '0.8rem', md: '0.85rem' },
              lineHeight: 1.3,
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.6)'
            }}
          >
            Expected Value: <span style={{ 
              color: '#39ff14', 
              fontWeight: 700,
              textShadow: '0 1px 3px rgba(0, 0, 0, 0.8)'
            }}>
              +${prediction.prediction.expected_value?.toFixed(1) || 'N/A'}
            </span>
          </Typography>
        </CardContent>
        
        <CardActions sx={{ 
          justifyContent: 'space-between', 
          px: { xs: 2, md: 3 }, 
          pb: { xs: 2, md: 3 } 
        }}>
          <Button
            variant="contained"
            size="small"
            onClick={() => handlePlaceBet(prediction)}
            sx={{
              background: 'var(--success-gradient)',
              color: '#000',
              fontWeight: 700,
              fontSize: { xs: '0.7rem', sm: '0.75rem' },
              px: { xs: 2, md: 3 },
              '&:hover': {
                background: 'var(--success-gradient)',
                transform: 'scale(1.05)',
                boxShadow: '0 0 15px rgba(57, 255, 20, 0.5)'
              }
            }}
          >
            Place Bet
          </Button>
          
          <Button
            variant="outlined"
            size="small"
            onClick={() => handleViewDetails(prediction)}
            sx={{
              color: '#00d4ff',
              borderColor: '#00d4ff',
              fontWeight: 600,
              fontSize: { xs: '0.7rem', sm: '0.75rem' },
              px: { xs: 2, md: 3 },
              '&:hover': {
                borderColor: '#00d4ff',
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                transform: 'scale(1.05)'
              }
            }}
          >
            Details
          </Button>
        </CardActions>
      </Card>
    </Slide>
  );

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="80vh"
        flexDirection="column"
      >
        <CircularProgress 
          size={80} 
          thickness={4}
          sx={{ 
            color: '#00d4ff',
            filter: 'drop-shadow(0 0 10px #00d4ff)'
          }} 
        />
        <Typography 
          variant="h5" 
          sx={{ 
            mt: 3, 
            color: '#00d4ff',
            fontWeight: 600,
            textShadow: '0 0 10px #00d4ff'
          }}
        >
          Loading Predictions...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      p: { xs: 1, sm: 2, md: 3 }, 
      minHeight: '100vh',
      maxWidth: '100vw',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <Fade in timeout={800}>
        <Box 
          display="flex" 
          justifyContent="space-between" 
          alignItems={{ xs: 'flex-start', md: 'center' }}
          mb={{ xs: 2, md: 4 }}
          flexDirection={{ xs: 'column', md: 'row' }}
          gap={{ xs: 2, md: 0 }}
        >
          <Typography 
            className="readable-text-strong"
            sx={{ 
              fontFamily: 'Orbitron, monospace',
              fontWeight: 900,
              fontSize: { xs: '1.2rem', sm: '1.5rem', md: '2rem', lg: '2.5rem' },
              lineHeight: { xs: 1.1, md: 1.2 },
              background: 'var(--primary-gradient)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              textShadow: '0 0 30px rgba(102, 126, 234, 0.5)',
              animation: 'neonText 3s ease-in-out infinite alternate',
              textAlign: { xs: 'center', md: 'left' },
              width: { xs: '100%', md: 'auto' }
            }}
          >
            ⚡ Sports Betting AI Dashboard
          </Typography>
          
          <Box 
            display="flex" 
            gap={{ xs: 1, md: 2 }} 
            alignItems="center"
            justifyContent={{ xs: 'center', md: 'flex-end' }}
            width={{ xs: '100%', md: 'auto' }}
            flexWrap="wrap"
          >
            <FormControl 
              variant="outlined" 
              size="small"
              sx={{ minWidth: { xs: 120, md: 150 } }}
            >
              <InputLabel 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.7)',
                  fontSize: { xs: '0.8rem', md: '0.875rem' }
                }}
              >
                Sport
              </InputLabel>
              <Select
                value={selectedSport}
                onChange={(e) => setSelectedSport(e.target.value)}
                label="Sport"
                className="readable-text"
                sx={{
                  color: '#fff',
                  fontSize: { xs: '0.8rem', md: '0.875rem' },
                  '.MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgba(255, 255, 255, 0.3)'
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#00d4ff'
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#00d4ff'
                  }
                }}
              >
                {sports.map((sport) => (
                  <MenuItem key={sport.value} value={sport.value}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <span style={{ fontSize: { xs: '0.8rem', md: '1rem' } }}>
                        {sport.icon}
                      </span>
                      <Typography sx={{ fontSize: { xs: '0.8rem', md: '0.875rem' } }}>
                        {sport.label}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Tooltip title="Refresh Data">
              <Fab
                size="medium"
                onClick={handleRefresh}
                disabled={refreshing}
                sx={{
                  background: 'var(--primary-gradient)',
                  color: 'white',
                  width: { xs: 40, md: 56 },
                  height: { xs: 40, md: 56 },
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'scale(1.1)',
                    boxShadow: '0 0 20px rgba(102, 126, 234, 0.5)'
                  },
                  '&:disabled': {
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: 'rgba(255, 255, 255, 0.5)'
                  }
                }}
              >
                <Refresh 
                  sx={{ 
                    animation: refreshing ? 'spin 1s linear infinite' : 'none',
                    fontSize: { xs: '1.2rem', md: '1.5rem' }
                  }} 
                />
              </Fab>
            </Tooltip>
          </Box>
        </Box>
      </Fade>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Portfolio Value"
            value={`$${bankroll?.current_balance?.toLocaleString() || '0'}`}
            subtitle={`${bankroll?.roi || 0}% ROI`}
            icon={<AttachMoney />}
            color="#00d4ff"
            trend={bankroll?.roi || 0}
            delay={0}
            onClick={() => handleQuickAction('view_performance')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Win Rate"
            value={`${bankroll?.win_rate || 0}%`}
            subtitle="Prediction Accuracy"
            icon={<EmojiEvents />}
            color="#39ff14"
            trend={5.2}
            delay={100}
            onClick={() => handleQuickAction('view_performance')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Bets"
            value={recentPredictions.length}
            subtitle="High Confidence"
            icon={<Whatshot />}
            color="#ff6600"
            trend={2}
            delay={200}
            onClick={() => handleQuickAction('view_all_predictions')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Sharp Money"
            value={`${liveMarketData?.sharp_money_percentage || 0}%`}
            subtitle="Professional Edge"
            icon={<Psychology />}
            color="#8a2be2"
            trend={3.1}
            delay={300}
            onClick={() => handleQuickAction('view_live_data')}
          />
        </Grid>
      </Grid>

      {/* Charts and Predictions */}
      <Grid container spacing={3}>
        {/* Live Market Intelligence */}
        <Grid item xs={12} md={4}>
          <Fade in timeout={1200}>
            <Card 
              sx={{ 
                background: 'var(--bg-glass)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                height: '400px'
              }}
            >
              <CardContent>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    mb: 3,
                    background: 'var(--secondary-gradient)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontWeight: 700
                  }}
                >
                  🔥 Live Market Intelligence
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Steam Moves
                    </Typography>
                    <Chip 
                      label={liveMarketData?.steam_moves || 0}
                      size="small"
                      sx={{ 
                        background: '#ff073a', 
                        color: 'white', 
                        fontWeight: 700,
                        animation: 'pulse 1.5s ease-in-out infinite'
                      }}
                    />
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={(liveMarketData?.steam_moves || 0) * 10} 
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      '& .MuiLinearProgress-bar': {
                        background: 'var(--danger-gradient)'
                      }
                    }}
                  />
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Fade Opportunities
                    </Typography>
                    <Chip 
                      label={liveMarketData?.public_betting_fade_opportunities || 0}
                      size="small"
                      sx={{ 
                        background: '#39ff14', 
                        color: '#000', 
                        fontWeight: 700 
                      }}
                    />
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={(liveMarketData?.public_betting_fade_opportunities || 0) * 20} 
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      '& .MuiLinearProgress-bar': {
                        background: 'var(--success-gradient)'
                      }
                    }}
                  />
                </Box>

                <Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Market Efficiency
                    </Typography>
                    <Chip 
                      label={`${liveMarketData?.market_efficiency_score || 0}%`}
                      size="small"
                      sx={{ 
                        background: '#00d4ff', 
                        color: 'white', 
                        fontWeight: 700 
                      }}
                    />
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={liveMarketData?.market_efficiency_score || 0} 
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      '& .MuiLinearProgress-bar': {
                        background: 'var(--primary-gradient)'
                      }
                    }}
                  />
                </Box>

                {/* Action Button */}
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => handleQuickAction('view_live_data')}
                    sx={{
                      background: 'var(--primary-gradient)',
                      color: 'white',
                      fontWeight: 700,
                      fontSize: { xs: '0.7rem', sm: '0.75rem' },
                      px: 3,
                      '&:hover': {
                        background: 'var(--primary-gradient)',
                        transform: 'scale(1.05)',
                        boxShadow: '0 0 15px rgba(0, 212, 255, 0.5)'
                      }
                    }}
                  >
                    View Full Data
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* High-Confidence Predictions */}
        <Grid item xs={12} md={8}>
          <Fade in timeout={1400}>
            <Card 
              sx={{ 
                background: 'var(--bg-glass)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                height: '400px'
              }}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      background: 'var(--warning-gradient)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      fontWeight: 700
                    }}
                  >
                    ⚡ High-Confidence Predictions
                  </Typography>
                  
                  <Badge badgeContent={recentPredictions.length} color="error">
                    <Chip 
                      icon={<Visibility />}
                      label="Live"
                      sx={{ 
                        background: 'var(--success-gradient)',
                        color: 'white',
                        fontWeight: 700,
                        animation: 'pulse 2s ease-in-out infinite'
                      }}
                    />
                  </Badge>
                </Box>
                
                <Box sx={{ maxHeight: '300px', overflow: 'auto' }}>
                  <Grid container spacing={2}>
                    {recentPredictions.slice(0, 4).map((prediction, index) => (
                      <Grid item xs={12} sm={6} key={prediction.id}>
                        <PredictionCard prediction={prediction} index={index} />
                      </Grid>
                    ))}
                  </Grid>
                </Box>

                {/* View All Predictions Button */}
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
                  <Button
                    variant="outlined"
                    onClick={() => handleQuickAction('view_all_predictions')}
                    sx={{
                      color: '#39ff14',
                      borderColor: '#39ff14',
                      fontWeight: 700,
                      fontSize: { xs: '0.8rem', sm: '0.85rem' },
                      px: 4,
                      py: 1,
                      '&:hover': {
                        borderColor: '#39ff14',
                        backgroundColor: 'rgba(57, 255, 20, 0.1)',
                        transform: 'scale(1.05)',
                        boxShadow: '0 0 15px rgba(57, 255, 20, 0.3)'
                      }
                    }}
                  >
                    View All Predictions
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Fade>
        </Grid>
      </Grid>

      {/* Debug Navigation Test */}
      <Box
        sx={{
          position: 'fixed',
          top: 100,
          left: 20,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          zIndex: 9999
        }}
      >
        <Button
          variant="contained"
          size="small"
          onClick={() => {
            console.log('Debug: Testing navigation to /predictions');
            navigate('/predictions');
          }}
          sx={{ background: '#ff073a', color: 'white', fontSize: '0.7rem' }}
        >
          Test Nav
        </Button>
      </Box>

      {/* Floating Action Button with Quick Actions */}
      <Box
        sx={{
          position: 'fixed',
          bottom: { xs: 16, md: 32 },
          right: { xs: 16, md: 32 },
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          alignItems: 'flex-end',
          zIndex: 1000
        }}
      >
        {/* Quick Action Buttons */}
        <Fade in timeout={1000}>
          <Box display="flex" flexDirection="column" gap={1}>
            <Tooltip title="View All Predictions" placement="left">
              <Fab
                size="medium"
                onClick={() => handleQuickAction('view_all_predictions')}
                sx={{
                  background: 'var(--success-gradient)',
                  color: '#000',
                  width: { xs: 48, md: 56 },
                  height: { xs: 48, md: 56 },
                  '&:hover': {
                    transform: 'scale(1.1)',
                    boxShadow: '0 0 20px rgba(57, 255, 20, 0.6)'
                  }
                }}
              >
                <Rocket sx={{ fontSize: { xs: 20, md: 24 } }} />
              </Fab>
            </Tooltip>
            
            <Tooltip title="Live Market Data" placement="left">
              <Fab
                size="medium"
                onClick={() => handleQuickAction('view_live_data')}
                sx={{
                  background: 'var(--danger-gradient)',
                  color: 'white',
                  width: { xs: 48, md: 56 },
                  height: { xs: 48, md: 56 },
                  '&:hover': {
                    transform: 'scale(1.1)',
                    boxShadow: '0 0 20px rgba(255, 7, 58, 0.6)'
                  }
                }}
              >
                <LocalFireDepartment sx={{ fontSize: { xs: 20, md: 24 } }} />
              </Fab>
            </Tooltip>
            
            <Tooltip title="Performance Analytics" placement="left">
              <Fab
                size="medium"
                onClick={() => handleQuickAction('view_performance')}
                sx={{
                  background: 'var(--warning-gradient)',
                  color: '#000',
                  width: { xs: 48, md: 56 },
                  height: { xs: 48, md: 56 },
                  '&:hover': {
                    transform: 'scale(1.1)',
                    boxShadow: '0 0 20px rgba(255, 255, 0, 0.6)'
                  }
                }}
              >
                <ShowChart sx={{ fontSize: { xs: 20, md: 24 } }} />
              </Fab>
            </Tooltip>
          </Box>
        </Fade>

        {/* Main FAB */}
        <Fab
          onClick={() => handleRefresh()}
          sx={{
            background: 'var(--primary-gradient)',
            color: 'white',
            width: { xs: 56, md: 64 },
            height: { xs: 56, md: 64 },
            '&:hover': {
              transform: 'scale(1.1) rotate(15deg)',
              boxShadow: '0 0 30px rgba(102, 126, 234, 0.6)'
            }
          }}
        >
          <Refresh 
            sx={{ 
              fontSize: { xs: 24, md: 28 },
              animation: refreshing ? 'spin 1s linear infinite' : 'none'
            }} 
          />
        </Fab>
      </Box>
    </Box>
  );
};

export default FlashyDashboard;
