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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_003.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_003.stl', 'source_sha256': '9b67d9f598ba095cda2cb6e0e37699af5bd393ddf59cc7e1e61245dd9322846b', 'input_faces': 84, 'input_vertices': 92, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.10236792266368866, -0.006956279277801514, 0.3556617498397827], [0.18673676252365112, 0.04860645532608032, 0.48045021295547485]]}
GEOMETRY_BASE85 = 'c$}q|dr(wW9LFz$A}R@pl#k+y;EEC;k6O@VRYVgXOW+fWMOlP2z{NoGF;^!|BMr5tnrX(>P<!}CWz(bu+!cH@W9AH2_{bPFXKJ#snwn-Dr_TBPzW2I&*=Cx$Gr#$Mf1h*qch0?g&e^-p!qBi-g|AUcOh?>yH9}Ej3{qm12DfKT^>TN8YE9j`5G9JZybRqtcm5pb;t-`lS#PUw*Dv?ja#h=;O1mvZwN=)7)_BTm%4$6oZpjPESJk@(udgbvbBlazPDYBFnVh0-RR8NWKukeDlXW~#&ZYB>x^^Ls58JQG+~K<PDRI3gUvg#IF5-Ge(PzZ_rD>EGL=#tw&b1Ps>)cA8|LWGaQnk1{%tuz%%Q{}Qnfhy2XSEam<jZo&^{%DFd){hfe(n5b%8SQc3g9=GD<#3XzP{!PkH3ZaPX{*m*D?8R=0+VW?^S0u-&e0XxZhrNz>PY3RSWYo-#zPJ$K+?38+EL_SDk*ZY!9f@(#?GBzS^K%V{X>BaI?O_Zyak1sM9f6C%*mrilDrixmn-B&H4s+RqgVxqpeI}u08o0<#*GlzxG}(b4Sdgfc^$|GB?Jxa${VRx6W(!uj7q)hPj%YACx<o8}+T+sBiKk>Tdr!>h%50mERJBa*erB-^z{pCckqipuTJCG3IR_y-xiuPoVxi6E9-iKX11A^}ok&6F2vfg&X6VT<;1P*P9XT3wB>7x6IR9IKvn8IUC&a++3L+<}Js(#4qmS=X18v7i>M4-17bQ96jI*wr)*sS%==2bmlm(^gY+<9CIX{@&(&pCb#StuX@cFY`>e_vVWDxUzl6YE0bH!AN}AT%q{1n$rmozPg>*SeX%g(1m!qydrDgAzI5-9PHG=B_z*q!<j!t-p6NxMJnn@?*<a27nfFooQs&)19He~Ez>75g(zVQ&g>Iv|d*1I3;3rCV`g8B^8<}rv+Y!LqcQJRiR?Bg<H!st;%4YjX()3LmBzN^)LEKf~W`1S%YMSTEWz1_MPVxHjJ}0?S@%d%ScaCQM>$SIOejkkchQ@z7iMg_%mYz@KIqqLMg?ZHu>hCJtP5reae-YRA<s2qW?)aMOB!r)){KakbJiXrWTz^9BX{?78w62moybceKVD4z1O!s@MnZNg@Wy~+QTc}Q07u8py8ks9cOK6^T*Xj8y@y|2I@3p?|R3O)?ifO#+NZv0s?=W98u#R-VFzT;v{Fr(7%)O*9oTT}y_T$XM&(nU?B3BacY3g8ZFIz|YMKRUUre0@mybo+xMc=P>_a^hy23r5FvZH~#IQv!V|88P;o-^R>D&_8v)pcQtA|pb)T~(I*y;?~qFGGXBT2*KLt5+*~*8hIBnj>#rM3IPDB4&%21Dy*$6}fDmjNE~k3O)gCl8q2C7HllI^r6UQdmrS|hrmnL7rAkTfQO+?UXO^#1Iq)Kz5uywpMqTanedVoBA<bn3H~_RB%3F~3FZWsz67~!e*(Gm#qg3Xf|qPQa_JX~SOT^LT>4VvvV9@)1&C7cND<*8?n6l5A36ZOKm0&Ml!$1sC_fep9t}Sf`T+b;_+iio;fKLLgcv0v0c?~XO9D@T9|Ii+FLgZpV<IMsm;}v%p9G%^eH1<y-VV)zx5H;cGvKq~Gofklnege*hvC!VQ=!T5sqiTX>21(Nc&RG94SqC2`grI__;~o?(EH(~4uKyI9|s)_9|s=;jew7VAB2#;pNQ!qrisWG;Vca46C3(Ze+BPd8f`-VKZe#%1|D<%pL|NB=Aq{->?`LWHgO+iwVae(!OGty*!gk'

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
