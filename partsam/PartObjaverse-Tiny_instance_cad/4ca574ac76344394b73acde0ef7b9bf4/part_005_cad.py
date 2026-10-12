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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ca574ac76344394b73acde0ef7b9bf4/part_005.stl', 'relative_path': '4ca574ac76344394b73acde0ef7b9bf4/part_005.stl', 'source_sha256': 'f4de3fd629d00d3a8a6fc6a654d69d4be09e7ae4c70dad0c4f296aef92c4cbb3', 'input_faces': 966, 'input_vertices': 680, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12326151877641678, 0.05817030370235443, 0.10622279345989227], [0.12325627356767654, 0.15754041075706482, 0.41464388370513916]]}
GEOMETRY_BASE85 = 'c$}r31#}e2yY@T5J+QbA5)w$T;F`fDI0QnlAwY1q;DdxEXmE!?gA<&f!{USpPS8OYU0{J_@!M7JQ`zq7{?7T%z1;KO=hsgv)%8|aRabXr_TMrfMat|7{VS~8oqZ~o)v72gGAh}Xkv)eF@6)~Ku+jquk9Jc$xX=CxUC=zRS<4P?%1C9bSC5{<x)1fLX7Q>KTE)xP;uSh*=<uQ426i1Zv`0_oH|W-XSWnd-*1Ox_p6ao8r7C58E#*u2TE<)cm;chMO|WF0bK-=m&SDMr`!nrZ?ufsM?+VWU2UCY<`(w<vdW=7)Eie0`ynUMo`EHh@?AThd&Mp4)^+`vWuUz>-_1CC$lK*^NJog<>I~>uL7ryoU3tc_-PbawVjA_Q}Q9>ps@}I9<$9>ne-wyD0J{ZD%+uH@)x9=^?%UeJ6<i4d|B>9VWAJDePwR9HwnVaa^sVp8z?JxF(&O0QK>aW#<&f9GJK3>1)3Y~9p|C{^Hsg1esc+!B{U*Hh0$L?O0+Fzv#`3>#7ynXFNov(a9!+piAG_~L5Nq)(Dhqe79eCL$VV_M&KKQH%f{ioA)Uywgh>x+I+(hugo;+K*9+HL8)<-2p=IV~-nH()X4J3lM;?WJBF;rWJkqWZJA>3rMVaJnwht*IaEce!tmEJpS3YN+#F_4;z(mH%~u*0(x->aLfi<aO>VyA=Jn@;X7jtt|I#xnmQwzWsh6wa2$Io!4_8m47#Y+VgV{_0O1SYX6LX_wszKK04n~s}{90`+i=(rSJl3XK+e7ug5~}yGG2V`b!n(=d~WsOZ60*PVK3Zjn`wVGA=>uyI$0$_KaCV{dvJo^(39=?QvetOyl8fU+Vw1w|IF=y3W*ZgSvCyS^O*Y&+wnzcjoCt=e_rW*JCSNU*|g>=b&-;&saL|z#yup(Q6tf5698?Jk^%`D=Vp<mCtxRO72!i%*Lni<?(6hSBKjFWf!&ItvJ=ww=$J4b%yHq&aCqtmUy0*WxzSQzP){^|NWj(|NP!HQRhG2#n0<J>q+N5=1u)@X)rHuIk6)_=ht!aeC<PRydGCpPil{Kziu2lLJO0Rbt!p#dgP_?(|9K3mGCZ}x94y+eZK`<=f1Oh20Cxvb(B}nNNP`rLjI6Oyu9n-aGkIC9_GF^PhD!~f$xX8KQEHT`Cs*DoM-sLeaEs;8n@?Ss6G4NlfP~=jW?&0)`9eYao-w0md;yuH81bz{DAxR6Qe2L&K(l8zO&HxquPEJzAdWzab5qXxkcyAY2o!dN>@wJ`j$oYshuY#$7_A-csG6jM<>#GF9cIPp*`cZzGdtT>YqhkG@et%ao;tg2hB&jH~G8HP+lv?Q9sn!Nd4x1kj`7(o7ywGS-jR)dbXl|2rNSLxBXtqD_?E8z7f9E{_VS{Jx4$9;m6~C(RB~pOy#Bfpzsa%!L1vp{lmNLrFN!I)cUrUJLtN{ETnb&mxJ<3szCXE&q(FluA=roO3(9hOv_2*Vaqb|2YAtSzwtg!>suGMr1k$$1dX@W^QnCL64Vbx-|%{D-)B&JGG68Ry3U{GzOrcw^}~aYbiF1#;PpE<gwb^z=tutYI|*9f@?;XNKb1yP`@amQ@>kPx-;(bk^?&mr)Shg=sGl1}@cJ$52aumCEpMkI{{h|}*XKUe&NO?deC_Fa|EY!U<BbQ<cxW0*{m`BEOV*di^}e+KvHsJA+CTLY_2-!|%C~V#x-OaS^Yc1lEZldjZc6Rkxsd!r0r6Vj-a9qb^QR+0>stdK({+4l*OgZ$W~A#ren+CNeEHV2zMbnt_oEMusQ$RSbRB=&O7*|5N#k?kHd-e$WsB4L;yNmKTGDlCP>uY~d1;>$x}MgPcYbu<eNLX2E%3l4-mdy(=sLC?Mg3nkOT5+>`ya=n#x#DG`%pd3J-T&9`1ak=x^>33)I#M$Zc~4D?UA7MZN=x%Je{zGx5x4(Kl$gPsUI>7OVIkxFc;<ZWnQAz7x#B(kd@{|?L2he)KPTad`)=$_E%YH{$k(gh|W&=S~FAqxZm0PS4h<Qu6BRXIQ%?~{FkYz{Fmm`Z~v@|)A~x$Fd8Rst(2F43M%hDkIFx~7t7E8{96q7*UYDV$d-G&9$U?SV|4T4rWf_Y{EytXx0_7Yar2N^t#7e}(0OOx(D`Ej=}1|F?&E*Hqk4w!qy8K*GEwV0#{NV5?d!#89eete`_@mTXgzsWAx`Vtw+y3pE=$4BYp?c*$`5Np?P=9l=i9xO(YXDYD^cffJWlKX@P2fCpWNoYE2=l0H)7F6p2zH~<hSZZ*LRGU&Udt*O@7#mcwPCk^=N&|{Zm(7>_08<M$&bxe2LogtpoM*qJtN-zV%F1s^|W^i(21tv^(|l_mtGnv(D4?eV38ibMx#at*>lsP5#k7=e54IWjo3@_NKWX-H^A(={l{e$F=L0)6BPI&U?<Z{NEAg{>?8s-*R#)jfXVBG)^j=q`Yvyuq70|sP%0lF4FoOnwG}TjAPXP+&;99IrsDSJ08T)dByz>dD$u)p!!c1-K)(@_C;QX^2p2JBQN2L^IHDwb>7Su{cnlbqaTNPx5aCH$H+c39vXd0(E7@&rZlc9d&FsdG2iW}TF`oRZzt7L=fiGZ&-ox)uYQlB^Jes?=bBG(v<}}{O5^jTi<h^>yo}ZQ&Us~MecK$x>v5G?MC~~eMAv0XtwgPF9kiPEy=Ri>zB6?m)!#gT#?PO9>ApO98ntJBJU_4H+L&0aZyQ__*Y{9@&i^Zf=JgW4M6ECGQ<mI|c>Q+YiPR5x4zlI-r}=VY6t(}^3F@D>>0`CNyzdphyzjO84A-q=miyk6*R}ps{>eV-&-5#3eJIg~`e9}Y+JEl97OVBezRQ`tNTRNMpP_XB!al(^p(pj*>>a#*m#5D~t?x|ngT{$R7aCVryHWjBHc`ITBYa*c-d(8ttaa4?(;Dl1dyX75AMrfv92ZRf!_~XB^GNoS*9W=0SRZ6xtPhee)-mCWb~@H3>3moD_xk(7<#u#ko>!v%t#?k^7bONzKfHCLb@I!hIIS<9H^q7`eEZf1biMpMY5kA4Qa$DFQ2(Thyr}iXe$th`H$BgWRi$xw`>Jkz6TY}!%BEDb9>!Iq^B#Up>qAn_1g$UjpJLr}7WSj|;C({!dM<pi?+Sd)^R<sGP3Oh_L|jMN7uV5H9@o*}<2oAZ!Fp&YkM&UahUa=;U+Ra6=XY>lyyujB@!rxITaxm{bC7M-ds=@iUi$Sddt=)74$DpRG;Kk;&z34f{X8@imG635_k1UO$B#rB4@(niUYt!w?Qgo4=H0m|ynZErYTY{HDwD+5AIF)Whj>5SxljFo_fD=;AGq%b`a<m=^O4rE0k02f=dW!<FWPVa@to?}wT9X`>{z_c$9qUum3*|n>i3ZQ_Rkxr{%4D*fBN2_^HzwYb{_u3=aKEi74BPZ?4j#8JB;o}*%P?$+I&s-{z2&z%YCsv+qUlE?Q|YH$9?Oz3AF#|GnVqocAE0KH=goRrqX${#!&h9Vbq`HJJNYW_fz?@gJ_*;kS$i{KTi?E^RGUT-d7*qP4!qCQ+ozCp#IOYliImqFU^bW6X`j($5!%7_n>uVrsJa47yCoY%*wj*;=P1;@1bN~PyKwW6SeblX<m;rWDT`*av;^8^VkKQU$Z>5Gvi%a#}2Nb>v*FT)zc|}_Kg{rQvE*7b?dO~i}`CPkNIoxF@J?G&MVeo*|&_kL;IWqkyH=fGuyTmOwjt`J+mdG9^H>J%%<{qZ|u4<i0*^?!l^&Sb4TJg8qZxO(0KzY(t5b@T%6Vy_jkuBH(rl3%_usrSO@kkxTy8Tdm%?s8d}d&_a`6sWyc23i#q?A54E$%Bf9P#d((L<ey8;u`*}-r4;nvs&n(tqSITbWi~Y>1Bk@{aJa>!hDEs0%8p`838hl(w*%#L_xjmwtVjbSuf%<Kw2aWTbZE4-u-duNmU29fw-_@?6zMoI8r~Xl_G++AVr}i%#P1ilJ2KAfRmv($a`>`J-sDAMtdtUc=tuOYUw$L)P?~N)#c`Zz$akzHyC9R+QzG#0%dM~#=Bdr7TPSH5`_z|o1ZDkUve>xY{l^5^x9loci{-$3K^7B^RP3N5yLHkw5Kja_0LF4o5DZ0OW`um`^pKS#KY29A)iu=j?nX|d5J&m4l-&$e=m2bYE?$@ha+*f8Uq4rnWK>LTk?^1c}TP&IXr1f*<bvkdvELvB``SJ3W_m`=i_oq`muZ~~P`r`e7&Dxr-Z~b`gyZpkbo^s7-y;^>e&O3dQejh0L$@@ULyx0fIzSsv!e)2w0t{>}<@WuYh^)rn2^UF?f-#&UG^=F^@aav#OLmYY1(REz1kNO$!;Vl)H(K_%tn#$vSi!0p4ucNK@4(d<bA6+d<&~xjnjnp2zXS4N-p?>pUN9D1;Ii_B}r1fprqUgNXhuasf){TeceVXJa@6+V+VxK1aVxK1YqMwB?+9UScO06Z-4|u<4iycV)@N6peGybk&x!9e?dG$#&e#Co~>fd-jTjva=dhon&dHR8_*W-cYi}zrdUye#Ps;8-y{P#I@e)8WPN=~MFDh5(L;(meo;*4lT`S#69=f(cPe!m&{c#gAeDogXLd=si?b@4sA`7*r$o%chLJ=%F8eDPj4dH-;)4)tfFLb~@VvY-6^K`t-eKghm#{~-C|ItpL3Q_L5OpFfRru}+Hp$(_p7&!OL_9_&x-Wh;>H@sY}leMop&>YtwPbnP_wVqXDY)RVk#k^JO+i{vNoL*(+v%WnO2fL}+Se0+Tn&kM3Io)=sNqPZ{LA6lQKyK3e;D>b9{0B?i$^Yi+q*~QC`E`P+#xB1SFHS?Xh>m-@^_GuBf`OoXN=e}iK4H{QPCtWi0?J09y;W{@f_nmW}@P2d@{G4FsJ1ZZ)Z00LJ!c6P2Mpn6I=Gy~5oBGO&12_129=zVi$CcmSL%be8-&>|W_UG2p$GC4fUj4APyulacFSh2s^H;-zy7ICw_WvPQ_VVlKKkA6Kyun9#d%FGP|8qs>J3B;jUp(*2zV)N`ajmbcEwNYIKQ^xv31+_4?bl^9UkM)1``Ohf7x!%yIv>!rU-ofcN7XHRwByRsb;(6DU-@;Ek3-AjwcK|m<<OOveNkSivf8wM*%##<WqWbo);8-=ZTk(rxW32c?B@MHrIapTgD<YvhWpXnU;j{deGR@SKcgu3m1XC2^&5PYw=`_9i}L!Q8=nSWl%FtUC-1jBDRkrC;ER0oXCr^(%ott1vM<Kl^w!%==a=kD<*oM)=zQC_uiMP#oxvCLsB^(>X7kSAi+-3}V5`}@Gx(x>$EeL_<J{njyyhN_;`My$K%W~pv-uBGzqZ#UGvD5+q-i}$xxe|iwQY^zzV%2jeV(l2mOspVTN2eT`_|S}zwF!7QT>jR4Wmrwh3t!QyL{C~vw30g#q~WuZ3Dk9()uI&V*Qc*<n^a_%?)Pr%ixRal79VqK7O*q{GshP*%$pL`=Z}u-yZg!&RgN!I<xs}@Wr_5b#|@k{FQytZ%4m6ct12Md7593&Zkb9`ZKoBy4vWa!)(4Ad@<i^%y*d1ci9)~xjlzNdtIDIvm~1OxWCK3HOHJQratcPvad|ZaNX3${oNjPc@_6>Ez;#{@WptTpN;$;1$F&z@J0En6Ibfy>EnvW&3xO*_HkyuGChR1(-J&#rEWeZl|OFgyEaojvhQ3@^*95ASMd5bmDH_!247s?LqW@!pZxhBaeZZ9l>aeiF(2o5{Pp)c*%$qjxA8*Vd_i8aFY=Ook(a$v@rBy)Z245`q?zwZA5Qz&m4_Gb`StCCE-!;G_CE<hk-VM~9=f~?zUYUWWoPpKX?$AWZ?Z4e!!$wRJTL#P`t?xuMft?GllXZjB<aSX!595(OEHdLU*}W(b(ei{e{7s~H1CI|19kJ-;EVq0Q|HNX#pF3c^2Kw3@a6rd@D2M<`0_lGeR03D9Jhb0#eV-p4?a#5YZ;v{k2l$Ow06ds`C{D`zC7M!-;v`Az0d#kA<W;TKMlUfH|N{2{wCMU;EVCLt;r;Rlks5iMfpd~!u?Igo52_D*;9O`zsYzu_@e%!Z6f_m=8M4><s<el;PpxK(cp{md861uf0O=~{p9%`(~$e}b(ejy&d7f9I`eYGV(v@po52_N-_{|^c>hT2r@<F_z3sk&*C(yd247s4lVeu;o6QT!7xx$07xx$2ay$3s`-|+0{*isrKZ-rmDt;{89}T`(m+D_4U%LMqe6j9@-Q&JIuU*aZI(T_$Ut#dEuaJGQuQ2%7SIEBDR~UTkE0n!+$(Qy;249T-gJ&G3dF6OZ<)!_Y!590hj9(qv@h|p!1|R!9*S%9~xk~#<gD>jec6uFepR`{!_+or^T(@2~zp#IneX)O*eX)O*eX$NZ9#q@FkEQ**!58gcG;@RYdWq)<*%!|dvM-(^tXWrV<n_zX^|CL<`R9Nrem?2>$l!}{p89Z<cAkpoL4%LyLD?72gR(E~kB*DSqjd8c*G2Zlb&-8>U1VQ858Ax9Z{{jJ{~CO;?xo7NmH)o{UQ71HbC6HbZM^@a=XZlI%76IGefj->!58DUUHk1^rS}pBUn(!Zm$1Lcxl=da#r;C|ML&ERxYKmL%f7h3WDnS7Hh&GiXy<#+XtVii@J0Cy52MZIm%$g~yy(2$X7j?}i+o@8++#K`48B+=Kdhwp?9%%>*%$BYY^xpIm){4<z9{ed7-d?&>?gl(Oqp}9**G`&qWzt`>HWL3{>Z*qe`H^*KT3|dducvP`)Bxu{qx|1+?U@2TMAy@Yc}r;z8KHpt@fGCJA*IA!@?8$%;ufJ7wuf}YM<%6lYLQt6OaAc{t<sKkbQCAmwoZ~0@)Y$ec2a(FEG?2?)$$2>GPV>-#cVq{Jp~#*m=KpT#4r<*%yC*k$v&^7ugrjS+=Qr=zA2>--Bdd{5{C}{3DH5>F-UlpZvXAYZ>~Ut@QUV$I{x|m;XNKY_W>QhxGSfrQHScrN6&hoL%|#mOoFToL|g+`SU`KO9#1c_}tW0AAT%<?oReaURJ+S+?PL3D17;IeM*%MRFC{Q(s?7P9_jP9!k0gP>v+45%1fW?wl+M+efe|jcBM4UAL;uh!k52qV%gi9%1hq^QnE&IU;dt#@a6A$IR@M&U;4hAa{A$6vwVeb_?}%{QGP!8`-!$NFY=}DGun&#95L&E`-C?1zCrq4r|{+Pbvhz%QhDk7xvuJWsDA1DytWm^j+)gkd_(<hXL4WuzP9bx9P*{_cRM@B9X0EJ;miH+>T-+PBYkh(8Jgvo+4Z%=wIg5pzP#*<@o$NleS(*hzmG5ZynIXDe|@0ap~r{Lmr`e_8tIhmN@zFDe|mtK?4MBc|MWng3jbgK>4B=1D*a#o(*wEO)tuD$%S};yRrOKhy&Gw2Fbl@-+$b2QQX_@hepM7Vr~>Y${=X149w?+P<v(V>!;Vv+tP84u6_j<M9(VknJAQ}pZZ-C(5d%F8eyhfHHU5U)0^dNplb|2Kd+@Wv&?NA6oZ}WW1{|-(CN*wC_kuU5u@PlAqTbyo6NPe2_kmfNIFyUSxdq4LI39H~zJzmJhwcV%QafdX8d1=V;BYm@sWBBg7952#;m~nl_OngkO`1A3qTX@PvEX8AlvJZAv;^2)jg;=x=S<(C|39GLQ(z47v4cp3`ck2;VyLSG>MMad-7z+6U|cfI24=rk9c7tT1GDj56TepzzvF{*WySAh#qX3vUD@#SZ1`C!)Kv}bVCn(xq2@A8jj3+L-EqvcFPLc`Fw-gEY2a`*oNAm<qd$UiKj?OFKkzs;POEWBjll@UgP=RXgTNEi_(P48Y79g$9su0|9snM%MrSoztKknV3-$;9235enfp1{}IHM4=V7v~&c$peK)M%|nD`;78D{vWTc5oT+Z_qU0-@vI6j8m%7NR6s$RDl)*R{<A*W&{@iXFxDcrN(_V4yzFZ9S)8G4};bR4+GajFs{hfdbLlEt8o^=I1zdj%=8*~i5d&lSd3u20y-bO0=xz~2h8d@fVy6(@uwOup-;g~AA*_Q1K-2%y@VbBGu;N>hV#6H&H*!>0cL6kzXXqgjs!Cu3LXRgN9`;1CaHv}G2M-LIF5&cSs50?@$&_0%vEC^g7IwVOz>=Q1oU@s1b8BJ6nG+d1aug91bB!V$J98e#t{VL{m@<D{ot+8&ET!z)zFpT)!^mOrQqe@MQS`#<B=Lq5R6^W`(PLNF7!6|F8C_+GWaSu0eTLc06wF}S~VPMT!dZ#uUBK88gHPn;8^_p4fF!|4fwSijY&2}A0rq)Krp_8V0^`m<`L852*!t?ufT`E(Fn#{+-OcMbE7%LbQO3ZI1;)A90{HUeFdHco(>%go(>+3V9ds8sH#2Hn1o==*8E;-Oje^ebQ-uf_ysf^9FE_8fnfYxjUe?tG)9eJC_5gFU_2bbco?)jco?{Y8hO+hs77w+05H?8;N0LcY7|gos2cg9L%>YCf%AjQsgX~O!D{4%4gxc^f%AgPsxeEA>1xbGFrEgT44wv_1hs=FfhR&IfG2{-tFc~<wQ4w^tH2KMO6W51O7K$XJn&L*B!cl=HP)%IT8%Xb#w(!9!7IRvp^Lza!SmHvqQ*is7C`5K7l3CY7)L;7fFr=atI<S_Mrt%v;}gd2XXs1tXYe-!<6mlISAQp`8if#yiy#<#Lo<TC!R2vYcFv{<#x0?B!Tr_ft;Q4t;}B>UFw?f+w)njeXk9Q<f3QE!9|Fw?W||hvl;sx!eF^T5cJxIs4u$prhl1Ow(NB#&YV?Bk1or}Wh6aK=gWEt`f!lyvK%0SEfCCVW8>`Vkje2U-fm*?Jz_p+iz_q}B&{AMOuou)5>;*22U|dj*9BTZgMh0j)a0YN1r~*y{{^>^g-Hn(9<FC+v!C%4uAQ*pCqpCaIKdQJ>FwWvm!8o(3mEB1zAsA<ZvND-){08?Rc1^qETJ`|9gSOUia~wATH$pJ35A6=F53UWZsNvE$F78hAst~;F8jl^Phjs@ub<^+<H#%l>`3vST(;whhU{-dN8ewX5LNE@3zQ8>s2;3g}9L$1oM|TRwBi$(&k8r2wg)VONtiZGlxHY&ev>doBSb@5M6)<~FV0sqM3@py#*@5YD@G|f^=z7hw#(F$|Fip}tk1%G>D@?Py{rCLB*dJ<j`|o*&ac5{3xBqhOh@6<V1-Aj0gZhEXf!(0)U^g(!iRn4y$Ko7vV!8sn9K0U70lXfZ1icMT0<)Z$=0JWdav&$BwZT?!7idRKuAPt*(?D=ruphKM*bnRuO#x1U90i|8ek{%-C#EaGE5I9|8^IgEx1o2yx4|qYra6&cPUIuF4vuSsJ3>2wyCR=X;C46;1eb?a0G9`+fTjeeM2><lAU_rtkQ39z;FaKw&`sct;5*Q};5%TJ6VqJCk3}xz#I!EBE^-pwRg<F)IWcVyZU?Ratq86FP6<r~P6=i?F};ZVSX@L-OqYNcgEv8=z?;B#q4&Ud!7L}Hxse}>+{lS(J#bxcSEx;sYcO(R+7jFzToGCZToIfK`V0A`0<)Z$o&sM4FM%!vF9AnE*Mg(K_n<ex_rNSCrdg36i>%0rX)SO)uniil$+ZJ=V%h@S5?lsa3S0)va$@=e`LXzcoS6OrJ_TM1oey3LUJG@A*Me_AuY+%ZSx!tnkRJ;V<ixZFxE44V+Ch_R5OQML9NYq23hE0k1!g%h{f_)td`C`9o!~#f^PzLVbC8eV)i`#5uS2hZuY*}mOfw@t7MYO~)9T<F;119rO|Gqw6Vs;P=3rlFNw6=N<;3(0@?-G@IWav7c7o?XXM^W}S3?(oSA(xW6Tw%&EGMQJksphU$cbrHaCLAHv=z7+@@WNbg5##(l2C7ONifTa=_lmJ;uCUWdI)?JJR2GTjzB(wBXPU{oCu8vCxTf{Ofw)q78#He(<<Pq;8xIPnj8a=6Vt}vCSY%<C)g7?3jTonSbRWEO!tBhfg_+(z!Bg`=nQZqI35}cjzx}w(;`0>X^|7tO5iHsX3zjlu8oir(}v*2U{7cfuqT-1#Pl!Z$Ko&K#B?WkFL(;n4xR#@0i6n-0gi<p1IL0{PE3D-Sum~y^+A3te2||Hauc~WKu%2SgBya2KrP@RV3rfpm&lLBOXS3KJ9sD94jluwgQr3#f~SIyK@WnDfqz0jgMWfqPE5U!9}6$!=Y`xvt~HSp(`w-QU<<SW*aBubG5r(yvG@}?F<k`S4juy?3?2iX2ptKY2tEki1wIJ=41Ev&3}!hoEr$GxAveJ_aa<Ys)C8BtaW!xOXdZ9@Fw2SQBjm^85prTW9lQuU7#a#53?2y`03He61>FkX1%3~G4So-1IWaAS{0bo_!Id>RmOxHSi-Svp^FY&s^MF}SOyiIri#X)ObOLxfI276y+!gr<?up|8;H}Vk;H}`-&}ZP+V3rfpyvUD5UgVb-xrtnhA}6MW!NtMpp<j_-dN9k0=@IY|<Rf?pjwgV-LfeDeBOk#XaoiI;4>}1v5Bv;z6MPdn3eJT5SY$$enUI^vwIFh0njf4Wc?td-`TdQ21n<G|5%3UbFYpj>duR)AdvHf+J8(zvB<NW1B=AjW0{AAF<-{}%@?(((`K3W_BG-J#iD@=)elW|4=_};-3i$}$jN{G7M{qYB_X4+oHU>9FK7yO!xEb;hJQT-c!3ofl;FHKv@V_`_!MGqapC;EV$c<?_a5gZ@iRlyM$KnZcVmcSR8QcvT3=T#<g6rV8F}NADA-EZMD6|iFDEK7w0Qe;MU+6pVJLD)h3vx}3yt075A-{BBmJ`!!;A_Z7@MIj%1qVZ0f`h?zpw+>3zzv~Ra6@n(s10mGK7x1Pcn9(k`~t`Cz$`DOsWmx%L{3cKg1>>UK~ICPfhR*pfJY!7!3}WS0Qm^^!*O-66<Q5!1>2w<z&7v>=tA%g@C)c;@MGjC_@nY)u5XYN)92vl$Vc!#9G?b{fc6IWMm~aT;<y3W59$N<16PBV16KogfHns=M?QkXaU70(1YgGSWAI1l8|A-TpCTuw55dpD`=DFE`@p@Soxq)tkKjr;t_k*m76<!)%Rx(k%YmCi>w=qu!=a<V;o!^A6X46>H_)fxtH|dm_!5pEg110tg13M>LEC^kfh$2vgDZiHLyLlogG)e*flGkvLTiBQf=5C7gGYf+KzD;rfS*FIYH~b|oS5zh??*m@$KiM;xDB)kxDB{8)EitHTojrgTohakS_oVS`3NqL;~L=p&@SNq;N8$Q;N9S>(Bqn1qmdKSZQyOlNAN%#4@5qKYvH&F*c(~|><!Kj%?-{EE(Fa3&Vzgem&9>-a2IGGxC?j<^mp(Y@NsA~cop)A2G7FrHt;}b2si}!2(EzRTHqqkeBdJB+|X>`Y{*A&4jktJmxOwPJ&}*#02~K`e}|3+{|=6ZuF~W<4LLC#51s`Mfd+v?z!jjr;0oY;&|Khr;B3$=;4H{Tum_HFfIXoWuqQYG>JJV8kB0UG_d{-ir)hExLrzQwfyaY`piRL+U|*;g*cY4&niZT2oCTU5oCWLw%>?!UTcCNt7O+3GGPpAG5!@Na{lL?pVVYd~A}6NZ!Gpj}p|!zH!Cuh9;KIm9aAq851*eCm1*b(mg45wR6F4t4Cpa&-GPD%9GPpCeEx0q7<<~O6%{_aH|JVNn-GBesXW$gw{~(?GoBEHBYkzZsT37Oi$y)}bVxM_b+|~bM4@{HT>{tE=CmB{;'

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
