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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_006.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_006.stl', 'source_sha256': 'b45391446853f3637643d58a4497c63fb0cf12b9d600760d6cdf1cf30b0b2a0a', 'input_faces': 40, 'input_vertices': 37, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.44136661291122437, 0.013513132929801941, 0.1861264705657959], [-0.44015973806381226, 0.06461672484874725, 0.2372300624847412]]}
GEOMETRY_BASE85 = 'c$}q`Ur19?9LLZ8sr#dut#a;9vp-y=A%lrVWV46#VN@#$l89RFE`^%5*+`<e4;7hUi1g>Bpa?Y540<RC^gh`}+n}Bd!j~ZGxgL6m(LLvW@7%c<L>)MMKj*{mo^$vy&Y}^M*-6yVOiujxQu=8kgiZ%>l8l%d8SEF+ZOP$L1F2`84lSn+9y<{2Gms3qEX2ihe@fWx7xpA}2?4*57)p(#V#!lOsklgePwZS;RD60MHY_UZmQZKFA8HNwulWCU*pw^Cec?}w^e#)Y<6)XTjqk#hUYx$o)|TZQ=M(VPkLNjm>FOP}CfO|KM^)cFK2YHNqtXL*?o0z;|5)|%XK#`7hshIGU;6O2(o343I9cSq;VD~B>-ImQdP%?k*?n_tAKg9WxcvpI*Y%<7b$yUu-(p_gulAEfLhAnaCnqZVta+(Rm}K>5zU8?3y{adzy?M?rU%SiB&40~u{-f&2VsC--H^&~b{=2&P`Z3i@sqcKf*3YAatJnH0bq0%E{mPpew$|-0!FTKT?^u{+UUz>9US8nuFPYBIvvYO*(Y)Nk_eXLBx&F&jJJoYvCe{0RmI|Cd6k_L+8}?kKmo#tL!Ph@~^_=Z9_ba!SCo7>mx6j3U^X2<QxmP1EWZF&}38B-fyc&sE#gjoL9a^saWDK_d)sxX4{O>2jrQBhQGTq2#FwJdXH`t5Z4)%h5$gN->*n>&A3F!yZYy>xft;kJaE4Uiz1XqJCn3PS(2CxZiK-Pl|V1isnRtIGxay{4xHX}EH&EP8JMsO9l2Duqr1GXVuU>n$ubc5~STBH|T3$8=@z;$2;(gTi03`VEvPk(8vL!yo0{^0aq@;~d!FFTZGlz-&Wh=uk*X`GQ<Q1U%n{RTjDW+V'

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
