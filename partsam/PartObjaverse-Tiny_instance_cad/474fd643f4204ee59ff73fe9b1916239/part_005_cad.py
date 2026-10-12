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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/474fd643f4204ee59ff73fe9b1916239/part_005.stl', 'relative_path': '474fd643f4204ee59ff73fe9b1916239/part_005.stl', 'source_sha256': '7b24145c94549377247d1fbda08a5c726cb7d22fbb079d212d894bc64a9ab73c', 'input_faces': 120, 'input_vertices': 118, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07517566531896591, -0.20012737810611725, -0.4645098149776459], [0.08694124221801758, 0.1214320957660675, 0.11685216426849365]]}
GEOMETRY_BASE85 = 'c$}q}4Nw)=7035MKoLJsi3P=Eqd}seBBCKEurG>$XaYoPOhxtyJR!jk9-t+)W}T*ujUVA73e`lOP$-BJV@fijz$R%xrjDf_bR13erES`on#{D?Cb4Nu?mg#E`&?gVI_+c5{QvuVXV0F!Z};9iWM%r_6RPm%0ma`oe6~7RQDlr&LY3`Bu8NX^qVjoLwpH1b5aRMPqIHkuuFhI#Q?@JLi7G5AFK|UAs!>aw2~ja>lyj@A!sXbKztvS(B>4(QX?c<0<;9L|MdJ9O1q%{l)P=KS)bFbQ<7bR$L4Py(jXt5;ubbbKs^}-qr3mr#be)#R>T$=<i2o(qA-Or~+UxSzh`UDI`0GB(*Wx>f>y=GZ$5=J(P05Xl7f;doMjqEc)k$^K+mngw_1XQDzxE*4nIAx0ODP$ke8+GP@pA*O(eX=bxsH14nB>Z}4CY}rs-ujVOV?G}7ZTT+yO^6BHh6P=;%9tcZ5t?G8~&<O9-G%c;rbzOQ=f+I0&%6Yk?REhnfftz{_!OBeRP296lF9~zP*FEdr3a`pVrhxd}tl#@9*LIMkwVgB{|IR^>F=LZ@Ve~@G|0xbBM>MWG~fG@<$Ulk8J1sn?I*~^W1wUC@*Iwb9YW2-Pe~t?x5q~54oQ&T6sJN4iMLty3b>LmeKh)pCYcd7IVIPVh-h}T|6$2J>9Pk5<f7j$D6AGHJl$&Lw%aVJBgbW$;^Y#@O?EpIe*`4%#|f{UBxehxRH=e{TQWA9_LI~JJs3T%YEuM8tJ;f{i2P3k2!<<9DejuzTYO|=GC2?KNw5>Xorpv*UyY+-WbOHyt9exymgVeQo5MNC33KpH0T=h#IKH0eoaLSjl=#M+~@L-`MSHV9^>a`96$HF4qWc@;>K_!adXYfSLpb~v$ekRjk@P+NMok-QQgKi=BZuPlwTR%E4lmgXD`w5(bdc&)47jd+;_#B8-09T&!#%&pZ}vI#aBM~UHPuEr&E0Nqr5bwlInzYALIMq{Q>cLZ&eZR&Zg&Ey^u;=ch=Psf2X09@&j(XPve;UG4r;xI;r{#-ITAUFQ#K<rJeGX8kOsu|CD(`W;ONM-bCDV4;>_4)%g<|=js6B#z(n_sQ;DwPt&;lAe^piey^Okl3qah+U85#PfsW3f0{=5YSNc94qEh;L%zmsgj>hW{N<zdDL#HLk2<Nr*LdnvGJcfe<9RSI?Pw-Gp^5s@{&e<=H#ahl6IVQwsDI;w=`D0T@FexA9KOiEV`^lJ&)<E7Tdq68t@owPXlbKk%k!@{Olzk)d%w@~Lwy9jzed+B;@0=bozu`k`Ih%ipLK!wUGM4NFB7-E*Sa(21l6(31M2eQ#MLyD^8<O_aMxCyq<WTlMvtv0uGM2+(j0dB-g%O^bsqC12X<2Zex45v`<xzc?zvh^`9=WGhwAlO&bQ2~p5A`qcg@55hlyL~Z9Q5&Mg3QPo9Fp{p8wUsB;wZfLXS=5e9QXcex;1Kb)7QPZ*v{%dKVY=I;mxS)Q1)kx30799j_91hdsmNu#(qtv$l=6b-mVBoFJ~2J;B`0`vK4SUgFku&GY*~=9cwTvyXm*`m(I=`ufSlwLk1Ii8o*3{mRZ|#LcraxK7rYYHzNT{i=_i`?;x<@0p)Q+%R~bqbT?DynZ{ExMyw<U$@k@hu+h02Vb`}p7ZU+he&r96L+^`|8OCT`u9A(gZoM1{gu*EP2*rbQp0r;!{6m`%cJ$f_~d2g@9yUOnM1FTw)QYTjQ!FJ3hy^Men(tA5X^O4aSe2TaZ~xdY2L--V}$VjFCw0~Wglq#W<7CpT|U?Mblky>?DzZlJ*uK{(@tOJdB?KP)Q%4DbDBJj`SZiPp6&UN*X`toncpluNaH!?Z^S*}d$^zO{v%Ys_cMNepL>w`KNtRx^yFfGzOFCl`(2$x_p6+@^FHxR4)a}0YWuS8*v)4rDTQjFxOEXhVmI$}cx~k+l%Emxy_GMC|L?Z)ak2mJR(^))VLG+V8Ug<Ryb8S+{u?5uAy?{s@KW!GpAH`ZoeDn{b)*jxF-1fOG#owzempb`UTP@3)IfNtW8s5velSA%Nzn1|li(*p$HLo0+#_NXbTYiu3Gk!f{h_1br3SzU;4$!r`oY_9{y3;V{5beAP(S$9BGN^yL`a{8kbVU;1AYa3CPMlw)LDjHsgJ@-T@IfPp8-vU&w!V8o)oc0#N!C*S3z^(SHVAqkUkqB{W{cHi}R%Bz^{SNg+2i<^_%dy@UqTk5hWtlBc#uRZiLT+e+nV}w-C~AMV(TdC$$K^1b!oQ1H4ox{6=_L$01^ih<t?f&mdf0T>4^Y8GJE(A<nDtI=2G3QY+zI@MQ?;w;`l2M;!;wllnA#1$-rR6MQ9nIkW)240Q_;((CxH!0WmN;PXW+5HSxS{ag`?MLaAb9-06jD`KIDIE3_zph@tH;Fm&^;g`avK<)4;@ESA$UV~pE;t^;fGy(o05wk_iL7#K*T>^YGbT)h<zKelI!$%`01|j_{5mC@c#4LOl37rXj5I!r@<`?S!pZ-<!?~frTm^=P)WIglFWy$-@i=x)Q7OAYv09u;-#Gm}}XUiE=`5JPu7Ha'

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
