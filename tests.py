"""
Unit tests for LPG optimization system
"""

import unittest
import numpy as np
from backend.optimization.vam_solver import VAMSolver
from backend.optimization.dp_engine import DPInventoryOptimizer, DPVehicleRouter
from backend.optimization.network_flow import NetworkFlowOptimizer


class TestVAMSolver(unittest.TestCase):
    """Test Vogel's Approximation Method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.supply = np.array([100, 150, 120])
        self.demand = np.array([80, 90, 100])
        self.cost_matrix = np.array([
            [2, 3, 1],
            [4, 2, 5],
            [1, 5, 3]
        ])
    
    def test_vam_solver_initialization(self):
        """Test VAM solver initializes correctly"""
        solver = VAMSolver(self.supply, self.demand, self.cost_matrix)
        self.assertEqual(solver.n_suppliers, 3)
        # Supply (370) > Demand (270), so a dummy customer is added → 4 customers
        self.assertEqual(solver.m_customers, 4)
    
    def test_vam_balancing(self):
        """Test problem balancing (supply = demand)"""
        unbalanced_supply = np.array([100, 150])
        solver = VAMSolver(unbalanced_supply, self.demand, self.cost_matrix[:2])
        # After balancing, total supply should equal total demand
        self.assertAlmostEqual(np.sum(solver.supply), np.sum(solver.demand))
    
    def test_vam_solution_feasibility(self):
        """Test solution is feasible (allocations >= 0)"""
        solver = VAMSolver(self.supply, self.demand, self.cost_matrix)
        solution = solver.solve()
        self.assertTrue(np.all(solver.allocation_matrix >= 0))
    
    def test_vam_cost_calculation(self):
        """Test total cost is calculated correctly"""
        solver = VAMSolver(self.supply, self.demand, self.cost_matrix)
        solution = solver.solve()
        # Cost uses the (possibly expanded) cost matrix after balancing
        expected_cost = np.sum(solver.allocation_matrix * solver.cost_matrix)
        self.assertAlmostEqual(solution.total_cost, expected_cost)


class TestDPEngine(unittest.TestCase):
    """Test Dynamic Programming optimization"""
    
    def test_eoq_calculation(self):
        """Test Economic Order Quantity calculation"""
        optimizer = DPInventoryOptimizer(['loc1', 'loc2'], 7)
        eoq, cost = optimizer.calculate_optimal_order_quantity(
            annual_demand=5000,
            holding_cost_per_unit=50,
            ordering_cost=2000,
            lead_time_days=3
        )
        
        self.assertGreater(eoq, 0)
        self.assertGreater(cost, 0)
    
    def test_safety_stock(self):
        """Test safety stock calculation"""
        optimizer = DPInventoryOptimizer(['loc1'], 7)
        safety_stock = optimizer.calculate_safety_stock(
            z_score=1.96,
            daily_demand_std=10,
            lead_time_days=3
        )
        
        self.assertGreater(safety_stock, 0)
    
    def test_vehicle_routing(self):
        """Test vehicle routing optimization"""
        router = DPVehicleRouter(num_vehicles=3, max_capacity=100)
        nodes = ['depot', 'loc1', 'loc2', 'loc3', 'loc4']
        distances = np.array([
            [0, 10, 20, 30, 15],
            [10, 0, 15, 25, 20],
            [20, 15, 0, 18, 12],
            [30, 25, 18, 0, 22],
            [15, 20, 12, 22, 0]
        ])
        demands = {'loc1': 20, 'loc2': 30, 'loc3': 25, 'loc4': 15}
        
        result = router.optimize_multi_vehicle_routing(
            nodes, distances, demands, vehicle_costs_per_km=50
        )
        
        self.assertGreater(len(result['routes']), 0)
        self.assertGreater(result['total_cost'], 0)


class TestNetworkFlow(unittest.TestCase):
    """Test Network Flow optimization"""
    
    def test_network_creation(self):
        """Test network graph creation"""
        optimizer = NetworkFlowOptimizer()
        optimizer.add_node("A")
        optimizer.add_node("B")
        optimizer.add_edge("A", "B", 100, 50)
        
        self.assertIn("A", optimizer.nodes)
        self.assertIn("B", optimizer.nodes)
    
    def test_min_cost_flow(self):
        """Test min-cost flow solution"""
        optimizer = NetworkFlowOptimizer()
        
        # Build simple network
        optimizer.add_edge("S", "A", 100, 1)
        optimizer.add_edge("A", "T", 100, 1)
        optimizer.add_edge("S", "B", 100, 2)
        optimizer.add_edge("B", "T", 100, 2)
        
        result = optimizer.solve_min_cost_flow("S", "T", 100)
        
        self.assertGreater(result['total_flow'], 0)
        self.assertGreater(result['total_cost'], 0)


if __name__ == '__main__':
    unittest.main()
