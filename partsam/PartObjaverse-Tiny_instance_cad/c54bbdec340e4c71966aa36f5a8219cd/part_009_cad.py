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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c54bbdec340e4c71966aa36f5a8219cd/part_009.stl', 'relative_path': 'c54bbdec340e4c71966aa36f5a8219cd/part_009.stl', 'source_sha256': 'de725dca05adf96e45f5f6cd32f93f8be0e00d1e16f3689235c7a2c7ed9df17b', 'input_faces': 832, 'input_vertices': 584, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1186002865433693, -0.06532415747642517, -0.11458460986614227], [0.2291898876428604, 0.2463671863079071, 0.03406320884823799]]}
GEOMETRY_BASE85 = 'c$}r22UHcw+O-=nVpfcxbIci0Kv7iM957%`h{pgbW>L)222{)u%pNl;=7@>Lh#46J#yL2SI*wrs=qQHIe)slXIQRZ*{p<Uj)oVXz^YV6`s_Lrh?qd9W9Wps7_*YV~b9K+9)>0JX$f-Cfp@Abu4eT2j;yQHrI6Eb;_{P7Vx};5~)_&dWlu%_t`F?>ReMgqBV=7-a$g6x6Q~97_BS($wJ+#-bk^KS<ziIEmA%Q>qkO94i2mbh6!PCp5ipjlV71Jcs|MH*Xk0Mwi{ZGajMOwV<l+O>fz8kjA_-t;HAAYkK@fGtQ7UQ$2*1{8p>KE^euR5+;Z+zB@UOq1IL2joF-<1Ej_?7@C@%3zv<0b#q8yhA6MLWcQ-5`0)ZO?3w&o}!V6AgJQdDL+UIB%69N5yaMdQQqy$aSgl*;=of`1<1p;;TU`BE`>~5G(PngTyzVD!W|HTe7nF`mp`tYj<XeZ~D^Yi1^{1&KkZRooTg{e^xE=)mQcsZ;36tQsPdPK>URVXXN|V>ar%iubvM$FZsRSOL>$QyAR9HM>~mc%I+E^=bhde{@Tw8;ulGrA%3OG@Uv&TAm1zD*&Hdq<I_XP|BLv_)-4Of_nZs=pC<4ljxLn*_8K9+o+DcFE85Y;@_F&cgQ9bmBmPxWi8r6GC%*doREgJ5u3senmfDD~eC49}2OL7Beo9q@e?vj}7krWYYGMiabzCLC<>0dg8T?;MN**=BZl3tNi@_gqQ+&l`h$i(A_3;3H{s4Zd#OZS08L8syC)P-Ps*8(Df3RFQf%pw+sJ9;8bLDgA-H7ke4)OLcBwi^u5PsbSlHXiEGD6Oq^^g7Hn{Ql_c2rOFl=${n#aBn%65sme`AG4vp2!&AD0ZS;7t@!*&)PzKrP3QIzt+zWew{qxoAb|ypWuT0&O1;)XZnRpT;rUG@7eLP<jHx`N6xRO?UQ)Vw&JUA=k$~ESU$qP*g$+eG;Ngl0k7e&_eMJ&?Ke|C$KDlRfAI&(U$B+bzqU6P{<vG{C-GY%(0-HPTk1-FQ#GftlIQdU<iDy(yuK$~`mI``Km49cQU2Mr`$>842Oy9AK$QPWyCHJ@Ztn^|Wjf+ZbZ>_1zZLTMC1t2*^^7;-C)Px}Pq9k7>jysV747&&`lnhs68&xN4e`~ahB)uZM<b-&mmNfWjcf4V&kT|N+jlqogefS`<_bOJbIGm9<GlxdmyoVfuFfy_q;D^c?V`Q2imx`zcSZaW^(IUGX-V)C)+3Mpv7wxISR(xMDQL&4RfkJ|nX(x9OUFn%njW8@CfDg70f^t*Q+#VlTrX;HHTcc)qF;HrOTSX{W`ch+9@pt+tHdk5J9kU|B|W5^%Ghz!<>%Hg_^VySS0}oRmvZ?JgYTP!@;7YXU;JYI#aBPigg+`z9l1_>T-_;t+;?2pmPyjz)HfFKb;oV!pIg_WA0|vdd{aM^KUZap5AogMk4TmBo3{i_mU>v|1V42v>Uq-rSyE4#e~*#;tNc-Zk7`ro_m0JiuU5>B@5^>q+-AZ5bROkD^{|uFYwJNf#P3oA<Ho}r6Qti(>AwT*z6AAOXSwuGYjkJ$gH!Q+$6F>zJs<wKP4d)#Bj?r2?w=#|Jmf0;{p;YjyD?4jrK}cTcWaAs78y2He0@3mF`X~s`h6$mu`CaPzxxEr+1*9XYjNs}{7QD@8UL}b<k{wl_}69S`ZBSc=BT8t65nP7^8Y?GOg_(AD89b-9{kLXXh*+_h*z3R9?MVv>hdiT-`f4EoHvW#Jo&wB8vKio@O>-#h0FP^-QhQ14F5=(3DRyIE5gs?i}KH1JwWp8c7p$C8m@~k*{8~RT~2KlztP|DwPNC1zt$69J<&_bsSi9nMf~i&Hc5P^#ps9cvdeX$dt};_zTcV#B+GTD`1O}{joxAe>g{AH@wLmH;kyr)@2kc&n=kb-u%-BFQfcw^d*x<`p7DflzKQSaw0ENDFC~#D%WQn#vegHPKYb_GO-I(E{tuMGd@;Wb{7Shn?{MDKB6iBUOg}JLeD%dMDW}@wsjRb9k6pOFnvcf#5I9SGeT_5byPbCM8&8LC-HdijbzLC8S6V}!`)6?7E&e_@y{{iJBi`|)d|%amBH}wc!S9<kNzT*oH(7`3)#jr<-=qFj$J<zECFmLE#~%wj_|;uA%(Lo^*Rqb&XMIL_%I1{uQ=4;6eAT%%&U^EDnD|)_!5<QZc4<>c#tm)SX80X$h;QoUu~5!$&5QiU*JY?rWzpsp;yYAA{;0GO^7G82;O`ED&+$k7+FpG1**Wx+jZ-4zys6dUN8UyI9&aSy_ouI~{)+NkvtJ~?mv7nf^w*ubHV*Z0Z>Ov`^(jX%Z*soS{MX3(RBzQm@@V;Uj*|YFI7oaoe+<f#Y4%j9j~NXSU;S^y&-Rh=N~u>A@dr)Ud{Ey~9^LiO67kojq5Nt`^q-{-;Rl8yPiX9DIZyjK;_F!lqTPS?+m=NUUn3Fa;dp3K{>FN?MFBalGQNb2C;H)YSck^=h;PYLWr^gAo{sp4J6Lz|`qdltn=kRLmY`iuJB&g5l!9OMCC(f9Rpvo+IV;u?Zf^L#1Ha03tuLMjf3ZK#yLR$Y(FxhH4%$^5?cx_H^<YlwFk8-Fcn+>FxBO_|!v0uitw=*ThkrtQ<^P0n=$~km^X-K(XqWS7=YtB$bLp{+pUT%|@NYIod7^uw-@fdCJk3JHSGVcQq#Z6ymU%;+?uGIMB%{4H+!-(WYBR>kpZ&1^^>LD?e?hDRzf?kdnTL)RzuzIWZ`P_ZPw9SD#8->tlJjbBBV-&<TI4{y+8*WceT#C|z98#X^~_Z9t$mI}O1x6x(n-Vrtr5x-^a<m@PrvzI%sW5FhoAl_6XtP;R?{>1^NyjMdD@K4kiT|5)aRsQGt&F|z%HoI?jDOW_^Gqd54{RRNxosH<a+v#@`q)T{%-qym6>I69oW>57TF*1Hub5kxj4?}ztw+olB~=AqrJY5!Tf34zBzkKzqaiU%JRkH+x8!&%o+GL{Y~4Miaa*`Q>!^p#<TzE&u`4Lef~@T*9&ElamDs}(W}mu>)ZDF(&F#Kx49nGYbBsI*RTH24BzH@*Hfo17PT24)XZnaw;fN^Hm?wGGyW*c3*+ZD<CVV7OMKh$O;1q~Z#y1NJOJNj{M6<Yjzs-u9B;Los`$3!vsyeD@iybRvTYUOZN`7SVvO`(+xbFwnX_E{C*{yTov*Ku&jCxs|Brbm^aJ8Im5_L|Unlgd#%?Rn9vSDgpT6z9rnG8@c$@iAZ#NS0HuI_WU?Y5+`B(eid==V1Gx~Xl&uiqfYo67(PBPBpKmDKMfU>_d%F%cv{GH!Xo>B{>A1a9(;oGbel*r@oZPpb^@)`Ix>kz%<tJQ4RjO&)y<xyUnb&lTkCVbm<QE0cd>C0m|HhjJ0xp-!s_$}X|-919(_qBx&#J62{S$j0FNPOQ9DF4+N(yo@LBgNOJ--TcAt@Kw*#R-VFS=U)whQYU4A8Lc9A&<@a@L#^oI#Zi76TZ#5)HL-8^4qRs_r%Eewq5sXOIvJ^&(}^%e(Qv1^84Ds*6?lC&+3yU@T<hg^8~9M<`Gj&41Ak)xZ-v~e0{UG+@D&r4?%stzX^ZGaXcqk6PM9%Q(f{{_`R$(A8trr&)S)-(m%AOrj6p;+!tuus%%W(?rL-j=A*wn;M?3^m>0HyZ*xClPHKnzrFNk|KM0ieHNWcw-{!tXT^<bI_CBbG!zRRKyl*mRs}29+I;l@>r&aFDOl|?<+unbfMg}3iQ8lSIt#*E_x4TV)-(WYM|Fj#O(SKYT_v8I>UQ?NRo5i=e@3S<D7vJ_iQQL9_KA&@{%l+kk)_nCX{M(yQZ+l$P|6YGU{{Bl4zYfngOt%VbkvN<CQ&SNa@l|UnDZj}*QR0<{9`GM-KtH+CXi9otA6p3b^*`@h|LBBx-~A|$;~p9BEH{>HNq-%gj+d7HVClLE{^+q7AL?9}`An-6wpIK(L-4$MVZ5yK%%h^kSI4K~IjY40>%uix;AfhN=f>xw#n&QRZxerVDxSk{43p<<+N5Cd_1AszoP38xd^LOy;(vKAzWKDn$n?Hmc^JM|k|V|`uSbaIys75dvr_VvH*J^C0iL+7f6kAytB9{B_C<U`W10W7zzRF$^F51{Q?C)yTh8lPPkg=AYrJ15T^;_s*6<JcOF8wQ{;qb&Q(+$ZRmHs_;$Q0opYx;g^LgyDq3|btL_eS8GCIAle?5<N$hg?y;uj5rudl=S(A*Pwdd!6XS7Y?67twewJ#h~5mw$ohd*;r_qpU`JyG3}eTQFpx;p-LR;UE3Zbytxf@vq!Op12aY?h@v7k?-YGCPw1Jys)l*<knE~FB%GeXege4dcW=?pJSK64=9N7d`)SYpY(d0#8=lI$8*kKo5*@h&Ho+#m?CJeKOLog)yO<MB`$sq-UsEi6c9hTFno^}@c*t+E`z_UtF)KWyobAdZW#oh&xe&o2mLbmKc7cc87lL*=Cuhv$8EFMJ855S)gJh{vSa+eK2zS0XvYu0pEd^d@8=}-ul2qlzB;Qb+TGI=&(E_wg#UR9=C7W2;m>{r-}^P<TQ7&7`#bzzshCe|zr{LaM2=k&cd|a(x8AKlX_p&?;kT@gb={{bW2Ai@0>oDv3`hTL*ID|N=CKL>)_bU*cXNiy?{$hs9-l?1pLr>=eo*V4-Ibx9Ti`jcy6!ssTDx)HZV!h_`SqK-(zllua{})LQtsfqM^~dAJ5=wR-q-sT!1u~F!B@&(z07X$&C5`pzbi{W(LdG|Uv2vq=UvyLmwd19J>k!)jea{cZ&UesgCOM5HT2tDd54Mi2}V4h18c38%X&un_5ksbpHM#!rgazH@D}kkUL$`GXX)qG{h9Yje6k&`qbXq+SI=aH&vk+_A`H)6|HuKqcuUNW4V~nE&zhPG{>Hl)e+uBf)!e*@_^R75sR#3nx-!05yB34Lb0YHd`MEx>1pJddk!QCh)F+*<4_%7!JeAKGe#W;>#P{vF9QWtBtHW>d3gcw`y||C?sf9e3b(}ZO4)d(pdryYz_iYf~v(Q)PeMUY19M5ZZhX2?B^LPt)$)k1Yjy!i8;eCx)l+?2}HUROKl_=+*O+qsGX`4}>0Vjeb&x$_CQ)@WZQIn6z^=_>?8a~HWGv{Ts>{8@8W5GD@;(__7^Gd{@3c$R-;{MbOzQZhB*YEc5`MCxD%x-+&)Jo=Sb=xNR<^RGw`>~niQ7=ZrFR%^Yi@qr=4t~*rm``1EPs!jrMIe6fk~VSaeAPD}t_$xY>(a-o;dfB~9~`l6+;bMb^IVM256gt4_w{*4;g7GSiU0Nr;_F_+eB?d`??XLq!RPx*r7PZ-DNT}*XUIGBhch$fKFB)53jbIf>Nzq+>c<@Q2)^@nv|}>voBr+3L3>@yC+jh5!m|whO*7w>>(}i34*qZt<XM3ClIFS}QO<%nP)_%c9p!o%@)bVc6PW@!;kiIcj=iFMZ>|>g!~N--T<|B>LiwwA!hK!-{Nn59OsM~I?_?Y{bu6|w!}T@hnA|5?`ne$fYi5-5uL!))I$REZtPje$UdOsFdv)ZAI*R$|#0)vF;_r?4rDM@g3gn(C-?u||#IO5=`j6Wn&vUGO{SjaHD$3Kl7VZlU1tH#T7s?;rQ|<@Nw}TPS`$zK@toQV6Bj8_Li~Lhp;yFyk(a5u}F7hvSk@3fLH3ISKRVk-s0N3ZHrHC(C1?PR3Am=qzkAxpO2G^0FlRQ5$wO_e6{q?1tdT5q>eO4oW!Fch_bDfvqdfJ8ftXpwjXD8{mKYexbVbtfQl;!E;)gxiZ|E(GNe}#katGc3H?v89J{Xh5w{Nlm5fBZggmekLU=kVVKq5OQ`s{Zi;{-X_u_Z%(Hh1D!?Sa07jUw?WvK<cN~N0h%v#Chb;A?p)U^H1<+bwNFE|0?CQtaR8X{%I?ommW>Q{d)-~_~A9tPr|2lmhzij;IF%j^3=nA3G;w@;;Ut=;`{#dz&(S%w?69UebykU?-h-Zr$sxIKV^ojTlBwLBYt#2td|PCk@``KcZC0Y8RY3&2=B|PcHWo1|LZZBzf7kF!0&eh^TmYElHXKzH2kz6te>YjFH7&M<#*ybT^5FQ__lDwukMcf%8OfMzl0V$6TVYreBXGCSDMSx4E3gz8`LGeuMYo!`{L9KxUUI~L%iEgtOxF$$8*lDXA!^sEBg7^34J8~^EJf(o(bozk*$fuIp4?-uXflk<G&^GIpR+#sJHMF^1MZ9{0Z^q0vMmWM&drbV;bV8B;&kI$H+QUi*(p8@%v9A|AYWpw`k9D!N0N|_2#ex??<xdhu`cC{C8MCSSOmq*Yh>UdL!VSJlE1odLlkY1lG6RM$7eXy6p@9Pzjv(=?lC+9TWhc^RKdv{h7XgV*}0`93bl`t-(0NhyR28m3QO*ecBYn9}h!3-&6m~_gaAK;z}85FZ0<5_+{pzU#)P)I-&4V<af(~`^Tt8@*c=sArkQ%50#DBH=+iwMSS7yXm|Syl1E>)3Gr?7A%AET-h*7(j`;77Wq+Cy8;<uw4`SdK8HD`N*e{`f+XMgGO!yUAc98GU`vm+R?%Y3<ALHtcOYmbRA^zaBA@cK;k5QgH=jFWCn%FmD{`xoKCyf$c3&lPGHKNo3@dp<~{?fbU`G%#9H~hqS?0;AsFZ*78`ueC3d~W6-?<cGmf)UUC9$ML#(!S=qgW)@0LLNS6wmu(<JibFw&cAtm#Ye!mk48Vg9FFJbl@G&T5{u_5eN*w=c=vha4_b=&wCl1?Ge<s#Uu7QFZ}S519;?zv<SAMSc_LO~o#vYcpX)s>F{|wV(I?s+l%FpfgL?ZAY!-h_X7TmUGw{94Db8~KYdPTi<i@!Da)69`roZzb&+KH3OXDzKD2FN_zNs6|y8_R>%{!aHzt{`wd56oA$NI1}@?2BV4-ZX|d0!uChX4FD;s<oaykF=b@&qr%dOo^=^b_;Ac=!iSz;BEDHOuwEhftsUv2OYEY@qmWhr_q;C;L40I@l*^atMLn&mDPge5+;nN~cNU>u(xJycYgN_V1Y!V-TOCtoX{zdw9QV-G%tEN!Y(yG7|d_BhMoKp%vHBarASO?|tTfjCwxwq`&l&hG~fZ@EG%813br2I(&t{=eWdMKKaVNP4nightc28V}48slIH;Cr+LIzqmLo~?l{~>?5u$Jnir*<rYF95AKbtj{(fhym&SCKcC_4VjXcRJ%F`b8Y|7dZ{*;=i=ZaXbYR7}&yIkP93;TS`XXYS(!2!5mn;$FrO<(sRzTOqYcS(}*+2nH!{(wZ(=RQ2&HkV93B7V;|5^p*jgy(^qpNX#rEJA*+Lp0ZwvEp}fmG-i97$f(O=6&16SDUrLd40G~pm;Lkvj<6gncBx<J_@osD)HU&B7e(I@_t>LnHhe`EV^jwVcB1z#O4rR3rvg?-P<4goLiSbyknr0$DDw1-rCb7zCJY-*Xg?AvJX~IaYLTdX(uIqa((Ovw)cdeuv+pfBkIe36g8?D^8ap;eZp$wBg~s?2f&XhD!z3Ye5GR;&f9m7l*f7m`x4c`8<5}crJPqYuaNy5>a|^nKkkfu$Q<`f58RGP-2P7zug@*MOv-tC_;LAsXgu~;Z^r&%?PY-z5<hvrl;5;ETzsYAIPulu=ds^ApR43i#)gZppC~52z83YP4%>wIzPY9TwY!65|AaRA3F04zVV`;R_p(n#OL+^wQ)}5Du2pI)d9<xLq}*zuv&gfhzWB<WeE2>Gx{7b<>@WFs|5B(I@BY&7l(5U#2R5l3`~}s;w=_6|{a*bV!LJr5{n{E>9{a17wSe!L1^v3$R@v{R9cqp8<T`_X6>7zKuk1nmD}Tvj`X?Ft;d9kSKN~Rwe(qJ+=k#GVzR%FAlHXkV{VKz^w7msCaxuz3rI+~XqHpjE{~_&WN?VA2TQ(o+tL~r2P@i4air=&#{2Rq^J$-G1Jljgb&y<4eDNK|8sU?+z|1nPbk+tJJ@lDHp;Ge?vXHMECdCU%Mrx#suAG~9<?6b7wXaj#lMe(gehG3s%Xb<s~@N@Fq&OG8W_7_I=LVN{9;w{0gu%EK@BE;JrLcGJ|Xz?p0!T0@5e62@w>@SQsDg8;?Pz~n|+ac{`Ny~|OV%tL8-*5L5U-9S&f3&0A4_V8p;+sm3gnxX$_$J>#^pj6>;a6NQzP4`!`h(qk_`_PtdRcpT82bx-qu~2yk@b=3tGDz+b?ti0Pu*7F{m`wt`_lVbo^=whxR;jiW!be6@!|FHo-_Hl>@&8O+y_6uKc2UCA1wQKtql*se{>tqak^BIc+<Hj@EyG+UTHR4_T!qbl$Y^BDK<%btJQy(#IJ~lKQg=I(Gtf=J8B*UF<(w9F6B`o5~aPY=ljDi|Eu_>SN`H#p6-C}T~pp$n(CF8Jf=E_;HT}xd+2G^kSB)g+S5-ZUTM-?;+3;mF&}7+W#6rO^#T4);DIB2^>hPK`+nkEvtT|@^6iuNkfvfAC6A>y=TWzHcn-d_pzQlMk1qjVY4eNZU3gP`<wI5YEmq(?Wbane&rP}8!CzQe)(7h3k+Lt}Tzm<9ztVVL@+C#u*J|g6`#{t7uHv8jEbXG~3Wu*m)R#Q=8^kvUKY*`hZYlK>-wo|J%}T$V%-_22CG1CkTm|cig*9azqq|2Vf9@La-5z7T!v3IK8VLU%dyG?mO~v1<ydMgG?9`C-dCc|4!cR8K_@WG2B7Z+)?mr3s>{>D&DQ`;S?`?7}h9BHc@~fNf9M0g6N|ktRVHD205YIJ~Sy`|@Z16RF-}nUh2gYN+>RK=4d4l_7Wldq^pL<i<-LyX|*3D(2G2cgqqCe!q{jG9$ik$af{bylc`0EQxymq~~_*&8+`2Hj0`)ZXUkSFjY{8y(@59@DBKQRrBgMY(E#!aQJFY@RYu>StwA=jri>Vy2flO^&o{M1q6D{b0|Z~F5U@{Ii~*P$NVN&e2tS_=0?N~ch{ZnYY(@b^@^vf@5%VIk~GjjAc<Rg!bU-<5*+M|~w;dzKr%c?14#AWO9Tot4$e6VC+-#-coDPojNi;d#2|RS)IA^b7vZ%6<u+J6v9X_+33D-V(SD@p+46$fIU|5C3vo<Z1j$+Fk4L6?wvsOF5N!U2xv-?eYA*!v~bV>KutT73mDWj2rxfZ%5+%GW_-3gldPoYUO|Y=*N*=aZ-YMr~A`8!!-W=)c^jccLP2Czy9>j%e}_`^-u4b8+G&JXvV`}AF2o0hwM)Mh3rl)PR&IwPR>EiL^d=tIR`l>H48Z>IS&tmop>0Wn}@-UR0pynIXl&!Y^WVMJ2@LwAshd)lCzQXQS*}Xk)5f9$<E|b)RN><<O<aC<O<~K)N17FWG`w>vKP57wGO#1xgoUyxgohFwFTKwKXOZQJ8E}wJ8}<dKXMOpAaw{ikUWfs!J*VK<WTYi>Ll_6@>J?H@>KFHY6N)}c^-8>c^-Kwbs2dnc@=dvc@=pBbtBo(P2>&a&D0&_&Ey#BK5`6sKlLzqKlupt1o;U0B=sEmB>DW0;~MoU^&I&s`3m(6`3m_m^%U9Ai{#7Xo75ZRo8+fdEBPt;8}%RZH*z*RXjVJ0aTx4EEk-u9D%pkXPOVLLCpV=wCpRVgQCpM!$o|w$WPfr$Y5>{Lf#iPVk<>9{LuZpmk|U^_$r0o&JPeMb9w*0<uTw9Q4ZTagPPS72B3sF?sGrHN$Z6DU_TV&fb{+;7rWPU_T83PhT$WmcT$b!kRmtw;hSUb+hU7+64{{@NO=@{^O>zZlQE~;cGc^a<nVgG<!3y=e9atg%Z3lfr{+s-m`Um+jIf;6MZ0HfPp$ExH<jd5(<jdqUJPbZX-Az74KFP!2J=EpoJ>)e!3|>N=NnS#pN1Z@6bS(MmkK@>nBbJB3+o(Ip+sI3)E67X9v#9gP^O%1Y4}(LfUCANjF4S7&F65e2XL3!lC$%Wqlk7n)LN>Gz*@Ik-nvYzKT$!4iT$x;nnulD8T%MYjT%KHxnx9;bT$WmZT$Ws#>O?M0E=4U!E=4XwEle&$u1GbJE0SwatB?)#BG(|dq;@2?B!^NblS9c{sWIfO<nz=7@_F)a)ZfX!k>684kl&LX?4g<M!Ny^5K57ASK5}uYiCmmqm0FElm0XuvpInz*hw4MFLw2QBC%ckMQA?8zEl4g!cA{n_JCU<cKiPq^kpHoR{z?9a{FHi|{FIzXJxWd_@29RL?<dcvhLPu!hf@cWhm(6!gUCI}?Wujq?a6JZ{mE^}?Wn=zcH|D!LF5kP9@JrELwk{XkQ-5(kQ<TRsMX1C<Py~4<PzkZ)Es0(Gm&$WGgIxznaTFlj|$kH{7HfSP5wlFOMOH(^fCD@`5pBS@;mZ->J##N@*C>!<TvEkJPb~uJ|w4*A5ecKKOiSj&ythKr>V!ur^!dDd&x)1d#KyVd&t|UYslNkYk3$PMU5m!krz@IkQb6?P^Xh;kS9|ok|&cxs3XZC<iXTI<iX^D)B)sy<UZ8iWJ3eUeaOA2UC6!2U8x<&UCAA(t;rq9ZK%!2ZOBcjKIEq4`c!vveX=XHIN6n4gqnkFXijnwav^FSav^e29tM}7I+06|O*{-PM$JtwMlQ(1-~v=fashIFYId@r*~o_GBj+c(P@Tyx<kHkq<kIAd)C%N^WH)McvKzS;)r(w<>`kpp_9i!?HY7J9`%+ty4Q)sECAX*cAh##`Qv=EV<RI!Wau9hq4}(WjL&>Ab<EazK<H=K~Q^`}vGpV!4Gs$zQ^T>0_OQ=i9OUNs!tH>+K>!};ahHfUWCvTy~khhR`QumX0k`GXikPnb!sVB*?<T&biavV89`S-nd0uO@|e;jwH_o&y%_sI9DSIPIu$<!<4Wb$q5WwN0+$+yXWQlFClB!8!VBY!75+Ch!`a7P{nSD?C(4Rt41AlIihCD$i+ruvaPlLt`!$pgqksQt)>jwBlzK^{U5r*0vKlQ-}%IG!3ujwj!wUMCxBCEp}Jp}rzNA-|=jk>8TPQH^`)Z~SbqBM*a%Pz#d{ElVy!E=P4Imm_;p8<IWAjj4^ujmb@@HOWoLUepR?FLGt7Gr2Ok1T`1A1UWYkgTLBA6|!*{{E}+iR~u~TWAaP#eQFZf(97ie<U7<eWJ6Dp?~s3`o+KN3n*1v{nR<?F=p}M8`5yHu`5yTJ4}-5!W69UZhj|#hiMoxviM*J)l)RWcojQwbXb5>ac@(t^c@()jwI;bcxi{65+?za<>OnTN8hI!=kXo4>NbW|hMD9jzOD#`sOKwFiM{Y%KMlDNjMs7?kO>Ru~p_U^1kiDs8$ll~S)QaRf<c8E5WJ6n$8<Iy*L&+n^8>w5#8_8#>=gDWu52?SAACliu-;>{w?d_q)eXl(agY!`Hk@JvUsKv=H<SNvv<SJxuYF)B7xi+;9xi+~H)s<X{{0p@d*-$6)FXa5xEad#;OjP6kHWNP^oN5PsN=_v|q9&3bkuOm9lP{2WQs<L*lBZCIlc$i))ShHBxdpX7xdpiawGFuexh}OGxh}aLwF9{xS*7+M8`_Ahl3l58WLNSp)Dq-h$hoLF$%bYo=OSmJ+LN=89jM0rssle8oTfnEk_~-FP9uMzz9)Ynf2F=5e<gpWz9xSrfB12vQeRPDlMPKFzasxeeL((=e2bbyzD2%7Jx#tuj;9_a$CD3H_mB^fcT=~Kcax*3Yst~%bvz7SPK_cjCoiHdBrhV*rp_SGCWlcclf%eksUhUC<Pp@t<Pqdx>OgWZxi7U3+0b6(zGO4CE7?r$M(s%MM(#{)L+(s&OKnPSOKw7~Pi{i4M|CCFBUhmoAy*++q81`oBA25UB^z3TT#j6pY9bq2hFq3hgIbwvXjO6zvM1GzY-laAC%HD&n`~$!a&2;BsxP@QxfQiNxfQt+)t}sn+>;ta?n&-X9Zv2~9?HYuQPk1oQRH#d@#Jx2jXH&_k;ADo$>HQV)Vbt2<i*q_<i+F_)Rp8FWD9jY+0ZRy3wbMbCwVJ*7xe&n7x^GHmVA(Wj2cHiM%JkbWSxA0nn=DtzOMZHzVSK_gYWV%_!$p_pHuIVpOgQh-Y5S>eo0Lxza+n)-X<IRC;0{0*!*DVcd~I9oSkaiH)iKya7k(fa!Il;4}<$q>y!JCM^ihK4IMxpP1dMG$cBcKHS%ie2J#82PTfE@G@h)JZ&7cO4ShnsMSezoOMXWFNc~3sNVensp>a=W$HU;9JPa;IEkZ8B`@mv646aD^Bv&NYqBbViA~&TrAvYyAqk55>k?T<_lk1V)s3pj5<dW3f<dWpPJPiI~2Q}^wzwj{lIrSyk(EDUV?~o1sm27A-+0c9B=j0dE2jmyz*E|ePp<W}Wkgre=ldq5u@i2HjbrX3#c@cFnc@cRUbvoJ5QRHdlan$Z)Lwl3Qktb1yk`0|ho<v?ijUpSmmb`!*NsT5)k}W(8KET7^eLM`_MO{nYMcz)0B1f?t+j$tgjyjaQj=YM8!ON(D<YnZA)NW)$+maWO=Tcjd=aOeon~`Ubr&1e}r;;a9eaI8Z<9{4}zIOIb4*#$Jb^gEq8Do%=;eVuW`<ofJ{iXlS$v<-aYZIWKZ)Ri9nqvRsKV#um+gNoe{{zFOrBV'

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
