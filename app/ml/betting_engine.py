import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.models import Game, Bet, Bankroll, Prediction
from app.ml.prediction_model import PredictionModel
from app import db
from config import Config

class BettingEngine:
    """
    Automated betting engine that analyzes predictions and places bets
    """
    
    def __init__(self):
        self.prediction_model = PredictionModel()
        self.min_confidence = Config.MIN_CONFIDENCE_THRESHOLD
        self.max_bet_percentage = Config.MAX_BET_PERCENTAGE
        self.kelly_multiplier = 0.5  # Conservative Kelly Criterion multiplier
        
    def calculate_kelly_bet_size(self, probability: float, odds: float, bankroll: float) -> float:
        """
        Calculate optimal bet size using Kelly Criterion
        
        Args:
            probability: Predicted probability of winning (0-1)
            odds: American odds
            bankroll: Current bankroll
            
        Returns:
            Recommended bet size
        """
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Kelly formula: f = (bp - q) / b
        # where: b = odds received on bet, p = probability of winning, q = probability of losing
        b = decimal_odds - 1
        p = probability
        q = 1 - probability
        
        kelly_fraction = (b * p - q) / b
        
        # Apply conservative multiplier and cap at max percentage
        kelly_fraction = max(0, kelly_fraction * self.kelly_multiplier)
        kelly_fraction = min(kelly_fraction, self.max_bet_percentage)
        
        return bankroll * kelly_fraction
    
    def calculate_value_bet(self, prediction_prob: float, market_odds: float) -> Tuple[bool, float]:
        """
        Determine if a bet has positive expected value
        
        Args:
            prediction_prob: Model's predicted probability
            market_odds: Market odds (American format)
            
        Returns:
            Tuple of (is_value_bet, edge_percentage)
        """
        # Convert market odds to implied probability
        if market_odds > 0:
            implied_prob = 100 / (market_odds + 100)
        else:
            implied_prob = abs(market_odds) / (abs(market_odds) + 100)
        
        # Calculate edge
        edge = prediction_prob - implied_prob
        edge_percentage = (edge / implied_prob) * 100 if implied_prob > 0 else 0
        
        # Require minimum edge for value bet
        is_value = edge > 0.05  # 5% minimum edge
        
        return is_value, edge_percentage
    
    def analyze_game_for_bets(self, game: Game) -> List[Dict]:
        """
        Analyze a game and generate betting recommendations
        
        Args:
            game: Game object to analyze
            
        Returns:
            List of bet recommendations
        """
        recommendations = []
        
        # Get model predictions
        predictions = self.prediction_model.predict_game(game)
        
        if not predictions:
            return recommendations
        
        # Get current bankroll
        bankroll = Bankroll.query.first()
        if not bankroll:
            return recommendations
        
        for prediction in predictions:
            bet_type = prediction['bet_type']
            predicted_outcome = prediction['predicted_outcome']
            probability = prediction['probability']
            confidence = prediction['confidence_score']
            
            # Skip low confidence predictions
            if confidence < self.min_confidence:
                continue
            
            # Get relevant odds based on bet type and outcome
            odds = self._get_relevant_odds(game, bet_type, predicted_outcome)
            if not odds:
                continue
            
            # Check for value bet
            is_value, edge = self.calculate_value_bet(probability, odds)
            
            if is_value:
                # Calculate bet size using Kelly Criterion
                bet_size = self.calculate_kelly_bet_size(probability, odds, bankroll.current_balance)
                
                # Apply minimum and maximum bet constraints
                min_bet = 10.0  # Minimum $10 bet
                max_bet = bankroll.current_balance * self.max_bet_percentage
                
                bet_size = max(min_bet, min(bet_size, max_bet))
                
                # Calculate expected value
                expected_value = self._calculate_expected_value(probability, odds, bet_size)
                
                recommendation = {
                    'game_id': game.external_id,
                    'game_info': {
                        'home_team': game.home_team,
                        'away_team': game.away_team,
                        'commence_time': game.commence_time.isoformat(),
                        'sport': game.sport
                    },
                    'bet_type': bet_type,
                    'bet_value': predicted_outcome,
                    'odds': odds,
                    'predicted_probability': probability,
                    'confidence_score': confidence,
                    'edge_percentage': edge,
                    'recommended_stake': round(bet_size, 2),
                    'expected_value': round(expected_value, 2),
                    'kelly_percentage': round((bet_size / bankroll.current_balance) * 100, 2),
                    'reasoning': self._generate_bet_reasoning(prediction, edge, confidence)
                }
                
                recommendations.append(recommendation)
        
        # Sort by expected value descending
        recommendations.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return recommendations
    
    def _get_relevant_odds(self, game: Game, bet_type: str, outcome: str) -> Optional[float]:
        """Get the relevant odds for a specific bet type and outcome"""
        if bet_type == 'moneyline':
            if outcome == 'home':
                return game.home_odds
            elif outcome == 'away':
                return game.away_odds
            elif outcome == 'draw':
                return game.draw_odds
        elif bet_type == 'spread':
            # For spread, we assume the prediction is for home team covering
            if outcome == 'home':
                return game.home_odds  # This would be spread odds in practice
            elif outcome == 'away':
                return game.away_odds
        elif bet_type == 'total':
            if outcome == 'over':
                return game.over_odds
            elif outcome == 'under':
                return game.under_odds
        
        return None
    
    def _calculate_expected_value(self, probability: float, odds: float, stake: float) -> float:
        """Calculate expected value of a bet"""
        if odds > 0:
            win_amount = stake * (odds / 100)
        else:
            win_amount = stake * (100 / abs(odds))
        
        expected_win = probability * win_amount
        expected_loss = (1 - probability) * stake
        
        return expected_win - expected_loss
    
    def _generate_bet_reasoning(self, prediction: Dict, edge: float, confidence: float) -> str:
        """Generate human-readable reasoning for the bet recommendation"""
        bet_type = prediction['bet_type']
        outcome = prediction['predicted_outcome']
        
        reasoning_parts = []
        
        if confidence >= 0.8:
            reasoning_parts.append("High confidence prediction")
        elif confidence >= 0.7:
            reasoning_parts.append("Strong prediction")
        else:
            reasoning_parts.append("Moderate confidence prediction")
        
        reasoning_parts.append(f"{edge:.1f}% edge over market")
        
        if bet_type == 'moneyline':
            reasoning_parts.append(f"Model strongly favors {outcome} to win")
        elif bet_type == 'spread':
            reasoning_parts.append(f"Model predicts {outcome} covers the spread")
        elif bet_type == 'total':
            reasoning_parts.append(f"Model predicts game goes {outcome}")
        
        return ". ".join(reasoning_parts) + "."
    
    def simulate_bet_placement(self, recommendations: List[Dict], max_bets: int = 5) -> List[Dict]:
        """
        Simulate placing bets based on recommendations
        
        Args:
            recommendations: List of bet recommendations
            max_bets: Maximum number of bets to place
            
        Returns:
            List of placed bet simulations
        """
        placed_bets = []
        bankroll = Bankroll.query.first()
        
        if not bankroll:
            return placed_bets
        
        # Sort recommendations by expected value and take top N
        top_recommendations = recommendations[:max_bets]
        
        for rec in top_recommendations:
            # Check if bankroll allows this bet
            can_bet, message = bankroll.can_place_bet(rec['recommended_stake'])
            
            if can_bet:
                # Create simulated bet
                bet_simulation = {
                    'game_id': rec['game_id'],
                    'sport': rec['game_info']['sport'],
                    'bet_type': rec['bet_type'],
                    'bet_value': rec['bet_value'],
                    'odds': rec['odds'],
                    'stake': rec['recommended_stake'],
                    'predicted_probability': rec['predicted_probability'],
                    'confidence_score': rec['confidence_score'],
                    'expected_value': rec['expected_value'],
                    'edge_percentage': rec['edge_percentage'],
                    'reasoning': rec['reasoning'],
                    'status': 'simulated',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                placed_bets.append(bet_simulation)
                
                # Update simulated bankroll
                bankroll.current_balance -= rec['recommended_stake']
            else:
                print(f"Cannot place bet: {message}")
                break
        
        return placed_bets
    
    def run_daily_analysis(self) -> Dict:
        """
        Run daily analysis and generate betting recommendations
        
        Returns:
            Dictionary with analysis results
        """
        # Get upcoming games for next 3 days
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(days=3)
        
        upcoming_games = Game.query.filter(
            Game.commence_time >= start_time,
            Game.commence_time <= end_time,
            Game.completed == False
        ).order_by(Game.commence_time).all()
        
        all_recommendations = []
        analysis_summary = {
            'games_analyzed': len(upcoming_games),
            'total_recommendations': 0,
            'high_confidence_bets': 0,
            'total_expected_value': 0.0,
            'sports_covered': set()
        }
        
        for game in upcoming_games:
            try:
                game_recommendations = self.analyze_game_for_bets(game)
                all_recommendations.extend(game_recommendations)
                
                analysis_summary['sports_covered'].add(game.sport)
                
                for rec in game_recommendations:
                    analysis_summary['total_expected_value'] += rec['expected_value']
                    if rec['confidence_score'] >= 0.75:
                        analysis_summary['high_confidence_bets'] += 1
                
            except Exception as e:
                print(f"Error analyzing game {game.external_id}: {e}")
                continue
        
        analysis_summary['total_recommendations'] = len(all_recommendations)
        analysis_summary['sports_covered'] = list(analysis_summary['sports_covered'])
        
        # Simulate bet placement
        simulated_bets = self.simulate_bet_placement(all_recommendations)
        
        return {
            'analysis_summary': analysis_summary,
            'recommendations': all_recommendations,
            'simulated_bets': simulated_bets,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def backtest_strategy(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Backtest the betting strategy on historical data
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            
        Returns:
            Backtest results
        """
        # Get historical games with results
        historical_games = Game.query.filter(
            Game.commence_time >= start_date,
            Game.commence_time <= end_date,
            Game.completed == True,
            Game.home_score.isnot(None),
            Game.away_score.isnot(None)
        ).order_by(Game.commence_time).all()
        
        # Initialize backtest variables
        starting_bankroll = 1000.0
        current_bankroll = starting_bankroll
        total_bets = 0
        winning_bets = 0
        total_staked = 0.0
        total_profit = 0.0
        
        bet_history = []
        
        for game in historical_games:
            # Skip if game doesn't have odds
            if not game.home_odds or not game.away_odds:
                continue
            
            try:
                # Generate what the recommendations would have been
                recommendations = self.analyze_game_for_bets(game)
                
                for rec in recommendations:
                    if current_bankroll < rec['recommended_stake']:
                        continue
                    
                    total_bets += 1
                    stake = rec['recommended_stake']
                    total_staked += stake
                    current_bankroll -= stake
                    
                    # Determine actual outcome
                    actual_outcome = self._determine_actual_outcome(game, rec['bet_type'])
                    bet_won = (actual_outcome == rec['bet_value'])
                    
                    if bet_won:
                        winning_bets += 1
                        # Calculate winnings
                        odds = rec['odds']
                        if odds > 0:
                            winnings = stake * (odds / 100)
                        else:
                            winnings = stake * (100 / abs(odds))
                        
                        profit = winnings
                        current_bankroll += stake + winnings
                    else:
                        profit = -stake
                    
                    total_profit += profit
                    
                    bet_record = {
                        'game_id': game.external_id,
                        'date': game.commence_time.date().isoformat(),
                        'bet_type': rec['bet_type'],
                        'bet_value': rec['bet_value'],
                        'actual_outcome': actual_outcome,
                        'stake': stake,
                        'odds': rec['odds'],
                        'won': bet_won,
                        'profit': profit,
                        'bankroll_after': current_bankroll,
                        'confidence': rec['confidence_score']
                    }
                    
                    bet_history.append(bet_record)
                
            except Exception as e:
                print(f"Error in backtest for game {game.external_id}: {e}")
                continue
        
        # Calculate metrics
        win_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
        bankroll_growth = ((current_bankroll - starting_bankroll) / starting_bankroll * 100)
        
        return {
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': (end_date - start_date).days
            },
            'bankroll': {
                'starting': starting_bankroll,
                'ending': round(current_bankroll, 2),
                'growth_percentage': round(bankroll_growth, 2)
            },
            'betting_stats': {
                'total_bets': total_bets,
                'winning_bets': winning_bets,
                'losing_bets': total_bets - winning_bets,
                'win_rate': round(win_rate, 2),
                'total_staked': round(total_staked, 2),
                'total_profit': round(total_profit, 2),
                'roi': round(roi, 2)
            },
            'performance_metrics': {
                'average_bet_size': round(total_staked / total_bets, 2) if total_bets > 0 else 0,
                'profit_per_bet': round(total_profit / total_bets, 2) if total_bets > 0 else 0,
                'max_bankroll': max([bet['bankroll_after'] for bet in bet_history] + [starting_bankroll]),
                'min_bankroll': min([bet['bankroll_after'] for bet in bet_history] + [starting_bankroll])
            },
            'bet_history': bet_history[-50:]  # Last 50 bets for review
        }
    
    def _determine_actual_outcome(self, game: Game, bet_type: str) -> str:
        """Determine the actual outcome of a bet based on game results"""
        home_score = game.home_score
        away_score = game.away_score
        
        if bet_type == 'moneyline':
            if home_score > away_score:
                return 'home'
            elif away_score > home_score:
                return 'away'
            else:
                return 'draw'
        
        elif bet_type == 'spread':
            if game.point_spread:
                home_cover = (home_score - away_score) > game.point_spread
                return 'home' if home_cover else 'away'
        
        elif bet_type == 'total':
            if game.total_points:
                total_score = home_score + away_score
                return 'over' if total_score > game.total_points else 'under'
        
        return 'unknown'
