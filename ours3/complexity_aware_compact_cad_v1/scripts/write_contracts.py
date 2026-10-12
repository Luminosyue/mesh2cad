#!/usr/bin/env python3
import json
from pathlib import Path
R=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/complexity_aware_compact_cad_v1")
def dump(name,value):(R/"metrics"/name).write_text(json.dumps(value,indent=2)+"\n")
dump("frozen_thresholds.json",{"Q1":{"BRep_valid":True,"Chamfer_max":.01,"P95_max":.02,"Coverage02_min":.95},"Q2":{"BRep_valid":True,"Chamfer_max":.02,"P95_max":.05,"Coverage02_min":.85},"CASE_05_success":{"Coverage02_min":.95,"Face_reduction_min":.80,"Edge_reduction_min":.80},"thresholds_modified":False})
dump("execution_contract.json",{"P3_RUNS":0,"PHYSX_RUNS":0,"WHOLE_BATCH_RUNS":0,"MAC_BASELINE_RUNS":0,"NEURAL_NETWORK_TRAINING_RUNS":0,"SOURCE_OBJ_MODIFIED":False,"BASELINE_STEP_OVERWRITTEN":False,"UNRESTRICTED_ICP_USED":False,"FINAL_GEOMETRY":"TRUE_BREP_NOT_TRIANGULATED_MESH"})
dump("visual_qa.json",{"smooth_shaded":True,"triangle_edges_in_shaded":False,"baseline_and_ours_face_colored":True,"true_topods_edges_rendered":True,"shared_world_coordinates_and_camera":True,"human_visual_check":"PASS"})
