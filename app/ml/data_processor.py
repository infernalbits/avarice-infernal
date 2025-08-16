import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.models import Game, TeamStats, Bet
from app.api.sports_data import SportsDataAPI
from app import db

class DataProcessor:
    """
    Processes and updates sports data, team statistics, and historical information
    """
    
    def __init__(self):
        self.sports_api = SportsDataAPI()
    
    def update_team_stats(self, sport: str, season: str = None) -> Dict:
        """
        Update team statistics from external sources
        
        Args:
            sport: Sport to update (e.g., 'americanfootball_nfl')
            season: Season year (defaults to current)
            
        Returns:
            Update results
        """
        if not season:
            season = str(datetime.now().year)
        
        updated_teams = 0
        errors = []
        
        try:
            # Map sport keys to ESPN format
            sport_mapping = {
                'americanfootball_nfl': ('football', 'nfl'),
                'basketball_nba': ('basketball', 'nba'),
                'soccer_epl': ('soccer', 'eng.1')
            }
            
            if sport not in sport_mapping:
                return {'error': f'Unsupported sport: {sport}'}
            
            espn_sport, espn_league = sport_mapping[sport]
            
            # Get team data from ESPN
            teams_data = self.sports_api.get_espn_team_stats(espn_sport, espn_league)
            
            if not teams_data or 'sports' not in teams_data:
                return {'error': 'Failed to fetch team data from ESPN'}
            
            # Process each team
            for sport_data in teams_data['sports']:
                for league_data in sport_data.get('leagues', []):
                    for team_data in league_data.get('teams', []):
                        try:
                            team_info = team_data['team']
                            team_name = team_info['displayName']
                            
                            # Get or create team stats record
                            team_stats = TeamStats.query.filter_by(
                                team_name=team_name,
                                sport=sport,
                                season=season
                            ).first()
                            
                            if not team_stats:
                                team_stats = TeamStats(
                                    team_name=team_name,
                                    sport=sport,
                                    season=season
                                )
                                db.session.add(team_stats)
                            
                            # Update basic stats if available
                            record = team_info.get('record', {})
                            if 'items' in record:
                                for item in record['items']:
                                    if item['type'] == 'total':
                                        stats = item['stats']
                                        team_stats.wins = stats.get('wins', 0)
                                        team_stats.losses = stats.get('losses', 0)
                                        team_stats.draws = stats.get('ties', 0)
                                        team_stats.games_played = team_stats.wins + team_stats.losses + team_stats.draws
                            
                            # Calculate additional metrics from recent games
                            self._calculate_advanced_stats(team_stats, sport)
                            
                            updated_teams += 1
                            
                        except Exception as e:
                            errors.append(f"Error processing team {team_data.get('team', {}).get('displayName', 'Unknown')}: {str(e)}")
                            continue
            
            db.session.commit()
            
            return {
                'updated_teams': updated_teams,
                'errors': errors,
                'sport': sport,
                'season': season
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update team stats: {str(e)}'}
    
    def _calculate_advanced_stats(self, team_stats: TeamStats, sport: str):
        """Calculate advanced statistics for a team"""
        # Get recent games for this team
        recent_games = Game.query.filter(
            db.or_(
                Game.home_team == team_stats.team_name,
                Game.away_team == team_stats.team_name
            ),
            Game.sport == sport,
            Game.completed == True,
            Game.home_score.isnot(None),
            Game.away_score.isnot(None)
        ).order_by(Game.commence_time.desc()).limit(20).all()
        
        if not recent_games:
            return
        
        # Calculate scoring averages
        points_for = []
        points_against = []
        recent_results = []
        home_games = []
        away_games = []
        
        for game in recent_games:
            is_home = (game.home_team == team_stats.team_name)
            
            if is_home:
                team_score = game.home_score
                opponent_score = game.away_score
                home_games.append(game)
            else:
                team_score = game.away_score
                opponent_score = game.home_score
                away_games.append(game)
            
            points_for.append(team_score)
            points_against.append(opponent_score)
            
            # Determine result
            if team_score > opponent_score:
                recent_results.append('W')
            elif team_score < opponent_score:
                recent_results.append('L')
            else:
                recent_results.append('D')
        
        # Update basic stats
        if points_for:
            team_stats.avg_points_for = sum(points_for) / len(points_for)
            team_stats.avg_points_against = sum(points_against) / len(points_against)
            team_stats.points_for = sum(points_for)
            team_stats.points_against = sum(points_against)
        
        # Recent form (last 5 games)
        if len(recent_results) >= 5:
            team_stats.recent_form = ''.join(recent_results[:5])
            recent_5_for = points_for[:5]
            recent_5_against = points_against[:5]
            team_stats.recent_avg_points_for = sum(recent_5_for) / len(recent_5_for)
            team_stats.recent_avg_points_against = sum(recent_5_against) / len(recent_5_against)
        
        # Home/Away splits
        home_wins = sum(1 for game in home_games if game.home_score > game.away_score)
        home_losses = sum(1 for game in home_games if game.home_score < game.away_score)
        away_wins = sum(1 for game in away_games if game.away_score > game.home_score)
        away_losses = sum(1 for game in away_games if game.away_score < game.home_score)
        
        team_stats.home_wins = home_wins
        team_stats.home_losses = home_losses
        team_stats.away_wins = away_wins
        team_stats.away_losses = away_losses
        
        # Calculate efficiency metrics
        if team_stats.avg_points_for > 0:
            # Simple efficiency calculation (can be enhanced with more advanced metrics)
            team_stats.offensive_efficiency = team_stats.avg_points_for / 100.0  # Normalized
            team_stats.defensive_efficiency = max(0, 100.0 - team_stats.avg_points_against) / 100.0
        
        # Update timestamp
        team_stats.last_updated = datetime.utcnow()
    
    def update_game_results(self, sport: str = None) -> Dict:
        """
        Update game results for completed games
        
        Args:
            sport: Specific sport to update (optional)
            
        Returns:
            Update results
        """
        updated_games = 0
        errors = []
        
        try:
            # Get games that need result updates (recently completed)
            query = Game.query.filter(
                Game.completed == False,
                Game.commence_time < datetime.utcnow()
            )
            
            if sport:
                query = query.filter(Game.sport == sport)
            
            pending_games = query.all()
            
            # Map sport to ESPN format for getting scores
            sport_mapping = {
                'americanfootball_nfl': ('football', 'nfl'),
                'basketball_nba': ('basketball', 'nba'),
                'soccer_epl': ('soccer', 'eng.1')
            }
            
            for game in pending_games:
                try:
                    if game.sport in sport_mapping:
                        espn_sport, espn_league = sport_mapping[game.sport]
                        
                        # Get recent scores
                        scores_data = self.sports_api.get_espn_scores(espn_sport, espn_league)
                        
                        if scores_data and 'events' in scores_data:
                            # Look for matching game
                            for event in scores_data['events']:
                                competitors = event.get('competitions', [{}])[0].get('competitors', [])
                                
                                if len(competitors) >= 2:
                                    home_competitor = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                                    away_competitor = next((c for c in competitors if c.get('homeAway') == 'away'), None)
                                    
                                    if (home_competitor and away_competitor and
                                        home_competitor['team']['displayName'] == game.home_team and
                                        away_competitor['team']['displayName'] == game.away_team):
                                        
                                        # Check if game is completed
                                        status = event.get('status', {})
                                        if status.get('type', {}).get('completed'):
                                            game.home_score = int(home_competitor.get('score', 0))
                                            game.away_score = int(away_competitor.get('score', 0))
                                            game.completed = True
                                            updated_games += 1
                                            break
                    
                except Exception as e:
                    errors.append(f"Error updating game {game.external_id}: {str(e)}")
                    continue
            
            db.session.commit()
            
            # Update related bet results
            self._update_bet_results()
            
            return {
                'updated_games': updated_games,
                'errors': errors
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update game results: {str(e)}'}
    
    def _update_bet_results(self):
        """Update bet results based on completed games"""
        # Get pending bets for completed games
        pending_bets = db.session.query(Bet, Game).join(
            Game, Bet.game_id == Game.external_id
        ).filter(
            Bet.result.is_(None),
            Game.completed == True
        ).all()
        
        for bet, game in pending_bets:
            try:
                # Determine bet outcome
                actual_outcome = self._determine_bet_outcome(bet, game)
                
                if actual_outcome == bet.bet_value:
                    bet.result = 'win'
                    # Calculate profit
                    if bet.odds > 0:
                        bet.profit_loss = bet.stake * (bet.odds / 100)
                    else:
                        bet.profit_loss = bet.stake * (100 / abs(bet.odds))
                elif actual_outcome == 'push':
                    bet.result = 'push'
                    bet.profit_loss = 0.0
                else:
                    bet.result = 'loss'
                    bet.profit_loss = -bet.stake
                
                bet.settled_at = datetime.utcnow()
                
                # Update bankroll
                bankroll = Bankroll.query.first()
                if bankroll:
                    bankroll.update_after_bet(bet.result, bet.stake, bet.profit_loss)
                
            except Exception as e:
                print(f"Error updating bet {bet.id}: {e}")
                continue
    
    def _determine_bet_outcome(self, bet: Bet, game: Game) -> str:
        """Determine the outcome of a bet based on game results"""
        if bet.bet_type == 'moneyline':
            if game.home_score > game.away_score:
                return 'home'
            elif game.away_score > game.home_score:
                return 'away'
            else:
                return 'draw'
        
        elif bet.bet_type == 'spread':
            if game.point_spread:
                home_cover = (game.home_score - game.away_score) > game.point_spread
                return 'home' if home_cover else 'away'
        
        elif bet.bet_type == 'totals':
            if game.total_points:
                total_score = game.home_score + game.away_score
                if total_score == game.total_points:
                    return 'push'
                return 'over' if total_score > game.total_points else 'under'
        
        return 'unknown'
    
    def generate_historical_data(self, sport: str, days_back: int = 90) -> Dict:
        """
        Generate historical data for model training and backtesting
        
        Args:
            sport: Sport to generate data for
            days_back: Number of days to go back
            
        Returns:
            Generated data summary
        """
        try:
            # This would typically involve:
            # 1. Fetching historical odds data
            # 2. Generating synthetic team statistics based on known performance patterns
            # 3. Creating realistic game scenarios
            
            start_date = datetime.utcnow() - timedelta(days=days_back)
            teams = self._get_sport_teams(sport)
            
            if not teams:
                return {'error': f'No teams found for sport: {sport}'}
            
            generated_games = 0
            
            # Generate games for each week
            current_date = start_date
            while current_date < datetime.utcnow():
                # Generate 10-15 games per week
                num_games = np.random.randint(10, 16)
                
                for _ in range(num_games):
                    try:
                        # Select random teams
                        home_team, away_team = np.random.choice(teams, 2, replace=False)
                        
                        # Generate realistic game data
                        game_data = self._generate_synthetic_game(
                            home_team, away_team, current_date, sport
                        )
                        
                        # Check if game already exists
                        existing_game = Game.query.filter_by(
                            external_id=game_data['external_id']
                        ).first()
                        
                        if not existing_game:
                            new_game = Game(**game_data)
                            db.session.add(new_game)
                            generated_games += 1
                    
                    except Exception as e:
                        print(f"Error generating game: {e}")
                        continue
                
                current_date += timedelta(days=7)  # Move to next week
            
            db.session.commit()
            
            return {
                'generated_games': generated_games,
                'sport': sport,
                'period': f'{days_back} days',
                'start_date': start_date.date().isoformat(),
                'end_date': datetime.utcnow().date().isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to generate historical data: {str(e)}'}
    
    def _get_sport_teams(self, sport: str) -> List[str]:
        """Get list of teams for a sport"""
        team_lists = {
            'americanfootball_nfl': [
                'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills',
                'Carolina Panthers', 'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns',
                'Dallas Cowboys', 'Denver Broncos', 'Detroit Lions', 'Green Bay Packers',
                'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs',
                'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
                'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants',
                'New York Jets', 'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers',
                'Seattle Seahawks', 'Tampa Bay Buccaneers', 'Tennessee Titans', 'Washington Commanders'
            ],
            'basketball_nba': [
                'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
                'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
                'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
                'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
                'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
                'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
                'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
                'Utah Jazz', 'Washington Wizards'
            ]
        }
        
        return team_lists.get(sport, [])
    
    def _generate_synthetic_game(self, home_team: str, away_team: str, 
                                game_date: datetime, sport: str) -> Dict:
        """Generate realistic synthetic game data"""
        
        # Generate external ID
        external_id = f"synthetic_{sport}_{hash(f'{home_team}_{away_team}_{game_date.isoformat()}') % 1000000}"
        
        # Generate realistic scores based on sport
        if sport == 'americanfootball_nfl':
            home_score = np.random.normal(24, 8)
            away_score = np.random.normal(21, 8)
            total_base = 45
        elif sport == 'basketball_nba':
            home_score = np.random.normal(110, 12)
            away_score = np.random.normal(108, 12)
            total_base = 220
        else:
            home_score = np.random.normal(2, 1)
            away_score = np.random.normal(1.5, 1)
            total_base = 2.5
        
        home_score = max(0, int(home_score))
        away_score = max(0, int(away_score))
        
        # Generate odds based on scores (reverse engineering)
        score_diff = home_score - away_score
        
        # Moneyline odds
        if score_diff > 0:
            home_odds = np.random.randint(-200, -110)
            away_odds = np.random.randint(110, 200)
        else:
            home_odds = np.random.randint(110, 200)
            away_odds = np.random.randint(-200, -110)
        
        # Point spread
        point_spread = np.random.uniform(-10, 10)
        
        # Total points
        actual_total = home_score + away_score
        total_points = actual_total + np.random.uniform(-5, 5)
        
        return {
            'external_id': external_id,
            'sport': sport,
            'home_team': home_team,
            'away_team': away_team,
            'commence_time': game_date,
            'completed': True,
            'home_score': home_score,
            'away_score': away_score,
            'home_odds': home_odds,
            'away_odds': away_odds,
            'point_spread': point_spread,
            'total_points': total_points,
            'over_odds': -110,
            'under_odds': -110
        }
