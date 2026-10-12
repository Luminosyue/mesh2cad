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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_002.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_002.stl', 'source_sha256': '036a9456d04ce6a24746681ae3ee357f58aa9f87298e928f3a2163df21e9a073', 'input_faces': 36, 'input_vertices': 34, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1078837662935257, 0.15129266679286957, -0.04544106125831604], [0.11760766804218292, 0.19511090219020844, 0.028338909149169922]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;1X*RCa{8<-gwK$wR?grO|8s3bEvwOB8&ppub604xpyFnY3IsBb_dBSRTOwR%cwadMHmm4doWnuWTKf_hqhQAtr^UVMI0N-9X)EitD!6)0Yukywxl<ZBq4=qMO#>L}DIkPEngPH=FYx7!{_Kj@1+45AOHOU>JlMcg5WeG;<xf?aY)z~XWCOR$L_i0iIH7FY1iJ_<IE$7MM-afY?iBT?*K_WBrDoEKF+O#HwGRP_qxRwuyrqqzqro{)&@o(CyEA?h{I{0kLV$c6Yfq1#|DSRK<{NH`pjpKOmsoZ$h>T(Eqn^ggWNi6#yYPpCM|oC8U}=U@|Oa2A`4RUFM;jCes4hsO&{Jh%oduJH53B5dLbj`FR@;u!IWCJv8Bn19uKA>t_^WhmmOPeS4mT^v2$(Zu2L4iley=Q!A%PH65#PY-C~@bmyP2R%KYiG$Na07`C;+Q?mGz{J1+!koa|o|cG|)j@(F0Hd*I^-L4uvbq_?SzQ?D22mj9gVF*}HXoGD52Xd6Y<?(P1WJoR*&<N31eBJ9vL&Ew87M6UWy?U>@=#h9%9aHOA%x8V#GtZB4vIl+1t`r8WphK-!`Pfqz9N(@52e|mY<8&KFg7cadsw0F1<}k<HZ#<3Fg7ESe;J|S!3d3dSoknN!w&?QpllE=jKpSv@`a&naVX6OWrJvGD4Q3Eg&06p2LnTZHzSh>Gp?!y0UE%LLau1gb)qIyWS#GTX2BC}fHx}}#3M`$g+MwI%mV-m98P}'

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
