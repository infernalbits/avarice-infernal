import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TablePagination
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Schedule,
  Remove
} from '@mui/icons-material';
import { sportsBettingAPI } from '../services/api';
import moment from 'moment';

const BettingHistory = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bets, setBets] = useState([]);
  const [filteredBets, setFilteredBets] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  useEffect(() => {
    loadBettingHistory();
  }, []);

  useEffect(() => {
    filterBets();
  }, [bets, statusFilter]);

  const loadBettingHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await sportsBettingAPI.getBets('all', 200);
      setBets(response.data.bets || []);
    } catch (err) {
      setError('Failed to load betting history');
      console.error('Betting history error:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterBets = () => {
    let filtered = bets;
    
    if (statusFilter !== 'all') {
      if (statusFilter === 'pending') {
        filtered = bets.filter(bet => !bet.result);
      } else {
        filtered = bets.filter(bet => bet.result === statusFilter);
      }
    }
    
    setFilteredBets(filtered);
    setPage(0); // Reset to first page when filtering
  };

  const getResultIcon = (result) => {
    switch (result) {
      case 'win':
        return <CheckCircle color="success" />;
      case 'loss':
        return <Cancel color="error" />;
      case 'push':
        return <Remove color="action" />;
      default:
        return <Schedule color="action" />;
    }
  };

  const getResultColor = (result) => {
    switch (result) {
      case 'win':
        return 'success';
      case 'loss':
        return 'error';
      case 'push':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatOdds = (odds) => {
    if (!odds) return 'N/A';
    return odds > 0 ? `+${odds}` : `${odds}`;
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '$0.00';
    return `$${amount.toFixed(2)}`;
  };

  const getPaginatedBets = () => {
    const startIndex = page * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return filteredBets.slice(startIndex, endIndex);
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
        Betting History
      </Typography>

      {/* Filters */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            label="Status"
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <MenuItem value="all">All Bets</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="win">Won</MenuItem>
            <MenuItem value="loss">Lost</MenuItem>
            <MenuItem value="push">Push</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {/* Betting History Table */}
      <Paper elevation={2}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Game</TableCell>
                <TableCell>Bet Type</TableCell>
                <TableCell>Selection</TableCell>
                <TableCell align="right">Odds</TableCell>
                <TableCell align="right">Stake</TableCell>
                <TableCell align="right">Confidence</TableCell>
                <TableCell align="center">Result</TableCell>
                <TableCell align="right">Profit/Loss</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {getPaginatedBets().map((bet) => (
                <TableRow key={bet.id} hover>
                  <TableCell>
                    <Typography variant="body2">
                      {moment(bet.created_at).format('MMM DD, YYYY')}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {moment(bet.created_at).format('HH:mm')}
                    </Typography>
                  </TableCell>
                  
                  <TableCell>
                    <Typography variant="body2">
                      Game: {bet.game_id}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {bet.sport}
                    </Typography>
                  </TableCell>
                  
                  <TableCell>
                    <Chip 
                      label={bet.bet_type} 
                      size="small" 
                      variant="outlined"
                    />
                  </TableCell>
                  
                  <TableCell>
                    <Typography variant="body2">
                      {bet.bet_value}
                    </Typography>
                  </TableCell>
                  
                  <TableCell align="right">
                    <Typography variant="body2" fontFamily="monospace">
                      {formatOdds(bet.odds)}
                    </Typography>
                  </TableCell>
                  
                  <TableCell align="right">
                    <Typography variant="body2" fontFamily="monospace">
                      {formatCurrency(bet.stake)}
                    </Typography>
                  </TableCell>
                  
                  <TableCell align="right">
                    <Chip
                      label={`${(bet.confidence_score * 100).toFixed(1)}%`}
                      size="small"
                      color={
                        bet.confidence_score >= 0.8 ? 'success' :
                        bet.confidence_score >= 0.7 ? 'warning' : 'error'
                      }
                    />
                  </TableCell>
                  
                  <TableCell align="center">
                    <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                      {getResultIcon(bet.result)}
                      {bet.result && (
                        <Chip
                          label={bet.result.toUpperCase()}
                          size="small"
                          color={getResultColor(bet.result)}
                        />
                      )}
                    </Box>
                  </TableCell>
                  
                  <TableCell align="right">
                    <Typography 
                      variant="body2" 
                      fontFamily="monospace"
                      color={
                        bet.profit_loss > 0 ? 'success.main' :
                        bet.profit_loss < 0 ? 'error.main' : 'text.primary'
                      }
                      fontWeight={bet.profit_loss !== 0 ? 'bold' : 'normal'}
                    >
                      {formatCurrency(bet.profit_loss)}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          component="div"
          count={filteredBets.length}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      </Paper>

      {filteredBets.length === 0 && (
        <Paper elevation={2} sx={{ p: 4, textAlign: 'center', mt: 2 }}>
          <Typography variant="h6" color="textSecondary">
            No betting history found
          </Typography>
          <Typography variant="body2" color="textSecondary" mt={1}>
            {statusFilter !== 'all' 
              ? `No bets with status "${statusFilter}" found`
              : 'Start making predictions to see your betting history here'
            }
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default BettingHistory;
