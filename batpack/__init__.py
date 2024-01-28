from typing import List
import cvxpy as cp
import numpy as np



def pack_battery(series:int, parallel:int, cell_capacities:List[int]):
    """
    Packs a battery with the given parameters.

    series: number of banks in pack
    parallel: number of cells in bank
    cell_capacities: list of cell capacities measured (usually in mAh, but units doesn't 
        matter as long as they are in the same units)
    
    """
    cells_count = series*parallel
    assert cells_count == len(cell_capacities), "Series and parallel must match the number of cells."
    capacities = np.array(cell_capacities)
    ideal_pack_size = capacities.sum()/series
    X = cp.Variable((cells_count, series), boolean=True) 
    constraints = [
        cp.sum(X, axis=1) == 1,             # cell could be used only once
        cp.sum(X, axis=0) == parallel,      # each bank has that many cells in parallel
        ]
    b = np.array(series)
    b.fill(ideal_pack_size)
    objective = cp.Minimize( cp.sum_squares(  capacities @ X  - b))
    problem = cp.Problem(objective, constraints)
    problem.solve()
    bank_indices = tuple( range(1, series+1))
    return [b @ bank_indices for b in X.value ]

