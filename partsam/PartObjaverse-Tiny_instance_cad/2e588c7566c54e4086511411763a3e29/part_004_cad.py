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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e588c7566c54e4086511411763a3e29/part_004.stl', 'relative_path': '2e588c7566c54e4086511411763a3e29/part_004.stl', 'source_sha256': '4329c0d8da9569a450550aeecb642d37ccfcedc1afb1c5a6d239351e0d985523', 'input_faces': 914, 'input_vertices': 508, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.07964858412742615, 0.09971195459365845, 0.09345616400241852], [0.1499962955713272, 0.16430191695690155, 0.13214322924613953]]}
GEOMETRY_BASE85 = 'c$}r23D^x~{J-b5uh|t^j>t=vY$;0|OV$WwOLVeELP)lBWGUH7_AJM)2w7h5%6To>O7<;u5Q!*D5tW~r@BN+TJg@(C{jcB8b<K6(=hK)oXXcq_o=wf0q|cDwl0QYQTWuR&^p&?Pd&^<vw+43YH=sx7uKmmP?mIZf%I)O#ALVDwS~YFnF2)*Y4UO&6wSVV+vDJLBHM%_;TgDgLtxvxJ{a)|=TAzMhy4rdD*L(HvdN1$)#_N5%-uqng>GIE(@l`5S#`m7@fB7fdy;BGt>%6YkJx1zXPPG~M`N@=8o;<wejm<Xw=ZbE0c=%H%4>s=Q>>rG4mh8>_Ck{LNM~)TS<ox$uYvlN?Tg!1$Uv!Rd_1!Lc>JQFwBKdnKdvmMocG>?@J?DEv)6Pl$<(05=o?lH*^5&61#VyX~3AyCIk50GVrmx~_&hf1RE0VmqRkozFe<WK?=R5<;vOBqder@M_1GlFpd-FiGwN4%!GT1qP|M{onIKy_zbxYly<jupaA99ZGd$)&Nw{$IK{~be|^9zm5lH|?9*9JTL2d0gb^RNDj<lq17e2&z}mE_H>&a>tEe6c0joBL)Cl;738p!4^Ful02DNY~QN{^3(MlDxTZM|%0*g^Qiv6>8ki$%BPjI=?HFrC5?T_pj|G$FJVjxo-Y1XUO?f+2HK&D^w>bDlgr^+22Y((YX%cMl0oaof;|U|9bIcZyw3?t6b;1H=I1!bW7BA3)Y;T=*|5z)<j*mP_tcf{3r4|pTi61Bzp5;-P8BY1L+IMeZSB%$(#GPG?e4Nu|Fm1I9*rC{k`#U_<ngf&qXKqzi~>=f6nvH^$Cw&o#@R&MV83*8Tq!9!+&nd`4`(S=M&r3xelRD|H^T?E_RON@3<$?n+LK?m;18lYv(#!Lo&oU=QF*ha~$i<SxMg9N>@SluNCY3u1JxRP97<6SI%?kABo;P^zle%e}CP7<vNV45f@dS>y%CO=Kg6vN8Ok3{<?BLGjq!4A1fz%b1mm-^6h7%%5$i9Jvq<!HpuV#Zcmaow{8`b^Gux}&&A=kaz69wOL^_lB+;8|IX81_<k9GI{=h4;|F#xVKCj7hp}D`NJQu!-?WF!}JtQvbxoFoXF)Cm4P1JK?_4&}reUt7;{n<RD)Q6Ez<oB+Y=RMT3O_DeFf6-EYZ+oc+f@c@UdCRkwbIrAUYI*jz+bzdA`lI}=D-)8U^6t+#`v-G8=Nvz>W>3_8_pjfW5S5>NbgTEi`_dhj<7~<#pG)jW@a9^dn|ZKFVdpqnpNBUcjVjNf*n^4QJX~x_RCx}~za-z=yNq-HeAmw;cyoO(n7Oqvhx5JqUI=E(yuo3oB65Gf+~!=La7s?ekGGNfy<yHoZ?5kJGY@=rGwQt%*qM8Sw>(FVQqPn7nhcC8&*2$WWq;~(t8l$UZytQ|L{xnquG3_Lw_JrAG)wa4;e2hjM3uL9dPz?G91f36^ya?d$x<GupRK3g+u$t^*6+;{ym@d_>!|YJA2rI!{k!fu*Ef8=U4l3Fjrt>ezuaH1g&b#X7WtkVV>U#UPs(lh&`i0`&*gQFZ=D{T;LWw&V&+zZ+H&7%w}j3tl<Pn}Y)##f=*_MCv*bEcKU=MnoIKR5lHAt=%M-l0wsX?tO-nl8tL+?L@so0V>M<=3nrnH`de8UQIXTah-JSdG+i@wun`?W<%!4mwalTjEGoiHw<DLDfPqdy1#ysfc+TPImS#zzQwH*@tx=FmZJoxvYiTCDOe)PSsd2rA8sB#is(^8J#`I?lI*}uhm^T0EIhwqpBdyH|8<FnF9dtrDt`QAToIoCIsw?Kk7_g@*5df$9yf9E*i$=T$+JadHnF5a73|7foDkNcjTG+Oe8xi>~V7v$RBHgkPmw7nfXx<c~eHRV3FnvvkmwOwuI;T#p^IJCC|=i=md@t)H6S76RD*}uc6WN$gqT+4~Jhpqit<a?-R-1g+}&&u;kd&zz8kh||4+E@NS^#pG@3FeaPsCjr*N>q6WzFS+$@5u8~9_~zv_vYc)bgB2tLsjGCK0bC!p6k&qCGT~{xxSIPiSgb%+-_9r{c_)hkepA}8&cmN=`P2iU8L=$V1~D3|1nqPx_AFOJ}Uq2@6`L{k@P`1&&ShCJGsh4IiJRbQoQ9vbGKgA{#wVia^D8MD(xQX8O^nx(SDY1*>O2u@kF^Fyr(qR_muW)LRVwtJwSV2+cR!Xd&X`5r!Ohb2klaAuLj;~oanvpfpQh&y}93aF6zEVRyUJ;>j`-uhw8+8b6@7nsrSqMKcA568Mq>UZ)kgYPnOs#^=z?z@!mYrYC`J$a;xb!IiD@3<-RZPE&Cron&K@dnrk@;y?asaOO_8MfAw#v@3fvFck7v3Ii<W5TOi+CSlV0qo^o^EQ`+zLmE0)hZjjVF+Mdx|+cVn#waOlsyjLE%PqceA*Z!TEYkOGxgOLVO-nIXt{hIKRx0Ag0*B|%q25%lX@o)5V-C%$mZ^dD0X9se}d-HJKY^nFl1DXGn>(J<e)CaeR$nUSeb)&aDXzrGWGl%5Aw;C<SkJ};bB&|2dwcZH4bX=Z4-()$?j$fo5#(T%jdGCa~+>z(6Z%EFkSt;3{_KfD*o(W&9Cjb3`RdPPL$H?EKJ*>I5hjrY;_f?7<C-je8cizjI>o|a!yZtG~6N0N4x5zwRj-&N9x!a#54@_Pv<#I_8x&Mq~xcP$7^7rYdyZPlmWq<mKng=_)FW*l;!ri~=<3j2^H}8B_#+ztYxW}o!MV>d_BbtYrhowEH^$fXh+`&!W^64I5%k9QrqjDXeG0$JeAI#sY{ogd#hyIc8_9s!f*5|=rDkVqdw2QR8?Vb<sN9*Xpl&J5e{`6nox6zyHa~F=4_otg5&AiR~JO*M%rrfVQXl|B=NU2Yy-C4I-qPJXWZkA7Xf1`YAZkA8qj(O7V85@@nRsPA%=S6e#c?ot~nR379QFHTojKn3U-0yjJbMtv0u~W{+s82LE>l6Qp19Cn_eWiJt`f8H=y)^YCxmh3j@198U-gmvf)}(gQ9{pvm+!yL?&CUAU`f`Be-&U39m-=7xH184eH184J-*}INSAHVDuk}7@5AvRJbK||Hx%plTu3aIy@!oWE<GmT!vt8N&#(P<F^SvA@9g+5;@!r=w&3nK7b!o?$?G19XU1625HbvccZMXEuu*v&eyW^Y(O2~UJHCf)<Ivz-Fw!8f2UXbG@caZmiw$n5pR$i_%?K;iP_MV#??Y&630dhXe@5pte-RR~<J5zJBo#`L+x$IwMmb6=GuWD|#Z#7TTz72)tI7a(fbF=;I-+x-hiHvr;=4smJccmWnXa7l_BijF(oBaZRi@!H{%Zc_QLaSt4%<QKGlCnzw*60WMuV)idKfC=Y@^F)O^88RgyZamcGR@6?SukBO$=|CezeoFb<i0v*<@sma$=%=R4~Az~le{$j3HpzkoBd69f1|${zSTtPt=4(vJm|M-ZuV#Wcbm)p31g&u(Eruk>_=;E_Lr?iUBcdSqW$sk+-`FGahs)Hqrb0tV9!U=e$??v-QO5D(A*q1@Ru1NzsneZ@Z}vYxiP*Go;*VCOYwekUv)l(JiIlpd}bWa-QO68(cBz|30?eL_UHYs<2;%NbF7iS&wE^Rb6hBtXSQ62J<rSaVSGt*bKEJ?dtFrd(Qzs_H^#35$KvHUHU5?R!uXix!Sd4nb;no9&2cu(&2hG1c&Gd>>Lneo(>%>M-jG9bKDXj%Kgl?u=8=!<%X^A(Ma|7|#bEHb<i_}9@akDPpBBU9{22e#+#DATlsYH5F^(G9dm*ZvyX}MuSEI_6JKn3gF%In86(jxU<u&9wGoGxuf8BL?P8ff7_cz9+H8;nlee<LrsP&SLZ@alU?w#qeRBw53$Ir>l@pjG4@%GSopPUcxH66Ft+#JvMpD!lolXIQ?9_9<&+?YoQ&8i?d?H`?Y&^*n2ME2^EQ~&6Ehvw$|i00<}NT6p8+25FFvGV%m_{Ka=cw_C<sPe{qkmiv-rIWqoO>=Wz$<2*<rO@D)CD-?w&bN}A^I4jk^I5?=9p(I~XWV%)^5Dj=<@<Deo7|jV)7+e2v(|NvD$nk`3As6c=kxcJ@1@<P^L?6|^Mh_~%nt^-43V7opw2UD9-P`he!q_EYHrL|YHrR~`mLcd-%mT=o%bX+=Sej;=Sh8)N6Y@yxB47u9xgsiu9wbVkel<lnw#^v)(4Wi{Y~bDH8<yx-Q1i<E;Uw;Z_ZznoAcMf4xdR*dr#-VH4iWORq7ob2PQY?(=|8e(}U$?USHb}?sHA<UsyoeCA1SXH|O^?H|O_#)t1S5&|lDX0-6W1grxqWzo5Cf-r&Feqt_dRdo7pW%X>}VUz(fi8T`-0%kk-l>iP%G1Lt3p_Pef^(EZJI6y)YQ3SYg=QT2(g)6iVo$y#r?`R=ehSG0%S+*nVdxw)Q1b8|h3dp^c`68AX9dXn(gZSs2=Pjl;G&5iXinw#rkg7x>x`O^+`*VT}_<7qk{r~4c0b2K;C=lBcCyr%XawZ76k&~2EMGwpAZr&%wgxv^fzSO1FSj5E0P47slB(D4M#&Gk#}{>J*HaP@0)9`tM6_5*o1(-irv{Tgy}J(YVLV?9;4>23L5#=*4y(Olcl+D>+J*2(BNnC9ksFwM>NV49oj!Tde{mHioyb^Dc?o9ola)2vS$luLd;{d#vj1G%n?(0;w<=6X5zIOck}=|v@{pXjc;)13Kk?I&t(uHVz#T)!7CSwcQDzNGCd&2`;~J03-Dt|!#oTu<l=RhIK)d{Wz2n(KNPcRZ8aT;Hg<xxO*Dq^g`h<LB=4POkS+$C=&zPd^=fAJ^8E>%+K;_FpvD^$a?$qPe+lQ*(3OrvK??^1bxC-TpYaxh^yi?8v$n)*I2^(OlPcxZ`-_=6Y1k&Go2(iGAcgG7hZ$AkE!%DU1WV`|G+CGv6H9>^)9+_&aj`%wM?mHo1;Rx#J0%vra(Aquk?YJ<q&==H_}`_c+FST{o}u)8?q>ebN*;f5ty`oWadmFQMa~n(KNAGxt@0ceD36;idB>XFSavH`APXaLpqlmdWuMZ`bh+&E0h%jJIp<t^+Z0Yjkk4_c*>+S4qzM&Rw6Txn5`O&ywqV&>auCvsJD?<G}7X9=Wb7&~aeRbzMQ4{PC=ty~pvb_(5`=M_@cqb6x+S^9b(#tba(8=ghO&dmR7tv+}$!U*?tva(5jU^GfdiyYoetpS_plxQuVR^W)??pRRe}!HiPBGvA@(+nVeAzRq{J`!m0vCa+JsTaU9Xr__%+->3B(xjV0?^J1FUo|+o<yR!SF9%r7#olhax`DiyER!Yu?`9$|P<odlj@1}XEarUV1_2sV=wZD@$kNVdI$(?rZX<OQ|>@BO6-|F_d=bskXq5VgB|9@K0qw@dPKP{+Qq4NLrpB9Xdv8;FQZIfYtd@?=(_QEINAHuHqhxiEiDn0@q3}3<r<2_(wyayhD&*K67-lei$gf-#wcul-Kd>Sv0KLU&6kKhl${P+X-zm_ltw>R4_!7G-yz1e;Q9><U1-@$M3@9<Q(5l_Xxg3Ix*@R@KrJ`<k+N8%Ik_u;$v`}mu%8~!HV0ltjed;#x(*JiWb4`0UpcystV-W+cYd*Q9|9`HT92R;N&!iV7FU<e<F&w*d#bMTdLH@*_z1%JkO;pgCA_&NM0%pN0t6VDnWd<@Tu7lvi=!gwiI4KIaPhV}5u_;aus{v6&0w#D1vo#1PDC%g}Q1Mh<mgM;v4_&6BE$Kf;K7<?u^2ad<*;7j0Sd<niBPQaJrOW}w3QhY8PfzQQf!NK?}d?M_DPsHDY0sK9@FKmbR#XHCRSMPLYv;7q|+v~%cczwJIERR>gpMa0xPv8aM19$;E9klD9bbPk`H%oX4{|)~E9>IUW_rUM)J@_V=if_VKz_0KX_zXA`pMj5p6Yx>^AoxB$2=5Nx#Jl6IU<cf0ZM+r!9GmUcp&ze~*MQCO8h8WP8gGENggx+<co#SX?}EPr$KmhbAHg~JNBAtb5}$>yhP&|9_)d5Z--(}vH}SLhAJDFY{@}CinPY^7@yz&xuoV6vUJO>oi{Vef=kTZSy08si7w-r=;T`ebun*oF9|?!yBk`$l96lAF4`<@@@s)56z7mgvOYk^65iZ9Q@r`gPz7bD?bMYj61Du6#z*oVE_$qt>d=FoMPlJ8&Y4|AE86Sne4PU|E#$RW%y$P(3H^HmJDtLALN%#c*B>oUAfIoz1gz4~%_%%yt*G<>hY(E8mz)#`d!#()-crx6CC*xnh75EqUG&lpFhJOG@;UD0A;2^vY-U)WcJK-&0E8OODcnkblHrp$~>Ubr*BCLT|#Gio;@MrLvuq9p-Zw9;I&G6UYJNRpOKll;e4<8L@;iK`{a5X*~Uki8QYw;cMEWQIj4gbJT<JX~GH(lqm?HOW(58@f{e6Sdv4}Tawg+Gi}f_3pqcq7;mZ-jS;z47k&P&g7Ficf)4@hSLXI3Hh(uYoJ^HFzqF!&C9?FcII5?}i)k-S|G3gzv+@g&Xj1@f~m#z60M37vP)mwQw4~7GDNO;mh#p@NIlLJ{-P|56645+5R$Yg1?N{fz|OkcsckaUJfq;AHs{^Sztyy3x2~A+I7|qHrpfc6du9%!te3Dcp^;36Y-_+3w$X)1x~}K;3MD%_z3(h*av?LZv#8wZSaP$1#a_MydhqO&Gsi@CHzUe1gwacz)Qhr@KShbSQ9UeSB1^+s(54g8r~Rh5BuTm@!oJW-W&fA&c;8)=fSo3JbXRefv?B6!_)Y7{6}~l{}I0m?K<l!pKZ5dg!ym_&j}yKbK;M~O8Db=RoDoxinoN_@s{|za47yR{xO__e~gFVVmyR@4cFjb<6B`Wz7^jKx8r;9!*Dl#7(W5`;V1A2{1%VkC*cnKBz^>L#*g6p;aYq@z6~zJx8dvHbbKAY5Dv!|;*(%cd=fr{&GruPWxNC45Z1vP;uT>zydv&{MQ|UU4Q9c!;eT2}yDs~a&Gs`ef}g?n!M*rCJRT<E@%Uo66km)_hEwp#_;5G^ACC8gZ{a=hmtY(GCA=1Fh}$fK*TPG(*<KVri5JC-z!G>7yf7?<7sh?CH15M=VO2a9e;PK%pT?hu?eXXFwy-ze7JnOlh`)`04Cmn=;|t(=d;z`zZpSy^-@qU7Z}5}wDt;2b4DGt?GM{b#2j;}>&Gx)xkK=jqlCUaX60Z$g;<fSi@Ljw;{yzK|e;=O#L--8*EBH136&{9L@i6{9+>3vYAA^VSWB6Hk0zZrY3?ul@_$7D}zl2|aNAL^yPjEl}6Mh_S!;j+!;5z&Oz6CDCx8SScBz!ggIUIt2j(@;rdpFnt?}j&p4e_S<v#=umEM64)@S=DQm<`W?-?D^u9e0b(_MhMx{3m=r+=uVS<6t}<hcASS@rC#&a5DZ0J`@hehvHpfPrNJsB76yd5w8Yo;WkU+)$k|SY%c_h;)U=6un1lN&kGCVdGY+vhv&y1g0c8RcyahNUK}qEpU2DNbzob(4*m*!8-E2K06)eD;1l5jd?LOGZon7e3Gf>{0pA8s;@j|J@G^c3zX<=qFXDHhUB}(!v+V_AgeCEUco|q5FM~IL?ePY97x+Hj1s@G(;G^-`@GE>az8;40_4qgNd;A;x5Ilw-!q337_!;~%{29ND{|+zVzvDOH1^fnn75;=@#jn8Q_!aydJb<6WkHRhZQG6#{jqk+c;pccfJ`a9?&%-}rv;8gD4Sx%70h{72@EY)0yarwZ7R5{8xnK@F7k=9k+I8P;Hrvm`pYZee0k|JOfUkpb_&R((T!_!d$HPzX@%TVE6d#BOU{^eVH-RtWP4FtP8gBCmybAs}o9z$6LimID1F!)80G<Qp#dF}<VSYS2o)bQV=fn%b;&?&)F<2gd3@;1o;AQc8@D;os-VqMKJK}@kM0_y*DO`kqiZ6i)_!2w`Zo`xCt?(GW6+a9w;)n5H;a&V!JbjGNuKUun*<J{i!3*IPU<14Y{sQcRzkt69N8@keW8rLkEWQY?#~0xV@Ebe<-vtlhyYL_28T<$QJiLsb$A5#r<G<m5!W;OX_+RiU{uh1|UcqnT*Wfw)8vYABivNP2f;;h3_;)ZK{|--v^YCQ+3-}TK1^x+}?E~Oj_yD{WY=O7JYrz_LEj$*Mz+>^;Fc+R1zhepQI`Iyh?HAyA`~rRu9>5RcYv4M34L%pn$LHc>;dp#3-X9Lc`{S>|0RAdoA2z}3;}u{P+~(tW1^f{<+w;K(@qBnT_yC>_&jfSeneYrSJDvg02y@~Y@vN{Qo)ymnAH(zD55uzf!}wFM9{v>G2zJC9;ho`NyfZ!weu@vnKZ8r~&+uh1315b%z^!-+z6Bn}x8O(NulP~?cWBp%zw_DlOfkYjcqaT&SOI?&e+IsQKZ7@iZ{p4IesC<_5C0S{!av2ogbDbUcnaKwr{H_w5BMJZM|d9p5x)q3!!P33;h*?*{1*HRzlGm{H}O08ZFmj8jsF3E!T-R2g{Sae@zd}-{4{<LCgTV3P4EkR6TSj|g0H|oW3zoA9DonRTf<g(YupcO;eNa{jKxdid0=il5B|3$wCl>h*=+v>Uci6B55a@@A$%2FgRjCrhja1I@iA~LJ_hd#`{RA_cJNia9bOmK$Lr$dU<KUfBX~Ky7@O_6VLm)Jo&{#Zv*77rCOkbJ12b6eRDk0a%xL}h$M$qEE1nL|4D;Zb@m%m>JQw~bd<uUQuM8XEmGP#qGu{+`0}jLAz=QBJJcv()%kZiAmoNqY5)Z>Ico^RdkK&v06Zf{}O=8mJPyhe=Uw;4h$6m)~Mg0%J&A%DFoY(s|JKj5%ySTS`lZ^H~ymvFwIRg?`?Gan+e*lZ99_|'

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
