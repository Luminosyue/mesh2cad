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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f1150d2342a8470e912942c49e978f28/part_000.stl', 'relative_path': 'f1150d2342a8470e912942c49e978f28/part_000.stl', 'source_sha256': 'cd2b79d767b7654cff0ab75ba7554fd76465db9cb073c0a76931cbba29ed7797', 'input_faces': 26, 'input_vertices': 28, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49999991059303284, -0.4921022057533264, -0.2575210928916931], [0.4350760877132416, -0.15472596883773804, 0.3187750577926636]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;2?17DpMC@?cHfG`h(2t!$FQAuWUYO!8kK_w%D09YIZVDx0aP~U(^MuswmYW0-V;^ZQAD+P6%Gz)bd1@*N2qLQM-y!ia0lvI$oTVhUeDp0&QBe5VA$k#Bk&`~hf)KREaAQx}}ov`5l|NHxaw8N}AFr8poePKV6c*9JHc*FU$EB46ZdE1VG=mTi#59C6`7krQGMOM!M6<2_o;~@3&E;f5%;tYc44kMcnS1$k+{{}H1Cf>jg5r6Q~{}M?2!16g~!Qx@{x4`B@?S+Xu96Ngo#XWwlC$ae#CXV5Ln0j=3zvLbT^Fw>@A)C{nCB6oqIJ$cdbQVv?<{p?hx_jX2(cHsO-`8Z1B^(%14&DUO4`AlAMD-$zqlYt09Nqi}bI#nvW`2U_joaAFhl!)76PP%PzXDKlmymZ=?G8o;1`y^1=B~6vq^t!J1OXV0J!@r}5SO*gD9&0EKsSJ#E(oQCpllE=0A+({ekfZI%I1dBd{8!s=7F+7G#8W&qB)^#5X}f>GXXIhG{`_SE0hf?aoC~q>`*xnn+1qDpz<70IcBI`yij>ws2mH_{lZXrVW=F4Ee*utP<e5v9EdFi#9~l+F{m7fEeXV;P<c_P9Ecs@&B!FejH^gRfCg|pBNwpfI#H7gvd%c5S@6UY;LQpSFD4)?1k!=v5CZ@a_EXm'

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
