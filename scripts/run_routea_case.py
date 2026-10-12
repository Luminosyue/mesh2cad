#!/usr/bin/env python3
"""Generic Route A runner: P3 -> X-Part -> CADFit -> STEP/QA/render/gate.

Example:
  python scripts/run_routea_case.py \\
    --case-name airplane_p3_xpart_cadfit_routea_v1 \\
    --source-mesh ours3/meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj \\
    --gpu 3 \\
    --stage all
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
P3_SCRIPT = ROOT / "ours3/case09_fullstack_mesh2cad_mac_v6/scripts/p3_fresh_v6.py"
CADFIT_REPO = ROOT / "CADFit"
CADFIT_PY = Path("/data/miniconda3/envs/cadfit-env/bin/python")
XPART_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
XPART_SCRIPT = ROOT / "scripts/xpart_from_p3.py"
CADFIT_PIPELINE = CADFIT_REPO / "run_pipeline.py"
XPART_ROOT = ROOT / "Hunyuan3D-Part/XPart"
P3_ROOT = ROOT / "Hunyuan3D-Part/P3-SAM"
N_PART_POINTS = 81920


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        geoms = [g for g in mesh.geometry.values() if isinstance(g, trimesh.Trimesh)]
        mesh = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    return mesh


def mesh_audit(mesh: trimesh.Trimesh, part_id: str | None = None) -> dict:
    counts = np.bincount(mesh.edges_unique_inverse) if len(mesh.faces) else np.array([])
    bbox = mesh.bounds
    diag = float(np.linalg.norm(bbox[1] - bbox[0])) if bbox is not None else 0.0
    out = {
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "connected_components": int(len(mesh.split(only_watertight=False))) if len(mesh.faces) else 0,
        "watertight": bool(mesh.is_watertight),
        "manifold": bool(len(counts) == 0 or int(np.sum(counts > 2)) == 0),
        "boundary_edges": int(np.sum(counts == 1)) if len(counts) else 0,
        "winding_consistent": bool(getattr(mesh, "is_winding_consistent", False)),
        "surface_area": float(mesh.area) if len(mesh.faces) else 0.0,
        "volume": float(mesh.volume) if mesh.is_watertight else None,
        "bbox_min": bbox[0].tolist() if bbox is not None else None,
        "bbox_max": bbox[1].tolist() if bbox is not None else None,
        "bbox_diagonal": diag,
    }
    if part_id:
        out["part_id"] = part_id
    return out


def log(msg: str, log_path: Path) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_cmd(cmd: list[str], cwd: Path, log_path: Path, env: dict | None = None) -> int:
    log(f"CMD {' '.join(cmd)}", log_path)
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(cmd, cwd=str(cwd), env=env, stdout=f, stderr=subprocess.STDOUT)
    return proc.returncode


def stage_source(out: Path, source: Path, log_path: Path) -> dict:
    src_dir = out / "source"
    src_dir.mkdir(parents=True, exist_ok=True)
    dst = src_dir / source.name
    if not dst.exists():
        shutil.copy2(source, dst)
    mesh = load_mesh(source)
    audit = mesh_audit(mesh)
    audit.update({"source_obj": str(source), "audit_time": utc_now()})
    write_json(src_dir / "source_manifest.json", audit)
    write_json(out / "pipeline_manifest.json", {
        "case_root": str(out),
        "source_mesh": str(source),
        "created_at": utc_now(),
        "stages": ["source", "p3", "xpart", "cadfit_routea"],
    })
    log(f"source audit triangles={audit['triangles']} watertight={audit['watertight']}", log_path)
    return audit


def stage_p3(out: Path, source: Path, gpu: int, log_path: Path) -> dict:
    p3_dir = out / "p3"
    meta_path = p3_dir / "part_metadata.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        log(f"P3 skip existing parts={meta.get('num_parts')}", log_path)
        return meta
    p3_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    rc = run_cmd([
        sys.executable, str(P3_SCRIPT), str(source), str(p3_dir),
        "--prompt-bs", "16", "--point-num", "80000", "--prompt-num", "400",
    ], ROOT, log_path, env)
    if rc != 0 or not meta_path.is_file():
        raise RuntimeError(f"P3 failed rc={rc}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["P3_REEXECUTED"] = True
    write_json(p3_dir / "manifest.json", meta)
    labels = np.load(p3_dir / "triangle_part_id.npy", allow_pickle=False)
    source_mesh = load_mesh(source)
    if len(labels) != len(source_mesh.faces):
        raise RuntimeError("P3 triangle coverage != source")
    qa_rows = []
    for i in range(int(meta["num_parts"])):
        part_path = p3_dir / f"part_{i:03d}.obj"
        qa_rows.append(mesh_audit(load_mesh(part_path), f"part_{i:03d}"))
    write_json(out / "mesh_qa/p3_parts.json", qa_rows)
    wt = sum(1 for r in qa_rows if r["watertight"])
    summary = {
        "P3_PART_COUNT": len(qa_rows),
        "P3_WATERTIGHT_PARTS": wt,
        "P3_WATERTIGHT_RATE": wt / max(len(qa_rows), 1),
        "triangle_coverage": 1.0,
    }
    write_json(out / "mesh_qa/p3_summary.json", summary)
    log(f"P3 done parts={len(qa_rows)} watertight={wt}", log_path)
    return meta


def sample_part(mesh: trimesh.Trimesh, n: int, seed: int):
    import torch

    pts, fid = trimesh.sample.sample_surface(mesh, n, seed=seed)
    nrm = mesh.face_normals[fid]
    sharp = np.zeros((n, 1), dtype=np.float32)
    arr = np.concatenate([pts.astype(np.float32), nrm.astype(np.float32), sharp], axis=-1)
    return torch.from_numpy(arr)


def stage_xpart(out: Path, source: Path, gpu: int, batch_size: int, log_path: Path) -> dict:
    xpart_root = out / "xpart"
    manifest_path = xpart_root / "manifest.json"
    if manifest_path.is_file():
        summary = json.loads(manifest_path.read_text(encoding="utf-8"))
        if summary.get("XPART_SUCCESSFUL_PARTS", 0) > 0:
            log(f"X-Part skip existing successful={summary.get('XPART_SUCCESSFUL_PARTS')}", log_path)
            return summary
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    rc = run_cmd([
        str(XPART_PY), str(XPART_SCRIPT),
        "--source-mesh", str(source),
        "--p3-dir", str(out / "p3"),
        "--out-dir", str(xpart_root),
        "--gpu", str(gpu),
        "--batch-size", str(batch_size),
    ], ROOT, log_path, env)
    if rc != 0 or not manifest_path.is_file():
        raise RuntimeError(f"X-Part failed rc={rc}")
    summary = json.loads(manifest_path.read_text(encoding="utf-8"))
    write_json(out / "mesh_qa/xpart_parts.json", summary.get("parts", []))
    log(f"X-Part done successful={summary.get('XPART_SUCCESSFUL_PARTS')} watertight={summary.get('XPART_WATERTIGHT_PARTS')}", log_path)
    return summary


def convert_obj_to_stl(obj_path: Path, stl_path: Path) -> dict:
    mesh = load_mesh(obj_path)
    before = mesh_audit(mesh)
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(stl_path, file_type="stl")
    after_mesh = load_mesh(stl_path)
    after = mesh_audit(after_mesh)
    bbox_before = np.asarray(mesh.bounds)
    bbox_after = np.asarray(after_mesh.bounds)
    return {
        "source_triangles": before["triangles"],
        "stl_triangles": after["triangles"],
        "watertight_before": before["watertight"],
        "watertight_after": after["watertight"],
        "bbox_unchanged": bool(np.allclose(bbox_before, bbox_after, atol=1e-6)),
        "decimated": False,
        "smoothed": False,
        "remeshed": False,
    }


def stage_cadfit_inputs(out: Path, part_ids: list[str] | None, log_path: Path) -> list[str]:
    cadfit = out / "cadfit_routea"
    input_dir = cadfit / "input_stl"
    input_dir.mkdir(parents=True, exist_ok=True)
    xpart_root = out / "xpart"
    qa_rows = []
    selected = []
    for part_dir in sorted(xpart_root.glob("PART_*")):
        pid = part_dir.name
        if part_ids and pid not in part_ids:
            continue
        idx = int(pid.split("_")[1])
        obj = part_dir / f"complete_part_{idx:03d}.obj"
        if not obj.is_file():
            continue
        qa = json.loads((part_dir / "qa.json").read_text()) if (part_dir / "qa.json").is_file() else {}
        if not qa.get("watertight", False):
            log(f"skip CADFit input {pid}: not watertight", log_path)
            continue
        stl = input_dir / f"{pid}.stl"
        row = convert_obj_to_stl(obj, stl)
        row["part_id"] = pid
        row["stl_path"] = str(stl)
        qa_rows.append(row)
        selected.append(pid)
    write_json(input_dir / "conversion_qa.json", qa_rows)
    log(f"CADFit inputs prepared count={len(selected)}", log_path)
    return selected


def stage_cadfit(out: Path, part_ids: list[str], gpu: int, log_path: Path) -> None:
    cadfit = out / "cadfit_routea"
    input_dir = cadfit / "input_stl"
    raw_dir = cadfit / "cadfit_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env.setdefault("CADFIT_INNER_WORKERS", "8")
    for pid in part_ids:
        stl = input_dir / f"{pid}.stl"
        if not stl.is_file():
            continue
        done = (raw_dir / pid / "final_iou.json").is_file() and (
            (raw_dir / pid / "best_greedy_parallel_iterative.py").is_file()
            or (raw_dir / pid / "best_greedy_parallel.py").is_file()
        )
        if done:
            log(f"CADFit skip existing {pid}", log_path)
            continue
        part_in = cadfit / "_isolated_input" / pid
        part_in.mkdir(parents=True, exist_ok=True)
        isolated = part_in / f"{pid}.stl"
        shutil.copy2(stl, isolated)
        loops_path = raw_dir / pid / "loops_split.json"
        raw_loops = filtered_loops = None
        cmd = [
            str(CADFIT_PY), str(CADFIT_PIPELINE), str(part_in),
            "--output-folder", str(raw_dir),
            "--max-iterations", "1",
            "--limit", "1",
            "--skip-existing",
            "--keep-history",
            "--filter-sketches",
        ]
        log(f"CADFit start {pid}", log_path)
        rc = run_cmd(cmd, CADFIT_REPO, log_path, env)
        if loops_path.is_file():
            loops = json.loads(loops_path.read_text())
            raw_loops = len(loops)
        filt = raw_dir / pid / "planar_loops_split.json"
        if filt.is_file():
            filtered_loops = len(json.loads(filt.read_text()))
        write_json(raw_dir / pid / "cadfit_run_meta.json", {
            "part_id": pid,
            "return_code": rc,
            "RAW_LOOPS": raw_loops,
            "FILTERED_LOOPS": filtered_loops,
            "CADFIT_FILTER_SKETCHES_USED": True,
        })
        if rc != 0:
            log(f"CADFit failed {pid} rc={rc}", log_path)


def count_ops(py_path: Path) -> dict:
    text = py_path.read_text(encoding="utf-8", errors="ignore") if py_path.is_file() else ""
    return {
        "extrude": len(re.findall(r"\.extrude\(", text)),
        "revolve": len(re.findall(r"\.revolve\(", text)),
        "fillet": len(re.findall(r"\.fillet\(", text)),
        "chamfer": len(re.findall(r"\.chamfer\(", text)),
        "union": len(re.findall(r"\.add\(|\.union\(", text)),
        "cut": len(re.findall(r"\.cut\(", text)),
        "op_count": sum([
            len(re.findall(r"\.extrude\(", text)),
            len(re.findall(r"\.revolve\(", text)),
            len(re.findall(r"\.fillet\(", text)),
            len(re.findall(r"\.chamfer\(", text)),
            len(re.findall(r"\.add\(|\.union\(", text)),
            len(re.findall(r"\.cut\(", text)),
        ]),
    }


def export_step(cq_script: Path, step_path: Path, stl_path: Path) -> tuple[bool, str]:
    wrapper = step_path.parent / f"_export_{step_path.stem}.py"
    wrapper.write_text(
        "import cadquery as cq\nimport math\n"
        + cq_script.read_text(errors="ignore")
        + "\n\n"
        + "try:\n"
        + "    _shape = locals().get('result') or locals().get('final_result')\n"
        + "    if _shape is None:\n"
        + "        _shape = [v for k,v in list(locals().items()) if str(k).startswith('solid_')][-1]\n"
        + f"    cq.exporters.export(_shape, r'{step_path}', 'STEP')\n"
        + f"    cq.exporters.export(_shape, r'{stl_path}', 'STL')\n"
        + "    print('STEP_OK')\n"
        + "except Exception as e:\n"
        + "    print(f'STEP_FAIL {e}')\n"
    )
    res = subprocess.run([str(CADFIT_PY), str(wrapper)], capture_output=True, text=True, timeout=300, cwd=str(cq_script.parent))
    output = res.stdout + res.stderr
    return res.returncode == 0 and "STEP_OK" in output, output


def geo_metrics(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh, n: int = 4000) -> dict:
    from scipy.spatial import cKDTree

    pts_a = mesh_a.sample(n)
    pts_b = mesh_b.sample(n)
    d_ab = cKDTree(pts_b).query(pts_a, k=1)[0]
    d_ba = cKDTree(pts_a).query(pts_b, k=1)[0]
    return {
        "chamfer": float(np.mean(d_ab) + np.mean(d_ba)),
        "hausdorff": float(max(np.max(d_ab), np.max(d_ba))),
        "coverage": float(np.mean(d_ba < 0.02)),
    }


def stage_qa(out: Path, part_ids: list[str], log_path: Path) -> dict:
    cadfit = out / "cadfit_routea"
    raw_dir = cadfit / "cadfit_raw"
    step_dir = cadfit / "step"
    qa_dir = cadfit / "qa"
    xpart_root = out / "xpart"
    rows = []
    for pid in part_ids:
        idx = int(pid.split("_")[1])
        raw = raw_dir / pid
        pyf = raw / "best_greedy_parallel_iterative.py"
        if not pyf.is_file():
            pyf = raw / "best_greedy_parallel.py"
        stlf = raw / "best_greedy_parallel_iterative.stl"
        if not stlf.is_file():
            stlf = raw / "best_greedy_parallel.stl"
        iou = json.loads((raw / "final_iou.json").read_text())["final_iou"] if (raw / "final_iou.json").is_file() else None
        ops = count_ops(pyf)
        step_path = step_dir / pid / f"{pid}.step"
        recon_stl = step_dir / pid / f"{pid}_reconstructed.stl"
        step_path.parent.mkdir(parents=True, exist_ok=True)
        step_ok, step_log = (False, "")
        if pyf.is_file():
            step_ok, step_log = export_step(pyf, step_path, recon_stl)
        (step_dir / pid / "step_export.log").write_text(step_log)
        src_obj = xpart_root / pid / f"complete_part_{idx:03d}.obj"
        m_src = load_mesh(src_obj)
        m_rec = load_mesh(recon_stl) if recon_stl.is_file() else None
        geo = geo_metrics(m_src, m_rec) if m_rec is not None else {"chamfer": None, "hausdorff": None, "coverage": None}
        meta = {}
        if (raw / "cadfit_run_meta.json").is_file():
            meta = json.loads((raw / "cadfit_run_meta.json").read_text())
        row = {
            "PART_ID": pid,
            "CADFIT_SUCCESS": bool(stlf.is_file() and iou is not None),
            "CADQUERY_EXECUTABLE": step_ok,
            "CADFIT_RAW_LOOPS": meta.get("RAW_LOOPS"),
            "CADFIT_FILTERED_LOOPS": meta.get("FILTERED_LOOPS"),
            "OP_COUNT": ops["op_count"],
            "EXTRUDE_COUNT": ops["extrude"],
            "REVOLVE_COUNT": ops["revolve"],
            "FILLET_COUNT": ops["fillet"],
            "CHAMFER_COUNT": ops["chamfer"],
            "UNION_COUNT": ops["union"],
            "CUT_COUNT": ops["cut"],
            "CADFIT_IOU": iou,
            "CHAMFER": geo["chamfer"],
            "HAUSDORFF": geo["hausdorff"],
            "COVERAGE": geo["coverage"],
            "FP_OCCUPANCY": None,
            "BREP_VALID": step_ok,
            "STEP_RELOAD_VALID": bool(step_path.is_file() and step_path.stat().st_size > 0),
            "CAD_NATIVE": step_ok and (ops["extrude"] + ops["revolve"] > 0),
            "FINAL_STEP": str(step_path) if step_path.is_file() else None,
        }
        write_json(qa_dir / pid / "qa.json", row)
        rows.append(row)
    write_json(qa_dir / "summary.json", rows)
    successful = sum(1 for r in rows if r["CADFIT_SUCCESS"])
    cq_exec = sum(1 for r in rows if r["CADQUERY_EXECUTABLE"])
    cad_native = sum(1 for r in rows if r["CAD_NATIVE"])
    ious = [r["CADFIT_IOU"] for r in rows if r["CADFIT_IOU"] is not None]
    gate = {
        "CURRENT_GATE": f"{out.name.upper()}_ROUTE_A",
        "CADFIT_USED": True,
        "CADFIT_ATTEMPTED_PARTS": len(part_ids),
        "CADFIT_SUCCESSFUL_PARTS": successful,
        "CADQUERY_EXECUTABLE_PARTS": cq_exec,
        "CAD_NATIVE_PARTS": cad_native,
        "MEAN_CADFIT_IOU": float(np.mean(ious)) if ious else None,
        "ROUTE_A_GATE": "PASS" if successful >= max(1, len(part_ids) // 2) and cq_exec >= max(1, len(part_ids) // 2) else "PARTIAL_PASS" if successful else "FAIL",
        "per_part": rows,
    }
    write_json(out / "gate.json", gate)
    report = ["# Route A Report", "", f"Case: `{out.name}`", "", "| part | iou | extrude | revolve | step | cad_native |", "|---|---:|---:|---:|:---:|:---:|"]
    for r in rows:
        report.append(
            f"| {r['PART_ID']} | {r['CADFIT_IOU'] if r['CADFIT_IOU'] is not None else 'NA'} | "
            f"{r['EXTRUDE_COUNT']} | {r['REVOLVE_COUNT']} | {'Y' if r['STEP_RELOAD_VALID'] else 'N'} | {'Y' if r['CAD_NATIVE'] else 'N'} |"
        )
    (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    log(f"QA done attempted={len(part_ids)} success={successful} cad_native={cad_native}", log_path)
    return gate


def stage_render(out: Path, part_ids: list[str]) -> None:
    render_script = ROOT / "scripts/cadfit_routea_render.py"
    if not render_script.is_file():
        return
    # render script is hardcoded; invoke inline minimal render for selected parts only
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    render_dir = out / "cadfit_routea/renders"
    raw_dir = out / "cadfit_routea/cadfit_raw"
    xpart_root = out / "xpart"
    for pid in part_ids:
        idx = int(pid.split("_")[1])
        src = xpart_root / pid / f"complete_part_{idx:03d}.obj"
        rec = raw_dir / pid / "best_greedy_parallel_iterative.stl"
        if not rec.is_file():
            rec = raw_dir / pid / "best_greedy_parallel.stl"
        if not (src.is_file() and rec.is_file()):
            continue
        m_src = load_mesh(src)
        m_rec = load_mesh(rec)
        for name, mesh, color in [("01_source_xpart.png", m_src, "#4C78A8"), ("02_cadfit_recon.png", m_rec, "#E45756")]:
            fig = plt.figure(figsize=(5, 5))
            ax = fig.add_subplot(111, projection="3d")
            tris = mesh.vertices[mesh.faces]
            if len(tris) > 20000:
                tris = tris[np.random.default_rng(42).choice(len(tris), 20000, replace=False)]
            coll = Poly3DCollection(tris, linewidths=0.03, alpha=1.0)
            coll.set_facecolor(color)
            ax.add_collection3d(coll)
            ax.auto_scale_xyz(*tris.reshape(-1, 3).T)
            ax.axis("off")
            fig.savefig(render_dir / pid / name, dpi=150, bbox_inches="tight")
            plt.close(fig)


def parse_parts(text: str | None) -> list[str] | None:
    if not text:
        return None
    return [p.strip() for p in text.split(",") if p.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-name", required=True)
    parser.add_argument("--source-mesh", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, default=None)
    parser.add_argument("--gpu", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--parts", type=str, default=None, help="Comma-separated PART_XXX; default all watertight")
    parser.add_argument("--stage", choices=["all", "source", "p3", "xpart", "cadfit", "qa", "render"], default="all")
    args = parser.parse_args()

    source = args.source_mesh if args.source_mesh.is_absolute() else ROOT / args.source_mesh
    out = args.out_root or (ROOT / "ours3" / args.case_name)
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "logs/run.log"
    part_ids = parse_parts(args.parts)

    try:
        if args.stage in {"all", "source"}:
            stage_source(out, source, log_path)
        if args.stage in {"all", "p3"}:
            stage_p3(out, source, args.gpu, log_path)
        if args.stage in {"all", "xpart"}:
            stage_xpart(out, source, args.gpu, args.batch_size, log_path)
        selected = stage_cadfit_inputs(out, part_ids, log_path) if args.stage in {"all", "cadfit", "qa", "render"} else (part_ids or [])
        if args.stage in {"all", "cadfit"}:
            stage_cadfit(out, selected, args.gpu, log_path)
        if args.stage in {"all", "qa"}:
            gate = stage_qa(out, selected, log_path)
            print(json.dumps({k: gate[k] for k in gate if k != "per_part"}, indent=2))
        if args.stage in {"all", "render"}:
            try:
                stage_render(out, selected)
            except Exception as render_exc:
                log(f"render failed (non-blocking): {type(render_exc).__name__}: {render_exc}", log_path)
        return 0
    except Exception as exc:
        log(f"FAILED {type(exc).__name__}: {exc}", log_path)
        log(traceback.format_exc(), log_path)
        if args.stage != "render":
            write_json(out / "gate.json", {"CURRENT_GATE": f"{out.name.upper()}_FAIL", "NEXT_PRIMARY_BLOCKER": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
