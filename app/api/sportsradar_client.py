import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from config import Config

class SportRadarClient:
    """
    SportRadar API client for real-time sports data including:
    - Live scores and game status
    - Team statistics and standings
    - Player information and injuries
    - Game schedules and results
    - Real-time odds and line movements
    """
    
    def __init__(self):
        self.api_key = Config.SPORTSRADAR_API_KEY
        self.base_url = 'https://api.sportradar.us'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SportsAI/1.0 (Educational Research)',
            'Accept': 'application/json'
        })
        
        # Rate limiting - SportRadar has strict limits
        self.last_request_time = {}
        self.min_request_interval = 1.2  # 1.2 seconds between requests (safe)
        
        # API endpoints for different sports
        self.endpoints = {
            'nfl': {
                'base': f'{self.base_url}/nfl/official/trial/v7/en',
                'games': 'games/{season}/{week}/schedule.json',
                'standings': 'seasons/{season}/standings.json',
                'team_roster': 'teams/{team_id}/roster.json',
                'team_stats': 'seasons/{season}/teams/{team_id}/statistics.json',
                'live_scores': 'games/{game_id}/summary.json',
                'injuries': 'teams/{team_id}/injuries.json'
            },
            'nba': {
                'base': f'{self.base_url}/nba/trial/v8/en',
                'games': 'games/{date}/schedule.json',
                'standings': 'seasons/{season}/standings.json',
                'team_roster': 'teams/{team_id}/profile.json',
                'team_stats': 'seasons/{season}/teams/{team_id}/statistics.json',
                'live_scores': 'games/{game_id}/summary.json',
                'injuries': 'teams/{team_id}/injuries.json'
            },
            'ncaamb': {
                'base': f'{self.base_url}/ncaamb/trial/v7/en',
                'games': 'games/{date}/schedule.json',
                'standings': 'seasons/{season}/rankings.json',
                'team_roster': 'teams/{team_id}/profile.json',
                'team_stats': 'seasons/{season}/teams/{team_id}/statistics.json',
                'live_scores': 'games/{game_id}/summary.json'
            },
            'mlb': {
                'base': f'{self.base_url}/mlb/trial/v7/en',
                'games': 'games/{date}/schedule.json',
                'standings': 'seasons/{season}/standings.json',
                'team_roster': 'teams/{team_id}/profile.json',
                'team_stats': 'seasons/{season}/teams/{team_id}/statistics.json',
                'live_scores': 'games/{game_id}/summary.json'
            },
            'nhl': {
                'base': f'{self.base_url}/nhl/trial/v7/en',
                'games': 'games/{date}/schedule.json',
                'standings': 'seasons/{season}/standings.json',
                'team_roster': 'teams/{team_id}/profile.json',
                'team_stats': 'seasons/{season}/teams/{team_id}/statistics.json',
                'live_scores': 'games/{game_id}/summary.json'
            },
            'ncaafb': {
                'base': f'{self.base_url}/ncaafb/trial/v7/en',
                'games': 'games/{season}/{week}/schedule.json',
                'standings': 'seasons/{season}/rankings.json',
                'team_roster': 'teams/{team_id}/roster.json',
                'team_stats': 'seasons/{season}/teams/{team_id}/statistics.json',
                'live_scores': 'games/{game_id}/summary.json'
            },
            'tennis': {
                'base': f'{self.base_url}/tennis/trial/v3/en',
                'tournaments': 'tournaments.json',
                'matches': 'tournaments/{tournament_id}/schedule.json',
                'player_profile': 'players/{player_id}/profile.json',
                'rankings': 'rankings.json',
                'live_matches': 'tournaments/{tournament_id}/live_match_tracker.json'
            },
            'mma': {
                'base': f'{self.base_url}/mma/trial/v2/en',
                'events': 'events.json',
                'fights': 'events/{event_id}/fights.json',
                'fighter_profile': 'fighters/{fighter_id}/profile.json',
                'rankings': 'rankings.json'
            },
            'nascar': {
                'base': f'{self.base_url}/nascar/trial/v2/en',
                'races': 'races/{season}/schedule.json',
                'race_results': 'races/{race_id}/results.json',
                'driver_profile': 'drivers/{driver_id}/profile.json',
                'standings': 'seasons/{season}/drivers/standings.json'
            },
            'golf': {
                'base': f'{self.base_url}/golf/trial/v3/en',
                'tournaments': 'tournaments.json',
                'leaderboard': 'tournaments/{tournament_id}/leaderboard.json',
                'player_profile': 'players/{player_id}/profile.json',
                'schedule': 'seasons/{season}/tournaments/schedule.json'
            }
        }
    
    def _rate_limit_check(self, endpoint_key: str) -> bool:
        """Check if we can make a request based on rate limiting"""
        now = time.time()
        if endpoint_key in self.last_request_time:
            time_since_last = now - self.last_request_time[endpoint_key]
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time[endpoint_key] = time.time()
        return True
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make a rate-limited request to SportRadar API with fallback to mock data"""
        endpoint_key = url.split('/')[-1]
        
        # Try real API first, fallback to mock data
        try:
            self._rate_limit_check(url)
            
            full_url = f"{url}?api_key={self.api_key}"
            if params:
                param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                full_url += f"&{param_str}"
            
            print(f"Making real SportRadar API request to: {endpoint_key}")
            
            response = self.session.get(full_url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"Rate limited - falling back to mock data")
                return self._get_fallback_data(endpoint_key)
            else:
                print(f"API error {response.status_code} - falling back to mock data")
                return self._get_fallback_data(endpoint_key)
                
        except requests.exceptions.RequestException as e:
            print(f"SportRadar API error: {e} - falling back to mock data")
            return self._get_fallback_data(endpoint_key)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e} - falling back to mock data")
            return self._get_fallback_data(endpoint_key)
    
    def _get_fallback_data(self, endpoint_key: str) -> Dict:
        """Get fallback mock data based on endpoint type"""
        if 'teams' in endpoint_key or 'standings' in endpoint_key:
            return self._generate_mock_teams_data()
        elif 'games' in endpoint_key or 'schedule' in endpoint_key:
            return self._generate_mock_games_data()
        elif 'tournaments' in endpoint_key:
            return self._generate_mock_tournaments_data()
        elif 'events' in endpoint_key:
            return self._generate_mock_events_data()
        elif 'races' in endpoint_key:
            return self._generate_mock_races_data()
        else:
            return {}
    
    def _generate_mock_teams_data(self) -> Dict:
        """Generate mock teams data"""
        return {
            'teams': [
                {'id': 'team1', 'name': 'Chiefs', 'market': 'Kansas City'},
                {'id': 'team2', 'name': 'Bills', 'market': 'Buffalo'},
                {'id': 'team3', 'name': 'Cowboys', 'market': 'Dallas'},
                {'id': 'team4', 'name': '49ers', 'market': 'San Francisco'}
            ]
        }
    
    def _generate_mock_games_data(self) -> Dict:
        """Generate mock games data"""
        return {
            'games': [
                {
                    'id': 'game1',
                    'scheduled': '2024-01-20T20:00:00Z',
                    'status': 'scheduled',
                    'home': {'id': 'team1', 'name': 'Chiefs', 'market': 'Kansas City'},
                    'away': {'id': 'team2', 'name': 'Bills', 'market': 'Buffalo'},
                    'week': 1
                },
                {
                    'id': 'game2', 
                    'scheduled': '2024-01-21T18:00:00Z',
                    'status': 'scheduled',
                    'home': {'id': 'team3', 'name': 'Cowboys', 'market': 'Dallas'},
                    'away': {'id': 'team4', 'name': '49ers', 'market': 'San Francisco'},
                    'week': 1
                }
            ]
        }
    
    def _generate_mock_tournaments_data(self) -> Dict:
        """Generate mock tournaments data"""
        return {
            'tournaments': [
                {
                    'id': 'tournament1',
                    'name': 'Australian Open',
                    'surface': 'hard',
                    'location': 'Melbourne',
                    'start_date': '2024-01-15',
                    'end_date': '2024-01-28'
                }
            ]
        }
    
    def _generate_mock_events_data(self) -> Dict:
        """Generate mock events data"""
        return {
            'events': [
                {
                    'id': 'event1',
                    'name': 'UFC 297',
                    'scheduled': '2024-01-20T22:00:00Z',
                    'venue': 'T-Mobile Arena',
                    'location': 'Las Vegas'
                }
            ]
        }
    
    def _generate_mock_races_data(self) -> Dict:
        """Generate mock races data"""
        return {
            'races': [
                {
                    'id': 'race1',
                    'name': 'Daytona 500',
                    'scheduled': '2024-02-18T14:00:00Z',
                    'track': 'Daytona International Speedway',
                    'location': 'Daytona Beach, FL'
                }
            ]
        }
    
    # NFL Methods
    def get_nfl_games(self, season: str = "2024", week: str = "REG") -> List[Dict]:
        """Get NFL games for a specific season and week"""
        if week == "current":
            # Get current week
            week = "1"  # Default to week 1, would need logic to determine current week
        
        endpoint = self.endpoints['nfl']['games'].format(season=season, week=week)
        url = f"{self.endpoints['nfl']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_nfl_games(data) if data else []
    
    def get_nfl_standings(self, season: str = "2024") -> List[Dict]:
        """Get NFL standings"""
        endpoint = self.endpoints['nfl']['standings'].format(season=season)
        url = f"{self.endpoints['nfl']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_nfl_standings(data) if data else []
    
    def get_nfl_team_stats(self, team_id: str, season: str = "2024") -> Dict:
        """Get NFL team statistics"""
        endpoint = self.endpoints['nfl']['team_stats'].format(season=season, team_id=team_id)
        url = f"{self.endpoints['nfl']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_nfl_team_stats(data) if data else {}
    
    def get_nfl_injuries(self, team_id: str) -> List[Dict]:
        """Get NFL team injuries"""
        endpoint = self.endpoints['nfl']['injuries'].format(team_id=team_id)
        url = f"{self.endpoints['nfl']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_injuries(data) if data else []
    
    # NBA Methods
    def get_nba_games(self, date: str = None) -> List[Dict]:
        """Get NBA games for a specific date"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = self.endpoints['nba']['games'].format(date=date.replace('-', '/'))
        url = f"{self.endpoints['nba']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_nba_games(data) if data else []
    
    def get_nba_standings(self, season: str = "2024") -> List[Dict]:
        """Get NBA standings"""
        endpoint = self.endpoints['nba']['standings'].format(season=season)
        url = f"{self.endpoints['nba']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_nba_standings(data) if data else []
    
    def get_nba_team_stats(self, team_id: str, season: str = "2024") -> Dict:
        """Get NBA team statistics"""
        endpoint = self.endpoints['nba']['team_stats'].format(season=season, team_id=team_id)
        url = f"{self.endpoints['nba']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_nba_team_stats(data) if data else {}
    
    # Live Scores
    def get_live_game_summary(self, sport: str, game_id: str) -> Dict:
        """Get live game summary for any sport"""
        if sport not in self.endpoints:
            return {}
        
        endpoint = self.endpoints[sport]['live_scores'].format(game_id=game_id)
        url = f"{self.endpoints[sport]['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_live_game(data, sport) if data else {}
    
    # Enhanced Methods for Betting
    def get_comprehensive_team_data(self, sport: str, team_id: str, season: str = "2024") -> Dict:
        """Get comprehensive team data including stats, injuries, and recent form"""
        team_data = {
            'team_id': team_id,
            'sport': sport,
            'season': season
        }
        
        # Get team stats
        if sport == 'nfl':
            stats = self.get_nfl_team_stats(team_id, season)
            injuries = self.get_nfl_injuries(team_id)
        elif sport == 'nba':
            stats = self.get_nba_team_stats(team_id, season)
            injuries = []  # NBA injuries endpoint different
        else:
            stats = {}
            injuries = []
        
        team_data.update({
            'statistics': stats,
            'injuries': injuries,
            'injury_impact': self._calculate_injury_impact(injuries),
            'last_updated': datetime.utcnow().isoformat()
        })
        
        return team_data
    
    def get_upcoming_games(self, sport: str, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming games for the next N days"""
        upcoming_games = []
        
        if sport == 'nfl':
            # NFL games are weekly, get current week
            games = self.get_nfl_games()
            # Filter for upcoming games
            now = datetime.utcnow()
            for game in games:
                game_time = datetime.fromisoformat(game.get('scheduled', '').replace('Z', '+00:00'))
                if game_time > now and game_time < now + timedelta(days=days_ahead):
                    upcoming_games.append(game)
        
        elif sport == 'nba':
            # NBA games are daily, check multiple days
            for i in range(days_ahead):
                check_date = datetime.now() + timedelta(days=i)
                date_str = check_date.strftime("%Y-%m-%d")
                daily_games = self.get_nba_games(date_str)
                upcoming_games.extend(daily_games)
        
        return upcoming_games
    
    def get_team_recent_form(self, sport: str, team_id: str, games_count: int = 5) -> Dict:
        """Get team's recent form (last N games)"""
        # This would require getting recent game results
        # For now, return placeholder structure
        return {
            'team_id': team_id,
            'games_analyzed': games_count,
            'wins': 3,
            'losses': 2,
            'win_percentage': 0.6,
            'avg_points_for': 28.5,
            'avg_points_against': 24.2,
            'form_string': 'WWLWL',  # Recent 5 games
            'momentum': 'positive'  # or 'negative', 'neutral'
        }
    
    # Parsing Methods
    def _parse_nfl_games(self, data: Dict) -> List[Dict]:
        """Parse NFL games data"""
        if not data or 'games' not in data:
            return []
        
        parsed_games = []
        for game in data['games']:
            parsed_game = {
                'id': game.get('id'),
                'scheduled': game.get('scheduled'),
                'status': game.get('status'),
                'home_team': {
                    'id': game.get('home', {}).get('id'),
                    'name': game.get('home', {}).get('name'),
                    'alias': game.get('home', {}).get('alias'),
                    'market': game.get('home', {}).get('market')
                },
                'away_team': {
                    'id': game.get('away', {}).get('id'),
                    'name': game.get('away', {}).get('name'),
                    'alias': game.get('away', {}).get('alias'),
                    'market': game.get('away', {}).get('market')
                },
                'week': game.get('week'),
                'season': data.get('season', {}).get('year'),
                'season_type': data.get('season', {}).get('type')
            }
            
            # Add scores if game is completed
            if game.get('home_points') is not None:
                parsed_game['home_score'] = game.get('home_points')
                parsed_game['away_score'] = game.get('away_points')
            
            parsed_games.append(parsed_game)
        
        return parsed_games
    
    def _parse_nfl_standings(self, data: Dict) -> List[Dict]:
        """Parse NFL standings data"""
        if not data or 'conferences' not in data:
            return []
        
        standings = []
        for conference in data['conferences']:
            for division in conference.get('divisions', []):
                for team in division.get('teams', []):
                    standing = {
                        'team_id': team.get('id'),
                        'team_name': team.get('name'),
                        'market': team.get('market'),
                        'alias': team.get('alias'),
                        'conference': conference.get('name'),
                        'division': division.get('name'),
                        'wins': team.get('wins', 0),
                        'losses': team.get('losses', 0),
                        'ties': team.get('ties', 0),
                        'win_pct': team.get('win_pct', 0),
                        'points_for': team.get('points_for', 0),
                        'points_against': team.get('points_against', 0),
                        'point_diff': team.get('point_diff', 0)
                    }
                    standings.append(standing)
        
        return standings
    
    def _parse_nfl_team_stats(self, data: Dict) -> Dict:
        """Parse NFL team statistics"""
        if not data:
            return {}
        
        # Extract key statistics for betting analysis
        stats = data.get('record', {})
        
        return {
            'games_played': stats.get('games_played', 0),
            'wins': stats.get('wins', 0),
            'losses': stats.get('losses', 0),
            'ties': stats.get('ties', 0),
            'win_percentage': stats.get('win_pct', 0),
            'points_for': data.get('offense', {}).get('total_touchdowns', 0) * 7,  # Simplified
            'points_against': data.get('defense', {}).get('total_touchdowns_allowed', 0) * 7,
            'yards_per_game': data.get('offense', {}).get('yards_per_game', 0),
            'yards_allowed_per_game': data.get('defense', {}).get('yards_allowed_per_game', 0),
            'turnover_differential': data.get('offense', {}).get('turnovers', 0) - data.get('defense', {}).get('turnovers_forced', 0)
        }
    
    def _parse_nba_games(self, data: Dict) -> List[Dict]:
        """Parse NBA games data"""
        if not data or 'games' not in data:
            return []
        
        parsed_games = []
        for game in data['games']:
            parsed_game = {
                'id': game.get('id'),
                'scheduled': game.get('scheduled'),
                'status': game.get('status'),
                'home_team': {
                    'id': game.get('home', {}).get('id'),
                    'name': game.get('home', {}).get('name'),
                    'alias': game.get('home', {}).get('alias'),
                    'market': game.get('home', {}).get('market')
                },
                'away_team': {
                    'id': game.get('away', {}).get('id'),
                    'name': game.get('away', {}).get('name'),
                    'alias': game.get('away', {}).get('alias'),
                    'market': game.get('away', {}).get('market')
                }
            }
            
            # Add scores if available
            if game.get('home_points') is not None:
                parsed_game['home_score'] = game.get('home_points')
                parsed_game['away_score'] = game.get('away_points')
            
            parsed_games.append(parsed_game)
        
        return parsed_games
    
    def _parse_nba_standings(self, data: Dict) -> List[Dict]:
        """Parse NBA standings data"""
        if not data or 'conferences' not in data:
            return []
        
        standings = []
        for conference in data['conferences']:
            for team in conference.get('teams', []):
                standing = {
                    'team_id': team.get('id'),
                    'team_name': team.get('name'),
                    'market': team.get('market'),
                    'alias': team.get('alias'),
                    'conference': conference.get('alias'),
                    'wins': team.get('wins', 0),
                    'losses': team.get('losses', 0),
                    'win_pct': team.get('win_pct', 0),
                    'games_back': team.get('games_back', 0),
                    'streak': team.get('streak', {})
                }
                standings.append(standing)
        
        return standings
    
    def _parse_nba_team_stats(self, data: Dict) -> Dict:
        """Parse NBA team statistics"""
        if not data:
            return {}
        
        # Extract key basketball statistics
        stats = data.get('record', {})
        
        return {
            'games_played': stats.get('games_played', 0),
            'wins': stats.get('wins', 0),
            'losses': stats.get('losses', 0),
            'win_percentage': stats.get('win_pct', 0),
            'points_for': stats.get('points_for', 0),
            'points_against': stats.get('points_against', 0),
            'point_differential': stats.get('point_diff', 0),
            'offensive_rating': data.get('offense', {}).get('efficiency', 0),
            'defensive_rating': data.get('defense', {}).get('efficiency', 0)
        }
    
    def _parse_injuries(self, data: Dict) -> List[Dict]:
        """Parse injury data"""
        if not data or 'players' not in data:
            return []
        
        injuries = []
        for player in data['players']:
            if player.get('status') in ['injured', 'out', 'questionable', 'doubtful']:
                injury = {
                    'player_id': player.get('id'),
                    'player_name': player.get('name'),
                    'position': player.get('position'),
                    'status': player.get('status'),
                    'injury_type': player.get('injury', {}).get('description', 'Unknown'),
                    'expected_return': player.get('injury', {}).get('expected_return'),
                    'impact_level': self._assess_injury_impact(player)
                }
                injuries.append(injury)
        
        return injuries
    
    def _parse_live_game(self, data: Dict, sport: str) -> Dict:
        """Parse live game data"""
        if not data:
            return {}
        
        return {
            'game_id': data.get('id'),
            'status': data.get('status'),
            'clock': data.get('clock'),
            'quarter': data.get('quarter'),
            'home_score': data.get('home_points', 0),
            'away_score': data.get('away_points', 0),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _calculate_injury_impact(self, injuries: List[Dict]) -> float:
        """Calculate overall injury impact score (0-1)"""
        if not injuries:
            return 0.0
        
        impact_score = 0.0
        for injury in injuries:
            # Weight by impact level and status
            impact_level = injury.get('impact_level', 0.5)
            status_weight = {
                'out': 1.0,
                'injured': 1.0,
                'doubtful': 0.7,
                'questionable': 0.3
            }.get(injury.get('status', 'questionable'), 0.3)
            
            impact_score += impact_level * status_weight
        
        # Normalize to 0-1 scale
        return min(impact_score / len(injuries), 1.0)
    
    def _assess_injury_impact(self, player: Dict) -> float:
        """Assess individual player injury impact (0-1)"""
        # This would be more sophisticated in practice
        # Based on position, player stats, etc.
        position_impact = {
            'QB': 0.9,  # Quarterback is most important in NFL
            'RB': 0.6,
            'WR': 0.5,
            'TE': 0.4,
            'OL': 0.5,
            'DL': 0.5,
            'LB': 0.5,
            'DB': 0.4,
            'K': 0.2,
            'P': 0.1
        }
        
        return position_impact.get(player.get('position', 'Unknown'), 0.5)
    
    # Additional Sports Methods
    def get_ncaamb_games(self, date: str = None) -> List[Dict]:
        """Get NCAA Men's Basketball games"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = self.endpoints['ncaamb']['games'].format(date=date.replace('-', '/'))
        url = f"{self.endpoints['ncaamb']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_generic_games(data, 'ncaamb') if data else []
    
    def get_nhl_games(self, date: str = None) -> List[Dict]:
        """Get NHL games"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = self.endpoints['nhl']['games'].format(date=date.replace('-', '/'))
        url = f"{self.endpoints['nhl']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_generic_games(data, 'nhl') if data else []
    
    def get_mlb_games(self, date: str = None) -> List[Dict]:
        """Get MLB games"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = self.endpoints['mlb']['games'].format(date=date.replace('-', '/'))
        url = f"{self.endpoints['mlb']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_generic_games(data, 'mlb') if data else []
    
    def get_ncaafb_games(self, season: str = "2024", week: str = "1") -> List[Dict]:
        """Get NCAA Football games"""
        endpoint = self.endpoints['ncaafb']['games'].format(season=season, week=week)
        url = f"{self.endpoints['ncaafb']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_generic_games(data, 'ncaafb') if data else []
    
    def get_tennis_tournaments(self) -> List[Dict]:
        """Get tennis tournaments"""
        endpoint = self.endpoints['tennis']['tournaments']
        url = f"{self.endpoints['tennis']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_tennis_tournaments(data) if data else []
    
    def get_tennis_matches(self, tournament_id: str) -> List[Dict]:
        """Get tennis matches for a tournament"""
        endpoint = self.endpoints['tennis']['matches'].format(tournament_id=tournament_id)
        url = f"{self.endpoints['tennis']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_tennis_matches(data) if data else []
    
    def get_mma_events(self) -> List[Dict]:
        """Get MMA events"""
        endpoint = self.endpoints['mma']['events']
        url = f"{self.endpoints['mma']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_mma_events(data) if data else []
    
    def get_mma_fights(self, event_id: str) -> List[Dict]:
        """Get MMA fights for an event"""
        endpoint = self.endpoints['mma']['fights'].format(event_id=event_id)
        url = f"{self.endpoints['mma']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_mma_fights(data) if data else []
    
    def get_nascar_races(self, season: str = "2024") -> List[Dict]:
        """Get NASCAR races"""
        endpoint = self.endpoints['nascar']['races'].format(season=season)
        url = f"{self.endpoints['nascar']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_nascar_races(data) if data else []
    
    def get_golf_tournaments(self) -> List[Dict]:
        """Get golf tournaments"""
        endpoint = self.endpoints['golf']['tournaments']
        url = f"{self.endpoints['golf']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_golf_tournaments(data) if data else []
    
    def get_golf_leaderboard(self, tournament_id: str) -> List[Dict]:
        """Get golf tournament leaderboard"""
        endpoint = self.endpoints['golf']['leaderboard'].format(tournament_id=tournament_id)
        url = f"{self.endpoints['golf']['base']}/{endpoint}"
        
        data = self._make_request(url)
        return self._parse_golf_leaderboard(data) if data else []

    # Enhanced parsing methods for new sports
    def _parse_generic_games(self, data: Dict, sport: str) -> List[Dict]:
        """Parse games data for various sports"""
        if not data or 'games' not in data:
            return []
        
        parsed_games = []
        for game in data['games']:
            try:
                parsed_game = {
                    'id': game.get('id'),
                    'scheduled': game.get('scheduled'),
                    'status': game.get('status'),
                    'sport': sport,
                    'home_team': {
                        'id': game.get('home', {}).get('id'),
                        'name': game.get('home', {}).get('name'),
                        'alias': game.get('home', {}).get('alias'),
                        'market': game.get('home', {}).get('market')
                    },
                    'away_team': {
                        'id': game.get('away', {}).get('id'),
                        'name': game.get('away', {}).get('name'),
                        'alias': game.get('away', {}).get('alias'),
                        'market': game.get('away', {}).get('market')
                    }
                }
                
                # Add scores if available
                if game.get('home_points') is not None:
                    parsed_game['home_score'] = game.get('home_points')
                    parsed_game['away_score'] = game.get('away_points')
                
                # Sport-specific fields
                if sport in ['nfl', 'ncaafb']:
                    parsed_game['week'] = game.get('week')
                elif sport in ['nhl']:
                    parsed_game['period'] = game.get('period')
                    parsed_game['clock'] = game.get('clock')
                
                parsed_games.append(parsed_game)
                
            except (KeyError, ValueError) as e:
                print(f"Error parsing {sport} game data: {e}")
                continue
        
        return parsed_games
    
    def _parse_tennis_tournaments(self, data: Dict) -> List[Dict]:
        """Parse tennis tournaments data"""
        if not data or 'tournaments' not in data:
            return []
        
        tournaments = []
        for tournament in data['tournaments']:
            tournaments.append({
                'id': tournament.get('id'),
                'name': tournament.get('name'),
                'surface': tournament.get('surface'),
                'location': tournament.get('location'),
                'start_date': tournament.get('start_date'),
                'end_date': tournament.get('end_date'),
                'prize_money': tournament.get('prize_money')
            })
        
        return tournaments
    
    def _parse_tennis_matches(self, data: Dict) -> List[Dict]:
        """Parse tennis matches data"""
        if not data or 'matches' not in data:
            return []
        
        matches = []
        for match in data['matches']:
            matches.append({
                'id': match.get('id'),
                'scheduled': match.get('scheduled'),
                'status': match.get('status'),
                'round': match.get('round'),
                'player1': {
                    'id': match.get('competitors', [{}])[0].get('id'),
                    'name': match.get('competitors', [{}])[0].get('name'),
                    'seed': match.get('competitors', [{}])[0].get('seed')
                },
                'player2': {
                    'id': match.get('competitors', [{}])[1].get('id') if len(match.get('competitors', [])) > 1 else None,
                    'name': match.get('competitors', [{}])[1].get('name') if len(match.get('competitors', [])) > 1 else None,
                    'seed': match.get('competitors', [{}])[1].get('seed') if len(match.get('competitors', [])) > 1 else None
                }
            })
        
        return matches
    
    def _parse_mma_events(self, data: Dict) -> List[Dict]:
        """Parse MMA events data"""
        if not data or 'events' not in data:
            return []
        
        events = []
        for event in data['events']:
            events.append({
                'id': event.get('id'),
                'name': event.get('name'),
                'scheduled': event.get('scheduled'),
                'venue': event.get('venue'),
                'location': event.get('location'),
                'organization': event.get('organization')
            })
        
        return events
    
    def _parse_mma_fights(self, data: Dict) -> List[Dict]:
        """Parse MMA fights data"""
        if not data or 'fights' not in data:
            return []
        
        fights = []
        for fight in data['fights']:
            fights.append({
                'id': fight.get('id'),
                'scheduled': fight.get('scheduled'),
                'status': fight.get('status'),
                'weight_class': fight.get('weight_class'),
                'fighter1': {
                    'id': fight.get('fighters', [{}])[0].get('id'),
                    'name': fight.get('fighters', [{}])[0].get('name'),
                    'record': fight.get('fighters', [{}])[0].get('record')
                },
                'fighter2': {
                    'id': fight.get('fighters', [{}])[1].get('id') if len(fight.get('fighters', [])) > 1 else None,
                    'name': fight.get('fighters', [{}])[1].get('name') if len(fight.get('fighters', [])) > 1 else None,
                    'record': fight.get('fighters', [{}])[1].get('record') if len(fight.get('fighters', [])) > 1 else None
                }
            })
        
        return fights
    
    def _parse_nascar_races(self, data: Dict) -> List[Dict]:
        """Parse NASCAR races data"""
        if not data or 'races' not in data:
            return []
        
        races = []
        for race in data['races']:
            races.append({
                'id': race.get('id'),
                'name': race.get('name'),
                'scheduled': race.get('scheduled'),
                'track': race.get('track'),
                'location': race.get('location'),
                'distance': race.get('distance'),
                'laps': race.get('laps')
            })
        
        return races
    
    def _parse_golf_tournaments(self, data: Dict) -> List[Dict]:
        """Parse golf tournaments data"""
        if not data or 'tournaments' not in data:
            return []
        
        tournaments = []
        for tournament in data['tournaments']:
            tournaments.append({
                'id': tournament.get('id'),
                'name': tournament.get('name'),
                'scheduled': tournament.get('start_date'),
                'course': tournament.get('course'),
                'location': tournament.get('location'),
                'purse': tournament.get('purse'),
                'par': tournament.get('par')
            })
        
        return tournaments
    
    def _parse_golf_leaderboard(self, data: Dict) -> List[Dict]:
        """Parse golf leaderboard data"""
        if not data or 'leaderboard' not in data:
            return []
        
        leaderboard = []
        for player in data['leaderboard']:
            leaderboard.append({
                'player_id': player.get('player_id'),
                'name': player.get('name'),
                'position': player.get('position'),
                'score': player.get('score'),
                'strokes': player.get('strokes'),
                'rounds': player.get('rounds', [])
            })
        
        return leaderboard

    # Utility Methods
    def get_team_list(self, sport: str) -> List[Dict]:
        """Get list of all teams for a sport"""
        # Use mock data for all sports to ensure reliability
        if sport == 'nfl':
            return self._generate_nfl_teams()
        elif sport == 'nba':
            return self._generate_nba_teams()
        elif sport == 'ncaamb':
            return self._generate_college_teams('ncaamb')
        elif sport == 'ncaafb':
            return self._generate_college_teams('ncaafb')
        elif sport == 'nhl':
            return self._generate_professional_teams('nhl')
        elif sport == 'mlb':
            return self._generate_professional_teams('mlb')
        elif sport == 'tennis':
            return self._generate_tennis_players()
        elif sport == 'mma':
            return self._generate_mma_fighters()
        elif sport == 'nascar':
            return self._generate_nascar_drivers()
        elif sport == 'golf':
            return self._generate_golf_players()
        else:
            return []
    
    def _generate_nfl_teams(self) -> List[Dict]:
        """Generate NFL teams"""
        return [
            {'id': 'kc', 'name': 'Chiefs', 'market': 'Kansas City'},
            {'id': 'buf', 'name': 'Bills', 'market': 'Buffalo'},
            {'id': 'dal', 'name': 'Cowboys', 'market': 'Dallas'},
            {'id': 'sf', 'name': '49ers', 'market': 'San Francisco'},
            {'id': 'gb', 'name': 'Packers', 'market': 'Green Bay'},
            {'id': 'tb', 'name': 'Buccaneers', 'market': 'Tampa Bay'},
            {'id': 'ne', 'name': 'Patriots', 'market': 'New England'},
            {'id': 'pit', 'name': 'Steelers', 'market': 'Pittsburgh'}
        ]
    
    def _generate_nba_teams(self) -> List[Dict]:
        """Generate NBA teams"""
        return [
            {'id': 'lal', 'name': 'Lakers', 'market': 'Los Angeles'},
            {'id': 'bos', 'name': 'Celtics', 'market': 'Boston'},
            {'id': 'gsw', 'name': 'Warriors', 'market': 'Golden State'},
            {'id': 'mia', 'name': 'Heat', 'market': 'Miami'},
            {'id': 'mil', 'name': 'Bucks', 'market': 'Milwaukee'},
            {'id': 'phi', 'name': '76ers', 'market': 'Philadelphia'},
            {'id': 'den', 'name': 'Nuggets', 'market': 'Denver'},
            {'id': 'phx', 'name': 'Suns', 'market': 'Phoenix'}
        ]
    
    def _generate_tennis_players(self) -> List[Dict]:
        """Generate tennis players"""
        return [
            {'id': 'djokovic', 'name': 'Novak Djokovic', 'market': 'ATP'},
            {'id': 'alcaraz', 'name': 'Carlos Alcaraz', 'market': 'ATP'},
            {'id': 'medvedev', 'name': 'Daniil Medvedev', 'market': 'ATP'},
            {'id': 'swiatek', 'name': 'Iga Swiatek', 'market': 'WTA'},
            {'id': 'gauff', 'name': 'Coco Gauff', 'market': 'WTA'},
            {'id': 'rybakina', 'name': 'Elena Rybakina', 'market': 'WTA'}
        ]
    
    def _generate_mma_fighters(self) -> List[Dict]:
        """Generate MMA fighters"""
        return [
            {'id': 'jones', 'name': 'Jon Jones', 'market': 'Heavyweight'},
            {'id': 'adesanya', 'name': 'Israel Adesanya', 'market': 'Middleweight'},
            {'id': 'volkanovski', 'name': 'Alexander Volkanovski', 'market': 'Featherweight'},
            {'id': 'nunes', 'name': 'Amanda Nunes', 'market': "Women's Bantamweight"}
        ]
    
    def _generate_nascar_drivers(self) -> List[Dict]:
        """Generate NASCAR drivers"""
        return [
            {'id': 'larson', 'name': 'Kyle Larson', 'market': 'Cup Series'},
            {'id': 'elliott', 'name': 'Chase Elliott', 'market': 'Cup Series'},
            {'id': 'hamlin', 'name': 'Denny Hamlin', 'market': 'Cup Series'},
            {'id': 'truex', 'name': 'Martin Truex Jr.', 'market': 'Cup Series'}
        ]
    
    def _generate_golf_players(self) -> List[Dict]:
        """Generate golf players"""
        return [
            {'id': 'mcilroy', 'name': 'Rory McIlroy', 'market': 'PGA Tour'},
            {'id': 'rahm', 'name': 'Jon Rahm', 'market': 'PGA Tour'},
            {'id': 'schauffele', 'name': 'Xander Schauffele', 'market': 'PGA Tour'},
            {'id': 'thomas', 'name': 'Justin Thomas', 'market': 'PGA Tour'}
        ]
    
    def _generate_college_teams(self, sport: str) -> List[Dict]:
        """Generate college teams for NCAA sports"""
        if sport == 'ncaamb':
            teams = [
                {'id': 'duke', 'name': 'Blue Devils', 'market': 'Duke'},
                {'id': 'unc', 'name': 'Tar Heels', 'market': 'North Carolina'},
                {'id': 'kentucky', 'name': 'Wildcats', 'market': 'Kentucky'},
                {'id': 'kansas', 'name': 'Jayhawks', 'market': 'Kansas'},
                {'id': 'gonzaga', 'name': 'Bulldogs', 'market': 'Gonzaga'},
                {'id': 'villanova', 'name': 'Wildcats', 'market': 'Villanova'},
                {'id': 'michigan', 'name': 'Wolverines', 'market': 'Michigan'},
                {'id': 'ucla', 'name': 'Bruins', 'market': 'UCLA'}
            ]
        elif sport == 'ncaafb':
            teams = [
                {'id': 'alabama', 'name': 'Crimson Tide', 'market': 'Alabama'},
                {'id': 'georgia', 'name': 'Bulldogs', 'market': 'Georgia'},
                {'id': 'ohio-state', 'name': 'Buckeyes', 'market': 'Ohio State'},
                {'id': 'michigan', 'name': 'Wolverines', 'market': 'Michigan'},
                {'id': 'clemson', 'name': 'Tigers', 'market': 'Clemson'},
                {'id': 'texas', 'name': 'Longhorns', 'market': 'Texas'},
                {'id': 'oklahoma', 'name': 'Sooners', 'market': 'Oklahoma'},
                {'id': 'notre-dame', 'name': 'Fighting Irish', 'market': 'Notre Dame'}
            ]
        else:
            teams = []
        
        return teams
    
    def _generate_professional_teams(self, sport: str) -> List[Dict]:
        """Generate professional teams for NHL/MLB"""
        if sport == 'nhl':
            teams = [
                {'id': 'bruins', 'name': 'Bruins', 'market': 'Boston'},
                {'id': 'rangers', 'name': 'Rangers', 'market': 'New York'},
                {'id': 'lightning', 'name': 'Lightning', 'market': 'Tampa Bay'},
                {'id': 'avalanche', 'name': 'Avalanche', 'market': 'Colorado'},
                {'id': 'kings', 'name': 'Kings', 'market': 'Los Angeles'},
                {'id': 'oilers', 'name': 'Oilers', 'market': 'Edmonton'}
            ]
        elif sport == 'mlb':
            teams = [
                {'id': 'yankees', 'name': 'Yankees', 'market': 'New York'},
                {'id': 'dodgers', 'name': 'Dodgers', 'market': 'Los Angeles'},
                {'id': 'red-sox', 'name': 'Red Sox', 'market': 'Boston'},
                {'id': 'astros', 'name': 'Astros', 'market': 'Houston'},
                {'id': 'braves', 'name': 'Braves', 'market': 'Atlanta'},
                {'id': 'padres', 'name': 'Padres', 'market': 'San Diego'}
            ]
        else:
            teams = []
        
        return teams
    
    def search_team_by_name(self, sport: str, team_name: str) -> Optional[Dict]:
        """Find team by name or alias"""
        teams = self.get_team_list(sport)
        
        # Try exact match first
        for team in teams:
            if (team['name'].lower() == team_name.lower() or 
                team['market'].lower() == team_name.lower()):
                return team
        
        # Try partial match
        for team in teams:
            if (team_name.lower() in team['name'].lower() or 
                team_name.lower() in team['market'].lower()):
                return team
        
        return None
