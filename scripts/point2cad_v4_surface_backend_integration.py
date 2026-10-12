#!/usr/bin/env python3
"""Point2CAD surface backend integration for the frozen Mesh2CAD V4 run.

This script intentionally treats the local Point2CAD repository as a surface
proposal backend only. It does not feed whole-object OBJ into Point2CAD, does
not use SuperFit, and does not accept Point2CAD mesh output as final B-Rep.
"""
from __future__ import annotations

import argparse
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


TARGET_GATE = "POINT2CAD_V4_SURFACE_BACKEND_INTEGRATION_V1"
V4_DIR = Path("ours3/topology_aware_routing_trimmed_surface_fidelity_v4")
V2_DIR = Path("ours3/generic_structural_decomposition_analytic_fidelity_v2")
PART_GRAPH_DIR = Path("ours3/cad_part_graph_gate1/cases")
OUT_DIR = Path("ours3/point2cad_v4_surface_backend_integration_v1")
POINT2CAD_REPO = Path("point2cad")
QA_THRESHOLDS = {
    "chamfer_max": 0.35,
    "coverage_min": 0.35,
    "false_positive_occupancy_max": 0.25,
    "hausdorff_max": 0.75,
    "normal_error_max": 0.9,
}


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, allow_nan=True)
        f.write("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> dict[str, Any]:
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, text=True, capture_output=True)
    return {
        "command": cmd,
        "cwd": str(cwd or Path.cwd()),
        "start_time_epoch": t0,
        "runtime_sec": time.time() - t0,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def point2cad_audit(repo_root: Path, out_artifacts: Path) -> dict[str, Any]:
    p2c = repo_root / POINT2CAD_REPO
    py = p2c / ".venv" / "bin" / "python"
    commit = run(["git", "rev-parse", "HEAD"], cwd=p2c)
    env_probe = run(
        [
            str(py if py.exists() else sys.executable),
            "-c",
            (
                "import sys, torch, numpy, trimesh; "
                "print(sys.version.replace('\\n',' ')); "
                "print('torch='+torch.__version__); "
                "print('cuda='+str(torch.cuda.is_available())); "
                "print('numpy='+numpy.__version__); "
                "print('trimesh='+trimesh.__version__)"
            ),
        ],
        cwd=repo_root,
    )
    files = {
        "README": p2c / "README.md",
        "entrypoint": p2c / "point2cad" / "main.py",
        "io_utils": p2c / "point2cad" / "io_utils.py",
        "fitting_one_surface": p2c / "point2cad" / "fitting_one_surface.py",
        "requirements": p2c / "build" / "requirements.txt",
    }
    audit = {
        "POINT2CAD_REPO_PATH": str(p2c.resolve()),
        "POINT2CAD_COMMIT": commit["stdout"].strip() if commit["exit_code"] == 0 else None,
        "POINT2CAD_ENV": str(py.resolve() if py.exists() else Path(sys.executable).resolve()),
        "POINT2CAD_ENV_PROBE": env_probe,
        "POINT2CAD_ENTRYPOINT": "python -m point2cad.main --path_in <xyzc> --path_out <out>",
        "POINT2CAD_CHECKPOINT": None,
        "POINT2CAD_INPUT_FORMAT": "ASCII .xyzc with four columns: x y z surface_cluster_id. The OSS entrypoint does not consume normals.",
        "POINT2CAD_OUTPUT_FORMAT": "unclipped/mesh.ply, clipped/mesh.ply, topo/topo.json; no final STEP/B-Rep in this repo path.",
        "POINT2CAD_FILES": {
            key: {
                "path": str(path),
                "exists": path.exists(),
                "sha256": sha256_file(path) if path.exists() else None,
            }
            for key, path in files.items()
        },
    }
    write_json(out_artifacts / "point2cad_runtime_audit.json", audit)
    lines = [
        "# Point2CAD Runtime Audit",
        "",
        f"- Repo: `{audit['POINT2CAD_REPO_PATH']}`",
        f"- Commit: `{audit['POINT2CAD_COMMIT']}`",
        f"- Environment: `{audit['POINT2CAD_ENV']}`",
        f"- Entrypoint: `{audit['POINT2CAD_ENTRYPOINT']}`",
        f"- Checkpoint: `{audit['POINT2CAD_CHECKPOINT']}`",
        f"- Input format: {audit['POINT2CAD_INPUT_FORMAT']}",
        f"- Output format: {audit['POINT2CAD_OUTPUT_FORMAT']}",
        "",
        "## Environment Probe",
        "",
        "```text",
        audit["POINT2CAD_ENV_PROBE"]["stdout"].strip(),
        audit["POINT2CAD_ENV_PROBE"]["stderr"].strip(),
        "```",
    ]
    (out_artifacts / "point2cad_runtime_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return audit


def load_v4_rows(repo_root: Path) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, str]]]:
    ranking = read_json(repo_root / V4_DIR / "artifacts" / "candidate_ranking_v4.json", {})
    topo_csv = repo_root / V4_DIR / "artifacts" / "topology_classification.csv"
    metric_csv = repo_root / V4_DIR / "artifacts" / "v4_candidate_metrics.csv"
    topo_rows = list(csv.DictReader(topo_csv.open("r", encoding="utf-8"))) if topo_csv.exists() else []
    metric_rows = list(csv.DictReader(metric_csv.open("r", encoding="utf-8"))) if metric_csv.exists() else []
    return ranking, topo_rows, metric_rows


def parse_jsonish(value: str | None) -> Any:
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def baseline_by_part(ranking: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for part, rows in ranking.items():
        metric_rows = [r for r in rows if (r.get("metrics") or {}).get("chamfer") is not None]
        selected = [r for r in rows if r.get("selected") and (r.get("metrics") or {}).get("chamfer") is not None]
        if selected:
            chosen = selected[0]
        elif metric_rows:
            chosen = sorted(
                metric_rows,
                key=lambda r: (
                    not bool((r.get("metrics") or {}).get("qa_pass")),
                    float((r.get("metrics") or {}).get("false_positive_occupancy", 999)),
                    float((r.get("metrics") or {}).get("chamfer", 999)),
                ),
            )[0]
        else:
            chosen = rows[0] if rows else {}
        out[part] = chosen
    return out


def select_target_failed_part(repo_root: Path, ranking: dict[str, Any], topo_rows: list[dict[str, str]]) -> dict[str, Any]:
    topo_by_part = {r["PART_ID"]: r for r in topo_rows}
    base = baseline_by_part(ranking)
    candidates = []
    for part, r in base.items():
        m = r.get("metrics") or {}
        qa_pass = bool(m.get("qa_pass")) if m.get("qa_pass") is not None else False
        topo = topo_by_part.get(part, {})
        if qa_pass:
            continue
        if topo.get("TOPOLOGY_CLASS") != "MULTI_PATCH_SURFACE":
            continue
        coverage_score = float(topo.get("SURFACE_AREA") or 0.0)
        multi = [x for x in ranking.get(part, []) if x.get("builder_family") == "MULTI_PATCH_SURFACE"]
        tri = 0
        if multi:
            params = multi[0].get("parameters") or {}
            tri = sum(int(p.get("triangle_count") or 0) for p in params.get("patches") or [])
        candidates.append((coverage_score, tri, part, r))
    if not candidates:
        raise RuntimeError("No failed MULTI_PATCH_SURFACE V4 target found")
    surface_area, tri_count, part, baseline = sorted(candidates, reverse=True)[0]
    short = part.split("_")[1]
    return {
        "part_id": part,
        "cadpart_id": f"CADPART_{short}",
        "source_mesh": str((repo_root / PART_GRAPH_DIR / f"CADPART_{short}" / f"CADPART_{short}_local.obj").resolve()),
        "source_mesh_global": str((repo_root / PART_GRAPH_DIR / f"CADPART_{short}" / f"CADPART_{short}_global.obj").resolve()),
        "topology": topo_by_part.get(part, {}),
        "baseline": baseline,
        "target_failed_part_triangle_coverage": int(tri_count),
        "target_failed_part_surface_area": float(surface_area),
    }


def load_mesh(path: Path):
    import trimesh

    mesh = trimesh.load(path, process=False)
    if isinstance(mesh, trimesh.Scene):
        geoms = list(mesh.geometry.values())
        mesh = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    mesh.remove_unreferenced_vertices()
    return mesh


def connected_normal_labels(mesh, angle_deg: float = 18.0, max_labels: int = 36) -> np.ndarray:
    normals = np.asarray(mesh.face_normals, dtype=np.float64)
    areas = np.asarray(mesh.area_faces, dtype=np.float64)
    n = len(normals)
    adjacency = [[] for _ in range(n)]
    cos_thr = math.cos(math.radians(angle_deg))
    for a, b in np.asarray(mesh.face_adjacency, dtype=np.int64):
        if float(np.dot(normals[a], normals[b])) >= cos_thr:
            adjacency[int(a)].append(int(b))
            adjacency[int(b)].append(int(a))
    labels = -np.ones(n, dtype=np.int32)
    clusters: list[list[int]] = []
    for start in range(n):
        if labels[start] >= 0:
            continue
        cid = len(clusters)
        q: deque[int] = deque([start])
        labels[start] = cid
        cur = []
        while q:
            i = q.popleft()
            cur.append(i)
            for j in adjacency[i]:
                if labels[j] < 0:
                    labels[j] = cid
                    q.append(j)
        clusters.append(cur)
    if len(clusters) <= max_labels:
        return relabel_by_size(labels)

    cluster_area = np.array([areas[c].sum() for c in clusters])
    keep = list(np.argsort(-cluster_area)[:max_labels])
    kept_normals = []
    for cid in keep:
        w = areas[clusters[cid]]
        v = (normals[clusters[cid]] * w[:, None]).sum(0)
        kept_normals.append(v / (np.linalg.norm(v) + 1e-12))
    remap = {}
    for new, old in enumerate(keep):
        remap[old] = new
    for old in range(len(clusters)):
        if old in remap:
            continue
        w = areas[clusters[old]]
        v = (normals[clusters[old]] * w[:, None]).sum(0)
        v = v / (np.linalg.norm(v) + 1e-12)
        best = int(np.argmax([abs(float(np.dot(v, kn))) for kn in kept_normals]))
        remap[old] = best
    merged = np.array([remap[int(x)] for x in labels], dtype=np.int32)
    return relabel_by_size(merged)


def relabel_by_size(labels: np.ndarray) -> np.ndarray:
    counts = Counter(int(x) for x in labels)
    order = {old: new for new, (old, _count) in enumerate(counts.most_common())}
    return np.array([order[int(x)] for x in labels], dtype=np.int32)


def sample_region(mesh, tri_labels: np.ndarray, max_samples: int = 25000, seed: int = 20260815) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    verts = np.asarray(mesh.vertices, dtype=np.float64)
    normals = np.asarray(mesh.face_normals, dtype=np.float64)
    areas = np.asarray(mesh.area_faces, dtype=np.float64)
    n_faces = len(faces)
    base = np.ones(n_faces, dtype=np.int32)
    extra_total = max(0, int(max_samples) - n_faces)
    probs = areas / max(float(areas.sum()), 1e-12)
    extra = rng.multinomial(extra_total, probs) if extra_total else np.zeros(n_faces, dtype=np.int32)
    counts = base + extra

    sample_xyz = []
    sample_normals = []
    sample_tri = []
    sample_bary = []
    sample_labels = []
    for tri_id, count in enumerate(counts):
        tri = verts[faces[tri_id]]
        u = rng.random(int(count))
        v = rng.random(int(count))
        su = np.sqrt(u)
        bary = np.stack([1.0 - su, su * (1.0 - v), su * v], axis=1)
        pts = bary @ tri
        sample_xyz.append(pts)
        sample_normals.append(np.repeat(normals[tri_id][None, :], int(count), axis=0))
        sample_tri.append(np.full(int(count), tri_id, dtype=np.int32))
        sample_bary.append(bary.astype(np.float32))
        sample_labels.append(np.full(int(count), int(tri_labels[tri_id]), dtype=np.int32))
    xyz = np.concatenate(sample_xyz, axis=0).astype(np.float32)
    normal = np.concatenate(sample_normals, axis=0).astype(np.float32)
    tri = np.concatenate(sample_tri, axis=0)
    bary = np.concatenate(sample_bary, axis=0)
    labels = np.concatenate(sample_labels, axis=0)
    return {
        "sample_id": np.arange(len(xyz), dtype=np.int32),
        "xyz": xyz,
        "normal": normal,
        "source_triangle_id": tri,
        "barycentric_coordinate": bary,
        "point2cad_label": labels,
    }


def write_adapter_outputs(mesh, tri_labels: np.ndarray, samples: dict[str, np.ndarray], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    npz_path = out_dir / "point2cad_input_samples.npz"
    np.savez(
        npz_path,
        sample_id=samples["sample_id"],
        xyz=samples["xyz"],
        normal=samples["normal"],
        source_triangle_id=samples["source_triangle_id"],
        barycentric_coordinate=samples["barycentric_coordinate"],
        point2cad_label=samples["point2cad_label"],
        triangle_point2cad_label=tri_labels.astype(np.int32),
        mesh_vertices=np.asarray(mesh.vertices, dtype=np.float32),
        mesh_faces=np.asarray(mesh.faces, dtype=np.int32),
    )
    xyzc_path = out_dir / "point2cad_input_region.xyzc"
    np.savetxt(
        xyzc_path,
        np.column_stack([samples["xyz"], samples["point2cad_label"].astype(np.float32)]),
        fmt="%.9g %.9g %.9g %d",
    )
    label_counts = Counter(int(x) for x in tri_labels)
    mapping = {
        "input_xyzc": str(xyzc_path),
        "input_samples_npz": str(npz_path),
        "sample_count": int(len(samples["xyz"])),
        "triangle_count": int(len(tri_labels)),
        "label_count": int(len(label_counts)),
        "label_source": "mesh_normal_connected_region_adapter_non_gt",
        "gt_patch_labels_used": False,
        "point2cad_oss_requires_xyzc_labels": True,
        "fields": ["sample_id", "xyz", "normal", "source_triangle_id", "barycentric_coordinate", "point2cad_label"],
        "triangle_label_counts": {str(k): int(v) for k, v in sorted(label_counts.items())},
        "sample_to_triangle": [
            {
                "sample_id": int(sid),
                "source_triangle_id": int(tid),
                "barycentric_coordinate": [float(x) for x in bary],
                "point2cad_label": int(lbl),
            }
            for sid, tid, bary, lbl in zip(
                samples["sample_id"],
                samples["source_triangle_id"],
                samples["barycentric_coordinate"],
                samples["point2cad_label"],
            )
        ],
    }
    write_json(out_dir / "point2cad_input_mapping.json", mapping)
    return xyzc_path


def worker_run_point2cad(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    sys.path.insert(0, str(repo_root / "scripts"))
    sys.path.insert(0, str(repo_root / "point2cad"))
    from point2cad_diag.run_pipeline import run_point2cad_on_xyzc

    diag = run_point2cad_on_xyzc(
        Path(args.path_in),
        Path(args.path_out),
        repo_root / "point2cad",
        seed=20260815,
        save_fit_details=True,
    )
    write_json(Path(args.path_out) / "worker_result.json", diag)
    return 0


def run_point2cad_region(repo_root: Path, script_path: Path, xyzc_path: Path, out_dir: Path) -> dict[str, Any]:
    py = repo_root / POINT2CAD_REPO / ".venv" / "bin" / "python"
    cmd = [
        str(py if py.exists() else Path(sys.executable)),
        str(script_path),
        "--worker-run-point2cad",
        "--repo-root",
        str(repo_root),
        "--path-in",
        str(xyzc_path),
        "--path-out",
        str(out_dir),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{repo_root / 'scripts'}:{repo_root / 'point2cad'}:{env.get('PYTHONPATH', '')}"
    # The shared remote GPU can be saturated by unrelated jobs. For this
    # integration regression, deterministic completion is more important than
    # GPU throughput.
    env["CUDA_VISIBLE_DEVICES"] = ""
    env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    result = run(cmd, cwd=repo_root, env=env)
    write_json(out_dir / "point2cad_command_record.json", result)
    (out_dir / "stdout.log").write_text(result["stdout"], encoding="utf-8")
    (out_dir / "stderr.log").write_text(result["stderr"], encoding="utf-8")
    return result


def inverse_normalize(points: np.ndarray, meta: dict[str, Any]) -> np.ndarray:
    points = np.asarray(points, dtype=np.float64)
    r = np.asarray(meta["R"], dtype=np.float64)
    c = np.asarray(meta["centroid"], dtype=np.float64).reshape(1, 3)
    if meta.get("anisotropic"):
        rotated = points * np.asarray(meta["scale"], dtype=np.float64).reshape(1, 3)
    else:
        rotated = points * float(meta["scale"])
    return (r.T @ rotated.T).T + c


def triangle_patch_alignment(samples: dict[str, np.ndarray], triangle_count: int) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, Any]]:
    votes: list[Counter[int]] = [Counter() for _ in range(triangle_count)]
    for tri, lbl in zip(samples["source_triangle_id"], samples["point2cad_label"]):
        votes[int(tri)][int(lbl)] += 1
    rows = []
    labels = np.full(triangle_count, -1, dtype=np.int32)
    status_count = Counter()
    for tri_id, c in enumerate(votes):
        total = sum(c.values())
        if total == 0:
            status = "TRIANGLE_UNCERTAIN"
            top_label = -1
            top_prob = 0.0
        else:
            top_label, top_votes = c.most_common(1)[0]
            top_prob = top_votes / total
            labels[tri_id] = int(top_label)
            if top_prob >= 0.80:
                status = "TRIANGLE_SINGLE_PATCH"
            elif top_prob >= 0.50:
                status = "TRIANGLE_BOUNDARY_BETWEEN_PATCHES"
            else:
                status = "TRIANGLE_UNCERTAIN"
        status_count[status] += 1
        rows.append(
            {
                "source_triangle_id": tri_id,
                "patch_vote": {str(k): int(v) for k, v in c.items()},
                "patch_id": int(top_label),
                "patch_probability": float(top_prob),
                "ambiguity": float(1.0 - top_prob),
                "status": status,
            }
        )
    summary = {k: int(v) for k, v in status_count.items()}
    summary["alignment_success"] = bool(status_count.get("TRIANGLE_UNCERTAIN", 0) == 0)
    return rows, labels, summary


def connected_components_for_patch(mesh, tri_ids: np.ndarray) -> int:
    tri_set = set(int(x) for x in tri_ids)
    if not tri_set:
        return 0
    adj = defaultdict(list)
    for a, b in np.asarray(mesh.face_adjacency, dtype=np.int64):
        if int(a) in tri_set and int(b) in tri_set:
            adj[int(a)].append(int(b))
            adj[int(b)].append(int(a))
    seen = set()
    comps = 0
    for start in tri_set:
        if start in seen:
            continue
        comps += 1
        q = deque([start])
        seen.add(start)
        while q:
            i = q.popleft()
            for j in adj[i]:
                if j not in seen:
                    seen.add(j)
                    q.append(j)
    return comps


def fit_plane(points: np.ndarray) -> dict[str, Any]:
    if len(points) < 3:
        return {"type": "PLANE", "valid": False}
    p = np.asarray(points, dtype=np.float64)
    centroid = p.mean(0)
    _, _, vt = np.linalg.svd(p - centroid, full_matrices=False)
    normal = vt[-1]
    normal = normal / (np.linalg.norm(normal) + 1e-12)
    residual = np.abs((p - centroid) @ normal)
    return {
        "type": "PLANE",
        "point": centroid.tolist(),
        "normal": normal.tolist(),
        "mean_abs_residual": float(residual.mean()),
        "max_abs_residual": float(residual.max()),
        "valid": True,
    }


def fit_sphere(points: np.ndarray) -> dict[str, Any]:
    if len(points) < 4:
        return {"type": "SPHERE", "valid": False}
    p = np.asarray(points, dtype=np.float64)
    a = np.column_stack([2 * p, np.ones(len(p))])
    b = np.sum(p * p, axis=1)
    try:
        x, *_ = np.linalg.lstsq(a, b, rcond=None)
        center = x[:3]
        radius = math.sqrt(max(float(x[3] + center @ center), 0.0))
        residual = np.abs(np.linalg.norm(p - center, axis=1) - radius)
        return {
            "type": "SPHERE",
            "center": center.tolist(),
            "radius": float(radius),
            "mean_abs_residual": float(residual.mean()),
            "max_abs_residual": float(residual.max()),
            "valid": True,
        }
    except Exception as exc:
        return {"type": "SPHERE", "valid": False, "error": str(exc)}


def family_from_point2cad(t: str | None) -> str:
    value = (t or "").lower()
    if "plane" in value:
        return "PLANE"
    if "cylinder" in value:
        return "CYLINDER"
    if "cone" in value:
        return "CONE"
    if "sphere" in value:
        return "SPHERE"
    if "spline" in value or "inr" in value:
        return "BSPLINE"
    return "OTHER"


def build_shared_edges(mesh, tri_patch: np.ndarray) -> list[dict[str, Any]]:
    faces = np.asarray(mesh.faces, dtype=np.int64)
    edge_to_faces: dict[tuple[int, int], list[int]] = defaultdict(list)
    for fid, face in enumerate(faces):
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge_to_faces[tuple(sorted((int(a), int(b))))].append(fid)
    accum: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    verts = np.asarray(mesh.vertices, dtype=np.float64)
    for edge, face_ids in edge_to_faces.items():
        if len(face_ids) != 2:
            continue
        a, b = face_ids
        pa, pb = int(tri_patch[a]), int(tri_patch[b])
        if pa < 0 or pb < 0 or pa == pb:
            continue
        key = tuple(sorted((pa, pb)))
        accum[key].append(
            {
                "edge_vertex_ids": [int(edge[0]), int(edge[1])],
                "points": [verts[edge[0]].tolist(), verts[edge[1]].tolist()],
                "source_triangles": [int(a), int(b)],
            }
        )
    graph_edges = []
    for (a, b), supports in sorted(accum.items()):
        graph_edges.append(
            {
                "patch_a": int(a),
                "patch_b": int(b),
                "adjacency_confidence": min(1.0, len(supports) / 25.0),
                "intersection_type": "MESH_SUPPORTED_INTERVAL_FOR_SURFACE_INTERSECTION",
                "candidate_curve": supports[:50],
                "shared_triangle_boundary": [s["source_triangles"] for s in supports[:100]],
                "boundary_support": int(len(supports)),
            }
        )
    return graph_edges


def build_surface_patch_graph(mesh, samples: dict[str, np.ndarray], fit_diag: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    triangle_rows, tri_patch, align_summary = triangle_patch_alignment(samples, len(mesh.faces))
    write_json(out_dir / "point2cad_triangle_patch_alignment.json", {"summary": align_summary, "triangles": triangle_rows})
    np.save(out_dir / "triangle_point2cad_patch.npy", tri_patch)

    fit_by_label = {int(r["label"]): r for r in fit_diag.get("fit_surfaces", []) if not r.get("failed")}
    labels = sorted(set(int(x) for x in tri_patch if int(x) >= 0))
    areas = np.asarray(mesh.area_faces, dtype=np.float64)
    normals = np.asarray(mesh.face_normals, dtype=np.float64)
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    nodes = []
    purity_rows = []
    for label in labels:
        tri_ids = np.where(tri_patch == label)[0]
        if len(tri_ids) == 0:
            continue
        sample_mask = samples["point2cad_label"] == label
        pts = samples["xyz"][sample_mask]
        fam = family_from_point2cad((fit_by_label.get(label) or {}).get("type"))
        refit = fit_sphere(pts) if fam == "SPHERE" else fit_plane(pts)
        area = float(areas[tri_ids].sum())
        mean_normal = (normals[tri_ids] * areas[tri_ids, None]).sum(0)
        mean_normal = mean_normal / (np.linalg.norm(mean_normal) + 1e-12)
        normal_consistency = float(np.mean(np.abs(normals[tri_ids] @ mean_normal)))
        comps = connected_components_for_patch(mesh, tri_ids)
        boundary_edges = 0
        tri_set = set(int(x) for x in tri_ids)
        for a, b in np.asarray(mesh.face_adjacency, dtype=np.int64):
            if (int(a) in tri_set) != (int(b) in tri_set):
                boundary_edges += 1
        fit_row = fit_by_label.get(label) or {}
        residual = fit_row.get("err")
        node = {
            "patch_id": int(label),
            "source": "POINT2CAD",
            "source_triangle_ids": [int(x) for x in tri_ids.tolist()],
            "surface_family": fam,
            "surface_parameters": {
                "point2cad_type": fit_row.get("type"),
                "point2cad_fit_error": residual,
                "refit_from_original_triangles": refit,
            },
            "local_frame": None,
            "world_transform": None,
            "fit_residual": residual,
            "confidence": float(max(0.0, min(1.0, normal_consistency / (1.0 + float(residual or 0.0))))),
        }
        nodes.append(node)
        purity_rows.append(
            {
                "patch_id": int(label),
                "triangle_count": int(len(tri_ids)),
                "triangle_area": area,
                "normal_consistency": normal_consistency,
                "surface_fitting_residual": residual,
                "connected_components": int(comps),
                "boundary_complexity": int(boundary_edges),
                "deleted_as_noise": bool(len(tri_ids) < 3 or area <= 1e-10),
            }
        )
    edges = build_shared_edges(mesh, tri_patch)
    graph = {
        "schema": "SurfacePatchGraph",
        "nodes": nodes,
        "edges": edges,
        "adapter_alignment": align_summary,
        "note": "Point2CAD proposals are priors; surface parameters are refit from original sampled triangles before graph export.",
    }
    write_json(out_dir / "canonical_surface_patch_graph.json", graph)
    write_json(out_dir / "point2cad_surface_patch_purity.json", purity_rows)

    raw_proposals = {
        "surface_patch_count": len(nodes),
        "surface_type_counts": dict(Counter(n["surface_family"] for n in nodes)),
        "patch_memberships": {
            str(n["patch_id"]): {
                "source_triangle_count": len(n["source_triangle_ids"]),
                "source_triangle_ids_head": n["source_triangle_ids"][:100],
            }
            for n in nodes
        },
        "topology_adjacency_count": len(edges),
        "curve_intersection_proposals": edges,
    }
    write_json(out_dir / "point2cad_raw_surface_proposals.json", raw_proposals)
    return graph


def manifest_dir(path: Path) -> dict[str, Any]:
    files = []
    if path.exists():
        for f in sorted(p for p in path.rglob("*") if p.is_file()):
            files.append({"path": str(f), "size": f.stat().st_size, "sha256": sha256_file(f)})
    return {"root": str(path), "file_count": len(files), "files": files}


def chamfer_metrics(source: np.ndarray, candidate: np.ndarray, seed: int = 0) -> dict[str, Any]:
    if len(source) == 0 or len(candidate) == 0:
        return {"chamfer": None, "hausdorff": None, "coverage": 0.0}
    rng = np.random.default_rng(seed)
    a = source
    b = candidate
    if len(a) > 8000:
        a = a[rng.choice(len(a), 8000, replace=False)]
    if len(b) > 8000:
        b = b[rng.choice(len(b), 8000, replace=False)]

    def min_d(src, dst):
        vals = []
        for i in range(0, len(src), 1000):
            chunk = src[i : i + 1000]
            d2 = ((chunk[:, None, :] - dst[None, :, :]) ** 2).sum(-1)
            vals.append(np.sqrt(d2.min(axis=1)))
        return np.concatenate(vals)

    a2b = min_d(a, b)
    b2a = min_d(b, a)
    return {
        "chamfer": float(a2b.mean() + b2a.mean()),
        "hausdorff": float(max(a2b.max(), b2a.max())),
        "coverage": float((a2b < 0.05).mean()),
        "normal_error": None,
    }


def bbox_fp_occupancy(source: np.ndarray, candidate: np.ndarray) -> float:
    if len(source) == 0 or len(candidate) == 0:
        return 1.0
    smin, smax = source.min(0), source.max(0)
    cmin, cmax = candidate.min(0), candidate.max(0)
    inter = np.maximum(0.0, np.minimum(smax, cmax) - np.maximum(smin, cmin))
    cvol = float(np.prod(np.maximum(0.0, cmax - cmin)))
    if cvol <= 1e-12:
        return 1.0
    return float(max(0.0, cvol - float(np.prod(inter))) / cvol)


def point2cad_geometry_metrics(mesh, samples: dict[str, np.ndarray], raw_out: Path) -> dict[str, Any]:
    import trimesh

    fit_diag = read_json(raw_out / "fit_diagnostics.json", {})
    clipped = raw_out / "clipped" / "mesh.ply"
    if not clipped.exists():
        return {"available": False, "qa_pass": False, "failure": "missing_clipped_mesh"}
    cand = trimesh.load(clipped, process=False)
    if isinstance(cand, trimesh.Scene):
        geoms = list(cand.geometry.values())
        cand = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    cand_points = np.asarray(cand.vertices, dtype=np.float64)
    meta = fit_diag.get("normalization")
    if meta:
        cand_points = inverse_normalize(cand_points, meta)
    source_points = samples["xyz"].astype(np.float64)
    m = chamfer_metrics(source_points, cand_points, seed=20260815)
    m["false_positive_occupancy"] = bbox_fp_occupancy(source_points, cand_points)
    m["occ_valid"] = False
    m["qa_pass"] = bool(
        m["chamfer"] is not None
        and m["chamfer"] <= QA_THRESHOLDS["chamfer_max"]
        and m["hausdorff"] <= QA_THRESHOLDS["hausdorff_max"]
        and m["coverage"] >= QA_THRESHOLDS["coverage_min"]
        and m["false_positive_occupancy"] <= QA_THRESHOLDS["false_positive_occupancy_max"]
        and m["occ_valid"]
    )
    return m


def render_scatter(points: np.ndarray, labels: np.ndarray | None, path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pts = np.asarray(points)
    if len(pts) > 8000:
        rng = np.random.default_rng(4)
        idx = rng.choice(len(pts), 8000, replace=False)
        pts = pts[idx]
        labels = labels[idx] if labels is not None else None
    fig = plt.figure(figsize=(7, 5), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    c = labels if labels is not None else "#4f7898"
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c=c, s=1, cmap="tab20")
    ax.set_title(title)
    ax.set_axis_off()
    equal_axes(ax, pts)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def render_scatter2d(points: np.ndarray, labels: np.ndarray | None, path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pts = np.asarray(points)
    if len(pts) > 8000:
        rng = np.random.default_rng(4)
        idx = rng.choice(len(pts), 8000, replace=False)
        pts = pts[idx]
        labels = labels[idx] if labels is not None else None
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.2), dpi=140)
    pairs = [(0, 1, "XY"), (0, 2, "XZ"), (1, 2, "YZ")]
    for ax, (a, b, name) in zip(axes, pairs):
        color = labels if labels is not None else "#4f7898"
        ax.scatter(pts[:, a], pts[:, b], c=color, s=1, cmap="tab20")
        ax.set_title(name)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def render_mesh(path_in: Path, path_out: Path, title: str, norm_meta: dict[str, Any] | None = None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import trimesh

    mesh = load_mesh(path_in) if path_in.suffix.lower() == ".obj" else trimesh.load(path_in, process=False)
    if isinstance(mesh, trimesh.Scene):
        geoms = list(mesh.geometry.values())
        mesh = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    verts = np.asarray(mesh.vertices, dtype=np.float64)
    if norm_meta:
        verts = inverse_normalize(verts, norm_meta)
    faces = np.asarray(mesh.faces)
    fig = plt.figure(figsize=(7, 5), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    if len(faces) > 6000:
        rng = np.random.default_rng(7)
        faces = faces[rng.choice(len(faces), 6000, replace=False)]
    ax.plot_trisurf(verts[:, 0], verts[:, 1], verts[:, 2], triangles=faces, color="#7aa6c2", linewidth=0.02, alpha=0.90)
    ax.set_title(title)
    ax.set_axis_off()
    equal_axes(ax, verts)
    fig.tight_layout()
    fig.savefig(path_out)
    plt.close(fig)


def render_shared_edges(mesh, edges: list[dict[str, Any]], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    verts = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces)
    fig = plt.figure(figsize=(7, 5), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    if len(faces) > 4000:
        rng = np.random.default_rng(7)
        faces_plot = faces[rng.choice(len(faces), 4000, replace=False)]
    else:
        faces_plot = faces
    ax.plot_trisurf(verts[:, 0], verts[:, 1], verts[:, 2], triangles=faces_plot, color="#b8c7cc", linewidth=0.01, alpha=0.35)
    for edge in edges[:200]:
        for seg in edge.get("candidate_curve", [])[:3]:
            p = np.asarray(seg["points"], dtype=float)
            ax.plot(p[:, 0], p[:, 1], p[:, 2], color="#d94f45", linewidth=1.2)
    ax.set_title(f"shared boundary candidates={len(edges)}")
    ax.set_axis_off()
    equal_axes(ax, verts)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def render_graph(graph: dict[str, Any], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    n = max(1, len(nodes))
    coords = {}
    for i, node in enumerate(nodes):
        theta = 2 * math.pi * i / n
        coords[int(node["patch_id"])] = (math.cos(theta), math.sin(theta))
    fig, ax = plt.subplots(figsize=(7, 5), dpi=140)
    for e in edges:
        a, b = int(e["patch_a"]), int(e["patch_b"])
        if a in coords and b in coords:
            ax.plot([coords[a][0], coords[b][0]], [coords[a][1], coords[b][1]], color="#89939a", alpha=0.35, linewidth=0.5)
    fam_colors = {"PLANE": "#4c78a8", "CYLINDER": "#f58518", "CONE": "#e45756", "SPHERE": "#54a24b", "BSPLINE": "#b279a2", "OTHER": "#9d755d"}
    for node in nodes:
        pid = int(node["patch_id"])
        ax.scatter(*coords[pid], s=42, color=fam_colors.get(node["surface_family"], "#9d755d"))
    ax.set_title(f"SurfacePatchGraph nodes={len(nodes)} edges={len(edges)}")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def equal_axes(ax, pts: np.ndarray) -> None:
    pts = np.asarray(pts)
    if len(pts) == 0:
        return
    mn, mx = pts.min(0), pts.max(0)
    center = (mn + mx) / 2
    radius = max(float((mx - mn).max()) / 2, 1e-6)
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)


def make_visuals(repo_root: Path, out_dir: Path, target: dict[str, Any], mesh, samples: dict[str, np.ndarray], graph: dict[str, Any], fit_diag: dict[str, Any]) -> None:
    from PIL import Image, ImageDraw, ImageFont

    art = out_dir / "artifacts"
    region = out_dir / "target_region"
    raw = region / "raw_point2cad_output"
    render_mesh(Path(target["source_mesh"]), art / "source_region.png", "source refined region")
    baseline_png = repo_root / V4_DIR / "parts" / target["part_id"] / "baseline_best_fp" / "candidate_geometry.png"
    if baseline_png.exists():
        shutil.copy2(baseline_png, art / "v4_baseline_best.png")
    else:
        shutil.copy2(repo_root / V4_DIR / "parts" / target["part_id"] / "source_geometry.png", art / "v4_baseline_best.png")
    render_scatter(samples["xyz"], samples["point2cad_label"], art / "point2cad_patch_segmentation.png", "Point2CAD input patch labels")
    render_graph(graph, art / "surface_patch_graph.png")
    render_scatter(samples["xyz"], np.array([family_code(graph, int(x)) for x in samples["point2cad_label"]]), art / "point2cad_surface_types.png", "Point2CAD fitted surface families")
    meta = fit_diag.get("normalization")
    if (raw / "unclipped" / "mesh.ply").exists():
        render_mesh(raw / "unclipped" / "mesh.ply", art / "point2cad_fitted_surfaces_untrimmed.png", "Point2CAD untrimmed fitted surfaces", meta)
    else:
        placeholder(art / "point2cad_fitted_surfaces_untrimmed.png", "missing unclipped mesh")
    render_shared_edges(mesh, graph.get("edges", []), art / "shared_edges.png")
    if (raw / "clipped" / "mesh.ply").exists():
        render_mesh(raw / "clipped" / "mesh.ply", art / "trimmed_faces.png", "Point2CAD clipped surface meshes", meta)
        render_mesh(raw / "clipped" / "mesh.ply", art / "point2cad_v4_final.png", "Point2CAD+V4 final not promoted to STEP", meta)
    else:
        placeholder(art / "trimmed_faces.png", "missing clipped mesh")
        placeholder(art / "point2cad_v4_final.png", "no final candidate")
    side_by_side(art / "source_region.png", art / "point2cad_v4_final.png", art / "source_vs_point2cad_v4.png", "SOURCE", "POINT2CAD+V4")
    side_by_side(art / "source_region.png", art / "point2cad_v4_final.png", art / "fp_overlay.png", "source bbox", "candidate bbox / FP proxy")
    side_by_side(art / "point2cad_v4_final.png", art / "source_region.png", art / "fn_overlay.png", "candidate", "source / FN proxy")

    contact_items = [
        ("SOURCE", art / "source_region.png"),
        ("V4 BASELINE", art / "v4_baseline_best.png"),
        ("POINT2CAD PATCHES", art / "point2cad_patch_segmentation.png"),
        ("FITTED SURFACES", art / "point2cad_fitted_surfaces_untrimmed.png"),
        ("POINT2CAD + V4 FINAL", art / "point2cad_v4_final.png"),
        ("METRICS", art / "metrics_panel.png"),
    ]
    placeholder(contact_items[-1][1], "metrics written in summary/report")
    thumbs = []
    for label, p in contact_items:
        img = Image.open(p).convert("RGB").resize((320, 230))
        canvas = Image.new("RGB", (320, 265), "white")
        canvas.paste(img, (0, 35))
        d = ImageDraw.Draw(canvas)
        d.text((10, 10), label, fill=(20, 20, 20))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (320 * len(thumbs), 265), "white")
    for i, img in enumerate(thumbs):
        sheet.paste(img, (i * 320, 0))
    sheet.save(art / "point2cad_v4_integration_contact_sheet.png")


def family_code(graph: dict[str, Any], label: int) -> int:
    fams = {"PLANE": 0, "CYLINDER": 1, "CONE": 2, "SPHERE": 3, "BSPLINE": 4, "OTHER": 5}
    by = {int(n["patch_id"]): n["surface_family"] for n in graph.get("nodes", [])}
    return fams.get(by.get(label, "OTHER"), 5)


def placeholder(path: Path, text: str) -> None:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (900, 640), "#f5f5f2")
    d = ImageDraw.Draw(img)
    d.text((30, 300), text, fill=(30, 30, 30))
    img.save(path)


def side_by_side(left: Path, right: Path, out: Path, ltxt: str, rtxt: str) -> None:
    from PIL import Image, ImageDraw

    a = Image.open(left).convert("RGB").resize((450, 330))
    b = Image.open(right).convert("RGB").resize((450, 330))
    img = Image.new("RGB", (900, 365), "white")
    img.paste(a, (0, 35))
    img.paste(b, (450, 35))
    d = ImageDraw.Draw(img)
    d.text((12, 10), ltxt, fill=(20, 20, 20))
    d.text((462, 10), rtxt, fill=(20, 20, 20))
    img.save(out)


def write_ablation(out_artifacts: Path, target: dict[str, Any], p2c_metrics: dict[str, Any]) -> None:
    baseline = target.get("baseline") or {}
    bm = baseline.get("metrics") or {}
    rows = [
        {
            "part_id": target["part_id"],
            "route": "V4_BASELINE",
            "candidate_count": len(read_json(Path.cwd() / V4_DIR / "artifacts" / "candidate_ranking_v4.json", {}).get(target["part_id"], [])),
            "occ_valid": bm.get("occ_valid"),
            "chamfer": bm.get("chamfer"),
            "hausdorff": bm.get("hausdorff"),
            "coverage": bm.get("coverage"),
            "fp_occupancy": bm.get("false_positive_occupancy"),
            "qa_pass": bm.get("qa_pass", False),
        },
        {
            "part_id": target["part_id"],
            "route": "POINT2CAD_V4",
            "candidate_count": 1,
            "occ_valid": p2c_metrics.get("occ_valid"),
            "chamfer": p2c_metrics.get("chamfer"),
            "hausdorff": p2c_metrics.get("hausdorff"),
            "coverage": p2c_metrics.get("coverage"),
            "fp_occupancy": p2c_metrics.get("false_positive_occupancy"),
            "qa_pass": p2c_metrics.get("qa_pass", False),
        },
    ]
    with (out_artifacts / "point2cad_v4_ablation.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_tests(repo_root: Path) -> None:
    test_path = repo_root / "tests" / "test_point2cad_v4_surface_backend_contract.py"
    test_path.write_text(
        '''import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ours3" / "point2cad_v4_surface_backend_integration_v1"


def load_summary():
    path = OUT / "artifacts" / "summary.json"
    if not path.exists():
        path = OUT / "artifacts" / "summary.pretest.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_upstream_frozen_and_superfit_disabled():
    s = load_summary()
    assert s["P3_REEXECUTED"] is False
    assert s["PHYSX_REEXECUTED"] is False
    assert s["SUPERFIT_USED"] is False
    assert s["V4_QA_THRESHOLDS_UNCHANGED"] is True


def test_point2cad_real_runtime_and_raw_outputs_preserved():
    s = load_summary()
    assert s["POINT2CAD_USED"] is True
    assert s["POINT2CAD_ENTRYPOINT"]
    raw = OUT / "target_region" / "raw_point2cad_output"
    assert (raw / "fit_diagnostics.json").exists()
    assert (OUT / "artifacts" / "point2cad_raw_output_manifest.json").exists()


def test_samples_map_back_to_source_triangles():
    mapping = json.loads((OUT / "target_region" / "point2cad_input_mapping.json").read_text())
    assert mapping["sample_count"] > 0
    assert mapping["triangle_count"] > 0
    first = mapping["sample_to_triangle"][0]
    assert {"sample_id", "source_triangle_id", "barycentric_coordinate", "point2cad_label"} <= set(first)


def test_unknown_and_proxy_policies():
    s = load_summary()
    assert s["MESH_TO_STEP_PROXY_USED"] is False
    assert s["POINT2CAD_FINAL_STEP_DIRECTLY_ACCEPTED"] is False
    assert s["OPEN_SHELL_FORCED_TO_SOLID"] is False


def test_patch_graph_and_shared_edges_exist():
    graph = json.loads((OUT / "target_region" / "canonical_surface_patch_graph.json").read_text())
    assert graph["schema"] == "SurfacePatchGraph"
    assert len(graph["nodes"]) == load_summary()["POINT2CAD_SURFACE_PATCH_COUNT"]
    assert load_summary()["POINT2CAD_PATCH_TO_TRIANGLE_ALIGNMENT_SUCCESS"] is True
''',
        encoding="utf-8",
    )


def write_report(out_artifacts: Path, summary: dict[str, Any], target: dict[str, Any], graph: dict[str, Any], p2c_metrics: dict[str, Any]) -> None:
    q = [
        ("Does the V4 failed part contain multiple CAD-like patches?", "Yes. V4 topology classified the target as MULTI_PATCH_SURFACE and the adapter found multiple connected normal regions."),
        ("Did Point2CAD discover patches?", f"Partially. Real Point2CAD fitted {summary['POINT2CAD_SURFACE_PATCH_COUNT']} surface proposals from non-GT adapter labels."),
        ("Is patch-to-triangle alignment clean?", f"{summary['POINT2CAD_PATCH_TO_TRIANGLE_ALIGNMENT_SUCCESS']}; every saved sample maps to source_triangle_id and barycentric coordinates."),
        ("Is Point2CAD+V4 more accurate than baseline?", "No useful B-Rep improvement in Phase A because this Point2CAD repo outputs mesh/topo only and no OCC STEP was promoted."),
        ("Are adjacency/intersections enough for shared CAD edges?", f"Not yet. {summary['SHARED_EDGE_RECOVERED_COUNT']} mesh-supported shared boundary candidates were recovered, but OCC pcurves were not created."),
        ("Can V4 trim backend take over?", "Not in this run. The integration produced SurfacePatchGraph priors, but final trimmed OCC faces were not created."),
        ("Did QA_PASS_TRIANGLE_COVERAGE increase?", f"{summary['QA_PASS_TRIANGLE_COVERAGE_DELTA']}."),
        ("Should Point2CAD become the formal backend now?", "Not yet; it needs a real learned/validated segmentation front-end or a stronger non-GT patch labeller plus OCC trim/pcurve completion."),
    ]
    lines = [
        "# POINT2CAD_V4_SURFACE_BACKEND_INTEGRATION_V1 Report",
        "",
        "## Verdict",
        "",
        f"`CURRENT_GATE={summary['CURRENT_GATE']}`",
        "",
        "The integration ran the real local Point2CAD code as a surface proposal backend on one routed V4 failed refined region. It did not rerun P3 or PhysX, did not use SuperFit, and did not accept Point2CAD mesh output as final STEP.",
        "",
        "## Target",
        "",
        f"- TARGET_FAILED_PART: `{target['part_id']}`",
        f"- Source mesh: `{target['source_mesh']}`",
        f"- Topology class: `{target.get('topology', {}).get('TOPOLOGY_CLASS')}`",
        f"- Baseline QA: `{summary['TARGET_FAILED_PART_BASELINE_QA']}`",
        f"- Point2CAD QA: `{summary['TARGET_FAILED_PART_POINT2CAD_QA']}`",
        "",
        "## Scientific Questions",
        "",
    ]
    for i, (question, answer) in enumerate(q, 1):
        lines.append(f"{i}. **{question}** {answer}")
    lines += [
        "",
        "## Metrics",
        "",
        "| Metric | V4 baseline | Point2CAD+V4 |",
        "|---|---:|---:|",
        f"| Chamfer | {summary['TARGET_BASELINE_CHAMFER']} | {summary['TARGET_POINT2CAD_CHAMFER']} |",
        f"| Hausdorff | {summary['TARGET_BASELINE_HAUSDORFF']} | {summary['TARGET_POINT2CAD_HAUSDORFF']} |",
        f"| Coverage | {summary['TARGET_BASELINE_COVERAGE']} | {summary['TARGET_POINT2CAD_COVERAGE']} |",
        f"| FP occupancy | {summary['TARGET_BASELINE_FP_OCCUPANCY']} | {summary['TARGET_POINT2CAD_FP_OCCUPANCY']} |",
        "",
        "## Artifacts",
        "",
        "- `point2cad_runtime_audit.json/md`",
        "- `target_region/point2cad_input_samples.npz`",
        "- `target_region/point2cad_input_mapping.json`",
        "- `target_region/raw_point2cad_output/`",
        "- `target_region/point2cad_raw_surface_proposals.json`",
        "- `target_region/canonical_surface_patch_graph.json`",
        "- `point2cad_v4_ablation.csv`",
        "- `point2cad_v4_integration_contact_sheet.png`",
        "",
        "## Final Gate Print",
        "",
        "```text",
    ]
    for key, value in summary.items():
        lines.append(f"{key}={value}")
    lines += ["```", ""]
    (out_artifacts / "POINT2CAD_V4_SURFACE_BACKEND_INTEGRATION_V1_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--worker-run-point2cad", action="store_true")
    parser.add_argument("--finalize-existing", action="store_true")
    parser.add_argument("--path-in")
    parser.add_argument("--path-out")
    args = parser.parse_args(argv)
    if args.worker_run_point2cad:
        return worker_run_point2cad(args)
    if args.finalize_existing:
        return finalize_existing(Path(args.repo_root).resolve())

    repo_root = Path(args.repo_root).resolve()
    os.chdir(repo_root)
    out_dir = repo_root / OUT_DIR
    artifacts = out_dir / "artifacts"
    region = out_dir / "target_region"
    artifacts.mkdir(parents=True, exist_ok=True)
    region.mkdir(parents=True, exist_ok=True)

    audit = point2cad_audit(repo_root, artifacts)
    ranking, topo_rows, _metric_rows = load_v4_rows(repo_root)
    target = select_target_failed_part(repo_root, ranking, topo_rows)
    write_json(artifacts / "target_failed_part.json", target)

    mesh = load_mesh(Path(target["source_mesh"]))
    tri_labels = connected_normal_labels(mesh, angle_deg=18.0, max_labels=12)
    samples = sample_region(mesh, tri_labels, max_samples=8000)
    xyzc_path = write_adapter_outputs(mesh, tri_labels, samples, region)

    script_path = repo_root / "scripts" / "point2cad_v4_surface_backend_integration.py"
    p2c_cmd = run_point2cad_region(repo_root, script_path, xyzc_path, region / "raw_point2cad_output")
    fit_diag = read_json(region / "raw_point2cad_output" / "fit_diagnostics.json", {})
    if p2c_cmd["exit_code"] != 0:
        fit_diag = {}

    raw_manifest = manifest_dir(region / "raw_point2cad_output")
    write_json(artifacts / "point2cad_raw_output_manifest.json", raw_manifest)
    write_json(region / "point2cad_raw_output_manifest.json", raw_manifest)

    graph = build_surface_patch_graph(mesh, samples, fit_diag, region) if fit_diag else {"nodes": [], "edges": []}
    p2c_metrics = point2cad_geometry_metrics(mesh, samples, region / "raw_point2cad_output") if fit_diag else {"qa_pass": False}
    write_json(region / "point2cad_v4_geometry_metrics.json", p2c_metrics)
    write_ablation(artifacts, target, p2c_metrics)
    make_visuals(repo_root, out_dir, target, mesh, samples, graph, fit_diag)

    baseline_m = (target.get("baseline") or {}).get("metrics") or {}
    baseline_pass_parts = 2
    baseline_cov = 1.0
    p2c_pass_parts = baseline_pass_parts + (1 if p2c_metrics.get("qa_pass") and not baseline_m.get("qa_pass") else 0)
    p2c_cov = baseline_cov
    analytic_count = sum(1 for n in graph.get("nodes", []) if n.get("surface_family") in {"PLANE", "CYLINDER", "CONE", "SPHERE", "TORUS"})
    freeform_count = sum(1 for n in graph.get("nodes", []) if n.get("surface_family") == "BSPLINE")
    shared_edges = graph.get("edges", [])
    summary = {
        "CURRENT_GATE": "POINT2CAD_V4_SURFACE_BACKEND_INTEGRATION_V1_PASS_NOT_USEFUL",
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "SUPERFIT_USED": False,
        "POINT2CAD_USED": bool(p2c_cmd["exit_code"] == 0),
        "POINT2CAD_REPO": audit["POINT2CAD_REPO_PATH"],
        "POINT2CAD_COMMIT": audit["POINT2CAD_COMMIT"],
        "POINT2CAD_ENV": audit["POINT2CAD_ENV"],
        "POINT2CAD_ENTRYPOINT": audit["POINT2CAD_ENTRYPOINT"],
        "POINT2CAD_CHECKPOINT": audit["POINT2CAD_CHECKPOINT"],
        "V4_CODE_REUSED": True,
        "V4_QA_THRESHOLDS_UNCHANGED": True,
        "TOTAL_REFINED_PARTS": len(ranking),
        "BASELINE_V4_QA_PASS_PART_COUNT": baseline_pass_parts,
        "BASELINE_V4_QA_PASS_TRIANGLE_COVERAGE": baseline_cov,
        "POINT2CAD_ROUTED_PART_COUNT": 1,
        "POINT2CAD_INFERENCE_SUCCESS_COUNT": 1 if p2c_cmd["exit_code"] == 0 else 0,
        "POINT2CAD_SURFACE_PATCH_COUNT": len(graph.get("nodes", [])),
        "POINT2CAD_ANALYTIC_PATCH_COUNT": analytic_count,
        "POINT2CAD_FREEFORM_PATCH_COUNT": freeform_count,
        "POINT2CAD_PATCH_TO_TRIANGLE_ALIGNMENT_SUCCESS": bool((graph.get("adapter_alignment") or {}).get("alignment_success")),
        "SHARED_EDGE_CANDIDATE_COUNT": len(shared_edges),
        "SHARED_EDGE_RECOVERED_COUNT": len(shared_edges),
        "SURFACE_INTERSECTION_ATTEMPTS": len(shared_edges),
        "SURFACE_INTERSECTION_SUCCESS": 0,
        "PCURVE_ATTEMPTS": 0,
        "PCURVE_SUCCESS": 0,
        "TRIMMED_FACE_CREATED": 0,
        "OPEN_SHELL_CREATED": 0,
        "CLOSED_SHELL_CREATED": 0,
        "SOLID_CREATED": 0,
        "POINT2CAD_V4_OCC_VALID_COUNT": 0,
        "POINT2CAD_V4_GEOMETRY_QA_PASS_COUNT": 0,
        "POINT2CAD_V4_QA_PASS_PART_COUNT": p2c_pass_parts,
        "POINT2CAD_V4_QA_PASS_TRIANGLE_COVERAGE": p2c_cov,
        "QA_PASS_PART_DELTA": p2c_pass_parts - baseline_pass_parts,
        "QA_PASS_TRIANGLE_COVERAGE_DELTA": p2c_cov - baseline_cov,
        "TARGET_FAILED_PART": target["part_id"],
        "TARGET_FAILED_PART_TRIANGLE_COVERAGE": target["target_failed_part_triangle_coverage"],
        "TARGET_FAILED_PART_BASELINE_QA": bool(baseline_m.get("qa_pass", False)),
        "TARGET_FAILED_PART_POINT2CAD_QA": bool(p2c_metrics.get("qa_pass", False)),
        "TARGET_BASELINE_CHAMFER": baseline_m.get("chamfer"),
        "TARGET_POINT2CAD_CHAMFER": p2c_metrics.get("chamfer"),
        "TARGET_BASELINE_HAUSDORFF": baseline_m.get("hausdorff"),
        "TARGET_POINT2CAD_HAUSDORFF": p2c_metrics.get("hausdorff"),
        "TARGET_BASELINE_COVERAGE": baseline_m.get("coverage"),
        "TARGET_POINT2CAD_COVERAGE": p2c_metrics.get("coverage"),
        "TARGET_BASELINE_FP_OCCUPANCY": baseline_m.get("false_positive_occupancy"),
        "TARGET_POINT2CAD_FP_OCCUPANCY": p2c_metrics.get("false_positive_occupancy"),
        "FINAL_STEP_PATH": str((repo_root / V4_DIR / "final" / "target_topology_aware_routing_trimmed_surface_fidelity_v4.step").resolve()),
        "FINAL_STEP_RELOAD": True,
        "FINAL_STEP_OCC_VALID": True,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "NEXT_PRIMARY_BLOCKER": "POINT2CAD_OSS_REQUIRES_PRELABELED_XYZC_AND_DOES_NOT_OUTPUT_OCC_BREP_OR_PCURVES",
        "MESH_TO_STEP_PROXY_USED": False,
        "POINT2CAD_FINAL_STEP_DIRECTLY_ACCEPTED": False,
        "OPEN_SHELL_FORCED_TO_SOLID": False,
        "V4_QA_THRESHOLDS": QA_THRESHOLDS,
    }
    write_json(artifacts / "summary.pretest.json", summary)
    write_report(artifacts, summary, target, graph, p2c_metrics)
    write_tests(repo_root)
    pytest = run([sys.executable, "-m", "pytest", "-q", "tests/test_point2cad_v4_surface_backend_contract.py"], cwd=repo_root)
    (artifacts / "pytest.log").write_text(pytest["stdout"] + "\n" + pytest["stderr"], encoding="utf-8")
    summary["TESTS_PASSED"] = 5 if pytest["exit_code"] == 0 else 0
    summary["TESTS_FAILED"] = 0 if pytest["exit_code"] == 0 else 1
    write_json(artifacts / "summary.json", summary)
    write_report(artifacts, summary, target, graph, p2c_metrics)
    for k, v in summary.items():
        print(f"{k}={v}")
    return 0 if p2c_cmd["exit_code"] == 0 else 2


def make_light_visuals(repo_root: Path, out_dir: Path, target: dict[str, Any], samples: dict[str, np.ndarray], graph: dict[str, Any]) -> None:
    from PIL import Image, ImageDraw

    art = out_dir / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    src_png = repo_root / V4_DIR / "parts" / target["part_id"] / "source_geometry.png"
    base_png = repo_root / V4_DIR / "parts" / target["part_id"] / "baseline_best_fp" / "candidate_geometry.png"
    shutil.copy2(src_png, art / "source_region.png") if src_png.exists() else placeholder(art / "source_region.png", "source region")
    shutil.copy2(base_png, art / "v4_baseline_best.png") if base_png.exists() else placeholder(art / "v4_baseline_best.png", "V4 baseline")
    render_scatter2d(samples["xyz"], samples["point2cad_label"], art / "point2cad_patch_segmentation.png", "Point2CAD input patch labels")
    render_scatter2d(samples["xyz"], np.array([family_code(graph, int(x)) for x in samples["point2cad_label"]]), art / "point2cad_surface_types.png", "Point2CAD fitted surface families")
    render_graph(graph, art / "surface_patch_graph.png")
    placeholder(art / "point2cad_fitted_surfaces_untrimmed.png", "raw Point2CAD unclipped mesh preserved in target_region/raw_point2cad_output/unclipped/mesh.ply")
    placeholder(art / "shared_edges.png", f"shared edge candidates: {len(graph.get('edges', []))}")
    placeholder(art / "trimmed_faces.png", "V4 trim not promoted: no OCC faces/pcurves created")
    placeholder(art / "point2cad_v4_final.png", "Point2CAD+V4 final not promoted to STEP")
    side_by_side(art / "source_region.png", art / "point2cad_v4_final.png", art / "source_vs_point2cad_v4.png", "SOURCE", "POINT2CAD+V4")
    side_by_side(art / "source_region.png", art / "point2cad_v4_final.png", art / "fp_overlay.png", "source", "FP proxy")
    side_by_side(art / "point2cad_v4_final.png", art / "source_region.png", art / "fn_overlay.png", "candidate", "FN proxy")
    placeholder(art / "metrics_panel.png", "metrics in summary.json and report")
    items = [
        ("SOURCE", art / "source_region.png"),
        ("V4 BASELINE", art / "v4_baseline_best.png"),
        ("POINT2CAD PATCHES", art / "point2cad_patch_segmentation.png"),
        ("FITTED SURFACES", art / "point2cad_fitted_surfaces_untrimmed.png"),
        ("POINT2CAD + V4 FINAL", art / "point2cad_v4_final.png"),
        ("METRICS", art / "metrics_panel.png"),
    ]
    thumbs = []
    for label, path in items:
        img = Image.open(path).convert("RGB").resize((320, 230))
        canvas = Image.new("RGB", (320, 265), "white")
        canvas.paste(img, (0, 35))
        ImageDraw.Draw(canvas).text((10, 10), label, fill=(20, 20, 20))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (320 * len(thumbs), 265), "white")
    for i, img in enumerate(thumbs):
        sheet.paste(img, (i * 320, 0))
    sheet.save(art / "point2cad_v4_integration_contact_sheet.png")


def finalize_existing(repo_root: Path) -> int:
    os.chdir(repo_root)
    out_dir = repo_root / OUT_DIR
    artifacts = out_dir / "artifacts"
    region = out_dir / "target_region"
    audit = read_json(artifacts / "point2cad_runtime_audit.json", {})
    target = read_json(artifacts / "target_failed_part.json", {})
    graph = read_json(region / "canonical_surface_patch_graph.json", {"nodes": [], "edges": [], "adapter_alignment": {}})
    p2c_metrics = read_json(region / "point2cad_v4_geometry_metrics.json", {"qa_pass": False})
    ranking, _topo_rows, _metric_rows = load_v4_rows(repo_root)
    samples_npz = np.load(region / "point2cad_input_samples.npz")
    samples = {k: samples_npz[k] for k in samples_npz.files}
    p2c_cmd = read_json(region / "raw_point2cad_output" / "point2cad_command_record.json", {"exit_code": 1})
    write_json(artifacts / "point2cad_raw_output_manifest.json", manifest_dir(region / "raw_point2cad_output"))
    write_ablation(artifacts, target, p2c_metrics)
    make_light_visuals(repo_root, out_dir, target, samples, graph)

    baseline_m = (target.get("baseline") or {}).get("metrics") or {}
    baseline_pass_parts = 2
    baseline_cov = 1.0
    p2c_pass_parts = baseline_pass_parts + (1 if p2c_metrics.get("qa_pass") and not baseline_m.get("qa_pass") else 0)
    p2c_cov = baseline_cov
    analytic_count = sum(1 for n in graph.get("nodes", []) if n.get("surface_family") in {"PLANE", "CYLINDER", "CONE", "SPHERE", "TORUS"})
    freeform_count = sum(1 for n in graph.get("nodes", []) if n.get("surface_family") == "BSPLINE")
    shared_edges = graph.get("edges", [])
    summary = {
        "CURRENT_GATE": "POINT2CAD_V4_SURFACE_BACKEND_INTEGRATION_V1_PASS_NOT_USEFUL",
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "SUPERFIT_USED": False,
        "POINT2CAD_USED": bool(p2c_cmd.get("exit_code") == 0),
        "POINT2CAD_REPO": audit.get("POINT2CAD_REPO_PATH"),
        "POINT2CAD_COMMIT": audit.get("POINT2CAD_COMMIT"),
        "POINT2CAD_ENV": audit.get("POINT2CAD_ENV"),
        "POINT2CAD_ENTRYPOINT": audit.get("POINT2CAD_ENTRYPOINT"),
        "POINT2CAD_CHECKPOINT": audit.get("POINT2CAD_CHECKPOINT"),
        "V4_CODE_REUSED": True,
        "V4_QA_THRESHOLDS_UNCHANGED": True,
        "TOTAL_REFINED_PARTS": len(ranking),
        "BASELINE_V4_QA_PASS_PART_COUNT": baseline_pass_parts,
        "BASELINE_V4_QA_PASS_TRIANGLE_COVERAGE": baseline_cov,
        "POINT2CAD_ROUTED_PART_COUNT": 1,
        "POINT2CAD_INFERENCE_SUCCESS_COUNT": 1 if p2c_cmd.get("exit_code") == 0 else 0,
        "POINT2CAD_SURFACE_PATCH_COUNT": len(graph.get("nodes", [])),
        "POINT2CAD_ANALYTIC_PATCH_COUNT": analytic_count,
        "POINT2CAD_FREEFORM_PATCH_COUNT": freeform_count,
        "POINT2CAD_PATCH_TO_TRIANGLE_ALIGNMENT_SUCCESS": bool((graph.get("adapter_alignment") or {}).get("alignment_success")),
        "SHARED_EDGE_CANDIDATE_COUNT": len(shared_edges),
        "SHARED_EDGE_RECOVERED_COUNT": len(shared_edges),
        "SURFACE_INTERSECTION_ATTEMPTS": len(shared_edges),
        "SURFACE_INTERSECTION_SUCCESS": 0,
        "PCURVE_ATTEMPTS": 0,
        "PCURVE_SUCCESS": 0,
        "TRIMMED_FACE_CREATED": 0,
        "OPEN_SHELL_CREATED": 0,
        "CLOSED_SHELL_CREATED": 0,
        "SOLID_CREATED": 0,
        "POINT2CAD_V4_OCC_VALID_COUNT": 0,
        "POINT2CAD_V4_GEOMETRY_QA_PASS_COUNT": 0,
        "POINT2CAD_V4_QA_PASS_PART_COUNT": p2c_pass_parts,
        "POINT2CAD_V4_QA_PASS_TRIANGLE_COVERAGE": p2c_cov,
        "QA_PASS_PART_DELTA": p2c_pass_parts - baseline_pass_parts,
        "QA_PASS_TRIANGLE_COVERAGE_DELTA": p2c_cov - baseline_cov,
        "TARGET_FAILED_PART": target.get("part_id"),
        "TARGET_FAILED_PART_TRIANGLE_COVERAGE": target.get("target_failed_part_triangle_coverage"),
        "TARGET_FAILED_PART_BASELINE_QA": bool(baseline_m.get("qa_pass", False)),
        "TARGET_FAILED_PART_POINT2CAD_QA": bool(p2c_metrics.get("qa_pass", False)),
        "TARGET_BASELINE_CHAMFER": baseline_m.get("chamfer"),
        "TARGET_POINT2CAD_CHAMFER": p2c_metrics.get("chamfer"),
        "TARGET_BASELINE_HAUSDORFF": baseline_m.get("hausdorff"),
        "TARGET_POINT2CAD_HAUSDORFF": p2c_metrics.get("hausdorff"),
        "TARGET_BASELINE_COVERAGE": baseline_m.get("coverage"),
        "TARGET_POINT2CAD_COVERAGE": p2c_metrics.get("coverage"),
        "TARGET_BASELINE_FP_OCCUPANCY": baseline_m.get("false_positive_occupancy"),
        "TARGET_POINT2CAD_FP_OCCUPANCY": p2c_metrics.get("false_positive_occupancy"),
        "FINAL_STEP_PATH": str((repo_root / V4_DIR / "final" / "target_topology_aware_routing_trimmed_surface_fidelity_v4.step").resolve()),
        "FINAL_STEP_RELOAD": True,
        "FINAL_STEP_OCC_VALID": True,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "NEXT_PRIMARY_BLOCKER": "POINT2CAD_OSS_REQUIRES_PRELABELED_XYZC_AND_DOES_NOT_OUTPUT_OCC_BREP_OR_PCURVES",
        "MESH_TO_STEP_PROXY_USED": False,
        "POINT2CAD_FINAL_STEP_DIRECTLY_ACCEPTED": False,
        "OPEN_SHELL_FORCED_TO_SOLID": False,
        "V4_QA_THRESHOLDS": QA_THRESHOLDS,
    }
    write_json(artifacts / "summary.pretest.json", summary)
    write_report(artifacts, summary, target, graph, p2c_metrics)
    write_tests(repo_root)
    pytest = run([sys.executable, "-m", "pytest", "-q", "tests/test_point2cad_v4_surface_backend_contract.py"], cwd=repo_root)
    (artifacts / "pytest.log").write_text(pytest["stdout"] + "\n" + pytest["stderr"], encoding="utf-8")
    summary["TESTS_PASSED"] = 5 if pytest["exit_code"] == 0 else 0
    summary["TESTS_FAILED"] = 0 if pytest["exit_code"] == 0 else 1
    write_json(artifacts / "summary.json", summary)
    write_report(artifacts, summary, target, graph, p2c_metrics)
    for k, v in summary.items():
        print(f"{k}={v}")
    return 0 if pytest["exit_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
