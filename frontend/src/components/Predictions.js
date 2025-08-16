import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
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
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import {
  TrendingUp,
  SportsSoccer,
  Sports,
  MonetizationOn
} from '@mui/icons-material';
import { sportsBettingAPI } from '../services/api';
import moment from 'moment';

const Predictions = () => {
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [selectedSport, setSelectedSport] = useState('americanfootball_nfl');
  const [minConfidence, setMinConfidence] = useState(65);
  const [betDialogOpen, setBetDialogOpen] = useState(location.state?.action === 'place_bet');
  const [selectedPrediction, setSelectedPrediction] = useState(location.state?.selectedPrediction || null);
  const [betAmount, setBetAmount] = useState('');

  const sports = [
    { value: 'americanfootball_nfl', label: 'NFL' },
    { value: 'basketball_nba', label: 'NBA' },
    { value: 'soccer_epl', label: 'Premier League' }
  ];

  useEffect(() => {
    loadPredictions();
  }, [selectedSport, minConfidence]);

  const loadPredictions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await sportsBettingAPI.getPredictions(selectedSport, minConfidence / 100);
      setPredictions(response.data.predictions || []);
    } catch (err) {
      setError('Failed to load predictions');
      console.error('Predictions error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePlaceBet = async () => {
    if (!selectedPrediction || !betAmount) return;

    try {
      const betData = {
        game_id: selectedPrediction.game.external_id,
        bet_type: selectedPrediction.prediction.bet_type,
        bet_value: selectedPrediction.prediction.predicted_outcome,
        odds: selectedPrediction.game.home_odds || -110, // Default odds
        stake: parseFloat(betAmount),
        predicted_probability: selectedPrediction.prediction.probability,
        confidence_score: selectedPrediction.prediction.confidence_score
      };

      await sportsBettingAPI.placeBet(betData);
      setBetDialogOpen(false);
      setBetAmount('');
      setSelectedPrediction(null);
      
      // Could add success notification here
    } catch (err) {
      console.error('Bet placement error:', err);
      // Could add error notification here
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.7) return 'warning';
    return 'error';
  };

  const getBetTypeIcon = (betType) => {
    switch (betType) {
      case 'moneyline': return <Sports />;
      case 'spread': return <TrendingUp />;
      case 'total': return <SportsSoccer />;
      default: return <Sports />;
    }
  };

  const PredictionCard = ({ prediction }) => {
    const { game, prediction: pred } = prediction;
    const confidenceColor = getConfidenceColor(pred.confidence_score);

    return (
      <Card elevation={2} sx={{ mb: 2 }}>
        <CardContent>
          {/* Game Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              {game.away_team} @ {game.home_team}
            </Typography>
            <Chip 
              label={`${(pred.confidence_score * 100).toFixed(1)}% Confidence`}
              color={confidenceColor}
              icon={getBetTypeIcon(pred.bet_type)}
            />
          </Box>
          
          {/* Game Details */}
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                {moment(game.commence_time).format('MMM DD, YYYY HH:mm')}
              </Typography>
              
              <Box mt={1}>
                <Typography variant="body1">
                  <strong>Prediction:</strong> {pred.bet_type} - {pred.predicted_outcome}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Probability: {(pred.probability * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              {/* Odds Display */}
              <Box mb={1}>
                <Typography variant="body2" color="textSecondary">
                  Current Odds
                </Typography>
                <Box display="flex" gap={1}>
                  {game.home_odds && (
                    <Chip label={`Home: ${game.home_odds > 0 ? '+' : ''}${game.home_odds}`} size="small" />
                  )}
                  {game.away_odds && (
                    <Chip label={`Away: ${game.away_odds > 0 ? '+' : ''}${game.away_odds}`} size="small" />
                  )}
                </Box>
              </Box>
              
              <Button
                variant="contained"
                startIcon={<MonetizationOn />}
                onClick={() => {
                  setSelectedPrediction(prediction);
                  setBetDialogOpen(true);
                }}
                disabled={moment(game.commence_time).isBefore(moment())}
                fullWidth
              >
                Place Bet
              </Button>
            </Grid>
          </Grid>
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
      <Typography variant="h4" component="h1" gutterBottom>
        AI Predictions
      </Typography>

      {/* Controls */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
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
          </Grid>
          
          <Grid item xs={12} sm={6} md={6}>
            <Typography gutterBottom>
              Minimum Confidence: {minConfidence}%
            </Typography>
            <Slider
              value={minConfidence}
              onChange={(e, newValue) => setMinConfidence(newValue)}
              min={50}
              max={95}
              step={5}
              marks
              valueLabelDisplay="auto"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Button
              variant="outlined"
              onClick={loadPredictions}
              fullWidth
            >
              Refresh Predictions
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Predictions List */}
      {predictions.length > 0 ? (
        <Grid container>
          <Grid item xs={12}>
            {predictions.map((prediction, index) => (
              <PredictionCard key={index} prediction={prediction} />
            ))}
          </Grid>
        </Grid>
      ) : (
        <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary">
            No predictions available for the selected criteria
          </Typography>
          <Typography variant="body2" color="textSecondary" mt={1}>
            Try lowering the confidence threshold or selecting a different sport
          </Typography>
        </Paper>
      )}

      {/* Bet Placement Dialog */}
      <Dialog open={betDialogOpen} onClose={() => setBetDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Place Bet</DialogTitle>
        <DialogContent>
          {selectedPrediction && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedPrediction.game.away_team} @ {selectedPrediction.game.home_team}
              </Typography>
              
              <Typography variant="body1" gutterBottom>
                <strong>Bet Type:</strong> {selectedPrediction.prediction.bet_type}
              </Typography>
              
              <Typography variant="body1" gutterBottom>
                <strong>Prediction:</strong> {selectedPrediction.prediction.predicted_outcome}
              </Typography>
              
              <Typography variant="body1" gutterBottom>
                <strong>Confidence:</strong> {(selectedPrediction.prediction.confidence_score * 100).toFixed(1)}%
              </Typography>
              
              <TextField
                label="Bet Amount ($)"
                type="number"
                value={betAmount}
                onChange={(e) => setBetAmount(e.target.value)}
                fullWidth
                margin="normal"
                inputProps={{ min: 1, step: 1 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBetDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handlePlaceBet} 
            variant="contained"
            disabled={!betAmount || parseFloat(betAmount) <= 0}
          >
            Place Bet
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Predictions;
