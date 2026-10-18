#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection

import cadquery as cq


PROTOCOL = "Synthetic-Complex-BRepGPT-Style-HighMesh-v1"
CASES = [
    "complex_flange_housing",
    "ribbed_mounting_bracket",
    "pocketed_boss_plate",
]
TESS = [
    (0.03, 0.05),
    (0.015, 0.035),
    (0.008, 0.025),
    (0.004, 0.018),
    (0.002, 0.012),
]


def sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def cyl_z(radius, height, x, y, z0):
    return cq.Workplane().newObject([cq.Solid.makeCylinder(radius, height, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))])


def cyl_x(radius, length, x0, y, z):
    return cq.Workplane().newObject([cq.Solid.makeCylinder(radius, length, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))])


def tri_prism(points, height, z):
    return cq.Workplane("XY").polyline(points).close().extrude(height).translate((0, 0, z))


def build_complex_flange_housing():
    profile = [
        (12, 0), (55, 0), (55, 8), (48, 8), (48, 16), (42, 16),
        (42, 26), (34, 26), (34, 38), (24, 38), (24, 52), (12, 52),
    ]
    solid = cq.Workplane("XY").polyline(profile).close().revolve(360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
    groove1 = cq.Workplane("XY").polyline([(42.5, 17.5), (53.5, 17.5), (53.5, 24.5), (42.5, 24.5)]).close().revolve(360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
    groove2 = cq.Workplane("XY").polyline([(31, 37.5), (39, 37.5), (39, 42.5), (31, 42.5)]).close().revolve(360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
    solid = solid.cut(groove1).cut(groove2)
    # Bolt and relief holes around the flange, kept away from groove edges.
    for r, n, rad in [(38, 6, 3.2), (26, 4, 2.6)]:
        for i in range(n):
            a = 2 * np.pi * i / n + (np.pi / 4 if n == 4 else 0)
            solid = solid.cut(cyl_y(rad, 70, r * np.cos(a), -8, r * np.sin(a)))
    return solid


def cyl_y(radius, length, x, y0, z):
    return cq.Workplane().newObject([cq.Solid.makeCylinder(radius, length, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))])


def build_ribbed_mounting_bracket():
    base = cq.Workplane("XY").box(120, 70, 12).translate((0, 0, 6))
    wall = cq.Workplane("XY").box(18, 62, 70).translate((-36, 0, 47))
    top = cq.Workplane("XY").box(62, 22, 16).translate((-20, 0, 84))
    solid = base.union(wall).union(top)
    # Three connected cylindrical bosses on the wall.
    for y, z, rad in [(-21, 45, 12), (0, 55, 14), (22, 45, 11)]:
        solid = solid.union(cyl_x(rad, 26, -52, y, z))
        solid = solid.cut(cyl_x(rad * 0.38, 50, -62, y, z))
    # Four triangular ribs from base to wall.
    for y0 in [-28, -10, 10, 28]:
        rib = cq.Workplane("YZ").polyline([(y0 - 4, 12), (y0 + 4, 12), (y0 + 4, 62), (y0 - 4, 12)]).close().extrude(16).translate((-44, 0, 0))
        solid = solid.union(rib)
    # Base slots and pockets.
    for x in [-34, 34]:
        solid = solid.cut(cq.Workplane("XY").box(18, 42, 16).translate((x, 0, 6)))
        for y in [-22, 22]:
            solid = solid.cut(cyl_z(4.2, 20, x, y, -2))
    solid = solid.cut(cq.Workplane("XY").box(34, 9, 20).translate((10, -35, 8)))
    return solid


def build_pocketed_boss_plate():
    solid = cq.Workplane("XY").box(130, 82, 14).translate((0, 0, 7))
    # Raised pads and bosses.
    for x, y, r in [(-42, -24, 13), (42, -24, 13), (-42, 24, 13), (42, 24, 13), (0, 0, 18)]:
        solid = solid.union(cq.Workplane("XY").box(28, 24, 8).translate((x, y, 18)))
        solid = solid.union(cyl_z(r, 16, x, y, 14))
        solid = solid.cut(cyl_z(r * 0.38, 40, x, y, -4))
    # Rectangular pockets and long slots.
    for x, y in [(-22, 0), (22, 0), (0, -31), (0, 31)]:
        solid = solid.cut(cq.Workplane("XY").box(26, 14, 10).translate((x, y, 14)))
    for x in [-58, 58]:
        solid = solid.cut(cq.Workplane("XY").box(10, 42, 18).translate((x, 0, 8)))
    # Side semi-cylindrical channels.
    for y in [-41, 41]:
        solid = solid.cut(cyl_x(5.5, 150, -75, y, 12))
    return solid


BUILDERS = {
    "complex_flange_housing": build_complex_flange_housing,
    "ribbed_mounting_bracket": build_ribbed_mounting_bracket,
    "pocketed_boss_plate": build_pocketed_boss_plate,
}


def shape_stats(obj):
    shape = obj.val()
    bb = shape.BoundingBox()
    return {
        "solid_count": len(shape.Solids()),
        "face_count": len(shape.Faces()),
        "volume": float(shape.Volume()),
        "bbox": [float(bb.xlen), float(bb.ylen), float(bb.zlen)],
        "valid": bool(shape.isValid()),
    }


def mesh_stats(path: Path):
    mesh = trimesh.load(path, force="mesh", process=True)
    comps = len(mesh.split(only_watertight=False))
    verts = np.asarray(mesh.vertices)
    return {
        "vertex_count": int(len(mesh.vertices)),
        "triangle_count": int(len(mesh.faces)),
        "connected_component_count": int(comps),
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "volume": float(mesh.volume),
        "surface_area": float(mesh.area),
        "bbox": [float(x) for x in mesh.extents],
        "nonfinite_vertex_count": int((~np.isfinite(verts)).any(axis=1).sum()) if len(verts) else 0,
    }


def mesh_ok(s):
    return s["connected_component_count"] == 1 and s["is_watertight"] and s["is_volume"] and s["volume"] > 0 and s["nonfinite_vertex_count"] == 0


def draw(ax, mesh, center, scale, color):
    verts = (np.asarray(mesh.vertices) - center) / scale
    faces = np.asarray(mesh.faces)
    view = np.array([[0.866, -0.5, 0.0], [0.2887, 0.5, -0.8165]])
    pts = verts @ view.T
    z = verts @ np.array([0.408, 0.408, 0.816])
    order = np.argsort(z[faces].mean(axis=1))
    tri = pts[faces[order]]
    shade = z[faces[order]].mean(axis=1)
    shade = (shade - shade.min()) / (np.ptp(shade) + 1e-9)
    base = np.array(matplotlib.colors.to_rgb(color))
    colors = np.clip(base * (0.56 + 0.44 * shade[:, None]), 0, 1)
    ax.add_collection(PolyCollection(tri, facecolors=colors, edgecolors=(0, 0, 0, 0.03), linewidths=0.04))
    ax.set_aspect("equal")
    ax.set_xlim(-0.72, 0.72)
    ax.set_ylim(-0.72, 0.72)
    ax.axis("off")


def render_mesh(path: Path, out: Path, title: str):
    mesh = trimesh.load(path, force="mesh", process=False)
    center = (mesh.bounds[0] + mesh.bounds[1]) / 2
    scale = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0])) or 1
    fig, ax = plt.subplots(figsize=(6, 5.4), dpi=180)
    draw(ax, mesh, center, scale, "#5b8fd9")
    fig.text(0.02, 0.98, title, ha="left", va="top", fontsize=9)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)


def generate_inputs(root: Path):
    ds = root / "datasets/synthetic_complex_brepgpt_style_v1"
    art = root / "artifacts/synthetic_complex_brepgpt_style_v1"
    all_audits = {}
    for case in CASES:
        case_dir = ds / case
        case_dir.mkdir(parents=True, exist_ok=True)
        builder = BUILDERS[case]
        obj = builder()
        cad = shape_stats(obj)
        if cad["solid_count"] != 1 or not cad["valid"] or cad["volume"] <= 0:
            raise RuntimeError(f"CAD gate failed for {case}: {cad}")
        gt_py = case_dir / "ground_truth.py"
        gt_py.write_text(f"import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts/synthetic_complex_brepgpt_style'))\nfrom run_complex_demo import BUILDERS\nimport cadquery as cq\nresult = BUILDERS['{case}']()\ncq.exporters.export(result, 'ground_truth.step')\n", encoding="utf-8")
        gt_step = case_dir / "ground_truth.step"
        cq.exporters.export(obj, str(gt_step))
        candidates = []
        for tol, ang in TESS:
            tmp = case_dir / f"candidate_tol_{tol:g}_ang_{ang:g}.stl"
            cq.exporters.export(obj, str(tmp), tolerance=tol, angularTolerance=ang)
            ms = mesh_stats(tmp)
            candidates.append({"path": tmp, "tol": tol, "ang": ang, **ms, "ok": mesh_ok(ms)})
        valid = [c for c in candidates if c["ok"] and c["triangle_count"] <= 180_000]
        if not valid:
            valid = [c for c in candidates if c["ok"]]
        chosen = max(valid, key=lambda c: c["triangle_count"])
        stl = case_dir / "input_high_mesh.stl"
        if stl.exists():
            stl.unlink()
        os.replace(chosen["path"], stl)
        for c in candidates:
            if c["path"].exists():
                c["path"].unlink()
        audit = {
            "protocol_name": PROTOCOL,
            "case_name": case,
            "selected_tolerance": chosen["tol"],
            "selected_angular_tolerance": chosen["ang"],
            "triangle_target": "prefer 80k-180k if geometry supports it",
            "triangle_target_reached": chosen["triangle_count"] >= 80_000,
            "ground_truth_step_faces": cad["face_count"],
            "ground_truth_solid_count": cad["solid_count"],
            "ground_truth_volume": cad["volume"],
            "ground_truth_bbox": cad["bbox"],
            "ground_truth_valid": cad["valid"],
            **{k: v for k, v in chosen.items() if k not in {"path", "tol", "ang", "ok"}},
            "stl_sha256": sha256(stl),
            "step_sha256": sha256(gt_step),
        }
        (case_dir / "mesh_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        render_mesh(stl, case_dir / "input_render.png", f"{case}\ntriangles={audit['triangle_count']} | STEP faces={audit['ground_truth_step_faces']}")
        all_audits[case] = audit
        print(f"GENERATED {case} triangles={audit['triangle_count']} step_faces={audit['ground_truth_step_faces']}")
    art.mkdir(parents=True, exist_ok=True)
    (art / "input_audits.json").write_text(json.dumps(all_audits, indent=2), encoding="utf-8")


def run_case(root: Path, case: str, workers: int, gpu: str, timeout: int, skip_existing: bool):
    ds = root / "datasets/synthetic_complex_brepgpt_style_v1" / case
    out = root / "outputs/synthetic_complex_brepgpt_style_v1_workers4" / case
    inp = out / "cadfit_input"
    inp.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ds / "input_high_mesh.stl", inp / "input_high_mesh.stl")
    obj = out / "input_high_mesh"
    status_path = out / "run_status.json"
    audit = json.loads((ds / "mesh_audit.json").read_text())
    status = {
        "protocol_name": PROTOCOL,
        "case_name": case,
        "prior_mode": "no_prior",
        "gpu_requested": gpu,
        "cadfit_inner_workers": workers,
        "step_face_count": audit["ground_truth_step_faces"],
        "input_triangle_count": audit["triangle_count"],
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": "",
        "runtime_seconds": 0,
        "exit_code": None,
        "status": "exception",
        "error": "",
    }
    if skip_existing and (obj / "final_iou.json").exists() and (obj / "best_greedy_parallel_iterative.stl").exists():
        status.update({"status": "success", "exit_code": 0, "error": "skipped_existing"})
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return status
    cmd = [
        sys.executable, "run_pipeline.py", str(inp),
        "--output-folder", str(out),
        "--max-iterations", "1",
        "--limit", "1",
        "--skip-existing",
    ]
    status["command"] = cmd
    env = os.environ.copy()
    env["CADFIT_INNER_WORKERS"] = str(workers)
    env["CUDA_VISIBLE_DEVICES"] = gpu
    t0 = time.time()
    try:
        with (out / "stdout.log").open("wb") as so, (out / "stderr.log").open("wb") as se:
            proc = subprocess.run(cmd, stdout=so, stderr=se, timeout=timeout, env=env)
        status["exit_code"] = proc.returncode
        if proc.returncode != 0:
            status["status"] = "process_error"
            status["error"] = f"run_pipeline exited {proc.returncode}"
        elif not ((obj / "best_greedy_parallel_iterative.py").exists() and (obj / "best_greedy_parallel_iterative.stl").exists() and (obj / "final_iou.json").exists()):
            status["status"] = "missing_output"
            status["error"] = "missing CADFit final outputs"
        else:
            iou = json.loads((obj / "final_iou.json").read_text())
            status["status"] = "success"
            status["final_iou"] = iou.get("final_iou")
            status["cadfit_reported_duration"] = iou.get("duration")
    except subprocess.TimeoutExpired:
        status["status"] = "timeout"
        status["error"] = f"timeout after {timeout}s"
    except Exception as exc:
        status["status"] = "exception"
        status["error"] = repr(exc)
    finally:
        status["runtime_seconds"] = time.time() - t0
        status["end_time"] = datetime.now(timezone.utc).isoformat()
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    return status


def export_step(script: Path, out_step: Path):
    try:
        ns = runpy.run_path(str(script))
        candidates = []
        for k in ["final_result", "result"]:
            if k in ns:
                candidates.append(ns[k])
        candidates += [v for v in ns.values() if hasattr(v, "val") or hasattr(v, "wrapped")]
        for obj in candidates:
            try:
                cq.exporters.export(obj, str(out_step))
                reopened = cq.importers.importStep(str(out_step)).val()
                return {"success": True, "faces": len(reopened.Faces()), "solids": len(reopened.Solids()), "error": ""}
            except Exception as exc:
                last = repr(exc)
        return {"success": False, "error": last if "last" in locals() else "no cadquery object"}
    except Exception as exc:
        return {"success": False, "error": repr(exc)}


def collect(root: Path):
    ds = root / "datasets/synthetic_complex_brepgpt_style_v1"
    outs = root / "outputs/synthetic_complex_brepgpt_style_v1_workers4"
    art = root / "artifacts/synthetic_complex_brepgpt_style_v1"
    rows = []
    for case in CASES:
        case_art = art / case
        case_art.mkdir(parents=True, exist_ok=True)
        for name in ["ground_truth.py", "ground_truth.step", "input_high_mesh.stl", "mesh_audit.json", "input_render.png"]:
            src = ds / case / name
            if src.exists():
                shutil.copy2(src, case_art / name)
        out = outs / case
        obj = out / "input_high_mesh"
        for src, dst in [
            (obj / "best_greedy_parallel_iterative.py", case_art / "generated_cad.py"),
            (obj / "best_greedy_parallel_iterative.stl", case_art / "reconstructed_cad.stl"),
            (obj / "final_iou.json", case_art / "final_iou.json"),
            (out / "run_status.json", case_art / "run_status.json"),
            (out / "stdout.log", case_art / "stdout.log"),
            (out / "stderr.log", case_art / "stderr.log"),
        ]:
            if src.exists():
                shutil.copy2(src, dst)
        step_audit = {"success": False, "error": "not run"}
        if (case_art / "generated_cad.py").exists():
            step_audit = export_step(case_art / "generated_cad.py", case_art / "reconstructed_cad.step")
        audit = json.loads((case_art / "mesh_audit.json").read_text())
        status = json.loads((case_art / "run_status.json").read_text()) if (case_art / "run_status.json").exists() else {}
        iou = json.loads((case_art / "final_iou.json").read_text()).get("final_iou", "") if (case_art / "final_iou.json").exists() else ""
        if (case_art / "reconstructed_cad.stl").exists():
            render_comparison(case_art, audit, status, iou)
        ops = count_ops(case_art / "generated_cad.py")
        rows.append({
            "case_name": case,
            "step_faces": audit["ground_truth_step_faces"],
            "input_triangles": audit["triangle_count"],
            "input_vertices": audit["vertex_count"],
            "watertight": audit["is_watertight"],
            "status": status.get("status", ""),
            "iou": iou,
            "runtime_seconds": status.get("runtime_seconds", ""),
            "step_export_success": step_audit.get("success", False),
            "generated_program_lines": ops["lines"],
            "extrude_count": ops["extrude"],
            "revolve_count": ops["revolve"],
            "cut_count": ops["cut"],
            "union_count": ops["union"],
            "error": status.get("error", ""),
        })
    fields = list(rows[0].keys()) if rows else []
    with (art / "demo_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    report = ["# Synthetic-Complex-BRepGPT-Style-HighMesh-v1", "", "Reference style: complex CAD/B-rep program reconstruction demo inspired by B-rep generative CAD work. This is not a BRepGPT benchmark and uses synthetic CadQuery-created inputs.", ""]
    report += ["| case | STEP faces | triangles | status | IoU | runtime s | STEP export |", "|---|---:|---:|---|---:|---:|---|"]
    for r in rows:
        report.append(f"| {r['case_name']} | {r['step_faces']} | {r['input_triangles']} | {r['status']} | {r['iou']} | {r['runtime_seconds']} | {r['step_export_success']} |")
    for r in rows:
        case = r["case_name"]
        report += ["", f"## {case}", "", f"![input]({case}/input_render.png)", f"![comparison]({case}/comparison.png)"]
    (art / "demo_report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"SUMMARY={art / 'demo_summary.csv'}")
    print(f"REPORT={art / 'demo_report.md'}")


def count_ops(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    return {
        "lines": len(text.splitlines()),
        "extrude": len(re.findall(r"\.extrude\s*\(", text, re.I)),
        "revolve": len(re.findall(r"\.revolve\s*\(", text, re.I)),
        "cut": len(re.findall(r"\.cut\s*\(|hole\s*\(", text, re.I)),
        "union": len(re.findall(r"\.union\s*\(|\.add\s*\(", text, re.I)),
    }


def render_comparison(case_art: Path, audit: dict, status: dict, iou):
    inp = trimesh.load(case_art / "input_high_mesh.stl", force="mesh", process=False)
    rec = trimesh.load(case_art / "reconstructed_cad.stl", force="mesh", process=False)
    # CADFit writes reconstructed STL in its normalized coordinate frame, while
    # the synthetic input keeps CAD model units. Normalize each side for visual QA.
    inp_center = (inp.bounds[0] + inp.bounds[1]) / 2
    rec_center = (rec.bounds[0] + rec.bounds[1]) / 2
    inp_scale = float(np.linalg.norm(inp.bounds[1] - inp.bounds[0])) or 1
    rec_scale = float(np.linalg.norm(rec.bounds[1] - rec.bounds[0])) or 1
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), dpi=180)
    draw(axes[0], inp, inp_center, inp_scale, "#5b8fd9")
    draw(axes[1], rec, rec_center, rec_scale, "#d9904f")
    axes[0].set_title("Input high mesh", fontsize=10)
    axes[1].set_title("CADFit reconstruction", fontsize=10)
    fig.text(0.5, 0.02, f"{audit['case_name']} | triangles={audit['triangle_count']} | STEP faces={audit['ground_truth_step_faces']} | IoU={iou} | runtime={status.get('runtime_seconds','')} | no_prior | normalized visual comparison", ha="center", fontsize=8)
    fig.savefig(case_art / "comparison.png", bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--timeout-seconds", type=int, default=5400)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()
    root = Path.cwd()
    if args.generate:
        generate_inputs(root)
    if args.run:
        results = []
        for case in CASES:
            res = run_case(root, case, args.workers, args.gpu, args.timeout_seconds, args.skip_existing)
            results.append(res)
            print(f"RUN {case} {res['status']} {res['runtime_seconds']:.1f}s", flush=True)
        out_root = root / "outputs/synthetic_complex_brepgpt_style_v1_workers4"
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "run_summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    if args.collect:
        collect(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
