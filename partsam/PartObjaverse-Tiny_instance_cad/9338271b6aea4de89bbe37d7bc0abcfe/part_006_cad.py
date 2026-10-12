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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_006.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_006.stl', 'source_sha256': 'c7bf84d440d45af6318df364f3d4ae5c82318162c53783e0c76078a126a79c3e', 'input_faces': 756, 'input_vertices': 574, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10617449134588242, -0.08819343149662018, -0.3486659526824951], [0.07313628494739532, 0.2505596876144409, 0.4999999701976776]]}
GEOMETRY_BASE85 = 'c$}r22b2}Xw*IRJamX0~K|BZ&6cLpS>bYJ;4EPX1Mdf-B2LXvQ2$Gv1Nl*|0C3!}2P9oW9hbRh|05Mz+l0*>$R}e&awX43}r+d%&|JPgZ;i~n0{p;%8yQ-_h>8`QWL;0>MqwK#bDx>|JKUy_Vib@exM)l3e?9-)VMpm63z4|+<gyHm$b@C%^TefQFsJ?1ojpsA6I%d{r5~<OwQ==NSBQ-kp%<Pldp~tg5GoQ~O-n>J%tPIVwI(O)mp_gmcZ&<H(<c?akBZDLV%YTJ*3bAONO*y3f+w8qtYy9;`y_^(0*6GLwT2?JrZzOdy-Z0$z=4?(Xo>(-|F27&WX!L{cZJZBF<fP)!ZCPf2s>m#}pUC#~aD2%*{!5qEn>Zz&496Fo<46Cq*YHHik^6%6CFlBH`#OflyMDPZn2+S#-sqYQ>rB7(z7Wbsa*iK+Wwqh%%>_RV^}paQ`ae;rg5mMa4}|iOob!oo@m8BSUsTC8aVFLL+U#fFp%p={W@a5Sd7Wst-0+8^8-n$j$K5$QgIpbIx6IUkd(j%x&NCOk$O&+7M#WWz-+$%vAa~oITWa$D<*(0zTs`&m0<)hMD#YDg56m$-d&d3{@Avk*CjP05`$BQ1KRwg5|NJ{&hWLex(@kE}^X(1s{f8!*IPsaG{M~x}CmMeG(#N6t14a)q`TrRYwM(75s=v|M`FDr-C(##7zh}=1w|C>M<4k{E%>FdA-!HSLndAHLU7>cl$4|#i{maew7+$sJVw2y#GMmlu_-pBbyHoIZS?6GoyWokLmk$Mb9Nb;k`s*O~wm069Dn4@=U+u75#%Ip)6C<nHeD-3$rFwsqibrGRcL%u#9$RP656RW%?L%ClUD0+=f02r-J}W{zhIYkdKHLu?ALdb!4|DIca6a5`5s?pbFAMpch}b;QuE;fQ*QeyG=4=S^D0qDDp4?R2t@P5?Adg_biL&ANK3^%~gS#?5_XFZb-JOd}yT+W_X!?z>GvMy`dv}ERfF<VqR~4V#7(8B*^YLOHWsdPFIgd}~E;x@*=5cTypUk~?%IpjtFUk3MNiOqYF7r`w%Vj>yIiJY43vB+^B2SD@$@zR??t%09A~~Ng%wxziD&upzM11B^5uZ7a|L9$FZM!&6jORQY<C%FBoX4}|Jf4|Hc)w-C@tN~@_TzxNGCsEp@x3B7Y`;Cx(%$bL$u;*E=I$;3G~-%LJ-9!})zR9cP5fyu?h4i4bi*7I|CVXyei8fq!hAChyA3pX#1ci#{l$H}li|^?Cckg=!muxb-1|EJduBhaM}_LUT{6u5H*s<JXCZ!Yxw)Uj9~=E?i2u=jq0v9n_XWAS_^7@At}MAHRR2;1bDvddg+C7QH-9wu*~H{B2SRb0{Alj8-kQ=Mh4}2%<~|!gU4DOvciQ^0Y44P>UxxV0m3o<RcBVq8AJq1e6U_0gP%hLD>X7%A;h7af{SfIqFWVfKiseK7ka%Frd~>{iXk?xfqA!k_YwFLj&r9*i!@n`>SD&!`@=b%B;PGOvGM?HVI*v^?&I!hetoz->agX#iJeKvcji2c*OvR&*-@DwzD|T0QaGbb!zKXT@DsJ+>r;umzLmbIt9EbUw6Wh$PtPieGKQitP!_~BgW*jE=w=l<rxx1o=ZTG9K4g|S!$CWbuxUB!qAdfdbZ}t~0H`YF16*@S}@LwPEg6(4N{_yU$Aa_d?GhDr%Z;Q!0eT3~#@K~qZ?IFJO^bAvfUCS+@{s)h>p0z#1E7zW$s{bQxn@%(BDUi9^94|Z%Gk04S{@Cmn+^uqHs^R0(Hkmj)9>C>s^!bE7JA>mVlD5R~$d>(~<H$T-tD@<j2zcVi50g!v-3xyhjL+Q7_;G89kKJUrceu)0!+*2)W#*A}tIho&%KWZO8~?YF_IVQHhj|R#<$S;+J(k<&1W})PqAltdY-Fw%u`2GCP@drKt_C}TJo@>iiNW(L7Q5qHv!AJdgg77H=&|PwcX51UZL;4p>$7`~H~XoZY5PrZ_5P5pq52)l8}2sVF~#Ivxa%4d|4{95rhePzIl+El9^2e<d+_{9RPHdw)XyGiu49oRHV$*|@y}-l<0qVS!`%vVykNT|=YC+Gs2$&$sy=hS-`@UabgKT0JpAV<lmGg^bAtWP+{Ji~^!<E)kgLDXhtA(b;o~FBxILBoVX!`Pb?Wx5p*X!ZyP<seyiT8Fc=TP%y_J_&nRd<2Fx;EC$_pMx=8?zmHu*&PI99AO$n3Xdy%E9wXP&5kAs#xuS1$B3ak8KPFw}40-uT0ze)B4OwtlZp9|rSh?rr%l)UH^|F1CJ8TR(wzF;8s%F4W%0)lNS<ewu~)lX?8M4Wa&wJv%AO9Ipj`nfhLjW#)NRa(-TA9%o+S%Ar)8pI4cyQ7v*)#b++#N0^KF%sGC%M;{x9_lxIM<`M7+o>wJTHy8Re$fMv1Jg+j3as55^`Csw`p8uK0UqPNCALcS24_xNMT;`MD`XV3ZoR2&72^(iV^2hUb9**a2<_U0q9+o_Y=V9hC&PT-exrpy_|A_d^Ilih~x4Yru`kc7+$u8zNF1a%$_nNK=^MAM*CeG36q2nky_Z#y#IFDP&dE7Ghm}A^Z?!Wh7{=lN#RQWKM`6R$)KFno4>cK_1sq$gY`M9y>hDSJ0J}!d$#~nP%^)b#R=W)(F#{G|RE;)~LKMvX@^NE4Wd|a+C@?kFXiF5ype3)}Sk)cIwzj6K;=Xp5BIr9j|7xlSa{&`XQ(le(1O{GKQmN{SNna9$HH8%BQBSPa@avnd-qu~B^SaAP33?5_7*I{rM+`rC)t36(Bs(hHsd?Mg7ALcTjD07hybN{|@X;njW9z8oEG@d2r@xwg9_4&FjxPRRSSKR-6-4@)xZiB}^@p4n;!(8U$aea{wbD2*9T;{`^^NAHaTHov!?c(v7hhuy)cR9YO?{j`{vpA!e;oqg%_fB}8VXn?~G2DL+2lozK<^BJ-|9r*q*UeAK)#CCWrrK`|&y9&IR}P2bkGOej%KCk0ZA}$F@`QbElzB3j^<xhe+nKU{&OJMW`;EQz^v(|`pSBIm??jb_-{XSE`S&|`qG+cN%s3G|dgjH@b1(DABHKUSP_;V9W4rT(uQTBBN<XLMiQ%^2WSsb)BSX*Ce*ME+Lce!>zNxK!&z2c(ui9)m{~nB%SbXL#;-7vs#Plbg&zZYT?C-Dmk~*7$JaPR`<~@)9+zuZ9@nt(+@%!43bLvU^eSv>hGRJ!!SMUgaU-NUdU!Q*mMXQH7es|0I{Ju!Wcc0(ABNb0{Y_iMbiTvXOo@{U8iu(w2c^~oOrMj5qJ_|$FdFC!SUsst&H_XUQRiC;4zIyn>hAYJ3>yqUDeHJ{z^>H7OobMydqu_iWk(}=%ejM@K$UL!rMsBJ+naeyC+AH&9F7u3l%RHIOJmqt2tm7!d<5>&C*KNu9x()7u^L<BhzV9$kaDCi&B<K4MbC>%~<l}RZPaIt4!(8U$aea{wbIvEyt6FzcPyAl+?yZ|?#>3g;;c*Tg1NX-{c%pUt+*I||W9`Gw&-Gi{`oA9!Ki>-OKi`5Y?3c%n<o@qC@CZ1MAIW+AFn5u^%!j$mC(iXnKFno49=OcM?>FQVuh!M>m-`3fBoD_pVIBwfpO*yppO?TruFua)g8R=);1O=G$j9d*pD4J@hq=rr#`Q%$%sHRv$;*As{=|D5=JLHwWJ;}mcD#q*BQclnk=(u=ZGG{cin)AG6?wt6_3_?`@9)h0_fCA@U-O)6mc@HE=JGw8cXMyc#d|#O&6$S#@9_{naq*~mAD8DnA-H@`7;Sofl!+_ePcoP9Cz;FllhL*lM~Cv{_o(%E+wXbuy{q7|exCQPg8Th{rk0r(BHtS`m+y_ewcW;>IO2UZ^E~gXvkutrWMx~K_xv8NZ_L#-mdE)%&h>AYX@6IX`pjc|{rvHm;W5PL>q#Dt@A%B);0at$B=>MV@j3RJ_#_;kIe(XD?t#ZeeC96Se><Kv+%1Fs;(V8!zdJMcnDcjY@C3O3T^?MaT@ilX0FQA0@OOFeDEG6-hj~=w<8zTu3|xtPT;?Jl=KLK$_KowJiOcQc`@ZDvybVFFI8NDcedh6@wtl=v$BAaY;yxa&dvId#eDr@$3GSaqYww<9mc{oY=JNYd<fC4bO+4{Ei@E%s#aw>RlAM3PxS!25Tz+3;F2AqE+Wlbj5#R5a%kOvb@r$OKIO6*tbNPKRUgd(}-oSIA^E3~~dCFW3Iu|-mCFk>$d6YS>8<O*NhIt~rMd-YioX=~2zXe)^&TGkCkxzuV%m<vWW9sd{442<+nal6CJ{R9@6YZ6m&lf>|`t#htqu~BLH}DuZUmuved|Y^*8+aW36BY59D-qvgF5)xi^Ic6(w{ZrX3!U$IIL>$G32?rCO3v3$<}u!H*>HTH4-Ln6!DAvmbAR5>{pD;w<9oe2X}`-e=kN923CwF<bklSbSA6$(3+<d?*30<=;Cbc`EdIrOugx<*0bI^chz~n3%cz+Dz+BFMP|fc!-y`LG4CZn^hF@RI$6zk!W4IFz+V7oWK8fUfo$<MtPa?TLpJex)*{RMWZ(E-^!T#s@Fp~SnC4GtE^1k5pIAM66`8nWneonMe|GB|9{_!f+$;=1JGye)a&-^R!JoB%Z%lTK#<@_t~JoB%(zMOx>T+YAZICB0Kb2<NtxtxE+T+Y8@F6Un{m-DZ{^US{jm-DY;%P-6ijuZbl?yA1P)RXh^!1K(<1J5%bkL!#1c+qO>7n%5&zZ%1RnK{p2W$wM%Zkgd?K0I?dAKtGo=EF0W^WpvaVm`dj#e8@_j+hVcb1@&@=VCs*A79Le_v?%K@IDvw;e9UV!~0y!hxhj@=EM73%!iMRd(d7F@b?P|T+f;F-!Cwa_1a|Xi|@jcyC+wKxcn|Gx&Pe?Tz(gp-2aZoTznUnT;?Oc3rjBZk>7<S_vb$s%dzj>#dqF3{Qe5NgIs>+mE61UUm-5P+vedSzWi=0ImeGI&9&{4-)$wwa|?6%9bEE6zP?*STz=;T_rLRs`0~3pbN;T)@#9&$SD1SEJ01V}Q+&hfAUET=Rp_tLCVyOL{;yS)qEb+mQJp#j{uGTM{bNo2r)XX3{g3_>tzrEJ|JOf7yWLUh4qe_?wveB%Y#~2K*+PDSvW5IQXg&D)T3^@Nz_Eq=Ol9?D_?hsdpq=1H!4HP^haU_-8afGnH2f^+osRXh;F~#C_rf=WUkm*Mel7e-XnLCUC*gmE{>QPN3i%VzPvB3$zXz=kUmtxzzL72ib!mt~ek^n}{8;$S&~fma;rC$MWy;2D1W(`VNZ*A20DdKOBK%7D<<Kec%i&i+SHQ1=&w(~|tj~dO;#hqZz6tyw=oa`v@MEBR;P;?iW6-X#PICN=MZb+j``<&^jQ-w??YaN=;P}wCG|sr6XQFRrVw^2Q8HK(Xg>m*K%3$=(V2rbgD5KFgqcP5=pv*$wkkU9?f#qiCn`RhiO;OgOZ`NX*y^3-YeRC4+*aF=HPsf^$Yh&n2_?0+*<d@@^kza-5)ELK%j!k16qe1Y4(D#j@<KV|({56ISgdd1J$Pd>sf6zKo*+TwD6!L}AtQJVKp0pr*A^5^+cH8HbjW-<rIcNs_bMPHe$d7=&0#EvrWBmyDQ;t>I&naj@_~EGc1GYJZyr089hC@fFWLr<6J){NErV6@T(aYtaf5Ts`%XPZshgO2Gp=0&cr8@K__$s<|*QF}7Cp>LKb*_f?h39Q*K&!%6!2T$g>yQU|D&%`&`@VsF^u)G35ubcH<Xi!I9X#bmZR`oX0$&B~=nj1ezB@eCeF^R1J|e9I&5!+*)#Z|2E)D$){wiH6>XHw7E&Po-W*=RuL9^hm)8$27u7`Gmr){XtRnR{0yv>c!>*32{f0Ro_<UyVa`EJ<0PhcP2ux&TQCtn&lmxWe@r`)KG-JqA?uR}Xtgl56N2v2ph&>rq1(rcmlu%D8;T-3`YpcmlNbSbZk1HA_R1|2g~mk6{s{I$At(WN4^D?DvOb<&`j@Vw0p(2DRSu|LYCJn|q<g?v|RpBdOkS8UrA@yVA!&LyGc;VCz2V^`=!_-oOQF3{faUEry1Z?uQ|i1Zq$gZ&iO<xjm_40;}3=~70Q%Z}Aj@RjwdUb<9*_JA+1%L{bALOa9LHdKe=^}sgdd7H}63h>3T-#@Wm1y6;1XKddqu#e8zwlm_BFNU0pL(9NZZq&xk&_ChJqa80md%(W{e;)0)9Oxs`Qqarr1?c>t{X+}Er_<P`^9EWJ{%YGCvpx;$$QRe8u%ZWUtNGyz2G*w|2KfSrRS=pEPx~%~^`)?`0JbTO^`)_{7)l|mFNA#;$ND1Jz6f&V{pCl@{AhCl#4L*Kiej5mXrBW{S`wb(DXdpmmk-;O!1@wcmxgUhVtq-hD}o#fBagyp1NobEz*@T81*PTp!2eR#Qz4%X{SH1GJ`VjBJ`Vpb^xyFB!mov1f?o??$FW-5v7QR~k<h#0N5a1eeH8vp_*Kw<!LNd!41ExOGW-bWUGUr&BcL_mNhiUNfS(NgAQ1Bd?346JAcrH!ku)cea}L@>`bMCQZ=erIZw>SbdFnILd4WEhhdw5q9O(1OI3_jGp1H~@9oM-i<llg1!@mJP9vX*_Bj$L-r0w5EAwLxQ2K-R?LD2E=gW!ijC&Leep8=f*KLh?Yw42(08w&Xi&^O>W!2bfxf&T^mcjyuL-{F6TegOY7{5t3)_;v6#pf%x1sV~S=TU@lYI@Z61byVjq6!Jr$L*a+O4}=baAB30#5vMwGA$>oP+xy6!^mL#tr_ol@-vVv_4Shp;CeT-B(3hm^1AV(5eNS39a4g8rK#tV@>ChSQq*RCeqq;n&eJf}O_?zfiO_x*3>QQC=joRO=%Q0p3N0sz9VfiL(M}C@)w_BH7Wi<+aBVts89)<syj*l+?fNoVuKMl*%5QF?S?WgE+4|IpJ{$s@04UNK2)n&UbJC)Uc2K+WGZ$mut4^n${dDgL-?pQw++f9M)fWKMmL%I}jtj3(Ae-O(LA|ClV%J#Q|ey9F-5T^k4NtzB%$Lm%cE7CM4>FZ#*4&ssjFYSA1eFWMaz9v0`>T*(9J)*3ys(me8zE@U%P)T1C%Qdkb`FC`@UAlP6Y76+Ph;ak-2>eHSeO#9ZpdYHFe+SF&AO`td8q3rU=r(2jM~JZt+5&zijS)J=%4(~C&&6^s;*oDb?a}20$7+7Z`kB~n26P*IEy`Dys~xMIouqGp<rauXzP7UceFaMWPrepn)P&}Tr{i@Cjuk0AaImk9<=TixzNMCKS|5hK2w$Ck8|ZReSv{<*ucCboT@uRb36=EKv0NS7k)K89lrEnrtIgr7AVvgw7=EW-KU<gkp?g%)&%*L7#31i!|2DM)`nj@xCt~b?Hiw^1V?>uPl+{N9-ovtoc;uVwb@g<~aIEHYte=kU-iCe-U!U^T<toQ&CnxEfW4Srvk#C}GfBy}o{wH4_G3r6{!PD_-iep83IpCXMxe4NtZ>LLFz5YpP7x>$CU)Ry)4`uZiW&N$%-=WK|%IZ0l^tWUAc5Fv}iH^5lm)*+hz3{gpMjhxc@CWqzrMlb){a7Xa5-cx44Dz38KTns3pr0!14<N>V=)LgsX$<J{nX>wDz<<Weh)2E+wMUnZj@8nR_4BdaJm{zJcW7;^OBu)N^G?#Y!EzhKBi~5b{w|7sr~WUBIAyR;($esByc*+Jkrs23z7duiAs+cBv>%}LacF<|y1K7x>vC3E{aIOmi}ttaaz<JGk4pNwSgwoh$S<Ptt;;TD^>O%H5TiEqXZSDm`o)wN^dpt@i?F;1G05-JevU5BK=&%^zeJ2LppV1Pr7@t(K4rCi!0+Q_#3SFD+M`RBW3{AX{akD}2f7#jHm#58Qp&N~$4UCuSZ<AY<mvxZNc~+H{Z9Q~7;#ErpQI(>>3B87u_7(vBz*%cH$Xh{9khR0YYf^CzKQPZ2D<#Ftp22|Z>W7!T}~^jzpJEgg5@UIj{E{0?>jo5l+`xy4H2UO^e6a#>-7t1yh9JFq+fvL1&BfZkoMWSJO%w)S^sau_zv0z{#~l0%QwpE(*b`7%ZCt;{4;tT{hd#5$7*rM`ggHiHg6A4-vZm~Qo^yC=_LI#Sbhfa$ls%Ee-}i*Q~wu4oD$e4X>oWuUjM|gA}!=3{XJN|2l2>1t9@Us|AM{*-$?g$J$k35te#ia*Vn!=y*pA?FRG+(gylxqj{FL0Kb=p?YHRrVh*1xE9{yXsekF}}=zf*-E3mu*F~}d(ewi*$Lcdbhe~TF3KwHBvr#f^DmDP3ue-O(D5s&;+dR;SJdOB9iIo2=7cFTBs_&c>etxI{wYA+}0pThD}h(|uEY=4(Uzf=F0MV#{3Cuuo&I$r<4u_C?3N%|<3qlia-srDOmS%N~os$;c^V?7n}6QM5rMEEt(@$hTlUxN;Xe+|A8^g8%T@Qaky^~!oG<Yz;d!Y@Uxvytl!j$I~QjCHi_LS<u<R>Xd2-C}G@`VKthyc%sHeI1^1o`5z@z`8YvRT1keVjcO}h`9*55Pl+JR)yXGKLOici$Z=J@}+IZp^zT{eFuI3{HxH#@UOyGLx0e|s-ciS3Vj{^DEwLIYWTD8-$N(BPe88ULn*%sjxFTJAm;(_W8nKiUxn`nKNd>)jm0wg8<F!-_#5GmL(jq=hd+lLjs^Pj81g)Z_1{C!!dKR1qu$?5jxFRjqmW+%T@6pV34RUy7HGt=ehd69DCCDjhrkbq9|e5{eiZyL<TDI8R)!x8eFeTB`fC%)SnQkhM(i_!z8eBP4nG9`73ewmSKtRjkHHUyuMDja$gKkUj&uzAY$J~SYG^<Be#mt-t}%42xgNR{o~|3DLs7_IheCcmt_kF68>;VO9cdN#jk+AxWva3|L0M0Q{Jqd?;O~Vm3oQd*7XChHIr#hFr$JwXp9a6lv6^tKr$WAHn$_#mtfxZ08T3y0X7EMQZ2r`q%G$Sj$Vn@c@Bj6`u1@}=zEGk6k+s}1Jk2P$<!d^YKk2B|L;2~ugG$r?(Fd*#beB^94P|c-Cj'

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
