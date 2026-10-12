#!/usr/bin/env python3
"""Isolated, bounded B0/M2 TRAIN_SELF_DECODE diagnostic.

No training, no checkpoint writes, no optimizer.  It is deliberately separate
from the active legacy runner and labels all results as train-self diagnostics.
"""
from __future__ import annotations
import argparse,ast,json,pathlib,re,sys,tempfile,types
import numpy as np, torch
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
from geometry_prefix_adapter import GeometryPrefixAdapter
from transformers import AutoTokenizer
DATA=ROOT/'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'; OUTROOT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2'
EOS=(128001,128008,128009); MAX_NEW=4096
def enc(tok,r,arm):
 user=core.markers(arm)+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
 pre='<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+user+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n';p=tok.encode(pre,add_special_tokens=False);t=tok.encode(pathlib.Path(r['target_dsl']).read_text()+'<|eot_id|>',add_special_tokens=False)
 s=int(r['clean_contract']['actual_surface_tokens']); extra=(s-1)+(0 if arm=='b0' else 7); t=t[:4096-extra-len(p)]
 return torch.tensor([p+t]),len(p)
def install(model,arm,state): return core.install_precomputed_second(model,arm,state)
def safe_parse(text,hit):
 if hit:return False,'PARSER_SKIPPED_HIT_CAP'
 if len(text)>12000:return False,'PARSER_SKIPPED_OVERSIZE'
 depth=0
 for c in text:
  if c in '([{':depth+=1
  elif c in ')]}':depth-=1
  if abs(depth)>256:return False,'PARSER_SKIPPED_DEEP_NESTING'
 try: ast.parse(text);return True,None
 except (SyntaxError,ValueError,MemoryError,RecursionError) as e:return False,type(e).__name__
def stage_exec(text,row,work):
 r={'exec':False,'step_write':False,'step_reload':False}
 try:
  # Register the module before execution: placement_v3 uses dataclasses whose
  # type resolution requires the module to be present in sys.modules.
  spec=__import__('importlib').util.spec_from_file_location('cad',ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py');m=__import__('importlib').util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
  clean=m.extract_dsl_code(text);m.parse_dsl(clean)
  with tempfile.TemporaryDirectory(dir=work) as d:
   d=pathlib.Path(d);step=d/'x.step';stl=d/'x.stl';m.execute_dsl(clean,step,stl);r['exec']=True;r['step_write']=step.exists() and stl.exists()
   if r['step_write']:
    import cadquery as cq;cq.importers.importStep(str(step));r['step_reload']=True
 except Exception as e:r['error']=f'{type(e).__name__}: {e}'[-500:]
 return r
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','m2'],required=True);ap.add_argument('--checkpoint',type=pathlib.Path,required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--n',type=int,default=20);ap.add_argument('--tag',default='');a=ap.parse_args();suffix=('_'+a.tag) if a.tag else '';out=OUTROOT/f'{a.arm}_train_self_diag_{a.checkpoint.name}{suffix}';out.mkdir(parents=True,exist_ok=False);work=out/'tmp';work.mkdir()
 rows=json.loads(DATA.read_text())['records']; order=sorted(rows,key=lambda r:__import__('hashlib').sha256(r['cad_id'].encode()).hexdigest())[:a.n]
 core.heldout_geometry.install();dev=torch.device(a.device);tok=AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False)
 model=core.module.SpatialLMLlamaForCausalLM.from_pretrained(a.checkpoint,torch_dtype=torch.bfloat16,device_map=dev,local_files_only=True)
 if a.arm=='m2':
  model.edge_proj=GeometryPrefixAdapter(256,model.config.hidden_size,target_norm=1.9414176940917969).to(device=dev,dtype=torch.bfloat16);model.edge_proj.load_state_dict(torch.load(a.checkpoint/'geometry_prefix_adapter.pt',map_location=dev));model.config.separate_edge_tokens=True;model.separate_edge_tokens=True
 else:model.edge_proj=None
 model.config.use_cache=True;model.gradient_checkpointing_disable();model.eval();state={};orig=install(model,a.arm,state);plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);per=[]
 try:
  with torch.no_grad():
   for i,r in enumerate(order,1):
    ids,prompt=enc(tok,r,a.arm);pids=ids[:,:prompt].to(dev);surface,_=plugin._load_cad_separate_edge(r['surface_input']);surface=torch.tensor(surface,device=dev).unsqueeze(0);second,mask=core.second_input(r,a.arm);state['raw_mask']=mask;edge=None if second is None else second.to(dev).unsqueeze(0)
    gen=model.generate(input_ids=pids,attention_mask=torch.ones_like(pids),point_clouds=surface,edge_clouds=edge,max_new_tokens=MAX_NEW,do_sample=False,use_cache=True,eos_token_id=list(EOS),pad_token_id=128001)
    new=gen[0,pids.shape[1]:].cpu();text=tok.decode(new,skip_special_tokens=True);hit=int(new.numel()>=MAX_NEW);eos=bool(new.numel() and int(new[-1]) in EOS);parse,why=safe_parse(text,hit);stage=stage_exec(text,r,work) if parse else {'exec':False,'step_write':False,'step_reload':False,'error':why}
    fail='STEP_RELOAD_PASS' if stage['step_reload'] else ('STEP_WRITE_FAIL' if stage['exec'] else ('EXEC_FAIL' if parse else why))
    per.append({'cad_id':r['cad_id'],'generated_tokens':int(new.numel()),'eos':eos,'hit_cap':bool(hit),'has_result':bool(re.search(r'(?m)^\s*result\s*=',text)),'parse':parse,**stage,'failure_stage':fail,'generated_text':text})
    print(a.arm,i,'/',len(order),r['cad_id'],fail,flush=True)
 finally: core.module._splice_geometry=orig
 (out/'per_sample.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in per));
 keys=('eos','has_result','parse','exec','step_write','step_reload','hit_cap');summary={'arm':a.arm,'checkpoint':str(a.checkpoint),'N':len(per),'MAX_NEW_TOKENS':MAX_NEW,'protocol':'TRAIN_SELF_DECODE only, not held-out','counts':{k:sum(x.get(k,False) for x in per) for k in keys},'failure_stages':dict(__import__('collections').Counter(x['failure_stage'] for x in per))};(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
