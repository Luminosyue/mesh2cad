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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_006.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_006.stl', 'source_sha256': '178c01ced228c4ac60be466c66d6fcbc41d1ce339451ac0eb3eedb9156984739', 'input_faces': 36, 'input_vertices': 38, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12405242025852203, 0.2626802921295166, -0.05318529158830643], [0.04112178087234497, 0.47822678089141846, 0.17242549359798431]]}
GEOMETRY_BASE85 = 'c$}qGYe*DP6u#?Q^RepsHeF3wr7cZ+m>JHJ^&?4_$RHtX(_NHAZQU%ha6qx3l&t7MFT(`W6f+66R(H+(AyH<f+0!EILG+|QQPI6;jx{42L=Aj=-}(03GiT1+y`xRHcTf=FiXe5HzvRdr2w`w13R0#wnhJ9DrSpqQ%4I|jKD(y*P)61o?FJbsBNeJVeQB;ym8?{y7?M<KrOHrjG#Pb8ImO02J@Z%T3QP6WFU{AL=xH32n50%F#;TROmH&FV(H6KVYkxoM<&}Iql@g!P(aPA;^vTS8Zf*$pBxauxShlkV{NAB47IXfQR~ajlnl3ZnQdfDG#SOAUS0I1E*)GUe-@F5{Mtw@~yE@>$2V)<zc+%BpNbFmB3ZH<#-l<>g^Jyo*=jsOsq0gKp&5)lS^blgx$^o&@t&4;DytCyRux62vuem=0eap7BiG8l_HTb0BV@<y}zp8r_^4`Aa7U%Qf-@%{!k<c!w^KK00Kqm7!iGS%U_?sp=`y_SZ#_vJ?aFIpgSN92XZk%cq_d{9^On@J}tX1OQHiOU0S6C(YHDo=2e2;_{aXx=T26N+%W;cs{E-*rvo69$tC%JyI0qW~Q$HaY-m*@A}dcXWY{T|4--hz2rE>zdU@7ccPHup*VQd6ppeZ@~y?S=K$kw*}3(U^g|a%;gaJ`B%g=}i&*ryq`_+Ss?ew)z;bcP%_G*|mKw#O=d^A5sf-=!;GRHv1iiIvXoto@B&36Y`$TI}P!S{|j#@Yy^LBHS|fIYc9h2nC0gn{#*m~8<HJ6Ab#V~1bk+PP`|UhEmbQyP2MMFj>g;3$xyh`)5M??9VN_!u_4<&N(vVK-BGgmzmF0p+JiG;jSB3D+7-16MHodSMIeIdU<A`46hZi#8-i&M<Y3eusNE_2DSRnHDZ(j~6n+S%703~&6{vj>Onc*fXW@Mqdy4w>#NItIHw-xfbr|YM1k=&TO4QM)qmaW<GoFJw3iWK{P}HILj7$gMv$I*rDZJ1NKs`NAFPx8z0>3r{w+gYR(5B1m6!w4mbp5_~RzUJ0o4HcDO~orSXsutHR-5kVBs5`1wo>ka=qLFIY-#'

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
