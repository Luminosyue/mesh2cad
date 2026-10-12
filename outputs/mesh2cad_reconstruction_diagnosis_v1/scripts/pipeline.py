#!/usr/bin/env python3
"""PARTSAM_MESH2CAD_IOU_TOP1000_V1.

The source tree is treated as immutable.  Every artifact, including extracted
PartSAM face-label parts, is written below OUTPUT_ROOT.  The pipeline is
checkpointed per part and can be resumed safely.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


PARTSAM_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/partsam")
OUTPUT_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1")
MESH_DIR = PARTSAM_ROOT / "PartObjaverse-Tiny_mesh"
LABEL_DIR = PARTSAM_ROOT / "PartObjaverse-Tiny_instance_gt"
PYTHON = Path("/data/miniconda3/envs/cadfit-env/bin/python")
SEED = 20260918
SUPPORTED_SOURCE_EXTENSIONS = {".obj", ".stl", ".ply", ".glb"}
AUDIT_FIELDS = [
    "case_id", "object_id", "part_id", "mesh_path", "extension", "vertices", "faces",
    "connected_components", "watertight", "is_volume", "bbox_x", "bbox_y", "bbox_z",
    "bbox_diagonal", "surface_area", "volume", "centroid_x", "centroid_y", "centroid_z",
    "valid_mesh", "invalid_reason", "candidate_selected", "source_object_path", "label_path",
]
TOP_FIELDS = [
    "rank", "case_id", "object_id", "part_id", "source_mesh_path", "cad_code_path", "step_path",
    "reconstructed_mesh_path", "geometry_class", "cad_exec_pass", "step_reload_pass",
    "source_watertight", "recon_watertight", "iou64", "iou128", "iou256", "cd", "ncd",
    "hausdorff", "normal_consistency", "bbox_error", "centroid_error", "surface_area_error",
    "volume_error", "operation_count", "sketch_entity_count", "parameter_count", "quality_level",
]


def ensure_layout() -> None:
    for rel in ("audit", "candidates", "manifests", "top1000", "plots", "comparisons", "logs", "scripts"):
        (OUTPUT_ROOT / rel).mkdir(parents=True, exist_ok=True)


def clean_json(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): clean_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean_json(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, Path):
        return str(x)
    if isinstance(x, float) and not math.isfinite(x):
        return None
    return x


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(clean_json(obj), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            out = {}
            for key in fields:
                value = row.get(key, "")
                if isinstance(value, (dict, list, tuple)):
                    value = json.dumps(clean_json(value), separators=(",", ":"), ensure_ascii=False)
                if value is None:
                    value = "NA"
                out[key] = value
            w.writerow(out)
    os.replace(tmp, path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def source_inventory() -> list[dict[str, Any]]:
    rows = []
    for p in sorted(PARTSAM_ROOT.rglob("*")):
        if not p.is_file():
            continue
        st = p.stat()
        rows.append({
            "path": str(p), "relative_path": str(p.relative_to(PARTSAM_ROOT)), "size": st.st_size,
            "mtime_ns": st.st_mtime_ns, "sha256": sha256(p),
        })
    return rows


def source_guard(stage: str) -> None:
    path = OUTPUT_ROOT / "audit" / "source_inventory_before.json"
    current = source_inventory()
    if not path.exists():
        dump_json(path, {"stage": "before", "root": str(PARTSAM_ROOT), "files": current})
        return
    before = load_json(path)["files"]
    a = {(x["relative_path"], x["size"], x["sha256"]) for x in before}
    b = {(x["relative_path"], x["size"], x["sha256"]) for x in current}
    ok = a == b
    dump_json(OUTPUT_ROOT / "audit" / f"source_integrity_{stage}.json", {
        "stage": stage, "unchanged": ok, "before_file_count": len(a), "current_file_count": len(b),
        "removed_or_changed": sorted(a - b)[:100], "added_or_changed": sorted(b - a)[:100],
    })
    if not ok:
        raise RuntimeError("Source PartSAM tree changed; refusing to continue")


def case_id(object_id: str, part_id: int) -> str:
    return f"{object_id}_part_{part_id:03d}"


def _mesh_as_scene_geometry(path: Path):
    import trimesh

    # Geometry-only audit: decoding/copying embedded high-resolution textures
    # into every labeled submesh is unnecessary and can multiply RAM usage.
    scene = trimesh.load(path, force="scene", process=False, skip_materials=True)
    mesh = scene.to_geometry()
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"Could not concatenate scene geometry: {path}")
    return mesh


def audit_extract_one(label_path_str: str) -> list[dict[str, Any]]:
    import trimesh

    label_path = Path(label_path_str)
    object_id = label_path.stem
    object_path = MESH_DIR / f"{object_id}.glb"
    labels = np.load(label_path, allow_pickle=False)
    mesh = _mesh_as_scene_geometry(object_path)
    if labels.ndim != 1 or not np.issubdtype(labels.dtype, np.integer):
        raise ValueError(f"Invalid label array {label_path}: {labels.shape} {labels.dtype}")
    if len(labels) != len(mesh.faces):
        raise ValueError(f"Face-label mismatch {object_id}: {len(mesh.faces)} != {len(labels)}")
    rows: list[dict[str, Any]] = []
    for pid in np.unique(labels).astype(int):
        cid = case_id(object_id, pid)
        cdir = OUTPUT_ROOT / "candidates" / cid
        cdir.mkdir(parents=True, exist_ok=True)
        source_obj = cdir / "source.obj"
        ids = np.flatnonzero(labels == pid)
        part = mesh.submesh([ids], append=True, repair=False)
        if not isinstance(part, trimesh.Trimesh):
            raise TypeError(f"Submesh is not Trimesh: {cid}")
        part.remove_unreferenced_vertices()
        if not source_obj.exists():
            part.export(source_obj, file_type="obj", include_color=False)
        vertices = np.asarray(part.vertices)
        faces = np.asarray(part.faces)
        finite = bool(np.isfinite(vertices).all())
        area = float(part.area) if len(faces) else 0.0
        bounds = np.asarray(part.bounds) if len(vertices) else np.zeros((2, 3))
        ext = bounds[1] - bounds[0]
        diag = float(np.linalg.norm(ext))
        reasons = []
        if len(vertices) < 20:
            reasons.append("vertices_lt_20")
        if len(faces) < 20:
            reasons.append("faces_lt_20")
        if not finite:
            reasons.append("invalid_coordinates")
        if not math.isfinite(area) or area <= 1e-15:
            reasons.append("zero_area")
        if not math.isfinite(diag) or diag <= 1e-12:
            reasons.append("degenerate_bbox")
        # Avoid Trimesh.split/face_adjacency here.  Some GLBs are unwelded
        # triangle soups; materializing face components can consume tens of GB.
        # One edge pass gives topology and a sparse vertex graph gives the count.
        try:
            from scipy.sparse import coo_matrix
            from scipy.sparse.csgraph import connected_components
            if len(faces) == 0:
                components = 0
            else:
                edges = np.sort(np.vstack((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]])), axis=1)
                unique_edges, edge_counts = np.unique(edges, axis=0, return_counts=True)
                data = np.ones(len(unique_edges) * 2, dtype=np.uint8)
                rr = np.r_[unique_edges[:, 0], unique_edges[:, 1]]
                cc = np.r_[unique_edges[:, 1], unique_edges[:, 0]]
                graph = coo_matrix((data, (rr, cc)), shape=(len(vertices), len(vertices))).tocsr()
                components = int(connected_components(graph, directed=False, return_labels=False))
                topo_watertight = bool(np.all(edge_counts == 2))
        except Exception:
            components = -1
            topo_watertight = False
        signed_volume = float(np.einsum("ij,ij->i", vertices[faces[:, 0]], np.cross(vertices[faces[:, 1]], vertices[faces[:, 2]])).sum() / 6.0) if len(faces) else 0.0
        is_volume = bool(topo_watertight and abs(signed_volume) > 1e-15)
        volume = abs(signed_volume) if is_volume else None
        centroid = np.asarray(part.centroid) if len(vertices) else np.zeros(3)
        row = {
            "case_id": cid, "object_id": object_id, "part_id": pid, "mesh_path": str(source_obj),
            "extension": ".obj", "vertices": len(vertices), "faces": len(faces),
            "connected_components": components, "watertight": int(topo_watertight),
            "is_volume": int(is_volume), "bbox_x": float(ext[0]), "bbox_y": float(ext[1]),
            "bbox_z": float(ext[2]), "bbox_diagonal": diag, "surface_area": area, "volume": volume,
            "centroid_x": float(centroid[0]), "centroid_y": float(centroid[1]), "centroid_z": float(centroid[2]),
            "valid_mesh": int(not reasons), "invalid_reason": ";".join(reasons), "candidate_selected": 0,
            "source_object_path": str(object_path), "label_path": str(label_path),
        }
        dump_json(cdir / "source_provenance.json", {
            **row, "source_object_sha256": sha256(object_path), "label_sha256": sha256(label_path),
            "source_obj_sha256": sha256(source_obj), "source_face_ids_count": len(ids),
            "source_face_ids_sha256": hashlib.sha256(ids.astype(np.int64).tobytes()).hexdigest(),
            "coordinate_policy": "original_glb_scene_coordinates_no_normalization", "source_modified": False,
        })
        rows.append(row)
    return rows


def audit_extract(workers: int) -> None:
    ensure_layout()
    source_guard("audit_start")
    labels = sorted(LABEL_DIR.glob("*.npy"))
    rows: list[dict[str, Any]] = []
    errors = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(audit_extract_one, str(p)): p for p in labels}
        for i, fut in enumerate(as_completed(futs), 1):
            p = futs[fut]
            try:
                rows.extend(fut.result())
            except Exception as exc:
                errors.append({"label": str(p), "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
            if i % 10 == 0 or i == len(labels):
                print(f"AUDIT_OBJECTS={i}/{len(labels)} PARTS={len(rows)} ERRORS={len(errors)}", flush=True)
    rows.sort(key=lambda r: (r["object_id"], int(r["part_id"])))
    # Stratified deterministic selection: valid parts, CAD-likeness proxy, and broad complexity coverage.
    valid = [r for r in rows if int(r["valid_mesh"]) == 1]
    for r in valid:
        dims = np.sort(np.maximum([r["bbox_x"], r["bbox_y"], r["bbox_z"]], 1e-12))
        r["_score"] = float(math.log1p(int(r["faces"])) + 0.4 * math.log1p(int(r["vertices"])) - 0.15 * math.log1p(dims[-1] / dims[0]))
    by_object: dict[str, list[dict[str, Any]]] = {}
    for r in valid:
        by_object.setdefault(r["object_id"], []).append(r)
    for group in by_object.values():
        group.sort(key=lambda r: (-r["_score"], int(r["part_id"])))
    selected = []
    depth = 0
    target = min(2000, len(valid))
    objects = sorted(by_object)
    while len(selected) < target:
        added = False
        for obj in objects:
            if depth < len(by_object[obj]) and len(selected) < target:
                selected.append(by_object[obj][depth])
                added = True
        if not added:
            break
        depth += 1
    selected_ids = {r["case_id"] for r in selected}
    for r in rows:
        r["candidate_selected"] = int(r["case_id"] in selected_ids)
        r.pop("_score", None)
    write_csv(OUTPUT_ROOT / "audit" / "all_parts.csv", rows, AUDIT_FIELDS)
    dump_json(OUTPUT_ROOT / "audit" / "audit_summary.json", {
        "PARTSAM_ROOT": str(PARTSAM_ROOT), "TOTAL_SOURCE_OBJECT_N": len(labels), "TOTAL_PART_MESH_N": len(rows),
        "VALID_MESH_N": sum(int(r["valid_mesh"]) for r in rows),
        "INVALID_MESH_N": sum(not int(r["valid_mesh"]) for r in rows),
        "WATERTIGHT_N": sum(int(r["watertight"]) for r in rows),
        "NON_WATERTIGHT_N": sum(not int(r["watertight"]) for r in rows),
        "CANDIDATE_TARGET_N": target, "CANDIDATE_SELECTED_N": len(selected), "errors": errors,
    })
    source_guard("audit_end")
    if errors:
        raise RuntimeError(f"Audit had {len(errors)} object failures")


def normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n <= 1e-15:
        raise ValueError("zero vector")
    return np.asarray(v, float) / n


def basis_for_axis(axis: np.ndarray) -> np.ndarray:
    z = normalize(axis)
    ref = np.array([1.0, 0.0, 0.0]) if abs(z[0]) < 0.8 else np.array([0.0, 1.0, 0.0])
    x = normalize(np.cross(ref, z))
    y = normalize(np.cross(z, x))
    return np.column_stack([x, y, z])


def candidate_axes(mesh) -> list[np.ndarray]:
    v = np.asarray(mesh.vertices, float)
    center = v.mean(axis=0)
    _, _, vh = np.linalg.svd(v - center, full_matrices=False)
    raw = [np.eye(3)[i] for i in range(3)] + [vh[i] for i in range(3)]
    areas = np.asarray(mesh.area_faces)
    normals = np.asarray(mesh.face_normals)
    scored = []
    for a in raw:
        a = normalize(a)
        if a[np.argmax(np.abs(a))] < 0:
            a = -a
        if any(abs(float(np.dot(a, b))) > 0.995 for _, b in scored):
            continue
        dot = np.abs(normals @ a)
        cap = float(areas[dot > 0.94].sum() / max(areas.sum(), 1e-15))
        side = float(areas[dot < 0.16].sum() / max(areas.sum(), 1e-15))
        local = (v - center) @ basis_for_axis(a)
        ext = np.ptp(local, axis=0)
        compact = float(min(ext[0], ext[1]) / max(max(ext[0], ext[1]), 1e-15))
        score = 1.8 * min(cap * 2.0, 1.0) + side + 0.15 * compact
        scored.append((score, a))
    scored.sort(key=lambda x: -x[0])
    return [a for _, a in scored]


def polygon_area(points: np.ndarray) -> float:
    p = np.asarray(points, float)
    return 0.5 * float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - p[:, 1] * np.roll(p[:, 0], -1)))


def resample_loop(points: np.ndarray, n: int = 48) -> np.ndarray:
    p = np.asarray(points, float)
    if len(p) > 1 and np.linalg.norm(p[0] - p[-1]) < 1e-10:
        p = p[:-1]
    if len(p) < 3:
        raise ValueError("loop has fewer than 3 vertices")
    if polygon_area(p) < 0:
        p = p[::-1]
    q = np.vstack([p, p[:1]])
    seg = np.linalg.norm(np.diff(q, axis=0), axis=1)
    total = float(seg.sum())
    if total <= 1e-15:
        raise ValueError("zero perimeter loop")
    s = np.r_[0.0, np.cumsum(seg)]
    targets = np.linspace(0.0, total, n, endpoint=False)
    out = []
    for target in targets:
        i = min(int(np.searchsorted(s, target, side="right") - 1), len(seg) - 1)
        alpha = 0.0 if seg[i] == 0 else (target - s[i]) / seg[i]
        out.append(q[i] * (1.0 - alpha) + q[i + 1] * alpha)
    return np.asarray(out)


def align_loop(points: np.ndarray, previous: np.ndarray | None) -> np.ndarray:
    if previous is None:
        return points
    options = []
    for base in (points, points[::-1]):
        for k in range(len(points)):
            options.append(np.roll(base, k, axis=0))
    return min(options, key=lambda x: float(np.mean(np.sum((x - previous) ** 2, axis=1))))


def projected_profile(mesh, axis: np.ndarray, max_entities: int = 192) -> dict[str, Any]:
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    v = np.asarray(mesh.vertices, float)
    center = np.asarray(mesh.bounds).mean(axis=0)
    B = basis_for_axis(axis)
    local = (v - center) @ B
    triangles = local[np.asarray(mesh.faces), :2]
    polys = []
    for tri in triangles:
        p = Polygon(tri)
        if p.is_valid and p.area > 1e-18:
            polys.append(p)
    if not polys:
        raise ValueError("no valid projected triangles")
    geom = unary_union(polys)
    if not geom.is_valid:
        geom = geom.buffer(0)
    if geom.is_empty:
        raise ValueError("empty projected union")
    # Edge-on triangles have zero projected area and can otherwise make a
    # profile miss a true extreme.  Affinely match the retained silhouette to
    # the exact projected bounds (no independent CAD/source normalization; the
    # resulting profile is still constructed directly in the source frame).
    gb = np.asarray(geom.bounds, float)
    exact_min = local[:, :2].min(axis=0)
    exact_max = local[:, :2].max(axis=0)
    gspan = np.maximum(gb[2:] - gb[:2], 1e-15)
    exact_span = exact_max - exact_min
    from shapely.affinity import affine_transform
    sx, sy = exact_span / gspan
    geom = affine_transform(geom, [sx, 0.0, 0.0, sy, exact_min[0] - sx * gb[0], exact_min[1] - sy * gb[1]])
    span = float(max(np.ptp(local[:, 0]), np.ptp(local[:, 1])))
    tol = max(span * 2e-4, 1e-10)
    for _ in range(9):
        simp = geom.simplify(tol, preserve_topology=True)
        geoms = list(simp.geoms) if simp.geom_type == "MultiPolygon" else [simp]
        entities = sum(len(g.exterior.coords) - 1 + sum(len(h.coords) - 1 for h in g.interiors) for g in geoms)
        if entities <= max_entities:
            geom = simp
            break
        tol *= 1.7
    geoms = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    min_area = max(float(geom.area) * 1e-6, 1e-18)
    profiles = []
    for g in geoms:
        if g.area < min_area:
            continue
        outer = np.asarray(g.exterior.coords[:-1], float)
        holes = [np.asarray(h.coords[:-1], float) for h in g.interiors if Polygon(h).area >= min_area]
        profiles.append({"outer": outer.tolist(), "holes": [h.tolist() for h in holes]})
    if not profiles:
        raise ValueError("no retained profile polygons")
    return {
        "kind": "extrusion", "center": center.tolist(), "basis": B.tolist(), "axis": B[:, 2].tolist(),
        "zmin": float(local[:, 2].min()), "zmax": float(local[:, 2].max()), "profiles": profiles,
        "simplify_tolerance": tol, "sketch_entity_count": entities,
    }


def section_loft_profile(mesh, axis: np.ndarray, ruled: bool, section_count: int = 32, points_per_loop: int = 40) -> dict[str, Any]:
    from scipy.optimize import linear_sum_assignment
    from shapely.geometry import Point, Polygon

    v = np.asarray(mesh.vertices, float)
    center = np.asarray(mesh.bounds).mean(axis=0)
    B = basis_for_axis(axis)
    local = (v - center) @ B
    zmin, zmax = float(local[:, 2].min()), float(local[:, 2].max())
    span = zmax - zmin
    if span <= 1e-12:
        raise ValueError("zero loft span")
    tracks: dict[str, list[dict[str, Any]]] = {"outer": [], "hole": []}
    zs = np.linspace(zmin + 0.0015 * span, zmax - 0.0015 * span, section_count)
    cross_span = float(max(np.ptp(local[:, 0]), np.ptp(local[:, 1]), 1e-12))
    for section_index, z in enumerate(zs):
        sec = mesh.section(plane_origin=center + B[:, 2] * z, plane_normal=B[:, 2])
        loops = []
        if sec is not None:
            for d in sec.discrete:
                pts = (np.asarray(d) - center) @ B
                p2 = pts[:, :2]
                if len(p2) >= 4 and abs(polygon_area(p2)) > 1e-14:
                    loops.append(p2)
        if not loops:
            continue
        poly_rows = []
        for q in loops:
            try:
                poly = Polygon(q)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                if poly.is_empty or poly.geom_type != "Polygon":
                    continue
                poly_rows.append({"raw": q, "poly": poly, "area": float(abs(poly.area)), "center": np.asarray(poly.centroid.coords[0])})
            except Exception:
                continue
        poly_rows.sort(key=lambda x: -x["area"])
        classified = {"outer": [], "hole": []}
        for i, item in enumerate(poly_rows):
            point = Point(item["center"])
            depth = sum(1 for prior in poly_rows[:i] if prior["poly"].contains(point))
            typ = "hole" if depth % 2 else "outer"
            sampled = resample_loop(item["raw"], points_per_loop)
            classified[typ].append({"points": sampled, "center": sampled.mean(axis=0), "area": item["area"]})
        for typ in ("outer", "hole"):
            current = classified[typ]
            active_ids = [i for i, t in enumerate(tracks[typ]) if section_index - t["last_index"] <= 3]
            pairs = []
            if active_ids and current:
                cost = np.zeros((len(active_ids), len(current)), float)
                for ai, tid in enumerate(active_ids):
                    t = tracks[typ][tid]
                    for ci, item in enumerate(current):
                        dc = np.linalg.norm(t["last_center"] - item["center"]) / cross_span
                        da = abs(math.log(max(item["area"], 1e-15) / max(t["last_area"], 1e-15)))
                        cost[ai, ci] = dc + 0.12 * da
                rr, cc = linear_sum_assignment(cost)
                pairs = [(active_ids[int(a)], int(c)) for a, c in zip(rr, cc) if cost[a, c] <= 0.32]
            used = set()
            for tid, ci in pairs:
                item = current[ci]
                p = align_loop(item["points"], tracks[typ][tid]["last_points"])
                gp = center + p[:, 0, None] * B[:, 0] + p[:, 1, None] * B[:, 1] + z * B[:, 2]
                tracks[typ][tid]["sections"].append(gp.tolist())
                tracks[typ][tid].update({"last_index": section_index, "last_center": item["center"], "last_area": item["area"], "last_points": p})
                used.add(ci)
            for ci, item in enumerate(current):
                if ci in used:
                    continue
                p = item["points"]
                gp = center + p[:, 0, None] * B[:, 0] + p[:, 1, None] * B[:, 1] + z * B[:, 2]
                tracks[typ].append({"sections": [gp.tolist()], "last_index": section_index, "last_center": item["center"], "last_area": item["area"], "last_points": p})
    outer_rows = sorted((t for t in tracks["outer"] if len(t["sections"]) >= 4), key=lambda t: (-len(t["sections"]), -float(t["last_area"])))[:4]
    hole_rows = sorted((t for t in tracks["hole"] if len(t["sections"]) >= 4), key=lambda t: (-len(t["sections"]), -float(t["last_area"])))[:4]
    outer_tracks = [t["sections"] for t in outer_rows]
    hole_tracks = [t["sections"] for t in hole_rows]
    if not outer_tracks:
        raise ValueError("no loft outer track with >=4 sections")
    entities = points_per_loop * sum(len(t) for t in outer_tracks + hole_tracks)
    return {
        "kind": "multi_loft", "center": center.tolist(), "basis": B.tolist(), "axis": B[:, 2].tolist(),
        "zmin": zmin, "zmax": zmax, "outer_tracks": outer_tracks, "hole_tracks": hole_tracks,
        "ruled": ruled, "sketch_entity_count": entities,
    }


def primitive_profile(mesh, axis: np.ndarray, kind: str) -> dict[str, Any]:
    v = np.asarray(mesh.vertices, float)
    center = np.asarray(mesh.bounds).mean(axis=0)
    B = basis_for_axis(axis)
    local = (v - center) @ B
    mins, maxs = local.min(axis=0), local.max(axis=0)
    ext = maxs - mins
    if kind == "box":
        return {"kind": "box", "center": center.tolist(), "basis": B.tolist(), "mins": mins.tolist(), "maxs": maxs.tolist(), "sketch_entity_count": 4}
    radial = np.linalg.norm(local[:, :2] - 0.5 * (mins[:2] + maxs[:2]), axis=1)
    radius = float(np.quantile(radial, 0.99))
    return {"kind": "cylinder", "center": center.tolist(), "basis": B.tolist(), "zmin": float(mins[2]), "zmax": float(maxs[2]), "radius": radius, "sketch_entity_count": 1}


def cad_code(spec: dict[str, Any]) -> str:
    payload = repr(clean_json(spec))
    return f'''#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {payload}
OUT = Path(__file__).resolve().parent

def vec(v):
    return cq.Vector(float(v[0]), float(v[1]), float(v[2]))

def build():
    s = SPEC
    kind = s["kind"]
    B = s.get("basis")
    center = s.get("center")
    if kind == "extrusion":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["zmin"] * axis[i] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        result = None
        height = s["zmax"] - s["zmin"]
        for profile in s["profiles"]:
            solid = cq.Workplane(plane).polyline(profile["outer"]).close().extrude(height)
            for hole in profile["holes"]:
                cutter = cq.Workplane(plane).polyline(hole).close().extrude(height)
                solid = solid.cut(cutter)
            result = solid if result is None else result.union(solid)
    elif kind == "multi_loft":
        def loft(track):
            wires = [cq.Wire.makePolygon([vec(p) for p in section], close=True) for section in track]
            return cq.Solid.makeLoft(wires, ruled=bool(s.get("ruled", True)))
        outer = [loft(track) for track in s["outer_tracks"]]
        # Keep disjoint solids as a legal STEP compound.  Global Boolean fusion
        # is unnecessary for training geometry and scales poorly with profiles.
        for track in s.get("hole_tracks", []):
            cutter = loft(track)
            cut_outer = []
            for solid in outer:
                try:
                    cut_outer.append(solid.cut(cutter))
                except Exception:
                    cut_outer.append(solid)
            outer = cut_outer
        result = outer[0] if len(outer) == 1 else cq.Compound.makeCompound(outer)
    elif kind == "box":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["mins"][0]*B[i][0] + s["mins"][1]*B[i][1] + s["mins"][2]*B[i][2] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        dx=s["maxs"][0]-s["mins"][0]; dy=s["maxs"][1]-s["mins"][1]; dz=s["maxs"][2]-s["mins"][2]
        result = cq.Workplane(plane).rect(dx,dy,centered=False).extrude(dz)
    elif kind == "cylinder":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["zmin"] * axis[i] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        result = cq.Workplane(plane).circle(s["radius"]).extrude(s["zmax"]-s["zmin"])
    else:
        raise ValueError(kind)
    cq.exporters.export(result, str(OUT / "reconstructed.step"))
    cq.exporters.export(result, str(OUT / "reconstructed.stl"), tolerance=0.001, angularTolerance=0.05)
    return result

if __name__ == "__main__":
    build()
'''


def execute_cad(code_path: Path, timeout: int = 240) -> dict[str, Any]:
    out = code_path.parent
    result = {"cad_parse": False, "cad_execution": False, "step_export": False, "step_reload": False, "mesh_export": False, "error": None}
    try:
        ast.parse(code_path.read_text(encoding="utf-8"))
        py_compile.compile(str(code_path), doraise=True)
        result["cad_parse"] = True
        proc = subprocess.run([str(PYTHON), str(code_path)], cwd=out, text=True, capture_output=True, timeout=timeout)
        (out / "cad_execution.log").write_text(proc.stdout + "\n--- STDERR ---\n" + proc.stderr, encoding="utf-8")
        if proc.returncode != 0:
            raise RuntimeError(f"cad.py returned {proc.returncode}: {proc.stderr[-1000:]}")
        result["cad_execution"] = True
        step = out / "reconstructed.step"
        stl = out / "reconstructed.stl"
        result["step_export"] = step.is_file() and step.stat().st_size > 100
        result["mesh_export"] = stl.is_file() and stl.stat().st_size > 84
        if not result["step_export"] or not result["mesh_export"]:
            raise RuntimeError("missing or empty STEP/STL")
        from OCP.BRepCheck import BRepCheck_Analyzer
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        reader = STEPControl_Reader()
        if reader.ReadFile(str(step)) != IFSelect_RetDone:
            raise RuntimeError("STEP read failed")
        reader.TransferRoots()
        shape = reader.OneShape()
        result["step_reload"] = bool(not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())
        if not result["step_reload"]:
            raise RuntimeError("STEP BRep invalid")
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        (out / "cad_traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
    result["cad_valid"] = int(all(result[k] for k in ("cad_parse", "cad_execution", "step_export", "step_reload", "mesh_export")))
    return result


def _scan_fill(surface: np.ndarray, axis: int) -> np.ndarray:
    moved = np.moveaxis(surface, axis, 0)
    n = moved.shape[0]
    any_hit = moved.any(axis=0)
    first = np.argmax(moved, axis=0)
    last = n - 1 - np.argmax(moved[::-1], axis=0)
    idx = np.arange(n, dtype=np.int32).reshape((n,) + (1,) * (moved.ndim - 1))
    filled = (idx >= first[None, ...]) & (idx <= last[None, ...]) & any_hit[None, ...]
    return np.moveaxis(filled, 0, axis)


def voxel_occupancy(mesh, bmin: np.ndarray, pitch: float, shape: tuple[int, int, int]) -> np.ndarray:
    """Uniform non-watertight-tolerant occupancy on one explicitly shared grid.

    Surface triangles are rasterized after the same world-to-grid transform.
    Interior is the majority vote of X/Y/Z scan fills, unioned with the exact
    surface and a final 3-D hole fill.  This treats open sheets conservatively
    (one-voxel occupancy) while filling volumes supported along >=2 axes.
    """
    from scipy.ndimage import binary_fill_holes

    work = mesh.copy()
    work.vertices = (np.asarray(work.vertices, float) - bmin) / pitch
    vox = work.voxelized(pitch=1.0, method="subdivide")
    pts = np.asarray(vox.points)
    if not len(pts):
        raise ValueError("empty surface voxelization")
    ids = np.round(pts).astype(np.int64)
    keep = np.all((ids >= 0) & (ids < np.asarray(shape)), axis=1)
    ids = ids[keep]
    surface = np.zeros(shape, dtype=bool)
    surface[ids[:, 0], ids[:, 1], ids[:, 2]] = True
    fills = [_scan_fill(surface, axis=i) for i in range(3)]
    majority = (fills[0].astype(np.uint8) + fills[1].astype(np.uint8) + fills[2].astype(np.uint8)) >= 2
    return binary_fill_holes(surface | majority)


def voxel_iou(source, recon, resolution: int) -> tuple[float, int, int, float, int, int]:
    bounds = np.vstack([source.bounds, recon.bounds])
    bmin, bmax = bounds.min(axis=0), bounds.max(axis=0)
    max_extent = float(np.max(bmax - bmin))
    if max_extent <= 1e-15:
        raise ValueError("degenerate union bbox")
    pitch = max_extent / float(resolution - 4)
    bmin = bmin - 2.0 * pitch
    shape = tuple(int(math.ceil((bmax[i] - bmin[i]) / pitch)) + 3 for i in range(3))
    if max(shape) > resolution + 6:
        raise RuntimeError(f"unexpected voxel grid shape {shape}")
    a = voxel_occupancy(source, bmin, pitch, shape)
    b = voxel_occupancy(recon, bmin, pitch, shape)
    inter = int(np.logical_and(a, b).sum())
    union = int(np.logical_or(a, b).sum())
    if union <= 0:
        raise ValueError("empty voxel union")
    return inter / union, inter, union, pitch, int(a.sum()), int(b.sum())


def geometry_metrics(source, recon, samples: int = 18000) -> dict[str, Any]:
    import trimesh
    from scipy.spatial import cKDTree

    diag = float(np.linalg.norm(source.extents))
    if diag <= 1e-15:
        raise ValueError("degenerate source diagonal")
    sp, sf = trimesh.sample.sample_surface(source, samples, seed=SEED)
    rp, rf = trimesh.sample.sample_surface(recon, samples, seed=SEED + 1)
    st, rt = cKDTree(sp), cKDTree(rp)
    a, ia = rt.query(sp, workers=1)
    b, ib = st.query(rp, workers=1)
    sn, rn = source.face_normals[sf], recon.face_normals[rf]
    normal = 0.5 * (np.abs(np.sum(sn * rn[ia], axis=1)).mean() + np.abs(np.sum(rn * sn[ib], axis=1)).mean())
    cd = float(0.5 * (a.mean() + b.mean()))
    haus = float(max(a.max(), b.max()))
    bbox_error = float(np.max(np.abs(recon.extents - source.extents)) / diag)
    centroid_error = float(np.linalg.norm(recon.bounds.mean(axis=0) - source.bounds.mean(axis=0)) / diag)
    area_error = float(abs(recon.area - source.area) / max(source.area, 1e-15))
    return {
        "cd": cd, "ncd": cd / diag, "hausdorff": haus, "normalized_hausdorff": haus / diag,
        "normal_consistency": float(normal), "bbox_error": bbox_error, "centroid_error": centroid_error,
        "surface_area_error": area_error,
    }


def complexity_from_code(code: str, spec: dict[str, Any]) -> dict[str, int]:
    operations = sum(code.count(f".{name}(") for name in ("extrude", "revolve", "cut", "union", "intersect", "fillet", "chamfer"))
    if spec["kind"] == "multi_loft":
        operations += 1
    params = 0
    stack = [spec]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
        elif isinstance(x, (int, float)):
            params += 1
    return {"operation_count": operations, "sketch_entity_count": int(spec.get("sketch_entity_count", 0)), "parameter_count": params}


def evaluate_hypothesis(source, hdir: Path, spec: dict[str, Any]) -> dict[str, Any]:
    import trimesh

    hdir.mkdir(parents=True, exist_ok=True)
    code = cad_code(spec)
    (hdir / "cad.py").write_text(code, encoding="utf-8")
    dump_json(hdir / "parameters.json", spec)
    result = {"hypothesis": hdir.name, "geometry_class": spec["kind"], **complexity_from_code(code, spec)}
    result.update(execute_cad(hdir / "cad.py"))
    if not result["cad_valid"]:
        dump_json(hdir / "metrics.json", result)
        return result
    try:
        recon = trimesh.load(hdir / "reconstructed.stl", force="mesh", process=False)
        i64, inter, union, pitch, sv, rv = voxel_iou(source, recon, 64)
        result.update({"iou64": i64, "iou64_intersection": inter, "iou64_union": union, "iou64_pitch": pitch,
                       "iou64_source_occupancy": sv, "iou64_recon_occupancy": rv, "iou_valid": True})
    except Exception as exc:
        result.update({"iou_valid": False, "iou_failure_reason": f"{type(exc).__name__}: {exc}"})
    dump_json(hdir / "metrics.json", result)
    return result


def generate_specs(mesh) -> list[dict[str, Any]]:
    axes = candidate_axes(mesh)
    specs: list[dict[str, Any]] = []
    errors = []
    second = axes[1] if len(axes) > 1 else axes[0]
    jobs = (("extrusion", axes[0], None), ("loft", axes[0], True),
            ("extrusion", second, None), ("loft", second, True))
    for kind, axis, ruled in jobs:
        try:
            specs.append(projected_profile(mesh, axis) if kind == "extrusion" else section_loft_profile(mesh, axis, bool(ruled)))
        except Exception as exc:
            errors.append(f"{kind}: {type(exc).__name__}: {exc}")
    # Remove numerically duplicate specs while preserving order.
    out = []
    seen = set()
    for spec in specs[:4]:
        key = hashlib.sha256(json.dumps(clean_json(spec), sort_keys=True).encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            out.append(spec)
    if not out:
        raise RuntimeError("No CAD hypotheses generated: " + "; ".join(errors))
    return out


def render_overlay(source, recon, path: Path, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import trimesh

    def proj(points):
        az, el = np.radians(35.0), np.radians(22.0)
        rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
        rx = np.array([[1, 0, 0], [0, np.cos(el), -np.sin(el)], [0, np.sin(el), np.cos(el)]])
        q = np.asarray(points) @ (rz @ rx).T
        return q[:, [0, 2]]
    sp = trimesh.sample.sample_surface(source, min(8000, max(1500, len(source.faces) * 2)), seed=SEED)[0]
    rp = trimesh.sample.sample_surface(recon, min(8000, max(1500, len(recon.faces) * 2)), seed=SEED + 1)[0]
    sx, rx = proj(sp), proj(rp)
    fig, ax = plt.subplots(1, 3, figsize=(12, 4), dpi=120)
    ax[0].scatter(sx[:, 0], sx[:, 1], s=.25, c="#444444"); ax[0].set_title("SOURCE")
    ax[1].scatter(rx[:, 0], rx[:, 1], s=.25, c="#1976d2"); ax[1].set_title("CAD")
    ax[2].scatter(sx[:, 0], sx[:, 1], s=.2, c="#666666", alpha=.45)
    ax[2].scatter(rx[:, 0], rx[:, 1], s=.2, c="#e53935", alpha=.35); ax[2].set_title("OVERLAY")
    for a in ax:
        a.axis("off"); a.set_aspect("equal", adjustable="datalim")
    fig.suptitle(title); fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def fit_case(row: dict[str, str]) -> dict[str, Any]:
    import trimesh

    cid = row["case_id"]
    cdir = OUTPUT_ROOT / "candidates" / cid
    status_path = cdir / "status.json"
    old = load_json(status_path, {})
    required = [cdir / "source.obj", cdir / "cad.py", cdir / "reconstructed.step", cdir / "reconstructed.stl", cdir / "metrics.json", cdir / "parameters.json"]
    if old.get("state") == "COMPLETE" and all(p.exists() for p in required):
        return load_json(cdir / "metrics.json")
    started = time.time()
    status = {"case_id": cid, "state": "RUNNING", "started_unix": started, "attempt": int(old.get("attempt", 0)) + 1}
    dump_json(status_path, status)
    try:
        source = trimesh.load(cdir / "source.obj", force="mesh", process=True)
        specs = generate_specs(source)
        hroot = cdir / "_hypotheses"
        records = []
        for i, spec in enumerate(specs):
            records.append(evaluate_hypothesis(source, hroot / f"candidate_{i:02d}", spec))
        valid64 = [r for r in records if r.get("iou_valid") and r.get("iou64", 0.0) >= 0.50]
        valid64.sort(key=lambda r: (-float(r["iou64"]), int(r.get("operation_count", 999999))))
        for rec in valid64[:2]:
            hdir = hroot / rec["hypothesis"]
            recon = trimesh.load(hdir / "reconstructed.stl", force="mesh", process=True)
            i128, inter, union, pitch, sv, rv = voxel_iou(source, recon, 128)
            rec.update({"iou128": i128, "iou128_intersection": inter, "iou128_union": union, "iou128_pitch": pitch,
                        "iou128_source_occupancy": sv, "iou128_recon_occupancy": rv})
            rec.update(geometry_metrics(source, recon))
            rec["volume_error"] = float(abs(rv - sv) / max(sv, 1))
            dump_json(hdir / "metrics.json", rec)
        ranked = [r for r in records if r.get("iou128") is not None and r.get("cad_valid")]
        if not ranked:
            ranked = [r for r in records if r.get("iou_valid") and r.get("cad_valid")]
        if not ranked:
            raise RuntimeError("No valid CAD hypothesis")
        ranked.sort(key=lambda r: (-float(r.get("iou128", -1.0)), -float(r.get("iou64", -1.0)), int(r.get("operation_count", 999999))))
        best = ranked[0]
        hdir = hroot / best["hypothesis"]
        shutil.copy2(hdir / "cad.py", cdir / "cad.py")
        shutil.copy2(hdir / "parameters.json", cdir / "parameters.json")
        # Fresh execution in the final location; no candidate STEP/STL is copied.
        final_exec = execute_cad(cdir / "cad.py")
        if not final_exec["cad_valid"]:
            raise RuntimeError(f"Final CAD execution failed: {final_exec.get('error')}")
        recon = trimesh.load(cdir / "reconstructed.stl", force="mesh", process=True)
        i64, i64i, i64u, p64, sv64, rv64 = voxel_iou(source, recon, 64)
        i128, i128i, i128u, p128, sv128, rv128 = voxel_iou(source, recon, 128)
        metrics = {
            "case_id": cid, "object_id": row["object_id"], "part_id": int(row["part_id"]),
            "source_mesh_path": str(cdir / "source.obj"), "cad_code_path": str(cdir / "cad.py"),
            "step_path": str(cdir / "reconstructed.step"), "reconstructed_mesh_path": str(cdir / "reconstructed.stl"),
            "geometry_class": best["geometry_class"], **final_exec,
            "source_watertight": bool(source.is_watertight), "recon_watertight": bool(recon.is_watertight),
            "iou_valid": True, "iou64": i64, "iou128": i128, "iou256": None,
            "iou64_intersection": i64i, "iou64_union": i64u, "iou64_pitch": p64,
            "iou128_intersection": i128i, "iou128_union": i128u, "iou128_pitch": p128,
            "iou64_source_occupancy": sv64, "iou64_recon_occupancy": rv64,
            "iou128_source_occupancy": sv128, "iou128_recon_occupancy": rv128,
            **geometry_metrics(source, recon), "operation_count": best["operation_count"],
            "sketch_entity_count": best["sketch_entity_count"], "parameter_count": best["parameter_count"],
            "hypotheses_generated": len(records), "hypotheses": records,
            "coordinate_policy": "original_coordinate_system", "icp_used": False,
            "posthoc_alignment_used": False, "selected_by": "highest_valid_iou128_then_complexity",
        }
        metrics["volume_error"] = float(abs(rv128 - sv128) / max(sv128, 1))
        metrics["surface_area_error"] = float(abs(recon.area - source.area) / max(source.area, 1e-15))
        metrics["quality_level"] = "A" if i128 >= .95 else "B" if i128 >= .90 else "C" if i128 >= .80 else "D"
        metrics["hard_quality_pass"] = bool(i128 >= .90 and metrics["ncd"] <= .01 and metrics["bbox_error"] <= .03 and metrics["centroid_error"] <= .02)
        dump_json(cdir / "metrics.json", metrics)
        dump_json(cdir / "transform.json", {
            "normalization_used": False, "source_to_cad": np.eye(4).tolist(), "cad_to_source": np.eye(4).tolist(),
            "fitting_frame": load_json(cdir / "parameters.json", {}).get("basis"), "coordinate_policy": "original_coordinate_system",
        })
        render_overlay(source, recon, cdir / "overlay.png", f"{cid} | IoU128={i128:.4f} | {metrics['geometry_class']}")
        status.update({"state": "COMPLETE", "finished_unix": time.time(), "duration_seconds": time.time() - started, "hard_quality_pass": metrics["hard_quality_pass"]})
        dump_json(status_path, status)
        # Keep hypothesis code/metrics but prune bulky geometry after the winner is secured.
        for p in hroot.glob("candidate_*/*"):
            if p.name in {"reconstructed.step", "reconstructed.stl"}:
                p.unlink(missing_ok=True)
        return metrics
    except Exception as exc:
        status.update({"state": "FAILED", "finished_unix": time.time(), "duration_seconds": time.time() - started, "error": f"{type(exc).__name__}: {exc}"})
        dump_json(status_path, status)
        (cdir / "traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
        return {"case_id": cid, "object_id": row["object_id"], "part_id": int(row["part_id"]), "cad_valid": 0, "iou_valid": False, "failure_reason": status["error"]}


def rebuild_manifests() -> dict[str, Any]:
    ensure_layout()
    audit_rows = read_csv(OUTPUT_ROOT / "audit" / "all_parts.csv")
    selected = [r for r in audit_rows if r["candidate_selected"] == "1"]
    records = []
    for row in selected:
        cdir = OUTPUT_ROOT / "candidates" / row["case_id"]
        metrics = load_json(cdir / "metrics.json")
        status = load_json(cdir / "status.json", {})
        if metrics:
            records.append(metrics)
        elif status.get("state") == "FAILED":
            records.append({"case_id": row["case_id"], "object_id": row["object_id"], "part_id": int(row["part_id"]), "cad_valid": 0, "iou_valid": False, "failure_reason": status.get("error")})
    fields = sorted({k for r in records for k in r if k != "hypotheses"})
    write_csv(OUTPUT_ROOT / "manifests" / "all_candidates.csv", records, fields)
    valid = [r for r in records if r.get("cad_valid") and r.get("step_reload") and r.get("iou_valid")]
    write_csv(OUTPUT_ROOT / "manifests" / "valid_candidates.csv", valid, fields)
    rejected = [r for r in records if r not in valid or not r.get("hard_quality_pass")]
    write_csv(OUTPUT_ROOT / "manifests" / "rejected.csv", rejected, fields)
    ranked = sorted(valid, key=lambda r: (-float(r.get("iou128", -1)), int(r.get("operation_count", 999999))))
    write_csv(OUTPUT_ROOT / "manifests" / "ranked_by_iou.csv", ranked, fields)
    summary = {
        "selected_candidates": len(selected), "attempted": len(records), "complete": sum(load_json(OUTPUT_ROOT / "candidates" / r["case_id"] / "status.json", {}).get("state") == "COMPLETE" for r in selected),
        "failed": sum(load_json(OUTPUT_ROOT / "candidates" / r["case_id"] / "status.json", {}).get("state") == "FAILED" for r in selected),
        "cad_exec_pass": sum(bool(r.get("cad_valid")) for r in records), "iou_valid": sum(bool(r.get("iou_valid")) for r in records),
        "qualified": sum(bool(r.get("hard_quality_pass")) for r in records),
    }
    dump_json(OUTPUT_ROOT / "manifests" / "progress.json", summary)
    return summary


def fit_all(workers: int, limit: int | None, retry_failed: bool) -> None:
    ensure_layout()
    source_guard("fit_start")
    rows = [r for r in read_csv(OUTPUT_ROOT / "audit" / "all_parts.csv") if r["candidate_selected"] == "1"]
    todo = []
    for r in rows:
        state = load_json(OUTPUT_ROOT / "candidates" / r["case_id"] / "status.json", {}).get("state")
        if state == "COMPLETE":
            continue
        if state == "FAILED" and not retry_failed:
            continue
        todo.append(r)
    # Stable hash order prevents early canaries from over-representing one
    # source object while remaining deterministic across resumes.
    todo.sort(key=lambda r: hashlib.sha256(r["case_id"].encode("utf-8")).hexdigest())
    if limit is not None:
        todo = todo[:limit]
    print(f"FIT_TODO={len(todo)} WORKERS={workers}", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fit_case, r): r for r in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            r = futs[fut]
            try:
                m = fut.result()
                print(f"FIT {i}/{len(todo)} {r['case_id']} CAD={m.get('cad_valid')} IoU128={m.get('iou128')} PASS={m.get('hard_quality_pass')}", flush=True)
            except Exception as exc:
                print(f"FIT_WORKER_CRASH {r['case_id']} {type(exc).__name__}: {exc}", flush=True)
            if i % 10 == 0 or i == len(todo):
                print("PROGRESS", json.dumps(rebuild_manifests(), sort_keys=True), flush=True)
    source_guard("fit_end")


def duplicate_filter(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    # Conservative near-duplicate audit.  A rounded invariant descriptor only creates
    # candidate groups; source-mesh normalized Chamfer then confirms duplicates.
    import trimesh
    from scipy.spatial import cKDTree

    groups: dict[tuple, list[dict[str, Any]]] = {}
    for r in rows:
        src = trimesh.load(r["source_mesh_path"], force="mesh", process=False)
        e = np.sort(np.maximum(src.extents, 1e-15))
        ratio = e / e[-1]
        key = (round(float(ratio[0]), 2), round(float(ratio[1]), 2), round(float(src.area / max(np.linalg.norm(src.extents) ** 2, 1e-15)), 2))
        groups.setdefault(key, []).append(r)
    kept, removed = [], []
    for group in groups.values():
        group.sort(key=lambda r: (-float(r["iou128"]), int(r["operation_count"])))
        accepted_clouds = []
        for r in group:
            mesh = trimesh.load(r["source_mesh_path"], force="mesh", process=False)
            pts = trimesh.sample.sample_surface(mesh, 1800, seed=SEED)[0]
            center = mesh.bounds.mean(axis=0); scale = float(np.linalg.norm(mesh.extents))
            pts = (pts - center) / max(scale, 1e-15)
            duplicate_of = None
            for kr, kp in accepted_clouds:
                a = cKDTree(kp).query(pts, workers=1)[0].mean()
                b = cKDTree(pts).query(kp, workers=1)[0].mean()
                if 0.5 * (a + b) <= 0.003:
                    duplicate_of = kr["case_id"]
                    break
            if duplicate_of:
                removed.append({**r, "duplicate_of": duplicate_of})
            else:
                kept.append(r); accepted_clouds.append((r, pts))
    kept.sort(key=lambda r: (-float(r["iou128"]), int(r["operation_count"])))
    return kept, removed


def reproduce_one(row: dict[str, Any]) -> dict[str, Any]:
    import trimesh

    src = trimesh.load(row["source_mesh_path"], force="mesh", process=True)
    with tempfile.TemporaryDirectory(prefix="partsam_repro_", dir=str(OUTPUT_ROOT / "logs")) as td:
        d = Path(td)
        shutil.copy2(row["cad_code_path"], d / "cad.py")
        execution = execute_cad(d / "cad.py")
        if not execution["cad_valid"]:
            return {"case_id": row["case_id"], "pass": False, "reason": execution.get("error")}
        recon = trimesh.load(d / "reconstructed.stl", force="mesh", process=True)
        i128 = voxel_iou(src, recon, 128)[0]
        delta = abs(i128 - float(row["iou128"]))
        return {"case_id": row["case_id"], "pass": delta <= .005, "iou128_original": float(row["iou128"]), "iou128_reproduced": i128, "delta_iou": delta,
                "step_sha256": sha256(d / "reconstructed.step"), "stl_sha256": sha256(d / "reconstructed.stl")}


def final_plots(rows: list[dict[str, Any]]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    vals = np.array([float(r["iou128"]) for r in rows])
    ncd = np.array([float(r["ncd"]) for r in rows])
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150); ax.hist(vals, bins=35, color="#1976d2"); ax.set_xlabel("IoU128"); ax.set_ylabel("Count"); fig.tight_layout(); fig.savefig(OUTPUT_ROOT / "plots" / "iou_distribution.png"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150); ax.plot(np.arange(1, len(vals) + 1), vals, color="#d32f2f"); ax.set_xlabel("Rank"); ax.set_ylabel("IoU128"); ax.grid(alpha=.25); fig.tight_layout(); fig.savefig(OUTPUT_ROOT / "plots" / "iou_rank_curve.png"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150); ax.scatter(ncd, vals, s=8, alpha=.55); ax.set_xlabel("NCD"); ax.set_ylabel("IoU128"); fig.tight_layout(); fig.savefig(OUTPUT_ROOT / "plots" / "iou_vs_ncd.png"); plt.close(fig)
    levels = [sum(r["quality_level"] == q for r in rows) for q in "ABCD"]
    fig, ax = plt.subplots(figsize=(7, 5), dpi=150); ax.bar(list("ABCD"), levels, color=["#2e7d32", "#66bb6a", "#ffb300", "#d32f2f"]); ax.set_ylabel("Count"); fig.tight_layout(); fig.savefig(OUTPUT_ROOT / "plots" / "quality_breakdown.png"); plt.close(fig)


def copy_top(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out_rows = []
    for rank, row in enumerate(rows, 1):
        d = OUTPUT_ROOT / "top1000" / f"{rank:06d}"
        d.mkdir(parents=True, exist_ok=True)
        srcs = {
            "source.obj": Path(row["source_mesh_path"]), "cad.py": Path(row["cad_code_path"]),
            "reconstructed.step": Path(row["step_path"]), "reconstructed.stl": Path(row["reconstructed_mesh_path"]),
            "metrics.json": OUTPUT_ROOT / "candidates" / row["case_id"] / "metrics.json",
            "parameters.json": OUTPUT_ROOT / "candidates" / row["case_id"] / "parameters.json",
            "transform.json": OUTPUT_ROOT / "candidates" / row["case_id"] / "transform.json",
            "overlay.png": OUTPUT_ROOT / "candidates" / row["case_id"] / "overlay.png",
        }
        for name, src in srcs.items():
            if src.exists():
                shutil.copy2(src, d / name)
        nr = dict(row)
        nr.update({"rank": rank, "source_mesh_path": str(d / "source.obj"), "cad_code_path": str(d / "cad.py"), "step_path": str(d / "reconstructed.step"), "reconstructed_mesh_path": str(d / "reconstructed.stl")})
        out_rows.append(nr)
    return out_rows


def finalize(workers: int) -> None:
    ensure_layout()
    source_guard("finalize_start")
    rebuild_manifests()
    records = []
    for cdir in sorted((OUTPUT_ROOT / "candidates").iterdir()):
        m = load_json(cdir / "metrics.json")
        if m:
            records.append(m)
    qualified = [r for r in records if r.get("cad_valid") and r.get("step_reload") and r.get("iou_valid") and float(r.get("iou128", 0)) >= .90 and float(r.get("ncd", 99)) <= .01 and float(r.get("bbox_error", 99)) <= .03 and float(r.get("centroid_error", 99)) <= .02]
    deduped, duplicate_removed = duplicate_filter(qualified)
    write_csv(OUTPUT_ROOT / "manifests" / "duplicates_removed.csv", duplicate_removed, sorted({k for r in duplicate_removed for k in r}) if duplicate_removed else ["case_id", "duplicate_of"])
    # Reproduce beyond rank 1000 so failures can be backfilled without lowering quality.
    repro_pool = deduped[: min(len(deduped), 1100)]
    repro = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(reproduce_one, r): r for r in repro_pool}
        for i, fut in enumerate(as_completed(futs), 1):
            rr = fut.result(); repro.append(rr)
            if i % 25 == 0 or i == len(futs):
                print(f"REPRO={i}/{len(futs)} FAIL={sum(not x['pass'] for x in repro)}", flush=True)
    repro_map = {r["case_id"]: r for r in repro}
    dump_json(OUTPUT_ROOT / "manifests" / "reproducibility.json", repro)
    reproducible = [r for r in deduped if repro_map.get(r["case_id"], {}).get("pass")]
    selected = reproducible[:1000]
    if len(selected) == 1000:
        selected = copy_top(selected)
    fields = TOP_FIELDS
    for r in selected:
        r["cad_exec_pass"] = int(bool(r.get("cad_valid")))
        r["step_reload_pass"] = int(bool(r.get("step_reload")))
    write_csv(OUTPUT_ROOT / "manifests" / "top1000.csv", selected, fields)
    if selected:
        final_plots(selected)
    vals = np.array([float(r["iou128"]) for r in selected]) if selected else np.array([])
    ncds = np.array([float(r["ncd"]) for r in selected]) if selected else np.array([])
    failures = [r for r in records if not r.get("hard_quality_pass")]
    from collections import Counter
    causes = Counter((r.get("failure_reason") or ("iou_below_090" if float(r.get("iou128", 0) or 0) < .90 else "auxiliary_metric_gate")) for r in failures)
    audit = load_json(OUTPUT_ROOT / "audit" / "audit_summary.json")
    summary = {
        "PARTSAM_ROOT": str(PARTSAM_ROOT), "OUTPUT_ROOT": str(OUTPUT_ROOT), "TOTAL_PART_MESH_N": audit["TOTAL_PART_MESH_N"],
        "CANDIDATE_ATTEMPTED_N": len(records), "CAD_EXEC_PASS_N": sum(bool(r.get("cad_valid")) for r in records),
        "IOU_VALID_N": sum(bool(r.get("iou_valid")) for r in records),
        "IOU_GE_099_N": sum(float(r.get("iou128", 0) or 0) >= .99 for r in records),
        "IOU_GE_098_N": sum(float(r.get("iou128", 0) or 0) >= .98 for r in records),
        "IOU_GE_095_N": sum(float(r.get("iou128", 0) or 0) >= .95 for r in records),
        "IOU_GE_090_N": sum(float(r.get("iou128", 0) or 0) >= .90 for r in records),
        "QUALIFIED_N_BEFORE_DEDUP": len(qualified), "QUALIFIED_N_AFTER_DEDUP": len(deduped), "FINAL_SELECTED_N": len(selected),
        "TOP1000_IOU_MEAN": float(vals.mean()) if len(vals) else None, "TOP1000_IOU_MEDIAN": float(np.median(vals)) if len(vals) else None,
        "TOP1000_IOU_STD": float(vals.std()) if len(vals) else None, "TOP1000_IOU_MIN": float(vals.min()) if len(vals) else None,
        "TOP1000_IOU_MAX": float(vals.max()) if len(vals) else None,
        "TOP1000_IOU_P10": float(np.percentile(vals, 10)) if len(vals) else None, "TOP1000_IOU_P25": float(np.percentile(vals, 25)) if len(vals) else None,
        "TOP1000_IOU_P50": float(np.percentile(vals, 50)) if len(vals) else None, "TOP1000_IOU_P75": float(np.percentile(vals, 75)) if len(vals) else None,
        "TOP1000_IOU_P90": float(np.percentile(vals, 90)) if len(vals) else None, "TOP1000_IOU_P95": float(np.percentile(vals, 95)) if len(vals) else None,
        "TOP1000_NCD_MEAN": float(ncds.mean()) if len(ncds) else None, "TOP1000_NCD_MEDIAN": float(np.median(ncds)) if len(ncds) else None,
        "REPRODUCIBILITY_FAIL_N": sum(not r["pass"] for r in repro), "DUPLICATE_REMOVED_N": len(duplicate_removed),
        "PRIMARY_FAILURE_CAUSE": causes.most_common(1)[0][0] if causes else "NA",
        "CURRENT_GATE": "PARTSAM_CAD_IOU_TOP1000_COMPLETE" if len(selected) == 1000 else "PARTSAM_CAD_TOP1000_NOT_READY",
    }
    dump_json(OUTPUT_ROOT / "audit" / "final_summary.json", summary)
    top20 = selected[:20]
    bottom20 = selected[-20:] if selected else []
    median20 = selected[max(0, len(selected)//2-10):len(selected)//2+10]
    failures = sorted(failures, key=lambda r: float(r.get("iou128", -1) or -1), reverse=True)[:20]
    report = ["# PARTSAM Mesh2CAD IoU Top1000 V1", "", f"CURRENT_GATE={summary['CURRENT_GATE']}", "", "## Summary", ""]
    report += [f"- {k}={v}" for k, v in summary.items()]
    for title, group in (("Top 20 case", top20), ("20 around median", median20), ("Bottom 20 accepted case", bottom20), ("20 primary failure case", failures)):
        report += ["", f"## {title}", "", "| case_id | IoU128 | NCD | source | CAD | overlay |", "|---|---:|---:|---|---|---|"]
        for r in group:
            c = OUTPUT_ROOT / "candidates" / r["case_id"]
            report.append(f"| {r['case_id']} | {r.get('iou128','NA')} | {r.get('ncd','NA')} | {r.get('source_mesh_path', c/'source.obj')} | {r.get('reconstructed_mesh_path', c/'reconstructed.stl')} | {c/'overlay.png'} |")
    (OUTPUT_ROOT / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    source_guard("finalize_end")
    print(json.dumps(summary, indent=2), flush=True)


def status() -> None:
    ensure_layout()
    audit = load_json(OUTPUT_ROOT / "audit" / "audit_summary.json", {})
    progress = rebuild_manifests() if (OUTPUT_ROOT / "audit" / "all_parts.csv").exists() else {}
    final = load_json(OUTPUT_ROOT / "audit" / "final_summary.json", {})
    print(json.dumps({"audit": audit, "progress": progress, "final": final}, indent=2))


def main() -> None:
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("audit"); a.add_argument("--workers", type=int, default=12)
    f = sp.add_parser("fit"); f.add_argument("--workers", type=int, default=20); f.add_argument("--limit", type=int); f.add_argument("--retry-failed", action="store_true")
    z = sp.add_parser("finalize"); z.add_argument("--workers", type=int, default=20)
    sp.add_parser("status")
    args = p.parse_args()
    if args.cmd == "audit": audit_extract(args.workers)
    elif args.cmd == "fit": fit_all(args.workers, args.limit, args.retry_failed)
    elif args.cmd == "finalize": finalize(args.workers)
    else: status()


if __name__ == "__main__":
    main()
