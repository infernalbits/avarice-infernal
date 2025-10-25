from app import db

class Bet(db.Model):
    __tablename__ = 'bets'
    id = db.Column(db.Integer, primary_key=True)
    # Add other fields as per your application's requirements
    # Example:
    # game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    # game = db.relationship('Game', backref=db.backref('bets', lazy=True))
    # bet_type = db.Column(db.String(64), nullable=False) # e.g., 'moneyline', 'spread', 'total'
    # bet_side = db.Column(db.String(64), nullable=False) # e.g., 'home', 'away', 'over', 'under'
    # odds = db.Column(db.Float, nullable=False)
    # amount = db.Column(db.Float, nullable=False)
    # potential_payout = db.Column(db.Float, nullable=False)
    # status = db.Column(db.String(64), default='pending') # e.g., 'pending', 'win', 'loss', 'void'
    # created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    # settled_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Bet {self.id}>'