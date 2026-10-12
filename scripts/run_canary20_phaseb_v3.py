#!/usr/bin/env python3
"""Phase-B actual V3 M2 aggregation, Sonata count, and splice-label audit."""
from __future__ import annotations
import json,sys,torch,numpy as np
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); OUT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool/canary20';sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
from geometry_prefix_adapter import GeometryPrefixAdapter
from transformers import AutoTokenizer
CK=ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1/checkpoint_epoch_15'; LIMIT=4096; DEV=torch.device('cuda:1')
def prompt(tok,arm):
 u=core.markers(arm)+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...';s='<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+u+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n';return tok.encode(s,add_special_tokens=False)
def main():
 rows=[json.loads(x) for x in (OUT/'CANARY20_PER_CAD_PHASEA.jsonl').read_text().splitlines() if x]; core.heldout_geometry.install();tok=AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False);plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
 model=core.make_model('m2',DEV,1.9414176940917969);model.edge_proj.load_state_dict(torch.load(CK/'geometry_prefix_adapter.pt',map_location=DEV));model.eval();state={};orig=core.install_precomputed_second(model,'m2',state);out=[]
 try:
  for r in rows:
   sid=r['cad_id'].split('__',1)[1];base=OUT/r['dataset']/sid;gp=base/'geometry_pack_v1'/sid;c2=np.load(base/'curve_tokens/curve_tokens.npy');surf,_=plugin._load_cad_separate_edge(str(gp/'surface_points.npy'));st=torch.tensor(surf,device=DEV).unsqueeze(0)
   # Actual frozen Sonata path; no count estimate.
   with torch.no_grad(): S=int(model.forward_point_cloud(st,DEV,torch.bfloat16,projector=model.point_proj).shape[1])
   raw=np.zeros((128,256),np.float32);k=min(len(c2),128);raw[:k]=c2[:k];state['raw_mask']=torch.tensor([True]*k+[False]*(128-k));edge=torch.tensor(raw,device=DEV).unsqueeze(0)
   # Invoke the actual trained GeometryPrefixAdapter, not a replacement pooling rule.
   with torch.no_grad(): summary,smask=model.edge_proj(edge,state['raw_mask'].to(DEV).unsqueeze(0)); summary_ok=summary.shape==(1,8,model.config.hidden_size) and bool(torch.isfinite(summary).all()) and int(smask.sum())==8
   dsl=(gp/'cad_target.dsl').read_text(); p0=prompt(tok,'b0');p2=prompt(tok,'m2');target=tok.encode(dsl+'<|eot_id|>',add_special_tokens=False); eos=tok.convert_tokens_to_ids('<|eot_id|>'); b0=len(p0)+(S-1)+len(target);m2=len(p2)+(S-1)+7+len(target)
   # Actual multimodal call reaches the production splice/labels path with full target+EOS.
   result={'cad_id':r['cad_id'],'surface_token_count':S,'curve_count':int(len(c2)),'curve_summary_shape':list(summary.shape),'curve_summary_valid':bool(summary_ok),'dsl_tokens':len(target),'eos_supervised':bool(target and target[-1]==eos),'b0_real_seq_len':b0,'m2_real_seq_len':m2,'b0_context_pass':b0<=LIMIT,'m2_context_pass':m2<=LIMIT,'v3_encode_b0':False,'v3_encode_m2':False}
   try:
    for arm,ids,second in [('b0',p0,None),('m2',p2,edge)]:
     state['raw_mask']=torch.tensor([] if arm=='b0' else [True]*k+[False]*(128-k)); labels=torch.tensor([[-100]*len(ids)+target],device=DEV); inp=torch.tensor([ids+target],device=DEV); pc=st
     with torch.no_grad():z=model(input_ids=inp,attention_mask=torch.ones_like(inp),labels=labels,point_clouds=pc,edge_clouds=second if arm=='m2' else None)
     result['v3_encode_'+arm]=bool(torch.isfinite(z.loss))
   except Exception as e:result['splice_error']=repr(e)[-500:]
   result['clean_status']='CLEAN_PASS' if all([result['curve_summary_valid'],result['eos_supervised'],result['b0_context_pass'],result['m2_context_pass'],result['v3_encode_b0'],result['v3_encode_m2']]) else 'CLEAN_REJECT';out.append({**r,**result});print(r['cad_id'],result['clean_status'],flush=True)
 finally:core.module._splice_geometry=orig
 (OUT/'CANARY20_PER_CAD.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in out));print(json.dumps({'clean':sum(x['clean_status']=='CLEAN_PASS' for x in out),'n':len(out)},indent=2))
if __name__=='__main__':main()
