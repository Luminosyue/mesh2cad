#!/usr/bin/env python3
"""Run one 100-step smoke arm exclusively from OFFICIAL_LLAMA_GEOMETRY_BASE_V1."""
from __future__ import annotations
import hashlib,json,pathlib,sys
import torch

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
CODE=ROOT/'scripts/spatiallm_curve_token_c2_frozen_v2';sys.path.insert(0,str(CODE))
import train_canonical_smoke as core

BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'
EXPECTED=json.loads((BASE/'BASE_CONTRACT.json').read_text())['llm']['state_sha256']

def llm_hash(model):
 h=hashlib.sha256()
 for k,t in sorted(model.state_dict().items()):
  if k.startswith(('point_backbone.','point_proj.','edge_proj.')):continue
  x=t.detach().cpu().contiguous();h.update(k.encode()+b'\0');h.update(str(tuple(x.shape)).encode()+b'\0');h.update(str(x.dtype).encode()+b'\0');h.update(x.view(torch.uint8).numpy().tobytes())
 return h.hexdigest()

def file_sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def normal_text_gate(tok):
 marker={128011,128012,128013};bad=[]
 rows=core.load_records('train')+core.load_records('val')
 instruction='Generate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
 for r in rows:
  text=instruction+'\n'+pathlib.Path(r['target_dsl']).read_text()
  hit=marker.intersection(tok.encode(text,add_special_tokens=False))
  if hit:bad.append({'cad_id':r['cad_id'],'ids':sorted(hit)})
 return bad

def main():
 if '--output' not in sys.argv:raise SystemExit('--output required')
 out=pathlib.Path(sys.argv[sys.argv.index('--output')+1])
 arm=sys.argv[sys.argv.index('--arm')+1]
 core.BASE_MODEL=BASE
 original=core.make_model
 def checked_make_model(selected_arm,device):
  model=original(selected_arm,device);actual=llm_hash(model)
  if actual!=EXPECTED:raise RuntimeError(f'initial LLM hash mismatch {actual} != {EXPECTED}')
  out.mkdir(parents=True,exist_ok=True)
  (out/'PRE_OPTIMIZER_CONTRACT.json').write_text(json.dumps({'arm':arm,'parent_contract':'OFFICIAL_LLAMA_GEOMETRY_BASE_V1','initial_llm_hash':actual,'expected_llm_hash':EXPECTED,'match':True,'optimizer_steps_at_measurement':0},indent=2)+'\n')
  return model
 core.make_model=checked_make_model
 tok=core.AutoTokenizer.from_pretrained(BASE,local_files_only=True,use_fast=False)
 bad=normal_text_gate(tok)
 if bad:raise RuntimeError(f'normal text uses geometry IDs: {bad[:3]}')
 core.main()
 report_path=out/'SMOKE_REPORT.json';report=json.loads(report_path.read_text())
 report.update({
  'parent_contract':'OFFICIAL_LLAMA_GEOMETRY_BASE_V1','initial_llm_hash':EXPECTED,
  'normal_text_uses_geometry_marker_ids':False,'normal_text_checked_records':240,
  'point_pad_attention':0 if arm!='b0' and report.get('entry_budget_failures')==0 else None,
  'smoke_train_sha256':file_sha(core.DATA/'pilot_smoke_train.json'),
  'smoke_val_sha256':file_sha(core.DATA/'pilot_smoke_val.json'),
  'official_llama_geometry_interface_adaptation':{'first20_mean':report.get('first20_mean'),'last20_mean':report.get('last20_mean'),'val_loss':report.get('post_val_loss_48'),'train_loss_down':report.get('loss_trend_down')},
 })
 report_path.write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
