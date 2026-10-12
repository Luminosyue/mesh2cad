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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_002.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_002.stl', 'source_sha256': 'ddf090425ed03f70a97272857fc179ba72187c78295241884623c100c9ed9b47', 'input_faces': 1288, 'input_vertices': 743, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4606434106826782, -0.4999998211860657, -0.428632915019989], [0.4286468029022217, 0.07046964764595032, 0.42863279581069946]]}
GEOMETRY_BASE85 = 'c$}r2cbL`08@96x7OEgcrLKY$MQI8MC=nDDK><YtM3xRxrGubBdau$HJoMhH2omZpy@T`x?3JG#8(-ecJ=tW={_$Pk=XJe4_j#BznV!kyK>g=4WzK7<|L(O$pWTpJs<vfGWViBKz1wu}*`ZaN9uIfv)-S=z<@@rV*2yn4s#m{pg4Nr4yJYJ&Jz8}ySv9F-^|n<?mPsnvwrlsE-CJ~N-nDz{HsaTA(Wyrp&+pN`MYlHI=Tem)saPhdV(BtT1C#zA|I6wX!Fl-Yi`zZ5^E5px>MR(3q(;cM@a;SQJRA0%ojFeXzLDP6KIz>O#Z>x1w{8@5pPscl?5F*D_lAu8*qkiNf1udTNIu$6zAGi{yVc9C_se^KgGl-qzT5Vjy^(xMJigY~U0L0*pQQb@<@ZI(Ibq5gKmVM~Bk3LOx4)Pg_U&79FZcb*Pj8F(w<zDfK5c&_pF)k7`P#MEr;+j(#6M9glHQt8YOb#j*4-Luhw1p6AB$Yq!gptU6v@Y(rhGd&|A9z(%3PnAQF*Kf@y+tA96uqW`Z~*%Z`RjZ|94CO`Z=QQX)VTY7i~|kLgnPMZS<FwjBoUpmA%)y{^vS(N9twu%kTJ~i$}+a)nECJF;1*H&kV^hpJ_vszi@2yy3>{K{5bbu#E*S5%=eA)Y|X(p#<Nwu^>E)e=7p8x<OsjMt(Hcwn^XB#g<;X_&N(_RqkNn<Yfbb&*SDkX+)???Q`Zkg(pS1N$@hQl6-{4R`EG1WB)wI5<p+K_?`j#X*ME~g^z+HNDC*x-zV+7V!;$OGN|^6|9-Sv8Bj2w1Ml_$<%C}xR9?hrf$4mV5=5?zn-|c2xw@jI(em+L|o!>^S^z$*>;dkXbMmsn|TCDPYvz?#0w%X6%>_>dJe6%0kM?0_a^D)MobGfJTjq&N!&AK-1JB?Oc5Z_#HwQsJU+BetFARl8r)V{eM2EMVr1^FB6TTmWj9n-$Kjs^J}>s656Sg!)#SbqZFSbqZFST_RSST_RSST_RSnAd@C%<I56=5<hCV?GAyjrkb(#=HxBW8MY%8}lnjZ_KYCy)nOn^v3)O(i`(ANN>!ez&GZL>FfCt<ZsLiYfN30K37qHKjR+0_fW*2Q^()8IQZ_LmFcf`DnIr)+IOodKUwc{v_B)^gs5$#ceGD>dqo!Cw_nTcmnUg+m-AuY8u;pIHU5?FIz7+(=_~yDSvbA+op*Xg(%W+@`@S37dOloV?I-72aUxt_E62@qe*W2~s_T$X;FrJPU)T9_SR{RH{us62Gkj~`@e`5qtW8n=iuGsw^v9<7{bD~g*7x16<G1+v7pma5oAsch(%)Y5e7L^aPg`8_WH^6odY^M@-0twp>ApDQaM-u2EIJ+WoAr#8$9XRQF@L;lsjbTM(k4G2d+cpT!@h%`w7B}Yu%9+)&FPHNyZ9FA?PK?=^t!&YOCAXO4!&J)wqG7=b0Jm!(yCp9_Q!XYcQ_etf4ANbXT$Y!AL!%HN2}9S<?q{i$@dwb+ILfx?=U_CKl}2d;qk0}2R})V|I<rU{ukDs3%9fO?Nb~5ayt0V^Q2#R|E_Sq+b7>u`A?jBF5I5lxAArR2mVvX{rr=R^cKEue<$0^YQAw@>z7jp!oDs~+I`Qc@$gg?)eg&P&%Qq$_uJvON~)aQx2pU05#|xT-D>%<$owi<T=~V8oDYwG?Yos+HDC0+sIJxp>*C;x;rXb2`_IphMdsH=OQr9o#*bBbOG?;JW?WebjZXOeviTb|zBhC^A0GeOcjo`)mnRwDetoO&TYqPcmIpuiT&v^Z@;E<@RO!FZc|JT21HVfXH6HZ%Y}{X!XT+Qfk#Uai)Jr)Y9_RM{<|?1B$EkK$Fl=+!cY5ADl#y@Kzi!TdQX~23elNPt?_b+$`dN4$SrZ!i_iMY{L&{(D@P+U=5B#!KPlU(0)vkE7oL?VUm!aS4$!%djD8G?DS^GNuj@+tV&Mg<h^F{lX_8I?yU%vH;@O;sJS~=wh>(%>NRQ?mkoePhD?K`RG{C<q#yZ`HZCQ`5CGgf8fy9MXEVLzy^kzUu=A-&zBvzmupe?A-O7yRUJd!O?Ee7y3lq&Lol=dV4i%*l-W<Vr87`{^Hb{Le|uBgg8tC+yqIqohLp{e0|0znl(_E2nq9l(3(+K>2oyMgF|AYMoa5jQ?(4_OGwkReT#iSci4`mB$XN@f=NW;p=tSd3lRUU%$rLaD7eRp}yL8^OW{A$w;q#-9C2f8S1)Kj{Eluz3yp0x!*MZzM$7VyZA(veq6H?k@<)pE7fv;*tbTg{e=74ct8JOAA)bacFxZ~xbHvSH=6&J2^+(H+F1OF1GYrc>+xCYiKQ9(x8B$h_Ji?hq}Suqy(OAHsFzWmz^6R!urBJl4Q@o%RqZ=Nx<=M{tA*MZ+T0ghy-wmg+!um%^1gbiJ@d^=@m24y4pmovt$)>ivp(w;zTLT#zupG->&%Zu@^P}Y%h<2=x7zm(uAs^@>Of>&(!Q;I)|tS6ewKgTBqP0ruh%8FN%?5Mcl~O8*bn;s!u?yrzN_2cNFVeI>Fo>mtMc?Z;ID6PQsI=apH%n@wT>kea>Ksc;{Ahuz1`W{!@hN8?ruN7O|AX=jy2}ysYttx-g+n_KX#>|+D}%wuKaf6BJ)W5X+14f{`vU3uSL^eAG#?+zv=Lg!+wy@Pto*&--PtHT=IQud;_IlJ+U|JCpUds?Yo-%of1i3xuY6a6W;zb?Aw`|t8rWHFE^6@uBra~vVYhb@sp-aJ>dWOfRt@vKelYn9^Zee;l8k+_TXH#-($aF-=1<RGJd$vYCjl1+-J2Pj2|PtqkYmlZ)}gYbBk3QGxWc0wk7Nb?VKD<ANb#>^j6)ak#S<peC|+2zSCrknnznkMz5P%cw>hC;GedHeXAGOO^K!t%JZH|Z;yRWwZrP!(RCg_$p6N78#448-1|w`5BjA}`*mSI=$C{A+roa5UbkB}T^z{=-#*xNXV{PF_1s7w?5~XULBAX2(f#gN(eecC_Gh%dLA%wD*4Mdqd0%+`+Pj`o^Ww<q$hxilpx>KwpEdoyv7?cE^z%;k4tv9Xus@me&xx=f?0*W(*&WG;{ZHDAG__AyT~?KUWnFdd$n%T#t;RRhIiG&M)_$GtYX7XC3v@pAHub!~elqa?xvZYo+3yAU6uK7O=NNvl&(Xd<f2h)SXV^FQfx&ePGY@{bx+mg4J5;rkaa|ifE}v#2)qP~VQT{_Y)N{}auck)wxo5dQ&SOS9xCMS!>!;Cf_MW-iA9rmF`>||YeLvY~|Kw$bRC=?&dX-f7wX(15h@{u^Vos5W?>_dBT8Hyxj$GHul5MXV|LgWe+Tn1O$UfOh&XVD}6z8)pY2RFzv~R9UR=Kp3k$IulNyFFcq_y?L$;fqCx8r=)ZS9-ucAU?;ZQprN-51UK4u0Hy2S4t<gKyq<>{nJr%gKE|&gZ_bee=E_=X2k;ug;C;qt|(Sb01<|9~Et9z0Waxz0Yx*4pQx7>?^cy?kj@y#=b)P=Ds3GZ|p0yZ|*C!Z|*C!Z|*DH?Jc7HtM{4sar;vIxP2*p+`hC=gJ^rQ50CTpKD_bc5kJ`f4}DCvkFmeizPZ2EzPZ2EzPZ13)|64>)7bxO-`xKPzOnz;zPbOm+TW+jV?Mv&o6j%Sr2^4@(a&Z0anFf5z4@GI`uaH$KkhjZKkhjZKkhlv^mTbo-lpnhKKJ3rJ@@^d5UsDCr}%Nt-6wux9~ONM)xP;0>MmF3`{r}H_T!$@f7`8m<J>^|=DC4$*L-zd^BlwQgZn#v+&PBf2lwTbQ`P$z<J?C3apyKak5Jb&&u#GI&TVvh^V|mCJh!oj)KKSf#<`RB&2uNKbb%9*amcxu>FaYg?VIOp+BeVHth$zJH}l-g@O67yKmO03Z|1q2_RVuScd^=+nCGH#KKC{4o9Ck1k2@DV*hrlh8|RkVk2|;QQBS2e&QY~*o}&i7agM5e^BmQwUol!Q{rrv}cV1n(yh?ALGi%>CXLi;+a6CMo_4&5;&GT)mMP}t2=iAl=))Dg@9^X8NciuXs>SLbsYu`NQ|96h^jrR!JH{T<;dq%4C#(NFzo9{L3#l2MdjrSVbH{WZxf7Vm^8}C`PZ@y=-s#a6J`5p&9?mbSoO1^KtZ_<9;`=-`v|82fk(!Tj#$t}cw-FQD`m%DN_oPY3sZRjPn&YJJn@Z;XEY2SRmh9CES?Trn}H{Jtk-+T{f?;D`f8}B8xZ@!ldeB-^O_RaT_PLa2chR1m@K9{!kee*r6_T%2e4y>uJXTFEUk9!Z>|87-I<2|zW&G*RKH{T-%`55n!t*(C^@qOdHxl`oik#K$W__qch^8L8?<M`(LaVPJmDj(zhyY}PWzrRs7a@}BF)OY>+T-@&pv~T{d06*?`1^DLg3ak<@`o8%)2ko1`b8y<9Qu}`6cNE$;e@EfGw#47>n!nS~zWF;1tM3cSH-0ywee-uCfp7e7MEmCNMx2?&RQ|^ASOVYp9gCAA)jwB?`+YBd-0yqw<9^?(^D%zkYxnM^_6vDcKCb6)&%n194L=h0?OiG#Gkp?%kUrBv^?OO`YaPA!P}q-AU+r60epl&ff1SVSI}26*+IMEs&UvEgZG2rGYe$1!e)`6|hu^I3GupS_;r)#Ej}27kXBE|WGyT}Ry&~!DGry_xp*d<iJ4dK5zLi^zXI)=+b9;3zl_PzAg?+06^Xta2NP2sLnqQ`G?N{?FDCdAPDu2D6Bu??4kKF-n{pWHkOU>wYwZBxY4?(@Y>!r>eXRGzcYB1w)*mqffv>&TJU~l-k*42FKKKjO4<-e@fPuE)yGxWXnGwi$Xsr551z4l4(w0ubIFIeX-+DH3IE7Ur#+bz~)R7#|MYWMY@vy=Xwqw>-BHO8Uo>v5=kCkOYnJkj*Y_<9_=U2?16lX9PR>Z^7OeD1TlJ(GI0QNMSXr0(xQJK$URj&3*nq^H&WJubcWN$<Y;duq5H?A$-8eR=sm)OCBP{fr*Z+IQK{1oL`vA$7jO{>oy!Y2U7__E&lw+Vg5E|5Ez?E#lu$`!^Rq)@8EFpZ%eGMU5-%+Y8kGP>(mO)%VK(Cvzl!?K|hyepTn6mcN1eohkcai}4WndOwUGOX{wE7telMk2mdGFR1;t9&gqsS=By;=K|gDfzNY6(C_tYsr&FC_52d_BfiUXP0;T;eFgRWVlOe$^Sl$xuY(O#`bp|J%c9@4Z|_sjS;2VNxLEzJS?|XV*E=8fgZW-mo%^KKRlftZZ}QyDJTiSfkF=k(T0LLud8B=J70=_$qvU$(ckWJu8fPQr!ME{sd9?55Rp$w2`WU`WZ@pAO?WZ{R(BohGR)2Nwp~rvH&U)&1bB)u_Rl<H!V|A{g$D5OLgvzJkjmY@azB9CIWc(*J*~odAnlF011wQjdkGJG1Kd5}3`ZqG(w4cT~n;vg&UQ6xAM<0lcH|<;adb|aGU3I>v$D8)kIQP@zEv;lhb*{;|rPZ)dO4xTew{$8Nbi;mfOLcB({T16D_N}Yx+|v4{RjPlTQ%hAo`uzExC-#PYm-A<5^j|4q-{$<;`nBJuVL!(Cv(@>A8_A#ZXQ$}ai0|t2=gWJxMe<p$&Yzv$4faLSm*M>R8MU6c+Xt)n7^~F#IK6&q-{pOrUiY-`@IFqjSK7CqRPW>Tybkg&d@V9xg8X^!<`z-oKS*Chy+?D3U)>Y-lb=)X%glUid_9kXa_aYG&MT>r{0pe}WwudHyCCn&jC#fN`?731w?)!t=ltnvw0*4Q>V27Gw5QGcGOI<S9g+0CIM3NuG~(M;d0*ByF>+liEAPu5Shp|IK1bC1GHY^vb*`Vc!m*6Tr}oY9seN;NYTq26LH@@04DvU|XONFEK7;he_;kMOcPyj%t9^6+YTul{+K-#Rn}(_Sn(GgK-1?(^bN#_L*B`6I1b!DBT@STyu7~#f%T)fxdK>u0dTV{MQ~Abvu6=VocebXf_B8Gn+BfePvFSgke2n{%_Raf|(<-NW|7_eJwQt@ZwQt@ZwQt@Z-49Bue2n|M>FfKu_Ragd_RagdRd%iNjs1r9&HYBw{ATJL(b%_G1=^_h0LDH_`{q6>NN?<;g7n5dD%N_C@0<I&z&G}F?wUg?A7kIBeRJRF{&!L3W9&-<-`JPB6LP8Fw;KCi?VI~vEA?@e-q=6Ky0uZhu|E%dV}EW{>g)UF{$Km%{@*D*TKUHFh4#(o3+JUVC&T^j+<INr<Mxv(ALIE*`{whJ_RZ&`AieQ?l$P~BRUYGcE%43fwOFN7zHdH18h-Hnh#&X-h#&X-`1+HlBJH4`Q*w1v`5Vu_+BctntvoYTKF0HSoUi8vzWF>Jq&J?&(>kU`%BjbdbMS!go97AIH_sF7<|lpMJg*3R<GdnyN5RvP_F=rGwP~n)<Ge-t=J|>J<V(so&SA7~p2NgWk5>5`=Revv&wuO<sVX1id`bJ}`BLmkvon7F#`%@@&GRd_!D!z%&(lmlSfBCD^EB<7=V^``Q~4O@d)hb8_w3<^Kl96Jo;MnPaDIp%cixC^o;SwM9#rS+d45#mY3>($!+!GF*~&lEJvBqW&ue?ae%i`ysy^@S+86d+?Qgnucf`NZN$qo1%-^4p?@TMPE9}P(Usk_AJpXefy`%kRXLd&Xc@5S6%*fxyx28w)PyR8%uctLQT7Fymn~n1CN>abGIvj1E!0#JvA8XVxweOv$+Bs=Qne!R7zxK`ckMn7N?VIhdeY5=o-)Mi+*X^%;v;DPiwtwIo?XP{a{eyZL?H{B!+CM0#(f)CM-)Q@o?Qi{}-eV-M>JVvv?b}z2tNqo-HBvM39cR>@uy1{xtlD{Xn|)zF?JMP5BU|r|<a52MYX4=W_h;lg<6^tQe$dW?yYA1>H_9LQJDNuFaW@TB{bF1<hHs6JUN^~YuIj%gS}zOVG3u4JWu|)0G1|?=w+2Pq&HbTKO3*L$Bmc@w)|2gSq*eE_^dgIu*J|4$^iRx)DgSBB_@9{R@W}twKQU9jLX|52fB(iz)@oiEp77#vv^xAaToru`t_oN7;vp|edGR12TnxPzE(RANgzrO3!lGs1```x%;fK+(uxJJNVYoc{2wWbngjR+tQ-0z6UOekX0kjVMloz?YsEKBW@ABd~FY=<#z`4D6+KU`$E%<i6o0SmGiROYu^T0XbI|<>t(fsh;a3Qn+ELs#U1Q$n3z{TOxXcAl+z8@_J-wzi??}7`%_YlJQ(7dp2mwbfq9cT{t4mcZ{1<nTFhTa0-24_ZZhcm;sqFLd*^igi~Y4~MJjiH8U8Mr9zSQo7WOWmKRexlF8Wyz}o`U)&<SdZ`3<2%AKUtY4*{19ybm-C_#f8K~cdx$=Ik^EjHFX4(_yvp}p<vZnQt0!q2(HgMK<u|;jhBkw%!Bx<va25Dbv@tAmK*p|(-VRIO)#CcKxONu4)0px$rmPjIv()`w^ac1eFPd0tzKT|ctHQ6NP2dvr*^6jh_;u=86@478Z>hEB1@vC{7TW4|)P`jpkbem*7n%nyNnT~phOm^i0`(Am1s?3hTrWQG;y8K=oeQ6W&l19m3E^SrV0akZ+lw;^-uJyYjh=*0!zT#g<6fkqhtZSpVfYAo3O)kwCWH^7XW)bIAwoEX5I%;UhL6EV(G&1dc%K)W(Y@#icrUyMJr3`IH-+lCi4dMj2ronr!wccngzy^l2z-S4uOWnEUd%*ypu6E6@P70le2_NUPY53%gm<DT@J{#xFFK)f&=fd@Hl0HVuS1W*>)^HMK6ov>DAewY2;pg7OhQ+oo8eWki|&Q@(jP7%ydB*HZ--YB!V}S{@I<&7A>0mK2)Bc~qO0Mqa36FH+z0N9#^Ani=TN_PCWJeB(F7fX&V<Ln%g`P04*GZ*A-n}W0B?b}62dFco$v~H9QpyQ$HX{7_;o_~g10^_vy>h~#XrVp;Vz_|19yS@qwC=Qa6fb{+z;-CE`mj;!QJ5Ygzy^)>0?XyyjPyna?eRnDqd6mY!ciQ9!m%>M_0ki;ZIN(7Tpei0)LFIgg=It62ha=iSTH+G1?4n4C^&q_!QbMA$^?}K8|*UC4_gPeP9XUEofg@LiiK3Gb|yz7wrg32p_f5$FZ=4@HtCGlTi7aP$$tbp*oJC4MdlP+GJU%-ImdoqFX|3yM?wF-3p7Y2=&Vf`cQOSs87d*`h6T@LG*Q4^n#T>PK3`}>2u&bA-t42E~ef`(Ix0&cro|dC4}&Bv^P8)?n4OoL;J#_BjA4UNOUQ@l(LN^gr}p&;OTG*Dswdj?GH-`Z?jYgZ$<mTqTOH#;azBZSVH&&`UWg2^Ya8D{2?Jc4?Pc`r*88I;UVY<cm!=Ugb?nD_J(`HJ<!2$4|o9j0XzU6Yo+hK#-cmnvGBX-7FhHX_+8i`geRhV;fe4x^eB9kaWjn&ehVEAzXi8L`@nq|EA0s3_UK5sJ=`6g4tIwqp($_*V`35^{2sa$eh(gm?t%xw<IoeZ=!ft)_)S81AUY48M;{MFd%^?Z&S(#~Gu#Os0C$2rpkv{&^jQZ&xCQFKE#Q{uM7Sl~5uFB4qn|pW?ck1Z8?-&#25yUXhugwk&`Izl+Pw=Q+!`GOw}xAx<KS_$bt^(R865}@q#cvdPH-~Z9PI#ippBXn!WP=nO8-wd0qqEPr2YwLTQ~vEgm!_uP`6Bka3b0YZbexW(dKY-%8`gBz?o3_T*~|3y<YreDgD7xEFpXqy#il_uajQBUmJZEt_?RrUx6FJ&!Er2&%pPi55o7uKUzxVnm=;wEAT^}U)GD~(R#4xYw+{%t7u*LRk#lNFkA;NgZ^SEE(8D1Qu;akKlmE@D|`+9nfR6Rib`397klxk7o*UR;8Ac1Lb$XS51{kVkKlRmF7#7)7d)2`o{cVsXTu}CcnckbE`|reJ<w5b5BNT`1biRtdUaiIDP4hzzXB}{O9)T3((5TKAw0p;dpsTQ>D`_dNKiV1&*IM@gx^8C!tcN{(FyQOxFpw*Yn3E~XQ1=o8Sr{^7rY*xj?RUr!v%=BlzT4iem5a}4>}UQ2QC=un}URJVK0iH-O;z;?(lo)Ab1dc_8uYJlMpV3-Ur`D9~R@Y@D4(FgO%RL8wg=J|JUXF)KV(mr~KJ^_)~Zcx&mH7-;W`Ld!ZBH3G`(zLil}jJUpIp^FCS-mJnW!7KRH`-sO~S3_ONw2!G~9ZZF-JmI~qjEEU3e2;oNw;in1Vmk8mP3E_r>@Kc2FBVOe9;%zT_5yF$v58=u1d~^dmA6|lPgO|Vy(2ei{cnUfTo&xtq2f)4IeCS<pKKNrx=_X6D=oI*4IEKCr$KcUuH+VEW6zvZWg+~#>AEA@skKoPdMtC!vH$kbibza)M7n~P<gy=>8^rGE$e@&(jC)4h_Pv_Im^J#b8?@Jg9OK5jJHWn~m7SQf`{7hj?O`+ZO80*cr>rK1sahQ+snU8+>k2a54>EkxWSdP)YdTftoypN`RKO=-sqNCuG@EJn*3-lxS3;17jGyE@nXM$2`>pN-lN8m@83wIL2`n$q9e_>q);gjfRl(C}6k9m;`eG(R}1&i9SXcbtr0xX&n7EORf|F#s1eg}(w4U2vci~a+PCX$bY@Eu;{K>xIqCc=M`J`I)crxC(O(C^_R@E-JQcn^FS{SH11Uq=6iFT;PJQs+PTES#No$O&hMtD_a*>TrFu3S1v<gW7N#_)WAH{3hHMeG+a9H$WeQ8^DjF72yM3`44%q3S9%Qf)}8R;05q3bT&K-o{uhs=ff+})$mGqKY9?}58s}kG;4xl3E>uKE4T$b5PcUO2oFVv!$aZm=mdB?JPaKH4};%99rzu%B_Z6JHf>FNx5n4)@6bOEdFlQdL4S_m+PZ%y(Ek%Cs~!)-885@Bn;t*!GQQrWE%bP6#dvH*+v)Ks{0D7(&`KZA2N~}N=^H)%S2I6W)0cX_EMz_{r0@0on$7&1%~;X%aS`)%5o1fw-!;tdHH<|)--Ts8kPyy>9)Pnkj<a}rTY}Qx`7HkLgzzPF6?_Tahc1Bk!Mo8}@NPI2oe!tN7txjQMff*#Kl~efYl2c4-?tLNRnZo3Rrm#TAp8Q{932WbhdZF-;SO*zIt)&RUqs)5UxcfnEn$iB{JCi5Q2NT`Ct4$ve+{lLS~FChnv_@ciBS2Upnjs2LiMdgdx(|`wNE+PPc(C=J%y#cMQ?`M|0ew-dLz_dH|S5%Z$kb14gD|rRcJhX#ds0@HZ*>|WqgVL6&i1UF&;&&g!J)gF@7b4Zy|&;q4J$f=(q5<TwC}n$|w8{br8NmJu}e;naMLV?Uf0w1XrTnGodx%n)F{Lv@%?oagd29Pua^eR&-seQNL=8C0$?PENE*u3!E(>eQnkAT{s6?F(G|@5WWM=1<P|>QbPK3pRj%&6xPp=!bJ#Sd2aK6f0vN{tS7t!Ee6Xo@8AUWOf33-Li#hZ@C<ZFLi#hca7nayLi#hfusoxSuCvmg*@fkqeg--RT?fyBi}F4Beo^up0uP}aMbW`<QMeE~9TqJB7lPMXN~IiYDbE~u4%Zhhg!<RA)N`afPi{%{_PbuBq8s5<crUsM-V3J?!u!yV;eGG{^b`01d<fkJAA*md+hNfi@DcbJA$$Ve1&i*1Pr#?p-S8>+Bq4kp-3g1j@NxJkA$%D96g~_eM7P4CTi}E6el!){4}V4opGNn>dui*_gzy=3AAANriynZ_!siL$i|8Tv5bb-B5Kcpn!D;YSLils^1pGPtC3*_}68-``34Z}!LyyDP;4A1+_$Y0Cg%G|>2wy-C!WZCk=ze%VZGDaqzJ#8JPt&HC(6jJa+VK*45xz(pT|%$IS810^=$G)9)c+EC4ZcR*E}@s<%hcx*WxmAc5nfF7VxSjqqvO%3@OXHZl;4~G=e_uh5I#o;r=eHiH27~q_#e4<Br5%i&sX5D;EU*aSoAD>5x(HXm*{2mEPNThgnkBJg1;t&ucGJRtMD~K_&YQW{tnKPsPu2RWTMg{sQ5+rEL;@*2QErG+@F}<F2WC@xzStT-0&ZymG=6B5dIdu2!9KIgI<8YfqxIR<L`uUu0$2WnbFIzgz#U4@D215e2MnGK?vXOeJ^{W(jWLN{ttxk=jc`VDt+)dA^Zg){3H4u{3DzrQK|Gn4nnweVtPN7CWPA&!X3~ea0j?MA>0Ek3KylHdJw`LLw(ti5N_ke059J0q7~W(ZUsMtJ_tWZ-#<hM=OKjuOHeA~;6Fn6I{GdAEq#BT5dI1M9sUXamk_=)QK^iHI|<=3gzy7sX7~ZPI4WbMIG=?Jqc>m);X<g4k3xiSiNy3VRDuvL<;BBjUNk$L7rvRGRL0p&#@pxcP55W@3;1XFS3)=;QR$Dcgm8XT##w&GTWL5yT#gV<M%%&3a6dx$J+uS-9y}E74iAMVqdnls@D#KoJOv(!wt?F)7Dp1oiwNOq=m1!B0xUWko(3;KXTb~L`RG)5KD-be0WX9ndC?7hix7Sj9Ra@yw?+rTt>Ko5>G!#ogm800xGy0*1|1KNfoGtz;91mj1|j?bIsyIw9!CiGM+d<D;TC8sxCLAueFzrK1DA*IB7_rBSql>REc_em!*%#NbN)9%_!snF_!roJ@t&wSA1Z4>K0>%GS_Uo)>vk?f+lxLB>Wc^HE79VizAH}OiWUy_bz#PWXra*9D8zUXEdh6f+oPr6_Hf(8^mU{yA^ZmMaH#wbQzy~9p*rTJ4McAyq_@e<P`llvEpM{E=(hctw*Q&6<~LN<7u_!j^r2|}#PmMRAL{q~j0MqhuxN5<oFp@*MEixtSU<*~)Uhx1Zj1Io`@*7Q;6CtZbOt;co=ynQL_dH<$H6n<v1os|KV=(>z6XzmW9U#g2G2t$!}H*k=oEM*yb2u&i!Op!!E4ZIu;>C<bUwTWUX3n<SHmmNN$?7IVq*GwH<1t?g0_c;z=P1Xa9jFg5Fz{#IvV~6UW`tMr_%?E3E?H^Sa>Y$yMz#4hR%bR!RyhL@OpRyx(Z%Jdu>2h!yDjr=n8lpyd0efPo!Oz6T)-RLGU2zKNnpL&xMzwOW-BcXDK1P7F`dor>twyb?`dMu@;>RFGb~Z9WS2p;$^fU{4(4WZ2~ui8=)`3jo^CZBl%WBtH71u3TQ>R0$dq=46Y16gVuxVaV_B&y=dS?HB>$~Mqh<RUxypR&CpliX7Fq13-D`jeY7fEAFhr*0#}D0MXSM&!jFf_DxArS|9NZcJ!rN>#S+5L62i}WQ5U@p%?95Fe@`Bg*Y||*t%)jxv!ZhCtc390UfhcoL^Ht!;bQ1La51<x`Yc=<?&?J^v^V-J{490oO$ZMT)pIZ*Jlu;KUJUc%2`_B)U33`yF8n?^2Yw%R(BZHHKZn+ZpM&o}Z-eiE|4dLS?fWMooD)ylIwx@}<+b4_(5&zia1HcsxCZ=WsBfMmgll<G6HP+zg_Ga{XhFCjeO7=FzK;-o8m$f2rq7-xgu4*JJwtumlMwC{Dqm-`6Wob3oeAMlXm7YTeLsp2{tz7w*MB}CF>j{yzZ^aK?1t1*wY_~*ZS{8u^?&ky)XT9=_nsa2+tTJYqkpYB{LQvrUcq0ouK)Zk@^?SIeN>|VL)}60i*W1z08RCRzy'

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
