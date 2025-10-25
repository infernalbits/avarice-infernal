from app import db
from datetime import datetime

class Bankroll(db.Model):
    __tablename__ = 'bankroll'
    id = db.Column(db.Integer, primary_key=True)
    current_balance = db.Column(db.Float, nullable=False, default=0.0)
    starting_balance = db.Column(db.Float, nullable=False, default=0.0)
    max_daily_loss = db.Column(db.Float, nullable=False, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Bankroll {self.id} - Balance: {self.current_balance}>'