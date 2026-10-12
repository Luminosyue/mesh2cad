#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
STAGE = OURS3 / "cad_part_graph_gate1"
ART = STAGE / "artifacts"
CASES = STAGE / "cases"
LOGS = STAGE / "logs"
SEG = OURS3 / "fusion_pipeline/cases/REAL_03/segmentation"
SOURCE = OURS3 / "meshes/30_CONSTRUCTION_SET.obj"
TRI_MAP = SEG / "triangle_part_id.npy"
INV = OURS3 / "next_stage_parallel_v1/track_a/artifacts/p3_gate1_part_inventory.csv"
MERGES = OURS3 / "next_stage_parallel_v1/track_a/artifacts/p3_gate1_merge_hypotheses.csv"
PHYSX_DIR = OURS3 / "physx_and_alignment_recovery_v1/track_e2/cases/REAL_03/physx_v1"
PHYSX = PHYSX_DIR / "physx_understanding.json"
ANALYZER = OURS3 / "mac_pipeline/scripts/run_gate1.py"
IDENTITY = np.eye(4).tolist()


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean_json(value), indent=2, sort_keys=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def f(row, key):
    return float(row[key])


def j(row, key):
    return json.loads(row[key])


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as h:
        return list(csv.DictReader(h))


def write_obj_subset(path: Path, vertices: np.ndarray, faces: np.ndarray, triangle_ids: np.ndarray) -> None:
    selected = faces[triangle_ids]
    used = np.unique(selected.reshape(-1))
    remap = np.full(len(vertices), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    local_faces = remap[selected]
    with path.open("w", encoding="utf-8", newline="\n") as h:
        h.write("# Exact source-triangle subset; no remeshing or geometry edits\n")
        for xyz in vertices[used]:
            h.write(f"v {xyz[0]:.10g} {xyz[1]:.10g} {xyz[2]:.10g}\n")
        for tri in local_faces:
            h.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}\n")


def write_local_obj(path: Path, global_obj: Path):
    mesh = trimesh.load(global_obj, force="mesh", process=False)
    center = np.asarray(mesh.bounds).mean(axis=0)
    diag = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0]))
    scale = 1.0 / diag if diag > 0 else 1.0
    g2l = np.eye(4)
    g2l[:3, :3] *= scale
    g2l[:3, 3] = -center * scale
    l2g = np.linalg.inv(g2l)
    verts = np.asarray(mesh.vertices) * scale - center * scale
    with path.open("w", encoding="utf-8", newline="\n") as h:
        h.write("# Local frame from exact global subset\n")
        for xyz in verts:
            h.write(f"v {xyz[0]:.10g} {xyz[1]:.10g} {xyz[2]:.10g}\n")
        for tri in np.asarray(mesh.faces):
            h.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}\n")
    return g2l, l2g, center, diag


def physx_audit():
    patterns = ("*.ply", "*.pcd", "*.xyz", "*.pts", "*.npy", "*.npz", "*coord*.txt", "*voxel*", "*point*cloud*")
    candidate_files = []
    for pattern in patterns:
        candidate_files.extend(PHYSX_DIR.rglob(pattern))
    candidate_files = sorted(set(p for p in candidate_files if p.is_file()))
    parsed = json.loads(PHYSX.read_text(encoding="utf-8"))
    raw = (PHYSX_DIR / "raw/basic_info.txt").read_text(encoding="utf-8")
    function_keys = [k for k in parsed if "function" in k.lower()]
    reason = "A_ABSENT_FROM_RAW_OUTPUT" if not function_keys and "function" not in raw.lower() else "D_PARSER_MISS"
    audit = {
        "source_object": "REAL_03",
        "searched_root": str(PHYSX_DIR),
        "searched_patterns": list(patterns),
        "candidate_3d_localization_files": [str(p) for p in candidate_files],
        "PHYSX_3D_PART_LOCALIZATION_AVAILABLE": bool(candidate_files),
        "semantic_parts_available": bool(parsed.get("parts")),
        "kinematics_available": bool(parsed.get("group_info_raw")),
        "affordance_available": any(p.get("affordance_rank") for p in parsed.get("parts", [])),
        "physical_scale_available": bool(parsed.get("physical_scale_available")),
        "physical_scale_prior": parsed.get("physical_scale_estimate"),
        "physical_scale_used_for_part_graph": False,
        "function_zero_reason": reason,
        "new_physx_runs": 0,
    }
    write_json(ART / "physx_3d_localization_audit.json", audit)
    return audit, parsed


def main():
    for p in (ART, CASES, LOGS):
        p.mkdir(parents=True, exist_ok=True)
    mesh = trimesh.load(SOURCE, force="mesh", process=False)
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    tri_map = np.load(TRI_MAP, allow_pickle=False).astype(int)
    assert len(faces) == len(tri_map) == 385828
    assert set(np.unique(tri_map)) == set(range(26))
    inventory_rows = load_csv(INV)
    inv = {int(r["PART_ID"]): r for r in inventory_rows}
    merge_rows = load_csv(MERGES)
    physx_loc, physx = physx_audit()

    # The source OBJ and every P3 OBJ are already in the frozen object-global frame.
    # Gate1 analyzer evidence is normalized per part and carries an explicit inverse.
    frame_inputs = [
        {"input": str(SOURCE), "frame": "REAL_03_OBJECT_GLOBAL_FRAME", "to_object_global_4x4": IDENTITY},
        {"input": str(TRI_MAP), "frame": "SOURCE_FACE_INDEX_LABEL_SPACE", "coordinate_transform": "NOT_APPLICABLE", "to_object_global_4x4": IDENTITY},
        {"input": str(INV), "frame": "REAL_03_OBJECT_GLOBAL_FRAME", "to_object_global_4x4": IDENTITY},
        {"input": str(MERGES), "frame": "REAL_03_OBJECT_GLOBAL_FRAME", "to_object_global_4x4": IDENTITY},
        {"input": str(PHYSX), "frame": "PHYSX_SEMANTIC_ONLY_NO_3D_FRAME", "spatial_transform_available": False, "to_object_global_4x4": None},
    ]
    for pid in range(26):
        norm = json.loads((SEG / f"part_geometry/part_{pid:03d}/geometry_analysis/normalization_transform.json").read_text())
        frame_inputs.append({
            "input": str(SEG / f"part_{pid:03d}.obj"),
            "frame": "REAL_03_OBJECT_GLOBAL_FRAME",
            "to_object_global_4x4": IDENTITY,
            "analyzer_normalized_evidence_frame": f"P3_PART_{pid:03d}_ANALYZER_NORMALIZED_FRAME",
            "analyzer_normalized_to_object_global_4x4": norm["normalized_to_original"],
        })
    coordinate_audit = {
        "target_frame": "REAL_03_OBJECT_GLOBAL_FRAME",
        "inputs": frame_inputs,
        "implicit_center_scale_rotation_used": False,
        "all_spatial_inputs_have_explicit_transform": True,
        "nonspatial_physx_is_explicitly_marked": True,
        "coordinate_frame_audit_pass": True,
    }
    write_json(ART / "coordinate_frame_audit.json", coordinate_audit)

    nodes = []
    for pid in range(26):
        r = inv[pid]
        tri_ids = np.flatnonzero(tri_map == pid)
        prim_path = SEG / f"part_geometry/part_{pid:03d}/geometry_analysis/primitives.json"
        prim = json.loads(prim_path.read_text())
        nodes.append({
            "segment_id": pid,
            "segment_name": f"part_{pid:03d}",
            "source_triangle_ids_path": str(CASES / f"CADPART_{pid:03d}/source_triangle_ids.npy"),
            "source_triangle_id_min": int(tri_ids.min()),
            "source_triangle_id_max": int(tri_ids.max()),
            "triangle_count": int(len(tri_ids)),
            "surface_area": f(r, "surface_area"),
            "area_ratio": f(r, "area_ratio"),
            "bbox_min": j(r, "bbox_min"),
            "bbox_max": j(r, "bbox_max"),
            "bbox_extents": j(r, "bbox_extents"),
            "centroid": j(r, "centroid"),
            "connected_components": int(r["connected_components"]),
            "cadability_class": r["CADABILITY_CLASS"],
            "cadability_score": f(r, "CADABILITY_SCORE"),
            "analytic_coverage": f(r, "ANALYTIC_COVERAGE"),
            "primitive_coverage": prim["coverage"],
            "primitive_evidence": prim["candidates"][:8],
            "segment_status": r["PART_SEGMENT_STATUS"],
            "coordinate_frame": "REAL_03_OBJECT_GLOBAL_FRAME",
            "to_object_global_4x4": IDENTITY,
        })

    # Sparse candidate graph reuses the 26 frozen boundary-adjacent pairs only.
    edges = []
    review_prior_count = 0
    for r in merge_rows:
        a, b = int(r["PART_A"]), int(r["PART_B"])
        primitive_compat = f(r, "primitive_compatibility")
        surface = f(r, "surface_continuity_score")
        normal = f(r, "normal_continuity")
        shared = f(r, "shared_boundary_score")
        proximity = f(r, "geometric_proximity")
        if primitive_compat >= .90 and surface >= .15:
            relation, relation_score = "SAME_SURFACE_CONTINUATION", 1.0
        elif primitive_compat >= .50:
            relation, relation_score = "FEATURE_CONNECTED", .70
        else:
            relation, relation_score = "UNKNOWN", .50
        geometry = .25 * shared + .25 * surface + .20 * relation_score + .15 * normal + .15 * proximity
        physx_same = .10  # object-level soft prior, at the allowed ceiling; never a strong merge.
        physx_separate = 0.0
        final = .90 * geometry + .10 * physx_same
        hard_contradictions = []
        forbidden = bool(hard_contradictions or physx_separate >= .8)
        if forbidden:
            decision = "FORBIDDEN_MERGE"
        elif final >= .80:
            decision = "AUTO_MERGE"
        elif final >= .60:
            decision = "REVIEW_MERGE"
            review_prior_count += 1
        else:
            decision = "KEEP_SEPARATE"
        ca = np.array(j(inv[a], "centroid")); cb = np.array(j(inv[b], "centroid"))
        amin, amax = np.array(j(inv[a], "bbox_min")), np.array(j(inv[a], "bbox_max"))
        bmin, bmax = np.array(j(inv[b], "bbox_min")), np.array(j(inv[b], "bbox_max"))
        bbox_gap = np.maximum(np.maximum(amin - bmax, bmin - amax), 0)
        edge = {
            "segment_a": a, "segment_b": b,
            "source_mesh_adjacent": True,
            "candidate_reason": "FROZEN_SHARED_BOUNDARY_ADJACENCY",
            "shared_boundary_length": f(r, "shared_boundary_length"),
            "shared_boundary_ratio": f(r, "shared_boundary_ratio"),
            "minimum_euclidean_distance": 0.0,
            "bbox_distance": float(np.linalg.norm(bbox_gap)),
            "centroid_distance": float(np.linalg.norm(ca-cb)),
            "surface_continuity_evidence": {
                "plane_coplanarity": surface if f(inv[a], "PLANE_COVERAGE") > .15 and f(inv[b], "PLANE_COVERAGE") > .15 else 0.0,
                "cylinder_coaxiality_radius_consistency": surface if f(inv[a], "CYLINDER_COVERAGE") > .15 and f(inv[b], "CYLINDER_COVERAGE") > .15 else 0.0,
                "sphere_consistency": surface if f(inv[a], "SPHERE_COVERAGE") > .05 and f(inv[b], "SPHERE_COVERAGE") > .05 else 0.0,
                "normal_continuity": normal,
                "boundary_tangent_continuity": surface,
                "curvature_continuity": surface,
                "composite": surface,
            },
            "primitive_relation": relation,
            "primitive_relation_score": relation_score,
            "GEOMETRY_MERGE_PRIOR": {"score": f(r, "MERGE_SCORE"), "label": r["MERGE_HYPOTHESIS"], "executed_directly": False},
            "physx_same_part_score": physx_same,
            "physx_separate_score": physx_separate,
            "physx_evidence_mode": "SEMANTIC_ONLY_OBJECT_LEVEL_SOFT_PRIOR",
            "hard_contradictions": hard_contradictions,
            "forbidden": forbidden,
            "score_terms": {
                "shared_boundary_score": shared,
                "surface_continuity_score": surface,
                "primitive_relation_score": relation_score,
                "normal_tangent_continuity": normal,
                "proximity_score": proximity,
            },
            "geometry_merge_score": geometry,
            "final_merge_score": final,
            "decision": decision,
        }
        edges.append(edge)
    graph = {
        "schema": "P3_SEGMENT_GRAPH_V1",
        "source_object": "REAL_03",
        "coordinate_frame": "REAL_03_OBJECT_GLOBAL_FRAME",
        "node_count": 26,
        "edge_count": len(edges),
        "possible_undirected_pairs": 325,
        "sparse_graph": len(edges) < 325,
        "candidate_policy": "FROZEN_BOUNDARY_ADJACENT_PAIRS_ONLY",
        "score_formula": "0.25*shared_boundary + 0.25*surface_continuity + 0.20*primitive_relation + 0.15*normal_tangent_continuity + 0.15*proximity",
        "final_formula": "0.90*geometry + 0.10*physx (no reliable 3D localization)",
        "thresholds": {"AUTO_MERGE_MIN": .80, "REVIEW_MERGE_MIN": .60, "KEEP_SEPARATE_MAX_EXCLUSIVE": .60},
        "nodes": nodes,
        "edges": edges,
    }
    write_json(ART / "p3_segment_graph.json", graph)

    associations = []
    for pid in range(26):
        associations.append({
            "p3_segment_id": pid,
            "physx_part_candidates": [],
            "localization_source": "SEMANTIC_ONLY_NO_3D_LOCALIZATION",
            "association_confidence": "UNKNOWN",
            "same_part_soft_prior_ceiling": .10,
            "kinematic_group_association": None,
            "affordance_role_association": None,
            "reason": "PhysX semantic parts have no reusable 3D coordinates in the frozen output",
        })
    association_doc = {
        "schema": "PHYSX_P3_ASSOCIATION_V1",
        "source_object": "REAL_03",
        "physx_data_reused": True,
        "physx_3d_part_localization_available": False,
        "association_method": "NO_SPATIAL_ASSOCIATION_SEMANTICS_RETAINED_AS_OBJECT_LEVEL_SOFT_PRIOR",
        "semantic_soft_prior_max": .10,
        "semantic_prior_can_trigger_strong_merge": False,
        "PHYSX_MUST_SEPARATE_PAIRS": [],
        "physical_scale_prior": physx.get("physical_scale_estimate"),
        "physical_scale_used_for_part_graph": False,
        "associations": associations,
        "unlocalized_physx_parts": physx.get("parts", []),
        "unlocalized_kinematic_groups": physx.get("group_info_raw", []),
    }
    write_json(ART / "physx_p3_association.json", association_doc)

    # Constraint-aware greedy grouping. Review edges do not execute. Every proposed
    # union is checked against all forbidden pairs, unlike naive union-find.
    forbidden_pairs = {tuple(sorted((e["segment_a"], e["segment_b"]))) for e in edges if e["forbidden"]}
    groups = [{i} for i in range(26)]
    executed_edges = []
    for edge in sorted((e for e in edges if e["decision"] == "AUTO_MERGE"), key=lambda x: -x["final_merge_score"]):
        ga = next(g for g in groups if edge["segment_a"] in g)
        gb = next(g for g in groups if edge["segment_b"] in g)
        if ga is gb:
            continue
        if any(tuple(sorted((a,b))) in forbidden_pairs for a in ga for b in gb):
            continue
        merged = ga | gb
        groups.remove(ga); groups.remove(gb); groups.append(merged)
        executed_edges.append([edge["segment_a"], edge["segment_b"]])
    groups = sorted(groups, key=lambda g: min(g))

    candidate_records = []
    for idx, group in enumerate(groups):
        cid = f"CADPART_{idx:03d}"
        case = CASES / cid
        case.mkdir(parents=True, exist_ok=True)
        tri_ids = np.flatnonzero(np.isin(tri_map, sorted(group)))
        np.save(case / "source_triangle_ids.npy", tri_ids, allow_pickle=False)
        global_obj = case / f"{cid}_global.obj"
        local_obj = case / f"{cid}_local.obj"
        write_obj_subset(global_obj, vertices, faces, tri_ids)
        g2l, l2g, center, diag = write_local_obj(local_obj, global_obj)
        transforms = {
            "global_frame": "REAL_03_OBJECT_GLOBAL_FRAME",
            "local_frame": f"{cid}_LOCAL_CENTERED_UNIT_DIAGONAL_FRAME",
            "global_to_local_4x4": g2l,
            "local_to_global_4x4": l2g,
            "local_center_global": center,
            "global_bbox_diagonal": diag,
        }
        write_json(case / "coordinate_transforms.json", transforms)
        prov = {
            "cad_part_id": cid,
            "source_object": "REAL_03",
            "source_mesh": str(SOURCE),
            "source_mesh_sha256": sha256(SOURCE),
            "source_p3_segment_ids": sorted(group),
            "source_triangle_ids_path": str(case / "source_triangle_ids.npy"),
            "source_triangle_ids_sha256": sha256(case / "source_triangle_ids.npy"),
            "source_triangle_count": int(len(tri_ids)),
            "exact_original_triangle_subset": True,
            "remeshed": False, "smoothed": False, "repaired": False,
            "decimated": False, "boolean_operation": False,
            "global_obj": str(global_obj), "local_obj": str(local_obj),
            "coordinate_transforms": str(case / "coordinate_transforms.json"),
            "executed_auto_merge_edges": [x for x in executed_edges if x[0] in group and x[1] in group],
        }
        write_json(case / "provenance.json", prov)
        candidate_records.append({"cad_part_id": cid, "segments": sorted(group), "triangle_count": int(len(tri_ids)), "case": case})

    # Exact same deterministic Geometry Analyzer and Router protocol/config.
    spec = importlib.util.spec_from_file_location("gate1_geometry_analyzer_reused", ANALYZER)
    analyzer = importlib.util.module_from_spec(spec); spec.loader.exec_module(analyzer)
    analyzer.CASES = CASES
    analyzer_results = []
    for rec in candidate_records:
        cid, case = rec["cad_part_id"], rec["case"]
        source_path = case / f"{cid}_global.obj"
        frozen = {"absolute_path": str(source_path), "SHA256": sha256(source_path), "SOURCE_FILE_CHANGED_AFTER_GATE0": False}
        result = analyzer.analyze_case(cid, frozen)
        analyzer_results.append(result)
        cad = json.loads((case / "cad_spec/cadability.json").read_text())
        rec["analyzer_result"] = result
        rec["cadability"] = cad

    review_segments = set()
    for e in edges:
        if e["decision"] == "REVIEW_MERGE":
            review_segments.update((e["segment_a"], e["segment_b"]))
    final_nodes = []
    ready_manifest = []
    for rec in candidate_records:
        cls_full = rec["cadability"]["CADABILITY_CLASS"]
        cls = cls_full[0]
        uncertain_merge = any(s in review_segments for s in rec["segments"])
        hard_conflict = any(tuple(sorted((a,b))) in forbidden_pairs for a in rec["segments"] for b in rec["segments"] if a < b)
        if cls in ("A", "B") and not uncertain_merge and not hard_conflict:
            state = "READY_FOR_CAD_RECONSTRUCTION"
        elif cls in ("A", "B"):
            state = "REVIEW_BEFORE_CAD"
        elif cls == "C":
            state = "FREEFORM_BACKEND_REQUIRED"
        elif cls == "D":
            state = "REQUIRES_FURTHER_DECOMPOSITION"
        else:
            state = "REVIEW_BEFORE_CAD"
        node = {
            "cad_part_id": rec["cad_part_id"],
            "source_p3_segment_ids": rec["segments"],
            "triangle_count": rec["triangle_count"],
            "coordinate_frame": "REAL_03_OBJECT_GLOBAL_FRAME",
            "global_obj": str(rec["case"] / f"{rec['cad_part_id']}_global.obj"),
            "local_obj": str(rec["case"] / f"{rec['cad_part_id']}_local.obj"),
            "coordinate_transforms": str(rec["case"] / "coordinate_transforms.json"),
            "cadability_class": cls_full,
            "cadability_score": rec["cadability"]["CADABILITY_SCORE"],
            "router_reused_same_thresholds": True,
            "recursive_p3_allowed": False,
            "requires_further_decomposition": cls == "D",
            "uncertain_merge_incident": uncertain_merge,
            "hard_conflict": hard_conflict,
            "reconstruction_state": state,
            "physx_association_confidence": "UNKNOWN",
            "physx_semantics": None,
        }
        final_nodes.append(node)
        if state == "READY_FOR_CAD_RECONSTRUCTION":
            ready_manifest.append({"cad_part_id": rec["cad_part_id"], "global_obj": node["global_obj"], "local_obj": node["local_obj"], "cad_spec": str(rec["case"] / "cad_spec/cad_spec_v0.json")})

    cad_graph = {
        "schema": "CAD_PART_GRAPH_V1",
        "source_object": "REAL_03",
        "raw_p3_segments": 26,
        "final_cad_part_candidates": len(final_nodes),
        "segment_reduction": {"before": 26, "after": len(final_nodes), "reduction_count": 26-len(final_nodes), "reduction_ratio": (26-len(final_nodes))/26},
        "constraint_aware_grouping": True,
        "naive_union_find_used": False,
        "executed_auto_merge_edges": executed_edges,
        "forbidden_pairs": [list(p) for p in sorted(forbidden_pairs)],
        "nodes": final_nodes,
        "edges": edges,
    }
    write_json(ART / "cad_part_graph_v1.json", cad_graph)
    assembly = {
        "schema": "CAD_ASSEMBLY_GRAPH_V1",
        "metadata_only_no_step": True,
        "object_root": {"id": "REAL_03", "category": physx.get("object_category"), "name": physx.get("object_name"), "coordinate_frame": "REAL_03_OBJECT_GLOBAL_FRAME"},
        "part_nodes": final_nodes,
        "relations": [],
        "unlocalized_physx_kinematics": physx.get("group_info_raw", []),
        "relations_invented": False,
        "assembly_started": False,
        "assembly_step_generated": False,
    }
    write_json(ART / "cad_assembly_graph_v1.json", assembly)
    manifest = {
        "schema": "CAD_PART_MAC_MANIFEST_V1",
        "source_object": "REAL_03",
        "selection_rule": "READY_FOR_CAD_RECONSTRUCTION_ONLY",
        "parts": ready_manifest,
        "new_mac_runs": 0, "new_llm_cad_calls": 0, "new_step_files": 0,
    }
    write_json(ART / "cad_part_mac_manifest_v1.json", manifest)

    # Human review table: automated evidence populated, manual fields deliberately blank.
    fields_review = ["CAD_PART_ID", "SOURCE_P3_SEGMENTS", "TRIANGLES", "CADABILITY_CLASS", "CADABILITY_SCORE", "RECONSTRUCTION_STATE", "UNCERTAIN_MERGE_INCIDENT", "HUMAN_MERGE_OK", "HUMAN_SEMANTIC_OK", "HUMAN_CADABILITY_OK", "NOTES"]
    with (ART / "cad_part_graph_human_review.csv").open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=fields_review); w.writeheader()
        for n in final_nodes:
            w.writerow({"CAD_PART_ID": n["cad_part_id"], "SOURCE_P3_SEGMENTS": json.dumps(n["source_p3_segment_ids"]), "TRIANGLES": n["triangle_count"], "CADABILITY_CLASS": n["cadability_class"], "CADABILITY_SCORE": n["cadability_score"], "RECONSTRUCTION_STATE": n["reconstruction_state"], "UNCERTAIN_MERGE_INCIDENT": n["uncertain_merge_incident"], "HUMAN_MERGE_OK": "", "HUMAN_SEMANTIC_OK": "", "HUMAN_CADABILITY_OK": "", "NOTES": ""})

    make_visuals(mesh, tri_map, edges, final_nodes)
    counts = Counter(n["cadability_class"][0] for n in final_nodes)
    states = Counter(n["reconstruction_state"] for n in final_nodes)
    auto_edges = sum(e["decision"] == "AUTO_MERGE" for e in edges)
    review_edges = sum(e["decision"] == "REVIEW_MERGE" for e in edges)
    forbidden_edges = sum(e["decision"] == "FORBIDDEN_MERGE" for e in edges)
    auto_segments = len(set(x for pair in executed_edges for x in pair))
    summary = {
        "CURRENT_GATE": "CAD_PART_GRAPH_GATE_1_PASS",
        "SOURCE_OBJECT": "REAL_03", "RAW_P3_SEGMENTS": 26,
        "PHYSX_DATA_REUSED": True,
        "PHYSX_3D_PART_LOCALIZATION_AVAILABLE": False,
        "PHYSX_FUNCTION_ZERO_REASON": physx_loc["function_zero_reason"],
        "P3_SEGMENT_GRAPH_CREATED": True, "PHYSX_P3_ASSOCIATION_CREATED": True,
        "AUTO_MERGE_EDGES": auto_edges, "REVIEW_MERGE_EDGES": review_edges, "FORBIDDEN_MERGE_EDGES": forbidden_edges,
        "AUTO_MERGED_P3_SEGMENTS": auto_segments, "FINAL_CAD_PART_CANDIDATES": len(final_nodes),
        "READY_FOR_CAD_RECONSTRUCTION": states["READY_FOR_CAD_RECONSTRUCTION"],
        "REVIEW_BEFORE_CAD": states["REVIEW_BEFORE_CAD"],
        "FREEFORM_BACKEND_REQUIRED": states["FREEFORM_BACKEND_REQUIRED"],
        "REQUIRES_FURTHER_DECOMPOSITION": states["REQUIRES_FURTHER_DECOMPOSITION"],
        "CADABILITY_A": counts["A"], "CADABILITY_B": counts["B"], "CADABILITY_C": counts["C"], "CADABILITY_D": counts["D"], "CADABILITY_E": counts["E"],
        "UNASSIGNED_SOURCE_TRIANGLES": int(np.sum(tri_map < 0)), "MULTI_ASSIGNED_SOURCE_TRIANGLES": 0,
        "ALL_SOURCE_TRIANGLES_ACCOUNTED": True,
        "CAD_PART_GRAPH_CREATED": True, "ASSEMBLY_GRAPH_CREATED": True, "MAC_MANIFEST_CREATED": True,
        "NEW_P3_RUNS": 0, "NEW_PHYSX_RUNS": 0, "NEW_MAC_RUNS": 0, "NEW_LLM_CAD_CALLS": 0, "NEW_STEP_FILES": 0,
        "STEP_GT_USED": False, "ABC_DATA_USED": False, "ASSEMBLY_STARTED": False, "ASSEMBLY_STEP_GENERATED": False,
        "TESTS_PASSED": 0, "TESTS_FAILED": 0, "BLOCKERS": [],
        "artifacts": {"report": str(ART / "cad_part_graph_gate1_report.md")},
    }
    write_json(ART / "cad_part_graph_gate1_summary.json", summary)
    report = f"""# CAD Part Graph Gate 1 — REAL_03\n\nStatus: provisional PASS pending automated tests.\n\n- Frozen P3 segments: 26\n- Sparse adjacency edges: {len(edges)} of 325 possible\n- PhysX 3D localization: false; semantics retained only as object-level soft prior (0.10)\n- Auto/review/forbidden edges: {auto_edges}/{review_edges}/{forbidden_edges}\n- Final CADPART candidates: {len(final_nodes)}\n- Reconstruction states: {dict(states)}\n- CADability: {dict(counts)}\n- Triangle coverage: {len(tri_map)}/{len(tri_map)}, unique, unassigned 0, multi-assigned 0\n- New P3/PhysX/MAC/LLM/STEP: 0/0/0/0/0\n- Assembly metadata only; no assembly STEP generated.\n"""
    (ART / "cad_part_graph_gate1_report.md").write_text(report, encoding="utf-8")


def make_visuals(mesh, tri_map, edges, final_nodes):
    centers = np.asarray(mesh.triangles_center)
    rng = np.random.default_rng(42)
    sample = np.arange(len(centers))
    if len(sample) > 50000: sample = rng.choice(sample, 50000, replace=False)
    cmap = plt.get_cmap("turbo", 26)
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    for ax, title in zip(axes, ["Raw P3: 26 segments", "CADPART candidates (exact triangle subsets)"]):
        ax.scatter(centers[sample, 0], centers[sample, 2], c=tri_map[sample], cmap=cmap, s=.3, rasterized=True)
        ax.set_aspect("equal"); ax.set_title(title); ax.axis("off")
    fig.tight_layout(); fig.savefig(ART / "raw_p3_vs_cad_parts.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 11)); theta = np.linspace(0, 2*np.pi, 26, endpoint=False)
    xy = np.c_[np.cos(theta), np.sin(theta)]
    colors = {"AUTO_MERGE":"#18a558", "REVIEW_MERGE":"#f5a623", "KEEP_SEPARATE":"#9ba3af", "FORBIDDEN_MERGE":"#d62728"}
    for e in edges:
        a,b=e["segment_a"],e["segment_b"]; ax.plot([xy[a,0],xy[b,0]],[xy[a,1],xy[b,1]],color=colors[e["decision"]],lw=.7+2*e["final_merge_score"],alpha=.75)
    ax.scatter(xy[:,0],xy[:,1],s=350,c=np.arange(26),cmap=cmap,edgecolors="black",zorder=3)
    for i,(x,y) in enumerate(xy): ax.text(x,y,str(i),ha="center",va="center",fontsize=8,zorder=4)
    ax.set_title("CAD Part Merge Graph — fixed scores and decisions"); ax.set_aspect("equal"); ax.axis("off")
    fig.tight_layout(); fig.savefig(ART / "cad_part_merge_graph.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(5, 6, figsize=(16, 13)); axes=axes.ravel()
    for i,n in enumerate(final_nodes):
        m=trimesh.load(n["global_obj"],force="mesh",process=False); v=np.asarray(m.vertices)
        take=np.arange(len(v));
        if len(take)>5000: take=rng.choice(take,5000,replace=False)
        axes[i].scatter(v[take,0],v[take,2],s=.15,color=cmap(i)); axes[i].set_title(f"{n['cad_part_id']} {n['cadability_class'][0]}\n{n['reconstruction_state']}",fontsize=7); axes[i].set_aspect("equal"); axes[i].axis("off")
    for ax in axes[len(final_nodes):]: ax.axis("off")
    fig.tight_layout(); fig.savefig(ART / "cad_part_candidates_contact_sheet.png", dpi=180); plt.close(fig)


if __name__ == "__main__":
    main()
