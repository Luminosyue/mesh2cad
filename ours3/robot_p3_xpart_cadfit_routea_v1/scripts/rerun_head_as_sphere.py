#!/usr/bin/env python3
"""Replace robot PART_005 (head) CAD with a sphere / ellipse-revolve instead of the thin extrusion."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CASE = ROOT / "ours3/robot_p3_xpart_cadfit_routea_v1"
CADFIT = ROOT / "CADFit"
GT = CASE / "cadfit_routea/input_stl/PART_005.stl"
OUT = CASE / "cadfit_routea/head_sphere_rerun"
RAW = CASE / "cadfit_routea/cadfit_raw/PART_005"
STEP_DIR = CASE / "cadfit_routea/step/PART_005"
BACKUP = CASE / "cadfit_routea/cadfit_raw/PART_005_maxiter1_extrude_backup"

sys.path.insert(0, str(CADFIT))
from iou import mesh_iou_cpu_boolean as compute_iou  # noqa: E402


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def write_sphere_script(path: Path, radius: float, stl_path: Path) -> None:
    path.write_text(
        "import cadquery as cq\n"
        "import math\n\n"
        f"result = cq.Workplane('XY').sphere({radius:.8f})\n"
        f"cq.exporters.export(result, r'{stl_path}')\n"
        "print('OK')\n"
    )


def write_ellipse_revolve_script(path: Path, rx: float, ry: float, rz: float, stl_path: Path) -> None:
    # Half-ellipse in XZ, revolve around Z → ellipsoid aligned with CADFit local axes.
    path.write_text(
        "import cadquery as cq\n"
        "import math\n\n"
        f"rx, ry, rz = {rx:.8f}, {ry:.8f}, {rz:.8f}\n"
        "wp = cq.Workplane('XZ')\n"
        "wp = wp.moveTo(0, -rz)\n"
        "wp = wp.ellipseArc(rx, rz, -90, 90)\n"
        "wp = wp.close()\n"
        "result = wp.revolve(360, (0, 0, 0), (0, 1, 0))\n"
        f"cq.exporters.export(result, r'{stl_path}')\n"
        "print('OK')\n"
    )


def export_shape(shape, stl_path: Path, step_path: Path) -> None:
    cq.exporters.export(shape, str(stl_path))
    cq.exporters.export(shape, str(step_path), "STEP")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    gt = trimesh.load(str(GT), force="mesh", process=False)
    # CADFit normalizes GT so max extent = 2, centered.
    ext = np.asarray(gt.extents, float)
    scale = 2.0 / float(np.max(ext))
    local_ext = ext * scale
    rx, ry, rz = (local_ext * 0.5).tolist()
    print(f"source extents={ext} local_radii=({rx:.4f},{ry:.4f},{rz:.4f})")

    trials = []
    for r in [0.70, 0.75, 0.80, 0.82, 0.85, 0.88, 0.90, 0.92, 0.95, 1.00]:
        trials.append(("sphere", {"r": r}))
    # full ellipsoid + slightly shrunk (head is a bit flattened)
    for s in [0.90, 0.95, 1.00, 1.05]:
        trials.append(("ellipsoid", {"rx": rx * s, "ry": ry * s, "rz": rz * s}))
    # sphere using mean / min / volume-equivalent radius
    mean_r = float(np.mean(local_ext) * 0.5)
    min_r = float(np.min(local_ext) * 0.5)
    vol = abs(float(gt.volume)) * (scale ** 3)
    vol_r = (3.0 * vol / (4.0 * np.pi)) ** (1.0 / 3.0)
    for name, r in [("mean", mean_r), ("min", min_r), ("vol", vol_r)]:
        trials.append(("sphere", {"r": r, "tag": name}))

    rows = []
    best = None
    for i, (kind, params) in enumerate(trials):
        tag = params.get("tag", "")
        stl_path = OUT / f"cand_{i:02d}_{kind}{('_'+tag) if tag else ''}.stl"
        py_path = OUT / f"cand_{i:02d}_{kind}{('_'+tag) if tag else ''}.py"
        try:
            if kind == "sphere":
                r = float(params["r"])
                shape = cq.Workplane("XY").sphere(r)
                write_sphere_script(py_path, r, stl_path)
            else:
                shape = (
                    cq.Workplane("XZ")
                    .moveTo(0, -params["rz"])
                    .ellipseArc(params["rx"], params["rz"], -90, 90)
                    .close()
                    .revolve(360, (0, 0, 0), (0, 1, 0))
                )
                write_ellipse_revolve_script(py_path, params["rx"], params["ry"], params["rz"], stl_path)
            cq.exporters.export(shape, str(stl_path))
            iou = float(compute_iou(str(GT), str(stl_path), normalize=True, verbose=False))
        except Exception as exc:
            iou = 0.0
            print(f"FAIL {kind} {params}: {exc}")
        row = {"i": i, "kind": kind, "params": params, "iou": iou, "stl": str(stl_path), "py": str(py_path)}
        rows.append(row)
        print(f"[{i:02d}] {kind:10} {params}  IoU={iou:.4f}")
        if best is None or iou > best["iou"]:
            best = row

    dump_json(OUT / "trial_ious.json", {"best": best, "current_extrude_iou": 0.3314613744936094, "trials": rows})
    print("BEST", json.dumps({k: best[k] for k in best if k != "params"}, indent=2), best["params"])

    if best is None or best["iou"] < 0.20:
        print("No usable sphere/ellipsoid candidate")
        return 1

    # Install into PART_005, backing up the extrusion result once.
    if RAW.is_dir() and not BACKUP.is_dir():
        shutil.copytree(RAW, BACKUP)
        print(f"BACKED UP {RAW} -> {BACKUP}")

    RAW.mkdir(parents=True, exist_ok=True)
    STEP_DIR.mkdir(parents=True, exist_ok=True)

    best_py = Path(best["py"])
    best_stl = Path(best["stl"])
    installed_py = RAW / "best_greedy_parallel_iterative.py"
    installed_stl = RAW / "best_greedy_parallel_iterative.stl"
    installed_step = RAW / "best_greedy_parallel_iterative.step"
    step_copy = STEP_DIR / "PART_005.step"
    recon_stl = STEP_DIR / "PART_005_reconstructed.stl"

    # Re-export STEP from the winning script's shape.
    if best["kind"] == "sphere":
        shape = cq.Workplane("XY").sphere(float(best["params"]["r"]))
        installed_py.write_text(
            "import cadquery as cq\nimport math\n\n"
            f"result = cq.Workplane('XY').sphere({float(best['params']['r']):.8f})\n"
        )
    else:
        p = best["params"]
        shape = (
            cq.Workplane("XZ")
            .moveTo(0, -p["rz"])
            .ellipseArc(p["rx"], p["rz"], -90, 90)
            .close()
            .revolve(360, (0, 0, 0), (0, 1, 0))
        )
        installed_py.write_text(
            "import cadquery as cq\nimport math\n\n"
            f"rx, ry, rz = {p['rx']:.8f}, {p['ry']:.8f}, {p['rz']:.8f}\n"
            "result = (\n"
            "    cq.Workplane('XZ')\n"
            "    .moveTo(0, -rz)\n"
            "    .ellipseArc(rx, rz, -90, 90)\n"
            "    .close()\n"
            "    .revolve(360, (0, 0, 0), (0, 1, 0))\n"
            ")\n"
        )

    export_shape(shape, installed_stl, installed_step)
    shutil.copy2(installed_step, step_copy)
    shutil.copy2(installed_stl, recon_stl)
    dump_json(
        RAW / "final_iou.json",
        {
            "final_iou": best["iou"],
            "stl_id": "PART_005",
            "ground_truth": str(GT),
            "reconstruction": str(installed_stl),
            "num_iterations": 0,
            "duration": 0.0,
            "method": "sphere_or_ellipsoid_refit",
            "kind": best["kind"],
            "params": best["params"],
            "replaced_extrude_iou": 0.3314613744936094,
        },
    )
    print(f"INSTALLED {best['kind']} IoU={best['iou']:.4f} -> {installed_stl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
