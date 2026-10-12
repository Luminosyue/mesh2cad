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

PART_NAME = 'part_018'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_018.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_018.stl', 'source_sha256': 'e95c5636e88cbe3b1dd97568aaf60c8c036832806eac23a527134c53ab9c1c1b', 'input_faces': 668, 'input_vertices': 587, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11843379586935043, -0.2359306514263153, -0.25453850626945496], [0.14090465009212494, 0.2834339439868927, 0.3996196389198303]]}
GEOMETRY_BASE85 = 'c$}r22ej2h+qSb09YIhKR4iLSx&k6aM9u~U5fl-@f|L!1{@N%iqQC~Es31+S<3_1cq^ZDx!xj~#9N-{|z>98F6n)j#g1vn+$u%)~GXGlt`aWFGy6;?hGMUUwCfP}jT{;yjUfJ>fUEt&{tv_mNbH~w9&Z+F&J7D<8A$bEvTzu!<_s5)yF4zBz&gtC!x-PfIoO_)IYWE*7B5!!@mhsxH2DYf(AYOamUBgEX?|WyTyN354pn3bgw~rX0_=v%M?;fC*>ojfAyg|H4-3IY7@&Dz&vZ@Nnl{XY@Rhs$rl08}z_w{mB^33Ujb_IDNuYRG{>}?(Q*?4?^!yQ5H^eo(M%QxKQJLeW|aq||Gbob}9`*?SdXJ$UW)7{Ta-3o0yRWK}+A1_;TXRw^axIvrU^7r=1xZ9m~aIcLg|Mj(7pY%5$=LdPB*M<9RJX3zaUK>w7*k`AWr}p0OmY?X|JKxs+lAHE7T(-aDracXp?Jv2>Pp{4Oc>mQ?-MoAMI+z>eYtMdBFK1SkJ>Y8Lp-r~-k=(S8<feTjH|-O@qI<X;`b%=tU(V64&$#OwpI@Zw=X}<AXppB{*7Eo@cMY@h#L>P%o;|m@#}_mnVdXW~^bGCyiVoKDeJ;vRx4%AA&-7EjKIP^Qs%+;Q&-3__>ql65xyyP6xnIxXpWhJV>4NL6`RR&1!u#z%akjNShRga$Zpw#8>I09|$8b@fZ1ruk-2VP{lsCSQ|5<3`nT6Zk^CeyP(dq7Tvih!IzT_r9Gk@%~Q2p7j;mK_mdi?t7!>s($1$~3uKVFW@&wr(ZHQ#Rs_8YHR`VqIBk-PS3p7?Xdax4F~#7jY*Ok7oD%lA3?={c`FZ0%peW&cWU`U~zKZ=Fx?v2xSz@JPQKF8V!HZl=e(<hjS2x@^pH8+X>9`BIQ)`>!an<r{ADvsX8C=ezWg`X0|Ib+?u8S=m3x<IlFW=KGxd<V8!Txa*%Q=GFg!smpCV^YMWtL7uGH&zf(z%=g>5`KPmUEj;y7`$a(>A2-mNZ@9^Kmd%<HY`4TIm%8<l+{sD0?U^~Fk;gwDxi54c!Q)3B@_6ee!>s(K?)^f%>|AR(*_j!4znK%YmRou8yWILX<%><RjdP!iaUS7}Ps8Onk8sAh;c}e&T+VNkj!q7a2d8({B|&cb-SE_V$0xZw39r8W9xIRc=^EmDIu}{<4VU@HdU|~PwBc5sZr3Ns)6Me2^T}Cj9||2;-eZe{+&?bC{qwzN;}tfZnc06?sQk||E>CtkJU7?E&3N`X^Jl79_fYwUXTC^;%8z&W)>^*dvV1e&%JL1D<@@uMI9~t!a-Lsq<B6|-vX&ERA9G$Dp0M1;ol2Fw>&Oq^Omx?a`7pwn-wc=YVT7CfUSlWP#%+W%4t*}hZG_8wF>WKAacj67x2gG;PYAUe^Gt*@&!isSKR(ni%#)Ivc`{yN^Z4L-Vdi<s%{(u;v+=gYK`yTslFM@Z^Nw<y%~z$|cDQFa_b2lg*?8uRTb8-!!S%0=3!SH2XC*h+S;OUZS#tlnyt9kT{of<K=N!rna(<5_=RW_Q%g@;`HhBJ;`=1Es{>N~6zZBsn|M=5mTov<-<Ypc)T+SPk%Y1nqmpoFwxQ<Ki&r3J1813?h*l)kj-TqB>dCukXdTqG8UPn0BYoCkjb^OO&qulii=X&+|@#XnJ9xwU4SN{`hpSSY1%bpAJ?2a|oe4mT_bp8DBehXIJ7i^zIy&4N`JTs^4+#pXk9Ba)tT;^wIuC(SG9x1=gTVDR60WaEk=DA7p+;)68eQ&TIoozi{&b9DF<@Kv=JlkOOT5JBk@#|dP>TK`+eaa!P{54Bnw(-of(^uPga$$O{ji(3q2$%m$sUmCn@JRXaNcnJ6e(IciM!Niqy<R;xHCk=ssmXt?4e@!W6<PD)Cf})g^GI9!OK#d<a?}2ieA+*=?;G!Wl|2$_f5}bzNN(Cka??IOPnRgNmJg4V508`&H|587?sIwa^@X8%#_;s)%Zq|M{qi+lIc@ic`b%=t{yuMAp~#vKH~ERV+uV6eUN;Sw*FnSmd9vZ25YOfg4b7{Prwdvw4RSeeNN(l<zZ@}dNG|i`ydk-nH?nzec)wFG86Cck2yW`1-I{xQXq?yhcDuXX1!oL#d6j}t`xu_Rzj{%SJ0->qcI)%myP<M?en+{YAdeqeF(}wRrk;|Udis3RG%vq>N$<KK`GSt~L;S{a`>pwglb_gkx5p1v36B%OGfS&24Dl14?fGz%pE-4Qp6z%g_m6k=n!eWKmE0V!;qrJTCqF%>T3=hgXQ%y{bkCQHX|LaxJ-*V$)A1+PSo6QiTOZ`vyV?}l$}wD)<L6UOddUmk{riNaq54Q}%8BI5a{g*jWGx3CDaYhfPQ3NxUT*u<`6$$Gh9~RCLgPH?^zfd0wcWbU%CEa1l%H<d>lU{i9(c~pj~_q0!p1XqbY5lSsn#vmSo3pET6wB$srA<Ug4aVlS=_r%mh~}Q*2i#JA3tBz$Iln_@$;!qvg)#%-F7Q~W@wy8IOE*#_&YVM`93E<^G5NT+;YBN6l#CT&GAZZjyICe@ka7F-bg;j>vOKBk@~<R^)c69Ss#-x>tpg|eM~;}NflOgpL-=Y?GIls;Mw=ehsJZ_n}e<0at`0;m4Ew_i)}pf$Cn|V{Hnm3Z@9@%7o1zr+KK*-mfXzGhRff}l1K7qObXrS7@n^6gm+)})ASX&7M||;%qkmq-mbL9#*;&<t+nyY?Cd%lPc%ERKE$V{?e&32>I09|2Og;pJW?OCUs0cUvt^<C2cN(GT4?<E?ObM$mCO4yf4?11FS6$Etz+fcTbmcz%E|tmD6+Mi;j-Nfm+fY_Y&XMYyZQT-{dj9fYkdrl^dmgdkMKx8!Xy1?_ABa>eX~dSe%|DZ`(DY-eXQjE^9sSu{g2;|V&0B$bN^Q5=(n0XzkL*X4=A~L59sql?}xu1fM?$BANmeKa`PR6;fXdUci762?=dC+=RIcST=%%eJSn+9@4@9fDY?maj@7!s<zn78T+Z9h&V$|E^2Bvea&z60++0T@`CLb`^)}p`Yw6zzH~rhH(Jk(F;=V|7Qy<AqeIohPCsAQYPq&`pKF#OiJ}o=zfxKMHc$VCZXXl0<gWP5D`$BT_d%@@8_l4yC?~&!_3~}2<{9ZF${$7js*gnkV@;NhHUIz`A^RVHO=VpSNc_91Pf#GiX;<<t0^0|StY40dEUp!YdTs~KfaGnzyE}tt#xX72!6%%JH7#(T{>X}$PV~kslcy27Y|2zRMpBqc=|4uxXKh`ZrJok=po?{y>pL<8R$v?fxIQRI)b9kSN=kW1L`7W351td4m`3;xv1tj<1@6T_aa?26#DJ1vbQ!Ja1^0ccrKcr5~bGQ3^%lP0pH}6d(H}`>(`{x~8zJHNimJ@mZa{Gbt!Q=JcvkPwCA0_^7I>F`Q{ZxeWekz@rGSTH@&J4AK;pqd@LOlE1x`#r?%llcw<$GJh<$GJn&3j3|eEB{_aDV<ZT)elH+`LycJo5fUa9O^5Z!5VhU%t1M+`PAy+`PAyJkmbmy{+Wty=`XDN0USS#diXR%kKx$KR2FY8$S`w_{lypXNqlnN^Ztyw!%wOZ0DEc=DaXmo=1|K{KOrPJRBNt%o~!MdBboy&q!|aoswlA363i>PewTNq~UU2jd1c)4GLWz@9u=oJHyR&(C|#jXQ#U=zGsu%zi;eRW|sAQhs*Ol)vCbd^1f7ZQ+~3_RPVbXF|Q_v_g?On_w)PSeQ&=W-gm`<rzRgQv~lOL6T7Uu&QO=9X1wp+Z<_o0u5T3Dc&2%5caZz-Ci4AuBR{cjuKWDYd85MaVErXG^^fFJ{|Kl4nZL(*&ttwH?|tX|{+K;hzP`QJk3a18-p@3AFO(nQB0paLB5S_S$<O>SZMC&Nl9Qh}J7<lxeFXR0N9LRMk=(RT!KyX3{*~PHm*KL1CHM0;ox9dHJ|#ExkK|MT2&ew>OFrJ{@+KR-<6m{r9vjabnHS1WKK=V{TfX5YKXYZbP40OuzKfRJd>0)*@PW${1&M8LJ^3AKxcq)wa`XMR<mUTr$^GxQ;i(hfZ3yl+yZ=v@Cy#vO9dBOKJvN@MHDgzhoA3NH<EQSm@l@$nJA>S5f6Y6#@(uUPf4NP*%f)x^J{RA;r~3DDx%_Tla`WB3;qtqE$<258hRg5vB{%t*=~MGV{X2C-p^YbU%Iywvzh6YY;eP&4oAYhsS#p1T!sU3D+~hl*c6jxCedjyDabkG9$NJE?&7M4#ZyUFgn{g|-8Ml)A<MxuKn}hYqH0@Vt<B4wlb_cnsr_49p<Yy-h+-y64B{%19qEgc>q4uf!WTBP!ZLmAY{dN=iJ{S4^IQj2sd#wDz^}B-HA15N;=O(|!UYE<i>oHvZU617c^E9~pyPkO276sP+65Q`Ec%;7sH~EPjHx}5=cgg*~(}73+PDgP6?{wgizta)ipC68-L&s&>!EkxLB%eA~5bQ^DzDsV-cf;lUAi2p;41RoTsC?7E@W}jMx6C%pBlExD{`?G&%>RP>^FKT?{|oMx-zD@{d;>>UJ-+XJ$I(&7sq75w8~77G4fQ{x_CMhpa_RrqpYSzn*5d#ACw!;oI8F-{EmbsDafyn&nB$aoJT2pRp?&|Dr#eUbMoJs1=%;)s$J3II7uxrYd8%{zvRxy#)n)c)yHfamv46@n+cjoeU1neERT`hiJ{nW!?^OJ%;(PQr{0}NVQgIT^;@?-XU&R1jH^<XU9WS)+!@B+Wrg~f{ZQ^*L{XjzdgXp{XgZTH+{rDv1y^HS0f2raN6`!HU@n5O<59|NKI_*!W_?-2hv+gUlInMgytUJLvv)z~EnVc`k`+{<`|4GF+Dt<)24)~8*)_M&8t&0Du_yzqLpQYVDM33Ti`G+a*FlA}~iHakXafEVAx&LNAT0g}frSCsPzsKu(9incBsJp52Vb&jJ-7(7hgfc&2pJrc2Sbv0d+Uqe^HOCugTF=D)9`nZBALvQ^M=T#DexSZTu+4YG@06|etQ^m4ts3xp-P!0Lc)kC#se@L{e<S{&UH+gx-xDWktCRGT_Lr$`o2#gRmdBT8`Bbz8zO;%CD$1fA@g-EWQ&AFak1tD38T1-_Npeb~9q?tyDTQ8*FNH6Gw!_y^QBOs6v?jiZil!>AKwIOhlT!^n2Y&@Qm!i$^)yTO3t%1LkoH}Sdd~FqV*?(R3-Gpswu)YTCYE$OlF^_4j#Cjc-$kSRMUl-pL&BZsxw??nTx5hW4e7(QQ?6)SqGQI&?58nWvK%3#4QD%a=>2l9Ni|2U0KI<+*&%o;(y}#n@w@Sb_U|H+M0iR%5YukXol4Y$|1$-{cTH6GCeU|G}7wu11bGyErS47XiSHz!&R>BukQ9?xwEsl@j9W)1jj*2r?oTZ|?qyN-jof9g~RdKe8YAPzII90_d&OhhgX@vHtqo?9e$5+hpuI2jNY(;2)Ioce5IbNUZf2xYca=Z$jr{Y2t=c@Qi@nTAIRK!)(QgObD=TvG{70;qo@TaJC<y1To^YqD>=Py+2YN)7*UVyKOua2INua1us+MlOly^6Ie)}gEM>+ov`?O#?gUG00Cibv5$@Q>mjCbXZb;sX^2RJ@1o!@q|wLSMoc;g=KIKd+*tK4(=V&>Hw^D!Qwvk6w?jqT&h_wa_c^H|cXzMHjRI{&YP@tEi6V;?GiXql&udb@;9-&Qx(NS_fZQ#pNn$qHXZ4^tr2|EqWooo4&57=#19GpR3|#6&Im5;9IMxs^TiNHvUc(BWaV7v{!=T*2jMrdJjIA<GceMfxlhFC>7VJXo#LhXx|YXg@0R(i4Rrmc07NO<((?tRq+P?-z?|Qce)R?FU@iZ+VD*LDJ<vEH>J_)_^p(^7kw9BjJDNntbG}l3)H&pD)yl7<4e-!y6v?u$MQDE+h#wy2VaW5DUV)+*L_i({?J+$uiNDV74OhSAF`Z*?L$An>oHl1aaoG8wSSXs4xsz+RoIu_r}nj2eoL)8s$!Sp`S)1fp`u8|>-Zxq>zpm*X)VN`MPKMXIg7Ecm$y(xAzFmjV_+-eU@Luckan&{`)aL^-$h?+r>;j?-bUSa;P<m!nLgEhTbXmK4DIu8#@d^-jb8q*ii&FesWDG4#_Nd1y!AS?|4Qk%j;9q^*1Q7aU$1M3R^a@&PsP7fv`4STS41yHug2f4;@+5d&T4IqPpO!wq7&Ky|Bd76F|-3-hxT7PUTEKr(0&{`5kFkTFcrO3T!6+2?R%la@QqY7R&fd11V32CAQeN=Apzfr<woQVVcWrMKbTzY=cqbAu3{!S3qKQoJ=z67Ld8fG_o1WkqgY;qzK9>e`WMiJ_>ru85q$w~%36pn!jDnWTg5H-6w5cmdZE4X53+6?+6%AwG!>8G$FV#EHXWUYe_F)@u*dKZqSxRb#NUi|#NUj+1s#jO1wRIT20sQr1AQ9*H2a=Gq{y8?9rf}JD!Mvee|DuW=fLOCcXQ}h?VnUJU&T{|_Rphf{PXw))Mo*8Spe65n2LKS?@9c8^nUz&yxAsA`=#LzPzSxg;e_`0q6_f%;z!eNqp8>EKplsZ*MZRf3UoC73Vbg8l1q8HfwDW0cQv7XD>N713a`IOyaw%vnzFAZZy3>vwrNG)Jw)q3Tij21_Xo=UNyU#UPNF~HFJSJ_>$Uz!?s>}VoAkf&=LeRx{)ztOc>YrrpQ$)bX#cs2FVGX{XZX!3HnDzFAoq*Fdae0*tsC*1@te@s@SE@(2<=}*U%{WC4*BRte0LQ$saT3G!*^40qlzWy;(+hYa(8kUvu!uF??&!2^1G4SjXdoyVICcV4#j_>*8NAt$LN>%?^S#U`wp&sitEf2Li<|??GHQuT!#)5+P{Pz!@q<-gno@bgm1yMN?)H^aGe^5Z-JkTPQ*{fKZd68De9{Iud2-7RE&vvIyUBc&3|T{)?e_SGR|&|dD<i9`G?R+Xb=1^Z2w@)(+6Un*P;DbbPWD?mGg&++hU&fjCo$`XuQ_@@p`^&7W1xkv+$P^+AlyC;uql4=!^KbSobEH#=oLsjf(Z?YWz%=XQQv+XR&?;x*9(NKNDSppUt+j(DnEy)UnK0IuCsgze(xqDz?Nt{|3vi<1^?sd<MT6-H6w^G~gGrycE9-U4q}GVkc#6!*4`4;5XtIqtD<M<Cn1Q8<e*TpO0?B=i{G6m*AIBj`3Tl+Y<7&(5G+HuUfYU`uIiq^hNla#CG~$Utjh8(hY?6T?y?6p#$-Q@OPtk;qS)JMQ7vZ;<M;Sc&$xip3mZ&6WUKe$K$oWfS-V0gs#9Z!mmUN@GJ3K(YNqh@o%Hs@lUCETE!gnar_+oTy!3OF8&$xS^O%>T8qxXuf@NL&c(lq-+(@Y*L8TAeQI5Ye;hv#eGNYk|16r1*W2zOS8E}D9sV_RFa9-rKDrC9w|$3Pt-JAs_`T>J{9gPnbSM5D+Gsbr7QY+62YnU42fq{DfS;<y&%abmMu*^g=s8=@r|50?6|7r@_QbEkuS9Rduf#7$Z^bXiuRwd?uhrK-6%)|$0e>CKS|<j4XO^`-6!6!wd@W@>M1CjMcVb;<j#(f3By=!dw~20}JJ3h)ci`_tAI0B^za4!Te>;9CIt4!zKNy{a@2{eriabL5tI(GCtMHehjqsP@8#><eN&PIc9$FV)m-Y3~M)(0L+Oz-u_;%>!_;&b~Xk&a!ye{iP_FW&Xhp)%_`e<W(9>>#{(7r8t8NMyP1=<kb0)H{b80Yx3*1^|deO<I6zAxqWA+%4RE$|6^GxTD7GkgQ~bsqcCS_@x`^>xsT@qH*aNod~&ZH8}yZ;m#=H^*PZzRqVqT5IELv%VJE0H37XeuVZ{qRsJLI>mA-7yEzxFMa>{r|%1$(Es39ZW;cJAh_jrRhIuzL6=S?^t*8<NByUNJQe9*)Xx6^=rRUE'

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
