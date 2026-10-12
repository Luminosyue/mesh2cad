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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_011.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_011.stl', 'source_sha256': '4fc84686b6c7c0722ffe625f6478731d1e53dec00124694579586f0e807418a0', 'input_faces': 132, 'input_vertices': 114, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2008998990058899, -0.3132894039154053, -0.28940850496292114], [0.0004383176565170288, -0.15520310401916504, 0.084695965051651]]}
GEOMETRY_BASE85 = 'c$}q}Yitx%6vuCALEA!k)mq+zZCxm}wzL#1E1l(0D1~;FM?t}EE!)y9ZcE!>3NcPpLJZObP5gwqA$}-nVu%4BXyO)0fD-9~f`Ldv6l2r`O#HwHA9(J)|GUoIy(UJ7{B!>MJLldxb9Q!jXs|v#BbUizE=wQ1aJ4L(F|P3}m+cAn^mVj`drPC;{b_8H;QUbWjfPF@gIm+s9=6Z7Bi!5C<EyrO{<bB)63f@t)zjD05^e74*%9Wvwq;jun0W8bmhLdUo>yL8Sz=YpFR@;*{^OBFEjW1}p8t%ZJv-xqh%<8rYYd#dU3SdG?fPpcJUr{S5gy~cKYO@y{oGlxkG8+!@wc@7KRPS8Q}@mxH)o1#``gF&nd=qT>SKrY8v9XP?<cf$^%=3x8t?v=;@bZ4x*Ex6c=uP_*7lEqGtATW56JyL2#Yy8-yc2b<_w&@o;hgb^A;U5a<<^4o5ybzNS@e#z|9?S=jeN$dh3t#a&DvE`kTK?ZtL}({pR{ezp*~{@*Fvbi{APWxL$9+f8%pe|DAU}7Px)bJD()?Y4ZV(-zygT$E$CjGtFOdef}vN^H1TJzvBA*71!sV>_?lw;`;oP_1gTC_1gRu*XOUeK7Yma`6sVeo2TX9AYMC}T?vst!bDWu9xHih!LJwHJTxvbD(Yk2diLk2;IRr>?{pPOerNnwB98bIZti?4dB~q5)>*TeJnt3B?V<gb-8^<wa_8RYB~Sg`d{JjFDo(h0yj}9pgi5i0X!^C&V*L%toxI-5Zq6DckN@zk*grONui#eTsyyGjw?^IE`TC0FM<&U6^tB5f>OcI2h<6emZWT!$yIm-_bL{%Csei@w{;i)*51aN^T;Jc?a&p)-f5lVguedg!<UZPbLV@GMruitY&&Sy~Fl>5%71!Ti_RBY)nD$pZW&YJC1dlyGBInSY@Nm08@=&v!4?7q=WvmBJslT%7l(8Rhy`T7(+lNf`il_8nK2>nmyjXmGZr)9Jcsxt;&|TS2{PKZ8Q@!GPz0+1TXzEAtlzwi$Ibgbf6xZ(`HWGNv^!_HfcAqP*-{)-L(yONXP;vb}WDU758Q&N1l<PY4qhtJ>g6p3nwl2HR*gtqm|AU*N#<_u~%q{jx#MlpbN<ZD#!^Z0cPr2Us$Nn0Y`aQ3>{ynd_{ynd_=X*ZrdD<T8Jp1DDarA^o%A}|5wief;Hi!IB(fp|0QTgv4wJR3>-$(6P)WZzM|69P=MA976Y$yk85@`ZyCS-x#N6IHnhcdy^Nn=R4P#zdRrjVvWX<)pEN6-h43*h;=N^m|NOX25|CX<Q~AAslQD#ZDCd>EeRA4E+NybtG@k8{m{pN8mz_o03o&RvQb&4E|5D#dk_;u>b5|LN$x1il!3%|mZ_@cD?v@WrUl$8}A`H5I}aU=9yq29x2ZAQr$EpneM88~z@RMa+gzLsSR%8Hm~N_mlW7n}wJGpMe_ga}XyYX2U;A+Ckcd7=dpkg^>><$Nh7pPUJh0YsH!f@)6`zZ3J}@?8E(|q;gUevD@Vr;x&)E;mfe53o#1c1-~1y8@?QM3lYoUH;^`wwjwscZzOF-elv31KSkPt{1)UkVoekBO~|R*Ce$@yAMWc(>q$=_Ho~tXH6Y)B9QRL>g2)GvTZc7`$TuRVY8z44h<&(!hV(S48F3qY8)+x<JCWnQoz#JR2Xbv#vkm!e$hBilv#X{Zektj3(rUy2yq~lT`DMs)zlO9N`Q^y@u_l0g06A3~KwSX)aKD&TL0W=X3D18QRv^CuIqq%JO5|4}SA#W`$X6m~W6cs*jSc@8X%VR!u?l__sSf!%<hZXTtwnw<a;vbW3i&GJYO$u;RZ|NeB5fzNkb?DTV{+5~=}$|4ACCBPcmJVDU+MjsbgzukUdbQLVEtI}Q#pqI@ekcr{!PaI0_kH`(*'

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
