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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_004.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_004.stl', 'source_sha256': '9b1c63289b64999b0c2a7dbfa7762bef9eb1cb65eb52fa3c783d7264eee745d4', 'input_faces': 616, 'input_vertices': 433, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1776563972234726, -0.11181987822055817, 0.19608590006828308], [0.1761932522058487, -0.07284814119338989, 0.25477877259254456]]}
GEOMETRY_BASE85 = 'c$}r22ecJMwub8hDoIRuMF}286c`Z|6qRHHa+T=S0R%~haLGwP5E-yla+0WIj$i;(xFjXW*dU;Yh*@yv!ErDn<1i!4IE?tJdVjm==DoMpTko;fUi<H_s(06^vn%weyU1@*v{+dq|0<i$_6<8zuDUVKN}IA~M8VMEeR~uPt2t=Ms2p=~$lX8nb6U4;mER%9j4-3C_AD6IV`$a7sjBsR-Cngus%o#nLx&ITHmK|1p*;&6&+9f|Sb^ok`g9voV6Us)QoDAIRPE|DQe#s8$A2Yl6S5C&-}8oR%cY|>JD;uHV&9!{-gf`1ah~ofJTv<6*3eh_<GXR5p4w|;oM*dG|1oci^WOO3`{F!3vDm9|?spKL{ds2?Klpa=yK(Lfd~#!)2Q8EB_e=DDFTrWQ@@yV)`u`BNC-~^s{c)Z>-C<Ll`(CoXzjM>RIM@2hP0eKcy;qv<k8^Fm@=Ud4|Cmb}y%*=&Kgzul@F$nQ7WzZ=r9HpC9`e-iA>nhgn^x_QbMyC4HpY37P1X;tDE)4nYklR}PhU?w*Zb)aY0uJrI}-i#we*AXsDI%8eBt_iWeS@oIp3G^U@CF6KR=LuQy%pv+@By^`!l#j`c1j^r*fn9$>;Q<&)<!6&1dDQ@yYn9B9gbtHNNufW6Abs3M6lpYx|Y^!;<~uP3ZStg3~|B(*w`x|9r_?<x&5`Q@v@YeviLM{-iq#kMiM=<cabqAK;mW$@+dh$rI&TUwQVH<a15AQIbCwR1A4A=HalNrt`I7dosr>Nc$(R-4^zbzf0zsqry#*`XLYAd`G_bBf`CE^QC@aKgs9A!u@A5l0O}OFXQwx;lZWjq@UBDNIrZZJoWZ%(*AExNc`<QcUhS*zF%RN<n8Oi)0y2H!Z=eK%5yhT|LB|H=km(DDD%>K;hD{!%X7yadne>;;Rl`%pKD&eBdni-XB(~w<NIw|NPAu)enCme|3=58J<suZ*YuY>KeSi!WI3N}+!Hb`?kywvnW5jt%#--zPDuL~(m#8A>E{ne$a5DE|LX(c_vr8bLh^GW{qWuUGA>rml;`^JHalfp|8gY!yk;!zAO3aN{?vj_l81e1=ij@^_qC#f%-gN#AAf}8&&ZF%IDXf^ZHveE^0E^D8sXYb(_7k^J#%7Pyq!TaX{Y~#aBWXeSK1To6t3+tO{G2FAB1cEq_dJgULl-(4sMlvHq%aQi?`n|C++tp(;m&AQg_PyGe)@Pzu!Uf-#kh?$*c4X$tyF0_?lP6evtm@Lwy}Di)FlI)53MU_>*P4_+5oZ<E562m!K{EK>lP7Nd9<vd|u6y`$x)pcNg__9PN;C6jY!+I*v}hDS4Yi`^o=coaDbT^n>RA4U+%CKmWQdk^fgo{+naMHUBf~CI5q?!Zpvm&XVW;pV~<r=38@$`Bpjet@6zK!gap&0-0Bp>wK%+G!`Dslgn2ncr;JKy<$o36_feXoM<a~!u%OzS%1H5n|Q82{Z;ADgKZP-4<3;Ho40{Dx=(8?`!us2uKTf7?8jad9__nI50QS$=eg&s%gWDPm$OZUpSvzAKX+aBb0)}s=wHWWU$?i(fjIXDwtqFjkB{FH?;n3s2jRzr`)f{0etxiMUxIJW-w@})SHiPpek1#+kJh~t=U)3No8sKtpR6BTQtUvSYklRxTgmpAvRA#A;It>=yOW<Q)wz?5>viK3{o_>_n&8?$%Dv_Ax|!EQzfATs%FPWgtdDcQrSKs2TWROErSHXgI<LaUIQPn(Q@{Ha`{F#R4-bmdp4*0p?J-|Hwm;6zO&_k0bMN@LME&f{Ti=ayt*<;it>2dTxbtS0O7LiW!TkZkqkU9)#t}RkU+^GJ9OjMStL90r;|}iKO&rEc`ux28ajxS<c~D<?^j^?U#)b0ey#Vgjqdxms|9!q+xQ_RT*G<N^{kkvCqj>=C-<WKFu#o-gjmh>aPv<84C%ujRYHqTBl=~%<{ht}n`&Y?i|0_>_-#797X3MNj@aTO<`GUTQapbj<{b%~EksIUVC4Ih(mrO_D>8eHLd%UvA`(b<T79K2VEpdKsCH(Ud2_8If<=!y<-VurT<{0zUo)L-o+1wk$`eqYc$NOsLvFS-3jFox7EPHufJdVkiINnXdvlo<<_OGldeBkPJ@$WbF#x3&P7niL|w12v^KhtJu$TMS_%e-2tlGOitNus_#vSP^ngTkZvXC0q+m+<Jlb%=Z}Z<FxsTcu?_UwNNAcX6`5Y0A7ebxGp$rUuCOl9`lzt|=zpV`^lwotYM`!}{qel@s;-cFdm@;QeYy`%8=tdHP_bkelus<UOU-T!}xnV#xjNLuGzw{jBiD<s}aDzrRG*3)3!F;$#NP=Q`L`;@2pf_`LpH`MjB8C8d9wcac2md`9N;-bJOp&Z}LRZ?_yR4D0{V57&`w1KGd%B|i_jt}os+S?|p0H6ahy9hdpPe_0v7(^rIC=he&znO9BzV2LwuO~`}ITjhP>)oxN>*O6D4XS!Amx%cB<na>aQka2zcRf+iCRldBRe!6*W__;o77`8K2x|qxlFFm(5-hSW6`e^oEAM(t&qVgW`#0;rlrTp4>|D@8gP6fYTyC%H9PD$CPeetu@ueUnn>1T3<uR6oLx?)ZIdo=m1<J+1_oR{vD{Mpq|^7(LsHSxSk?UMXYl`a2D*k0Ywd?q||Qh28QA=!U+ZYq3Z#gO}-y)E_Y<q5A<Ipp3aFAD$X-4cI}aNURa-xL+TNVvbhjJ&@zDlT#Q*9&<x&vcaWm@Uyl_}I2Gzg2D{aT>LfI7f12-?#aB*$-dZI^??UXQoO&ry7ivcIx=*B%e3Ed!odl-%Lm8x6I;&wDYL!m%Cpp@t0<VvtRO>%lDp{epKS~y=02Z_mXOI{+f_~+FSM&U1!SvbMD2$b^q|G>?=}RJBD2IBt3xke=#uRnpfTw$*a_yi6IZREDYoLJ${t&a``h7pZ!(luaf`S%f1SEH10Y{`?K%-EYBs+)7ML$r)!m68`i&KbQmYSw6(<9S$%E1{lNkmkExEsL$2e<Z^JmcbB5Gs+@(wRlz#Zf3sS$Zl*IX+>}N9DcdU)~b842%4_=)jg<*Xi*L&C>ZYmS<Xdc+dJn+?(!i(N7`|XczmVMFF)e7Tz;@`u3)vHO!Q(LymzGAt&w|dp?DvW=wV5NNCpiaKTVZO>#lljV<+g|vG9VJf7w`IOPT~HVw7r{}Phy7lU7AC%z=a~<;j+6S#pZ*ShFM42#wC6}2*{95XT;2=Lf4VR}u1#guk(XB##`7xZA)nVTzgprmpPMxE`Mj4y?)5z->+jrd62Irh!uU819+Y*#TeYn)p8sY(?<sq>%jaS}^6ruKC@B7hw3GEKJxtawztRqg!+IACk@e1uhckY&x$?P!j~lFux5ryed%hDMt^0kce?h|pPY;%Pz*K0Mh~w9k`Nu5H-5BTDMZ$yKN$wAk=LUy_NAt{$yzi_ou_e*Y{rpb8U3j!_T*dF?@Mzx%_f9A42c_hFTzT}nsPZx;6VFY3EAQ!kE8)7|_6ylp!*xHV+_V=Sy<eA=_ip9U`?c~haQ4rsU-|t3uKQ=@!Q^Cp^B4JjUb)tf_&nj!?<AX>C%OJkqI^xV{h5ROZoekke&zm_WdC^e`5j<OvVW8ZTdB|cPIkG>OUm_qC*ntv?GL8Qdq>3eeNB0_YeOEbYnzuQxQ=V(Ugu<ezbo@w=VX25{s7@RpJ)Co>yh$k-vu|5lJ(Ow*pE$0)>rQBgzJ9ejEp<w(Rfk*>9vWx^|$lhaZtFf3z_p5?@MszPvz#Y@Myj*zW$v!kA4q<d#BE+pU3Yfr_QMl4^AiBlf8%ENlqu*quiWHel9bc_ohp)OZ1O--_Qh)<}tWm8Lq#de9SrskJd-HxB2AOc>V_$^1cs`-k0IQPT`vW>4(U3xaPldvy1xVzd6Xc6<qUQxwktRKWNDN{_bRa<-vhu`@Q9yw;o8gU%B~Ccr?Ct$~cO+jxXgWiKFw+bml8~H2=VZvZq2G{hpJ%I>DpgbKu?(;nBJ|TjqanM>3B2Kz{#Gu5pz6A1CAZukgF;7pD^KPd_O8DCOFI<>vUQMF03zS|quiQ^SLHv$loL<y;_mOU{+N9>VopAeAfU0$wlSdM;pE$hm;mPq>~7WCJ;GGLKN7a{;e|oC|o53D<K0lgBxlFI>+BGJhE@pLYVB-`l<1cO-A82-ow1)HFFS@TU`>-{H*;`5oRY6t3q8-bI`vEG7=;2xctj2m$@0=Qv-=Iga-xpNsPavtG^@%mM0iPL!%E=S0C_`iFA|uaTTPcv<?Ha|iQ%b9wGJ#OK^0`1E^;{|oKZbD}KgM5Sg+|L8eXN6yP?3y;o&HpqEU&`7wRL-{r39LgIaJUXxZnDeHwa6NCTF6T}DLq7!ZINnIk*Cq(pcKVNZ;C)JXbguXBtbC8p3fFd~+DbdqtAuMFdQVFpW;XC#&8tJ?)oa2vuTpy?uTq<NE_oFUV!s^-*UuX~ET1>KoAzryoRNG;y+wWcA-%7PeBMK}hkQuY;@tLg;X1yu85v)xKU1G^l)XmAQTj{zfpHWpka3jy22TE@cS!zZ;Zgqd<J|Tb@il+i$+?yHH~N8bl=@N5t-PQ3ygH5wWE=%2=}*Q{c7cqe>}mReag_R&bK8rK2l4Te*)HQHlMB~zahZ&ZRD-%ZLay^(kp^;JoF_b*KaZ^1ALr5h2~Q7B#_=l3@2+M^GEQcJ%(u!lPQ+gk9<3MGFt5U+^+Ndu;^^N|9B-cF`gauY%p1gEz00yLE7$c-d3KlZbJuI-=dRc3-PAv4y;gqidY#&njGtj$R<7}tr}rh>uj{h%|FT{mO!iM!*X4uB{)zbEWdEmhy*`}mf92khX?x<|d-^)bAM>5?=zXe)tk=q;_bGVl&gqHzneCDf%A-7in`YA!&ov8Wy-wXLJj$QDB~O$``J=oo@#&w`B`uPi{!t!uBaZI(Zf0KxkM?`;RBz$Y`_4Sc6XntS4m_jv^?m2G<cad=eFvWIlZ@|oCr|n$<15b$Ot#<KBYC1c${%>@(PaMwUrU}uT=#p*{d4+%9e<DHpVR-2=O_NEvTetz`RR(b$<|7kvZhzJ*q>B7=>Dny@BgH-?=AnUKdG#9bDjV1pH$wQW6Xcpc6@H_w^m<oErl<Gc6D4?1$+watSsfu|0bqOaqWC<bSG<RYeVsmpleg_D(pJgbzE1%ZikJr_Mo+H*eKZT)Vma`2CK&Ph1d<SN3C_Yb|3aI>;~%PVpU*OxV{*>5w_gg0&7$7kE7>Wd)e9&YyxbiwUv}jv-TX<D=BkqzO_PYi?AnQYplIs?P>fB^efhuTAPO-hhA&#d27$$r=y>+wvh4_=&AT8&@Wkg(b^pRQ|O7-mRVbjjfXvJZI!jj_*v+Twbj-p;b)^K&@ZmMkF{RbhT;37zc7*uUmDRak7~oSTz_RGFTORRHFuo;lI!n`<iZd5@3_bLZ_&q%<i!aiT64!~z3*>Ea^a*AU5(su`UKafjO4}7MzrRR(<iz9#rl64$suR|;vVOJMi;kM)Y`8`you=?u8YI!;Lo6)ogu#Szr>#9a<?2-2j;$)<$O2JPeIQ{d-#0x#rSgg{FruSt?{{N58nsh3q6cyc$l)j<cPLGSugINgel9!a?1G@G2NQ$3-P)5)-mnM8sjfTcc-i|b{}j4{84;&w3|QXQa&NZ8pH3yKa74k=j?pod_%N*ekHEwa(_dtG35=ZQx|^~x*`5Sd^hw=%EsUyM7z0j8s#%%tS-D8eiYixMQ*-&5<d;?{5@#bmQq|#Bi21wUCQ&gE`^nab%N(%Y1otSq4-W{w}#B8{K**0gQxM2pxvD5=G7Va`REzw`uIF_1$<e2UQD~PyYMOW?<l(qYY!X2GwNf?M(4=<t!+?t7rZ@wG}_JWZVecRe;Vz4OSEfC8LpouR!i(I%3D&W3I1wyPs*BLy<z={t#OpigFl4tkM7O=^Dt#@4RUMMbo@N@baXv@6Lfj})%Yec?aG?sFGF{xtSQz5HXZ&LzB9UCj;x2;24y|C{~1i#+MKiNr}KBmbW^TN;xEHDjcHeQ2mVTQTgvXhI>MfS55l)akIj+w`3X$f9q^9$v1qq;yEXnP{8Y5_4bZMF6}g^DtOnQ}lsBMGBm5=k`zdRLwSzqcABevnJ%_Tv_<`s~l(oYTM!P+R+l!3H&p|ui9PQdtn(H~lYK}Fcyg7AR;V(ybp{y150Bk&bIKB&dB4tDH!_loMdjLNK?e;=$zcdR!5j_iiC%zT>BK+m}Rx$0$?!{k$?m*eSSR2?Z`0w!@&?9qXU#4wP)`t5hW6Io~*6r;c$4^E-j&5eH1pW%F8L^sC=U(c&>jC%zw4Wn;3yrC)YmV$IreMmN!3*$R(dD=<f!B69yCvuBzNj4RR`?b866gykD}q05L_7a)bC&<p2)ls$9jj^WC(HhUxjHqe8!x}c`o9}7r~iuo(TM(u`;^tN{xA4rM)Z%|qpYg+-{ZeAqK|QpvfHfx8h_M?{)T&$U2FZH@kfm4quiscmi346e=?$vaF4Re*8dTI(1`vM_b9u``p@tm8PNy1$FYyCu5SGSBiga*@Q=8D-^lyw2l(^R&VOjm>hrjE{u3kmed1qFoC92cYJD;54;j(!o?`G%xPHg_QP%e1-;HTk_5^+}dXu%S);3^HufuOczl?tcy&=X6xn6B8!*vE$2!9^t^h&N@w6=mcD~PT7C9YRdcO`lS*Q=<rf;buY^D#CS{(Jn3=n>ZDSsR0&j=tC0-PZ2G--WJg?RVDh#6N&`ah|j`6`KbeZf!DUlPPohHfy(7Yll4ubM+@$dj^{fd(7G#%H~k!^v%|4TWgEm2XpnuTYCzd6Jw8BTY^0Wt7WZ`wf0yW*yGj~anB;|c@+MLwOQCASQBe`)>>lCVXp2&))rv1V8g5}qih*vPB*r8tF=~GGuR#08d~du-49!9ZKJgp@XOI_tgWYfJ!NYtclufUdh~PnHTd=D7r5s+yw)8?*--p*Xm`&ju1CS1gYSnq|1R3`_h1X@i(%MM*h2Jd{3x^=w~M)63>yU>ZEY#G7*@wxJ!>7Y4lq}Dg0-30(irot&BbQIJZtr>b;7#BT-{05=3{eX>|twDu=%jtt>s&5fbWbRXKfnyOyi!1;Uld*jZK67*4m}k%Hwm;HLc}ZyB2=|+WDf!{TwRhbVd9{=o;4C&!*M!rO;KaU2W|WtOV>vYgbsi4qqHy$=b!%s^LqbueWxYwF>w$Xy=PqOIfReFM^#9D`)KnYnNlCVZX6f%-U6WgTBVvdDgDPUx>btesTTO)LIK`H{n~O-TXO&exE_VJN>qioZ5>X&9&2SalHrs7J5RA@8)_JemB~W@i)2NiH~1T!tX#kAE2FoIHup=`VaUw(Boo!JJ-&?jvj{|iQj^L)yTT`8a{*0&|j}%PH)DKM2{rSX5wrj#(8{CIhfPs@%_=|(S5Q0d?)?+UYwqW?t|}-Zh>!&?~m@!Gj77-%;iW^?4}sgcr7T?T&jt_65R`%Lc6Zyx(|LDdVrBRLFb2FFgG9MqX)n{6T1P|4Pd?CZhYU4HGmBu&b9d4&DnXNGTQlm=ziSe^jzB34?h4sld?hherPurc0vz=cO|~ZwFm15ck@ks%!3UgPDOlu^irN(U}Ro$^VCIH4RdzxDnM6655mtxFD6zGd;!|62_4Zr;2nrrhwD190=SzO>tS_ZJ&02sUk^Q-XAdzlf4aG}6m~UruBN;?HiURXxYy~0#Oj70f_D3YF6eIX`|&RB9hfpVcQ>T0A!S!{Zx_nDQ0DY9p55EXJn!cH64;IA>{`$pT@~F8zYv`^vgcWb^@g>=H^cWv_a<&*EY93Ib1T*urm?QW--@2aa|at)kKFoH9IIr`u33Z8*P+w+1?WY@>W&|bcKg1T=<e|5#B9QK6WCz5TMzTFCa~_rsfN!(FX7oejjWq)9W9AnZ_ci*J<-+B-SLaiPZ4V%z9-u4f7_!6!rS0o+*(+ixplh{Rtq+eI2G`X%-Qulh0br0Q>1Ls|LMQHIs4E3wqO$f0nWL1CXaRFceb;!qC?*N7U#J=gxyRO2{+p(T(6q{1T`_hQv'

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
