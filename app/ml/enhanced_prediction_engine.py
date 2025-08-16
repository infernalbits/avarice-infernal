import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

from .advanced_ensemble_model import AdvancedEnsembleModel
from .advanced_data_integration import AdvancedDataIntegration

class EnhancedPredictionEngine:
    """
    Enhanced prediction engine that combines advanced ML models with comprehensive data integration
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.ensemble_model = AdvancedEnsembleModel()
        self.data_integration = AdvancedDataIntegration(config)
        self.feature_columns = []
        self.is_trained = False
        self.prediction_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def train_enhanced_model(self, historical_data: pd.DataFrame, target_column: str = 'outcome'):
        """Train the enhanced model with comprehensive data integration"""
        
        self.logger.info("Starting enhanced model training...")
        
        # Define feature columns
        self.feature_columns = [
            'home_team_win_rate', 'away_team_win_rate',
            'home_team_recent_form', 'away_team_recent_form',
            'home_team_rest_days', 'away_team_rest_days',
            'home_team_injuries', 'away_team_injuries',
            'h2h_home_wins', 'h2h_away_wins',
            'public_betting_percentage', 'sharp_money_percentage',
            'weather_impact_score', 'sentiment_score',
            'market_efficiency_score', 'rest_advantage',
            'injury_advantage', 'momentum_advantage'
        ]
        
        # Ensure all required features exist
        missing_features = [col for col in self.feature_columns if col not in historical_data.columns]
        if missing_features:
            self.logger.warning(f"Missing features: {missing_features}")
            # Add missing features with default values
            for feature in missing_features:
                historical_data[feature] = 0.0
        
        # Prepare training data
        X = historical_data[self.feature_columns]
        y = historical_data[target_column]
        
        # Train the ensemble model
        cv_scores = self.ensemble_model.train_models(X, y, self.feature_columns)
        
        self.is_trained = True
        self.logger.info("Enhanced model training completed!")
        self.logger.info(f"Cross-validation scores: {cv_scores}")
        
        return cv_scores
    
    async def generate_enhanced_predictions(self, games: List[Dict], teams: List[str]) -> List[Dict]:
        """Generate enhanced predictions with comprehensive data integration"""
        
        if not self.is_trained:
            raise ValueError("Model must be trained before generating predictions")
        
        self.logger.info(f"Generating enhanced predictions for {len(games)} games...")
        
        enhanced_predictions = []
        
        for game in games:
            try:
                # Get comprehensive data for the teams
                home_team = game.get('home_team', '').lower()
                away_team = game.get('away_team', '').lower()
                
                teams_for_data = [home_team, away_team]
                
                # Fetch comprehensive data
                comprehensive_data = await self.data_integration.fetch_comprehensive_data(
                    teams_for_data, sport='nfl'
                )
                
                # Process and enhance the data
                enhanced_data = self.data_integration.process_and_enhance_data(comprehensive_data)
                
                # Create feature vector for prediction
                feature_vector = self._create_feature_vector(game, enhanced_data, home_team, away_team)
                
                # Make prediction using ensemble model
                prediction_result = self.ensemble_model.predict(
                    pd.DataFrame([feature_vector]), self.feature_columns
                )
                
                # Create enhanced prediction object
                enhanced_prediction = self._create_enhanced_prediction(
                    game, prediction_result, enhanced_data
                )
                
                enhanced_predictions.append(enhanced_prediction)
                
            except Exception as e:
                self.logger.error(f"Error generating prediction for game {game}: {str(e)}")
                # Create fallback prediction
                fallback_prediction = self._create_fallback_prediction(game)
                enhanced_predictions.append(fallback_prediction)
        
        return enhanced_predictions
    
    def _create_feature_vector(self, game: Dict, enhanced_data: pd.DataFrame, 
                             home_team: str, away_team: str) -> Dict:
        """Create feature vector for prediction"""
        
        feature_vector = {}
        
        # Basic game features
        feature_vector['home_team_win_rate'] = game.get('home_team_win_rate', 0.5)
        feature_vector['away_team_win_rate'] = game.get('away_team_win_rate', 0.5)
        feature_vector['home_team_recent_form'] = game.get('home_team_recent_form', 0.5)
        feature_vector['away_team_recent_form'] = game.get('away_team_recent_form', 0.5)
        feature_vector['home_team_rest_days'] = game.get('home_team_rest_days', 7)
        feature_vector['away_team_rest_days'] = game.get('away_team_rest_days', 7)
        feature_vector['home_team_injuries'] = game.get('home_team_injuries', 0)
        feature_vector['away_team_injuries'] = game.get('away_team_injuries', 0)
        feature_vector['h2h_home_wins'] = game.get('h2h_home_wins', 0)
        feature_vector['h2h_away_wins'] = game.get('h2h_away_wins', 0)
        
        # Market features
        feature_vector['public_betting_percentage'] = game.get('public_betting_percentage', 50)
        feature_vector['sharp_money_percentage'] = game.get('sharp_money_percentage', 50)
        feature_vector['market_efficiency_score'] = game.get('market_efficiency_score', 70)
        
        # Enhanced data features
        feature_vector['weather_impact_score'] = self._get_weather_impact(enhanced_data, home_team)
        feature_vector['sentiment_score'] = self._get_sentiment_score(enhanced_data, home_team, away_team)
        feature_vector['rest_advantage'] = feature_vector['home_team_rest_days'] - feature_vector['away_team_rest_days']
        feature_vector['injury_advantage'] = feature_vector['away_team_injuries'] - feature_vector['home_team_injuries']
        feature_vector['momentum_advantage'] = feature_vector['home_team_recent_form'] - feature_vector['away_team_recent_form']
        
        return feature_vector
    
    def _get_weather_impact(self, enhanced_data: pd.DataFrame, team: str) -> float:
        """Get weather impact score for a team"""
        if enhanced_data.empty or 'weather_impact_score' not in enhanced_data.columns:
            return 0.0
        
        # Get the most recent weather data
        weather_data = enhanced_data[enhanced_data['weather_impact_score'].notna()]
        if not weather_data.empty:
            return weather_data['weather_impact_score'].iloc[-1]
        
        return 0.0
    
    def _get_sentiment_score(self, enhanced_data: pd.DataFrame, home_team: str, away_team: str) -> float:
        """Get sentiment score for the game"""
        if enhanced_data.empty or 'sentiment_score' not in enhanced_data.columns:
            return 0.0
        
        # Get recent sentiment data
        sentiment_data = enhanced_data[enhanced_data['sentiment_score'].notna()]
        if not sentiment_data.empty:
            # Calculate average sentiment for the last 24 hours
            recent_sentiment = sentiment_data.tail(10)['sentiment_score'].mean()
            return recent_sentiment
        
        return 0.0
    
    def _create_enhanced_prediction(self, game: Dict, prediction_result: Dict, 
                                  enhanced_data: pd.DataFrame) -> Dict:
        """Create enhanced prediction object with comprehensive analysis"""
        
        confidence = prediction_result['confidence'][0]
        prediction = prediction_result['prediction'][0]
        high_confidence = prediction_result['high_confidence'][0]
        
        # Calculate expected value
        home_odds = game.get('home_odds', -110)
        away_odds = game.get('away_odds', -110)
        
        if prediction == 1:  # Home team wins
            recommended_bet = 'home'
            odds = home_odds
            probability = confidence
        else:  # Away team wins
            recommended_bet = 'away'
            odds = away_odds
            probability = 1 - confidence
        
        # Calculate Kelly Criterion
        if odds > 0:
            implied_prob = 100 / (odds + 100)
        else:
            implied_prob = abs(odds) / (abs(odds) + 100)
        
        kelly_fraction = (probability - implied_prob) / (1 - implied_prob)
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        # Calculate expected value
        if odds > 0:
            expected_value = (probability * odds - (1 - probability) * 100) / 100
        else:
            expected_value = (probability * 100 - (1 - probability) * abs(odds)) / 100
        
        # Get data insights
        data_insights = self._generate_data_insights(enhanced_data, game)
        
        # Create enhanced prediction
        enhanced_prediction = {
            'game_id': game.get('id'),
            'home_team': game.get('home_team'),
            'away_team': game.get('away_team'),
            'commence_time': game.get('commence_time'),
            'prediction': {
                'recommended_bet': recommended_bet,
                'confidence_score': confidence,
                'probability': probability,
                'odds': odds,
                'expected_value': expected_value,
                'kelly_fraction': kelly_fraction,
                'high_confidence': high_confidence
            },
            'model_analysis': {
                'ensemble_confidence': confidence,
                'individual_model_predictions': prediction_result['individual_predictions'],
                'model_weights': prediction_result['model_weights'],
                'confidence_threshold': prediction_result['confidence_threshold']
            },
            'data_insights': data_insights,
            'risk_assessment': {
                'weather_risk': self._assess_weather_risk(enhanced_data),
                'injury_risk': self._assess_injury_risk(game),
                'market_risk': self._assess_market_risk(game),
                'sentiment_risk': self._assess_sentiment_risk(enhanced_data),
                'overall_risk_score': 0.0  # Will be calculated
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate overall risk score
        enhanced_prediction['risk_assessment']['overall_risk_score'] = self._calculate_overall_risk(
            enhanced_prediction['risk_assessment']
        )
        
        return enhanced_prediction
    
    def _generate_data_insights(self, enhanced_data: pd.DataFrame, game: Dict) -> Dict:
        """Generate insights from the integrated data"""
        
        insights = {
            'weather_conditions': 'Unknown',
            'social_sentiment': 'Neutral',
            'market_movements': 'Stable',
            'injury_impact': 'Minimal',
            'key_factors': []
        }
        
        # Weather insights
        if not enhanced_data.empty and 'weather_condition' in enhanced_data.columns:
            weather_data = enhanced_data[enhanced_data['weather_condition'].notna()]
            if not weather_data.empty:
                recent_weather = weather_data['weather_condition'].iloc[-1]
                insights['weather_conditions'] = recent_weather.title()
                
                if recent_weather in ['rain', 'snow', 'thunderstorm']:
                    insights['key_factors'].append('Adverse weather conditions')
        
        # Sentiment insights
        if not enhanced_data.empty and 'sentiment_score' in enhanced_data.columns:
            sentiment_data = enhanced_data[enhanced_data['sentiment_score'].notna()]
            if not sentiment_data.empty:
                avg_sentiment = sentiment_data['sentiment_score'].mean()
                if avg_sentiment > 0.1:
                    insights['social_sentiment'] = 'Positive'
                elif avg_sentiment < -0.1:
                    insights['social_sentiment'] = 'Negative'
        
        # Market insights
        public_betting = game.get('public_betting_percentage', 50)
        if public_betting > 70:
            insights['market_movements'] = 'Heavy public betting'
            insights['key_factors'].append('Public money heavily on one side')
        elif public_betting < 30:
            insights['market_movements'] = 'Sharp money movement'
            insights['key_factors'].append('Sharp money on opposite side')
        
        # Injury insights
        home_injuries = game.get('home_team_injuries', 0)
        away_injuries = game.get('away_team_injuries', 0)
        if home_injuries > 3 or away_injuries > 3:
            insights['injury_impact'] = 'Significant'
            insights['key_factors'].append('Multiple key injuries')
        
        return insights
    
    def _assess_weather_risk(self, enhanced_data: pd.DataFrame) -> float:
        """Assess weather-related risk"""
        if enhanced_data.empty or 'weather_impact_score' not in enhanced_data.columns:
            return 0.1
        
        weather_impact = enhanced_data['weather_impact_score'].abs().max()
        return min(weather_impact * 2, 1.0)
    
    def _assess_injury_risk(self, game: Dict) -> float:
        """Assess injury-related risk"""
        home_injuries = game.get('home_team_injuries', 0)
        away_injuries = game.get('away_team_injuries', 0)
        total_injuries = home_injuries + away_injuries
        
        if total_injuries == 0:
            return 0.1
        elif total_injuries <= 2:
            return 0.3
        elif total_injuries <= 5:
            return 0.6
        else:
            return 0.9
    
    def _assess_market_risk(self, game: Dict) -> float:
        """Assess market-related risk"""
        public_betting = game.get('public_betting_percentage', 50)
        
        # Higher risk when public betting is heavily skewed
        if public_betting > 80 or public_betting < 20:
            return 0.8
        elif public_betting > 70 or public_betting < 30:
            return 0.6
        else:
            return 0.3
    
    def _assess_sentiment_risk(self, enhanced_data: pd.DataFrame) -> float:
        """Assess sentiment-related risk"""
        if enhanced_data.empty or 'sentiment_score' not in enhanced_data.columns:
            return 0.2
        
        sentiment_data = enhanced_data[enhanced_data['sentiment_score'].notna()]
        if sentiment_data.empty:
            return 0.2
        
        sentiment_volatility = sentiment_data['sentiment_score'].std()
        return min(sentiment_volatility * 2, 1.0)
    
    def _calculate_overall_risk(self, risk_assessment: Dict) -> float:
        """Calculate overall risk score"""
        weights = {
            'weather_risk': 0.2,
            'injury_risk': 0.3,
            'market_risk': 0.25,
            'sentiment_risk': 0.25
        }
        
        overall_risk = sum(
            risk_assessment[risk_type] * weight
            for risk_type, weight in weights.items()
        )
        
        return min(overall_risk, 1.0)
    
    def _create_fallback_prediction(self, game: Dict) -> Dict:
        """Create fallback prediction when enhanced prediction fails"""
        
        return {
            'game_id': game.get('id'),
            'home_team': game.get('home_team'),
            'away_team': game.get('away_team'),
            'commence_time': game.get('commence_time'),
            'prediction': {
                'recommended_bet': 'home',
                'confidence_score': 0.5,
                'probability': 0.5,
                'odds': -110,
                'expected_value': 0.0,
                'kelly_fraction': 0.0,
                'high_confidence': False
            },
            'model_analysis': {
                'ensemble_confidence': 0.5,
                'individual_model_predictions': {},
                'model_weights': {},
                'confidence_threshold': 0.6
            },
            'data_insights': {
                'weather_conditions': 'Unknown',
                'social_sentiment': 'Unknown',
                'market_movements': 'Unknown',
                'injury_impact': 'Unknown',
                'key_factors': ['Fallback prediction - limited data']
            },
            'risk_assessment': {
                'weather_risk': 0.5,
                'injury_risk': 0.5,
                'market_risk': 0.5,
                'sentiment_risk': 0.5,
                'overall_risk_score': 0.5
            },
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }
    
    def save_model(self, filepath: str):
        """Save the enhanced prediction engine"""
        model_data = {
            'ensemble_model': self.ensemble_model,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained,
            'config': self.config
        }
        
        import joblib
        joblib.dump(model_data, filepath)
        self.logger.info(f"Enhanced prediction engine saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load the enhanced prediction engine"""
        import joblib
        model_data = joblib.load(filepath)
        
        self.ensemble_model = model_data['ensemble_model']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']
        self.config = model_data['config']
        
        self.logger.info(f"Enhanced prediction engine loaded from {filepath}")
    
    def get_model_performance_summary(self) -> Dict:
        """Get comprehensive model performance summary"""
        if not self.is_trained:
            return {'status': 'Model not trained'}
        
        # Get feature importance
        feature_importance = self.ensemble_model.get_feature_importance_summary()
        
        return {
            'status': 'Trained',
            'model_weights': self.ensemble_model.weights,
            'feature_importance': feature_importance.to_dict() if not feature_importance.empty else {},
            'confidence_thresholds': self.ensemble_model.confidence_thresholds,
            'feature_count': len(self.feature_columns),
            'last_updated': datetime.now().isoformat()
        }
