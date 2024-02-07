from typing import List
from batpack import pack_battery
import sys
import re
import fileinput

def main(args:List[str]):
    """
    Main entry point for the batpack command line tool.
    """
    m = None
    if len(args) > 0:
        m = re.match( r'(\d+)[sS](\d+)[pP]', args[0])
    if m:
        series = int(m.group(1))
        parallel = int(m.group(2))
        if len(args) > 1:
            s = " ".join(args[1:])
        else:
            s = " ". join(sys.stdin.readlines())
        cell_capacities = list(map(int, re.split( r'\s*[\s,]\s*' , s.strip())))

        banks = pack_battery(series, parallel, cell_capacities)
        print(banks)
        sums_per_bank = {i:0 for i in range(1, series+1)}
        for i in range(len(cell_capacities)):
            sums_per_bank[banks[i]] += cell_capacities[i]
        
        ideal_bank = round(sum(cell_capacities)/series, 2)
        squared_error_per_bank = {i: round((sums_per_bank[i] - ideal_bank)**2, 2) for i in range(1, series+1)}    
        squared_error_total = round(sum(squared_error_per_bank.values()), 2)
        print(f"Total squared error: {squared_error_total} \n    banks:  {squared_error_per_bank}")
        print(f"Ideal bank size: {ideal_bank} \n    banks:  {sums_per_bank}")
        for i in range(len(cell_capacities)):
            print(f"{banks[i]}\t{cell_capacities[i]}")       
    else:
        print("USAGE: batpack <series>s<parallel>p <cell capacities>")
        return


if __name__ == "__main__":
    main(sys.argv[1:])    
