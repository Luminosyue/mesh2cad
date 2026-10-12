#!/usr/bin/env python3
"""Compound kept per-case STEP parts into assembly STEP + STL."""
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"

import csv
import gc
import json
import time
from collections import defaultdict
from pathlib import Path

import trimesh
from OCP.BRep import BRep_Builder
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/p3_parts_cad_results")
OUT = ROOT / "assembly"


def part_key(source: str) -> int:
    stem = Path(source).stem  # part_000
    return int(stem.split("_")[1])


def load_mesh(path: Path):
    m = trimesh.load(path, force="mesh", process=False)
    if isinstance(m, trimesh.Scene):
        geoms = [g for g in m.geometry.values() if isinstance(g, trimesh.Trimesh)]
        m = trimesh.util.concatenate(geoms)
    return m


def assemble_case(case: str, rows: list[dict]) -> dict:
    dest = OUT / case
    dest.mkdir(parents=True, exist_ok=True)
    step_path = dest / f"{case}_cad_assembly.step"
    stl_path = dest / f"{case}_cad_assembly.stl"
    man_path = dest / "assembly_manifest.json"
    rec = {
        "case": case,
        "n_kept_parts": len(rows),
        "step": str(step_path),
        "stl": str(stl_path),
        "status": "ok",
        "error": None,
    }
    if step_path.exists() and stl_path.exists() and step_path.stat().st_size > 0:
        rec["status"] = "skipped_exists"
        rec["step_bytes"] = step_path.stat().st_size
        rec["stl_bytes"] = stl_path.stat().st_size
        return rec

    t0 = time.time()
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    meshes = []
    part_info = []
    for row in sorted(rows, key=lambda r: part_key(r["source"])):
        folder = ROOT / row["output"]
        step = folder / "model.step"
        stl = folder / "cad_rebuilt.stl"
        if not step.exists():
            raise FileNotFoundError(str(step))
        reader = STEPControl_Reader()
        status = reader.ReadFile(str(step))
        if int(status) != int(IFSelect_RetDone):
            raise RuntimeError(f"STEP read failed {step} status={status}")
        reader.TransferRoots()
        builder.Add(compound, reader.OneShape())
        if stl.exists():
            mesh = load_mesh(stl)
            meshes.append(mesh)
            n_faces = int(len(mesh.faces))
        else:
            n_faces = None
        part_info.append({"part": Path(row["source"]).stem, "step": str(step), "faces": n_faces})

    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    writer.Write(str(step_path))
    if meshes:
        assy = trimesh.util.concatenate(meshes)
        assy.export(str(stl_path))
        rec["stl_faces"] = int(len(assy.faces))
        rec["stl_bytes"] = stl_path.stat().st_size
    rec["step_bytes"] = step_path.stat().st_size
    rec["elapsed_sec"] = round(time.time() - t0, 2)
    rec["parts"] = part_info
    man_path.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def main():
    rows = list(csv.DictReader((ROOT / "all_manifest.csv").open()))
    kept = defaultdict(list)
    rejected = []
    for row in rows:
        case = row["source"].split("/")[0]
        if row["status"] == "kept":
            kept[case].append(row)
        else:
            rejected.append({"case": case, "source": row["source"], "reason": row.get("reason")})

    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    cases = sorted(kept)
    print(f"cases={len(cases)} kept_parts={sum(len(v) for v in kept.values())} rejected={len(rejected)}", flush=True)
    for i, case in enumerate(cases, 1):
        try:
            rec = assemble_case(case, kept[case])
        except Exception as e:
            rec = {"case": case, "n_kept_parts": len(kept[case]), "status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"FAIL {case}: {e}", flush=True)
        results.append({k: rec[k] for k in rec if k != "parts"})
        print(
            f"[{i}/{len(cases)}] {case} parts={rec.get('n_kept_parts')} "
            f"status={rec.get('status')} step_mb={round((rec.get('step_bytes') or 0)/1e6,1)} "
            f"dt={rec.get('elapsed_sec')}",
            flush=True,
        )
        gc.collect()

    summary = {
        "n_cases": len(cases),
        "n_ok": sum(1 for r in results if r["status"] in ("ok", "skipped_exists")),
        "n_error": sum(1 for r in results if r["status"] == "error"),
        "n_kept_parts": sum(len(v) for v in kept.values()),
        "rejected_parts": rejected,
        "cases": results,
    }
    (OUT / "assembly_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k != "cases"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
