#!/usr/bin/env python3
"""Render the already-built V10 CASE_YC4XCA selected candidates.

This script performs no fitting or recovery. It only reads accepted STEP
artifacts, creates a compound for visualization, and renders it.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from OCP.BRep import BRep_Builder
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
CASE = ROOT / "v10_geometry_gated_builder_contract_closure/cases/CASE_YC4XCA"
OUT = ROOT / "v10_geometry_gated_builder_contract_closure/artifacts/CASE_YC4XCA_visual"
SOURCE = ROOT / "meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
HELPER = ROOT / "case09_aircraft_end2end_cad_v1/scripts/end2end_pipeline.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("render_helper", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_shape(path: Path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"cannot read {path}")
    reader.TransferRoots()
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError(f"null shape {path}")
    return shape


def selected_step(part: dict) -> Path:
    part_dir = CASE / part["part_id"]
    family = part["selected"]
    for plan_path in sorted(part_dir.glob("plan_*.json")):
        payload = json.loads(plan_path.read_text())
        step = Path(payload.get("step") or "")
        if (
            payload.get("family") == family
            and payload.get("executed") is True
            and payload.get("rejected_stage") is None
            and payload.get("explosion", {}).get("GEOMETRY_EXPLOSION_STATUS") != "REJECT"
            and step.is_file()
        ):
            return step
    alt = part_dir / "geometry_alternative.json"
    if alt.is_file():
        payload = json.loads(alt.read_text())
        step = Path(payload.get("step") or "")
        if payload.get("family") == family and step.is_file():
            return step
    raise RuntimeError(f"selected STEP missing: {part['part_id']} {family}")


def main():
    V = load_helper()
    OUT.mkdir(parents=True, exist_ok=True)
    summary = json.loads((CASE / "case_summary.json").read_text())
    source = trimesh.load(str(SOURCE), force="mesh", process=False)
    bounds = np.asarray(source.bounds).T
    diag = float(np.linalg.norm(source.extents))

    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    meshes = []
    all_edges = []
    selected = []
    palette = [
        (76, 132, 164), (103, 161, 127), (192, 137, 76), (145, 118, 176),
        (92, 151, 179), (171, 105, 105), (104, 132, 92), (186, 158, 84),
        (99, 119, 153), (153, 119, 89), (122, 146, 162), (159, 124, 145),
        (92, 139, 126),
    ]
    for part in summary["parts"]:
        step = selected_step(part)
        shape = read_shape(step)
        builder.Add(compound, shape)
        vertices, faces, _ = V.tessellate(shape, deflection=0.003, angle=0.18)
        meshes.append(trimesh.Trimesh(vertices=vertices, faces=faces, process=False))
        edges, _ = V.true_edges(shape, diag)
        all_edges.extend(edges)
        selected.append({
            "part_id": part["part_id"],
            "builder": part["selected"],
            "step": str(step),
            "triangles": int(len(faces)),
        })

    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    assembly_step = OUT / "CASE_YC4XCA_v10_selected_compound.step"
    writer.Write(str(assembly_step))

    source_png = OUT / "CASE_YC4XCA_source.png"
    shaded_png = OUT / "CASE_YC4XCA_v10_shaded.png"
    edges_png = OUT / "CASE_YC4XCA_v10_true_edges.png"
    comparison_png = OUT / "CASE_YC4XCA_source_vs_v10.png"
    review_png = OUT / "CASE_YC4XCA_v10_review_sheet.png"
    V.render([source], bounds, source_png, colors=[(200, 202, 205)])
    V.render(meshes, bounds, shaded_png, colors=palette[: len(meshes)])
    V.render(meshes, bounds, edges_png, colors=[(151, 184, 201)] * len(meshes), edges=all_edges)
    V.compose([source_png, shaded_png], ["CASE_YC4XCA source tank", "V10 selected CAD (13 parts)"], comparison_png)
    V.compose([source_png, shaded_png, edges_png], ["Source", "V10 shaded", "V10 true edges"], review_png)
    manifest = {
        "case_id": "CASE_YC4XCA",
        "source": str(SOURCE),
        "assembly_step": str(assembly_step),
        "source_png": str(source_png),
        "shaded_png": str(shaded_png),
        "true_edges_png": str(edges_png),
        "comparison_png": str(comparison_png),
        "review_png": str(review_png),
        "part_count": len(selected),
        "selected": selected,
        "note": "Visualization-only compound of existing V10 accepted STEP candidates; no fitting or recovery rerun.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
