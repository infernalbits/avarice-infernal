import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import asyncio
from app.api.live_data_client import LiveDataClient
from app.models import Game, TeamStats

class EnhancedFeatureEngine:
    """
    Advanced feature engineering with public betting data, sharp money indicators,
    Vegas consensus, and comprehensive team analytics
    """
    
    def __init__(self):
        self.live_client = LiveDataClient()
        self.feature_cache = {}
        
    async def extract_comprehensive_features(self, game: Game) -> Dict[str, float]:
        """
        Extract comprehensive feature set including:
        - Basic team statistics
        - Public betting percentages
        - Sharp money indicators
        - Vegas consensus data
        - Weather and situational factors
        - Advanced analytics
        """
        features = {}
        
        # Basic team features
        basic_features = await self._extract_basic_team_features(game)
        features.update(basic_features)
        
        # Public betting and market features
        market_features = await self._extract_market_features(game)
        features.update(market_features)
        
        # Sharp money and professional betting features
        sharp_features = await self._extract_sharp_money_features(game)
        features.update(sharp_features)
        
        # Vegas consensus and line movement features
        vegas_features = await self._extract_vegas_features(game)
        features.update(vegas_features)
        
        # Advanced team analytics
        advanced_features = await self._extract_advanced_analytics(game)
        features.update(advanced_features)
        
        # Situational and contextual features
        situational_features = await self._extract_situational_features(game)
        features.update(situational_features)
        
        # Weather features (for outdoor sports)
        if game.sport in ['americanfootball_nfl']:
            weather_features = await self._extract_weather_features(game)
            features.update(weather_features)
        
        return features
    
    async def _extract_basic_team_features(self, game: Game) -> Dict[str, float]:
        """Extract basic team performance features"""
        features = {}
        
        # Get team stats
        home_stats = await self._get_team_stats(game.home_team, game.sport)
        away_stats = await self._get_team_stats(game.away_team, game.sport)
        
        if home_stats and away_stats:
            # Basic performance metrics
            features.update({
                'home_win_pct': home_stats.get('win_percentage', 0.5),
                'away_win_pct': away_stats.get('win_percentage', 0.5),
                'home_ppg': home_stats.get('avg_points_for', 0),
                'away_ppg': away_stats.get('avg_points_for', 0),
                'home_papg': home_stats.get('avg_points_against', 0),
                'away_papg': away_stats.get('avg_points_against', 0),
                'home_point_diff': home_stats.get('point_differential', 0),
                'away_point_diff': away_stats.get('point_differential', 0),
                
                # Performance differentials
                'win_pct_diff': home_stats.get('win_percentage', 0.5) - away_stats.get('win_percentage', 0.5),
                'ppg_diff': home_stats.get('avg_points_for', 0) - away_stats.get('avg_points_for', 0),
                'papg_diff': home_stats.get('avg_points_against', 0) - away_stats.get('avg_points_against', 0),
                'point_diff_advantage': home_stats.get('point_differential', 0) - away_stats.get('point_differential', 0)
            })
        
        return features
    
    async def _extract_market_features(self, game: Game) -> Dict[str, float]:
        """Extract public betting and market sentiment features"""
        features = {}
        
        try:
            # Get public betting data
            public_data = await self.live_client.get_public_betting_data(game.sport)
            
            # Find our game in the public data
            game_public_data = None
            for game_data in public_data.get('games', []):
                if (game_data['home_team'] == game.home_team and 
                    game_data['away_team'] == game.away_team):
                    game_public_data = game_data
                    break
            
            if game_public_data:
                public_betting = game_public_data['public_betting']
                betting_handle = game_public_data['betting_handle']
                
                features.update({
                    # Public betting percentages
                    'public_ml_home_pct': public_betting['moneyline']['home_percentage'] / 100,
                    'public_spread_home_pct': public_betting['spread']['home_percentage'] / 100,
                    'public_total_over_pct': public_betting['total']['over_percentage'] / 100,
                    
                    # Handle vs ticket disparities (sharp vs public indicators)
                    'handle_ticket_disparity': betting_handle['ticket_count_disparity'] / 100,
                    'reverse_line_movement': 1.0 if betting_handle['reverse_line_movement'] else 0.0,
                    
                    # Market sentiment features
                    'public_consensus_strength': max(
                        public_betting['moneyline']['home_percentage'],
                        public_betting['moneyline']['away_percentage']
                    ) / 100,
                    
                    # Contrarian indicators
                    'contrarian_ml_opportunity': 1.0 if public_betting['moneyline']['home_percentage'] > 70 or 
                                                       public_betting['moneyline']['home_percentage'] < 30 else 0.0,
                    'contrarian_spread_opportunity': 1.0 if public_betting['spread']['home_percentage'] > 75 or 
                                                          public_betting['spread']['home_percentage'] < 25 else 0.0
                })
        
        except Exception as e:
            print(f"Error extracting market features: {e}")
            # Default values if data unavailable
            features.update({
                'public_ml_home_pct': 0.5,
                'public_spread_home_pct': 0.5,
                'public_total_over_pct': 0.5,
                'handle_ticket_disparity': 0.0,
                'reverse_line_movement': 0.0,
                'public_consensus_strength': 0.5,
                'contrarian_ml_opportunity': 0.0,
                'contrarian_spread_opportunity': 0.0
            })
        
        return features
    
    async def _extract_sharp_money_features(self, game: Game) -> Dict[str, float]:
        """Extract sharp money and professional betting indicators"""
        features = {}
        
        try:
            public_data = await self.live_client.get_public_betting_data(game.sport)
            
            # Find game data
            game_data = next((g for g in public_data.get('games', []) 
                            if g['home_team'] == game.home_team and g['away_team'] == game.away_team), None)
            
            if game_data:
                sharp_money = game_data['sharp_money']
                steam_moves = game_data['steam_moves']
                
                features.update({
                    # Sharp money direction
                    'sharp_ml_lean_home': 1.0 if sharp_money['moneyline_lean'] == 'home' else 0.0,
                    'sharp_spread_lean_home': 1.0 if sharp_money['spread_lean'] == 'home' else 0.0,
                    'sharp_confidence': sharp_money['confidence'] / 100,
                    
                    # Steam move detection
                    'steam_move_detected': 1.0 if steam_moves['detected'] else 0.0,
                    'steam_move_magnitude': steam_moves['magnitude'],
                    'steam_move_home': 1.0 if steam_moves['direction'] in ['home', 'over'] else 0.0,
                    
                    # Sharp vs public disagreement (fade the public spots)
                    'sharp_public_disagree_ml': 1.0 if (
                        (sharp_money['moneyline_lean'] == 'home' and game_data['public_betting']['moneyline']['home_percentage'] < 40) or
                        (sharp_money['moneyline_lean'] == 'away' and game_data['public_betting']['moneyline']['home_percentage'] > 60)
                    ) else 0.0,
                    
                    'sharp_public_disagree_spread': 1.0 if (
                        (sharp_money['spread_lean'] == 'home' and game_data['public_betting']['spread']['home_percentage'] < 45) or
                        (sharp_money['spread_lean'] == 'away' and game_data['public_betting']['spread']['home_percentage'] > 55)
                    ) else 0.0
                })
        
        except Exception as e:
            print(f"Error extracting sharp money features: {e}")
            features.update({
                'sharp_ml_lean_home': 0.5,
                'sharp_spread_lean_home': 0.5,
                'sharp_confidence': 0.5,
                'steam_move_detected': 0.0,
                'steam_move_magnitude': 0.0,
                'steam_move_home': 0.5,
                'sharp_public_disagree_ml': 0.0,
                'sharp_public_disagree_spread': 0.0
            })
        
        return features
    
    async def _extract_vegas_features(self, game: Game) -> Dict[str, float]:
        """Extract Vegas consensus and line movement features"""
        features = {}
        
        try:
            # Vegas consensus data
            vegas_data = await self.live_client.get_vegas_consensus(game.sport)
            
            # Line movement data
            movement_data = await self.live_client._fetch_line_movements(game.sport)
            
            consensus = vegas_data['consensus_lines']
            market_maker = vegas_data['market_maker_moves']
            sharp_books = vegas_data['sharp_book_consensus']
            clv = vegas_data['closing_line_value']
            
            features.update({
                # Vegas consensus
                'vegas_spread_consensus': consensus['spread_consensus'],
                'vegas_total_consensus': consensus['total_consensus'],
                'vegas_ml_consensus': self._normalize_ml_odds(consensus['ml_consensus']),
                
                # Market maker movements
                'pinnacle_moved': 1.0 if market_maker['pinnacle_move'] else 0.0,
                'circa_moved': 1.0 if market_maker['circa_move'] else 0.0,
                'mm_move_direction': self._encode_direction(market_maker['move_direction']),
                
                # Sharp book consensus variance
                'sharp_book_variance': np.std([
                    sharp_books['pinnacle'],
                    sharp_books['bookmaker'],
                    sharp_books['betcris']
                ]),
                
                # Closing line value potential
                'clv_available': 1.0 if clv['clv_available'] else 0.0,
                'estimated_clv': clv['estimated_clv'],
                
                # Line movement features
                'recent_line_moves': len([m for m in movement_data if 
                                        datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) > 
                                        datetime.utcnow() - timedelta(hours=2)]),
                'sharp_trigger_moves': len([m for m in movement_data if m['trigger'] == 'sharp_money'])
            })
            
            # Current vs opening line differential
            if game.point_spread and game.total_points:
                features.update({
                    'spread_line_move': abs(game.point_spread - consensus['spread_consensus']),
                    'total_line_move': abs(game.total_points - consensus['total_consensus'])
                })
        
        except Exception as e:
            print(f"Error extracting Vegas features: {e}")
            features.update({
                'vegas_spread_consensus': 0.0,
                'vegas_total_consensus': 45.0,
                'vegas_ml_consensus': 0.0,
                'pinnacle_moved': 0.0,
                'circa_moved': 0.0,
                'mm_move_direction': 0.0,
                'sharp_book_variance': 0.0,
                'clv_available': 0.0,
                'estimated_clv': 0.0,
                'recent_line_moves': 0.0,
                'sharp_trigger_moves': 0.0,
                'spread_line_move': 0.0,
                'total_line_move': 0.0
            })
        
        return features
    
    async def _extract_advanced_analytics(self, game: Game) -> Dict[str, float]:
        """Extract advanced team analytics and efficiency metrics"""
        features = {}
        
        try:
            # Get enhanced team stats
            home_enhanced = await self.live_client.get_enhanced_team_stats(game.home_team, game.sport)
            away_enhanced = await self.live_client.get_enhanced_team_stats(game.away_team, game.sport)
            
            home_advanced = home_enhanced.get('advanced_metrics', {})
            away_advanced = away_enhanced.get('advanced_metrics', {})
            
            home_situational = home_enhanced.get('situational', {})
            away_situational = away_enhanced.get('situational', {})
            
            features.update({
                # Advanced efficiency metrics
                'home_off_efficiency': home_advanced.get('offensive_efficiency', 100),
                'away_off_efficiency': away_advanced.get('offensive_efficiency', 100),
                'home_def_efficiency': home_advanced.get('defensive_efficiency', 100),
                'away_def_efficiency': away_advanced.get('defensive_efficiency', 100),
                
                # Efficiency advantages
                'off_efficiency_diff': home_advanced.get('offensive_efficiency', 100) - away_advanced.get('defensive_efficiency', 100),
                'def_efficiency_diff': away_advanced.get('offensive_efficiency', 100) - home_advanced.get('defensive_efficiency', 100),
                
                # Pace and style factors
                'home_pace': home_advanced.get('pace', 70),
                'away_pace': away_advanced.get('pace', 70),
                'pace_differential': abs(home_advanced.get('pace', 70) - away_advanced.get('pace', 70)),
                
                # Shooting and turnover metrics
                'home_ts_pct': home_advanced.get('true_shooting_percentage', 0.55),
                'away_ts_pct': away_advanced.get('true_shooting_percentage', 0.55),
                'home_turnover_rate': home_advanced.get('turnover_rate', 0.15),
                'away_turnover_rate': away_advanced.get('turnover_rate', 0.15),
                
                # Situational performance
                'home_vs_winning_teams': home_situational.get('vs_winning_teams', 0.5),
                'away_vs_winning_teams': away_situational.get('vs_winning_teams', 0.5),
                'home_in_close_games': home_situational.get('in_close_games', 0.5),
                'away_in_close_games': away_situational.get('in_close_games', 0.5),
                'home_rest_advantage': home_situational.get('rest_advantage', 0.5),
                'away_rest_advantage': away_situational.get('rest_advantage', 0.5)
            })
        
        except Exception as e:
            print(f"Error extracting advanced analytics: {e}")
            # Default advanced features
            features.update({
                'home_off_efficiency': 100, 'away_off_efficiency': 100,
                'home_def_efficiency': 100, 'away_def_efficiency': 100,
                'off_efficiency_diff': 0, 'def_efficiency_diff': 0,
                'home_pace': 70, 'away_pace': 70, 'pace_differential': 0,
                'home_ts_pct': 0.55, 'away_ts_pct': 0.55,
                'home_turnover_rate': 0.15, 'away_turnover_rate': 0.15,
                'home_vs_winning_teams': 0.5, 'away_vs_winning_teams': 0.5,
                'home_in_close_games': 0.5, 'away_in_close_games': 0.5,
                'home_rest_advantage': 0.5, 'away_rest_advantage': 0.5
            })
        
        return features
    
    async def _extract_situational_features(self, game: Game) -> Dict[str, float]:
        """Extract situational and contextual features"""
        features = {}
        
        # Time-based features
        game_time = game.commence_time
        features.update({
            'day_of_week': game_time.weekday(),
            'hour_of_day': game_time.hour,
            'is_weekend': 1.0 if game_time.weekday() >= 5 else 0.0,
            'is_primetime': 1.0 if 19 <= game_time.hour <= 23 else 0.0,
            'days_until_game': (game_time - datetime.utcnow()).days
        })
        
        # Season timing
        try:
            # Approximate season week (would be more precise with real data)
            season_start = datetime(game_time.year, 9, 1)  # Approximate
            week_of_season = max(1, (game_time - season_start).days // 7)
            features.update({
                'week_of_season': week_of_season,
                'early_season': 1.0 if week_of_season <= 4 else 0.0,
                'mid_season': 1.0 if 5 <= week_of_season <= 12 else 0.0,
                'late_season': 1.0 if week_of_season >= 13 else 0.0
            })
        except:
            features.update({'week_of_season': 8, 'early_season': 0, 'mid_season': 1, 'late_season': 0})
        
        # Division/Conference features (would need real data)
        features.update({
            'division_game': 0.3,  # Mock probability
            'conference_game': 0.6,  # Mock probability
            'rivalry_game': 0.1   # Mock probability
        })
        
        return features
    
    async def _extract_weather_features(self, game: Game) -> Dict[str, float]:
        """Extract weather features for outdoor sports"""
        features = {}
        
        try:
            weather = await self.live_client.get_weather_data("stadium", game.commence_time)
            
            features.update({
                'temperature': weather['temperature'],
                'wind_speed': weather['wind_speed'],
                'precipitation': weather['precipitation'],
                'humidity': weather['humidity'] / 100,
                'weather_impact_score': weather['impact_score'],
                
                # Weather condition flags
                'is_cold': 1.0 if weather['temperature'] < 40 else 0.0,
                'is_hot': 1.0 if weather['temperature'] > 80 else 0.0,
                'is_windy': 1.0 if weather['wind_speed'] > 15 else 0.0,
                'is_wet': 1.0 if weather['precipitation'] > 0.1 else 0.0
            })
        
        except Exception as e:
            print(f"Error extracting weather features: {e}")
            features.update({
                'temperature': 70, 'wind_speed': 5, 'precipitation': 0,
                'humidity': 0.5, 'weather_impact_score': 0,
                'is_cold': 0, 'is_hot': 0, 'is_windy': 0, 'is_wet': 0
            })
        
        return features
    
    async def _get_team_stats(self, team_name: str, sport: str) -> Dict:
        """Get team statistics from database or API"""
        # This would query the database or API for team stats
        # For now, return mock data
        return {
            'win_percentage': 0.65,
            'avg_points_for': 28.5,
            'avg_points_against': 22.3,
            'point_differential': 6.2
        }
    
    def _normalize_ml_odds(self, odds: float) -> float:
        """Normalize moneyline odds to probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def _encode_direction(self, direction: str) -> float:
        """Encode direction as numeric value"""
        direction_map = {'up': 1.0, 'down': -1.0, 'stable': 0.0}
        return direction_map.get(direction, 0.0)
    
    def get_feature_importance_groups(self) -> Dict[str, List[str]]:
        """Return feature groups for analysis"""
        return {
            'team_performance': [
                'home_win_pct', 'away_win_pct', 'win_pct_diff',
                'home_ppg', 'away_ppg', 'ppg_diff',
                'home_point_diff', 'away_point_diff', 'point_diff_advantage'
            ],
            'public_betting': [
                'public_ml_home_pct', 'public_spread_home_pct', 'public_total_over_pct',
                'public_consensus_strength', 'contrarian_ml_opportunity', 'contrarian_spread_opportunity'
            ],
            'sharp_money': [
                'sharp_ml_lean_home', 'sharp_spread_lean_home', 'sharp_confidence',
                'sharp_public_disagree_ml', 'sharp_public_disagree_spread',
                'steam_move_detected', 'steam_move_magnitude'
            ],
            'vegas_lines': [
                'vegas_spread_consensus', 'vegas_total_consensus', 'vegas_ml_consensus',
                'pinnacle_moved', 'circa_moved', 'clv_available', 'estimated_clv'
            ],
            'advanced_analytics': [
                'home_off_efficiency', 'away_off_efficiency', 'off_efficiency_diff',
                'home_def_efficiency', 'away_def_efficiency', 'def_efficiency_diff',
                'pace_differential', 'home_ts_pct', 'away_ts_pct'
            ],
            'situational': [
                'is_weekend', 'is_primetime', 'division_game', 'conference_game',
                'early_season', 'mid_season', 'late_season'
            ],
            'weather': [
                'temperature', 'wind_speed', 'weather_impact_score',
                'is_cold', 'is_hot', 'is_windy', 'is_wet'
            ]
        }
