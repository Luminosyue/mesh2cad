#!/usr/bin/env python3
import argparse, hashlib, json, os, sys
from pathlib import Path
import torch

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v1'
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'SpatialLM'),str(ROOT/'scripts/separate_edge_tokens_v1')]
ap=argparse.ArgumentParser(); ap.add_argument('--arm',choices=['a0','a3'],required=True); a=ap.parse_args()
is_a3=a.arm=='a3'
ck=ROOT/('ours3/m2_exact9998_corrected_m2_train_v1/runs/m2/checkpoint-6000' if is_a3 else 'ours3/m2_exact9998_b0_m2_train_v1/runs/b0/checkpoint-6000')
if is_a3:
 os.environ.update(CAD_USE_SEPARATE_EDGE_TOKENS='1',CAD_SECOND_STREAM='curve_tokens',REQUIRE_CURVE_TOKEN_REGISTRY='1',CURVE_TOKEN_REGISTRY=str(ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'))
 from spatiallm_curve_token_v1 import curve_token_injector
 curve_token_injector.install()
import spatiallm
from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer
from transformers.modeling_utils import load_sharded_checkpoint
from spatiallm.tuner.framework.patcher import _attach_edge_projector
if is_a3:
 config=AutoConfig.from_pretrained(str(ck))
 model=AutoModelForCausalLM.from_config(config,torch_dtype=torch.bfloat16)
 _attach_edge_projector(model)
 incompatible=load_sharded_checkpoint(model,str(ck),strict=False,prefer_safe=True)
 raw_missing=list(incompatible.missing_keys)
 tied_alias_ok=(raw_missing==['lm_head.weight'] and model.config.tie_word_embeddings and model.lm_head.weight.data_ptr()==model.model.embed_tokens.weight.data_ptr())
 missing=[] if tied_alias_ok else raw_missing; unexpected=list(incompatible.unexpected_keys); mismatched=[]
else:
 model,info=AutoModelForCausalLM.from_pretrained(str(ck),torch_dtype=torch.bfloat16,output_loading_info=True)
 missing=info.get('missing_keys',[]); unexpected=info.get('unexpected_keys',[]); mismatched=info.get('mismatched_keys',[])
strict=(not missing and not unexpected and not mismatched)
model.cuda().eval(); model.set_point_backbone_dtype(torch.float32)
for p in model.parameters():p.requires_grad_(False)
tok=AutoTokenizer.from_pretrained(str(ck))
from separate_edge_tokens_v1.common import make_plugin,build_prompt,set_deterministic_serialization
set_deterministic_serialization(model.point_backbone); plugin=make_plugin(separate_edge=is_a3)
records=json.loads((ROOT/'ours3/exact9998_v1/exact9998_val.json').read_text())[:5]
calls=[]; hooks=[]
if is_a3:
 def hook(mod,inp,out):calls.append({'input_shape':list(inp[0].shape),'output_shape':list(out.shape)})
 hooks.append(model.edge_proj.register_forward_hook(hook))
before=hashlib.sha256(b''.join(x.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes() for x in model.edge_proj.state_dict().values())).hexdigest() if is_a3 else None
with torch.inference_mode():
 for r in records:
  p=ROOT/'cad_spatial_dataset'/r['point_clouds'][0]
  if is_a3:s,e=plugin._load_cad_separate_edge(str(p))
  else:s=plugin._load_cad_npy(str(p));e=None
  ids=tok.apply_chat_template([{'role':'user','content':build_prompt(separate_edge=is_a3)}],add_generation_prompt=True,return_tensors='pt').cuda()
  kw={'input_ids':ids,'attention_mask':torch.ones_like(ids),'point_clouds':torch.as_tensor(s[None],dtype=torch.float32,device='cuda'),'use_cache':False}
  if is_a3:kw['edge_clouds']=torch.as_tensor(e[None],dtype=torch.float32,device='cuda')
  out=model(**kw); assert torch.isfinite(out.logits).all()
  if is_a3: calls[-1].update(cad_id=r['id'],K=int(e.shape[0]),logits_finite=True)
for h in hooks:h.remove()
after=hashlib.sha256(b''.join(x.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes() for x in model.edge_proj.state_dict().values())).hexdigest() if is_a3 else None
rep={'arm':a.arm,'checkpoint':str(ck),'FRESH_LOAD':'YES','STRICT_RELOAD':'PASS' if strict else 'FAIL','missing_keys':missing,'unexpected_keys':unexpected,'mismatched_keys':mismatched,'eval_mode':not model.training,'optimizer_steps':0}
if is_a3:
 rep.update(PROJECTOR_CALLED='YES' if len(calls)==5 else 'NO',CURVE_TOKENS_SPLICED='YES' if all(c['input_shape'][-1]==256 and c['output_shape'][-1]==2048 for c in calls) else 'NO',PROJECTOR_KEYS=len(model.edge_proj.state_dict()),PROJECTOR_PARAM_N=sum(p.numel() for p in model.edge_proj.parameters()),C2_FROZEN='YES',projector_hash_before=before,projector_hash_after=after,PROJECTOR_CHANGED='NO' if before==after else 'YES',cases=calls)
(OUT/'audits'/f'{a.arm.upper()}_PREFLIGHT.json').write_text(json.dumps(rep,indent=2,default=str)+'\n')
print(json.dumps(rep,indent=2,default=str))
if not strict:raise SystemExit(2)
if is_a3 and not (rep['PROJECTOR_CALLED']=='YES' and rep['CURVE_TOKENS_SPLICED']=='YES' and rep['PROJECTOR_KEYS']==4 and rep['PROJECTOR_PARAM_N']==592128 and before==after):raise SystemExit(3)
