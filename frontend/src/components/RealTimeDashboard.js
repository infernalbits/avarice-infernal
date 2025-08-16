import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Chip, 
  IconButton, Switch, FormControlLabel, Alert,
  LinearProgress, Tooltip, Badge, Tab, Tabs
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Notifications, 
  NotificationsOff, Refresh, Speed, Warning,
  ShowChart, AccountBalance, Timeline
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, 
         Tooltip as RechartsTooltip, ResponsiveContainer,
         AreaChart, Area, PieChart, Pie, Cell } from 'recharts';
import io from 'socket.io-client';

const RealTimeDashboard = () => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [liveData, setLiveData] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [subscriptions, setSubscriptions] = useState({
    odds: false,
    games: false,
    predictions: false
  });
  const [selectedTab, setSelectedTab] = useState(0);
  const [realtimeMetrics, setRealtimeMetrics] = useState({
    totalValue: 0,
    activeOpportunities: 0,
    averageConfidence: 0,
    riskLevel: 'medium'
  });

  const socketRef = useRef(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = io('http://localhost:5001', {
      transports: ['websocket'],
      timeout: 20000,
    });

    newSocket.on('connect', () => {
      console.log('Connected to real-time server');
      setConnected(true);
      setSocket(newSocket);
      socketRef.current = newSocket;
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from real-time server');
      setConnected(false);
    });

    newSocket.on('connected', (data) => {
      console.log('Server confirmation:', data);
    });

    // Real-time data handlers
    newSocket.on('live_odds_update', handleOddsUpdate);
    newSocket.on('game_updates', handleGameUpdates);
    newSocket.on('prediction_alert', handlePredictionAlert);
    newSocket.on('market_alert', handleMarketAlert);
    newSocket.on('system_alert', handleSystemAlert);

    return () => {
      newSocket.close();
    };
  }, []);

  const handleOddsUpdate = (data) => {
    setLiveData(prev => ({
      ...prev,
      odds: data
    }));
    
    updateRealtimeMetrics(data);
  };

  const handleGameUpdates = (data) => {
    setLiveData(prev => ({
      ...prev,
      games: data
    }));
  };

  const handlePredictionAlert = (data) => {
    const newNotification = {
      id: Date.now(),
      type: 'prediction',
      level: data.alert_level,
      message: `New ${data.alert_level} confidence prediction available`,
      data: data,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setNotifications(prev => [newNotification, ...prev.slice(0, 19)]); // Keep last 20
    
    // Update metrics
    setRealtimeMetrics(prev => ({
      ...prev,
      activeOpportunities: prev.activeOpportunities + data.predictions.length,
      averageConfidence: calculateAverageConfidence(data.predictions)
    }));
  };

  const handleMarketAlert = (data) => {
    const newNotification = {
      id: Date.now(),
      type: 'market',
      level: 'high',
      message: 'Market movement detected',
      data: data,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setNotifications(prev => [newNotification, ...prev.slice(0, 19)]);
  };

  const handleSystemAlert = (data) => {
    const newNotification = {
      id: Date.now(),
      type: 'system',
      level: data.type === 'error' ? 'high' : 'medium',
      message: data.message,
      data: data,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setNotifications(prev => [newNotification, ...prev.slice(0, 19)]);
  };

  const calculateAverageConfidence = (predictions) => {
    if (!predictions || predictions.length === 0) return 0;
    const sum = predictions.reduce((acc, pred) => 
      acc + (pred.prediction?.confidence_score || 0), 0);
    return sum / predictions.length;
  };

  const updateRealtimeMetrics = (oddsData) => {
    // Update real-time metrics based on odds data
    const opportunities = oddsData.data?.odds?.length || 0;
    const totalValue = opportunities * 150; // Mock calculation
    
    setRealtimeMetrics(prev => ({
      ...prev,
      totalValue,
      activeOpportunities: opportunities
    }));
  };

  const toggleSubscription = (type) => {
    if (!socket) return;

    const newState = !subscriptions[type];
    
    if (newState) {
      // Subscribe
      socket.emit(`subscribe_${type}`, { sport: 'nfl' });
    } else {
      // Unsubscribe
      socket.emit('unsubscribe', { type, sport: 'nfl' });
    }
    
    setSubscriptions(prev => ({
      ...prev,
      [type]: newState
    }));
  };

  const getNotificationColor = (level) => {
    switch (level) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      default: return 'info';
    }
  };

  const MetricCard = ({ title, value, subtitle, icon, color = 'primary', trend = null }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {value}
              {trend && (
                <Box component="span" sx={{ ml: 1 }}>
                  {trend > 0 ? (
                    <TrendingUp color="success" fontSize="small" />
                  ) : (
                    <TrendingDown color="error" fontSize="small" />
                  )}
                </Box>
              )}
            </Typography>
            <Typography color="textSecondary">
              {subtitle}
            </Typography>
          </Box>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const LiveOddsPanel = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Live Odds Monitor
        </Typography>
        
        {liveData.odds ? (
          <Box>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Last Update: {new Date(liveData.odds.timestamp).toLocaleTimeString()}
            </Typography>
            
            {liveData.odds.data?.odds?.slice(0, 5).map((game, index) => (
              <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  {game.awayTeam} @ {game.homeTeam}
                </Typography>
                
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={4}>
                    <Typography variant="body2">Moneyline</Typography>
                    <Typography variant="body1">
                      {game.odds?.moneyline?.home} / {game.odds?.moneyline?.away}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">Spread</Typography>
                    <Typography variant="body1">
                      {game.odds?.spread?.home} ({game.odds?.spread?.homeOdds})
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">Total</Typography>
                    <Typography variant="body1">
                      O/U {game.odds?.total?.line}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            ))}
          </Box>
        ) : (
          <Typography color="textSecondary">
            No live odds data available. Enable live odds subscription to see updates.
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  const NotificationsPanel = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Live Notifications
          </Typography>
          <Badge badgeContent={notifications.length} color="error">
            <Notifications />
          </Badge>
        </Box>
        
        <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
          {notifications.length > 0 ? (
            notifications.map((notification) => (
              <Alert 
                key={notification.id}
                severity={getNotificationColor(notification.level)}
                sx={{ mb: 1 }}
                action={
                  <Typography variant="caption">
                    {notification.timestamp}
                  </Typography>
                }
              >
                <Typography variant="body2">
                  {notification.message}
                </Typography>
              </Alert>
            ))
          ) : (
            <Typography color="textSecondary">
              No recent notifications
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );

  const SubscriptionControls = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Real-Time Subscriptions
        </Typography>
        
        <Box display="flex" alignItems="center" mb={1}>
          <Box 
            sx={{ 
              width: 12, 
              height: 12, 
              borderRadius: '50%', 
              bgcolor: connected ? 'success.main' : 'error.main',
              mr: 1 
            }} 
          />
          <Typography variant="body2">
            {connected ? 'Connected' : 'Disconnected'}
          </Typography>
        </Box>
        
        <Box sx={{ mt: 2 }}>
          <FormControlLabel
            control={
              <Switch 
                checked={subscriptions.odds}
                onChange={() => toggleSubscription('live_odds')}
                disabled={!connected}
              />
            }
            label="Live Odds Updates"
          />
          
          <FormControlLabel
            control={
              <Switch 
                checked={subscriptions.games}
                onChange={() => toggleSubscription('game_updates')}
                disabled={!connected}
              />
            }
            label="Game Status Updates"
          />
          
          <FormControlLabel
            control={
              <Switch 
                checked={subscriptions.predictions}
                onChange={() => toggleSubscription('predictions')}
                disabled={!connected}
              />
            }
            label="Prediction Alerts"
          />
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Real-Time Dashboard
        </Typography>
        
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={() => window.location.reload()}>
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <Chip 
            icon={<Speed />}
            label={connected ? 'Live' : 'Offline'}
            color={connected ? 'success' : 'error'}
            variant="outlined"
          />
        </Box>
      </Box>

      {/* Real-Time Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Portfolio Value"
            value={`$${realtimeMetrics.totalValue.toLocaleString()}`}
            subtitle="Total exposure"
            icon={<AccountBalance />}
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Live Opportunities"
            value={realtimeMetrics.activeOpportunities}
            subtitle="Active betting opportunities"
            icon={<TrendingUp />}
            color="success"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg. Confidence"
            value={`${(realtimeMetrics.averageConfidence * 100).toFixed(1)}%`}
            subtitle="Prediction confidence"
            icon={<ShowChart />}
            color="info"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Risk Level"
            value={realtimeMetrics.riskLevel.toUpperCase()}
            subtitle="Current risk setting"
            icon={<Warning />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Subscription Controls */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <SubscriptionControls />
        </Grid>
      </Grid>

      {/* Main Content Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={selectedTab} 
            onChange={(e, newValue) => setSelectedTab(newValue)}
          >
            <Tab label="Live Odds" />
            <Tab label="Notifications" />
            <Tab label="Market Analysis" />
          </Tabs>
        </Box>
        
        <CardContent>
          {selectedTab === 0 && <LiveOddsPanel />}
          {selectedTab === 1 && <NotificationsPanel />}
          {selectedTab === 2 && (
            <Typography>
              Market Analysis Panel - Coming Soon
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default RealTimeDashboard;
