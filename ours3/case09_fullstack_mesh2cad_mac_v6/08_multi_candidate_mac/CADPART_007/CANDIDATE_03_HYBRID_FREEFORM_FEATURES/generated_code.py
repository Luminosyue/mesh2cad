# part_id: CADPART_007
import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Generate CAD model using V6 runtime.")
    parser.add_argument("--source-mesh", required=True, help="Path to the source mesh OBJ.")
    parser.add_argument("--output", required=True, help="Path to the output CAD file.")
    
    args = parser.parse_args()
    
    representation = "HYBRID_FREEFORM_FEATURES"
    sections = 64
    profile_count = 32
    tolerance = 0.001
    
    cmd = [
        "python3", '/data/home/cuiyuehan/project/mesh2cad/ours3/case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py',
        "--source-mesh", args.source_mesh,
        "--representation", representation,
        "--output", args.output,
        "--sections", str(sections),
        "--profile-count", str(profile_count),
        "--tolerance", str(tolerance)
    ]
    
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
