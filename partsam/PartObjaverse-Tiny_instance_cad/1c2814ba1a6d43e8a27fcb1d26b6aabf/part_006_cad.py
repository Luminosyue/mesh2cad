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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1c2814ba1a6d43e8a27fcb1d26b6aabf/part_006.stl', 'relative_path': '1c2814ba1a6d43e8a27fcb1d26b6aabf/part_006.stl', 'source_sha256': 'bc0caa97d02c8db89cb26c0abc2568fa3ed0358ed4fdc9d60ba50d1f0b369f0f', 'input_faces': 72, 'input_vertices': 52, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4475407600402832, -0.49999988079071045, -0.40404531359672546], [0.4457671642303467, 0.10957978665828705, 0.36559054255485535]]}
GEOMETRY_BASE85 = 'c$}q{T}V@57{}kaEnQCM$ISUr9>1EpwM>h`A_swxQml(bLZwS54MS}cDJoh)bk{{n(2Xpxx(TGZ5{#`6vMy|HvLsa6Wdz=I7hTx<p8em`drk|Y4m|w-&+k0v*?Zoz^K70Ty}?Q{M=d!W?O5+O62ihvtYpF;91jfmL#~mr%Q{jdb9Qi@JnlW_>D7@5a>YLA4-EwE9g_Xf&;h$svJZ_0$Ai9+zR}>IpYbl=g^-`}(0SjOpXN>b+MH5*vs1bz{p+!nt>Na(T9it7bMrIPbb9quGz*ueUoCfvJh7U}S`W_aV_xsFoa@(TSsn?TNiubRwJ&Gt=by{xpMFV*oH$mVbqc)SKbK%UcJQ^#$^BDF6(25`7kO;MvZU%Cc(5pPr9bDr_u^uGByx2rD^CrlL>_C&^wHKU9QEN#Q>s2vUzdt2>j6)9--(O+mQMLsM6TTjg=_Y~{cvMZwf@K0XK-bm;QiMJ->d4+xsoF1>*U=1<i&zm?>?E?PtJLNg&%EG)yKS<`{kV1a~`|vP}M8@tmXW<fdBSfv>f%s+Psi$pE=j=v%)p|EOp;_ldWFi+UMfQd8zt7^tx1>uT$YWW~1Ud!&MQPN4gKc>lB|0o@4CD$On=0{f|8QuHq5wGx;_dm-8QIKgypUjwiD6nYpCMW4Byyv(+mc_38LjQv6(gUnF#UO}-!P{Lye_{&23HKN>FAdsNdoe!}EP>**ylOmsRA`GnETAUn8bAI*Wie>Ix-|Nm%q&^0(|?1H-B+iA4X&_i?Jb-2wv&{lXIR1a+zd@J%+^x~c%C+N?;4!I6Jm@lWnen*O+Ti`7;*st6+s0rQzErON{-h|wQUfdgz8_}P83vvs3FkeGs2aQ5#0lb+;K8@|rYIrlW5LzSnYUI`E#eF{VeDvqujNFVK%$L!qqEP|e32&p(NW%)PgttK}pk;!uL|%zr+&3a`M1SsW$ZhDsd_7^W0wE31I(Rz`3Fjr8V?LKg2@M0Z7~TM%2Q7t{(6bm?3SW%tC1@>t1M2Kh3BDF}b<k4yJosE_34Fb99|qJh-bAB?Ml*Cbyr)N(W7YrZuiLL9EWcRdA35!n>aikTIZb;hL&no%WZzHv(&UhfROjT{pJWpuPX'

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
