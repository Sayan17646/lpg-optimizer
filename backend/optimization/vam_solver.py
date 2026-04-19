"""
Vogel's Approximation Method (VAM) for Transport Problem Optimization
Used for minimizing transportation cost from suppliers to customers
"""

import numpy as np
from typing import Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class TransportSolution:
    """Result of VAM optimization"""
    allocation_matrix: np.ndarray
    total_cost: float
    iterations: int
    balanced: bool
    penalties: Dict


class VAMSolver:
    """
    Vogel's Approximation Method Solver
    Solves the transportation problem efficiently
    """
    
    def __init__(self, supply: np.ndarray, demand: np.ndarray, cost_matrix: np.ndarray):
        """
        Initialize VAM solver
        
        Args:
            supply: Array of supply quantities from suppliers [S1, S2, ..., Sn]
            demand: Array of demand quantities to customers [D1, D2, ..., Dm]
            cost_matrix: Cost matrix [n_suppliers x m_customers]
        """
        self.supply = supply.copy()
        self.demand = demand.copy()
        self.cost_matrix = cost_matrix.copy()
        self.original_supply = supply.copy()
        self.original_demand = demand.copy()
        
        self.n_suppliers = len(supply)
        self.m_customers = len(demand)
        self.allocation_matrix = np.zeros((self.n_suppliers, self.m_customers))
        
        self._balance_problem()
        
    def _balance_problem(self):
        """Balance supply and demand by adding dummy rows/columns if needed"""
        total_supply = np.sum(self.supply)
        total_demand = np.sum(self.demand)
        
        if total_supply > total_demand:
            # Excess supply → add dummy customer (column) to absorb surplus
            deficit = total_supply - total_demand
            self.demand = np.append(self.demand, deficit)
            # Add zero-cost column for dummy customer
            dummy_col = np.zeros(self.n_suppliers).reshape(-1, 1)
            self.cost_matrix = np.hstack([self.cost_matrix, dummy_col])
            self.m_customers += 1
            
        elif total_demand > total_supply:
            # Excess demand → add dummy supplier (row) to represent unmet demand
            excess = total_demand - total_supply
            self.supply = np.append(self.supply, excess)
            # Add zero-cost row for dummy supplier
            dummy_row = np.zeros(self.m_customers).reshape(1, -1)
            self.cost_matrix = np.vstack([self.cost_matrix, dummy_row])
            self.n_suppliers += 1
        
        # Rebuild allocation matrix to match (possibly expanded) dimensions
        self.allocation_matrix = np.zeros((self.n_suppliers, self.m_customers))
    
    def _calculate_penalties(self, costs_2d: np.ndarray) -> np.ndarray:
        """Calculate penalties (difference between min and 2nd min)"""
        penalties = []
        for row in costs_2d:
            if len(row) >= 2:
                sorted_costs = np.sort(row)
                penalty = sorted_costs[1] - sorted_costs[0]
            else:
                penalty = 0
            penalties.append(penalty)
        return np.array(penalties)
    
    def solve(self) -> TransportSolution:
        """Solve using Vogel's Approximation Method"""
        iterations = 0
        active_supply = self.supply.copy()
        active_demand = self.demand.copy()
        cost_matrix = self.cost_matrix.copy()
        
        penalty_history = {}
        
        while np.sum(active_supply) > 0 and np.sum(active_demand) > 0:
            iterations += 1
            
            # Calculate row and column penalties
            row_penalties = []
            for i in range(len(active_supply)):
                if active_supply[i] > 0:
                    costs = cost_matrix[i]
                    valid_costs = []
                    for j in range(len(active_demand)):
                        if active_demand[j] > 0:
                            valid_costs.append(costs[j])
                    
                    if len(valid_costs) >= 2:
                        valid_costs.sort()
                        penalty = valid_costs[1] - valid_costs[0]
                    elif len(valid_costs) == 1:
                        penalty = valid_costs[0]
                    else:
                        penalty = 0
                else:
                    penalty = -1  # Mark as inactive
                row_penalties.append((penalty, 'row', i))
            
            col_penalties = []
            for j in range(len(active_demand)):
                if active_demand[j] > 0:
                    costs = cost_matrix[:, j]
                    valid_costs = []
                    for i in range(len(active_supply)):
                        if active_supply[i] > 0:
                            valid_costs.append(costs[i])
                    
                    if len(valid_costs) >= 2:
                        valid_costs.sort()
                        penalty = valid_costs[1] - valid_costs[0]
                    elif len(valid_costs) == 1:
                        penalty = valid_costs[0]
                    else:
                        penalty = 0
                else:
                    penalty = -1
                col_penalties.append((penalty, 'col', j))
            
            # Find max penalty
            all_penalties = row_penalties + col_penalties
            all_penalties.sort(reverse=True, key=lambda x: x[0])
            
            if all_penalties[0][0] <= 0:
                break
            
            max_penalty, penalty_type, index = all_penalties[0]
            penalty_history[f"iteration_{iterations}"] = {
                'type': penalty_type,
                'index': index,
                'penalty': max_penalty
            }
            
            # Find cell with minimum cost in selected row/column
            if penalty_type == 'row':
                i = index
                min_cost = float('inf')
                j = -1
                for jj in range(len(active_demand)):
                    if active_demand[jj] > 0 and cost_matrix[i][jj] < min_cost:
                        min_cost = cost_matrix[i][jj]
                        j = jj
            else:
                j = index
                min_cost = float('inf')
                i = -1
                for ii in range(len(active_supply)):
                    if active_supply[ii] > 0 and cost_matrix[ii][j] < min_cost:
                        min_cost = cost_matrix[ii][j]
                        i = ii
            
            if i == -1 or j == -1:
                break  # No valid cell found
            
            # Allocate min(supply[i], demand[j])
            allocation = min(active_supply[i], active_demand[j])
            if allocation <= 0:
                break  # Safety: avoid infinite loop on zero allocation
            self.allocation_matrix[i][j] += allocation
            active_supply[i] -= allocation
            active_demand[j] -= allocation
        
        total_cost = np.sum(self.allocation_matrix * self.cost_matrix)
        
        return TransportSolution(
            allocation_matrix=self.allocation_matrix,
            total_cost=total_cost,
            iterations=iterations,
            balanced=True,
            penalties=penalty_history
        )
    
    def get_solution_summary(self) -> Dict:
        """Get detailed solution summary"""
        solution = self.solve()
        
        routes = []
        for i in range(self.n_suppliers):
            for j in range(self.m_customers):
                if self.allocation_matrix[i][j] > 0:
                    routes.append({
                        'supplier': i,
                        'customer': j,
                        'quantity': self.allocation_matrix[i][j],
                        'cost_per_unit': self.cost_matrix[i][j],
                        'total_cost': self.allocation_matrix[i][j] * self.cost_matrix[i][j]
                    })
        
        return {
            'total_cost': solution.total_cost,
            'iterations': solution.iterations,
            'routes': routes,
            'allocation_matrix': self.allocation_matrix.tolist(),
            'penalties': solution.penalties
        }
