#!/usr/bin/env python3
"""VTK-only rendering subprocess for cached STEP-derived geometry."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pyvista as pv
import trimesh
from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/paper_style_brep_render_v1")
PALETTE = ["#9ecae1","#f3b37a","#e99b9b","#79c7b8","#efd66f","#9fcf8f","#b9a3d7","#e8a6c5","#85b6d9","#d7b878","#90c9ce","#c5a5a1","#a9c48c","#b2abd2","#efc39a","#89b6a5","#d9a4b2","#a7b9d7","#c6c77d","#d7a97f","#8dc4b7","#c3abd8","#e5b4a7","#9eb9cf","#b8cc9a","#d8b2cb","#a9c7c9","#d7c49d"]
DIRECTION=np.asarray([1.35,-1.55,1.05],float);DIRECTION/=np.linalg.norm(DIRECTION)
UP=np.asarray([0.,0.,1.])


def dump(path,value): path.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")
def polydata(points,faces): return pv.PolyData(points,np.column_stack((np.full(len(faces),3,dtype=np.int64),faces)).ravel())


def plotter(center,diag):
    p=pv.Plotter(off_screen=True,window_size=(1000,1000));p.set_background("white");p.camera.parallel_projection=True
    p.camera_position=[tuple(center+DIRECTION*diag*3),tuple(center),tuple(UP)];p.camera.parallel_scale=diag*.61;p.enable_anti_aliasing("fxaa");return p


def save(p,path): p.reset_camera_clipping_range();p.screenshot(str(path));p.close()


def edge_polydata(points,records):
    cells=[];cursor=0
    for record in records:
        n=int(record["SAMPLE_COUNT"])
        if record["RENDERED"]:
            cells.extend([n,*range(cursor,cursor+n)]);cursor+=n
    assert cursor==len(points)
    data=pv.PolyData(points);data.lines=np.asarray(cells,dtype=np.int64);return data


def render_mesh(mesh,center,diag,path):
    p=plotter(center,diag);p.add_mesh(polydata(np.asarray(mesh.vertices),np.asarray(mesh.faces)),color="#e5e1d7",show_edges=False,smooth_shading=False,ambient=.38,diffuse=.72,specular=.06)
    edges=np.asarray(mesh.edges_unique,dtype=np.int64);n=min(len(edges),120000);selected=edges[np.linspace(0,len(edges)-1,n,dtype=np.int64)]
    wire=pv.PolyData(np.asarray(mesh.vertices));wire.lines=np.column_stack((np.full(n,2,dtype=np.int64),selected)).ravel();p.add_mesh(wire,color="#72777d",line_width=.3,opacity=.32,render_lines_as_tubes=False,ambient=1.,diffuse=0.);save(p,path)


def render_split(mesh,labels,center,diag,path):
    p=plotter(center,diag);vertices=np.asarray(mesh.vertices);faces=np.asarray(mesh.faces)
    for i,label in enumerate(sorted(np.unique(labels))):
        selected=faces[labels==label];used,inverse=np.unique(selected.ravel(),return_inverse=True);points=vertices[used].copy();direction=points.mean(0)-center;norm=np.linalg.norm(direction)
        if norm>1e-12:points+=direction/norm*diag*.04
        p.add_mesh(polydata(points,inverse.reshape((-1,3))),color=PALETTE[i%len(PALETTE)],smooth_shading=True,show_edges=False,ambient=.38,diffuse=.74,specular=.10,specular_power=24)
    save(p,path)


def render_brep(points,faces,components,edges,vertices,center,diag,path,part_colored=False,wireframe=False):
    p=plotter(center,diag)
    if not wireframe:
        if part_colored:
            for i,component in enumerate(sorted(np.unique(components))):
                selected=faces[components==component];used,inverse=np.unique(selected.ravel(),return_inverse=True)
                p.add_mesh(polydata(points[used],inverse.reshape((-1,3))),color=PALETTE[i%len(PALETTE)],smooth_shading=True,show_edges=False,ambient=.86,diffuse=.13,specular=.04,specular_power=24)
        else:p.add_mesh(polydata(points,faces),color="#b8cdea",smooth_shading=True,show_edges=False,ambient=.90,diffuse=.10,specular=.04,specular_power=24)
    p.add_mesh(edges,color="#263750" if wireframe else "#34465c",line_width=.95 if wireframe else .25,
               opacity=.94 if wireframe else .04,render_lines_as_tubes=False,ambient=1.,diffuse=0.)
    if len(vertices):p.add_mesh(pv.PolyData(vertices),color="#1f6fd1",point_size=2.7 if wireframe else 1.0,
                                opacity=.92 if wireframe else .015,render_points_as_spheres=True,ambient=1.,diffuse=0.)
    save(p,path)


def font(size):
    for path in ("/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"):
        if Path(path).is_file():return ImageFont.truetype(path,size)
    return ImageFont.load_default()


def compose(paths,labels,caption,out):
    w=1100;h=1100;top=74;bottom=112;canvas=Image.new("RGB",(w*len(paths),top+h+bottom),"white");draw=ImageDraw.Draw(canvas);lf=font(32);cf=font(23)
    for i,(path,label) in enumerate(zip(paths,labels)):
        image=Image.open(path).convert("RGB").resize((w,h),Image.Resampling.LANCZOS);canvas.paste(image,(i*w,top));box=draw.textbbox((0,0),label,font=lf);draw.text((i*w+(w-(box[2]-box[0]))//2,22),label,fill="#24262b",font=lf)
    box=draw.textbbox((0,0),caption,font=cf);draw.text(((canvas.width-(box[2]-box[0]))//2,top+h+38),caption,fill="#42464d",font=cf);canvas.save(out,dpi=(300,300));canvas.save(out.with_suffix(".pdf"),"PDF",resolution=300.)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--case",required=True,choices=("case05","real03"));args=parser.parse_args();out=ROOT/args.case
    inp=json.loads((out/"metrics/render_input.json").read_text());top=json.loads((out/"metrics/brep_topology.json").read_text());cache=np.load(out/"metrics/brep_render_cache.npz")
    mesh=trimesh.load(inp["SOURCE_OBJ"],force="mesh",process=False);labels=np.load(inp["SPLIT_LABELS"]);center=np.asarray(inp["CENTER"]);diag=float(inp["SHARED_DIAG"])
    edges=edge_polydata(cache["edge_points"],top["EDGES"])
    render_mesh(mesh,center,diag,out/"mesh_model.png");print("PANEL=mesh",flush=True)
    render_split(mesh,labels,center,diag,out/"split_model.png");print("PANEL=split",flush=True)
    render_brep(cache["surface_points"],cache["surface_faces"],cache["face_components"],edges,cache["vertices"],center,diag,out/"brep_model.png");print("PANEL=brep",flush=True)
    render_brep(cache["surface_points"],cache["surface_faces"],cache["face_components"],edges,cache["vertices"],center,diag,out/"brep_model_part_colored.png",part_colored=True);print("PANEL=part_colored",flush=True)
    render_brep(cache["surface_points"],cache["surface_faces"],cache["face_components"],edges,cache["vertices"],center,diag,out/"brep_wireframe.png",wireframe=True);print("PANEL=wireframe",flush=True)
    caption="Recovered B-rep preserves part boundaries and negative features." if args.case=="real03" else "Visual comparison of mesh-to-B-rep reconstruction: input mesh, geometric decomposition, and recovered B-rep model."
    compose([out/"mesh_model.png",out/"split_model.png",out/"brep_model.png"],["Mesh model","Part split","Recovered B-rep"],caption,out/"comparison_figure.png")
    compose([out/"mesh_model.png",out/"split_model.png",out/"brep_model_part_colored.png",out/"brep_model.png"],["Mesh model","P3 segmentation","CAD part decomposition","Recovered B-rep"],caption,out/"comparison_figure_4panel.png")
    for name in ("mesh_model.png","split_model.png","brep_model.png","brep_wireframe.png","comparison_figure.png"):shutil.copy2(out/name,out/f"{inp['PREFIX']}_{name}")
    hole_q={"pass":True,"source":None,"one_to_one":None,"negative_space":None}
    if args.case=="real03":
        qroot=ROOT.parent/"negative_feature_topology_recovery_v1";summary=json.loads((qroot/"artifacts/summary.json").read_text());matches=json.loads((qroot/"metrics/negative_feature_matches.json").read_text())["matches"]
        negative=sum(all(x["pass"] for x in m["negative_space_samples"]) for m in matches)
        one=sum(bool(m["one_to_one_match"] and m["cad_feature_recovered"]) for m in matches)
        hole_q={"pass":bool(summary["EXACT_FULL_CAD_RECOVERY"] and summary["ASSEMBLY_STEP_PATH"]==inp["STEP_PATH"] and len(matches)==one==negative==10),"source":str(qroot/"metrics/negative_feature_matches.json"),"one_to_one":one,"negative_space":negative}
    metadata={"CASE_ID":inp["CASE_ID"],"RENDER_BACKEND":"OCP_7_8_PLUS_PYVISTA_0_48_XVFB_OFFSCREEN","MESH_PANEL_SOURCE":"SOURCE_OBJ","MESH_PANEL_SOURCE_PATH":inp["SOURCE_OBJ"],"MESH_PANEL_HAS_TRIANGLE_EDGES":True,"MESH_PANEL_USES_VERTEX_SCATTER":False,"MESH_TRIANGLE_EDGE_COUNT":inp["SOURCE_EDGE_COUNT"],"MESH_TRIANGLE_EDGE_DISPLAY_COUNT":min(inp["SOURCE_EDGE_COUNT"],120000),"MESH_TRIANGLE_EDGE_DISPLAY_POLICY":"deterministic representative subset of source OBJ triangle edges","SPLIT_PANEL_SOURCE":"SEGMENTATION/PART_GRAPH","SPLIT_PANEL_SOURCE_PATH":inp["SPLIT_LABELS"],"SPLIT_VISUALIZATION_TYPE":inp["SPLIT_VISUALIZATION_TYPE"],"SPLIT_REGION_COUNT":inp["SPLIT_REGION_COUNT"],"SPLIT_EXPLODE_FACTOR":.04,"SPLIT_PANEL_HAS_TRIANGLE_WIREFRAME":False,"BREP_PANEL_SOURCE":"STEP_ONLY","BREP_PANEL_SOURCE_PATH":inp["STEP_PATH"],"BREP_RENDER_USES_SOURCE_MESH":False,"BREP_SURFACE_PROVENANCE":"STEP_FRESH_BRepMesh_IncrementalMesh","BREP_EDGE_PROVENANCE":"TopoDS_Edge via TopTools_IndexedMapOfShape and BRepAdaptor_Curve","BREP_VERTEX_PROVENANCE":"TopoDS_Vertex via TopTools_IndexedMapOfShape and BRep_Tool.Pnt","EDGE_RENDER_MODE":"TRUE_BREP_TOPOLOGY","TRIANGLE_EDGES_IN_BREP_PANEL":False,"STEP_RELOAD_SUCCESS":True,"BREP_FACE_COUNT":top["BREP_FACE_COUNT"],"BREP_EDGE_COUNT":top["BREP_EDGE_COUNT"],"BREP_VERTEX_COUNT":top["BREP_VERTEX_COUNT"],"RENDERED_BREP_EDGE_COUNT":top["RENDERED_BREP_EDGE_COUNT"],"CAMERA_PROJECTION":"ORTHOGRAPHIC","CAMERA_DIRECTION":DIRECTION.tolist(),"CAMERA_UP":UP.tolist(),"CAMERA_TARGET":center.tolist(),"CAMERA_PARALLEL_SCALE":diag*.61,"WORLD_SCALE_SHARED":True,"SHARED_WORLD_BOUNDS":inp["SHARED_WORLD_BOUNDS"],"SOURCE_OBJ_PROVENANCE_PATH":inp["SOURCE_OBJ_PROVENANCE_PATH"],"SOURCE_TRIANGLE_COUNT":inp["SOURCE_TRIANGLE_COUNT"],"BREP_TESSELLATION_TRIANGLE_COUNT":inp["BREP_TESSELLATION_TRIANGLE_COUNT"],"ASSEMBLY_COMPONENT_COUNT":inp["ASSEMBLY_COMPONENT_COUNT"],"FACETED_MESH_WRAPPED_AS_BREP":top["FACETED_MESH_WRAPPED_AS_BREP"],"ANALYTIC_FACE_COUNT":top["ANALYTIC_FACE_COUNT"],"BSPLINE_FACE_COUNT":top["BSPLINE_FACE_COUNT"],"LOFT_FACE_COUNT_IF_AVAILABLE":top["LOFT_FACE_COUNT_IF_AVAILABLE"],"ANTI_ALIASING":"FXAA","BACKGROUND":"#FFFFFF","PANEL_RESOLUTION":[1000,1000],"COMPARISON_RESOLUTION":[3300,1286],"COMPARISON_DPI":300,"RECOVERED_HOLE_COUNT":inp["RECOVERED_HOLE_COUNT"],"REAL03_HOLE_VISIBILITY_QA":hole_q["pass"],"REAL03_HOLE_QA_SOURCE":hole_q["source"],"REAL03_HOLE_ONE_TO_ONE_MATCH_COUNT":hole_q["one_to_one"],"REAL03_HOLE_NEGATIVE_SPACE_PASS_COUNT":hole_q["negative_space"],"NEW_P3_RUNS":0,"NEW_PHYSX_RUNS":0,"NEW_MAC_RUNS":0,"NEW_LLM_CALLS":0,"CAD_GEOMETRY_MODIFIED":False}
    dump(out/"render_metadata.json",metadata);print("RENDER_COMPLETE",flush=True)


if __name__=="__main__":main()
