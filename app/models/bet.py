from app import db
from datetime import datetime

class Bet(db.Model):
    __tablename__ = 'bets'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('bets', lazy=True))
    bet_type = db.Column(db.String(64), nullable=False) # e.g., 'moneyline', 'spread', 'total'
    bet_side = db.Column(db.String(64), nullable=False) # e.g., 'home', 'away', 'over', 'under'
    odds = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    potential_payout = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(64), default='pending') # e.g., 'pending', 'win', 'loss', 'void'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Bet {self.id} - {self.bet_type} on Game {self.game_id}>'