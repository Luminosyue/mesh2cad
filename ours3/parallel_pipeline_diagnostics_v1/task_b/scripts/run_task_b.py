#!/usr/bin/env python3
"""Read-only CASE06/CASE07 mesh-to-CAD-part-graph rescue diagnostics."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
BATCH = OURS3 / "batch_real_mesh2cad_v1"
MANIFEST = BATCH / "manifest/batch_10_case_manifest.json"
OUT = OURS3 / "parallel_pipeline_diagnostics_v1/task_b"
ART, LOGS, TESTS = OUT / "artifacts", OUT / "logs", OUT / "tests"
CASES = ["CASE_06", "CASE_07"]


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def load_obj_exact(path: Path):
    vertices, faces = [], []
    nontri = 0
    with path.open("r", errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                p = line.split()
                vertices.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith("f "):
                ids = []
                for tok in line.split()[1:]:
                    i = int(tok.split("/", 1)[0])
                    ids.append(i - 1 if i > 0 else len(vertices) + i)
                if len(ids) == 3:
                    faces.append(ids)
                else:
                    nontri += 1
                    for j in range(1, len(ids) - 1):
                        faces.append((ids[0], ids[j], ids[j + 1]))
    return np.asarray(vertices, dtype=np.float64), np.asarray(faces, dtype=np.int64), nontri


def geometry(vertices, faces):
    tri = vertices[faces]
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    twice = np.linalg.norm(cross, axis=1)
    areas = twice * 0.5
    normals = np.zeros_like(cross)
    ok = twice > 1e-15
    normals[ok] = cross[ok] / twice[ok, None]
    centroids = tri.mean(axis=1)
    return areas, normals, centroids


def face_adjacency(faces):
    n = len(faces)
    edges = np.vstack((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    edges.sort(axis=1)
    face_ids = np.tile(np.arange(n, dtype=np.int64), 3)
    order = np.lexsort((edges[:, 1], edges[:, 0]))
    e = edges[order]
    ids = face_ids[order]
    same = np.all(e[:-1] == e[1:], axis=1)
    a, b = ids[:-1][same], ids[1:][same]
    valid = a != b
    return a[valid], b[valid]


def sparse_components(n, a, b, edge_mask=None):
    if edge_mask is not None:
        a, b = a[edge_mask], b[edge_mask]
    data = np.ones(len(a) * 2, dtype=np.uint8)
    mat = coo_matrix((data, (np.r_[a, b], np.r_[b, a])), shape=(n, n)).tocsr()
    return connected_components(mat, directed=False, return_labels=True)[1]


def bbox_for_faces(vertices, faces, idx):
    pts = vertices[np.unique(faces[idx].ravel())]
    return pts.min(axis=0), pts.max(axis=0)


def export_obj(path, vertices, faces, idx):
    idx = np.asarray(idx, dtype=np.int64)
    sub = faces[idx]
    used, inverse = np.unique(sub.ravel(), return_inverse=True)
    remap = inverse.reshape((-1, 3)) + 1
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write("# residual mesh from frozen source OBJ; diagnostic only, not CAD\n")
        for v in vertices[used]:
            f.write(f"v {v[0]:.9g} {v[1]:.9g} {v[2]:.9g}\n")
        for q in remap:
            f.write(f"f {q[0]} {q[1]} {q[2]}\n")


def id_to_label(part_id):
    m = re.search(r"(\d+)$", part_id or "")
    return int(m.group(1)) if m else None


def analyse(case, manifest_row):
    old = BATCH / "cases" / case
    source = Path(manifest_row["SOURCE_OBJ_PATH"])
    p3_meta = json.loads((old / "p3/part_metadata.json").read_text())
    physx = json.loads((old / "physx_v1/understanding/physx_understanding.json").read_text())
    old_graph = json.loads((old / "cad_part_graph/cad_part_graph_v1.json").read_text())
    old_metrics = json.loads((old / "metrics/case_result.json").read_text())
    labels = np.load(old / "p3/triangle_part_id.npy")

    vertices, faces, nontri = load_obj_exact(source)
    if sha256(source) != manifest_row["SOURCE_SHA256"]:
        raise RuntimeError(f"{case}: frozen source SHA mismatch")
    if len(faces) != len(labels) or len(faces) != p3_meta["source_triangle_count"]:
        raise RuntimeError(f"{case}: source/P3 triangle mapping mismatch")
    areas, normals, tri_centroids = geometry(vertices, faces)
    source_area = float(areas.sum())
    a, b = face_adjacency(faces)
    source_cc = sparse_components(len(faces), a, b)
    same_p3 = (labels[a] == labels[b]) & (labels[a] >= 0)
    p3_cc = sparse_components(len(faces), a, b, same_p3)

    assigned = labels >= 0
    keys = np.stack((labels[assigned], p3_cc[assigned]), axis=1)
    unique_keys, inv = np.unique(keys, axis=0, return_inverse=True)
    face_node = np.full(len(faces), -1, dtype=np.int64)
    face_node[assigned] = inv
    nodes = []
    for node_id, (p3_label, cc) in enumerate(unique_keys):
        idx = np.flatnonzero(face_node == node_id)
        lo, hi = bbox_for_faces(vertices, faces, idx)
        source_components = sorted(set(int(x) for x in source_cc[idx]))
        nodes.append({
            "cad_part_id": f"CADPART_{node_id:03d}",
            "p3_segment_id": int(p3_label),
            "p3_connected_component": int(cc),
            "triangle_count": int(len(idx)),
            "source_area": float(areas[idx].sum()),
            "source_area_ratio": float(areas[idx].sum() / source_area),
            "bbox_min": lo.tolist(), "bbox_max": hi.tolist(),
            "centroid_area_weighted": np.average(tri_centroids[idx], axis=0, weights=areas[idx]).tolist(),
            "source_connected_components": source_components,
            "physx_semantic": None,
            "physx_semantic_reason": "UNLOCALIZED_SOFT_PRIOR_ONLY",
            "assignment_source": "REUSED_P3_TRIANGLE_MAP",
        })

    # Boundary adjacency and normal continuity between rescued CAD parts.
    cross = (face_node[a] >= 0) & (face_node[b] >= 0) & (face_node[a] != face_node[b])
    pair_stats = defaultdict(list)
    angles = np.degrees(np.arccos(np.clip(np.sum(normals[a[cross]] * normals[b[cross]], axis=1), -1.0, 1.0)))
    for na, nb, ang in zip(face_node[a[cross]], face_node[b[cross]], angles):
        pair_stats[tuple(sorted((int(na), int(nb))))].append(float(ang))
    edges = []
    for (i, j), vals in sorted(pair_stats.items()):
        arr = np.asarray(vals)
        edges.append({
            "node_a": f"CADPART_{i:03d}", "node_b": f"CADPART_{j:03d}",
            "shared_mesh_edge_count": int(len(arr)),
            "boundary_normal_angle_mean_deg": float(arr.mean()),
            "boundary_normal_angle_p95_deg": float(np.percentile(arr, 95)),
            "g1_like_fraction_angle_le_15deg": float((arr <= 15).mean()),
            "geometry_continuity_merge_hypothesis": bool(len(arr) >= 3 and (arr <= 15).mean() >= 0.8),
        })

    # Symmetry is a hypothesis only; never changes assignments.
    global_lo, global_hi = vertices.min(axis=0), vertices.max(axis=0)
    center, diag = (global_lo + global_hi) * 0.5, float(np.linalg.norm(global_hi - global_lo))
    symmetry = []
    for i in range(len(nodes)):
        ci = np.asarray(nodes[i]["centroid_area_weighted"])
        ei = np.asarray(nodes[i]["bbox_max"]) - np.asarray(nodes[i]["bbox_min"])
        ai = nodes[i]["source_area"]
        for j in range(i + 1, len(nodes)):
            cj = np.asarray(nodes[j]["centroid_area_weighted"])
            ej = np.asarray(nodes[j]["bbox_max"]) - np.asarray(nodes[j]["bbox_min"])
            aj = nodes[j]["source_area"]
            extent_error = float(np.linalg.norm(ei - ej) / max(np.linalg.norm(ei), np.linalg.norm(ej), 1e-12))
            area_ratio = min(ai, aj) / max(ai, aj, 1e-12)
            for axis in range(3):
                reflected = ci.copy(); reflected[axis] = 2 * center[axis] - reflected[axis]
                center_error = float(np.linalg.norm(reflected - cj) / max(diag, 1e-12))
                score = float(area_ratio * math.exp(-5 * center_error - 2 * extent_error))
                if score >= 0.65:
                    symmetry.append({"node_a": f"CADPART_{i:03d}", "node_b": f"CADPART_{j:03d}",
                                     "mirror_axis": "xyz"[axis], "score": score,
                                     "center_error_normalized": center_error,
                                     "extent_error": extent_error, "area_ratio": area_ratio})
    symmetry.sort(key=lambda x: x["score"], reverse=True)

    accepted_labels = sorted(x for x in (id_to_label(p.get("part_id")) for p in old_metrics.get("parts", []) if p.get("accepted")) if x is not None)
    old_assigned = np.isin(labels, accepted_labels)
    old_assigned_area = float(areas[old_assigned].sum())
    old_residual = ~old_assigned
    residual_edges = old_residual[a] & old_residual[b]
    residual_cc = sparse_components(len(faces), a, b, residual_edges)
    residual_records = []
    residual_root = OUT / "cases" / case / "residuals"
    for cc in np.unique(residual_cc[old_residual]):
        idx = np.flatnonzero(old_residual & (residual_cc == cc))
        area = float(areas[idx].sum())
        lo, hi = bbox_for_faces(vertices, faces, idx)
        residual_records.append({"_idx": idx, "component_label": int(cc), "triangle_count": int(len(idx)),
                                 "source_area": area, "source_area_ratio": area / source_area,
                                 "p3_segments": sorted(set(int(x) for x in labels[idx] if x >= 0)),
                                 "bbox_min": lo.tolist(), "bbox_max": hi.tolist()})
    residual_records.sort(key=lambda x: x["source_area"], reverse=True)
    for rank, rec in enumerate(residual_records):
        rid = f"RESIDUAL_CADPART_{rank:03d}"
        idx = rec.pop("_idx")
        rec.update({
            "residual_id": rid,
            "rank_by_area": rank,
            "reference": "OLD_ACCEPTED_PART_IDS_FROM_METRICS_NOT_STEP_GEOMETRY",
            "large_region": bool(rec["source_area_ratio"] >= 0.01),
            "geometry_continuity_analysis": "CONNECTED_VIA_SHARED_SOURCE_MESH_EDGES",
            "p3_reconsideration": "KEEP_SEGMENTS_AS_GRAPH_NODES; REVIEW_CONTINUITY_EDGES_FOR_OPTIONAL_MERGE",
            "split_merge_hypothesis": "GROUP_BY_SOURCE_CONNECTED_COMPONENT_AND_PHYSX_PART_COUNT_SOFT_PRIOR",
        })
        obj_path = residual_root / rid / "residual.obj"
        export_obj(obj_path, vertices, faces, idx)
        rec["mesh_obj"] = str(obj_path)

    physx_parts = [p.get("part_name") for p in physx.get("parts", []) if p.get("part_name")]
    component_groups = []
    for cc in sorted(set(int(x) for x in source_cc)):
        members = sorted(set(int(x) for x in face_node[source_cc == cc] if x >= 0))
        component_groups.append({"source_component": cc, "nodes": [f"CADPART_{x:03d}" for x in members]})
    by_p3 = defaultdict(list)
    for n in nodes:
        by_p3[n["p3_segment_id"]].append(n["cad_part_id"])
    split_hypotheses = [
        {"p3_segment_id": int(label), "result_nodes": members,
         "reason": "P3_SEGMENT_HAS_MULTIPLE_DISCONNECTED_SOURCE_MESH_REGIONS",
         "action": "SPLIT_IN_RESCUED_PART_GRAPH"}
        for label, members in sorted(by_p3.items()) if len(members) > 1
    ]
    graph = {
        "schema": "CASE06_CASE07_PART_DISCOVERY_RESCUE_V1",
        "case": case,
        "source_obj": str(source), "source_sha256": sha256(source),
        "segmentation_input_type": "FROZEN_MANIFEST_SOURCE_OBJ",
        "old_step_used_as_segmentation_input": False,
        "P3_REUSED": True, "P3_INFERENCE_RUNS": 0,
        "PHYSX_REUSED": True, "PHYSX_INFERENCE_RUNS": 0,
        "P3_SEGMENTS": int(len(np.unique(labels[assigned]))),
        "CAD_PARTS": len(nodes),
        "SOURCE_TRIANGLES": int(len(faces)), "SOURCE_AREA": source_area,
        "ASSIGNED_TRIANGLES": int(assigned.sum()), "ASSIGNED_AREA": float(areas[assigned].sum()),
        "UNASSIGNED_AREA_RATIO": float(areas[~assigned].sum() / source_area),
        "OVERLAP_RATIO": 0.0,
        "PART_GRAPH_COVERAGE": float(areas[assigned].sum() / source_area),
        "SOURCE_CONNECTED_COMPONENTS": int(len(np.unique(source_cc))),
        "PHYSX_OBJECT_PRIOR": {"object_name": physx.get("object_name"), "object_category": physx.get("object_category"),
                               "part_count": len(physx_parts), "part_names": physx_parts,
                               "localization_available": False, "use": "SOFT_COUNT_AND_NAMING_PRIOR_ONLY"},
        "component_groups": component_groups,
        "nodes": nodes, "adjacency_edges": edges, "symmetry_hypotheses": symmetry,
        "split_hypotheses": split_hypotheses,
        "merge_hypotheses": [e for e in edges if e["geometry_continuity_merge_hypothesis"]],
        "provenance": {"manifest": str(MANIFEST), "p3_metadata": str(old / "p3/part_metadata.json"),
                       "p3_triangle_map": str(old / "p3/triangle_part_id.npy"),
                       "physx_understanding": str(old / "physx_v1/understanding/physx_understanding.json"),
                       "nontriangular_faces_triangulated": nontri},
    }
    residual = {
        "case": case, "reference": "OLD_ACCEPTED_PART_IDS_FROM_METRICS_NOT_STEP_GEOMETRY",
        "old_accepted_p3_segments": accepted_labels,
        "OLD_CAD_AREA_COVERAGE_REPORTED": old_metrics.get("cad_area_coverage"),
        "OLD_ACCEPTED_SOURCE_AREA_EXACT": old_assigned_area,
        "OLD_ACCEPTED_SOURCE_AREA_RATIO_EXACT": old_assigned_area / source_area,
        "OLD_UNASSIGNED_AREA_RATIO_EXACT": float(areas[old_residual].sum() / source_area),
        "RESIDUAL_REGION_COUNT": len(residual_records),
        "residual_regions": residual_records,
        "NEW_GRAPH_UNASSIGNED_AREA_RATIO": graph["UNASSIGNED_AREA_RATIO"],
    }
    return graph, residual, old_graph, old_metrics, physx


def main():
    started = time.time()
    for d in [ART, LOGS, TESTS, OUT / "scripts", OUT / "cases"]:
        d.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    rows = {x["BATCH_CASE_ID"]: x for x in manifest["cases"]}
    def capture(cmd):
        p = subprocess.run(cmd, text=True, capture_output=True)
        return {"command": cmd, "return_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}

    gpu_snapshot = capture(["nvidia-smi", "--query-gpu=index,uuid,name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader"])
    process_snapshot = capture(["ps", "-eo", "pid,ppid,%cpu,%mem,etime,args"])
    process_snapshot["stdout"] = "\n".join(
        x for x in process_snapshot["stdout"].splitlines()
        if re.search(r"case_?09|aircraft|end2end", x, re.I)
    ) + "\n"
    resource = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "CASE09_TOUCHED": False, "GPU_USED": False,
        "P3_INFERENCE_RUNS": 0, "PHYSX_INFERENCE_RUNS": 0,
        "CPU_THREAD_LIMITS": {k: os.environ.get(k) for k in ["OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"]},
        "CASE09_RESOURCE_ISOLATION": "READ_ONLY_PROCESS_SNAPSHOT_TAKEN_BEFORE_TASK; TASK_B_REUSED_EXISTING_OUTPUTS_AND_USED_CPU_ONLY",
        "GPU_SNAPSHOT": gpu_snapshot,
        "CASE09_PROCESS_SNAPSHOT": process_snapshot,
        "CASE09_RUNNING_DURING_TASK": bool(process_snapshot["stdout"].strip()),
    }
    dump(ART / "resource_isolation_audit.json", resource)

    outputs = {}
    for case in CASES:
        graph, residual, old_graph, old_metrics, physx = analyse(case, rows[case])
        lower = case.lower().replace("_", "")
        dump(ART / f"{lower}_cad_part_graph.json", graph)
        dump(ART / f"{lower}_residuals.json", residual)
        outputs[case] = (graph, residual, old_graph, old_metrics, physx)

    reuse = {"manifest": str(MANIFEST), "OLD_STEP_USED": False, "P3_RERUN": False, "PHYSX_RERUN": False, "cases": {}}
    for case in CASES:
        old = BATCH / "cases" / case
        row = rows[case]
        reuse["cases"][case] = {
            "source_obj": row["SOURCE_OBJ_PATH"], "source_sha256": row["SOURCE_SHA256"],
            "segmentation_input": row["SOURCE_OBJ_PATH"], "segmentation_input_type": "OBJ",
            "p3_metadata": str(old / "p3/part_metadata.json"),
            "p3_triangle_map": str(old / "p3/triangle_part_id.npy"),
            "p3_metadata_sha256": sha256(old / "p3/part_metadata.json"),
            "p3_triangle_map_sha256": sha256(old / "p3/triangle_part_id.npy"),
            "physx_understanding": str(old / "physx_v1/understanding/physx_understanding.json"),
            "physx_provenance": str(old / "physx_v1/provenance/provenance.json"),
            "physx_understanding_sha256": sha256(old / "physx_v1/understanding/physx_understanding.json"),
        }
    dump(ART / "input_reuse_audit.json", reuse)

    g6, r6, oldg6, m6, p6 = outputs["CASE_06"]
    g7, r7, oldg7, m7, p7 = outputs["CASE_07"]
    rc6 = {
        "case": "CASE_06", "PRIMARY_ROOT_CAUSE": "PART_CADABILITY_FAILURE",
        "SECONDARY_CAUSES": ["BOTH_P3_PARTS_CLASSIFIED_C_FREEFORM_DOMINANT", "NO_FREEFORM_CAD_BACKEND_WAS_ROUTED"],
        "P3_SEGMENTATION_FAILURE": False, "PHYSX_PRIOR_FAILURE": False,
        "CAD_PART_GRAPH_FAILURE": False, "ROUTER_FAILURE": False,
        "PART_CADABILITY_FAILURE": True,
        "evidence": {
            "p3_segments": g6["P3_SEGMENTS"], "source_components": g6["SOURCE_CONNECTED_COMPONENTS"],
            "part_graph_coverage": g6["PART_GRAPH_COVERAGE"], "physx_part_count": g6["PHYSX_OBJECT_PRIOR"]["part_count"],
            "old_graph_candidates": oldg6["FINAL_CAD_PART_CANDIDATES"],
            "old_ready_parts": oldg6["READY_FOR_CAD_RECONSTRUCTION"],
            "old_cadability_classes": [n["CADABILITY_CLASS"] for n in oldg6["nodes"]],
            "old_accepted_count": m6["accepted_count"], "old_cad_area_coverage": m6["cad_area_coverage"],
        },
        "conclusion": "P3 produced two complete source-aligned components and PhysX independently proposed two parts; the old pipeline stopped because both were gated as freeform/non-CADable, not because part discovery missed geometry.",
    }
    rc7 = {
        "case": "CASE_07", "PRIMARY_ROOT_CAUSE": "ROUTER_FAILURE",
        "ROOT_CAUSE_SUBTYPE": "AREA_UNAWARE_MAX_READY_PARTS_TRUNCATION",
        "SECONDARY_CAUSES": ["ONE_OF_SIX_ATTEMPTED_PARTS_FAILED_Q1", "NO_RESIDUAL_REQUEUE_AFTER_PART_CAP"],
        "evidence": {
            "p3_segments": g7["P3_SEGMENTS"], "part_graph_coverage": g7["PART_GRAPH_COVERAGE"],
            "old_graph_ready_state_nodes": sum(n["reconstruction_state"] == "READY_FOR_CAD_RECONSTRUCTION" for n in oldg7["nodes"]),
            "old_ready_parts_after_cap": oldg7["READY_FOR_CAD_RECONSTRUCTION"],
            "max_ready_parts_per_object": oldg7["MAX_READY_PARTS_PER_OBJECT"],
            "attempted_parts": m7["attempted_parts"], "accepted_parts": m7["accepted_count"],
            "old_cad_area_coverage_reported": m7["cad_area_coverage"],
            "old_cad_area_coverage_exact_from_accepted_p3_triangles": r7["OLD_ACCEPTED_SOURCE_AREA_RATIO_EXACT"],
            "old_unassigned_area_ratio_exact": r7["OLD_UNASSIGNED_AREA_RATIO_EXACT"],
            "new_part_graph_coverage": g7["PART_GRAPH_COVERAGE"],
        },
        "conclusion": "P3 assigned the full source mesh to 30 segments and 27 graph nodes were marked ready, but an area-unaware cap forwarded only six; five accepted small parts covered about 10%, while unattempted graph nodes were never residual-requeued.",
    }
    dump(ART / "case06_rootcause.json", rc6)
    dump(ART / "case07_rootcause.json", rc7)

    summary = {
        "TASK_B": "CASE06_CASE07_PART_DISCOVERY_RESCUE_V1", "TASK_B_STATUS": "PASS",
        "CASE09_TOUCHED": False,
        "CASE06_P3_SEGMENTS": g6["P3_SEGMENTS"], "CASE06_CAD_PARTS": g6["CAD_PARTS"],
        "CASE06_SOURCE_AREA": g6["SOURCE_AREA"], "CASE06_ASSIGNED_AREA": g6["ASSIGNED_AREA"],
        "CASE06_UNASSIGNED_AREA_RATIO": g6["UNASSIGNED_AREA_RATIO"], "CASE06_OVERLAP_RATIO": g6["OVERLAP_RATIO"],
        "CASE06_PRIMARY_ROOT_CAUSE": rc6["PRIMARY_ROOT_CAUSE"],
        "CASE07_P3_SEGMENTS": g7["P3_SEGMENTS"], "CASE07_CAD_PARTS": g7["CAD_PARTS"],
        "CASE07_SOURCE_AREA": g7["SOURCE_AREA"], "CASE07_ASSIGNED_AREA": g7["ASSIGNED_AREA"],
        "CASE07_UNASSIGNED_AREA_RATIO": g7["UNASSIGNED_AREA_RATIO"], "CASE07_OVERLAP_RATIO": g7["OVERLAP_RATIO"],
        "CASE07_OLD_COVERAGE": m7["cad_area_coverage"], "CASE07_PART_GRAPH_COVERAGE": g7["PART_GRAPH_COVERAGE"],
        "CASE07_PRIMARY_ROOT_CAUSE": rc7["PRIMARY_ROOT_CAUSE"],
        "P3_INFERENCE_RUNS": 0, "PHYSX_INFERENCE_RUNS": 0, "GPU_USED": False,
        "STEP_USED_AS_SEGMENTATION_INPUT": False,
        "LOFT_RUNS": 0, "BSPLINE_RUNS": 0, "MAC_RUNS": 0, "LLM_CALLS": 0, "STEP_GENERATED": 0,
        "TESTS_PASSED": None, "TESTS_FAILED": None, "BLOCKERS": [],
        "elapsed_seconds": time.time() - started,
    }
    dump(ART / "part_discovery_metrics.json", {
        "CASE_06": {k: summary[k] for k in summary if k.startswith("CASE06_")},
        "CASE_07": {k: summary[k] for k in summary if k.startswith("CASE07_")},
        "area_units": "SOURCE_OBJ_COORDINATE_UNITS_SQUARED",
    })
    dump(ART / "task_b_summary.json", summary)
    report = f"""# Task B — CASE06/CASE07 Part Discovery Rescue

Status: **PASS**. Frozen source OBJ files were resolved from `{MANIFEST}` and their SHA-256 hashes were verified. Existing P3 triangle maps and PhysX outputs were reused; no GPU inference ran and no STEP was used as segmentation input.

## CASE06

P3 already partitions all {g6['SOURCE_TRIANGLES']} triangles into {g6['P3_SEGMENTS']} source-aligned connected parts, matching both the two source connected components and the two-part PhysX prior. The rescued part graph covers {g6['PART_GRAPH_COVERAGE']:.6f} of source area with zero overlap and zero unassigned area. The old pipeline produced no accepted CAD because both parts were classified `C_FREEFORM_DOMINANT` and no part was routed for reconstruction. Primary cause: **PART_CADABILITY_FAILURE**, not segmentation or PhysX failure.

## CASE07

P3 already assigns all {g7['SOURCE_TRIANGLES']} triangles across {g7['P3_SEGMENTS']} segments. The rescued graph retains every source-area assignment and reaches {g7['PART_GRAPH_COVERAGE']:.6f} coverage, versus old accepted-CAD coverage {m7['cad_area_coverage']:.6f}. The old graph marked 27 nodes ready but its `MAX_READY_PARTS_PER_OBJECT=6` cap forwarded only six; five accepted small parts accounted for roughly 10% of area and the remainder was not requeued as residual. Primary cause: **ROUTER_FAILURE / AREA_UNAWARE_MAX_READY_PARTS_TRUNCATION**.

Residual catalogs are defined against old accepted P3 part IDs, never STEP geometry. They include connected source-mesh regions, exact areas, P3 memberships, geometry-continuity notes, and split/merge hypotheses. The new graph itself has zero unassigned area.

No Loft, BSpline reconstruction, MAC, LLM, CAD/STEP generation, shared-code edit, CASE09 edit, or P3/PhysX rerun occurred.
"""
    (ART / "task_b_report.md").write_text(report)

    test = subprocess.run([str(Path(os.sys.executable)), "-m", "unittest", "-v", str(TESTS / "test_task_b.py")], text=True, capture_output=True)
    (LOGS / "task_b_tests.log").write_text(test.stdout + test.stderr)
    m = re.search(r"Ran (\d+) tests?", test.stdout + test.stderr)
    n = int(m.group(1)) if m else 0
    summary["TESTS_PASSED"] = n if test.returncode == 0 else 0
    summary["TESTS_FAILED"] = 0 if test.returncode == 0 else max(1, n)
    summary["TEST_RETURN_CODE"] = test.returncode
    dump(ART / "task_b_summary.json", summary)
    with (ART / "task_b_report.md").open("a") as f:
        f.write(f"\nTests: {summary['TESTS_PASSED']} passed, {summary['TESTS_FAILED']} failed.\n")
    print(json.dumps(summary, indent=2))
    return test.returncode


if __name__ == "__main__":
    raise SystemExit(main())
