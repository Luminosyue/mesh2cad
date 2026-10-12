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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_009.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_009.stl', 'source_sha256': '99fe9d7fa606162305aa5f71e874269e0650310d5ee9310667994d030eb8a826', 'input_faces': 32, 'input_vertices': 44, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3702528476715088, 0.15610411763191223, 0.12844277918338776], [0.3912428617477417, 0.17207351326942444, 0.3076755702495575]]}
GEOMETRY_BASE85 = 'c$}q`PiPZC6vih>Q#H1>+8C{ElWlCWX^e_Z2vL;gB-mixgC0CdY&O^+O-xFys8EmMNksHu!Gk9cDjoz6#Vr~SUbM8JwNZOe{Da`dp0w!9&YNxCu!88o$NToTZ@+!XF0)$3)!-$3b(7TROyOn&AxurgOUCr_=<twU*)dW&;~=djXG_#8gGUZ(M;&C0oK<srWvHy~QPjQplp0gie6c)Q&W;=_mUBAe`?Du2I^~rU*^*9=BZ)*ziTB2o^UA+251V24{g?f;80Vr@Ru{kDo9(aT=?jfd>-oga2fRPN@C5P5L*73gtJ-oYhjcvRJo*mj_@+63a~bnr&-i_(Co%st$9dr};$-19&q)<<|Kt+yuLW`crDe|VBu%coC>eHqaq1)D>AOjszpLk!$-CV+e|wnoFP%7F;#NLzLvWFEE6e*+KOWoipI)3VaVsCVA-I^o>jv-t;72(!7de6(f{UD~D(}CY!Z{MR<~jYI^MT`deu>NdhT!79xv#u`d=UR{+7jopS8=|?t$g5y;39wDGUo?o@b8ki_5T1*56s}4B$+q)w~KhrKBvizYyK*lQ{vW~z|+_LRok3e(LM*bHD|!Xa}GUUnMXsrTT^X5M4Z%8t)aVHK3li7nI{Obs{PhBocOD)E#CLvTiaT~wqQb9ptgc<0pAAI3%(7!59%iHKJe{Ow}5X4-vMI26FjQ{s0#Q1_#o7+;Dg}9P*w0@@Vy}Bqg30ddZ;2)A*wF((Qp<5?+4C~H&bn(+DNq?{5q;;s?~%&NX`Xg)dQZLYouBQz0GjWMdgOa&AfvOzGx<AuYi_uIK8eveHvHR1iKi0DCH~hYgd2eTbgCPgj&YUW~E(Da*915HZ}PT5EsI4'

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
