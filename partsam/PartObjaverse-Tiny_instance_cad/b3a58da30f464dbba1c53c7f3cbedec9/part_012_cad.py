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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_012.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_012.stl', 'source_sha256': '43beb0dc6b65250858821c8c6a0d05f461545e5cbdb3de78f1f91344ab7d7e94', 'input_faces': 74, 'input_vertices': 61, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.02851197123527527, 0.310838520526886, -0.26158711314201355], [0.06279385089874268, 0.3590503931045532, 0.21532389521598816]]}
GEOMETRY_BASE85 = 'c$}q{eNa?o6vi(g0r6$BAYZ~o#05pv1qGH3ZfRz0I?P~9W){r4D-;PXD~=X3x5AHftR{<T#!*b#aTZdW>5s^2xV32sNjoYKH6j!>X*2erf0Wrw_dVyKc5Rz!>N01Z-#)zeob$f#?tO2SHEfze;wwwKc=f9*CAUeEh#1Krwc4Go2AjR5U{mw95NSI3;+oR^s~=cZwKha*m7X+iu(#NpMzd_RI7*E9veD7xbUEubJ=)~lU>E+1y2ci}?zhy}HQV*ixl0%4%Y}LQa+~~LuiHfr<)(ubx~MDGTo5|GBh}aE=PTa5<SSQ8$=42=dHl$!A)(s4FAR{5HIgq?{zSf-`3(7zHp;%qLU|5fj^X_9)sZgFzvo`^74-_&?d+yJN_HdVnew%DhGC)d{@(^@{P@p2zHpMqPp<ov`aE6m8s#54PWjbytGNHU#q4{3r17;6J7~PLtAc!KPxdg^jpRI~1xIN7F&FvLv+@0;{buqN%Sz7Qd4%V6qnv#0t$6a~p&jI_U(}N?ovq~j!{^V?eUEM7{QC~^yiC@9s{8#Y=l^)}Jnf72gwNmC#<o&^?LaTrz0=%9`Fp*T=WvHgdDON>^0l=mxzCrYInPBG`D*p=ybc$dc^w9yBVRF@D398gNWS`_?RD~>pWr^Xc5|PhvYYZZZ{z(v`VP;xaHBg|UDfuuJ6K)K+d{rlvxNKqI+^|DpYwRfb?&F@Bc9jgx}!ATw(YzQ3r_m{{lC?Pe{0<-U%6h)btBTbuE)vakKf?BVQ0B+T&#yaKXi@9@BNT`<&xDCtbes)jVEZ`rUyO2`c!;fo`C(m=RMx9m)g21f9oaw{*<}7Zn(LJKKBOhmvXAICurTA>Yku=cOGIt<pb`2^>)tx_BWh=^LO+;)Y|KP{=RhA7JhDwywB_WNzEISx8VT)UdEPD9%;0ld~JOKjhD`}`}}=n@ILOx>t;V)Jx1d?=1`v6g;D(dd}=rO%4htXQR+AHd}CfAU!6D+_<J{<K0)KG-_m&b=6cR!>t}!Y)BGHBObqz@k}HYVx$`Fb-gD%uKe#D>ZO2OP^V%@ysVwLHYKkR){MVQ_$-n<qu8TZVzEnI&{&;5v_j7jw`RXGzyq?i%K7U{Navwh@U1ncjRlunev3uvTU&16wM3jE&IO_b49AS!UN`oIc4MqRz$SE%R-$zco-h(*(Vi1DE5Q0PXn1-p{fe=?5Gz1(6jztKb0SyNi>0uU2jSy^smVzzdGUyVp&=T+h+`mYVd_5N8e<k2D=pt|#*a9sE=jky=k6eV{Y-lDp8!SUp!7?}vng~t<Cm{q!BLs^xJ_>4pCV~y%6lf|q1)KrR1ZSex420kuXdXBRJWr28s0o?}&cpmo2*Hc>SPCsb2%Znk1<wZ?q1j*~cs5i9&jx2f)4*BabZ8Pd9Xt~n4W0>3&|^9@0vZjD#`;De1V{SqK_o(OIMe_R2hTtVPKKs{lfko~8Q=`8`z(auxzKswDr-onA?%-CRsXtF@dFBYalQ4<z{idMovnJVKOa6-)^K{u4b}fP>*}Gm%|8G|Jy(?'

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
