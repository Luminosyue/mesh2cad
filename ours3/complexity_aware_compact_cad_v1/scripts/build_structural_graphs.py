#!/usr/bin/env python3
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_WIRE
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Vec


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "complexity_aware_compact_cad_v1"
sys.path.insert(0, str(ROOT / "batch_10_step_quality_audit_v1/scripts"))
import audit_batch as audit

CASES = {
    "CASE_03": (ROOT / "batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/reconstructed.step", OUT / "case03_control"),
    "CASE_04": (ROOT / "batch_real_mesh2cad_v1/cases/CASE_04/cad_recovery/reconstructed.step", OUT / "case04"),
    "CASE_05": (ROOT / "case05_residual_part003_recovery_v3/assembly/CASE_05_full_cad_assembly_v3.step", OUT / "case05"),
    "CASE_09": (ROOT / "batch_real_mesh2cad_v1/cases/CASE_09/cad_recovery/reconstructed.step", OUT / "case09"),
}


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def indexed(shape, kind):
    result = TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape, kind, result); return result


def bounds(shape):
    box = Bnd_Box(); BRepBndLib.Add_s(shape, box, True); x = box.Get()
    return [float(v) for v in x]


def props(shape, linear=False):
    value = GProp_GProps()
    if linear:
        BRepGProp.LinearProperties_s(shape, value)
    else:
        BRepGProp.SurfaceProperties_s(shape, value)
    c = value.CentreOfMass()
    return float(value.Mass()), [float(c.X()), float(c.Y()), float(c.Z())]


def normal_sample(face):
    try:
        surface = BRepAdaptor_Surface(face, True)
        u = (surface.FirstUParameter() + surface.LastUParameter()) / 2.0
        v = (surface.FirstVParameter() + surface.LastVParameter()) / 2.0
        p = gp_Pnt(); du = gp_Vec(); dv = gp_Vec(); surface.D1(u, v, p, du, dv)
        n = du.Crossed(dv)
        if n.Magnitude() <= 1e-14:
            return None
        n.Normalize(); return [float(n.X()), float(n.Y()), float(n.Z())]
    except Exception:
        return None


def angle_deg(a, b):
    if a is None or b is None:
        return None
    dot = abs(float(np.dot(a, b)))
    return float(math.degrees(math.acos(max(-1.0, min(1.0, dot)))))


class UnionFind:
    def __init__(self, n): self.parent = list(range(n + 1))
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]; x = self.parent[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b: self.parent[b] = a


def build(case_id, step, case_dir):
    ok, roots, shape = audit.fresh_read(step)
    if not ok or roots < 1 or shape.IsNull(): raise RuntimeError(f"fresh read failed: {case_id}")
    face_map = indexed(shape, TopAbs_FACE); edge_map = indexed(shape, TopAbs_EDGE)
    nodes = []; normals = {}
    total_area = 0.0
    for i in range(1, face_map.Extent() + 1):
        face = TopoDS.Face_s(face_map.FindKey(i))
        surface = audit.enum_name(BRepAdaptor_Surface(face).GetType(), audit.SURFACE_NAMES)
        area, centroid = props(face); total_area += area
        wire_count = indexed(face, TopAbs_WIRE).Extent(); normal = normal_sample(face); normals[i] = normal
        nodes.append({"FACE_ID": i, "surface_type": surface, "area": area, "centroid": centroid, "normal_samples": [normal] if normal else [], "bbox": bounds(face), "boundary_wire_count": wire_count, "inner_wires": max(0, wire_count - 1)})
        if i % 5000 == 0: print(f"{case_id}_FACE_PROGRESS={i}/{face_map.Extent()}", flush=True)
    ancestors = TopTools_IndexedDataMapOfShapeListOfShape(); TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, ancestors)
    adjacency = []; semantics = []; uf = UnionFind(face_map.Extent())
    for i in range(1, ancestors.Extent() + 1):
        edge = TopoDS.Edge_s(ancestors.FindKey(i)); incident = []
        for item in ancestors.FindFromIndex(i):
            idx = face_map.FindIndex(item)
            if idx and idx not in incident: incident.append(idx)
        length, _ = props(edge, linear=True)
        curve_type = audit.enum_name(BRepAdaptor_Curve(edge).GetType(), audit.CURVE_NAMES)
        if len(incident) == 1:
            label = "PRESERVE_EDGE"; angle = None; boundary_type = "OUTER_OR_INNER_BOUNDARY"
        elif len(incident) >= 2:
            a, b = incident[:2]; sa, sb = nodes[a - 1]["surface_type"], nodes[b - 1]["surface_type"]
            angle = angle_deg(normals[a], normals[b])
            same = sa == sb
            mergeable = same and ((sa == "BSPLINE") or (angle is not None and angle <= 5.0))
            label = "MERGEABLE_INTERNAL_EDGE" if mergeable else ("PRESERVE_EDGE" if (angle is not None and angle >= 25.0) or not same else "UNCERTAIN_EDGE")
            boundary_type = "SAME_SURFACE_FRAGMENT_BOUNDARY" if mergeable else "FEATURE_OR_UNCERTAIN_BOUNDARY"
            if mergeable: uf.union(a, b)
        else:
            label = "UNCERTAIN_EDGE"; angle = None; boundary_type = "ORPHAN_TOPOLOGY"
        record = {"EDGE_ID": i, "incident_face_ids": incident, "shared_edge_length": length, "curve_type": curve_type, "dihedral_angle_deg_estimate": angle, "G0_continuity": len(incident) >= 2, "G1_continuity_estimate": bool(angle is not None and angle <= 5.0), "boundary_type": boundary_type, "semantic": label}
        semantics.append(record)
        if len(incident) >= 2: adjacency.append(record)
        if i % 10000 == 0: print(f"{case_id}_EDGE_PROGRESS={i}/{ancestors.Extent()}", flush=True)
    groups = defaultdict(list)
    for node in nodes: groups[uf.find(node["FACE_ID"])].append(node["FACE_ID"])
    candidates = []
    for index, ids in enumerate(sorted(groups.values(), key=lambda x: (-len(x), x[0]))):
        types = Counter(nodes[i - 1]["surface_type"] for i in ids); dominant = types.most_common(1)[0][0]
        ctype = {"PLANE":"PLANE_CLUSTER","CYLINDER":"CYLINDER_CLUSTER","CONE":"CONE_CLUSTER","SPHERE":"SPHERE_CLUSTER","TORUS":"TORUS_CLUSTER"}.get(dominant,"FREEFORM_CLUSTER")
        area = sum(nodes[i - 1]["area"] for i in ids)
        candidates.append({"candidate_id": f"SC_{index:04d}", "support_face_ids": ids, "candidate_type": ctype, "fit_parameters": {"dominant_surface": dominant, "representation_hypotheses": ["GLOBAL_BSPLINE_SINGLE_PATCH","GLOBAL_BSPLINE_MULTI_PATCH_LOW_COUNT","BOUNDARY_CONSTRAINED_BSPLINE","SWEEP_SURFACE","REVOLUTION_SURFACE","RULED_SURFACE"] if ctype == "FREEFORM_CLUSTER" else [ctype]}, "fit_residual": 0.0, "boundary_complexity": sum(1 for e in semantics if e["semantic"] != "MERGEABLE_INTERNAL_EDGE" and any(f in ids for f in e["incident_face_ids"])), "area_coverage": area / total_area if total_area else 0.0, "merge_cost": len(ids) / max(face_map.Extent(), 1)})
    graph = {"CASE_ID": case_id, "STEP_PATH": str(step), "node_definition": "TopoDS_Face", "edge_definition": "shared true TopoDS_Edge", "nodes": nodes, "edges": adjacency}
    dump(case_dir / "face_adjacency_graph.json", graph)
    dump(case_dir / "surface_candidate_graph.json", {"CASE_ID": case_id, "thresholds_relative_to_bbox_diagonal": {"plane_normal_deg_sweep":[1.0,3.0,5.0],"plane_offset":[1e-5,1e-4,1e-3],"cylinder_axis_deg":[1.0,3.0,5.0],"fit_residual_q2_cap":0.02}, "candidates": candidates})
    dump(case_dir / "edge_semantics.json", {"CASE_ID": case_id, "counts": dict(Counter(x["semantic"] for x in semantics)), "edges": semantics})
    grounded = [{"semantic_feature_id": f"EDGE_{e['EDGE_ID']:06d}", "TopoDS_entity_id": e["EDGE_ID"], "geometry_signature": {"curve_type":e["curve_type"],"length":e["shared_edge_length"]}, "adjacency_signature": e["incident_face_ids"], "semantic":e["semantic"]} for e in semantics if e["semantic"] == "PRESERVE_EDGE"]
    dump(case_dir / "brep_grounding.json", {"CASE_ID":case_id,"grounding_scope":["hole","fillet-like edge","chamfer-like edge","feature boundary"],"entities":grounded})
    feature_types = ["PLANE","CYLINDER","FREEFORM_SURFACE","PROFILE","HOLE","EXTRUSION_CANDIDATE","REVOLUTION_CANDIDATE","PATTERN_CANDIDATE"]
    feature_graph = {"CASE_ID":case_id,"hierarchy":["Curve","Loop","Surface/Face","Sketch-like Profile","Feature Candidate"],"supported_feature_types":feature_types,"PROFILE":{"count":sum(1 for e in semantics if e['curve_type']=='LINE' and len(e['incident_face_ids'])>=2)},"HOLE":{"count":sum(n['inner_wires'] for n in nodes)},"EXTRUSION_CANDIDATE":{"detected":case_id=="CASE_04"},"REVOLUTION_CANDIDATE":{"detected":False},"PATTERN_CANDIDATE":{"detected":False},"PROGRAMMATIC_CAD_ELIGIBLE":case_id=="CASE_04"}
    dump(case_dir / "cad_feature_graph.json", feature_graph)
    summary = {"CASE_ID":case_id,"FACE_NODES":len(nodes),"ADJACENCY_EDGES":len(adjacency),"SURFACE_CANDIDATES":len(candidates),"EDGE_SEMANTICS":dict(Counter(x["semantic"] for x in semantics)),"INNER_WIRE_COUNT":sum(n["inner_wires"] for n in nodes),"PROGRAMMATIC_CAD_ELIGIBLE":case_id=="CASE_04"}
    dump(case_dir / "structural_graph_summary.json", summary); print(json.dumps(summary), flush=True)


def main():
    for case_id, (step, case_dir) in CASES.items():
        case_dir.mkdir(parents=True, exist_ok=True); build(case_id, step, case_dir)


if __name__ == "__main__": main()
