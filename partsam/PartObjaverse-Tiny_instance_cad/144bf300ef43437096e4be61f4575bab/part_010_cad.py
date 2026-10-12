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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_010.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_010.stl', 'source_sha256': '3f0fdd71a37b7b90a373d8e95500a348e6e4a55ca25ffda5a2e1aba74a99d366', 'input_faces': 788, 'input_vertices': 430, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22639784216880798, -0.22735126316547394, 0.1960345059633255], [0.016714096069335938, 0.008357219398021698, 0.41084617376327515]]}
GEOMETRY_BASE85 = 'c$}qt2T)Ym^X>)3tZUB57%^Z5!Gt4-2{Gry0Aj#E&_xl!5iwyR7%?y^=A5&R>$>Kg<Bnn1HM{C6Yy98S-$(uC_v*c>SMRyi)n9+NZ+D+Q=bjse+Rpwtau(O{ucB7GUihO+)iq5?0j;<e9U3)eSV-vTI-??D9JIp1tAE)#tz(aX&V3xTXf4)tQ0VB8DAy(i*JgvgT-^+=gTtf7L<Nls438QVs`%DHBSwen{OF-U5uv(W-MwKwH$%f3ZiYC+|Kq=WdI{F_&*zRRy|3|aN?Sg@ztlqM!c~Pg=FSw}bS&z!@GiN8*OGb(Z<~={cw@r-v*PbD;e^tLQzgM4NfchY+~cI^G9STT^b+25y}!h<4yY@<HP%&lbIGQsB;MhOE0T9hY2mH8zQh0Rc=)@VJR|-|Yb3Ar)K9`|pMC}Z@_^*E#ubq`hD&k6+cwlhJv~o~zv*fo;VozUB#y0IJ>hNd4xg6s)IKA54gODsH&+}Xys_ID@i!NnfH>Cz;BP4={>I{`(6@$%#ZSx8LHcLz`|XU>pLIZZQ$~3ipJiRC(^6;Va`5k7Vt$&<KP&Nf#A2L<JcT!$uOe}5xjP_!=0fzz*DAcl-BEbUtup7O9{<|sr2c>J{wnr~LYU7f*CnskcaHGZa8Jxz;1AR}wH5p`_oM#7BP5Phdv{#yGa>LFw@~UdL|zr%wm&D<QQx}o&rDk>evYLEi5={GOX}=568xivk+MFfb`jnh76jgA86@%cYTzB(flqASO~(H<MtGw`9pTNhj!%=kZ&PoI|Dh7XTYdH=$a(40gg34)0{=qWg*Wc{MR>#ZLWuux<T&X|_!Nn6iYMQGSd`fHJ%zUgKU*Pu$#-$0&tym(ZQxY!Ux$yDIx>!nzqx#Z@aBz`XG>k(_oB{Lli>fONutb~OPKJM>J!0NSQ;&H6WSxrsxjb;dd-sh_jbUz9tMIx`3n8?r~v;q<VOWfm;9%n!r#yb^?V5$E61N41i!oo{G0wP{Wtb<lQ@PkZG|_EY$9>A{F^Y|%HTEQ*j6&G`{9_E8@0esygx+N^>3-dYd>7TFLa(H_1QAuf1wO`pA{2CPfbRD?l>XulrZU!dCvvpt)jty_`vbPpIjxp?d(^J@Si5iyjUAlN8U+Kgf~ws6D#o&eiwi9qsQ>iavmu8+H62QC+>n@p4C%ykw)le&70u8x_6g+4f121JhlpNx_BsAjxQQ5@lCyF!N1a<(l?`f8u)zS;Mc^MrOv3=;LnGm&RTy)OT1mH(TB$a;U9HM{7r8SsONMm@Gn})c#W4k;QCt7$b$8;Ws1Z<HvoO8?goDUWm!L#_$TP+_L_*3vxC%c@ce+hBTIlcJZ~@Og`uB@kDoKdUiLuhF<*UzI6+r3uzuo3$?^Df<ZXKt{F;^FQs0t&h*Nbx___s?L?`fiZ?#!?L&wAvrEShzu|7X97v5ZdysTSG*eT3op+w=Wy^V5xX;UgAew-QpDSuCv<GXfao$QD}-V#e=gwK5i{d^gUI5CCh$nhh;A%4CP_|NM-K*n=n2=;*jwZRu?oF;j?<N^P^JoxHU`iS0g8tdxtkLBXmvuuRaKW7s9^W-n#we!;_ir#Y@{k(V&{KhjQr4M0s&>!tI;-sce6<x}i`&Fdy#y#=#WSvBxKpfwQ<*;AN{F?VWVZ0A|2ybh?SNd$|g8fa~=8e3c^T@h2waJBbwX-quULQ3>@-+J!`_<MD%fvsk|6u9g$Q1b3cq+W{Z82QGZx&%*-aZ2Va|-t74WBT-wJ(FuSxwfbX$JOT>p#B<Z!U2Ieai?%e3w-4lN07j-hI_jf8MdE=i+v(Ps6X^2Sf>PvzC$Znxmd$em%M)PDEe1Ud$_AqMw_pg4g!Q`Z4#NiN4LOg!qeg%5`VE&Fiab#bp@(aG4j|ft>KaV}QTK%}@MV+u&d3@KW*b(q87v5?KT5WKojv+K<-Kf5WVn@ZaYxykS%|so&_f73(doGW@TcmGy6&gniX?svP1MdWC)(ebLW+1rev`QpszJ$3A8qnp=4DU^iLM*7dEB_rtj*Vi%Y%*M%Ww1oGBcF1*&RsPxD1*Lc)_YKrjY9tC7xv>AC(Psl{@wZaf*?I-vj8z;OmPiv{)VDUiwDWS-_zqPD4t?uuLV=fIo%M<st*SOv-NB&KhI6E`2KHbkC{)jB$4dt=U&254(FH80bZ(ejFRpS5N5d7eki1TKstOxD2(`||WWC8g3jm6)zw=MGKPZC~R*%|lcO|{TB=NRFw#ayHws~fI&<L;sGZ<s0fFKdzA+@CvvFX}u~*2DV6@V_5``s*djd>OS1T<6}XKQ>ePY0kY4_50OCoX_XOWqya{l=`is4Z@o;gVBe~>$n~xD<DqgX;P<YTUGHlrM_D%cKT@C7e2g3{G?~X8{=wA98(?cZ(XhnZ|=Ts8m=$IxAr>>|A!g!JZ0Jx2me3TAbyd$(ogfy{F2w4l8QJ(_h9`LX@NLn!D~0eabL)b{u{k&z<<NmNs=eAgv7BO`U!bclkwbjt(fpyK1bx;@ob^Q(;i`61-)A&aSPtVKACk0eID_r@aFN)@!YX{2iB)c4E#r2#dAvVPV}>Kgz%;&HSzrT^ep(O;lgVxyyi<i8Mjb>*)GBxPqmzj_3MQ`gtkTA(ev><yX8Fmb2LZZlBLnllbCm-M|t=Usw3;cTJsOgSEn-YpL9?9W*s;b^>-=?{zY@C$1)esnbz>{(ifw1HQd*pWBuDUy%65e$4&gTSFXYv{{CHfOUi4RN6VgH5NFO^;my_<S<lv4E?8G5ZU}EZc3R?VkN!cOl}~~<&&U0GQ~>7d<8jQB;oq8a{_d-om-B}Z|NRC$*N0yNzj%l6rXjzgKZEcbu8qwA?-C}w@zGJtd)c4C$IZv{&Vz55ufM#}hem&+4|BLqj#ooHAM3<O+yn2>PuEJq+jd>Ud9$#;Y3s_sF1iZ+Y4`*E`BDn?7hNFpqFr-Fe;O2l|CLM9XQR(O%x~+@3*>wQ_7%&Z7l{A%IrvNNScl=|uzot)gg1Jvk#Skpy~ViB92DL>KN#aMeL?)?3Bnta!x3+A1@!-ZSFyG8Htc)-FfX=ueu&e}0qd@D6XgBk1OA`KQje`xL*b42n<7r7P`SRW-|E7@LS5mlmp`NbA<xn0oMqtu_<`J)jCY!1A8zs#>+gU&_SMh9sB^=8Tvwh(^zS40tGOxgzm+vy&JWHF|F$#H-=xa8PVdygxOPt$-rVZC?6=m0=GZ^`jYFKcmFV*c?yEx@gJ1V|km!Hd&u|aKX?{iOxA@e8|LOYh-!c%-SyM-#52dPt4_Sx({xz?c8To~`UG~ActzbZ$^e?DybaUCytaWi68Rk6(-!vZQRV{+}J5C6%m70TbM+D;fwe16M?S*~l!6?kv6N~U>%Pj1pDZa=%ax(n=9HK=3igjqM5RSY{bILqgqvBBiuD-$>ei<)uEVrv6?+JfAe@y<2=e`82H`_e$#)*UFx-)+5fcmHBL!6#3F~1-Bq0WSl;%E9^U)Gh$Z8+xl#a-cT7jU032N#9^#^bo2hpinWdTl|}x#a-%qm46hKU}#6^<3SGI6E`2fA{Q;dK!Q?J$eN`)g5tiG!Wi$E(Py%Pp2dA&T@FJdXS0tr#$}PTNXgx-Y;-pGaf}=zq@k18K=eLdb&9f>)-7#_#^Jfzj6ZNJj}#%%%y}*G9S0Apq{)-gtsO&!*gTHWvo99ahkWpbKizvFfR+I<2p~giuc7@;ox6Pf&c7FxL<$0jd}w6gZJEzbrR4H@uS+Hp1BvHtC~?y87I`^JrL{V<r}Q4gO@S>>OP1UorZCBz<Z#1&@SAk79W9s%b~cR1uU2A!WLE?{xt^Ux#Z(G^!xk()U&KJ-gB<D!h8B&8`eqZcG!P2YKBOjftW|5V<q&f;9lv2?PYuT=Qkiuw{o%%SWjX-SaKF&J<fPf$~upEtdR?R&-&75+s0V*v&A_)S4ADhdaSn><4QXtys=C%T)&H6qi^4gcrN+l0G{u>u|CaSjj`@i=Zn8-@IBO%)d>EM=P@tZDvT={*NHK`67C}(KZ5r!fjF%au`fN@fqFs<fzSCG`~1T!<Zb&vo>y$8xZj-ajQ+$-!E@Vqe7CS>wnqFG4Z%C%{%l;7iufC%<ax!^tt$56Hi6u)eDEIrW<Q?0Tirzb5>3H3$SwUhq<4Y;d}rY;v1jnUwfGkJP4RdyS~*ktU^}xO{I`1Gtr1u!srl{*KdOj)k1+STh<R-G5P9pw%ln3<6#Ksr*QvJTEuMF`{f6hm@qyf*kAT1MLB?g+5C;F;tK@yybip6%s+5!DwJzj$uIPu@pD)%&Jw;F9{j=xbRifA8exbeHC%o-gPuv%hvCg&drr-<J!Tad5Pv9%m!1t!%ak$Tx&L#1+rZeTcgRyJbRj5A*{>#b>Z`+lO?+U9*pq{D|<E8!(JP%tJ^*}!>JIVJotJxjTaRL5_|Ftc?v!srYdQAVmg@3C%`2JXJES^uQd_mswYvjISSw9@{gYjIUomnNk`NbSO?=@)y-m)uF;%Ke$9@&2j_}cB{dx7SEj{BG!_~KvXdy2Lz5YIc;E2GYin}xU5OvZPkCFkIuH5A`po*JY-*3o&vcg!!}I}EXFQ0GTH=V(iF32)5jgY{6WCZ9K)gK=F)Vm)`71Kzx^zu2xP@tvmiLGZm-^^-bk6vA_mPd)GvuX>B0hcCV}J)Q;L<kL&+BZu)^KN0tF?XR@%!dvE}KNGfrKUAli*x&HoLc4@{)Q0x#BK)p9c+Vb?2)@9)&XTwOXFQ)2o&-Km`wrq?3gb1c@nf9Dep1KC9=Hz%R|H?rrLp)0|G<6LkG%PYhs14g0Q1}HJ)Un(`CTQxrG$*v;<1AMN2`cmyIOcZYK`|P&0Mpz@c&H0c(*(RuciNcMDYi`_}%UU`JHbSZ~X89`<QDZ#Mdmv<+{u@9nT}t&$!-Vt0--}RUGp^t}l3_UtQ6I7U20Xjqi`iP3kFaJJJ~6KPH@J{b`NlIyhSr@8#Rh@_v-jL}^3JcI=1Kzw^6Xk7nYZw;%R_N%OMDCA{U$4Xmq{IS|L1!(06S)!^SB-{rJ=Uwy>?o;UjQ!V11{oUhcmJ_q*aa$C9H=C+Y~vW}t8iTM3RGgN6Sec0L!&y6GTJg+5t2yZUj1o!I!N!+jA3vay_g+5%tdy{57+fHfI!vNH|a20r)Zx<ZzkA8Zx&O_6Lx28A3{p$~Wuh6E)b(Op+iP&%3C%}K`P2sKie6f#R{tW(9arr&T{Bb9~lU;qr?=XSF8=T^?4x=^1&kP3dZ<IPMYxsS8#7+Dz)u0ddPd|U~&8o@o1ct|H*nisNKB%p$FTAx!BfS5O<36zM58<`FnRvdw(}~yhyB-ohst@i*{Z{k3?%GrO7V=&0Uxp8%;Jxbhl6kpv7whN2BEE-)32(l=0C`{E0snHP@RqYn@SNH92=~do@Sige`#_UI;6D`aE%i5Ei})KRB2E>pkJLFM6we!T_VBx<ukhB;7kE$c!gm90kz-%!&q=%|YO9~Zf73(ZZGCg${V5;60~ojU7k|&bSPu*E-AS_+3KX4m3(wUpJ>hTr$0Tuf9K!SMaC|S-Iur_$@!l_w@21V7xIbHjH@A;RpU>w4-~ER0*31~(mxq-EKjCAr_#ejiQeznJ?^lvSM1M2mIk)*n@Ow6epbxm-%^{7!H;TaTqx(1GJtZH$OK9J7hD!YOs(9`?x*YtUON2KRE-&+C%71|C$|Ah=r|r0YH{(4^OYb*W^m#Yz4_^BbXG^ys(jTj@)M<Fn``4b?!dor5aUbvK2>z?zP^str4(yY+S26Eq;Z3n^aG&zz^}F<@@Wy+7cwQ=w?<!i?_lUE0KgQL9`}2b%!zAyV7kC~!iuWe%)bC*uCr2;5A1Cp5lg@odivMaytdj)xtzJF(ok?>&i0@Jj=JPsrijcfztQc?qzro-21^+L;TNt<EJDxW9tMG=5IH}(@X9>rZSAJ);?8W|OH1N8}H&=LT4M)7!uElp7ZB#?~{aE`r8t-}YqrpEPA-pYNBgWO~82G>62yeWfiua*|7VvHJ<9Fo~`0iyq`51gB(-^7$+jl(APOgM{1~ii2kIkh=M}p^l<hKOywzsIqKOTJ9MZ%jr2VmY^xqrR^Z;tAY_Z6?(;HRy`@6%H^<9p)^ckrpZ!Fw0Sd*VR;KH^wxtn@RoH{MGw1%UrJRd}<@yq~eI_&vOy=Q!y@6A!F6ry1Zg9|~`6+yn24Q}JC(%a|M^d{=xIF+b;ec)eYC(=P#7S6M5-w|^zPannq^Ul!zk@}|sqiBrTI{Tw+R{MV(iqIaak34iV)_+3YZHy?hD-y`ngyO4IPzyygi#u4Au5A*lvSAB)oZ%lYzK7rqzwf-Z(e@K_-GTV3Vha>97NuA3p;k)RkP=4oZBfPnD8h-y;#`|*Kx!}Xz;XQR0??)Figx5m5$a{&kD90PWUU*BJrdYSt`++aAdZOr9UwJRqPV#sBVkOKt9)`U6@tt2g-AH(2_#olUeP-eNTk;s;tsYIV9vWwYk6sMk$3uQ+G4|o_l1FzUe)YciZd{hvV})J9n+rXW_W<h`-d}RJlfNg>D&qa#)E~dUm|H~(Z|#;B?{k|PfOjk~S^T%{s4saxj6$42g~4kT<o(9%ln?&Lyug>3F+t+zx`^LZ8?_VOoOndyn=H)`=jV~|ZyOjOdc|SzlZGXVuG$m*zl7hB&8e5cyMB<ryRha;g#V4l!dojAmfw|ZGv|VLa-1SMVQHY^ElUT2zt#r4|DJJDPeF`V>uD3-8u?A)SmUzryQjJPRMC-jWxTdP7u2)Q1m5!m-m7XIhyRM1!fQE~$#+z(0QdPCv*GXb2YxTB_9y!D?05M0UM2S>+nVl(ANF{f)HA+^{7!0$KMen0{uW+yZ#h8foZ*Q0-3m+>ZC>Xfb!H9c^I<jci~f=4M{8bh@EiAo&vcM+Y55zn&iCL0TT7o!r}=j~AFIufbsJ{D`}c0fU%EkfZPZV)FB#qigTK5>c(YGs;kDtXIo^v&!vEzizv~%B975k#&6*|0lTXQWz4gmR`0wjFTlBC7vJY6IXMkTgU3l~NtN6a!=NtGZ%iw>voUB9Z2K*g}w*2KBtlR6ok>@({cFdJ5_NCkI(*LL<;4687ZyO+eHV#^W_``~%pwIplq|d#tfj2vYe`FaZc@y<|I{(*SLl*4p_AH{R{-&TyUahz`ILPi#Ar-0qW$XX_pF$3E|G)ZENKY@X|KC4_%&Dm&H7%Dej=DH-7&&OGe|glh(WMx5NjqGSw$i2Ta3R`Cm$AbIXe(XH4(Fq-ba6YJo3_$L?64DUrGK)+d1&WhjS830rKm22b(y5gQe9@~60ge`T_zAurmbYCS^~tAX)B2$uW$ryrN`RgNwnuN&r;$<+KJ3Jfp{M6be@|;yp;AfT~c&eL%fsrV%9c`I!+g}E>o%Fh!gDiB-*idwM=EaB*vb{{PUP&7LTXXCxw3L?89WnkKpl1#0j+H8B4`k!k8<GC(~ZYdXtH#(pJY-(|<AJtmb*~j2XfF3B*Hb&tng>`#OX3635)h#FJ@HWsg&c7t)@`zON?UN!v@8O1jh__N1+JSvy>wwlj5k;&OI;McN8ip&g)0JzZ82yV7=Lz8b^<wEcK)BjQ!GLv>lEODE#pw7arCA8L19+;pi+?M__Bj&DS}E@L!eya475U|b&__oL4;`uTDEo{Z_t<5h_3(Dq_1ANJAJZoC!k`cRH`XXYJ1>`7bI>8(pEUC!$AP?w41-FYm4=XE9SL)(*e_^>uN*5}MIxY2)=UGM9$o+{+)vBpZA>vF6+du@2L4o}wY&DuJ#XLVV7C*}%eeF5yJvO{?80ODZU!HlPH3&!y#_NVR7*x7hL?O4XX#(W`+AIf8WD6u>?k>?&KzD9cn`#zTVA?@+3ZxnTZUHa-0MBSe_(2hS&JBTrkGhQrn#xm|G9-l~`ExK&dC6i+hW=ww`-%lJ!JA|=RoH2|!fjF49szKccqKNy`R>u<QKb~<Cd0q%(`ZIqZaSPh9>|1s(Lpc}w$%it|Fy;$pO~Y8jSdKf0b&aJ@3(k8i`=#b#t%f~sCGkeuN+;XlnY5K&XonZkR(g#c-c0+nF6#Mc8}(}KKYQp}=3UKW%HFHXNuGa_=PP_g7ppF(i0{xo!uobmujBk~p;mU9E*ZK^A+K_5BDT`L!x~OfA7RYB^f^g=hj=FQWpccGS?40g-plbEWt<a?d4_l+?F+QC`CoK7M0|nv7IN8m9qpq$?+Eb)+8ddB7wgGnO;P$o-56a)IDntYV@KKN?7nZ~+-)YmjWG`~_eR!th&fNOwhNq_Q>^n8d$xtgPchdO`W|IJl|7sDq~>T2vEnvRuOOezr4lRuxx|WFPra3VHfPbW2GS_o$tk^$_@*u|b-76Wg!otD8?>L0+e5w8&QEdAba|o6J6)a<EAAEXQ^t6~m})$~v6chG8#v|z#5;%;cTAV_<j#}d!DH)*l|D$km3TdCJV@>w?HlBNC8zpuSeHxG`-r!*wtdu>?C@>cO8;SZ?sE2h5Ak8<UQRBRSaJ7s`CXUmy1XX7$1%QU?B9tMcT1Q1y4+<?u9Ck>KZR}Vx9b0&w4X7Djq(4awlSvCm+5oa&c4s%SBWnZAESMY{kzY(eZ}6sB7cL&&XH4nQfox5wYS87aGY<6UlZSEjc>{QNqmp<qOOe%oMW{P=2Fil&fr|B{#%F@ca!s=_>06hS<4gF_Ja5wd#Y+VK>Zu>IgbAz^$y~fjQ0oiCE_W}pGv))_&R%fnR9s6Zmv}C@3MDKiJ$V=UCMnPAF1zg`ir(U!~ygDmOXn%thjLfSiCO79e^WfE15)I;fb`BB<eDScp~j-<g)Q(+GggDAs$P6Eb}QmlKwHo(X>svjMils@gUlvtZRS+_VW?6)3^rIT2TDY-0P#Me<mJHdnEG@W6S}xNAuV);%M4Y%rlAH6xJEd*i#s12*(!0n8S(t&>qa1#}Eh7R>ubN`~mbI$e7`b6U96~6HlVOK$qFNtYS@O_H#1l!^|8(j5C6HgV@(G9P1#~G=@DN!WvBMhq5iYY+x>hSJU1|E*r0*t?*{r3U8vloO%=SGTQ07EY)QZ@p{_pnJ*i!rahDADt{MUYUpAlpT=Vex}@kbmv|-Zg{)EaE>o8!v=v@QTj8~|)2P=Hr_i3sy5=(GY}zS2HkUY!b|&+zA-9=zrZM(r##w6D<Mr(Aa^iI2O|;b-n8n<SSyu+}656vEb2jlj+6$Q{d+eK8M<#3B%(@rRe;M;HB3@2=6Kh;gypi@|#$H0afc8q(l|r0BJArxT5znPPmFFfA&!WAUTsEFhdp={XAYM#+CAn-oowmvqr^^K5d9>#-UpAgaJCf&4AdaQ2uD5Zzgb`1pJ)U)q(q)b=GiWQEN?YM%+OgEh#N%j3vKAG;hc4}P>B9J<cx)W~!iZyO&#~)GEXO^aIGOf%#!zF7XUrtx2-*`_OCs?M+UnR?o*zyeK|P9iJY#2%eFbyRVO=X&>jcJ`&iR-?ypr}r#+bn#r*f>*SXV0hAIJP=_CwiS9kBm(A?`yvkX$wnrmeKv8;24H(jG)E8;8*D>41IHNIj5vAoFG8KD3p80MA#t7jYe3y6e)6*pGHA)>TWF*1CA<(!v4jp|1nhgu?x3_oD7c+?{p+YiY)qwe0NfJl>t>1TbcHKYDSjA;kS?w_*%6u6m5wh1i9*3+)=zK6bbf?MAFI8@H$J!uTqVS_5ibCNXbU=IX&(`Vj}y4q&g1tlLC8g!5-&t}e{ih&6R#?`yCgKh8%D;=b&YACLFtaU*@|u&2uQ)upyB?z%K4R$K#W#kaNNyog)S-<MoNU5e^bQ5R2gtr@SnE;Z?2om_2lRj4Zvm(iuNF2$&wiJK5Bt~s&dT&XKFZ#Gv|7dKr>=+cr{an)!m+>N*z?dHVJ#8o+FgDxJd&p^(DeNngrvEp**l2@19v>Woc(w&Lhu{Ry4+uHG-<UDCNq4p<kPVLWLmDQy@bp<<Yplx8?*;pMbM_rP*KF_Pp-jyd;pLMu$K0V2)Iri42Bj?<kTshheX}2M6!?8EyJgA;`(xoo#PK@Pk$9JOLTbKTJKAmVcrS8r6*<2gy&eZ;PxEk$h?4v(>pw>un2duLa<cf1VB{`;Y<chPdqO8-KoICrh)<bP#cg|%C&au+I#ML<`HQDb9<jSz$mC3u3Q+26zS(SA<lT$tQV0|8(<8mBZJC0rH4#Z^{uOxLb;`+?*MctUVBYRqrJ#Is;8+)(j<A?s9<EZQJ8s@ee`KH9x=-Z84an5^Pj=_!GNB#T{x_r`rvvm1~_!Dh~|DvD5&uM?8ud=_={|j*zZH0f({>tOZ&glTGerV0f@q8igNL!u%nf%|n{7YNm_q4O9-xL3!{ega;h#$~?K;LZqhW0<yZ-}#KKj!&=5kH`<@FUufc-{l{;tjdyjP-_N_{Q;m;W)lgf49T`(*8lM?4R^=O6yX}0dfCg>_@Ca*#-1tMRcj8OJN7>hn1)c5Eo&LO4Ox^OY<CsbJ0IPbzWknors<2r?5txliG>ciSw8}pV{-QVmj!Ohd7s=t@iQU#16DSajsNvaxiXQjz#$uBrZTZ4`URh&S!@U)6UHpg?Vlv_M-@W3sDsQi8>!~KK3gc7pASoq2|zmShKUgvvvn^-ziQU<9A-mPK;ZM`8{;Lp)R#_>8DFCT?P^R(pI{g9d1rr>DG3*CT*pScDO3-_PTV?r7>}D+P#@?5OI6jO?Yl?;>NVA=~6)#7vk!)+p@kc)M{)^sT<f~18oCiXX6UAtFwkC)NL8F0=e46)oC|pzNQ>+ZPr<nv1@ZY?HQ*bV>To9rCpzPHeZ?Z(vZh0v(8#}*n@U^p4XPRK5bv-?!tPSvZk7>yD9w}+x5Ex=c_9D4$R|gSBnd4sLwfYVLdMFje*Bq7{3~Q+p}-Vo~Fw<U8WO9(*BuxBy}XQk`X+va8KGw54OV{X@~1FT$k>|(X^wPZ#r=}Z4=M!LEN3T8h=anMBz5HN3*sV>LI#>>C%pR2=PEWz6b4gjM0Pf!kIIiabtMgM4y)QGjZ&ZjM<aNI}#71J&mzcoL-DMh&YnAszF`5t%--w4yW&E;@-3)88?Qx!kDioYf|<C_I184o&6mgi|6=1{jcl(^H04qYyb5>vio1p{O>>WvOlv>4edXF^wrtlN&Rh==BWRtirufeqWuq)7Yv;'

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
