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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d33f78f60a245e0b4cf812637509e9a/part_009.stl', 'relative_path': '4d33f78f60a245e0b4cf812637509e9a/part_009.stl', 'source_sha256': '4bdc837d078ed24c50ece9e88b77e834af6561fa6d83c1fe24f8df47ff64a760', 'input_faces': 896, 'input_vertices': 539, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11100659519433975, -0.49688705801963806, -0.16420632600784302], [0.1275944709777832, 0.13962623476982117, 0.12780360877513885]]}
GEOMETRY_BASE85 = 'c$}r23z$t+|Ht=S-EX;*9J;uNq)>9y43&f=No6EOH$^v1a=N{}q@tpGO(jwo!wd~E2Se_WqGHCNTtj!|*8i+IpWoVN{hXfX|NQ^nXFZ?KeEnKypS9NBd+m+4caNmx8ea5QBk!4E)wY#w=Xs`8^lEqy4;}g7@F7D-oqyl`qZ7QUrMdYfeC67HJ$nyG@E-Ouo7_Hh)R2))It7|sdPj#QEdx#N7%}p}k%R9WG-BlKLrvao@I9l3M)Fa^2H!t4@^jPn?K-v$v}@KfFedPS{8c`32w8{j`n({*jDJ?`FbvH7eR)Al9z6AQ{QP8>XrANdffL7z<K@BQ3*zS9u~DUYkUad;weIocb}Nj{gXF=SsZPB;PF+uaTD=_qJXKGgF~_a9-%Hhd<htH|UsWF<*Y$QBbpPa1UvjW<X<l+{hBKa$>+vi(Sl+2G$>~%WFAvR`<J3z(-dwj{a;eWcbZk-Ve3j%*D2&bRd}ZJ4)XTh_Rxk6V>zS95d8%IKYqnc2^QG(Ue5rbwFI{ivOV!))QO9rRi~5oSD;LF%b9nB<g|T^9^6Uqldg-S`)k`k*f&EW7;~&UdRv4T6<KNV&x95wlx8tws<$TFi^>+N-dV9X8dVl;?|8l;ldVl=gdb`eb|91SN_1=M-obmT^KPZgNW&A_4uXO6ApMa{j>!13-zFiBQ^`BQ<7@N!Zhh|rF>h1d1_2j43%lgk%_2gNz+<LqIRlSVAuD9!7)yw$ndb|GB@k?&&_itGkJN_BD3kzd&8UMiSHcq`AXX-QdTphO`$#p-HpVrThm&Khg$@P5MT+NrxPpen+rE?h{$@P3muIJ14qvp%@qvp%@qvlKJQXk&6CO_W!BDp?aB-iIl*6wNfvEwY)8Oil^$>!?1r1R72)pbedavhLdUza4;*CpGJx-Qv%)OE@BqpnLjm-_I|Tb*&1`-0^9z96~2FNAlV=Zv%5PbJs)Uz@A@ug*`aSNC6?%l%GregBnQ-+ygC>i%o{QTJclkGlWr+}?jn>N(?V_dhC^{Y+p-qLa)1Dp0)TGiN=s&y-y6OKq<9r8+;YUhPYDF8e^q^}bYcy)U)>sC}vJN9{{(KWbm9bE)@sEOf_*=LO02bA-*+bA;sjIl|Vf=LpG9+xKp%ydZi!>zvP(JbdcyxVd-gUgvlu51za%ZXP;OC2k%*UgGZ0w;Y}ydpyD1>k4D@Ah|bZic>Ggsp}=z^>X~dd2W5l$!P9nyY=$DbiL%dUcRrcmt5D&IOuxGr9SK1m8E&siCXS@*z$>+vkoN>k=y5~EiXFboRK%JFgCa2oSo*>%XsQ~JI<<J#yKO`t+(Sm+pU-J)b)0pRlSU-uD9c?>Sa82y&Y%jy>D)C$20fE!r0u7C)dxw*T?dlbvu7oVQlV?XR1?g*R87e$J4F1>o(7=_s7$%x9e8b`{U`>+jXnz{qa=CFY8v-`{Nm{&)BpjFLpeGxrK$Xxr}FE_IaiC!LP1%#xpcOc|~k4<5@Cm&$8HD#!c5tuIptyLwRn!jAzMAw_e6g*W2+_{mZ!NdOM!__!&1{Z^x7R(8f;AczSsyg|WGeXJ}UW==xtjB{yEZ<hnj<!}#2I<1e`$f64Xu>s;6C@t0hWzx`Y_{yO(m|9bp&uIu&q>s;!?>yFKfx1J@}>)BhgWnS!f%K0w2zCK8<uMaxc_4@iCxxPNw&sEn4o$GpiebBkC*VhM~+xoSSIpb-sx8(YI8(e+4GoErkl3d@vB-i&Zo$Gpi|B_tazwGC#`<Kpjy}p0xT-WRSm(Ha=<BR6*c(NamT<-@0tINCf>?=Ym_sn(HE&D6U^?popy&u!LuGjl9$@PBBey-Y&>0H<A{g}>mz21-MT<U{gEOW+3_Q{g#{j=nH|17!QKTEFn&$fTHf6hq!prDKCKmCoRr7Wrt?&9R{mF8JR=a%Mylxd}TIPHbfJXBOg<*$%8b8;{JqtZO1sGO6B(r1<C!J<adJoyv)c{2LB+pDSkIgY1=lY8l}@wx3({vrLhb@EVpc4=Nx)JoOoFb*m1=cX^9|AwV`Ny=Pj95RY7c5*L0-#yNh`O!S>A^NZB<iWHt(Y&~|lZVsZqMt5qKa6L%=n|FZaGV{TJe0mTTE9I><;zR+KvDf@p0vanf7=hamp+Nl?ds&A^hM4%*nZMiP~U{lT}l5lqVrOm&N#1OeC}nwYCCy2ZIqfv>eI(DZda&0x^4r-SE)QFZoQ0yzkb%Z$DjXCft#<7uAl97qw}7+f#V#_y6WuYvOa^wJ)B&|O~%vqL;wDHw}o{wmj1gtc{uH*=<yf#bn;O8Qnh}lPhabdXI7c-InGa=eo9h{nU|sJ`xbLN!=vMwcW{ZD-|dX2pO1*<xqDUpBhll@-R<OZ{$>^Ra*v03^vAQ<8MjdW@dBs+Zr?cTsw8C>pF6}oew#nwjGLcF&(m<;4yRt$p*>EUzr%d>QF*?5{N$nZ)$aO{&*k_tiq2*p_o(&O-N|LWdBuI*`t$<#ys-IZb$%U)=2zSj&F3Fk5}OCpo{o-l-ZsYJSL*vm$0zqUC->3@IoBCKAIiA3cXH|9AJ1Ri^F42?+dtQ(U~xaEK9oNFU-DVb`1t+g#LeY8AmeP0v)h->b=a?uj;EJ@w7{+3rmp{gI_Hajp8n~qf3LW|lZVptoONaUp?_H?S!Iqn_Z^vc$>shf<74Z&e#+-cF4rshTt8p!T+jV{t8-r~Nj=5!^mW$>xg3woua}e%j*ib*=W`{O`<kp1$z}XyUcAKU{XBd{pXhPs9bFQeduan%{|%ga|Nhe7?T71aICrztkAJ=G<<`sfmhtiHw>s;@ODadc+_?^i5-V{0y`1Bh+}@Wto?voyzE@AD-p>a(-`CFvI{P<2AMBi`etxHO|B_s;pK^VZJe-#4oL_$aoHNdT{z}~MC3!~iK&L*G{{Fw@vsnKF+~c>`;ePJta=y#>+waBsF7xR3zt!0<`Tcz7%&*_iHfR6o=S5s6%cy>KaR03yH<$f$IH_jbagbbp-%wI*#&fb$FS+hV@_+3|jhmNLH}1N%xte#$^?LU651r$&{jfim<MH$L&U}Ru>pSaEt|yYqzFO9atyld^F85`bcQ3I)-1RTHjI;DFx!k8t&-2{xWpnrXU_V!_t58zIxYswy<^C?`yI=2~?~==YPtJGS5BqsLZqg6?NuB%m-~KAkj+=Yw^ZupYy?)x`WE|u?^7A6+{;P92kG!Nt@$VPpr`;E%Uf&mN{cG<0lAm_JkbcztBAj$C<L}-FC70(!>0fevf3)@L{uoMX!o0ipWj}ZK50dNqwa)$P1O2Fdh2(l);pgtY!q44(MKHMq^X2Y8CD;2;KX><^lI#7LtylX`KX><OlI#7aU+?ZS{d#v_XTO))Puk;D`$?V4J}{ir$~mv)e3xABw{5-JS4*z<&ywqXvh82(ll^|Sa-8K@|81S?l00|VTs`kduAfIF*Uv$=AN3sM=k9Y*Fu5K5yU&S!?miDnuAc`b*Uxuea(m~xD*gMp`yA@$?(?$b`gzmO-RDi)k9w{QC0*>C7xKLC=d#~x;^g{y-_PCWecO+EuJ?2I{ez#o&-;?==Y2ol?5rz$JnB6_IJu*`u6B2F{a!_K{a(e^tM@9Qq%LaRc6M_8UPyBNUdZ;N-V1q2U6~j6y_w`P{<>bjPqY1~_i29azEAV}ao^+l^*M3-(eK%8Kk7Z3U%#5`TLo3`zJK$QxlgM1mXhoDmXhoDmbM@D-ZGrb_g3$3CD-q7CD-q7Z9nQgt>pSWt)IK^X@ki<oOLDp7C(32OG~cb8~eHYzFKlw=klIEn9|D`XL&#G=kEJ?$@Tkr$@P19zutWhZ~Is8;ls&&-0Q!}_4|Lx<vweVKe?|nZua}y-2HP6$@QOWNUr}}!%ObxTu)>kCD(uc;^*(EbuPL4=Q4i(GyL`0+xb^CA1>{;F4R17XpvUVtKr=-IOd<wn9%$Z#{VZY!!P__{S%rF9WVO-{u3JWFL^GGw6kFo{A|1$tc_R0Q($#G1+NNg;Z^a*@I1URegV7)zW~1+cEc~nuZLIR*W*Lrjrb6JB)k(hd=h^!(uPLb!;xmDuV$pRhv(uZKZDHFcBlR!cn9o`_lH-Sr32f;JMi{+4cHw&2VMxf<A!OtIffg^%=h?jq&-J79)eHdA^ZV23V#5<4c?C5hWCa2@V<Cgcm>`SZwuSuZSh9%Y`hU(1y;kW;K?urPsS_5s(58Q02|{0ybZhnZ-WQn<#-Uk4qlI6hYyBB@WJ@~a3p>|J{CTSKgryTr5XPZ&G-{Agg=3gfDhm!@C<kxo`Ls)eephc7uXf=g13fk@z!`l*a&ZkSAtdWN_Y}X#*^@hurgi|KMMx%v+(m_8~l9yG8n`!!+XQ)@ZR_!I2a#<-v{r<@59HyvG`c#W(>{vvozz6!zb{^@q6J2{9gQ4n1SDl_kw-!UU+BN1@DZvg01mZcmvoFZ-7^TmGBC9B22;)@$#@DULHRao`s)@w}j{8E%8g?W%#A|wXipSEq)6egx`YS1MkD{!873)d<=7wNi+To&G=*Rar`m-Zg?+#H-0m`6~7tp347r^@k?N5{1UtcY=yVL>%#_keY_m3fS1D)U?QG?mxbl=vUojsCSDJ34qM{Q@lNnkyc2#6ycWL(9|&*32jX|Zd+@vP(J&LwWNt>&j6Y2?{wRD5e-s}M@5YDYH^H0noA4g6C*A|^2rt1q;>}<Sycu2>*2nAOWnekH4DP`M&;MmS6_&+Q@j9>`UI%Xqo8wLK4zLs60lykvgI|pgfCKRX_%L`EJ`8^Zj>bnbH;+*B2tPl{96U{*!}!b&uqhmd*MX^wNh)KON?ryI!|TFk%uzGuuo-y|I1C@gvGjn$al@PNUnA{@Nc%m~euF<o+E%za(!PNC@JIYp_)es~1>c7Gcs}*UKY^b`+Df<zzKy?4{VMo7{yWFH3U0yYM%tW6n+iX`r{a_0EBIu50(>5yfKP$1;#2UC;D`7}_&k_{&%>9(0(>dH34V!h!gs(Td<T9A9>fpfC*U#s1fHA_Wl}=aO*4Kxk{yV&pCavVcpN`Y{onj-JdtMnFEZ2bUo_+U;X!;qz6}=P+wk@9OME@P7#84*@obobXXEd~5ApZ$m*K1U%lLTsJU$+u1Yf}?;aTtlJPV%<=isyP&uPY&z`6JmJRE7uU@n}C=i<}gRD2r#8k~&3hQ9zO;4k2>!zuXd_;mOYJ{`}4^YA=;Ib4b_$2Y@G_-1@3+=1`JkHACt5&RT9fuF)t5~4I~H-%>WB$-*SCuznH!=LcOcnQsTF+6}5<J%+cd$<oC!1v)t;orESIX8~-v+)F)@juDTdGaUC_+Gdl--~|-x8dL6YvFo)ExrgY#uwqUU^YGre-FNozlTqRFXI#Oad1374u1(w!e7GQg<1H!_)It(pNTJopW_ShH8kVv;1YZtz5#~u4fsaSKgTxGjDHnrU&BJU3@^mz!(4nm{xO_}e~iBYU&G(PUxY8<FXC^)*YP*;8E`s217861@CEn^xEx=Be*-t;-{8C9PJB213p|4Vf}72l;VIlS<EhY`hp9B<|B#vU@E@A-pW$KrXM7hd!FS<b(@K~h!(#j^d?VZ*Gr!xJe>sO`Js3CZWexlmevf~P?}7X9J@_B+C~j!ZZR6%#-W&6?;U4<j!)GppGvOZmU1-jmad0A>iO;0o_<PWt$BW=vI1!&n{aR>_XD!@IZulMkLL`4Q(n7SU3DN8mIF+`XEEg`P{Xn(^{y;lQ_9Z+@OH7PrU-NtBXVWSrMzinuy-H*?5~EoOzgL5-c49Q!%J0=CJ0mfgZRYpRAS;&`&DQgK<;YHvErh3NN66;FBeWv2k6{sQ5!v%_5$!Fq`{7%(2gvS&576!;y93@y>p?ac_Mo*RyBfBmH72_fHm21gyA;-<RU*3(R-%<7y9kz}l_9$rmZ4Q3y9`#Kok4aLJcCxB>{?i#)|Biv*p$|ZY&h&h>qj;M_M_cH_9(oE79!glX}?C=H#Fn>;BkB({u4AW6@KDp<G;aF+%)6A!vx$k<A1;t2~juA_#yZwehA+W58(UpEs?esegzNUU*X$n#t*|k@x%B@cmh9(m*E)Av6i73uLx7|ig;D%;Z^Yp(2QLLem0&0f5lBRevE7{ehfbtY2U&Pa4)_A{{nu4e}U)GjIV<G@KyLm_!GVn{~rE^e~<5kzvDacUGNWl7rq-F!gu4_;C_4?z6ox@H{oky=6(&$_-Bze3+BMJcn+QqzryqJ6>vMg0xzT)-vbZhd+@*EN&Ig-DKSd3ZjxxmE5nL-WxOV=ir2*J!U}j@ygE$5tK;RNSvTeR+4w)KrGxlC_%AVQ>ld2w9g+4qTnxX(7vuBb27Deq8-9V$#%I7hd<H&+X8cpQ3jY+(h8yv0d_MdhpN|*7op=ErhP&`Ez8dbvSK~|JHhd|*3~s`g;S1mzd;vZOeumG%XD0Y-cP7pF8<931PK2}YiTJB92Y(fR6XxS@;?v;@d^$c27UI+Jk7&l%!9Dmo{73jV{v-YuH0%B^el}i~bD=U`7Ow_t;??kaur6K?uLG;&b?{oSJYEa00?oRw!q3K&;V-yp#(yT;f&YvbC-~<^G0phONP8Q;13$;#!QX|8@ptjba2`Gxp9E*)lkf>}20j6Q4o<<J!=H_`O!!|o1vmT@&x9|+PjSO+JQKbQvvI@ucqV)e&c_W4@J#p~EWi!JcqYt(Vcc*vo(bQFt8v4ncqaS+F2xO(;hFG5xC}R3fM>$j;R4)n4xR~Lfpc)fnRq6A3C_d~-@r5BIQRxG*M)J^82$&2$1~yMG~;97czg{01e}OJfsci+;$!hA;hXrA_%m=i{tW&!oQ6M*KLtO+pTgx?%=lEeF2R2mGrk=DnBYH)8UF$PmEb>%89xfmwML%B%JS@0mTQeXi&f*<s~XoDc@{HX1J+6OpT&&VhP4v?XEEbvz$%IUvzYO6FgekG7Bg<1y$sE@MxMotAA!XQ{<E0zBDgZae-<;oD8auT$+MVodG<0K3E##?;-la@_$d5A_%8k+{t%puKZHLFC*cp{kH87|Blu|e96lO<3_gp?waj?iNNW;lm(z^5ferCCcuQChZ;77=>*D9(jbI(T5q>T_3qKcc0nfo(;H}~Lcx${%r1gYp@O(TC?@Tk^9G-(W#~Z-2@CJAdSO>3xSAli$DtJ{`53h<>gAMU&cum*@uZag>TRecbinJ?Wci0y1j$aQi$FIi+(Tw+nZScN$H`o&IhIfVM;a%~Luo2!7zW|<#Ux0UjE$|L_5VppHcslHYr{le1=Drur_|1_v3=V-k@gev?n1&C;`@_z7fBYJn@%FGe-X1?2Ho(uuYr`6NZM-t9f>*}N!>V|ByezDSm&Gf>ns`OLIt<{|@iSp7{7k%Ag1@$!(TrabX*a-|;1&2ycn0i_XW&EO_4rWyZa4_P8^4!k{4UrRzYD(|cEfMSZ-rg)Tk!#~BR&AX4qkv?hxdUU@IH8N7{q(yH^OxMM*J4o3-8?{A+bi%zx`jp`@hUR+jIU8;q`y%{<YWG|FT=8FZ-8Zd-q5w{W}1Ok^h;$$d+LKR*m;RKWMTz'

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
