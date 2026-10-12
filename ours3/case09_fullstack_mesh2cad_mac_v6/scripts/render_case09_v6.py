#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import numpy as np
import trimesh
from OCP.BRepCheck import BRepCheck_Analyzer

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'case09_fullstack_mesh2cad_mac_v6'
V6=OUT/'10_assembly/CASE09_fullstack_mesh2cad_mac_v6.step'
V51=ROOT/'case09_nonwing_semantic_recovery_v5_1/12_assembly/CASE09_nonwing_semantic_recovery_v5_1.step'
SOURCE=ROOT/'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
ART=OUT/'artifacts'

spec=importlib.util.spec_from_file_location('v',ROOT/'case09_aircraft_end2end_cad_v1/scripts/end2end_pipeline.py')
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)

def shape(path):
    ok,roots,result=V.read_step(path)
    assert ok and roots and result and not result.IsNull() and BRepCheck_Analyzer(result).IsValid()
    return result

def mesh(result):
    vertices,faces,_=V.tessellate(result,deflection=.004,angle=.2)
    return trimesh.Trimesh(vertices,faces,process=False)

def main():
    ART.mkdir(parents=True,exist_ok=True)
    source=trimesh.load(SOURCE,force='mesh',process=False);bounds=np.asarray(source.bounds).T;diag=float(np.linalg.norm(source.extents))
    v6shape=shape(V6);v51shape=shape(V51);v6mesh=mesh(v6shape);v51mesh=mesh(v51shape)
    v6edges,_=V.true_edges(v6shape,diag);v51edges,_=V.true_edges(v51shape,diag)
    source_shaded=ART/'source_shaded.png';v6_shaded=ART/'v6_final_shaded.png';v6_true=ART/'v6_final_true_edges.png';v51_shaded=ART/'v5_1_reference_shaded_rerendered.png';v51_true=ART/'v5_1_reference_true_edges_rerendered.png'
    V.render([source],bounds,source_shaded,colors=[(205,207,210)])
    V.render([v6mesh],bounds,v6_shaded,colors=[(113,174,205)])
    V.render([v6mesh],bounds,v6_true,colors=[(154,195,215)],edges=v6edges)
    V.render([v51mesh],bounds,v51_shaded,colors=[(205,170,118)])
    V.render([v51mesh],bounds,v51_true,colors=[(215,187,143)],edges=v51edges)
    V.compose([source_shaded,v6_shaded],['Original CASE09 OBJ','V6 final CAD shaded'],ART/'source_vs_v6_final_shaded.png')
    V.compose([v51_shaded,v6_shaded],['V5.1 reference CAD','V6 final CAD'],ART/'v5_1_vs_v6_final_shaded.png')
    V.compose([v51_true,v6_true],['V5.1 reference true BRep edges','V6 final true BRep edges'],ART/'v5_1_vs_v6_final_true_edges.png')
    print(ART/'source_vs_v6_final_shaded.png')
    print(ART/'v5_1_vs_v6_final_shaded.png')
    print(ART/'v5_1_vs_v6_final_true_edges.png')

if __name__=='__main__':main()
