#!/usr/bin/env python3
import json,os,re,sys,time
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'v8_missing_architecture_completion'
MAC_ROOT=ROOT/'external/Multi-Agent-CAD'
for env_path in (ROOT/'.mac_env',Path('/data/home/cuiyuehan/project/pair_agent/.env')):
 if not env_path.is_file():continue
 for line in env_path.read_text(encoding='utf-8-sig').splitlines():
  if '=' not in line or line.lstrip().startswith('#'):continue
  k,v=line.split('=',1);v=v.strip().strip('"').strip("'")
  if k in ('DASHSCOPE_API_KEY','OPENAI_API_KEY','OPENAI_BASE_URL','OPENAI_API_BASE','TEXT_MODEL') and v and not os.environ.get(k):os.environ[k]=v
 if os.environ.get('DASHSCOPE_API_KEY'):break
sys.path.insert(0,str(MAC_ROOT))
from multi_agent_cad import config
import multi_agent_cad.nodes as nodes
nodes._DS_BASE_URL=os.environ.get('OPENAI_BASE_URL') or os.environ.get('OPENAI_API_BASE') or config.DS_BASE_URL
client=nodes._llm_client();model=os.environ.get('TEXT_MODEL') or config.CODER_MODEL
summary=json.loads((OUT/'artifacts/pretest_summary.json').read_text())
target=summary['grounding'][0]
context={'failure_type':'GEOMETRY_RESIDUAL','target_entity_id':target['occ_entity_id'],'target_semantic':'MAIN_WING_LEADING_EDGE','allowed_program_region':'PARAMETERS.leading_offset','current_parameter':summary['optimization']['final_parameters']['leading_offset'],'pre_repair_metrics':summary['optimization']['final_metrics'],'locality_contract':'Only leading_offset may change. Do not regenerate the part, change builder, topology, feature sequence, or any other parameter.','delta_bounds':[-0.03,0.03]}
system='You are the local repair coder in Multi-Agent-CAD. Return strict JSON only with target_entity_id, parameter, delta, failure_type, rationale. Produce one bounded local CAD program parameter patch. Do not emit a whole-part program and do not alter topology, builder, or feature sequence.'
started=time.time();request_sent=True;path=OUT/'18_targeted_repair/CADPART_001/mac_local_patch.json';path.parent.mkdir(parents=True,exist_ok=True)
try:
 response=client.chat.completions.create(model=model,temperature=0,max_tokens=768,messages=[{'role':'system','content':system},{'role':'user','content':'Choose a local patch for this grounded OCC entity using only the supplied contract:\n'+json.dumps(context)}])
 raw=response.choices[0].message.content;match=re.search(r'\{.*\}',raw,re.S);patch=json.loads(match.group(0)) if match else {}
 record={**patch,'provider_request_sent':request_sent,'provider_response_received':True,'model':model,'elapsed_seconds':time.time()-started,'prompt_tokens':getattr(response.usage,'prompt_tokens',None),'completion_tokens':getattr(response.usage,'completion_tokens',None),'total_tokens':getattr(response.usage,'total_tokens',None),'raw_response':raw,'mac_framework':str(MAC_ROOT),'whole_part_regeneration_requested':False,'allowed_program_region':'PARAMETERS.leading_offset'}
except Exception as exc:
 record={'provider_request_sent':True,'provider_response_received':False,'model':model,'elapsed_seconds':time.time()-started,'mac_framework':str(MAC_ROOT),'whole_part_regeneration_requested':False,'allowed_program_region':'PARAMETERS.leading_offset','target_entity_id':target['occ_entity_id'],'error_type':type(exc).__name__,'error':str(exc),'blocker':'MAC_PROVIDER_FREE_TIER_QUOTA_EXHAUSTED_403' if 'Free quota exhausted' in str(exc) else 'MAC_PROVIDER_ERROR'}
path.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
