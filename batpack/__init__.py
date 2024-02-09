from typing import List
import cvxpy as cp
import numpy as np

class Battery:
    def __init__(self, name, series, parallel, cell_capacities) -> None:
        cells_count = series*parallel
        if cells_count != len(cell_capacities): 
            raise ValueError(
                "Series and parallel must match the number of cells.\n"
                f"{series}s{parallel}p -> Cell count: {cells_count} != {len(cell_capacities)} from file\n"
                )
        self.name = name
        self.series = series
        self.parallel = parallel
        self.cell_capacities = cell_capacities                
        self.ideal_bank = round(sum(cell_capacities)/series, 2)

    def __str__(self) -> str:
        return self.name
    
    def pack(self) -> "BatteryPacked":
        trys = (10, 30, 120)
        packed = None
        for time_limit in trys:
            print(f"Trying to pack {self} in {time_limit} seconds")
            banks = pack_battery(self.series, self.parallel, self.cell_capacities, time_limit)
            counts_per_bank = {i: banks.count(i) for i in range(self.series+1)}
            missing = None
            for i in range(0, self.series+1):
                if counts_per_bank[i]  == self.parallel:
                    del counts_per_bank[i]
                elif counts_per_bank[i]  == self.parallel - 1:
                    missing = i
            if counts_per_bank[0] == 1 and len(counts_per_bank) == 2 and counts_per_bank[missing] == self.parallel - 1:
                print(f"Fixing missing in bank {missing} in {banks}")
                banks = [missing if b == 0 else b for b in banks] 
                counts_per_bank[missing] += 1
                counts_per_bank = {0:0}
            if counts_per_bank[0] == 0 and len(counts_per_bank) == 1:
                packed = BatteryPacked(self, banks)
                if packed.good_enough():
                    break
                print(f"Packed battery squared error: {packed.squared_error_total}. May be we can do better...")
            else:
                print(banks)
        return packed

class BatteryPacked:
    def __init__(self, bat:Battery, banks:List[int]) -> None:
        self.bat = bat
        self.banks = banks
        sums_per_bank = {i:0 for i in range(1, bat.series+1)}
        for i in range(len(bat.cell_capacities)):
            sums_per_bank[banks[i]] += bat.cell_capacities[i]
        self.sums_per_bank = sums_per_bank
        self.squared_error_per_bank = {
             i: round((sums_per_bank[i] - bat.ideal_bank)**2, 2) 
             for i in range(1, bat.series+1)}    
        self.squared_error_total = round(sum(self.squared_error_per_bank.values()), 2)
    
    def good_enough(self):
        return self.squared_error_total < 500.
    
    def __str__(self) -> str:
        s = (
            f"=== {self.bat}\n"
            f"Total squared error: {self.squared_error_total} \n    banks:  {self.squared_error_per_bank}\n"
            f"Ideal bank size: {self.bat.ideal_bank} \n    banks:  {self.sums_per_bank}\n"
            )
        for i in range(len(self.bat.cell_capacities)):
            s +=f"{self.banks[i]}\t{self.bat.cell_capacities[i]}\n"       
        return s


def pack_battery(series:int, parallel:int, cell_capacities:List[int], time_limit:int=60):
    """
    Packs a battery with the given parameters.

    series: number of banks in pack
    parallel: number of cells in bank
    cell_capacities: list of cell capacities measured (usually in mAh, but units doesn't 
        matter as long as they are in the same units)
    time_limit: time limit for the solver in seconds
    
    """
    cells_count = series*parallel
    assert cells_count == len(cell_capacities), "Series and parallel must match the number of cells."
    capacities = np.array(cell_capacities)
    
    ideal_pack_size = capacities.sum()/series
    b = np.array(series)
    b.fill(ideal_pack_size)

    X = cp.Variable((cells_count, series), boolean=True) 
    constraints = [
        # X[0][0] == 1,                       # to cut some symmetric solutions out of search space
        cp.sum(X, axis=1) == 1,             # cell could be used only once
        cp.sum(X, axis=0) == parallel,      # each bank has to have that many cells in parallel
        ]
    objective = cp.Minimize( cp.sum_squares(  capacities @ X  - b))
    problem = cp.Problem(objective, constraints)
    
    problem.solve(solver='SCIP',  scip_params={"limits/time":time_limit})

    bank_indices = tuple( range(1, series+1))
    return [int(b @ bank_indices) for b in X.value ]

