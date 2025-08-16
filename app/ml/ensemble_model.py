"""
Enhanced ensemble machine learning models for sports betting predictions
Combines multiple algorithms for improved accuracy and robustness
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
import joblib
import json
from typing import Dict, List, Tuple, Optional
from app.models import Game, TeamStats
from app.ml.prediction_model import PredictionModel


class EnsembleModel(PredictionModel):
    """Enhanced ensemble model combining multiple ML algorithms"""
    
    def __init__(self):
        super().__init__()
        self.models = {}
        self.weights = {}
        self.scalers = {}
        
        # Model configurations
        self.model_configs = {
            'xgboost': {
                'class': XGBClassifier,
                'params': {
                    'n_estimators': 300,
                    'max_depth': 8,
                    'learning_rate': 0.05,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'random_state': 42,
                    'eval_metric': 'logloss'
                }
            },
            'random_forest': {
                'class': RandomForestClassifier,
                'params': {
                    'n_estimators': 200,
                    'max_depth': 12,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'random_state': 42
                }
            },
            'gradient_boost': {
                'class': GradientBoostingClassifier,
                'params': {
                    'n_estimators': 150,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'subsample': 0.8,
                    'random_state': 42
                }
            },
            'neural_net': {
                'class': MLPClassifier,
                'params': {
                    'hidden_layer_sizes': (100, 50, 25),
                    'activation': 'relu',
                    'alpha': 0.01,
                    'learning_rate': 'adaptive',
                    'max_iter': 500,
                    'random_state': 42
                }
            },
            'logistic': {
                'class': LogisticRegression,
                'params': {
                    'C': 1.0,
                    'penalty': 'l2',
                    'solver': 'liblinear',
                    'random_state': 42
                }
            }
        }
    
    def train_ensemble_models(self, X: pd.DataFrame, y: pd.Series, bet_type: str) -> Dict:
        """Train ensemble of models with cross-validation"""
        print(f"Training ensemble models for {bet_type}...")
        
        # Initialize containers
        self.models[bet_type] = {}
        self.weights[bet_type] = {}
        self.scalers[bet_type] = {}
        
        model_scores = {}
        
        # Time series split for proper temporal validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        for model_name, config in self.model_configs.items():
            print(f"  Training {model_name}...")
            
            try:
                # Create and train model
                model = config['class'](**config['params'])
                
                # Scale features for neural networks and logistic regression
                if model_name in ['neural_net', 'logistic']:
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    self.scalers[bet_type][model_name] = scaler
                else:
                    X_scaled = X
                    self.scalers[bet_type][model_name] = None
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_scaled, y, cv=tscv, scoring='accuracy')
                model_scores[model_name] = cv_scores.mean()
                
                # Train on full dataset
                model.fit(X_scaled, y)
                self.models[bet_type][model_name] = model
                
                print(f"    {model_name}: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
                
            except Exception as e:
                print(f"    Error training {model_name}: {e}")
                model_scores[model_name] = 0.0
        
        # Calculate ensemble weights based on performance
        self._calculate_ensemble_weights(bet_type, model_scores)
        
        return {
            'bet_type': bet_type,
            'model_scores': model_scores,
            'weights': self.weights[bet_type],
            'ensemble_score': np.average(list(model_scores.values()), 
                                       weights=list(self.weights[bet_type].values()))
        }
    
    def _calculate_ensemble_weights(self, bet_type: str, scores: Dict[str, float]):
        """Calculate ensemble weights based on model performance"""
        # Softmax transformation for weights
        score_values = np.array(list(scores.values()))
        
        # Add small epsilon to avoid division by zero
        score_values = np.maximum(score_values, 0.01)
        
        # Softmax with temperature (higher temp = more uniform weights)
        temperature = 2.0
        exp_scores = np.exp(score_values / temperature)
        softmax_weights = exp_scores / np.sum(exp_scores)
        
        # Create weights dictionary
        self.weights[bet_type] = {}
        for i, model_name in enumerate(scores.keys()):
            self.weights[bet_type][model_name] = softmax_weights[i]
        
        print(f"  Ensemble weights for {bet_type}:")
        for model_name, weight in self.weights[bet_type].items():
            print(f"    {model_name}: {weight:.3f}")
    
    def predict_ensemble(self, game: Game, bet_type: str) -> Dict:
        """Make ensemble prediction for a game"""
        if bet_type not in self.models:
            return super().predict_game(game)  # Fallback to base model
        
        # Extract features
        features = self.extract_features(game)
        feature_df = pd.DataFrame([features])
        
        # Get predictions from all models
        model_predictions = {}
        model_probabilities = {}
        
        for model_name, model in self.models[bet_type].items():
            try:
                # Apply scaling if needed
                if self.scalers[bet_type][model_name] is not None:
                    X_scaled = self.scalers[bet_type][model_name].transform(feature_df)
                else:
                    X_scaled = feature_df
                
                # Get prediction and probability
                pred = model.predict(X_scaled)[0]
                prob = model.predict_proba(X_scaled)[0]
                
                model_predictions[model_name] = pred
                model_probabilities[model_name] = prob.max()
                
            except Exception as e:
                print(f"Error in {model_name} prediction: {e}")
                continue
        
        # Ensemble prediction using weighted voting
        ensemble_pred = self._weighted_ensemble_prediction(
            model_predictions, self.weights[bet_type]
        )
        
        # Ensemble confidence using weighted average
        ensemble_confidence = self._weighted_ensemble_confidence(
            model_probabilities, self.weights[bet_type]
        )
        
        return {
            'bet_type': bet_type,
            'predicted_outcome': ensemble_pred,
            'probability': ensemble_confidence,
            'confidence_score': ensemble_confidence,
            'model_version': 'ensemble_v1.0',
            'individual_predictions': model_predictions,
            'individual_probabilities': model_probabilities,
            'ensemble_weights': self.weights[bet_type]
        }
    
    def _weighted_ensemble_prediction(self, predictions: Dict, weights: Dict) -> str:
        """Combine predictions using weighted voting"""
        if not predictions:
            return 'home'  # Default fallback
        
        # Count weighted votes for each outcome
        outcome_weights = {}
        
        for model_name, prediction in predictions.items():
            weight = weights.get(model_name, 0.0)
            if prediction not in outcome_weights:
                outcome_weights[prediction] = 0.0
            outcome_weights[prediction] += weight
        
        # Return outcome with highest weighted vote
        return max(outcome_weights.items(), key=lambda x: x[1])[0]
    
    def _weighted_ensemble_confidence(self, probabilities: Dict, weights: Dict) -> float:
        """Calculate ensemble confidence using weighted average"""
        if not probabilities:
            return 0.5
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for model_name, prob in probabilities.items():
            weight = weights.get(model_name, 0.0)
            weighted_sum += prob * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.5
    
    def train_models(self, retrain: bool = False) -> Dict:
        """Train ensemble models for all bet types"""
        print("Training Enhanced Ensemble Models...")
        
        # Prepare training data
        X, feature_info = self.prepare_training_data()
        
        if X.empty:
            return {'error': 'No training data available'}
        
        results = {}
        bet_types = ['moneyline', 'spread', 'total']
        
        for bet_type in bet_types:
            if bet_type in X.columns:
                y = X[bet_type]
                feature_cols = [col for col in X.columns if col not in bet_types]
                X_features = X[feature_cols]
                
                # Train ensemble for this bet type
                result = self.train_ensemble_models(X_features, y, bet_type)
                results[bet_type] = result
        
        # Save models
        self.save_ensemble_models()
        
        return {
            'ensemble_results': results,
            'feature_count': len(feature_cols) if 'feature_cols' in locals() else 0,
            'training_samples': len(X),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def save_ensemble_models(self, filepath_prefix: str = 'models/ensemble_model'):
        """Save ensemble models, weights, and scalers"""
        try:
            # Save models
            joblib.dump(self.models, f'{filepath_prefix}_models.pkl')
            joblib.dump(self.weights, f'{filepath_prefix}_weights.pkl')
            joblib.dump(self.scalers, f'{filepath_prefix}_scalers.pkl')
            
            print(f"Ensemble models saved to {filepath_prefix}_*.pkl")
            
        except Exception as e:
            print(f"Error saving ensemble models: {e}")
    
    def load_ensemble_models(self, filepath_prefix: str = 'models/ensemble_model'):
        """Load ensemble models, weights, and scalers"""
        try:
            self.models = joblib.load(f'{filepath_prefix}_models.pkl')
            self.weights = joblib.load(f'{filepath_prefix}_weights.pkl')
            self.scalers = joblib.load(f'{filepath_prefix}_scalers.pkl')
            
            print(f"Ensemble models loaded from {filepath_prefix}_*.pkl")
            
        except FileNotFoundError:
            print(f"Ensemble model files not found at {filepath_prefix}_*.pkl")
            print("Training new ensemble models...")
            self.train_models()
        except Exception as e:
            print(f"Error loading ensemble models: {e}")
    
    def predict_game_enhanced(self, game: Game) -> List[Dict]:
        """Enhanced prediction using ensemble models"""
        predictions = []
        bet_types = ['moneyline', 'spread', 'total']
        
        for bet_type in bet_types:
            if bet_type in self.models:
                # Use ensemble prediction
                pred = self.predict_ensemble(game, bet_type)
            else:
                # Fallback to base model
                base_preds = super().predict_game(game)
                pred = next((p for p in base_preds if p['bet_type'] == bet_type), None)
                
                if pred:
                    pred['model_version'] = 'base_fallback'
            
            if pred:
                predictions.append(pred)
        
        return predictions
    
    def get_model_performance_summary(self) -> Dict:
        """Get performance summary of ensemble models"""
        summary = {
            'ensemble_info': {
                'model_count': len(self.model_configs),
                'models': list(self.model_configs.keys()),
                'bet_types': list(self.models.keys()) if hasattr(self, 'models') else []
            },
            'performance': {}
        }
        
        if hasattr(self, 'weights') and self.weights:
            for bet_type, weights in self.weights.items():
                summary['performance'][bet_type] = {
                    'model_weights': weights,
                    'top_model': max(weights.items(), key=lambda x: x[1])[0],
                    'weight_distribution': {
                        'max_weight': max(weights.values()),
                        'min_weight': min(weights.values()),
                        'weight_std': np.std(list(weights.values()))
                    }
                }
        
        return summary
