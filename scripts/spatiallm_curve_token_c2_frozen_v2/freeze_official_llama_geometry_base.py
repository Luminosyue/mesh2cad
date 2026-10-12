#!/usr/bin/env python3
"""Materialize and freeze OFFICIAL_LLAMA_GEOMETRY_BASE_V1 exactly once."""
from __future__ import annotations
import hashlib, json, pathlib, sys
import torch

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(ROOT/'scripts/spatiallm_curve_token_c2_frozen_v2'))
import train_canonical_pilot as pilot

OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'

def state_hash(model):
 h=hashlib.sha256(); n=0
 for k,t in sorted(model.state_dict().items()):
  if k.startswith(('point_backbone.','point_proj.','edge_proj.')): continue
  x=t.detach().cpu().contiguous()
  h.update(k.encode()+b'\0');h.update(str(tuple(x.shape)).encode()+b'\0');h.update(str(x.dtype).encode()+b'\0')
  h.update(x.view(torch.uint8).numpy().tobytes());n+=1
 return h.hexdigest(),n

def file_sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def main():
 if OUT.exists():raise FileExistsError(f'refusing overwrite: {OUT}')
 OUT.mkdir(parents=True,exist_ok=False)
 model,prov=pilot.make_official_model('b0',torch.device('cpu'))
 llm_hash,llm_tensors=state_hash(model)
 tok=pilot.AutoTokenizer.from_pretrained(pilot.TOKENIZER_BASE,local_files_only=True,use_fast=False)
 model.save_pretrained(OUT,safe_serialization=True,max_shard_size='2GB');tok.save_pretrained(OUT)
 contract={
  'contract':'OFFICIAL_LLAMA_GEOMETRY_BASE_V1','status':'FROZEN','parent_for_arms':['B0','B1-BM','M2-C2-BM'],
  'llm':{'name':'Llama-3.2-1B-Instruct','source_sha256':prov['official_model_sha256'],'trainable_in_children':True,'state_sha256':llm_hash,'state_tensor_count':llm_tensors},
  'geometry_frontend':{'sonata':{'source':'SpatialLM1.1-Llama-1B','frozen':True},'surface_projector':{'source':'SpatialLM1.1-Llama-1B','frozen':True}},
  'spatiallm_llm_tensors_loaded':0,
  'marker_contract':{'point_start':128011,'point_end':128012,'point_pad':128013,'vocab_size':128256,'embedding_rows_added':0},
  'initialization_provenance':prov,'files':{}
 }
 for p in sorted(OUT.iterdir()):
  if p.is_file() and p.name!='BASE_CONTRACT.json':contract['files'][p.name]={'size':p.stat().st_size,'sha256':file_sha(p)}
 (OUT/'BASE_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')
 print(json.dumps({k:v for k,v in contract.items() if k!='files'},indent=2))

if __name__=='__main__':main()
