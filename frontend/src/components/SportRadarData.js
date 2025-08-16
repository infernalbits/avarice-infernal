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
  Button,
  ButtonGroup,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge
} from '@mui/material';
import {
  Refresh,
  Sports,
  TrendingUp,
  TrendingDown,
  PersonOff,
  Schedule,
  EmojiEvents,
  Assessment,
  ExpandMore,
  Speed,
  Warning,
  CheckCircle
} from '@mui/icons-material';

const SportRadarData = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSport, setSelectedSport] = useState('nfl');
  const [dataType, setDataType] = useState('games');
  const [teams, setTeams] = useState([]);
  const [games, setGames] = useState([]);
  const [standings, setStandings] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamStats, setTeamStats] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const sports = [
    { value: 'tennis', label: 'Tennis', icon: '🎾' },
    { value: 'ncaamb', label: 'NCAAMB', icon: '🏀' },
    { value: 'nba', label: 'NBA', icon: '🏀' },
    { value: 'nhl', label: 'NHL', icon: '🏒' },
    { value: 'nfl', label: 'NFL', icon: '🏈' },
    { value: 'ncaafb', label: 'NCAAFB', icon: '🏈' },
    { value: 'mlb', label: 'MLB', icon: '⚾' },
    { value: 'mma', label: 'MMA', icon: '🥊' },
    { value: 'nascar', label: 'NASCAR', icon: '🏎️' },
    { value: 'golf', label: 'Golf', icon: '⛳' }
  ];

  const dataTypes = [
    { value: 'games', label: 'Games', icon: <Schedule /> },
    { value: 'standings', label: 'Standings', icon: <EmojiEvents /> },
    { value: 'teams', label: 'Teams', icon: <Sports /> }
  ];

  useEffect(() => {
    loadData();
  }, [selectedSport, dataType]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      switch (dataType) {
        case 'teams':
          await loadTeams();
          break;
        case 'games':
          await loadGames();
          break;
        case 'standings':
          await loadStandings();
          break;
        default:
          break;
      }

      setLastUpdate(new Date());
    } catch (err) {
      setError(`Failed to load ${dataType} data: ${err.message}`);
      console.error('SportRadar data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTeams = async () => {
    const response = await fetch(`/api/sportsradar/teams?sport=${selectedSport}`);
    if (!response.ok) throw new Error('Failed to fetch teams');
    const data = await response.json();
    setTeams(data.teams || []);
  };

  const loadGames = async () => {
    const response = await fetch(`/api/sportsradar/games?sport=${selectedSport}&days=7`);
    if (!response.ok) throw new Error('Failed to fetch games');
    const data = await response.json();
    setGames(data.games || []);
  };

  const loadStandings = async () => {
    const response = await fetch(`/api/sportsradar/standings?sport=${selectedSport}&season=2024`);
    if (!response.ok) throw new Error('Failed to fetch standings');
    const data = await response.json();
    setStandings(data.standings || []);
  };

  const loadTeamStats = async (teamId) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/sportsradar/team-stats/${teamId}?sport=${selectedSport}&season=2024`);
      if (!response.ok) throw new Error('Failed to fetch team stats');
      const data = await response.json();
      setTeamStats(data.teamData);
      setSelectedTeam(teamId);
    } catch (err) {
      setError(`Failed to load team stats: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'TBD';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'scheduled': return 'info';
      case 'inprogress': return 'warning';
      case 'complete': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getWinPercentageColor = (winPct) => {
    if (winPct >= 0.7) return 'success';
    if (winPct >= 0.5) return 'warning';
    return 'error';
  };

  const TeamsView = () => (
    <Grid container spacing={2}>
      {teams.map((team, index) => (
        <Grid item xs={12} sm={6} md={4} key={team.id || index}>
          <Card 
            elevation={2} 
            sx={{ 
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                elevation: 6,
                transform: 'translateY(-4px)'
              }
            }}
            onClick={() => loadTeamStats(team.id)}
          >
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Sports color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" component="div">
                  {team.market} {team.name}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Team ID: {team.id}
              </Typography>
              <Box mt={2}>
                <Button 
                  size="small" 
                  variant="outlined"
                  onClick={(e) => {
                    e.stopPropagation();
                    loadTeamStats(team.id);
                  }}
                >
                  View Stats
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  const GamesView = () => (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Matchup</TableCell>
            <TableCell align="center">Date/Time</TableCell>
            <TableCell align="center">Status</TableCell>
            <TableCell align="center">Score</TableCell>
            <TableCell align="center">Week</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {games.map((game, index) => (
            <TableRow key={game.id || index} hover>
              <TableCell>
                <Box>
                  <Typography variant="body1" fontWeight="bold">
                    {game.away_team?.market} {game.away_team?.name} @ {game.home_team?.market} {game.home_team?.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {game.away_team?.alias} @ {game.home_team?.alias}
                  </Typography>
                </Box>
              </TableCell>
              
              <TableCell align="center">
                <Typography variant="body2">
                  {formatDate(game.scheduled)}
                </Typography>
              </TableCell>
              
              <TableCell align="center">
                <Chip 
                  label={game.status || 'Scheduled'} 
                  color={getStatusColor(game.status)}
                  size="small"
                />
              </TableCell>
              
              <TableCell align="center">
                {game.away_score !== undefined && game.home_score !== undefined ? (
                  <Box>
                    <Typography variant="body2">
                      {game.away_score} - {game.home_score}
                    </Typography>
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    -
                  </Typography>
                )}
              </TableCell>
              
              <TableCell align="center">
                <Typography variant="body2">
                  {selectedSport === 'nfl' ? `Week ${game.week || '-'}` : '-'}
                </Typography>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const StandingsView = () => (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Team</TableCell>
            <TableCell align="center">Record</TableCell>
            <TableCell align="center">Win %</TableCell>
            <TableCell align="center">Points For</TableCell>
            <TableCell align="center">Points Against</TableCell>
            <TableCell align="center">Diff</TableCell>
            {selectedSport === 'nfl' && <TableCell align="center">Division</TableCell>}
            {selectedSport === 'nba' && <TableCell align="center">GB</TableCell>}
          </TableRow>
        </TableHead>
        <TableBody>
          {standings.map((team, index) => (
            <TableRow key={team.team_id || index} hover>
              <TableCell>
                <Box display="flex" alignItems="center">
                  <Typography variant="body1" fontWeight="bold">
                    {team.market} {team.team_name}
                  </Typography>
                  <Chip 
                    label={team.alias}
                    size="small"
                    variant="outlined"
                    sx={{ ml: 1 }}
                  />
                </Box>
              </TableCell>
              
              <TableCell align="center">
                <Typography variant="body2">
                  {team.wins}-{team.losses}{team.ties ? `-${team.ties}` : ''}
                </Typography>
              </TableCell>
              
              <TableCell align="center">
                <Chip 
                  label={`${(team.win_pct * 100).toFixed(1)}%`}
                  color={getWinPercentageColor(team.win_pct)}
                  size="small"
                />
              </TableCell>
              
              <TableCell align="center">
                <Typography variant="body2">
                  {team.points_for || '-'}
                </Typography>
              </TableCell>
              
              <TableCell align="center">
                <Typography variant="body2">
                  {team.points_against || '-'}
                </Typography>
              </TableCell>
              
              <TableCell align="center">
                <Box display="flex" alignItems="center" justifyContent="center">
                  {team.point_diff > 0 ? (
                    <TrendingUp color="success" fontSize="small" />
                  ) : team.point_diff < 0 ? (
                    <TrendingDown color="error" fontSize="small" />
                  ) : null}
                  <Typography variant="body2" sx={{ ml: 0.5 }}>
                    {team.point_diff > 0 ? '+' : ''}{team.point_diff || 0}
                  </Typography>
                </Box>
              </TableCell>
              
              {selectedSport === 'nfl' && (
                <TableCell align="center">
                  <Typography variant="body2">
                    {team.division || '-'}
                  </Typography>
                </TableCell>
              )}
              
              {selectedSport === 'nba' && (
                <TableCell align="center">
                  <Typography variant="body2">
                    {team.games_back || '0'}
                  </Typography>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const TeamStatsModal = () => {
    if (!teamStats) return null;

    return (
      <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">
            Team Statistics
          </Typography>
          <Button onClick={() => setTeamStats(null)}>Close</Button>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">Basic Statistics</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  <ListItem>
                    <ListItemIcon><Assessment /></ListItemIcon>
                    <ListItemText 
                      primary="Games Played" 
                      secondary={teamStats.statistics?.games_played || 'N/A'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                    <ListItemText 
                      primary="Wins" 
                      secondary={teamStats.statistics?.wins || 'N/A'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Warning color="error" /></ListItemIcon>
                    <ListItemText 
                      primary="Losses" 
                      secondary={teamStats.statistics?.losses || 'N/A'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><TrendingUp /></ListItemIcon>
                    <ListItemText 
                      primary="Win Percentage" 
                      secondary={`${((teamStats.statistics?.win_percentage || 0) * 100).toFixed(1)}%`} 
                    />
                  </ListItem>
                </List>
              </AccordionDetails>
            </Accordion>
          </Grid>

          <Grid item xs={12} md={6}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">Injuries</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {teamStats.injuries && teamStats.injuries.length > 0 ? (
                  <List>
                    {teamStats.injuries.slice(0, 5).map((injury, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <Badge 
                            badgeContent={injury.impact_level ? Math.round(injury.impact_level * 10) : 0}
                            color={injury.status === 'out' ? 'error' : 'warning'}
                          >
                            <PersonOff />
                          </Badge>
                        </ListItemIcon>
                        <ListItemText 
                          primary={injury.player_name}
                          secondary={`${injury.position} - ${injury.status} (${injury.injury_type})`}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="text.secondary">No injury data available</Typography>
                )}
                
                {teamStats.injury_impact !== undefined && (
                  <Box mt={2}>
                    <Typography variant="body2">
                      Overall Injury Impact: {(teamStats.injury_impact * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          </Grid>
        </Grid>
      </Paper>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          SportRadar Live Data
        </Typography>
        
        <Box display="flex" alignItems="center" gap={2}>
          {lastUpdate && (
            <Typography variant="body2" color="text.secondary">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </Typography>
          )}
          <IconButton onClick={loadData} disabled={loading}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Sport</InputLabel>
            <Select
              value={selectedSport}
              label="Sport"
              onChange={(e) => setSelectedSport(e.target.value)}
            >
              {sports.map((sport) => (
                <MenuItem key={sport.value} value={sport.value}>
                  {sport.icon} {sport.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <ButtonGroup variant="outlined" fullWidth>
            {dataTypes.map((type) => (
              <Button
                key={type.value}
                variant={dataType === type.value ? 'contained' : 'outlined'}
                onClick={() => setDataType(type.value)}
                startIcon={type.icon}
              >
                {type.label}
              </Button>
            ))}
          </ButtonGroup>
        </Grid>
      </Grid>

      {dataType === 'teams' && <TeamsView />}
      {dataType === 'games' && <GamesView />}
      {dataType === 'standings' && <StandingsView />}
      
      <TeamStatsModal />
    </Box>
  );
};

export default SportRadarData;
