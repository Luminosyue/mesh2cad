# part_id: CADPART_004
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Generate CAD part via V6 runtime.')
    parser.add_argument('--source-mesh', required=True, help='Path to the source OBJ mesh.')
    parser.add_argument('--output', required=True, help='Path to the output file.')
    args = parser.parse_args()

    cmd = [
        'python3', '/data/home/cuiyuehan/project/mesh2cad/ours3/case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py',
        '--source-mesh', args.source_mesh,
        '--representation', 'PROFILE_EXTRUSION',
        '--output', args.output,
        '--sections', '64',
        '--profile-count', '1',
        '--tolerance', '0.001'
    ]

    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    main()
