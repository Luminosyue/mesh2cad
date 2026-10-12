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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ee67f09ba90c4b91bd2ff00e24332345/part_002.stl', 'relative_path': 'ee67f09ba90c4b91bd2ff00e24332345/part_002.stl', 'source_sha256': '0a1f6553ecbbe0bd028e2422ddc3468714944d3fa90cf2de6fdfa0e219185f1d', 'input_faces': 640, 'input_vertices': 375, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18969449400901794, 0.019913628697395325, -0.012753201648592949], [-0.15775486826896667, 0.09419173002243042, 0.044497132301330566]]}
GEOMETRY_BASE85 = 'c$}r23z$vS-^cf$i%S{zC>+<J5aXKbb_>ZgZZTw>!MKGPgDFHi<T5Hz6b+6`MsCdvGouT$rHpQhl62uzDp9(j@>jjH*7~eto&BEodEV!JJ<obRpZ)#+`t5!8*=Mc2&za{R-?wC`%9i?9$C{gx{=wFImL*0xtFo1zoHl*J=;Ue5rlih{vZ7@!{%JlFH@IJXLX?$m&5jw9JZ*GZOnYBU$Fc2Vn)qVIrld_zOPVq=C2dTy$nQ>?G%dL}pEf=zHMw}ZQOmZioA_EbZsMEc`#=6GQ+x>S*<ObW#j#wR{(KjCP!~SgFY@E<W$rdVzDnfI+@&dk0Z;BO?G%vzT}E@2zq@Fq*!HKoj$m*}cpi)^mnr|d9gSsfAKdk<+%7jVBT^o;Iz1=*kB(8t*=dZ-1LxYTko9vcnfu1=Tqo-upXG?{!1(h;a=$O0m-};$ReMP013!_u)$)!PWc|_K$BJ$L=r?3;Z+~>P%oj|vC7;Qbxii0%JU`CXrBmf`tq9NUBc<ed2)?^h=E2n&a@#%Ce!e`u;Twy>&ga`>9+Uk&xn1{Fd0cj@)#^A$Rg}4Ze}OzdK2PpuMa%Q!|9Pc4p5!Cy{BwSSfoD0+dF$o=E|!@qw~x$H`Ht__%HvtkXu3Q<Gn3SLh>p)x^_`RC@qZep>OZ(7UzbyM*<)tzyBw8o=FYS}s{ZPSYh<4b`v%D4N^BK&o}FQDPLr?KllxL<%j0!A$Ex#Lv$ML+vNp{sG;-&_bsJ?})kzD?-1>WFUZgyDWJJE%$M)pDy%{gc^Ojq$DC~1FyY)PIzCF49c7OSP`72dd`L4I+`{BklSQ;s}PoGrpbN?#pymcs}UT50_sf9-Fq<_9g?l&QBk(vAMdo|yz_mSJ5KBfBezFVGp|HQb>@_#S;*CClFZIJJ~b#}zyLNlLKU+&jUsFh*nfyXNsnDstS?!<nj-iNRLl({?W!3}czQre@1M(+5E^32@!)LR?tZ;{9Q+Nncf*WvzG63yH_IljQmZBK5`uw_5rKPT03CKsveHtU=8LL;}!%$3J&b?-gT%-v5r<weS^JF4fKeS&{``V2ZOk6-7y-r8GHURTy<MJi|haZlUnk#Z;Qi*;u1tB_j|sb1&0KG5Seb)Mtvsn1JXwTXpB?jC++llq*VSYYPPU+eco$^)$*%s2b^J-NO2gzOhQou|%2wVrF#`KdYI%&q6o7nr&0sdsa~Tw~_CUgy^S?dtXZb5>m^?Uu|gG;%j_ah{pG`@-ve6SL&`*SW6Oxt+32orkTtYF;|GercrKw>)!|nY%5c_eQGMxvuxk-=bcxp5OSK>fHMMw!LBb!nNx7nIEjPH+3pBayxi_x7;7|L#Uq5yRNsq`N&jxow|8T)p52NqCThR{z@w}^1ze-QJ?38GLD&B)&AWRDff3fnrHS2c>6mm<@^)y_CMKfi<yV|d-70!`q&-jsrN;%U)^^lo4Na~Po5vQ>a$A<%{;bbfmv^Pa%<%0>T@%AQrNs<t(ZKj(8%3gt<-TaKj_?9IBHL%JTwo`#~l>j-@a{x{2b|A*X!KLov8N9{fu?)tB1|pf3a(UnfpEUZrN7r%v{&&+*f0q+HdU%>V3(~koQYE_s8|lGjq#R@2-kb^P8t$=kA!Hs{TYHc|3O3O$*H2w>7Q6%mbeKKyLCHGuQPx4|a=F`^{ddj-#4d_jT@Gm%H1{UGmU<#om`Xb}@5(pFke))CYdPx*;s5Ug!2Z_o~n7#vN*&uT%4husm;hftmX}_5MpER)yu%>)blkTjg^eQ}?lY-6wbEW)_6y6?=uxpKC8qE;MrguG#83)AK5M;QGQnk@C=dOCPsFcz<_C75Vwlx$bZ2dALG&e{Zh)>psChV%6&k-N)9NWad`apK@h=LgK<gGw+m{Z`Qk>KJLKj0W;V2I``$ogx{aMlcw%}$gPgq^7yRF>V76vU#RY*yt%&r(S3s1;r;z5)qRxCb^qW7bzh`&-AC8^0(HaZRpw!xhvrrC;CfFz^Qz86_2j<Qx2pGdQ5AKbm*22h*6Ez*FZ<HG*<B*!?%}0t!}0}3^CQ-i>w5d{GV1m6++nSmGT6-BsyE8>VwY3T9ijST5ATkY>*o~R$LHy9AIaEY=DJ?z!F8q8dE0iQx<AYMdx4qTyRYP%x$CKSa(`NF=DJ?z!R`ONC0`foi?fycOme-x=-ed_-G4sA`l9>j`&jaTr(Ulw0ndK*{c6C|N7ws?s$4%u_!HJVVdna|K<CzftFOJv%&*mxPr4#=f91LAy3z9(xjVFG*!&iJ_-C2x=WhFA>{K&%znz~Y&--chJg#%={HwVU^W|;x%|5QDzyD16fSK!hod*-XQ12Jdr&hLFM|7^&DQByC4%N9{r@Xm-p4EL^Pk)DX$Mw|fJmA@{#dEH&%1QOQ%Cu1Dtxoy5X6|nPF-P|89+2y%&izBj<eT-Dr;oeuY^Is(dYwC4j;sDWk67{Q`9kOVc|_-aZ#~Z)_K!uXe`2&ePP=LD<MKGkts|exc|P#bw~u!*a(mmtd^5K^^}fuRtIb^3>pWO@pQ>N=yjmB2XFVbh+*Mm%Z`Nh?eM_jGb;_FuS7hgzeO&U;dY4e~$w;}K@Xbmy*T)lD*F62bd1!s~^w+uW@AzL)`<*&Q?l<^@`rL)`1Do>A+^xP#?e|DG^?v=So=0?U|EG?+4)0RmV}x>^YrJ{r`w;pBy#0Bu33&S3eD4wP_MzT>bfdbiYIIQN?V?(bbnfgtvQ@s$h3b1no$Gbbn>+ER^UOXzZ-3S`pSPae{r*YSKlXR^K5bzgArE}GZkyci?A3Bz)44OFX-=fv?NKt{>=W?x_p|N<JoP%awk}cUbJKA(k9Fm_N$0;5$o1D+q`p7Yxqklg=61P?d1jwrR(StlqI&)c<<#rk%?jVIJMcC2{{G{r>!IGF9rFE~-A_J$h4Q|4Wt+J}ZdE&^?kiZQyt&PKq;uyR?)NUJ@4<BLKgRQ&r;pBcAHS!M&G%;3%12b*V$Lp^S9?MpXYg6_vH1b>^QH5^wmM;-J72GfDt8`IeSc8TgF5#m%u?6$arJ$;&iy%EawFwV&8~T7AIsC<;rY?>)a%^&_<nUgWDZc*$)D=`WSu+92JSX<Ke@HJ7xy82zvs>Qe$V#ww`1?wWah!L346lof9kJZZ=YsrzSyFkH$(Z3QS$R;HS^CbG;()Q-<(Lf@0H{{vyacy-{$$$=c(7ZJGPs8T?fa>>(*I&Os@Mn_h0RuZRP=T=k&koK9%Q3o!b{4$uo1uQ*ZJ7=y>XN?kmwL>^gLg->07Y$gMknQS%tro6h}*7UY?^+b&j}w^~1{`T3Ok-cskmQVr#GXq`~Mzv$fgd_u072Rwaz`g=}KAKQ6xlbJh57Va_Yt=}4|*Sp|1weFlzzel*ghUd<}zy>pSUzoq!%<UOfRDGMx>UnvK`aaW}+k9`Sb8B%!bzN;wd9cvPgR3XxM9SSaw(T+dI58zv|53f=bz;@HXG)=wyE}$vo4KDnFfCo3mmk#kliu8YT75sMbKm9zdm`2AT-OJSuD&T>SC3EBea<BHdzsGl^<!o9NGUY(;A_is&3c#IJ~(z$*!839?_8(euc7L9B5&@bsNacnZXMdWJ5p{x^7bCHf53D6z8M!cn7KYqom*2sm${qp<4bbex+;Gs)wz|kFvrY;sVeu)8?K(CX7c-yCwC63-;Z>z`@2`#Y&3J--<t<-`(U@(CphYT)u+TV`MT^E)$f(ACl9`_ey`NI^FUs%ncFuWQuSLKtLrWLsn&%??vx&%ZRS35yHpGHy85Z#zjW>nKeOA+El+*ml=@xF^6b}5OxkGXdcWRW_t$-#o%_SD!|0pkeWRaT-ya6J9zr?ypE|caecVKK-{?G?rQXMS_p9g1BK3Q&&fS~#s_P_O{cf&v>qH>O%>AA|{yOUSU%#i1&F}1fPakh?zjrj(>=UT9Ox3r#S*<TMyH7Ur;K3Q$k#eiX8TDNJy87MOA$JzFP}k2E^}Dm<>F-953YfX>@6C08-N(0nVc2<g9!!(ZL6**^*O&Ws^t$7zcW+Gzn0a8+xm>f}eRqzkKlPM6pZ+Q8?-RUvupfV)pz|qtIbr#>QR;O~m?rB3W%#=VPwxKP@i{a1UHN0Xtp9R=6DhZ=b`S3#bh0DW>)cy!H9nXV>3DRmkH;F8pz`h$UkW>)<obO2hBk8|<yOMrOf&btUX)|@arX68*WvR&$k%0UX^>&&ZiU6!X72aY2XhjhGjm<9bLWK)>Uc(+*&eoEo$KqNC^{ojZr2$T*2nj9Mt0bBa$k$^>rmwJVSnXQY19`LoLb^iwye@tWovAb@h3hav@9#c$baH9q1FHDPkh?6YX1NI6Q4hekD*dj@$Eaj2^T~7H!unpL->dAXG^&l!e579;IHE^!9(~<__GY*S@3f_3xACv`~ti#O8Eu+)+oh0@mukB@IJg9J{XS01s}u*<HO+?d^kP`j>HGyaj+jAhj)f|;hpgourA&LuMW%L)$xBU#qTWTVh9hyxA7qE!i~7#^SF!eW(Z$YJZ8WV4B_M8^Y}PC1#ZMs@R<zZJK@{-PW&kR4nK-tg5q^vVq17c&Ou$gBHkF@g$s7a8{^I4J$Q5ccGwfY9j{kBZiDS%PrN-o1U`Td!6(8|xZo6gBAy1P;c0j}Ou^If8E`y41D_1<$0y^7um_%q_l0-heeqVX65a~G1&TT17Pf`|T|7R8$Kjv&ar_<l1O5*F2K)wp1J8#a;`#V`_&UBGUj|>om*Ml^v-muG5<~c7FbjVSe+s^aKZUPj2>$?Hz(2sPC`B>vSPbC}U^~14-VF}M1&8C^@IG)5-Usgr<M6I{Ti6+Ii#LTW@TPceSRJp8Uk}Cnay{F^f3y^X_>cJe(8UFJ<L~3IFob8qMYx`KG8w|3U<gkt9-U!-I0F|Pf%nH-Fod^<<M8%)cbI~A$NR#WcwhWJhVVIXCq4(yfk*Ki`~<v&pTMs|F_&FsTX?l7#m2Z`bG#Z}8QzXp#&3r8@SE`xQP<|R5)9$L6z}s(OYsJ_MScTAcr0v>$KvsD2p*4*h7)nYG<-Ck3e)jad^((gPsgXi$@o-!0!+jw;KN{Fd>Gyvw!(YkP2eqf6TAu(b6gd+h5uz;n+N}52>+ybWW!weDV~e(g2(Y)_$K%cz6oCg-@w=4OJF{}1W$+S@pOC)T!xRqhr)UIP`o#sgbO}~_r{07r|=>8Xt)j^jZbF?&x0S}dHB~*%%NYiExcTmVgtM!-UxQX1^eKQ@Mf?p-VBd{ZSfeqK5UBD$7{gacn!Q1ydE!w|6wVLx$+N&@RRU;T<{hAB>omd_*R&S3qFBw#h+mae-tL+55mDP2^Z{)55`+Dgg0Oaza93+1zX^^<JB3$Yryt+4ZIHQj@QBK!M=Dsyb-()Z-m!p2)`H3!SBUq!yJ4z{xUp)zl<M)SMg)`Whmy~%dj#ohVXOnW?T&6XJ83j4B;O^G3S275Wdg4HZSjE2;WvbR>C6qC0>MIfnx5y!nSZ<lwvII!@IzEybJD!qjAAh+>a;2>3A|e2~Nc);p5;0d>ozxhv7;1K-e1}h<Acb@J@I`SOss0mxp4GF3+~`^OoW#_<8(2>)Jg29()mh4}TNBfWL|Fg-h|h_y+hez5!nW$KosSg~ekEd;pHcAHcgYgb#ub<AZQNT#EbgiSPw{BAy0c#MAIcU^e~;J{RWVbMaYl7d{J5g`4nHd^}u(kH<&CCHP2uAWX*x;$7hwyer-o4#nHzcf#Jd;1K*yybT<Ux4~^V9k=lT4B?Am9=;eq0Kdi$;Af#&+s?8ryh4;>BV4c<UIDKPWALhYG^~$D<7HtDye$5&rC16VL-<cntYJSfgntH4;(~ACpW&}Egl~acalvQsE%=iR;SPKh*Xx<X5Pm;HcrQ2@7i@+1!kaOK-v%4tm0=aw0Iz~qg}38^)$yu$S%&a(um)ZZFAwYB<?#xz9$o>j1RLR%@QScLUJ;LG2(Jt8#p~id;cUDoJ{7)<PsKOGWB6wLU3eK6JcqxFAB1P{gLnb_2rs|`a33DPpN8A;r}6pLwKZ}+oQ%)M`!IwrfGhC@_;y%?Z^uu;EBGn=M%G%frryX9-WqnnTjTwqANR9%_Gbtm3Mb)1@eyzwJ_1jGNq7Q201m_l;5O`p+jvXZ5O0asg5~jAcu6SM&XQ~k|JG7`4;OqB{}%rk?!`aG_rneNetZX9f$zXq!G-uL{Bi5rI{G+6_;7~sd*B23J@{R)8}5URVK=-n-V_ePo8m2@A8(0wf)nvh_}wrKzZ;K(kKl25Je-Ti<Ne?)ydT~Jrs6&Dj&MBQ5s!r<@mRbG9Edl;V_;W22Cog<;<fQx;GMW&8~hf$7PRqNctbb<Z;0Q)5S|DZ<B9ll@BscCei)v`591f1SZgoBs<;@!{{y3OF@*mP%i>}P{~n6<^?Qc!ui#JkSNIY587}xLegxmc5WW^}!3Ceh*W%L{!bd>|7rY-Ig?C{HZw-6lg3a*Ocuj`zYVbB(ueH?}!f$2>zmXxlG^~P`#>>E}xL{el46gqPkAmf_(ATumOTzMaN&Grk0lyBv0an6qz^{iD@$2zYFd8p~mtY9L3D(7L!f%B=@mui@a4Oybp8z-G6Y$mWU0m=Wz8cSf1$YMj5DefC;mPo6JQ+`b^KrpGcmm$Mc(jAVU>{s?0X__04!7gW@j`eCFT{U?Vm<ziZQ(Upqg&%O@eZ&*-k){114H=Ta0GrgelJYG@5Ot;0eCOGBee03cpKOfZ-du?weUK4X;>03jsI#XinUg_;K%r{`03&i-#4m6<&yu?|3$^Me~$Q|g#8~@c>l}rpS{ih^1I?*p&!BH`(7tL6U7&O33-uj5UZy3Up^<aX8'

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
