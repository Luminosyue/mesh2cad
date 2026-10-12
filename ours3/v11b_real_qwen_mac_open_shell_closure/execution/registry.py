"""V11B BuilderRegistry; all sources share this single dispatch."""
from __future__ import annotations
from typing import Any
from builders import occ_api
from design_plan.schema import REGISTRY_VERSION
from design_plan.validator import validate_plan
from execution.builders import DISPATCH

def execute(plan:dict[str,Any],eligibility:dict[str,Any],catalog:dict[str,Any],guard_cfg:dict[str,Any],counters:dict[str,int],resolved=None)->dict[str,Any]:
 validation=validate_plan(plan,eligibility,catalog) if resolved is None else {'PLAN_STATUS':'PLAN_EXECUTABLE','PLAN_EXECUTABLE':True,'PLAN_SCHEMA_VALID':True,'PLAN_GEOMETRY_VALID':True,'PLAN_REFERENCE_VALID':True,'resolved':resolved,'builder':resolved.get('builder') or plan.get('builder'),'reasons':[]}
 builder=validation.get('builder') or plan.get('builder')
 if not validation.get('PLAN_EXECUTABLE'):
  counters['INVALID_BUILDER_REQUEST']=counters.get('INVALID_BUILDER_REQUEST',0)+1
  return {'BUILDER_EXECUTED':False,'PLAN_STATUS':validation.get('PLAN_STATUS'),'PLAN_EXECUTABLE':False,'shape':None,'validation':validation,'HISTORICAL_STEP_REUSED':False,'FALLBACK_USED':False,'FRESH_BREP':False,'REGISTRY_VERSION':REGISTRY_VERSION}
 fn=DISPATCH.get(builder)
 if fn is None:return {'BUILDER_EXECUTED':False,'PLAN_STATUS':'PLAN_EXECUTION_FAILED','PLAN_EXECUTABLE':True,'shape':None,'validation':validation,'error':'NO_DISPATCH','HISTORICAL_STEP_REUSED':False,'FALLBACK_USED':False,'FRESH_BREP':False}
 try:
  with occ_api.registry_authorized():result=fn(validation['resolved'],eligibility['part_bbox'],guard_cfg,counters)
 except Exception as exc:return {'BUILDER_EXECUTED':False,'PLAN_STATUS':'PLAN_EXECUTION_FAILED','PLAN_EXECUTABLE':True,'shape':None,'validation':validation,'error':f'{type(exc).__name__}: {exc}','HISTORICAL_STEP_REUSED':False,'FALLBACK_USED':False,'FRESH_BREP':False}
 result.update({'validation':validation,'PLAN_EXECUTABLE':True,'HISTORICAL_STEP_REUSED':False,'FALLBACK_USED':False,'REGISTRY_VERSION':REGISTRY_VERSION,'builder':builder})
 return result
