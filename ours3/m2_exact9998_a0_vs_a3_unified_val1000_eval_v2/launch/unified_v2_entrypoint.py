#!/usr/bin/env python3
import json,os,runpy,signal,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); OUT=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2'; T=120
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
variant=sys.argv[sys.argv.index('--variant')+1]
if variant in ('j2','j2o','j2p'):
 os.environ.update(CAD_USE_SEPARATE_EDGE_TOKENS='1',CAD_SECOND_STREAM='curve_tokens',REQUIRE_CURVE_TOKEN_REGISTRY='1',CURVE_TOKEN_REGISTRY=str(ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'))
 from spatiallm_curve_token_v1 import curve_token_injector; curve_token_injector.install()
 import torch,spatiallm
 from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer
 from transformers.modeling_utils import load_sharded_checkpoint
 from spatiallm.tuner.framework.patcher import _attach_edge_projector
 from separate_edge_tokens_v1 import common
 def strict_load(checkpoint,separate_edge=True,device='cuda',dtype=torch.float32,freeze_sonata=True):
  m=AutoModelForCausalLM.from_config(AutoConfig.from_pretrained(str(checkpoint)),torch_dtype=dtype);_attach_edge_projector(m)
  inc=load_sharded_checkpoint(m,str(checkpoint),strict=False,prefer_safe=True)
  alias=(list(inc.missing_keys)==['lm_head.weight'] and m.config.tie_word_embeddings and m.lm_head.weight.data_ptr()==m.model.embed_tokens.weight.data_ptr())
  if (inc.missing_keys and not alias) or inc.unexpected_keys:raise RuntimeError(str(inc))
  m.to(device);m.set_point_backbone_dtype(torch.float32)
  if freeze_sonata:
   for p in m.point_backbone.parameters():p.requires_grad_(False)
  return m,AutoTokenizer.from_pretrained(str(checkpoint))
 common.load_model=strict_load
import geometry_pack_v1.decode_joint_j0_j2 as dec
def exec_v2(code,out_dir):
 from edge_aware_cad_planner_v1.cad_dsl import parse_dsl
 out_dir.mkdir(parents=True,exist_ok=True); dsl=out_dir/'pred.dsl'; dsl.write_text(code if code.endswith('\n') else code+'\n')
 try:parse_dsl(code)
 except Exception as e:return {'parsed':False,'step_ok':False,'error':f'parse: {e}','failure_reason':'PARSE_FAIL','exec_timeout':False}
 result=out_dir/'v2_worker_result.json'; result.unlink(missing_ok=True)
 cmd=['/data/miniconda3/envs/spatiallm/bin/python',str(OUT/'launch/v2_exec_worker.py'),'--dsl',str(dsl),'--out',str(out_dir),'--result',str(result)]
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
 try:stdout,stderr=p.communicate(timeout=T)
 except subprocess.TimeoutExpired:
  os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  return {'parsed':True,'step_ok':False,'error':f'execution exceeded {T}s','failure_reason':'EXEC_TIMEOUT','exec_timeout':True,'execution_timeout_seconds':T}
 if p.returncode or not result.exists():return {'parsed':True,'step_ok':False,'error':(stderr or stdout)[-400:],'failure_reason':'EXEC_EXCEPTION','exec_timeout':False}
 r=json.loads(result.read_text());r['exec_timeout']=False
 if not r.get('step_ok') and 'failure_reason' not in r:r['failure_reason']='STEP_EXPORT_FAIL'
 return r
dec._exec_step=exec_v2
raise SystemExit(dec.main())
