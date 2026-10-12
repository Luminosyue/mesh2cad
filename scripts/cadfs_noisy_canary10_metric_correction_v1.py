#!/usr/bin/env python3
"""Correct only the normal-deviation statistic for the completed Noise Canary10.

The original report compared normals on independently sampled surface points,
which is not a correspondence-based normal-deviation measure.  This writes a
separate correction artifact and never overwrites the original evidence.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/cadfs_noisy_overfit100_v1/noise_canary10'
sys.path[:0]=[str(ROOT/'scripts')]
from geometry_pack_v1.surface import face_normals

def vertex_normals(v,f):
 t=v[f];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ans=np.zeros_like(v,dtype=np.float64)
 for j in range(3):np.add.at(ans,f[:,j],cross)
 q=np.linalg.norm(ans,axis=1,keepdims=True)
 return np.divide(ans,q,out=np.zeros_like(ans),where=q>1e-18)

def main():
 rows=json.loads((OUT/'audits/NOISE_CANARY10_RECORDS.json').read_text())['records'];out={'purpose':'correspondence-based vertex-normal deviation correction; original independent-sample normal field statistic is not interpreted','levels':{}}
 for lev in ('N1','N2','N3'):
  vals=[]
  for r in rows:
   f=np.load(r['faces_path']);a=vertex_normals(np.load(r['levels']['N0']['vertices_path']),f);b=vertex_normals(np.load(r['levels'][lev]['vertices_path']),f)
   angle=np.degrees(np.arccos(np.clip((a*b).sum(1),-1,1))); vals.append({'cad_id':r['cad_id'],'mean_deg':float(angle.mean()),'median_deg':float(np.median(angle)),'p95_deg':float(np.percentile(angle,95))})
  a=np.asarray([x['mean_deg'] for x in vals]);out['levels'][lev]={'per_cad':vals,'mean_angle_deg':{'min':float(a.min()),'median':float(np.median(a)),'p90':float(np.percentile(a,90)),'max':float(a.max())}}
 (OUT/'audits/NOISE_CANARY10_NORMAL_METRIC_CORRECTION_V1.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
