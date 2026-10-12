#!/usr/bin/env python3
"""Serially continue B1 and M2 4096 decode after B0 PASS on GPU 1."""
from __future__ import annotations
import json,pathlib,subprocess,time,os
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/official_parent_v1'
SCRIPT=ROOT/'scripts/spatiallm_curve_token_c2_frozen_v2/decode_canonical_pilot.py'
def wait_pass(report):
 while True:
  if report.exists():
   d=json.loads(report.read_text())
   if d.get('status')=='PASS' and d.get('completed')==200:return
  time.sleep(30)
def run(arm,run_name,out_name,log_name):
 out=BASE/'decodes_4096'/out_name
 if out.exists():raise FileExistsError(out)
 cmd=['python3',str(SCRIPT),'--arm',arm,'--run',str(BASE/'runs'/run_name),'--output',str(out),'--device','cuda:0','--max-new-tokens','4096']
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='1')
 with (BASE/'decode_logs'/log_name).open('w') as log:
  result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise SystemExit(f'{arm} decode failed: {result.returncode}')
 wait_pass(out/'DECODE_REPORT.json')
wait_pass(BASE/'decodes_4096/b0_best_e03/DECODE_REPORT.json')
run('b1','b1_bm','b1_best_e03','b1_4096.log')
run('m2','m2_c2_bm','m2_best_e03','m2_4096.log')
(BASE/'decodes_4096/QUEUE_COMPLETE').write_text('PASS\n')
