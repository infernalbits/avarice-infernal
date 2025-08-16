from app import create_app, db
from app.models import Game, Bet, Prediction, TeamStats, Bankroll
from app.ml.prediction_model import PredictionModel
from app.ml.data_processor import DataProcessor
from app.ml.betting_engine import BettingEngine
from config import Config
import click
from datetime import datetime, timedelta

app = create_app()

@app.cli.command()
def init_db():
    """Initialize the database with tables and sample data."""
    with app.app_context():
        db.create_all()
        
        # Create initial bankroll
        bankroll = Bankroll.query.first()
        if not bankroll:
            bankroll = Bankroll(
                current_balance=Config.INITIAL_BANKROLL,
                starting_balance=Config.INITIAL_BANKROLL,
                max_daily_loss=Config.INITIAL_BANKROLL * 0.1
            )
            db.session.add(bankroll)
            db.session.commit()
            print(f"Created initial bankroll: ${Config.INITIAL_BANKROLL}")
        
        print("Database initialized successfully!")

@app.cli.command()
@click.option('--sport', default='americanfootball_nfl', help='Sport to update')
def update_games(sport):
    """Update games and odds from external API."""
    from app.api.sports_data import SportsDataAPI
    
    with app.app_context():
        sports_api = SportsDataAPI()
        
        # Fetch and update games
        odds_data = sports_api.get_odds_data(sport)
        if not odds_data:
            print("Failed to fetch odds data")
            return
        
        parsed_games = sports_api.parse_odds_data(odds_data)
        updated_count = 0
        
        for game_data in parsed_games:
            existing_game = Game.query.filter_by(external_id=game_data['external_id']).first()
            
            consensus = sports_api.get_consensus_odds(game_data)
            
            if existing_game:
                existing_game.home_odds = consensus.get('moneyline', {}).get('home')
                existing_game.away_odds = consensus.get('moneyline', {}).get('away')
                existing_game.draw_odds = consensus.get('moneyline', {}).get('draw')
                existing_game.point_spread = consensus.get('spread', {}).get('line')
                existing_game.total_points = consensus.get('total', {}).get('line')
                existing_game.over_odds = consensus.get('total', {}).get('over')
                existing_game.under_odds = consensus.get('total', {}).get('under')
                existing_game.updated_at = datetime.utcnow()
            else:
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
        print(f"Updated {updated_count} games for {sport}")

@app.cli.command()
@click.option('--sport', default='americanfootball_nfl', help='Sport to generate data for')
@click.option('--days', default=90, help='Number of days of historical data')
def generate_data(sport, days):
    """Generate synthetic historical data for testing."""
    with app.app_context():
        processor = DataProcessor()
        result = processor.generate_historical_data(sport, days)
        print(f"Generated data result: {result}")

@app.cli.command()
@click.option('--sport', default='americanfootball_nfl', help='Sport to update stats for')
def update_stats(sport):
    """Update team statistics."""
    with app.app_context():
        processor = DataProcessor()
        result = processor.update_team_stats(sport)
        print(f"Team stats update result: {result}")

@app.cli.command()
def train_model():
    """Train the machine learning models."""
    with app.app_context():
        model = PredictionModel()
        result = model.train_models(retrain=True)
        print(f"Model training result: {result}")
        
        # Save models
        try:
            model.save_models()
            print("Models saved successfully!")
        except Exception as e:
            print(f"Error saving models: {e}")

@app.cli.command()
@click.option('--days', default=30, help='Number of days to backtest')
def backtest(days):
    """Run backtest on historical data."""
    with app.app_context():
        engine = BettingEngine()
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Load models first
        engine.prediction_model.load_models()
        
        result = engine.backtest_strategy(start_date, end_date)
        print(f"Backtest result: {result}")

@app.cli.command()
def daily_analysis():
    """Run daily betting analysis."""
    with app.app_context():
        engine = BettingEngine()
        
        # Load models
        engine.prediction_model.load_models()
        
        result = engine.run_daily_analysis()
        print(f"Daily analysis result: {result}")

@app.cli.command()
def evaluate_model():
    """Evaluate model performance on recent predictions."""
    with app.app_context():
        model = PredictionModel()
        result = model.evaluate_predictions()
        print(f"Model evaluation result: {result}")

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Game': Game,
        'Bet': Bet,
        'Prediction': Prediction,
        'TeamStats': TeamStats,
        'Bankroll': Bankroll,
        'PredictionModel': PredictionModel,
        'DataProcessor': DataProcessor,
        'BettingEngine': BettingEngine
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
