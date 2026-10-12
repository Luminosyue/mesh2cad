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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_008.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_008.stl', 'source_sha256': '0cf2badc51509a33ece77aa3729c1b19d601a54dddc9e2bac548d1d731e2577e', 'input_faces': 458, 'input_vertices': 328, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09749062359333038, -0.3670613169670105, 0.05647220462560654], [0.3284217119216919, -0.2660077214241028, 0.18471424281597137]]}
GEOMETRY_BASE85 = 'c$}r133yFsx5sxPp^}&*4KW;ZL<Etb5p44i(NJQl<^)L%5kv$v?N&|IR#8LLaH?q4P-FOF$QJWVgeuB0Q*%oVHQe*A|NngVocrASJomZR_pI;#%ko<9de=Mcz4J6Krhu2fhCh`w&$ziG^@^IN%un;zGLq8L2lh)E5tce^jE7cS{OXTW=XB~88`slA%h1Nw=$|yAUs{bQOO5E{Mm0h$HIj#>rKcsPCJasMpQQY45>rMbIs79ABo0e*{2W|Ayius7e$7zJc+3CskB>^F+S6^#R4$VS|C-|v%ea<%)z9V^p8ry+Z|o<2>&719H}-pp-}b=>@teLMqJ7yQ@teLMi{GA*hW0Bn#BXgoQ2cs<V&d0JeUJ8sM~UC|JVN~1vAyWGd4KV1fysz-?<v~fvLa5CD|;l5;St%c`PdHlNqfuoVdB^S>Vi0PH>3UEY1wXZro~Eo`-uba+fp#z_IIVdrCY)6^6xsv!@s&Q+Bb?6zuEddjCc81X>W|}iuMDWiQicH@qQWqXT#m%nB`N%uW!l}zZTgG?Hg}Eo*_%bZ=I@RT&a~2r_g%0e)Uqb#cyf3al7kyZ7FlbuXQ*fe#5&j`ps=5e%s_z$Y)Lm%zI4GUgWLqkoLzT5Wi7p$wyn^DSqppQK)D1;eFEY*%0yDBapv#HbLT>fgRxYc^`G_G8b{K_ZPqRWDxQ>a#iA3C#R#|X6V;?Ia&OsnIV3QPeZpnwShmN{kIsG{n;ndUTd>u2i9W%>frq%SL$+WFY?zrqJ5D&nBRp*&^{A+S`Jpjygax9|ChCqXLEmvZ|~)|Q}lHx+WUlJJ-06n|H$@eU%i*ax38<b(=|_Hx&`As&;ad!tByE}mt$RRX|~gK9U2Ee!?=9n#cx}P{bfnmCVpG%9*EzjGy2`Q1>^cC1^(w;hasn>y)k|<{JVyr&MjNPUw1kDZ$CucESpg0l$GMw`(s_{waa3>4R<5YhHuYG{Oj|j&X(sMyIl9Lb6%W&OYvy<vt}Uw{-L{E_ltepYs49^?{Zxy){YObJ|9gLzfp4l{Og(`&aq7N+r2L0bZw0JN?nCGCAwmLR#`0dvGzY9esf$h#^v!D#`}*~j{JQ>u8d0$@{xRu28G0LNn$=%{=zvkrh1O+xQtLM@|hJSe*In~=IiiA%wwN!;@1+A(Ejc)w7)k*{Kn5=h<~gk_UWOCh%>DR;)E7(^P83GqkWxzShwDvp?&RYn8!3j^0$tg0zc1lOXOP2%eHB5`J0bV<DBWa0C|QrL7t;q9FTU_EodLn0{w1XE`Dv%R^-ET)wmUp^Jjl<j_dl@Q}^M#YH}dQbv<iO>q{K{<2?8?5|Pi%Mexu1J;!z38p+|3zrM%AblopDzdY2rW-<7)8X^9@>4<Z<g822pLlOVnO6<FZ)lJuRYpwoT)`_{ThWNGV!_a=t;(e}ub7wc?<F!QM+x?oFZu|XOwD`@OR;KH`TNj*^Iv9mIi{J7R`55zi?Q`|p@1wmXwm;6*3EfQBb*OnhNBc$bXwUP<l3fSqZHHlQ<I;ZIi~P%uMxH$9jk}w%&Kr$^|0?g(u{UwQ7x)(auK5V_xMMWd?VL3jSKx5$yUbR&uiI=AzwHli#90xEb2#LxTYPQWBkXJIGt+IIm+puAwA35Zb^kigD}8e5-I7<&(P-adIQrcl0{_rf@YfiD^ERfX_$@O>V!R2Z5$8>NwC`IPc^3Tvbr{)6{8}dN9qr0IwBOlF{PvX?ufC->_R+A!-LCUx?Y{!+u*v}OTO)g(kvRYK#W?Gv?M5B8=F7Ue5{&&bD1EnU9Zc(O%<r_3;<v5Gem5VS#5@+9kM?sv!MGxQkf(Ja;->^ld_Ct0&g<_Mp$?nIVqBZ2N!_d|%Q0S_xAsA+r2hKm_3-b(e%CK_#JV-Jce~D`o^~1izS@EIYcr7Nz}aqoT|@oNda+nP6OSODlUSd&h&Y@Zza2;2`r!PuYJPiM{mwerHq}C%Q}fY&cslZ_d=2a2@l~|vd15>%yU*3HN3})!8FBDWxs7r0c}eTN1m|k*9~jrEaadQ4yJBCwzK4ESw?Uk(w{bsqe}r{)W}Vz4c6|w+>(>7T|L{}dx7Oc{eR1z8;*aZu@kTAg{k7vY^1r<KwB%p>9o)wO9=WdTQ_ow5^I@nL*6%Rf<L39jqCO@3b6xkZ^Et=p7$APLOK<eMb0+3}S|I!-aIWf8%)PFD!`ln@qyK%3XHQwgzlr<TIJyY;V^Rq2pDO+M96k*5JE>N#>pHO~zD2(m!%z?2Q+f$+IX{i@O%eZ4TfV2f#dxFNM;zyU+H~_?SHEQk?m=^V0`C2WecjsYhn{18C#IrbK0n*N{&Dl$n)j3aYowINdVM@u{Pv?>Scfln?{V|5>@M@A*BpcA-F}M^-}zj0^abvhB};Q%*Oi$OkLQrpt8!h}tu<&r{Q57bf89ge*H)a5Z*vfTNmaM!TkX56i2rwEX>aNGGtL?95$5;7c;sJZ9_~TEm+<pF&iTHhuPco8Tl{yd!zoYY`N@9A7vtb_i0!K=?7M13_qeVr%b<tI|8+R(#QV<aw;qhe^K$k)iLX7%!Smb-%$pILiuy!<j`<Bv#e4=d$GWOG3I1CXkmv2uyqB+{-|Q^Z<9;mqEm#uwLht=(zyC&_#F;h_&;8Z;ez`Xdb?|+QI`qA^$8|khjvqz8+izn1p1}Ksxg;O!zf>R8wMQG&ZRI39cQ#!Bf9mE_GLKL2K48@Kz&W&ZBJ$aY_abxAah{iRq`lFwINq<Gd0-z*{#)AXljh=iw`3dmN3?=JFG1e-?Cob@UAHbMajfaz<GCtejO;U8p)=CnQhYVuH-7l)B-a0r;y3<UwN~P!1f9Y>G>~zb_wKBbe(y$$-#Va+w6`{nS}*^8#c1(cb}hiT?iAZ3|2}F0+Mhpw`c%!6_~!7{;<qP0lJ;iGvtOj$H+#je*-N0`swENU&H?cocN1luYbQN^!G3sy_Ln}F_O^{pB_B&??>y1?x6<BLqK^2D<3+`9{4^Eq4_(?Q|2{BA{C0awtgFe%sAuEO;@8WBNF2NWOo?Mp=q`RO7|);P*f#Qg!P2fb{FQ>>_shWdm*fu-CpAmX8T-1b8?YV{kk9g(Xy2`yd<U_lB*OpxKRAca-QOxd-x-8BM*<}uYlFg4AAQkq@tbd2@%=Od-yJ+B=3)QU!Fv8~l;mmTO%cEC&~m)rRlc4j?H5l+{$Cu$bIYlclBey}EcDCw4$H_XlBZF24(jH7&x)RkI^11|`oH#v|5%pP!P<8z#&w48vnx7Fdwcv^_+vL>zCP@Zc~4)5I6qC3y4ePPvPJx#Y{Ix+bVr=^(~!@OY_$LTnT$&-avF8>Ig0ozvoK!&aMV8&e&;!+^}i>1TG|{(`(F(_*Zpxw+H2F!pg!mEUT-$|6zyx?K>NlYNqftr6_}Tj9;Zc}?~jj`Z$sPw@!Kx&dr|I1_><oizn$MVEKd^M{MI+q@m%3kTjon&S4I3rX{;Y3=A5+G^J=2srR;ZYu++!iup#2-T;=^9EA=t=!>>L16aI>RGG6nKCh&K`zOaY=jPG=hS|I=H8sd+6EphbAG05{qApBkM{ZUWth&a!Rxz){f;QiCC>p{CwJloapeBalKmBaVG^v>`Xu88=>#^8J6g6@bjdlc%EcpUSU)dTsIJcRWyAzkWb+0h5>`{8?+G2|D-&+Uu$5Ac1!NV+Zi-TX2MbzAlV{@JOhTTn9c`RoI%^JU*k94&Jw#>;a+FB~A_wPy_zzsc_*CeLlN^>DP$vY`FZrTAW%55G}qwDfDqEwmZ)nvV9j+F_maIx6|tV=@q*-w%xovC^-39)63x7TU*ebn}}{%c0*|_fgLkV=ykhr|4(P;X7lw31~kh81cV|!uR6Jli=@k4eRICT%0GqQxWGQ+{^l`?pTMJ@S8zld~V-`eR^g(@@!QY^*M7w>aV{$3-#yow(fgN>R?`(gZ4dG2Ya;Kn|k?qsE_mc`Ku<F-^TOdcYcpO5RCgbBNP6ip?n_+#=Q70Mf`1RQUAFw<i0RsSGw&lOYb+*-ZK3sw|TT?&cL{aufe+FcQ(uOvEsL^U5EL-gmd1^cqw%=Z?8wcch10Hw*c>po!EEnE};%x_se-`+&PH)45)#+t=@}!u-XyS`Pyx~r_`#0bJcnb`S(J6ZQdsAmvg7kzUn#jdwqe_*;tm3{CVEmzutiSFP(*-&!yJ!+2Yqce@Fbh$Jj4XRitj_x=V<^pWhX`ufzO~xq|l9-$DMK@mSC8@4&wR``wb6C2?%89-`m!{9bYD<W^U|{^}LR8&p;5X&><f{qlRS7E}cH(XnT!fA&+<^LRI$d)5CzoX*%U_IX3_{LtzZ+P{bURGWW8>Tm7)8h+m6_6y-yC(k_drB1&TKz%;hihWVvTm1G%K4{-A8}-kH-`M;J=h*8tSm$vC;SVi>elPxv^XD@BHlqsSOpcL!w1Yn4*E<wNzXcW`|Jg;vZ%r=)f0yyH9<)yb5Qq1OHSlA})3zfJ`LFDWe#iIO=IVFegL?Dc?*7x<zrBjexUA>P<h$+{<MSODZ$LTpThtH!8J#hYohx9x;U(b@^}=&hRAtnS_oH@eAofLAUHDH|LLCkl$9;669{l`XWOqIXc4>e-o%d1BZ&=UYHbH$nJ;iT3ctGlJsnQgA^82l^J9dk!|KHC=*}d^Rd|yZYcgv%Fgo*vQttHy?Ts1~s!?@12%6DDo#-(#IFZ!-_s6Wp)E7zwsxC8Q!sqS{p*k8c!+>hGS^LT!UjLmmlpIRQC>&)ie;pe$z_bG|{Zsq{Qar$}wSdR=sJ|pY7?F;+dA>wy_FSXtnf_r4baJRZyGQ%+5B5BCqD;)WpZiVN%cIn7xG1i0C>oCrr<dNu?<JA|ulKL1=N4nKtZ_-@))%K4^{Js3W)x-z#zF^Cqfqb05H~GFT@?SR7J%9Tu)ZzL()Pc{>dj4rV&&*nY_`H9O@A5HTOD6K<J!=Ha!}F5=kBHCjHd?3sc;C6a3geB(^O8kBD&y6@Tn#_pf35RdY{9x;gMMxNURtg&@@%vge%@ckpa{fSzX5T0ZX2VbrM<QA7Wnyn*g0R;6~7`+elIl=UZei2FQWa180?GRD@Z<ik4tXrLHi;J=hdzPXXNj5L$JTJBGTR#>m`0GpX;oD&qVx-@H_XZHoC-?W^r!6eg8V{<&5X0HBDJz&0kASbotf0a;iU0{qKMEJ}}~c^{e-Y$p81R-am8X&|gg>HHrKsc{X(*c{cf5>NxVZ<oVRE$@9tI(G)MI+Q`evKT%hbe<H7@DPBcgL0(1vk@_>ap~E5_)|RHY12uxIG=|)P98c{*jwknV*dXd)Y7g>Ya&MaA52!KZrVi`ou)5R_$RDsxU1|imjKiuptRhWuFtskZF53rFBgw(!P-;DLD7h9jgj|bUm8Q5nwK};xxhzd_4QdFv204scj~qr0r$&+^IZxr#w&ZYfl*6JOruJJ)n&NiUC~`Y;N1Ea|YFlz!&T$+yo*YN+MeRd&&UY`G;sl4KI;@|=hEn^I`||IHQU{QSl1ESz$O()&f~I&Bbud|}K^{e(?674H``%%Ts7uI7=aQ9vLtaFlN1aTbN1jPjJe_Kg4dyYOI-ES6Y^4q+EA35I`T<#KH?o!7lcu-<wJBL?U2+3*ZE6*AZE^)_8FB@308McbYH_ksUvd$0Vd^{N!sJ3!Z*n2B7uA#OMOJ@2s0FB=<O1Y^RBv)YvJdqgvJcsh>Pz<J82o68OVbpWqn06;BUh$YBr6RjD-9(ptwpX(u12j&u12mzQyfGsPgYu%97KMXrnm&vpIm}mlv<2jlw6XgxD-usAl0Aj&$xj!#TJ_4n$#L(rD5cn<T^CP^{L@xrBUSi<VG~b?@^nP-y=7sMw6AcBsV5Ep()m>t;jmLIkh#pIk^S34Y>umJxy^ewKX}G+=<$X+==`?wI%s|a%Y<2F4T79F66G%j^wW7?$kK4(q3ex3FPkN4{3@&qV^?!L{6mkBPWtSrYTOQrjnHoAt#elsKdx9<nh!D@_6!8>J;)+@(h~dFKCKCr)H2pCr_jfBTpnxpbjBVAdjV{l9di6k0p<!DNds)PN$9_EB%z5P99BDJc*`w8g&F&=_s<&$z-M9kd@9QPb1HASSEELbuL-y60*|o$qUI#smsVq$v;pRk$)gBrYT-Pokw0ko<p5Uo<shMI-NX*`U!P9S*ew*v?uwN!|plk3Qh6v4)bta5`GSQt-%x*q^~TwAh|S6aaC$Ha#eB|O>r%1S#m9M1*#vp0=Wd$gIt2_O?|F`y~*l=JL`~Z4twaZzo>8ccb*O_NmJ}YRe$e8eMnaNimXg=acUtCu+mcG;^cBP#g(Y#$(6_<G{t3TihZf2$fekaFHNx*RpsHupB2Akz7NR{S%;T2#gA!<Z&1&YZ;*d;SRVB-^(^@?*-m{(cGlWXQ+%8HhOAW8`ZiS~Yn(g9&$<3?^Jm4EscJ1==9;`pzDzzsQ~WFSHThTapH#JW|K!h#-%?AHl_@SlQ*5DDC0FH|w$K!ZQX7y%$&n6gOl?YSK-Q@ZsSU^t$+f9r<l5w5YAtdwIfz<;97HZgEkQ0ueuwH!euo@D)yNw6OaQeqIe=V)rno*eoUAmOT%X*G+JfAS+=`~S4NY-tn&P%J#Vx7P<d)<n)NpbWay@Egay@btYDsbxvOi66QK}DFX>oE<^1IY><afyxsg=kT$u+4V<eKEVG{udm5#&bX<}}4o4ttMUhZ;eyL#|E@Ay+2{Qp=D7$%U!DWTjr@!sG%}b-onf&x-${DZWE}On%I><_=BqAJpH-N-vO=o+tl7zDvDCzDs^U{hh4z9{CaVDfJ%tDft=o7Fp>PveKL67t|-zo8-T#_o+9@_sQ3(SIAeG-*uYei_}Zxi{x|E^W<~nGt>*@Gvs{gZ)E40o=;PJil+D^^)UG)`8ZASQR+VOQSu?`9<oxCe2Bc?VSA}LRFk}w`Y)<U{ug-%bq{$5Ih(qVypQ>1(-iM?*ly}+>S3}{J6Y*%a<0R+IqU#U@h<9S@-A`~bpttzywPF5P}fm6kk^sd&=jwwZYHlKucvM!uP1M!=8`v&w>WG&^%ymme2jd8dVqX_e9&QWF&>`&1^%c1Wa~fw7#`~XUH=2F|N1Z8KR3Jn%L$HH|Ni(K7vrtIF=(ES|EUi)8`Re~?LPpWL~hC'

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
