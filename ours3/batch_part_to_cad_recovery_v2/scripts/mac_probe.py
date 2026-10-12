#!/usr/bin/env python3
import json,sys,time
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/batch_part_to_cad_recovery_v2')
REPO=Path('/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD');sys.path.insert(0,str(REPO))
from multi_agent_cad.config import DS_API_KEY,DS_BASE_URL,SPEC_PLANNER_MODEL
from openai import OpenAI
result={'MAC_CONFIG_PRESENT':bool(DS_API_KEY),'MAC_ENDPOINT':DS_BASE_URL,'MAC_ENDPOINT_REACHABLE':False,'MAC_HTTP_STATUS':None,'MAC_QUOTA_AVAILABLE':False,'MAC_API_AVAILABLE':False,'error':None,'LLM_CALLS':0,'probe_type':'STRICT_MINIMAL_ENDPOINT_HEALTH_CHECK_NO_MESH'}
try:
 r=OpenAI(base_url=DS_BASE_URL,api_key=DS_API_KEY,timeout=30).chat.completions.create(model=SPEC_PLANNER_MODEL,messages=[{'role':'user','content':'Return exactly OK. This is an endpoint health check; no geometry input is supplied.'}],max_tokens=4,temperature=0)
 result.update({'MAC_ENDPOINT_REACHABLE':True,'MAC_HTTP_STATUS':200,'MAC_QUOTA_AVAILABLE':True,'MAC_API_AVAILABLE':True,'LLM_CALLS':1,'response_received':bool(r.choices)})
except Exception as e:
 s=str(e);status=403 if '403' in s else (401 if '401' in s else None);result.update({'MAC_ENDPOINT_REACHABLE':status is not None,'MAC_HTTP_STATUS':status,'error':{'type':type(e).__name__,'message':s},'MAC_SKIP_REASON':'HTTP_403_QUOTA_EXHAUSTED' if status==403 else 'ENDPOINT_PROBE_FAILED'})
OUT.joinpath('artifacts').mkdir(parents=True,exist_ok=True);OUT.joinpath('artifacts/mac_endpoint_probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
