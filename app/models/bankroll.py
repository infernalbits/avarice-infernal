from app import db

class Bankroll(db.Model):
    __tablename__ = 'bankroll'
    id = db.Column(db.Integer, primary_key=True)
    # Add other fields as per your application's requirements
    # Example:
    # current_balance = db.Column(db.Float, nullable=False, default=0.0)
    # starting_balance = db.Column(db.Float, nullable=False, default=0.0)
    # max_daily_loss = db.Column(db.Float, nullable=False, default=0.0)
    # updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Bankroll {self.id}>'