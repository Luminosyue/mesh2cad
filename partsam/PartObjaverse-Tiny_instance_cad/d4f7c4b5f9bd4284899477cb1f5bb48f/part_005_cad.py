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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d4f7c4b5f9bd4284899477cb1f5bb48f/part_005.stl', 'relative_path': 'd4f7c4b5f9bd4284899477cb1f5bb48f/part_005.stl', 'source_sha256': '11fa0f28cf0cc4d6bac6e28dbce73e5029e3155460f5fbfa3bd9543606bc8ea4', 'input_faces': 36, 'input_vertices': 44, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.054840490221977234, 0.38219884037971497, -0.4505167007446289], [0.0506545752286911, 0.4287949204444885, -0.4335780739784241]]}
GEOMETRY_BASE85 = 'c$}qGO=uHA7@Z`owXv;L(`fzO`nPQpL};iY!Uik_8>^|{K`%*YHW-lpB(+*ZsL+cyQ4sB+M1xR&P98m&-o%S|uwYve54{K#!Mosm>zj4=a|F?WkN5WFW#`T8?6>Jus4gOYjt=qe!o!YAoe)$_A|fX3(nN9CE*}~hn+k|lN2j6i&gpZ5>GJ_GDXy7$yF6Snj~V9i!cjABn1#{OL@76t87<{)())9l%C^+Y7jt8_yzWdS;zmzb+_-N1>j=vT)6J1*HHpU6rDaQE@?~wM=FuyeQ!Av4zQqqZUHP*OYflK1*>Rtr>&l<JKlR9&_uJ+7Ucb__-_I_2b>mk5183frurH_5d48jKZ%&to>u&z%)mdF0u5&-n$#r+VeJ^f1`seDhZ@o-c{>s4WP49Y@pX<uMke{E?<>xy0^ZZ<Q^B?(g#nL@5rgJ~PKiA#;d^&W)(yUj!8Mv#Pm+R_2O6T)(UHL!FShJSqoN(RUx3?$eEYEp!_l@c9IWz~Wx|~Yqc@{FS=5=|v?!Kq?*T=d%T<8AZ-fN~i{<N>V4V~$IeK;rtRio@~g`B6gkw`<KzO@w-f7RN0djGq%nNDOOV!(aiG4L)~2W55B9sxVS4e-6Ps8iFD!axBY244@}2rpp>yc=`GfF^hlzXyOJ@SU=@%G!-0-VWRX-VWXd+yGA4?BVseCR_*JB#Rzr3yOFYxD7lCz8$y=oN$ka@5eRa0q`Bjw+Yw=-hlZw1Eb)rvNmG>(y2f&68h7p^w*fCjq-h1`9J-~)cenm@?P$tO{eN<U*y9GigAf2DW&)U9V5l@'

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
