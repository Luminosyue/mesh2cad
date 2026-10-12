#!/usr/bin/env python3
"""Audit generated and canonical STEP solids without changing geometry."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GeomAbs import (
    GeomAbs_BezierSurface,
    GeomAbs_BSplineSurface,
    GeomAbs_Cone,
    GeomAbs_Cylinder,
    GeomAbs_OffsetSurface,
    GeomAbs_OtherSurface,
    GeomAbs_Plane,
    GeomAbs_Sphere,
    GeomAbs_SurfaceOfExtrusion,
    GeomAbs_SurfaceOfRevolution,
    GeomAbs_Torus,
)
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
FROZEN = ROOT / "airplane3_fullseq_14bit_ir_v1/frozen_success_v1/step"
CANON = ROOT / "airplane3_fullseq_14bit_ir_v1/dataset/DeepCAD/geometry_pack_v1"
PARTS = ["PART_000", "PART_001", "PART_005"]
SURF = {
    GeomAbs_Plane: "Plane",
    GeomAbs_Cylinder: "Cylinder",
    GeomAbs_Cone: "Cone",
    GeomAbs_Sphere: "Sphere",
    GeomAbs_Torus: "Torus",
    GeomAbs_BSplineSurface: "BSplineSurface",
    GeomAbs_BezierSurface: "BezierSurface",
    GeomAbs_SurfaceOfRevolution: "SurfaceOfRevolution",
    GeomAbs_SurfaceOfExtrusion: "SurfaceOfExtrusion",
    GeomAbs_OffsetSurface: "OffsetSurface",
    GeomAbs_OtherSurface: "Other",
}
ORDER = [
    "Plane",
    "Cylinder",
    "Cone",
    "Sphere",
    "Torus",
    "BSplineSurface",
    "BezierSurface",
    "SurfaceOfRevolution",
    "SurfaceOfExtrusion",
    "OffsetSurface",
    "Other",
]


def read_step(path: Path):
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {path} status={status}")
    reader.TransferRoots()
    return reader.OneShape()


def count_shapes(shape, kind) -> int:
    exp = TopExp_Explorer(shape, kind)
    n = 0
    while exp.More():
        n += 1
        exp.Next()
    return n


def face_edge_count(face) -> int:
    exp = TopExp_Explorer(face, TopAbs_EDGE)
    n = 0
    while exp.More():
        n += 1
        exp.Next()
    return n


def diagonal(shape) -> float:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    x0, y0, z0, x1, y1, z1 = box.Get()
    return max(((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2) ** 0.5, 1e-9)


def display_triangles(shape, linear: float, angular: float) -> int:
    BRepMesh_IncrementalMesh(shape, linear, False, angular, True)
    total = 0
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        loc = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(face, loc)
        if poly is not None:
            total += int(poly.NbTriangles())
        exp.Next()
    return total


def audit(path: Path) -> dict:
    shape = read_step(path)
    valid = bool(BRepCheck_Analyzer(shape).IsValid())
    types = Counter()
    plane_triangles = 0
    face_edge_hist = Counter()
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        kind = SURF.get(BRepAdaptor_Surface(face).GetType(), "Other")
        types[kind] += 1
        ne = face_edge_count(face)
        face_edge_hist[ne] += 1
        if kind == "Plane" and ne == 3:
            plane_triangles += 1
        exp.Next()
    faces = count_shapes(shape, TopAbs_FACE)
    diag = diagonal(shape)
    linear = max(diag * 0.0012, 1e-4)
    angular = 0.12
    tris = display_triangles(shape, linear, angular)
    curved = sum(types[k] for k in ORDER if k != "Plane")
    return {
        "path": str(path),
        "brep_valid": valid,
        "solid_count": count_shapes(shape, TopAbs_SOLID),
        "shell_count": count_shapes(shape, TopAbs_SHELL),
        "BREP_FACE_N": faces,
        "edge_count": count_shapes(shape, TopAbs_EDGE),
        "surface_types": {k: int(types.get(k, 0)) for k in ORDER},
        "plane_triangular_face_n": plane_triangles,
        "curved_face_n": curved,
        "face_edge_count_histogram": {str(k): int(v) for k, v in sorted(face_edge_hist.items())},
        "DISPLAY_TESSELLATION_TRIANGLE_N": tris,
        "tessellation_linear_deflection": linear,
        "tessellation_angular_deflection_rad": angular,
        "diagonal": diag,
    }


def gate(row: dict) -> str:
    faces = row["BREP_FACE_N"]
    tris = row["DISPLAY_TESSELLATION_TRIANGLE_N"]
    plane_tri = row["plane_triangular_face_n"]
    curved = row["curved_face_n"]
    bspline = row["surface_types"]["BSplineSurface"] + row["surface_types"]["BezierSurface"]
    if faces > 0 and plane_tri >= 200 and plane_tri / faces >= 0.8:
        return "FACETED_BREP"
    if faces > 0 and tris >= 8 * faces and (bspline > 0 or curved > 0):
        return "TRIANGLES_ARE_RENDER_TESSELLATION"
    if faces > 0 and plane_tri / faces < 0.5 and tris > faces:
        return "TRIANGLES_ARE_RENDER_TESSELLATION"
    return "REVIEW"


def main() -> None:
    rows = []
    for part in PARTS:
        for role, path in (
            ("generated", FROZEN / f"{part}.step"),
            ("canonical", CANON / f"airplane__{part}" / "target.step"),
        ):
            print(f"auditing {part} {role}", flush=True)
            row = audit(path)
            row["part"] = part
            row["role"] = role
            row["gate"] = gate(row)
            rows.append(row)
            print(
                part,
                role,
                "faces",
                row["BREP_FACE_N"],
                "tris",
                row["DISPLAY_TESSELLATION_TRIANGLE_N"],
                "bspline",
                row["surface_types"]["BSplineSurface"],
                "plane_tri",
                row["plane_triangular_face_n"],
                row["gate"],
                flush=True,
            )
    out = ROOT / "paper_teaser_demo_v2/reports/audit_rows.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
