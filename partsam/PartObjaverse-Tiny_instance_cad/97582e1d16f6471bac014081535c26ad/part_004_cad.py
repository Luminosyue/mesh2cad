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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_004.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_004.stl', 'source_sha256': '02581cfac1c2c19ae16c02af9125377fdde44badbf08afb0ae5d66ab8b0b2d58', 'input_faces': 828, 'input_vertices': 478, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2657366693019867, -0.45818060636520386, -0.006344452500343323], [0.2657366693019867, 0.1657259464263916, 0.18291699886322021]]}
GEOMETRY_BASE85 = 'c$}r22b2^=+qQei7{CAuC@>%hDoH>kY7-=f1r!tzhOn!o1pxs`Hc9e=2qJmNK_o{>z2qzkl0+FnQFs*v6_MZYO+C-mlivN#`Op93sdHa@Z*6sTrLJ^LYM41o9!vifu|7HV+tQ@cmSw^{RvxQga__!fIwkihliKTTpLL)3=AWnUH+i{n(yKnJpEamN=j1+}dY7o;FHtR}Qi)Rj5-B}<_wC&wwSCXtos*4Ur$hHX$zi|G8y$Kjhkq_v@wrN+{1u)k<sahzfBbh>I17POzRz}r)jl_Szvy=@+!w+cTKLZi^RqMJ@}4-q=q>Tx^;g8Vx;0*C{J_<#;#-%yN;*#EBa4l1W$Gcm{ZjjM@f$W-5bImD+oi{*?_an7Q;GNQxkGV&^*Q2OA6T0HCkN%Z_W4obyN%p~;-|i|T+%;0QsZatxL5osqvW~n^5Np!GmFN(uia&+#(%KW-dNx5o?r8m{&ie@r_sZ4zIEwtd0)HEx5vfLb!lhp`zHEcI)NM8#kX!8*)2M*#)6D|FMjacz+;k5*Z1SfGtrOa^Y!GT;&(r~JvM%#AF1Cn-yM<iOupvE#!vJk>F1quSmHglY@3w(JDENa-JB}Em80keiFcysW+{gQ)x>xI_;I87DO=Y{`rnj2oZ)j5{7AiAxvuS_LsGh?`-40`u<0l9odE@RNW3Q5*30iZu051dIVAd#_V(!l@dH&{$+xqlp7>Vfe&V}@t7*R5cik@Kf4qq1=ijcIBwgRn%fx@-rnbwv>oq^E^6i%2_dX!LKi5UczrXEt$*1+ptb-ZVZ=xT`XZa55&*`A~c<E1R|4y%h>OVM4>dmS5%9@OPFCELDPkeh%AN_sr`O7o%BjtZ}$^j{d`@a83;!P^QOVU5wMg2h=MV*nwmSp5d+H)iIgF9wOdkE~G8<h0NCLf4x|6VyH`jPyHY)wCP?m9^)`?pfAfj&<k$f!Ri`jPjVcV7Cl`^pcR?xh`44uQoxb=;|6Q2YCHs~2YENBT9sH=a00TQ11RkCemyvEm0yAKohM>e!?6rGD=jF24WciF>6Se_ti-C^V~pK6lfGO<KM`?veP#Htmyi4^Ef(f%Nmz|E%}diSM>PrTyijq7vU~HbDGPzV2F2U0X>#+WqTk{Cq{FU0Y3^Wf}RA@e|)0&m;XS!H=}tnt#jthu)ko?_<}RCiU*L`c2C#sqspwkF;r$U-#Ax@!hjGrGA|o8|O$m$vwmmj{8abRnj$SkD(&<wR{_wmv-gu{dJC(^9$<py|X?Wu_z-yS}*E*-@(Xuo8U*r&)Qq{yZFmO>2HDam8F~m)<@z8dd`yZG1Oy))Q|u02jaUWb4Ys%b+mPy7*j{nJzZDZ)3+b!bBk6|fATH;{v2AmC)T(2me6tfO6$F`zH@VxwijP_DJRGCXI}eU>S6fFEwR2eWP$i@N?>)Y?^gX)<_n=-tKGQxmy2n;yYkthSl`~UU!OBJ`;NHh9(q>Pzv5LH_X3`Or1@9k57P8K-`<SB<kFV7`194bPIfsE=l}S_S&5&Lkj`24?ZNTs1b3?++7X{lV1EA7^85Lh<DWZFeXDeQ`hisSLl++m#`<nM;=fiYEzVy&Ov>3BSvJnMM;6m^ek(qmVA5sz&Rf5hh)>78SHEL#cbX#o!1GUO`2?mu5RCIzQ*JL*PmA^Kp!&{T9ahKs)_3R5iH@xt7vKGza;_1dzMZbVwK))<PLOgKs(xsA1=?FD`OdmSa%;bSue84Ji)D0Nax!T-xBgJZ{m`k_tIW?<mOI*ilj?{cxc7pjYfaa77})Znem~y5CgX<nRhsk{drnpHgU?^m@AT$;IxZF{ujw2sC*!bFbHqGJXYx}zKWoxR=TGl+li&O27FU1xv-`xKwrZ#Nc?zpP_%ZeK6_at=`s|L3gVy-Bq`wCjH;{Qt@TqI!2P;&U{JDer==-%iE55tFmyT~It7-nvAJK94-0n4+{~r3j?U#!mxZFy|qra~#()8x2zbr+@N4IHyd0%Hw7fmOnq2$APY^;nM_RM7U`~9omxk7X0J7O1lRr8;Bn9hIt9+vd&Sxq&cSBq)6d@)nMUzybp)oQy`(#cv#^IN5{#((;Tr0*P^zER(!mOl4LUtK@Ueoy8#PU-6U{m5HD$BV8lblh88PW=;(yq7=ly^h;kN@w_7>-60j`_HTIe6wBG6*FFy`trY+L-Uz?gyhF5+ePx@KXF^;qwa!qjsH-R#1B1(fAeiEpQ3x^?}FoX{^~u~_MUtFYgha8F6m$H>3bH&`PbFAx<4=d&drTq?{jTG<!fuZT7EFY^h4X$sK0!qj5Bt@yB5azi`2J9Rgm<Zq>nZI&#r5|U%RFC(r#&n>D%{?Rlojet*?D~q<lhi-_&{hG{&EQChm##?Wv42bBk?>^@C~nfBdu~)^|UebV2^^RD3%AY3c_i6pu^CnMC~WuIu*{-`b<;+Y>IXjrHA0JU5rKFxGd*;qPs-Jl6Lw;khaA#Km`mJonM~`0g0|OJ8fd=#Z@GXVQFx79Z2{J6cKnKzc!$|5&A#>U`<npLa<*SH742Wlim<^U2z;i*I$zt?P$&D`lJr?z*Y-+RhVoewJcMy#;rd72mCUP1D(vs^iV3oZ|auZPWR|g_&BvDL(a|9ePIFNwu_CKUiG-z&E+19Q^p!M?QVuX7|SXOVqcT+mcQ&$F3dHetNdheTDrw7smQlIrXjX#kGCn+s8MalK6jUe+hW$e67Cqbw$nRi1On5*KW}9;^oHjo$>c9F1}lQik5HjTJqk3ONV3~=q|cf=hMeOkn!BDduM~BlQ8e{e5Y!WBbv`Xd*l3BlXX4u-SFM9ejxu2oi7y4xg*X`m=^`T=VrTG=h1@~>io(}KVkmk`QCiS+8OVA^A<nz7SH$Qb=I5lejw!w-G``HH7(A6QGNeJt@lX!-u&dZ67lg<GwC{F$MW~2oW1x7<AdjW{XK9h-uLEpwl}ZCw+c^^_j3Ddemp<eYwj1~SJHN9d+{%(={%&I&c{4Iah~S+_9L2(Ra@svelNZ^kFpbd#*-l9iRU{H+|c&_L6x}pRwng>$+_a<d*h75I1{|5+p^gH5~9C2o?n*!(nI@80N+jQ7x-R33ek^(NmrK2^XS(O{o28|ym8=N#sSZ#zX#~=5kH~7`xg{lAn~YohkEz?#Co^zorLd#=LZtT`Otjz|LgmLZ}Giw_+Gf4pZHzC4>Fzyyzv}AaXb%tenP!_et_>tknf1+TM6~+FZ1|(Nr&&X!}r?qeD8bxF5m0UJ%aKx^M?@ghk)lN&L3J7ognG<?5*Qc$r(D{;|EWz)AddAT~eL_eE*mNx?eP9f{bq#zRh@LGhT(7t8XQYlYacfamMrQ^}pzP`qG;^zBMDCiQ^c)|Hdudr^@;JWNB|+{Dkq%^8>7Ntr5D;4JDCJ*16W}tVi$@$1&IQ6UHCUw^=8KSSNbEpLLwwPuFpdmrlaCZR5N1G##7uk>5*)b*sa=)$@bi`f-%5AKj*;&pO&>9qsux>r*?V`3ZVH>$L#uH3vU39=2mV^y0G~w^@(-z4)vL9oB<x6XLV346&~C{K&d;9P7#^UOUwIF6&my^ApC~z|wB|d)mMMjJAKr^S$=pL)(8SX9-!CB=#?V>F;HJ<c)hS<DQM5IPN)~&$t(4+>7|$xc8Eddrp%svd;9zZT|u0IiBy0+o?KkyZDiD`=XB9A$)J#_TQ$zZ@i=HGw*x-tbVT}KHqD{`(ERF-%Wc!yzlVcv?}X+1@Zmfcd(9@zl$I8>Gvz-eZTe`(sdj2sNgZ3M}?Xe*L@)7U7=#kyQWsq@q3NV)BMcSoPN7>enh$1lv~74D7PTKS3Wl7<9hME@(gKt21i>v<LY;GwK(5v4<XuviyvB{_3Kjao}XCn_Vk<@f2Pi>E#}q!g=NLJnTNZ(bsioF-qduwd3!SR_F}K={(1+U=ew^l&%gMy?$>(jg7<Y@;NM<J=SQxtBiyHS9bq+3R`u2$i&%I3Jx1%Jp04AZy}FKbo9N$#YU;Yr&7$kRfc>$ib3)gNp{u%13^ZEf#`Z6l{uS}P@7Eape)(q{%rO1nzh7zkb#<NVXPp};eo^D!)P8N#-#tIl-&6VC4Z4<L`c}!?TE5;oy@;;UEmwVazOL)tysYah=Ft6;T)GbsDx>=Vq0)EjIYUVI4crfP-yqQLp7e~K>n<yuu|L0@?mvC1`xv42>|+$HuKVA4bl=0zzK654mc~D<`y|dR_DP;>EPk+@?yFers|3b3&G5ONZ+rVTr*z*Yxa3uR-#qN|^kJW8T(ZW0OZSD`g1Rr{tnVVe#XgeFK2j*9uRixf{jOV`mTS3no1^8nRQIDC_M?JLm+N_$w}17Q?qAu5k7)Yde%B`UyXu_Pe6l}gu|H-#dQH=3KP@;=_tQe|9WBqXy8mW*`)^qa>-ubv?$?DL*8Msst+@Kbbbrrcf6sQFQooVz2U_e02JR{^e(0#~ABGp8vVUk#tg7Q&b=_~Y*>4P8)bY>SK6Qv`x1q|*^*gleMNMav?pwMSbl=jo>xl2aNB241X}ZrD+|yLk`F&7((PppAkmoh{P{)arx?k#M(*08Zu+lo-)Ykn~Kl`gzp9<Q(2J3#TJxKRs?fdI$xpE%izpUpGfhrBvx28@s`429rFYU$p<O5Bogq~~IoNGA0tkC_NR6Pd?at;!zxK-o-tmh_v&P|+VWpuu|ebEHbF%R?-fBy@*PnmFzljujzsqqufaT5K=dEx{0)o-NdNA_+#KXP8~q33FxH(5>fyvgb~MDuyN*=9-qxd~DZ{$Cy44`?-Zi_~w9voinpzjIUb$$6Ibvz}+Ub$?U8sh)oYIR6Tk|69+CI4`qma$Yv5qO?o9Sn3o>e{FxwZ~uDYXLNoS>&KqoNxB)F-^Kco^7*E{rt|%cjS~O)lk(h<JwW%nAJ+54P!~N<^iTOf{YtNFHSztsJIFW_7_m<C&$*<#LeC|gJe%~noMXDKo@3fAe-S^J^9d=>;MFB7<T-_IYJSSqkn;EE({Um+zQBI*H|ja5pL5c{U&F)?t<-bX&~JLK>TVjVeknbN4II^T*x-+I#1GD`x=GT%^`q|3d>0fykUB*77ssF1dHbpb;#<RW>VDpq*1A9U*gDP6l`WEgYu!HWkBfJTpLo8U=ts^^@e|LN6a7g1$>+tlIoEbVdafP3`+M>I1tv?qI714^xM8(@MAjvtvP*Q|V$}CC&ky!_TGwF-=jn-l<UDj+1x=?{kq;%^MSs05?{~r$-{QR9;=JCUr>XkA@74Xz{qO4cv_U8JU)!hUdGnU8$HykCpTRwWSU+;UUrpCrq3wF#AhcKS8<_hE^7{<#EyVhfbk0rDbz5$||6r%-{RjW*Mf%*<&U=#1`awF5-u_bkMUAAt1P45>?=>y!LD3Uuq&>LF*`>Xidl&L|8QjN+^&{h3uY%%dbl)S^kHjz9L40?%-W&0^(0e1n(GxU&|3Xrap?tff-p&0J@iVxW66;6Gr`RU(L!X_}^MPztwLCi>5I=aY-g~jzaPOtuP0ddoy(bgko{YP*$RYW=fAn6B`|ovKFIjEHcOO`@Uedqzq<l}D+kG|u;91gcLu>Do@(-l<6W`+Aj-PuwcFJh+L+75*_Mf%;R7tn=Jn{Yc)3l#vpQYdNRtv=sR@Qq#e(nVYI<D2{CfqMd^dt8Qmi(mo@2~fiLXEknbmqF|lY33he!bV^wkmd5er{1^jI@(%KWTZ4E-t>6)I;~Vn=jXS$EC93C*G$@^dt9GDpt_+%fB*9(@Sn8f48}srq6w?V6xuVvR_UT-@dh4&o}n`qvP1pRQ0p#y)XAuz4zs0oukh!s`teFL-n4R{l%k4B;At@b-%OkP<^k*tEzwbl8)!s2I;!})Ozvl!Y@d@Tlre*Ic?`-;#*4#N;w4bJS=|j%y&mJDu+ZrGEQ##kN8fT*6NR6E$!Ail<TOJ)43AbPw#(C#>wD~lHyyV+H{kCUGWF4$IE5JxBnVAUDEqDi|kXGdv_VNlSDt#k2((2^b7USee?kn^*i|3w4+)cSLA!--pQl+y!qrY(e&ziep0`LmjCeD;`^&Nm3;Us9MN(p@S^zc?LP*}`&}$3^F(Kz`qr{7G7j6b>*=|1gF51ey8Nm8>lbFP)ppuk<2U<K#<$SJJyvSJ8Yq6^xRK~b<{_09i62;%s`WeYJsl?pey#aDev<dSr0x0qE%EK@NAx^r@H4uvaXs^K@r!+|=U1gZ)pf&-?cyiiw@maS<K(!#;=A3S)$-rbO}<y5SI&v=-`QQ>H_)Yzo<G<5R{X^8W1=5>k5n|_9;vx^8tX^;X_ukm|JOa$<-^5Kyw_^(!HOo_gEjYN<?j;i&4#MY(fA4XY|Xt~$xq_F+)O=ANO}qPdp$pK-e~R#i=TK;__15!C*CWz7X2fB;{4p)TbAd>&hwMvZezcH|L}%MCBh?FIOMeQSScN1uVR<bXr5+#6}wBt|EsImmCFBrU&VeaoQEdiP={c+0$Lre02e`v!A0PFXhAq1TnH@=7lKQo&%!0)s_2VwRk%Ld3$73MAs8M)FgzUX2M>qS2!=<X&EOI6P_!OA6dr^=4-bOhMytVZ!voM4-~sSpv?)9ocF?}C1CK`Efk(q*(05^@6W}rM5`y6m(JAnU@CV^A9ep320>2MWLMOtL;Bn}9*yt#D96UB0Mxw*eQSdOhKROWZ4=15-!bz}=)`4xfG+F^J4Hrd=z(wKwXg)YUTmUTu7l0o_OTv%A<<P2dIk+xbAFd1cM*G0M;gN(sl#|gR@L1R@+ac70(c!Ssw3s?di>b#n>Ulc67##sGhL@s4;id3$bP&88{s?^={s`WH4uChno6y1VCU_(2z#HKe=xBHaybK)!8(jk56AszJ;a)Tc{6siB84gdOrC{^B?EKw5@Lgz5_%8Tv^gj4*_<r;O_<s07^da~`_+f(KN6|-MqmRRn!X?nB;Sz9pv@%>Cu7W-XSAi>`W#CG1S@bFRDaxlTWpWo~nGLqkyRGOy!#?zW*av4tAB3~QxzUH=+;Cp%s3!R+1(!t|!e!w~XycgoYRr2ZtsPSiwJ9f~&%~75GnA`Qe@r?1sRuv#dK7&aHtol>vFvDOI6IsZ%>?I!??bb|_rVXKx!?!jhtNFm6Vy`;v<zGWZh$@qH-H<VmElHkE%a%)7F-d19Igl#MjwG6Azy{jJn$3b=}AHj>aYfRs!3=-9X23O4GE2?!$#z(F`*W9Sc^Q>CRC&jEAsqj2!*LbKb#lM1Dm#OQHMF;%%~5}3}-^K!kOSKXl^(QoD0nh=jFMEuY|)F;qW=S8$JYo0k7fbb+G4|pQnby58-e&98RMr;M4FybQOFM{+M8RGHIIh))EX)3y1aSI&><$Ivn2P?^nT-(UtH@o?-Y*I9!d%+g0*z^c;MScld#_Fz<bmU^tz;rIX)ue8Z>0;V9+y1$+oy53eWhhe-2#p7S|;1w93yBCRXr?Njo17CwQlhF4P-CwTY6G39)ivOi2&97IpU=fh!NIDAPkydRwb8=Vb*7Y?6=!)1cu<KYlQ7oeZPCM@LlL3loC&LZ8}@LY5zJQtpW&V%Q`i_rP-e9~XUyL`p_orf==7vT%=*XSkqYdFL^e#?7*2Y-Wx;1KZ*XA5`KEI$3c35G*xCfEeSU!(uTJog{+W%N!=KJV}zMt8)#*AD8+=xgvkcm~=Ao&nE7+rqQpnP@k7COi-A0?&izqg~<oa1cEfQ}2e4quG7R$KlIpHaHvQXE@o?zGudOzb)+>-@`s%wEr1Bf*RlOO1#5_BmC|#dIrr3n_&2=75)3p=zDNyxI4NU?hbcFKZU!($Ix@|G1$Df(W~%P@?dy9@75VT0<WiBym7KKKcA#rO!)-DVP`nBBN#pq4u7CG(4DYpCp-AN0POwF=pA$i{7N`%4~I9<z3?0G>*yXh8C{F+v7%$X;dJtD-r*LS4yP067QygMbT51p{sr9*{{sJnZiD}Weu8d;KY?E*7;a72#(QrgEyJzC!3~Gz=w`S%+ydPKw}4+lx56*M-gCE-m;a#G(5>(__(yaL{3CoF-3(uce@0!{v<=e^I-<Maj&Li&u9&|u`YXB%{uTZM_1fCM;qZULA+t||VKbTe3%!jR|2Dz!Zv?}?qyNIc!+%=ZW{jGC{3pI)6AWiXGt<wrl8@|!%#1skSwLhXSd8OdUbFDCVKZi%esPC)H2M$x55NBd{R`iOzbL1_cu%j~Zd0zedFP+e-{GI(>*${`b^0fD?zL&J%^SXnUbCWo#PBWjNBBq5xfN5UhF=bcmf_F=?Fn~)+Y=0@hC>gu6WSB*1gD@aVbiBfAM)C~;g`@itZ2V5+yZ^wiuNPJ&CwJq+V2dvLR-Quc^|Jm8}5j9u%d0=a67a;Y{tfbrQgf|UK_MM+y-uorowIEZZT!ljbPaOej4qL_OPPg6vLg-PFD0AWH=d3fm5vLSlc<=_IigyC$taT3GRXRhkL-o&`Izxcn&%jo&&E#*TC!G{pfahKYSG34IhP%p?lzC@BwrOd;s2zu7x+lL3BPGgdNJkl*>T0Cp-|Ij5@Hx-x?mk-;YKI!lU6C=wx^X{4qKo{uthbu7x+j>F5qP9X^Eafe*n4$<F}l)9Bl9AGkmIF5DlUgnj@|g6E>k;JNS`bUnNV-j42sx5K;9gYZG}Y&b0(mWD$r!SF<M3p^2?hq~}Qcon(}UInj2x56vo+2}{`Y<L_x5*`O9qix}2_@!`o0d0Y{g-!c0ZOcJhz%7X55DW*=k-lhKHM|-9$QNzfh7X`yebK&P_!zp&7wtQSkD{(G+Sd&4N4NN*ebewdbg3`emkrNB(|pmsZ+IB`hA%o+818|-;){+ghC882zUWw#L^*YaTM&{c;}_tX=qqqdxH0+$+!%fpO@oc5!Y#w0NjSWYwt`=W-$6UV@4z$BH{qG^67(&22|Nq!1<!)}qOIY+a2vE4+y-unz6dvkYZDAtCm60uFkB6723Lb?p{?Osa6PmaTn}!9z6Cde8=`N*4dMD|N4P#*2W<t{fo-%2Y{SnG4A($g!ZqN!1jEe<hC86I!yVv$=sR#fcp5qro(3;Qm%xkR)#xmEHM{`r3on32p>5z%a0=QKPJv%WYr`+Y4Z`7hv=UkyHd-C71V0-NPovMF)nTJm;pgBd2!>0b)!-6vakLg(94>&?gA2g<(ME87_z|=r{0LkOtq&K2A4luJkHaNV8!ibyi9Q2A36~-mE=Mq25v>6mtqWI#D-#S?L7T%>U~lX){1Vy$ehE%S`}v~Z7sKPwX};+9$nb1*u`l}lGQ1L9?Tdcz46i~L_@duO!}HKlzUcSV@I*Al7ybSkPDNk#MZedEUqu_hufmOe(KhOh$%boECN(Lin)qJ1Jx{qBtppo=Hm1y<r5?OC?bXZE)L|*KH2O4L8h#3W4mSD({6#pN35OHtXYiD8m>Lf6q3^>}&<Vsd@lT^C;nVOb^mF(Wd>B0fABOj$`{2Fs26Q8AbOpQtUQRGP9sLlV4v#^{!eihe=umhFJO~{O4}!;|6W|Gy$#}})4DW69EBGY*IeG#996o}cgO9-b&`;rg@J4hSyb)eOeVKadicWyL!tKz(a634F4uu17cXTY=9Ug&x2#<glp)24O<jt^YGp2ofK`?wCJq4eKzeEqiU&3e6z3^H1IJyBo4u3*0ywIm@xeImn9y}g>4IU2<LfiYIZNTslw3{#5W(<!(hx?*!%<yz{p)cAd4KGJG!0%IkUC^#@7x*=_9sC;H9u2_l;cjSmxEnki9RUxA7ov;cMbzCw!nT<5+(sFnp)S8d&%<BA7tk-^3-CGgEPM|B6g>_f=UIjeg~OxaP$nE6f(yZU`1t|Y^UTk=35M?qhw|Z2G#rYc`QRdOUi4l#FMKz_a1NeVko*`e3zvZlp@m_SzMtnm#<MG+<>B(gslan`@vM7zc1|=0oP#(ydB^*BZ=(;wdEiIUf-z-Rn6kQ`@_8722!4n-hLallGUdtqzx}UKqyNl$&x-pWr6&Gm{58JVzf23K6}i-x)G(`@8)pjtXD%h>H@jEX{{TWsR@w'

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
