"""
Advanced Risk Management System
Implements portfolio theory, correlation analysis, and dynamic risk controls
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from scipy.optimize import minimize
from sklearn.covariance import EmpiricalCovariance
import warnings
warnings.filterwarnings('ignore')

from app.models import Bet, Game, Bankroll
from app import db


class AdvancedRiskManager:
    """Advanced risk management with portfolio optimization"""
    
    def __init__(self):
        self.max_portfolio_correlation = 0.7  # Maximum correlation between bets
        self.max_single_bet_weight = 0.15     # Maximum 15% of bankroll on single bet
        self.max_daily_risk = 0.25            # Maximum 25% of bankroll at risk per day
        self.min_diversification_score = 0.6  # Minimum portfolio diversification
        
        # Risk tolerance levels
        self.risk_levels = {
            'conservative': {'max_bet': 0.08, 'max_daily': 0.15, 'min_confidence': 0.75},
            'moderate': {'max_bet': 0.12, 'max_daily': 0.20, 'min_confidence': 0.70},
            'aggressive': {'max_bet': 0.15, 'max_daily': 0.25, 'min_confidence': 0.65}
        }
        
        self.current_risk_level = 'moderate'
    
    def calculate_optimal_portfolio(self, predictions: List[Dict], bankroll: float) -> Dict:
        """Calculate optimal bet sizing using Modern Portfolio Theory"""
        
        if not predictions:
            return {'bets': [], 'total_risk': 0, 'expected_return': 0}
        
        # Extract prediction data
        expected_returns = []
        probabilities = []
        correlations = []
        
        for pred in predictions:
            # Calculate expected return
            prob = pred['prediction']['probability']
            odds = self._extract_odds(pred)
            
            if odds and prob > 0:
                expected_return = (prob * (odds - 1)) - ((1 - prob) * 1)
                expected_returns.append(expected_return)
                probabilities.append(prob)
            else:
                expected_returns.append(0)
                probabilities.append(0.5)
        
        expected_returns = np.array(expected_returns)
        
        # Calculate correlation matrix
        correlation_matrix = self._estimate_bet_correlations(predictions)
        
        # Optimize portfolio using mean-variance optimization
        optimal_weights = self._optimize_portfolio_weights(
            expected_returns, correlation_matrix, bankroll
        )
        
        # Apply additional risk constraints
        adjusted_weights = self._apply_risk_constraints(
            optimal_weights, predictions, bankroll
        )
        
        # Create betting recommendations
        betting_plan = self._create_betting_plan(
            predictions, adjusted_weights, bankroll
        )
        
        return {
            'betting_plan': betting_plan,
            'portfolio_metrics': self._calculate_portfolio_metrics(
                adjusted_weights, expected_returns, correlation_matrix
            ),
            'risk_analysis': self._analyze_portfolio_risk(betting_plan, bankroll)
        }
    
    def _estimate_bet_correlations(self, predictions: List[Dict]) -> np.ndarray:
        """Estimate correlations between betting opportunities"""
        n_bets = len(predictions)
        correlation_matrix = np.eye(n_bets)
        
        for i in range(n_bets):
            for j in range(i + 1, n_bets):
                pred_i = predictions[i]
                pred_j = predictions[j]
                
                correlation = self._calculate_bet_correlation(pred_i, pred_j)
                correlation_matrix[i, j] = correlation
                correlation_matrix[j, i] = correlation
        
        return correlation_matrix
    
    def _calculate_bet_correlation(self, pred1: Dict, pred2: Dict) -> float:
        """Calculate correlation between two betting opportunities"""
        correlation = 0.0
        
        game1 = pred1.get('game', {})
        game2 = pred2.get('game', {})
        
        # Same game correlation
        if (game1.get('home_team') == game2.get('home_team') or 
            game1.get('away_team') == game2.get('away_team')):
            correlation += 0.8
        
        # Same sport correlation
        if game1.get('sport') == game2.get('sport'):
            correlation += 0.2
        
        # Same bet type correlation
        if (pred1.get('prediction', {}).get('bet_type') == 
            pred2.get('prediction', {}).get('bet_type')):
            correlation += 0.1
        
        # Time proximity correlation
        time1_str = game1.get('commence_time', '')
        time2_str = game2.get('commence_time', '')
        
        if time1_str and time2_str:
            try:
                time1 = datetime.fromisoformat(time1_str.replace('Z', '+00:00'))
                time2 = datetime.fromisoformat(time2_str.replace('Z', '+00:00'))
                time_diff = abs((time1 - time2).total_seconds()) / 3600  # hours
                
                if time_diff < 24:  # Same day
                    correlation += 0.15
                elif time_diff < 72:  # Same weekend
                    correlation += 0.05
            except:
                pass
        
        return min(correlation, 0.95)  # Cap at 95%
    
    def _optimize_portfolio_weights(self, expected_returns: np.ndarray, 
                                  correlation_matrix: np.ndarray, 
                                  bankroll: float) -> np.ndarray:
        """Optimize portfolio weights using mean-variance optimization"""
        
        n_assets = len(expected_returns)
        
        if n_assets == 0:
            return np.array([])
        
        # Risk aversion parameter (higher = more conservative)
        risk_aversion = 2.0
        
        # Objective function: maximize utility (return - risk penalty)
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights, np.dot(correlation_matrix, weights))
            utility = portfolio_return - (risk_aversion * portfolio_variance)
            return -utility  # Minimize negative utility
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},  # Weights sum to 1
        ]
        
        # Bounds (0 to max single bet weight)
        max_weight = self.risk_levels[self.current_risk_level]['max_bet']
        bounds = [(0, max_weight) for _ in range(n_assets)]
        
        # Initial guess (equal weights)
        initial_weights = np.ones(n_assets) / n_assets
        
        # Only optimize if we have positive expected returns
        if np.any(expected_returns > 0):
            try:
                result = minimize(
                    objective, initial_weights, 
                    method='SLSQP', 
                    bounds=bounds, 
                    constraints=constraints
                )
                
                if result.success:
                    return result.x
                else:
                    print(f"Optimization failed: {result.message}")
            except Exception as e:
                print(f"Portfolio optimization error: {e}")
        
        # Fallback: equal weights with risk constraints
        equal_weights = np.ones(n_assets) / n_assets
        return np.minimum(equal_weights, max_weight)
    
    def _apply_risk_constraints(self, weights: np.ndarray, 
                              predictions: List[Dict], 
                              bankroll: float) -> np.ndarray:
        """Apply additional risk management constraints"""
        
        if len(weights) == 0:
            return weights
        
        risk_settings = self.risk_levels[self.current_risk_level]
        
        # Apply maximum single bet constraint
        max_single_weight = risk_settings['max_bet']
        weights = np.minimum(weights, max_single_weight)
        
        # Apply maximum daily risk constraint
        total_daily_risk = np.sum(weights)
        max_daily_weight = risk_settings['max_daily']
        
        if total_daily_risk > max_daily_weight:
            scaling_factor = max_daily_weight / total_daily_risk
            weights *= scaling_factor
        
        # Apply minimum confidence constraint
        min_confidence = risk_settings['min_confidence']
        for i, pred in enumerate(predictions):
            confidence = pred.get('prediction', {}).get('confidence_score', 0)
            if confidence < min_confidence:
                weights[i] = 0
        
        # Renormalize if needed
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights) * min(np.sum(weights), max_daily_weight)
        
        return weights
    
    def _create_betting_plan(self, predictions: List[Dict], 
                           weights: np.ndarray, 
                           bankroll: float) -> List[Dict]:
        """Create detailed betting plan with stake amounts"""
        
        betting_plan = []
        
        for i, (pred, weight) in enumerate(zip(predictions, weights)):
            if weight > 0.001:  # Minimum meaningful weight
                stake = weight * bankroll
                
                betting_plan.append({
                    'game': pred.get('game', {}),
                    'prediction': pred.get('prediction', {}),
                    'recommended_stake': round(stake, 2),
                    'weight_in_portfolio': round(weight, 4),
                    'expected_value': self._calculate_expected_value(pred, stake),
                    'risk_contribution': self._calculate_risk_contribution(pred, weight),
                    'confidence_tier': self._get_confidence_tier(
                        pred.get('prediction', {}).get('confidence_score', 0)
                    )
                })
        
        # Sort by expected value (highest first)
        betting_plan.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return betting_plan
    
    def _calculate_expected_value(self, prediction: Dict, stake: float) -> float:
        """Calculate expected value for a bet"""
        prob = prediction.get('prediction', {}).get('probability', 0.5)
        odds = self._extract_odds(prediction)
        
        if odds and prob > 0:
            return (prob * (odds - 1) * stake) - ((1 - prob) * stake)
        return 0
    
    def _extract_odds(self, prediction: Dict) -> Optional[float]:
        """Extract odds from prediction data"""
        # This would extract odds from the prediction
        # For now, use a mock value
        return 2.0  # Mock odds
    
    def _calculate_risk_contribution(self, prediction: Dict, weight: float) -> float:
        """Calculate risk contribution of a bet to the portfolio"""
        confidence = prediction.get('prediction', {}).get('confidence_score', 0.5)
        variance = (1 - confidence) * weight
        return variance
    
    def _get_confidence_tier(self, confidence: float) -> str:
        """Get confidence tier for a prediction"""
        if confidence >= 0.80:
            return 'high'
        elif confidence >= 0.70:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_portfolio_metrics(self, weights: np.ndarray, 
                                   expected_returns: np.ndarray,
                                   correlation_matrix: np.ndarray) -> Dict:
        """Calculate portfolio performance metrics"""
        
        if len(weights) == 0:
            return {}
        
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_variance = np.dot(weights, np.dot(correlation_matrix, weights))
        portfolio_std = np.sqrt(portfolio_variance)
        
        # Sharpe ratio (assuming risk-free rate of 0)
        sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
        
        # Diversification ratio
        avg_correlation = np.mean(correlation_matrix[np.triu_indices_from(correlation_matrix, k=1)])
        diversification_score = 1 - avg_correlation
        
        return {
            'expected_return': round(portfolio_return, 4),
            'volatility': round(portfolio_std, 4),
            'sharpe_ratio': round(sharpe_ratio, 4),
            'diversification_score': round(diversification_score, 4),
            'number_of_bets': np.sum(weights > 0.001),
            'max_bet_weight': round(np.max(weights), 4),
            'portfolio_concentration': round(np.sum(weights**2), 4)  # Herfindahl index
        }
    
    def _analyze_portfolio_risk(self, betting_plan: List[Dict], bankroll: float) -> Dict:
        """Analyze portfolio risk characteristics"""
        
        total_stake = sum(bet['recommended_stake'] for bet in betting_plan)
        total_expected_value = sum(bet['expected_value'] for bet in betting_plan)
        
        # Calculate Value at Risk (VaR) at 95% confidence
        var_95 = self._calculate_var(betting_plan, 0.95)
        
        # Calculate maximum potential loss
        max_loss = total_stake  # Worst case: lose all bets
        
        # Risk categories
        sport_exposure = {}
        bet_type_exposure = {}
        
        for bet in betting_plan:
            sport = bet['game'].get('sport', 'unknown')
            bet_type = bet['prediction'].get('bet_type', 'unknown')
            
            sport_exposure[sport] = sport_exposure.get(sport, 0) + bet['recommended_stake']
            bet_type_exposure[bet_type] = bet_type_exposure.get(bet_type, 0) + bet['recommended_stake']
        
        return {
            'total_stake': round(total_stake, 2),
            'percentage_of_bankroll': round((total_stake / bankroll) * 100, 2),
            'expected_profit': round(total_expected_value, 2),
            'var_95': round(var_95, 2),
            'max_potential_loss': round(max_loss, 2),
            'profit_to_risk_ratio': round(total_expected_value / total_stake, 4) if total_stake > 0 else 0,
            'sport_exposure': {k: round(v, 2) for k, v in sport_exposure.items()},
            'bet_type_exposure': {k: round(v, 2) for k, v in bet_type_exposure.items()},
            'risk_level': self.current_risk_level,
            'risk_warnings': self._generate_risk_warnings(betting_plan, bankroll)
        }
    
    def _calculate_var(self, betting_plan: List[Dict], confidence_level: float) -> float:
        """Calculate Value at Risk using Monte Carlo simulation"""
        
        n_simulations = 10000
        outcomes = []
        
        for _ in range(n_simulations):
            portfolio_pnl = 0
            
            for bet in betting_plan:
                # Simulate bet outcome
                prob = bet['prediction'].get('probability', 0.5)
                stake = bet['recommended_stake']
                
                if np.random.random() < prob:
                    # Win
                    odds = self._extract_odds({'prediction': bet['prediction']})
                    portfolio_pnl += stake * (odds - 1) if odds else stake * 0.9
                else:
                    # Loss
                    portfolio_pnl -= stake
            
            outcomes.append(portfolio_pnl)
        
        # Calculate VaR
        var_percentile = (1 - confidence_level) * 100
        var = np.percentile(outcomes, var_percentile)
        
        return var
    
    def _generate_risk_warnings(self, betting_plan: List[Dict], bankroll: float) -> List[str]:
        """Generate risk warnings based on portfolio analysis"""
        
        warnings = []
        total_stake = sum(bet['recommended_stake'] for bet in betting_plan)
        
        # High concentration warning
        if total_stake / bankroll > 0.3:
            warnings.append("HIGH RISK: Portfolio concentration exceeds 30% of bankroll")
        
        # Correlation warning
        correlations = []
        for i in range(len(betting_plan)):
            for j in range(i + 1, len(betting_plan)):
                corr = self._calculate_bet_correlation(
                    {'game': betting_plan[i]['game'], 'prediction': betting_plan[i]['prediction']},
                    {'game': betting_plan[j]['game'], 'prediction': betting_plan[j]['prediction']}
                )
                correlations.append(corr)
        
        if correlations and np.mean(correlations) > 0.6:
            warnings.append("MEDIUM RISK: High correlation between bets reduces diversification")
        
        # Low confidence warning
        low_confidence_bets = [bet for bet in betting_plan 
                              if bet['prediction'].get('confidence_score', 0) < 0.7]
        if len(low_confidence_bets) > len(betting_plan) * 0.5:
            warnings.append("MEDIUM RISK: More than 50% of bets have low confidence")
        
        return warnings
    
    def update_risk_level(self, new_level: str):
        """Update risk management level"""
        if new_level in self.risk_levels:
            self.current_risk_level = new_level
            print(f"Risk level updated to: {new_level}")
        else:
            print(f"Invalid risk level: {new_level}")
    
    def get_risk_summary(self) -> Dict:
        """Get current risk management settings summary"""
        current_settings = self.risk_levels[self.current_risk_level]
        
        return {
            'current_level': self.current_risk_level,
            'settings': current_settings,
            'constraints': {
                'max_portfolio_correlation': self.max_portfolio_correlation,
                'max_single_bet_weight': self.max_single_bet_weight,
                'max_daily_risk': self.max_daily_risk,
                'min_diversification_score': self.min_diversification_score
            },
            'available_levels': list(self.risk_levels.keys())
        }
