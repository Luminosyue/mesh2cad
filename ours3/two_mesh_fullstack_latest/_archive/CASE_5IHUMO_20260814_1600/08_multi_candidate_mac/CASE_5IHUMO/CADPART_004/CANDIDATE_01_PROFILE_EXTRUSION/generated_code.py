#!/usr/bin/env python3
# case_id: CASE_5IHUMO; part_id: CADPART_004; MAC-selected representation: PROFILE_EXTRUSION
import argparse, subprocess, sys
def main():
    p=argparse.ArgumentParser();p.add_argument("--source-mesh",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    cmd=[sys.executable,"/data/home/cuiyuehan/project/mesh2cad/ours3/two_mesh_fullstack_latest/scripts/runtime.py","--source-mesh",a.source_mesh,"--representation","PROFILE_EXTRUSION","--output",a.output,"--sections","14","--profile-count","12","--tolerance","0.001"]
    raise SystemExit(subprocess.run(cmd,check=False).returncode)
if __name__=="__main__":main()
