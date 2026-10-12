import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='CADPART_002 MAIN_WING_RIGHT Reconstruction')
    parser.add_argument('--source-mesh', required=True, help='Path to the source OBJ mesh')
    parser.add_argument('--output', required=True, help='Path to the output file')
    args = parser.parse_args()

    cmd = [
        'python3', '/data/home/cuiyuehan/project/mesh2cad/ours3/case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py',
        '--source-mesh', args.source_mesh,
        '--representation', 'HYBRID_SKIN_CAPS',
        '--output', args.output,
        '--sections', '64',
        '--profile-count', '64',
        '--tolerance', '0.001'
    ]
    
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    main()
