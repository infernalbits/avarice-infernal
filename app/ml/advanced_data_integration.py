import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import os
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    url: str
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    last_request: float = 0
    enabled: bool = True

class BaseDataProvider(ABC):
    """Abstract base class for data providers"""
    
    @abstractmethod
    async def fetch_data(self, **kwargs) -> Dict:
        """Fetch data from the source"""
        pass
    
    @abstractmethod
    def parse_data(self, raw_data: Dict) -> pd.DataFrame:
        """Parse raw data into structured format"""
        pass

class WeatherDataProvider(BaseDataProvider):
    """Weather data integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    async def fetch_data(self, city: str, date: datetime) -> Dict:
        """Fetch weather data for a specific city and date"""
        try:
            # Get coordinates for city
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': city,
                'limit': 1,
                'appid': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(geo_url, params=params) as response:
                    geo_data = await response.json()
                    
                    if not geo_data:
                        return {}
                    
                    lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
                    
                    # Get weather data
                    weather_url = f"{self.base_url}/forecast"
                    weather_params = {
                        'lat': lat,
                        'lon': lon,
                        'appid': self.api_key,
                        'units': 'imperial'
                    }
                    
                    async with session.get(weather_url, params=weather_params) as response:
                        weather_data = await response.json()
                        return weather_data
                        
        except Exception as e:
            logging.error(f"Error fetching weather data: {str(e)}")
            return {}
    
    def parse_data(self, raw_data: Dict) -> pd.DataFrame:
        """Parse weather data into structured format"""
        if not raw_data or 'list' not in raw_data:
            return pd.DataFrame()
        
        weather_records = []
        for item in raw_data['list']:
            weather_records.append({
                'datetime': item['dt_txt'],
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed'],
                'weather_condition': item['weather'][0]['main'].lower(),
                'weather_description': item['weather'][0]['description'],
                'pressure': item['main']['pressure'],
                'visibility': item.get('visibility', 10000) / 1000  # Convert to km
            })
        
        df = pd.DataFrame(weather_records)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df

class InjuryDataProvider(BaseDataProvider):
    """Injury data integration from multiple sources"""
    
    def __init__(self):
        self.sources = {
            'espn': 'https://www.espn.com/nfl/injuries',
            'rotowire': 'https://www.rotowire.com/football/nfl-lineups.php',
            'sportsline': 'https://www.sportsline.com/nfl/injuries/'
        }
    
    async def fetch_data(self, sport: str = 'nfl') -> Dict:
        """Fetch injury data from multiple sources"""
        injury_data = {}
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source_name, url in self.sources.items():
                if sport in url:
                    task = self._fetch_source_data(session, source_name, url)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    injury_data.update(result)
        
        return injury_data
    
    async def _fetch_source_data(self, session: aiohttp.ClientSession, source: str, url: str) -> Dict:
        """Fetch data from a specific source"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    return {source: html}
                else:
                    return {}
        except Exception as e:
            logging.error(f"Error fetching from {source}: {str(e)}")
            return {}
    
    def parse_data(self, raw_data: Dict) -> pd.DataFrame:
        """Parse injury data from multiple sources"""
        injury_records = []
        
        for source, html_content in raw_data.items():
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                if source == 'espn':
                    injuries = self._parse_espn_injuries(soup)
                elif source == 'rotowire':
                    injuries = self._parse_rotowire_injuries(soup)
                else:
                    injuries = []
                
                injury_records.extend(injuries)
                
            except Exception as e:
                logging.error(f"Error parsing {source} data: {str(e)}")
        
        df = pd.DataFrame(injury_records)
        if not df.empty:
            df['date_updated'] = datetime.now()
            df['source'] = source
        
        return df
    
    def _parse_espn_injuries(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse ESPN injury data"""
        injuries = []
        # ESPN specific parsing logic
        # This is a simplified version - real implementation would be more complex
        return injuries
    
    def _parse_rotowire_injuries(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse Rotowire injury data"""
        injuries = []
        # Rotowire specific parsing logic
        return injuries

class SocialMediaDataProvider(BaseDataProvider):
    """Social media sentiment analysis integration"""
    
    def __init__(self, twitter_api_key: Optional[str] = None):
        self.twitter_api_key = twitter_api_key
        self.reddit_url = "https://www.reddit.com/r/nfl/search.json"
    
    async def fetch_data(self, team: str, keywords: List[str] = None) -> Dict:
        """Fetch social media data for a team"""
        social_data = {}
        
        # Fetch Reddit data
        reddit_data = await self._fetch_reddit_data(team, keywords)
        social_data['reddit'] = reddit_data
        
        # Fetch Twitter data if API key available
        if self.twitter_api_key:
            twitter_data = await self._fetch_twitter_data(team, keywords)
            social_data['twitter'] = twitter_data
        
        return social_data
    
    async def _fetch_reddit_data(self, team: str, keywords: List[str]) -> Dict:
        """Fetch Reddit posts and comments"""
        try:
            search_query = f"{team} {' '.join(keywords or [])}"
            params = {
                'q': search_query,
                'restrict_sr': 'on',
                'sort': 'hot',
                't': 'day',
                'limit': 25
            }
            
            headers = {
                'User-Agent': 'SportsBettingAI/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.reddit_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return {}
        except Exception as e:
            logging.error(f"Error fetching Reddit data: {str(e)}")
            return {}
    
    async def _fetch_twitter_data(self, team: str, keywords: List[str]) -> Dict:
        """Fetch Twitter data (placeholder for API integration)"""
        # This would require Twitter API v2 integration
        return {}
    
    def parse_data(self, raw_data: Dict) -> pd.DataFrame:
        """Parse social media data and calculate sentiment"""
        social_records = []
        
        for platform, data in raw_data.items():
            if platform == 'reddit' and 'data' in data:
                for post in data['data'].get('children', []):
                    post_data = post['data']
                    social_records.append({
                        'platform': 'reddit',
                        'title': post_data.get('title', ''),
                        'content': post_data.get('selftext', ''),
                        'score': post_data.get('score', 0),
                        'comments': post_data.get('num_comments', 0),
                        'created_utc': post_data.get('created_utc', 0),
                        'sentiment_score': self._calculate_sentiment(post_data.get('title', '') + ' ' + post_data.get('selftext', ''))
                    })
        
        df = pd.DataFrame(social_records)
        if not df.empty:
            df['datetime'] = pd.to_datetime(df['created_utc'], unit='s')
        
        return df
    
    def _calculate_sentiment(self, text: str) -> float:
        """Simple sentiment analysis (placeholder for more sophisticated analysis)"""
        positive_words = ['win', 'victory', 'great', 'amazing', 'excellent', 'good', 'strong']
        negative_words = ['lose', 'defeat', 'terrible', 'awful', 'bad', 'weak', 'injury']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count == 0 and negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)

class MarketDataProvider(BaseDataProvider):
    """Market data integration for odds and betting trends"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.bookmakers = {
            'fanduel': 'https://api.fanduel.com/v1/odds',
            'draftkings': 'https://api.draftkings.com/v1/odds',
            'bet365': 'https://api.bet365.com/v1/odds'
        }
    
    async def fetch_data(self, sport: str, event_ids: List[str] = None) -> Dict:
        """Fetch odds data from multiple bookmakers"""
        market_data = {}
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for bookmaker, base_url in self.bookmakers.items():
                if bookmaker in self.api_keys:
                    task = self._fetch_bookmaker_odds(session, bookmaker, base_url, sport, event_ids)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    market_data.update(result)
        
        return market_data
    
    async def _fetch_bookmaker_odds(self, session: aiohttp.ClientSession, bookmaker: str, 
                                  base_url: str, sport: str, event_ids: List[str]) -> Dict:
        """Fetch odds from a specific bookmaker"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_keys[bookmaker]}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'sport': sport,
                'region': 'us'
            }
            
            if event_ids:
                params['event_ids'] = ','.join(event_ids)
            
            async with session.get(base_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {bookmaker: data}
                else:
                    return {}
        except Exception as e:
            logging.error(f"Error fetching {bookmaker} odds: {str(e)}")
            return {}
    
    def parse_data(self, raw_data: Dict) -> pd.DataFrame:
        """Parse market data into structured format"""
        market_records = []
        
        for bookmaker, data in raw_data.items():
            if 'events' in data:
                for event in data['events']:
                    for market in event.get('markets', []):
                        if market['key'] == 'h2h':  # Head-to-head market
                            for outcome in market.get('outcomes', []):
                                market_records.append({
                                    'event_id': event['id'],
                                    'bookmaker': bookmaker,
                                    'team': outcome['name'],
                                    'odds': outcome['price'],
                                    'market_type': 'moneyline',
                                    'timestamp': datetime.now(),
                                    'sport': event.get('sport', ''),
                                    'home_team': event.get('home_team', ''),
                                    'away_team': event.get('away_team', '')
                                })
        
        df = pd.DataFrame(market_records)
        return df

class AdvancedDataIntegration:
    """Main data integration orchestrator"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.providers = {}
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all data providers"""
        if 'weather_api_key' in self.config:
            self.providers['weather'] = WeatherDataProvider(self.config['weather_api_key'])
        
        self.providers['injury'] = InjuryDataProvider()
        self.providers['social'] = SocialMediaDataProvider(
            self.config.get('twitter_api_key')
        )
        
        if 'market_api_keys' in self.config:
            self.providers['market'] = MarketDataProvider(self.config['market_api_keys'])
    
    async def fetch_comprehensive_data(self, teams: List[str], sport: str = 'nfl') -> Dict:
        """Fetch data from all available sources"""
        comprehensive_data = {}
        
        # Fetch data from all providers concurrently
        tasks = []
        
        # Weather data for team cities
        if 'weather' in self.providers:
            for team in teams:
                city = self._get_team_city(team)
                if city:
                    task = self.providers['weather'].fetch_data(city, datetime.now())
                    tasks.append(('weather', team, task))
        
        # Injury data
        if 'injury' in self.providers:
            task = self.providers['injury'].fetch_data(sport)
            tasks.append(('injury', sport, task))
        
        # Social media data
        if 'social' in self.providers:
            for team in teams:
                task = self.providers['social'].fetch_data(team, [sport, 'betting', 'odds'])
                tasks.append(('social', team, task))
        
        # Market data
        if 'market' in self.providers:
            task = self.providers['market'].fetch_data(sport)
            tasks.append(('market', sport, task))
        
        # Execute all tasks concurrently
        for data_type, identifier, task in tasks:
            try:
                result = await task
                comprehensive_data[f"{data_type}_{identifier}"] = result
            except Exception as e:
                logging.error(f"Error fetching {data_type} data for {identifier}: {str(e)}")
        
        return comprehensive_data
    
    def _get_team_city(self, team: str) -> Optional[str]:
        """Get city for a team (simplified mapping)"""
        team_cities = {
            'chiefs': 'Kansas City',
            'bills': 'Buffalo',
            'patriots': 'Boston',
            'jets': 'New York',
            'dolphins': 'Miami',
            'ravens': 'Baltimore',
            'bengals': 'Cincinnati',
            'browns': 'Cleveland',
            'steelers': 'Pittsburgh',
            'texans': 'Houston',
            'colts': 'Indianapolis',
            'jaguars': 'Jacksonville',
            'titans': 'Nashville',
            'broncos': 'Denver',
            'raiders': 'Las Vegas',
            'chargers': 'Los Angeles',
            'cowboys': 'Dallas',
            'eagles': 'Philadelphia',
            'giants': 'New York',
            'commanders': 'Washington',
            'bears': 'Chicago',
            'lions': 'Detroit',
            'packers': 'Green Bay',
            'vikings': 'Minneapolis',
            'falcons': 'Atlanta',
            'panthers': 'Charlotte',
            'saints': 'New Orleans',
            'buccaneers': 'Tampa Bay',
            'cardinals': 'Phoenix',
            'rams': 'Los Angeles',
            'seahawks': 'Seattle',
            '49ers': 'San Francisco'
        }
        
        return team_cities.get(team.lower())
    
    def process_and_enhance_data(self, raw_data: Dict) -> pd.DataFrame:
        """Process and enhance raw data with derived features"""
        enhanced_data = []
        
        # Process weather data
        for key, data in raw_data.items():
            if key.startswith('weather_'):
                weather_df = self.providers['weather'].parse_data(data)
                if not weather_df.empty:
                    enhanced_data.append(weather_df)
        
        # Process injury data
        for key, data in raw_data.items():
            if key.startswith('injury_'):
                injury_df = self.providers['injury'].parse_data(data)
                if not injury_df.empty:
                    enhanced_data.append(injury_df)
        
        # Process social media data
        for key, data in raw_data.items():
            if key.startswith('social_'):
                social_df = self.providers['social'].parse_data(data)
                if not social_df.empty:
                    enhanced_data.append(social_df)
        
        # Process market data
        for key, data in raw_data.items():
            if key.startswith('market_'):
                market_df = self.providers['market'].parse_data(data)
                if not market_df.empty:
                    enhanced_data.append(market_df)
        
        # Combine all data
        if enhanced_data:
            combined_df = pd.concat(enhanced_data, ignore_index=True)
            
            # Add derived features
            combined_df = self._add_derived_features(combined_df)
            
            return combined_df
        else:
            return pd.DataFrame()
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features to the dataset"""
        df_enhanced = df.copy()
        
        # Weather impact features
        if 'weather_condition' in df.columns:
            weather_impact = {
                'clear': 0, 'clouds': -0.05, 'rain': -0.15, 'snow': -0.25, 'thunderstorm': -0.3
            }
            df_enhanced['weather_impact_score'] = df['weather_condition'].map(weather_impact).fillna(0)
        
        # Social sentiment features
        if 'sentiment_score' in df.columns:
            df_enhanced['positive_sentiment'] = (df['sentiment_score'] > 0.1).astype(int)
            df_enhanced['negative_sentiment'] = (df['sentiment_score'] < -0.1).astype(int)
        
        # Market efficiency features
        if 'odds' in df.columns:
            df_enhanced['implied_probability'] = 1 / (df['odds'] + 1)
        
        # Time-based features
        if 'datetime' in df.columns:
            df_enhanced['hour_of_day'] = pd.to_datetime(df['datetime']).dt.hour
            df_enhanced['day_of_week'] = pd.to_datetime(df['datetime']).dt.dayofweek
            df_enhanced['is_weekend'] = (df_enhanced['day_of_week'] >= 5).astype(int)
        
        return df_enhanced
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary statistics for the integrated data"""
        summary = {
            'total_records': len(df),
            'data_sources': df['platform'].unique().tolist() if 'platform' in df.columns else [],
            'date_range': {
                'start': df['datetime'].min().isoformat() if 'datetime' in df.columns else None,
                'end': df['datetime'].max().isoformat() if 'datetime' in df.columns else None
            }
        }
        
        # Weather summary
        if 'weather_condition' in df.columns:
            summary['weather_conditions'] = df['weather_condition'].value_counts().to_dict()
        
        # Sentiment summary
        if 'sentiment_score' in df.columns:
            summary['sentiment_stats'] = {
                'mean': df['sentiment_score'].mean(),
                'std': df['sentiment_score'].std(),
                'positive_posts': (df['sentiment_score'] > 0).sum(),
                'negative_posts': (df['sentiment_score'] < 0).sum()
            }
        
        return summary
