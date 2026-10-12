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

PART_NAME = 'part_019'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_019.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_019.stl', 'source_sha256': '9985fb2964625a6254cad156bb40ed16aaef571a69e0e1ed54d80d09d2b3ba44', 'input_faces': 60, 'input_vertices': 86, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.24061483144760132, -0.22052429616451263, 0.21959565579891205], [0.411755234003067, -0.10450618714094162, 0.2705244719982147]]}
GEOMETRY_BASE85 = 'c$}q|eN0tl9LJx_1ye%Ax>!ioQIHFG<vrdMIGCtG;DsQkTi$cS3t0^8!eFjdr>!+=))KPyHg*&FgEfoQfE0_v>*Y;KnWC-1ZJD#?W>Kc=W%a!L9(<m=+FG6Mx9^Y7dCvFwJ->6F!@2e%bD#yWV=YRKPZ)n~DMBPdkOeim+ztCHUG)jI2M(H080F;P+FDXkY~O7{jp%9XK39FE+nTLdH&<m^ZHl$3&fVa4);j9k`&@)?bJo<mFt2~ydBBDLj?GNBDXDQb<r(F_9>KT-y=iJX534eU#`=k_-TOKDTdg@yx!O@O+D})<ILZ#Bs$KhFTpaIP6-`w?cx+f4uZ6|4>&$hNlD{dF>D&2UI{wJI(;`=ZduAuUpuU$%na|Apm^j{_^YQ9A2dl@~K0>(fb?^tS0blg*dY;u2TP)RSJa?R`$I>_<&da$DockC}-K_rXkRh=T$`b>uPf^)Zgc~0(VLp{!<`cPcSgezC4LJ8lHBq29C#AmaN~he@-!dqz7q|{w=XDn5vp&teG9cEef7L;`PfZ&TeK<FOb06)*2;+}r7?Mvx;u*@5ZuHajav$J2aPFfoe~fZpPQ+()UIlzQI?vL1KAG*KJ|#QoIPK*@#)o=N(eVX#%F*fC8S3-BaZ(!J_blbcmG}F^@!BT+0-dKk%MjPAnYt<W9BOBE!u|5~|3JCsFtI*&M^4dsdv8*XzHO8G;Oh*$Nd13llKQE=x`y$XN@=|DVl?GO=cjbMc5DOnSE}<VSIeR)_dq?KT{{_{a}0^~7-@CPzh+K)9{f4)zna)Ux$>xaP^?FdXr>&6Ck%=8=%FpF&MoJM#d$sEcNsrCBRyBfZ$}xoHPQD5>VZ119cTQcSK3GV)h<@&M{R@Rdi}XFc9D)(F845>*1e;mzwc5n>rdN+w6AqvA6wV3Cha@UeM6eG@3i?-Z2a6+uT=l!G#l^g8J7Apc81N{^^)`+KquxI4?9fzpu>37`!!padqJv`bEPSDT-@)RBjAg5et3oX1l^F{d;WZJeEUz7Yt7eb|5e`4qdznMcKfKfF7)1YR)6jh>AmgG7yaM)mCZZ5;1$=azWE2^=c?uR<Qspoc^xSeVjqlF)0dPlqz{YF1LwXU8RzwTURc5S<+u^iUwbl!ay7MC`hSP2<0<#-DW?78?`MC`{gKPY_|`(HPR^Ck3!@^}9Lbbxk>8An^>eNQ=l*J04&}!0;ZpsoJ&&y`>n*QXr$6UDzKjYsZ)}USUQfy%=5INBt4_Q0HS?V_alPG)5Q$~@Yo^L6e990=4z7RyDYHNAUwz7?C;jhFnIv388d*2!CddnMY{5|uS_b*uI3jVZ0*!$DE*z`j{AxHy@;DsHIATF<kZ;40gQFPqA;?2<gyRSUy%X}4I4p490_RAci=za`PS6U-O*lx4gFu%-z63`woDYU`B)8&-#t{R$4)O<}7Y~D$Lw-NZy%97O@&I@YLO^eWd^wJ#a2~#5X?`D$dvUA*y$AB`Fh?fnM#ytveW{@Nkdw9N!TO2XAt(LMg5DD?fSlaZ%{VeZ6Cr;P<|_r=4tW_|vlTQ0@^rXn2WTne#Ip!|iDpB-0s5N&YK5HC77z6iO@Um&5rxRMV!9skJ8;~NV+Cj+<n|&{fW`bzKP_$@I=Si64-Nk-<!vlpIgPy*H?_SeXbHQS0q7~LyXh={0d<`gmH'

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
