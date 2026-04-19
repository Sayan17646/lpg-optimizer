"""
Advanced example demonstrating all three optimization algorithms
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

import numpy as np
from optimization.vam_solver import VAMSolver
from optimization.dp_engine import DPInventoryOptimizer, DPVehicleRouter
from optimization.network_flow import NetworkFlowOptimizer, LPGNetworkBuilder
from models.data_models import INDIA_LPG_NETWORK
import time


def example_vam_optimization():
    """
    Example 1: Vogel's Approximation Method for Transport Problem
    Minimize cost of transporting LPG from plants to distribution hubs
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Vogel's Approximation Method (VAM)")
    print("="*70)
    
    # Supply from 3 plants (MT/day)
    plants = ['Jamnagar', 'Kochi', 'Mumbai']
    supply = np.array([1850, 720, 580])  # MT/day
    
    # Demand at 5 distribution hubs (MT/day)
    hubs = ['Delhi', 'Mumbai', 'Bangalore', 'Kolkata', 'Hyderabad']
    demand = np.array([500, 400, 300, 250, 280])  # MT/day
    
    # Transportation cost matrix (₹ per MT)
    cost_matrix = np.array([
        [850, 650, 920, 1200, 1100],   # From Jamnagar
        [1050, 1250, 800, 950, 1000],  # From Kochi
        [680, 320, 920, 1100, 950],    # From Mumbai
    ])
    
    print(f"\nSupply (MT/day): {dict(zip(plants, supply))}")
    print(f"Demand (MT/day): {dict(zip(hubs, demand))}")
    print(f"\nTransport Cost Matrix (₹/MT):")
    print(f"         {hubs}")
    for i, plant in enumerate(plants):
        print(f"{plant:12} {cost_matrix[i]}")
    
    # Solve using VAM
    start = time.time()
    solver = VAMSolver(supply, demand, cost_matrix)
    solution = solver.solve()
    elapsed = time.time() - start
    
    print(f"\n✅ VAM Solution:")
    print(f"   Total Transportation Cost: ₹{solution.total_cost:,.0f}")
    print(f"   Iterations: {solution.iterations}")
    print(f"   Execution Time: {elapsed*1000:.2f} ms")
    
    print(f"\n📊 Allocation Details (Top 5 routes):")
    summary = solver.get_solution_summary()
    for i, route in enumerate(summary['routes'][:5]):
        plant = plants[route['supplier']]
        hub = hubs[route['customer']]
        qty = route['quantity']
        cost = route['total_cost']
        print(f"   {i+1}. {plant:12} → {hub:12} : {qty:6.0f} MT @ ₹{cost:,.0f}")


def example_dp_optimization():
    """
    Example 2: Dynamic Programming for Inventory Optimization
    Minimize inventory holding and ordering costs
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Dynamic Programming - Inventory Optimization")
    print("="*70)
    
    # Initialize DP engine
    locations = ['Jamnagar_Hub', 'Kochi_Hub', 'Mumbai_Hub', 'Delhi_Hub']
    optimizer = DPInventoryOptimizer(locations, time_periods=7)
    
    print(f"\nOptimizing inventory for {len(locations)} distribution hubs")
    print(f"Planning horizon: 7 days\n")
    
    # Example: Calculate EOQ for Delhi Hub
    print("📦 Economic Order Quantity Analysis (Delhi Hub):")
    print("-" * 50)
    
    eoq, total_cost = optimizer.calculate_optimal_order_quantity(
        annual_demand=150000,  # MT/year
        holding_cost_per_unit=50,  # ₹/MT/day
        ordering_cost=2000,  # ₹ per order
        lead_time_days=3
    )
    
    print(f"   Annual Demand: 150,000 MT")
    print(f"   Optimal Order Quantity (EOQ): {eoq:,.0f} MT")
    print(f"   Annual Holding Cost: ₹{(eoq/2) * 50 * 365:,.0f}")
    print(f"   Annual Ordering Cost: ₹{(150000/eoq) * 2000:,.0f}")
    print(f"   Total Annual Cost: ₹{total_cost * 365:,.0f}")
    
    # Safety stock calculation
    print(f"\n🔒 Safety Stock Calculation:")
    print("-" * 50)
    
    safety_stock = optimizer.calculate_safety_stock(
        z_score=1.96,  # 95% service level
        daily_demand_std=50,  # MT
        lead_time_days=3
    )
    
    print(f"   Service Level Target: 95%")
    print(f"   Daily Demand Std Dev: 50 MT")
    print(f"   Lead Time: 3 days")
    print(f"   Safety Stock Required: {safety_stock:,.0f} MT")


def example_vehicle_routing():
    """
    Example 3: Vehicle Routing Optimization
    Minimize distance and cost for LPG deliveries
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Dynamic Programming - Vehicle Routing")
    print("="*70)
    
    # Initialize router
    router = DPVehicleRouter(num_vehicles=3, max_capacity=20)
    
    # Cities to serve
    nodes = ['Depot', 'Mumbai', 'Pune', 'Nashik', 'Nagpur', 'Aurangabad']
    
    # Distance matrix (km)
    distances = np.array([
        [0, 150, 240, 380, 800, 350],      # Depot
        [150, 0, 120, 250, 750, 220],      # Mumbai
        [240, 120, 0, 200, 680, 200],      # Pune
        [380, 250, 200, 0, 580, 150],      # Nashik
        [800, 750, 680, 580, 0, 500],      # Nagpur
        [350, 220, 200, 150, 500, 0],      # Aurangabad
    ])
    
    # Demand at each location (MT)
    demands = {
        'Mumbai': 15,
        'Pune': 12,
        'Nashik': 8,
        'Nagpur': 18,
        'Aurangabad': 10
    }
    
    print(f"\n🗺️  Delivery Network:")
    print(f"   Depot: Mumbai")
    print(f"   Cities to serve: {len(nodes)-1}")
    print(f"   Vehicle capacity: 20 MT")
    print(f"   Total demand: {sum(demands.values())} MT")
    
    # Solve routing
    start = time.time()
    result = router.optimize_multi_vehicle_routing(
        nodes, distances, demands, vehicle_costs_per_km=50
    )
    elapsed = time.time() - start
    
    print(f"\n✅ Routing Solution:")
    print(f"   Vehicles Used: {result['vehicles_used']}")
    print(f"   Total Distance: {result['total_cost']/50:,.0f} km")
    print(f"   Total Cost: ₹{result['total_cost']:,.0f}")
    print(f"   Execution Time: {elapsed*1000:.2f} ms")
    
    print(f"\n🚛 Vehicle Routes:")
    for route in result['routes']:
        cities = ' → '.join(route['route'])
        print(f"   Vehicle {route['vehicle_id']+1}: {cities}")
        print(f"        Distance: {route['distance']:.0f} km | Load: {route['load']:.0f} MT | Cost: ₹{route['cost']:,.0f}")


def example_network_flow():
    """
    Example 4: Network Flow for Multi-Level Distribution
    Optimize 3-level network: Plants → Hubs → Retailers
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Min-Cost Max-Flow Network Optimization")
    print("="*70)
    
    # Build India-scale network
    plants = INDIA_LPG_NETWORK['plants']
    hubs = {h['id']: {'demand': 300} for h in INDIA_LPG_NETWORK['distribution_hubs']}
    retailers = {c['id']: {'demand': c['demand_mt']} for c in INDIA_LPG_NETWORK['major_cities']}
    
    print(f"\n🌍 India-Scale LPG Network:")
    print(f"   Suppliers (Plants): {len(plants)}")
    print(f"   Distribution Hubs: {len(hubs)}")
    print(f"   Retail Points (Cities): {len(retailers)}")
    
    # Build network
    start = time.time()
    network = LPGNetworkBuilder.build_india_network(plants, hubs, retailers)
    elapsed = time.time() - start
    
    # Solve min-cost max-flow
    total_demand = sum(d['demand'] for d in retailers.values())
    result = network.solve_min_cost_flow('SOURCE', 'SINK', total_demand)
    
    print(f"\n✅ Network Flow Solution:")
    print(f"   Total Flow: {result['total_flow']:,.0f} MT/day")
    print(f"   Demand Satisfaction: {result['efficiency']*100:.1f}%")
    print(f"   Total Distribution Cost: ₹{result['total_cost']:,.0f}")
    print(f"   Network Build Time: {elapsed*1000:.2f} ms")
    
    # Network summary
    summary = network.get_network_summary()
    print(f"\n📊 Network Topology:")
    print(f"   Nodes: {summary['num_nodes']}")
    print(f"   Routes: {summary['num_edges']}")


def main():
    """Run all examples"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║    LPG OPTIMIZATION SYSTEM - COMPREHENSIVE EXAMPLES         ║
    ║                                                            ║
    ║  Demonstrating:                                          ║
    ║  1. Vogel's Approximation Method (Transport Problem)     ║
    ║  2. Dynamic Programming (Inventory Optimization)          ║
    ║  3. Vehicle Routing (DP-based)                            ║
    ║  4. Network Flow (Min-Cost Max-Flow)                      ║
    ║  5. India-Scale LPG Distribution Network                 ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Run all examples
        example_vam_optimization()
        example_dp_optimization()
        example_vehicle_routing()
        example_network_flow()
        
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n💡 Next Steps:")
        print("   1. Run: python run.py  (start Flask backend)")
        print("   2. Run: npm start       (start React frontend)")
        print("   3. Open: http://localhost:3000  (access dashboard)")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
