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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_003.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_003.stl', 'source_sha256': '343dee14f88cc05b64f1d62f872df792da16851411a39a6d5fecaa8d4240d54e', 'input_faces': 218, 'input_vertices': 195, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.296700119972229, 0.11863160133361816, -0.16375896334648132], [-0.11372581869363785, 0.43457549810409546, 0.1632055938243866]]}
GEOMETRY_BASE85 = 'c$}q~3s{c#8^?d0NRu2g!<t7}I!vS{L=Top4moXOS#OdvSvfcMpyo6gHiwGdgruBFNxe@g5i@4(WaBlP*^K6Y8JjVCp8NjV|6P0j*Y&^t|JQY2-_QH?b3gZU{|?VnA|o6e-35QziVFib9zWGo2t67KcQGd}Vb<i>xWrB~X3n=0jmg(PPjvl|QG+8#+le_M$!mOEVr+s}56LTJLa>*g<TW8aVOB!SjOh4;@o~D}KW18DoaQG^ikTUweec+%dyt>h)!R>6DE*Hg7p(-v^U=o^UC(zrAF8P}x_JP7cl;Om>T6LS>%M6f`_}Gjc>LEBKhb@0gnhYW9{D1?=ULsCg4maCR9~RKuRcO~q%x0vM!sq0XL~8%uyXR1Wl2<zdUZLCuj`xF_T5K1a0mHf&A1BsUKP-VzUNG3->!9y?#m~*9(6+;=Slj3>bHIuxyQ&iz3;Mz>JhPAXHX#L$sNjhQet>~(6W=E)DOO{Ji8D3xvA6#<!1a|Bj1|tP4_Dg3gG-}oGHJOCGWNv_#*N_E{*T*%l8%a#wp6<iunrr^gOA@xN_=Sv2{B2JExL-`QFo%M{SnQ{jcMT@{!a})1<xRi=|z8{KM<JEC#-mXWm8iwqRc!$G-W<H5zYyJCnypx2mMPjt<)>U;0L_(>|Q~CN3S@O5-}ffA<9WrkaQ8biX4~InQlxnqO&9To#QhUdi<z8qD<+Ipxu~BZ-{nbPw`P%YVwJdIqpBx9G|DYppf(O{uy0RA)>O=kawpP2<yQ^XNJ&+_|2R1Jr-@MiAvu8lL)y`VixBk>(}ySfP<`p1ZM-@+c?R7oYPwPj)M^82M2@(Rgc$O1@|uaDwufM(v<H`P<1?Mn==TD?f*tX}%`QJpSPCRHx}4uTS+%TlN=+@x0u2=l$EHAzwE+mitg1an#V?-0>*YrQA73dG<cE(0Au-h34yV4g2$4KBW45I#VD1@@ECJZ|}-|XcI`ja-}oPyR@|t_jCJ|4{5xkKd*-&yY|!lUHXds_ytwu-?!s^w6l`^1I{#Grsm(%eo;QiCttbb!|P{TecF#E$29gY#Fvq8%E+PnSe43oh79HX-gO<-{}10Kp6XY|O<_N23i|`DQs2a`$?U(%z8GOO^kttC>ZiCik^P->>AtMVQZ9WTJ&5aU@+HleXfuuWo#YZqzTEu$C91p3p~7P0t55vQJG@?g4dDF0T&6ylmfSnQ{q$h}jD0nYztW+AbU{<T?yue|eXnhsPS;!Cg!6An;q@?MD)%SHh4W-D=5;mwAe{qZ_NlX!r^_t9-)FurH1umvP(Q`mD)Qyg@TcA2{M9>o{LPJgU#|BmY<=+){F~S4{^ZhR9-q*j)`MI>yny->GM&duJ!!v)Lk@KQi^M79t8FsBB>!G%sjV+d@KZBNNyikNq5MsA`5bO`l<GH!rLliyH`j54_m?#AJ@Q50VCu6h-KBY#ts~jrIfmD{?;WbsY#PFTwH?i$y2f;fbYlejrxSR;e6zfW>RA@R*R{`6d7n0?=ZF;R#eQ&0sz<oDqx|yT2As#@OZ7{mvI=;85343MpQZff_Vo_ab-ntLulRpQ^DA%YN$1Qz{53yj()iAWrzy{X+vJ-gybsfLeGAA}!r!8OXRYG?nCu3#Kej~$@2kvXq+j=8e_ArtBNuc(PWg&n<owx|&*}S(ktG%zUxBYE0VULrUJp;v`2OGXd`;LydF0`rus`#oGM=yDRHt%LWq)1`&9}K%DV-;#`FZS{@@O8#We3V*YOtF9r9V?1C3aqh#lSb6x=GJ9Wz2B$mE>{U|AH&UG~V5l$4C2c|BLd-7Y<MJ_-ngpJy?IQq34Bq{Z1A6-2&;{Fxyw`Hu9yz3wP7~-76+vqz|BVqO|m*=cc;nAp7_G{mmEtndGZCYN?;rTe%gszWf9G(%FqXZ=DwL_{4+sypxZ9XtCJ%@+|h%)ZO&lkVZstoww#(pz(fzs>Q|^x7in)JgF{uVF>$^AM^Xtbw}E#PkaTwwd5+zySe!8N%Ecc^SL_FO8dR8FIuM2`<{|j%zo0cbM#&O!1X`z-(uhVc_r6BEQkHbAnJqK(XGs4<BMVN?>^$bI&bCi8#d5)tLs+UU*=3d_G2#4xn!<gO6O-?U(M>p=l|<ZasKUZ(E79{wx@YF71iVMZoklaGoQuz<M~G=`4iLlx~1%!dw;>c&tqPn8HeT@`I6t_x%BT`PO^Vs)*0%X(-!KpaIUQ6{bJ_(jJ-O~V&Kca?wv#9(=#}avnSv0s1?gC2EJ%Ba~WMXcpm3DTtIn5kY$<0z*isbc!zY=ME0YjX@8kL{-F2Xy1w<?QF`xHJH@fTyPU2oEtp<R{kR{^{-iK|zgi%zvl#f|%KEi*e{(x?{Z5VexqE#Vodb1!5%FvWU3Ww~_S3%N`?|1Xt;N8XgYLaYf8VtQU)R4Qoj)c&mCil+?qk}QO2$+^fA%}(8Tlf%l+FQl-DTd#8;)?E>e;lOO@$w^ALhpAVRv_a9#x;?JYglYUz8T#(!Mi|t>W=j7rCD^`tm%SR@rx{$9Y~JM(+=GeUV?0M%O)inElPJbndAY=cyhgWi9)kEvM&*HTo9s_h(jeJ<}xWr}Du2IMowo;_<g@cwJ?8%Qo_@qwdhpBhtb!_WLfSJd*EJIv?u#*00*r`5>RP<Lgd(jqmG=)!QrvzIoNllwVnQ`vlk7me0qF#W@xOUrm`!@1IKGE%Mdcnor69<QE<XU;deWtNB}ANA^Yh_pST$I^S}co}1#+aP~`ccwetd-f1!Lt-X5hr0eFnu;1c0ey^ys<L6P!9p&VIQ_B6Rnwn?ii}@Y$c>Z4`Uwr3IeKrNpr*o;UZ~ifW)}eXHJ~}VO=wjY4=W_UbuIno?d_ISCAzyj)fPXIgv5eM<xa-CKZ`J&B<^AonPNYR`IM0$ryieV-^NoC|EQ)^alj^r(|J4<Au1eRxruT4DpKJ775+h4Wd0rj)ePH1__T8MgpJyK*q46S)e5GRszmL6=!|zeyF+9G*OZ;B+@n))1@e1MbZ<}d<se+%+YD#1FqaN`2v-T>@i+K^AtG%=MxsdHa=aoD*oqW-73$M41FL1rSm+71k)wQ(WrEjwjSqyyTxI*ulW={|Dl^!dpPH9-+0gHhze3~2xjr`kh!5rc)JXh!<gdPoqyO<DT^D8jj)IU$u_*Y<)1OKaEfdzC4{(pZ3)=;a#LyKn+IzI>P3w{n94DAm-ti@g}_9Jx8hvtIw!P}wRz}vxFp_{>5!Ku*qz^UMOq07MUf>WSN!6{$``ZibrFM=k67l9W;mxC9B-+`_LzXM(kO#`n6uYqQR*MKvjyTO^@9ngK?9pF9CBVb(*fK@G4YEh2RISV=)oCSU#IvM;v_$`Fa<DsvC$AiZ}hk(a`W1+8tb)5u`1t&pgfs?@Np)0`a!DfWcWl#&affi3|(HPnW+!*W*?GAPazX*K^9HvDNExJJ^a5r#sgw9QHU0qv1C2)PgA2)>lae&qXJAfN$(FxiCS`XX-+zz3$BUFGL!FJI4U^}pr7VV+WL+gW|2m3?a!2Vzvp>tcP1Gp`?DYOx|DcIBI-aHXHhikD8ItSVbJO?}z+5tQhJOkPeJOiA7(AgL22=)cLK<&UTV0)+&*dF|pP4AvU=<KIOA~YV_9vlyT6Z$;(P4HZ(KX@*92~-9z0q;WS{0g)!_!V#nv?(|Q>;v@#`+)mF!@>Q)qiyD9G&B#qL5nF`Ox0qe7KgORfF1+qXfa)j`OpF2`QSI8y}`N;0<Y2{U5nQdI!8e_fuq3DT8x8!0Nn)s0DKUkb1^g>TnsLSt^${WOP~wDCEy}x3|QBr;5hVU0yG0W0Xz}91w0XKLTo{g3$$3MMIm$pxDb3Cx&?e3d<>caj?ki)7Gt3=gLR!}!_)9x*PY-lTC~){3!!r}s54mCXTi<D9T7SQB6RMI(76@V8Qco&iqN?=v?aJTH~`uO8~`4S(0MpQ=TN8@I21e#p>q&I=NF*Oz|C+!FCcX8gV1>dLg#_dK=45DNQBOj(9YmE=qPAs@F;LkXe)3}us75d?1~<FBXsTx4FGoq4}}f}4+W1y=o}3l4vq#t*@HU24h;o|qNh4XM%dZAJN&2r`u+Dup$C@je+1Y4mw$g<w*8m&w8{DF<vB9KiJph{+8_O({Y`&E6@LPzPb1R'

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
