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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/74c05ea2f5d64357a75e4ecafb9570f9/part_003.stl', 'relative_path': '74c05ea2f5d64357a75e4ecafb9570f9/part_003.stl', 'source_sha256': '49cddc39f530a327ee9703562d1cc311ae384b662637b74adc0556761bc45710', 'input_faces': 31, 'input_vertices': 63, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.18919801712036133, 0.06763000041246414, -0.3403083384037018], [0.19358842074871063, 0.0682491660118103, -0.31748393177986145]]}
GEOMETRY_BASE85 = 'c$}q{PfQa*6vn45AfPCJs^TAH{l@}U6c!62DqOrYk|oiDG0|@57ElAYZ3sq9YCP-37(H<4!5B{_9`tHY)|25N9!yMnGv0gGH@okR-PbWOI^@gu_$8f8zWI__I~8k)i(nlT?%<`4g(e}Swu!h{b-n!JoSPe3TDcPu?LL=_{K?Gai}sa>SQU58jGLSD%n8Gs%#NE0!^|#wdCyt8zU*aO$uBs!axU=Pg0ten|NTiTVORqR<G%5)t5u%i#n{L5V1{MCkzQOcZ@$;?^t;zuE;gQOdFjVJEic3}T5j~Dw7ilW(eLxMJH)4GpX$%gI$mk}uH{AZla^0SztwVabzRF#`G;Dbetg5{h3E4=FI2CEa^{?J=A3fooO0%za^{?J=A3e_+Xr(dUZj06XU-{S&M9ZkDQC_pXU-{S&Uw!2oUdksdwKNC=cR8q!#!tQ^_+3lbH-KA8CN}LT=krB)pNcN^&EMH_Mx6Lu6oY6>N(@8=ZveKGp>5hIOSh=PRu|3pd9cIYoYu(r~Emm{5hxmIj8(Nr~Emm{Ok6?{E3V5S}1?cDSyr>f6gg?&MAM+DSyr>|GIO^{O!;yHRF7ltww~9YJpcO>(o3^63Rucf1(yg|LTddhX4DCIsj+r0c{5jfzE-Bqo2jO4YXg#CpYkYI43}ppkwG~aNY{q3u;B*gYzJ00yKbr8s`>JH>eqXH_rW_agd2VhVvHCE>IKtPMrHdNzhUBQ#dz*<n=V5cj0^lGzvP5Zs8mQb%LVk9XKBXjrdm__%P1$D%<h;rSHJm0G$N&qMyLoPDP^e*q=UYey@Vxk=l<O{>yOHYJd3>_EN>OQ;q%?Q561egKx@o#V@lTT6q'

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
