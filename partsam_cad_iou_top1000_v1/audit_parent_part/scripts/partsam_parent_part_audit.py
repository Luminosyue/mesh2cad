#!/usr/bin/env python3
"""Read-only parent/part topology audit for PartSAM face-label segmentation."""
import csv
import argparse
import hashlib
import json
import math
import os
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

SOURCE = Path("/data/home/cuiyuehan/project/mesh2cad/partsam")
OUTPUT = Path("/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1")
AUDIT = OUTPUT / "audit_parent_part"
SEED = 20260918
ALGO_VERSION = 3


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def checksum(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def components(vertices, faces):
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    if not len(faces):
        return 0
    e = np.concatenate((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    a = coo_matrix((np.ones(len(e) * 2, dtype=np.uint8),
                    (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])),
                   shape=(len(vertices), len(vertices))).tocsr()
    return int(connected_components(a, directed=False, return_labels=False))


def edge_data(faces):
    edges = np.sort(np.concatenate(
        (faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]])), axis=1)
    unique, inverse, counts = np.unique(edges, axis=0, return_inverse=True, return_counts=True)
    return unique, inverse, counts


def topology(mesh, edges=None):
    faces = np.asarray(mesh.faces)
    vertices = np.asarray(mesh.vertices)
    _, _, counts = edges if edges is not None else edge_data(faces)
    degenerate = int(np.count_nonzero(
        (faces[:, 0] == faces[:, 1]) | (faces[:, 1] == faces[:, 2]) |
        (faces[:, 2] == faces[:, 0]))) if len(faces) else 0
    return {
        "vertices": len(vertices), "faces": len(faces),
        "connected_components": components(vertices, faces),
        "boundary_edge_count": int(np.count_nonzero(counts == 1)),
        "nonmanifold_edge_count": int(np.count_nonzero(counts > 2)),
        "degenerate_face_count": degenerate,
        "watertight": int(mesh.is_watertight),
        "is_volume": int(mesh.is_volume),
        "euler_number": int(mesh.euler_number),
        "volume": float(mesh.volume) if mesh.is_volume else "",
        "surface_area": float(mesh.area),
    }


def audit_one(pair):
    import trimesh
    from scipy.spatial import cKDTree

    object_id, parent_path, label_path = pair
    labels = np.load(label_path, allow_pickle=False)
    scene = trimesh.load(parent_path, force="scene", process=False, skip_materials=True)
    parent = scene.to_geometry()
    if not isinstance(parent, trimesh.Trimesh) or labels.ndim != 1 or len(labels) != len(parent.faces):
        raise ValueError(f"Face labels do not match GLB geometry: {object_id}")
    if not np.issubdtype(labels.dtype, np.integer):
        raise ValueError(f"Noninteger labels: {object_id}")
    faces = np.asarray(parent.faces)
    unique_edges, inverse, counts = edge_data(faces)
    parent_row = {"object_id": object_id, "parent_mesh_path": str(parent_path),
                  "annotation_path": str(label_path), **topology(parent, (unique_edges, inverse, counts))}

    # Coordinate-identical vertices can have distinct GLB indices. This is
    # diagnostic only: it never changes the raw topology or watertight result.
    _, vertex_to_geom = np.unique(np.asarray(parent.vertices), axis=0, return_inverse=True)
    geom_edges = np.sort(vertex_to_geom[unique_edges], axis=1)
    _, raw_to_geom, _ = np.unique(geom_edges, axis=0, return_inverse=True, return_counts=True)
    geom_occurrence = raw_to_geom[inverse]
    geom_counts = np.bincount(geom_occurrence)

    # Per-(edge, label) incidence identifies boundaries caused by face-label cuts.
    face_labels = np.tile(labels, 3)
    pairs = np.stack((inverse, face_labels), axis=1)
    unique_pairs, pair_counts = np.unique(pairs, axis=0, return_counts=True)
    per_edge_min = np.full(len(counts), np.iinfo(np.int64).max, dtype=np.int64)
    per_edge_max = np.full(len(counts), np.iinfo(np.int64).min, dtype=np.int64)
    np.minimum.at(per_edge_min, inverse, face_labels)
    np.maximum.at(per_edge_max, inverse, face_labels)
    geom_min = np.full(len(geom_counts), np.iinfo(np.int64).max, dtype=np.int64)
    geom_max = np.full(len(geom_counts), np.iinfo(np.int64).min, dtype=np.int64)
    np.minimum.at(geom_min, geom_occurrence, face_labels)
    np.maximum.at(geom_max, geom_occurrence, face_labels)
    parent_row["coordinate_welded_boundary_edge_count_diagnostic"] = int(np.count_nonzero(geom_counts == 1))
    parent_row["coordinate_welded_nonmanifold_edge_count_diagnostic"] = int(np.count_nonzero(geom_counts > 2))

    part_rows = []
    parts = []
    for part_id in np.unique(labels):
        pid = int(part_id)
        cid = f"{object_id}_part_{pid:03d}"
        part_path = OUTPUT / "candidates" / cid / "source.obj"
        ids = np.flatnonzero(labels == part_id)
        part = parent.submesh([ids], append=True, repair=False)
        part.remove_unreferenced_vertices()
        info = topology(part)
        boundary_ids = unique_pairs[(unique_pairs[:, 1] == pid) & (pair_counts == 1), 0]
        raw_segmentation = int(np.count_nonzero(
            (counts[boundary_ids] >= 2) & (per_edge_min[boundary_ids] != per_edge_max[boundary_ids])))
        geom_boundary_ids = raw_to_geom[boundary_ids]
        segmentation = int(np.count_nonzero(
            (geom_counts[geom_boundary_ids] == 2) &
            (geom_min[geom_boundary_ids] != geom_max[geom_boundary_ids])))
        external = int(np.count_nonzero(geom_counts[geom_boundary_ids] == 1))
        nonmanifold = int(np.count_nonzero(geom_counts[geom_boundary_ids] > 2))
        boundary_n = len(boundary_ids)
        if info["watertight"]:
            reason, priority = "WATERTIGHT_SOLID" if info["is_volume"] else "WATERTIGHT_NON_VOLUME", (
                "PRIORITY_A" if info["is_volume"] and info["connected_components"] <= 3 else "PRIORITY_C")
        elif info["degenerate_face_count"] or info["nonmanifold_edge_count"]:
            reason, priority = "MESH_DEFECT", "PRIORITY_C"
        elif boundary_n and segmentation / boundary_n >= 0.9 and external / boundary_n <= 0.1 and not nonmanifold:
            reason, priority = "SEGMENTATION_BOUNDARY", "PRIORITY_B"
        else:
            reason, priority = "UNRESOLVED_OPEN_BOUNDARY", "PRIORITY_C"
        part_rows.append({
            "object_id": object_id, "part_id": pid, "case_id": cid, "mesh_path": str(part_path),
            "parent_mesh_path": str(parent_path), "annotation_path": str(label_path),
            "parent_watertight": parent_row["watertight"],
            **info, "segmentation_boundary_edge_count": segmentation,
            "raw_indexed_segmentation_boundary_edge_count": raw_segmentation,
            "parent_open_boundary_edge_count": external,
            "boundary_edges_with_nonmanifold_parent": nonmanifold,
            "non_watertight_reason": reason, "cad_candidate_priority": priority,
        })
        parts.append(part)

    # The label array is an exhaustive partition of the parent's indexed faces.
    # Compare the independently exported part files as a separate placement check.
    box = np.stack([p.bounds for p in parts])
    combined_bounds = np.stack((box[:, 0].min(axis=0), box[:, 1].max(axis=0)))
    diag = max(float(np.linalg.norm(parent.extents)), 1e-12)
    bbox_error = float(np.max(np.abs(combined_bounds - parent.bounds)) / diag)
    outside = 0
    extracted = []
    checked = 0
    reference_points = trimesh.sample.sample_surface(parent, 16384, seed=SEED)[0]
    reference_tree = cKDTree(reference_points)
    parent_vertex_tree = cKDTree(parent.vertices)
    worst_part_vertex_distance = 0.0
    for row in part_rows:
        path = Path(row["mesh_path"])
        if not path.is_file():
            continue
        em = trimesh.load(path, force="mesh", process=False, skip_materials=True)
        if not isinstance(em, trimesh.Trimesh) or len(em.faces) != row["faces"]:
            continue
        checked += 1
        outside += int(np.any(em.bounds[0] < parent.bounds[0] - diag * 1e-5) or
                       np.any(em.bounds[1] > parent.bounds[1] + diag * 1e-5))
        part_points = trimesh.sample.sample_surface(em, 256, seed=SEED)[0]
        row["part_to_parent_sampled_surface_distance"] = float(
            reference_tree.query(part_points)[0].mean() / diag)
        row["part_to_parent_max_vertex_distance"] = float(
            parent_vertex_tree.query(em.vertices)[0].max() / diag)
        worst_part_vertex_distance = max(worst_part_vertex_distance,
                                         row["part_to_parent_max_vertex_distance"])
        extracted.append(em)
    chamfer = ""
    sampled_chamfer = ""
    if checked == len(part_rows) and extracted:
        union = trimesh.util.concatenate(extracted)
        ppoints = trimesh.sample.sample_surface(parent, 4096, seed=SEED)[0]
        upoints = trimesh.sample.sample_surface(union, 4096, seed=SEED)[0]
        sampled_chamfer = float((cKDTree(ppoints).query(upoints)[0].mean() +
                                 cKDTree(upoints).query(ppoints)[0].mean()) / (2 * diag))
        union_tree = cKDTree(union.vertices)
        chamfer = float((parent_vertex_tree.query(union.vertices)[0].mean() +
                         union_tree.query(parent.vertices)[0].mean()) / (2 * diag))
    consistency = {
        "object_id": object_id, "parent_mesh_path": str(parent_path),
        "part_count": len(part_rows), "parent_faces": len(parent.faces),
        "parts_faces": sum(row["faces"] for row in part_rows),
        "all_label_faces_accounted_for": int(sum(row["faces"] for row in part_rows) == len(parent.faces)),
        "parts_union_bbox_error": bbox_error,
        "parts_union_chamfer": chamfer,
        "chamfer_method": "all vertices, bidirectional nearest-neighbor / parent bbox diagonal",
        "parts_union_sampled_surface_chamfer": sampled_chamfer,
        "worst_part_to_parent_max_vertex_distance": worst_part_vertex_distance,
        "part_surface_distance_method": "256 sampled points to 16384 sampled parent points; nonzero sampling floor",
        "extracted_part_meshes_checked": checked,
        "extracted_part_bbox_outside_parent_n": outside,
        "parts_union_parent_iou": "NA",
        "iou_note": "Non-watertight surfaces: no reliable solid occupancy ground truth",
    }
    return parent_row, part_rows, consistency


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "checkpoints").mkdir(exist_ok=True)
    meshes = {p.stem: p for p in (SOURCE / "PartObjaverse-Tiny_mesh").rglob("*.glb")}
    labels = {p.stem: p for p in (SOURCE / "PartObjaverse-Tiny_instance_gt").rglob("*.npy")}
    baseline = json.loads((OUTPUT / "audit" / "source_inventory_before.json").read_text())["files"]
    before = {entry["relative_path"]: entry["sha256"] for entry in baseline}
    current = {str(p.relative_to(SOURCE)): checksum(p) for p in sorted(SOURCE.rglob("*")) if p.is_file()}
    if before != current:
        raise RuntimeError("Source file hashes differ from original audit baseline")
    ids = sorted(meshes.keys() & labels.keys())
    print(f"SOURCE_OBJECTS={len(meshes)} ANNOTATIONS={len(labels)} PAIRED={len(ids)}", flush=True)
    pending = [(oid, meshes[oid], labels[oid]) for oid in ids
               if not (AUDIT / "checkpoints" / f"{oid}.json").is_file() or
               json.loads((AUDIT / "checkpoints" / f"{oid}.json").read_text()).get("version") != ALGO_VERSION]
    if args.limit is not None:
        pending = pending[:args.limit]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(audit_one, pair): pair[0] for pair in pending}
        for i, fut in enumerate(as_completed(futures), 1):
            oid = futures[fut]
            try:
                parent, parts, consistency = fut.result()
                result = {"version": ALGO_VERSION, "parent": parent, "parts": parts, "consistency": consistency}
                path = AUDIT / "checkpoints" / f"{oid}.json"
                tmp = path.with_suffix(".tmp")
                tmp.write_text(json.dumps(result, allow_nan=False), encoding="utf-8")
                os.replace(tmp, path)
                print(f"AUDIT {i}/{len(pending)} {oid} parts={len(parts)}", flush=True)
            except Exception:
                print(f"FAILED {oid}: {traceback.format_exc()}", flush=True)

    results = [record for path in sorted((AUDIT / "checkpoints").glob("*.json"))
               if (record := json.loads(path.read_text())).get("version") == ALGO_VERSION]
    parents = [r["parent"] for r in results]
    parts = [p for r in results for p in r["parts"]]
    consistency = [r["consistency"] for r in results]
    mapped = [{
        "object_id": p["object_id"], "parent_mesh_path": p["parent_mesh_path"],
        "part_id": p["part_id"], "part_mesh_path": p["mesh_path"],
        "mapping_source": "matching_GLB_stem_and_NPY_face_labels_verified_against_GLB_face_count",
        "mapping_confidence": "HIGH", "annotation_path": p["annotation_path"],
    } for p in parts]
    write_csv(AUDIT / "object_part_mapping.csv", mapped, list(mapped[0]) if mapped else
              ["object_id", "parent_mesh_path", "part_id", "part_mesh_path", "mapping_source", "mapping_confidence"])
    write_csv(AUDIT / "part_watertight_audit.csv", parts, list(parts[0]) if parts else ["object_id", "part_id"])
    write_csv(AUDIT / "parent_watertight_audit.csv", parents, list(parents[0]) if parents else ["object_id"])
    write_csv(AUDIT / "parent_part_consistency.csv", consistency, list(consistency[0]) if consistency else ["object_id"])
    priority = [{"object_id": p["object_id"], "part_id": p["part_id"], "case_id": p["case_id"],
                 "part_mesh_path": p["mesh_path"], "parent_mesh_path": p["parent_mesh_path"],
                 "priority": p["cad_candidate_priority"], "reason": p["non_watertight_reason"],
                 "part_watertight": p["watertight"], "part_is_volume": p["is_volume"],
                 "connected_components": p["connected_components"],
                 "segmentation_boundary_edge_count": p["segmentation_boundary_edge_count"],
                 "boundary_edge_count": p["boundary_edge_count"]} for p in parts]
    write_csv(OUTPUT / "manifests" / "cad_candidate_priority.csv", priority,
              list(priority[0]) if priority else ["case_id", "priority"])
    reasons = Counter(p["non_watertight_reason"] for p in parts)
    levels = Counter(p["cad_candidate_priority"] for p in parts)
    joint = Counter((p["parent_watertight"], p["watertight"]) for p in parts)
    summary = {
        "TOTAL_PART_N": len(parts), "MAPPED_TO_PARENT_N": len(mapped),
        "UNMAPPED_PART_N": max(0, int(json.loads((OUTPUT / "audit" / "audit_summary.json").read_text())["TOTAL_PART_MESH_N"]) - len(mapped)),
        "PARENT_OBJECT_N": len(parents),
        "WATERTIGHT_PART_N": sum(p["watertight"] for p in parts),
        "NON_WATERTIGHT_PART_N": sum(not p["watertight"] for p in parts),
        "WATERTIGHT_RATE": sum(p["watertight"] for p in parts) / len(parts) if parts else 0,
        "PARENT_WATERTIGHT_N": sum(p["watertight"] for p in parents),
        "PARENT_NON_WATERTIGHT_N": sum(not p["watertight"] for p in parents),
        "PARENT_WATERTIGHT_PART_WATERTIGHT_N": joint[1, 1],
        "PARENT_WATERTIGHT_PART_NONWATERTIGHT_N": joint[1, 0],
        "PARENT_NONWATERTIGHT_PART_WATERTIGHT_N": joint[0, 1],
        "PARENT_NONWATERTIGHT_PART_NONWATERTIGHT_N": joint[0, 0],
        "NONWATERTIGHT_SEGMENTATION_BOUNDARY_N": reasons["SEGMENTATION_BOUNDARY"],
        "NONWATERTIGHT_MESH_DEFECT_N": reasons["MESH_DEFECT"],
        "NONWATERTIGHT_UNRESOLVED_N": reasons["UNRESOLVED_OPEN_BOUNDARY"],
        "PRIORITY_A_N": levels["PRIORITY_A"], "PRIORITY_B_N": levels["PRIORITY_B"],
        "PRIORITY_C_N": levels["PRIORITY_C"],
        "CHECKED_EXTRACTED_PART_N": sum(x["extracted_part_meshes_checked"] for x in consistency),
        "BBOX_OUTSIDE_PARENT_N": sum(x["extracted_part_bbox_outside_parent_n"] for x in consistency),
        "PARTITION_FACE_COUNT_MISMATCH_N": sum(
            x["parent_faces"] != x["parts_faces"] for x in consistency),
        "MAX_NORMALIZED_PART_VERTEX_DISTANCE": max(
            (x["worst_part_to_parent_max_vertex_distance"] for x in consistency), default=None),
        "SOURCE_FILE_HASHES_UNCHANGED": current == {str(p.relative_to(SOURCE)): checksum(p) for p in sorted(SOURCE.rglob("*")) if p.is_file()},
        "SOURCE_OBJECTS_WITH_ANNOTATIONS_N": len(ids),
        "OBJECTS_CHECKPOINTED_N": len(results),
    }
    summary["CURRENT_GATE"] = ("PARTSAM_PARENT_PART_WATERTIGHT_AUDIT_COMPLETE"
                               if len(results) == len(ids) and len(ids) == len(meshes) == len(labels)
                               and summary["UNMAPPED_PART_N"] == 0 and summary["SOURCE_FILE_HASHES_UNCHANGED"]
                               and summary["BBOX_OUTSIDE_PARENT_N"] == 0
                               and summary["CHECKED_EXTRACTED_PART_N"] == len(parts)
                               and summary["PARTITION_FACE_COUNT_MISMATCH_N"] == 0
                               and summary["MAX_NORMALIZED_PART_VERTEX_DISTANCE"] <= 1e-5 else
                               "PARTSAM_PARENT_PART_WATERTIGHT_AUDIT_NEEDS_REVIEW")
    (AUDIT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
