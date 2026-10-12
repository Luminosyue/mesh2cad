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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_005.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_005.stl', 'source_sha256': 'e88b078bdb4776e1dc3759d6ac68149392e2f75c6a216d80d11f3aa4484b5fd0', 'input_faces': 1104, 'input_vertices': 640, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18954920768737793, -0.08637619018554688, -0.3249800205230713], [0.18805286288261414, 0.37388694286346436, -0.05411146953701973]]}
GEOMETRY_BASE85 = 'c$}rZ2b2}X7Pj4I$dZw)!hn*4phyk}5G5)S6ihSZ3`!D2p;3}V0RyPW0d+uf7DSmNIZhyti9t{l6&0=lQ25TS{q)S~8veEZ^?j_h@B8#?QC(eKRlB-Rvu?+B*|HaP^iMe_^nOZ3x3S|$<a3HTqx%dWIiOdc5jBTCH#XoDGQRxrbp9h<J9O+Ga7H`hD)sI&qSx?B4Pz@c?pwc7_1H>%hYcS&yvNYEVZ(d(5&xkcgGcm<_#^uFc&<<6xN_Y(wW`P7U!{8N%d!8Le{PdDRBX9FQ8aw#7SY(2Q+Fpu`JqJoxb>T&{osQoj2}u~u_xLOw^Tp9)xZtWe*Ds7n~iSiwJX|p@SQRLZ1J6U(sbjymk00k)q@{&e%KoAyCoVLKlI8cd!zmI;_An5?6l6;{_J<?c}IO5j`m~m!%0Iw^VL%{ht|KpQTSGVxKi8Ceb=?{<|b|bnH|3JDerGI=Wje|pRYamp|qi^eb-y{57Upqo=@(%mG8cD+IPRwtEeBpuE3^S`RTEFH~RW{)NJF&<~-)B-^GtlkN4Fd>-qoO+;l5HwCWDueGi>FvEGy)RMU4~TzqF-4uAdlp`BYc`}))K3-ns=>$j#;&9VF06<>e4P1Fxf*tF8uZ@qpn<G@`T?`uyGKfUfT-}p@LN%<E_ZMl^n?(X>7<1X8?_Ez=B<J<Lz64Vb_^}G1#R{hT9SJ&L?dc(h~Z(pyI_`~X3^?!JW`dRuPKWz8E=Ue^nygF*tt;SFKE9%?h$H8~4@#FbnYy7yI?l*qOnn&@a)~&qNya?jk^TI8OZ_NwOcgp$ag<I|;<EKB`_6uMC;0H_9*zP;;%|BL{cD;PmSKh&QcHH@?uYV4AF}}SHxQEnFx7Go-S(#;~f2{Q_*i?PjTHnIo_xi}Fy*{5;-+9Pdp9|Jd|Fc#8ek-7UeDnVP^<-aZ^(TGg8_z-f;JVTN`I6`S2d4jO)$y0d4|ebViLak4Hx3y;?pt4fhAXM>RLbV-Pp9R;cg)`_w8fV%oEGW__jJ~Lv8;;rx1I0sv*bJcEcp&UOTNR;lJC6p+WF2qubuC_dhC3MpC#YnXUTV7`|W&(pC#XU_1O8&@-y<CcU^YA^UB-#&TEgI@4V}^^PS~q%xkZHJKtG;M!xg<+0J)ff7<!Z>mNJcS$;;o^Xj+roman|@4R~KeCPG2o$tJUv-6!-zn$;AezWtPSC5_VyneIuo#kibJMX-9zVps&=R2=|?0o0dW9K`sAMAYR%{x2adFAbV=askfo!9?%zVqs_^PT70`OfPfJKuTb?R;nXVQc(k$#-6V+WF4Ak9NNE>ap{k<!9tO&$siP*FSc?^UiDMJMX&eeCPF#o$tK!+WF4&?R=Lp{;hoH-CsN3dA^<Ry#BQFop)Y4-+Aq~^PSfoJKuTb?R@8zxAUFX&vw4^+HdDOub=IF=lNE?bLZ?d8rs!4xtaKBOZ7VEbkP64eL$-C&Xt4%roJi#ji0`2<`MDJKiYCI+IM=+N)bPtIBU1goA>lOPE1SD^6L*r`@!pNjvBw&d*(g{t9)SkDST<EId7=hPY1O8zh?f${(b6@_^~rr9f|hCL;IWZZra;lXnU^dd@Xh)Maw6f^M>Zk(Y&=Q-dt~J`1{GxzB{!1F;hOgZkM*_LCvqzzR`AG?tIAH=cg}i(sm9%s@I!l`oVoVq<L;!K`r0y&Lp3IX@#jjJadNbZ>n^l{IXQ-pLdT$`{5o<P5Jn=61rdcE2r_}3*9j7k8idxS^Y1}_zj<JW9kXV^+}2LgVUZnZtm}hZ_W4*&sn5-Zbi$3rhKRSQ=<LwrP`+bL3g|6@xMlBeyw><`*Un;iqBsYb6oG^^LzAqn`nOh>!=wgvD+%8M*B|JpN?sJZiMx`x0!V`yrlUt?dSc6v>&eMJZ}9u{@sVwPcwdO)rm=Fd`>Brs{VN62OG_%|LZ12`%dmZO+D_+r_8uY-`RIv^!<%boSo$JbGJOM<LVPrKKRR^wOapt(+}?AP-?XA)~s~G)RWLx=k=5`CJ%+n-K*uxcGrF=`^jn@|7Xqpik;FbCE9l{EivZ}&CH?e#pGG|dSB9uJf9NnJFR~+<((0|b^ZFKn&z8l&h0n-Jho42wC`^JPVeu9%Q|nTOg8Iy==ITuO?$3(JsR!1H5X|87h0O}5bjj<W39iAxxb;Zbxrx;w%*H)Zf~LUm+SR>XIjwokDGADtPkm(g2oSbnXl#JUQPA+XJ={ov}R^ph04}jrsL{@8UN{%Hy@4m!$tR*@}Y`Nbsd<Jn4t5eoUU(!2buEWviU#Iaa&jCMZR-7uC^sD)%)_bj?aAKbiFFuWU2Ps2A#i`S0_dLPV4PD{)d;+^<mqMB|6@^oAOTgmPyfmuywqaPuyVE4X1O{B|82;(RH#_TiRLH`0-W4`;4EXhtCf-%B}0h<dHr<yk>;9vqP@U(Z18Q<VjOL?b%)GFEaTfz2y^TT@AN-<XE&HW<1Ak>bcGQ{e%w}>;1Z4`{$~z8=mj3X{hB##Ob=-?7qd?KVO>h<|bZCj`oAO&zOFQP54*W!?dZ3bX?u7<8WK~W9pC7eD=&)GvD2~1wKExy^Xo9V24X)UldFTFVuR<nDU`c?M?aE5l7zEc7AT!6TA0DO0@5EU8nOm?SSUX5q-4$r9N7I%D$9n-^txY%Xjau`FljExq4q(X&#(hNZUE$``3+*dyDn6fzNlhPdDukCmb{5*8Snd={gP{H|GtVS(h5^JGo0}`R=_<-V9GT{+iC0n>rpkjY*C6onoJ!(D9bjly}`bUori&;-|f){&{yCi}sy2&*-?FSX%QzsRY-|vqG<!d=Y;p=kaJixPPwR_eWga=PaBtB)b3O<C-6j_T5G+P5WanwAbg#aFu$-9~Yzfv~0_x(Y`ZnkSQNuvAOQwg26K8{5@8h>y7^<&(Ub#y_DaScV?Z_{adYaea-ccKC5|i@CW94oqvb)GvnrZb6ua~4*Pt!(HZUMwAK2YTWiT+bNt3hT@Mp(n)Sh{eQl(vCwE63&)tuj`R<hZ&(-qXO#cManwa&$X<vDgmY<~SPudo(r@b@PlwVR<>u23?zaKE&lpA_l=k=L-Iu18XnQ4yC{-Nv1<p!pHcfz~s7u~J>vuf?pXy3i`vCfxpU+td_mu6}|4A${;bkxyk-|5<(@_9{p_j2obdR;4ZztnxHnb&T&&c=6k_cG(kT|E0(v>!fOPV-uaM>HSLOfY_^kYmP`bM=Me(SCU7G3~bt+s(cwSfT!WbKK|)9d8wnnRUjkknc@X&#r_cI^I4$9__npE->C!nSFBb^3!i?KeQ#k<S^@SxWYQ)d-*gzUmx9P&M3b?>zS+frQ+4YdR>DSX#eCl<Hy-n@p!cFHoE<ksi(u`MD4dXwEX^MjGt%q{&vf?&>Wv=tA5%g-3KPNc}K^?E4topJDj5Z&_(^@b+mtGj@0~>xc(h&{|Oxr6$+|<`Sg3HJwy8$Km1W6y<ZioFH%1r>+oJ}Plb5n2lw|h=MDYxsP0cH)OugX)gsN;i!UFI_JfyFOh1Rx(slpb?NKei<RRUkm)&|a+IQCsCm&7LeAFse$kelaF!N=D?gLj<3+edDtM@BkN1aC(I~za!^CUBV+*~>LMEk*Dvi3v#eAAzi31ED;Q&n9Lvz1GZ_JeER)p7Om2R`4Ov|Rn^1AX;4@9fw8#_T7odVVy1cvpU(A6|V^+dupBBwzW20=mxRE1Kf-w-(g?e6xqYe6r^8@YId|^PVlG^R(C{e>=adtmW-?o^Gb|Vo+{>JAaKkd8>B1r)O&U(DOdunOWM5^Yk~@_}U-7`LOZBm0t5-*UWx8FShma`R?@b#t&6$?DL&6bBrImG{4_}c%kuwyO-&B{_`v2$2S~n#zXq1clP-F=J%L=j`QU6yQ6(~{D(U43RF&t_JiZE={m6ShR&l^#g>@zmmKZqiht>QaA%hB!!Kvoywk2ia<uOpETsK*-~B#6{JG}w^owVceC2PuN9#HIoA&d{1mg!cPSbwdFgzvNcdxvw{V?M(T_36)QNPI_I*%6iOOE!P>Hq1z#U17I-T$iUczbVgQnVjzTTlI0b>HjE`A+?RN9q0AH!mgHcUP=2zVmA>ZO@sDTK-Z4eV%IerS?OEf7KtdSm)O_Klps7^lv&(uarxP_QOLOXn#I@^oXyX(ywX11#2ex{I+Fu944js>T%m{RsYW!+7D;4FExLk{ZII#o<2W()@8rfM)$XF2Q9zgjJ9+3hsn{td;VwjM{V%=&IgTkKeMc7lCS)4t<|6Xochb-ji27FmacEPOYQaf<%gK@9G~;bu4v!Q@9KE&nc%A@JiLsyKhD+he7>i)=ZW4ru3D^5@%bIYI<AHn(SEBI_`n<&PtkR+)K|&TemLzbt-r`czrR}d5AL1SlYI3&-%ZC=wuU<1<`g%+bE1o`CpQkIMEl{?WNpu&-?Tr^x6yhkvTm2s^}+L<$Fx168?}9YxNZlXcV*Wf@zv8~mbUZaHNT%t*SFB`Kl$o$Z$GSl`XF6DNBpAa-MZ79*O`$$CE9nhCu@7g=k@u{tKGFdwQnBrl~3-Ye#!iLA6sA5_Oq@AM}C(Q?K{i9R)5|u?Vm9*9~yt!Y|T3}8|(hCND<?^Yij8F(EV%O|9m=K{ho8QKflxWJf82}cXwYazt4SiX1{hM+IK1})b@8f=JVbC1x!2LZU6b|aZa7mb)!j3op)tITK}k(y8hRgo8t2i@6+qO9;f}ed71I!ciuc;>YqPkug~AMNaxGQ#k-<?cc<=)Lcd%~iuQvI>uDZ8QeEEzT)C?4EV)hZW0_(p(Z1VzkM>)UJAHoe?q1pt|9pMKSAN(q?YH!c>Q9XM$eb^(sgD0#S5l(=;EwOL9|q}uJGiQu@!cg)@jPBg-?yBZhp+F`V)ttP4L<R))_?O2t$)W>pC4?sPVY<Fe82x5<GfZce?14k)&9R+U)$N|wE7FjX}^uC?em@FLpt7u$NBu=)~9uUQvdNIzVeq=>3Z05qt6fDyr%1ahXSe5zWe4^+CNtd>G&^GF2U4accZRLDP>cl{qWTtI!||3^!ZMX0h-_6+;_xR&ts$Xyt7Zzo(fuie0}<d@r)m?{0sMSmaY$Do2p-~g6_Ac6xMOOs-@Pm|Dfib3M=&fmhHOCTvvmib>Cj|y3cpsdRp_#)6G(%{cw@>IzDsU?el|ipKJeLt>W{&btzbWqQ88_AITT5ANHM>^(u6_$Pr&XmGwE@t@?$}50897$A95ufB8QS>HQt`w$FD)e5HP!J5zn_IagQLhrW)_5C1qr`}vc7{`Sw@q~)i)<-gu@DLPKN^zr#l{AtaDQx7Nk>hE?z=f!hYzwP=}>t8fQ$J?eSj30XNlCD3WPTw2t$JSeG)*rXa#9h(8n=MY)pW93N>IuKpOy|++0{VVnRS)B*zg~~$>&?fa{m?hZ^t_$kKOXJJR(;t#7dvAQ`~3LV|JL`Yty=l~@RA1lymlt(sLwC@I`3)o_|EGrt*_%bdBECeKRE3t9aj^}Z;JNaH4}84By`{9D}U)59ajmPe7<wyy3V_av7h?<{r719mmXuDuY;>5EH~}sxj6muZj;x7XC^Jz^S-I=saQetVA<D}-)jDPewO*$Z<g`x^~Ce-^~Ce-^(3Pndp#+8QtPqTPy8(FCw`Xo(<^VUpI-g;`iXC^pTU|rKGyP9zQE6tFFfDQ7hXM9zHr9YQvZ#a?5oQkP=CDfz4v&*g#G%Qm2H)lxALRs+xam(ca!n6<ZJva`5He<zV^yn`Pxa%w!*aA-fwumz2CskvfseB_Zz`}1=P3qKb~*ze-7QP^;`Ql&$st)8NRiD^L%^%mQla8f6FLu?cdxYtF-=0srtKH;yj&4O*XI4apm8~dcM7nbyjUxzjbx(x9T~xAByZ$-`a0`zP;bhC~xhzGs@fh?e6g_O*`!83;Zn47x-D8FT8r}=L^rbpD*yUJYW3vww~8|KJxr5&qqZ*UKxGgz2`O0x1ZNCeCv5FqaOQt?VGl%bbR=qPcwY$`PB36=Tpzm@_f3ao$<3gpL)Lie44$7`quNf=iATY8Rf0#@r?4;^SF~^jq&aG6`pUuukd{PeMLq+*87SK-+Eu+`S$w?x79ZF*R<Dt{zIc#S9fT8a>r_WhUYW+F1&W1)^EMH@qGKejWhPNwx9PN>6eG-``9PXYI*zp5`LEVOI~^V{Sv<Ye#!kZ*J|Ti@4Gxd%lod$<&1B?fAf6%{aZ$P>-}3sdHem_s?}P4Nq_xaZ2nbk&+Ey?&+@*}^X>PI_*vdJ;@j^V-5mF>G3BlI)t+y^ug)lMy|4Cs`+aq0J^uIAo^QXe&M0raug>tT_thD`^}ag8x87H0w9|TDol)L;U!BoT>wR@bKUnXpGwQeAS7+2?y|2zVul2q<qkijsbw>Tx`|1qedSC6l_k{7Y{C<I-<@bwKZ)-ipuIP6`iFc7_KhyRXeMI-+`QFg=eC4}qO}*CdEN+p6wOZc#9S7h39Va$Vu65?T`v>y-%Ufoj78+K~_`&U+bX?8Mr|(IY9#;SQWZ&<hp6_1zf#2^Q)8FrgHC}J(&wV?;XZ@tlJ0~Af-}-&c^X=c)f_X+5KYaEeztf#F{T5nUW`k*;_4}ab+rJMwdFC2F+-14W_uFTr==E;adaU0oJ>UMl(m8q9`1bFio}cCS(3871>h=16Z;fx9v{CPu|My(aw|~zKpD4V^lrJ}z_kLsbJH0$DHtT&Ur0)}kuQcN%J$I2U=DgEN>3wWgQoom5`qCCHKTpeF)_rfVaRR>ocXQ9Te>V@E81sqot>5=O-~N5y9oBBEIkvtZ@O=CG0e9HwZF*n)-zRv!{e6PFbgA*PeE)!NfB)d*S^ueCum5`t&$qwFaPqvn-ITY!_waoCdyn9-PM_;I^naJ)`Sy1y;oLWjZ+{Qt`S$lPPUF^zI-afXcJS@*cAUoRjBkGz<oQ{?3u^p_@$K)FJm3CK$@A^+lsw=5PAQn$G_3vR|NhGJ?eDLGsl&Cr^?g_RqVZpta@O}_o^O9YmVPm;zWsfg=iA?>)tk4|l(W90^L+a|Iwy7eP95j|@AN$1{!TA+vB)l+@BZ%qJwMBLfRm>0(*E~<uju*q_loiL&TDz=d&msm`W`You<C9-umAhZ*h$H|wV(ape|o<C{b%~3o5r`lNA-OBd(_xTh4yIw`@eVfeEWOXVD^Bnzt(rT8NT&hZu+9f_D1)E_ua4a{uo^^tnY_C-~N6$baA!u?eCU7-~MhnzTN~gf9&t2J>ULbIy`Wz&Nu6OY|qc~J@%qg`*d9Szv~X)Rb;<jSJZdl9ew|LIroAxO@nnJ|0xoAoT5(O9#Q{vSxouk>8=0i@_;)3zy9fR?b@~K{J;I%<=g%ZL{fi@<D5qS3n)tnZ$PWXC~tswqYYuv%CP8~fU<;eJG2xm>cH*bJm_UdS@cIZZzPID;$KHK4=gHW{-x|$_+K~;-35z&3a7zIgz!dm6)gG@yb)eY2roh3fkhX=OW+UD1o%UECAuD732#NefVaZ?(Jx`qZ{Yp#cjy)PJNPDAGN61DemS7J0v7!j{+Ds^G9f$%-2l&l2cWy*-Q3p!gzz0`9yky8^bSI}Aet902w!zn<-T6!{-(ic+`p@Y@IiDVypel$kPtpX2yZ}_z)QGK8wlZT=t_7Syc69D?}U@l{qTP7M=~M&2YM6!11`pWl725n|IdMo!EMn2@BsR;Eg@VKEeIEduQ{sHU)SijgYZH6<r*P;8r=YI;QCJ!!s+NvI32!#Cd0{G=LJ-*=K{yV0j{wv+?I9+P-#;DJq@4ce8PPr>(5h>7>GUt4}=G!Ps4-ZL6PVYiGGpjNC<a92f>3V--QrvhCTz|7m0f#5k#B8%_tK@pMryMXS6RY8V`4dA0>plMWR(CIz-|zv>W^w{45#|KMVIq`@;R<=h1=i^Y93CFgyYtg${y8!6VUr@JM(#+5;XA4?v%U2f%TW*cZ9CUq|8?A$%Ua1fPfhL~{p}|Ag}gRM)}z;q_>p80GbF?HJXE;M#Btv=iI{egut!<7odQgz$reaC@`|EZPxn4>v)(z+D(aO$g!Y=)G`txCVM3Tmx>32H_xMt10>@+!Styc7wYy&e{>eEeYY~Xe(Isez-YYix6HO>F=K-_b69Hvj<d{!`b0wsFYvEv2b1LXa(1WA4VU8ABMZ4&%#~do@jr#Cp-jw9v%XZMn}M-;TO?S@Qd(xbR;|;9)}Kx$H6b41K=0np=caD6z+v~f_uS_qYuH4!>!ReaBH|8D)XTp$HJ?bBe~(#a1K=FTMmwee_;-O4gUh4K=;8X;4u0L9ER6KVqqi}N8$rQcsaTTUPJligz#sC@E&v@ypMHc4<USp5dHx@5B~uFj{XV%4&Oj!O}W9ba0%9#^>7JzEh=luT8@RQ#;CS{tHO=ZM_|zh;l^-Hv^^}^1g;4?Xm!|uE1@;uO7H_{Q&_YeEZP!&0B(dfhed0_jo>PT@W%mFncE*T$8*6S!}$o|Us)$)z4(<7J|2nB(G>J&I0gO*l{Mujj)h}bXO_V+Z~`i8N&?5i^<z{YhU>#^(5`SB_zAQp`~=(^9Rl};hoPh4VelCAMR*MS5;`7!37&wCgD1c*qc6ZO!(-8*@L2dcv={sw+y{Le?gMv6Tf^PqwrD-LE!+T=HKhT^!mC(ka=@$LY^ba$**F%y$U1WZz6c*h!|+jf2f7B{0k1$8!z<wT(1q}O@Y|7i1AP-+2)_x3&=24cyp9mwj4p?lvwm$Rgbx$Kr_ep{9@ei@gz!J;5AZ*5&VcIg@b9cy!Z}&P>Y}n{)n)Bk3)hABpt4TwK^w!OHDL+iji>`l2!DlEf+d9W;ynOAz&er_tpewTR|ZsN?O4egk`G=97bk@O=cvj$@;^fOEA%-06`UBg)+C}I!-?=}^j&y0{66{?{64$@eFJ`jakGFBUW$g`rSK+n9lQxXL<k>1H^ZA5Lk9@qztB_gDaOiQ=xqVzzu*FdaA8!+6-IO77iK(_M(e_*;r{3zcn@QuKOsCD{R*B9zl6%Ye+gZQzmj|W5+VGbqbm3KKSKB%`W1W*-is!}iQLP*gzy&heRvDJ3|#;(;GQibgtw!c;O+29^bmX!{u@02AK-rcjmrJ_n`7bIxkrWJ!u0#?gm6o=Kir@GZAl0hLSKSkqAv?^Ec_e&c@F*!PDS^^d+DQ8LU=d23|>ZG>?VZ2MNh)t!q?HiVNtoZ>u5{3C2hS<IpOb7Y3uj2ITcRj+~1?$!q-tbmiHC%z9BuLpGEYoNE|1GzaxbIA%siCsJ;nH2p5UyV9HF2#Ix{V_#uu(E5UEUZxX_>k$5^1Wh3z*Jdk72S76b(a9OwvA^f_GnMj*%k3=D~C@fkG7A*mn;Cc!X!g5_wPkN-jzXGaqd^DgT{AoZ#crIE9mJpWql#OU?B+8)W;4*M=v^-oKE{Wa^mxN0b!gmnDcM`&PQUCeK`L6|3<@jVkLwH9(L--xEI4t^iKw0!GEP4!n2Y!PP-X4h>k*FStnuPGZ=sobga4obVTnny^R)$5Zz@k;*+Hkc<42#6#NKA!$a4gyeZo}VMOb9O|geMciLkQtGv>F@-KTJKRB9RDx&++#hUnhj+-Yn*P!lIwUq9<U{bFhT)UEEjUtC5JOPg_S~C>#$@;dl!7sXFlv{e2JIiV%K=5FUiS0S|&-4d}d+`Bsh)E>8&GO$b*YgewukGT(DWt|btO+=OrpdO4sR178WK{s>=ze?q^8e}cb3_ru@72hc6>0r(R_cs@E07M%vqhhIZS!>_?FpgrLi;9ltCa4+}?v_1R;+yQL@cYvFs_28y(eY62wA8v>?gB!v@^bt4+KZ<sPABDT4z2WX~A9M`d2Of(~hsVM*(6`|k@B(xzya3*Y9)!2ShtO}~L+}~&B76q^8T}vpGyEr-Ek^lIID3q09ymLE8=4Ew#n`=#+#va2KOwvYoeOV)=Mlow&{yDT@Mv@(JR0taJ`IaL2={~^N6W&G!|l;>aC^83S{`l!*F*1y>%k4s3UC9s8CnT$20uawcS9e7MW2Pc!M)MJaBp}FItd;FPe<Q^r^9cfpTTd#TM6NV=yCWU{4M$&{4IPD{Rh4X{|}Y@!~Zxg#W*U(J|i1Zf^k%Wy+|IS7-Om!`;}ZoQP#zx>}djMVK@NG8YwD!mdk|jkAcj6%#Vcd*XU7LbU!S)Tyna%P6~g6o`psK4rH#e!at$1hw#>9VQ<|o&bnTlJxvT+Iwo_?FCCQ^N;AJov)8!|y%W9-&W_#{HD~W)UW-c3^yav*w+;xOLC*y;*A3xA=!rn)IwQOd{XCGlE(tF{7s8^G1DR`@@C<ZFAae~A9*f2WGS^JuKIp@N%r#cHJ6bJ}xh4yH>$Y$Zts2N&=Y<=hRRWoLLAX9zIgpu0gqxxj1DSb8xC43*EZQoNnX`nwye8ZWeFhdC6v)hp!d~7Kehqy!keO$N=c8`~GV`+VC+K!q^Z@*1B*sUgFCqLQAv_a(51t9XO9*cwg!iIhcrTnr2>(C`|Bj}>zr!~O;T$m<!a31YSVH(FA^Zm+d?6B>Be5?MyU;J;FZu7g&{TLAyps_A0!@KaX!jR{@FMg*co94S9S=`{pF^L7MZ3VF&Ee<ZMge^mXc5q71<}TV%x4GTnrNdy=Cg)y4YWC21FnvCfxFNSZ*MHz8tn_WhU3u};dpo`IujlWPeI>>r@-EGlkg67Qy}wMO!y?aH<0<fCVU=EgU`d)&>vvY-{EVpJll!h2xLBc3YSG?%#|gCV+rAMXiivE#$P#(h2=T5JbX9$2P}Fakohbld>!x0K<4w2@b`r9DRduv3Qj~f!-?=>bV(rd`A&E$It!i(4<m%f5yByK3A}`QL+CD8bSE5w-$%cIMHj*E!!9}j7JUwO;pfptuxMjgv<3V;+!d__i`Irk+rVAnrwHMGXb-pt{n8H|2ls;~q9HiMwM|4_*rk0F(XMb;&OMPjCvtpOB<e)sPD1!Tv=e+E+z}lKcZ7$dAHu`orG)TdGzmTo|H66ir!9BE51^0155S$#5pZXC6#4-?3jPQ^0)GT26T-itzrv#VW0Ze`3lhQ=(0kwtZ~-(QTmZflP?c-F#5E_uEu6?RLnLORv*Cv#@p>d4M(4t<BQcM%^C&MoD-v_${UzEeisy4I+6JCSUGvd4aDzy^8i{)7L|AkjTo0~|x^Qi{F8T^AS|6^@@k8kAa09OIRdg<VUnFWo;w3`(1+)tM0z3k}8y*1<A%q8@Wns}$@Bp|MS`6+5$DxJcIQS{r_A>3g556BA1K$tVL`T9k;i~9RxGH=PIuO1GjzxRJv2bZL9xe?RN1uj^!$r`i;HS7QVHrcs9UWh@;2CH$cn16$+5~<Lo{Bbtr^1ub%J5`(I3e60Ed%$5pF|76Pr{wiJaA{Y1DXw%IX2zV`PTvtqSN3Y+!UPxH-#Icli<d1L-cvLAzTUV2UmjcLc7Cv!3EJya6vdX+8)jg$DnPUj88TUJLn@$<{#ngXh%3ZoRbi~4ebJpJ`Udo=R>=}`QQTR6L0}IKOvkK?F#3GbD@vHx!@e=qi_y5fVP80JHVpZ;0GchpVUtvgvS%YW6^uzvG6Fg8Z24?9t96W%fZ9oLFgUuAh-`9+ygBEi{1|RfS)0RpGAwp&%!;?l5kJBFV`;DTnl{>t_4>|N5i7e!PVi4gm8IuFg%#^lqZDmL`%Ze=*L!sa7#kCIa&v94mU#|fFGdU%?RNpgm5FYI@}1Zj8=pz!)4I&aCzEWh7c}<mV^tzdC;P89yl9%JDd#;pe5h{oCCeX$sF6l-uM^Ji<W~W7sNW5^HDe_S{fED?qtqu;p}J;Cv)x#J7{4i^N+B%o(Shgi#eI=k8nY>l#{t$3Ezd5bu!mC;Y#S;PUd<j+z_qeWUimWjnNuT=6WmK6ul1?z2C`PtA&Gva0|4ilezv2KZsU^AB5|p_rUki*YyeEx@bPQE?gTe0E^~#GWScu_0YUd=Ke~!0a^|gtpJNwgGF1x4d92-HgLywftaG%{=fdO6EpwF^Mm92KT@>+rvINUMgPqmk-9Se5mU!@Ib^Iw22G4fdJW`%oc{x1E}vc'

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
