#!/usr/bin/env python3
# case_id: CASE_5IHUMO; part_id: CADPART_007; MAC-selected representation: SWEEP
import argparse, subprocess, sys
def main():
    p=argparse.ArgumentParser();p.add_argument("--source-mesh",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    cmd=[sys.executable,"/data/home/cuiyuehan/project/mesh2cad/ours3/two_mesh_fullstack_latest/scripts/runtime.py","--source-mesh",a.source_mesh,"--representation","SWEEP","--output",a.output,"--sections","16","--profile-count","14","--tolerance","0.001"]
    raise SystemExit(subprocess.run(cmd,check=False).returncode)
if __name__=="__main__":main()
