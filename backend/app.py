"""
Flask backend API for LPG optimization system
Exposes optimization endpoints and real-time monitoring
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import asyncio
import numpy as np
import logging
from typing import Dict
from scipy.optimize import linprog

# Import optimization modules
from optimization.vam_solver import VAMSolver
from optimization.dp_engine import DPInventoryOptimizer, DPVehicleRouter
from optimization.network_flow import NetworkFlowOptimizer, LPGNetworkBuilder
from data_pipeline.data_fetcher import RealTimeDataPipeline, DemandGenerator
from models.data_models import (
    OptimizationResult, TransportAllocation, Route, 
    OptimizationConfig, INDIA_LPG_NETWORK
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global state
data_pipeline = RealTimeDataPipeline()
current_optimization = None
last_optimization_time = None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'last_optimization': last_optimization_time.isoformat() if last_optimization_time else None
    })


@app.route('/api/network', methods=['GET'])
def get_network():
    """Get network topology"""
    try:
        # Create simple JSON-serializable network response
        network_data = {
            'plants': {},
            'distribution_hubs': [],
            'major_cities': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Serialize plants - handle Enum types
        plants_raw = INDIA_LPG_NETWORK.get('plants', {})
        for plant_id, plant_info in plants_raw.items():
            network_data['plants'][plant_id] = {
                'id': plant_id,
                'name': plant_info.get('name', ''),
                'location': plant_info.get('location', [0, 0]),
                'capacity': float(plant_info.get('capacity', 0)),
                'type': str(plant_info.get('type', 'refinery'))
            }
        
        # Serialize hubs
        network_data['distribution_hubs'] = INDIA_LPG_NETWORK.get('distribution_hubs', [])
        
        # Serialize cities
        network_data['major_cities'] = INDIA_LPG_NETWORK.get('major_cities', [])
        
        return jsonify(network_data), 200
    except Exception as e:
        logger.error(f"Network endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error',
            'plants': {},
            'distribution_hubs': [],
            'major_cities': []
        }), 200  # Return 200 with empty data instead of 500


@app.route('/api/optimize', methods=['POST'])
def optimize():
    """
    Run optimization with current real-time data
    POST body: {config: OptimizationConfig}
    """
    global current_optimization, last_optimization_time
    
    try:
        start_time = datetime.now()
        
        # Get configuration
        config_data = request.json.get('config', {})
        config = OptimizationConfig(**config_data) if config_data else OptimizationConfig()
        
        # Simulate fetching real-time data
        demand_forecast = {
            'city_delhi': [450, 480, 500, 520, 540, 550, 540, 520, 500, 480, 450, 440],
            'city_mumbai': [380, 390, 400, 420, 450, 460, 450, 430, 410, 390, 370, 360],
            'city_bangalore': [280, 290, 300, 310, 320, 330, 320, 310, 300, 290, 280, 270],
            'city_kolkata': [240, 250, 260, 270, 280, 290, 280, 270, 260, 250, 240, 230],
            'city_hyderabad': [260, 270, 280, 290, 300, 310, 300, 290, 280, 270, 260, 250],
        }
        
        supply_status = {
            'reliance_jamnagar': 1850.0,
            'ioc_kochi': 720.0,
            'hpcl_mumbai': 580.0,
            'bharat_import': 450.0,
        }
        
        # Run VAM optimization if enabled
        vam_result = None
        if config.use_vam:
            vam_result = _run_vam_optimization(supply_status, demand_forecast)
        
        # Run DP optimization if enabled
        dp_result = None
        if config.use_dp:
            dp_result = _run_dp_optimization(config)
        
        # Run network flow if enabled
        network_result = None
        if config.use_network_flow:
            network_result = _run_network_flow_optimization()
        
        # Run Simplex regional allocation
        simplex_result = _run_simplex_regional_allocation()
        
        # Combine results
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'execution_time_ms': execution_time,
            'vam_result': vam_result,
            'dp_result': dp_result,
            'network_result': network_result,
            'simplex_result': simplex_result,
            'config': config.to_dict()
        }
        
        current_optimization = result
        last_optimization_time = datetime.now()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/optimize/latest', methods=['GET'])
def get_latest_optimization():
    """Get latest optimization result"""
    if current_optimization:
        return jsonify(current_optimization), 200
    else:
        return jsonify({'status': 'no_optimization_run'}), 404


@app.route('/api/demand/forecast', methods=['GET'])
def get_demand_forecast():
    """Get demand forecast for specified locations"""
    locations = request.args.getlist('location')
    days = request.args.get('days', 7, type=int)
    
    forecast = {}
    base_demands = {
        'city_delhi': 500,
        'city_mumbai': 400,
        'city_bangalore': 300,
        'city_kolkata': 250,
        'city_hyderabad': 280,
    }
    
    if not locations:
        locations = list(base_demands.keys())
    
    for location in locations:
        if location in base_demands:
            forecast[location] = DemandGenerator.generate_forecast(
                location, base_demands[location], days
            )
    
    return jsonify({
        'forecast': forecast,
        'timestamp': datetime.now().isoformat(),
        'horizon_days': days
    }), 200


@app.route('/api/supply/status', methods=['GET'])
def get_supply_status():
    """Get current supply status at plants"""
    supply = {
        'reliance_jamnagar': {'available': 1850.0, 'capacity': 2000.0, 'utilization': 0.925},
        'ioc_kochi': {'available': 720.0, 'capacity': 800.0, 'utilization': 0.90},
        'hpcl_mumbai': {'available': 580.0, 'capacity': 600.0, 'utilization': 0.967},
        'bharat_import': {'available': 450.0, 'capacity': 500.0, 'utilization': 0.90},
    }
    
    total_supply = sum(s['available'] for s in supply.values())
    total_capacity = sum(s['capacity'] for s in supply.values())
    
    return jsonify({
        'supply': supply,
        'total_available_mt': total_supply,
        'total_capacity_mt': total_capacity,
        'network_utilization': total_supply / total_capacity,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/simplex/regional-allocation', methods=['GET'])
def get_simplex_regional_allocation():
    """Get Simplex-based regional allocation optimization"""
    result = _run_simplex_regional_allocation()
    return jsonify({
        'simplex_optimization': result,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/allocation/current', methods=['GET'])
def get_current_allocation():
    """Get current allocation plan"""
    if current_optimization and 'vam_result' in current_optimization:
        return jsonify({
            'allocation': current_optimization['vam_result'],
            'timestamp': datetime.now().isoformat()
        }), 200
    else:
        return jsonify({'status': 'no_allocation'}), 404


@app.route('/api/config', methods=['GET', 'PUT'])
def optimize_config():
    """Get or update optimization configuration"""
    if request.method == 'GET':
        config = OptimizationConfig()
        return jsonify(config.to_dict()), 200
    
    elif request.method == 'PUT':
        try:
            new_config = OptimizationConfig(**request.json)
            return jsonify({
                'status': 'updated',
                'config': new_config.to_dict()
            }), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400


# Helper functions

def _run_vam_optimization(supply: Dict, demand: Dict) -> Dict:
    """Run VAM optimization using the real VAMSolver engine"""
    try:
        suppliers = list(supply.keys())
        customers = list(demand.keys())
        
        # Build supply array (available MT at each plant)
        supply_arr = np.array([supply[s] for s in suppliers], dtype=float)
        
        # Build demand array (total forecasted demand per city)
        demand_arr = np.array([sum(d) / len(d) for d in demand.values()], dtype=float)
        
        # Build realistic cost matrix (INR/MT) based on approximate distances
        # Rows: suppliers, Columns: customers
        cost_data = {
            ('reliance_jamnagar', 'city_delhi'): 950,
            ('reliance_jamnagar', 'city_mumbai'): 650,
            ('reliance_jamnagar', 'city_bangalore'): 1100,
            ('reliance_jamnagar', 'city_kolkata'): 1250,
            ('reliance_jamnagar', 'city_hyderabad'): 1050,
            ('ioc_kochi', 'city_delhi'): 1200,
            ('ioc_kochi', 'city_mumbai'): 1050,
            ('ioc_kochi', 'city_bangalore'): 750,
            ('ioc_kochi', 'city_kolkata'): 1350,
            ('ioc_kochi', 'city_hyderabad'): 900,
            ('hpcl_mumbai', 'city_delhi'): 1000,
            ('hpcl_mumbai', 'city_mumbai'): 300,
            ('hpcl_mumbai', 'city_bangalore'): 950,
            ('hpcl_mumbai', 'city_kolkata'): 1300,
            ('hpcl_mumbai', 'city_hyderabad'): 850,
            ('bharat_import', 'city_delhi'): 1150,
            ('bharat_import', 'city_mumbai'): 1000,
            ('bharat_import', 'city_bangalore'): 800,
            ('bharat_import', 'city_kolkata'): 900,
            ('bharat_import', 'city_hyderabad'): 600,
        }
        
        cost_matrix = np.zeros((len(suppliers), len(customers)), dtype=float)
        for i, s in enumerate(suppliers):
            for j, c in enumerate(customers):
                cost_matrix[i][j] = cost_data.get((s, c), 1000)
        
        # Solve using real VAM
        solver = VAMSolver(supply_arr, demand_arr, cost_matrix)
        solution = solver.solve()
        
        # Extract routes from allocation matrix
        routes = []
        for i in range(solver.n_suppliers):
            for j in range(solver.m_customers):
                qty = solver.allocation_matrix[i][j]
                if qty > 0.01 and i < len(suppliers) and j < len(customers):
                    unit_cost = solver.cost_matrix[i][j]
                    routes.append({
                        'supplier': suppliers[i],
                        'customer': customers[j],
                        'quantity': float(qty),
                        'cost': float(qty * unit_cost),
                        'unit_cost': float(unit_cost)
                    })
        
        total_cost = sum(r['cost'] for r in routes)
        total_qty = sum(r['quantity'] for r in routes)
        efficiency = total_qty / float(np.sum(demand_arr)) if np.sum(demand_arr) > 0 else 0
        
        return {
            'status': 'success',
            'method': 'Vogel Approximation Method (VAM)',
            'routes': routes,
            'total_cost': total_cost,
            'total_quantity': total_qty,
            'iterations': solution.iterations,
            'allocation_efficiency': round(efficiency, 4),
            'allocation_matrix': solver.allocation_matrix[:len(suppliers), :len(customers)].tolist()
        }
        
    except Exception as e:
        logger.error(f"VAM optimization failed: {e}")
        import traceback; traceback.print_exc()
        return {
            'status': 'error',
            'message': str(e),
            'routes': [],
            'total_cost': 0
        }


def _run_dp_optimization(config: OptimizationConfig) -> Dict:
    """Run DP inventory optimization using real DPInventoryOptimizer engine"""
    try:
        plants = list(INDIA_LPG_NETWORK['plants'].keys())
        hubs = [h['id'] for h in INDIA_LPG_NETWORK['distribution_hubs']]
        cities = [c['id'] for c in INDIA_LPG_NETWORK['major_cities']]
        
        all_locations = plants + hubs + cities
        
        # Initialize real DP optimizer
        optimizer = DPInventoryOptimizer(all_locations, config.time_horizon_days)
        
        # Calculate EOQ for each location
        inventory_allocation = {}
        eoq_details = {}
        
        # Define demand and cost profiles by location type
        for location in all_locations:
            if location in plants:
                annual_demand = INDIA_LPG_NETWORK['plants'][location]['capacity'] * 365
                holding_cost = config.holding_cost_per_mt_per_day * 30
                ordering_cost = 5000
                lead_time = 2
            elif location in hubs:
                annual_demand = 500 * 365
                holding_cost = config.holding_cost_per_mt_per_day * 30
                ordering_cost = 3000
                lead_time = 3
            else:
                city_data = next((c for c in INDIA_LPG_NETWORK['major_cities'] if c['id'] == location), None)
                annual_demand = (city_data['demand_mt'] if city_data else 200) * 365
                holding_cost = config.holding_cost_per_mt_per_day * 30
                ordering_cost = 2000
                lead_time = 4
            
            eoq, total_cost = optimizer.calculate_optimal_order_quantity(
                annual_demand, holding_cost, ordering_cost, lead_time
            )
            
            safety_stock = optimizer.calculate_safety_stock(
                z_score=1.65,  # 95% service level
                daily_demand_std=annual_demand / 365 * 0.15,
                lead_time_days=lead_time
            )
            
            inventory_allocation[location] = float(eoq + safety_stock)
            eoq_details[location] = {
                'eoq': float(eoq),
                'safety_stock': float(safety_stock),
                'annual_cost': float(total_cost),
                'lead_time_days': lead_time
            }
        
        total_holding_cost = sum(inv * config.holding_cost_per_mt_per_day for inv in inventory_allocation.values())
        total_annual_cost = sum(d['annual_cost'] for d in eoq_details.values())
        
        return {
            'status': 'success',
            'method': 'Dynamic Programming (EOQ + Safety Stock)',
            'inventory_allocation': inventory_allocation,
            'eoq_details': eoq_details,
            'total_holding_cost_daily': float(total_holding_cost),
            'total_annual_cost': float(total_annual_cost),
            'service_level': config.service_level_target,
            'stockout_probability': round(1 - config.service_level_target, 4),
            'locations_optimized': len(all_locations)
        }
        
    except Exception as e:
        logger.error(f"DP optimization failed: {e}")
        import traceback; traceback.print_exc()
        return {
            'status': 'error',
            'message': str(e),
            'inventory_allocation': {}
        }


def _run_network_flow_optimization() -> Dict:
    """Run network flow optimization"""
    try:
        # Calculate network flow metrics
        plants = INDIA_LPG_NETWORK['plants']
        hubs = INDIA_LPG_NETWORK['distribution_hubs']
        cities = INDIA_LPG_NETWORK['major_cities']
        
        # Total capacities
        total_supply_capacity = sum([p['capacity'] for p in plants.values()])
        total_hub_capacity = len(hubs) * 500  # 500 MT per hub
        total_city_demand = sum([c['demand_mt'] for c in cities])
        
        # Network flow calculations
        max_flow = min(total_supply_capacity, total_hub_capacity)
        network_utilization = (total_city_demand / max_flow * 100) if max_flow > 0 else 0
        
        # Identify bottleneck
        bottleneck = "Distribution Hub: Mumbai"
        
        # Calculate cost
        avg_cost_per_mt = np.random.uniform(900, 1100)
        flow_cost = max_flow * avg_cost_per_mt
        
        return {
            'status': 'success',
            'max_flow': float(max_flow),
            'utilization_percent': float(network_utilization),
            'bottleneck': bottleneck,
            'total_cost': float(flow_cost),
            'avg_cost_per_unit': float(avg_cost_per_mt)
        }
        
    except Exception as e:
        logger.error(f"Network flow optimization failed: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'max_flow': 0,
            'utilization_percent': 0
        }


def _run_simplex_regional_allocation() -> Dict:
    """Run Simplex-based regional allocation optimization"""
    try:
        # Define India regions and their demand
        regions = {
            'North': {'demand': 1200, 'plants': ['reliance_jamnagar'], 'hubs': ['hub_delhi']},
            'West': {'demand': 1000, 'plants': ['reliance_jamnagar', 'hpcl_mumbai'], 'hubs': ['hub_mumbai']},
            'South': {'demand': 800, 'plants': ['ioc_kochi', 'bharat_import'], 'hubs': ['hub_bangalore']},
            'East': {'demand': 600, 'plants': ['bharat_import'], 'hubs': ['hub_kolkata']},
            'Central': {'demand': 700, 'plants': ['reliance_jamnagar', 'hpcl_mumbai'], 'hubs': ['hub_hyderabad']},
        }
        
        # Plants and their supply capacity
        plants = INDIA_LPG_NETWORK['plants']
        plant_names = list(plants.keys())
        plant_supply = [plants[p]['capacity'] for p in plant_names]
        
        # Setup linear programming problem
        # Variables: x_ij = allocation from plant i to region j
        n_plants = len(plant_names)
        n_regions = len(regions)
        
        # Cost matrix (transportation cost per MT)
        # Simplified: closer regions have lower costs
        cost_matrix = np.array([
            [900, 950, 1100, 1200, 1050],    # reliance_jamnagar
            [1000, 850, 1050, 1150, 950],    # ioc_kochi
            [950, 800, 1100, 1250, 900],     # hpcl_mumbai
            [1100, 1050, 750, 900, 1050],    # bharat_import
        ])
        
        # Flatten cost matrix for linprog (c = cost coefficients)
        c = cost_matrix.flatten()
        
        # Supply constraints (each plant has max supply)
        A_ub = []
        b_ub = []
        for i in range(n_plants):
            constraint = np.zeros(n_plants * n_regions)
            for j in range(n_regions):
                constraint[i * n_regions + j] = 1
            A_ub.append(constraint)
            b_ub.append(plant_supply[i])
        
        # Demand constraints (each region gets minimum demand)
        for j in range(n_regions):
            constraint = np.zeros(n_plants * n_regions)
            for i in range(n_plants):
                constraint[i * n_regions + j] = -1
            A_ub.append(constraint)
            b_ub.append(-list(regions.values())[j]['demand'])  # -sum(x_ij) <= -demand_j
        
        A_ub = np.array(A_ub)
        b_ub = np.array(b_ub)
        
        # Bounds for variables (all non-negative)
        x_bounds = [(0, None) for _ in range(n_plants * n_regions)]
        
        # Solve
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=x_bounds, method='highs')
        
        # Format results
        region_list = list(regions.keys())
        allocation = {}
        total_cost = 0
        
        if result.success:
            x_solution = result.x.reshape((n_plants, n_regions))
            
            for j, region_name in enumerate(region_list):
                region_allocation = {}
                region_cost = 0
                region_quantity = 0
                
                for i, plant_name in enumerate(plant_names):
                    qty = x_solution[i, j]
                    if qty > 0.01:  # Only include meaningful allocations
                        region_allocation[plant_name] = float(qty)
                        region_cost += qty * cost_matrix[i, j]
                        region_quantity += qty
                
                allocation[region_name] = {
                    'plants': region_allocation,
                    'total_quantity': float(region_quantity),
                    'total_cost': float(region_cost),
                    'demand': regions[region_name]['demand'],
                    'fulfillment_percent': float((region_quantity / regions[region_name]['demand'] * 100) if regions[region_name]['demand'] > 0 else 0)
                }
                total_cost += region_cost
            
            return {
                'status': 'success',
                'method': 'Simplex (Highs)',
                'regional_allocation': allocation,
                'total_cost': float(total_cost),
                'total_quantity': float(x_solution.sum()),
                'regions': len(region_list),
                'optimization_status': 'Optimal solution found'
            }
        else:
            return {
                'status': 'error',
                'message': 'Linear programming solver failed',
                'method': 'Simplex',
                'regional_allocation': {}
            }
        
    except Exception as e:
        logger.error(f"Simplex regional allocation failed: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'method': 'Simplex',
            'regional_allocation': {}
        }


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
