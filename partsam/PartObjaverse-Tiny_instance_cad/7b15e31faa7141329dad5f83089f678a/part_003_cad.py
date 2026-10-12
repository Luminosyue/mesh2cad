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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b15e31faa7141329dad5f83089f678a/part_003.stl', 'relative_path': '7b15e31faa7141329dad5f83089f678a/part_003.stl', 'source_sha256': '2b5e36ff42cab5588742b9182752fb0d5b74adf672b1dc1959d03f5c1e32a7ef', 'input_faces': 654, 'input_vertices': 492, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13152694702148438, -0.09127296507358551, -0.4197501540184021], [0.13007456064224243, 0.04696473479270935, 0.12600629031658173]]}
GEOMETRY_BASE85 = 'c$}r23Al~bzsKK$BXcrGX{Rz|ibN<j2{}lH1{t<7Lm@LoJ2DSB<{@meb2yH0IF2|wWT+#`JftlpDyn}an*R4)Ykk)H-)o(H?{lAfkLUM%zx(s9{aeGk);sP;n}nRXiaF}<e&@ZT`L2hmIgW?|PBCYAufaq6_UJXF+JHf$;+(>gi$AS%T6bvG=A}4ixbsGZp1p?j7+j&Aufh|(AFoiwSE2X7!9xdk8_;#&;GVq%Z`$qEA-!Baq))d&z1+_gYt^k;#rJ5XD!wtk|Kndi(T2#$aHi13f4tXFd_1&1Ei;;rKCo2qz=CH@eqrP?!Tmp7G<imo<ucFp$&&k<B`KafSLLtqxyf%7k$Idc`L`Rqd|k=IRm+>@Hzv#c{&%{X{A#U`%(JflriL+ia6+9_gI|L`SZHf3?i3pullz-q-X4pGAA4qp%-3cG?O(V^^6N!+WJdGcJr~RTKkVLa@Z`KpB!9Y<S$^tC$%93IHOtRUUl!e8o9q61d_J81+FbY7=DNQ&*ZuW39UF80c-)#l9=GO?$L;x}d9LPaf9;6h)G!twwlvk?@rsA5oZk|Q`!B588k4u)yge2VR((_UH}LFm#cS7;`#1Q)lX8D~{DW0$|85#?@|%Yx_qR*jZt%yO%W(@QeQfeiFD{GjZ#GVUJ$_7a-CvvQ{$}I!*XCY-Q=U^i*v(j9HrMmb<8OB})|buoe6zWpZ#LKSEzmk4=KAuuwZ1%VtuK#T>&xQ@?pkj2*WzA(H9rK`{k6E)UyFPFwYaywmJd_M#pKSi-Oj%^oy&~k;Y(E&FSyF!POV)^UprxN|B{*Nd!r9Y?u=}xjw^r6RlNEa1`l`ZqqgV$T=GbX%W1L7Yi^eh{kSnLR{J%#+poFZelL&J{&1a=sy#Jstr6-wc_b?q5B`y2@`e7@G0Ves`B33Y+vMjKCssw5x4ACwG>MN{-sWC=?m4<OX8SFkt-RfSi+kmt%qh8(_1-)=5BsI38~oRb^X0s4JkI2^r!N#d@@<8k2LCI+Tz9??f0pI_k4CmgetwT^r@!NuS<yWB{N9yvUBQDTj;Qim64d&g(`2W?%YGtx=!yK2N3I+;^AA6m70tc;@W6{<qrC6VUk$Fy`{BMH=NsiCP4^pImv@>e9uCYf%7?!E$>6$t8164N!YCj3^NhiD`5-(n>eu&UjgQBz@d=mP^?uC#tGT^@HMjS#=GOiVtvbI+@@uV<WV`ofoi_OO%WGx(e;g&bbGC!xeJ8J%<!^ps@xNtxXUTk%@0zOe93EiuzsJNbKkR!so=*K<1`qDID0%p!r6#Y|Qt=wEnR#AssODA9c_uHNTdlj&Z!4brdUDKudEDxk=Jxn#Zud)byI=5Z{nFg-m(FANOLMDV!3%-pSo_!GR{O)p$E^DwxwRiXZuQsWR)00O`|EM5zg`}zzaF>x>%X~ow&V>Kua)cK_s|Nt&i41Uc=1qdUU`+!z<v7@B`>jPU38w%h7pPnTP}Gxf2U9^?r;3VO1ZsS7sVUxS|itQ&ZeoE(Y)sUvR)@NXOqEm4V66d+!nL^%PFdS$9YQ|#^Ni+tTuSNh~lkst2|TFXQ_HO%62+KCaLR6i-#ZkM~y@I+={oDEZZMAwNU2qc!5STfB3`r%?6*`QPumYf0Mym6jk-Uu~qU&m$mOoe&&E0|L&*d^;$N*w3Dnq{IBwgx5-p_ZWLb{i~DbFm*Wr$H=Yq|{5@`szsIfd_qa8l!OpX$Oa9vDsy*Z9%j<oc2UBj!_5^+|tay9!?5?pS7Wdzkr25-3GDY$!-<bWixbCknfA`6fS9jJ$k7qW{c!sLXpCtL(TgH5_xi=rKmYgVg&-nGx^WWxr{zt|xoFMtW{OhCFk$*xj#gp$|7d@Y|aptqHQ|s}P_bI<Fdi`eSYW+I5myDDAP!)6i9y|S(<o5YabL+V0ue5GVtoiKmkzuvJ4$n<7IP*MMCdDjYZ<Oj+sW`>QCcPoKb>8_8H_tmBw~oUew~oUew~oV_+s9##TgPE9k98dOxOE(k6fQP0*81|ewT?VK=oiUD3+ksBJaLPfhfOxAaX!&<h~!6atK-AsG3xn%=6XJqPFK$pzPMZQI#twhx$5i;gIDh=xig@;$se7sj;CWPrWrhIujIkqA8nKT%9X*A*Gg3PeHZ`CG<dn+)qP^wMUn@8+&Vbcyz;m;uRLzeE00_ADsU^Pc)=`H{?TN0KdZT3?_0lC_rGzi6+e+nt)Ju#83uo?hUDRE%}xG#A9)-J-fom;@O<+WuluDOpFqAciq~GDo)4tt3mg3C5%qjv@fJBg!4X6Ht9jg4jdO_(X$EKfoddJC8NBupHJ(|gQVq_0aIz9)e?wCWD!xZOkMbWc9yU1pD_FjFrosP-m-8feU{8j@_52zB*G@T3ndkdTezv|G2mkB=X$J4JMDZd?+YHY2gY#9c%?8)|YyVi;e&4}iiZ30ij=#5kVT0@OT=`a}!Jjyz=6~Ze83xz;_vhl02WxE&NPc^u8vnB8(hRQGMVHKN2G`^N#h_G!>vh^`gBt&)tpd^GAKr8;)8IcXRpWnSp2-=1=jgNygU_$2`c<fsYX9xpU82V`cw$wm!S(sN{Y5qZ^Yrg*j8BU-83xzuVp?O9vwy>j>!%s~*Z?*E&z(`@Q)PLl==~KMb4S?VdR^4tsE!+*hIWwruYPl7-jj9YeVoS^KPB%6L&q<r8@$1_c`EPgX8C*4<b9&=;W8$_*-y>?y=%7_yk8mhd@tO_<WCMz?Z0-x<kQco`S$HZlaF{z&GXdan+@Ju&HuokBU24t?}oZAIhA0Ruhd@7pTPR>)pggG>7^vM&YS<?=6TcO*7@Dz)_K$8)_GHN`@HFK>%8gZvCf+wx9`^y+Z}2kc!7Ai-<^itb{c%vaJ7HuEjIb&B+0||($WoHsLTR6ZizQco-1BGhp&8Wo57#1ulD=6ylDpS-df!+Rd~=WKfa*4o*UcQ<iQ+rKl(~F+-z{J!vh0Hn!M|$>iWE5`Ba0yHAC%p?mI%&etA}wv#;MYx9?k1r+1LtT1OtY){)1pb>wkt9eLbZM;^D<k;kod<Z){qdE8n@9=Fz!$E|hbacdm~j(<Nywy#+OId0)1hfl=fPJs~ycZLR5$11ORw({kFmCr?;DZ66w@Vs{<4?k3TWUThsT<6!^Zja5gmABesbKM^Qj?1HC%`1=F*WsGm*WsGm*WvJN*WsGm*Wo&keI2g3eLTsze4OO=eNgY`#!GJ9Pi5yk51HL(g5=iyS~kx8T42f&#jX3k;BTcTN^adh+Faj1`sys2B)N5eYIA*m>Ps9uS#taS*XG>+`d_#_MRM!@+UENH+VM4?CbimkvOfQx1=RKJl!J<QS|EAwo-B3V|EK75$*uc+o9p|1XLMD?b3Cc8uaaAARr_O(;?{Epo9pKczB(Vxki2pO)lPl=S)uYw$+><GH+w)`f0pf{_${vY;@7D6jHMD4Pk+<6-w99sLh(o*b)6IUj(Xpk`*+3vXrHLYYkWp#G(YE?Ez6ayYVzO#$%Df`FnO2Rb7Xx(dn^8TrFSK_p8wcf@2^1LB*m@gOW8Q{A$ajO#aGr=<1;Bij$33^y;+ivQpaJZ&OdT|!oK#37r!OvtH1C?S>7p}q4=;VYToR4e2c-Y=WjOG^Eo)}xZ<t9k{V7=mE+*?Sphk2kvp%M{NssgJh$aEd7E2uJe>=56>n5j?WdN1t9f#5ow|-q>#Df*yfGWs&u50bs`$L-YJ5(uko}E3GD>mld8y64=S5f26}O(d`c9RV{c*;8qOSj2<dW}IBXcUxjy2yrZp}B3Tl3B1)_n6#@1nT%+&DW|$H~Yu{S_~ATHR0WJ1ED~H$GAE9cmppV~WV}3BIvk@!E~meZ<2POm02L_P5=q_TScH#{LSmxT$#N9%CN*4&14(BRiEd_e<SQikEF;%+GL-tBP}c)AK)2s-k-T6n|}X^!#`7&Q$!uXR2O~Gmi72;s;9@$Bp0{=M>MA&p6I_{O6U5b36$TDL7w^*Yn2lD)91J#UIUY9B)H&vlKtGS+$?zXCTkr@;caA`+{-Yb}k)WA8Y=2+?qcgx8{$>t@#sf@@7)3_3LqK{d(M5zaF>NZ=`v}<e2kcb9?@4ZqI+s?e-5Fq4u-&ep7S%{bp$PRHM9pf2z6t{xsZXfl*$+pVi!cKkH<Kjq>{aujcmq-$3(^jq>{avgY>t<?!5yS)TXWn%nQYePfTR-&I-f_ie7<*L&Q0zi)G0KDZ`ctsCq21~%8_Bd=eIS>EQ}?-?Gsu`TBO*W8}}n%nbVbNhU~sAO8K@v*sXkH@X?vANg&noZJTtuK#T>&xTT`trE7zCt~gro|c`k6Yv8acg`$Zl7PCOHt32t>4dRZvTEpbNlx*ULNcBGr^IU)wo%|=h58$Jx}m#!|gH4!?XQf$QiypR{J%#+poFZelL&J{>bjjyJL;N$L-^r=JxSTb8GyaaNRvI=a1(0{L$Q=Kbl+f$G7+0J+a#FajX3vx7zP<tNoGP1LX5UXMJ16x1{Ve_~f$kd>#t6H+i-Fk_XRTHaWjD37?*!o^SkkQ1Of(WP8G8PMe(PD*nNRGYnokQPo?rvXv)?IzRJVD{`w)IA;4bx7)9|-G0rj_J=mLR{WGtUcZJm%u6%)pxcs1k{X)4#B%jsJjYR!^PDH(j8eaEOC6>7*BSDDEYM`H$@!ggaLJ!04|G-cvHlV!zj93G553Y-J%4MyHfH-hZnfXzR{K33-TpSluiJ}FyX%gM_c@M;yiPHvcekjYwhJi!w8s8vd*53BtDm;leyrC2_owXz;~eKsH^Pnz;rF6<;f3yZl>g9;eQp$rQz3j|$`+<vVYu-3xjvs8`Q0dhiq9Xo+qS#08{L85jo;(O<8HZnZq!Aez}LmsM;qXuL>r<F@Oj-ROPxYReIL-avb3ix<?_*oee`!PUXRZ{+P06e*h8CzW}+YB3(@BfVZvupxA;z8>J&a7nu*V(yzp<jexe(r(Rc7dN8!ie1$)DdF>VYdgdd8&g%>&;Kg5k;j;iNP{8-A2rQBG!@Nc^@GOF%Td>-J&t8NTLU&9Z?52Br-jpNaY`0@A&=w$pPbP75dKf;Y5bq1+#0BsA>o*?B$((YmOcPL(u&oJ6HjIkI*n}xoP4#B@kpN9~m;RE>22x1`h4rKdCbTs~cH)^<15Pbw+5MKcG;Y+fu1X=)JnOr5&f_TB}!|GFq@b$=BAFY9Zn7ZnrkKjvC*Tbj}FAiVT-N=tt!{^86L(Afev#l7K4_}E~#nJqD!Rx~6Qit%5leaEf9bb{U9!IO;i&0lav@AZa8&%xM<Ho&iRE1TA3x5yW#pj~1B4{3b1-@St&5IYj4y+D&g|AJ%I%rjVdFrc;R>2pcuJY(T_-k(b>Bf2VFZ_A@1@t@oQMMgJFW@hc>nM62FZj=}pQ%Imf06fR^iTX()b%g)FZ?m;`U?FH|GgW(yKx%5g+GlygZ_XQk;QhQpWrW(>l5@e{ue%9Cja-aU&;Fm`aAw>>iQMEh0mhyuhAdy-?(wxjkD+<__O$P=oS1Cwtb48!+$}pBj{PY;MZZ-sYCc1<h_pG#$Tka8|WYSPpRu7dIkTj8^5`661|B(i9dy2#UEzd$LJ~im*hH(p2Yvi=P$|sE$lb+Ci)XTLR~+hH}M}+R|LI^FXKjOH|{{=@ps^JqB-!n*%pW9#NSP>+~^&6!ArqPQHSuk$Xg06jd!Rk7aEU`qb>){fq%@6T5ddqK7fA+e-~O9{~+7$MDM~sO0Eadhwy^egw>=D;meV?CRz($h`P$558&^lu0m*G{3<tAy0HXZgkOT6ht9??W?LdU55Iz3i_s<c5P4UitMCiS8$ws&XHnNebP+z0x@MuX@h99k?#3bX0R9ku7n*@T$hMv6F8t@@I*1;^ALsLD=;!#4$om<39G^~IAE5{EJE<!j&A?Z7C)UGm+>4gM-;2+K-hsb|ZMo4r_)2jq*FEUHc)=^eDpH5=rO8_neHb54U8T`7_}tVLkKTc=;6`~j?nX=E@5bjsbK*;}EeDzl{}8!Kp?Bj2e-QQ{bqHUAybq$~@p05u0xcQk<ESr=I)#70jdE@jM~mW%;~n(hj`GFW_K%~~!QW4=VrX%^;69j-I)pDmULRTx|F@&+Dngw_Df<ug|BZ@m!jEwMa5ws+eewPAozYJCer$Ug?TjB5r*ic}`{M;43L8ot!uKKXP;@xHBX#vb`{G}wu8wFY`~o-TyD<k%#LvOMi_XN)X4?$(UHm+9%|_?o1)mF>OC7?`BJW&uK7KlN%|a9LGpK7iIurlB8{fI{E&2`qTl{78EBqC<T|zJ8uaWBt`Ym4YtFWuoA^g|my^4N^k5Jdw=r{OF)D=O$!tZh;!;Kwi8h!^p72Sm2&bAaZ6~B{Q+tD3(!P8;s)FJ#f@}{F1_>I)H4Nb$RP}fFu6aKgxpSy7sJ%T@q{{;OQ|0&xJqo3eEBiE<sQM};CV8^IK_$=}sLqEqKqOL6T2>vj29YR0Gf9b|WH_oGH@#pcU(Np+yY&(gb#(zPsbLe@z;1^&Qs6+TO<h_7i#Gjz9Gw50TN$NU*p2ClIW2_sm62f;!$Kku<UqmP1-*jVOoOrjXLiq7$5BzxiB=jZxB>ZIbdHnO_o{Ubw52U_cgz#?=!oQ6M@o(cNqT}%s@l(-B_^J45=w$q4+Axg}ehO`Pfp!hV_dwg?d*EL}TjO8CKTou#uR@>2zliUSc8J;+9oSbwdq(ZMp6pMdL-0c1!jHy}Mc=`X#g9X$;HS`E;n%q5sw6j-qbd01_yuSxegXbnLiiczX8dY5mbtMWosVCS--yn{Z^UmxXW(a$Q}_*TY@v-w_!M*-J_VnOrr}fZn~5}X3f+p|gx`q1AJw+^X}i$msJ<lASD|b1Lf^x$#xFzX;Fsa&qto#7@iWn>_?h?_#8k#!==7+4F`fM*bZ*rCnj5u$*D#hF@aqWSm!iw@%lWSG?cKT3)s0q!@Xw&H;Ge-aLtn?YbEBmjT?pZOqs{TX@q^H&_(Ax==+pS8$vqf-9sgXMYHI@83ZH;)f<A+9f^UpA!#BqJ(WmiG(+)o&d?U0uz7hT@v?cy2d<(Q4z6HJwA$$Psf)C(dLwn<2!;eG<;YZ@fpo8&)8LKgb@S_;FZj4!bd{=Y;zAOF}bQFFRd4zx3oh!}Uc#;slA^H?vXe0a+lxu)C#Eb2IKKo(XH|Dd@ruYW<CkWx2P`(jm8&P*-;wj2KMf;i(&G>E;yy(+zw{IW0k%=C}XW~CZ_eFV8?f|+UFJdp-_flT?58T*8x&8P9Xc!;nJ32?0@9)EldUw;N4~R^1WU_q^8pd~U`_|Wu7tsFrm(f?y{`i;Cj)d^N-RR>+KXUZN_eXo<dsANc_HI1S_xj-bp&juZ`Htr8X^YSfc-_|L(T@17Zr|Q_V+*<&FLX6t=vsU-x*lDN7vB}R))2z4LpR`sCgInhtBG~wT1T0+L=yRv`2Kog18vzr9m%L}<8n7vxv>mg8Rb{-S!f8q6ff9&_@%@mn9zmzC3wLW<CjqHV*E0^V9njJe#VU!Xac@D+J+FmEg^hsv?cyoH(I&T4o$$f!#_tPMAetT_Y?R|OQIDypQG+}XxpfqZK<<uRQ;{_uJA9q@sb-|(60DSZgggQXSNC7jcoyVCs<E6dck|agzv$&?(m+luCOkA?hdQzj&&_J9wmf-j1ayKS{q-(jYr(5j#k50$5$nUui{3Vgt#2Va{hP!h1`Gs#5K2L{D*S(H_g}c(cir2=JH<Fw@HW>&w-sB?mzM3u8|mh=f40-j9OI'

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
