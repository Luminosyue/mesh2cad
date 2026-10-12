#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))
from run_airplane_routeb_v2 import main as run_main


if __name__ == "__main__":
    # reuse airplane runner with only-stage1
    sys.argv = [sys.argv[0], "--only-stage1", *sys.argv[1:]]
    raise SystemExit(run_main())
