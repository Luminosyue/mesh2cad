from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from scipy.spatial import cKDTree


def reload_shape(path: Path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP_RELOAD_FAILED:{path}")
    reader.TransferRoots()
    shape = reader.OneShape()
    if shape is None or shape.IsNull():
        raise RuntimeError(f"STEP_RELOAD_NULL:{path}")
    return shape


def signature(shape) -> dict[str, Any]:
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    counts = {}
    for name, kind in (
        ("solid_count", TopAbs_SOLID),
        ("shell_count", TopAbs_SHELL),
        ("face_count", TopAbs_FACE),
        ("edge_count", TopAbs_EDGE),
        ("vertex_count", TopAbs_VERTEX),
    ):
        exp = TopExp_Explorer(shape, kind); n = 0
        while exp.More(): n += 1; exp.Next()
        counts[name] = n
    surfaces = {}
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        try:
            name = str(BRepAdaptor_Surface(face).GetType())
        except Exception:
            name = "OTHER"
        surfaces[name] = surfaces.get(name, 0) + 1
        exp.Next()
    bbox = None
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    box = Bnd_Box(); BRepBndLib.Add_s(shape, box)
    bbox = list(box.Get())
    diag = float(np.linalg.norm(np.asarray(bbox[3:]) - np.asarray(bbox[:3])))
    return {
        **counts,
        "shape_type": str(shape.ShapeType()),
        "surface_types": surfaces,
        "bbox": bbox,
        "bbox_diag": diag,
        "brep_valid": bool(BRepCheck_Analyzer(shape).IsValid()),
    }


def topology_metrics(shape, source_diag: float) -> dict[str, Any]:
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCP.TopExp import TopExp, TopExp_Explorer
    from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape
    from OCP.TopoDS import TopoDS

    face_map = TopTools_IndexedMapOfShape()
    edge_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_FACE, face_map)
    TopExp.MapShapes_s(shape, TopAbs_EDGE, edge_map)

    areas = []
    triangle_like_faces = 0
    bspline_control_points = 0
    pcurve_count = 0
    trimmed_face_count = 0
    for index in range(1, face_map.Size() + 1):
        face = TopoDS.Face_s(face_map.FindKey(index))
        props = GProp_GProps()
        try:
            BRepGProp.SurfaceProperties_s(face, props)
            areas.append(float(props.Mass()))
        except Exception:
            areas.append(0.0)
        edge_count = 0
        explorer = TopExp_Explorer(face, TopAbs_EDGE)
        while explorer.More():
            edge = TopoDS.Edge_s(explorer.Current())
            edge_count += 1
            try:
                if BRep_Tool.CurveOnSurface_s(edge, face, 0.0, 0.0) is not None:
                    pcurve_count += 1
            except Exception:
                try:
                    if BRep_Tool.CurveOnSurface_s(edge, face) is not None:
                        pcurve_count += 1
                except Exception:
                    pass
            explorer.Next()
        if edge_count:
            trimmed_face_count += 1
        if edge_count == 3:
            triangle_like_faces += 1
        try:
            surface = BRepAdaptor_Surface(face)
            if "BSplineSurface" in str(surface.GetType()):
                bspline = surface.BSpline()
                bspline_control_points += int(bspline.NbUPoles() * bspline.NbVPoles())
        except Exception:
            pass

    lengths = []
    for index in range(1, edge_map.Size() + 1):
        props = GProp_GProps()
        try:
            BRepGProp.LinearProperties_s(TopoDS.Edge_s(edge_map.FindKey(index)), props)
            lengths.append(float(props.Mass()))
        except Exception:
            lengths.append(0.0)

    edge_faces = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, edge_faces)
    shared_edges = sum(edge_faces.FindFromIndex(i).Extent() > 1 for i in range(1, edge_faces.Extent() + 1))
    total_area = sum(areas)
    tiny_area_limit = max(total_area * 1e-5, 1e-12)
    short_edge_limit = max(source_diag * 1e-4, 1e-12)
    tiny_faces = sum(area <= tiny_area_limit for area in areas)
    short_edges = sum(length <= short_edge_limit for length in lengths)
    face_count = max(len(areas), 1)
    edge_count = max(len(lengths), 1)
    return {
        "unique_face_count": len(areas),
        "unique_edge_count": len(lengths),
        "tiny_face_count": tiny_faces,
        "tiny_face_ratio": tiny_faces / face_count,
        "short_edge_count": short_edges,
        "short_edge_ratio": short_edges / edge_count,
        "triangle_like_face_count": triangle_like_faces,
        "triangle_like_face_ratio": triangle_like_faces / face_count,
        "bspline_control_point_count": bspline_control_points,
        "shared_edge_count": int(shared_edges),
        "pcurve_count": int(pcurve_count),
        "trimmed_face_count": int(trimmed_face_count),
        "design_edge_ratio": 1.0 - short_edges / edge_count,
    }


def _points(shape):
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS
    BRepMesh_IncrementalMesh(shape, 0.003, False, 0.35, True).Perform()
    points=[]; exp=TopExp_Explorer(shape,TopAbs_FACE)
    while exp.More():
        face=TopoDS.Face_s(exp.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(face,loc)
        if tri is not None:
            trsf=loc.Transformation(); points.extend([[p.X(),p.Y(),p.Z()] for p in (tri.Node(i).Transformed(trsf) for i in range(1,tri.NbNodes()+1))])
        exp.Next()
    return np.asarray(points,float)


def fidelity(source: trimesh.Trimesh, shape) -> dict[str, float]:
    cad=_points(shape); src,_=trimesh.sample.sample_surface(source,min(4000,max(500,len(source.faces))),seed=7)
    if len(cad)==0: return {"silhouette_iou":0.0,"chamfer":math.inf,"hausdorff":math.inf}
    da=cKDTree(cad).query(src)[0]; db=cKDTree(src).query(cad)[0]
    lo,hi=source.bounds; scale=np.maximum(hi-lo,1e-9)
    def raster(points,a,b):
        xy=((points[:,[a,b]]-lo[[a,b]])/scale[[a,b]]*255).astype(int).clip(0,255); out=np.zeros((256,256),bool); out[xy[:,1],xy[:,0]]=True; return out
    ious=[]
    for a,b in ((0,1),(0,2),(1,2)):
        x,y=raster(src,a,b),raster(cad,a,b); ious.append(float((x&y).sum()/max((x|y).sum(),1)))
    return {"silhouette_iou":float(np.mean(ious)),"chamfer":float((da.mean()+db.mean())/2),"hausdorff":float(max(da.max(),db.max()))}


def verify(source: trimesh.Trimesh, shape, part_bbox: dict[str, Any], max_faces: int = 5000, max_edges: int = 20000) -> dict[str, Any]:
    sig=signature(shape); metrics=fidelity(source,shape)
    source_diag=float(np.linalg.norm(source.extents)); ratio=sig["bbox_diag"]/max(source_diag,1e-12)
    topo=topology_metrics(shape,source_diag)
    explosion=ratio>4.0 or sig["face_count"]>max_faces or sig["edge_count"]>max_edges or not sig["brep_valid"]
    surfaces=sig["surface_types"]
    bspline_count=sum(v for k,v in surfaces.items() if "BSplineSurface" in k or "BezierSurface" in k)
    analytic_count=sum(v for k,v in surfaces.items() if any(name in k for name in ("Plane", "Cylinder", "Cone", "Sphere", "Torus", "SurfaceOfRevolution")))
    if sig["face_count"]<=12 and bspline_count==0 and analytic_count==sig["face_count"]: classification="V6_NATIVE_COMPACT_CAD"
    elif sig["face_count"]<=80 and bspline_count>0: classification="V6_FREEFORM_COMPACT_BREP"
    elif sig["face_count"]>1000: classification="V6_MESH_WRAPPED_BREP"
    elif sig["face_count"]>80 or sig["edge_count"]>500: classification="V6_HIGH_FIDELITY_FRAGMENTED_BREP"
    else: classification="V6_FREEFORM_COMPACT_BREP" if bspline_count else "V6_NATIVE_COMPACT_CAD"
    surface_groups=len(surfaces)
    fragmentation_score=max(0.0,(sig["face_count"]-12)/max(sig["face_count"],1))
    return {
        **sig,
        **metrics,
        **topo,
        "bbox_ratio":ratio,
        "geometry_explosion":bool(explosion),
        "nativeness_status":"PASS" if not explosion else "FAIL",
        "structural_class":classification,
        "surface_group_count":surface_groups,
        "bspline_face_count":bspline_count,
        "analytic_face_count":analytic_count,
        "fragmentation_score":fragmentation_score,
        "patch_fragmentation":fragmentation_score,
        "face_edge_complexity":sig["face_count"]+sig["edge_count"],
    }
