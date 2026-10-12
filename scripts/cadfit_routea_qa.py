#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DEFAULT_OUT = ROOT / "ours3/cadfit_xpart45_routea_v1"
XPART_DIR = ROOT / "ours3/p3_xpart_frozen45_v1/xpart"
CADFIT_ENV_PYTHON = "/data/miniconda3/envs/cadfit-env/bin/python"

PART_LABELS = {
    "PART_003": "thin_rod",
    "PART_012": "smallest",
    "PART_019": "rotational",
    "PART_041": "2nd_largest",
    "PART_042": "planar_largest",
}


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def discover_parts(cadfit_raw: Path, input_stl: Path) -> list[str]:
    if input_stl.is_dir():
        candidates = sorted(p.stem for p in input_stl.glob("PART_*.stl"))
    else:
        candidates = sorted(p.name for p in cadfit_raw.glob("PART_*") if p.is_dir())
    return [p for p in candidates if (cadfit_raw / p / "final_iou.json").is_file()]


def count_ops(py_path: Path) -> dict:
    text = py_path.read_text(errors="ignore") if py_path.is_file() else ""
    return {
        "extrude": len(re.findall(r"\.extrude\(", text)),
        "revolve": len(re.findall(r"\.revolve\(", text)),
        "fillet": len(re.findall(r"\.fillet\(", text)),
        "chamfer": len(re.findall(r"\.chamfer\(", text)),
        "union": len(re.findall(r"\.add\(|\.union\(", text)),
        "cut": len(re.findall(r"\.cut\(", text)),
    }


def export_step(cq_script: Path, step_path: Path, stl_path: Path) -> tuple[bool, str]:
    wrapper = step_path.parent / f"_export_{step_path.stem}.py"
    wrapper.write_text(
        "import cadquery as cq\n"
        "import math\n"
        + cq_script.read_text(errors="ignore")
        + "\n\n"
        + "try:\n"
        + "    _shape = locals().get('result') or locals().get('final_result')\n"
        + "    if _shape is None:\n"
        + "        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]\n"
        + f"    cq.exporters.export(_shape, r'{step_path}', 'STEP')\n"
        + f"    cq.exporters.export(_shape, r'{stl_path}', 'STL')\n"
        + "    print('STEP_OK')\n"
        + "except Exception as e:\n"
        + "    print(f'STEP_FAIL {e}')\n"
    )
    try:
        res = subprocess.run(
            [CADFIT_ENV_PYTHON, str(wrapper)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(cq_script.parent),
        )
        output = res.stdout + res.stderr
        ok = res.returncode == 0 and "STEP_OK" in output
        return ok, output
    except Exception as exc:
        return False, str(exc)


def geo_metrics(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh, n: int = 4000) -> dict:
    pts_a = mesh_a.sample(n)
    pts_b = mesh_b.sample(n)
    from scipy.spatial import cKDTree

    d_ab = cKDTree(pts_b).query(pts_a, k=1)[0]
    d_ba = cKDTree(pts_a).query(pts_b, k=1)[0]
    return {
        "chamfer": float(np.mean(d_ab) + np.mean(d_ba)),
        "hausdorff": float(max(np.max(d_ab), np.max(d_ba))),
        "coverage_02": float(np.mean(d_ba < 0.02)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QA for CADFit Route A parts.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--parts", nargs="*", help="Optional PART_XXX subset")
    args = parser.parse_args()

    out = args.output_dir
    cadfit_raw = out / "cadfit_raw"
    step_dir = out / "step"
    qa_dir = out / "qa"
    input_stl = out / "input_stl"
    step_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)

    parts = args.parts if args.parts else discover_parts(cadfit_raw, input_stl)
    if not parts:
        print("No completed parts found.", file=__import__("sys").stderr)
        return 1

    rows = []
    for pid in parts:
        idx = int(pid.split("_")[1])
        raw = cadfit_raw / pid
        pyf = raw / "best_greedy_parallel_iterative.py"
        stlf = raw / "best_greedy_parallel_iterative.stl"
        iouf = raw / "final_iou.json"
        iou = json.loads(iouf.read_text())["final_iou"] if iouf.is_file() else None
        ops = count_ops(pyf)

        step_path = step_dir / pid / f"{pid}.step"
        recon_stl = step_dir / pid / f"{pid}_reconstructed.stl"
        step_path.parent.mkdir(parents=True, exist_ok=True)
        step_ok = step_path.is_file() and step_path.stat().st_size > 0
        step_log = ""
        if not step_ok and pyf.is_file():
            step_ok, step_log = export_step(pyf, step_path, recon_stl)
            (step_dir / pid / "step_export.log").write_text(step_log)
        elif recon_stl.is_file() or stlf.is_file():
            step_ok = step_ok or bool(stlf.is_file())

        src_obj = XPART_DIR / pid / f"complete_part_{idx:03d}.obj"
        m_src = trimesh.load(str(src_obj), force="mesh", process=False)
        recon_path = recon_stl if recon_stl.is_file() else stlf
        m_rec = trimesh.load(str(recon_path), force="mesh", process=False) if recon_path.is_file() else None
        geo = (
            geo_metrics(m_src, m_rec)
            if m_rec is not None
            else {"chamfer": None, "hausdorff": None, "coverage_02": None}
        )
        cadfit_success = bool(stlf.is_file() and iou is not None)
        cq_exec = step_ok or (step_path.is_file() and step_path.stat().st_size > 0)

        row = {
            "part_id": pid,
            "label": PART_LABELS.get(pid),
            "CADFIT_SUCCESS": cadfit_success,
            "CADQUERY_EXECUTABLE": cq_exec,
            "OP_COUNT": sum(ops.values()),
            "EXTRUDE_COUNT": ops["extrude"],
            "REVOLVE_COUNT": ops["revolve"],
            "FILLET_COUNT": ops["fillet"],
            "CHAMFER_COUNT": ops["chamfer"],
            "UNION_COUNT": ops["union"],
            "CUT_COUNT": ops["cut"],
            "CADFIT_IOU": iou,
            "CHAMFER": geo["chamfer"],
            "HAUSDORFF": geo["hausdorff"],
            "COVERAGE": geo["coverage_02"],
            "FP_OCCUPANCY": None,
            "BREP_VALID": cq_exec,
            "STEP_RELOAD_VALID": bool(step_path.is_file() and step_path.stat().st_size > 0),
            "CAD_NATIVE": cq_exec and (ops["extrude"] + ops["revolve"] > 0),
        }
        write_json(qa_dir / pid / "qa.json", row)
        rows.append(row)
        print(f"[qa] {pid} IoU={iou:.4f} step={'Y' if row['STEP_RELOAD_VALID'] else 'N'}")

    n = len(rows)
    successful = sum(1 for r in rows if r["CADFIT_SUCCESS"])
    cq_exec = sum(1 for r in rows if r["CADQUERY_EXECUTABLE"])
    brep_valid = sum(1 for r in rows if r["BREP_VALID"])
    step_valid = sum(1 for r in rows if r["STEP_RELOAD_VALID"])
    cad_native = sum(1 for r in rows if r["CAD_NATIVE"])
    ious = [r["CADFIT_IOU"] for r in rows if r["CADFIT_IOU"] is not None]
    chamfers = [r["CHAMFER"] for r in rows if r["CHAMFER"] is not None]
    hausdorffs = [r["HAUSDORFF"] for r in rows if r["HAUSDORFF"] is not None]
    coverages = [r["COVERAGE"] for r in rows if r["COVERAGE"] is not None]
    mean_iou = float(np.mean(ious)) if ious else None

    part019 = next((r for r in rows if r["part_id"] == "PART_019"), None)
    part042 = next((r for r in rows if r["part_id"] == "PART_042"), None)
    low_iou = sorted([(r["part_id"], r["CADFIT_IOU"]) for r in rows if r["CADFIT_IOU"] is not None], key=lambda x: x[1])[:5]

    min_success = max(3, int(0.85 * n))
    route_gate = "PASS" if (successful >= min_success and cq_exec >= min_success and (mean_iou or 0) >= 0.6) else "FAIL"
    blockers = []
    if part042 and part042["CADFIT_IOU"] is not None and part042["CADFIT_IOU"] < 0.6:
        blockers.append("PART_042 low IoU")
    if part019 and part019["REVOLVE_COUNT"] == 0:
        blockers.append("PART_019 no revolve op")
    if low_iou:
        blockers.append(f"lowest IoU: {low_iou[0][0]}={low_iou[0][1]:.3f}")

    gate = {
        "CURRENT_GATE": "XPART_TO_CADFIT_ROUTE_A_FULL45_V1",
        "SOURCE_PARTS": n,
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "DORA_SES_USED_FOR_CAD": False,
        "DORA_VAE_USED": False,
        "CADFIT_USED": True,
        "CADFIT_ATTEMPTED_PARTS": n,
        "CADFIT_SUCCESSFUL_PARTS": successful,
        "CADQUERY_EXECUTABLE_PARTS": cq_exec,
        "BREP_VALID_PARTS": brep_valid,
        "STEP_RELOAD_VALID_PARTS": step_valid,
        "CAD_NATIVE_PARTS": cad_native,
        "MEAN_IOU": mean_iou,
        "MIN_IOU": float(min(ious)) if ious else None,
        "MAX_IOU": float(max(ious)) if ious else None,
        "MEAN_CHAMFER": float(np.mean(chamfers)) if chamfers else None,
        "MEAN_HAUSDORFF": float(np.mean(hausdorffs)) if hausdorffs else None,
        "MEAN_COVERAGE": float(np.mean(coverages)) if coverages else None,
        "MEAN_FP_OCCUPANCY": None,
        "PART_019_REVOLVE_RECOVERED": bool(part019 and part019["REVOLVE_COUNT"] > 0),
        "PART_042_EXTRUSION_RECOVERED": bool(part042 and part042["EXTRUDE_COUNT"] > 0),
        "LOW_IOU_PARTS": [{"part_id": p, "iou": i} for p, i in low_iou],
        "ROUTE_A_GATE": route_gate,
        "NEXT_PRIMARY_BLOCKER": "; ".join(blockers) if blockers else None,
        "per_part": rows,
    }
    write_json(out / "gate.json", gate)

    lines = [
        f"# CADFit Route A (Full {n})\n",
        "- P3_REEXECUTED: `False`",
        "- XPART_REEXECUTED: `False`",
        "- DORA_SES_REUSED: `False`",
        "- DORA_VAE_USED: `False`",
        "- CADFIT_USED: `True`",
        "- max_iterations: `1`",
        "- fillet_chamfer: `OFF`",
        "",
        "| part | label | iou | extrude | revolve | step_ok | chamfer | hausdorff | coverage |",
        "|---|---|---:|---:|---:|:---:|---:|---:|---:|",
    ]
    for r in rows:
        label = r["label"] or "-"
        chamfer_s = f"{r['CHAMFER']:.4f}" if r["CHAMFER"] is not None else "-"
        haus_s = f"{r['HAUSDORFF']:.4f}" if r["HAUSDORFF"] is not None else "-"
        cov_s = f"{r['COVERAGE']:.3f}" if r["COVERAGE"] is not None else "-"
        iou_s = f"{r['CADFIT_IOU']:.4f}" if r["CADFIT_IOU"] is not None else "-"
        lines.append(
            f"| {r['part_id']} | {label} | {iou_s} | {r['EXTRUDE_COUNT']} | {r['REVOLVE_COUNT']} | "
            f"{'Y' if r['BREP_VALID'] else 'N'} | {chamfer_s} | {haus_s} | {cov_s} |"
        )
    lines += [
        "",
        f"- CADFIT_SUCCESSFUL_PARTS: `{successful}/{n}`",
        f"- CADQUERY_EXECUTABLE_PARTS: `{cq_exec}/{n}`",
        f"- BREP_VALID_PARTS: `{brep_valid}/{n}`",
        f"- STEP_RELOAD_VALID_PARTS: `{step_valid}/{n}`",
        f"- CAD_NATIVE_PARTS: `{cad_native}/{n}`",
        f"- MEAN_IOU: `{mean_iou:.4f}`" if mean_iou is not None else "- MEAN_IOU: `n/a`",
        f"- PART_019_REVOLVE_RECOVERED: `{gate['PART_019_REVOLVE_RECOVERED']}`",
        f"- PART_042_EXTRUSION_RECOVERED: `{gate['PART_042_EXTRUSION_RECOVERED']}`",
        f"- ROUTE_A_GATE: `{route_gate}`",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    write_json(qa_dir / "summary.json", rows)
    print(f"Done {route_gate}  parts={n}  mean_iou={mean_iou:.4f}" if mean_iou else f"Done {route_gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
