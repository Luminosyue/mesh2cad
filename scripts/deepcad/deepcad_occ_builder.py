"""Build DeepCAD solids via OCP (CadQuery stack) when DSL execution fails."""

from __future__ import annotations

import os
from copy import copy
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-deepcad")

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.GC import GC_MakeArcOfCircle
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.gp import gp_Ax2, gp_Ax3, gp_Circ, gp_Dir, gp_Pln, gp_Pnt, gp_Vec

from cadlib.curves import Arc, Circle, CurveBase, Line
from cadlib.extrude import CADSequence, CoordSystem, Extrude
from cadlib.macro import EXTRUDE_OPERATIONS, EXTENT_TYPE
from cadlib.sketch import Loop, Profile


def _write_step(shape, step_path: Path) -> None:
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    status = writer.Write(str(step_path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP write failed: status={status}")


def _write_stl(shape, stl_path: Path) -> None:
    import cadquery as cq

    step_path = stl_path.with_suffix(".step")
    _write_step(shape, step_path)
    solid = cq.importers.importStep(str(step_path))
    cq.exporters.export(solid, str(stl_path))


def point_local2global(point, sketch_plane: CoordSystem, to_gp_Pnt=True):
    g_point = point[0] * sketch_plane.x_axis + point[1] * sketch_plane.y_axis + sketch_plane.origin
    if to_gp_Pnt:
        return gp_Pnt(float(g_point[0]), float(g_point[1]), float(g_point[2]))
    return g_point


def create_edge_3d(curve: CurveBase, sketch_plane: CoordSystem):
    if isinstance(curve, Line):
        if __import__("numpy").allclose(curve.start_point, curve.end_point):
            return -1
        start_point = point_local2global(curve.start_point, sketch_plane)
        end_point = point_local2global(curve.end_point, sketch_plane)
        topo_edge = BRepBuilderAPI_MakeEdge(start_point, end_point)
    elif isinstance(curve, Circle):
        center = point_local2global(curve.center, sketch_plane)
        axis = gp_Dir(*sketch_plane.normal)
        gp_circle = gp_Circ(gp_Ax2(center, axis), abs(float(curve.radius)))
        topo_edge = BRepBuilderAPI_MakeEdge(gp_circle)
    elif isinstance(curve, Arc):
        start_point = point_local2global(curve.start_point, sketch_plane)
        mid_point = point_local2global(curve.mid_point, sketch_plane)
        end_point = point_local2global(curve.end_point, sketch_plane)
        arc = GC_MakeArcOfCircle(start_point, mid_point, end_point).Value()
        topo_edge = BRepBuilderAPI_MakeEdge(arc)
    else:
        raise NotImplementedError(type(curve))
    return topo_edge.Edge()


def create_loop_3d(loop: Loop, sketch_plane: CoordSystem):
    topo_wire = BRepBuilderAPI_MakeWire()
    for curve in loop.children:
        topo_edge = create_edge_3d(curve, sketch_plane)
        if topo_edge == -1:
            continue
        topo_wire.Add(topo_edge)
    return topo_wire.Wire()


def create_profile_face(profile: Profile, sketch_plane: CoordSystem):
    origin = gp_Pnt(*sketch_plane.origin)
    normal = gp_Dir(*sketch_plane.normal)
    x_axis = gp_Dir(*sketch_plane.x_axis)
    gp_face = gp_Pln(gp_Ax3(origin, normal, x_axis))

    all_loops = [create_loop_3d(loop, sketch_plane) for loop in profile.children]
    topo_face = BRepBuilderAPI_MakeFace(gp_face, all_loops[0])
    for loop in all_loops[1:]:
        topo_face.Add(loop.Reversed())
    return topo_face.Face()


def create_by_extrude(extrude_op: Extrude):
    profile = copy(extrude_op.profile)
    profile.denormalize(extrude_op.sketch_size)

    sketch_plane = copy(extrude_op.sketch_plane)
    sketch_plane.origin = extrude_op.sketch_pos

    face = create_profile_face(profile, sketch_plane)
    normal = gp_Dir(*extrude_op.sketch_plane.normal)
    ext_vec = gp_Vec(normal).Multiplied(float(extrude_op.extent_one))
    body = BRepPrimAPI_MakePrism(face, ext_vec).Shape()
    if extrude_op.extent_type == EXTENT_TYPE.index("SymmetricFeatureExtentType"):
        body_sym = BRepPrimAPI_MakePrism(face, ext_vec.Reversed()).Shape()
        body = BRepAlgoAPI_Fuse(body, body_sym).Shape()
    if extrude_op.extent_type == EXTENT_TYPE.index("TwoSidesFeatureExtentType"):
        ext_vec = gp_Vec(normal.Reversed()).Multiplied(float(extrude_op.extent_two))
        body_two = BRepPrimAPI_MakePrism(face, ext_vec).Shape()
        body = BRepAlgoAPI_Fuse(body, body_two).Shape()
    return body


def create_cad_from_sequence(cad_seq: CADSequence):
    body = create_by_extrude(cad_seq.seq[0])
    for extrude_op in cad_seq.seq[1:]:
        new_body = create_by_extrude(extrude_op)
        if extrude_op.operation in {
            EXTRUDE_OPERATIONS.index("NewBodyFeatureOperation"),
            EXTRUDE_OPERATIONS.index("JoinFeatureOperation"),
        }:
            body = BRepAlgoAPI_Fuse(body, new_body).Shape()
        elif extrude_op.operation == EXTRUDE_OPERATIONS.index("CutFeatureOperation"):
            body = BRepAlgoAPI_Cut(body, new_body).Shape()
        elif extrude_op.operation == EXTRUDE_OPERATIONS.index("IntersectFeatureOperation"):
            body = BRepAlgoAPI_Common(body, new_body).Shape()
    return body


def export_deepcad_json(source_json: Path, step_path: Path, stl_path: Path | None = None) -> dict:
    import json

    data = json.loads(source_json.read_text(encoding="utf-8"))
    cad = CADSequence.from_dict(data)
    cad.normalize()
    shape = create_cad_from_sequence(cad)
    step_path.parent.mkdir(parents=True, exist_ok=True)
    _write_step(shape, step_path)
    out = {"step": str(step_path), "ok": True, "fallback": "deepcad_ocp"}
    if stl_path is not None:
        _write_stl(shape, stl_path)
        out["stl"] = str(stl_path)
    return out
