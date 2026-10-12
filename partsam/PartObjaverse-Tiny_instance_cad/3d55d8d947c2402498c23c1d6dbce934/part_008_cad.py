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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_008.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_008.stl', 'source_sha256': 'ed60a61fcf0c29f3957e8a0041d165371cf09f305ffa2555f5d075b71ec19161', 'input_faces': 40, 'input_vertices': 36, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41754013299942017, -0.4628039598464966, 0.08967842161655426], [-0.4071246385574341, -0.3601812720298767, 0.22058622539043427]]}
GEOMETRY_BASE85 = 'c$}qG&1(}u6ras@ldef>)M)&yQ+wE2g9wR5q+swMLQwW#4?@9&c7p{;+f6ML5%M2+(2E!8)tiSR6;Z1o2zv2k@Qe6A=*5#W)8DMKuPaD9@c4b~+qbjxmbZT09w@TSHNvLaYyG~>n2a1NvgIILnwtqar`roF7Aq)UE{*rEPF?Y@TWp!#@n(b0Oz55G-el{XSLR-8K3oc$?HlvqY#{wh&0C#7_??^0g+S=B%0!u0PL}yyzTLG;Y@zmh{qrk<-3O1pDSZ6>?S%xtacc5|>GRyg*Q9*y)BM$YKfb8z7pLFE>cj7s*58?aEwiGKk$et+Oa8-(!j0)CFOvLKyBdG5wNZr)vj2wm$^QF=_r0Y08}Mm;R({?~s;_-c&-3MN<=4i4J&onV=cV53*mKY3KPBaBU*~tP4JG!M`ucsfPy0)Knos*1)hGScKJ9N*pY%7%C;g?qKL6;sq`%sy{nbA0ul8wwwNLv?ebrw-J{^93yxd5MTST~GI<%U`Xpp8{8k0xET=l<3L-ov#M?+TZLC%Ncz+r<AK}$Sg@ZHc7M-85Z&Z36oX%Pb=GC&91fj$I0Xz(<&#KQ*9KubJga0l8!4asr53=^1H;1=|LVA0?yXo&|5ZbM5f8Qg-lP($*Zh(Qr~pbPFo9|ImWcn(@3H+UXe;)uarXcsjk-z%aZVjpl1xL>zYMf+dBuD`3R4#xbEZMie{S(|qbi>5^%xnFnEn}?ZVivpi1^#?L}jc5'

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
