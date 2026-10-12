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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ff841231d7d4c54ac917e63c678c9fc/part_004.stl', 'relative_path': '4ff841231d7d4c54ac917e63c678c9fc/part_004.stl', 'source_sha256': 'ac9196e4f4163ddc0075dc92ea912a12b316055aa0a1ae4954869838e46b8747', 'input_faces': 32, 'input_vertices': 34, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18152856826782227, -0.18760675191879272, 0.03203825280070305], [0.0005353465676307678, 0.23179882764816284, 0.15407425165176392]]}
GEOMETRY_BASE85 = 'c$}?OYe-Z<7@ghqk*21#KC;@q5x5D9P-`zM+z67|9$RgtrPQ`vv!}Z2N-y<V5S0=1FhdGAP%|pn%F154x@AH{4+xZkqz7n54}X;YiS9k~RT>2m4Giae=YBJD=9?L=)uIW|GTz3r-A8m*uZA(DhcPWH6rBYd9HJ{}Yu<Jhi-fMU?|5|KvIW)*6)R*r4eLag!)Ztn3^TH)8jOM=JJ(s@v~OLV>s%))`W*XamniG59DAN9$Ky@OM!}S56pDm@ZJ~+>+l+fnGDszwHU-&(`z@(5_?m5Z5tmK8si1Gs$Yw=1FYmvD{7mVA60cdj-h=$!r_kAoyZ4n?D5|SgkiD$p`6J%7DzS7yeG&Qu8_)ObY{Gc=yaok3)1$Z^@$oqD<ikdMfA_(Uc%%M2=1DZ&0@kl@!TkO#_%tVoe(2$~&Cr)rkWT|2SA3A`=63j$o<(}GuSpKBPw#_I7PRUr_L05{I`dAiP|y=yi8`?U$z0#E7yenh@iyi;tmXPiE!Ja)vV7QAz90Uiq+0l4<7Qui-gAcQIj`Zz*P2idOnZG9digozOI{H=%jo2~y9@c|eKX<HTw7HKJ>nIgr=jl(@@?Dd2Cgf0>oAXJPf-omi~0KX4XE3iX{KuU|NI2|WpQczKG<75h>acRuwM9DUWXyODxp8l<8_F6$}vBMkKgf$pS!-~I`nO^I9I9T39tX@(#z17I?JI~9pm+hJHhXXcN}z<d7Ib&xdruP*XEW%?`wk}>1!|U2}`JPL+{Fh5A&wCH=%c(T8a64Uhwm6OXKws-b{hM{|5Yc=6|^W{n3G0{QTVT(>b&IY^rt8Ywu}vlrptU<sKrx_H6rrr;ZPd{lMQp^$p2?_tYo;m#02N?kd7C;ws`ngb~DphzApf6AvaHNH~;uAn^dgP~ri^HPl0?Bx>RzgptHUhz}ziPJ9^gD8doMqljw><B4mDkHS%L6bR#qD>#z4KwM84M_f-_M;J?7M|=!n4Dm6<M-xU9w^~$ct>#a^il0qV4rI`e<JXacuie0r@8!9ETtcfQP&q?6OU?3SOhohz_O@LB'

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
