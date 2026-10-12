import argparse
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-mesh', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--representation', type=str, default='GLOBAL_LOFT')
    parser.add_argument('--sections', type=int, default=32)
    parser.add_argument('--profile-count', type=int, default=32)
    parser.add_argument('--tolerance', type=float, default=0.14112092)
    args = parser.parse_args()
    subprocess.run(['python3', '/data/home/cuiyuehan/project/mesh2cad/ours3/two_mesh_fullstack_latest/scripts/runtime.py', '--source-mesh', args.source_mesh, '--representation', args.representation, '--output', args.output, '--sections', str(args.sections), '--profile-count', str(args.profile_count), '--tolerance', str(args.tolerance)])