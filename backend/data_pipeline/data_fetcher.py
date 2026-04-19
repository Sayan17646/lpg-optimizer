"""
Real-time data pipeline for LPG optimization
Fetches data from APIs, web scrapers, and databases
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    async def fetch(self) -> Dict:
        """Fetch data from source"""
        pass


class APIDataSource(DataSource):
    """Fetch data from REST API"""
    
    def __init__(self, url: str, headers: Optional[Dict] = None):
        self.url = url
        self.headers = headers or {}
    
    async def fetch(self) -> Dict:
        """Fetch from API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, headers=self.headers, timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"API Error: {resp.status}")
                        return {}
        except Exception as e:
            logger.error(f"API fetch failed: {e}")
            return {}


class GovernmentDataSource(DataSource):
    """Fetch from government petroleum ministry data"""
    
    def __init__(self):
        # Reference: pib.gov.in, petroleum.nic.in, iocl.com, hpcl.com, reliance.com
        self.sources = [
            "https://petroleum.nic.in/api/lpg-production",
            "https://iocl.com/api/inventory",
            "https://hpcl.com/api/supply"
        ]
    
    async def fetch(self) -> Dict:
        """Fetch government LPG data"""
        data = {}
        for source in self.sources:
            try:
                ds = APIDataSource(source)
                result = await ds.fetch()
                data.update(result)
            except Exception as e:
                logger.warning(f"Government source fetch failed: {e}")
        return data


class RealTimeDataPipeline:
    """
    Orchestrates real-time data collection for LPG system
    """
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        self.last_update = {}
        self.cache = {}
    
    def add_source(self, name: str, source: DataSource):
        """Register a data source"""
        self.sources[name] = source
    
    async def fetch_all(self) -> Dict:
        """Fetch from all sources concurrently"""
        tasks = []
        source_names = []
        
        for name, source in self.sources.items():
            tasks.append(source.fetch())
            source_names.append(name)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for name, result in zip(source_names, results):
            if isinstance(result, Exception):
                logger.error(f"Error from {name}: {result}")
                data[name] = {}
            else:
                data[name] = result
                self.last_update[name] = datetime.now()
        
        return data
    
    async def fetch_demand_forecast(self) -> Dict[str, List[float]]:
        """
        Fetch LPG demand forecast by location
        Returns: {location_id: [hourly_demand_mt]}
        """
        # Mock implementation - in production, connect to IEA, industry reports
        forecast = {
            'city_delhi': [450 + i*10 for i in range(24)],
            'city_mumbai': [380 + i*8 for i in range(24)],
            'city_bangalore': [280 + i*7 for i in range(24)],
            'city_kolkata': [240 + i*6 for i in range(24)],
            'city_hyderabad': [260 + i*5 for i in range(24)],
        }
        return forecast
    
    async def fetch_supply_status(self) -> Dict[str, float]:
        """
        Fetch current LPG supply at plants
        Returns: {plant_id: available_mt}
        """
        # Mock - connects to ERP systems of IOC, HPCL, Reliance
        supply = {
            'reliance_jamnagar': 1850.0,
            'ioc_kochi': 720.0,
            'hpcl_mumbai': 580.0,
            'bharat_import': 450.0,
        }
        return supply
    
    async def fetch_transportation_costs(self) -> Dict[str, float]:
        """
        Fetch current transportation costs by route
        Returns: {route_id: cost_per_mt_inr}
        """
        # Mock - can integrate with logistics APIs
        costs = {
            'jamnagar_delhi': 850,
            'jamnagar_mumbai': 650,
            'kochi_bangalore': 920,
            'mumbai_pune': 320,
            'delhi_jaipur': 450,
        }
        return costs
    
    async def fetch_weather_data(self) -> Dict:
        """
        Fetch weather data affecting transportation
        Can impact demand and delivery times
        """
        # Integration with weather APIs (OpenWeatherMap, weatherapi.com)
        weather = {
            'timestamp': datetime.now().isoformat(),
            'regions': {
                'north': {'temp': 35, 'condition': 'clear', 'impact': 'normal'},
                'west': {'temp': 32, 'condition': 'cloudy', 'impact': 'normal'},
                'south': {'temp': 28, 'condition': 'rainy', 'impact': 'delayed'},
                'east': {'temp': 30, 'condition': 'clear', 'impact': 'normal'},
            }
        }
        return weather
    
    async def fetch_market_prices(self) -> Dict:
        """
        Fetch current LPG market prices
        Used for cost optimization
        """
        prices = {
            'wholesale_price_inr_per_kg': 48.5,
            'retail_price_inr_per_kg': 91.5,
            'timestamp': datetime.now().isoformat(),
            'source': 'petroleum.nic.in'
        }
        return prices
    
    async def stream_real_time_data(self, interval_seconds: int = 300):
        """
        Continuously stream data at specified interval
        Default: every 5 minutes
        """
        while True:
            try:
                logger.info("Fetching real-time data...")
                
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'demand_forecast': await self.fetch_demand_forecast(),
                    'supply_status': await self.fetch_supply_status(),
                    'transportation_costs': await self.fetch_transportation_costs(),
                    'weather': await self.fetch_weather_data(),
                    'prices': await self.fetch_market_prices(),
                }
                
                self.cache = data
                logger.info(f"Data fetched at {data['timestamp']}")
                
                yield data
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Data pipeline error: {e}")
                await asyncio.sleep(interval_seconds)


class DemandGenerator:
    """Generate synthetic demand for testing"""
    
    @staticmethod
    def generate_hourly_demand(base_demand: float, hour: int) -> float:
        """
        Generate hourly demand with realistic patterns
        Peak hours: 6-9 AM, 18-21 PM
        """
        peak_multipliers = {
            6: 1.4, 7: 1.5, 8: 1.6, 9: 1.5,
            18: 1.3, 19: 1.4, 20: 1.3, 21: 1.2
        }
        
        multiplier = peak_multipliers.get(hour, 1.0)
        noise = 0.95 + (hour % 3) * 0.03
        
        return base_demand * multiplier * noise
    
    @staticmethod
    def generate_forecast(location_id: str, base_demand: float, days: int) -> List[float]:
        """Generate multi-day demand forecast"""
        forecast = []
        
        for day in range(days):
            for hour in range(24):
                hourly_demand = DemandGenerator.generate_hourly_demand(base_demand, hour)
                # Add day-to-day variation (weekday vs weekend)
                day_multiplier = 1.1 if day % 7 in [5, 6] else 1.0
                forecast.append(hourly_demand * day_multiplier)
        
        return forecast
