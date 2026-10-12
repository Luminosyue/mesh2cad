"""Real Multi-Agent-CAD planner call and strict output-to-V11 adapter."""
from __future__ import annotations
import json,os,urllib.error,urllib.request
MODEL='qwen3.7-plus-2026-05-26'
def call_mac(part_id,eligibility,catalog,timeout=120,context=None):
 # Read provider config without exposing the key in outputs.
 import sys;sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD')
 from multi_agent_cad import config
 refs=sorted(catalog['entries']);allowed=eligibility['ALLOWED_BUILDERS']
 schema={'plan_version':'V11','part_id':part_id,'construction_family':'<allowed builder>','builder':'<same allowed builder>','builder_eligibility_ref':'BUILDER_ELIGIBILITY.<exact builder>','geometry_refs':{'required_ref_key':'exact catalog ref'},'topology_refs':{},'feature_refs':{},'execution_options':{},'reasoning_summary':'text','confidence':0.0,'CANDIDATE_SOURCE':'MAC_PLAN'}
 roles='Architect evaluates construction family; Geometry maps only authoritative refs; Critic rejects missing/unmeasured refs; Planner returns final JSON.'
 prompt={'workflow':'Architect -> Geometry -> Critic -> Planner','role_contract':roles,'part_id':part_id,'ALLOWED_BUILDERS':allowed,'ALL_ALLOWED_EXACT_REFS':refs,'V11_SCHEMA':schema,'MAC_CONTEXT':context or {},'strict':'Return final Planner JSON only. No CadQuery/OCC/code/STEP. No raw numeric geometry. Exact refs only.'}
 model=getattr(config,'SPEC_PLANNER_MODEL',MODEL);url=str(config.DS_BASE_URL).rstrip('/')+'/chat/completions'
 def invoke(role,instruction,context,max_tokens=900):
  payload={'model':model,'temperature':0,'max_tokens':max_tokens,'messages':[{'role':'system','content':f'You are the Multi-Agent-CAD {role}. {instruction}'},{'role':'user','content':json.dumps(context)}]}
  req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+str(config.DS_API_KEY)})
  with urllib.request.urlopen(req,timeout=timeout) as resp:raw=json.loads(resp.read())
  return raw['choices'][0]['message']['content'],raw.get('usage') or {}
 try:
  architect,ua=invoke('Architect','Choose a construction family from ALLOWED_BUILDERS using only the inventory. Do not produce code or numeric geometry.',prompt)
  geometry,ug=invoke('Geometry','Draft a strict V11 plan using exact reference strings only. Never output OCC/CadQuery/code/STEP or numeric geometry.',{**prompt,'ARCHITECT_OUTPUT':architect})
  critic,uc=invoke('Critic','Audit the draft against V11 schema, exact refs, and allowed builders. List concrete corrections. Never execute geometry.',{**prompt,'ARCHITECT_OUTPUT':architect,'GEOMETRY_OUTPUT':geometry})
  text,up=invoke('Planner','Return exactly one final strict V11 Structured Plan JSON, no markdown or commentary.',{**prompt,'ARCHITECT_OUTPUT':architect,'GEOMETRY_OUTPUT':geometry,'CRITIC_OUTPUT':critic},1200)
  start,end=text.find('{'),text.rfind('}');plan=json.loads(text[start:end+1]) if start>=0 and end>start else {}
  plan.setdefault('CANDIDATE_SOURCE','MAC_PLAN');plan['REAL_MAC_CALL']=True
  return {'ok':True,'plan':plan,'raw':text,'agent_outputs':{'Architect':architect,'Geometry':geometry,'Critic':critic,'Planner':text},'usages':[ua,ug,uc,up],'real_calls':4,'status_code':200,'model':model}
 except urllib.error.HTTPError as exc:return {'ok':False,'external_failure':exc.code==403,'status_code':exc.code,'error':f'HTTPError:{exc.code}','model':model,'real_calls':1}
 except Exception as exc:return {'ok':False,'external_failure':True,'status_code':None,'error':f'{type(exc).__name__}:{exc}','model':model,'real_calls':1}
def fixture_adapter(mac_payload):
 # Adapter never changes refs: it only extracts a final Planner plan envelope.
 plan=mac_payload.get('planner_output') if isinstance(mac_payload,dict) else None
 return dict(plan) if isinstance(plan,dict) else None
