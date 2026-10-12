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

PART_NAME = 'part_021'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_021.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_021.stl', 'source_sha256': '6c14fad44440201b040bc8c4e9ae2cbb3cc590700180ecc0483cb48205f4087f', 'input_faces': 908, 'input_vertices': 701, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21269908547401428, -0.11412467062473297, -0.46081286668777466], [0.21176521480083466, 0.1669592708349228, 0.48309212923049927]]}
GEOMETRY_BASE85 = 'c$}rZ2UHc;7xq0^Vl@94qkyqrTdc7}jT%k3c8yVE#fDx*G<HD&ONe8Qy#O{WToptVq+<_rRTL0ZH1??1f-Ny7Q7~f4J7@1_U}lnUt#7?=*4pd&-G_b8oH=FAnPD(r^)6Y;RpS3@OU-NccW>8Ol0^JZa+Lyn{ANw`_L<pi+Kf3aQU&tGf0~B$9o*-uVJ=dDG_S!ppPAl%4L-Fr=s3PzgQk`S<EQ)0@*6X4^mM;*KEm%lX39(-)t~wGm>E9m=Z0-tv}|f=)u^c@$nt;rUpci3*2C@3rir?AyMIimGP7<@n$CANy_Cv+bAvBcd@o+8EwIcvga0Nyk~C<}dHVjL2JHXfzCftuLd_pM$gj)(y4ZPCPFCzi;VXw~v;TDCQYtrnWG?%)*x!9~Bl+|HI?sL$^5y3_yM)>U(sJ0Z#`(28lc@evm!H-9N|mLt^mE?{*}}IUs>0{nt@3dyfAXs=gI~W)3Y9;lEtMl5D$C`UXuFE?ucTZSzU`0;`wu=@LiPHl4b{_n(2+%XT@O+_Tc*yVJk7T>+)CxkQ`Z`NrTpoARNl<j*?M1ol@~!j56H{W`%>CZ+o?VM66m~a2h-S(e<zH-cSE^C?Vq}n{RZh<>3n8dCsF&PhO^(W+cxo8>S~`!$4TAFe$)Ef>3l|80;qjbH?jXwI{DI<U+zxR`^`%4pyOFX?FPSv8~O4qdl35@*l*sAeb0J(sJ^M|*>BY*oQ@mxN4UXn-Hm)@ntcv^FLgDy&(;!l@`t~qa%`!~IsZjE*YDQ+s~&paGH?cczR>6g_Ls2V?h>7+B`f5j!4JPj<xAsj^mA)!5c|7=cTznjDPQY-c~>I&l8=+dyESzV`@1XdBEO?N(&$%Zzq@l5jgQnoF8|lwUUXiky3oAPd^utO<;%lMMRC4A{JC7tyoTZI`*Jz8+`=fovu%cl&X=PKxg3v<)L&BSbRM_wj;C>GpLCe!h2~39<#tp5dVaZw%b&`AofIyAlw~%}pOlG)@n-e6&!g|9_+Y&G(0H?a*>!iC-fx_;P2ca%6mRz5AF`ju<(;>#dFcHnrD+^0!;bAq`w!pRy~RTMUWymy#qh~g@2d}J{ucTFJXlZlA24I7As^#Yn!RiX`y<$Ixq*C(wSvs$c(O0m52nvv8Jp7d{@eK>RDQ<_vcYfd!{gj5nflS5(w}^LrI~cSwL5#z`D(sYrgSKkGiCNx>c5me>{oKzME+p)ib#HMjN9LN+<xPv_P3?<;Ok6Pk3^a$cYUwv{i1T__N4Z=rF6k~zQN=98|!q=@5K4LOVIdHJSx!j-kRcp@lcxj-R{xa&i-fQYu8oh-Hmiy%`Y0aEv#cWzXSV`3weBc+UFSkL_V%pHjn?5_U!L@%K5W4Z)d*^w`cQ32kCt79i-!Gz7$?a?IX9g%+TjcX@z^~JWsy3VDOcXqj^5|%Vob6`$r3-$oJi!t@q`lpHewa|D+s)pH`L1aXPk9`BF+t_PhN<>xKQ^NvfyjTRj4gvac9?IXal;qcXQ$xV{`|-!7h~!+zeweiP0=zKiOk%<#!J_-S>hK9<0e=M26hk<Zt$;)20HS#=-vU;4yc_8Vb5{LbUVqdN7wGr2a`zxr+(Z}#z-nI1Y{`pBQ>>5x^CdS5<qgpO;Q(Sz!#Bv;{ev;NIw>PMf6RF3A`YI)PTFZ;DvO~*;D%;oRd#p7yv(-<ztjmtk>NcFeR@XprzQqH6pYKQd6xm->q9zWHSsQ&VVrhHvYexLKRvi4KG1M;bV<>dF+ubfBoNEx4X*hA;bnfo~3H!0hYpR<CFD?5TN=zaNoomd`kgHWG$IX}BG<x2s_aol$}fA0Y5_o8(ZzI3(@mp`kYG5>r;F5eMM$F(Jw<^1xM*HZu8bmMh1xg_Tw`@%3UY{@R1UoMibOI|IO8~j66X<o>_>$CN~d}tE;0atSj`QL|8`BM6rT=xIT<m3A7)sI7K@?Y#nhtc`UJ?(z%zscnKT&DU+!wzjU`0sbyNcp`gEN1_8rhfifX0+#hSMn?NEBH{pGVah8gI}ZD7AoI6e!0Qd>OZ^vIfJi!O5@q;n0Z0(%O_5dFQ+fy>q&Ax=U2PDnU3qxLT3LrgKwRYv5h__KPTT>`#$e`zj{gSAtgWK{ObNxPi@_ol7C{~F_w=z-HopU$xqnV_6b<Wi~NSAX<b%k9@@@+9{cs`8`t-w`+Q#E75O^gePJ1mqolj!+v^?W`Rjc*!$aq5`-GzXK#}ie+z-H)cVzLpHo-QJ{X3{9?<<P-117&{Kag~j{WtY!-FJGeJmaDB<um1Yo=$H|?PE{6&iTzEdEbluK#`v?iLPIgpXFPlA56Y7=k0KVe=dvWqdk3bF4yNO`)}p(KA~^)Ne{i>ET4{BwBOKt>_3%R%eHg*m%09DD^mGNV1sk)U*d7ny)E7ENZ$9U{WV|uvn#cOb)rv}!EcpL`<$Zv34A$v5{)y9QvZV9m(D(=cC-6#$u{`s3;BBG7>E2^_S@V%MEzvVSZDC-RHAWWALoA9L+?j_!Sj92cAVFF_O<KhtPwc||6CZiL%@B5FXtYi>z*b3YifTvDTniOcad*%e9PD2q_dn~FOKSC9UDvSrukCL7ZFsyz#8Wa`LSUUT+VD`Imu)9(D%J&e8+w!`L@<^)DFtDQnXIllFo4c_FcyPTT(h7H@!EFC*{t&ynjnNNxtQyJ9Pgpk4>U_T9eW^f9DFr{!R0>eUv<ND2<;YKdBDY)9$}JNAF7qZ|vcD_d%G^zem2({exhx|8Xv-{hPzozur|cJ@h{AkBat<Nk`c~*qE=wCwB97GU+gvAJN#bKeQwrg#WQ|f0&fQe&krg{;<g36K32WCMEH4wSD7M8{MBuNwJ*2x3h771z%fdwf&VdF`BP$ZT_Ktl=^n%pTn0<-r(!4e@G7JM{+r*FYe>>jimEc61TEnH;~4gG-@|rmlC(IkNulGssdeC?TMSnSL$@3d`q7ZbluQ=Ic6-4L%COrMf!Xxb|L%Imu+KzgJIrTJM~aJbiVv{vuN_~rSknqVhEov_SMp(>({Bg#I<~#@t98gRqLal4Zgi)NuKYv9vOOHn_u?471z1^)$C(GY<=_s<*ej-#y95c>X=`7zmfPIkN-Azxct!t2Wh+|F5&vrn0A2j?!V;wj>H9Ae!>dAZre6*PSg3?bzAP<Fj((v^TOtNERxHg&&REDHGzKqpxbr5uk9<WCtvb-P7LC5QnR=m-;iv*U$kGszNjc4`z|ScY%crrIR983^6ie5C_j+%PuAi6x$h~uo>&t7IseE$Dqot>f$viiXBx|&-Qk?U|NbfO_Z+h>=zYoIhkeUJ-nS(BVqI9l*XQxy({)?(r2{8uyjkbwoHOJfxIw;>R-W%K5~p&0;tB3wr62sshW=7!Po#332@}{)tBCzf<!tu7aXl%dcD4qVrF<n}H2X)gxL+K;7xccA8^-Gbu0PHMFU~*zJFO!&|4liZ@5%Y6k5D^n`vfInFz08_HLUM)LVxV{?omCZz`t_zzLa%>)=ed_5wB|r{W!l(NxFVozpTacTJtl*C|~y7nr+C>*~j-U4j*2368ad+8IgC|L+4BByLg;9{E*+9=V|LRSeJV#9y(t>`>A1_E%LL!z&e{}@TJ^I)SlXXqMXo+^DhiAth2TR56;K)5NTq6+J{&ZK4X9T09pr~qfVY-zdhEq;k=IYO`-O&B(!Az+81#=FTUe`jIVF-i^fBIW$Y6!#^}d`J>Jc5UQ*ycd|vTo`Fb*~Q#|=|=21De_%dA1bRY8Vik0VM{F@B&D|e%PyS5Lv#=l~}Y99O8Z(HJDuwSb*?ZdTwwdTv0>KvfsI!5q(jDODgbs{NW+doV3&)Bb<&*fnMT<mwF{kFDGHv8H>S&DyRIIcW<7(X9~f5iEXmhf|9?1!CkdF(g7%+L3*Uv<XaWgq)zZ9l2RU1on<MZ-SF9(RfTt5vDLq`65vFEsz!0P-zLT^_e_XW1`$-o^WzBHv!su-~x7rL&Lyv$n6$e0k?Cey)psg)QzR=kLDA<zQc7i*vv)Vc1t#<BoDU+H)%GABy}vC&<_K5AuQ4?Bl-Jb~2yG;enN0e)6YSFE(WBeK}<X`vKQ;4EaZn@IETto9Equ<(z*wIEv@RDxP--7IFT;idYvu<NNdj3k>B*vp+j$@Q)A2y5N67@5|rc<NZncBEEk=5R_q<7u_H1q;@#qk8&1rIn%4~bvxFF%fb4kty4vQ?h3kY$U}eT=S8vJTn_F#<n*PvoIjfL&wR}HBY{nLzQ=mOFNf>r_H2WHwkocl<1ZNe8M!>){bOR;AI3hO=g70Xa`e8GmB_~pcx3S9b2spOX%auriS^|Cb0_fpXZ{7fZ}ojb$F+KtkLPj*qyCL~y%>Lh?~h{pkgv?h;rzJ|Xuo5PZO{2LgA#bY@1pwyOKeNd_Zv*U?4Lp7))`Zm>vO0xua951rR%UWrZ$&@b<;Nb4ev{1YN6kGpP=nOoiR1IobR)EJoI(&{cKD%&cD8o=dWir@3Ugw;r!gW+`nT24$<*r{yIbT3>cG0$F+^8b;%l&PrfxUh<s__vr}|lF)zrMXFJGuj(T#2{b!s%&o_zkXa2?gzW+M;(&<EA2fwV#_1u4z{q%)A4*M=A-?slamov8ymounAI(^=Ml<PTfHT$D~<GlTc*$--zO#S2^#m|BFr*Qe-wjp18Zfx7Pg!AR=<XdL-;QW14IbV(@-`VQ{{r=M#J(}|uluhAzx|sT1iS~kDg?wwLxjcTNJ=tG4jC|*iLjFBxbbqezg3_EHbS#cON4H^rVJ9ws-ez7$qMNY4<TdAy%A)%KWpCv(hH<6+o?>qq?w46P<U7ZtQa{@EmgMugkrl`FnZo;O_|_S*G@j*wZ%)y1_P#hx`4<y;pEf#`_W72*zmcyjyPit*R4Vg4in?@KKd+sAGkG5sb(Zs2c+vNjph)`twH%d6zIApAjUQ!TZR%fJR63V)rUcKsUh__P=zM8TKIf0Rd4}^HoIh^^jR%Ww5I<+zGm(!gU#5Pv`mg2dL!>7kH+V4bn}?j^eu?bG`N6};w{`iOe-9to4gMJNrJ!wb?010Qhp!9P@$q`!8k)eq*AD70Yh-)QU)Z1fadcJc7fa+vT>lxz4ef7<Y=ZjV;`;me(tW)Y+2FK(yh(mN`8i=^ZT3T=>A2QGBk6qsXGAUbza7K#VrX01mnsoe*xyj&2=&)VcV53D%Cf&{C;Qs-^N2EhUYlddx6bOr&yyoca(?J7I<C^)br<_C>~EY%`SJ;c?=K>rQ9mn-bEy8ZPY^$^*zI6{sTYkai_I;A{o_3ES2UvWBYm4j<44-%&Hk!P^5wA(e$KgbG<*k-x8avgvp<4->D&4|uRUvUJM8r2e0%0GI_{aryk6|=hjI>6Io4rblyBeJhyC^WblsFj|9&t{@9%s<<!JXKPJ0bLuh6?Z-h7vEd)mu#{>C=cJ~saiyzjM_M1DSx!xKk&-M722AF_noxl=a%-bW5UbBg^)9&aOi(0ZZy){ULG{JycgZx4@Se|bK)^UzwS*^lLN_W7hyen#7iG(N-kbN+sR@-11><V)d^oWJ=Nm9O+J!|TzGot(d=^igWJzER}MJ63Z3{zxu=)IDyu9n0Y#X5X_St((>zK}NqvxkUB@x%_R1seEVeH*|d{@?+8|U+#Q^=A&iDbd-}ozO|blJwI@6_u~8=-Kf8;>C<x!e#~*ocMj|rsrQ{%ZFHX|WsaeCP_~aC-+pZw`L<bu`8u=Rll?2DIDc&RUW1Q($?q_)kJ|^6Z@V^&d?o8Lm2chNf$P8Cjpud0C%kTMtHSlUevzLaW%Qza`?hzvoEyJzeX@>`FK;Wu=M|BDoZ4spLvGh?uTN6>5qad>y4>ONwq}xVjavUb9q)`Am1EnQPQLTzAP4!UbNM;R)+F+6KhAaV`02poXKMnNvuO@rH+qex{*tyvvA;Ky%6E?bn68KRu+{AE`;6+RbnQUp$zk)^kICi!&FIMW2@5*O?OdMkpZ&M<^PDh$@-0_CAm8e{n%9M}sa#HUeJ-c(4|E@A+v36Jb#(ycTQWZ6_TSQ;{o6IE-gc!2-{)?w!Ty~A<SUL)-p6jP#^vwoMD6LEdxOr;w)w9U+%GS=--p(r`Dfky8~OI@S=?WzQ~CE4o33;I%@*9wBR}Np+$IO-JJ;~KIQ9zf(>A4$@4S1Pe0kO|e*U>}JNzv6M^rt?{#GvMUJ1S~_#Nl_osBEWx7=^Y^VWYWUzav6=la}@;p2{W-OK(W&cFA7d`s_g^!qW}#(A87?-y>L?l)-OSvJl@{yiQCz5EjOzWshr-v7;fkNa_>FZ(|(=5|neU(oxO+t<jqjJ`<i<J>TU&-Y#huK%<L{65PDPcG-q7kpgbaeRNUp+1*$cMti_S^uN`j<lf``+57goH3ht-@Ks)`&Dl8`4sNHP2UTx#{TtfJbs4ErS(k-t-|e4wN;`%U-Om9^9|+LL*He;+Dgh-UPl;wn|qT4y>AQs%b~B2y)Xm*Yx1pC>n8q}FMSYV$hU^R;&N)-q<pDxkHNRP-HiV)-+t#49#{V1++U&3$+uOT!1XW8L_Ygc<$ekO<=gL-<9?s`#}>VBd-x~sBgbs#_7BZ-@O*UTap+x#fA0};hwE8Air=>>Jj?w8-{SsWg5H-xZ*qRkS~OmrucHmV#dTA>-d94dvVXrGkB5L$eE$@ZX=s1BK)FTr4LQT**SLfB&$+GlEpAui^}ZZ((xD$GwgSg3y|0ZE&9{X(xZRvfdHwTU%l9=Qhq?S(Ba(Pr#c;oCex(udM*pBgKi=em6SwrfHs1c_=cRHxjIGYUuLwzD|G_Nst=@;|d7C99miw#5d)&^2=WpwMn`>13fBE)1oq1dh4dv%%A-fIZ(^hbb>ZAGE_%!>Lyj@fuDgLj@be_TM`Fv|FO5*Vx&;1MEUa?iY-nR#@=6cp_p2Yoi(cn8PeHX9y<=`cTaU~a=xuy5Dai#h8;6;4gN8Nef@3WM~v*z0#2aqrI^5*#;9K_|^e!$ng>Bs0k$re0^%XwIe@86~krQbJMg9ADLQ499{{^Z|N1pC6TN4`AjM}EI6cruq$vkT7m3ik_qxzhA_qd$Sq*AkBQOg8wIik0K_z7*_j7@u-M)-8jN@oDy*4?o~`n5ayl&+EN7|M4WQf6pO_><{Do$D!ogri?nuz9-sqF1JIUHT)jO`oSo_0+&B#D2-eD`aXv8Exmu|`LVtS=hy6w@qC^89ll&?a{Pb!w)>5FogFhjLtl>NNd(&e#z8~*Pp)u1d*t)?*MDXhxAuY@o{#Xgaa-(n;O|+Ycs(vWbX)Hiy=M;Jy1o^c^LQyAw@Y<;erQ?W1ohlYzA`0()>CPHeZx3W3V-DOg|Ceh&3CS=#`Sqxz~zrWN8?;sSB1~lxs9*qxc)2aDjCL=QjmK~?`z|#*niKEZ!0`@TkmW6nlG;_jrtUF|MptS*Ohf84f9=kbBEgvzBb>@zWr&bbUM#I-}AU$=fdSYIl}$h$;R(Zt;<*R$5ndQ;p42!Q}q4iEV#nsAHLS_)<WgB-q-rw>}&m7T+V&+i?74?ZtMNx>#)(c-?#F8-N;o@T+h4gKP}Ja+jR<!6J>2K`Ih@l`Fi_Q>PP3d_AKZB)SdFR_XF)~Gr2xLjUr#}wTI`|+B4*9>!$Th9`_e~ZQU&PkF$^KiM{ZY(Z}^f^Q~(SE5>nk<Cfkp9#`yJ)+TU1_7%>;N4NF9wy)59>)JRz-@H>N_2XRgZ4ZCv>p-u`ykA@!#rY3bal7Gt4{7aAE<Z1Z*V&;Xc^zCE&gEc#WqI?2`wPCdztVi?nyp-aZ9OVHWAKaCqauF;=VRY!ee=}dYx_pcSJs4ZIoSVbzJ1MF!?<-8+`gsvwQ;NY@|q<)9v+tG>%-JAx^ByB=5zU2_qBba=4<PI(SCBxWIitTGunPn^R@kq=3CZGG>jkV)!kbLALB>!r8Qn$4)$r<{!R0>eVXPgtA`odr)VFzx`&}(oCSHe^nTI)6TW42BSSk_UOh7ST03aIvdYcS4whF>48GP5nr~lK)^J|ZtEUEEJ1@<bSCurJm*v$@<U1?8q4(ZokNNx_^{e-}9V$F0U-1axe#QRBQsFGWC)epF`N}IdZqEv7{P#kge&TWp&T{+z$<MRp_yPR;jF$s%QN91T$nVD_6_Rhw4`Tnt8hW0jy%%JA`4##0=X?0?g3>zk``Gz&IsbAwe&6%$^0cpYzN*9Zx%`x#uPbkV!hXRmUS}^&BHvnW5Bbs`^?AHq{FL*{okqTs^A}Al_+04Y8Q6zRqvzJPE=hDhVSl`i{hkH<d!*h+>3O}DFMatt{~jh|Dm{O6J{rX9OV{$0Z_8LuzU@&v?2BqrzU2i!hcfq<^~Kx#+`-iEns4rR>kC)*P2)=Q|23{&H0I-)#;xX?$F1dMclJ&5Li5e@LV5W$`=<F@<eTQNHGdt~-*jEleDih5njdUvH|_dn%iqZLG+ie(-+Y~v^X=R|rt7xmo3GoNZ-4j}^`rfpQZx>f{CGaDX+6?>^Liu|9N~P^dZ+p3^-d}{&H1MFSM&e1{ubOL-@LETeDl6SDR{`fX`iF{=6#FhRSABcXxfiy{=fEPuPQo>=ga#;%{T8G<yZB{H}7LL|6lvqR~;St@uTgxHQ&4sxBStQ>uI`Q(0ud#g8h$i4*hu6?t_Ya)BTb1$0S4jwfi#7H{Y*Gua`RX^Gmx9YrgsZ)be_jq5ZY{T+RR2{qO5t4*h)B?#DIXe4nnoj&T^r4?hRceDm`G=j&8%f79~{%{M=<uoRwR-}GEX^Ucpyq{0k`e*71$@9@pfd5V0~^Bh~@ZHIoIYWoe%H$RVZ7XHHZG(9)deDiZNXW<`QzUld%=9{1IISc<Z)L-*0uAcOJGxK{9HrHYN-l*xl3(YsbcVTlK!TF~5F08Iz?3>;LDe_J4fmmHfBj5NwiR|jl$2GlwVsrK3eA9a@c2|GSH^2Adx`2Jt`!+?s>3ti`H@|P=bX~;xc#l+jpGR_A&iSVIe<Zh+oNs!+Nb}9_7Zv53-Y>Gat>%2w`%6x@qwJgBgDUb(??E};PICFC_o<w2>F|y3Us>GGuy1;gOY_a|aY^oHIp6d?nB<<rzUlojoBL(<P4B1K-1+ZU%<r?w?s@E+-hY$bAF*$GU(W9SjD6GlcxGRFAJ6XooPE>#enr0NeLuzh1^cG=3GME$**Cp^=yZR>zUh5MrAiw8KHU61zoqJ>Os=2t?@Dads?mEx=D*jIt9_Kk^V#@!h4yN#*f;%Mq`g`j{`+Io-(wc}roYEjs{3*|roU^}eDmKg+pGI?zUl9#oz>^CZ~A-fV&C}p+Di2x_Dz5HtyG_%r5~T#--+95Ril4b!2ItI6#4ppf8Z;_zdG^ghYu_jny7aoYLt~+rSW5Q|Kx-)#ebUq_dhu?vGxD2e{!OIi+2C7|KvoxizFqe5vPWiTAw&c{8Jemg5N<1-k?T83H4S<jd-Z|oT$ckYOGLW6?6?)Xb5-}I2gJaEOY~S13qt2W4Riu)mVlQyb>XJEkf`*=z8!va42*WI2625jZ`&K)JRt2pc;qOIHblAu<*jv*s8`h=ytHs-QaEDNa!B0&}eWpKJQf{Tn)P#I}n0*A_VV32#$b8fg`~Cp!>o5z%gpfQ{x*oz6H<0=WoDsq5fc@0Xp`@=K!!DbShZrG#yXGXQ7jH?1Rsfz~iA~z~jMV5rRiTM}UR)2MZmb<9_%o^eY|r!Dpd;b=(`D`+~oO_5ut2LdQMuS!hpiPkipK#u7CatFcs#Mc^gih4{Pxya+7gvy9I{(D~pXa3FLxI1oG&Itx4#JRLd%JRLk4It4r#JOTPOSm-#gP;VXE@LA|+9go6ip<X&3j?Y4e>DUvWg$~j2V0;!j2s{X%2dWXL#xXTwp+~{7-~(#3P_JKI)o7wdrWzlp-jCq7OYmp$^I^zo0`82Q9mo?QI0s%3I0w8QIvTtlJPq0z+!^Hy{zQ#gYV?7w1dIBJdUuDm1a}Abgnk141mEk4^Q(+=6e0Kq%3q3OtORd>ZUk=t?}P3E?*m_l9t2+pzk*%>zXF#l!FmIH1N9O7waPQp@P#hYaa(*A`i1Ui<6ZcBUxP;=rw8)B0DD45fJY!-@M1N-RU;U>1}tI|e!dvI9J(9492}xX7&IBW8~l|T-fDD22<{D?3hoWILB9dpz>`onKh$pxco}pOcoOoL;n-_YuQ2d@=oIjL@F>)66zV$)zTj?Ze5uCA2*K^3eZlR(?bYZ2?Fa1(7XD;4yukhNS;RW{Uf>04Y=fSHt^<qs2|wQk-mAt{HS*MOE5RYS4)hvWgkX2*UhrO&<BsnhMtLFxZ-K4?Zvh8DCxQdOgP}vfgTY<UhF#FEUEp`axrln~LI^$ty#_u6eg@40KLZy)uYwD}KSQ^Ge+F-b27tGM1EGV#f#CkoF5v!PtM1&a2*Hh^?ZAz}t)T6}t-!5aipNlEgy1%6EL3Br3(tdZ!G6#QU_bCA=t%G+unpSFrFeb`*5;t#j?hoRpW^r(p&eX`=d$2YP%rQ(@O<b3m*Tl5ILxJZe1}1IfrV}d3k`KCp1*=apew*3;N{RIF2&a+!Hb~_!3)uLg2UB4dZ-#-L%qTC)bLefD6|h)R%4YKBcV31$eD_~KHx8*eqf<r>3A+a3-ts~P-C*VPeKUZsYV!dJajTx<gCN@gpL9CL7795I|2C<kTV`S6g(99;}M>^wh%fAA=n4ujq|sGMLYCWW3U?i5Q2w5M}kKpe+bkQd`S&AwNE}!<BG};)u`;kTFZr5L?!%OXs*O8Lhu~u3~+rlr=}XuCDsQLvxo<1zXxbL!S!7DSij(y;@H0+1cyUI!J-ZoQ4gUPaC{LLP!FNg!J-aTP!FNkaC{NhP!FN=z@kidlq>Wy$`f%J<q8b|i!xnNuF#7p?;^_7*cYE`t2rO4@kC<%Rbmz)I1H+dK~aZlsE5$oIKGJ6sE1G)EXu5pa_gfXenmV-xzEw|J5gqJlq>W;$`f%P<qBN|7Gvf-#*GNU@1qUg$N9ex|03c%&fgb26?zFQ)DJAi;#GJeuHt7x=j!+hK8tbeiLvJiZw~Ydcpch)40I^?A=*6@8U_vpdqc-d#q(`2+Cc^fK>LCNz|(Q;8K~nBa6jmD@O0$&!+F)l*tm+esExUI74^M}x;{jIS<q)fAEU2CJVu|b0&jsn1FwSG5Q4=uMqGcybtfDlcn8!6?1TIr&}ZOq=r7P`Qt@0CEatih!F8dJ!H;ncf_tdkMU4-k^}rp}Xr)F?Xf<#<HN-Qo8qhjmk<$Ws)xaM>TY`mF(Q#XR7Fr$rks9K0*dT=9fok-EHi9+*i=3YLp3sKi4^Un;XmwrPs^eTfLVhD?O>j-*G(uEIyVQl&LDa*!yQxuG4R?g#s?ZwX8py8-tqxwHM!Xs>F0AETm_@w7&xI}kuK>4(HUn2s^WRnDki?oSF^fn>J0+uy1pm*4kClXDieo1s1owb;0gE~m;+R6`gBO6CK^ucb9ZI7fLO0>~A~vBOLOXy(nSY`Tp^L!t!HuEK!J<qF<qBPn@<c30xk6ik%d0u>sgWYF9+a3x2<`>d#+s-@DHlGb&|n;2L@??hv>jNKSpnr%KtCKr974H=(DnmS=36LNXcWp55ruMvdVs%EW2qYdAO!!7bN?IX`ZxULh^09HR^S%U@4!M^f<>7nUDy-48b24Y8hJw7>Uae{i*YQ*b8Bc@a9iZGMjwlQXb7zdjz=GKf%XD-0oQ{zl8WbBWwc2<aC4{|xH-5nj@=A(tO|CAHU>9FzB}r$8slX(+CuOO`0>ybu;{z8=s%(R&~GC4q5nL<ouP?f52$uM5iG7T;`&=(;(6Bt+#OmMTo?J>p^4xg&?IQ0R6MT*i+L|X@H^0b;C(m;!Hv{=<d4;8qDDnE-iY-PTB-!I2*C}Z6~GO_A3>{wKLR(0)&n;Ow}gHOZV7G$Z47P&ZVhb$Zh|@s&K3JyHSV~uC(fq@v_7~6xEZuAxEZ)9v>Lc6xB>J%a09RfS`uslzYi^RVSXQ60{Sahgy28m-2vahxd@I?<D?qV@WgrEg{Fh=f-gglfiHv4K@-8}z-OSb;4|P8(EZ>O;52A7I2v^mEXIi#H@`tkgGC5-B3GPG2J`?p1AHEu1U?VG0zD4C0=@@54Za6{4!sC|4t@=Ff}N<F;JO$Sl@NlfKpTOpfNMaTfNOwjK^uc>fonoP1lI&th1LUC1-nA4gI&Spp%uX8!DXPOz-7RHWA2K+`5PfPANm_OAN&;R1V07ehF%2U2LAv(4gLX~4LuId20NfhU<ddp^Z@uMI29TLP6a1GqrnN_IOu+G95@~t3yue;Koh|!;3Lpu;3HrKnhsXLXQ8>^v*1h6JK#&;ThL#@x4=)Jh2SUPmr!v{d5O=0|AM{;79sd8c-6pff!~GJ1=qz`7yP*zpQ!N}v<<kO8df#hLOsB3@$)ud58Zd$!EcA3wZV5k!EvnknRYx6_#XI~;MwZhv{;Q0HL}$>t40P?0Sny^-jCc2=wfghG!?oSoC;nBoef?F{zeUd=rrhT@HFr&gy2Ag;2?zHh0qZ24K;45aT6i<N9Y~!k6<T4@K0*IE&5p1GA<l~OF#?2A_TvJ_Y?RPI1hRUJV?#&q{cvm;Lp{l18oHD1a1UwfDr5f9R&6O4}i`C4*<`G?gY;UheIEO!@&>L_y_7zg7q<2gy26Bf*(M4f**kG(0O1xcrJ7hco5oRE{<D(V+;Km{16-t-KwkeR-BX2K;1b8q753O?W|A_m*Qvag8M@UfCu2a{c(;j)c9Ws4#Dq~;1FCE`a4*JU<rC3EJE-jcv;{_;P0VP;P1f^Y7A9lj2dI1<G^FVKG5l4AFw}kHP|0K2O;=7gy7B42yg`IAox?Y{_WN12<-qC<F={`kJ%S!uba>Z;G5t`s2v;$mZ5XOGI%(2Ab22-GaMoKGiX)tShcD5s4+^7Xf>9okq+GjP6t1Q9s@rGKZ1S_egys*>Hz-?&V+6QXMztyzXcx#Z-tHmk3yXVuT<lAHP%C4fY*b^L9c_yfk!}dz$3uD5rStT1g}8|j)WcuM}iNiF-(n#YK%q*{sFocEHoAzi|_paJr4c>EXIon!BwF-U=f0AK(B*E2yUoqGZ)t8P~kU+z5u^K+cig?;Ez;o>caXPJ`4Xh<gNq@-3V4BUjNo2&f@%pW`kqF2cQ|?1K>!hcwN-mHVthrG*#CZspub}%XIy<41Fl{8(p6Y{v36ii25qv{m^0H{ooL2S8xb;A+!^CAvg&7nN+;a3J!#}mx|Y7!Ly*BNX6^5;AzlLrQ$VRus`&3@aIzTULZk@2&s5o7W^Z0vsAox3%&{6E)}o!f^R@~gKvOuL1VzTz;~cWz<0oT(0kxK@GEG(RJ`sB7W)FBe@Mmq1i@vXuchLBh2XcLFTo-N{{`<Z_%Cn)^eDIh{1Y?*oPf3yEZ#X3?-~w=mIV(7H-(l1Hw9OMz74JfE)OjOE)Q-1eGA+GTpL;%TpMhGmI7PAZJ_Uh+kmG)UBOepd!e<!d%-85AA?VTv!ETpS>SU}EBGAvG_)J|H25U+3-C$sDK+}5aYl^+&{N=3$Prvp;w?f&gy8oPf-68>z!kvnK_ze}HK~gloe_e&Lc4*xf`_W{Rd1IPt|kA!{uge=|H*U^{r}L-{7vI)xcYAfsAUzsl>1fh(xU&>lPN*JKy!%Sl1cvuGid#g'

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
