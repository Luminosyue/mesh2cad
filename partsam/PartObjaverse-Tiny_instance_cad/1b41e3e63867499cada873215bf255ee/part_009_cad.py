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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b41e3e63867499cada873215bf255ee/part_009.stl', 'relative_path': '1b41e3e63867499cada873215bf255ee/part_009.stl', 'source_sha256': 'ece8627c6b4d6c5b584abcafbb2d9ead1f99209125f09f6376c51f13cf645c5a', 'input_faces': 1088, 'input_vertices': 588, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10236421227455139, -0.0744427740573883, 0.3131709396839142], [0.1023692637681961, 0.1823832094669342, 0.4982462227344513]]}
GEOMETRY_BASE85 = 'c$}r33AmM0`~RPPnnN><YAemtNpq=oG*BTDBAhfRjVck9U6ckD86)f@8KOxVM7tcJkRcR0XBR4C^!6geZ{N@QthM)Z@BP27|MmOzUibC=?C-nYb=F?by4QY&`?=n}y^9pB<e7hGc~y=z=^1P5c@n33mApwq$4?wFc<6*?W5!JmdF6ax{#kwC;{F%)9T4&+d3V$wGIYY=@%1}|>z_NUUHvBE`oqSKpE!QdnCr)mA2L+@9)m_r7@G7a3?DRZX!3J|*6rFg3Ab$6Bs?|zzx-D^IfUrkR-3nqKKt4l(b&=V_jF0~!}#H$TlZ!2V}BQ9^}YEggZ_}ME3);UH`w^Pf9vc1Blx=iXs_B!v-Kap(D;dGgZ*1Ss``)Nd$axy_+G=gOXYK7rt$|Z@_pS;wCg(K9|`_l@8dI`^FOO`#y)>%rF;%|3-%u^`_am5{l{DXy)s+>@e`ZYX6xVElJkmuj>Z299+$!rz8~&f7@X%NbzaHVf8N~To6`Hw>)qIlf7;D!)92s%5qx`mwQrBF_U-X?{o8f8U}B*E_;TY%Djq3F_w9Pq?W32!z9L(DyMA<guVdJ(pWK;&_VMbo{p0HuogMIF2j}?5*Hit3x8(cBE3f60Kzq+CzAjt)y!9b}{=Mi`!S-d}-jv=xdTMPmo?FM6`7D1+z)wsve)OZmem~(w-*58!zhe6ie?7dm+ixG9_uZ!Sd5*7X7Vzyn$3AITnC?fIXWc%p(FWg-s`fGFIivraD#pKbdqKcwo)c%k74(}W{CSS4ej?L5ugm7=)tJ29pSR{G_NDvLc2j*n+&vNWcP;Y$yx+D3{KzQ>^Zog?{oj4W^uO2SZ{(tl1p)ufBIY>uT4emGhmGIy$BlkJ^{xx}vDy!8@jq{C81$Fl8TZF?_>29%KlWQQo~6a!_P_5px0>+`|HjPEw#EMOjqYe+{6Sxv?{#dv`MzKE_xtg#KDa4;{dhA?d+Xcv<DFOEKaO6Xgc;A^pSJnmH}r(*r{R~rA71!PU>~r4e8D$?eL(wmAJD$t2NM76G4po&0pE`-nY1U}kB(0S)_G#d4%5$V75w>$AL?S-kKAg$*Ny@HJS1jL_s1Xau+j9N^P%bIrfUB8jknxj=DCRR^HxU8_bSshkQdSa_9{&GBgbAgd9g0&$N3%ce*fAZr&l6k#<OUm`Cip~7N+~Lz2(jRQ|CaSecqv+{(AG4d=~Jd9~Cp}t?#O!-}k7$-V#eE2mIK&>1JIW`pq0iuZtOH+lT#i7;W9HAl=W)FKyP_yC3aI_rql`4y;4(M5n-h5~)@;;M;ve`*wfOexgQ^=lyl7{Al(5>$3W*8g9<!$DS|ie_v1e;nM%{*K=&ltNYXacz%!V+1kh7-VoSNT>oFcX7a1gfq<VF`=Regi{=OXc(vd2v-O`Cx6aSs$ngrsKX$HZ|JW@ik8Z0N@DsCNHtV@$zy0Zcc>8(&afxotHT%H+_P+1Un`HL4u5-<Pvb(K0zVk}0OV3~Hd-yhgwQuuR`!;{W@3b+;Wo$9u&+BJ?r>q|vWBmBqAI-kEt+g4?Jzx9ZH-5kQ9q~4|GV5oy@gtYE^!tg=x_M)IK1L>8UKsGnyKtMI3etU>N0G&a0pI44-Ors*9_3v-!{kMDobM+Vo8uC>x^H2+Z})*{tIGp^Y-d?>o;mpYKtDF`!oT(j_%=^tU;n#5(Eh>W{<@7n`-br+k2UREOfl<i<bB2;KgNuI$sx0k^=RRbCvnqg(|)cwUXcOE3ex?&POtj?#D-nz_mdbr%JlPcnZP=+ei+}b6Ybk|qW$;>Cj)+z^^@2=G0=bBGl$K3U_DzuzI2lBC!Q!9@a_JS_fP47Z}%VV+x<uTiFPIY{U@T^w;ix9n;+fP)a*aX4|l8(&*sPXUAR4~|L<1ckB>VMn4fs{{J=ir#<^l|V4rb*^FQ;m^`BR6quFQnmI?mdS(O6&yc>V0kJ(RNXd0Z){#W^a;%T%0C!RcgeIOqPj4Dj`!!|D}2Ys6t@$NYR-~Db@Ef(-?{)VUgUXbqF{0--R81%{CNaV4AZ}ZOEGbG^Kyo>IrZ2U(m`F<j1)?4(i8w=BYn~$+MpP78Quj2ajd`#?IVf;B2%y^cuo|j)>`k7IFeR@8|)|3qRHXpsMqfI||lv|%QAMrEt(YDw5g`bgM_!;?ypOIhq8Tn<~>-@sc$S>Po=a(J7&M*6Yb$;3L>-@4l`4wGzA}~K0`DMpReuaDF2YsDic0P4}+5UBY+41ZAvh%6(EBaWK)#>XnJbGSXx^MF?v2$U-w|N(y6ZCD~MK{z9_Cwyq=QarVHt!NYRSWnw?-EP@QxNdUJ8$jl0pI3by!-5+Pu@k^bqxA8zc!ul*MIbZ%B$1!D{|{j<Ig;Ob$Wh9E*n{x?kD2p(SZe~{j^G}v*nTXbslNo-KVnssQj|N%WJNSt*`UW`a17iKPvC6uk+5eS9xcBop-Li$~*VHRNlFHP<iLZukz0M<Xz<WiNL(+ymRAJdFOnUcWypa-nsr&-nsFsymRxZ@-DJu{$jr$@-8y`y~1=qM&5ZlJ`DIa?;>{x{U~`CTRSY^Cv4u$91-ws-o+aY4E96b#S2;meS6*a^FIZF@!RXW8Se&tn|Iu&a=ty!e5HdqKab8a-)p_eyI8~0#vd|saeCfGi@sQx?%TYJOxtCyJ1&^MI9uLXU+10n-F1iZqm};+_&Oi0@A8rPx4zCt>+5`U{iuAjzRpM2Uge|pbw0ZGDj(hVQu*lSLFJ<xzsg7F+uy-We+K4F=c5~^%17s`e01}v^3nCL^3jc7<)fQVm5=djn!MFH%lfgtUO(Em>qq-`{kZ<s`mw&dZhH3C!gOD+AJ-3g5&m~epuJvK&S#&AJyQ^9uh*ON*?+>_z7Dk4>(G5)_NBa>V0*nj-T3YKdG6#ud%IsHicAUmYCXGt?ER}7#{~bbTIa6)-r{C|8`v|@-kn#BE+6z&Uby*W-%GslWkFybRKB?O_WXa%f<Sw>AD(kj&{z58`e&bv9;_Z{Z}-F4y07*J`ce7le3g%`AC-^JSNZ7Hr^-jyzsg59ewB}IUFqw-$7d|=k|iIluk*{b*ViNXdVjWl#&rsQ#&wGAM_;GlXI!V)_WC*nKjS*Zw%6Aw_Iv5;6gv<4I>nA(U#D1Ktq14p>l8aqeVt-`eVt<GQ(vdp{`GZ=9lyR#vGb|d!-iRA9@P1O_4WBc<deCke|27wcXWXnk2>$NzCQ1=zCQ1=zCQ1=zCQ1=zCQ1A{iyRU=d1HBH-2^A<$QJC<$QJCmG?=d)!FjP`6`dBudh3-uk*<II*(jGDvzwM^T@SVd1QT^N3OlfBlo>j9$8=KksH6tBlmaJb)Rdmu1B1&^2_z3^2_-uzuY{l{Br%P{Bqw*<(Hdhm0x*ZoW43ezwC8x<iHtbKGk(`<Va;RPIceF`uh4ha<q!^)%^tP>-!1T*Y^`#Kk9yh_4WM(>+Aao&R6#nT>t8Rg7ek=g!qT$)@REj=j-!5e0^We`WfeY_!;MQwjX`|hM#esX4~uYG5n14E8AY5N7?VC&x`Og&VTIq_4$nT)qOMP>+=&kPJMo2eSLmn=To1b*#7nTi5<T_Ke6+vuNOWqzdk)*?0r}3>-($mZ!4}(&m(*PHvVI!_33$J?*m(3-}kn@zVB^)ec#*lqwafKU*Gq(zP|76e0AU3^{?)GyYZ;|-mbm6za85+YGbxMvcA6l(!Ra^(!PBj<oZ|nXnp<M%KADVt*`UZ^`r99`Z^z7dzFvY*ZJt$t9*3dOXZ`R2bGU*{3;)vubvY*U*)44r+QB0e3g%GK2<)t{#8D@@vD4v^QrPNwso|b2lZUi`uh1}?ESGD)AP|j-;C`UXU4Cd!&+ZI7q-5BK5KpbeAe}&o+DddKS#E{eva&X^&Hvtub%(9@u=s&uDyExn<&xBuMgAD#}lWwF?D<D`MdQqp0l6X*7&L(!1}r#K>MzqNBOoM!20^Rzt^}u?Su6RUgTWg&!~Us*~#}a>NoH+>LRSK>oKga>n?2ns*b|DxU(6*u5ZE5sBf|Db$ttdMtuu@MtzI*b$yHNU)Q(bXVkG+U)QnNesmp+ZLjN9@H6Uv`gbwkOV>5wXVfF%XVe|xXVfX-XVfDNjF|SiZVEr6{t7>%o(eyso@#Jc(~qwE!q;_Q@!1=Uuj<F*3pbj-tLn|7@vUawRDD|P*B$2Xs(Q9~zfVm+sxHp@8Fg`!zA(p2)#+JZ*Xe2B)o&=@)#=3&X8u)uVB+P2roE~&w7#x0w7#xaOl<ka^rPw<t*`4Ly<LaQcvM}b_wivfZ>kQ{`nulI+jqpYS9Pt{*Y&H;SM{r|A5|~vd{r-MeO-_0CB6&nKenFM`nq1%`nq1%^`q)?T|cVM*7c+6Y^@*u;Z%QLiYh-b^5oWRe!NGk?b&=?uWNl>uj|I6>T<oq-<y6^opaux+MCnYp{<v;zOI+f8(zokvxy)5_3SMfzCYd1yLq_Zf0*CXyv2=tKcgNVKcgOA`K}&b`K}&5)_8OJad-9V_!;%^_!;%^_!;%^*4Op$_!;%^_V4O?csovA4{yh#>)~zxx*i@sqaGeVQtOEM9r>wVupd<?@5b}*e19K^J$!tB!0-5?zdjT5)%UG5)trZqUKVKY{rvN`^!4d{&O_|`6wY5*e0#S3BTtkx{>XTseI$2Pe%A5a6E^Fu#RtA0DQsnqmwJE4`uhDH?c4RHeY@VAuioFWzJ7m4`?`Pq{*D{JdVk0I`u!d4M^*p&{T=J;_jjDH-rsTKQSa}#_Uio|_jlF%JFXw~{*D{JdVk0H>ir$}ch&nl?zpJ;cicRy_jg=B^}aLLJ%9Zf?B~i~HfHN5np<vDwtn<`K+Z3|(A<B!HQ0Ziy{=LHCz@>DlCA%6&vX5J%v1eGA2Io8?>o8g)pkZaTmRmchm7AS9_)Y2yW6t$?_G0KzVrJA-tOBJ?d3&VdVZAhDtW^OrM=oGru?&-{nfq^t^U7W?Q4<ye|@*Fw7g*`&*z2_!XwZNVbM<T2>2?r5quSVB_TWnZ3Bz8hKIm|3E>;iR`3n*aI_0N9KH$d1&f{s-vs9o!u`>6;r{RyXh&GI1AGO1IU(E+Z4dW@FH1(>Wb{tP&4lncLihqgxGUNh7QG1W3O7M7hMU062;p4xQaBfGfnEZ)fZL&$!Iv@qc7*WRXg&CBxExvuE(e!KPlrX%fXl-b2;quoWw;_-7p)JAwuI}#=b+cZ=fDG#F*_MICSwjd0G<QSMX!eE!t>B;;Cb-9=s@^hcs_b9JRe?wUI#CL7oyk03*r0FL9pmh_&)eSLiizc82k|Y2s#25y$XH=eiXeDeiVL~5Pkq10zUvRLI=a5H^7VF`w8Lc=x}&CJPo}G7R`gF!BYw0DQJIq3Va881uS|wd<T3hAv_7~2Ty`;K`(=EfhVGuz!Txy(M#dm;mPR5@ML%bdJ!zz7oGs$hTaU{2H!~tN6~R`6rP!kyOMEtGDf2_;nDCIbQ~;t0XzooK?pZQyTYPP;D+#-gm5ji87!I$*MiSNTfk?*wb6F4=-IGnIk+}_Dj|FtS{^<PE`wHp%fMyPif~!D4q6u$JqNA>hY8{4=s;NX8n`*!6ula53O7avz>VPudLtZx`w+t8(b=%*J@9yVEIJDw3y(x+z$4*N=v}brXm}Ld9UTLU_JF&?)zOBq=$UYJxCmMcE&`W8&w@+9r=YcA(Np15;L_-6uxJ^$G+c@hE{T?f%W{lMqG7lsToY{$H|JQ^B!p|Ajp4=|zZ!&a1GEp^0Pcy7hsSfwdJ@9tqa)$-;cn<CcofH@8zEc`tqxa%bI>Ai5#~LI5H60M0-wU17AJ&@p{3wb%v~`;xF}i^uF1R<C4@b+ftUIxTm|h3_vHImA%v@<-QaF~&#Gt+Ton$X#o^+NHG~$0i!zQ7S_S@(eCH&b5;EExek&Q@CL>M=?@LCn<R9yujPB@#u;>MFceoqc6Yd6|PYBl{gwIOGsc3DqC)|_1Y7@eB&<o)@a9y-FTo<mNjMLD1Xm41w7hDfMn-C5Y!adOLa1XdEAsj)w!QJ@I5kj~NS_|$1pP7vRhKwFZYr(ac7hwtE-$EvYe-5SQQCLFwP{@SvuOSn{#c5j`uFX6aCxlC&b>R~5-yx&*VF}?<X>(nQ5dKf{zdsx@dJGl+7@vhp(zYI4k7H1h5H3at7e&KxQMgDla?qM+7!GsHY7)Zdp<Utg;Ld0S?hJQAyTF~`a|z)Z=$WuRt~K~9{8us(=mGS<@B#P>LikJcIDDLA|0N;(75X#$75ok%yaPQ1A7V}HAcWsVWgWcBXW>uL60n5uXCV{9J5gB^J6Rj0@OQ%dLnegxqOvCT62k9=QtReD^cegeybG1}v5U{bpQFWK3E@3xQCLFw6SN2{A^dSDwVs3}gg;8^hasaOK8qhBgsY=9;hL<i>V$Adv@_fh?m!5)M?1ltSZD1C;dW>ZxE)*#m9<rk&%%GEt-n9fLikVk1X=)}fd4?hhW~(nCxrh&55oVzzo7eI(Qn~j;P244;P2r4WGqg`o5^^L5PlrZhx2LwI3fH58i${NR};eP(0%Ya_!aaZe30+<3L(56Er8d<ucC$UtMCRi0dIgeq6grO@Fw&NcoV#t5Pl8)5*GamehuD&z5{Q8UnhjuqB~&Gcj2}08uU|m4g4G-{5<*@EV>hZ9)1Dc55EAvL<p}!_rj~-m(llN(OvM%@JjS^cqRNIA-n?J1B-qFuYjLLKZc)$m!luS%i(82sXgKuLU>s+o=Qe68E+H9@1slM_u&uFr{NFa-RLrS8U61jgyrN=RQ4l#LM(g+AzT%$4p(Ons!9mAMLWQ4;WlV{xDDJIZ3nl8TM@!l&}y)#>^oJ^6R?DEW%LhNLilv_cUbfvSVFjBjtSvY&|hHD?_dexpYZbGpWq+SH{l=Q?dW1y^ig;_ybWCfZ-cj@Pr_T_H_)fxr&ud*5W?RO!bj2f;iK?L^aJ=L{4cs2-pzXXm(RkLSTkq9mEc^oDqNK{k&Cv0bKw?*@HuE}xHW6y974DyS_Q7c@oq^7H%Cv0o5PLKig07NJbDT&D#x`v`XekMTrS6i@DKd=+u`jTzaI$U@6oOB_wW()4fqX?*%3mxbdJ%Zu!L|0^dx+eV^e|SB*&uyA>0Jbg`2=l(H3wE=DH~%+zf3Aw`5M65yFko#&Bcis}WibZUmP_Wsb_C-@_8ZWzZw=5$2!_A>07109W9<H6Vl=qD|qZjJqM)2yVpRZitqFk0qD-`^oqfeGe`bGFmcZLiiU#co+H}ybFE~eI9-eo<RuTMF`9N&Wf^cCF5()gzz_LWmrP^TeJ!+A$$m}21^JZMr*(l!bi|EVF}^y&|0vB@b{hx;UCbmVA0yJgz%5(*|3E0Po4?kqi9`Nv>q%W>=D8tv_2eybI=BG4qOav3>Sk-piSWtaB;K=EZPVz4i`lm!bRaCgz&$f(K@hb7?u$J2dxQ92%ki&!xF-Oqg7!E;lDf+!hfP?z!JhI&`Pj`@E>Re_;=4}IX;Uo+!AetR)8zeXDdRuHF^fz8g7GDh1<Yw3E_5Vb+{ee9<2$thdZEQxC7h~tpnHLxO60hyAZ+=v=JPE&qJHQO;{i25yI!Ajp6g*u4n_eE8H2a4|j$;q4nTS@VSI=ceE}ndN$l0?m-A&iq?iNh5Mps!J@U`zVIc4@Wtqv@Wt>&Xbt!xxDQ$l?gRHmtH8bCUT9^w7knXlI(#8~0a_8h0PaZ$mnVb|vd7BadXNx)oe+M55Z;P@18;@n=(q5<?6Yw~cpG{c-Ue?cgx^Guz(?3;-z0?d(eL4W_$@+s2l@m21N-a_Lila;C-`mn9rP&t4!n~P{sNW#_X|D?e~E@*(HvMp_$$wZa3NX@7A*lw2p>R;!xF*?v?wegT;Q1y-j5c6C4~2(vgZnm{sZrW_o64^z3}Jg-|*+~XXsz>XYi-!pYW&f9`ppf2mXW*{uuoOwtMl%gz!hn_z?XK{T==dE)y~;d$h3KyUP&5=Om*)dIj1Nz5>1yZ3T<AhOdOLB7_H^ZQud$)o5GzYWNzo9efQu5N!_+gs(+Az}Ldpp&en-F7S2mU^D^`hKCTs!_f2KVepOU`S6YKP_!#7+8G`S-#`ctLOa2t=fZ>FJhVHU2VYMJk3f6CBjAzfrSM32BH9-gy#$^JPauTHqZh;D;hWKmV9`GC&G0xvcr4l*9t)2_d%>a?!eijk=mqd-coZRg6WS9Vj&?(P!lLEjZg5#b_-D_k{2mC4z7GEkze@-&Cxo9y-+-Tn7Zbvdp<Cg{;K$K8EV>PT9A1KMhnK)lpl`xYz)upwPoep+=v(kpa17l6$Ka*t+wf9&8Tt;q41NaP2|oj`K)--j!0XX3;q~yV=vVNo@CHJ7Gg=6X9)LH)ThIi&1%8bX-h>vwo8XP;et0AN3c3$|1zv~lg+)Jy*THMi&)~K28uU|m4ZIrN1Fwcxp`XC3;Fk&Em(Y)4(U0Jl;FVtLw`3(D{30Rz0wMeX`WyTKd>obEmE(LCK9vy8MbCkA;eMgi?@&KNcoHFe8zDRyy#k&L-;Q1hi(Uoa4&OltPeBL3Q{buS)$mk!8hQ;p4Zaf{2;T`u(Q9GR>)<Fn9UTl$hi9Tg;F<6&bQnAfo=phPL2rcT!1tg-VbL4ld*HhX;k(d5@Lli>G!LEu&qJ?==fU@)Bj9`CN6?Y*Bk;rMMEGI&A#?)#5d0uI9u~bBeh_|u5MG3igBQW~qhsOw;rq}ru;^&`K6oKI3SI~=AcW_mH^KAaxuMkW)?7mPRzmo4v>SXm+=3834J`|c%J0@`d=~yMA-o%X7v2p&i!O&}qEU3Ym#Wzlz7u`gOV#)Z--a&sQgwjB6VS)JRNbKPWb|<_RdXnOJG#V6)hG&2M4#|dHI2fzpig?K8c5+u=u=**W>WZ8H0GshEQRktmwKr>OyMc$GA~ubDLfT@#!J<F3Qt2<c&WNj;pv3%{pfmF^i?lagDSiT-QcC_RE2F_tMJ3<W>|EKm#T>seiVJpOV!N^+uB;;htN%4sxDXfL3E>+s^b;D4}HZ;)%prAMAyNhYrRy>u<!zOjhCu17M_o;_EI&;!uO)9yi^Ud@I3ToFIDp_Z0n+h=b$gaqAR^rO||fB^hJ0!d=DW!3w;5e1>5_&!q1@}c&U58!n@GpUg}=4@Gq$RUfO%h!uFoCa5FR)ZU$e5_Jc2jZ$T%)x4@4Q!b{NG;3e>rgz!`7WcVpKhTaZ~-T}wprG)U)=oI*Aco{ksUIssdP79@;p9(KW?+m4$w+cUtMq$zEq13Zl;T7o2Q0m#P@QdiIQ0lp`@Je)cDD~`E*gjttUWLvHrJhX-zl7cci{2edJ=Yet&%1@6NAC)yo{tMZht7aS=Y>+w*@flVd*9xnoJvLhU;o!!sedvrUf}<zOaCu}ul=O|FAI`=xtD<Y_AVy%hF(tcKT^=WSSmQZ{{bs@4{8'

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
