from app import db
from datetime import datetime

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('predictions', lazy=True))
    predicted_outcome = db.Column(db.String(64), nullable=False) # e.g., 'home_win', 'away_win', 'draw', 'over', 'under'
    confidence = db.Column(db.Float, nullable=False) # Probability or score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction {self.id} - Game {self.game_id} Outcome: {self.predicted_outcome}>'