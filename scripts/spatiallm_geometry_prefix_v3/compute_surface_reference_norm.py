#!/usr/bin/env python3
"""Estimate the frozen surface-token norm only from the formal V3 train split."""
import json, pathlib, sys
import numpy as np
import torch

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path[:0]=[str(ROOT/'scripts/spatiallm_curve_token_c2_frozen_v2')]
import train_canonical_smoke as core

BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'
DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/data/pilot_1k_train.json'

def main():
 out=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/norm_reference_v1'
 out.mkdir(parents=True,exist_ok=False)
 rows=json.loads(DATA.read_text())['records']
 device=torch.device('cuda:0')
 core.heldout_geometry.install()
 plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
 model=core.module.SpatialLMLlamaForCausalLM.from_pretrained(BASE,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True).eval()
 for p in list(model.point_backbone.parameters())+list(model.point_proj.parameters()):p.requires_grad_(False)
 vals=[]
 with torch.no_grad():
  for i,row in enumerate(rows,1):
   surface,_=plugin._load_cad_separate_edge(row['surface_input'])
   x=torch.tensor(surface,device=device)
   y=model.forward_point_cloud(x,device,torch.bfloat16,projector=model.point_proj)
   vals.extend(y.float().norm(dim=-1).flatten().cpu().tolist())
   if i%100==0:print(f'{i}/{len(rows)}',flush=True)
 report={'split':'pilot_1k_train','samples':len(rows),'surface_token_norm_count':len(vals),'mean':float(np.mean(vals)),'median':float(np.median(vals)),'p10':float(np.percentile(vals,10)),'p90':float(np.percentile(vals,90)),'official_test_read':False,'training_started':False}
 (out/'SURFACE_REFERENCE_NORM.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
