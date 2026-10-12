#!/usr/bin/env python3
"""Visualize existing V10 CASE09 accepted STEP candidates only."""
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
CASE = ROOT / "v10_geometry_gated_builder_contract_closure/cases/CASE09"
OUT = ROOT / "v10_geometry_gated_builder_contract_closure/artifacts/CASE09_visual"
SOURCE_AUDIT = ROOT / "case09_aircraft_end2end_cad_v1/00_source/source_audit.json"
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


def selected_step(part: dict) -> tuple[Path, dict]:
    part_dir = CASE / part["part_id"]
    family = part["selected"]
    candidates = []
    for record in sorted(part_dir.glob("plan_*.json")):
        payload = json.loads(record.read_text())
        step = Path(payload.get("step") or "")
        if (
            payload.get("family") == family
            and payload.get("executed") is True
            and payload.get("rejected_stage") is None
            and payload.get("explosion", {}).get("GEOMETRY_EXPLOSION_STATUS") != "REJECT"
            and step.is_file()
        ):
            candidates.append((step, payload))
    alt = part_dir / "geometry_alternative.json"
    if alt.is_file():
        payload = json.loads(alt.read_text())
        step = Path(payload.get("step") or "")
        if payload.get("family") == family and payload.get("rejected_stage") is None and step.is_file():
            candidates.append((step, payload))
    if not candidates:
        raise RuntimeError(f"selected STEP missing: {part['part_id']} {family}")
    return candidates[0]


def main():
    V = load_helper()
    OUT.mkdir(parents=True, exist_ok=True)
    summary = json.loads((CASE / "case_summary.json").read_text())
    audit = json.loads(SOURCE_AUDIT.read_text())
    source_path = Path(audit.get("SOURCE_OBJ") or audit.get("frozen_obj"))
    source = trimesh.load(str(source_path), force="mesh", process=False)
    bounds = np.asarray(source.bounds).T
    diag = float(np.linalg.norm(source.extents))

    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    meshes, edges_all, selected = [], [], []
    colors = [
        (75, 136, 169), (108, 165, 132), (192, 139, 78), (147, 119, 178),
        (91, 154, 182), (174, 106, 106), (106, 136, 94), (188, 160, 86),
    ]
    for part in summary["parts"]:
        step, payload = selected_step(part)
        shape = read_shape(step)
        builder.Add(compound, shape)
        vertices, faces, _ = V.tessellate(shape, deflection=0.003, angle=0.18)
        meshes.append(trimesh.Trimesh(vertices=vertices, faces=faces, process=False))
        edges, _ = V.true_edges(shape, diag)
        edges_all.extend(edges)
        selected.append({
            "part_id": part["part_id"],
            "builder": part["selected"],
            "step": str(step),
            "explosion_status": payload.get("explosion", {}).get("GEOMETRY_EXPLOSION_STATUS"),
            "triangles": int(len(faces)),
        })

    assembly_step = OUT / "CASE09_v10_selected_compound.step"
    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    writer.Write(str(assembly_step))

    source_png = OUT / "CASE09_source.png"
    shaded_png = OUT / "CASE09_v10_shaded.png"
    edge_png = OUT / "CASE09_v10_true_edges.png"
    compare_png = OUT / "CASE09_source_vs_v10.png"
    review_png = OUT / "CASE09_v10_review_sheet.png"
    V.render([source], bounds, source_png, colors=[(200, 202, 205)])
    V.render(meshes, bounds, shaded_png, colors=colors)
    V.render(meshes, bounds, edge_png, colors=[(151, 184, 201)] * len(meshes), edges=edges_all)
    V.compose([source_png, shaded_png], ["CASE09 source aircraft", "V10 selected CAD (8 parts)"], compare_png)
    V.compose([source_png, shaded_png, edge_png], ["Source", "V10 shaded", "V10 true edges"], review_png)
    manifest = {
        "case_id": "CASE09",
        "source": str(source_path),
        "assembly_step": str(assembly_step),
        "source_png": str(source_png),
        "shaded_png": str(shaded_png),
        "true_edges_png": str(edge_png),
        "comparison_png": str(compare_png),
        "review_png": str(review_png),
        "part_count": len(selected),
        "selected": selected,
        "note": "Visualization-only compound of existing V10 accepted STEP candidates; no recovery rerun.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
