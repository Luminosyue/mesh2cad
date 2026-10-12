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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_003.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_003.stl', 'source_sha256': '2a6f5f377c18d8420c0c6f44e7e6e5672eddfc0b706d127e0398d6218ad4babc', 'input_faces': 1104, 'input_vertices': 598, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19181428849697113, -0.1519605964422226, -0.49999991059303284], [0.2887566387653351, 0.42955371737480164, 0.1927991658449173]]}
GEOMETRY_BASE85 = 'c$}rZ1#}eI7xh~mY_P%I3Js71NJ1cJ3c>`31Q`YfY1}P=pn+nr;4rvO<1z$yt>Bsj2o|hx1{+|Ifk9rMb9VpJmB(A_t?y&4v-Yod-@bM0*0s7-S%fxBl{%*)|B5Q5KcssxGf+_|GATKg$gbgodUoy_QLf*BVKyZz`}EJHvzxSR9NOBZL@FaZyL64{9PU|F^{n14(9>J>?AAYgP<Y3F9r}lN=}LY`$378Voqj}*jsv<nKbH=u66me^m+@Ak)c?bO8JtBh+fO@n*r~?v-;R*#T9?our)nOXPaNhlitm^@dD~$(Uq^b!>Wtedz5Qj#QT9EXZRPx0e?EKI&3B}W*uv^pG2Y!*;ypKW`ZSd;@b8ZWu&=!=&c{>iS<kVbP*MC{A)LRe*XDe*oBr(E=XK}&)zGS(k20d4oR4nb&Y$b`Icf3V*WSdxzc=L)|E^tI_KnDLJJ>%vnbRAC+OV&*c*^BeK275Ej`D3|-RnpFt6HqP@2VgB;E}OZKaOd-L7&ZLzwYAvyR_r)&Hnw^*Jl>r&HkL<<aZB>9pZeo`g=HCZRIfMKT{F^c*ec_`P{GUtMBd~<lpPd_`H<Rb65CxPxiC#NL!Ta$E<jaeJ%Pd=WCpvF7@A|%{A5$E7`XP&zI{J)r5V$Rdx3DU%Fo9_TgD}o4c>hJ;A=3!q-brx<<Z|GJV&l7T><?A3lF&aUu4NZuzYK#7Y)lyK<F%_0my3uKv=);yY4L<@6eSC5`z1D}U+K7XN?caruR2NP5o#a@=`uwz~U9&MFpP`)h>cv(iiQZ|t?h-Pcd9|E{mSU(NZbDSSu%64$vr@a><6v2XVue1MN{U&8I$@a-taO$gxYY^?agzS*;)r9SmLxp%nxD(cha>j`<}xJ}ndJ%oEmdA{YA^S!cG>N#g>i|;C@@n<Ubjd{5(_25dch9z*jS2qUA`SyJ&<s2Q)zN41Zv!3M@`}V4n*f*8ooWD7Es`MN9+SejdpOIGI9Jou`VG3W3xG(1g-#i{H-`i`m?|2ho@pb)Ii?4fovKsXtO1mo9LGqnk(o#<SbSFt)w4|k+x?gAhtn4iz-^cG@-$?8tzkg)z<othV$NAf<)syr$Z?kXjuSxl*G?wFTxx&7F<~Sc$>)<W@*?$824zzPU*JF!sdZfMfJzxEEg5(2VQ6jAQ53{lF=+{yF_y3Cjsj`ei9cxSZt1p&vjy$u+-M7!$Ve!=uCFHo@CQ3f}_K5$yn5F#o_WNZ#+E!G2duqvN<stU9f4}aqlqbE6i%QA6(oP@ll=IEASk8CIE%Eh*QqRFM-szXarGJ!oB=zPWvftfTc21D=@a-@AO8R-X__%7dF!s&Ct)x6d2Pd(gV=ViQUe(2~a9yt7uqra1-}RI7{Jc`eiCL4_xBuwNzN1h983)Fd-0$vd;T0{u(jlw0{I&D3ueSJ6`epX<QvNc9CH>gU(l3kLk^Z$rmGaMfyWPF~#^j&(OFv3rUpo=N>FrJ4?c;o=ofCgVKB<S{U&QYmBjeML9y~tUpYOWP={`)A{G;;7e4TnH`{tbv?5nT4N&gC4ebC*vk4bm^d%n^&l*_54^c($U@fE#}9Cy*eb^JNvVFKs7S(EbjY_x&D-};n&b*Go4KVM-Z=j%}8_;=^aNcwYkV)*>d__D9=FT%d#>ms=>Q}u)HzSew)#W#wklJk8LChg>xzLI{gho$@uLwx(7Z`&;OGb}>RH>3E*u{1LN6c{Y&o4%KM?9F;!59nXw&sh9pUpLD2*w4N)`i;!bN@bZxy?#5+=X2t@_&=h&5v$qP^PQD+SpVqzr=PI+SpO*X;!p5-bUn(x<K0dvXW4qPE@^sL=K08l(tgG_mGg>nNIsQ*SkK2@_~Ig`k6D6wdp}<<#p}8Fhj+^Sy!yJdb9)ZM-M2Rzc>R06Za>KNtflakfh}&h`^u1^vhHk>Uarf-FNfWIdy8TgUkmPP$;a$}ThfPjVc!vVNRC_Uj->bLXf1!M`xf7v+h5v0e8(qG@w1lTeC*yk**ABVkbF+0W8d7cSJsDDa&dptXG%L!6BA|Kd1C%%ci;4jk@L;ajeTuzDXxFVv(J~gomJ^1>)`0?T>skKkL=sCq+(y~vzha8{FyJ--B&i<Px_v3#zk@c=<v<;Gr7H*)2qpObx&pS4SNfV@5me_>-f-z;&=L6%D-qh`)b`7x$fV@H$L^><bGT&!yCEo4KhhSg?^TN#$1#1Y0^vod0s`XSK;fjj&FaR`@f@Tcd2i~;|Bl!LVfnN;sxb;_3F&!)Smw<<H*qwH>8~mkb1b6u+creeOM*-Red-6_FEnKx*0vcB}u!{E&14uV9EdSQyJI(+$8zU2$c1F;#KyIjo<isIhxmC-~Q#zTJ}>7<MpH#@JQOnvpejY-+Z|r>K9tb`nL3H_O(Hgd|V^4h1~bRH+T9;`$^&3KkxspujhD?<eralIY`PgFGTA9pK2CgZ_>fyD<cBgSK928@#KC<Nx#0br93HpWARJL$K_wEWH~RFueG|khL8KUj+E0YvmAHA1@^U)9c6y8i*Ntvzk=&`pR|9oeA=V#zES+R<ded;KdN`b-PhnNN2*xzF&^Gu&h__I+OzieB`Htvz2)xd_2P*#9)G>fzGj|~a!wUr^AX>5T$it`x+>|T{H33UKeza1#YPriojFnbBwxwjZ=a;UHb(rQCUU-U;@c~ob8!B<u1fzK-<R97+U=D1(cau|Ovhkp=RG$p=KQLqmwDq<(OX;(`%1H~UC%H33}s7*|NDUja@>1-Ts?8P>_@=Y7x`TOp08$~`(0njI@p@e>2~73_+7@g7P5a~ENyAY-{mU_4K3wS4`P4hNr>cAV2I@ZT70ckKK315KFRnTVz>Bur5s7_zOsMMe9k{Y*1hH|FUkMrcJ{S}FJ=6@laJRkj>W6kxBudhdE;Ih*;lFTU|-pgOZvrpZ_dYj+d<Oj4UqXc@u2JzZ4VVcX^>p+uNV2V+Nc1lelVxZ1Lf}WK8#lP_B>7>e^T0C;J*vGJa^WyuSfmN*WJD`M}oB5S>pR$;qge>`<C~SjQ1_rcf9E(^KjBSE{}Td^;}LDu5&(0Ra5qVO2x2mtoD-ou&bG*-ZJf-!+v0QxnCLbOwMCLdiM2xQ@Gw7eWxU{pV$1I^=J=X*E(k1llzW<)8ZHZu+credhq5f)>7;EKE%woNbX<qU1s0@>I9#cc4_rZK3@1t_VwnnzoZ}9%D&@r)J#sdSdn#d_Iy`a+ZLJ5e%qmPeW!}APZ&CtbwD0zKc)8_b@$D#y}#=_LeZ{L_-aUZ>DMlQ+?y$^{d>qd_UbtC+h1efj^n2E|CbMZ<!%i7j_kSRxa-DC`sFPppL*M*oW6fp{fcKTzM3tVeZ!}pr5&1a{_L9>j!Jv`@Pyl&{zv>|R)>twirG`jGkOF2=8g8ePSP9Kh>`0uj(w#=oQw|-dr5yhV@9)I{Rf#Zcdg<37kg|s_6<FT_vefck=!nno&FP8A7_<u`=4_%{=Z%~p8YJdrM+!f%lYWjW{<a|Uol^fTXKQU`NqwYb?f8`(oPPQ8_D%it*zWIe*1QZ(@hQ;&iQmKCHKwUU$C#uNYB3c%O{!tCP#ApD4$}6ak-}4mwtCTfb-XGEsS8*HpqVE7pZ5vPlIsweap&y{I=Jezj-ab|M$wHL|^R7zYDR+I;ZZ(qZU7?%6ENr$ky-se$Oqwx@-gc+Qr*)KNOTo`q!j?`f$0Lx0d^-er@DFbW(Np)xG&;{p7p)PtHGWZuYe-a-VCqKPK(4%lO`$-Zn|b!)7tOkE%Qm>+ODCj<S;8<-5wM!&e8^W8WMYA=fo-ywrb}jO;rqXW{na_+f(V{|so<OWK#*H<{;-OFlt)*jIX|k@H<;lkq1|e0@cLjBl^rbN$<clX~*;jBp;8v~ne+-yFNbzUtje_VFIyI_mCgeq$}Z>A#eHV{Q+*Kbt%9g7|j!?KPW8d+7d=_s<<=inH&izDf2mQ&-~gTq!NS^3E>x8Mc7;^A*3$JviSA-K3wMT_@#<EYpq8%RgHDD;vb0U9^kz-_Dlyrp@r_%=zvqaMZos>XTk|V$FC&?h{5n;&rh)YCHSpq9(HLHLA$GF+zN$_eR+#it~_uGgN$gg$Z)pnRn%U2a2!$b3pD3&q+Hm`XhbrS>ivDc4$UKiXURi{y|a+t{*jAd;{r?RFmVS{UH7B1u_pVAHnr+?=QY%Y5>+n(jM#`tFW&%E-3APaysc3<LkewsU+XO+w=B4<?g3^9`wKTuIE0hVoq_pi1z3d^qu^*DI?iWSwHrv@Kc`ebn*XR=Q{)GQ=G3kQ~Z?Y>zK5c{gl^HpDKRJ>!{8XKjrmO7KoqndO2pkXFp~8(SP^v9Q2*`X6%e%Up>~<(mwUhW>3y1ML#ur%<skdwAg6rFM2QW9VOaX`inUrk$vswP)olv28pl7bhGqRH9T8yu7_9sEaQMSaSHp6MYe60_A|Y9AHFV8;WF-cjpFf2n>U($t$Riuuk7kLspp*^*-ttCn|mtt<$NlPw~U|a?k((_33=stTF2!)4m<9y>c{ynZf+U3)mMf4b2;-}w~X_~n2-T{UXlAO^OU1R!GWBQYo79c!{u?@?-0T1Q_hb=0|s$9)m(DjCzg`_lBeF_@19rl$3xgZlSan#^&Pl=j6z<+E&1P-{FSkVNAUG6_)PY(7Y815_Z>MiUjLqN?r!>BUke;)^{c&?^dr*Byt6G8`}P(&Mt-mS%H{SW-OFRvm-H^*mA}h3ZuDbcxp7GLJ&qRT`ca}1**CHjllkIe!DH^elDnGKUm6_6`Oj@7^Z2QB;(r;(zM5Y4L(FDRWSsvta}?(j5+vta;xCz(?OAosw_QQmPwG0I+lf+a)^D7D)ikn?_PUDfi~KfcET=D9SN2r~PLuW9+bQF@zTR$<^s8mRMmw;Veb;kp?aVuFxAs*nCvy6q`dHeVx#4&Ajoe3Me8Kuto%=eP^I6hN*8icBkJ9_fBtCyLjPEauAur`QK<bT?IsLwKvd^@x9rs6V*vhGV+?yHXxk4phdCn3RJ&n`<@>ZVnjEs?Sy1Dq;oR*s{`BZs4oy(cOC$B&4Nr&Y5`@{h=xE+>xFW0v~H@VM>Kfu1S^;cPcX4@j;c8eSA8}l2;{mA1tGH##GF_X)gX}hdrGM$zAq^TeKj&g>KI|Z{W;_nZvV&BX)K;~D}r*iL%<a7L;+#kgqmU6E7SJKbhC*wn|5nN9DnZmQUKGPPHai*@p<#hBe#lDi`hUC-eo4h~pq`dh1C(Ate?6Hh5TPm^dcr4H3l>qxd*3j1M>pk$kz=_Dw{Ckf!l1~PCu5W~S{>EB-prqd=?-A(1%eXz6m1l{c^1iRtZ1&Zli&8)BZ_50ddm;PU8S&LS6=hy8`cTd{#eJnwZ_QlECsgLgGuPQSuhpE#zVA3rZ=dj&q)&H;eeK2x$^XVT8RrLu&F6CBe&2OnwDNy0=JQRlKcm{3FX4Q01<Ck1)Q^4h)F}u1*#A+7_e-+)DfWNNu;a_QoU32RKJ}ginO`TJV&8G$rR>|DyejLVy#6b=Je{)1yxi}IjCc3K*w;2cm3{NgXUFjOSF5bz{HENN=V9CP$-eyB8tf~7%;kMiy~tEqcLe;ln*BP}c)l}t-ui?6OPknNug1yq3^g^^i)L%IhWiD^8S`EYpO^mh5BBv1*q=$-!@g0+doAbR;ilv>^R1Mx$+&f#K6|w6lZ5*7{;gR!TKoq$dA?M~R$*Tom~lPlbMv!2XWCqLGneP`xQ*QIY|Z5UG-n#FPe-O`@!PbJ_ex4;lJ)M9>oM%7*xxoc_-x|ec`cOt-+WowcVw@?z7kiC>rJ^-kjGiaa9^Z<A<t1SEs*D%1*(W&Wv`4^et6!I_6z&!u<bIw4fdVHzgyCY&qK#^2eZ__@;st<H}MZ99FX*@<at#e@eMq`(DD323tuVq(WwZhH$%NSy?N>Q7S3n;JsBrgjgt3Xf*y%qDoCC`_(Y4JaphJne-1p4ntzs`i<vjpux~FEC+*+sPw`JI+s66exs_Q~o?EG#9qb!;&ZXcv7d=Pga(?Ie8v7}quZ4bMUwQjU_8qe9<L7#2;AhD{Y=yM9^zs}~i}Tqo*Gryn8XJr7b4>fL^6YD$Z^*oJr2_l<soLxtuIHqc<vFQiOC8B)u{>8b|9v3)c)M4!uU8M2=keR$@$c-7wn_R-ALM<O;a=R%9aU%VVE@?wS)ZF5x&3MN4(#N7*5#Lc=C<I^#<ZiNZ4za_CNWgrcPed)?_Gw^OHJ2G=Id?Mc5%BZyF})r>{I1APNBB!8;O^t9j56b<466&>}%>#8CT=)%5#&JkJ)#<59X-&Ql7Kyc_n_E)H09n%_{dZ*<Q1+-$~29HeTz<<%(^+o6{?P^1L>}CeP`;hqLd%dp<he^U-EZW8YpikGv-_X|SwIDqUk=+p|^bGy0|M-xb)mm-BfvSMIZdrf~bQFS{oGwbL?hCiY@q%M-DW%lU2@*Qa{BJiq6rFPbI($$xm9v1@+pD|NoGuYHyGGR*$9x&3NQOYP@!y}Kgs7qp+u<C<g23HDWQ88@`kon>CmnZUmOWQgn=8!_D8v=5IYpR@9Qn)#>^r`PmX;!jDC=WL^vq1~1_!1e9gPk!;E+$WBz%D(Q?TGrt$y|{lW85&9Yrhm%5Poa!*A6;nCK|U|v>2kktWy~J>Y}OZFA2dVq**Zqv%gc9weG~838Ls#1N<CoT!25V+Q+XfHco%Yr^M6rQ-g~k=>Bygp)n#9)P+jh$vi)tB>$r=3`#E{vME$&Gf|SqWF#GoO@?Ob3zZv{})A#Hv&lBZ6EbmtGKH^WA4gTGxO!D4Vk@D;to$|A<zNyOZjhM^x@Vug3sl~q1t*pFf72cYC`?r;nepjt4{C&?QJl~s{*RXGtuF1Yp;Ai$7)eo}o*mGFcjk#L!{N%`RNb=8qM4m^KX)5i<?;QKO&5!d@Uj;Aa{9cQ%jjAO6>0#`f^{!ivtIcb$h|75me!JT2o9_p+ub+J;$DNQM@5$^c%j3Jf#y9J6dj-lo-WPr)Ij(V{r}))8_`OcGZg0tF|Dct8oYWcFSK9BB`h4rn`5R+1#k!Z%F{{P`)-hRP-RskyDvW)lOEGzG^uN}U&&%7Kzj4;bl8+Mogx786gmRL8P?W5Dn@^JY=3@m*{^sycl75db`&xEiIj<+B7V_s0{*wR1ic+5~g4x&OgCw7Um8HLj9OiawJQUyD9>~7Z@&vbAqe62_{<=MZ*O6wSR+jwDRySpRS-!2*TZ;E-U4F{<X^pfUE%l&}y)lPBujm%*e%+0Um)Te6L`iu<2grE(;JWl9uZgkl*IjRQn%B+7&(mVvue*BZkodLcSg+%#xZn9a8ZNQavm@7L_KnS}*|$H)Eblvxoi6=!*)}Q9$4>Ho)9sae-F@R<@s(7oc)V7-?X#3qxp;6k|GsE!tfgOE+0DL@<7upWzt+pFmVR_N%@I!jM``KTsV6UE-zy{gifbHL7RLQoec;8u<6#5YuQ>mb`>%P#NAlT?eExjR>FqE5CH>$W^8VzeR6MVnm1;`*(SDN8in1H{xM4p@`uU&aeMrYsULUB_+OV%<o;5$pd)M0Fw(J|zy=6Sad)nIUe&XYOZ?kS6i?4i;_q|oT@2#c&=ZJg%RWD}bdeaNMlkzk(<^CvsF`ut`Nql?HyYgQ2{n_$f(#V`g-TSFlE0ObYy!B^ak3A##R2V1gCHN-ZS68l7k$LK70Q&~sdpA4Cd+#pa{&<eu$KgFRN7}mVE2ZUqdk5aPclml?tjx2`vs=<@C11+AC4E$aC7%S@-*DhPd^JaylxJ6%jN4mg@OWZ=?k(wE<EKwFk4xI%NJ*b=5Bo}Z68lQ7X_oZL<2!smW{g`Y^@j9%-nZh{h>>z0oF?yApQ^#*r`lkf<ev~O?I%qz`$~`FlK-4)av!>21@|N4X3|mj_N=6z!S^Hf25-g3yrz%X$?GUbVuoXUT-yWLFRd%%n`+C*zA@pE<ljQZH%F8o`}(_zvd+)(fX5T%L{s+FYPaOR@6HPD@5cVUlD^z$>0d40@w(0MIWNAee@%ZQ<9}9D@^ST->RosoRu30H&c9PWN`L86NbdIzmOAd<@ATt;%RIiiuEkeI*Ja-btjE6AGP~T@1n-n~o+Q5VC7Y~U`fcNOZoCMy9M_)3m-8{BCQJHvAEo__!TrhbtL&S3a!CCQS-w~L*ELE1JiD~pX3P0{*+Vj)aBnA$r44w$Ofz$dkNMOdTt@cAs`<08Mn=l}<o(O@IHRSlE9qA^lIxgS)>nE#@r}og<$mpC9$tsr*N<gi>$FJv<D;H@9o6+4Bz<DAJb$lwm7lw-9-Afq6n_`v@>Bj@jQ-X*;ohE=?fZGZLy2v0lKsoA<b0oX;rh|`Z9M7TPV8lRayxf~pSSo*w_MUM8ogoP*z`c&7n>;Wd%1kY<+n|e{ep#l{M^Ph-a3-L$vhQN^^~QZ#C2d_-`JLYJ!*-(A9q^rZ<VTp*f%R)lze9O=KCD_dm_#+<?|!|yW;1+Bjb6=(Q=;$U(YAL-e5GZw~f~!r`@lw@ogEGU)?@W{J6q09{P5Y=Q?BNi|<)f_G_y2<m;>4UwYcTo|V9G`Fo|shb+E*P+_@V*ItVM{QYG<Zj^_d*Y<bp>)q~2f0??I#}j3#&lzby)ug{nJ|yoAlr4Y8Js-#0c5)x9HxobS)kH3DxqEWo`?0OX*Os4TU$52O;_EqM#2?Y$lE3}zUiOWT6D{eLu-1})>Y0}GX1Z?DU&4R49`{&HnXmUPvH14NB_#hhYuPtEAINoI?k)Rt1C2B8?bGzn!M@%y!E#(<RIJSJtsaOU|3=EA-j(%g&L@(;t6k+UDeZi1*0YxLZCOb2>HUO#)2J)Q-B4K86^%cgmHZ5OPc_XO-e)j<KeKP7KP>wg`(LkOotEvKdwbBwwBmf!S33L3-XZed<+x0|FX3oZ@;ravW~7W84M)rV<T_9G^+ku|eWb@%<-O_az1Y{<+?4mmXRYSv7WPtK;yC}vhq5m;zb%gs#)y9L?EhU|-Y?4Ed5!eDJ_(%v%O`x_sz(;%=S-^dnSJ9%F?pVyt-I{=J}Y~H(=W&^`-JO{@H$ZaGW;T!Cu^v@NA0*bF(}mX*Np$!T7T9mI+Hjfy^>Su*3s=x8Ofx7F8%(WGWM+a|Lac~eSIrb{J;BK#tc7sC`vtNG(->wLu-SB!Cug^U@ve1XhCoRaC&G4aC-24o9GjpFa_~F1o30&T`;K$z6ZSpHNm&Q7opd|7s2t)IO>cO&N$)>19}pA0(=sD7J3v+dJ23Nd>I-Kj>oYsBZ!lrCfLOJBq4}jK>r250H^T~&E_FYng^T)oC=y9Oqvdy3jDWCf;bNP$|g+u5=?pq90!ht8eju;6pJ7}2R#cui}OE+Aie@k0w>`-uONt@Lh0O|LQ{cL;XIxqh%Z3nz;P(k1?V~OIUIxdnKS-!MrsdH4-a7q;+)VN;GAGjXH;}XfHO)#J;9zxQwl*`2tk|{>H$s*evac)Ii4ek&m)LWBZw2A&%g=bL<I3|1o1m4o!dKnCeDiU%?Zv5E&=rfmjL@h1HiuE5NFhZ20;VB0jRGa1aS=naTNry5404x6za|gL0l3+oCTT|oCW+6ZJ78B^f}t^bJXb>#Cf#k^Qd0~K}_SpQRpe?Y49m<JTw8EfNKzsAa;#E#J8ZgZOP*mv1{BTz7Kt8OCB4E)8qPObsI~wVyw-I>*N}HiM^n{9?4@haWFK*BYA8mZs>L`U2_3(U1!vSYS21h4O|l%1P;PAu8AP7jv%fEtpctFu8JV81oZ*?;Mx;EML(wgJeuZcXN;ve+!=SBanKpNp?9En!D(%x>7aMP6vRmg;(bs9ybrwI8Gk@GK@IRGa18Vy*j1(&1o2vDEQ79t?gp;|??Dh>h28;Q1;2MYxA*u=ToXYYf*`I7O$Yu7`dJZ82PUPuApQuw4ow0lp<b>di1#9hH$c~eH-H^(_2@tlM>}J<GrBrs7=pN)Gk%7)gmwkjcSdz*RC7jUs275`Jc76av^ux~xGI9UE`qoLv_7~2xD}#4%HS%;Pta;$SDAi75C=lNz=2>N1aV<#d2nHHF$8f@Xa#T~s5i6%xB||NxE!<!v?{m?I0RZ390G2RAZ`I|0B!;P1=<Sy3%EbDCAcN7U4H~|6m&S4G#VTQo`N7=0sR9^x(U1jyc`+>CS40&4qmDx_rs+K;+f8v4qX6U23`PO16>DR1Kt7M1Kt6?gdn~Ky$ZerO@v+rCxRa!h#x`UgGv7dKY;!X{TKW<xT;NpScAR?lhSyhAq{CYXiac6a4<9k91N}ltqZOLuI@J0R7VikKoHl0()d!#mOSp%LK@OH_)PvA1o0K<b?_DNcIaO4cJONG2JmX|e5eCFA3Os={5v!nJOero8Vw!~oeYfzyT-W5&|%>5&`9Voa3r`rv>UiRxQUWHJ~lxR*G3T6gSG^d{sgWK)u2CtHE<0CaV=;dxCYc08VL3UmxB6$OM&wvh*fA|aDHe$Xkl<Za6xD>a6xbZXi;zha9$;Oe9Vg=&VwK>0`&&F#>yf{Ls}eK4qP1U2dx731J{IxfNO#qLYspdf`5f}2mcC=P-KlmYn>6$2yg__j6e|gfHnt{wg8j<0`37G0PPPZjRFq<kAhACj{;AHt^kuR2Tui0f-VJ<&IG&0*-6l`;ITO8Nzf7CN#K#t9^f7*>qzJ*@F<jnc!@I>J7XjCPw+<Y0cYHB#!YAJhaLbQK$`ss;++WMmC(iDmEeU4;t9|t;4aPxb4F)p41o?p5VwVff!l%`L4(1Kz(LRea1hwv86}`)paEdohAQcdO3<?4viQCdGyq%)Tn8Eqt^;lc4FiYaJewhi8zYF@Ib$$%D6|W>3(kM2TOAEW5Kn|o08c>OPDBtdf^Gya0<VG|0Ive?g5Cu00$+B<YpBg8dJ{}~1581z*d&NwA&3*9`@y6;mE^ge*tJd|-T_^yB(Eii*FYC4$!iZ{*ZPEbI)ZpCbOLw+>TWD_5O^$jG=ew++7=uE{uSCtNgl6=8$yGW<nfKTCe&X^9uJBAl;k$*8b66?e9Z&R3oW4}kKx1xpk=_MWtHUdpV&1=5a)xIRFdZuV%K~`?3$;DeW4Y>HJ}=_BAB!in6wU<v>BMRF}OCg3AC}2Ja-efhqeQ|`iX1aC#H45c<4CjU@+-WFzG}v=_2qruxo8YJRiDBNnZaDuZHeYlGjVb+o6}0<n<Nt6(zaPxYlFDv|g)$bzF7mYbAM2NL&YM!}`&NzT{d@DsF2|1#41L>SL}oDzR&=OYB+$6F-0^f@w~n`GMw%7S8l-olyqr2`&Rp<BUU!DDD3r2B*e%o?y~a;MCw$(9+;k;BSg(Suh3he~JXLk2A(QqnR_NA&6T;eZW4*r!|7O9kevK9k@NT6u3RO1Jo1jiMr^3AfACBo(OFLo(LX^Aa05v_JWoHdx1TmX~3?!_P}T2qs|D2+M$QQc5o-?VQ?pKPXuu+l&(!IG!>YF_%xKR$7uxdIp}}jb6^ue{0>Uj;~hQ|SHLxD2Ce{Z2ptb@2#!P$|A8Q051j^H58jL*o&#+SZjEa{2SGd!+8#U)JRjNt+yU2nK7#m91o2YnMDSAZ6zE9s6!0(vaeru2a1Uq$Xj5<laCxW~xIFlaBI*GqrS|a!L44M&4V^_0|ArvWi6G8|ApQYr2mb(02kivzgm#t=L7WyroDo6X2O0~GMLX+*AP$9|1BZg=K~3;&=u@Z(Hqri`B8Wdhsr`MzXJT)($%bHWa3C}i90+dWj5g3{Xe2li?Ui^n^bqt9@E>TqhY-YX5XApMH-rBJZ-LGM&q3SWf*{@woe!Rm_PQNG{0Tw)8oCtx8oUQVyc{|Oyc|3RIt)Ap+!sOI6WSl_YU@1_!~qE6iU{J`&<5bzU|(o?urK(7B1-N41KR&t@CWb(=x^W);Mvfe;LXmM=8SmgR&YG{g)?44pCE|;f^G%>1$Lz&-Ugip-UgoKj5g5L&}ralC{t_bY;YUs9O!KD9B?iKac*c%a4u*LXijhra0X~5a0YN1=nvpD;MCA`;MCw$(6r!G;PlXp;Pl`u2;!{JK48*Na8|G@J#kY6aW({TcIZ4XX=!jas3){E*b{sNL3|8459}I)jv)={E$D6VE%0;bQ}A<edYkAcaC(eS#i2AF6-N;JLj%G7;KtA<;Ktxz-Nvk65yX8E#J!=>VAuH78)-<_Kv#p;fDc0tfe(ZKfxZF%1O5X25BvrE6+!$Nx&{0dx(&Joybb&fLHrTA9ZdQO{0*vjh<*Z75Wj`@8vGW#7rF<$7rX+x9J~Vj8*~i#H*h~_UvNKg5Q4Z0v?rJ}02~CZ3=IHR2A6|Y1eXJsaK;bNlF*7^(%RsXU_YoY*bn?x5vB2znDhepE%+XEHrO?u-a`;ShQ@;*gTF#wfL-J4S16ssS7=Ev1@S*nKd>Ll`wz-?4}1^DBW~nOQ^*-%(1PGFa7$<ba7*wn2;%$*;;abbY|w(>Y~bwBLg4J+90+0++6Y_}S`XR?Tn{_|K^z4Q14n@;L0f_+foDR00nY?4KoGZr<_DAJ1GfVI3@rlw8Qk0%<D4<w8KKbT;81X3Xc2H>a7F}iCTKozCU9nGesF$VgUkrxlZpiK31~Jj1@Uocb}$9;DQFHb1@U=Bg7`;#uYz6I>_-G~7H8yy=7kmo=LJ`S)&o}pcZCiBcLn!C5D$k&fro>qLMMTzf|o&Of|r3eLKlEHf_EZ_=R#Y7Tj6@oMG()1HU~GywV#b3-ijdJ038S30CqTIGITI>9C$FeJ~R|uA6yJt7+egT0h$q<0es(iJ?AQ-aZvK(pqaoF#Al$H!KBpA&LD_;BZzxJPk?)YJ3^0xJAykvPk}pt2SU$-2ZF~Sh%Z8^{au7+0aFk^RFc~zG3hf!n1Xl<f;a*33}f&!{N@J)aS3Q%a9*_I5(wgQ(5|-Rd5X9)w3jV;UL$tRkHr0;!)?iPDDiL5skY=fmv{wqnJsyaCU(u^#BZS+ZOQXKF|7+ocY?n`w?WC@hVSQs=c0XYgKo7YuT_X$>m1@Q&<(cawGgpuy+nK%>Hxd?gKMotOlz?|&|jgGZOQ9B;>OUyw&e98u|KrFEqOgjTpU`=mc0HXP7lpsOJ1)M(|VSa`pk1Bxi7iay2P&aFtKZ0P3&546T8;!#7&`b;5hWFrqJF>@|vI6buU1i9@<MuzP}(&1?{LL-;WTx?pcV_Ks$gtppUukcZf4U$0*77N5pjhlnXisItDxjeQyr*A^0KsnCsq+xDA4M7Bm4o3rzQpPoOWM3E%|uQP=v3);qNBndS6yJL3j|xR{3oaXAkO;^H0>#5WPdzaxnAAc*@Z62w0$62w?yGrRr~(?=UPvm!y<SCJsjg}i5hD|^u2&^X6$Xhv{ha3*K`2z_9aAif682qwL16Q&^E58Vge4_*ab30?)(5yYdNvB()?ov{f)ycRkdJR0fOB8U$__kj<9??A7D?|?I->~s#9aZV~YGq?<bxIVNpxIQ=(LEIEU><29j_5&AzW&*qFx(I@}s544Kb3=aw=LUbUiPE+CfFM4OAU+7a2EK;taS%bg4!R1w4m<&>gC~FoA&A4Fqru_efzYwwf#3+}B5(wFD1vw~f_MjX6L<&s5`y>`bS-!-uKh6t@q6eU@OyAB4^g__xp3XffOCPp5yXw4^}&t6VbD-;7`O$3xH+^bxFxh1v?;h5xG~fZ+!*W+Ednlr_Ti5p4s>fnfe7LT2;wFP;_?XM{LtLs{NNv;)Xsi@9tTqpKSU7kMi9q94}uS(oy8!C7eXh17lMaC2Z1|7J3<G62ci9SL=bm}4g_}xcY{WNyMgV{p<p|>lQX(NM?i;yhoZd_kAg0NE(R|~+g*Yn-i0831ib`)1h#pI9s?gk+a;zT&I_gXniuWX8=M!M4?$dk+F?VRN6u9LU;mX_@;~a^ise66OZiLdpDnrnGR~RT|Ne+6v|$?Br*uwW9z5aKr<qCle*jS<=x+'

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
