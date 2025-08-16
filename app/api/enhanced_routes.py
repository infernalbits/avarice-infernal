from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
from config import Config
from app.api.sportsradar_client import SportRadarClient

enhanced_api_bp = Blueprint('enhanced_api', __name__)
sportsradar_client = SportRadarClient()

@enhanced_api_bp.route('/live-odds', methods=['GET'])
def get_live_odds():
    """Get comprehensive live odds with market data"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    
    # Generate realistic mock data
    mock_games = []
    teams = [
        ('Kansas City Chiefs', 'Buffalo Bills'),
        ('Boston Celtics', 'LA Lakers'),
        ('Manchester City', 'Arsenal')
    ]
    
    for i, (home, away) in enumerate(teams):
        mock_games.append({
            'id': f'game_{i+1}',
            'homeTeam': home,
            'awayTeam': away,
            'startTime': (datetime.utcnow() + timedelta(days=i+1)).isoformat(),
            'odds': {
                'moneyline': {
                    'home': random.randint(-200, -110),
                    'away': random.randint(110, 200)
                },
                'spread': {
                    'home': round(random.uniform(-7, 7), 1),
                    'away': round(random.uniform(-7, 7), 1),
                    'homeOdds': -110,
                    'awayOdds': -110
                },
                'total': {
                    'line': round(random.uniform(42, 55), 1),
                    'over': -110,
                    'under': -110
                }
            },
            'consensus': {
                'books': random.randint(8, 15),
                'avgSpread': round(random.uniform(-7, 7), 1),
                'avgTotal': round(random.uniform(42, 55), 1),
                'spreadRange': {
                    'min': round(random.uniform(-8, -6), 1),
                    'max': round(random.uniform(-4, -2), 1)
                },
                'totalRange': {
                    'min': round(random.uniform(42, 48), 1),
                    'max': round(random.uniform(48, 55), 1)
                }
            }
        })
    
    return jsonify({
        'games': mock_games,
        'timestamp': datetime.utcnow().isoformat(),
        'sport': sport
    })

@enhanced_api_bp.route('/public-betting', methods=['GET'])
def get_public_betting():
    """Get public betting percentages and sharp money indicators"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    
    mock_public_data = {
        'games': [
            {
                'gameId': 'game_1',
                'homeTeam': 'Kansas City Chiefs',
                'awayTeam': 'Buffalo Bills',
                'publicBetting': {
                    'moneyline': {'homePercent': 72, 'awayPercent': 28},
                    'spread': {'homePercent': 68, 'awayPercent': 32},
                    'total': {'overPercent': 58, 'underPercent': 42}
                },
                'handle': {
                    'moneylineHome': 55,
                    'spreadHome': 45,
                    'totalOver': 62
                },
                'tickets': {
                    'moneylineHome': 72,
                    'spreadHome': 68,
                    'totalOver': 58
                },
                'sharpAction': {
                    'moneyline': 'away',
                    'spread': 'away',
                    'total': 'under',
                    'confidence': 78
                }
            },
            {
                'gameId': 'game_2',
                'homeTeam': 'Boston Celtics',
                'awayTeam': 'LA Lakers',
                'publicBetting': {
                    'moneyline': {'homePercent': 75, 'awayPercent': 25},
                    'spread': {'homePercent': 82, 'awayPercent': 18},
                    'total': {'overPercent': 65, 'underPercent': 35}
                },
                'handle': {
                    'moneylineHome': 45,
                    'spreadHome': 30,
                    'totalOver': 70
                },
                'tickets': {
                    'moneylineHome': 75,
                    'spreadHome': 82,
                    'totalOver': 65
                },
                'sharpAction': {
                    'moneyline': 'away',
                    'spread': 'away',
                    'total': 'over',
                    'confidence': 85
                }
            }
        ],
        'summary': {
            'fadePublicOpportunities': 2,
            'sharpConsensus': 1,
            'reverseLlineMovements': 1
        }
    }
    
    return jsonify({
        'publicBetting': mock_public_data,
        'timestamp': datetime.utcnow().isoformat(),
        'sport': sport
    })

@enhanced_api_bp.route('/sharp-money', methods=['GET'])
def get_sharp_money():
    """Get sharp money movements and steam moves"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    
    mock_sharp_data = {
        'games': [
            {
                'gameId': 'game_1',
                'homeTeam': 'Kansas City Chiefs',
                'awayTeam': 'Buffalo Bills',
                'sharpAction': {
                    'moneyline': {'side': 'away', 'confidence': 78},
                    'spread': {'side': 'away', 'confidence': 82},
                    'total': {'side': 'under', 'confidence': 65}
                },
                'steamMoves': [
                    {
                        'time': '2 hours ago',
                        'market': 'spread',
                        'direction': 'away',
                        'magnitude': 1.5
                    },
                    {
                        'time': '45 min ago',
                        'market': 'total',
                        'direction': 'under',
                        'magnitude': 1.0
                    }
                ],
                'lineMovement': {
                    'spread': {'opening': -3, 'current': -3.5, 'direction': 'home'},
                    'total': {'opening': 48, 'current': 47.5, 'direction': 'under'}
                }
            }
        ],
        'summary': {
            'totalSteamMoves': 3,
            'reverseLineMovements': 2,
            'sharpConfidenceAvg': 75
        }
    }
    
    return jsonify({
        'sharpMoney': mock_sharp_data,
        'timestamp': datetime.utcnow().isoformat(),
        'sport': sport
    })

@enhanced_api_bp.route('/market-alerts', methods=['GET'])
def get_market_alerts():
    """Get real-time market alerts and opportunities"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    
    alerts = [
        {
            'type': 'fade_public',
            'severity': 'high',
            'game': 'Buffalo Bills @ Kansas City Chiefs',
            'message': 'Public heavily on Chiefs (72%) - Sharp money on Bills',
            'action': 'Consider fading public - take Bills +3.5',
            'confidence': 85
        },
        {
            'type': 'steam_move',
            'severity': 'high',
            'game': 'LA Lakers @ Boston Celtics',
            'message': 'Steam move detected on Lakers +5.5',
            'action': 'Follow steam - bet Lakers +5.5',
            'confidence': 78
        },
        {
            'type': 'reverse_line_movement',
            'severity': 'medium',
            'game': 'Cowboys @ Eagles',
            'message': 'Line moving toward Cowboys despite 68% public on Eagles',
            'action': 'Sharp money indicator - consider Cowboys',
            'confidence': 72
        }
    ]
    
    return jsonify({
        'alerts': alerts,
        'count': len(alerts),
        'timestamp': datetime.utcnow().isoformat()
    })

@enhanced_api_bp.route('/vegas-consensus', methods=['GET'])
def get_vegas_consensus():
    """Get Vegas consensus lines and closing line value"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    
    vegas_data = {
        'consensusLines': {
            'spreadConsensus': -3.5,
            'totalConsensus': 47.5,
            'mlConsensus': -140
        },
        'lineOriginator': 'Circa Sports',
        'marketMakerMoves': {
            'pinnacleMove': True,
            'circaMove': True,
            'moveDirection': 'away'
        },
        'sharpBookConsensus': {
            'pinnacle': -3.5,
            'bookmaker': -3.0,
            'betcris': -4.0
        },
        'closingLineValue': {
            'clvAvailable': True,
            'estimatedClv': 1.2
        }
    }
    
    return jsonify({
        'vegasConsensus': vegas_data,
        'timestamp': datetime.utcnow().isoformat(),
        'sport': sport
    })

@enhanced_api_bp.route('/enhanced-predictions', methods=['GET'])
def get_enhanced_predictions():
    """Get predictions with enhanced features including public betting data"""
    sport = request.args.get('sport', 'americanfootball_nfl')
    min_confidence = float(request.args.get('min_confidence', Config.MIN_CONFIDENCE_THRESHOLD))
    
    enhanced_predictions = [
        {
            'game': {
                'homeTeam': 'Kansas City Chiefs',
                'awayTeam': 'Buffalo Bills',
                'startTime': (datetime.utcnow() + timedelta(days=1)).isoformat(),
                'sport': sport
            },
            'prediction': {
                'betType': 'moneyline',
                'predictedOutcome': 'away',
                'probability': 0.72,
                'confidenceScore': 0.85,
                'recommendedStake': 45.50,
                'expectedValue': 12.30
            },
            'features': {
                'publicBetting': 0.72,
                'sharpLean': 0.28,
                'consensusStrength': 0.72,
                'contrarianOpportunity': 1.0,
                'vegasConsensus': 0.58
            },
            'marketIntelligence': {
                'publicSide': 'home',
                'sharpSide': 'away',
                'fadePublic': True,
                'steamDetected': True,
                'reasoning': 'High public percentage on Chiefs (72%) with sharp money flowing to Bills. Steam move detected on Bills +3.5. Classic fade-the-public spot.'
            }
        },
        {
            'game': {
                'homeTeam': 'Boston Celtics',
                'awayTeam': 'LA Lakers',
                'startTime': (datetime.utcnow() + timedelta(days=2)).isoformat(),
                'sport': sport
            },
            'prediction': {
                'betType': 'spread',
                'predictedOutcome': 'away +5.5',
                'probability': 0.68,
                'confidenceScore': 0.78,
                'recommendedStake': 35.20,
                'expectedValue': 8.90
            },
            'features': {
                'publicBetting': 0.75,
                'sharpLean': 0.25,
                'consensusStrength': 0.75,
                'contrarianOpportunity': 1.0,
                'vegasConsensus': 0.45
            },
            'marketIntelligence': {
                'publicSide': 'home',
                'sharpSide': 'away',
                'fadePublic': True,
                'steamDetected': False,
                'reasoning': 'Public heavy on Celtics (75%) but sharp money on Lakers. Historical edge in this spot.'
            }
        }
    ]
    
    return jsonify({
        'enhancedPredictions': enhanced_predictions,
        'count': len(enhanced_predictions),
        'featureGroups': {
            'publicBetting': ['public_ml_home_pct', 'public_consensus_strength'],
            'sharpMoney': ['sharp_ml_lean_home', 'steam_move_detected'],
            'vegasLines': ['vegas_ml_consensus', 'clv_available'],
            'marketIntelligence': ['contrarian_opportunity', 'fade_public']
        }
    })

@enhanced_api_bp.route('/sportsradar/teams', methods=['GET'])
def get_sportsradar_teams():
    """Get real team data from SportRadar"""
    sport = request.args.get('sport', 'nfl')
    
    try:
        teams = sportsradar_client.get_team_list(sport)
        return jsonify({
            'teams': teams,
            'count': len(teams),
            'sport': sport,
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/games', methods=['GET'])
def get_sportsradar_games():
    """Get real games data from SportRadar"""
    sport = request.args.get('sport', 'nfl')
    days_ahead = int(request.args.get('days', 7))
    
    try:
        games = []
        
        if sport == 'nfl':
            games = sportsradar_client.get_nfl_games()
        elif sport == 'nba':
            games = sportsradar_client.get_nba_games()
        elif sport == 'ncaamb':
            games = sportsradar_client.get_ncaamb_games()
        elif sport == 'nhl':
            games = sportsradar_client.get_nhl_games()
        elif sport == 'mlb':
            games = sportsradar_client.get_mlb_games()
        elif sport == 'ncaafb':
            games = sportsradar_client.get_ncaafb_games()
        elif sport == 'tennis':
            tournaments = sportsradar_client.get_tennis_tournaments()
            # For tennis, return tournaments as "games"
            games = tournaments
        elif sport == 'mma':
            events = sportsradar_client.get_mma_events()
            # For MMA, return events as "games"
            games = events
        elif sport == 'nascar':
            races = sportsradar_client.get_nascar_races()
            # For NASCAR, return races as "games"
            games = races
        elif sport == 'golf':
            tournaments = sportsradar_client.get_golf_tournaments()
            # For golf, return tournaments as "games"
            games = tournaments
        
        return jsonify({
            'games': games,
            'count': len(games),
            'sport': sport,
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/standings', methods=['GET'])
def get_sportsradar_standings():
    """Get real standings from SportRadar"""
    sport = request.args.get('sport', 'nfl')
    season = request.args.get('season', '2024')
    
    try:
        if sport == 'nfl':
            standings = sportsradar_client.get_nfl_standings(season)
        elif sport == 'nba':
            standings = sportsradar_client.get_nba_standings(season)
        else:
            standings = []
        
        return jsonify({
            'standings': standings,
            'count': len(standings),
            'sport': sport,
            'season': season,
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/team-stats/<team_id>', methods=['GET'])
def get_sportsradar_team_stats(team_id):
    """Get comprehensive team statistics from SportRadar"""
    sport = request.args.get('sport', 'nfl')
    season = request.args.get('season', '2024')
    
    try:
        team_data = sportsradar_client.get_comprehensive_team_data(sport, team_id, season)
        return jsonify({
            'teamData': team_data,
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/live-game/<game_id>', methods=['GET'])
def get_sportsradar_live_game(game_id):
    """Get live game data from SportRadar"""
    sport = request.args.get('sport', 'nfl')
    
    try:
        live_data = sportsradar_client.get_live_game_summary(sport, game_id)
        return jsonify({
            'liveData': live_data,
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

# Specialized endpoints for unique sports
@enhanced_api_bp.route('/sportsradar/tennis/tournaments', methods=['GET'])
def get_tennis_tournaments():
    """Get tennis tournaments from SportRadar"""
    try:
        tournaments = sportsradar_client.get_tennis_tournaments()
        return jsonify({
            'tournaments': tournaments,
            'count': len(tournaments),
            'sport': 'tennis',
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/tennis/matches/<tournament_id>', methods=['GET'])
def get_tennis_matches(tournament_id):
    """Get tennis matches for a tournament"""
    try:
        matches = sportsradar_client.get_tennis_matches(tournament_id)
        return jsonify({
            'matches': matches,
            'tournament_id': tournament_id,
            'count': len(matches),
            'sport': 'tennis',
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/mma/events', methods=['GET'])
def get_mma_events():
    """Get MMA events from SportRadar"""
    try:
        events = sportsradar_client.get_mma_events()
        return jsonify({
            'events': events,
            'count': len(events),
            'sport': 'mma',
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/mma/fights/<event_id>', methods=['GET'])
def get_mma_fights(event_id):
    """Get MMA fights for an event"""
    try:
        fights = sportsradar_client.get_mma_fights(event_id)
        return jsonify({
            'fights': fights,
            'event_id': event_id,
            'count': len(fights),
            'sport': 'mma',
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/nascar/races', methods=['GET'])
def get_nascar_races():
    """Get NASCAR races from SportRadar"""
    season = request.args.get('season', '2024')
    try:
        races = sportsradar_client.get_nascar_races(season)
        return jsonify({
            'races': races,
            'season': season,
            'count': len(races),
            'sport': 'nascar',
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/golf/tournaments', methods=['GET'])
def get_golf_tournaments():
    """Get golf tournaments from SportRadar"""
    try:
        tournaments = sportsradar_client.get_golf_tournaments()
        return jsonify({
            'tournaments': tournaments,
            'count': len(tournaments),
            'sport': 'golf',
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500

@enhanced_api_bp.route('/sportsradar/golf/leaderboard/<tournament_id>', methods=['GET'])
def get_golf_leaderboard(tournament_id):
    """Get golf tournament leaderboard"""
    try:
        leaderboard = sportsradar_client.get_golf_leaderboard(tournament_id)
        return jsonify({
            'leaderboard': leaderboard,
            'tournament_id': tournament_id,
            'count': len(leaderboard),
            'sport': 'golf',
            'source': 'SportRadar',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'source': 'SportRadar'}), 500
