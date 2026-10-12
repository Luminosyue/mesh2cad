import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Generate CAD model for CADPART_006")
    parser.add_argument("--source-mesh", required=True, help="Path to the source OBJ mesh")
    parser.add_argument("--output", required=True, help="Path to the output STEP file")
    args = parser.parse_args()

    representation = "REVOLVE_HUB_LOFT_BLADE"
    sections = 60
    profile_count = 12
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
