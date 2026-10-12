# part_id: CADPART_006
import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Generate CAD candidate for HYBRID_ANALYTIC_PATTERN")
    parser.add_argument("--source-mesh", required=True, help="Path to the source high-poly OBJ mesh")
    parser.add_argument("--output", required=True, help="Path to the output CAD file")
    args = parser.parse_args()

    cmd = [
        "python3", '/data/home/cuiyuehan/project/mesh2cad/ours3/case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py',
        "--source-mesh", args.source_mesh,
        "--representation", "HYBRID_ANALYTIC_PATTERN",
        "--output", args.output,
        "--sections", "61",
        "--profile-count", "61",
        "--tolerance", "0.001"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    print(result.stdout)

if __name__ == "__main__":
    main()