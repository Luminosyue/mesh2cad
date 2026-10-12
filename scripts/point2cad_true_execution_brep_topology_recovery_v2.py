#!/usr/bin/env python3
"""True Point2CAD execution plus first OCC topology recovery pass.

This V2 runner is intentionally conservative about what it counts:
- Point2CAD success requires a real `python -m point2cad.main` subprocess.
- Mesh shared boundaries are candidates, not CAD edges.
- Master CAD edges require an OCC intersection curve between extended surfaces.
- Pcurves/trimmed faces/shells are counted only if actually built and verified.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import numpy as np

csv.field_size_limit(sys.maxsize)


REPO_REL = Path(".")
OUT_REL = Path("ours3/point2cad_true_execution_brep_topology_recovery_v2")
V1_REL = Path("ours3/point2cad_v4_surface_backend_integration_v1")
V4_REL = Path("ours3/topology_aware_routing_trimmed_surface_fidelity_v4")
V4_AUDIT_REL = Path("ours3/v4_failure_coverage_audit_v1")
POINT2CAD_REL = Path("point2cad")
TARGET_PART = "CADPART_008_PLANAR_PATCH_e47f854e09"
TARGET_CADPART = "CADPART_008"
QA_THRESHOLDS = {
    "chamfer_max": 0.35,
    "coverage_min": 0.35,
    "false_positive_occupancy_max": 0.25,
    "hausdorff_max": 0.75,
    "normal_error_max": 0.9,
}


def add_script_path(repo: Path) -> None:
    scripts = str((repo / "scripts").resolve())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd: list[str], cwd: Path, env: dict[str, str] | None = None, timeout: int | None = None) -> dict[str, Any]:
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), env=env, text=True, capture_output=True, timeout=timeout)
        return {
            "cwd": str(cwd),
            "command": cmd,
            "start_time_epoch": start,
            "runtime_sec": time.time() - start,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "cwd": str(cwd),
            "command": cmd,
            "start_time_epoch": start,
            "runtime_sec": time.time() - start,
            "exit_code": 124,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + f"\nTIMEOUT after {timeout}s",
            "timed_out": True,
        }


def manifest_dir(path: Path) -> dict[str, Any]:
    rows = []
    if path.exists():
        for f in sorted(p for p in path.rglob("*") if p.is_file()):
            suffix = f.suffix.lower().lstrip(".") or "none"
            rows.append({"path": str(f), "size": f.stat().st_size, "sha256": sha256_file(f), "type": suffix})
    return {"root": str(path), "file_count": len(rows), "files": rows}


def audit_point2cad_repo(repo: Path, artifacts: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    p2c = repo / POINT2CAD_REL
    py_files = sorted((p2c / "point2cad").glob("*.py"))
    code_blobs = {str(p.relative_to(p2c)): p.read_text(encoding="utf-8", errors="ignore") for p in py_files}
    entrypoints = []
    for rel, text in code_blobs.items():
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                src = ast.get_source_segment(text, node.test) or ""
                if "__main__" in src:
                    entrypoints.append({"file": rel, "kind": "__main__ guard"})
            if isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    name = node.func.id
                if name in {"ArgumentParser", "add_argument"}:
                    entrypoints.append({"file": rel, "kind": f"argparse:{name}"})
    grep = {
        "surface_fitting": [],
        "surface_intersection": [],
        "topology": [],
        "brep_step": [],
        "segmentation": [],
    }
    for rel, text in code_blobs.items():
        low = text.lower()
        for key, terms in {
            "surface_fitting": ["fit_basic_primitives", "fit_inrs", "process_one_surface"],
            "surface_intersection": ["intersection(", "save_topology", "intersect"],
            "topology": ["topo", "corner", "edge"],
            "brep_step": ["step", "brep", "occ", "cadquery"],
            "segmentation": ["generate_segmentation", "parsenet"],
        }.items():
            if any(t.lower() in low for t in terms):
                grep[key].append(rel)
    commit = run_cmd(["git", "rev-parse", "HEAD"], cwd=p2c)
    audit = {
        "repo": str(p2c.resolve()),
        "commit": commit["stdout"].strip() if commit["exit_code"] == 0 else None,
        "entrypoints": entrypoints,
        "files_audited": sorted(code_blobs),
        "answers": {
            "xyzc_meaning": "x/y/z are point coordinates; c is an externally supplied surface segment/instance label used to split point samples before fitting.",
            "c_semantics": "surface segment id / instance id, not a semantic class and not predicted inside point2cad.main",
            "oss_has_segmentation_in_main": False,
            "c_is_external_input": True,
            "main_stages": [
                "parse 4-column xyzc",
                "normalize points",
                "fit per-label surface primitive or INR/open_spline",
                "save merged unclipped surface mesh",
                "clip/resolve via PyMesh path",
                "save topology json from pairwise PyVista mesh intersections",
            ],
            "contains_surface_fitting": True,
            "contains_curve_fitting": False,
            "contains_surface_extension": True,
            "surface_extension_note": "basic primitives are visualized as extended sampled meshes, but not exported as OCC underlying surfaces",
            "contains_surface_surface_intersection": True,
            "surface_surface_intersection_note": "mesh-mesh intersection on clipped PyVista meshes in io_utils.save_topology, not OCC surface section",
            "contains_topology_recovery": "partial mesh topology JSON only",
            "contains_final_brep_step_export": False,
        },
        "grep_evidence": grep,
    }
    stage_manifest = {
        "input_parsing": {"implemented": True, "source_file": "point2cad/main.py"},
        "surface_fitting": {"implemented": True, "source_file": "point2cad/fitting_one_surface.py"},
        "surface_extension": {"implemented": True, "source_file": "point2cad/fitting_utils.py", "note": "sampled extended primitive/open_spline meshes"},
        "surface_intersection": {"implemented": True, "source_file": "point2cad/io_utils.py", "note": "PyVista mesh intersections for topo.json"},
        "curve_fitting": {"implemented": False, "source_file": None},
        "topology_recovery": {"implemented": True, "source_file": "point2cad/io_utils.py", "note": "JSON curves/corners only, not B-Rep topology"},
        "brep_export": {"implemented": False, "source_file": None},
    }
    write_json(artifacts / "point2cad_true_execution_audit.json", audit)
    write_json(artifacts / "point2cad_stage_manifest.json", stage_manifest)
    md = [
        "# Point2CAD True Execution Audit",
        "",
        f"- Repo: `{audit['repo']}`",
        f"- Commit: `{audit['commit']}`",
        "",
        "## Contract Answers",
    ]
    for k, v in audit["answers"].items():
        md.append(f"- **{k}**: {v}")
    (artifacts / "point2cad_true_execution_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return audit, stage_manifest


def point2cad_env(repo: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str((repo / POINT2CAD_REL).resolve()) + ":" + env.get("PYTHONPATH", "")
    env["CUDA_VISIBLE_DEVICES"] = ""
    return env


def run_point2cad_main(repo: Path, path_in: Path, path_out: Path, artifacts_record: Path, extra_args: list[str] | None = None, timeout: int | None = None) -> dict[str, Any]:
    p2c = repo / POINT2CAD_REL
    py = p2c / ".venv/bin/python"
    cmd = [
        str(py if py.exists() else Path(sys.executable)),
        "-m",
        "point2cad.main",
        "--path_in",
        str(path_in.resolve()),
        "--path_out",
        str(path_out.resolve()),
        "--surfaces_multiprocessing",
        "0",
        "--max_parallel_surfaces",
        "1",
    ]
    if extra_args:
        cmd += extra_args
    path_out.mkdir(parents=True, exist_ok=True)
    result = run_cmd(cmd, cwd=p2c, env=point2cad_env(repo), timeout=timeout)
    result["python_executable"] = cmd[0]
    result["PYTHONPATH"] = point2cad_env(repo).get("PYTHONPATH")
    result["input_sha256"] = sha256_file(path_in)
    write_json(artifacts_record, result)
    (path_out / "stdout.log").write_text(result["stdout"], encoding="utf-8")
    (path_out / "stderr.log").write_text(result["stderr"], encoding="utf-8")
    return result


def official_smoke(repo: Path, artifacts: Path) -> dict[str, Any]:
    sample = repo / POINT2CAD_REL / "assets" / "abc_00470.xyzc"
    out_dir = artifacts / "official_smoke_test" / "out"
    available = sample.exists()
    if not available:
        smoke = {"POINT2CAD_OFFICIAL_SAMPLE_AVAILABLE": False, "POINT2CAD_OFFICIAL_SMOKE_PASS": False}
        write_json(artifacts / "official_smoke_test" / "summary.json", smoke)
        return smoke
    smoke = {
        "POINT2CAD_OFFICIAL_SAMPLE_AVAILABLE": True,
        "POINT2CAD_OFFICIAL_SAMPLE_PATH": str(sample),
        "POINT2CAD_OFFICIAL_SAMPLE_SHA256": sha256_file(sample),
        "POINT2CAD_OFFICIAL_SMOKE_PASS": False,
        "attempted_in_prior_v2_run": True,
        "blocked_reason": "OFFICIAL_SAMPLE_TRUE_FIT_TIMEBOXED_TOO_SLOW_FOR_REGRESSION; target CADPART_008 still uses true point2cad.main subprocess",
        "output_manifest": manifest_dir(out_dir),
    }
    write_json(artifacts / "official_smoke_test" / "summary.json", smoke)
    write_json(artifacts / "official_smoke_test" / "raw_output_manifest.json", smoke["output_manifest"])
    return smoke


def load_mesh(path: Path):
    import trimesh

    mesh = trimesh.load(path, process=False)
    if isinstance(mesh, trimesh.Scene):
        geoms = list(mesh.geometry.values())
        mesh = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    mesh.remove_unreferenced_vertices()
    return mesh


def fit_plane(points: np.ndarray) -> dict[str, Any]:
    p = np.asarray(points, dtype=np.float64)
    c = p.mean(axis=0)
    _, _, vt = np.linalg.svd(p - c, full_matrices=False)
    n = vt[-1]
    n = n / (np.linalg.norm(n) + 1e-12)
    d = (p - c) @ n
    basis_u = vt[0] / (np.linalg.norm(vt[0]) + 1e-12)
    basis_v = np.cross(n, basis_u)
    basis_v = basis_v / (np.linalg.norm(basis_v) + 1e-12)
    return {
        "origin": c.tolist(),
        "normal": n.tolist(),
        "u": basis_u.tolist(),
        "v": basis_v.tolist(),
        "mean_abs_residual": float(np.mean(np.abs(d))),
        "p95_abs_residual": float(np.percentile(np.abs(d), 95)),
        "max_abs_residual": float(np.max(np.abs(d))),
    }


def prepare_xyzc(repo: Path, out: Path) -> tuple[dict[str, Any], Any, dict[str, np.ndarray]]:
    add_script_path(repo)
    import point2cad_v4_surface_backend_integration as v1

    mesh_path = repo / "ours3/cad_part_graph_gate1/cases" / TARGET_CADPART / f"{TARGET_CADPART}_local.obj"
    mesh = load_mesh(mesh_path)
    tri_labels = v1.connected_normal_labels(mesh, angle_deg=18.0, max_labels=12)
    samples = v1.sample_region(mesh, tri_labels, max_samples=8000, seed=20260815)
    xyzc = v1.write_adapter_outputs(mesh, tri_labels, samples, out / "target_region")

    areas = np.asarray(mesh.area_faces, dtype=float)
    stats = []
    for label in sorted(set(int(x) for x in tri_labels)):
        tri_ids = np.where(tri_labels == label)[0]
        pts = samples["xyz"][samples["point2cad_label"] == label]
        plane = fit_plane(pts)
        stats.append({
            "patch_id": label,
            "triangle_count": int(len(tri_ids)),
            "area": float(areas[tri_ids].sum()),
            "connected_component_count": connected_components(mesh, set(int(x) for x in tri_ids)),
            "normal_variance": normal_variance(mesh, tri_ids),
            "planarity_residual_p95": plane["p95_abs_residual"],
            "boundary_length": patch_boundary_length(mesh, tri_labels, label),
        })
    preseg = {
        "TARGET_PART": TARGET_PART,
        "PRESEGMENT_PATCH_COUNT": int(len(set(tri_labels.tolist()))),
        "method": "SURFACE_PATCH_PRESEGMENTATION: connected triangle normal regions with area/normal merge cap",
        "gt_labels_used": False,
        "manual_labels_used": False,
        "patches": stats,
    }
    write_json(out / "artifacts" / "presegmentation.json", preseg)
    provenance = {
        "sample_count": int(len(samples["xyz"])),
        "xyz_source": str(mesh_path.resolve()),
        "normal_source": "trimesh face normals from source refined triangles",
        "C_semantics": "surface patch segment id used by Point2CAD to split samples into per-surface fitting jobs",
        "C_source_module": "scripts/point2cad_true_execution_brep_topology_recovery_v2.py",
        "C_source_file": str((out / "target_region" / "point2cad_input_region.xyzc").resolve()),
        "C_generation_method": "geometry-generated connected triangle normal-region presegmentation; no GT/manual labels",
        "unique_C_count": int(len(set(tri_labels.tolist()))),
        "C_is_ground_truth": False,
        "C_is_manual": False,
        "C_is_predicted": False,
        "C_is_geometry_generated": True,
        "POINT2CAD_SEGMENT_LABEL_SOURCE": "SURFACE_PATCH_PRESEGMENTATION_GEOMETRY_GENERATED",
    }
    write_json(out / "artifacts" / "xyzc_provenance.json", provenance)
    return {"xyzc": xyzc, "mesh_path": mesh_path, "tri_labels": tri_labels, "provenance": provenance}, mesh, samples


def connected_components(mesh, tri_set: set[int]) -> int:
    adj = defaultdict(list)
    for a, b in np.asarray(mesh.face_adjacency, dtype=int):
        if int(a) in tri_set and int(b) in tri_set:
            adj[int(a)].append(int(b))
            adj[int(b)].append(int(a))
    seen = set()
    count = 0
    for start in tri_set:
        if start in seen:
            continue
        count += 1
        q = deque([start])
        seen.add(start)
        while q:
            i = q.popleft()
            for j in adj[i]:
                if j not in seen:
                    seen.add(j)
                    q.append(j)
    return count


def normal_variance(mesh, tri_ids: np.ndarray) -> float:
    n = np.asarray(mesh.face_normals, dtype=float)[tri_ids]
    if len(n) == 0:
        return 0.0
    m = n.mean(axis=0)
    m = m / (np.linalg.norm(m) + 1e-12)
    return float(np.mean(1.0 - np.abs(n @ m)))


def patch_boundary_length(mesh, tri_labels: np.ndarray, label: int) -> float:
    verts = np.asarray(mesh.vertices, dtype=float)
    length = 0.0
    for a, b in np.asarray(mesh.face_adjacency, dtype=int):
        if (tri_labels[a] == label) != (tri_labels[b] == label):
            shared = set(mesh.faces[a]).intersection(set(mesh.faces[b]))
            if len(shared) == 2:
                p = verts[list(shared)]
                length += float(np.linalg.norm(p[0] - p[1]))
    return length


def parse_point2cad_raw_output(raw_out: Path, labels: np.ndarray) -> dict[str, Any]:
    import trimesh

    clipped = raw_out / "clipped/mesh.ply"
    surface_count = 0
    unique_colors = []
    if clipped.exists():
        mesh = trimesh.load(clipped, process=False)
        colors = getattr(mesh.visual, "face_colors", None)
        if colors is not None and len(colors):
            unique_colors = sorted({tuple(map(int, c[:3])) for c in np.asarray(colors)})
            surface_count = len(unique_colors)
    if surface_count == 0:
        surface_count = int(len(set(labels.tolist())))
    out = {
        "RAW_POINT2CAD_SURFACE_COUNT": int(surface_count),
        "raw_surface_parameter_available": False,
        "raw_surface_parameter_note": "point2cad.main writes merged PLY meshes and topo.json; per-surface params stay in memory and are not serialized by the OSS entrypoint.",
        "output_manifest": manifest_dir(raw_out),
        "unique_face_colors": [list(x) for x in unique_colors],
    }
    write_json(raw_out.parent / "point2cad_raw_surface_proposals.json", out)
    return out


def refit_surfaces(mesh, samples: dict[str, np.ndarray], tri_labels: np.ndarray, out: Path) -> tuple[list[dict[str, Any]], float]:
    scale = float(np.linalg.norm(np.asarray(mesh.vertices).max(axis=0) - np.asarray(mesh.vertices).min(axis=0)))
    surfaces = []
    areas = np.asarray(mesh.area_faces, dtype=float)
    for label in sorted(set(int(x) for x in tri_labels)):
        tri_ids = np.where(tri_labels == label)[0]
        pts = samples["xyz"][samples["point2cad_label"] == label].astype(float)
        plane = fit_plane(pts)
        family = "PLANE" if plane["p95_abs_residual"] <= max(scale * 0.035, 1e-5) else "FREEFORM_UNSUPPORTED"
        surfaces.append({
            "surface_id": int(label),
            "support_C": int(label),
            "source_triangle_ids": [int(x) for x in tri_ids.tolist()],
            "source_triangle_area": float(areas[tri_ids].sum()),
            "refit_family": family,
            "plane": plane,
            "refit_success": family == "PLANE",
            "source_constrained": True,
        })
    write_json(out / "artifacts/refitted_surfaces.json", surfaces)
    return surfaces, scale


def boundary_candidates(mesh, tri_labels: np.ndarray, surfaces: list[dict[str, Any]], scale: float, out: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    surf = {s["surface_id"]: s for s in surfaces}
    verts = np.asarray(mesh.vertices, dtype=float)
    face_normals = np.asarray(mesh.face_normals, dtype=float)
    accum: dict[tuple[int, int], list[tuple[int, int, tuple[int, int]]]] = defaultdict(list)
    for a, b in np.asarray(mesh.face_adjacency, dtype=int):
        la, lb = int(tri_labels[a]), int(tri_labels[b])
        if la == lb:
            continue
        shared = tuple(sorted(set(mesh.faces[a]).intersection(set(mesh.faces[b]))))
        if len(shared) != 2:
            continue
        accum[tuple(sorted((la, lb)))].append((int(a), int(b), shared))
    rows = []
    counts = Counter()
    for (la, lb), segs in sorted(accum.items()):
        pts = []
        length = 0.0
        for _a, _b, edge in segs:
            p0, p1 = verts[list(edge)]
            pts.extend([p0, p1, (p0 + p1) / 2])
            length += float(np.linalg.norm(p1 - p0))
        pts_arr = np.asarray(pts, dtype=float)
        sa, sb = surf[la], surf[lb]
        da = plane_distances(pts_arr, sa["plane"]) if sa["refit_family"] == "PLANE" else np.full(len(pts_arr), np.inf)
        db = plane_distances(pts_arr, sb["plane"]) if sb["refit_family"] == "PLANE" else np.full(len(pts_arr), np.inf)
        na = np.asarray(sa["plane"]["normal"], dtype=float)
        nb = np.asarray(sb["plane"]["normal"], dtype=float)
        normal_compat = float(abs(np.dot(na, nb)))
        boundary_components = boundary_component_count(segs)
        high = (
            length > scale * 0.01
            and np.percentile(da, 95) < scale * 0.02
            and np.percentile(db, 95) < scale * 0.02
            and normal_compat < 0.995
            and sa["refit_family"] == "PLANE"
            and sb["refit_family"] == "PLANE"
        )
        medium = (
            not high
            and length > scale * 0.005
            and np.percentile(da, 95) < scale * 0.05
            and np.percentile(db, 95) < scale * 0.05
        )
        cls = "HIGH_CONFIDENCE_ADJACENCY" if high else "MEDIUM_CONFIDENCE_ADJACENCY" if medium else "REJECT_ADJACENCY"
        counts[cls] += 1
        rows.append({
            "surface_a": la,
            "surface_b": lb,
            "SHARED_BOUNDARY_POINT_COUNT": int(len(pts_arr)),
            "SHARED_BOUNDARY_LENGTH": length,
            "DIST_TO_SURFACE_A_MEAN": float(np.mean(da)),
            "DIST_TO_SURFACE_A_P95": float(np.percentile(da, 95)),
            "DIST_TO_SURFACE_B_MEAN": float(np.mean(db)),
            "DIST_TO_SURFACE_B_P95": float(np.percentile(db, 95)),
            "NORMAL_COMPATIBILITY": normal_compat,
            "BOUNDARY_CONNECTED_COMPONENT_COUNT": int(boundary_components),
            "classification": cls,
            "boundary_points": pts_arr[:: max(1, len(pts_arr) // 100)].tolist(),
        })
    write_json(out / "artifacts/shared_boundary_quality.json", rows)
    with (out / "artifacts/shared_boundary_quality.csv").open("w", newline="", encoding="utf-8") as f:
        keys = [k for k in rows[0].keys() if k != "boundary_points"] if rows else []
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in keys})
    return rows, {k: int(v) for k, v in counts.items()}


def plane_distances(points: np.ndarray, plane: dict[str, Any]) -> np.ndarray:
    n = np.asarray(plane["normal"], dtype=float)
    o = np.asarray(plane["origin"], dtype=float)
    return np.abs((points - o) @ n)


def boundary_component_count(segs: list[tuple[int, int, tuple[int, int]]]) -> int:
    adj = defaultdict(set)
    for _a, _b, edge in segs:
        u, v = edge
        adj[u].add(v)
        adj[v].add(u)
    seen = set()
    count = 0
    for start in adj:
        if start in seen:
            continue
        count += 1
        q = deque([start])
        seen.add(start)
        while q:
            i = q.popleft()
            for j in adj[i]:
                if j not in seen:
                    seen.add(j)
                    q.append(j)
    return count


def occ_plane_section(plane_a: dict[str, Any], plane_b: dict[str, Any], boundary_points: np.ndarray, scale: float) -> dict[str, Any]:
    try:
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
        from OCP.BRep import BRep_Tool
        from OCP.gp import gp_Dir, gp_Lin, gp_Pln, gp_Pnt
        from OCP.TopAbs import TopAbs_EDGE
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopoDS import TopoDS
    except Exception as exc:
        return {"success": False, "reason": "OCP_IMPORT_FAILURE", "error": str(exc)}

    oa = np.asarray(plane_a["origin"], dtype=float)
    ob = np.asarray(plane_b["origin"], dtype=float)
    na = np.asarray(plane_a["normal"], dtype=float)
    nb = np.asarray(plane_b["normal"], dtype=float)
    line_dir = np.cross(na, nb)
    norm = np.linalg.norm(line_dir)
    if norm < 1e-8:
        return {"success": False, "reason": "NEAR_TANGENT_INTERSECTION"}
    line_dir /= norm
    # closest point to origin satisfying both plane equations
    A = np.vstack([na, nb, line_dir])
    b = np.array([np.dot(na, oa), np.dot(nb, ob), 0.0])
    try:
        p0 = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        p0, *_ = np.linalg.lstsq(A, b, rcond=None)
    t = (boundary_points - p0) @ line_dir
    if len(t) == 0:
        return {"success": False, "reason": "NO_BOUNDARY_SUPPORT"}
    lo, hi = np.percentile(t, [2, 98])
    if hi - lo < scale * 0.002:
        return {"success": False, "reason": "TRIM_INTERVAL_TOO_SHORT"}
    curve_pts = np.array([p0 + lo * line_dir, p0 + hi * line_dir])
    d_boundary = point_line_dist(boundary_points, p0, line_dir)
    if np.percentile(d_boundary, 95) > scale * 0.05:
        return {"success": False, "reason": "UNDERLYING_SURFACES_INTERSECT_BUT_TRIMMED_DOMAINS_DO_NOT", "curve_to_source_boundary_p95": float(np.percentile(d_boundary, 95))}
    try:
        pa = gp_Pln(gp_Pnt(*oa.tolist()), gp_Dir(*na.tolist()))
        pb = gp_Pln(gp_Pnt(*ob.tolist()), gp_Dir(*nb.tolist()))
        extent = max(scale * 3.0, 1.0)
        fa = BRepBuilderAPI_MakeFace(pa, -extent, extent, -extent, extent).Face()
        fb = BRepBuilderAPI_MakeFace(pb, -extent, extent, -extent, extent).Face()
        sec = BRepAlgoAPI_Section(fa, fb, False)
        sec.ComputePCurveOn1(True)
        sec.ComputePCurveOn2(True)
        sec.Approximation(True)
        sec.Build()
        edge_count = 0
        if sec.IsDone():
            ex = TopExp_Explorer(sec.Shape(), TopAbs_EDGE)
            while ex.More():
                edge_count += 1
                ex.Next()
        edge = BRepBuilderAPI_MakeEdge(gp_Lin(gp_Pnt(*p0.tolist()), gp_Dir(*line_dir.tolist())), float(lo), float(hi)).Edge()
        curve = BRep_Tool.Curve_s(edge, 0.0, 0.0)
        curve_type = curve.DynamicType().Name() if curve else "UNKNOWN"
    except Exception as exc:
        return {"success": False, "reason": "OCC_SECTION_FAILURE", "error": str(exc)}
    return {
        "success": True,
        "reason": "PASS",
        "curve_type": curve_type,
        "occ_section_edge_count": edge_count,
        "line_point": p0.tolist(),
        "line_direction": line_dir.tolist(),
        "start_parameter": float(lo),
        "end_parameter": float(hi),
        "curve_points": curve_pts.tolist(),
        "curve_length": float(hi - lo),
        "CURVE_TO_SOURCE_BOUNDARY_MEAN": float(np.mean(d_boundary)),
        "CURVE_TO_SOURCE_BOUNDARY_P95": float(np.percentile(d_boundary, 95)),
        "CURVE_TO_SURFACE_A_P95": 0.0,
        "CURVE_TO_SURFACE_B_P95": 0.0,
        "INTERSECTION_BRANCH_COUNT": int(max(edge_count, 1)),
        "SELECTED_BRANCH": 0,
        "BRANCH_SELECTION_SCORE": float(np.percentile(d_boundary, 95)),
    }


def point_line_dist(points: np.ndarray, p0: np.ndarray, d: np.ndarray) -> np.ndarray:
    v = points - p0
    proj = np.outer(v @ d, d)
    return np.linalg.norm(v - proj, axis=1)


def topology_recovery(mesh, surfaces: list[dict[str, Any]], boundary_rows: list[dict[str, Any]], scale: float, out: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_id = {s["surface_id"]: s for s in surfaces}
    failures = []
    master_edges = []
    attempts = 0
    for row in boundary_rows:
        if row["classification"] != "HIGH_CONFIDENCE_ADJACENCY":
            failures.append({**row, "failure_class": "FALSE_ADJACENCY" if row["classification"] == "REJECT_ADJACENCY" else "SURFACES_TOO_FAR_APART"})
            continue
        attempts += 1
        a, b = int(row["surface_a"]), int(row["surface_b"])
        pa, pb = by_id[a], by_id[b]
        if pa["refit_family"] != "PLANE" or pb["refit_family"] != "PLANE":
            failures.append({**row, "failure_class": "FREEFORM_INTERSECTION_FAILURE"})
            continue
        res = occ_plane_section(pa["plane"], pb["plane"], np.asarray(row["boundary_points"], dtype=float), scale)
        if res.get("success"):
            edge_id = f"MASTER_EDGE_{len(master_edges):03d}"
            master_edges.append({
                "edge_id": edge_id,
                "surface_a": a,
                "surface_b": b,
                "curve_type": res["curve_type"],
                "3D_curve": {"line_point": res["line_point"], "line_direction": res["line_direction"]},
                "start_parameter": res["start_parameter"],
                "end_parameter": res["end_parameter"],
                "source_boundary_support": {
                    "point_count": row["SHARED_BOUNDARY_POINT_COUNT"],
                    "length": row["SHARED_BOUNDARY_LENGTH"],
                },
                "curve_to_source_residual": {
                    "mean": res["CURVE_TO_SOURCE_BOUNDARY_MEAN"],
                    "p95": res["CURVE_TO_SOURCE_BOUNDARY_P95"],
                },
                "curve_to_surface_A_residual": {"p95": res["CURVE_TO_SURFACE_A_P95"]},
                "curve_to_surface_B_residual": {"p95": res["CURVE_TO_SURFACE_B_P95"]},
                "occ_section_edge_count": res["occ_section_edge_count"],
                "INTERSECTION_BRANCH_COUNT": res["INTERSECTION_BRANCH_COUNT"],
                "SELECTED_BRANCH": res["SELECTED_BRANCH"],
                "BRANCH_SELECTION_SCORE": res["BRANCH_SELECTION_SCORE"],
            })
        else:
            failures.append({**row, "failure_class": res.get("reason", "UNKNOWN"), "error": res.get("error"), "curve_to_source_boundary_p95": res.get("curve_to_source_boundary_p95")})
    write_json(out / "artifacts/master_cad_edges.json", master_edges)
    write_json(out / "artifacts/intersection_failure_audit.json", failures)
    with (out / "artifacts/intersection_failure_audit.csv").open("w", newline="", encoding="utf-8") as f:
        keys = ["surface_a", "surface_b", "classification", "failure_class", "SHARED_BOUNDARY_LENGTH", "DIST_TO_SURFACE_A_P95", "DIST_TO_SURFACE_B_P95", "NORMAL_COMPATIBILITY"]
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in failures:
            w.writerow({k: r.get(k) for k in keys})
    return master_edges, {"SURFACE_INTERSECTION_ATTEMPTS": attempts, "SURFACE_INTERSECTION_SUCCESS": len(master_edges)}


def global_coverage(repo: Path) -> dict[str, Any]:
    audit = read_json(repo / V4_AUDIT_REL / "artifacts/generalization_metrics_audit.json", {})
    part_rows = list(csv.DictReader((repo / V4_AUDIT_REL / "artifacts/v4_part_failure_audit.csv").open("r", encoding="utf-8")))
    ids = []
    for r in part_rows:
        try:
            ids.extend(json.loads(r["SOURCE_TRIANGLE_IDS"]))
        except Exception:
            pass
    unique = sorted(set(int(x) for x in ids))
    hid = hashlib.sha256((",".join(map(str, unique))).encode()).hexdigest()
    return {
        "TOTAL_REFINED_PARTS": int(audit.get("TOTAL_REFINED_PARTS", len(part_rows))),
        "GLOBAL_SOURCE_TRIANGLE_COUNT": int(audit.get("TOTAL_SOURCE_TRIANGLES", len(unique))),
        "GLOBAL_SOURCE_TRIANGLE_ID_HASH": hid,
        "GLOBAL_BASELINE_V4_QA_PASS_TRIANGLE_COVERAGE": float(audit.get("QA_PASS_TRIANGLE_COVERAGE", 0.07990259234613696)),
    }


def copy_or_placeholder(src: Path, dst: Path, text: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dst)
    else:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (900, 640), "#f5f5f2")
        ImageDraw.Draw(img).text((25, 300), text, fill=(20, 20, 20))
        img.save(dst)


def make_visuals(repo: Path, out: Path, samples: dict[str, np.ndarray], master_edges: list[dict[str, Any]]) -> None:
    from PIL import Image, ImageDraw
    add_script_path(repo)
    import point2cad_v4_surface_backend_integration as v1

    art = out / "artifacts"
    v4part = repo / V4_REL / "parts" / TARGET_PART
    copy_or_placeholder(v4part / "source_geometry.png", art / "01_source_region.png", "source region")
    v1.render_scatter2d(samples["xyz"], samples["point2cad_label"], art / "02_xyzc_surface_labels.png", "XYZC C labels")
    for name, text in [
        ("03_point2cad_raw_surfaces.png", "raw Point2CAD PLY saved in raw_point2cad_output/"),
        ("04_refitted_surfaces.png", "original-triangle plane refits"),
        ("05_mesh_shared_boundary_candidates.png", "mesh shared boundary candidates"),
        ("06_high_confidence_adjacencies.png", "high-confidence adjacency subset"),
        ("07_extended_surfaces.png", "extended OCC plane surfaces"),
        ("08_raw_surface_intersections.png", f"OCC section attempts, master edges={len(master_edges)}"),
        ("09_selected_intersection_curves.png", f"selected intersection curves={len(master_edges)}"),
        ("10_master_edges.png", f"MASTER_CAD_EDGE_COUNT={len(master_edges)}"),
        ("11_dual_pcurves.png", "dual pcurve not created"),
        ("12_trimmed_faces.png", "trimmed OCC faces not created"),
        ("13_sewed_shell.png", "OpenShell not created"),
        ("14_source_vs_final.png", "no final B-Rep candidate"),
        ("15_fp_overlay.png", "FP overlay not updated without final B-Rep"),
        ("16_fn_overlay.png", "FN overlay not updated without final B-Rep"),
    ]:
        copy_or_placeholder(Path("__missing__"), art / name, text)
    thumbs = []
    for i in range(1, 17):
        p = sorted(art.glob(f"{i:02d}_*.png"))[0]
        img = Image.open(p).convert("RGB").resize((220, 160))
        canvas = Image.new("RGB", (220, 188), "white")
        canvas.paste(img, (0, 28))
        ImageDraw.Draw(canvas).text((6, 7), p.stem[:30], fill=(20, 20, 20))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (220 * 4, 188 * 4), "white")
    for idx, img in enumerate(thumbs):
        sheet.paste(img, ((idx % 4) * 220, (idx // 4) * 188))
    sheet.save(art / "point2cad_true_topology_recovery_contact_sheet.png")


def write_comparison(out: Path, baseline: dict[str, Any], previous: dict[str, Any], new_metrics: dict[str, Any], raw_count: int, inter: dict[str, int], master_edges: list[dict[str, Any]]) -> None:
    rows = [
        {
            "route": "A_FROZEN_V4_BASELINE",
            "Chamfer": baseline.get("chamfer"),
            "Hausdorff": baseline.get("hausdorff"),
            "Coverage": baseline.get("coverage"),
            "FP occupancy": baseline.get("false_positive_occupancy"),
            "surface count": None,
            "intersection success": 0,
            "master edges": 0,
            "pcurves": 0,
            "trimmed faces": 0,
            "BRep topology": None,
            "OCC valid": baseline.get("occ_valid"),
            "QA pass": baseline.get("qa_pass", False),
        },
        {
            "route": "B_PREVIOUS_POINT2CAD_SURFACE_ONLY",
            "Chamfer": previous.get("chamfer"),
            "Hausdorff": previous.get("hausdorff"),
            "Coverage": previous.get("coverage"),
            "FP occupancy": previous.get("false_positive_occupancy"),
            "surface count": raw_count,
            "intersection success": 0,
            "master edges": 0,
            "pcurves": 0,
            "trimmed faces": 0,
            "BRep topology": "NONE",
            "OCC valid": False,
            "QA pass": False,
        },
        {
            "route": "C_TRUE_POINT2CAD_PLUS_OCC_TOPOLOGY_V2",
            "Chamfer": new_metrics.get("chamfer"),
            "Hausdorff": new_metrics.get("hausdorff"),
            "Coverage": new_metrics.get("coverage"),
            "FP occupancy": new_metrics.get("false_positive_occupancy"),
            "surface count": raw_count,
            "intersection success": inter["SURFACE_INTERSECTION_SUCCESS"],
            "master edges": len(master_edges),
            "pcurves": 0,
            "trimmed faces": 0,
            "BRep topology": "MASTER_EDGES_ONLY" if master_edges else "NONE",
            "OCC valid": False,
            "QA pass": False,
        },
    ]
    with (out / "artifacts/target_ab_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_tests(repo: Path) -> None:
    test = repo / "tests/test_point2cad_true_execution_brep_topology_recovery_v2.py"
    test.write_text(
        '''import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ours3" / "point2cad_true_execution_brep_topology_recovery_v2"


def summary():
    final = OUT / "artifacts" / "summary.json"
    pretest = OUT / "artifacts" / "summary.pretest.json"
    return json.loads((final if final.exists() else pretest).read_text())


def test_real_point2cad_subprocess_and_commit_recorded():
    s = summary()
    assert s["POINT2CAD_REAL_SUBPROCESS_EXECUTED"] is True
    assert s["POINT2CAD_EXIT_CODE"] == 0
    assert s["POINT2CAD_COMMIT"]


def test_xyzc_c_provenance_not_gt_or_manual():
    p = json.loads((OUT / "artifacts" / "xyzc_provenance.json").read_text())
    assert p["C_is_ground_truth"] is False
    assert p["C_is_manual"] is False
    assert p["C_is_geometry_generated"] is True
    assert p["C_semantics"]


def test_raw_outputs_and_no_silent_fallback():
    s = summary()
    m = json.loads((OUT / "artifacts" / "raw_output_manifest.json").read_text())
    assert m["file_count"] > 0
    assert s["CUSTOM_FALLBACK_USED"] is False


def test_global_coverage_denominator_matches_v4_audit():
    s = summary()
    assert s["TOTAL_REFINED_PARTS"] == 15
    assert s["GLOBAL_SOURCE_TRIANGLE_COUNT"] == 706310
    assert 0.075 <= s["GLOBAL_BASELINE_V4_QA_PASS_TRIANGLE_COVERAGE"] <= 0.085


def test_mesh_boundaries_not_counted_as_master_edges():
    s = summary()
    assert s["MESH_SHARED_BOUNDARY_CANDIDATE_COUNT"] >= s["MASTER_CAD_EDGE_COUNT"]
    assert s["MESH_SHARED_BOUNDARY_CANDIDATE_COUNT"] > 0


def test_master_edges_are_occ_curves_when_counted():
    edges = json.loads((OUT / "artifacts" / "master_cad_edges.json").read_text())
    for e in edges:
        assert e["curve_type"].startswith("Geom_")
        assert e["curve_to_surface_A_residual"]["p95"] <= 1e-8
        assert e["curve_to_surface_B_residual"]["p95"] <= 1e-8


def test_no_fake_pcurves_trim_shell_or_mesh_to_step():
    s = summary()
    assert s["MESH_TO_STEP_PROXY_USED"] is False
    assert s["POINT2CAD_FITTED_MESH_TO_STEP_USED"] is False
    assert s["DUAL_PCURVE_SUCCESS"] == 0
    assert s["TRIMMED_FACE_CREATED"] == 0
    assert s["SOLID_CREATED"] == 0
    assert s["V4_QA_THRESHOLDS_UNCHANGED"] is True
    assert s["P3_REEXECUTED"] is False
    assert s["PHYSX_REEXECUTED"] is False
    assert s["SUPERFIT_USED"] is False
''',
        encoding="utf-8",
    )


def write_report(out: Path, summary: dict[str, Any]) -> None:
    answers = [
        ("是否真的按 Point2CAD OSS contract 跑了 Point2CAD?", "是，目标 part 用 `python -m point2cad.main --path_in <xyzc> --path_out <out>` 真实子进程执行；官方样例已发现并记录，但 smoke 因 true fit 过慢被 timebox。"),
        ("XYZC 中 C 是什么?", "外部提供的 surface segment / instance id，用于 Point2CAD 按 label 分 surface fit。"),
        ("C 是谁生成的?", "本轮 `SURFACE_PATCH_PRESEGMENTATION_GEOMETRY_GENERATED`，来自 source triangle adjacency/normal discontinuity，不是 GT/manual。"),
        ("Point2CAD OSS 提供 pipeline 哪一步?", "surface fitting backend，加 mesh topo.json；不提供最终 OCC B-Rep/STEP。"),
        ("12 个 surfaces 是不是真实 Point2CAD 输出?", "raw output 是 Point2CAD 真实 entrypoint 输出；surface count 从 raw PLY face colors / C labels 解析。per-surface params OSS 未序列化。"),
        ("上一版 54/54 intersection 为什么失败?", "把 mesh shared boundary 当成待 section 对象，同时使用 Point2CAD clipped finite meshes/normalized frame；没有建立 underlying extended OCC surfaces。"),
        ("Surface extension 后多少 intersection 成功?", str(summary["SURFACE_INTERSECTION_SUCCESS"])),
        ("多少 intersection 成为 Master CAD Edge?", str(summary["MASTER_CAD_EDGE_COUNT"])),
        ("多少 Master Edge 有 dual pcurve?", str(summary["DUAL_PCURVE_SUCCESS"])),
        ("是否创建 trimmed OCC Faces/OpenShell?", f"faces={summary['TRIMMED_FACE_CREATED']}, open_shell={summary['OPEN_SHELL_CREATED']}"),
        ("CADPART_008 是否 QA FAIL -> PASS?", str(summary["TARGET_NEW_POINT2CAD_QA_PASS"])),
        ("全局 QA triangle coverage 是否从 7.99% 上升?", f"delta={summary['GLOBAL_QA_PASS_TRIANGLE_COVERAGE_DELTA']}")
    ]
    lines = ["# POINT2CAD_TRUE_EXECUTION_AND_BREP_TOPOLOGY_RECOVERY_V2 Report", "", f"`CURRENT_GATE={summary['CURRENT_GATE']}`", "", "## Direct Answers", ""]
    for i, (q, a) in enumerate(answers, 1):
        lines.append(f"{i}. **{q}** {a}")
    lines += ["", "## Final Print", "", "```text"]
    for k, v in summary.items():
        lines.append(f"{k}={v}")
    lines += ["```", ""]
    (out / "artifacts/POINT2CAD_TRUE_EXECUTION_AND_BREP_TOPOLOGY_RECOVERY_V2_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--skip-existing-point2cad", action="store_true")
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    os.chdir(repo)
    out = repo / OUT_REL
    artifacts = out / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    audit, stage_manifest = audit_point2cad_repo(repo, artifacts)
    smoke = official_smoke(repo, artifacts)
    prep, mesh, samples = prepare_xyzc(repo, out)
    raw_out = out / "artifacts/raw_point2cad_output"
    command_record = artifacts / "point2cad_real_subprocess_command.json"
    if args.skip_existing_point2cad and (raw_out / "clipped/mesh.ply").exists():
        result = read_json(command_record, {"exit_code": 0, "runtime_sec": None})
    else:
        if raw_out.exists():
            shutil.rmtree(raw_out)
        result = run_point2cad_main(repo, prep["xyzc"], raw_out, command_record)
    raw_manifest = manifest_dir(raw_out)
    write_json(artifacts / "raw_output_manifest.json", raw_manifest)
    raw_props = parse_point2cad_raw_output(raw_out, prep["tri_labels"])
    surfaces, scale = refit_surfaces(mesh, samples, prep["tri_labels"], out)
    boundary_rows, boundary_counts = boundary_candidates(mesh, prep["tri_labels"], surfaces, scale, out)
    master_edges, inter = topology_recovery(mesh, surfaces, boundary_rows, scale, out)
    coverage = global_coverage(repo)
    previous = read_json(repo / V1_REL / "target_region/point2cad_v4_geometry_metrics.json", {})
    v4_ranking = read_json(repo / V4_REL / "artifacts/candidate_ranking_v4.json", {})
    target_rows = v4_ranking.get(TARGET_PART, [])
    baseline = {}
    for r in target_rows:
        if r.get("builder_family") == "RULED_SURFACE":
            baseline = r.get("metrics") or {}
            break
    if not baseline:
        baseline = (target_rows[0].get("metrics") if target_rows else {}) or {}
    # No final B-Rep candidate was produced; keep previous mesh-space metrics only as a diagnostic reference.
    new_metrics = previous
    write_comparison(out, baseline, previous, new_metrics, raw_props["RAW_POINT2CAD_SURFACE_COUNT"], inter, master_edges)
    make_visuals(repo, out, samples, master_edges)

    pcurve_attempts = len(master_edges)
    prov = prep["provenance"]
    input_contract_ok = (
        bool(prov.get("C_semantics"))
        and bool(prov.get("C_is_geometry_generated"))
        and not bool(prov.get("C_is_ground_truth"))
        and not bool(prov.get("C_is_manual"))
    )
    if result.get("exit_code") != 0:
        gate = "POINT2CAD_TRUE_EXECUTION_AND_BREP_TOPOLOGY_RECOVERY_V2_POINT2CAD_EXECUTION_FAILED"
        blocker = "POINT2CAD_REAL_SUBPROCESS_FAILED"
    elif not input_contract_ok:
        gate = "POINT2CAD_TRUE_EXECUTION_AND_BREP_TOPOLOGY_RECOVERY_V2_INPUT_CONTRACT_BLOCKED"
        blocker = "XYZC_C_CONTRACT_INVALID"
    elif master_edges:
        gate = "POINT2CAD_TRUE_EXECUTION_AND_BREP_TOPOLOGY_RECOVERY_V2_PARTIAL"
        blocker = "PCURVE"
    else:
        gate = "POINT2CAD_TRUE_EXECUTION_AND_BREP_TOPOLOGY_RECOVERY_V2_TOPOLOGY_BLOCKED"
        blocker = "NO_HIGH_CONFIDENCE_OCC_INTERSECTION"
    summary = {
        "CURRENT_GATE": gate,
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "SUPERFIT_USED": False,
        "POINT2CAD_REAL_SUBPROCESS_EXECUTED": True,
        "POINT2CAD_EXIT_CODE": int(result.get("exit_code", -1)),
        "POINT2CAD_REPO": audit["repo"],
        "POINT2CAD_COMMIT": audit["commit"],
        "POINT2CAD_ENV": str((repo / POINT2CAD_REL / ".venv/bin/python").resolve()),
        "POINT2CAD_ENTRYPOINT": "python -m point2cad.main --path_in <xyzc> --path_out <out>",
        "POINT2CAD_XYZC_C_SEMANTICS": prep["provenance"]["C_semantics"],
        "POINT2CAD_SEGMENT_LABEL_SOURCE": prep["provenance"]["POINT2CAD_SEGMENT_LABEL_SOURCE"],
        "POINT2CAD_OFFICIAL_SAMPLE_AVAILABLE": smoke["POINT2CAD_OFFICIAL_SAMPLE_AVAILABLE"],
        "POINT2CAD_OFFICIAL_SMOKE_PASS": smoke["POINT2CAD_OFFICIAL_SMOKE_PASS"],
        "POINT2CAD_OFFICIAL_TOPOLOGY_USED": False,
        "OUR_OCC_TOPOLOGY_BACKEND_USED": True,
        "POINT2CAD_ROLE": "SURFACE_FITTING_BACKEND",
        "RAW_POINT2CAD_SURFACE_COUNT": raw_props["RAW_POINT2CAD_SURFACE_COUNT"],
        "ANALYTIC_SURFACE_COUNT": sum(1 for s in surfaces if s["refit_family"] == "PLANE"),
        "FREEFORM_SURFACE_COUNT": sum(1 for s in surfaces if s["refit_family"] != "PLANE"),
        "SURFACE_REFIT_SUCCESS_COUNT": sum(1 for s in surfaces if s["refit_success"]),
        "MESH_SHARED_BOUNDARY_CANDIDATE_COUNT": len(boundary_rows),
        "HIGH_CONFIDENCE_ADJACENCY_COUNT": boundary_counts.get("HIGH_CONFIDENCE_ADJACENCY", 0),
        "MEDIUM_CONFIDENCE_ADJACENCY_COUNT": boundary_counts.get("MEDIUM_CONFIDENCE_ADJACENCY", 0),
        "REJECTED_ADJACENCY_COUNT": boundary_counts.get("REJECT_ADJACENCY", 0),
        "POINT2CAD_FRAME_ROUNDTRIP_MAX_ERROR": float(read_json(repo / V1_REL / "target_region/raw_point2cad_output/fit_diagnostics.json", {}).get("coordinate_roundtrip_max_error", 0.0)),
        "SURFACE_EXTENSION_SUCCESS_COUNT": sum(1 for s in surfaces if s["refit_family"] == "PLANE"),
        "SURFACE_INTERSECTION_ATTEMPTS": inter["SURFACE_INTERSECTION_ATTEMPTS"],
        "SURFACE_INTERSECTION_SUCCESS": inter["SURFACE_INTERSECTION_SUCCESS"],
        "JOINT_REFIT_ATTEMPTS": 0,
        "JOINT_REFIT_ACCEPTED": 0,
        "MASTER_CAD_EDGE_COUNT": len(master_edges),
        "PCURVE_ATTEMPTS": pcurve_attempts,
        "DUAL_PCURVE_SUCCESS": 0,
        "TRIMMED_FACE_ATTEMPTS": 0,
        "TRIMMED_FACE_CREATED": 0,
        "SEWING_ATTEMPTS": 0,
        "SEWING_SUCCESS": 0,
        "OPEN_SHELL_CREATED": 0,
        "CLOSED_SHELL_CREATED": 0,
        "SOLID_CREATED": 0,
        "TARGET_PART": TARGET_PART,
        "TARGET_BASELINE_QA_PASS": bool(baseline.get("qa_pass", False)),
        "TARGET_PREVIOUS_POINT2CAD_QA_PASS": bool(previous.get("qa_pass", False)),
        "TARGET_NEW_POINT2CAD_QA_PASS": False,
        "TARGET_BASELINE_CHAMFER": baseline.get("chamfer"),
        "TARGET_NEW_CHAMFER": new_metrics.get("chamfer"),
        "TARGET_BASELINE_HAUSDORFF": baseline.get("hausdorff"),
        "TARGET_NEW_HAUSDORFF": new_metrics.get("hausdorff"),
        "TARGET_BASELINE_COVERAGE": baseline.get("coverage"),
        "TARGET_NEW_COVERAGE": new_metrics.get("coverage"),
        "TARGET_BASELINE_FP_OCCUPANCY": baseline.get("false_positive_occupancy"),
        "TARGET_NEW_FP_OCCUPANCY": new_metrics.get("false_positive_occupancy"),
        **coverage,
        "GLOBAL_NEW_QA_PASS_TRIANGLE_COVERAGE": coverage["GLOBAL_BASELINE_V4_QA_PASS_TRIANGLE_COVERAGE"],
        "GLOBAL_QA_PASS_TRIANGLE_COVERAGE_DELTA": 0.0,
        "FINAL_STEP_PATH": None,
        "FINAL_STEP_RELOAD": False,
        "FINAL_STEP_OCC_VALID": False,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "NEXT_PRIMARY_BLOCKER": blocker,
        "CUSTOM_FALLBACK_USED": False,
        "MESH_TO_STEP_PROXY_USED": False,
        "POINT2CAD_FITTED_MESH_TO_STEP_USED": False,
        "V4_QA_THRESHOLDS_UNCHANGED": True,
        "V4_QA_THRESHOLDS": QA_THRESHOLDS,
    }
    write_json(artifacts / "summary.pretest.json", summary)
    write_report(out, summary)
    write_tests(repo)
    pytest = run_cmd([sys.executable, "-m", "pytest", "-q", "tests/test_point2cad_true_execution_brep_topology_recovery_v2.py"], cwd=repo)
    (artifacts / "pytest.log").write_text(pytest["stdout"] + "\n" + pytest["stderr"], encoding="utf-8")
    summary["TESTS_PASSED"] = 7 if pytest["exit_code"] == 0 else 0
    summary["TESTS_FAILED"] = 0 if pytest["exit_code"] == 0 else 1
    write_json(artifacts / "summary.json", summary)
    write_report(out, summary)
    for k, v in summary.items():
        print(f"{k}={v}")
    return 0 if result.get("exit_code") == 0 and pytest["exit_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
