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

PART_NAME = 'part_019'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_019.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_019.stl', 'source_sha256': 'ca4174c7def6baf3632a75440a3900a3b395f901c94260f1049cc9f1c50e01d5', 'input_faces': 816, 'input_vertices': 434, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1497575044631958, 0.3016877770423889, 0.013232339173555374], [-0.11394553631544113, 0.44019851088523865, 0.11679238080978394]]}
GEOMETRY_BASE85 = 'c$}r22UHYE`|f)d^O{f;!-}J#n6rWjT8xNUSrr3=h>8)x99tB16)_-!h%%^{6M~8X8CTc5Ys9?nnAe<h`cw5heA9gAf6uw+UiQ4_`ORZdRbAoj>K@K^^|s69px~#1QaLHuSht#@h$yHyDB}Y|#s&ohhSnYxJjtLGmA?4N)~L=tox1ihDC3nWE`tI?143My8eN(Xc5|s|bQwH4WNe84D8JDmg93%$)_+83V3r>`)IT^d>vPqH4I0)oHmFw9IL-L~_)|dip=FID8Cjx5|G4atrIwT}2ZU<Q<)p6$Jd?iKvA}+zO3gCTR{}R(6Q50^R_>O+H?lP9$;fqG`a?#fN^RgMeaks_Szc>@bB`=PwYc=n{ko%kx!x(V9Z!3->wDs=^mms?lfPG_p!AJJV`O<_^`5(=MioH)*8;A{dS86rpTlqHE$dN#ZMskPe@!m*Gw*qnzuN%Ub<a-vrVE*}er1(!vix_$$KQo-ef3J#W4_RApWaty6ulw+*?~J{e~-U|KYawoC*#&$S-$9N>07#VmhD=-lJ@C+b<7o6-W)w&j*r&;75tB*WxHD4DYBp1vX{~~HfS%~RnFhtF4gxr%BNhG^;kEj$?>%O{S@sE48nCiPE5|>Z=ELVF>QFiRqEQu($_{-mgTiR8{{~v_aC9%${XQZ*URfwT;MC2Q)RnK$G_#go1Z>F{e|kI{Ha!QofzNVmA?6cBi6(HTzmAsweDS6UJV(&L-upR9r&Yn$bPEv-!@Bs-)*#eJ_++%psE~a_3$nDt;@>t#u|~^WWVg-Yqh6i{cI~I`>C|~8{-!HQqGIH(hRx&Epu+7{FmAo|L67OIy7~>j{e^~Aj_MM6_WF)MqWcdr*uO<pKRJ9f3I{V{2w>q#~L=t`7vHVyH~^EZ}~&|+Jm!bx4i}9HY|^vM^jb!7E=Y;uHsZWUH+cyNsfbt^=#~TP+o`j2l`p(o2<t={fC@)HP=!2<M+vSHP`nWWPLFQrEhY}eN&bz;U;~xVjBAI*BI+9-#5&Ay<I4u{s?~GuIpv_gWJ&m$;087{V3;AYqtsgoR|RL@vEE{&0!t-<98PQsry!roAG)g>i>2J`RDm5IsVF{m8j?X2h`(#SB{%<X+HW{wUq3?(*L3CzqVo?#@X!v)@RASDSF>B>SyeW?cI@2{N|wDWdX9h#cN_}4&T}p<qve0<7pl|3-yfj#Q1MZPSg8J`6U>Cr@qJ!k7uHukqY+vr{!{AXyc}#{DwbK|BEYfUu%1(qW?#h$aQG_+bs8s_0S~j$I^K)ZrS_y*m#V;U3u(__tDrF`QV!txMSQpILUEVBF3Wr>Dy)hwS~R0&ZEY_uQ(3t^L~4*+qhBiOKrve>Jg6hQ)L+X|LQjUZqJkC?<EIfep7E_Js0b{O79y3-of9QvRdkAfAs(QAIJkUV^+%g?fWp#B%*x56D#C+ckhks>hucZcBVuQUvnvh{^vg~>rs7uQ2wc-^eqWJWxK}so+$5K3i+`3ShK9}RuA-l?$nENz9w#4r}vd94ssq<L)HCy-#Bo*?2pC1cC7TbbVm7^kI>Jw`m%mY?M_&?Gh5-h!p<(2^)>E*c4LpBo+nAtH`%qpdP^#Zb^c|H%!kU{R`566$NVNO*{b)=16^c!>wu0MrGL^B<>T_8-2q#p^}gc2Th?Qp6_0fosiL2!BCle<4VQURE#`r7i+Lx<$CB%3)F0r6dW^U~TKt|R%KFy1qFsA$<p0KsS??>;m+=0wb(z#*jZpvhbMU`?mh+`PZ-D+hKZNn0drp>DLh7UZ#P-<l@tLw+ZBiZhL&l-qx)m`m9<{KZLki-$?gz;HX_{9J{)ZCC19lB#^}gwWC+fF<A1{3$XVf1ag#MJNi~f|Yi1m=_gZ^)>9wo20Uj>wRvf`Zcri@wdt4;S|{m-u<_lsq<5%ui2gZW)}ISJ!bo_W3^*2B32*mr}RP=C_z=>LKM*?)C?In)#P9PMr#CdWtl_ZRs8rsl|#N_F^}iRZfAU1XlL3@?lMn$r*GjZ2}adS5Hp5#>|5;l2}E3gb3(VUB$GAAbV!i6wXv^2vvi=#Sqg^s`F1%#&6(_?DZwF+Ph<$m_C9E`fHppThn9{Uy0>%?BOe?^=QTW|8vpzNvjLj(Uc~VSknAw^Hx_civOOis5?u=7w+ng#C5Y9{t>QPu62@Q72LFtADmYe)g;&^Q|>Eedd2P|M)es{dPss&leH6-pGY}^u8LMj&n%41@Srj(;iq?gFIy3Gyhfu`y$W|^@rtIruQw1J;p6O?^5}Drwik{Qbxm{^G()c9FQ0FJS&6#v>%6aY^B_2_dp`<FY*1ck474>4sSHaIG25puJ=tnTgd(xBMPmR_0<1ySe75x6zf?XDA&I>_Pg}8<C|qYYFQ)hr!7An)~{!6Osge&Uv1`w_2XF_`62HI)Spoe=krE`FwSS*qWm}y-0w0+;eNODwe%H-1sLb_=W?GKOTLo6C9x6a@k+X!U(1RY(zjl_fc3o54f*`WbJR2QHlC-t1*hqKV_Hr0b7hs4df(Kzrrf_;l&j32>dpt~XLkN+wOEdub=*DlCt@)6Y0CwR^?vsK%hL9Uyk7IMzfr#FT#VcPGAs4I$+sBF_bZBd{OdaUS@;m{Q)b*Bm7?&?ZE@c*y7$64yxTRj`;Qyuw@Un4jO!KDbLS!F<*m$1CP(;|NUSTRWK^u)SI(cpbvb;9lfP%Wh<1zcoJL<;a{=|_$}Q`$_>_|CTpfB2<@fx9`TAub_UY5V&>zDptn;-#avy2QXV7kE>|f=#M$vlTQWVb}mN%niK2aN;M*X=xQ9k0h?2oeVB>V!Q*pCZqVt$*Sz&w`wjD8yHFV_2(nNAqD(7STnlsQK+FGF`>-G16A^P$=Mcl6VzE}knVTV;9ESqrXf!a&S#=S``4-})!U%~&TK&vEuFKY2guDZU7KzDEZ7e*n+pmW&xPZ!6J<&`-z9IDfvLzDDnBlb+&wuT{+9tDEX$+?xAi-(5~ef4VJ4o~#rh^S|bM5cPlAkNU$VCF*@+*B|g5GH_0gKY;R`@Z733S%~~>+>iQ8v_n3bGzRC}b!iy4CKoYZPBrB7h}mT?`suj|ey+T7ziUBza9#ItZZzI%E1y$LTXw^@F2%b2bYhR*x7_)FJXveST8wup+I?H?lDz&lH52u|=H-EN<{^LNlU=*upN~cTm#ZKjHcrNR=+I8qV{ZN$*SmiQ`afs{^4NE?T>qBCTQQG4XCM#%T}0+{b?#=2=f!6jx0eohUOTx7{Wlts&)v5o&!1b5{+yl(e}scvx2B#+xUTCs_i6<St<(FaxkIpi9EZsKY+02Ezg%mKXTb@$t_o)Kzuk3||8NiI?T4#SzHKnhlWx;j=kW72;J%n5*OjSm9Iki87xeQ<%s#!Z9jJwT@~o8Xr!h4a^)%ms=l$se@Lc&m2IG@=pd4rAoU<&i9f(GG{{gt4Hd>DS_H7ybHm#7K`#sI!XP>vVJxApJHO`Dee-ci}`-1lH2F}|@mSQ~fx59mAR~MO=thwkbPS{_}8`-`klh5yyZy-O+Ta0#_;CVqU;+r7<{nR2{*S4E@jy~2w<}0;xB<jE068j}!1jc#sLikJH%W*J{3`^AeYQ{ududfgG`-KSf$Kx~BVd}6&Qe)<$-5--MFA)dj^O4$r9@pnwtp5qu@my)0!#wjB_RHw_ReE1JwgLNeZ)xdk>u2XUKNvkfCF*@+uO9H{pObmO@<PLW-I{=URxiMLFLVa#shI?S;<=rAUrnxv^Ir0Ithe3MQU9XTSXVpEk+Po$r=a|4SB!HC=aIfSZ&|GKz)YN<zfXoAxGYnCo>(_Q?_1utL-|EZR_cAzdn?w%n?$@<QQ@lxzhJ+gT7&nuVUtjgAI^JPp(XJ-{NtrD@BeO;`At1K5&5(1hn(+o=xY}~V;mlCL;lG_KY0+wVaqD)-}VzQUtX>8eyrZkG`+8NDTsZPTzXFqKXWvmBR+k@d%5}JQO{r_#?$^}j2ws4<Iw+}CsEHaYl_}iubObbb2uvRU#2CYxGn|nuPlvr<2}H|5R8AJLRim#JK?#$*BI1aAp!ewPPM&y-@Fv>fi-0d&att<XxIG$#v#TMulKXxms;E&V&1QhM)|1YSfAPN34eia{rz7&H(kAf=O*(=luz)-{_0mo<^lE22=p^L3iZ55!h23<`0CE_nHa}`a=%*xhhzP?`XfL5_?n{kEfLO`_n^x=^}aHoKj!`32HZCv1)+TD`Iz4?zVdll-7y619v_PPf=>wY$*aLUKNrQkm@DA>g0X?P-VkTZ`$+F~dSAPT=V&dd;6mx|8HDk#AA@-h_s4qv7=Zd)*Fc`BUIyp+rtp<Ag=Id`_V13<``Xa6C_jIr+}FlK{wQA^&%eeEUGe-i%MaymEyMFj#y#YXyaRB(uQ89>>=yFeZt3ca>)O=;{j5H7uijU}hGLw5jFjh6%hEpR|94lc6K9_ky>AUKgZdBbiOo^oWd+u=i%FitwUWItzmGETJQCoJ_0zi-`Wf^P{ka*8_nC3OqW=6E=B0i6U3%Yav_pQrI~#farVrXJ9D)5ZdnxA8uP6MpOq^SeZcNkr#^s-pf8M&ub!ATMk>mWMl)Q%Xz}@cXPxMY%kFiT+Vh*4C*Sxi%?2lR*zPh+FuB%q6oG*1qH}q%!OWbEYx3ALs+2>NlZWz8d+0+&NG#|k8+Ktk9t{l}F^OgEQ`sRvz()7OCY9IFF;hQ;pOM%@Ohv3t4-nE^baJ?^oMnBKuTw!VE#eLcb`NTO@o?Enxb|}B73-VrpVsd;`1AKM({haR^!rP$TuT8LD7I?_|t;br!-}4pqFS)xwwwn*Waxhuu2V?H7vL17XRw!Su6#6;abDiE-E1ktW-aChLMT95%`NkdR-eG6tIH-TML_Oyh%YA2Uh3CHi_^D-azvFY_fBe}s@&3G7A-p%}u3|l3+KznX;U(u$S>}OuOBTX>EjTaVV^}iXQIFeicwSiA66<PZbF63AXV_oypX9mAx~2*0zk%m6?YHZ)KjtcKSPw2UQT}?U-0!B%jnQuUZJZl}V&r+oGQBp|=a*eLw+z5@w8c^j;}&-k_vK9UKD}=)iF1qPWuP2SrDHYt)jH*PA7we~g8Cx{$Z=Ea^@-N|mNUsH-!MZyzo-L^nBN}t@w{2VM~<6uU3uQe@x7Zlt_jwOixd3nVHk()SFlck%Ax+3ov_YVcSZjvI-)=J!D#n;bG%3TS_17l-o<+GE05>d-;3kA-g;qu7At`D-=-Ma4GG1(J9Wmn<z!Kmzf=PC-)ez8zx-#6r(-RQ+a8<))oQuW&qr0TKApeH`=c`44)a*W1@|wv7`e_(sXr{T-QYOPOB(7?+`dcSGVv1fTjEQM|F<vFSE^sb`EZ>R*1rdQOS=K6r(3iAdfz;2H~LfSvFyLO;Ctz-*S=yr9lYc?s~6s&{?9e=zI`vg7ce@&*S_Lhp>{Ijx_*6)diL@A@gK$Ud>!)&{n`H!<JRC$<c);q(zkvN$3AlYRbH2M&{NdoycqR2=DBG5zv$1ZugIS~mm1UWz`r;i&!Lw!y#EQa!sqwkYUU=q4=H>T{`|tI|8WZT*OKdKxA?E<=dm4lpL6jV{N=CFZtZFKUbWX%Tvs1Q+<({HKcM$D*R}Xwe&HsJ+lng~|EOS`$I9H4=X2%8W$Bx$`pNo@lO6HgJs=b9#@pY}&#(2-Ikdak7w41NMX{d8oxycE48}Z0md1W*dJ5xw{tm|Zgg4%|dmcxBn18ar|1x_WMZ1fR$bD^cJBf3M(?R&xJIm)^rCOx?-p6uxAKJb1JL*3;1Ml%F!?)zY`(CBMG<m)1lRfB9-}<tCvv&se-Og0_%vZ|8d+T%f!3K<T>-GEfzLtphBwC(EvOikG6!?6uQR5C{-aqezf2=F+gYO38d9Bqp_%#d|Pgh*88om|RHHP_Q=uN!GJH7?ukbY3kmttugA?qo+5#w1J`&5bkutM)^j>}NbKiBX*V3h>aUkdNX%(WX~-W#oeAHN3kSR4CP`?4JM7Yjf=?^nxtG|q^|`Wa9I;}E%0=37haD2)Gm+;_Cc^W^xO=PX4%p83%KU$73XXCu*WsvXXyT5im*ah~*z{QC`UKJIJEu-O=g*8Snnt&a7%Wft1?dx|`8(<f2yD|_c*e3D+_eZK1q)U(zH_g|-axNm-)ihg$7iuLen{W86;G^m8@os=M-zm$0sG0r^{j9ZOIIOkhOp}Ya_2b7~dW&P^5Ao%Yxkym|gWBt4jMF08zR^vX^j+ijc`EfqidR@Wyvw=NOegvM^v_h^JpAFsN+xg3JHYs=TJ=(wBP|v6tC?67x?@!acaJ`di^M14x@0l;E7$3VdwA<w$tY^RG=>OY#xS!_whW95M-B7-ISzK?=sj`0atA_A>LNGq})8+dR<EMHUH+$T7EG2P&&-RsT(bzA2r{lWv)kHm=j^e(*a|QBzoO6!6XW5aC?~A?dQ9f5O^uOLaS&#LvBJkIJ!aDrvE1pk_!dJdlK)cqWa(*@cd>GHkr*OWCyny>oP;U6E>LFk8dvI&)^9<Raj*D;~ymwvJV=_OHz9k-cMpF;VJY#NpTl&UMVHk%-IJanb&!L_QJ~;OdYb@8fYWM^7^ePQMb}-ge`F+w?!=}ml)!HBN_cNPQQNHREl&{_k-;3Q!kiPQb2Cgf%4&L*BjY7MQL-4%(dk=hH);SdAFSJDY%D8WuMht;pb{FP__YrfR{;20@E!@8f{lLCn(i{D;q@$mWD#34UkN&5}pq@{sWu7#3ER6E@P8hd!RpoeE&lZH=bO!pF=z@KH`o<yIp9Dwb`4jKtI<f9Zk-l~-0`E~@jmG>gTOfVQ&8s-C4s^$Lm6{K~?h^Qm^UHI)F@B!(&EB<;AKWAH{cO(=)c^4fd@nzoH}>C6m)G@K#r19~kNe#}m!z*u9gO;Kmq$O#{U&{D*@v>9MlWBit9dn0k71YeRrmG@9$j<%wPl|v(*iA3M2c6G{ECAz*kAXjmckT2+4{f#sbx^Z|EoW>bgS3+|MyQVix{#}V^)->D&+Fy($p^sxHP#q^%Gfy;1bjyWD$akQga!=A_O~7e<nMS9jS%Mj^uLGQsi>vN?B2hTA5mkT$y}Lfu2ynA_VuMb|Uv8+fxgY?aBEWg7Z)dlk<>sQHzpuk$<9=CjUgXqn0Pzk#ke4kaLssQmc{kl7FVwB>zk<M6FFOL@q|HLoP-xkrlsC>r(5G>ymp=e<k-IucjuFSCc<ezmY$aiy5F|Ef!-4zOEny-=dZ$ixB*nTAKWr>+~VDIQb#hsg+uSY~?zALoG^v!!>)4>OdAD_%+p$EJE;0YB{n9!7r$l$RY&4S8Qunun58VvZ5lj3AGlv3E7oene0mbSAmN4{VzkXiQ0>7A{(jpWFxr%H9xrkxgtYw1!^901#&rRE^;|?8R}2uGUQTJJ8~&<acXXIadJs&UUEsY1NCRJ1KE*Ui0nu%OD#q&OLn4`AUlyODYm^)i6OXhR#c}tQ-2{llj~FKlIxSZQ+trRlVhl>$uZ=o)X(In<U$6h*gu6Bf-le$dr9zm>MrVa@-A`;^%gmWyodUjyoa1heMn9v@1R=AJIGt8Z^&E7o2d85o5-7~ugROq8>uhJ8_CJk7vyB}Ug~@DUb2NM_LzmA1)oxE`%th5!Os<h;FkRNCghgnPE=QNCvqFA*pqGeS@2I(6Iq1dvGk1OvE-`M0_3XXd<?-ws1?aY$Zib5DzySxCA(A0k=@D7sb$E`$xW%H$W6(Osl~~S$qlI`$qmVks1D>tWLK&q*_GUcT9({|+>Gi(ZboiFtwe4?_MlcKdyrcyw!PhwA=oo3T2X6JtCMSyYfzoZHOLL9^~nv$J*nNvJ;{ryG33SMzo<{if03V1#r}W7&w?|kV$TcC&IK6^!7CVohcE;OQ+JVr$>XUh<niQ5)IH=$<O$SN@&s}ybq6_=Jes<NJeoX;x`{lBJc7EJJc2x&x{*AbJd&DB9!VZU-Af)ro<g;dr;uk-PmyPm=P(4%r#>e~QY#ps&&d^-WBO7>PU*|s(uv%cJe(o8AGHm+AGt2|Cvsi#ECniZ$}EOp7iv|q3t6G&Q*1wi4b&oJ1Gyg6ja-i$$#CQK&nM5Js$`+=x-oR;xC(8q8|UVn2cb=M^U{>_CbY3`9vgF>g*Md9dqb`Zp^bFwMDPfzt72PMf=5xCD7JMdcr>+{Vq3R@L#Ztk+d3CKf$E{y_J!a{)Ru~E9|;~$^;B&8PH?bd%T3w)RB-lQ7Ce+%i!8JTS!e^Y(4J(Wi^)R&A`5*&7Mej8x`ModZ40iJwKygk#Pc&kaF?tYlNAHAVmU)_B()1Uk{nK*NDe12W(Xcitwt7_hdh)#fO<y(4<L7=o+pbC+}?l?>`6UB7P^}(LU0SJnJhwZ!z{HoK%@Ct_|Xi(?HPi*QFoKOk^54Qko%GcQO}bHk!MivkY|wRQpH%z<!8Z5sny6!Ie+V@Dp`c!!wN$1RcaS<7tW<%5rV%`$B;z`HfBYA>LltI@+5LRbvZenyp|z2ff`9pAjeU|$#LW;>SA&fc_~BiT<TErP_CP~48gOg-N>`ZQ>g99Q^*sjp5zJSU}_6;FnI*EA$bHjz+hWj0Sv*tv!WgKtpc?tix9ksD%Rg3hF~vhdvY6UYifIPYjRs^H*#BYJ8EBYJ9200AaZANSLzIMSF#UvF4>3NpSqOXpBzA4M-CuQryeFxCof<KUPZl1zRESaiXk|iD%NN^KMOvq*w(RN5rSW3>30R%oS%i?oFRAybrN|7*-VWmo5>rfYsnkPNesb>)C6)Oc{MeTyqX+KjUvaAqp3^D(c}dT!3(K#$#b~}7BU3?Mx8?bjXaw=fjpZ$lNwB(NghufK^{*Ir3R2g$wR2U$wSD4bo*owL$E0;x>B1`+mV}+GZm=VOPLJ8^Qeo+^T-{jUgYe3CD@zVh1!PPhI_0FLvTN8TXH}0U}`(^VDdO>XYx3*M(s-0$kV7k<Z0v(YJYMFIfxoS4kG(er<482{?r9ze{vW@a2$0Nc@_6q97FIS>RIw3@+Imk@+I<J#kLRcG6dhxip$g+)bHdQWH$p;>{U00V2wJ1tdZAI&E$3D&D0I#&E##=B=R=$Muy-u)I{<c@=EGz@=EeDYAksfc@Z_5yoek@T|kZ?&tV9jPhCh}$UQutA$U4<HhDTZggTQPLLNySPaaA3rG}Dy$vvq<$UVuOse{O!$sMUCaz}CxgKeMpU<mf2HYIzJ%TUEWFT>A*k8<zNBOfJ)Q#+8e_jx!&a70%8M(soOCVO+w_hAU0NbN_SNM1-COkPM{P8~;HPEMd|<OK3s>NN6N@)~Lgc?~(98bppKucZ2sSCW@e{mIM71F2zTp;O611IYu)zSLo4U-AIzWby#=Z0Zv7Y;r6^@CJt9B!=KL>SS^nc`J1oc`JD*HITfMe1JNYe1Lq88b%fxM;3aBe2!eu0KG&OA=rs}mn=eX73zJm2*K42w%jLJgy1?^TH63U&CkL=&9XPhr^)-MA}8+SXTkXmP>r0QJej(VJej<nx|zJ5yq&s@yq&y*x{<ttyoDin1w(KQbqzU&yo9=vyo5ZDx{N%J97bJ44kM4FMv%vmM^WdHN0Iwer;&w@Cif?Ir}iOtC%2+{kXw-(F$6nPYmlAExfz11Qa#8XthXvdaBJ#la%-|bbsE{9JeE3#JeE9_I-e|bI(aJDhZ;imA$wCtlD)}oslMd4<Yv^K<Ywf?)XwC_<a*SO<a*?q)E?xTWEZLz*@aw^`U|-v`L==(d|W{Y{+sGW7FvcZLhyd7xUUEn8cr4(LEcZ!{$0V_8G@q}+x;er+J`K3A~}k@jk=J$jr<37Ir$IrMQQ^1BKanDE%_$-AL<(NKja70c=7}CBkD@>Bl1V;GV(`qUIRj~9d#gCs4rQB;Aiv(ke`vSP-l~`kk3$K$!ExaQa6zQB%fpm{+*gc7MezWNBuxeBMaS1{y;8ZfbJxV5L}jefGk3A1L`@l2*K`DaW8Ra2<||2B6lGFO07cvmF!2YPWB@QQtOZd$w3Uk!wj~2kKkU^g9@}ZS*W=89ApUYP2ETCP437Le2gmYL&vC-$sz;~W(eLyT~8LeoxF*hOx;0FChuej-b&p<-b!9YT|r(&?!{Qa>lYeB9!3tLF42wQ5{|3TdAf0)$9WJMrkj^A&YRG2x_KPOc@{cKH}9jkE`;{it&{#-M?$+BZ0kyJS!yeTZ5;|OKy75Oty{rjT?=(K*w(q=chuYl+x~dR{UlWQC#h8pw!J3!Pikv}Z9fV=L-jY<_OIY8)UgKJei!_VI@Msy4}$IJ`50{ZL~wTg5iD|&P;au(wgy|i68wnT%wWrJf*(*D8*KSd@ITag23!6Ve3M$!V9U3HFH&6$w)`yk4{Aw+EuRbCM!l`r^1onlf9UFM_{qWU|Mb5awEc*4o|5B#Jow+gne)%)^uIYOtFHh25nWgB+~V&_l%KNx6JO>8i8mC={{UcTpz;'

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
