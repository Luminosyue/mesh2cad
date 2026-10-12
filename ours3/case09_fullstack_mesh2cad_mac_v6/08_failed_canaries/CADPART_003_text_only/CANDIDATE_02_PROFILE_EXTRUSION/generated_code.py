import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Generate CAD candidate via V6 runtime.')
    parser.add_argument('--source-mesh', required=True, help='Path to the source OBJ mesh.')
    parser.add_argument('--output', required=True, help='Path to the output CAD file.')
    args = parser.parse_args()

    cmd = [
        'python3', '/data/home/cuiyuehan/project/mesh2cad/ours3/case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py',
        '--source-mesh', args.source_mesh,
        '--representation', 'PROFILE_EXTRUSION',
        '--output', args.output,
        '--sections', '64',
        '--profile-count', '128',
        '--tolerance', '0.001'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error: {result.stderr}', file=sys.stderr)
        sys.exit(result.returncode)
    print(result.stdout)

if __name__ == '__main__':
    main()
