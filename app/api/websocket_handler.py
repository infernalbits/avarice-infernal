"""
WebSocket handler for real-time updates
Provides live data streaming to the frontend
"""

from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio
from app.api.sportsradar_client import SportRadarClient
from app.api.live_data_client import LiveDataClient


class WebSocketHandler:
    """Handles real-time WebSocket connections and data streaming"""
    
    def __init__(self, app: Flask = None):
        self.socketio = None
        self.sports_client = SportRadarClient()
        self.live_client = LiveDataClient()
        self.active_subscriptions = {}
        self.update_threads = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize WebSocket with Flask app"""
        self.socketio = SocketIO(
            app, 
            cors_allowed_origins="*",
            async_mode='threading',
            ping_timeout=60,
            ping_interval=25
        )
        
        # Register event handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"Client connected: {request.sid}")
            emit('connected', {'status': 'Connected to Sports Betting AI'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"Client disconnected: {request.sid}")
            self.cleanup_client_subscriptions(request.sid)
        
        @self.socketio.on('subscribe_live_odds')
        def handle_subscribe_odds(data):
            """Subscribe to live odds updates"""
            sport = data.get('sport', 'nfl')
            room = f"odds_{sport}"
            
            join_room(room)
            
            if room not in self.active_subscriptions:
                self.active_subscriptions[room] = set()
            self.active_subscriptions[room].add(request.sid)
            
            # Start odds update thread if not already running
            if room not in self.update_threads:
                thread = threading.Thread(
                    target=self.stream_live_odds,
                    args=(sport, room),
                    daemon=True
                )
                thread.start()
                self.update_threads[room] = thread
            
            emit('subscribed', {'type': 'live_odds', 'sport': sport})
        
        @self.socketio.on('subscribe_game_updates')
        def handle_subscribe_games(data):
            """Subscribe to game status updates"""
            sport = data.get('sport', 'nfl')
            room = f"games_{sport}"
            
            join_room(room)
            
            if room not in self.active_subscriptions:
                self.active_subscriptions[room] = set()
            self.active_subscriptions[room].add(request.sid)
            
            # Start game updates thread
            if room not in self.update_threads:
                thread = threading.Thread(
                    target=self.stream_game_updates,
                    args=(sport, room),
                    daemon=True
                )
                thread.start()
                self.update_threads[room] = thread
            
            emit('subscribed', {'type': 'game_updates', 'sport': sport})
        
        @self.socketio.on('subscribe_predictions')
        def handle_subscribe_predictions(data):
            """Subscribe to new prediction alerts"""
            sport = data.get('sport', 'nfl')
            confidence_threshold = data.get('min_confidence', 0.65)
            room = f"predictions_{sport}"
            
            join_room(room)
            
            if room not in self.active_subscriptions:
                self.active_subscriptions[room] = set()
            self.active_subscriptions[room].add(request.sid)
            
            # Start predictions thread
            if room not in self.update_threads:
                thread = threading.Thread(
                    target=self.stream_prediction_alerts,
                    args=(sport, room, confidence_threshold),
                    daemon=True
                )
                thread.start()
                self.update_threads[room] = thread
            
            emit('subscribed', {'type': 'predictions', 'sport': sport})
        
        @self.socketio.on('unsubscribe')
        def handle_unsubscribe(data):
            """Unsubscribe from updates"""
            subscription_type = data.get('type')
            sport = data.get('sport', 'nfl')
            room = f"{subscription_type}_{sport}"
            
            leave_room(room)
            
            if room in self.active_subscriptions:
                self.active_subscriptions[room].discard(request.sid)
            
            emit('unsubscribed', {'type': subscription_type, 'sport': sport})
    
    def stream_live_odds(self, sport: str, room: str):
        """Stream live odds updates"""
        while room in self.active_subscriptions and self.active_subscriptions[room]:
            try:
                # Get live odds data
                odds_data = asyncio.run(
                    self.live_client.get_live_odds_comprehensive(sport)
                )
                
                if odds_data and 'odds' in odds_data:
                    # Emit to all subscribers in room
                    self.socketio.emit(
                        'live_odds_update',
                        {
                            'sport': sport,
                            'data': odds_data,
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        room=room
                    )
                
                # Update every 30 seconds
                time.sleep(30)
                
            except Exception as e:
                print(f"Error streaming odds for {sport}: {e}")
                time.sleep(60)  # Wait longer on error
    
    def stream_game_updates(self, sport: str, room: str):
        """Stream game status and score updates"""
        while room in self.active_subscriptions and self.active_subscriptions[room]:
            try:
                # Get live game updates
                live_scores = asyncio.run(
                    self.live_client.get_real_time_scores(sport)
                )
                
                if live_scores:
                    self.socketio.emit(
                        'game_updates',
                        {
                            'sport': sport,
                            'games': live_scores,
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        room=room
                    )
                
                # Update every 60 seconds for scores
                time.sleep(60)
                
            except Exception as e:
                print(f"Error streaming game updates for {sport}: {e}")
                time.sleep(120)
    
    def stream_prediction_alerts(self, sport: str, room: str, min_confidence: float):
        """Stream high-confidence prediction alerts"""
        last_check = datetime.utcnow()
        
        while room in self.active_subscriptions and self.active_subscriptions[room]:
            try:
                # Check for new high-confidence predictions
                # This would integrate with your ML prediction pipeline
                new_predictions = self.check_new_predictions(sport, min_confidence, last_check)
                
                if new_predictions:
                    self.socketio.emit(
                        'prediction_alert',
                        {
                            'sport': sport,
                            'predictions': new_predictions,
                            'timestamp': datetime.utcnow().isoformat(),
                            'alert_level': 'high' if any(p['confidence_score'] > 0.8 for p in new_predictions) else 'medium'
                        },
                        room=room
                    )
                
                last_check = datetime.utcnow()
                
                # Check every 5 minutes for new predictions
                time.sleep(300)
                
            except Exception as e:
                print(f"Error streaming predictions for {sport}: {e}")
                time.sleep(600)
    
    def check_new_predictions(self, sport: str, min_confidence: float, since: datetime) -> List[Dict]:
        """Check for new high-confidence predictions since last check"""
        # This would integrate with your actual prediction pipeline
        # For now, return mock high-confidence alerts
        
        import random
        
        if random.random() < 0.3:  # 30% chance of new prediction
            return [{
                'game': {
                    'home_team': 'Chiefs',
                    'away_team': 'Bills',
                    'start_time': (datetime.utcnow() + timedelta(days=1)).isoformat()
                },
                'prediction': {
                    'bet_type': 'moneyline',
                    'predicted_outcome': 'away',
                    'confidence_score': random.uniform(min_confidence, 0.95),
                    'expected_value': random.uniform(5, 15),
                    'recommended_stake': random.uniform(20, 80)
                },
                'market_intelligence': {
                    'reasoning': 'Sharp money on Bills, public heavy on Chiefs - classic fade spot',
                    'steam_detected': True,
                    'contrarian_opportunity': True
                }
            }]
        
        return []
    
    def broadcast_system_alert(self, alert_type: str, message: str, data: Dict = None):
        """Broadcast system-wide alerts"""
        self.socketio.emit(
            'system_alert',
            {
                'type': alert_type,
                'message': message,
                'data': data or {},
                'timestamp': datetime.utcnow().isoformat()
            },
            broadcast=True
        )
    
    def send_market_alert(self, sport: str, alert_data: Dict):
        """Send market-specific alerts"""
        room = f"odds_{sport}"
        
        self.socketio.emit(
            'market_alert',
            {
                'sport': sport,
                'alert': alert_data,
                'timestamp': datetime.utcnow().isoformat()
            },
            room=room
        )
    
    def cleanup_client_subscriptions(self, client_id: str):
        """Clean up subscriptions when client disconnects"""
        for room, subscribers in self.active_subscriptions.items():
            subscribers.discard(client_id)
            
            # Stop threads if no more subscribers
            if not subscribers and room in self.update_threads:
                # Thread will stop on next iteration when it checks subscribers
                pass
    
    def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        return {
            'active_rooms': len(self.active_subscriptions),
            'total_subscribers': sum(len(subs) for subs in self.active_subscriptions.values()),
            'active_threads': len(self.update_threads),
            'room_details': {
                room: len(subscribers) 
                for room, subscribers in self.active_subscriptions.items()
            }
        }


# Global WebSocket handler instance
websocket_handler = WebSocketHandler()


def init_websockets(app: Flask) -> WebSocketHandler:
    """Initialize WebSocket handler with Flask app"""
    websocket_handler.init_app(app)
    return websocket_handler
