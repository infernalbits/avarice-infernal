import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import joblib
import logging
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedEnsembleModel:
    """
    Advanced ensemble model combining multiple ML algorithms with sophisticated voting systems
    """
    
    def __init__(self, model_name: str = "advanced_ensemble"):
        self.model_name = model_name
        self.models = {}
        self.weights = {}
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.confidence_thresholds = {}
        self.is_trained = False
        
        # Initialize base models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize all base models with optimized parameters"""
        
        # XGBoost with hyperparameter tuning
        self.models['xgboost'] = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        
        # Random Forest with optimized parameters
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Gradient Boosting
        self.models['gradient_boosting'] = GradientBoostingClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        
        # Neural Network
        self.models['neural_network'] = MLPClassifier(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=500,
            random_state=42
        )
        
        # Support Vector Machine
        self.models['svm'] = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            random_state=42
        )
        
        # Logistic Regression
        self.models['logistic_regression'] = LogisticRegression(
            C=1.0,
            solver='liblinear',
            random_state=42,
            max_iter=1000
        )
        
        # Initialize equal weights
        for model_name in self.models.keys():
            self.weights[model_name] = 1.0
    
    def preprocess_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Advanced feature preprocessing with engineering"""
        
        # Create advanced features
        data_processed = data.copy()
        
        # Team performance rolling averages
        for team in ['home_team', 'away_team']:
            if f'{team}_win_rate' in data.columns:
                data_processed[f'{team}_win_rate_5g'] = data[f'{team}_win_rate'].rolling(5, min_periods=1).mean()
                data_processed[f'{team}_win_rate_10g'] = data[f'{team}_win_rate'].rolling(10, min_periods=1).mean()
        
        # Head-to-head features
        if all(col in data.columns for col in ['home_team', 'away_team', 'h2h_home_wins']):
            data_processed['h2h_advantage'] = data['h2h_home_wins'] / (data['h2h_home_wins'] + data['h2h_away_wins'] + 1)
        
        # Momentum features
        if 'home_team_recent_form' in data.columns:
            data_processed['home_momentum'] = data['home_team_recent_form'].rolling(3, min_periods=1).mean()
        
        if 'away_team_recent_form' in data.columns:
            data_processed['away_momentum'] = data['away_team_recent_form'].rolling(3, min_periods=1).mean()
        
        # Market efficiency features
        if 'public_betting_percentage' in data.columns:
            data_processed['sharp_money_indicator'] = np.where(
                data['public_betting_percentage'] > 70, -1,  # Fade public
                np.where(data['public_betting_percentage'] < 30, 1, 0)  # Follow public
            )
        
        # Weather impact (if available)
        if 'weather_condition' in data.columns:
            weather_impact = {
                'clear': 0, 'rain': -0.1, 'snow': -0.2, 'windy': -0.15
            }
            data_processed['weather_impact'] = data['weather_condition'].map(weather_impact).fillna(0)
        
        # Time-based features
        if 'commence_time' in data.columns:
            data_processed['hour_of_day'] = pd.to_datetime(data['commence_time']).dt.hour
            data_processed['day_of_week'] = pd.to_datetime(data['commence_time']).dt.dayofweek
            data_processed['is_primetime'] = ((data_processed['hour_of_day'] >= 19) & 
                                            (data_processed['hour_of_day'] <= 22)).astype(int)
        
        # Injury impact features
        if 'home_team_injuries' in data.columns and 'away_team_injuries' in data.columns:
            data_processed['injury_advantage'] = data['away_team_injuries'] - data['home_team_injuries']
        
        # Rest days advantage
        if 'home_team_rest_days' in data.columns and 'away_team_rest_days' in data.columns:
            data_processed['rest_advantage'] = data['home_team_rest_days'] - data['away_team_rest_days']
        
        return data_processed
    
    def train_models(self, X: pd.DataFrame, y: pd.Series, feature_columns: List[str]):
        """Train all models with cross-validation and weight optimization"""
        
        logging.info("Starting advanced ensemble model training...")
        
        # Preprocess features
        X_processed = self.preprocess_features(X)
        X_scaled = self.scaler.fit_transform(X_processed[feature_columns])
        
        # Train each model and calculate cross-validation scores
        cv_scores = {}
        for name, model in self.models.items():
            logging.info(f"Training {name}...")
            
            try:
                # Cross-validation
                scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
                cv_scores[name] = scores.mean()
                
                # Train the model
                model.fit(X_scaled, y)
                
                # Calculate feature importance if available
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[name] = dict(zip(feature_columns, model.feature_importances_))
                elif hasattr(model, 'coef_'):
                    self.feature_importance[name] = dict(zip(feature_columns, np.abs(model.coef_[0])))
                
                logging.info(f"{name} trained successfully. CV Score: {cv_scores[name]:.4f}")
                
            except Exception as e:
                logging.error(f"Error training {name}: {str(e)}")
                cv_scores[name] = 0.0
        
        # Optimize weights based on cross-validation scores
        total_score = sum(cv_scores.values())
        if total_score > 0:
            for name in self.models.keys():
                self.weights[name] = cv_scores[name] / total_score
        else:
            # Equal weights if all models failed
            for name in self.models.keys():
                self.weights[name] = 1.0 / len(self.models)
        
        # Set confidence thresholds based on model performance
        for name, score in cv_scores.items():
            self.confidence_thresholds[name] = max(0.6, score * 0.8)
        
        self.is_trained = True
        logging.info("Advanced ensemble model training completed!")
        logging.info(f"Model weights: {self.weights}")
        
        return cv_scores
    
    def predict(self, X: pd.DataFrame, feature_columns: List[str]) -> Dict:
        """Make predictions with confidence scores and ensemble voting"""
        
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_processed = self.preprocess_features(X)
        X_scaled = self.scaler.transform(X_processed[feature_columns])
        
        predictions = {}
        probabilities = {}
        confidences = {}
        
        # Get predictions from each model
        for name, model in self.models.items():
            try:
                pred = model.predict(X_scaled)
                prob = model.predict_proba(X_scaled)
                
                predictions[name] = pred
                probabilities[name] = prob
                
                # Calculate confidence based on probability
                max_probs = np.max(prob, axis=1)
                confidences[name] = max_probs
                
            except Exception as e:
                logging.error(f"Error getting predictions from {name}: {str(e)}")
                predictions[name] = np.zeros(len(X))
                probabilities[name] = np.zeros((len(X), 2))
                confidences[name] = np.zeros(len(X))
        
        # Weighted ensemble prediction
        weighted_probs = np.zeros((len(X), 2))
        total_weight = 0
        
        for name in self.models.keys():
            weight = self.weights[name]
            weighted_probs += weight * probabilities[name]
            total_weight += weight
        
        if total_weight > 0:
            weighted_probs /= total_weight
        
        ensemble_prediction = np.argmax(weighted_probs, axis=1)
        ensemble_confidence = np.max(weighted_probs, axis=1)
        
        # Calculate ensemble confidence threshold
        ensemble_threshold = np.mean(list(self.confidence_thresholds.values()))
        
        # Filter predictions by confidence
        high_confidence_mask = ensemble_confidence >= ensemble_threshold
        
        return {
            'prediction': ensemble_prediction,
            'confidence': ensemble_confidence,
            'high_confidence': high_confidence_mask,
            'individual_predictions': predictions,
            'individual_confidences': confidences,
            'ensemble_probabilities': weighted_probs,
            'model_weights': self.weights,
            'confidence_threshold': ensemble_threshold
        }
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series, feature_columns: List[str]) -> Dict:
        """Comprehensive model evaluation"""
        
        predictions = self.predict(X_test, feature_columns)
        
        # Overall metrics
        accuracy = accuracy_score(y_test, predictions['prediction'])
        precision = precision_score(y_test, predictions['prediction'], average='weighted')
        recall = recall_score(y_test, predictions['prediction'], average='weighted')
        f1 = f1_score(y_test, predictions['prediction'], average='weighted')
        
        # High confidence predictions only
        high_conf_pred = predictions['prediction'][predictions['high_confidence']]
        high_conf_true = y_test[predictions['high_confidence']]
        
        if len(high_conf_pred) > 0:
            high_conf_accuracy = accuracy_score(high_conf_true, high_conf_pred)
            high_conf_precision = precision_score(high_conf_true, high_conf_pred, average='weighted')
        else:
            high_conf_accuracy = 0
            high_conf_precision = 0
        
        # Individual model performance
        model_performance = {}
        for name in self.models.keys():
            if name in predictions['individual_predictions']:
                model_acc = accuracy_score(y_test, predictions['individual_predictions'][name])
                model_performance[name] = {
                    'accuracy': model_acc,
                    'weight': self.weights[name]
                }
        
        return {
            'overall_accuracy': accuracy,
            'overall_precision': precision,
            'overall_recall': recall,
            'overall_f1': f1,
            'high_confidence_accuracy': high_conf_accuracy,
            'high_confidence_precision': high_conf_precision,
            'confidence_threshold': predictions['confidence_threshold'],
            'model_performance': model_performance,
            'feature_importance': self.feature_importance
        }
    
    def save_model(self, filepath: str):
        """Save the trained ensemble model"""
        model_data = {
            'models': self.models,
            'weights': self.weights,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance,
            'confidence_thresholds': self.confidence_thresholds,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        logging.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained ensemble model"""
        model_data = joblib.load(filepath)
        self.models = model_data['models']
        self.weights = model_data['weights']
        self.scaler = model_data['scaler']
        self.feature_importance = model_data['feature_importance']
        self.confidence_thresholds = model_data['confidence_thresholds']
        self.is_trained = model_data['is_trained']
        logging.info(f"Model loaded from {filepath}")
    
    def get_feature_importance_summary(self) -> pd.DataFrame:
        """Get comprehensive feature importance summary"""
        if not self.feature_importance:
            return pd.DataFrame()
        
        # Combine feature importance from all models
        all_features = set()
        for model_importance in self.feature_importance.values():
            all_features.update(model_importance.keys())
        
        importance_df = pd.DataFrame(index=list(all_features))
        
        for model_name, importance_dict in self.feature_importance.items():
            importance_df[model_name] = importance_df.index.map(importance_dict).fillna(0)
        
        # Calculate weighted average importance
        importance_df['weighted_avg'] = 0
        for model_name in self.models.keys():
            if model_name in self.weights:
                importance_df['weighted_avg'] += self.weights[model_name] * importance_df[model_name]
        
        return importance_df.sort_values('weighted_avg', ascending=False)
