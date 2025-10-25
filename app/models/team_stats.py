from app import db
from datetime import datetime

class TeamStats(db.Model):
    __tablename__ = 'team_stats'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(128), nullable=False, unique=True)
    sport = db.Column(db.String(64), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    points_for = db.Column(db.Integer, default=0)
    points_against = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TeamStats {self.team_name} ({self.sport})>'