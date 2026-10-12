#!/usr/bin/env python3
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs,STEPControl_Writer
from contracts.evidence_authority import BUILDER_CONTRACT,validate_requested_parameters
from builders.registry import get_builder

def load(path):return json.loads(Path(path).read_text())
def dump(path,value):Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(value,indent=2)+'\n')
def execute(measured_spec,construction_plan,output_step,source_mesh=None):
    spec=load(measured_spec);plan=load(construction_plan);requested=validate_requested_parameters(plan,spec)
    if plan.get("part_id")!=spec.get("part_id"):raise ValueError("CONTRACT_VIOLATION part_id mismatch")
    profiles=spec["profiles"][:requested]
    if not all(p.get("closed") and p.get("source")=="HIGH_POLY_MESH_SECTION" for p in profiles):raise ValueError("PROFILE_INVALID")
    builder=get_builder(plan["hypothesis"]);shape=builder.build(spec,profiles,plan)
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():raise RuntimeError("invalid candidate BRep")
    out=Path(output_step);out.parent.mkdir(parents=True,exist_ok=True);w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs)
    if w.Write(str(out))!=IFSelect_RetDone:raise RuntimeError("STEP_EXPORT_FAILED")
    contract={"candidate_id":plan["candidate_id"],"requested_hypothesis":plan["hypothesis"],"executed_builder":builder.name,
      "axis_source":"MEASURED_SPEC","station_source":"MEASURED_SPEC","profile_source":"GEOMETRY_ANALYZER",
      "requested_profile_count":requested,"executed_profile_count":len(profiles),"runtime_remeasurement":False,
      "runtime_override_count":0,"runtime_clamp_count":0,"historical_geometry_reused":False,
      "requested_parameters":{"profile_count":{"requested":requested,"executed":len(profiles),"modified":False}},
      "hypothesis_builder_match":BUILDER_CONTRACT[plan["hypothesis"]]==builder.name}
    trace={"part_id":spec["part_id"],"geometry_analysis_file":spec["geometry_analysis_file"],"measured_spec_file":str(Path(measured_spec).resolve()),
      "construction_plan_file":str(Path(construction_plan).resolve()),"candidate_program":plan.get("candidate_program"),"runtime_builder":builder.name,
      "axis":{"value":spec["axis"],"source":"MEASURED_SPEC"},"stations":{"value":spec["stations"],"source":"MEASURED_SPEC"},
      "profiles":{"count":len(profiles),"source":"GEOMETRY_ANALYZER"},"runtime_remeasurements":[],"runtime_overrides":[]}
    dump(out.parent/"candidate_execution_contract.json",contract);dump(out.parent/"geometry_trace.json",trace)
    print("AXIS_SOURCE=MEASURED_SPEC");print("STATION_SOURCE=MEASURED_SPEC");print("PROFILE_SOURCE=GEOMETRY_ANALYZER");print(f"EXECUTED_BUILDER={builder.name}")
    return contract,trace
def main():
    p=argparse.ArgumentParser();p.add_argument("--source-mesh");p.add_argument("--measured-spec",required=True);p.add_argument("--construction-plan",required=True);p.add_argument("--output",required=True);a=p.parse_args();execute(a.measured_spec,a.construction_plan,a.output,a.source_mesh)
if __name__=="__main__":main()
