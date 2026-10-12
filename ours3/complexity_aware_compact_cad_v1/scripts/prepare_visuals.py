#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT=Path("/data/home/cuiyuehan/project/mesh2cad/ours3");OUT=ROOT/"complexity_aware_compact_cad_v1"
sys.path.insert(0,str(ROOT/"batch_10_step_quality_audit_v1/scripts"));import audit_batch as audit
CONFIG={
"CASE_03":(OUT/"case03_control",ROOT/"meshes/B003QTD4Y6.obj",{"baseline":ROOT/"batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/reconstructed.step","occ":ROOT/"batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/reconstructed.step","ours":ROOT/"batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/reconstructed.step"},ROOT/"batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/CADPART_000/local_to_global_transform.json"),
"CASE_04":(OUT/"case04",ROOT/"meshes/ALPHABET_AZ_GRADIENT.obj",{"baseline":ROOT/"batch_real_mesh2cad_v1/cases/CASE_04/cad_recovery/reconstructed.step","occ":OUT/"case04/candidates/occ_unify.step","ours":OUT/"case04/compact_balanced.step"},ROOT/"batch_real_mesh2cad_v1/cases/CASE_04/cad_recovery/CADPART_000/local_to_global_transform.json"),
"CASE_05":(OUT/"case05",ROOT/"meshes/ASSORTED_VEGETABLE_SET.obj",{"baseline":ROOT/"case05_residual_part003_recovery_v3/assembly/CASE_05_full_cad_assembly_v3.step","occ":OUT/"case05/candidates/occ_unify.step","ours":OUT/"case05/compact_balanced.step"},None),
"CASE_09":(OUT/"case09",ROOT/"meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj",{"baseline":ROOT/"batch_real_mesh2cad_v1/cases/CASE_09/cad_recovery/reconstructed.step","occ":OUT/"case09/candidates/occ_unify.step","ours":OUT/"case09/compact_balanced.step"},ROOT/"batch_real_mesh2cad_v1/cases/CASE_09/cad_recovery/CADPART_000/local_to_global_transform.json")}

def mat(path):
    return np.eye(4) if path is None else np.asarray(json.loads(path.read_text())["CANONICAL_TO_SOURCE"],float)
def apply(v,M):return np.asarray(v)@M[:3,:3].T+M[:3,3]
for cid,(d,source,steps,ledger) in CONFIG.items():
    cache=d/"visual_cache";cache.mkdir(parents=True,exist_ok=True);mesh=trimesh.load(source,force="mesh",process=False);np.savez_compressed(cache/"source.npz",vertices=np.asarray(mesh.vertices),faces=np.asarray(mesh.faces));M=mat(ledger)
    for label,step in steps.items():
        ok,roots,shape=audit.fresh_read(step);topo=audit.topology_audit(shape);t=audit.tessellate(shape,topo["BBOX_DIAGONAL"]);ep,el,take=audit.edge_render_cache(shape,topo["EDGE_COUNT"],topo["BBOX_DIAGONAL"])
        np.savez_compressed(cache/f"{label}.npz",vertices=apply(t["vertices"],M),faces=t["faces"],face_ids=t["face_ids"],edge_points=apply(ep,M),edge_lengths=el)
        print(f"VISUAL_CACHE={cid}:{label} TRI={len(t['faces'])} EDGES={take}",flush=True)
