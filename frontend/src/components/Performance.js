import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Tab,
  Tabs
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { sportsBettingAPI } from '../services/api';

const Performance = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [bets, setBets] = useState([]);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    loadPerformanceData();
  }, []);

  const loadPerformanceData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [performanceRes, betsRes] = await Promise.all([
        sportsBettingAPI.getPerformance(),
        sportsBettingAPI.getBets('settled', 100)
      ]);

      setPerformance(performanceRes.data);
      setBets(betsRes.data.bets || []);
    } catch (err) {
      setError('Failed to load performance data');
      console.error('Performance error:', err);
    } finally {
      setLoading(false);
    }
  };

  const prepareChartData = () => {
    if (!bets.length) return [];

    let runningBalance = performance?.bankroll?.starting_balance || 1000;
    
    return bets
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      .map((bet, index) => {
        runningBalance += bet.profit_loss || 0;
        return {
          index: index + 1,
          balance: runningBalance,
          profit: bet.profit_loss || 0,
          date: new Date(bet.created_at).toLocaleDateString(),
          betType: bet.bet_type,
          result: bet.result,
          stake: bet.stake
        };
      });
  };

  const prepareBetTypeData = () => {
    if (!bets.length) return [];

    const betTypes = bets.reduce((acc, bet) => {
      const type = bet.bet_type;
      if (!acc[type]) {
        acc[type] = { name: type, wins: 0, losses: 0, total: 0, profit: 0 };
      }
      acc[type].total++;
      acc[type].profit += bet.profit_loss || 0;
      
      if (bet.result === 'win') {
        acc[type].wins++;
      } else if (bet.result === 'loss') {
        acc[type].losses++;
      }
      
      return acc;
    }, {});

    return Object.values(betTypes).map(type => ({
      ...type,
      winRate: type.total > 0 ? (type.wins / type.total * 100).toFixed(1) : 0
    }));
  };

  const prepareResultsData = () => {
    if (!bets.length) return [];

    const results = bets.reduce((acc, bet) => {
      const result = bet.result || 'pending';
      if (!acc[result]) {
        acc[result] = 0;
      }
      acc[result]++;
      return acc;
    }, {});

    const colors = {
      win: '#4caf50',
      loss: '#f44336',
      push: '#ff9800',
      pending: '#9e9e9e'
    };

    return Object.entries(results).map(([result, count]) => ({
      name: result.charAt(0).toUpperCase() + result.slice(1),
      value: count,
      color: colors[result] || '#9e9e9e'
    }));
  };

  const StatCard = ({ title, value, subtitle, color = 'primary' }) => (
    <Card elevation={2}>
      <CardContent sx={{ textAlign: 'center' }}>
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
      </CardContent>
    </Card>
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

  const chartData = prepareChartData();
  const betTypeData = prepareBetTypeData();
  const resultsData = prepareResultsData();

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Performance Analytics
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total ROI"
            value={`${performance?.bankroll?.roi?.toFixed(2) || '0.00'}%`}
            subtitle="Return on Investment"
            color={performance?.bankroll?.roi >= 0 ? 'success.main' : 'error.main'}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Win Rate"
            value={`${performance?.bankroll?.win_rate?.toFixed(1) || '0.0'}%`}
            subtitle={`${performance?.bankroll?.winning_bets || 0}/${performance?.bankroll?.total_bets || 0} bets`}
            color={performance?.bankroll?.win_rate >= 65 ? 'success.main' : 'warning.main'}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Prediction Accuracy"
            value={`${performance?.prediction_accuracy?.accuracy_percentage?.toFixed(1) || '0.0'}%`}
            subtitle="Model Performance"
            color={performance?.prediction_accuracy?.accuracy_percentage >= 65 ? 'success.main' : 'warning.main'}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Bankroll Growth"
            value={`${performance?.bankroll?.bankroll_growth?.toFixed(2) || '0.00'}%`}
            subtitle="Since Start"
            color={performance?.bankroll?.bankroll_growth >= 0 ? 'success.main' : 'error.main'}
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Paper elevation={2} sx={{ p: 2 }}>
        <Tabs value={tabValue} onChange={(e, val) => setTabValue(val)} sx={{ mb: 2 }}>
          <Tab label="Bankroll Growth" />
          <Tab label="Bet Types" />
          <Tab label="Results Distribution" />
        </Tabs>

        {/* Bankroll Growth Chart */}
        {tabValue === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Bankroll Growth Over Time
            </Typography>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'balance' ? `$${value.toFixed(2)}` : value,
                      name === 'balance' ? 'Balance' : 'Profit/Loss'
                    ]}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="balance" 
                    stroke="#1976d2" 
                    fill="#1976d2" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <Typography textAlign="center" color="textSecondary" py={4}>
                No betting history available
              </Typography>
            )}
          </Box>
        )}

        {/* Bet Types Performance */}
        {tabValue === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Performance by Bet Type
            </Typography>
            {betTypeData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={betTypeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'profit' ? `$${value.toFixed(2)}` : 
                      name === 'winRate' ? `${value}%` : value,
                      name === 'profit' ? 'Profit' :
                      name === 'winRate' ? 'Win Rate' :
                      name === 'total' ? 'Total Bets' : name
                    ]}
                  />
                  <Legend />
                  <Bar dataKey="profit" fill="#1976d2" name="Profit" />
                  <Bar dataKey="winRate" fill="#4caf50" name="Win Rate %" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Typography textAlign="center" color="textSecondary" py={4}>
                No bet type data available
              </Typography>
            )}
          </Box>
        )}

        {/* Results Distribution */}
        {tabValue === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Bet Results Distribution
            </Typography>
            {resultsData.length > 0 ? (
              <Box display="flex" justifyContent="center">
                <ResponsiveContainer width={400} height={400}>
                  <PieChart>
                    <Pie
                      data={resultsData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={150}
                      label={({ name, value, percent }) => 
                        `${name}: ${value} (${(percent * 100).toFixed(1)}%)`
                      }
                    >
                      {resultsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            ) : (
              <Typography textAlign="center" color="textSecondary" py={4}>
                No results data available
              </Typography>
            )}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default Performance;
