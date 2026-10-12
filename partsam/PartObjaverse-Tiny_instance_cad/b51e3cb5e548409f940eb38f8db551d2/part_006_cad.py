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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b51e3cb5e548409f940eb38f8db551d2/part_006.stl', 'relative_path': 'b51e3cb5e548409f940eb38f8db551d2/part_006.stl', 'source_sha256': '7f63eaf0adac0c1ba0162101e41dc3b262de89875790c5273969dedba4692f69', 'input_faces': 80, 'input_vertices': 52, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07630158960819244, 0.3953111469745636, 0.007040966302156448], [0.02649686485528946, 0.477711945772171, 0.23179638385772705]]}
GEOMETRY_BASE85 = 'c$}qHYitx%7`?mQ?SsDQ_WhbZr_Z&vi$P=P{*frPx;~ILk+2)s#zus)tqo{trdp+h)kwjBAt7z*52eP4#>Wq0E7pj0#|jaQin@V6CdRZzi5g4s-tV5Rcbb|Qo#y16IX!c}yPLZ=<7<m^xR|`k*oE-?Z+<6Z0x8VJ`h%gq?(M-|_pY9OHkLuYxMF<dp3UvPP8;iIPwG2@z1u_jZJK_2*LuA{)4O(u`a*$S+jfU`1ckpbu(LPF{oY3cJwbk7v#z;8YpHF}_G|z3TEmy%HAdc=5=;7h|5vS?#}+<{w5oo`$T#AieQ<nG@U-{jo5I&VzMJyKm3Jc+U*970*Dnpw|KDkPgL<wdel6~!1q%_2zd7qNJs*E*i01wjew}(|zNG%>Ks2KI(TXdwU%zJ1dfU%WQcuzQ)bDSpGF4w2I7j{Lu>K73XN#|r|6`c)V=rc#svq5SjPl0mjl;xKqb~`6tZzj23{9G<uU#Ddj@I8DevWuaKT18X9kAqMzCYEPH=^4PQ;+s1eXi(3L#D+yoRnuX_Cv%!G?MS1w^P5jf7n!gEjLZ(rwS==oPF#Nt^d9T`91&of~orc)3;FGn7AtY=gMVX^HAPDJZh@G|ISv~KfWmQK952ExprFr^wxV#)z=m}zNLQ8>;dBY3s=p@e67ZsXA?7fXgz-nQhw~wt)|8AJSg)ylOyE6GP-&`=C90uZ||Y?RP<2Zd#1xw{pizAP@a|Slljk6Z>63G$0_fh?J`wgdwWv$U++9f{?34pa^uHozp*<COx4$H6LO!N+DrS5Z8;O7bzk^|^4bG6rp0gmLgvGrazEQ$k5m7rXJ!7wYSZG^n{q!t@0EFWnSN(ui@#9bd){MO{D+rhzNhS2@&{+b)bnzx{Jos|Ib!i0d2$~*=IME3L)s|iE^eUw^m{iV7JuDcvj6JbQ`B=~?=f2Uit}XIUwNJ^m7SouE6%HBUp=pUmecu2vU|?!5KCn&iJ#700p(~GCSz=wS3jD&J^$)xUf=Y;kLH{C8d^A-fhG>&HE_5&D#6vzf{UO9=RxOl6mwK@G=gsegx0~u(2bZ;1+IjyQu-><AM4J?eI8~P14Za`V_r2_ht`pa`EJa2W46#W9CaK8;1X!TInaXFLT7R0aujmZg6jdHOToF&wU|)|E`Tmn`U=n=>(0XcTFlM`a?n|ac_rXd=u%`#Ft;ArI?NWH#!=3Z0d_$PPJ<Sl0-ef{&XLK)7MENB2%Qa1hc3g6OmGHtrqY*z{!}0Z&!=E^I*^9Wa?Epqv!Sz*aba!+vgMd9yf_XUM*`RhEjS5Ua5A)bXG!FU=dgogm(UJyBD5Vd;=u{f@k(C;`eWT|aG#9Xi9ixMZJ39*IP#p}Bxqlo&F+f(r&q(jFN4a|7sZuNT8}OD$&<Wm`4IE9IqAEw^S?cu^TnrNe*t0c>=y'

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
