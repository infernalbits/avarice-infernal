import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from app.models import Game, TeamStats, Bet, Prediction
from app import db

class PredictionModel:
    """Machine Learning model for sports betting predictions"""
    
    def __init__(self):
        self.models = {
            'moneyline': None,
            'spread': None,
            'total': None
        }
        self.scalers = {
            'moneyline': StandardScaler(),
            'spread': StandardScaler(),
            'total': StandardScaler()
        }
        self.feature_columns = []
        self.model_version = "1.0.0"
        self.min_accuracy_threshold = 0.65
        
    def extract_features(self, game: Game, home_stats: TeamStats = None, away_stats: TeamStats = None) -> Dict:
        """
        Extract features for ML model from game and team statistics
        
        Args:
            game: Game object
            home_stats: Home team statistics
            away_stats: Away team statistics
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Basic game features
        features['days_until_game'] = (game.commence_time - datetime.utcnow()).days
        features['is_weekend'] = game.commence_time.weekday() >= 5
        features['hour_of_day'] = game.commence_time.hour
        
        # Odds features
        if game.home_odds and game.away_odds:
            features['home_odds'] = game.home_odds
            features['away_odds'] = game.away_odds
            features['odds_differential'] = abs(game.home_odds - game.away_odds)
            
            # Convert American odds to implied probability
            home_prob = self._american_odds_to_probability(game.home_odds)
            away_prob = self._american_odds_to_probability(game.away_odds)
            features['home_implied_prob'] = home_prob
            features['away_implied_prob'] = away_prob
            features['market_efficiency'] = abs((home_prob + away_prob) - 1.0)
        
        if game.point_spread:
            features['point_spread'] = game.point_spread
            features['spread_magnitude'] = abs(game.point_spread)
        
        if game.total_points:
            features['total_points'] = game.total_points
        
        # Home team features
        if home_stats:
            features.update(self._extract_team_features(home_stats, 'home'))
        
        # Away team features  
        if away_stats:
            features.update(self._extract_team_features(away_stats, 'away'))
        
        # Head-to-head features
        if home_stats and away_stats:
            features.update(self._extract_matchup_features(home_stats, away_stats))
        
        return features
    
    def _extract_team_features(self, stats: TeamStats, prefix: str) -> Dict:
        """Extract features from team statistics"""
        features = {}
        
        # Basic performance metrics
        features[f'{prefix}_win_pct'] = stats.win_percentage
        features[f'{prefix}_games_played'] = stats.games_played
        features[f'{prefix}_point_diff'] = stats.point_differential
        features[f'{prefix}_avg_points_for'] = stats.avg_points_for
        features[f'{prefix}_avg_points_against'] = stats.avg_points_against
        
        # Advanced metrics
        features[f'{prefix}_off_efficiency'] = stats.offensive_efficiency or 0.0
        features[f'{prefix}_def_efficiency'] = stats.defensive_efficiency or 0.0
        features[f'{prefix}_sos'] = stats.strength_of_schedule or 0.0
        
        # Recent form
        if stats.recent_form:
            recent_wins = stats.recent_form.count('W')
            features[f'{prefix}_recent_form'] = recent_wins / len(stats.recent_form)
        else:
            features[f'{prefix}_recent_form'] = 0.5
        
        features[f'{prefix}_recent_ppg'] = stats.recent_avg_points_for or stats.avg_points_for
        features[f'{prefix}_recent_papg'] = stats.recent_avg_points_against or stats.avg_points_against
        
        # Home/Away performance
        if prefix == 'home':
            home_games = stats.home_wins + stats.home_losses
            features[f'{prefix}_home_win_pct'] = stats.home_wins / home_games if home_games > 0 else 0.5
        else:
            away_games = stats.away_wins + stats.away_losses
            features[f'{prefix}_away_win_pct'] = stats.away_wins / away_games if away_games > 0 else 0.5
        
        # Injury impact
        features[f'{prefix}_injury_impact'] = stats.injury_impact_score or 0.0
        features[f'{prefix}_key_injuries'] = stats.key_players_injured or 0
        
        return features
    
    def _extract_matchup_features(self, home_stats: TeamStats, away_stats: TeamStats) -> Dict:
        """Extract head-to-head matchup features"""
        features = {}
        
        # Performance differentials
        features['win_pct_diff'] = home_stats.win_percentage - away_stats.win_percentage
        features['off_eff_diff'] = (home_stats.offensive_efficiency or 0) - (away_stats.offensive_efficiency or 0)
        features['def_eff_diff'] = (home_stats.defensive_efficiency or 0) - (away_stats.defensive_efficiency or 0)
        features['ppg_diff'] = home_stats.avg_points_for - away_stats.avg_points_for
        features['papg_diff'] = home_stats.avg_points_against - away_stats.avg_points_against
        
        # Style matchups
        features['pace_matchup'] = abs(home_stats.avg_points_for - away_stats.avg_points_for)
        features['total_expected'] = (home_stats.avg_points_for + away_stats.avg_points_against + 
                                    away_stats.avg_points_for + home_stats.avg_points_against) / 2
        
        return features
    
    def _american_odds_to_probability(self, odds: float) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def prepare_training_data(self, lookback_days: int = 365) -> Tuple[pd.DataFrame, Dict]:
        """
        Prepare training data from historical games and outcomes
        
        Args:
            lookback_days: Number of days to look back for training data
            
        Returns:
            Tuple of (features_df, targets_dict)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        
        # Get completed games with outcomes
        completed_games = Game.query.filter(
            Game.completed == True,
            Game.created_at >= cutoff_date,
            Game.home_score.isnot(None),
            Game.away_score.isnot(None)
        ).all()
        
        training_data = []
        
        for game in completed_games:
            # Get team stats (this would ideally be historical stats at game time)
            home_stats = TeamStats.query.filter_by(
                team_name=game.home_team,
                sport=game.sport
            ).first()
            
            away_stats = TeamStats.query.filter_by(
                team_name=game.away_team,
                sport=game.sport
            ).first()
            
            if not home_stats or not away_stats:
                continue
            
            # Extract features
            features = self.extract_features(game, home_stats, away_stats)
            
            # Create targets
            home_won = game.home_score > game.away_score
            away_won = game.away_score > game.home_score
            total_score = game.home_score + game.away_score
            
            # Moneyline targets
            if home_won:
                moneyline_target = 'home'
            elif away_won:
                moneyline_target = 'away'
            else:
                moneyline_target = 'draw'
            
            # Spread target (if spread exists)
            spread_target = None
            if game.point_spread:
                home_cover = (game.home_score - game.away_score) > game.point_spread
                spread_target = 'home' if home_cover else 'away'
            
            # Total target (if total exists)
            total_target = None
            if game.total_points:
                total_target = 'over' if total_score > game.total_points else 'under'
            
            row = {
                'game_id': game.id,
                **features,
                'moneyline_target': moneyline_target,
                'spread_target': spread_target,
                'total_target': total_target
            }
            
            training_data.append(row)
        
        if not training_data:
            return pd.DataFrame(), {}
        
        df = pd.DataFrame(training_data)
        
        # Separate features and targets
        feature_cols = [col for col in df.columns if not col.endswith('_target') and col != 'game_id']
        self.feature_columns = feature_cols
        
        features_df = df[feature_cols].fillna(0)
        
        targets = {
            'moneyline': df['moneyline_target'].dropna(),
            'spread': df['spread_target'].dropna(),
            'total': df['total_target'].dropna()
        }
        
        return features_df, targets
    
    def train_models(self, retrain: bool = False) -> Dict:
        """
        Train prediction models
        
        Args:
            retrain: Whether to retrain existing models
            
        Returns:
            Dictionary with training results
        """
        if not retrain and all(model is not None for model in self.models.values()):
            return {'message': 'Models already trained'}
        
        # Prepare training data
        features_df, targets = self.prepare_training_data()
        
        if features_df.empty:
            return {'error': 'No training data available'}
        
        results = {}
        
        for bet_type in ['moneyline', 'spread', 'total']:
            if bet_type not in targets or targets[bet_type].empty:
                continue
            
            # Get corresponding features for this target
            target_indices = targets[bet_type].index
            X = features_df.loc[target_indices]
            y = targets[bet_type]
            
            if len(X) < 50:  # Minimum samples required
                continue
            
            # Scale features
            X_scaled = self.scalers[bet_type].fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train XGBoost model
            if bet_type == 'moneyline':
                model = xgb.XGBClassifier(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    eval_metric='mlogloss'
                )
            else:
                model = xgb.XGBClassifier(
                    n_estimators=150,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42,
                    eval_metric='logloss'
                )
            
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=5)
            
            self.models[bet_type] = model
            
            results[bet_type] = {
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'training_samples': len(X),
                'meets_threshold': accuracy >= self.min_accuracy_threshold
            }
        
        return results
    
    def predict_game(self, game: Game) -> List[Dict]:
        """
        Generate predictions for a game
        
        Args:
            game: Game object to predict
            
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        
        # Get team stats
        home_stats = TeamStats.query.filter_by(
            team_name=game.home_team,
            sport=game.sport
        ).first()
        
        away_stats = TeamStats.query.filter_by(
            team_name=game.away_team,
            sport=game.sport
        ).first()
        
        if not home_stats or not away_stats:
            return predictions
        
        # Extract features
        features = self.extract_features(game, home_stats, away_stats)
        
        # Create feature vector
        feature_vector = []
        for col in self.feature_columns:
            feature_vector.append(features.get(col, 0))
        
        feature_vector = np.array(feature_vector).reshape(1, -1)
        
        # Generate predictions for each bet type
        for bet_type, model in self.models.items():
            if model is None:
                continue
            
            try:
                # Scale features
                X_scaled = self.scalers[bet_type].transform(feature_vector)
                
                # Get prediction and probabilities
                prediction = model.predict(X_scaled)[0]
                probabilities = model.predict_proba(X_scaled)[0]
                
                # Get confidence score (max probability)
                confidence = max(probabilities)
                
                # Get class labels
                classes = model.classes_
                prob_dict = dict(zip(classes, probabilities))
                
                prediction_dict = {
                    'bet_type': bet_type,
                    'predicted_outcome': prediction,
                    'probability': prob_dict.get(prediction, 0.5),
                    'confidence_score': confidence,
                    'all_probabilities': prob_dict,
                    'model_version': self.model_version,
                    'features_used': json.dumps(list(features.keys()))
                }
                
                predictions.append(prediction_dict)
                
            except Exception as e:
                print(f"Error generating {bet_type} prediction: {e}")
                continue
        
        return predictions
    
    def save_models(self, filepath_prefix: str = 'models/betting_model'):
        """Save trained models to disk"""
        for bet_type, model in self.models.items():
            if model is not None:
                joblib.dump(model, f"{filepath_prefix}_{bet_type}.pkl")
                joblib.dump(self.scalers[bet_type], f"{filepath_prefix}_{bet_type}_scaler.pkl")
        
        # Save feature columns
        with open(f"{filepath_prefix}_features.json", 'w') as f:
            json.dump(self.feature_columns, f)
    
    def load_models(self, filepath_prefix: str = 'models/betting_model'):
        """Load trained models from disk"""
        try:
            for bet_type in self.models.keys():
                self.models[bet_type] = joblib.load(f"{filepath_prefix}_{bet_type}.pkl")
                self.scalers[bet_type] = joblib.load(f"{filepath_prefix}_{bet_type}_scaler.pkl")
            
            # Load feature columns
            with open(f"{filepath_prefix}_features.json", 'r') as f:
                self.feature_columns = json.load(f)
            
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    
    def evaluate_predictions(self) -> Dict:
        """Evaluate model performance on recent predictions"""
        # Get settled predictions from last 30 days
        recent_predictions = Prediction.query.filter(
            Prediction.created_at >= datetime.utcnow() - timedelta(days=30),
            Prediction.correct.isnot(None)
        ).all()
        
        if not recent_predictions:
            return {'error': 'No recent predictions to evaluate'}
        
        # Group by bet type
        by_bet_type = {}
        for pred in recent_predictions:
            if pred.bet_type not in by_bet_type:
                by_bet_type[pred.bet_type] = []
            by_bet_type[pred.bet_type].append(pred)
        
        results = {}
        
        for bet_type, preds in by_bet_type.items():
            correct = sum(1 for p in preds if p.correct)
            total = len(preds)
            accuracy = correct / total if total > 0 else 0
            
            # Average confidence of correct predictions
            correct_preds = [p for p in preds if p.correct]
            avg_confidence_correct = sum(p.confidence_score for p in correct_preds) / len(correct_preds) if correct_preds else 0
            
            # Average confidence of incorrect predictions
            incorrect_preds = [p for p in preds if not p.correct]
            avg_confidence_incorrect = sum(p.confidence_score for p in incorrect_preds) / len(incorrect_preds) if incorrect_preds else 0
            
            results[bet_type] = {
                'total_predictions': total,
                'correct_predictions': correct,
                'accuracy': accuracy,
                'avg_confidence_correct': avg_confidence_correct,
                'avg_confidence_incorrect': avg_confidence_incorrect,
                'meets_threshold': accuracy >= self.min_accuracy_threshold
            }
        
        # Overall metrics
        total_correct = sum(1 for p in recent_predictions if p.correct)
        total_predictions = len(recent_predictions)
        overall_accuracy = total_correct / total_predictions if total_predictions > 0 else 0
        
        results['overall'] = {
            'total_predictions': total_predictions,
            'correct_predictions': total_correct,
            'accuracy': overall_accuracy,
            'meets_threshold': overall_accuracy >= self.min_accuracy_threshold
        }
        
        return results
