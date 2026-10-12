import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--source-mesh', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
args = parser.parse_args()

subprocess.run(['python3', '/data/home/cuiyuehan/project/mesh2cad/ours3/two_mesh_fullstack_latest/scripts/runtime.py', '--source-mesh', args.source_mesh, '--representation', 'GLOBAL_LOFT', '--output', args.output, '--sections', '32', '--profile-count', '32', '--tolerance', '0.001'])