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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78c7c67eae00428b9bc50c288776c75b/part_007.stl', 'relative_path': '78c7c67eae00428b9bc50c288776c75b/part_007.stl', 'source_sha256': '26b5869f215707bb2be6ade439886e9be96c47b13a77cd2dd73580cd6314f965', 'input_faces': 472, 'input_vertices': 267, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09169332683086395, -0.36329185962677, -0.15929174423217773], [0.20804554224014282, 0.09287059307098389, -0.04449703171849251]]}
GEOMETRY_BASE85 = 'c$}r12T&DByM{+Gq5g`BIUPa4906BF9dkx7u3|VuQBe^Q#W?01c2z(@J)k0r7yuCy92DcO*;R~tjBCyT)9%lF@9VGLy0_}qy;OC*&%87}J>6e_-7}W%-K_H2D)_0USj`%5J-@u7=%uJ)tAzRmhYa`e8&`jHP*@(tMtuF}tFCbC+rxc89wk(n?C9$^&L`NhxxvxZ|0l<~21oxf!6Ct3qlb<O_Vv^Kj$VP|{Br$q0bW6Vxz{xtyELt9Xi}@LVXEQ(_)|Ey3uc$FJsG-szrUobAvo}mu8OZ!s;)+dju&;cc(|B#RYToV<a*31sjuwrbXe4Cbh2p5^Bt}A-#<z{s9$U8WyQDn){=HiZ>wg?{RUg3e*2(!y}p(`JVX2zH<P3vGa}B){q7x;`zjvs;%iF+cZ%=nApJBuj}%{7l98mhW4?P}pIlGfvr9BG&$`xf-zw6M`9vsu)os6Ahu%Q@!vo;gcV8#{?WsyXl|co?*VfFI`&qi2Lj5Msq#x$peNTwLuZh%GE&Ih+W*SqZKh1_<e676UE4Cwb-*ClW+R-wKh;N7rm*+K9+b!*A`8w^8`Ysg{WPCg~$oQy3Z*LdhY3>GTCt@+4Yu{AyHA@W{S7TaB%;Uf@sQ;w;2B{Y}LVPW*KKy2jcIxdYmxp1#?B6DefARPVY5&&>crNd3_=cn@($6aC=;x<?;%jyl56C!FhOZQE0>8S4#EG%zF^LncWb`)qeb5W(hr#U#>JRl4-<;$iabjE?|AViY7Rfj(;Uy1!?<?gW$~dcG&JvgA0;vh&_q;CgpiDI*9<Ef57rm~be(i#3a_wrjS=uijCF5_d+8l9J{(YSM{!=mhU8$ky|FJCiZS(Gy_UA1`e6(K#Kdbc$iSvnnqMx%y!&lo!NF4HcRXZd6v;PW_`JL*4`x@K9PwFo7Yph)b>!tRIP2z7$l;<?mi<0_kvrXb_rLtuF)eDm_zkLUz{`qBFBo6O%L!1mgx{=Q*&tqz;p?-@f@wHa&GGFSe9rAnieS7g0&wVof=DNIZ@-vAi<>o9|?`DUM>Ec)Nhkrg=#z#Fnbhos-zrXlj^MGa9ddzRH0Wp}@nlfLOyc6U(ltRl*qC;9sJ6hN$#CL_9X!-k38)d#Utuy+6a(|T6FFi3;#?7t>@{9F)_?hi6?}Kb49<)N`R*OHsn#8?fgcasDHat>%KQHOG`qUNq?OFlxwQ}9%+8pu#^IPFjgy;lS`fHed1ns;}7hijR6#2pJDC*lzK>drq%$M;GoR0R3<%6#_8!gZKsT}+|2g30jAFvKqFM}UH6TWTaFY>$}qS1a<bNC}o7&kQ^)?sw?DtVsO+hu;WgF7*9X??_3%C(R@shlo|cG6XeV`a*KP2!jCgY|xK&adLnxq<fU%#{45-Ru90Jm*CZnP0=KR+wME&C5iaRgrlyO{<1{y<s8zNn<6ysUxN!uZD*&5M8-f+BY|7j67Al;#|?{nUb$evCk#m6sOlSMEiJ3`<6e>%e*PWUTC7n(-03kHz2=z78YL%O~U@N+8WPWculZqjn2t(-x1>whvv}HqGKYZ9Ybk*=Jz?nMO&8HBje*cQr4x?v7n#C$I`SP=e_1}Z_yb|B;J$+Z_J}zU-*ma$+dAsCHQ@Q^AK&HPue%AtuSsm&K*RfuHiWsC8K`BCmp08w<k$`<F$0e|ME&b#BX7{`}_D;uDcEtzuX|%XS7T2(N433Ao2U!Oa3subjlKcdht;4ua{pV*B|WQ7dim{b$1ybwb5IN2gUx=MDc?PFOv3yU!natr!eu=9`f93#xD42OD2hLb8LppZ<&7Z&kmR(zDrF!*XwB*hrwY}#Wy}!Df89-7RGsU+H~;)W2L^u!3y&-v$6JlJLY5WFn$9o&J^G2ACvTd2J(rL{d}(Y4Xerd#Bx3i@t-hmiTGD-B=2d~qY<|+PKa;moFnVYqWYr#_{Oq6%`F#S#JU}d`hVXPUzy)s@}A+;EacDIiSj&(T`$R3Mu*B0hi2>UtHd926!B*Ki2jGF;jO=m6Vv63IB#5Xga7Ob=KcJGz0#l8OCqJ;W3sT{y^q5FGB7+!>J`6@b55UT$Ya$UqNSZ(&2c_xv_gD?{}l06=Sb|!znHKuWZzjU^<&)R{HPRrigqTIknz>xx5)Z24rnCtWB%ADM(X!Yk$u)u$_T&LNBB#N#!5Ted=PIrLt@1bKP>rMP4*Dqkgy)UC1|<$nf1`lmviv7s*~k9_5=34=WpRRv>PkBY%B75tc&cs%E}=!KWeoW@Z-0@-&Y@T;<Xy%G^W``@w;EyEaT7pU5mI3zwP|(Qa|a0%)7CuGxF)*jWLg%I$}L88x23<)h<!%u{aOkGHv>P9t|G5<lL%V$bx^Ss>I3H^P9P3>Q))&y6R;ahu0f$&O9-0o5W{gio~Hd0Ov_<dL#7D?Xtv!DY*mk_M4^Rn;&M#bDF-M^E+jVuWXzt^KSgSLVj;N@ezIzPw9u{!&;2<#w)T;l&SF&50*BMk>`SZaPFMoD0$hORUPvidI^4`-I7nV_sivZ4F#XT@7HLn^t(z2sjseo4*&OB*e?n_lJ#P2m>=U<*G2NV;;hN~G8>D+uY5uN&UmCO*5ilb@aGwDKAPDT?JukWKX8@oQ|6`iGCrnW4dF+gllKM1&J}TJ+XH^h&aw|{D=Yu#TLw#982>JY{r7r*_zhDQ%5|$ZICpLGh97cV)~kB=Jn~Y3vGBEB!=#_j(=adVLf{)iXCbZzqn$h1GLFiU-*8^#dDv9S0)Jg~<jLT^k{^s4-@?D~3FBsk^O(863*xobUb&CjZV>k0l77giYwt+jGpD-Ze4D-pe$~?wC#IDVc;0^d;phAEL!L1`OGo>zr6rC`bDd;fEb&j_`%OlCN6*D``BX}ieyqBWef-KWxv#;km-tFYe_4;(p=wx<Wd_5a9WHUG%{zd+wB0Da)@29IEiE5oUD&6?_k4u?e(Gi1x6)a(6EI=DJV*8u#KSP#z2fh6-tv8Yb51SzomVZF{zlKiIJ|5D-)ExaH-kIgkJNn~;j2-y&zcX#qn~$%!Z*y5_eay%mv~>8>;vDwvYfwE*NLcqeJtx2nI`kPw-wsI=e1w_b_=kdYW8@aPYi^gc@p#gb${_ngwOM&$?LQ1FNT^e4~XBYu;d?8^@<W#h6}a_#s8Ye!g?ZpB5S3~_0mo<zgoU9i63L{pW)9Ri2gWC+4X~;G!Fh%YdNQw*G0pBbO-&62*CG+zzP|d-!3xmM!N>cx4VMi|M>;y)zH>>A89*ReC<j$@>TgB7`Lkn#8(RkAy1tyg!L62hx%4!PRjL>b;x_qveCZxNQo=M1mD9y_zN9nzfgjnBc9I|HOuvje)3#eNUFq_=}RT}5m;yDS{XREzpF347Tkc}8<>Y3T~NPsC3#O*)=x(KFKPk5=>{1evr~k`qiWw8{-JlWUX*_pV4YU-fbSfG_oKh+;QVmc6TY2;ypLM^i{idryx^-5axT-<hge@>0r2~U<Ne}p59}Ky0^#?1Bky6BZf6j;TgJfGDhElsmD^!mT$&Ew*nO#7D~oWhXu1^s%X2tq7HN$*S+WP?<Fj4XubPeTDyq#()E~AL`^dZI_+D_VW~TUa&*A&PDoyg9*|917Ewd0OzGdaRfcf4a_-awSUo`T@_o?nT;opCZygD)x?SFPWg!$I+p5pXD_Aj-lCcai95qTl?5S}+^4(i)=mAF!`1|ZLmS_;4AGORE6<1!EGxfSrwKa#jLG7lKnu7Y3klhoI$md3f)-voa|IXM@Y?;MxEQw?X(pK11~KeRLTKK!7(=cJ!8!8jk@dJMlqE6ne*8ptOtiXN8sCtjEHks9xf{Q0&y`~lAL{-%x@k9ptc20v%MoHs2YUYM_01K?X)Nj@}vEQ|P=?hXIIa?J0>0P_!id}(=))OhYPb@PS4%1P$MvL&zN4Yl(q_=?(I#-R<)=l}5|mn{~5!&9u&88_kk)RBGA_#jTkNp1HD{_JbX7?0s{ZdE^T&yv625g_wu$@c~8Vr7!}YOjOHFAv&dexIEeUnzG0=W5Qo+3gnmg4U8hjgBQGJ}n73@Z$>LyJFr;691~T%@OfO6_NQ;Ka|0It*r#VL<+uRZ1qC>-VMc9GZ$dL9u$jlHuOXNvTitERXB$JUtR(~qy)Zaj1Iy1FmMfgyWWY?-u2!R=f>z5_*u<xemL3$-z}UriErGMfcK!fwwU*-*HGWw*i(LQdMCc2#6R#q#z{W6T;li10u_#mpJs#iKE6+B5e?us55{{#*&aAQzv&3S-Y$G!^1*w$x;9pPEou(dqsw%8E@S;P_^JIckNmD{uAK?Ld{gWfKX1kO%)W*8bLQbY+!S}zPkDg)m)gkvj9ZN2TcR9~NqvXI_+CBpSLF4T&BQk+SCDx$J#C0{sY6fH@7#5k^t<>iJa6(S_>Jr&PAmsY;yX;``{JwCm+^i6XnA~RO?oB1>CIuB|E~<i`(~LOw3D5J_t8BqaNnSE$1#pO<ole(kb-$R)d2p!YclWVm|Mu7kA2|t`?l&b4fC6*!PkysUiv4<eGMby;QL46`@hc|IVTvJ#=~#-PM*u;?}hK#0Xt8KZ)qp*oyI2lWqu8Z&ce3|#(RJv8tb&w{F8Fs{^6$Y+t*xU;Kvr1_aT$b?|U=cfB09NsxQ@3rZV~`h}^d@#a8k6`tF}_bW{KNs{j2z;S6{BU;Pt~Q`5%(-+#iHo!f^wxn&HC&Oy|9<RJ1`>LT)3axirXIhZ_-x|BSQ970`A4k3@H{z@KC4yCRjhmt2ye<4pGPh`<~8H>*ASago1t{}&fH&TBkZzOM~E+=m$Z=o(FZz0E1myqMhanwcRIPxayJn|;;2I?I0267B_HaUj8o;r)Xo*bQ9)=+0qXOVRcB+np^%q{NJp432cPjWBnXmT%dU+NfgUvfWc5V;?@KXoj*KY0K(m^^?ykUEY$knBkfA$yVsQ^%7Bla16+vXSgXoj~>?ds8Qpy~%zoI)_o0k;BM~S#*w~t|Ld0x3lQHgBnZTK~AP_Bqx*iQa6+Lk`Ge1kPng%QRB&n$VaGg<Rj#x)J^20<Sgn2auzw08bi(`AE2%$A0VeuqseLH-O9Jv-OZwNYHry>T}@p>UQM1!ok7-hBzY!zl=3asN3rPamRp)pn^N7$P07yGo@8gT3$+*7h3rc0OLisyMD0iZiQJsppWK|>f;xcQg4~iikld22Qa#BkxeawNxed7k)ky9@?nLz>cOrMAdXu}6`%wMJeaJtv=<H7oBm0vlQx}sblNYk+96^mDN01Y#+sTRK6c(M$)E#6q`6M-&e3E>cx|e*Ke35#Pe36_@Jw(nXU!@))UnN_pN68lQpVTb!pX3|VO!5u#HR=KKHS!f|8u<$O59)66ALR4YRPuT98RgsBJHw*$+1zr8nnB$|&LFR)t|qS~Yt)%!T}P2M@(8LMc?7wu@@=hlWzo5DZZS~nQk#+Ml510&l53M|Qk}^)$&OSPvLm?~)s<Y0Y)}1(Y)`I1ZBDL1u1;-1u1<EKwj?`{Yf)8lEpk0-8*)8zLuv<dL$VXK6WNK}mfDTnmfV@zhuoRmgZeYM2e~(k&O@pG<e}u@)XC)G<f$w=FQ6_Y>l#5`Kn`coc^fs6yp5bhO(7?d_p#`FjA|wyBmYi4N&cODfqI&JfqaX4k$j7MpPEg+Pku_hN`6XyNwtt)l3!E*B)=xVqTV3CBEO(sBflU&p<W?BAwQ=6L4HhrNIg$}NWMosL%v78OFc`zOTMFg%N=)EbbgRqo>Q+=FOjd4k5e<q$H^w@TC#~eovM*_9YLN>_N8_u`;yyH8<X3S8z|p$O#>F4E9RDbR2!;+Y(uU@txK*%u0X9#u0SqFtw}CNE=6@Dmm=FztC4NVWvTY$vg9(<8sswMlGN(tlH?Lp2XYB=X=*KUX>t{6J#rOtRcb?WRdRi*6S+RQ3AHV`3AsJBGr2vv3$+Ki3)zF(o2=_lvIltxi_QVm;bdK>k^{(7s0+wb$n#lrUP%onuOuf>w~=*CA}5e{vgo{@x{s{uG4g)$3F`0U6Xa9W3*=Meo77w6o8-T!_sM^e-%y{D-;lphUy{F&^X7rRChJA#{M1)uz37~e`hu(%ofYa6vR-ulOz$!IGdYL)keoyQK)px)Kz>iXOMXv&OT9yWOMXXvKz>L5q<qU|pICJMC%61feMEguenh@Zy-vPNK1@AMK1`0Jn#hslY1HXtU46;Z$Uf9|WFK;CY6Eg>avf?#avgGc<y-D6&!Tf)1wVN?U3uwq>VykWZO8@4|DskR|BGCdT7g`YT$oypT$o&tT8dndT!d;%E<!F&ElVy=wx*ULTa)usOOo@Gt*9l)R^&p|(&R$qV$>?+V&uxys^rRKJ8FHh9k~&;3Aquu6}3IN6}cm|3%Mh?JJo}%>kx8x@*ozShfxE_x=tYvBTu5vCr={JWzl&RbtQQfc`G%6tm{tlR`M<uoztoN$-15(r;~r9o+AH7K1aPtK1aSy{fm5?{EYgB{EYmO`i1<FTp$lr&w~Y6bS^~APcB3*OwC6wOtz*fWNUIks-6c6@>*vrY7SX1I_IH&AiH<Vlh@YjfBG*9-+naxK0o}2h5!1OKYkYf{x6T_w)LNn<nG<_>+3!@LFAQ>e=+(AK>0Ttk>^J'

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
