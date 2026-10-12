#!/usr/bin/env python3
from .inventory import write_inventory_once
from .config import DATA_ROOT, OUTPUT_DIRS
def main():
    for name in OUTPUT_DIRS: (DATA_ROOT / name).mkdir(parents=True, exist_ok=True)
    print(write_inventory_once())
if __name__ == '__main__': main()
