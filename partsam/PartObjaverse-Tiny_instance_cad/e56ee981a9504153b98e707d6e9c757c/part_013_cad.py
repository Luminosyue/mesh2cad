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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_013.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_013.stl', 'source_sha256': 'cd841fa61df084c2152e3c8bcb9df5e4fa8efd30777957a71a46248efcc8dafa', 'input_faces': 880, 'input_vertices': 576, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2057608664035797, -0.26993390917778015, -0.27048811316490173], [0.411755234003067, 0.13431115448474884, 0.27524203062057495]]}
GEOMETRY_BASE85 = 'c$}qO2Xqxxx1Jk9550yuK<GufB%utTfb<$VUaEy2kfQQ4^d?0>K`CBDK%`0)2+4#{5|U7)Ns~(vNI<G6DBwGL_IJiP7vEcNy@zYB@4MeQbLO1A_bD^?X4$?~hT!}f|0|`X-pSF#tgC5cAzFTI%)sc;@AV%zs@kv-<2_n#Tc>{#7q#uurhRvhHb(oX{D6U@`bU?K(972!RIhv$z5Jlz(W9gL4tsle^nih+H|slO)Igz+dbjV0f#P$8I<MEQqSvZeMW3MmAOB?&T`=B`IvPiqA^nhzr^lXb^e?)#U<K>ncD8jdbaU&(<bTyGCfmCCYlN*^Q+ge7w;!m>_8mQ?hpqe2{wq4#x5npV{mKLTzTR@HQvXdizMp%-)|Y9lfBr}rmwDr55`ET|JW|GGR()aX*3>Bn|3_Vp7rF`E8E=5@_;bu(+)lnWN8J51;+`qGiE(LHZ`!)|UUS87R>fbqedvzg!s2b+Xtd&>(*DpmMVEdvUTk6g;`fP4J_P9UzFM=*+#l%jzOU%;kJPQA-za|2=5J*GpIW2(x!+h@*XPbpbobwk9K`K6nWpr|{5qW5`Rc6%rJX=s#tXW2t9gPFuK?YN*Nx1qo1+sHzXj;BpZe&hJpS;>N`ItoPBxYHy$j-PUAvl+<nB+P?u_?*oUQB7owx_;7_V>h=j^Z2%aW9N@nk0VbK4xHeQS9MZl`9?1MdF6qRaURUHhoJt?TH2pzf3XZ~NTNSAWW)18#px-B(~Cw<G(R;gPLtzkQ?j2f9^%wbH)z-3)Gj@Peame+KGuyuQcNY+WD1y7cEOy3FSXL%BcwdHs|A^w%50`o@k&-SgM%HIVx`wXt$vM^9~}+*hA><gndNlN0eu{sijikJPQ%$Ku`o57ec9^fP;GUEh;S@qeK1_<zd|TQ}Q=ss4v<EGez{U(4gOb$`ePp1&(@q{g{)Uv}25(Cex0`qra+JigW)j=Afb4_P<9?QqOp-&<~ty>9C*H^jT^TV+}Iuh|gqu5W~-+4Ii#Q|JM;Kdf7w3m>rKIJzYFe?^*-KY_Z8qod!vrNr?SUCzgLMR;64tX1+PP<Ph7rG+^z7Z$1c1KlXIP`R(s?QP!Y7G+c7rLXF3>ptjCK0r5j{t@ra2Q9rP@2@YP#4Gu5FpB+tVuzBSujq1pfUbpZSMoDZck<`_*@OR@KhR&vALy^-5A;{^2l^}dBijkgALy^-kJBGDf2>*YeBY8Es_`ls%j4QHPmS+}&9<&rIi|$%6<zLM&^74J{uQ7*``6;U-2b#*N<L_pb8~&H=hFW^EgS3ETPo{=)cx67D(i#R?14RgJt(KzK6Fj$&Ut`!t7V9?Uj*v1KmIyXxt$N6Df^UmXFT6`RW`++*7B~l?vHG$uKxl0Kl>eYtj|7YzYEZ1|Npwje%Y5-+24Ilf91Rg&Xb_@zwuRDH(F&-&JR-87JCxh{xrP1Sf6`R@#ibL?9cig_GjzNan+vzy6lf}Xae`Yb}{u_(PbF-^Vf>XIYD1ipW8j&Svj8s>arb2FWgBvpS+^W{cC3)9?$4P$~jPfiTw$>)BZe-$5k<ha*ox{y^MG3vj5)il5E{r_EbG5KR&|q9=hWP=)Q~T>Uk2nDRtTZ`iB+W@lSy6ocB_8ar@Og%K6sO$NsIH|E*k~ayyBgmFE<z+k9THp*!t=_%V;SM+fEkC{TCe8#12tv?9v+KTvo4-(@W8=QbQx;tO4a?(C0a25|j(n-06jWybYWbmuuGLj%^+8>`Qofjazew2tI`1-kS65}-T&`Lq=KdHXh{|F7t1-+Q4X`yaY<J`d2Hb!p0s8MYpIWFw)!ObG9DQm@ClE_B-unO`oj{a3Vxz2BH~+gfoh-3Q&8)7G*->-S^-t-jO)>uWD2+Nc*R%==mG1+j51-3Q&OzQDfT`}Mq}M*q@(M-S+~apjw%wqCdLCfg4UpYS}8dM(y9q1*kqG{WA8y=!%T9=hM_xP9H3F}7|k^d5HW+N!mz@2tr4qS}QMZrul6ILtmL7)v+Xx)FOR$=!}`dMxXwuOzzL3Dli-%!9UWj$6z7JlZkGrr5fFV-cnQ+Q=XIeDT=_hm?K>=sMc>4Li-_n(@9eUb9xV<F=npCo28dN*A$p>&2X-O8Wu2?7zQw30pV%#47#Qa#rE`t!J^{cD6X_)_u_Z(UnqcJyUJ2e`{v4yFZ4fo~?VougdFcgOn3)-GFZPEo1k``&&~U*E^{R?*2<%gYNj}esiv0Fzt}LpHkPPK8pM4zuAuOJB9ZzSzqcpbU7|ZPft#C_digV{kN`lvURhCmf-fMak4+_<K`by{1B+49pAcH-2WW!DE`#uthRN3TYgS8HnltH)~&Pc4=VA3?vuLo!}N7rzjD8$%DABWpv!SN^>JTwYLOJi_3VdIVaj;DAM9rR$o`}5{zzSe?&Qy?J*-ETOHuL`x<7(-nYZSUIL@n}zYe+mpuZo_@rCX~Kdt^pSpT9xlH#|wlewSJ<+!}PQ`rwSUnIEwBXv{iGH+`<fgd9I93}G>x(40J+bYl4pH++U_3)cMErj>^Eu#-A{hXSE&(WL49CVM%`=7k5KOYsZ<lD#jZQb`^$x)@94-4}11avuGV`K?#XVT4NB|oA2P1a>T=)-kxXHp7}3-Oh@7rM+h>-{j^xBJ~magW#XR^{`!-Y~_TCsOx8mw94!jNo<-tx?8nc8KKuoHqH~hyDlZGG0dGmVB;R=1X<wo76Sv{)rqft#%ZTt631A&*4w2W>>ENMsR{VF21t;S?`l6#qED9Yyj)t;1tFG1)^Esb<}d_PoOUI$H+PX{hW2o?N9UNbk_f9o$8Kbpzehqv_EI_xUvt5cgIoc26P!mGkq!N!?YZh;{Th=6@SV&N?rQXlIyB}703Nj8>Ro&nGGDTPGRxxI0ouY91~(#kJ%LOj*HZ_Casiy>Ie4ocu`-*%iNmE_0zkhD)HKKjP<)w>^Icc)}LlSggrUt&L62;&}IJkMhEk`FCt5vJHAr4!dW-uzC1J=KW8kSf6N`nKwZYs7?g+G8C=$K$5HAgbSI9zL%Dv$(c?<~v@6Hw*2Wi)DRG2uKzHKUpe~QA<Hb04yrgb*fR28ek@dKp8B^8!hDUHa`_}Kb>&tk(UZ4A)<0DInZ`}smPWB0w630^Qx&Bwvj=AG#=p9&JHRYH)j#lArJl^8rvF`htPx$=qdl<s&IN~LB6S|DAdGH&4?&-JoxH9jcYtWr|?b*!ttyMNwi5GNT>WG(9|I43a-1+0whc5HS`06m<x5#b#zWyC(AG#IFx{RZ_G=;}IYw!toT(pHhayz|m$GZLRUvP^1)9o(%P5S?nbKK6N)cx*!kh)ju(hn1U;W+MiL%FYiTpHI$o;dSyY&!dY*5u>vIO-!F^0*$a-sg^^)g|kXb~{G%7`JXzs$uKKu&GLX19cf+D??{)XJ=C$k6f1mbQxdkk3Ou24vulhSL(Xd<$O#V%(@x2&mCW>`zNyQ#P`B@)|d1-p~N>pcjoE2k9b@an(cSTOX~hAP4>IvYaO1$dXLv)+;Nn;PwH~Ku?tx*a7Kxv6|>mZwNn*rT}S)ozR!5PXUd&$$5H!kjjda6u2<U87wzT#uL<4jj-%I1=K41h6<urljPIM{vJzjZ`$H}(@zrYQIc4Wn_a#bv19cf+Gpr=*Q}uoB_)6W7x;$^^tYz!^<m@qu|DjvcGsn37uV)Eo{e0RUcRonngzoGY!Sz{hvQf#0Kwaj8@vx1pYm=juxH$ThkxE>o?pvqrbLWH9y;7I?aAuIL`wtg8>5ikB7|niodS9LI>lU!z4(HvY#Bs%!+|KhPMb`(Wa(|BJKk1Hdpzh4ys0-|e5~=F^h3<v!#P`i~zHk37dzJV?_emY`^+x>0?R0Cg&mCW>YrWst=Z>#gHuGuQ54kQX@shd*UB=5Qmg_Y8znYQ{Qujia`JffcZR=M1uax*o-QRJAI`8s^+Pd*>hrRCjN?nt>d>*{kl<O~Vs>b){=BJgo$aP@*FdlEmML)RXXl@<J^{2K~;_LljovoX@Dl74ox)-{PuXogXuAlju5?`r%q09LCynA_EtAmwzNnPLge6KrRPW|0km3)x8wJWQV4_f1Mtp9ymiEp4T<12MJPn~!{_ch(1&c|xE+5bz+D)ExKCUv>bR!QgjmtOwh&L633(4F<<zJA8`TS_4{j(5x0x_@aiMb{JFvUPK84<(M~{<d7-Sgpj}H-8-0&v#CVSD@}Zr%a#3?Yvh{iI>#1QPq|CWlf!I>%N4NO8!XQgzl{WAJ1led}AfPQa7Y7&tvbbU_I(fb^Vlj*DsWKd3&u>#wGJ1P<Qt0mb=;i^~WpmmAWo<xn9*j$m50oo$~{9FLW7SU+^E?&acnZ{rZ`9*7ozha%$Yqm1O<ILnXdeawS_gzKl?G-`1wKuC2MFu7_LRIP1=5XPyS=GVW5>HeXlb>t7ai);&*Uyrk~m@LY}8((c^O?+?}U9(4bchw6D?Q6F2kX1}k_N9g`f-c{nOPl&d4Z|l`cd;@hSzC%s!fBW{zekyf;yY|X{YIa)6ex4k@SBWol4Z3qaEOnUc*WRPV*PHVk-#7RdMK^!H%i~>{ML9qFZ#?Jvee<g4M(F;5IhAvx|JqCLPtV@UdCa(&@tocMXI>@lQujf3*5{-Gwr*T2qWIZNEXexRqUyXmQpncLs9MT-Tk3|?kq`P0Wx0Nvua$fV)SdIg`kJ<`ukE13SLzycC%(%Y@_qd)mGiUIHL1(-j_GUb-ltzF=YOf|(4F<U)l6=Gc@H&?HGJIv5tG&PRmFAO{>qKY^O~>1x7^OUZ<OadBWxqzSN2n`^9A;@p69`FcN_zC=Q${MEXQ}VS9xADbH%Z~v7hpMr)NFH{h$B0l82@z#n$~3uI_ioSL!~g%lO{9&h-z~R^toZf-d7Lb#LQ?eD0L*Goc&MWqkF^ce(zr17h9rmAWo<xqod8{mCBJ{qg(V@s+v(-HGqaaMoMzRo;^rlMGweUhks3_wbsHxqf&j<vodSaA#ZhruJ0cdzkNc;rhwFmG>n2yIpPFda0?;UxT{ax{f??*8l!Jxj!}2l=oDDy7S(n!w|l2tv}+Fc?w;Vx{Tu+<GBAusB&LDViN1azgON<N!@_%yx*ufll|YUx#f<R)V<K<dqus<JRWasN6tT)KhQPk&ilQmF?`=43F`Yj=o)nAeEu+j`*U}a@*dK<f6&(b_a-XuGrd<%aX(8`RNg}xKcD9N7OSkhxAa~<!*Tq4uJV4>pZp8gpSDAJKOCsbc=_WVu>NwU@*dUL`-J=1sIKzfSn3vZ`My!x{gmr>Ojh4lugi4au77-l`ra723Ei1@tFzg<c4L<Eepu@M>$BAN!%OqC-l&cG9(az<?UW5s-rq{y9~Pp#zttyH<$iwn;{kWP{2x{0b|#!S;EtCyEQ0HQ{v&^HBIn)ENY)phPFCXOZGPVEPv`q1=+d9^{lC^e%GSM^qEg&(4Ah<PYua^Xf99*DeBWdl18m*cyHxoeCs233H>^9<)_vpdDBr*MYDBZ%J)819j?_))@_QU_^-(<Du8)-OYou;LcfMaM_c8nVwxN9g<tsaZ$D7_z`M%63Gm+c5G(Z`zulQ8%r~H0Xwo`OE*N5)3ll?RH!=`=8c>P(HaR2u#Q@*d1x&__&oxtPoxS!viSH5oz)SY-e+Q5Eml%Rf(d4Ci4AG++Pd3P(fbM|tgdtAny@3|f5vcCW3PVWDTZOZqRQn#SXeA934V*lq4RlZ-Ax<6m2^8K>+N(}t7P5J)X{CU5v>z}k!zDG7L$FiUCy{F@!KwbLhQXG#rc)IfaveXUeGT$5>_jTSUr>5|DlSeAwUu%1=aDDGvNy_|!u0wa?we=R)U+|MMUVU>K`{6;h!|ryZZb@CXBlWJEl;1N*-6wVU+4t=|u7BWuqB8HG`=C4DpRT*l^+#q;cIU0seb8mzYO9`b{*>RK{C-2~Ug*y6A67hN|2%G^{vP0q=UjhY8|C*TQa7MGzXw<pbiwY=$Ayo&{pni}Z0pA5mIvMa57cGeS~Egy-3-osNQv)z6>Qz#w11Mj9jRN;9X~+VIt){O&*L9hne}Qh%I|Z0-s-mQ?N?ptztN{Ak1P0@^7|jDo6u$d%`OqF7kRGyK1c7+(AM=bTa@2BNnL~P^#AoJ_D_p3O8<Q|dvJeh@A{|z?Ulb?3xD%1zg1DVL|9fWzc#3^>rdB6q<<3s{ZH54tNp+F)3ti_s{eogbZx%q!$e^-faAf33Hw;s`@nJFgN2P0)&<xTJV>KI)zh@>z@p%#gyj-e7FYzl2tH>6dcf-ot0}AscoTfignQ%zW(OaK{!Isd0^S9EYYJ=x-W0qR@HOyk=tEv$M)0B-PZ+QScnS0|3|JF<jIgo71_9pzpDJt`%BP`>czI#vgw+Ao2B&^igZ~J1@a4i*Q2qf|fm45jg%tu81gAI-hi?ccfG-s`TiBPtPr)e`IpG6B4V=bX5@RK-3QoB~IWr6R5%?gCy)CdEcumB#I?w>mDl9+ZKv)Ev>U2gu!YJ@Cv{f2d9lQ>F*ap}dyeO_I04xoj8~4r&%m!XuSY=_wfR(_hy?4<j;d|gzCj#{d>w&+AdLIBsgLgokj=%`;4^U?ca56ZR4ZwAT1Hq~MbJQVR0=@*FR|CHWABAh9fdjz561Gy<eBeCrNw~%YMuUHidaHq7fp-(uUE{nX9IpMdmQe0}0-Os@ZOy@b2p53UTJ#@{*BHVP;LA|w3*a2^!oor|UMC1MgHz5??$rgp4n7iX_5}6-ryQeoE($mV{1fzfIdBCy<@#qD&jZ3m;Iwu%fIk|*7v0d;MHt5-Ttj@Q#&c&da6CAzIXN_*e}pB$X?z(lM#3QQo)}9bU_<am;I9Fzfp^8dy8s7+w-?q)SU4~e{6me`+?l}X;4{G&0~dnp8m}XzfVsdcB2E>6g~8?A%MC0BPWecAFdsM(oaQyn<LtmJ;B^t}3c!lsjWOn?z%Jml=9JNR-652FR1I8H3)mE#?vn@iBFqP#0dWcfhJe2<thccKz`o#p@%b&_o8W}a!3kTr_}lpWHrgP*PS_e@>w%lVzZJGo*jnH>;2VT(5%wK$Gk7y$ZwPA%YysW^pS{3d;Dmj^3H!NtGkk7_Hi#Dx&d3<VP9gl=!~BuJzl7ZY{tBKEWmNAGG~!`GFDfiIFq4bd#Am`n;8nymWrY<3<^yjltc|dSz;N)!!m5E2R&nw2_*@=s5ziy6jIa{G8sM?QjtJWT+zwt?SSIv=Fe`YPaL0LJ&wvlW$sZ>%e&QGKIS1}t5Lg0yw6L+l`T_fbQ@<(-djr@2obFE>{T~|RuNw1E;k(!1Tf%bSnc!QBMIpqK_$pzmg>41y2Ja%Qld$)I1HozRe`$RGzi@Bjk%&P!up#(Q!qSDE0^S5CpO?b;N?~lobHUg7fW^SCqOHroQ{ZPs7vhCo0UiZkD#}&}n+}`<{<^SM@L?;A)ApzEM{!|!ffc|%5@q5+K${Dk4^Crwg7FYO0MCG!W(O~b&(}qt9%~$@$A}g2!J@1yVolf<ybk)>0Qd&@P2B4#FhdY?y0!zZCu{?LQ{3Z}u*<+i@Eqd07r6cf+9RF}-zIpNU&iMjg`F4n3-B&@d2vlPVfliX7sKa=qAWOw>k$5d`VWDB0`G#K7IsP4LEusFM#Aa|YX@u%{s-Fq8<-#bXEC-UVJCqWco9)vMp$NG9`G6Bn%TmZ0hfc<2;yrB0yBgEF50>)EVGC4Z}7^ZOcz!Hm=C;u5SLX0mH;m<t|=fa8!!mGsIa`$9xx1?`W%ja6P5+1d)3DMY9j{3pHZ6vZvpRnn13&9moOjjYw+j7LU0{n5coM^e#FO**bvWyK9m4f1HUBvaYWcJz#qXki)(h^{yT7Q;uXa;IgvLxkvo!8pRxg;fo~MJO;{Z8F!*o6(mXuQG>nz_yTS$t>kRA&o<g~TYkx+5$04sMk1`{l3L^HO2tH5Phrn^*Y4Fi4;A!wgVe!c0c;qtiro!qAs}8IH{#5wrzOdWCpTOzb&A5Iud`5h#u$dn2*G%+@IL+l;SQ7}dg7*>D3;yT@Ul4C3$|Hp}07ih<N1inTMuJyEyz2wQ!RrZYD6A5&4tPc6Wj$a+@M6f-ion|7S%j4i;x&~p2l#KuODYdRoh-;}%GKY1A>e0(-4m7syb7L(JU#=w2YwW}oe1=UuNSso*jK=v;46{G>w){hzeaAa1nvNzB<wR`BZ0HPM<9NafS-YnLrg~iXM%SVHbmH4z~1035Z7+NA>bVm>lVOX;FW|m@$lYDSO;7eRvYEDQC10gS|8>0QAYf^$kF@)p8#`!|0XO1<%IdcX`Q3>j>-u`zz+z!AuJYn5q!U}3n;&UvICeO_fdWyWyH4%+aYW_a2NPCVLMU26J=YmKO~_%31!503;SN!Vc=fyL&El;d=JWYW1TyK@*^lCeoI)Y#%CqM>)?M1yN2>>D7%II<SxqZqKtSE;U|xW&#;8Kz{?5C>EZI6C?ih$MqZTXMH%sC!fJZ>j6fI(-d<P)$|F!loc7y#D6fYy;=_dX5H=C`4)}kB4MO=Klo1~z%!_g_%7`x!HbvMv;3Dv~!WN=@A<Br;{yZDyvr$I;kg!d{jsy3B9}~70<$F;^oc4`vDBp%M;*W)0^zbtc;dO92qg+GzHIxyj^UHaZpGO(-s$w0=9>mWygayEB;H**=m>s+z_L~~O{HR+K*A@b5;D4cSzXC6SAII2_0Jnp$gKt*==YUT{?8XB7f_Fe}v;l^LQ_fNDl?CPl{|mWI&jZ(Swk3WTbLSK=5qvx5W<2mHcr51rdEf(ZT2p9kp))mML2z2LXzi*9YyeJcBCU;`fCIs4&84+>Ja9fZt?9J3uLkZ0r#*xAj%46vaN3h-Z+ZaC0A2}uUvXds@CMjhUjvo{&xL(5E3i0tT@SCZO@Z~n>Av*rL3<zJOK>^^dyrEe<W+v0qiA2P4y*@GeJh3j5$1LAD)>wo3QqfNVeH3*FEH*q9zN4Q2L1_7=hC{^*Xv^6Cr<AK?qE*cL0#f?aqot}I^Z;xj2KTw%z^CiTXp!XI>tqu&T?ll56@zr5~s5_ol{;1HUh7L*n|RK1E&~;Ax?z3!7UG;9S;GIfrsImTEIwf>cbWE;|k^~@gIbJ=izmSa1%Jq!NHh^g#Ex%J$&!uz(e4l3;V{yYa`)W@K1$J@bEJ);b`zLJbZTa0Y3q!KI}n12={?65H{Jv>n!0EaB6cR+9ezd9_`_?=7+#{!PlU#>wrtZhYS1I!+Qkbf4~=E40C|f!OOs};lN1n$*4C4xCs1xVLd&(-w^h2@xk~!7=9;C=eL#c$x8Ukhw%=_ScjvJ#G4C?^6*|s*dDwq$~pj>fz!T2ITHs=0p9~3Z2&F>H-y#l@V-k})5RO(Ghrk+J;%@-I1juAz6SnY3S0qRQdm_FpBV_tf$u|~wgWeSM<bpifaAa^w<$+Y0%O4o3CrT)^9P{^oa!7$J;Ed4bT)12;d3itXYgw1Yk6Q1@P}ew$mrp-6XBmYM_ossE&xx0Q=4_sE@4w}>RVy-k1!YbBhl75oWsuHoF@5We143*k9cWuO>PfA(-9U2&xF3xKKT%RByNAljx(emXU5%V^Qy-0i3o3k)0vy@Q2|&ToX!bFah4z~2~N*L^!!{JSQu-0Rn(~gECNo?L$^J=*Ae~%PGbqdcnAxC(>pZUYr6nDfzzHudlNm25vGA35O%`D`zqlX@VAAH^6)!G!jHh|IgFmG?*VUv_r^5?f$xE*<5}P-@IH7l&h|e8lfdcO<Aui0C4}@2M)GugPDdNW=^5j+#?K#ww_Q9LpOeux@dRPVG=2v~cnN$P$}HeX@MCy(xCA@`ehB&TBk&g&e}vD3zq|M~d?vgLUI_EAC@?QL`Fte&PB<RCF80Y%uKkiY?eCSbw^v3P@r;=BnSn*YDc13bH(?_9m%_gF@cD~yJ$Pa4>vYbjj{TlE<#0}%L2{xF@jo&D{|06Tr}d21wJ>01@EBoRJp9~FxD$Lc%60(vgWpCT{{&12KZo4D4SWes_cCxl!baeWg-!GDb3WlLaH<o5dW7}Br@=>afvdn{;L|O@1K^wC-x%NtaM}lH-|G+bf|Jj`fZqvMf-gqdG~k!uQ&Dd*@LTXG+@l?^Klm(MHy=0`ygjaI4QvPgCE~vdxEg$@hkgssbDeM$IGr(~Q67yl;&hIn^TZh72jElD-<iPAz=xu}A;8|?bnOCMPdEeoO<~<V{BEAG6*%oFEm7VQWpCozg}9z@Huxy?c_eU>i$~)#;Rx_hVXt}kyCcFf;IuxMMtNzJ5vMaDoi&#MH-fi9-`)at1E)HBQIBvN_&qU~f(70IzSNkfWBt4b3`X6xxc744GH{w_l&8CaTfzGv2EBkoz^Tpw)FVs)j}iAcAuI)W20R&SaSZSTI9;2B>j{&=_ldF}gdGPS1V4s#c^~ix@a~9fH((3!GVpmRU?uQ#*yA4quYy0q+I<cf2mU7Vs0pwRcwOXCZD12{I=9eyqA-xo8N_Mr&4}`hD9eJJpnS;>%mGgQqG$D+z*FFK&ZP5JV_-FKTCZr0s|73x{u=VH5>N-H^ERD>2Lro;(^?UQ@+g$`M1D~&Jpt0Y!zYLh#pp8dEI6J2>0JIPZ~{2ZJDS6jfy2Rb!xtgI{NVSH*EfI{!Rh&ko?G?+*MR?k{QeI3IXLxgJNic$4^CsDdGZ|d<u`D8PNe6$E5KB6I>Xa5!dajNeg?T63p@bs!83VA;3IH)KS0mt9^f7Dz3^!w@G^Kh=JW;N4e%7qwJX3h@LD)Wh5?I$m%-Vx7O*5Z?GLmEeE=K-z6<v_3cLb-2IETuo(DgHd42%6AN(NZ>~`Q*@b;}dLHRTMcmL~xfBw<>t115@gTO1*pN+b&j1_G;KO$}4DkJ^QM+*}F(T|w+c<IxB0l7^KD*'

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
