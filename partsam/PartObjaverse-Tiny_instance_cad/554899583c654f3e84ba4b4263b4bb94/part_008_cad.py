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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/554899583c654f3e84ba4b4263b4bb94/part_008.stl', 'relative_path': '554899583c654f3e84ba4b4263b4bb94/part_008.stl', 'source_sha256': 'acf86ec799f9dab604b67f6c7d210c1bf4cf0c0f6921933369ffaa2e8eed3232', 'input_faces': 648, 'input_vertices': 443, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07728356122970581, 0.36514005064964294, -0.09054884314537048], [0.04303687810897827, 0.4979691505432129, 0.003603146178647876]]}
GEOMETRY_BASE85 = 'c$}r230RHW-~OLuma&vEJ5xjvMKW#UDVdKXQ#)fMQ8LFyQDjIuW;TUPWy~>e#L0L%IK(k*j(O%d$IRRM-nZZ3fBoO<daw8GT<f|&`?mJ?`95o{XRY--&%RDqKkNK<8vdNL#xA!q3cF~UDmI#(Hg<5tm|+74N4kw1HNi?NCBFLms!5&wJ9Q1T(#C3&oCgh#92nv3t#fWR#LKy^&Ur|9#F&WSkwM`Rg9a<Veej6L!FhgUNbsn^d7o=}cr>i5YgoIkE?W1${41(*_#=Dg;XE-f+wn)sJk{MhzCnF9%}f{H;FK-C-gWmz^;utGtN5nmDDf?^HtWRyJq>ZJk04I`mlX9`yP6`tWl0F?AKAZNK39WpXj0;u@=awgt(CZ|lEv3z1K{@<k2sCz!*4ho{@|UGr}k<#j(hISRq<!ESpThWsoqzPYYxp!llb~r_*3_bZ(QxUMf}Xk;u~{J;%hUXuaUUU6U5h@Pm|+Xaw1Zt-stf-?u0;`ukI!C?==E>j@Tsib(hAh65loiamJSvUtg}4N#gVyiuyfYNd6Z4y&JyuO-El!eJ!no<fG3GM17mCIIlI<o26czF5>GOZV}&Pt7S<0K5mEevafwz@|iYnrPT9;Z#lCS?e@1O=VdO_2KD>6N_}%&e>pGn*%rvZh#toso+<fje>X)tT*`;|$J5t+>zjHPMx2e4mr307O>o?t8FF0R-m@v+`i2tM&^}2!(O;k4;cxFEaZJ}&td{TBsE2%(+>tou#yK)R%{{9k{;k$%hYYu^6366(`k4vv+s~7BFs`eFJa+^j&x)3%lK*Ra#QEY2KceUoi9f3>+W%;n_<FAv%cVUB+oBydEXVay;>|Ys{@c=szu`UnFkfj0b8Gmz-)6}9nj`B;e7&wD;*6Pu<1P)tIQhW_{c9hG<6eC%$2E^Ef;gL>Vtg*V`IF>lDS-MnMo4{wgHGDn;{R!fwCD97;Jf^jEOC0j72jlUgZ6RhB<-yC`bT`@f-BO_M!$ZWzw`5_BG0acS4f<hFT}Ta_riECX2JORcwc<2o+qxCjXp9yEn#;MXG0*yPyacXA8J`p|9*4vjkTSme~sg=im#8@D!%47812*GlKAHF-Nd)FE3-&G|9T2>b{#^V-dm;Jv^T$quRAmm=Vi{t^|j~#;{28-zCOiY;_GhgN4sU76JKkTBJ+m+cn0D>-i71p?4_N}Yqz5Q-AjnmwhG4EhBU+<I|S`-%2_D!x35Az)pBsXH|;6DY2FINFMbjIzG;n&A4BIP#MyWk*Tu`N(qG!`MED`SB#!Z^QR3*Q&O|<sy`=pODSc&}=uXDsxPuF#9bUay^PT_v4C-4JCrSL6Y3Sc7Q_%k2?h@Y^JQd?7-GX*@PL=Vj)fs_&92TJdwpuu^L&MRJjc=hHTn9@&mb*i7zQ6wrzuW+fhdx25Ut~4nTnR_Jwde)^+<DaZOh&&abjSIg#W*q4-i169JHelc@nG1~RnE)sM@NjqYGrQ7IP5(U{ngPI=QZ8~{peZLgwL&TUYm+aePh9VGR`e?T+wbf6VYEM(q;b9537UoTE7kXoAz#!IDXa9p3do4#GgA>+TWO54S9Y#D91IN%|`n?D2MoEo#eRsKlPYTI(*qKdTkJn>$FBb>sGxMHSNYctZR29Ug95rDZXJ!503K*GVkdEUm(ul4OqWgxuSlfXX0y7mE^dVipL}$gYhYR$0WqBtCxAteBm~Z|0PY%%Un1I*U^WY@LReee&(0BZ+(L<7}rsweQ5XG>*DLroRT=ESLZP=jkqTM*ZEoZda~qc_Pq*!|1+tt+x(~WqqhGN+Tm<x^w-+@l8-q*d|km#xQ^B~-X(b~xrq9w*I~Y@8a-RuVQMzccOvF1<CbvDvoXieZi`BweG2cx^>X1L;*6<;eT7fNT&e$lAL6tckNl$zlD}o{UYzgqIuggwEf(vtM=Ih(nNWZ9ILXJ5y%zPWyvMkD*EUh=S6qVlJ&vLNun`GT?_DzTEQ0G!bNDb%&j0fQ)L%9V{Z)M~*7v;$sP8^N@-ZL3iuKMV9`*lz!s9-cajyLkiuz%f5y!C$*8OH(;pgj(_HlPyEay|LE&Ba@U91-cN1@&PTH$=%JSC2?=Q_#9V)jCuCK+gd7k^xbMd2I0d=S4<McGH`A9y0Z-&l;F2GQ96*twzKyEx-I%DsqnZFY^X;~(>b1?#$Tgd@(^dIkLG6IiE{D#CAWg>jW(E#qHbw=D7*9f$Z!GO?d5VvF+%{1fZ`jsp|r`|hQ1+^lH$9V&n4TbBA^JnXuKdF*5n^!vx%X#d#yGH$gEg>YW^KIF=A!^7pcTIDa2m%+Os=I32qCrO-JFT~ef!@RBUd<b#tKNjC~b-%QmWpWJGi}km0ej!na)4@Ah;s@Ul-#92sj;q-YUHh%Ce^3k8<G?4fA2!7Ofq7!Rhn$x-dxnfdQ;i(t8HDj>{ICM+zRPLE*|Qz(AAZRw^-M>R{}#^M4o74@F_u2O4cGlWoLAL0F;cJMZtTnUrJ{b=5E&1atD8~(u`P}}sWSSbI(*&OAsEjEVr8B*evCt$lr%YCa|K)MbE?gRU#EuD*H7#s`ywrQI^s{fj`~|iVg50WMmyABfpL3qlw23)mTk}uD^_A%=rR=R=5BA)pZW>?dn!rd8>8G2KYAYglN-_RMe3tpwobr#JxofMb_~|RKQbG>p$PT~3vF>+|I^q%^zPJI;w&x!U)zrOhsz*;m*N;FXCuWo7IKz$F!s^5@%rL@!HFNGUZZES@6)@T<8}HO`=xm|#MfS2MEt!k<-ByGFN<&P?JDhH2>1=-u<ixa@7EjkudKy*TYC!r3e2m<+YZ5!kJHcahlZiwKcve1so$N6_^q*?8oZ8TfA6po{=zKepMGkj)OU$T{;>fVw=HJiI=7k5JPTu<T-0R3x4yxr73Klg+tVd}LOAlt+5^A!W87c&4uHQo2j|teyv(;c_fps|dp(r;rtSCSI?@*YCjDvfI)nP<Ixgk-7vH#LLhiTMoj!F5{DWSYS2uN#^}_OMq4<{j_oTihBoh0LklEs!I<>{Pz3M09%FwTa_~tQRP(N`c_EBluWF0VOEyK9le+Tnp*jn+;{)xzQt|RsvO=rXZXP@{6yXA5}Vu=evoX#m|=b&rYCw+3qe(G5roL6ct_PwPY#n)A@fO)2+ChMKyFMF&@0T&SGd;yH(^fKZb?%lwA)h|lg!L%9sdehP(H|2ciImo(T`5{t#W3|R;hg$b=AMsmH@pTvKN`1qT3b_Au|4Y874X7{vfA$+$FU8kA?~3#F+#%PyR_P$tpBmH9o<rTGJx$AEas0k}k>~qyvVSm@?1lUO@@Rj3#4MTLwEK%>9GT)uA<l(#*$*3E%obn!;)^&1iY$=xUmS(|=Cze1PgBb|*mrph7vHjfKH~2;&y;%4^q7wmZ=oIHmdQG0{O1Yo*KN8=99_^OwAU>>chRqjgrC3LdYo4X>Q@^rzCP+V>^E%PWZkwDcSQdt7m(}Jw7xFZ^Eo#zOa3ztNPiio6vcBO`%tuJSc0qzrr&?ZacUex{-0llO8!@#qJL_+;JDs4vTmANK9PNv#W`MlOYid-H&yS7ule*xKOVyVN$-0b^?lP&e_<Kq-8~oe6TMJ>Q5^37?_CmK@4W~4Uv7wf*NZc#zu~?3`cJ#0AI<NM;yF|Ewa9aIbKIBdmWywi)dBr`$1qmD->etvw_Yc{Y2UAY=%*_(zv_pUkT{xGi{0|M-B!$(g%-<kbsO!aowdqyu#O$OcKO@(H1_O*=Ucm7(Vk^GjgUAGYhk{3{sDOozlwcPj{@QwGU74bypy}hc&Yjn_ctzYG2hN;mnm^J24h}1ZA2Wu;<#UG))f0Da~AyU7~H2jdSHFqej4q6V2ZTAd8HHldfPGHmbl0~r7hoq=L9dK(azzeW{KZ39oOab2bhOz{Dpi%qA(s8W=VbXs=u)xE9Wl0VS8DucbUNkX_u2nWgap$j6nOJ`7%(BKh6X5)8UGkA95N?`<pH_!*jv*J&|Y44|t9<<E`vR49PFCK8|<EM7`tU>&}ECf7?>A^0|#W?r-jF7vEC#hKvW(#Lajf^I{>|?f0^{uCFCxKayaLeq2|vo5XP$ihYFbWvnmbAK<uMDxm)LV;Db6yI?(7We0!X4V+htOguM^zkzx2l>zNj$}d#n)$g>7KJwo>O2)bA<tAAN^wZWOf4Ar;$>-@yd46Dwc`Lr@s@_NZYE{LzIP}Ez-YX_d`e)P|nMVz)Yok3Im&Z8Q?G#_1^$zQPf<5~8r%mGPQgB@xUf;%joUse$<5p+~&2(4ln-`qH{qC6l$iH@|w7<D|dGXEtQ<49ZxN-7%S$jNJ+x$1KFaOuF|IrsS$b77e?~e9){mU?k=Tb`Md&`^wi2u+m<I|j#Ec-HZy-Ub{`6J~2I81zP<wsmcJ8hAtR~zi(#-?H1{u4Y|K3{4K-^~^CyuPHgk2#_c;{VhO>)j8zxPEg2Wq#Eae}{QsfcHT8zUu&4H*{BeVE*q_Dp=0r?nPObbj~AizAIekNdGmfF6*%IN)GZ5e<gVuy|2o@o5pQJ{L&kziJv||e61Je2TO$tsQ+dP?sqpiV_yBWjO1_p>k;nzV>Qe(OUI59zrYUh4Fx-4JnXu{dH4?6b$K6*pVu4p(jHFRWjtCUCt-eGe_+1UAJSxooY%7~To;$#;=0HhBKtVqp#$izdcLwgnu1D;Z$AGB<7Zt})Ze>F=23I^3b-B{IAR_s&_{erP%*UUrbV)E)XhqoBIj|rEzbA(easIhXGwn=iwws37BACB`o(s*TsMZc3os6M9zcKZ{}d_58L$iOX`gS8_(_MPolL1`(O(4|q@PTgyTj$*i(kb4t%fJ^pM5+;j(@it+U?p(oM-EVA>uc;!aV${3C5LUmduO#exAs`QUN?yX_piv`NxGL|C9z1^8Mbm%HjIRz<4k{mFvf_t652DpBxj$`C>cC-?(U9M`_1>_oTjYMkkEd1~dB0=c3#n4(lT0K==MgkkntmcJS#d=VduiGeqLHpM-gP)48eQSJ%R&KeqHh{(XF~|IGap{?uILb2kj*ut(x3iND4U^Ca)bjWfd|<a3KyTwkR#vHwne6)Aq>)o5o=H=Nff_bAER@&~Tp?7G;`w-_~6>ixJ1`OL49hU1<V-~7{I%#-bg;ko5PpK(&}L9y@lfd-co6U2Yj2JJtr3HE_H=SgxtLo&EO*@JbipntT~9~Fo7;=?StehgzOO_ll&a35`|953yuyYg_l)W2RF^<z%Tysz6?dWQHNuunEG@5blLZN=A@KZt(h{iE)5Cj3Xw5Z|||w5QJXsQ9|V{cv6rE6cp8Yg0K!^2u(5@p;Dw^ZT83;%jgFeAoWEu^(dPv;A|lbIAbHx4u3*8SQhUkIVzQ)DJVo|A>98R<gLXzjn_iPV$c4jQQ>H+}+>$`m>>^Kg$mLtw$#Dbq!A9x~niB?>AR_$IItdExx<&`|4{Z++Q2M43g_Yvkws8a4`_|Gn(UhyZeIKQvcLVTt{;q5dXdR9QphP@y&^^v3|S6Cdl_A-=O_96Y`vRQhd{v3aDSXAof+Mo^z$$tGC4UH8vObp@F}`A94o$Rnda`=#!TDlFxpQ!#_%=eCr!OJjXm4@*MZk^ZG83di4k3dK@zk@&DQ`zA+#Z*Ke)ic;00>zTn$@G@l6UFV9s=l=GTX4)gzC@z@7?tP<aF$_e@RABlV-DlU}IfidvC`p9vOTWgDNzKeOxWPKLzXO|BU-*BZK=JQf-aolcBNs?z*tdIKKXzY()1c|S&FazzmEC&101;@lU*FOUP%PRD{@5@C}zX$ivnFrDSPah;pewVY+KBu<H{?d5W=_kpjPboZi8n^@FVR+%il8?(F#GjafJl~{>Z>c&D``%ff@xI}{^Ab7Us-u{fp5@4WkmY_y_)n`Le#%cWek?UkiLVd6^WAe!%ZhvA8z<kzb)hxE{gJcXQpwx@1=`2|BkDKnAiiPwcsy?$xDU?(92TSgh|+it*1!Svht*gnpZz@WT<*ON&xfxxS|M@5lHv0{-O~N2`1;MGk$>&>h?6*IrNpuRfcFkx2I0ML!!oPn`)8ly`Rdeg%>M@~h;Q8Hg7d9CAJ6+5O+)=l!DzRfT5|tuDYa32%gwhqZcAU8&n-dOh{NY^U+?cMpKgh7x)_M}aW?LFKGVr+wZv~8i*?7kF5Zi+8ZN#e(hl#<=eZ0Q|5?2F+6}x{GW4yE_rDXbA&z}0o@+JhiFN9EIg{jB{2HDMZC;D<7Sl|8lNOHnE@^V#XDnxc&-W4LHx9U8O9>I*5LyJkE9kKo_dk)#P=E1Zyx-jYZnVVt{6u{7$$faw=$v2n6~;=h#n<H)Mf^$^#!DRA&+rYy@!o&XM~w4nzH21^hj@=;=pTsvWP>i^>mPfee$pr0*EJt5zOlw9#J^Ax&ub2?5nmS?i|5AGH_3Wuv|f+;EB4_%(UQ~hJkIE|NqkdfymvO&Ie>ZWT?X=TsVwJfcs>Zv{Yo4`K8Y1EuAJ~*Q~U9__~x`=yeH!G0nPjverY$1lSe6-H(blCl{{_m9z-iNMb;_fM@R7u??cgFKkmbE)2oZGfB6pYS+2Lk?*vla#J2<vMf(IfaGeSeU$f!+tka%&ZZgJz__fjz-!Vh>$Hpm>#5Y}SjC}fR!1HDA72=z_?nL~U+Q{E_HID212yuo!kozg4^ET9X%0@pr#o+l>(suYwqwzlUL;#+f1ZE>n-%Dt>E78(!M#r1TbFm}Fc}0J`$2{>&d}HiV<azJ5yoc2$luwcR_j;rL7#*JfysIO=*%$8_wTK&XpQAZ66yKDcjC@9q!|#sjw1wZRGV*WV9OLAgFXEgs;&)J=TVfsG-BEmt-BHHrjo-sKbrxTL4DbETd*5LnSYiO;XF1~cB>U`f|DO^ozV4z2uCJF>Wjts-=HR$a!;t@{T$xXduTtSpoq+hChGRcd{UGvLa0Tsf<~`Pz^yA3K?k2A5y(48j7^BZK&nO(X+Z~MCHV=`{+*J6rkD_1p7D$!&mCnKsy)ge<-?(!!+HLGKv`=U;@eL!~@O!Om$(Wa>Rzm%JdvQJ9ErfRKTw8q8+2?qFQS`p-Z?)s?;D^0N`={#=Kg?fz-C3LOe$Sxo2t@qpF8Do+qYuVgv2gMA`BTyU)e2+19u$N64Q659sCNdxBbq)3^&k7=ysU1c-BvF|JET;{y0hV}>|>3i9>V{p5&ZHKaGhR%gg9CP`lVAM_C-~ni?21q@1{(Lvhh4Lq})2`*B_7Je0SW(aUZydZx}fq_2<3Ee#W()__~J0a6O(eBmV{7;{WG;pLG)U4<DPtU+jqY_~&$pGqWw?)NPG+*fSe(rbLRbx#4$Zy7I%(Uu|Zi{^YiZU$`{xUjmjR&zK8{e|H9+Z`Mo`-?*tL-jkl2h5eQHUgR@64!?s+NJ4)-IfOWT@2PF6iTNk%2;#hJkN9maA)n*-kk12a<j;MAHtq@Hd~SttJE<YokwMyeIbMU47;pR?k(Og6zUf5BweR9QD=fZoc{1WW_<hacuHXHNG|{zqh{Z84WL_zv*=a+9zxfHNGS%N#{r~@jbePBg=qIF&JiPv|KOt>orD=8ZiVKTkN2-qONOquBAS*3Hb|9Cc7A2P=7pCST7baU#-)mqi@;eRsiu{iJl11?&>ND~q@@?v$<lE%S)GOr6<nz=E<n!cg>PfQFqvUMz5$Zwm5%K}*PVxcrZt5no(yip(<ZaZ=<Za|M>I!lid3|14PF+Y{L0(9n$D%lann+eUjhsLpNgYKVN%p69Bm0w^uqbXx9Yj_dOjg>8+>%^{MR9c&#Vx44$t}n|sguY($rGtRk(DkbPb5#Jt|Ct*Pp7USPbbf!rjTcm<Eg3Scyb(dH93wP%c6KPHJLn_98O(84kwSG&L)o_2T>=GgUFroiWhYVbpm+^c^P#BS?OM~(x1u8$m{aTOzI*Q#hKKf$(iIV>T$Bt-^f|yv(#&3rPs-4$){Nq-=IDvD}6#%`jC8s{0EETyVSqQcgcUTDE>m#tiWH$g{+`O$c4xysiny!$>pf!$>qq^s7~Z+<a*TV<a%Tesxw(>W3mU?mql?$Y7?^3PUMc{Kx!|t(xK!)@<0~FQ7nq5Q3sQiP9`f|NuEYd%`4lf87zvoP*;+b{zTqF-at(xZy={oXOdIM%UKjJqDGUIjwLT5Cr~5F3FLU{XmUI`mPPS&YB+g1c?xv|c?x*~HH55m6nO$Ujyj1PN1jieN}f+%$f7ugMR5dm2wCYMas+uKi{k#&KIH!70P2rqrCrGZ<nB~Ia(8kUYI|}QvJbU2*@xUJujr|s)YfFBEy<o_H)>O|8@VC1Iaz5lveE|RhUD5*7jkWKWvU~&GPx|(fn1hcoLY)poLqofm|TGTS%X@Um8$*CXBNe8sV~WI$uC$GKcGG$KOo<t-X`B7U!q<nUn1vF&y#b=C#czErANpo$cL#1$cM@Msk_Naw~_agGpK1~rR&KV<c-?D`y0hc)Wy{0<i+Iq)P>~v<QVEaatwJ4HG!;jBzX+EFN@;-RDW`Ra>u;lNo_>+Co642ZbYs_ZAn&Ig<Oa1KrKdgAQxv*oR3AZHH+c`EQ(7~tB{peCzmAGptc~_qBf<rAS>-jZc6S!ok&(XmE42ek2;;)k35(<i#(V-lp0SSN*+dyBM&1FXHgtNjU|VW2T~`K2a*G*;p6~vcj^docd{Qfh^({|*^k_uMR5b|-#u9a7R5EGwaH5D$u-H9@`@d`G}WG5nry?OxE!@Mxg5DZi{kcFFS61h<o4u9>N2v@b>y#m!AKUxQPf4`C~_E!;_=iu<nd%9i{iD^MdWnqF6tt((oFI$@-b=_S?O7_($nN)<TKP8WTk(Q&ydftD9)wcCFhdwQ2!#|A>U(B{F+7aC+ZjSCvrh6sM=o^WKmp#T9RCXY)>smwkKC%QCyW;ja-%NPOV3FC%0iy+>Yu&R_aS`NA5}ONLCt1RyvT}lRSVLMOHeFJb)a`qBx8?o*YJ=$f9@#bsTvfbq;kLS?O%@9C9)>imY@RS!pUcnVe?z@4hyTx|5tn-o&DKD|I({D|sV};vIQq4|OkfH+e64A9W{rCy%|4Me)zn4D!$9Ocuqvs9VTNH;{Lcw^38b+sNtE<>Ykodg>zbdh$AI0(l+TM2#n#$g8Na<W=NlEQ*&>r<0eGmr$pWmynaF6Ua*A$VueY)cNGi)V0+4WTgwqYso99F=V9+$ScTeSQIbLD|4x{s0+wSjpSM6G1M5c(g?EBk>oMtP-=hjFlrFBKRJlpj~YPkNA64QPVP(Y&7!ymwF|iixf|7o+>P9sMR5lf#cipr$Y1XV+OjBaLG>hiQ|nVb$@R%~SQOWyx{+&<Yf>AMmDVQLBv+(XCRZfeQp=KU$;GI}$;HUl)B<E{@&^s7_Wd7N6u+UqCBGp*r@kO7eL#LrzE8bHzE8eMy+poA{+*gb{+;|Q^#u7>@-NiG<X^~#sQbx>$or@n<bC8l)Q#jl<Q*)Ex8#+T)Fsr7<gfPwOIQ@or7k8boll-ip24Dc3N?m2g*=)?aVT{RIg}ho?Mn_McV$tmr}if+?MT*>-L!x2AKX|JS71?GmfDD1mRy)xhpg0rth6{;X+E;j{N%#qQq&^kQsm0iGUUqSx>QGUU2<a<#r5(^HL5Muk!(vYN-aY!O17dFAzP6(YJPHlo{vVgCMzwV{rji5Ahjg9Ah`s!2Knp#PYD*q<yjOvu_$(7QQVN)l&rJ|S!q9VL$WuE;?~r`WTivNt;ubv!^myPKd>nFr4A?ik~>gC$Q{T&)PZClayx1OxgEI;wL7^Dxf#`uth70~8QFu{fb2nbrPd_7lAWoQ$j;=d+Q0WjRaq44*e^Qvm5%<`zO!S0DlJV`YV%EBD^}w|qZXptkPDG3Qp=GmlHIBG$?oJX)b?bhkz}P&WTj!`F67QEihEJVla(6Dy~saOBgj9J`%uS{`;Z4v$B_q+4J?YIsbk5}WD_-l9KmCosB6h4@^<at`?~Ecip|trWTnT*O3#p$o+F#dr&ttUq~?;9-XUKkU!~q7UnN^u6hEfECO;<sL;Xblhy0O6aegbPx_`^hqS%I7f^0*!quP`0$d#y7$d$-7SQNWbtCC&GUQ~Co(l%r-@((PE{i*H9N_&!(4j?NHCi{~O)G)GvJUp*-^|Q)nXZ_#(FP8rOQ+r(PyZ_<R|NG7FU#oxn&Gvb*{_~Q(t6u@Re)Hx1rxx&FH3Mq@1r=62zW'

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
