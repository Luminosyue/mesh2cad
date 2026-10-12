#!/usr/bin/env python3
"""Stage A for PARTOBJAVERSE_LLM_CAD_PILOT_V1.

Audits recursively discovered GLB/NPY pairs, exports exact face subsets as OBJ,
computes provenance/statistics, selects a diverse CAD-like Pilot20, and performs
deterministic spot checks.  It never mutates source data or the prior pilot.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import shutil
import sys
import traceback
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import trimesh


DIRS = ["audit", "manifests", "split_parts", "selected_parts", "geometry",
        "renders", "prompts", "cad_code", "step", "recon_mesh", "metrics",
        "logs", "reports", "scripts"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def finite_float(x):
    x = float(x)
    return x if math.isfinite(x) else None


def load_mesh(path: Path):
    mesh = trimesh.load(path)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"Unsupported loaded geometry: {type(mesh).__name__}")
    return mesh


def export_exact_obj(vertices: np.ndarray, faces: np.ndarray, path: Path) -> None:
    # Deliberately write only v/f records; no processing, welding, or repair.
    with path.open("w", encoding="ascii", newline="\n") as f:
        f.write("# exact source face subset; vertices re-indexed only\n")
        for v in vertices:
            f.write(f"v {v[0]:.17g} {v[1]:.17g} {v[2]:.17g}\n")
        for tri in faces:
            f.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}\n")


def mesh_stats(vertices: np.ndarray, faces: np.ndarray):
    part = trimesh.Trimesh(vertices=vertices, faces=faces, process=False, validate=False)
    bmin, bmax = vertices.min(0), vertices.max(0)
    bsize = bmax - bmin
    eps = max(float(np.max(bsize)), 1.0) * 1e-10
    valid = bool(len(vertices) and len(faces) and np.all(np.isfinite(vertices)) and np.all(bsize > eps))

    # Connectivity uses face adjacency only and does not modify geometry.
    try:
        components = int(len(trimesh.graph.connected_components(part.face_adjacency, nodes=np.arange(len(faces)))))
    except Exception:
        components = 0

    area = float(part.area)
    watertight = bool(part.is_watertight)
    volume = abs(float(part.volume)) if watertight and math.isfinite(float(part.volume)) else None

    centered = vertices - vertices.mean(0)
    cov = centered.T @ centered / max(len(vertices), 1)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    evals, evecs = evals[order], evecs[:, order]
    pca_dims = np.ptp(centered @ evecs, axis=0)
    positive = pca_dims[pca_dims > eps]
    aspect = float(positive.max() / positive.min()) if len(positive) else 0.0

    normals = np.asarray(part.face_normals)
    areas = np.asarray(part.area_faces)
    if len(normals) and areas.sum() > 0:
        q = np.round(np.abs(normals), 2)
        _, inv = np.unique(q, axis=0, return_inverse=True)
        bins = np.bincount(inv, weights=areas)
        planar_ratio = float(bins.max() / areas.sum())
        axis = evecs[:, 0]
        perp = np.abs(normals @ axis)
        cylindrical = float(np.average(perp < 0.25, weights=areas))
    else:
        planar_ratio = cylindrical = 0.0

    axis = evecs[:, 0]
    axial = centered @ axis
    radial = np.linalg.norm(centered - np.outer(axial, axis), axis=1)
    rmean = float(radial.mean()) if len(radial) else 0.0
    rotational = float(max(0.0, 1.0 - float(radial.std()) / (rmean + eps)))
    try:
        convexity = float(area / part.convex_hull.area) if part.convex_hull.area > 0 else 0.0
    except Exception:
        convexity = 0.0
    bbox_volume = float(np.prod(bsize))
    compactness = float((volume or 0.0) / bbox_volume) if bbox_volume > 0 else 0.0

    if watertight and cylindrical > 0.55 and rotational > 0.55:
        cls = "CYLINDER_LIKE"
    elif planar_ratio > 0.18 and aspect < 8.0 and cylindrical < 0.55:
        cls = "BOX_BOOLEAN_LIKE"
    elif rotational > 0.62 and cylindrical > 0.38:
        cls = "REVOLVE_LIKE"
    elif planar_ratio > 0.22 and aspect < 12:
        cls = "EXTRUDE_LIKE"
    elif (not watertight) and (planar_ratio > 0.16 or min(pca_dims) < 0.12 * max(pca_dims)):
        cls = "SHELL_LIKE"
    else:
        cls = "FREEFORM_LIKE"

    return part, {
        "part_vertex_count": int(len(vertices)), "part_face_count": int(len(faces)),
        "bbox_min": bmin.tolist(), "bbox_max": bmax.tolist(), "bbox_size": bsize.tolist(),
        "components": components, "watertight": watertight, "surface_area": area,
        "volume": volume, "bbox_aspect_ratio": aspect,
        "pca_eigenvalues": evals.tolist(), "pca_axes": evecs.T.tolist(),
        "planar_ratio": planar_ratio, "cylindrical_tendency": cylindrical,
        "rotational_symmetry_score": rotational, "convexity": convexity,
        "compactness": compactness, "coarse_class": cls, "valid_part": valid,
    }


def choose_pilot(rows, n=20):
    eligible = [r for r in rows if r["valid_part"] and r["part_face_count"] >= 100 and
                r["components"] >= 1 and min(r["bbox_size"]) > 1e-10]
    groups = [
        # Box candidates are intentionally selected first. Some open CAD-like
        # boxes are classified as extrusions, so use geometry evidence too.
        ("BOX_BOOLEAN_LIKE", lambda r: r["coarse_class"] == "BOX_BOOLEAN_LIKE" or
         (r["components"] == 1 and r["planar_ratio"] > 0.05 and r["bbox_aspect_ratio"] < 30.0)),
        ("EXTRUDE_LIKE", lambda r: r["coarse_class"] == "EXTRUDE_LIKE"),
        ("REVOLVE_CYLINDER_LIKE", lambda r: r["coarse_class"] in ("REVOLVE_LIKE", "CYLINDER_LIKE")),
        ("SHELL_LIKE", lambda r: r["coarse_class"] == "SHELL_LIKE"),
        ("HARDER_FREEFORM", lambda r: r["coarse_class"] == "FREEFORM_LIKE"),
    ]
    selected, used_keys, used_uids = [], set(), set()

    def score(r):
        quality = (2.0 if r["components"] == 1 else 0.0) + math.log10(r["part_face_count"] + 1)
        quality += 0.5 * r["convexity"] + 0.3 * r["planar_ratio"]
        return quality

    for bucket, predicate in groups:
        cand = sorted((r for r in eligible if predicate(r) and (r["object_uid"], r["instance_id"]) not in used_keys),
                      key=lambda r: (r["components"] != 1, -score(r), r["object_uid"], r["instance_id"]))
        picks = []
        for r in cand:
            if r["object_uid"] not in used_uids:
                picks.append(r)
                used_uids.add(r["object_uid"])
                if len(picks) == 4: break
        for r in cand:
            if len(picks) == 4: break
            if (r["object_uid"], r["instance_id"]) not in {(x["object_uid"], x["instance_id"]) for x in picks}:
                picks.append(r)
        for r in picks:
            key = (r["object_uid"], r["instance_id"])
            if key not in used_keys:
                x = dict(r); x["pilot_bucket"] = bucket
                selected.append(x); used_keys.add(key)

    # Backfill only if a heuristic class has fewer than four candidates.
    for r in sorted(eligible, key=lambda r: (r["object_uid"] in used_uids, -score(r), r["object_uid"], r["instance_id"])):
        if len(selected) >= n: break
        key = (r["object_uid"], r["instance_id"])
        if key not in used_keys:
            x = dict(r); x["pilot_bucket"] = "BACKFILL"
            selected.append(x); used_keys.add(key); used_uids.add(r["object_uid"])
    return selected[:n]


def write_csv(path: Path, rows, fields=None):
    rows = list(rows)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    args = ap.parse_args()
    root, out = args.data_root.resolve(), args.output_root.resolve()
    for d in DIRS: (out / d).mkdir(parents=True, exist_ok=True)

    glbs = sorted(root.rglob("*.glb")); gts = sorted(root.rglob("*.npy"))
    gm, nm = defaultdict(list), defaultdict(list)
    for p in glbs: gm[p.stem].append(p)
    for p in gts: nm[p.stem].append(p)
    matched = sorted(k for k in gm.keys() & nm.keys() if len(gm[k]) == len(nm[k]) == 1)
    missing = sorted(gm.keys() - nm.keys()); orphan = sorted(nm.keys() - gm.keys())
    duplicates = {k: {"glb": [str(x) for x in gm[k]], "gt": [str(x) for x in nm[k]]}
                  for k in gm.keys() | nm.keys() if len(gm[k]) > 1 or len(nm[k]) > 1}
    audit = {"experiment": "PARTOBJAVERSE_LLM_CAD_PILOT_V1", "data_root": str(root),
             "mesh_roots": sorted({str(p.parent) for p in glbs}), "gt_roots": sorted({str(p.parent) for p in gts}),
             "GLB_N": len(glbs), "GT_N": len(gts), "MATCHED_N": len(matched),
             "MISSING_GT_N": len(missing), "ORPHAN_GT_N": len(orphan),
             "matched_uids": matched, "missing_gt_uids": missing, "orphan_gt_uids": orphan,
             "duplicate_uids": duplicates}
    json_dump(out / "audit/DATASET_AUDIT.json", audit)
    (out / "audit/DATASET_AUDIT.md").write_text(
        "# Dataset audit\n\n" + "\n".join(f"- {k}: {audit[k]}" for k in ["data_root","mesh_roots","gt_roots","GLB_N","GT_N","MATCHED_N","MISSING_GT_N","ORPHAN_GT_N"]) +
        "\n\nOnly strict one-to-one basename matches are eligible.\n", encoding="utf-8")

    rows, object_results, mismatch = [], [], []
    log_path = out / "logs/stage_a.log"
    with log_path.open("w", encoding="utf-8", buffering=1) as log:
        for oi, uid in enumerate(matched, 1):
            mp, gp = gm[uid][0], nm[uid][0]
            try:
                mesh = load_mesh(mp)
                labels = np.asarray(np.load(gp)).reshape(-1)
                if len(labels) != len(mesh.faces):
                    mismatch.append({"object_uid": uid, "status": "FACE_GT_MISMATCH", "face_count": len(mesh.faces), "gt_count": len(labels)})
                    object_results.append(mismatch[-1]); log.write(f"{uid} FACE_GT_MISMATCH {len(mesh.faces)} {len(labels)}\n"); continue
                objdir = out / "split_parts" / uid; objdir.mkdir(parents=True, exist_ok=True)
                source_hash = sha256(mp); source_area = float(mesh.area)
                obj_rows = []
                for iid_raw in sorted(np.unique(labels).tolist()):
                    iid = int(iid_raw)
                    if iid < 0: continue
                    face_ids = np.flatnonzero(labels == iid)
                    sf = np.asarray(mesh.faces)[face_ids]
                    used = np.unique(sf)
                    remap = np.full(len(mesh.vertices), -1, dtype=np.int64); remap[used] = np.arange(len(used))
                    verts, faces = np.asarray(mesh.vertices)[used].copy(), remap[sf]
                    obj_path = objdir / f"part_{iid:03d}.obj"
                    export_exact_obj(verts, faces, obj_path)
                    part, st = mesh_stats(verts, faces)
                    rec = {"dataset": "PartObjaverse-Tiny", "object_uid": uid, "instance_id": iid,
                           "case_id": f"POBJ_{uid}_PART_{iid:03d}", "source_glb": str(mp), "source_gt": str(gp),
                           "source_face_count": int(len(mesh.faces)), "part_face_count": int(len(faces)),
                           "face_ratio": float(len(faces) / len(mesh.faces)),
                           "area_ratio": float(part.area / source_area) if source_area > 0 else None,
                           "part_obj": str(obj_path), "source_sha256": source_hash, "part_sha256": sha256(obj_path)}
                    rec.update(st); rows.append(rec); obj_rows.append(rec)
                json_dump(objdir / "manifest.json", {"object_uid": uid, "source_glb": str(mp), "source_gt": str(gp),
                          "source_face_count": int(len(mesh.faces)), "gt_count": int(len(labels)), "parts": obj_rows})
                object_results.append({"object_uid": uid, "status": "SPLIT_OK", "source_faces": int(len(mesh.faces)),
                                       "labeled_faces": int(np.sum(labels >= 0)), "parts": len(obj_rows),
                                       "exported_faces": int(sum(x["part_face_count"] for x in obj_rows))})
                log.write(f"[{oi}/{len(matched)}] {uid} SPLIT_OK parts={len(obj_rows)}\n")
            except Exception as e:
                object_results.append({"object_uid": uid, "status": "ERROR", "error": repr(e)})
                log.write(f"{uid} ERROR {e!r}\n{traceback.format_exc()}\n")

    with (out / "manifests/PART_MANIFEST.jsonl").open("w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n")
    csv_fields = ["dataset","object_uid","instance_id","case_id","source_glb","source_gt","source_face_count",
                  "part_face_count","part_vertex_count","face_ratio","area_ratio","bbox_min","bbox_max","bbox_size",
                  "components","watertight","surface_area","volume","bbox_aspect_ratio","planar_ratio",
                  "cylindrical_tendency","rotational_symmetry_score","pca_eigenvalues","pca_axes","convexity",
                  "compactness","coarse_class","valid_part","part_obj","source_sha256","part_sha256"]
    write_csv(out / "manifests/PART_MANIFEST.csv", rows, csv_fields)

    pilot = choose_pilot(rows)
    pilot_fields = ["case_id","object_uid","instance_id","pilot_bucket","coarse_class","part_obj","part_face_count",
                    "part_vertex_count","components","watertight","bbox_size","bbox_aspect_ratio","surface_area","volume",
                    "planar_ratio","cylindrical_tendency","rotational_symmetry_score","convexity","compactness"]
    write_csv(out / "manifests/PILOT20.csv", pilot, pilot_fields)
    for r in pilot:
        link = out / "selected_parts" / f'{r["case_id"]}.obj'
        if link.exists() or link.is_symlink(): link.unlink()
        try: link.symlink_to(Path(r["part_obj"]))
        except OSError: shutil.copy2(r["part_obj"], link)

    rng = random.Random(20260918)
    ok_objects = [r for r in object_results if r["status"] == "SPLIT_OK"]
    object_sample = rng.sample(ok_objects, min(5, len(ok_objects)))
    part_sample = rng.sample(rows, min(10, len(rows)))
    qa_objects = []
    for r in object_sample:
        qa_objects.append({**r, "pass": r["labeled_faces"] == r["exported_faces"]})
    qa_parts = []
    for r in part_sample:
        q = trimesh.load(r["part_obj"], process=False)
        passed = isinstance(q, trimesh.Trimesh) and len(q.faces) == r["part_face_count"] and len(q.vertices) == r["part_vertex_count"] and sha256(Path(r["part_obj"])) == r["part_sha256"]
        qa_parts.append({"case_id": r["case_id"], "obj": r["part_obj"], "expected_faces": r["part_face_count"],
                         "read_faces": int(len(q.faces)), "expected_vertices": r["part_vertex_count"], "read_vertices": int(len(q.vertices)), "pass": bool(passed)})
    systemic = len(mismatch) > 0
    split_pass = (not systemic and len(ok_objects) == len(matched) and len(pilot) == 20 and
                  all(x["pass"] for x in qa_objects + qa_parts))
    qa = {"seed": 20260918, "source_object_checks": qa_objects, "split_part_checks": qa_parts,
          "all_checks_pass": all(x["pass"] for x in qa_objects + qa_parts)}
    json_dump(out / "audit/SPOT_CHECKS.json", qa)
    (out / "audit/SPOT_CHECKS.md").write_text("# Deterministic spot checks\n\n" +
        f"- Seed: 20260918\n- Source objects checked: {len(qa_objects)}\n- Split parts checked: {len(qa_parts)}\n- All checks pass: {qa['all_checks_pass']}\n",
        encoding="utf-8")

    summary = {**{k:audit[k] for k in ["GLB_N","GT_N","MATCHED_N","MISSING_GT_N","ORPHAN_GT_N"]},
               "OBJECTS_SPLIT_N": len(ok_objects), "TOTAL_PART_N": len(rows),
               "VALID_PART_N": sum(bool(r["valid_part"]) for r in rows), "FACE_GT_MISMATCH_N": len(mismatch),
               "PILOT20_N": len(pilot), "classification_counts": dict(Counter(r["coarse_class"] for r in rows)),
               "pilot_bucket_counts": dict(Counter(r["pilot_bucket"] for r in pilot)),
               "object_results": object_results,
               "CURRENT_GATE": "STAGE_A_SPLIT_PASS" if split_pass else "STAGE_A_SPLIT_FAIL",
               "NEXT_ALLOWED_STAGE": "STAGE_B_LLM_CAD_PILOT20" if split_pass else "NONE"}
    json_dump(out / "reports/STAGE_A_SUMMARY.json", summary)
    (out / "reports/STAGE_A_SUMMARY.md").write_text("# Stage A summary\n\n" + "\n".join(
        f"- {k}: {summary[k]}" for k in ["GLB_N","GT_N","MATCHED_N","MISSING_GT_N","ORPHAN_GT_N","OBJECTS_SPLIT_N","TOTAL_PART_N","VALID_PART_N","FACE_GT_MISMATCH_N","PILOT20_N","classification_counts","pilot_bucket_counts","CURRENT_GATE","NEXT_ALLOWED_STAGE"]) + "\n", encoding="utf-8")

    print("PARTOBJAVERSE_LLM_CAD_PILOT_V1")
    print(f"DATA_ROOT={root}")
    print(f"MESH_ROOT={audit['mesh_roots']}")
    print(f"GT_ROOT={audit['gt_roots']}")
    for k in ["GLB_N","GT_N","MATCHED_N"]: print(f"{k}={summary[k]}")
    for k in ["OBJECTS_SPLIT_N","TOTAL_PART_N","VALID_PART_N","FACE_GT_MISMATCH_N","PILOT20_N"]: print(f"{k}={summary[k]}")
    print(f"PILOT20_MANIFEST={out / 'manifests/PILOT20.csv'}")
    print(f"SPLIT_ROOT={out / 'split_parts'}")
    print(f"PART_MANIFEST={out / 'manifests/PART_MANIFEST.jsonl'}")
    print(f"AUDIT_REPORT={out / 'audit/DATASET_AUDIT.json'}")
    print(f"CURRENT_GATE={summary['CURRENT_GATE']}")
    print(f"NEXT_ALLOWED_STAGE={summary['NEXT_ALLOWED_STAGE']}")
    return 0 if split_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
