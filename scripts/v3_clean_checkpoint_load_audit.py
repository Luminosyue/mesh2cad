#!/usr/bin/env python3
"""Append-only runtime load evidence for frozen V3 clean checkpoints."""
import json,pathlib,sys,gc,torch
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
OUT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/CHECKPOINT_LOAD_AUDIT.json'
cases={'B0':ROOT/'ours3/v3_clean_training_v1/runs/b0_clean/checkpoint_epoch_08','M2':ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1/checkpoint_epoch_15'}
out={}
for arm,p in cases.items():
 try:
  m=core.module.SpatialLMLlamaForCausalLM.from_pretrained(p,torch_dtype=torch.bfloat16,device_map='cpu',local_files_only=True)
  out[arm]={'checkpoint':str(p),'loadable':True,'parameter_count':sum(x.numel() for x in m.parameters()),'adapter_requires_separate_geometry_prefix_adapter_pt':arm=='M2'}
  del m;gc.collect()
 except Exception as e: out[arm]={'checkpoint':str(p),'loadable':False,'error':repr(e)}
OUT.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
