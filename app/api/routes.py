from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app import db
from app.models.game import Game
from app.models.bet import Bet
from app.models.prediction import Prediction
from app.models.team_stats import TeamStats
from app.models.bankroll import Bankroll
from app.api.sports_data import SportsDataAPI
from app.ml.prediction_model import PredictionModel
from config import Config

api_bp = Blueprint('api', __name__)
sports_api = SportsDataAPI()
prediction_model = PredictionModel()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@api_bp.route('/games', methods=['GET'])
def get_games():
    """Get upcoming games with odds"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    
    try:
        # Fetch games from database
        games = Game.query.filter(
            Game.sport == sport,
            Game.commence_time > datetime.utcnow(),
            Game.completed == False
        ).order_by(Game.commence_time).limit(20).all()
        
        return jsonify({
            'games': [game.to_dict() for game in games],
            'count': len(games)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/games/update', methods=['POST'])
def update_games():
    """Update games and odds from external API"""
    sport = request.json.get('sport', 'americanfootball_nfl')
    
    try:
        # Fetch latest odds data
        odds_data = sports_api.get_odds_data(sport)
        if not odds_data:
            return jsonify({'error': 'Failed to fetch odds data'}), 500
        
        # Parse and store games
        parsed_games = sports_api.parse_odds_data(odds_data)
        updated_count = 0
        
        for game_data in parsed_games:
            # Check if game exists
            existing_game = Game.query.filter_by(external_id=game_data['external_id']).first()
            
            # Calculate consensus odds
            consensus = sports_api.get_consensus_odds(game_data)
            
            if existing_game:
                # Update existing game
                existing_game.home_odds = consensus.get('moneyline', {}).get('home')
                existing_game.away_odds = consensus.get('moneyline', {}).get('away')
                existing_game.draw_odds = consensus.get('moneyline', {}).get('draw')
                existing_game.point_spread = consensus.get('spread', {}).get('line')
                existing_game.total_points = consensus.get('total', {}).get('line')
                existing_game.over_odds = consensus.get('total', {}).get('over')
                existing_game.under_odds = consensus.get('total', {}).get('under')
                existing_game.updated_at = datetime.utcnow()
            else:
                # Create new game
                new_game = Game(
                    external_id=game_data['external_id'],
                    sport=game_data['sport'],
                    home_team=game_data['home_team'],
                    away_team=game_data['away_team'],
                    commence_time=game_data['commence_time'],
                    home_odds=consensus.get('moneyline', {}).get('home'),
                    away_odds=consensus.get('moneyline', {}).get('away'),
                    draw_odds=consensus.get('moneyline', {}).get('draw'),
                    point_spread=consensus.get('spread', {}).get('line'),
                    total_points=consensus.get('total', {}).get('line'),
                    over_odds=consensus.get('total', {}).get('over'),
                    under_odds=consensus.get('total', {}).get('under')
                )
                db.session.add(new_game)
            
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Updated {updated_count} games',
            'sport': sport
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predictions', methods=['GET'])
def get_predictions():
    """Get betting predictions"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    min_confidence = float(request.args.get('min_confidence', Config.MIN_CONFIDENCE_THRESHOLD))
    
    try:
        # Get upcoming games
        upcoming_games = Game.query.filter(
            Game.sport == sport,
            Game.commence_time > datetime.utcnow(),
            Game.commence_time < datetime.utcnow() + timedelta(days=7),
            Game.completed == False
        ).all()
        
        predictions = []
        
        for game in upcoming_games:
            # Generate predictions using ML model
            game_predictions = prediction_model.predict_game(game)
            
            for pred in game_predictions:
                if pred['confidence_score'] >= min_confidence:
                    # Save prediction to database
                    prediction = Prediction(
                        game_id=game.id,
                        bet_type=pred['bet_type'],
                        predicted_outcome=pred['predicted_outcome'],
                        probability=pred['probability'],
                        confidence_score=pred['confidence_score'],
                        model_version=pred['model_version'],
                        features_used=pred['features_used']
                    )
                    db.session.add(prediction)
                    
                    predictions.append({
                        'game': game.to_dict(),
                        'prediction': prediction.to_dict()
                    })
        
        db.session.commit()
        
        return jsonify({
            'predictions': predictions,
            'count': len(predictions)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bets', methods=['GET'])
def get_bets():
    """Get betting history"""
    status = request.args.get('status', 'all')  # all, pending, settled
    limit = int(request.args.get('limit', 50))
    
    try:
        query = Bet.query
        
        if status == 'pending':
            query = query.filter(Bet.result.is_(None))
        elif status == 'settled':
            query = query.filter(Bet.result.isnot(None))
        
        bets = query.order_by(Bet.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'bets': [bet.to_dict() for bet in bets],
            'count': len(bets)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bets', methods=['POST'])
def place_bet():
    """Place a new bet (simulation)"""
    try:
        data = request.json

        # Validate required fields
        required_fields = ['game_id', 'bet_type', 'bet_value', 'odds', 'stake', 'confidence_score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate data types and values
        try:
            game_id = str(data['game_id'])
            bet_type = str(data['bet_type'])
            bet_value = str(data['bet_value'])
            odds = float(data['odds'])
            stake = float(data['stake'])
            confidence_score = float(data['confidence_score'])
            predicted_probability = float(data.get('predicted_probability', 0.5))
        except ValueError:
            return jsonify({'error': 'Invalid data type for one or more fields.'}), 400

        if stake <= 0:
            return jsonify({'error': 'Stake must be a positive number.'}), 400
        if not (0 <= confidence_score <= 1):
            return jsonify({'error': 'Confidence score must be between 0 and 1.'}), 400

        allowed_bet_types = ['moneyline', 'spread', 'total']
        if bet_type not in allowed_bet_types:
            return jsonify({'error': f'Invalid bet type. Allowed types are: {", ".join(allowed_bet_types)}'}), 400

        # Get or create bankroll
        bankroll = Bankroll.query.first()
        if not bankroll:
            bankroll = Bankroll(
                current_balance=Config.INITIAL_BANKROLL,
                starting_balance=Config.INITIAL_BANKROLL,
                max_daily_loss=Config.INITIAL_BANKROLL * 0.1  # 10% daily loss limit
            )
            db.session.add(bankroll)
            db.session.commit()

        # Check if bet can be placed
        can_bet, message = bankroll.can_place_bet(stake)
        if not can_bet:
            return jsonify({'error': message}), 400

        # Get game
        game = Game.query.filter_by(external_id=game_id).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        # Create bet
        bet = Bet(
            game_id=game_id,
            sport=game.sport,
            bet_type=bet_type,
            bet_value=bet_value,
            odds=odds,
            stake=stake,
            predicted_probability=predicted_probability,
            confidence_score=confidence_score,
            game_start_time=game.commence_time
        )

        db.session.add(bet)
        db.session.commit()

        return jsonify({
            'message': 'Bet placed successfully',
            'bet': bet.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        # Log the exception for debugging, but return a generic error to the client
        print(f"Error placing bet: {e}")
        return jsonify({'error': 'An unexpected error occurred while placing the bet.'}), 500

@api_bp.route('/bankroll', methods=['GET'])
def get_bankroll():
    """Get current bankroll status"""
    try:
        bankroll = Bankroll.query.first()
        if not bankroll:
            # Create initial bankroll
            bankroll = Bankroll(
                current_balance=Config.INITIAL_BANKROLL,
                starting_balance=Config.INITIAL_BANKROLL,
                max_daily_loss=Config.INITIAL_BANKROLL * 0.1
            )
            db.session.add(bankroll)
            db.session.commit()
        
        return jsonify(bankroll.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/performance', methods=['GET'])
def get_performance():
    """Get performance metrics"""
    try:
        # Get bankroll
        bankroll = Bankroll.query.first()
        if not bankroll:
            return jsonify({'error': 'No bankroll found'}), 404
        
        # Get recent bet statistics
        recent_bets = Bet.query.filter(
            Bet.created_at > datetime.utcnow() - timedelta(days=30)
        ).all()
        
        # Calculate additional metrics
        total_stakes = sum(bet.stake for bet in recent_bets)
        total_returns = sum(bet.profit_loss for bet in recent_bets)
        
        # Get predictions accuracy
        settled_predictions = Prediction.query.filter(
            Prediction.correct.isnot(None)
        ).all()
        
        correct_predictions = sum(1 for p in settled_predictions if p.correct)
        total_predictions = len(settled_predictions)
        prediction_accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        return jsonify({
            'bankroll': bankroll.to_dict(),
            'recent_performance': {
                'bets_last_30_days': len(recent_bets),
                'total_stakes_30_days': total_stakes,
                'total_returns_30_days': total_returns,
                'roi_30_days': (total_returns / total_stakes * 100) if total_stakes > 0 else 0
            },
            'prediction_accuracy': {
                'correct_predictions': correct_predictions,
                'total_predictions': total_predictions,
                'accuracy_percentage': prediction_accuracy
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/team-stats', methods=['GET'])
def get_team_stats():
    """Get team statistics"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    team = request.args.get('team')
    
    try:
        query = TeamStats.query.filter_by(sport=sport)
        
        if team:
            query = query.filter_by(team_name=team)
        
        stats = query.all()
        
        return jsonify({
            'team_stats': [stat.to_dict() for stat in stats],
            'count': len(stats)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enhanced routes moved to enhanced_routes.py to avoid async issues
