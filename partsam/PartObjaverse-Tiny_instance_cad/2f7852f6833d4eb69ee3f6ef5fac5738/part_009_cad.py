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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_009.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_009.stl', 'source_sha256': '073abd464cb0a31d08f515479ea112f11da54bb043592e1f2c6514aa831cddec', 'input_faces': 36, 'input_vertices': 34, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04729747027158737, 0.26593607664108276, -0.06746681034564972], [0.046181902289390564, 0.48566538095474243, 0.17242549359798431]]}
GEOMETRY_BASE85 = 'c$}qGe@K&26n&dIb-B{1ZF6Sd$e7ZwKur;GgV2IyEVM`oZRu8qINd}DDLxAdi%7H|MpVnp#E@Lr52M`3u>OlhrB<3nK@nw0N<mTY-S4ixkwMgh!#VHlzWeU(dvCLtLqg+-Fmxo5A4=;BA%r1{#E}M@v%adr=1Qxn-6<i_;Ik3nwsji{EhQ4tKpORxHdlpHpTp^M?b&(*r?)$t^-gO|xx-m$V}60P+GV4@YrD19M&~K%83ryr)xhoI{&mP{3BK~IZZBhXnBT~1I`d_}QS2MvKVoyfK;G*W`)18kh^x=PEsi&J%Ac{hsVUzhjwiAX@O|C#p`iHU<>Qb)+!yQ*j7-2>S2!s4`R{MQpX~T{B`7{Q{yEhDAkV?r{VL)#?Aw|O`6nZl!(!hzP%Y%yDD#4^+I9@`C$v6<dOmg?22LqG2>DHWpby+9*#+?TH6DOG(|3hFcs&Di`CHnR&>vEi)dckvcp#6jt<(cP8Qlu|HupS+^?A)b5XTR%hdjk)Sf~G%5I^}YkI~fCC(!2;QaBe9T~!2m?@x`v_Zg0be)4Zu^AJ}&13vGFzXQC=+ajDF4|ST>EV%|gnE{`?s2c@;`j8L&%uUCE&s~IgGX8q6SL6rIm!#Wn80YZayYq!SmxhEqgYA%?oYca;B$;zVJ=a4=gYqw(5PVI8a8K5rx(V~Lh_f(%d2|Hoyw@-E^K)M(e4e>kxQFGLmw|WWbP4;-LjT=g$NC^HxeU(JH=8YdFaME#$g4juoU^t?sK?;xHClpS`?6gB3MnBBk@U6Ot)i#SOf~{M_fxOR_`9dR^1q+@B3gr*A_2j)hC)T5W!DG6^gIO9Q4|Z1b;w%OT3oNgd~A;-WF2Z9#xTu(^^_D6Y@tN7mjw5hU`(JMC9YTEdKGd6Y8C1v<Z#qUsMW|a)N0fk1k<4u97Q}uB7*4{iZBZHJ1Ipltw4@J9fR=-WDd0g^<oNkZ5C3*qCX$=F^)v7z*y#4%o1r_$e;dNehnU)DgLARZDr6k6|ek2bN#%u7IPTu1uaBM>L{1M><8VdS&{'

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
