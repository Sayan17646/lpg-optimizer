"""
Network Flow Optimization for LPG Distribution
Uses max-flow min-cost algorithms
"""

import heapq
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Edge:
    """Represents a network edge"""
    to_node: str
    capacity: float
    cost: float
    flow: float = 0.0
    reverse_capacity: float = 0.0


class NetworkFlowOptimizer:
    """
    Min-Cost Max-Flow solver for LPG distribution network
    """
    
    def __init__(self):
        """Initialize network flow optimizer"""
        self.graph = defaultdict(lambda: defaultdict(lambda: Edge))
        self.nodes = set()
    
    def add_node(self, node_id: str):
        """Add node to network"""
        self.nodes.add(node_id)
    
    def add_edge(
        self,
        from_node: str,
        to_node: str,
        capacity: float,
        cost: float
    ):
        """
        Add edge to network
        
        Args:
            from_node: Source node
            to_node: Destination node
            capacity: Maximum flow capacity
            cost: Cost per unit of flow
        """
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        
        # Forward edge
        self.graph[from_node][to_node] = Edge(
            to_node=to_node,
            capacity=capacity,
            cost=cost,
            flow=0.0
        )
        
        # Reverse edge (for cancellation)
        self.graph[to_node][from_node] = Edge(
            to_node=from_node,
            capacity=0,
            cost=-cost,
            flow=0.0
        )
    
    def successive_shortest_paths(
        self,
        source: str,
        sink: str,
        max_flow: float
    ) -> Tuple[float, float, Dict]:
        """
        Successive Shortest Paths algorithm
        Finds min-cost max-flow
        
        Returns:
            (total_flow, total_cost, flow_decomposition)
        """
        total_flow = 0.0
        total_cost = 0.0
        flow_decomposition = {}
        
        while total_flow < max_flow:
            # Find shortest path using Dijkstra
            distances, parents = self._dijkstra(source)
            
            if sink not in distances or distances[sink] == float('inf'):
                break  # No more augmenting paths
            
            # Find bottleneck capacity
            path = self._reconstruct_path(source, sink, parents)
            bottleneck = float('inf')
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                bottleneck = min(bottleneck, self.graph[u][v].capacity)
            
            # Limit by remaining flow needed
            flow_increment = min(bottleneck, max_flow - total_flow)
            
            if flow_increment == 0:
                break
            
            # Update flows
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.graph[u][v].flow += flow_increment
                self.graph[u][v].capacity -= flow_increment
                self.graph[v][u].capacity += flow_increment
                
                # Record flow
                flow_key = f"{u}->{v}"
                if flow_key not in flow_decomposition:
                    flow_decomposition[flow_key] = 0
                flow_decomposition[flow_key] += flow_increment
            
            # Update cost
            path_cost = distances[sink] * flow_increment
            total_cost += path_cost
            total_flow += flow_increment
        
        return total_flow, total_cost, flow_decomposition
    
    def _dijkstra(self, source: str) -> Tuple[Dict, Dict]:
        """
        Dijkstra's algorithm for shortest path
        
        Returns:
            (distances, parents)
        """
        distances = {node: float('inf') for node in self.nodes}
        distances[source] = 0
        parents = {node: None for node in self.nodes}
        
        pq = [(0, source)]
        visited = set()
        
        while pq:
            curr_dist, curr_node = heapq.heappop(pq)
            
            if curr_node in visited:
                continue
            visited.add(curr_node)
            
            if curr_dist > distances[curr_node]:
                continue
            
            for next_node in self.graph[curr_node]:
                edge = self.graph[curr_node][next_node]
                
                if edge.capacity > 0:
                    new_dist = curr_dist + edge.cost
                    
                    if new_dist < distances[next_node]:
                        distances[next_node] = new_dist
                        parents[next_node] = curr_node
                        heapq.heappush(pq, (new_dist, next_node))
        
        return distances, parents
    
    def _reconstruct_path(
        self,
        source: str,
        sink: str,
        parents: Dict
    ) -> List[str]:
        """Reconstruct path from source to sink"""
        path = []
        current = sink
        
        while current is not None:
            path.append(current)
            current = parents[current]
        
        path.reverse()
        return path
    
    def solve_min_cost_flow(
        self,
        source: str,
        sink: str,
        demand: float
    ) -> Dict:
        """
        Solve min-cost flow problem
        
        Returns:
            Solution with flows and total cost
        """
        total_flow, total_cost, flows = self.successive_shortest_paths(
            source, sink, demand
        )
        
        return {
            'total_flow': total_flow,
            'total_cost': total_cost,
            'flows': flows,
            'satisfied': total_flow >= demand * 0.95,  # 95% satisfaction
            'efficiency': total_flow / demand if demand > 0 else 0
        }
    
    def get_network_summary(self) -> Dict:
        """Get summary of network topology"""
        edges = []
        
        for from_node in self.graph:
            for to_node, edge in self.graph[from_node].items():
                if edge.cost >= 0:  # Skip reverse edges
                    edges.append({
                        'from': from_node,
                        'to': to_node,
                        'capacity': edge.capacity,
                        'cost': edge.cost,
                        'flow': edge.flow
                    })
        
        return {
            'num_nodes': len(self.nodes),
            'num_edges': len(edges),
            'nodes': list(self.nodes),
            'edges': edges
        }


class LPGNetworkBuilder:
    """
    Builds LPG distribution network from supply/demand data
    """
    
    @staticmethod
    def build_india_network(
        plants: Dict,  # {id: {capacity, location}}
        hubs: Dict,    # {id: {demand, location}}
        retailers: Dict  # {id: {demand, location}}
    ) -> NetworkFlowOptimizer:
        """
        Build India-scale LPG distribution network
        """
        optimizer = NetworkFlowOptimizer()
        
        # Add source
        optimizer.add_node("SOURCE")
        
        # Add plants
        for plant_id, plant_data in plants.items():
            optimizer.add_node(plant_id)
            optimizer.add_edge("SOURCE", plant_id, plant_data['capacity'], 0)
        
        # Add hubs
        for hub_id in hubs.keys():
            optimizer.add_node(hub_id)
        
        # Add retailers
        for retailer_id in retailers.keys():
            optimizer.add_node(retailer_id)
        
        # Add sink
        optimizer.add_node("SINK")
        
        # Connect plants to hubs (distribution routes)
        for plant_id in plants.keys():
            for hub_id in hubs.keys():
                # Capacity: hub demand, Cost: proportional to distance
                cost = plants[plant_id].get('distance_to_hub', {}).get(hub_id, 1)
                optimizer.add_edge(plant_id, hub_id, float('inf'), cost)
        
        # Connect hubs to retailers
        for hub_id in hubs.keys():
            for retailer_id in retailers.keys():
                cost = hubs[hub_id].get('distance_to_retailer', {}).get(retailer_id, 1)
                optimizer.add_edge(hub_id, retailer_id, float('inf'), cost)
        
        # Connect retailers to sink
        for retailer_id, retailer_data in retailers.items():
            optimizer.add_edge(retailer_id, "SINK", retailer_data['demand'], 0)
        
        return optimizer
