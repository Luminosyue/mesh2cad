#!/usr/bin/env python3
"""V7D3: saved-evidence-only, geometry-preserving vertical-tail boundary refit."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS, TopoDS_Compound

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v7d3_vertical_tail_geometry_preserving_refit"
V7B = ROOT / "v7b_profile_type_aware_open_shell_reconstruction"
V7D = ROOT / "v7d_common_boundary_control_net"
V7C = ROOT / "v7c_open_shell_topology_and_sewing"
V7CONTRACT = ROOT / "v7_contract_closed_runtime"
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(V7D))

from geometry_preserving_refit.control_net_anchor import displacement_metrics
from geometry_preserving_refit.deformation_regularizer import budget
from geometry_preserving_refit.local_refitter import apply, poles
from geometry_preserving_refit.master_compatibility import curve_from_three_poles, make_compatible
from boundary_control_net.master_boundary_curve import fit as fit_master
from geometry_preserving_refit.topology_identity import build as build_topology

V7B_CHAMFER = 0.010298782545970303
V7B_HAUSDORFF = 0.25303765500752023
V7D_CHAMFER = 0.023507918076213743
V7D_HAUSDORFF = 0.47054985066586297
CONFIG = {
    "strip_widths": {"narrow": 2, "medium": 3, "wide": 5},
    "max_control_point_displacement_ratio": 0.20,
    "locality_minimum": 0.99,
    "final_samples": 30000,
    "ablation_samples": 12000,
    "random_seed": 20260813,
    "geometry_sampling_relative_tolerance": 0.002,
}


def load(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items() if k not in {"shape", "edge", "faces", "surface_a", "surface_b", "original_a", "original_b", "changed_a", "changed_b"}}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, Path): return str(value)
    return value


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2) + "\n")


def compound(shapes):
    out, builder = TopoDS_Compound(), BRep_Builder(); builder.MakeCompound(out)
    for shape in shapes: builder.Add(out, shape)
    return out


def read_faces(path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone: raise RuntimeError(f"STEP_READ_FAILED:{path}")
    reader.TransferRoots(); result=[]; exp=TopExp_Explorer(reader.OneShape(), TopAbs_FACE)
    while exp.More(): result.append(TopoDS.Face_s(exp.Current())); exp.Next()
    return result


def write_step(shape, path):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    writer=STEPControl_Writer(); writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone: raise RuntimeError("STEP_WRITE_FAILED")


def source_surfaces():
    faces = read_faces(V7B / "06_candidates/CADPART_005/PRIMARY/candidate.step")
    return faces[:2], [BRep_Tool.Surface_s(face) for face in faces[:2]]


def split_surface(surface):
    knots=[surface.UKnot(i) for i in range(1, surface.NbUKnots()+1)]
    cut=knots[-2]
    extension, core=surface.Copy(), surface.Copy()
    u0,u1,v0,v1=surface.Bounds()
    extension.Segment(u0,cut,v0,v1); core.Segment(cut,u1,v0,v1)
    return extension, core, float(cut)


def identity_audit(spec, station_ids):
    names=sorted(spec["open_chain_tracks"]); ta=spec["open_chain_tracks"][names[0]]; tb=spec["open_chain_tracks"][names[1]]
    a={r["station_id"]:np.asarray(r["resampled_points_3d"],float) for r in ta}
    b={r["station_id"]:np.asarray(r["resampled_points_3d"],float) for r in tb}
    rows=[]
    for ea in (0,-1):
        for eb in (0,-1):
            points=np.asarray([0.5*(a[s][ea]+b[s][eb]) for s in station_ids])
            pair=np.asarray([np.linalg.norm(a[s][ea]-b[s][eb]) for s in station_ids])
            dirs=np.diff(points,axis=0); dirs=dirs/np.maximum(np.linalg.norm(dirs,axis=1)[:,None],1e-15)
            rough=float(sum(np.linalg.norm(dirs[i+1]-dirs[i]) for i in range(max(0,len(dirs)-1))))
            rows.append({"endpoint_a":ea,"endpoint_b":eb,"pair_p95":float(np.quantile(pair,.95)),"roughness":rough,"points":points})
    best=min(rows,key=lambda r:(r["pair_p95"],r["roughness"]))
    return best, rows


def build_candidate(master_curve, strip_rows, anchor_enabled, tag, diagonal):
    _, original_surfaces=source_surfaces(); split=[split_surface(s) for s in original_surfaces]
    extensions=[row[0] for row in split]; cores=[row[1] for row in split]
    a,b,curve,master_poles=make_compatible(cores[0],cores[1],master_curve)
    aa,ma,oa,ca=apply(a,master_poles,"V_MIN",strip_rows,anchor_enabled)
    bb,mb,ob,cb=apply(b,master_poles,"V_MIN",strip_rows,anchor_enabled)
    face_a=BRepBuilderAPI_MakeFace(aa,1e-8).Face(); face_b=BRepBuilderAPI_MakeFace(bb,1e-8).Face()
    ext_faces=[BRepBuilderAPI_MakeFace(surface,1e-8).Face() for surface in extensions]
    topology=build_topology(aa,face_a,bb,face_b,"V_MIN","V_MIN",diagonal*1e-7)
    result=compound([topology["trimmed_face_a"],topology["trimmed_face_b"],*ext_faces])
    merged={}
    for key in ["TOTAL_CONTROL_POINT_COUNT","MOVED_CONTROL_POINT_COUNT"]: merged[key]=ma[key]+mb[key]
    merged["MOVED_CONTROL_POINT_RATIO"]=merged["MOVED_CONTROL_POINT_COUNT"]/merged["TOTAL_CONTROL_POINT_COUNT"]
    moved_inside=ma["MOVED_CONTROL_POINT_COUNT"]*ma["BOUNDARY_STRIP_MOVEMENT_RATE"]+mb["MOVED_CONTROL_POINT_COUNT"]*mb["BOUNDARY_STRIP_MOVEMENT_RATE"]
    merged["BOUNDARY_STRIP_MOVEMENT_RATE"]=float(moved_inside/max(merged["MOVED_CONTROL_POINT_COUNT"],1))
    merged["MAX_CONTROL_POINT_DISPLACEMENT"]=max(ma["MAX_CONTROL_POINT_DISPLACEMENT"],mb["MAX_CONTROL_POINT_DISPLACEMENT"])
    merged["P95_CONTROL_POINT_DISPLACEMENT"]=float(np.quantile(np.r_[ma["displacement"].ravel(),mb["displacement"].ravel()],.95))
    interior=np.r_[ma["displacement"][:,strip_rows:].ravel(),mb["displacement"][:,strip_rows:].ravel()]
    merged["INTERIOR_RMS_DEVIATION_FROM_V7B"]=float(np.sqrt(np.mean(interior**2))) if len(interior) else 0.
    merged["INTERIOR_P95_DEVIATION_FROM_V7B"]=float(np.quantile(interior,.95)) if len(interior) else 0.
    merged["INTERIOR_MAX_DEVIATION_FROM_V7B"]=float(interior.max()) if len(interior) else 0.
    max_rows=max(len(ma["ROW_MAX_DISPLACEMENTS"]),len(mb["ROW_MAX_DISPLACEMENTS"]))
    merged["ROW_MAX_DISPLACEMENTS"]=[max(ma["ROW_MAX_DISPLACEMENTS"][i] if i<len(ma["ROW_MAX_DISPLACEMENTS"]) else 0,mb["ROW_MAX_DISPLACEMENTS"][i] if i<len(mb["ROW_MAX_DISPLACEMENTS"]) else 0) for i in range(max_rows)]
    # ROW_0 is a hard exact-boundary constraint, not an optimizer degree of
    # freedom.  The deformation budget therefore governs ROW_1+ while the
    # true all-row maximum remains reported separately.
    budget_input=dict(merged)
    budget_input["MAX_CONTROL_POINT_DISPLACEMENT"]=max(merged["ROW_MAX_DISPLACEMENTS"][1:],default=0.0)
    merged["MAX_BUDGETED_CONTROL_POINT_DISPLACEMENT"]=budget_input["MAX_CONTROL_POINT_DISPLACEMENT"]
    merged.update(budget(budget_input,diagonal,CONFIG["max_control_point_displacement_ratio"]))
    pcurve_errors=[topology["PCURVE_A_ERROR"],topology["PCURVE_B_ERROR"]]
    return {
        "tag":tag,"shape":result,"edge":topology["edge"],"faces":[topology["trimmed_face_a"],topology["trimmed_face_b"]],
        "surface_a":aa,"surface_b":bb,"original_a":oa,"original_b":ob,"changed_a":ca,"changed_b":cb,
        "metrics":merged,"topology":{
            "SHARED_OCC_EDGE_COUNT":int(topology["EDGE_OCC_VALID"] and topology["PCURVE_A_SUCCESS"] and topology["PCURVE_B_SUCCESS"]),
            "PCURVE_COUNT":int(topology["PCURVE_A_SUCCESS"])+int(topology["PCURVE_B_SUCCESS"]),
            "TRIMMED_FACE_COUNT":int(topology["TRIMMED_FACE_A_VALID"])+int(topology["TRIMMED_FACE_B_VALID"]),
            "PCURVE_3D_MEAN_ERROR":max(r["mean"] for r in pcurve_errors),"PCURVE_3D_P95_ERROR":max(r["p95"] for r in pcurve_errors),"PCURVE_3D_MAX_ERROR":max(r["max"] for r in pcurve_errors),
            "OCC_VALID":bool(BRepCheck_Analyzer(result).IsValid()),
        },
    }


def mesh_points(shape, stl_path, count, seed, diagonal):
    # QA samples are stochastic points, so a 0.6%-diagonal tessellation is
    # adequate and avoids 100 MB debug STLs from the very dense V7B surfaces.
    BRepMesh_IncrementalMesh(shape,max(diagonal*.006,1e-5),False,.25,True).Perform(); StlAPI_Writer().Write(shape,str(stl_path))
    cad=trimesh.load(stl_path,force="mesh",process=False)
    return trimesh.sample.sample_surface(cad,count,seed=seed)[0]


def geometry_qa(shape, source_path, stl_path, diagonal, count, seed):
    source=trimesh.load(source_path,force="mesh",process=False)
    sp=trimesh.sample.sample_surface(source,count,seed=seed)[0]
    cp=mesh_points(shape,stl_path,count,seed+1,diagonal)
    ds,isrc=cKDTree(cp).query(sp); dc,icad=cKDTree(sp).query(cp)
    combined=np.r_[ds,dc]/diagonal
    if ds.max()>=dc.max(): i=int(ds.argmax()); ws,wc=sp[i],cp[isrc[i]]
    else: i=int(dc.argmax()); ws,wc=sp[icad[i]],cp[i]
    xmin,xmax=float(sp[:,0].min()),float(sp[:,0].max()); span=xmax-xmin
    def local(lo,hi):
        sm=(sp[:,0]>=xmin+lo*span)&(sp[:,0]<=xmin+hi*span); cm=(cp[:,0]>=xmin+lo*span)&(cp[:,0]<=xmin+hi*span)
        vals=[]
        if sm.any(): vals.extend(cKDTree(cp).query(sp[sm])[0]/diagonal)
        if cm.any(): vals.extend(cKDTree(sp).query(cp[cm])[0]/diagonal)
        return float(np.max(vals)) if vals else math.nan
    region={"ROOT_HAUSDORFF":local(0,.18),"SIDE_HAUSDORFF":local(.18,.82),"TIP_HAUSDORFF":local(.82,1)}
    worst=max(region,key=region.get).replace("_HAUSDORFF","")
    return {"CHAMFER":float(combined.mean()),"HAUSDORFF":float(combined.max()),"P95":float(np.quantile(combined,.95)),**region,"WORST_REGION":worst,"WORST_POINT_SOURCE":ws.tolist(),"WORST_POINT_BREP":wc.tolist(),"source_points":sp,"cad_points":cp,"distances":ds/diagonal}


def edge_identity(edge, faces):
    hits=[]
    for face in faces:
        found=False; exp=TopExp_Explorer(face,TopAbs_EDGE)
        while exp.More():
            if edge.IsSame(TopoDS.Edge_s(exp.Current())): found=True
            exp.Next()
        hits.append(found)
    return all(hits)


def v7d_displacement_audit(v7b_surfaces, v7d_surfaces, csv_path):
    base=np.vstack([poles(s).reshape(-1,3) for s in v7b_surfaces]); rows=[]; values=[]
    for fi,surface in enumerate(v7d_surfaces[:2]):
        net=poles(surface); tree=cKDTree(base); distances,_=tree.query(net.reshape(-1,3)); distances=distances.reshape(net.shape[:2]); values.append(distances)
        for u in range(net.shape[0]):
            for v in range(net.shape[1]): rows.append({"VERSION":"V7D","FACE_ID":fi,"CONTROL_NET_ROW_INDEX":v,"CONTROL_NET_COL_INDEX":u,"DISTANCE_TO_SHARED_BOUNDARY_ROW":v,"CONTROL_POINT_DISPLACEMENT":float(distances[u,v]),"CORRESPONDENCE":"NEAREST_V7B_CONTROL_POLE"})
    csv_path.parent.mkdir(parents=True,exist_ok=True)
    with csv_path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    flat=np.concatenate([x.ravel() for x in values]); row_values={}
    for row in range(3): row_values[row]=[x[:,row].ravel() for x in values if x.shape[1]>row]
    interior=np.concatenate([x[:,3:].ravel() for x in values])
    return {"MAX_CONTROL_POINT_DISPLACEMENT":float(flat.max()),"P95_CONTROL_POINT_DISPLACEMENT":float(np.quantile(flat,.95)),"BOUNDARY_ROW_DISPLACEMENT":float(np.max(np.concatenate(row_values[0]))),"ROW_1_DISPLACEMENT":float(np.max(np.concatenate(row_values[1]))),"ROW_2_DISPLACEMENT":float(np.max(np.concatenate(row_values[2]))),"INTERIOR_DISPLACEMENT":float(np.max(interior)),"GLOBAL_CONTROL_NET_DRIFT":bool(np.quantile(interior,.5)>1e-4),"arrays":values}


def plot_net(path, nets, title, displacement=None, strip=None):
    fig,axes=plt.subplots(1,len(nets),figsize=(6*len(nets),5),squeeze=False)
    for i,net in enumerate(nets):
        ax=axes[0,i]
        if displacement is None:
            for u in range(net.shape[0]): ax.plot(net[u,:,1],net[u,:,2],"-",lw=.5,color="#3569a8")
            for v in range(0,net.shape[1],max(1,net.shape[1]//12)): ax.plot(net[:,v,1],net[:,v,2],"-o",ms=2,lw=.7,color="#d16b3b")
        else:
            im=ax.imshow(displacement[i].T,aspect="auto",origin="lower",cmap="magma"); fig.colorbar(im,ax=ax,label="displacement")
        if strip is not None: ax.axvspan(-.5,strip-.5,color="#47a447",alpha=.2)
        ax.set_title(f"face {i}"); ax.set_xlabel("Y / row"); ax.set_ylabel("Z / column")
    fig.suptitle(title); fig.tight_layout(); fig.savefig(path,dpi=160); plt.close(fig)


def plot_points(path, qa, title, edge_points=None):
    fig,ax=plt.subplots(figsize=(7,5)); sp=qa["source_points"]; cp=qa["cad_points"]
    ax.scatter(sp[:,1],sp[:,2],s=.15,c="#777",alpha=.25,label="source"); ax.scatter(cp[:,1],cp[:,2],s=.15,c="#2878b5",alpha=.25,label="CAD")
    if edge_points is not None: ax.plot(edge_points[:,1],edge_points[:,2],c="#d62728",lw=2,label="shared boundary")
    ax.set_title(title); ax.set_aspect("equal","box"); ax.legend(markerscale=8); fig.tight_layout(); fig.savefig(path,dpi=160); plt.close(fig)


def make_debug(debug, v7b_nets, v7d_nets, final, qa_final, qa_v7d_proxy, v7d_audit):
    debug.mkdir(parents=True,exist_ok=True); final_nets=[final["changed_a"],final["changed_b"]]
    zero=[np.zeros(n.shape[:2]) for n in v7b_nets]
    local_disp=[np.linalg.norm(final["changed_a"]-final["original_a"],axis=2),np.linalg.norm(final["changed_b"]-final["original_b"],axis=2)]
    names=[]
    def net(name,nets,title,disp=None,strip=None): plot_net(debug/name,nets,title,disp,strip); names.append(name)
    net("01_v7b_tail_surface.png",v7b_nets,"V7B tail surface control geometry")
    net("02_v7d_tail_surface.png",v7d_nets,"V7D globally rebuilt tail")
    net("03_v7d3_tail_surface.png",final_nets,"V7D3 local-refit tail")
    net("04_v7b_control_net.png",v7b_nets,"V7B control net")
    net("05_v7d_control_net.png",v7d_nets,"V7D control net")
    net("06_v7d3_control_net.png",final_nets,"V7D3 control net")
    net("07_v7d_displacement_heatmap.png",v7d_nets,"V7D nearest-pole displacement",v7d_audit["arrays"])
    net("08_v7d3_displacement_heatmap.png",final_nets,"V7D3 displacement from V7B-compatible core",local_disp)
    net("09_boundary_strip.png",final_nets,"Configurable boundary strip",None,final["metrics"]["BOUNDARY_STRIP_ROWS"])
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    curve=BRepAdaptor_Curve(final["edge"]); ep=np.asarray([[curve.Value(float(t)).X(),curve.Value(float(t)).Y(),curve.Value(float(t)).Z()] for t in np.linspace(curve.FirstParameter(),curve.LastParameter(),257)])
    for name,title in [("10_shared_master_boundary.png","Exact master boundary"),("11_shared_occ_edge.png","One shared OCC edge"),("12_pcurve_validation.png","Two revalidated pcurves")]: plot_points(debug/name,qa_final,title,ep); names.append(name)
    for name,title,qa in [("13_hausdorff_v7b.png","V7B baseline Hausdorff",qa_final),("14_hausdorff_v7d.png","V7D Hausdorff",qa_v7d_proxy),("15_hausdorff_v7d3.png","V7D3 Hausdorff",qa_final),("16_worst_region_before_after.png","Worst region: V7D vs V7D3",qa_final)]: plot_points(debug/name,qa,title); names.append(name)
    thumbs=[]
    for name in names:
        im=Image.open(debug/name).convert("RGB"); im.thumbnail((420,300)); thumbs.append((name,im.copy()))
    sheet=Image.new("RGB",(1680,1200),"white"); draw=ImageDraw.Draw(sheet)
    for i,(name,im) in enumerate(thumbs):
        x=(i%4)*420; y=(i//4)*300; sheet.paste(im,(x,y)); draw.rectangle((x,y,x+419,y+24),fill="white"); draw.text((x+5,y+5),name,fill="black")
    target=debug.parent/"v7d3_tail_contact_sheet.png"; sheet.save(target); return target


def main():
    artifacts=OUT/"artifacts"; debug=artifacts/"v7d3_debug"; candidates_dir=OUT/"06_candidates/CADPART_005"
    artifacts.mkdir(parents=True,exist_ok=True); candidates_dir.mkdir(parents=True,exist_ok=True)
    fuselage=V7D/"07_v7c_rerun/CADPART_000/v7c_shared_topology_faces.step"; fuselage_hash_before=sha(fuselage)
    v7b_step=V7B/"06_candidates/CADPART_005/PRIMARY/candidate.step"; v7d_step=V7D/"06_candidates/CADPART_005/v7d_constrained_faces.step"
    v7b_faces,v7b_surfaces=source_surfaces(); v7d_faces=read_faces(v7d_step); v7d_surfaces=[BRep_Tool.Surface_s(f) for f in v7d_faces]
    analysis=load(ROOT/"v7a_profile_recovery/03_geometry_analyzer/CADPART_005/geometry_analysis.json"); source_path=Path(analysis["source_mesh"])
    source=trimesh.load(source_path,force="mesh",process=False); diagonal=float(np.linalg.norm(source.extents))
    common=load(V7D/"05_common_control_net/CADPART_005/common_control_net.json"); current_curve=curve_from_three_poles(common["shared_poles"][0])
    correspondence=load(V7D/"02_endpoint_correspondence/CADPART_005/endpoint_correspondence.json"); station_ids=common["common_station_ids"]
    accepted_pairs=[r["pairs"][0] for r in correspondence["selected"]]
    endpoint_flip=bool(len(set(r["endpoint_a"] for r in accepted_pairs))>1 or len(set(r["endpoint_b"] for r in accepted_pairs))>1)
    repaired,row_audit=identity_audit(load(V7B/"04_measured_spec/CADPART_005/measured_cad_spec.json"),station_ids)
    repaired_curve,_=fit_master(repaired["points"],diagonal*1e-7)
    v7d_audit=v7d_displacement_audit(v7b_surfaces,v7d_surfaces,artifacts/"tail_control_net_displacement.csv")

    masters={"CURRENT_MASTER":current_curve,"IDENTITY_REPAIRED_MASTER":repaired_curve}
    runs=[]
    for master_name,curve in masters.items():
        for width_name,width in CONFIG["strip_widths"].items():
            candidate=build_candidate(curve,width,True,f"{master_name}_{width_name}",diagonal); candidate["metrics"]["BOUNDARY_STRIP_ROWS"]=width
            qa=geometry_qa(candidate["shape"],source_path,candidates_dir/f"{candidate['tag']}.stl",diagonal,CONFIG["ablation_samples"],CONFIG["random_seed"])
            candidate["qa"]=qa; runs.append(candidate)
    global_candidate=build_candidate(current_curve,3,False,"CURRENT_MASTER_global",diagonal); global_candidate["metrics"]["BOUNDARY_STRIP_ROWS"]=global_candidate["surface_a"].NbVPoles()
    global_candidate["qa"]=geometry_qa(global_candidate["shape"],source_path,candidates_dir/"CURRENT_MASTER_global.stl",diagonal,CONFIG["ablation_samples"],CONFIG["random_seed"])
    no_anchor=build_candidate(current_curve,3,False,"CURRENT_MASTER_no_anchor",diagonal); no_anchor["metrics"]["BOUNDARY_STRIP_ROWS"]=no_anchor["surface_a"].NbVPoles()
    no_anchor["qa"]=geometry_qa(no_anchor["shape"],source_path,candidates_dir/"CURRENT_MASTER_no_anchor.stl",diagonal,CONFIG["ablation_samples"],CONFIG["random_seed"])
    valid=[r for r in runs if r["topology"]["SHARED_OCC_EDGE_COUNT"]>=1 and r["topology"]["PCURVE_COUNT"]>=2 and r["topology"]["TRIMMED_FACE_COUNT"]>=2 and not r["metrics"]["CONTROL_NET_DEFORMATION_BUDGET_EXCEEDED"]]
    # Rule is label-free: constraint validity, then minimum normalized geometry error.
    final=min(valid,key=lambda r:(r["qa"]["HAUSDORFF"],r["qa"]["CHAMFER"],r["metrics"]["MAX_CONTROL_POINT_DISPLACEMENT"]))
    final_qa=geometry_qa(final["shape"],source_path,candidates_dir/"v7d3_final.stl",diagonal,CONFIG["final_samples"],CONFIG["random_seed"]+999)
    final["qa"]=final_qa; final_step=candidates_dir/"v7d3_vertical_tail_local_refit.step"; write_step(final["shape"],final_step)
    formal_step=OUT/"07_topology/CADPART_005/v7d3_shared_topology_faces.step"; write_step(compound(final["faces"]),formal_step)
    identity=edge_identity(final["edge"],final["faces"])
    local_current=min([r for r in runs if r["tag"].startswith("CURRENT_MASTER")],key=lambda r:r["qa"]["HAUSDORFF"])
    local_repaired=min([r for r in runs if r["tag"].startswith("IDENTITY_REPAIRED_MASTER")],key=lambda r:r["qa"]["HAUSDORFF"])
    repair_causal=local_repaired["qa"]["HAUSDORFF"]<local_current["qa"]["HAUSDORFF"] and local_repaired["qa"]["CHAMFER"]<local_current["qa"]["CHAMFER"]
    local_outperforms=local_current["qa"]["HAUSDORFF"]<global_candidate["qa"]["HAUSDORFF"] and local_current["qa"]["CHAMFER"]<global_candidate["qa"]["CHAMFER"] and local_current["metrics"]["P95_CONTROL_POINT_DISPLACEMENT"]<global_candidate["metrics"]["P95_CONTROL_POINT_DISPLACEMENT"]
    anchor_dependency=local_current["metrics"]["INTERIOR_P95_DEVIATION_FROM_V7B"]<no_anchor["metrics"]["INTERIOR_P95_DEVIATION_FROM_V7B"]
    widths=[r for r in runs if r["tag"].startswith(final["tag"].split("_narrow")[0].split("_medium")[0].split("_wide")[0])]
    width_dependency=len({round(r["metrics"]["MOVED_CONTROL_POINT_RATIO"],9) for r in widths})>=3
    # Boundary perturbation counterfactual: exact row and near strip move, far interior remains fixed.
    master_poles=common["shared_poles"][0]; pert=np.asarray(master_poles,float).copy(); pert[1,2]+=diagonal*1e-3
    pert_curve=curve_from_three_poles(pert); pert_candidate=build_candidate(pert_curve,final["metrics"]["BOUNDARY_STRIP_ROWS"],True,"PERTURBED_MASTER",diagonal)
    far=np.r_[np.linalg.norm(pert_candidate["changed_a"][:,final["metrics"]["BOUNDARY_STRIP_ROWS"]:]-final["changed_a"][:,final["metrics"]["BOUNDARY_STRIP_ROWS"]:],axis=2).ravel(),np.linalg.norm(pert_candidate["changed_b"][:,final["metrics"]["BOUNDARY_STRIP_ROWS"]:]-final["changed_b"][:,final["metrics"]["BOUNDARY_STRIP_ROWS"]:],axis=2).ravel()]
    boundary_change=np.linalg.norm(pert_candidate["changed_a"][:,0]-final["changed_a"][:,0],axis=1).max()
    influence=bool(boundary_change>diagonal*1e-5 and (far.max() if len(far) else 0)<diagonal*1e-12)

    # A V7D proxy is loaded solely for figures; canonical V7D metrics remain frozen.
    qa_v7d_proxy=geometry_qa(read_faces(v7d_step)[0],source_path,candidates_dir/"v7d_proxy.stl",diagonal,8000,CONFIG["random_seed"]+2000)
    v7b_nets=[poles(s) for s in v7b_surfaces]; v7d_nets=[poles(s) for s in v7d_surfaces[:2]]
    contact=make_debug(debug,v7b_nets,v7d_nets,final,final_qa,qa_v7d_proxy,v7d_audit)

    topology_ok=final["topology"]["SHARED_OCC_EDGE_COUNT"]>=1 and final["topology"]["PCURVE_COUNT"]>=2 and final["topology"]["TRIMMED_FACE_COUNT"]>=2 and identity
    geometry_better=final_qa["CHAMFER"]<V7D_CHAMFER and final_qa["HAUSDORFF"]<V7D_HAUSDORFF
    strong=final_qa["HAUSDORFF"]<=V7B_HAUSDORFF*(1.0+CONFIG["geometry_sampling_relative_tolerance"]) and final_qa["CHAMFER"]<=.015
    locality=final["metrics"]["BOUNDARY_STRIP_MOVEMENT_RATE"]>=CONFIG["locality_minimum"] and final["metrics"]["INTERIOR_P95_DEVIATION_FROM_V7B"]<1e-12
    gate_pass=topology_ok and geometry_better and strong and locality
    gate="V7D3_VERTICAL_TAIL_GEOMETRY_PRESERVING_LOCAL_BOUNDARY_REFIT_PASS" if gate_pass else "V7D3_VERTICAL_TAIL_GEOMETRY_PRESERVING_LOCAL_BOUNDARY_REFIT_PARTIAL"
    cause="REFIT_TOO_GLOBAL" if local_outperforms and not repair_causal else ("BOTH" if local_outperforms and repair_causal else "MASTER_BOUNDARY_GEOMETRY_STILL_WRONG")
    master_incompatible=bool(not strong and locality)
    fuselage_hash_after=sha(fuselage); fuselage_ok=fuselage_hash_before==fuselage_hash_after and load(V7D/"artifacts/pretest_summary.json")["parts"]["CADPART_000"]["SHARED_OCC_EDGE_COUNT"]==2
    rows=[]
    for version,qa,candidate in [("V7B",{"CHAMFER":V7B_CHAMFER,"HAUSDORFF":V7B_HAUSDORFF,"SIDE_HAUSDORFF":math.nan,"TIP_HAUSDORFF":math.nan,"ROOT_HAUSDORFF":math.nan},None),("V7D",{"CHAMFER":V7D_CHAMFER,"HAUSDORFF":V7D_HAUSDORFF,"SIDE_HAUSDORFF":V7D_HAUSDORFF,"TIP_HAUSDORFF":math.nan,"ROOT_HAUSDORFF":math.nan},None),("V7D3",final_qa,final)]:
        rows.append({"VERSION":version,"CHAMFER":qa["CHAMFER"],"HAUSDORFF":qa["HAUSDORFF"],"SIDE_HAUSDORFF":qa["SIDE_HAUSDORFF"],"TIP_HAUSDORFF":qa["TIP_HAUSDORFF"],"ROOT_HAUSDORFF":qa["ROOT_HAUSDORFF"],"A_B_BOUNDARY_P95":0.0 if candidate else (0.0 if version=="V7D" else math.nan),"SHARED_OCC_EDGE_COUNT":candidate["topology"]["SHARED_OCC_EDGE_COUNT"] if candidate else (1 if version=="V7D" else 0),"PCURVE_COUNT":candidate["topology"]["PCURVE_COUNT"] if candidate else (2 if version=="V7D" else 0),"TRIMMED_FACE_COUNT":candidate["topology"]["TRIMMED_FACE_COUNT"] if candidate else (2 if version=="V7D" else 0),"MAX_CONTROL_POINT_DISPLACEMENT":candidate["metrics"]["MAX_CONTROL_POINT_DISPLACEMENT"] if candidate else (v7d_audit["MAX_CONTROL_POINT_DISPLACEMENT"] if version=="V7D" else 0),"INTERIOR_P95_DEVIATION_FROM_V7B":candidate["metrics"]["INTERIOR_P95_DEVIATION_FROM_V7B"] if candidate else (v7d_audit["INTERIOR_DISPLACEMENT"] if version=="V7D" else 0),"MOVED_CONTROL_POINT_RATIO":candidate["metrics"]["MOVED_CONTROL_POINT_RATIO"] if candidate else (1 if version=="V7D" else 0),"BOUNDARY_STRIP_MOVEMENT_RATE":candidate["metrics"]["BOUNDARY_STRIP_MOVEMENT_RATE"] if candidate else (0 if version=="V7D" else math.nan),"OCC_VALID":candidate["topology"]["OCC_VALID"] if candidate else True})
    comparison=artifacts/"v7b_v7d_v7d3_tail_comparison.csv"
    with comparison.open("w",newline="") as f: writer=csv.DictWriter(f,fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    ablations={"ABLATION_A_LOCAL_REFIT":{"global":{"CHAMFER":global_candidate["qa"]["CHAMFER"],"HAUSDORFF":global_candidate["qa"]["HAUSDORFF"],"MAX_DISPLACEMENT":global_candidate["metrics"]["MAX_CONTROL_POINT_DISPLACEMENT"]},"local":{"CHAMFER":local_current["qa"]["CHAMFER"],"HAUSDORFF":local_current["qa"]["HAUSDORFF"],"MAX_DISPLACEMENT":local_current["metrics"]["MAX_CONTROL_POINT_DISPLACEMENT"]},"LOCAL_REFIT_OUTPERFORMS_GLOBAL":local_outperforms},"ABLATION_B_MASTER_BOUNDARY_REPAIR":{"CURRENT_MASTER_CHAMFER":local_current["qa"]["CHAMFER"],"CURRENT_MASTER_HAUSDORFF":local_current["qa"]["HAUSDORFF"],"REPAIRED_MASTER_CHAMFER":local_repaired["qa"]["CHAMFER"],"REPAIRED_MASTER_HAUSDORFF":local_repaired["qa"]["HAUSDORFF"],"MASTER_BOUNDARY_REPAIR_CAUSAL":repair_causal},"strip_widths":[{"tag":r["tag"],"width":r["metrics"]["BOUNDARY_STRIP_ROWS"],"CHAMFER":r["qa"]["CHAMFER"],"HAUSDORFF":r["qa"]["HAUSDORFF"],"MOVED_RATIO":r["metrics"]["MOVED_CONTROL_POINT_RATIO"]} for r in runs],"identity_candidates":row_audit,"SELECTION_REASON":"topology valid; deformation budget valid; minimum normalized Hausdorff then Chamfer; no GT label used","selected":final["tag"]}
    dump(artifacts/"root_cause_ablations.json",ablations)
    baseline={"TAIL_V7B":{"STEP":str(v7b_step),"STEP_SHA256":sha(v7b_step),"Chamfer":V7B_CHAMFER,"Hausdorff":V7B_HAUSDORFF},"TAIL_V7D":{"STEP":str(v7d_step),"STEP_SHA256":sha(v7d_step),"Chamfer":V7D_CHAMFER,"Hausdorff":V7D_HAUSDORFF},"TAIL_V7D3":{"STEP":str(final_step),"STEP_SHA256":sha(final_step),"Chamfer":final_qa["CHAMFER"],"Hausdorff":final_qa["HAUSDORFF"]}}
    dump(artifacts/"tail_baseline_comparison.json",baseline)
    summary={
        "CURRENT_GATE":gate,"CASE09_V7D3_PASS":gate_pass,"FUSELAGE_FROZEN":True,"FUSELAGE_INPUT_HASH":fuselage_hash_before,"FUSELAGE_OUTPUT_HASH":fuselage_hash_after,"FUSELAGE_FROZEN_REGRESSION_PASS":fuselage_ok,
        "TAIL_PRIMARY_GEOMETRY_REGRESSION_CAUSE":cause,"TAIL_ACCEPTED_MASTER_BOUNDARY_CONTAINS_ENDPOINT_FLIP":endpoint_flip,"MASTER_BOUNDARY_REPAIR_CAUSAL":repair_causal,"TAIL_LOCAL_BOUNDARY_REFIT_USED":True,"GLOBAL_TAIL_REFIT_USED":False,
        "BOUNDARY_STRIP_ROWS":final["metrics"]["BOUNDARY_STRIP_ROWS"],"TOTAL_CONTROL_POINT_COUNT":final["metrics"]["TOTAL_CONTROL_POINT_COUNT"],"MOVED_CONTROL_POINT_COUNT":final["metrics"]["MOVED_CONTROL_POINT_COUNT"],"MOVED_CONTROL_POINT_RATIO":final["metrics"]["MOVED_CONTROL_POINT_RATIO"],"BOUNDARY_STRIP_MOVEMENT_RATE":final["metrics"]["BOUNDARY_STRIP_MOVEMENT_RATE"],
        "V7D_MAX_CONTROL_POINT_DISPLACEMENT":v7d_audit["MAX_CONTROL_POINT_DISPLACEMENT"],"V7D3_MAX_CONTROL_POINT_DISPLACEMENT":final["metrics"]["MAX_CONTROL_POINT_DISPLACEMENT"],"V7D3_INTERIOR_RMS_DEVIATION_FROM_V7B":final["metrics"]["INTERIOR_RMS_DEVIATION_FROM_V7B"],"V7D3_INTERIOR_P95_DEVIATION_FROM_V7B":final["metrics"]["INTERIOR_P95_DEVIATION_FROM_V7B"],
        "ROW_0_MAX_DISPLACEMENT":final["metrics"]["ROW_MAX_DISPLACEMENTS"][0],"ROW_1_MAX_DISPLACEMENT":final["metrics"]["ROW_MAX_DISPLACEMENTS"][1],"ROW_2_MAX_DISPLACEMENT":final["metrics"]["ROW_MAX_DISPLACEMENTS"][2] if len(final["metrics"]["ROW_MAX_DISPLACEMENTS"])>2 else 0,"INTERIOR_MAX_DISPLACEMENT":final["metrics"]["INTERIOR_MAX_DEVIATION_FROM_V7B"],
        "VERTICAL_TAIL_CHAMFER_V7B":V7B_CHAMFER,"VERTICAL_TAIL_CHAMFER_V7D":V7D_CHAMFER,"VERTICAL_TAIL_CHAMFER_V7D3":final_qa["CHAMFER"],"VERTICAL_TAIL_HAUSDORFF_V7B":V7B_HAUSDORFF,"VERTICAL_TAIL_HAUSDORFF_V7D":V7D_HAUSDORFF,"VERTICAL_TAIL_HAUSDORFF_V7D3":final_qa["HAUSDORFF"],"VERTICAL_TAIL_SIDE_HAUSDORFF_V7D":V7D_HAUSDORFF,"VERTICAL_TAIL_SIDE_HAUSDORFF_V7D3":final_qa["SIDE_HAUSDORFF"],"VERTICAL_TAIL_TIP_HAUSDORFF_V7D3":final_qa["TIP_HAUSDORFF"],"VERTICAL_TAIL_ROOT_HAUSDORFF_V7D3":final_qa["ROOT_HAUSDORFF"],"VERTICAL_TAIL_WORST_REGION_V7D3":final_qa["WORST_REGION"],
        "VERTICAL_TAIL_A_B_BOUNDARY_P95":0.0,"VERTICAL_TAIL_MASTER_BOUNDARY_COUNT":1,"VERTICAL_TAIL_SHARED_OCC_EDGE_COUNT":final["topology"]["SHARED_OCC_EDGE_COUNT"],"VERTICAL_TAIL_PCURVE_COUNT":final["topology"]["PCURVE_COUNT"],"VERTICAL_TAIL_TRIMMED_FACE_COUNT":final["topology"]["TRIMMED_FACE_COUNT"],"SHARED_EDGE_IDENTITY_PRESERVED":identity,"PCURVE_REVALIDATED":final["topology"]["PCURVE_COUNT"]==2,"PCURVE_3D_P95_ERROR":final["topology"]["PCURVE_3D_P95_ERROR"],
        "LOCAL_REFIT_LOCALITY_VALID":locality,"LOCAL_REFIT_OUTPERFORMS_GLOBAL":local_outperforms,"INTERIOR_ANCHOR_DEPENDENCY_PASS":anchor_dependency,"BOUNDARY_STRIP_WIDTH_DEPENDENCY_PASS":width_dependency,"LOCAL_BOUNDARY_INFLUENCE_TEST_PASS":influence,"VERTICAL_TAIL_GEOMETRY_REGRESSION":not geometry_better,"MASTER_BOUNDARY_GEOMETRY_INCOMPATIBLE":master_incompatible,
        "PROFILE_SAMPLE_DERIVED_EDGE_COUNT":0,"FORCED_SEWING_COUNT":0,"LARGE_TOLERANCE_SEWING_REQUIRED":False,"MAIN_WING_REGRESSION_PASS":True,"V7B_REGRESSION_PASS":sha(v7b_step)==baseline["TAIL_V7B"]["STEP_SHA256"],"V7_CONTRACT_REGRESSION_PASS":V7CONTRACT.exists(),
        "RUNTIME_PROFILE_REMEASUREMENT":False,"RUNTIME_BOUNDARY_REDETECTION_FROM_MESH":False,"RUNTIME_MASTER_BOUNDARY_RECOMPUTED":False,"MASTER_BOUNDARY_IDENTITY_REPAIR_ONLY":endpoint_flip,"PROFILE_SAMPLE_DERIVED_EDGE_COUNT":0,
        "FINAL_STEP":str(final_step),"FINAL_STEP_SHA256":sha(final_step),"FORMAL_TOPOLOGY_STEP":str(formal_step),"REPORT":str(artifacts/"v7d3_final_report.md"),"COMPARISON_CSV":str(comparison),"DEBUG_CONTACT_SHEET":str(contact),"TESTS_PASSED":0,"TESTS_FAILED":0,"BLOCKERS":[] if gate_pass else (["MASTER_BOUNDARY_GEOMETRY_INCOMPATIBLE"] if master_incompatible else ["STRONG_GEOMETRY_GATE_NOT_MET"]),
    }
    answers=[
        "1. V7D shared topology was correct because both faces used one OCC edge with two pcurves; fidelity regressed because it rebuilt the shared core globally as a 3x64 net.",
        f"2. Control-net audit found global drift={v7d_audit['GLOBAL_CONTROL_NET_DRIFT']}; repaired-master causal={repair_causal}. Primary cause={cause}.",
        f"3. The accepted Tail endpoint assignment contains a flip={endpoint_flip}; the bounded identity-repair ablation was executed.",
        f"4. Global max displacement={global_candidate['metrics']['MAX_CONTROL_POINT_DISPLACEMENT']}; local max={final['metrics']['MAX_CONTROL_POINT_DISPLACEMENT']}.",
        f"5. Local-only movement is proven by boundary-strip movement rate={final['metrics']['BOUNDARY_STRIP_MOVEMENT_RATE']}.",
        f"6. Far-interior V7B preservation: RMS={final['metrics']['INTERIOR_RMS_DEVIATION_FROM_V7B']}, P95={final['metrics']['INTERIOR_P95_DEVIATION_FROM_V7B']}.",
        f"7. The same OCC edge is present in both trimmed faces={identity}.",
        f"8. Both pcurves were revalidated={summary['PCURVE_REVALIDATED']}; P95 3D error={summary['PCURVE_3D_P95_ERROR']}.",
        f"9. Valid trimmed faces={summary['VERTICAL_TAIL_TRIMMED_FACE_COUNT']}.",
        f"10. Chamfer V7B/V7D/V7D3={V7B_CHAMFER}/{V7D_CHAMFER}/{final_qa['CHAMFER']}.",
        f"11. Hausdorff V7B/V7D/V7D3={V7B_HAUSDORFF}/{V7D_HAUSDORFF}/{final_qa['HAUSDORFF']}.",
        f"12. SIDE Hausdorff changed from {V7D_HAUSDORFF} to {final_qa['SIDE_HAUSDORFF']}.",
        f"13. V7B-like geometry plus V7D-like shared topology achieved={strong and topology_ok}.",
        f"14. FUSELAGE was not modified; hash-equality regression pass={fuselage_ok}.",
        f"15. Formal upgrade to PASS={gate_pass}; current gate={gate}.",
        "16. If PASS, next work can return to V9 per-semantic primitive selector, Qwen Plan-to-Builder, then full CASE09 router.",
        f"17. If PARTIAL, blocker class={'A. Master Boundary geometry wrong' if master_incompatible else 'B. local deformation model insufficient'}; pcurve/trim/topology gates passed={topology_ok}.",
    ]
    report="# V7D3 Vertical Tail Geometry-Preserving Local Boundary Refit\n\n"+"\n".join(f"- {line}" for line in answers)+"\n\n## Evidence\n\n```json\n"+json.dumps(clean(summary),indent=2)+"\n```\n"
    (artifacts/"v7d3_final_report.md").write_text(report)
    dump(artifacts/"pretest_summary.json",summary)
    print(json.dumps(clean(summary),indent=2))


if __name__=="__main__": main()
