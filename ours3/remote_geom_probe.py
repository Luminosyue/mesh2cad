#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "ours3"))

import remote_extended_cad_metrics as ext
import remote_geometric_effectiveness_bench_v1 as bench

print("OCP_IMPORT_OK")
print("COMMON", __import__("OCP.BRepAlgoAPI", fromlist=["BRepAlgoAPI_Common"]).BRepAlgoAPI_Common)
print("FUSE", __import__("OCP.BRepAlgoAPI", fromlist=["BRepAlgoAPI_Fuse"]).BRepAlgoAPI_Fuse)
print("GPROP", __import__("OCP.BRepGProp", fromlist=["BRepGProp"]).BRepGProp)
print("BT", __import__("OCP.BRep", fromlist=["BRep_Tool"]).BRep_Tool)
print("BRepMesh", __import__("OCP.BRepMesh", fromlist=["BRepMesh_IncrementalMesh"]).BRepMesh_IncrementalMesh)

gt = ROOT / "cad_spatial_dataset/DeepCAD/train/0002_00024054/model.step"
pr = ROOT / "ours3/p1_exact9998_val1000_eval_v2/deepcad__0002_00024054/pred.step"

gt_shape = ext.read_shape(gt)
pr_shape = ext.read_shape(pr)
print("GT_TOPO", ext.topology_features(gt_shape))
print("PR_TOPO", ext.topology_features(pr_shape))

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location

BRepMesh_IncrementalMesh(gt_shape, 1e-3, False, 0.5, True)
ex = TopExp_Explorer(gt_shape, TopAbs_FACE)
if ex.More():
    face = TopoDS.Face_s(ex.Current())
    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face, loc)
    print("TRI_TYPE", type(tri), repr(tri))
    print("TRI_DIR", [x for x in dir(tri) if "Node" in x or "Tri" in x or "Null" in x][:30])

for name, op in [("common", BRepAlgoAPI_Common(gt_shape, pr_shape)), ("fuse", BRepAlgoAPI_Fuse(gt_shape, pr_shape))]:
    op.Build()
    print(name, "done", op.IsDone(), "null", op.Shape().IsNull())
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(op.Shape(), props)
    print(name, "vol", props.Mass())

gt_points = bench.tessellated_surface_points(gt_shape, 32, 0)
pr_points = bench.tessellated_surface_points(pr_shape, 32, 1)
print("GT_POINTS", gt_points.shape, gt_points[:2].tolist())
print("PR_POINTS", pr_points.shape, pr_points[:2].tolist())
print("CD", bench.standardized_cd(gt_points, pr_points, 1.0))
