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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/29e480b958df44a2ac3a4ed12b7ee1a0/part_004.stl', 'relative_path': '29e480b958df44a2ac3a4ed12b7ee1a0/part_004.stl', 'source_sha256': 'bcd6d81709edef6edc3fbf486dd98ea43de654b876b13969e1dd05b991dfa218', 'input_faces': 712, 'input_vertices': 440, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03643154725432396, -0.0687737762928009, 0.0057659633457660675], [0.12011275440454483, 0.3030070960521698, 0.15246155858039856]]}
GEOMETRY_BASE85 = 'c$}r22Xsx@-}lc=l;|SS+tq6j!RW3b22r9D!bPH&kmwP|s4?1T(OtchM6Wr@=>F<pnBihZ8DsQ5!;|0d`}L4_z3*D@dLC<i*Y|UO*>|6Pb~}6TbC=*C&s4q!{uMGhm!I*sRmw0#84X`!X!zi$-rd6^%MFMaVKcI7T>gFb+0EKC4enqwh8m+vgoQ_TA6%lky+q9(RZEn$m*_EYaMa+g1G)?x92PF|23`9_h9}1(dv%QnPySr8Ql$!I?E$6A+DF^}hyT(i7r|X(?TRERQkj}3>d0ru!6b2`!(_z!Z9glYogIEVsPUT9mq^^PG{<52Z2sKM5_g2WUo3HZQ`-gkY(L<q>Fw#0=1AO3iru66q`jbVSNeRjHU4baeoc3-ndW1Jdm`Ss=x&Wq9llT8D){>}jSoJsQ_K16Fa5juy>p7hU2j@n)XxtN9Z>(UEmq5UY4|ZMUsjaUw4P7U_|a;o^>f+`i2qw+oZfF}_Cs2Zem|i+)s64<x^=7V(9fsR@6z;_Vk0#kQdjTGF>*Wd*-*E?=2OykPUEkpqCVfbx@-FQPRM6tN5o&23eouFk=yk1td014kIMBl-XPz0&3DBntta!$?QZHb^J#kbymfokk0cF8eH=;9@3%jw-?PdZBQ+jgAW`F=e6_sh-~D6Mr{C7k)`2!!e%G9wW7P|0xTHRLn%1ZBWcl~ne%Ai;8c(RA<#$)jJyG+?+fqL}2Zf?P{IPYC#_wN`S8uUP>&=m2;be8s8b>wX*WQ}m9(6rd(`7rX?Q2H%K>hrd=Lh{<FIe-jpRA(y<#?21y2guj)cSH?X@YXrIyOW9UaPY9XCr<c%6YN%kD9)!AL_I8PVHC5ib#zcbBk@&@2y{h>-Wn&M}4bX>)q*7QS))ssET;ucUqtJ!0uZAj#Eh*H;Sa+qMxfh(Drc*95qkt_u&BTZ|-lKpgi-(YTW3bezX2P?ycU3<7}Zg^wYhXuQ6@}?#n$-<5u4RI_@0f?&>&l&M!J&)31)!c6Y?)Kzr8Tw?N}-j$<4J<<a{v7EN5J?bl>D#_1?8v|Ihoi}deni)_?<BFr7Q@6j4}Bs@SnRp_tfabEfZ@jXv|((g4`uH~_Ye?&f|#vz|Y8&D5N%P-dQ)biAJbm#hjaddMG;+~hZ-i^xl^uAqB<Cbc?>%X|q#8O&*cZ2TBG~KSvsJCUc(62r{)wttbKJ8b|6QNp8>qB~%<`cUS<Do#J){pUBO^qAVDy-M|B43QV)?pgA1|HOT&-jlo>gUr*<a4|#%Hf$>`;WcQD;MtXw)Qvc{XoonV@oZ^{cO~Fu>X^Y`wMQUad(prI=-yS6Hv}Uks7!5MQHn4xvS}QtP5+A&+)(3sYmwJ`ZRZ(Tn=BX{m|OJ0qtCQ(F%?Ggz9~|_CHZ~U*EO@<MOf2hxSL!F;Dtg8aMLq)_QQw^G7*1Ttxcu*R<W;S^e~Woh#lTeR%e@`uCEnv|jD6JXdOdIbWq{Ut`-%ja$P?pr5>HfO%}A=PLcYzNC&j=e7|@pAf8Zv(k2q!?@Jw&sirRestnNjH?Qm_m(e2K4<4?dE99?XgivJJk_`rJNk&0FI`J5zqvijYV^<ToAkQFKI(NGSE_5=5#+Dq)Umud+A+En()*QMqh3Fk*1tV=l*Y|86ZHNKk3M)Fh2BT{VjJ}O&IOpiomugHv*HrWJ2yIF9`4uy`Ih(Fpr4DIS{{2uC!{~W4f9N@w^~2$1>H1mg*H2>?NvBX+tGcsuf`pvZsGYguAkPA{rNtmKhsj5M=qat7^iWUaorEuwY=6pS<wFrWkI{HnsFTcHyHgemA}T#ZpC$;an_%q<#D#Fg?bOXq4S9&_6^#nMi-=S>4$#!`_bL#&xbT_oqC}C!EvO&)`!FEDdL;(oOYdFjrBtIT<G^f-{9|WUuZe)`zjz_tcLa<`}?A(pV;OaH)9IuXZxVmdR=#;-AF&Wy!Kx!EP7jt_?+(Ory=XLz8#mIYuwt?MCTKG`30!YUA{U_jF6!iACJ1C{|A)NxS6%Rmd|zl8RoZ6euy`!fqCrb%z9t;fh&+t&=$-Oi*{+dyQ<tnJgzYMd$Ts^&-3!2fB4PDIw5Wm=DnH$h^I-1b~?O3@7Hm*p~kJpXR%H@brbFIx|zluyWgBq-&z~(_1#&-%QVvd@BF=n_A7huw;DH6dFedo4p@Z#zdse`_ww=D53NhBasABR8aHws)A`sw)Ixm@wQJnGmQCx?dAbJ1%d+A~-}JS%uk&Fo%s-{NYTU94>%8i!V`Bbk*%RsW)Wp2Fbj9|s<Cgze^#6yAF>j3OkL!+`qW#v24nn(hnSp#lE@58x%&Fxx%i48bFyHv1--Nxuyi_bu<BnhF>HO)+wh#T`Wp|Am8A7zZTp>HPy)3Vu8n-&M)&6Wbui}17&qDgv?e#fn8i!Fo`_>{p@mGBw8W*o=JzFQvAwD)<*A<q{K>2%Q(&wMi68Tu>Q@uZXxfYwz567UtdBtGdnW1=I9x15f&Th-3<+l#@K>8wQF|JZ4Vch&X5c%gjh36rkkFJ2F8h5(=bRB3opW!-3w;}zO>R6`)y})xR=A6de!@}^qYqv@Jm1EdTq;EDy*Fnx>m$m$+>pkLLr?4(a(=TPbe--riiF`hsYpV5Pj&h*?wW+oH>$oH4!V!#T6VJgQr^bz6yXrc~7}y-^f|?r;_ZX?`LD#qUG0)A|iTr<Unqu6U_A^Ld`=*xPT#yCp?&7(1J~Fz*;dwHnt(Mc;Sx)0t&P7<iMfsqAro;SY6kV;?bsRVmpCX=^b+*RGhT!@aVl-}=doZ5w=SKUc-Hi0-J+bbdwgveF?!>zG#zP(N?!5kZ?uYC_Jnc*!??zIK{VC#!P5+}lsIs=N+4DB8>%9)o_dKy$53ai}a9?)=PH8;t57@8OPowD^W%}!Qw1*tgavJB-YTP(cQp;(LDTQ(OHWT8dGwOQQ8om+bPb`JF*Kw@ZvR}kHc~m9DI|a_ta`gAc_1b@nc)#CupW*tD5BHO?G4d;L68nPPm$d(zlRII5GVz_Zle1tJtfOx9VmV`ns<)qo{xq_`#+@f@y5Dp?O@n>G>oH948l;~up2qdeu_#wpe>~U5&&2%PXe!b#*^7DW(;&>}yS5^I#vc0owZ;WtAJBIf(py`xKe&_*&+D@HQT}v3+K=563!p#5yg>S1<woo0_YHL(ad)(#pBjHo(el`iV_wLTj{UbG`dj8%XxA;7FmIkLgn4h>Hmsko`Cwe0Sb_e;dB$bS!~D~hMLP|{JX^+&c>Qqf=N8`8{_HFgh`9GP9WU<B>-jZ(aoweVVm+VG2K(&52wZnR%H^zEU9amr^nJqD^=~yDi+Q#FdZdrrj(x=+KOlV<3+b(O-8EhHjQZSlJpCEh-IA#DhHFV~jI)tfd0(}3e{A;h(ED=!`!C{e6Q=6t_5CrQF808Fd+e`x{(NYId8uz9jXNWvb^f&2f1Cw54y?_Xe@E{?`m!xBkNSll#&rzT!<bOq-~22%pQ#b1<JVE38`9?~s^ixhPz&?z)?tWOdyI3BN1L$jY8H)ho_V%JKcBvU`D(`x$p5eEx^6VOH^4d}|00z0`#9}yuKMrL-x@4OJ_QY3SGso$LirbLM%=X|G)cZ+tM%%y<BklQblxyVcxrjvhq2x@1_#X4blyH#|CBz0ctnl}{a#EG)}4hP;J(71;yK$TE86SI6XZW4T-PVgDpA;{KYEUQdMz}QG=4?beXb!d5&!3wo^u%aFX(f|Ui%Z`RmVqZIi~HybGfAl_F-v;qaT)NjqCbU#D4d2MV)6HO;cn1{)f+x%)YvAu}|PU@GuN<$Eg8YKf{}$+>?7FK4B4_|DpTvyqG>3`PWFL^Mm~&p93pRl&8)`oUhp(=qJ1OBcI9Bhv@xQ_R#A)+a5yvj$PLe?tw)xpN~0?xKX8mq&M=s#l9}<Z-_e+^&HN4Tv6lhg*Q<jA5QAJ!u87>tlNvZk-kki>|<sX#(JaKJ;Z}?4rhIL3iIUDCy4(Yh4YO3V^KdlUm<?&-C(_*Z8O%1FF)dbPaZ=*E<O$Q)3hM=V^jN2)cajEQqK{r&8-lxR1xO~`9iS{J=_-0|6@^@Xa0^uK26#qeFYQG<=xNm`D7n>S$~~Bt%E+8_o4^mT*<W!<DuhA%#&%Okbe3goX2cFjPt4vCd+wJ=UemM1FUBTj6=L)^h_=P-qv{TjGKsfL?F)j`kX|)tWH3D(=420ZK;NOE^!TUvtDCOf3+g!)x=+TUuF78{`P7y=x<N&ARhc%KW*Qb0Iet2$lno<3fA#rCQR1$F;d^d{Z5#HbE3k7aNXUHaXz>4h0a&bt;bQHjXd$ZGGEo!c)gD+Q^XGsK)yrL;5pnm4dPih_1DieW}-eL`P>_yFiz|7SP=Hhra$6;ru$LLS;3|2M|;64h<BQ#=g<z0YpYme#M=i=lDPZPX{>+agAflJr~T6?>aFA3-Mtm&q0i^2sc`<|nAQR5-+nt@^O;r=>zoxl=Z#6!>l#~2VH}<AhIq@3+FsVnQ+N&@h(z3Lf}Uq5Z#?uo(V7s0xIL<!j+d-WP|mI6u?||&73-@P`LQ2yEJXUr3#0XOuM3zT|47{Nbw9CqzyBSti~Wt2eH+e6swN@6e@2}4!^DO-Cn<d%@xtEoHQwwI#(%3Th^HB<{np(lE!GduuOmLEvW~;g`!%cZE5u9sY5qp7H#$!^zri`EVa0dU{70=s{X0K0{TV&ickz7HHN=Mf;*US0Ki#Q^^SMtRh__E1q5XVu!rZUpX2Nznck|3cz2(ir^SS2Qj?Qw=^?7dJTL5uqTyO1Hfx~oMxUGta|K(+Bex60KKZ>f3_|z=APIJ8;gZCT1HbUGttG-t;r@qAa%@~IG?){@QeQXh&({AjAc<D9Tf7}VHv5tt0MEuOBvD%;O)yI1L-zdbR3u^vG%OzTGu7qgZ@8VUOuj_tstk0iJK>8->G#@MJKGwsjViEuQ>|Ct}k3!hT@1BYHoe|pZ#`Ij;uUzIL#Jd@@v^*X&aSong3F3o0Yx|nphidy68<ry;k)x-k&ypAOMRDxsjEZ;X>2(XI#W~6KeTX0R#(r(x5cGq-Sf?0o2Tj#{BD?5%-(Bq~;+-(At<HbwJmEO{4Do7r*J}D!VF@YXPb1I|U*H_VzS9Hy{>!ED-pTB#>pDl9wAlaM8HM>M-*K%^*DWukfByS&O&`A(`L6RpJQ($CUp^N5vk06|C2w4R(DYpoXnne?mO}j22Q8;Nt*_4i_G^BKS9m;J@9Sz=-FMn|)IfYzVQqK&N$dk1FY05yuWjo3%^GnP?-9HjYTPP&QP+pYRUeJJ_BBU74>IX~%3R(R^GlH~$ftTnP4C<_6z@a2_CoseskA@10;jJ0I__$oOV_vVnOKjQwTI%mS90lk)v@$3`r(OTSnp0efcHx7SRI$H-$o+;0<*Oq%$wD)zv(ay@tS+IzZq4Y;(TquOyr+Gi|%usJTJ0JZbJGy{+qSk!(z1^?c1=<Hj1Cu@>^c-<G+qu!@YE!Y(H8F^Zd+xNdNTs81*g}@m#Eb1o4mKbi7y>-{D-R@m0iqhv7MrY3Z=9<JP{Hx-K<#WyHDG$D2s+Jptvslc?v9_QZQB`h&giOnrX2cE3mb%nH4(d9MuC-R(XhKKw_04mz_LI^Vlrd*ZqDV#p@VztDcnt8=}uP7nEjb;((rqd1Z>Bc2ec_2Rl6jd|&^H}bhwQ^%>f{?`>L;;XW2KX<MDq~p<gfO9m*-XppmcCJW=^Y6$UNPlLN_J8NSAl+A4lW?A4I6ZZ~b?_X_?2Ge4Bf5=V*D`ZrzwoLi;w`e_-1>QUoQDTAK-}@|Xib0gD$a-QH${ByHXWy~Wp3;T{|V;#L>bJV#Z8<ydE@-pm{<+xY>i&yeNC};i2Kgd{etW4UAz~o9)kGzC;A+*8fMn}a(jfM9;)=yb-QC?8I*taNTk1BQ`^@WIUMVm0?~-OS89K7J}-=Y(|6w^zW=q>n`Mi|esbY-#QRN(*YbM=<9$w!<%mb+!uls$CEe%QW8x9Ncn;|+H`Mb>xBqU$v)|vU{Vfa50n7&b5N~&Eqr}~OuVEEAiTmntSJ(g64|rei+I|!1<KIu#^1u9Uyymm!3F7%vuhaT3KUn*@yTUWX?P+!W;27o5dC0!+IpUW?wVY<;7WB7)?-3ttTcG(5I*;>?CSI7A&vn_N`S3aAd|L_Y&>jw5=bJM>qMUd7ApPUhsONy3I*&Ofk3)QDeLSxd8e-mPw*vXJT&U|?`=HY}H@m$O>F?x3JKoBKahPEP;u+^^y*V=;!@RL!3*P^XZ<L_*kg5jWZyZcOe9}_AU-#o9IB&hQ9r64&O>g|;i*wn~oyh;mKYG7r`Z9?r;zxeee(r1$g714DgqK{T`B<&IwLYD%ZXx~6oI1W-S$m*<3f#l~vPou~_wpRT8SoJGuzCjGD?OZy{(tc?&RM6lLHe3i@xJ@R3+zYZ9_e$$b@Ok`GZSB7zj)@BrgwIGi1W0gACdoKADly8?}c^UH5>NRhx2RyF{X6D`<~?)vH$RVg>$y>%Lh`#r`YwmV`sY?eR3k7T%)7)eqTPr`Y3-vq_0{W&ym`D@ErN87S>1WF5o$F^FWHYH8Z<DFRYL_%;&B^<nPL_>kp^T36!T!W5jolL4U5%e0hra!zk=;+dM|Uy4eiZJzNgwEj8Zb9OFd`q|f^!+I{1JgcR|7i?OeN6OZ$sS#1&D|0nu6_alzO5y*e-I-KvU&Ybjh+%fVt-tW9yg!kR8CL*8ak1!8Z-->nk-nobe6~TP+E>zbo?zc-3zu<*_?lTha%?_<c{HJO<UW||@J5t1}1nRgp>P<lZ`FRuKuMTPcj$hWSO%V^9rt36U_W@}CKer-&y)fqac)aIweo91pJs+dbBXjR*v}2FMsE6y(*#E@)A)iq{A)lI^R%^XYyMumf-9g;3O7nNe<M&Ed_y@%Iby%t6E9W!R=L{RJli^Rif9LNRT)A=XWqeyqe^+IVK8WAXluLtn*N1rSKM274Xgi*JhLh{<j(Fc?O~Sg~un*AjYb^IhIZ{<a{QQ*&EoZ;-cprE_1m($HMdxjI#lu+FRqu)Zo360F&vorTujRLn_Ch{KXY09#bI=a_PN6&A-x|AbjM0ARF$~}TFc0xdc<*8Foe$?N3(=2^ca!j*{C*dtujWGh?Py(JxqJ9y-}HDb;#cnK`GDP-ALGI+3FY590`GV7ti*GF*#o3sG-89+&!J-Y9Z?;uH|?b_=se?i-Ad#3kW^ULbe^Q`YyS|3-?_Z=LVcWw!#VA+MyUTsxiJr2Z-;#9M_~QzYe&B@_v8KJ$>W;dU8^|m<3k!vZ_Yk|>qVD`8+}|_&iuo%kI!2P`BV+S@5gGELAp$V{5?ozoe#|udvTvZ%}^gVp5l4T-+{P%Iv{<kGCJ>>e?=nwD9oeD3tsH+{tCi#Y|kL1ADJ4zV=I^oeh0tLv&wntd}yt0i}A5?Ey{V-((_yEeK*8!$0Pq>?7Php27Z6>dK=1_dl&lsrOT-2U3ZaBqae&P^U)6+M>Al*63yR>{W?zbF=I+#K0Cim*HP|y+0Y*Ihan#Ov-W3morQ9&zJ~a8PkrvY?rcUs@y2^C%c}zV@!Q*&|E8Jn`CV}T%`0La*pY;N%z?U?$MgPU)d^1V>(33&i7VWNlCw@$I>XoK(e<mJeo9dOefIzRPd|HC`v3ar=QsWp|F=K=JepjFEy>zJ39qLwCyUP}uO~01glE!!Ad8P9&m>Qvghx`sqbT9A^eN=5Hp6(9?AhsW$^OYIlB|N1a286~M$bzY&rTMXe1tt1d&SQZf5q!OBfla)q=fHK!Vf6n%q*vrTiA=<kP>b}2{)x@C1+*%no`1zDB<tudC7TspWji!jVa+^x<9#XvN|WL4!s?@9sgd3?oak-{nnv`D^bEVDB<Fiun#>8IScFA$M&V(g-g<N(mlu?Y?GY)ES%N`3ID@(c}RZ9_V|YqeohJhK?&cWgm2LwkRPxOZy8_OPq=onzDw3O^txp68su-t{*-W8N;rTLu0sjer-U2P>yqp8dW|UIR+Ml@O1L>C+<;!2T#H_bUYlH-<*q~tSD=JT(f!H(yq{8(aB)hw5G7oK68579kOO%Cew1)kN;rrTZb=EZrPn9dXT7wgghMFduJl&qR;;hClyGlKIFcSl7VkxlB#)qkW9S3P;zP+X<jIuqEV@Y+pGuxZc2UCXDB(CtcoHQXO$kTQO|r@BMNz^%DdFz)f#iX_pYD`!XG*vOJ&YX2`szS$P8M%K?m%uz3D+~e^h@E2^z!stWbsPm^5l|~aAA4{vUn+SVRAuAI6u8OS-cQAKRGWYoShQRMG5DjmmrJ#k@JuXP{Kv&RmtK(<f7y%lyGZGxDO@Vm)?>r-j>{#+@BI2L=Pd0cO?%Z52J*~(0h}`BgtdPv6S!(`UtXk40#550VTYOKA9{&i@b`wnG)Vkcag={k++lgQNo8Q;Y3P!H9d|jK8d`VJe?9AO9>CBgd^zDWbr6+1UZ}%4yE@bi+3l7lG{<jE$E%e;vLB1P08Z*$Suf$lyEiU%eWFQLoY_JNER<oE=IOf!nx@s$>N2{xyinia5j2DvUq-SHnKM*oQ0m3ES{a5g`9~J&Opya7SBV@Ku$*qr>7Snix(xQCugRFbJDAj#aokel1o#<?J42!DdBnaK4kH}<ay*dl<-`7f3o->@?7$KN_ZK47+HJ_c^P>PCA^6qOBSC&-b7BIgm=;xki}P#cary0!YAmP$>Q6|C&-s5;os={$l`~|zme}!!jI`^$>JBtkI8Q+VZ#Rhg)DxHEH3LhgX_D7WP@Cn5*|hgkD`QQ=uOB?xL%K;ghx=qL+FjjjksPPLJ9Y!gnQE)lN)ng-kTEcP6>z6+mXdPlf%fpDB&LTw&ZYnD|%b9cpb8MC9-%8aw~EhO1Kjx+=3FWNiR+o_aT4Y4+w|QgXks6;yKAd<jRzAF?w3Exa<dt@w0Fq8zh{G{+ulS2U#Tii4uNF3I9w9pQGO(-(Y_`NB@QV3;X9eO85vRyoY|4e3t!w4?U4AzM8y;98U=^rcWn}k0pywA&dV=UQAv~32&t@B#W;ki*F-~pCNB0AEShCQ^NNt;Xmo;$>P_^f0AEQ!k#wxJ+k;qvPjt51_|5gscm5K++;i1j}op*&q1zD&qdEc7Jp}e#b1!~^Y0({S>hk~_p4;_o8$~k`xigoB#WOSi(e+Ev%w$n^JTL5QSu}56-xLxeFs^5J^46!7bU!bzLYFJle~evgc6=cpFkELNuEX?O$iU6g!@s#gXyEl;$z9;!^z?i<iX?~lyE0{I9WWD+=(1a2{)#<Ba62niwBa$tC1U%9h7io<I8$W_*;5SO1K;)T!dbREMAOUgq)8O_MzL!;<?E_<gAo%M!GLqJR3P9IV~lehVD%k&q7W^PDKf)re`9HXCS90dr-m#Jsnv*z47Iru#FP-q-Q3J=OlZQy(r-v^wMPU_T(Jo>Xh(!N_Yh&yqEqxS$rOOFZmE9e2_keEIyZfkbHm=PNL5zi!UQ5k$<9uPtw<r#W#^plK(>qU!*6H#dne~lCM$1Zu)+*_zAL`{5K{1FZ~i({5SHy<n%U3*q45nEdH1*5-x0mgdOxZWO3;f4t9>ZWbt8S2RWJ&UPlQppoACFN0G&2$P3AfDd9!*5oGZp<VEE9l<;hNU$S^_@@(=nN_YajJ6Sx8Jc0Z@B|Mtmi!9!QJeoX?5}suHvd$CknXHk?>O&t-9?!q`p@);jTam@vki|QZ`;dE5!cKY%vUpAM=XIWw>76XgNb(p;crZPLEFMH2OzuhvhteyP#fy<c$t@}22J}2+@l50f<Zme9GIUuNmZ3i-i-hypAmLOtNceY3*rNYT7C%Q8KSCDYLl%!Gi!UaNuO*9bC5s;;i{B<&<j>`~{Z%=I-&4XL>G#Rvf093v)7T*4Z1mS;aao^bql61l!WHS>WN|yWBDoeN{4L#&EMArTEx9!%+|l-BJttf(S<R9aNbf-Iz`qC5Ym>!ukw35V0-29^0eXJ2xUA<2*uJdu3NXERQF;clxUA=j+P<vwiZXpsma!SR9wl6Yo{lUo>%S8GES%8>2|qF5SIFYW$xq0?Qo^U{yU5}j$fwD>DdCOuC1mkw<c;J-l<-9QXtMYK@<j3wO4vyWccFy4(fg6b2b0Bnki|QZyOG;a!VT%cWbwviaR*tvGWqj5uOTJej9!y0-h|wQ_t1>qh1`W@YDRBEHj~?KW3nRYE6L(Z$dTl3lyDdNT(bBKau;%YO1L?F3R!$CxjDH$C0w08oGd<+T%BBn5)Pn8k;Mm*1IXnm;j;9BWbyvwvgFc~a4C8}viJaUDRMbVxB?{{K?%>JgqKmm%jx~d{dm3Ql<*2lcolshc_8m+6(zie5?)J>B1f^l)>6XjDdA1@;pE|Lk4=>DW=c4oK7~Am?Hx}ECsM-O=yS>9OUT>E+bQ84^p#}sjpQBVos{q{N_Z<J`~%%2$0ch{vJxoaEtK#E`Yf{eO!5ZuYD(BepH5y%|B*hOJe3|xpH806@5fTY6Di@z^jYNKAe)D;=l|=!2K(|)?$=21ABFv&-%R<llCQt{F*&dQ{*g&=P-@w$C2zVs^pH5W%s9q>0U&$zEd'

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
