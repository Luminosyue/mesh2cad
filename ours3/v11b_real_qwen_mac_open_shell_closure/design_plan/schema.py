"""V11B Structured CAD Plan schema; all geometry is exact catalog references."""
from __future__ import annotations
import re
from typing import Any

PLAN_VERSION="V11"
VALIDATOR_VERSION="V11B.1"
RESOLVER_VERSION="V11B.1"
REGISTRY_VERSION="V11B.1"
REF_GRAMMAR=re.compile(r"^(MEASURED_SPEC|BUILDER_ELIGIBILITY)(\.[A-Za-z][A-Za-z0-9_]*)+$")
ALLOWED_PLAN_KEYS={"plan_version","part_id","construction_family","builder","builder_eligibility_ref","geometry_refs","topology_refs","feature_refs","execution_options","reasoning_summary","confidence","CANDIDATE_SOURCE","candidate_source","hypothesis_id","REAL_QWEN_CALL","REAL_MAC_CALL"}
REQUIRED_PLAN_KEYS={"plan_version","part_id","construction_family","builder","builder_eligibility_ref","geometry_refs"}
HYPERPARAM_KEYS={"occ_tolerance","max_degree","optimizer_iterations","sample_count"}
NAKED_GEOMETRY_TOKENS=("length","radius","axis","station","depth","angle","transform","control_point","profile_coordinate","origin","normal","direction","height","grid","coordinate")
BUILDER_REQUIRED_REFS={
 "PLANE":["origin_ref","normal_ref","support_ref"],
 "EXTRUSION":["profile_ref","direction_ref","depth_ref"],
 "REVOLUTION":["profile_ref","axis_origin_ref","axis_direction_ref","angle_ref"],
 "LOFT":["profile_refs","station_refs","correspondence_ref"],
 "SWEEP":["section_profile_ref","spine_ref","frame_policy_ref"],
 "CYLINDER":["axis_ref","radius_ref","height_ref"],
 "GENERAL_BSPLINE":["surface_grid_ref","support_ref","parameterization_ref"],
 "PERIODIC_BSPLINE":["periodic_surface_grid_ref","periodic_direction_ref","support_ref"],
 "OPEN_SHELL":["surface_refs","master_boundary_refs","wireframe_refs","topology_refs"],
}
REF_EXPECTED_TYPE={
 "origin_ref":"point","normal_ref":"vector","support_ref":"support","profile_ref":"profile","profile_refs":"profile_list","direction_ref":"vector","depth_ref":"scalar","axis_origin_ref":"point","axis_direction_ref":"vector","angle_ref":"scalar","station_refs":"scalar_list","correspondence_ref":"correspondence","section_profile_ref":"profile","spine_ref":"profile","frame_policy_ref":"frame_policy","axis_ref":"axis","radius_ref":"scalar","height_ref":"scalar","surface_grid_ref":"grid","parameterization_ref":"parameterization","periodic_surface_grid_ref":"grid","periodic_direction_ref":"vector","surface_refs":"topology_list","master_boundary_refs":"topology_list","wireframe_refs":"topology_list","topology_refs":"topology_list",
}
EXPECTED_FRAME="SOURCE_GLOBAL"
def is_ref(value:Any)->bool:return isinstance(value,str) and bool(REF_GRAMMAR.match(value))
def walk_naked_numbers(obj:Any,path:list[str]|None=None)->list[dict[str,Any]]:
 path=path or [];found=[]
 if isinstance(obj,dict):
  for key,val in obj.items():
   low=str(key).lower()
   if key in {"reasoning_summary","execution_options"}:continue
   if str(key).endswith("_ref") or str(key).endswith("_refs"):continue
   if any(token in low for token in NAKED_GEOMETRY_TOKENS) and isinstance(val,(int,float,list)):found.append({"path":path+[str(key)],"value":val,"key":str(key)})
   else:found.extend(walk_naked_numbers(val,path+[str(key)]))
 elif isinstance(obj,list):
  for i,val in enumerate(obj):found.extend(walk_naked_numbers(val,path+[str(i)]))
 return found
