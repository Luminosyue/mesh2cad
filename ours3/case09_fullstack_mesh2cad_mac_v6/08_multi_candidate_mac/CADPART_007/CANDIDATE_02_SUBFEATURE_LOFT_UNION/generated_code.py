# part_id: CADPART_007
import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Generate CAD model using V6 runtime.")
    parser.add_argument("--source-mesh", required=True, help="Path to the source mesh OBJ file.")
    parser.add_argument("--output", required=True, help="Path to the output CAD file.")
    args = parser.parse_args()

    cmd = [
        "python3", '/data/home/cuiyuehan/project/mesh2cad/ours3/case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py',
        "--source-mesh", args.source_mesh,
        "--representation", "SUBFEATURE_LOFT_UNION",
        "--output", args.output,
        "--sections", "64",
        "--profile-count", "16",
        "--tolerance", "0.0005"
    ]
    
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()