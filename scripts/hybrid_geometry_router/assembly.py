from __future__ import annotations

from pathlib import Path

import numpy as np

from .io_utils import load_mesh


def centroid_translation(source, recon) -> list[list[float]]:
    delta = np.asarray(source.centroid, float) - np.asarray(recon.centroid, float)
    return [
        [1.0, 0.0, 0.0, float(delta[0])],
        [0.0, 1.0, 0.0, float(delta[1])],
        [0.0, 0.0, 1.0, float(delta[2])],
        [0.0, 0.0, 0.0, 1.0],
    ]


def load_step_shape(path: Path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone or not reader.TransferRoots():
        raise RuntimeError(f"STEP_READ_FAILED:{path}")
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError(f"STEP_NULL_SHAPE:{path}")
    return shape


def transform_shape(shape, matrix: list[list[float]]):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Trsf

    trsf = gp_Trsf()
    trsf.SetValues(*[float(matrix[r][c]) for r in range(3) for c in range(4)])
    out = BRepBuilderAPI_Transform(shape, trsf, True)
    return out.Shape()


def write_compound_step(shapes: list, out_path: Path) -> bool:
    from OCP.BRep import BRep_Builder
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
    from OCP.TopoDS import TopoDS_Compound

    out_path.parent.mkdir(parents=True, exist_ok=True)
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for shape in shapes:
        builder.Add(compound, shape)
    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    if writer.Write(str(out_path)) != IFSelect_RetDone:
        return False
    reader = STEPControl_Reader()
    return reader.ReadFile(str(out_path)) == IFSelect_RetDone and reader.TransferRoots()


def cadfit_world_shape(step_path: Path, src_mesh_path: Path, recon_stl_path: Path):
    src = load_mesh(src_mesh_path)
    recon = load_mesh(recon_stl_path)
    matrix = centroid_translation(src, recon)
    return transform_shape(load_step_shape(step_path), matrix), matrix


def cadfit_world_mesh(recon_stl_path: Path, matrix: list[list[float]]):
    mesh = load_mesh(recon_stl_path)
    mesh.apply_transform(np.asarray(matrix, float))
    return mesh
