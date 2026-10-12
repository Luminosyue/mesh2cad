"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/42e5ff17de214f0d8aabd509f090a46c/part_006.stl', 'relative_path': '42e5ff17de214f0d8aabd509f090a46c/part_006.stl', 'source_sha256': '8fb090a3b97d6c098a2cebcbbf0f88de6a9f46cd1fe05e7cd7f1624952a32052', 'input_faces': 120, 'input_vertices': 78, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13735896348953247, -0.49799779057502747, -0.47629132866859436], [0.13735687732696533, -0.2881278395652771, -0.07630297541618347]]}
GEOMETRY_BASE85 = 'c$}q|S!i5U7{^a$n%2hJHC-l?<tCG4vM-a=PTM3iW@{#s2_xcz3OXU3!JxFsq!eo?j#x?`)E6tow}RqZBT{QgL^FX>TwbaM8%Ww2K@?G3UVP9(J?G~C-JJX73ZfT2e!u)VGr8w{=PnbEx;GVzwWCt};r?~ktt~>R+9ry{>16uU#CUSL<;3Kf0<qJ~)j@n?^zm5yi2`w2%=nKdr^nO&BZj{#74$b5{?y6zsr1;1XHKS%CsjT;_WX2G=F`uPO(x~vb%%mYMn`><an|^+N0B^*%%2w*7bGt)x>gkPq0ukRzn`ATDu(Y}y6cqF_{-j@Wv4v*>G>PByyCBK^zX_1T)AMfb?y5z-sG}VF7CZ`L(h%#g}0r?Q%>XaLy39Y`S>EMPI>;_Tl0FJ|Nf~Z+k9Vqdv5J~-Zan0_|3EGlqXi6`$*5jk5%7x8c#VNFFrVD{@=uC@3K=a#+S@_C03`doAY`3zL{q(ytd+$=U?dl*!<k*H)n1A%Kmc4DHjKyyr$=wvp;>MuS58=)U2&vub#Q%l#9aLhk9=Hi;cJX#l~m9d-Q9)zdWb@hMQwo^!1^2<~gl%_Wn!nf1>SYS_hufI#6z{+v_uTo$}133s-G9_BsE4%K7)xexv=#bK0MjQ(x%1<2hY-lxN?YwDnQ^Fmfg2ux>o3brY|oW<w5r=Q;I}a^82I^YOgzJg2^kb2rU=!+vJDwV#pm{hXMax~}qYaw%uKj#y6D5#<}MJC@UU<M(&w%>0YhoPJ&NoUUui`F)1x)ECP6eTL_JJipKIoX#g-lbARA70BiEb)$U4eU;_beHA&suZnTsf^A<>-&t<;9XY@M^V}LAo5`B%z@A@}^XC`O={mA<_WTk*UR<=zSLJcr+d$*BZ)=Us^3-H)m2U&7G3`}Ah3X(WzY0ur{;OAk_CVYJd>1GRn5Qg63re{UEQb5w9+dK}DCOHw%J+kn@cr-#FaWQBH_18*_JRR;FT5LUfgb`Jz!rD|yax2aYv5&|2fiEJ4tn4o%uV?|S@p8KDCK@xZD1!@5ATGxqm<Wy``~r(Qk3!sQOb9MUifaX4D`aw;5DFMo39`1LFd|lbyEz1ZSWAhAMAwp!^2=ZJP0;|?eIo;Em#Myg_nb+@IBxzuoPa3wNM_F6_YiDQa&Q<7&r{Z;KT3%l=27|g)0uiBk&`#9tOL>L3kIu4~)Y5;630FJP3xtA$S<x4~}T-Jc2&Z+(PJ=VmEjU-VN^shsFB!qWma006z#G1_$7W;g5h3cm(rT-YTnFRtHLX6<7kVg71}81nvM!;CsMwumoNXuLY~c`kqnV2)4q5U=P>|?}7J$9a@h%v_2|t2CLxBa0A>6H{b`fxg7u>f)~mvkmUje+y&o)QpYA)4}fk^z};{>7R>Kb9*-8dirxS8Q*-^unEzb=;mJQ~e=O;r+%8YbdPv2ig`3wV;Sy7l6Y4G~{sz#uKp_'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
