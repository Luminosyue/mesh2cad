#!/usr/bin/env python3
import json,sys
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/batch_cad_nativeness_recovery_v3');REPO=Path('/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD');sys.path.insert(0,str(REPO))
from multi_agent_cad.config import DS_API_KEY,DS_BASE_URL,SPEC_PLANNER_MODEL
from openai import OpenAI
d={'MAC_CONFIG_PRESENT':bool(DS_API_KEY),'MAC_ENDPOINT_REACHABLE':False,'MAC_HTTP_STATUS':None,'MAC_QUOTA_AVAILABLE':False,'MAC_API_AVAILABLE':False,'probe_type':'CURRENT_STAGE_STRICT_MINIMAL_ENDPOINT_TEST','LLM_CALLS':0}
try:
 r=OpenAI(base_url=DS_BASE_URL,api_key=DS_API_KEY,timeout=30).chat.completions.create(model=SPEC_PLANNER_MODEL,messages=[{'role':'user','content':'Return exactly OK.'}],max_tokens=4,temperature=0);d.update(MAC_ENDPOINT_REACHABLE=True,MAC_HTTP_STATUS=200,MAC_QUOTA_AVAILABLE=True,MAC_API_AVAILABLE=True,LLM_CALLS=1)
except Exception as e:
 s=str(e);status=403 if '403' in s else 401 if '401' in s else None;d.update(MAC_ENDPOINT_REACHABLE=status is not None,MAC_HTTP_STATUS=status,error={'type':type(e).__name__,'message':s})
OUT.joinpath('artifacts').mkdir(parents=True,exist_ok=True);OUT.joinpath('artifacts/mac_endpoint_probe.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
