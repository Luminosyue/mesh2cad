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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_012.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_012.stl', 'source_sha256': 'd4e74b0925c6d85a5a2e94311f6c8476354d5f612d1d24612c865dce31a5f09c', 'input_faces': 81, 'input_vertices': 91, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11770004034042358, -0.13482119143009186, -0.4999975264072418], [0.1179095134139061, 0.12295190989971161, 0.4999997615814209]]}
GEOMETRY_BASE85 = 'c$}q|du&ui6vn58YF|8CEK-pR2ur1uM=NZhxLXP>v=o*Kt&0)1!d8m%>XIsHkSmV}LL-FGf|$4@B1mjPc$KoHdx?n#)PGO{8Y)W&iSYq~!4_LuXU=?!J2w|&^d=|Y?|wad=FIHu+*?;skDkd)UPIZ>he~2&;}{c>$dXyLw`y(W60a{~<?3}&tS|ZE3hVAU3yNLtC|1pCY)ieqB~`Y`nk}coZcEo}6|1V&R+X<@ysB!cSNQqmulu~*_bn@5?dA8Qvd5=unQ7_TdhNen@uG+Np)El!`hnb24zAAjf**wX>te`fYnE>o_o0rgYeGGBcg_l5JGbCdp+?uQ<ZE>|rC<Hk38DUb-Ph>8?mGF#t(&KXhPv7)KeXpNnSU|&9F5c6E&ZL_nkml}-56O%-&sjM^M9e#_t%~bSk?E}HjuAR>n-Qe-9bLvkxM@N_Po-+XWO1Llz-xzCYn!MPg)0k%dRHjJEvTy^<nKf<ZD~jldnH0JwV#^Bh}G2o<AKqFRi;%j=SL|&ByRpe<H{Ig?!_!OXTYT&r#X`ZJA$l=@g9{djb7)w$i-bxPQ`WUd9UVaq=&}AC&%m@}1>rvhH=QL5_P%)-NASzP@SLF*)uXx&EF3<a=UP7_v?m{C-ERzAtCP_ebddgSXZC4Hu;U(+;J+bMGq$sm_rrYX07Z<m;|BCEutoJZL#?{RHwunOl@Tjk<W5e|2AT<oC<AR@Tyf8JN@(xz3??(#SX5+tvJvZJQ~-lO2!j$Ma@?ALU()QGEa1^t&w<eTIGGWnJm>q5p_Fdi_#mee{%!Du+eBKE8gV!=g`PUdndzv-X{le!E;ZciWDC@<WGRim$sT)jBNJM|-J^eDiwh3B3<Gtkyp<gM9P%<w?w!`KEQ#6HCcA?}t!gh0HhYA1yWMs8yY?Z{E*Z>JakH``?plBj5ac@!0Z?)8`6qH_AGH$a#%=m3;r6V$^>i{c*mNw5}g{gOTTeK5jSp`l7?~JnQ~b@jY8>PDj>%m>>AKQTBOH?h|{Uk$lrR5cXMnf|768gXH^nwJPKK?VmMTty|bPE{;*^u<S2o{?#=~pJCr{yOsQq{j%)SbiQfXH)Ou~Jap`DlKEGZKEr-!>@szIX7mYI?dPy>xR)sTo*792tNPCTJo3%Y1-;-snQuDhLj{KdmixBwwPxz)!<j*4oeO=<ay=JgTzNjTq8jOk_BP4><@3uZ+(5qG;8yw%6;C-!{f?eQ&j){JsjTC=d^WNlPiL{5uj?B5Y*<-P`X!35pC3W}I6J4S{-SrOAJ#ch@jX#4`JC-Ylm0wg3*`^0kotQ<You@dww%;|Z$JF8(*Jy2Q0B+CI$X+I)UkCPH)i)_Ohg=ii>fG(c!d(CxWa1v3RRi)uU?_-|Nj-LAMYW7iPt@;3@olFa3Z)DG#V^49^4Du2ih0h2b>HY08R!Eggyx#2p$AY1rGv`gboD@9R?OU0xZ-97CH(nbUb(@cmnh}@C5Kg=ydQz@C;}XSm<o<i#!(caPvsx@hp$gJSOv)%EN&WoR1J(2%Q5KIu~3Bo(Xk<XM$%z=Yc2jn8G6mIt`oy&Vv?!pXZUwqXe1<&O=TKbQX9P#wtMwE`z$jW#CfiTyQCP0YdP6=p68T@CyjR#R$Pp=v1)KY_L!}*a^;rW`Tu{1!scCAp{SHJ_8my7(5*O6hd$c^a*eZxHmKjEVMs3mWMb3;-E3$82mjB+8_KlkH>iQ;Gyw&n#T|x={&~p$PnvX6cwG^<5B<4{e9`;N38sFXa1ymghhTbpWi+_&|F0^q9=Y3M6)$qzZRze`wKafqvQ'

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
