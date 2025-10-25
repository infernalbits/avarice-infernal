from app import db
from datetime import datetime

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(128), unique=True, nullable=False)
    sport = db.Column(db.String(64), nullable=False)
    home_team = db.Column(db.String(128), nullable=False)
    away_team = db.Column(db.String(128), nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_odds = db.Column(db.Float)
    away_odds = db.Column(db.Float)
    draw_odds = db.Column(db.Float)
    point_spread = db.Column(db.Float)
    total_points = db.Column(db.Float)
    over_odds = db.Column(db.Float)
    under_odds = db.Column(db.Float)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Game {self.id} - {self.home_team} vs {self.away_team}>'