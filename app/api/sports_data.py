import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

class SportsDataAPI:
    """Handles fetching data from various sports APIs"""
    
    def __init__(self):
        self.odds_api_key = Config.ODDS_API_KEY
        self.odds_base_url = Config.ODDS_API_BASE_URL
        self.espn_base_url = Config.ESPN_API_BASE_URL
        
    def get_odds_data(self, sport: str, region: str = 'us', markets: str = 'h2h,spreads,totals') -> Optional[List[Dict]]:
        """
        Fetch odds data from The Odds API
        
        Args:
            sport: Sport key (e.g., 'americanfootball_nfl', 'basketball_nba')
            region: Region for odds (us, uk, au)
            markets: Markets to fetch (h2h, spreads, totals)
        """
        try:
            url = f"{self.odds_base_url}/sports/{sport}/odds"
            params = {
                'apiKey': self.odds_api_key,
                'regions': region,
                'markets': markets,
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching odds data: {e}")
            return None
    
    def get_espn_team_stats(self, sport: str, league: str) -> Optional[Dict]:
        """
        Fetch team statistics from ESPN API
        
        Args:
            sport: Sport name (e.g., 'football', 'basketball')
            league: League name (e.g., 'nfl', 'nba')
        """
        try:
            url = f"{self.espn_base_url}/{sport}/{league}/teams"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching ESPN team stats: {e}")
            return None
    
    def get_espn_scores(self, sport: str, league: str, limit: int = 50) -> Optional[Dict]:
        """
        Fetch recent scores from ESPN API
        
        Args:
            sport: Sport name (e.g., 'football', 'basketball')
            league: League name (e.g., 'nfl', 'nba')
            limit: Number of games to fetch
        """
        try:
            url = f"{self.espn_base_url}/{sport}/{league}/scoreboard"
            params = {
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching ESPN scores: {e}")
            return None
    
    def get_historical_odds(self, sport: str, date_from: str, date_to: str = None) -> Optional[List[Dict]]:
        """
        Fetch historical odds data
        
        Args:
            sport: Sport key
            date_from: Start date (ISO format)
            date_to: End date (ISO format, optional)
        """
        try:
            url = f"{self.odds_base_url}/sports/{sport}/odds-history"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'american',
                'dateFormat': 'iso',
                'date': date_from
            }
            
            if date_to:
                params['dateTo'] = date_to
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical odds: {e}")
            return None
    
    def parse_odds_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Parse raw odds data into standardized format
        
        Args:
            raw_data: Raw API response data
            
        Returns:
            List of parsed game data
        """
        parsed_games = []
        
        for game in raw_data:
            try:
                game_data = {
                    'external_id': game['id'],
                    'sport': game['sport_key'],
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'commence_time': datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00')),
                    'bookmakers': []
                }
                
                # Parse bookmaker odds
                for bookmaker in game.get('bookmakers', []):
                    bookmaker_data = {
                        'name': bookmaker['key'],
                        'markets': {}
                    }
                    
                    for market in bookmaker.get('markets', []):
                        market_key = market['key']
                        outcomes = {}
                        
                        for outcome in market.get('outcomes', []):
                            outcomes[outcome['name']] = {
                                'price': outcome['price'],
                                'point': outcome.get('point')
                            }
                        
                        bookmaker_data['markets'][market_key] = outcomes
                    
                    game_data['bookmakers'].append(bookmaker_data)
                
                parsed_games.append(game_data)
                
            except (KeyError, ValueError) as e:
                print(f"Error parsing game data: {e}")
                continue
        
        return parsed_games
    
    def get_consensus_odds(self, game_data: Dict) -> Dict:
        """
        Calculate consensus odds from multiple bookmakers
        
        Args:
            game_data: Parsed game data with bookmaker odds
            
        Returns:
            Dictionary with consensus odds
        """
        consensus = {
            'moneyline': {},
            'spread': {},
            'total': {}
        }
        
        # Collect all odds for averaging
        moneyline_odds = {'home': [], 'away': [], 'draw': []}
        spread_odds = {'home': [], 'away': []}
        total_odds = {'over': [], 'under': []}
        spread_values = []
        total_values = []
        
        for bookmaker in game_data.get('bookmakers', []):
            markets = bookmaker.get('markets', {})
            
            # Moneyline
            if 'h2h' in markets:
                h2h = markets['h2h']
                if game_data['home_team'] in h2h:
                    moneyline_odds['home'].append(h2h[game_data['home_team']]['price'])
                if game_data['away_team'] in h2h:
                    moneyline_odds['away'].append(h2h[game_data['away_team']]['price'])
                if 'Draw' in h2h:
                    moneyline_odds['draw'].append(h2h['Draw']['price'])
            
            # Spreads
            if 'spreads' in markets:
                spreads = markets['spreads']
                for team, data in spreads.items():
                    if team == game_data['home_team']:
                        spread_odds['home'].append(data['price'])
                        if data.get('point'):
                            spread_values.append(data['point'])
                    elif team == game_data['away_team']:
                        spread_odds['away'].append(data['price'])
            
            # Totals
            if 'totals' in markets:
                totals = markets['totals']
                if 'Over' in totals:
                    total_odds['over'].append(totals['Over']['price'])
                    if totals['Over'].get('point'):
                        total_values.append(totals['Over']['point'])
                if 'Under' in totals:
                    total_odds['under'].append(totals['Under']['price'])
        
        # Calculate averages
        for market, odds in moneyline_odds.items():
            if odds:
                consensus['moneyline'][market] = sum(odds) / len(odds)
        
        for market, odds in spread_odds.items():
            if odds:
                consensus['spread'][market] = sum(odds) / len(odds)
        
        if spread_values:
            consensus['spread']['line'] = sum(spread_values) / len(spread_values)
        
        for market, odds in total_odds.items():
            if odds:
                consensus['total'][market] = sum(odds) / len(odds)
        
        if total_values:
            consensus['total']['line'] = sum(total_values) / len(total_values)
        
        return consensus
