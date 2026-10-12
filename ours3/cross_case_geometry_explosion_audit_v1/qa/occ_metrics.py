"""OCC topology metrics used by geometry explosion guards."""
from __future__ import annotations

from typing import Any

import numpy as np

from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.GeomAbs import GeomAbs_BSplineSurface, GeomAbs_BezierSurface
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS


def _bbox_tuple(box: Bnd_Box) -> tuple[list[float], list[float]]:
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return [float(xmin), float(ymin), float(zmin)], [float(xmax), float(ymax), float(zmax)]


def bbox_of_shape(shape) -> dict[str, Any]:
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, True)
    if box.IsVoid():
        return {
            "bbox_min": [0.0, 0.0, 0.0],
            "bbox_max": [0.0, 0.0, 0.0],
            "bbox_diag": 0.0,
            "centroid": [0.0, 0.0, 0.0],
            "volume": 0.0,
            "void": True,
        }
    lo, hi = _bbox_tuple(box)
    extents = np.asarray(hi, float) - np.asarray(lo, float)
    return {
        "bbox_min": lo,
        "bbox_max": hi,
        "bbox_diag": float(np.linalg.norm(extents)),
        "centroid": ((np.asarray(lo) + np.asarray(hi)) * 0.5).tolist(),
        "volume": float(abs(np.prod(np.maximum(extents, 0.0)))),
        "void": False,
    }


def read_step(path):
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        return None
    reader.TransferRoots()
    shape = reader.OneShape()
    if shape is None or shape.IsNull():
        return None
    return shape


def _explore(shape, kind):
    explorer = TopExp_Explorer(shape, kind)
    while explorer.More():
        yield explorer.Current()
        explorer.Next()


def _vertex_xyz(vertex) -> np.ndarray:
    pnt = BRep_Tool.Pnt_s(TopoDS.Vertex_s(vertex))
    return np.asarray([pnt.X(), pnt.Y(), pnt.Z()], float)


def measure_shape(shape, max_edges: int = 8000, max_faces: int = 4000) -> dict[str, Any]:
    bbox = bbox_of_shape(shape)
    edge_lengths = []
    edge_bboxes = []
    for i, raw in enumerate(_explore(shape, TopAbs_EDGE)):
        if i >= max_edges:
            break
        edge = TopoDS.Edge_s(raw)
        props = GProp_GProps()
        BRepGProp.LinearProperties_s(edge, props)
        length = float(props.Mass())
        edge_lengths.append(length)
        box = Bnd_Box()
        BRepBndLib.Add_s(edge, box, True)
        if not box.IsVoid():
            lo, hi = _bbox_tuple(box)
            edge_bboxes.append((lo, hi, length))
        else:
            edge_bboxes.append((bbox["bbox_min"], bbox["bbox_max"], length))

    face_diags = []
    face_aspects = []
    face_areas = []
    face_bboxes = []
    control_points = []
    control_steps = []
    pcurve_domain_errors = 0
    for i, raw in enumerate(_explore(shape, TopAbs_FACE)):
        if i >= max_faces:
            break
        face = TopoDS.Face_s(raw)
        box = Bnd_Box()
        BRepBndLib.Add_s(face, box, True)
        if box.IsVoid():
            continue
        lo, hi = _bbox_tuple(box)
        extents = np.maximum(np.asarray(hi, float) - np.asarray(lo, float), 1e-12)
        diag = float(np.linalg.norm(extents))
        aspect = float(extents.max() / extents.min())
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        area = float(abs(props.Mass()))
        face_diags.append(diag)
        face_aspects.append(aspect)
        face_areas.append(area)
        face_bboxes.append((lo, hi, diag, aspect, area))
        try:
            adaptor = BRepAdaptor_Surface(face)
            kind = adaptor.GetType()
            if kind in (GeomAbs_BSplineSurface, GeomAbs_BezierSurface):
                surf = adaptor.BSpline() if kind == GeomAbs_BSplineSurface else adaptor.Bezier()
                nu, nv = surf.NbUPoles(), surf.NbVPoles()
                poles = []
                for u in range(1, nu + 1):
                    row = []
                    for v in range(1, nv + 1):
                        p = surf.Pole(u, v)
                        xyz = np.asarray([p.X(), p.Y(), p.Z()], float)
                        poles.append(xyz)
                        row.append(xyz)
                    if len(row) >= 2:
                        control_steps.extend(np.linalg.norm(np.diff(np.asarray(row), axis=0), axis=1).tolist())
                control_points.extend(poles)
                if len(poles) >= 2:
                    grid = np.asarray(poles).reshape(nu, nv, 3)
                    control_steps.extend(np.linalg.norm(np.diff(grid, axis=0), axis=2).ravel().tolist())
            umin, umax, vmin, vmax = adaptor.FirstUParameter(), adaptor.LastUParameter(), adaptor.FirstVParameter(), adaptor.LastVParameter()
            if not np.isfinite([umin, umax, vmin, vmax]).all() or abs(umax - umin) > 1e6 or abs(vmax - vmin) > 1e6:
                pcurve_domain_errors += 1
        except Exception:
            pass

    vertices = []
    for i, raw in enumerate(_explore(shape, TopAbs_VERTEX)):
        if i >= 20000:
            break
        vertices.append(_vertex_xyz(raw))

    edge_arr = np.asarray(edge_lengths, float) if edge_lengths else np.asarray([0.0])
    face_arr = np.asarray(face_diags, float) if face_diags else np.asarray([0.0])
    aspect_arr = np.asarray(face_aspects, float) if face_aspects else np.asarray([1.0])
    area_arr = np.asarray(face_areas, float) if face_areas else np.asarray([0.0])
    cp = np.asarray(control_points, float) if control_points else np.zeros((0, 3))
    steps = np.asarray(control_steps, float) if control_steps else np.asarray([0.0])
    cp_bbox = None
    if len(cp):
        cp_lo = cp.min(axis=0).tolist()
        cp_hi = cp.max(axis=0).tolist()
        cp_bbox = {
            "bbox_min": cp_lo,
            "bbox_max": cp_hi,
            "bbox_diag": float(np.linalg.norm(np.asarray(cp_hi) - np.asarray(cp_lo))),
        }

    return {
        **bbox,
        "edge_count": int(len(edge_lengths)),
        "face_count": int(len(face_diags)),
        "vertex_count": int(len(vertices)),
        "max_edge_length": float(edge_arr.max()),
        "p95_edge_length": float(np.percentile(edge_arr, 95)),
        "min_edge_length": float(edge_arr.min()),
        "edge_lengths": edge_arr.tolist(),
        "edge_bboxes": edge_bboxes,
        "max_face_bbox_diag": float(face_arr.max()),
        "p95_face_bbox_diag": float(np.percentile(face_arr, 95)),
        "face_aspects": aspect_arr.tolist(),
        "face_areas": area_arr.tolist(),
        "face_bboxes": face_bboxes,
        "vertices": [v.tolist() for v in vertices],
        "control_point_count": int(len(cp)),
        "control_point_bbox": cp_bbox,
        "control_net_step_p95": float(np.percentile(steps, 95)) if len(steps) else 0.0,
        "control_net_step_max": float(steps.max()) if len(steps) else 0.0,
        "control_points": cp.tolist()[:4000],
        "pcurve_domain_error_count": int(pcurve_domain_errors),
        "entity_count": int(len(edge_lengths) + len(face_diags) + len(vertices)),
    }
