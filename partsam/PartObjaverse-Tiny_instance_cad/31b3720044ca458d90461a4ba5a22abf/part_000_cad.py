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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/31b3720044ca458d90461a4ba5a22abf/part_000.stl', 'relative_path': '31b3720044ca458d90461a4ba5a22abf/part_000.stl', 'source_sha256': '3c1e3f7e5ddd0da0fd2efe4588e4613065efa548c17c5fa004421043398749d5', 'input_faces': 44, 'input_vertices': 37, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.014853149652481079, 0.1754118949174881, -0.1189856231212616], [0.14322614669799805, 0.3375561237335205, 0.11607562005519867]]}
GEOMETRY_BASE85 = 'c$}q`&1=(O9LJv|t$kUyb!+ULoim+-C=@TNFUX*JQM4#IY>0T!vZXkbwM(|)3qmftisDH@*l8dh6g-FrUGbpcK^QW<dhrkNwv+C8;`fQo&qok_%ERZ=FUglAee%?)8wr#B9A$R8v~gm~U`)&$Gug81EzZrj{=xb74UOf)Tnx$k=cdm(7c{oaZrQW0KjYcQEPJwf)UH@|v*j&%jrmJ0Z`Kw0$;LI`<+*>Q(RTUw{S!wj*2IB|b=&&akrmf4b@k3V$MFX%A8MSz=cU){iu}vdPv=#6r~Kkott$_{-P=(0$ei}bJnBiGIuoA%<Kp{R56Pn*lG7e`eeI*FN9MFg=26e(=Z^$ezu$Zp>mhm6Lvq>^Y!x?EJu;^~GM7E8h1Ro>U;Ve;Jv5g+G^agm<>98PN9MFg=CUU^)PAXY4m797)8{~Q+C!g1r#975tp}RZ<LU2C^XT`QoPJYNt$&i!<9}P{BoB{wV!OuUr6;MoI%8sH_^#1xbZr?T6hl(IWz1FoYRjlr|9i_Q@N4Mha}ZN_4otyw@Ey2CK@Cj7bubO4;Awat*bDE2n_vNM!iT|K@L~8UxCcH89|OzqG59#R4?YgJz`bw_J_45DBk&=x2p@tEfO+@;ya&v}d*Deh0Z+np%mkjF2A4y)0cPO_JOk$88F)Wfg!jXDf+e`%Zn#s|bkq3LU*NA1hzpGUA<{GBuR-^jhxtuJFNIT2hU-e_p9OK_VwJFMJNAHf'

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
