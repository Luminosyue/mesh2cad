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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_005.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_005.stl', 'source_sha256': 'ca4d5f624d20bbbb2f9cf8061f152cf69c1bb9e6eadbf6daa8b7b4cf0dc06cb8', 'input_faces': 430, 'input_vertices': 280, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24443595111370087, -0.4143713116645813, -0.4879723787307739], [0.24804918467998505, 0.07817071676254272, 0.4701416492462158]]}
GEOMETRY_BASE85 = 'c$}r030PIt+Q%1zhzbINXm-=%h?F_ubX7b@Ma(e7IZ^Zwf<q2m$I7(ra7)99i=vjpQB!du6-dC8of8TO8V(4QXqjS`T3s_uyJx-YzmIEg`0n#P-^cU3&;NIRuCw+&d#|<jKKmFE=Hlwd#9ve9+%Nc5wGm^yJeVJw6FXzpq?p*5ZKuV*>%_dt^FJ+<!iT>RG0KU}Ve<mU$IgtI5zyTf&@--EKpRs)-1Hf<W<*aLH+{zVSnflkr_7AC`<WA?<74fwTX*c%zKtm;u#IWH>Hqjw+rA6d{R4_}_%01va*C(r?<=pE?P&{bpz~_C*T`4w`Q}`;z95IZ$!ekZDX*{4d1b-s!?I@~t3>;xc13bOnr9a?4(t4IMYmnc#Q`PUn}+>Xpxd9oX!4eI<H;)v3k&6b9KOe_OkMwF9^@+;Wfsc)YhH2RnkjpA?UH<Y|0^pB<?U*o-FlcQduHjIuiO7aqlABQIZyV=iAChCw=2(5yKU};a(m4y87|qneu5VZ|ME?7ye}@)`^wO4*_*caBX7FldQm<vnrEkLte3rQdSkIa^?xgtkDKP%PL~b3<GI>&hT5mDE3VEn|GdqzHwAv3OWSL?nA)?Oua(H2Mbxs%-Zo_{d5d3Uv3#60&&mdG)s2TyPN%8=7G+<{$4&EW)PNnbuh_U-oR4?2zm|`i=GnpUowB!{^FFCNk2~DUXguWmoe-b*WPWvCskiKy?3KIW$7w&>EW9Egf6cRkb6d=kx8!vqub!HGMK{jxb`<T$PuOghedG7O665pE<(%sLJCl-i?U(c<uU;ym_LhhJOJvVx?OtP+e8r9*RNC(!lBvDY-Kz5}J}}WNdCRL^$(!b+pQr8Qx|PYE#hKG&uPnciL$9aax+I@3&9n0f@0ca8ZX6=o+p;go=S%Z!b?djy^7%d1DMvn!YVSkk)Zdr;j?(*!M(0)M+4+5{?5(3WiTO4#RLu9C&A+A3x$9H%>g-E8Zwc>`MgCD1&3D!zP4o}X-q@5Wd+UOQVtt(WD~(UJ(zQ(Xtm{Xg$-d&xRvEONi?L#SHZP~`s?CH~Chq_5{+G$$@U)q{$g8#bh<Pw5|J&-k@^l`xw@&dC{?vJ0d!u)>_pU?d+tfbiD(&y+<und8&raVuV3xcZ`{)q$<GF*{s{{J$JPZDS+H2m_p`U0U+u#Calk{@gE4$JT%HH~6NAk8i9#`f0qIp&lvQM5bETx>@Z+q$I659WoVqR#T#fR@TOJ4O{Ed0ezyXARd8uEegSNE34^T=eLbAXOhM%fj4{A-@IJ+e(6|4MEb^6I#hEAsf)Jgfb}R(bqehK8n6yB5*nyxi}8El2V!GFbS{t*iBx)W&ok*_IIUYFLV{AEReuJjA%V(?|5<U!d#X=(YaUMsrgrZ^Y5{i+Q++brqf!UQU#K#Sx$FbljQ;(R^WE8RfEPrK|VI-V!@)8*Oh-H?a;R7KwRk^x1Q1f0REb3m=!OYhT5qeZ{_B<dvFZgx^>p=Fy{`<k`mU|J{EcC;IW|PS<IcIF+tr>ei0eWN(?Z@TBZ5wNjI5yXi?{T{-9fEqz|gxRumy$&*}Ndw9k7*W<Fch6Syle}5dLTgR-sTas6rpV0Y=wO&i<{Ub-}{YiK7?Cxg$dYI6DJoVFe(goQo$*wWfPkIfyUTEuy(QE68ZEHz1wVPJ|oNinhyklJL+h?VAGn(Yd=dp^%c~n`qanw)Uk-74Inl?lZqt`d;i2cF(sRR@ZruJpnAIuA**XD&X?{+xl1K&J(JXG-*52loEuhVOD4c-1&o2K=q*S4fHy7Q>{fpbq)=hfdMb?2Skh_CF$xBL6&nY!_FzGH8mEHp`6kDg*4Y5wG@U9z`@Ukj)C*U&>8A6$1>V(wsi-)sK5<HNEGhLT@dDdxMG(Y)3?bDy(V_BQ7c!+0uV{dC98dUyW_Go4TU@li+2eUtk6X>uv`GdfgUN8puNXLakpqkWR!L34FJJ2}lP^<!-oGMe_^>z~xWG9^Lh*<a4-X31M72aTiG2lV5g#qF`uack<P8~;Y{xSkHX6iwUNwMSe}8-|MeRd}`65OICc?qlH@o4C_lo!`DzTz}C|MdamZ-TA`&GJ0)(DHjI5Mg3&Ph~pVHPF#=REzwKGbyK^3Y3-MrQq0x)kSD2TsUO=Q=NS6;fhOJjt>U$HJEZM+>i4#O{#t_Ems0=6b;;F>e3f;qwDofGhV@hP#`V+IpydkkhIP`G)seh$T~#Nf(|x&d-8PjrUPt?BSpPL|T>mSId(!=Z@%mE5V?9xp_9Ab*PO*~7;y%N0y{qE2<7}BGyy1FU#iPBgG-*3+cS1X{o|GLH>jpft?AjxHtIxU})c$F^FLlQ!>ImIeS>K*Y>xL!zS*h$<$h1V+v$8|`DN`%+<bE`7dC*vuz2$Tt8h^(77Nd7uU)~GBc-7w*8NIgtt8GKc8}G+7Z@eEfddIx8Mu>IFcpnJQ7MXPSfyx)N$t!ar&&Z$G;ajI3*B$4Gb>yqum%<zGOVyd94pHKJmg9JO&LhtXd}!TM@-oYHzHZ(@*(=F=ML%Ecr*(rxjV+NqJKk5EXLxJxhvci=&%+z<=WUr!$t!p6i*+)vUy1D5*eJT6*SyvAC9V7Fk2|S<$NCS?;y<SK({X+I>9+7qRBErS{|+B~kJ@YA6zQ2k|8Dp`W%Q2qzpj_?hVN@eueDdaTah<@AFSfF`<Xk!8^2ew<H4EaH$D^3Pu4sU^9!E&b^c8DrXEpQ)c>he@w_W5t6b;P(lTYQuK6^Z((pZ+4cJ89_`O@5edZ|n&Le1ED=FEcAI<kqS7oof6Okj2PtCJGx~k+?9nn2c(7f?^g00Ow(cbX9Li5Jw6(;L8@=EqGaUK8Sk5bvQ;r?l|S9dJ<ir$~LK|Ify8dV~D)^kLnS@O!6^W>GpV(~nudx*}n_BX}z9C+K4GT{x+iyYqYyvQ2!$#L?g?eyG<P3edEwUN9MKb_VG&6~1v$eaFHEY^+rAL~3z`H`M?X<qG+aDsfm1@SyJ_fe_rmHX3<$=-DD<CF4v)V!r-_tRoLAJIME)4cKdp6z;~Xm5CasCnb_Lu>2Dx#Ijr70c(v;b-^QDti_<`3!CU`iInB3G1u#?EA}GWN(|gNVGRRU)8+v`Km=pI7?oAR4gBVhrg4%UguxQMte8$e0b$Dy?<P?PWH+v-#kk9Te|1Z4sUq=ToL|0dE@hK%^RO@+ZIpA*UiV9ia4G-FX_DF_<Ob}pnh(x7SGc@7^Cwn{$8f+)#McNw)CTg@^RKYOWcsDJN~myi~bG2FF3s6_XQ<C>72Zu+IAIhR!F{0=OX#|Yo2Z0b6EDaf+mH!@jRxF7$-qp$XC1=QY4=j%`3;3AJ(0(rDlCU+H?2^%ZhaSIX^_qUtd+{sh<eluU~Hup13>3{*qTM=EvfqrJuf1&`!(hfBKr#>3{XpSEr!=_fKE%+4o_Nz1~N@1AZU8067=D06ZT#8$2I8&tC5$XCh~VdCmg!oB`(f5AX(it+&?}<Yw>|unooeV-)9Q$o1f5;1BKfPvpOl>%r@>y?-H-z&sPd)9f|gUNOiq;27{|6z6^@&b?8bBa!35k>Cl)Y2XRqcw`JX9vp`p4UPkkvX=!Jf*cJVjeQD1aqe!fKK2^P_+tW5oJSy|!6U%2_L`2Iii`$N1;2$H34ROwCbAFsO>kcn=fB%)hrRaOD;32#3&lCpUSA_Gqc~?H_k**+dyqT8d%#<fso<^Py~r%^UholnT|pKjv%p!{cCoa7#mH~K$Lw{~UI&n$gAagrqBw6uao&eK3f>3)(q1LVi^!wkquAa><RviAZ^0?{QtY)G#rZQ7=Y=TFQ&5~Ip*T-Oaef=c`2!T^?Z^~xEhon6*~<&*0rmpdM*hhJ*9JdkB7X!w23I1_fh)mhk?X)`!JCkSz?;Ak$XCG;;C9Hrf!l!_BR#;4!F7=}!F9pz$U0zmu&2FVLcWNs1AY<gg5u1OHQDn&&aOxguq)Uf`8TjXH~{%7H~`!qISAYzyc)R<yc&D~c@BI5`~dkQ_yO42N#vhkXPjR@BtQ3lD9#O#^}r3lz9`OhkhQ>dz<=2L`<;obf!EyEKyh|QdV$@+ZphkTH}E4Sl8?VfD9$&LmEfD;lgP8+li-cWP2i2-p~wjEP;d~k9XJSVLN*4Q!1a)I!S%piNO!Oo*azte_5n9x&&OyJ6z7ii8iH(#d<onZ+y?m~xDB{I(goZa*#PMRZUC-<WZ)WLC!{Ob3G9aS2fKkAA_Kq;!GXyB;6U&I<ZAE$@Ji$b@JetI@&ULA{4<h|^`G(D89VHZv95gp&OXQnU>~qQ(iiLx_O{nwOr#TD`+|KjADmE}pD>YpK0HBjzRjM`ncK+k!MDL@kSD-rz@H#L1%Cn_j2r?Ug7GmJ#W@_=1{@A<g{%+O#!4#`=hy5t5cx8)HTY%l3&;lG7r?cUHNdsN&PXS)Gq^U=4O|=C2-y(a2>c2%5c~@G4deju8{ielmEaZNd}I+gAN&*YXYfzpXGp%Y&+wXaU5qgwa9wbHq(8Vm*c0gu_5?p=&&S+T6z9A4%0u2m{sq1VzK`T%@jmhiJTK07khj4+&w%fM3y`0H3&3lTgTaF_p4Ol^hay{nTVdRUqBtk8=VL1Yxg4ATE=1;m^YA$fQJl{s?}P8-Gn_{jfX{<hA=iM{V4qeY6Tk`B24_AW`CR=sinEK8NPeAjL2<5$bO+Z2yCU7duHc7EB)`r*L~;HOc@z8{SVf)$tKekhMsPBCIC3a>IJh%12;3Rm3~2&41N$NCf&IYVNH4HA*ca&o_60XZHUT#UcS3dqcLEP%&##5UP@LByKLxJ^=O9mjbHF!{--Ex$xx9hm`~!;fFGzk~f5B_czaeXad2#*~=?dn>`4*C&*IOvgrO5BVrQi&t3eEs8MJ9ung2y6<gU5n<Av=S6fjc0ZfjfX(BK^QE!OfB0;O5{KNMCRZaC>A^aC>ktvJ*HM9EBVPjsky#TnqjPoQ})^r-QE|Z-8&$TwX<SE<<s?hWrJ54SXH>8~8f70{JVr0$h%~1uh5YB1^%!;6um^@FDOL<WlewuoXELYz2oQdx68iJ&_&2J;B|OEy3NuU69SeUBF$DEx=vDJ&^6eJ;1LcgTb$Z$04J@<G_oNAAuKx4<ggS2f?S2SHV|tE>EL4e}Urs74jPREAT1gb?_<habyMfIQTHK9DEp@hRg-0fp;Mffp>uyA(wy`fhQxa;D|6MXFr$!>A(0t|5NDZT>cOL#&_x;kIL_SX79`Kurwm92EVtm--J2S!@=wP+Yb8=uZTT#'

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
