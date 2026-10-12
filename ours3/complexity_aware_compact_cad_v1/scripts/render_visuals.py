#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
import pyvista as pv
from PIL import Image,ImageDraw,ImageFont

ROOT=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/complexity_aware_compact_cad_v1")
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(n):return ImageFont.truetype(FONT,n) if Path(FONT).is_file() else ImageFont.load_default()
def poly(data):
    f=np.asarray(data["faces"],np.int64);cells=np.column_stack([np.full(len(f),3),f]).ravel();p=pv.PolyData(np.asarray(data["vertices"]),cells);p.cell_data["brep_face_id"]=np.asarray(data["face_ids"]) if "face_ids" in data else np.arange(len(f));return p
def bounds(arrays):
    pts=np.vstack([np.asarray(x["vertices"]) for x in arrays]);return np.array([pts.min(0),pts.max(0)])
def camera(b):
    c=b.mean(0);e=b[1]-b[0];r=max(np.linalg.norm(e),1e-6);d=np.array([1.35,-1.55,1.05]);d=d/np.linalg.norm(d);return [(c+d*r*2.6).tolist(),c.tolist(),[0,0,1]],max(e.max()*.68,r*.38)
def render(data,path,b,color="#a9c5e8",face_colors=False,edges=False):
    p=pv.Plotter(off_screen=True,window_size=(820,700));p.set_background("#f5f6f7");m=poly(data)
    if face_colors:p.add_mesh(m,scalars="brep_face_id",cmap="tab20",show_edges=False,smooth_shading=True,ambient=.32,diffuse=.65,specular=.18)
    else:p.add_mesh(m,color=color,show_edges=False,smooth_shading=True,ambient=.30,diffuse=.68,specular=.22,specular_power=22)
    if edges and len(data["edge_lengths"]):
        pts=np.asarray(data["edge_points"]);lines=[];off=0
        for n in np.asarray(data["edge_lengths"],int):lines.extend([n,*range(off,off+n)]);off+=n
        line=pv.PolyData(pts);line.lines=np.asarray(lines);p.add_mesh(line,color="#26323f",line_width=1.15,opacity=.85)
    cam,scale=camera(b);p.camera.parallel_projection=True;p.camera_position=cam;p.camera.parallel_scale=scale;p.enable_anti_aliasing("fxaa");p.show(screenshot=str(path),auto_close=True)
def label(path,text):
    im=Image.open(path).convert("RGB");d=ImageDraw.Draw(im);d.rectangle((0,0,im.width,42),fill="#25364b");d.text((14,10),text,font=font(20),fill="white");return im
def compose(paths,labels,out):
    ims=[label(p,l) for p,l in zip(paths,labels)];canvas=Image.new("RGB",(sum(x.width for x in ims),max(x.height for x in ims)),"white");x=0
    for im in ims:canvas.paste(im,(x,0));x+=im.width
    canvas.save(out,dpi=(180,180))
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--case",required=True);a=ap.parse_args();cid=a.case.upper();dirs={"CASE_03":"case03_control","CASE_04":"case04","CASE_05":"case05","CASE_09":"case09"};d=ROOT/dirs[cid];cache=d/"visual_cache";src=np.load(cache/"source.npz");base=np.load(cache/"baseline.npz");occ=np.load(cache/"occ.npz");ours=np.load(cache/"ours.npz");b=bounds([src,base,occ,ours])
    render(src,d/"source_mesh.png",b,"#c7cbd0");render(base,d/"baseline_cad_shaded.png",b,"#a9c5e8");render(occ,d/"occ_unify_cad_shaded.png",b,"#b7d7bc");render(ours,d/"ours_compact_cad_shaded.png",b,"#e7bd75")
    render(base,d/"baseline_face_colored.png",b,face_colors=True);render(ours,d/"ours_face_colored.png",b,face_colors=True);render(base,d/"baseline_true_edges.png",b,"#b9c8dc",edges=True);render(ours,d/"ours_true_edges.png",b,"#e7bd75",edges=True)
    compose([d/"source_mesh.png",d/"baseline_cad_shaded.png",d/"occ_unify_cad_shaded.png",d/"ours_compact_cad_shaded.png"],[f"{cid}  SOURCE MESH","BASELINE FRAGMENTED STEP","OCC UNIFY BASELINE","OURS COMPACT STEP"],d/"comparison.png")
    compose([d/"baseline_face_colored.png",d/"baseline_true_edges.png",d/"ours_face_colored.png",d/"ours_true_edges.png"],["BASELINE BREP FACES","BASELINE TRUE EDGES","OURS BREP FACES","OURS TRUE EDGES"],d/"topology_comparison.png")
    print(json.dumps({"case":cid,"render_success":True,"triangle_edges_in_shaded":False}))
if __name__=="__main__":main()
