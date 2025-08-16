import React, { useState, useEffect } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, 
  Button, Chip, LinearProgress, Fade, Zoom,
  Alert, CircularProgress, Divider, List, ListItem,
  ListItemText, ListItemIcon, Paper, Accordion,
  AccordionSummary, AccordionDetails
} from '@mui/material';
import {
  Psychology, AutoGraph, TrendingUp, TrendingDown,
  Speed, LocalFireDepartment, Visibility, ShowChart,
  ExpandMore, CheckCircle, Warning, Info
} from '@mui/icons-material';
import axios from 'axios';

const EnhancedMLDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [featureImportance, setFeatureImportance] = useState({});
  const [dataInsights, setDataInsights] = useState({});

  const loadEnhancedData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get model performance
      const performanceRes = await axios.get('https://apexanalytics-ai.space/api/enhanced/model-performance');
      setModelStatus(performanceRes.data.model_performance);
      
      // Get feature importance
      const importanceRes = await axios.get('https://apexanalytics-ai.space/api/enhanced/feature-importance');
      setFeatureImportance(importanceRes.data);
      
      // Get enhanced predictions
      const predictionsRes = await axios.get('https://apexanalytics-ai.space/api/enhanced/predictions');
      setPredictions(predictionsRes.data.predictions || []);
      
    } catch (err) {
      console.error('Error loading enhanced data:', err);
      setError('Failed to load enhanced ML data. The model may need to be trained first.');
    } finally {
      setLoading(false);
    }
  };

  const trainModel = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await axios.post('https://apexanalytics-ai.space/api/enhanced/train-model');
      await loadEnhancedData(); // Reload data after training
    } catch (err) {
      console.error('Error training model:', err);
      setError('Failed to train the enhanced model.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEnhancedData();
  }, []);

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#39ff14';
    if (confidence >= 0.7) return '#ffff00';
    return '#ff073a';
  };

  const getRiskColor = (risk) => {
    if (risk <= 0.3) return '#39ff14';
    if (risk <= 0.6) return '#ffff00';
    return '#ff073a';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} sx={{ color: '#00d4ff' }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ 
        mb: 3, 
        background: 'var(--primary-gradient)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        fontWeight: 900,
        textAlign: 'center'
      }}>
        🤖 Enhanced AI Prediction Engine
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Model Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Fade in timeout={500}>
            <Card sx={{ 
              background: 'var(--bg-glass)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Psychology sx={{ fontSize: 40, color: '#8a2be2', mr: 2 }} />
                  <Box>
                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                      Model Status
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      {modelStatus?.status || 'Unknown'}
                    </Typography>
                  </Box>
                </Box>
                
                {modelStatus?.status === 'Trained' && (
                  <Box>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1 }}>
                      Model Weights
                    </Typography>
                    {Object.entries(modelStatus.model_weights || {}).map(([model, weight]) => (
                      <Box key={model} display="flex" justifyContent="space-between" mb={0.5}>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          {model.replace('_', ' ').toUpperCase()}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                          {(weight * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        <Grid item xs={12} md={6}>
          <Fade in timeout={700}>
            <Card sx={{ 
              background: 'var(--bg-glass)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <AutoGraph sx={{ fontSize: 40, color: '#39ff14', mr: 2 }} />
                  <Box>
                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                      Model Actions
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      Train and manage the enhanced model
                    </Typography>
                  </Box>
                </Box>
                
                <Button
                  variant="contained"
                  onClick={trainModel}
                  disabled={loading}
                  sx={{
                    background: 'var(--success-gradient)',
                    color: '#000',
                    fontWeight: 700,
                    mb: 2,
                    '&:hover': {
                      background: 'var(--success-gradient)',
                      transform: 'scale(1.05)'
                    }
                  }}
                >
                  {loading ? 'Training...' : 'Train Enhanced Model'}
                </Button>
                
                <Button
                  variant="outlined"
                  onClick={loadEnhancedData}
                  disabled={loading}
                  sx={{
                    color: '#00d4ff',
                    borderColor: '#00d4ff',
                    fontWeight: 600,
                    '&:hover': {
                      borderColor: '#00d4ff',
                      backgroundColor: 'rgba(0, 212, 255, 0.1)'
                    }
                  }}
                >
                  Refresh Data
                </Button>
              </CardContent>
            </Card>
          </Fade>
        </Grid>
      </Grid>

      {/* Enhanced Predictions */}
      {predictions.length > 0 && (
        <Fade in timeout={1000}>
          <Card sx={{ 
            mb: 4,
            background: 'var(--bg-glass)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <CardContent>
              <Typography variant="h5" sx={{ 
                mb: 3, 
                color: 'white', 
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center'
              }}>
                <TrendingUp sx={{ mr: 1, color: '#39ff14' }} />
                Enhanced Predictions
              </Typography>
              
              <Grid container spacing={2}>
                {predictions.slice(0, 6).map((prediction, index) => (
                  <Grid item xs={12} md={6} key={prediction.game_id || index}>
                    <Paper sx={{ 
                      p: 2, 
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                          {prediction.home_team} vs {prediction.away_team}
                        </Typography>
                        <Chip
                          label={prediction.prediction.recommended_bet.toUpperCase()}
                          sx={{
                            background: prediction.prediction.recommended_bet === 'home' ? '#39ff14' : '#ff073a',
                            color: '#000',
                            fontWeight: 700
                          }}
                        />
                      </Box>
                      
                      <Box mb={2}>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1 }}>
                          Confidence: {(prediction.prediction.confidence_score * 100).toFixed(1)}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={prediction.prediction.confidence_score * 100}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            '& .MuiLinearProgress-bar': {
                              background: getConfidenceColor(prediction.prediction.confidence_score)
                            }
                          }}
                        />
                      </Box>
                      
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          Expected Value:
                        </Typography>
                        <Typography variant="body2" sx={{ 
                          color: prediction.prediction.expected_value > 0 ? '#39ff14' : '#ff073a',
                          fontWeight: 700
                        }}>
                          {prediction.prediction.expected_value > 0 ? '+' : ''}
                          {(prediction.prediction.expected_value * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                      
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          Risk Score:
                        </Typography>
                        <Typography variant="body2" sx={{ 
                          color: getRiskColor(prediction.risk_assessment.overall_risk_score),
                          fontWeight: 700
                        }}>
                          {(prediction.risk_assessment.overall_risk_score * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                      
                      {prediction.data_insights.key_factors.length > 0 && (
                        <Box mt={2}>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                            Key Factors:
                          </Typography>
                          {prediction.data_insights.key_factors.slice(0, 2).map((factor, i) => (
                            <Chip
                              key={i}
                              label={factor}
                              size="small"
                              sx={{
                                mr: 0.5,
                                mb: 0.5,
                                background: 'rgba(0, 212, 255, 0.2)',
                                color: '#00d4ff',
                                fontSize: '0.7rem'
                              }}
                            />
                          ))}
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Fade>
      )}

      {/* Feature Importance */}
      {featureImportance.top_features && Object.keys(featureImportance.top_features).length > 0 && (
        <Fade in timeout={1200}>
          <Card sx={{ 
            mb: 4,
            background: 'var(--bg-glass)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <CardContent>
              <Typography variant="h5" sx={{ 
                mb: 3, 
                color: 'white', 
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center'
              }}>
                <ShowChart sx={{ mr: 1, color: '#ff6600' }} />
                Feature Importance Analysis
              </Typography>
              
              <Grid container spacing={2}>
                {Object.entries(featureImportance.top_features).slice(0, 10).map(([feature, importance], index) => (
                  <Grid item xs={12} sm={6} md={4} key={feature}>
                    <Paper sx={{ 
                      p: 2, 
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                      <Typography variant="body2" sx={{ 
                        color: 'white', 
                        fontWeight: 600,
                        mb: 1,
                        textTransform: 'capitalize'
                      }}>
                        {feature.replace(/_/g, ' ')}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={importance * 100}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          '& .MuiLinearProgress-bar': {
                            background: `hsl(${index * 36}, 70%, 60%)`
                          }
                        }}
                      />
                      <Typography variant="body2" sx={{ 
                        color: 'rgba(255, 255, 255, 0.7)', 
                        mt: 0.5,
                        fontSize: '0.8rem'
                      }}>
                        {(importance * 100).toFixed(1)}%
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Fade>
      )}

      {/* Enhanced Features Overview */}
      <Fade in timeout={1400}>
        <Card sx={{ 
          background: 'var(--bg-glass)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <CardContent>
            <Typography variant="h5" sx={{ 
              mb: 3, 
              color: 'white', 
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center'
            }}>
              <LocalFireDepartment sx={{ mr: 1, color: '#ff073a' }} />
              Enhanced AI Features
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Accordion sx={{ background: 'rgba(255, 255, 255, 0.05)' }}>
                  <AccordionSummary expandIcon={<ExpandMore sx={{ color: 'white' }} />}>
                    <Typography sx={{ color: 'white', fontWeight: 600 }}>
                      🤖 Advanced Ensemble Models
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="XGBoost, Random Forest, Neural Networks"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Gradient Boosting & Support Vector Machines"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Weighted Voting System"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                    </List>
                  </AccordionDetails>
                </Accordion>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Accordion sx={{ background: 'rgba(255, 255, 255, 0.05)' }}>
                  <AccordionSummary expandIcon={<ExpandMore sx={{ color: 'white' }} />}>
                    <Typography sx={{ color: 'white', fontWeight: 600 }}>
                      🌐 Comprehensive Data Integration
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Real-time Weather Data"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Social Media Sentiment Analysis"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Injury Reports & Market Data"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                    </List>
                  </AccordionDetails>
                </Accordion>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Accordion sx={{ background: 'rgba(255, 255, 255, 0.05)' }}>
                  <AccordionSummary expandIcon={<ExpandMore sx={{ color: 'white' }} />}>
                    <Typography sx={{ color: 'white', fontWeight: 600 }}>
                      📊 Advanced Risk Assessment
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Multi-factor Risk Scoring"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Weather & Injury Impact Analysis"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Market Sentiment Integration"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                    </List>
                  </AccordionDetails>
                </Accordion>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Accordion sx={{ background: 'rgba(255, 255, 255, 0.05)' }}>
                  <AccordionSummary expandIcon={<ExpandMore sx={{ color: 'white' }} />}>
                    <Typography sx={{ color: 'white', fontWeight: 600 }}>
                      🎯 Intelligent Betting Insights
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Kelly Criterion Optimization"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Expected Value Calculations"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle sx={{ color: '#39ff14' }} /></ListItemIcon>
                        <ListItemText 
                          primary="Real-time Market Intelligence"
                          sx={{ '& .MuiListItemText-primary': { color: 'rgba(255, 255, 255, 0.8)' } }}
                        />
                      </ListItem>
                    </List>
                  </AccordionDetails>
                </Accordion>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Fade>
    </Box>
  );
};

export default EnhancedMLDashboard;
