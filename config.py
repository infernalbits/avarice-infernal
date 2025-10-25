import os


class Config:
    # API Configuration
    ODDS_API_KEY = os.getenv('ODDS_API_KEY')
    ESPN_API_KEY = os.getenv('ESPN_API_KEY')
    SPORTSRADAR_API_KEY = os.getenv('SPORTSRADAR_API_KEY')
    
    # Enhanced ML API Keys (placeholder values - replace with real keys)
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    FANDUEL_API_KEY = os.getenv('FANDUEL_API_KEY')
    DRAFTKINGS_API_KEY = os.getenv('DRAFTKINGS_API_KEY')
    BET365_API_KEY = os.getenv('BET365_API_KEY')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///sports_betting.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application. Set it in .env or environment variables.")
    
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
