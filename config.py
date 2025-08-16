import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    ODDS_API_KEY = os.getenv('ODDS_API_KEY', 'demo_key')
    ESPN_API_KEY = os.getenv('ESPN_API_KEY', '')
    SPORTSRADAR_API_KEY = os.getenv('SPORTSRADAR_API_KEY', 'lnWmN7AiRP5FZD9tROHT1yhBpssNO0GvPVqsLQ3Z')
    
    # Enhanced ML API Keys (placeholder values - replace with real keys)
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'your_openweather_api_key_here')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'your_twitter_api_key_here')
    FANDUEL_API_KEY = os.getenv('FANDUEL_API_KEY', 'your_fanduel_api_key_here')
    DRAFTKINGS_API_KEY = os.getenv('DRAFTKINGS_API_KEY', 'your_draftkings_api_key_here')
    BET365_API_KEY = os.getenv('BET365_API_KEY', 'your_bet365_api_key_here')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///sports_betting.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Betting Configuration
    INITIAL_BANKROLL = float(os.getenv('INITIAL_BANKROLL', 1000))
    MAX_BET_PERCENTAGE = float(os.getenv('MAX_BET_PERCENTAGE', 0.05))
    MIN_CONFIDENCE_THRESHOLD = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', 0.65))
    
    # Model Configuration
    MODEL_RETRAIN_INTERVAL_HOURS = 24
    HISTORICAL_DATA_DAYS = 365
    
    # Sports Configuration
    SUPPORTED_SPORTS = [
        'tennis',
        'basketball_ncaa', 
        'basketball_nba',
        'hockey_nhl',
        'americanfootball_nfl',
        'americanfootball_ncaa',
        'baseball_mlb',
        'mma',
        'motor_nascar',
        'golf'
    ]
    
    # API URLs
    ODDS_API_BASE_URL = 'https://api.the-odds-api.com/v4'
    ESPN_API_BASE_URL = 'https://site.api.espn.com/apis/site/v2/sports'
