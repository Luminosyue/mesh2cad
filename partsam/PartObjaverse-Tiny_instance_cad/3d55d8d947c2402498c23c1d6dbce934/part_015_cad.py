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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_015.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_015.stl', 'source_sha256': '0ea53e400e457b148ac4c3083c5ad7a7bbd4844ac8d5e9f24bf6f9d668fbd53f', 'input_faces': 120, 'input_vertices': 100, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03615117818117142, -0.46280404925346375, -0.31060123443603516], [0.14846761524677277, -0.19542810320854187, 0.27054762840270996]]}
GEOMETRY_BASE85 = 'c$}qJZERCj7(V-;Y-Jk*=fHyX@*&-3t)-iD;H0IFicV(5fr7$XMi(#!utSms%o;U*#6&~jhx%g>(C}A{38=|vVl*Kdl@Mf^nqXp#KmDUIQ4`O5dCuj%?>#0)@ABsP=+ig%p1!^JtogyZ`Zjg#Sf*Zl>#KpQjY?59sWx?}R6e+Ov^1XBcVMDMwYokX29FJG*_7W_qYkOVvE8Nd(Q<696YC%Ai^ZMT*#7dta&h0t{_^e;`MKg#<0b8n?<pQAY2C3pnT$K#opI+`=RY1{eF~X9&z(9?r}X*{-x8`HuU<ND@hj_keST%`#H=lEe3Mrn%{$?~eq`jLtIy;wrkP*8P<O%ScTK<K`b$3hhWD4g*B^f2*pAD#yz#yK{NxMnbseAj-j^4?%vYLvzq93yFZ0z8R?OP+#+Ug*{Nov0-uPbr$d|9CEuWY4WnO+>()aRH>NWDK&h!5B5x&e9-iTbW<umYQ{$!@%vMq0Xna`X%amm^rzL)R*<EV9ggfH`f^%1_8|6=lV+BToUm-)ba3g64uKlygrHlM<m`M`V%U*-ezDSVj^%%||Z{HL$HV_hHN%Y0ycgm3bdpPSFP*Y#$%@BF1N^Ui|LXKZ=nn|yWA;dgEGFMXMp^KX1P|HhZ|FMXMp^Dlib|Mi;pZ1XRDnV0h~eJ{T%`@ZW>{o?O0e3^IJU!Jw)jW6?s>1SqadE?8x>TSMa%NyUDhlQPI-E|YsBjd~GQRSz}v$lDbzSkeVoM-8K&(q)6pR>)g^krVov-G|5`8D^U_4^`xnGbwlgzv3?*I(1tc@VzL2j)TeG9Q=+;mdqr9)xf5C;wER*w#n-GB4Lh`ffh&+a3NkxxDIxbVOI9-W`q=+18LuIt<#khI@Pd-PSPmzqf{S^f}b)8U#K7PM5P#S1nM1E9e^F4UD%z6W+*pEi_>r;|f}#2l2SBE?up_7VsA6`M}#4k3$pQ&Uh;{;R426pj*&`ct+Pc`dolf@F?^xz%=6-Xu|c3JJ60h4%c}UI*J~|J9Mp5^l!v941<TE=K*7kcR&+%GTsDD*vxnsI*cB~H|xsl>H(&}Q_$VOhZ)}tP521oJ<x=AGM<7?p$GAux}MOr5tswdLEi`5!T3&S!V$(dLKEK4cn&&;9>jO)D(Kn@90nhT-U2K#z6+Xgl<}?5gpV>l3_Xk<#JB5uOxFM~3!a6(7r2e_?a+jeGd=)KxPkF3bQV2`uhg|%R|7Bv9)g|=T*3HCXu?|=Z-6FjWIO~NLJ#8oy4LDi3XFh9pqBveX1pJo@E*pOLKEK1cmz6v9>j-qJ*X=QOn@h#?*MLMd<dHGA;y!?gsT}(Kqt_Hc%QCbU5kP3;O)?hfOj$82Tiz!@x{=DH-YB|Yiir-{^_TO>qmudpuQg><U9S3CH~H+zA<<Ysr=v^_t8|V|DM)3L3d2`H^~sfhX'

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
