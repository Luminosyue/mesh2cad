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

PART_NAME = '__PART_NAME__'
SOURCE_INFO = __SOURCE_INFO__
GEOMETRY_BASE85 = '__GEOMETRY_BASE85__'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

MIN_TRIANGLE_ALTITUDE = 1e-7  # Original numeric coordinates; CAD kernel precision.

def build(force_independent=False):
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing_tolerance=max(1e-7,construction_scale*1e-7)
    sewing=BRepBuilderAPI_Sewing(sewing_tolerance,True,True,True,False)
    planar_faces=[]
    skipped=[]
    subtolerance=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        twice_area=np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))
        if twice_area<=1e-12:
            skipped.append(index)
            continue
        longest=max(np.linalg.norm(points[1]-points[0]),np.linalg.norm(points[2]-points[0]),np.linalg.norm(points[2]-points[1]))
        if twice_area/longest/construction_scale < MIN_TRIANGLE_ALTITUDE:
            subtolerance.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    if force_independent:
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    else:
        sewing.Perform()
        shape=cq.Shape.cast(sewing.SewedShape())
        representation='faceted_surface'
    if SOURCE_INFO['input_watertight'] and not subtolerance and not skipped and not force_independent:
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
    if not shape.isValid():
        # Sewing can split near-coincident source edges into sub-tolerance edges
        # after restoring the source scale. Preserve the original planar triangles
        # independently in that case, rather than altering the input geometry.
        shape=cq.Compound.makeCompound(planar_faces).scale(1/construction_scale).translate(tuple(center))
        representation='independent_faces'
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'subtolerance_faces_skipped':subtolerance,
                  'min_triangle_altitude_original_units':MIN_TRIANGLE_ALTITUDE,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':sewing_tolerance/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    print('CAD_STAGE build',time.time(),flush=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    print('CAD_STAGE export',time.time(),state,flush=True)
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        print('CAD_STAGE step_reimport',time.time(),flush=True)
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']:
            shape,metadata=build(force_independent=True)
            state=describe(shape)
            if not state['valid']: raise RuntimeError('Independent-face fallback is invalid')
            shape.exportBrep(str(out/(PART_NAME+'.brep')))
            shape.exportStep(str(out/(PART_NAME+'.step')))
            report.update(metadata);report['cad']=state
            reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
            report['step_reimport']=describe(reopened)
            if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid after independent-face fallback')
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
