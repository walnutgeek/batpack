from pathlib import Path
from typing import List
from batpack import Battery, BatteryPacked
import sys
import re
import fileinput


def main(args:List[str]):
    """
    Main entry point for the batpack command line tool.
    """
    print_help = False
    try:
        if len(args) != 1:
            raise ValueError("one file argument is required")
        f = Path(args[0])
        if not f.exists():
            raise ValueError(f"file {f} does not exist")
        cell_capacities = list(map(int, re.split( r'\s*[\s,]\s*' , f.read_text().strip())))
        m = re.match( r'(\d+)[sS](\d+)[pP]_.*', f.stem)
        if not m:
            raise ValueError(f"file {f} does not match the battery pack spec like 3s10p_...")
        bat = Battery(f.stem, int(m.group(1)), int(m.group(2)), cell_capacities)
        packed = bat.pack()
        if not packed:
            print(f"Failed to pack battery {f.stem}")
        else:
            print(packed)            
    except Exception as e: 
        print(e)
        print_help = True       
    if print_help:
        print("batpack - optimally allocate cells into banks within battery pack\n"
              "Script takes single argument - path to a file with cell capacities, named \n"
              "starting with battery pack spec following with underscore and then whatever.\n\n"
              "Example: batpack test/3s10p_bp8.txt")


if __name__ == "__main__":
    main(sys.argv[1:])    
