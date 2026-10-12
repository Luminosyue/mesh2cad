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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/71daf747a9b54b9299cc495533141eb5/part_005.stl', 'relative_path': '71daf747a9b54b9299cc495533141eb5/part_005.stl', 'source_sha256': 'd65d574d70ffe15125ce02958571104a6eb6a31394b0565c5197af242a0e582f', 'input_faces': 28, 'input_vertices': 29, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.16648396849632263, -0.17234334349632263, -0.4137313961982727], [0.18274188041687012, -0.1562224179506302, -0.3808959126472473]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;2?_w|9ZEtnY?K$wR?grO|8s3bEvwOB8&ppub604xpyFnY3IsBb_dBSRTOwR%cwadMHmm4doWnuWTKf_hqhQAtr^UVMI0N-9X)EitD!6)0Yukywxl<ZBpN>L?g%>L}DIkPEngPB;+Zf7BjGJ5;hA-4CKCSKZo=B(4AxpP6t2L^C)SgT)&(yN*KCC8CHcoNPLRYz|DE0VWPL$D!j2#GJg>DCWS#8Cn#<>K|OLyoD_Opji>coC6IHAnF$%M6tIa?;lq8Cp_am238+ujAAcLJYmXB6!R65gu&tm4)&p#pKwVBEUw@cf@%&_++oEI6mt@`M?%br;6H|<9xDF8Dd8wK@dfMGU^Qof#Q(!6;VIpL)jcqAboV&0uf!S-Fma4<VAy&LTX;TrcJCOrc!Y^##Fw_iact=aCXSv?7{pSJW7r#jlIs+kxK>?YWMBYcPGGJ}OGL_YAVCm-(b%(GrU`Lb&Vm|QjscYWIiMKC=7C}mn+=LVY<4Kk0%fy9*?dq8Vsk@jMkt#b%I1V(5St51GeOy0P&O}=W`(kOp=<#t%@1XRXbC7=0Lm7I(o#^iFqAC{rDdROQ7Bs+ia~5KC@l?Ti$U2UP+Aho7J;$_p|lW`%?G7H;Su1?$Rxsys|ZGb25|f%7s%*3QIip}&N84`@I)2h%?gSiV8Agk6awi+P)IQV00ekSc>'

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
