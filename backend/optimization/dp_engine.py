"""
Dynamic Programming Engine for Inventory Management and Vehicle Routing
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class InventoryState:
    """Represents inventory at a point in time"""
    location_id: str
    quantity: float
    holding_cost: float
    reorder_point: float
    lead_time: int  # days


@dataclass
class RoutingDecision:
    """Vehicle routing decision"""
    from_node: str
    to_node: str
    quantity: float
    cost: float
    time_hours: float


class DPInventoryOptimizer:
    """
    Dynamic Programming for inventory optimization
    Minimizes total inventory holding and stockout costs
    """
    
    def __init__(self, locations: List[str], time_periods: int):
        """
        Initialize DP inventory optimizer
        
        Args:
            locations: List of location IDs
            time_periods: Number of time periods to optimize over
        """
        self.locations = locations
        self.time_periods = time_periods
        self.memo = {}
        
    def calculate_optimal_order_quantity(
        self,
        annual_demand: float,
        holding_cost_per_unit: float,
        ordering_cost: float,
        lead_time_days: int
    ) -> Tuple[float, float]:
        """
        Economic Order Quantity (EOQ) using DP
        
        Returns:
            (optimal_order_quantity, total_annual_cost)
        """
        # EOQ formula: sqrt(2 * D * S / H)
        eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)
        
        # Reorder point = demand during lead time + safety stock
        daily_demand = annual_demand / 365
        reorder_point = daily_demand * lead_time_days
        
        # Total cost = holding cost + ordering cost
        num_orders = annual_demand / eoq
        total_holding_cost = (eoq / 2) * holding_cost_per_unit
        total_ordering_cost = num_orders * ordering_cost
        total_cost = total_holding_cost + total_ordering_cost
        
        return eoq, total_cost
    
    def calculate_safety_stock(
        self,
        z_score: float,  # Service level
        daily_demand_std: float,
        lead_time_days: int
    ) -> float:
        """Calculate safety stock level"""
        return z_score * daily_demand_std * np.sqrt(lead_time_days)
    
    def optimize_multi_period_inventory(
        self,
        initial_inventory: Dict[str, float],
        demand_forecast: Dict[str, List[float]],  # location -> [period1, period2, ...]
        holding_costs: Dict[str, float],  # location -> cost per unit per period
        replenishment_costs: Dict[str, float],  # location -> cost per order
        max_capacity: Dict[str, float],  # location -> max inventory
    ) -> Dict:
        """
        Optimize inventory levels across multiple periods using DP
        
        Returns:
            Optimal replenishment schedule and costs
        """
        dp_table = {}
        decision_table = {}
        
        # Initialize
        for location in self.locations:
            dp_table[location] = [0] * (self.time_periods + 1)
            decision_table[location] = []
        
        # Forward pass: calculate optimal cost for each period
        for t in range(self.time_periods):
            for location in self.locations:
                if t == 0:
                    # First period
                    current_inv = initial_inventory.get(location, 0)
                else:
                    current_inv = initial_inventory.get(location, 0)  # Simplified
                
                demand = demand_forecast.get(location, [0] * self.time_periods)[t]
                holding_cost = holding_costs.get(location, 0)
                replenish_cost = replenishment_costs.get(location, 0)
                capacity = max_capacity.get(location, float('inf'))
                
                # Find optimal order quantity for this period
                if current_inv < demand:
                    # Need to replenish
                    order_qty = min(demand + holding_cost, capacity - current_inv)
                    cost = replenish_cost + (current_inv + order_qty - demand) * holding_cost
                else:
                    # No replenishment needed
                    order_qty = 0
                    cost = (current_inv - demand) * holding_cost
                
                dp_table[location][t + 1] = dp_table[location][t] + cost
                decision_table[location].append({
                    'period': t,
                    'order_qty': order_qty,
                    'cost': cost,
                    'ending_inventory': max(0, current_inv + order_qty - demand)
                })
        
        return {
            'total_costs': {loc: dp_table[loc][-1] for loc in self.locations},
            'decisions': decision_table,
            'schedule': self._extract_replenishment_schedule(decision_table)
        }
    
    def _extract_replenishment_schedule(self, decisions: Dict) -> List[Dict]:
        """Extract actionable replenishment schedule"""
        schedule = []
        for location, decisions_list in decisions.items():
            for decision in decisions_list:
                if decision['order_qty'] > 0:
                    schedule.append({
                        'location': location,
                        'period': decision['period'],
                        'order_quantity': decision['order_qty'],
                        'cost': decision['cost']
                    })
        return schedule


class DPVehicleRouter:
    """
    Dynamic Programming for vehicle routing optimization
    Minimizes total routing cost and time
    """
    
    def __init__(self, num_vehicles: int, max_capacity: float):
        """
        Initialize DP vehicle router
        
        Args:
            num_vehicles: Number of vehicles available
            max_capacity: Maximum capacity per vehicle
        """
        self.num_vehicles = num_vehicles
        self.max_capacity = max_capacity
        self.memo = {}
    
    def tsp_nearest_neighbor(
        self,
        start_node: str,
        nodes: List[str],
        distances: np.ndarray,
        demands: Dict[str, float]
    ) -> Tuple[List[str], float]:
        """
        Nearest Neighbor heuristic for TSP
        Quick approximation for vehicle routing
        """
        unvisited = set(nodes)
        current = start_node
        route = [start_node]
        total_distance = 0
        unvisited.discard(start_node)
        
        total_capacity = 0
        
        while unvisited:
            # Find nearest unvisited node
            nearest = None
            min_dist = float('inf')
            
            for node in unvisited:
                node_idx = nodes.index(node)
                curr_idx = nodes.index(current)
                dist = distances[curr_idx][node_idx]
                
                if dist < min_dist:
                    min_dist = dist
                    nearest = node
            
            if nearest:
                node_demand = demands.get(nearest, 0)
                if total_capacity + node_demand <= self.max_capacity:
                    route.append(nearest)
                    total_distance += min_dist
                    current = nearest
                    total_capacity += node_demand
                    unvisited.discard(nearest)
                else:
                    break  # Vehicle capacity full
        
        # Return to start
        if len(route) > 1:
            last_idx = nodes.index(route[-1])
            start_idx = nodes.index(start_node)
            total_distance += distances[last_idx][start_idx]
        
        return route, total_distance
    
    def optimize_multi_vehicle_routing(
        self,
        nodes: List[str],
        distances: np.ndarray,
        demands: Dict[str, float],
        vehicle_costs_per_km: float
    ) -> Dict:
        """
        Optimize multi-vehicle routing
        
        Returns:
            Routes for each vehicle with total cost
        """
        routes = []
        unserved = set(nodes)
        unserved.discard(nodes[0])  # Remove depot
        total_cost = 0
        
        for vehicle_id in range(self.num_vehicles):
            if not unserved:
                break
            
            # Find best route starting from depot
            best_route = [nodes[0]]
            best_distance = 0
            current = nodes[0]
            vehicle_capacity = 0
            
            while unserved:
                nearest = None
                min_dist = float('inf')
                
                for node in unserved:
                    node_idx = nodes.index(node)
                    curr_idx = nodes.index(current)
                    dist = distances[curr_idx][node_idx]
                    
                    node_demand = demands.get(node, 0)
                    if (vehicle_capacity + node_demand <= self.max_capacity and 
                        dist < min_dist):
                        min_dist = dist
                        nearest = node
                
                if nearest:
                    best_route.append(nearest)
                    best_distance += min_dist
                    vehicle_capacity += demands.get(nearest, 0)
                    current = nearest
                    unserved.discard(nearest)
                else:
                    break
            
            # Return to depot
            if len(best_route) > 1:
                last_idx = nodes.index(best_route[-1])
                depot_idx = 0
                best_distance += distances[last_idx][depot_idx]
            
            vehicle_cost = best_distance * vehicle_costs_per_km
            routes.append({
                'vehicle_id': vehicle_id,
                'route': best_route,
                'distance': best_distance,
                'cost': vehicle_cost,
                'load': sum(demands.get(n, 0) for n in best_route if n != nodes[0])
            })
            total_cost += vehicle_cost
        
        return {
            'routes': routes,
            'total_cost': total_cost,
            'vehicles_used': len(routes),
            'unserved_nodes': list(unserved) if unserved else None
        }
