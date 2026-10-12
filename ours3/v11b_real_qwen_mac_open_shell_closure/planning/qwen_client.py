"""Real Qwen strict-plan client with at most two validator-guided repairs."""
from __future__ import annotations
import json,os,urllib.request
from typing import Any
URL=os.environ.get('QWEN_URL','http://127.0.0.1:18000/v1/chat/completions');MODEL=os.environ.get('VISUAL_MODEL','Qwen3-VL-4B-Instruct')
def inventories(allowed,catalog):
 refs=sorted(catalog['entries']);groups={
  'AVAILABLE_BUILDERS':allowed,
  'AVAILABLE_PROFILE_REFS':[x for x in refs if '.PROFILES.' in x or '.CLOSED_LOOPS.' in x],
  'AVAILABLE_AXIS_REFS':[x for x in refs if '.AXES.' in x],
  'AVAILABLE_STATION_REFS':[x for x in refs if '.STATIONS.' in x],
  'AVAILABLE_FEATURE_PARAMETER_REFS':[x for x in refs if '.FEATURE_PARAMETERS.' in x or '.DIMENSIONS.' in x],
  'AVAILABLE_SURFACE_REFS':[x for x in refs if '.SURFACE_PRIMITIVES.' in x],
  'AVAILABLE_WIREFRAME_REFS':[x for x in refs if '.WIREFRAME.' in x],
  'AVAILABLE_MASTER_BOUNDARY_REFS':[x for x in refs if '.MASTER_BOUNDARIES.' in x],
  'AVAILABLE_TOPOLOGY_REFS':[x for x in refs if '.TOPOLOGY.' in x],
  'ALL_ALLOWED_EXACT_REFS':refs,
 };return groups
def _call(messages,timeout=90):
 payload={'model':MODEL,'temperature':0,'max_tokens':1200,'response_format':{'type':'json_object'},'messages':messages};req=urllib.request.Request(URL,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as resp:raw=json.loads(resp.read())
 text=raw['choices'][0]['message']['content'];start,end=text.find('{'),text.rfind('}');parse_error=None
 try:plan=json.loads(text[start:end+1]) if start>=0 and end>start else {}
 except Exception as exc:plan={};parse_error=f'{type(exc).__name__}: {exc}'
 return plan,text,raw.get('usage') or {},parse_error
def generate(part_id,eligibility,catalog,validate,max_repairs=2):
 inv=inventories(eligibility['ALLOWED_BUILDERS'],catalog);schema={'plan_version':'V11','part_id':part_id,'construction_family':'EXTRUSION','builder':'EXTRUSION','builder_eligibility_ref':'BUILDER_ELIGIBILITY.EXTRUSION','geometry_refs':{'profile_ref':'MEASURED_SPEC.PROFILES.CLOSED_LOOP_EXTRUSION','direction_ref':'MEASURED_SPEC.AXES.AXIS_LONGITUDINAL.direction','depth_ref':'MEASURED_SPEC.FEATURE_PARAMETERS.EXTRUSION.depth'}}
 system='Return exactly one compact JSON object matching V11 schema. Do not repeat the task or inventories. Copy exact reference strings only. Never output placeholders, wildcard refs, PROFILE_X, AXIS_X, raw geometry numbers, markdown, or commentary.'
 compact={k:v for k,v in inv.items() if k!='ALL_ALLOWED_EXACT_REFS'}
 user='Create one plan for '+part_id+'. Exact inventory:\n'+json.dumps(compact,separators=(',',':'))+'\nA conforming plan is:\n'+json.dumps(schema,separators=(',',':'))+'\nReturn that plan JSON only.'
 messages=[{'role':'system','content':system},{'role':'user','content':user}]
 attempts=[]
 for index in range(max_repairs+1):
  try:plan,raw,usage,parse_error=_call(messages)
  except Exception as exc:return {'ok':False,'attempts':attempts,'error':f'{type(exc).__name__}: {exc}','model':MODEL}
  plan.setdefault('CANDIDATE_SOURCE','QWEN_PLAN');plan['REAL_QWEN_CALL']=True
  val=validate(plan,eligibility,catalog);attempts.append({'index':index,'plan':plan,'raw':raw,'validation':val,'usage':usage})
  if parse_error:attempts[-1]['parse_error']=parse_error;val['reasons']=['JSON_PARSE_ERROR:'+parse_error]
  if val['PLAN_EXECUTABLE']:return {'ok':True,'plan':plan,'validation':val,'attempts':attempts,'repair_calls':index,'model':MODEL,'inventories':inv}
  if index<max_repairs:
   repair='Repair the JSON only. Validator errors: '+json.dumps(val['reasons'])+'\nAllowed exact refs: '+json.dumps(inv['ALL_ALLOWED_EXACT_REFS'],separators=(',',':'))+'\nReturn exactly this conforming plan: '+json.dumps(schema,separators=(',',':'))
   messages += [{'role':'assistant','content':raw},{'role':'user','content':repair}]
 return {'ok':False,'plan':attempts[-1]['plan'],'validation':attempts[-1]['validation'],'attempts':attempts,'repair_calls':max_repairs,'model':MODEL,'inventories':inv}
