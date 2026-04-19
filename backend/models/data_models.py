"""
Data models for LPG optimization system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class SupplySourceType(Enum):
    """Type of supply source"""
    REFINERY = "refinery"
    IMPORT_TERMINAL = "import_terminal"
    STORAGE_FACILITY = "storage_facility"


class LocationRole(Enum):
    """Role of location in network"""
    SUPPLIER = "supplier"
    DISTRIBUTION_HUB = "hub"
    RETAIL_POINT = "retail"
    STORAGE = "storage"


@dataclass
class Location:
    """Represents a location in the network"""
    location_id: str
    name: str
    role: LocationRole
    latitude: float
    longitude: float
    capacity: float  # Storage capacity in MT
    current_inventory: float  # Current inventory in MT
    
    def to_dict(self) -> Dict:
        return {
            'location_id': self.location_id,
            'name': self.name,
            'role': self.role.value,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'capacity': self.capacity,
            'current_inventory': self.current_inventory
        }


@dataclass
class Demand:
    """Represents demand at a location"""
    location_id: str
    date: datetime
    quantity: float  # Demand in MT
    priority: int = 1  # 1=critical, 2=high, 3=normal, 4=low
    forecast_confidence: float = 0.8
    
    def to_dict(self) -> Dict:
        return {
            'location_id': self.location_id,
            'date': self.date.isoformat(),
            'quantity': self.quantity,
            'priority': self.priority,
            'forecast_confidence': self.forecast_confidence
        }


@dataclass
class Supply:
    """Represents supply from a source"""
    source_id: str
    location_id: str
    date: datetime
    quantity: float  # Available supply in MT
    cost_per_unit: float  # INR per MT
    source_type: SupplySourceType
    
    def to_dict(self) -> Dict:
        return {
            'source_id': self.source_id,
            'location_id': self.location_id,
            'date': self.date.isoformat(),
            'quantity': self.quantity,
            'cost_per_unit': self.cost_per_unit,
            'source_type': self.source_type.value
        }


@dataclass
class Route:
    """Represents a route between two locations"""
    from_location: str
    to_location: str
    distance_km: float
    travel_time_hours: float
    transport_cost_per_mt: float  # INR per MT
    capacity_mt: float  # Maximum load capacity
    vehicle_type: str = "tanker"  # tanker, truck, etc.
    
    def to_dict(self) -> Dict:
        return {
            'from': self.from_location,
            'to': self.to_location,
            'distance_km': self.distance_km,
            'travel_time_hours': self.travel_time_hours,
            'cost_per_mt': self.transport_cost_per_mt,
            'capacity_mt': self.capacity_mt,
            'vehicle_type': self.vehicle_type
        }


@dataclass
class TransportAllocation:
    """Result of optimization - allocation of shipments"""
    from_location: str
    to_location: str
    quantity_mt: float
    cost_inr: float
    route: Route
    scheduled_date: datetime
    vehicle_id: Optional[str] = None
    status: str = "planned"  # planned, in_transit, delivered
    
    def to_dict(self) -> Dict:
        return {
            'from': self.from_location,
            'to': self.to_location,
            'quantity_mt': self.quantity_mt,
            'cost_inr': self.cost_inr,
            'scheduled_date': self.scheduled_date.isoformat(),
            'vehicle_id': self.vehicle_id,
            'status': self.status
        }


@dataclass
class OptimizationResult:
    """Complete optimization solution"""
    timestamp: datetime
    total_cost_inr: float
    total_quantity_transported_mt: float
    allocations: List[TransportAllocation] = field(default_factory=list)
    inventory_plan: Dict = field(default_factory=dict)
    unmet_demand_mt: float = 0.0
    service_level: float = 0.95  # 95% = 5% unmet demand acceptable
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_cost_inr': self.total_cost_inr,
            'total_quantity_mt': self.total_quantity_transported_mt,
            'allocations': [a.to_dict() for a in self.allocations],
            'inventory_plan': self.inventory_plan,
            'unmet_demand_mt': self.unmet_demand_mt,
            'service_level': self.service_level,
            'execution_time_ms': self.execution_time_ms
        }


@dataclass
class NetworkNode:
    """Node in the LPG distribution network"""
    node_id: str
    location: Location
    node_type: str  # source, hub, demand_point
    priority: int = 1


@dataclass
class NetworkEdge:
    """Edge in the LPG distribution network"""
    edge_id: str
    from_node: str
    to_node: str
    route: Route
    is_active: bool = True


@dataclass
class OptimizationConfig:
    """Configuration for optimization"""
    optimization_interval_hours: int = 6
    time_horizon_days: int = 7
    service_level_target: float = 0.95
    use_vam: bool = True
    use_dp: bool = True
    use_network_flow: bool = True
    max_vehicles: int = 100
    vehicle_capacity_mt: float = 20.0
    holding_cost_per_mt_per_day: float = 50.0  # INR
    stockout_penalty_per_mt: float = 5000.0  # INR (severe penalty)
    
    def to_dict(self) -> Dict:
        return {
            'optimization_interval_hours': self.optimization_interval_hours,
            'time_horizon_days': self.time_horizon_days,
            'service_level_target': self.service_level_target,
            'use_vam': self.use_vam,
            'use_dp': self.use_dp,
            'use_network_flow': self.use_network_flow,
            'max_vehicles': self.max_vehicles,
            'vehicle_capacity_mt': self.vehicle_capacity_mt,
            'holding_cost_per_mt_per_day': self.holding_cost_per_mt_per_day,
            'stockout_penalty_per_mt': self.stockout_penalty_per_mt
        }


# India-scale LPG network initialization data
INDIA_LPG_NETWORK = {
    'plants': {
        'reliance_jamnagar': {
            'name': 'Reliance Jamnagar Refinery',
            'location': (22.3039, 70.0577),
            'capacity': 2000.0,  # MT/day
            'type': SupplySourceType.REFINERY
        },
        'ioc_kochi': {
            'name': 'IOC Kochi Refinery',
            'location': (9.9689, 76.2540),
            'capacity': 800.0,
            'type': SupplySourceType.REFINERY
        },
        'hpcl_mumbai': {
            'name': 'HPCL Mumbai Refinery',
            'location': (19.0176, 72.8479),
            'capacity': 600.0,
            'type': SupplySourceType.REFINERY
        },
        'bharat_import': {
            'name': 'Bharat LPG Import Terminal',
            'location': (17.6869, 83.2185),
            'capacity': 500.0,
            'type': SupplySourceType.IMPORT_TERMINAL
        }
    },
    'distribution_hubs': [
        {'id': 'hub_delhi', 'name': 'Delhi Hub', 'location': (28.7041, 77.1025)},
        {'id': 'hub_mumbai', 'name': 'Mumbai Hub', 'location': (19.0760, 72.8777)},
        {'id': 'hub_bangalore', 'name': 'Bangalore Hub', 'location': (12.9716, 77.5946)},
        {'id': 'hub_kolkata', 'name': 'Kolkata Hub', 'location': (22.5726, 88.3639)},
        {'id': 'hub_hyderabad', 'name': 'Hyderabad Hub', 'location': (17.3850, 78.4867)},
    ],
    'major_cities': [
        {'id': 'city_delhi', 'name': 'Delhi', 'location': (28.7041, 77.1025), 'demand_mt': 500},
        {'id': 'city_mumbai', 'name': 'Mumbai', 'location': (19.0760, 72.8777), 'demand_mt': 400},
        {'id': 'city_bangalore', 'name': 'Bangalore', 'location': (12.9716, 77.5946), 'demand_mt': 300},
        {'id': 'city_kolkata', 'name': 'Kolkata', 'location': (22.5726, 88.3639), 'demand_mt': 250},
        {'id': 'city_hyderabad', 'name': 'Hyderabad', 'location': (17.3850, 78.4867), 'demand_mt': 280},
        {'id': 'city_pune', 'name': 'Pune', 'location': (18.5204, 73.8567), 'demand_mt': 200},
        {'id': 'city_ahmedabad', 'name': 'Ahmedabad', 'location': (23.0225, 72.5714), 'demand_mt': 220},
        {'id': 'city_jaipur', 'name': 'Jaipur', 'location': (26.9124, 75.7873), 'demand_mt': 180},
    ]
}
