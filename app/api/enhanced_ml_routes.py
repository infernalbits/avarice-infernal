from flask import Blueprint, request, jsonify
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import json

from ..ml.enhanced_prediction_engine import EnhancedPredictionEngine
from ..ml.advanced_ensemble_model import AdvancedEnsembleModel
from ..ml.advanced_data_integration import AdvancedDataIntegration
from .. import db
from ..models import Game, Prediction, Bet
from config import Config

# Create blueprint
enhanced_ml_bp = Blueprint('enhanced_ml', __name__, url_prefix='/api/enhanced')

# Initialize enhanced prediction engine
config = {
    'weather_api_key': Config.WEATHER_API_KEY if hasattr(Config, 'WEATHER_API_KEY') else None,
    'twitter_api_key': Config.TWITTER_API_KEY if hasattr(Config, 'TWITTER_API_KEY') else None,
    'market_api_keys': {
        'fanduel': Config.FANDUEL_API_KEY if hasattr(Config, 'FANDUEL_API_KEY') else None,
        'draftkings': Config.DRAFTKINGS_API_KEY if hasattr(Config, 'DRAFTKINGS_API_KEY') else None,
        'bet365': Config.BET365_API_KEY if hasattr(Config, 'BET365_API_KEY') else None
    }
}

enhanced_engine = EnhancedPredictionEngine(config)

@enhanced_ml_bp.route('/train-model', methods=['POST'])
def train_enhanced_model():
    """Train the enhanced ensemble model"""
    try:
        # Get training data from database
        games = Game.query.all()
        
        if not games:
            return jsonify({'error': 'No training data available'}), 400
        
        # Convert to DataFrame
        training_data = []
        for game in games:
            # Create feature vector for each game
            game_data = {
                'home_team_win_rate': game.home_team_win_rate or 0.5,
                'away_team_win_rate': game.away_team_win_rate or 0.5,
                'home_team_recent_form': game.home_team_recent_form or 0.5,
                'away_team_recent_form': game.away_team_recent_form or 0.5,
                'home_team_rest_days': game.home_team_rest_days or 7,
                'away_team_rest_days': game.away_team_rest_days or 7,
                'home_team_injuries': game.home_team_injuries or 0,
                'away_team_injuries': game.away_team_injuries or 0,
                'h2h_home_wins': game.h2h_home_wins or 0,
                'h2h_away_wins': game.h2h_away_wins or 0,
                'public_betting_percentage': game.public_betting_percentage or 50,
                'sharp_money_percentage': game.sharp_money_percentage or 50,
                'market_efficiency_score': game.market_efficiency_score or 70,
                'weather_impact_score': 0.0,  # Will be enhanced with real data
                'sentiment_score': 0.0,  # Will be enhanced with real data
                'rest_advantage': (game.home_team_rest_days or 7) - (game.away_team_rest_days or 7),
                'injury_advantage': (game.away_team_injuries or 0) - (game.home_team_injuries or 0),
                'momentum_advantage': (game.home_team_recent_form or 0.5) - (game.away_team_recent_form or 0.5),
                'outcome': 1 if game.home_team_score > game.away_team_score else 0
            }
            training_data.append(game_data)
        
        df = pd.DataFrame(training_data)
        
        # Train the model asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        cv_scores = loop.run_until_complete(enhanced_engine.train_enhanced_model(df))
        loop.close()
        
        return jsonify({
            'message': 'Enhanced model trained successfully',
            'cross_validation_scores': cv_scores,
            'training_samples': len(df),
            'feature_count': len(enhanced_engine.feature_columns)
        })
        
    except Exception as e:
        logging.error(f"Error training enhanced model: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/predictions', methods=['GET'])
def get_enhanced_predictions():
    """Get enhanced predictions with comprehensive data integration"""
    try:
        # Get upcoming games
        upcoming_games = Game.query.filter(
            Game.commence_time > datetime.now()
        ).order_by(Game.commence_time).limit(10).all()
        
        if not upcoming_games:
            return jsonify({'error': 'No upcoming games found'}), 404
        
        # Convert games to dict format
        games_data = []
        teams = set()
        
        for game in upcoming_games:
            game_dict = {
                'id': game.id,
                'home_team': game.home_team,
                'away_team': game.away_team,
                'commence_time': game.commence_time.isoformat(),
                'home_team_win_rate': game.home_team_win_rate or 0.5,
                'away_team_win_rate': game.away_team_win_rate or 0.5,
                'home_team_recent_form': game.home_team_recent_form or 0.5,
                'away_team_recent_form': game.away_team_recent_form or 0.5,
                'home_team_rest_days': game.home_team_rest_days or 7,
                'away_team_rest_days': game.away_team_rest_days or 7,
                'home_team_injuries': game.home_team_injuries or 0,
                'away_team_injuries': game.away_team_injuries or 0,
                'h2h_home_wins': game.h2h_home_wins or 0,
                'h2h_away_wins': game.h2h_away_wins or 0,
                'public_betting_percentage': game.public_betting_percentage or 50,
                'sharp_money_percentage': game.sharp_money_percentage or 50,
                'market_efficiency_score': game.market_efficiency_score or 70,
                'home_odds': game.home_odds or -110,
                'away_odds': game.away_odds or -110
            }
            games_data.append(game_dict)
            teams.add(game.home_team.lower())
            teams.add(game.away_team.lower())
        
        # Generate enhanced predictions
        if not enhanced_engine.is_trained:
            return jsonify({'error': 'Model not trained. Please train the model first.'}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        enhanced_predictions = loop.run_until_complete(
            enhanced_engine.generate_enhanced_predictions(games_data, list(teams))
        )
        loop.close()
        
        return jsonify({
            'predictions': enhanced_predictions,
            'total_predictions': len(enhanced_predictions),
            'model_status': 'enhanced',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error generating enhanced predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/data-integration/weather', methods=['GET'])
def get_weather_data():
    """Get weather data for teams"""
    try:
        team = request.args.get('team')
        if not team:
            return jsonify({'error': 'Team parameter required'}), 400
        
        # Initialize data integration
        data_integration = AdvancedDataIntegration(config)
        
        # Fetch weather data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        weather_data = loop.run_until_complete(
            data_integration.providers['weather'].fetch_data(team, datetime.now())
        )
        loop.close()
        
        if not weather_data:
            return jsonify({'error': 'No weather data available'}), 404
        
        # Parse weather data
        weather_df = data_integration.providers['weather'].parse_data(weather_data)
        
        return jsonify({
            'team': team,
            'weather_data': weather_df.to_dict('records') if not weather_df.empty else [],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error fetching weather data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/data-integration/social', methods=['GET'])
def get_social_data():
    """Get social media sentiment data for teams"""
    try:
        team = request.args.get('team')
        keywords = request.args.get('keywords', '').split(',')
        
        if not team:
            return jsonify({'error': 'Team parameter required'}), 400
        
        # Initialize data integration
        data_integration = AdvancedDataIntegration(config)
        
        # Fetch social data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        social_data = loop.run_until_complete(
            data_integration.providers['social'].fetch_data(team, keywords)
        )
        loop.close()
        
        # Parse social data
        social_df = data_integration.providers['social'].parse_data(social_data)
        
        return jsonify({
            'team': team,
            'social_data': social_df.to_dict('records') if not social_df.empty else [],
            'sentiment_summary': {
                'average_sentiment': social_df['sentiment_score'].mean() if not social_df.empty else 0,
                'positive_posts': (social_df['sentiment_score'] > 0).sum() if not social_df.empty else 0,
                'negative_posts': (social_df['sentiment_score'] < 0).sum() if not social_df.empty else 0,
                'total_posts': len(social_df)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error fetching social data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/data-integration/injuries', methods=['GET'])
def get_injury_data():
    """Get injury data for teams"""
    try:
        sport = request.args.get('sport', 'nfl')
        
        # Initialize data integration
        data_integration = AdvancedDataIntegration(config)
        
        # Fetch injury data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        injury_data = loop.run_until_complete(
            data_integration.providers['injury'].fetch_data(sport)
        )
        loop.close()
        
        # Parse injury data
        injury_df = data_integration.providers['injury'].parse_data(injury_data)
        
        return jsonify({
            'sport': sport,
            'injury_data': injury_df.to_dict('records') if not injury_df.empty else [],
            'total_injuries': len(injury_df),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error fetching injury data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/model-performance', methods=['GET'])
def get_model_performance():
    """Get enhanced model performance summary"""
    try:
        performance_summary = enhanced_engine.get_model_performance_summary()
        
        return jsonify({
            'model_performance': performance_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error getting model performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/feature-importance', methods=['GET'])
def get_feature_importance():
    """Get feature importance analysis"""
    try:
        if not enhanced_engine.is_trained:
            return jsonify({'error': 'Model not trained'}), 400
        
        feature_importance = enhanced_engine.ensemble_model.get_feature_importance_summary()
        
        return jsonify({
            'feature_importance': feature_importance.to_dict() if not feature_importance.empty else {},
            'top_features': feature_importance.head(10).to_dict() if not feature_importance.empty else {},
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error getting feature importance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/comprehensive-analysis', methods=['POST'])
def get_comprehensive_analysis():
    """Get comprehensive analysis for specific teams"""
    try:
        data = request.get_json()
        teams = data.get('teams', [])
        sport = data.get('sport', 'nfl')
        
        if not teams:
            return jsonify({'error': 'Teams parameter required'}), 400
        
        # Initialize data integration
        data_integration = AdvancedDataIntegration(config)
        
        # Fetch comprehensive data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        comprehensive_data = loop.run_until_complete(
            data_integration.fetch_comprehensive_data(teams, sport)
        )
        loop.close()
        
        # Process and enhance data
        enhanced_data = data_integration.process_and_enhance_data(comprehensive_data)
        
        # Get data summary
        data_summary = data_integration.get_data_summary(enhanced_data)
        
        return jsonify({
            'teams': teams,
            'sport': sport,
            'comprehensive_data': comprehensive_data,
            'enhanced_data': enhanced_data.to_dict('records') if not enhanced_data.empty else [],
            'data_summary': data_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error getting comprehensive analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/save-model', methods=['POST'])
def save_enhanced_model():
    """Save the enhanced model"""
    try:
        filepath = 'models/enhanced_prediction_engine.pkl'
        enhanced_engine.save_model(filepath)
        
        return jsonify({
            'message': 'Enhanced model saved successfully',
            'filepath': filepath,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error saving enhanced model: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enhanced_ml_bp.route('/load-model', methods=['POST'])
def load_enhanced_model():
    """Load the enhanced model"""
    try:
        filepath = 'models/enhanced_prediction_engine.pkl'
        enhanced_engine.load_model(filepath)
        
        return jsonify({
            'message': 'Enhanced model loaded successfully',
            'filepath': filepath,
            'model_trained': enhanced_engine.is_trained,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error loading enhanced model: {str(e)}")
        return jsonify({'error': str(e)}), 500
