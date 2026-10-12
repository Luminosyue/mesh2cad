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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d75e06c3ff8f44f9a9b163399e43f0fd/part_001.stl', 'relative_path': 'd75e06c3ff8f44f9a9b163399e43f0fd/part_001.stl', 'source_sha256': '638dec67a36cb8d7ccc1b90b460279179f159f18f4eaf5e3170153cb98157c14', 'input_faces': 1216, 'input_vertices': 732, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16900861263275146, -0.49960267543792725, -0.1788906455039978], [0.21083061397075653, -0.4758380949497223, -0.09468287974596024]]}
GEOMETRY_BASE85 = 'c$}r3cbL>v8@ID7qF|w_pdcflSWv1;m7$6vh)NNq4B{dvWvL2+jxUIUfJhM$&;b!pR77bDyX@@l%u+-UWofoivAv247I=LXzdW1!$(x+XAK&$TT-W38KEEW-IY~~Elam3vcR8a>Rm=HvnU#HV+3-+D%aS<Ps%nkT8a;OCpsX?1jmVymVO1>k<&WyTZauqp?~`GTw;ru`f7X~mqwBQ@)oV4lS-tw9dV@!f9y@yAhyf!<-=8IZr-8%9WZC|hAp^6s?DCa2HfdZx)a0uAp~<2D$3Nwz4ONyW^KFSv{?F&7np>^3Z2GBY3krh#*pDS!MI&F#_4{?lB!m3;h53mf-&*!_L69Gs*D}zz@@C`)=c(;)&(t@adTFOMdaBP4T{kT^$Pcf%ymbB42ZR0jPwz+u`SFQE5<z}sV#mTDKXmeFJjhRtydf_z&(LvOeEx#_{rgq7kFWh!--dZXel&CP7N1X^XvN97L4K%P!_xe*nhpK_;u?8@e$kxL{E-!x`ukN;wc;Q@wxL=g$WOIdP#EM}jTgiN^Z!|r7nuLEk{que?sJ*%xJ4&b_8p(tC%f|k{U=g6Uf<2rXIO5KpDNSV$=~i+!gqX5ugwec!;!ypyuRj%UHjkMAV0q5?b72Mx^i2>*H2dWFAnmpc^?%8`SH3R7Y633&^;dH#}Wg#1^Lmcx8`_#>!NQy^B(8$lkX;c$Frb!j@Q@qt!I1Y2KlkQy`AgYddGJhtO1Yb1^Lm5^-GUWc))z$akiRI%JKS|KU8yXZjc|&{iHNc^pSz3eu(^GD<{Y6yX~CSCNId3cNykfzpvcvKW<qs6bJdKl0`*9e)!9(fxdO;h4Dat%SYRS{7|h!o4vkuc!TeJMLW0gov+Xx-){E$x_;#P7P($Ob;$8kSB@#o6F+r@@AyYPsg&dOHIMc4qFk@9c_RO=<lKjQ*6{a}r^`9VbN%Te?|F%K>XYO3HGitYiCnL*`Qtltobx+vXOZu`>-klmJns3$ck^(5L)R1(`Hu7P!r~x5eCx=fAU`_1O`so{bud53w|ZS2=ts_;vf1m$3ZL_x-}vFJMc(rp&Y!p0>+AZleV610`ZJ$%`bp&VBH#J#pV;j6b^TPmez`$@Y+X0!{FZ&zcOJE$sITj5KQVpnC)S9keCI{)1F79Zedky21L|uYy$_ha-UqBdTlw<qeOrC^IP3knYXjeTNhLoi4)Vk8`V<AOKdxt>A3FL<eqf$|`UU!-0k?1V`CA_K-=Evp_w@(s!pLTy&-$UyPi+nI!+*Zx^s8^{`1*s}uheIKw_lmQ_NzxO@bw4x{)4aUyZ0Z%*ZWVbdpZC4WqcBznCa^e?(+y=^SI9=!`J6gZ0!%F&rkRM!1zIZ?I${ZP~UAQ<Ag}HeTBY$&iKvrb^NBjdtMl)MgCgv^K~2>zIS1vw?9O``novCPYt-QDA4bHTc96V{ak+F`Yo~p{ZO6On|(h0EkeIF{V@I3^>rM@eb4lx-1pSi@j!^@p!)7}oadnW?(>>)j_Jo3=eWL}cgCOUyUzv2pX$5kH~WUXAV11D-`y`gzr63H`MmFhwoLH*yw{k%_J`=leFOWO>1%&eU-Rhug6V5NOqFdPcwMM(UKi@S_a(;FrmxpaxK(}Md9jxE+!o}!*EN3Hb#3^1UB|O7_Z<g)-%0bipQKt>_w~2PdBxkjzIh*0-@K2RzIz|rQ{LCl!!K9Q5A?a;y1sG0P4l_mhR0<3uDfXGuK7W}`&>}pd@dNiJ{Q76|0#WsH=l#1ug}4>^?44OzCH)j^634<Twm`e>Ko6&XzuX>Z@+cl*YM5fzWVNXM&H*AU&jN{?-K>y{uzli*cRmL_(Xkkd}8|UdrIe3zV_?;k^1JiD7N<H0&l;y{$8}r>zm^-_092^>AT~xUQ-La{WJB?ciVz|9XG0PjvGy1$Bpq%Mi+Sdr(PFnzK%oi)5f=^uh+#h!~Ok-@x1Blc;57NJa76so;Q6R&!?@g&oz8=Ja0A3^7Wrk|KIY0e0{HRedE1Gee=C0+@^uApTsZfvCZq7?_cVh?_cVh?_btSmHgMm9n15Ae0}eW=bh#2KiY3i-+kZ2PkZ0QH{Um-YkrD*`;XqwP2U}t;-|eA<D2ir;qKqWef@-a0Mplb0Mplb0MplbfHYsnKZdXK0P36b0M<?K$Gzv>?N|8be2Dtye2D40{i^qiao_pkerWpcybXTZyp7@O{V=p~lCS-GKQw*4ABGw|>N~$Wt}uNaSEz5!Uzxs+E5ft0eaBzt>r7wg>r7wg>(cTtUuXI{UuXI{U#Gq~UuTVN>pTAX95j9R{TJVyw={iy4q7d0_>U*!!!)1qq59^$tLf|bFjTpse}9>OHhrCcHhrCcHhrCcPRq~uKP^AwfA!7z=TxJ=^L@veab}vY<IK8i@_qf2al7g3xZU-Qd4AK^aeL^!XY+mg%l8h`*Y6#suiraNU%z*lzJBjW%fow+>l@!YLeqQr_Sb#iF?@aBiM)QJFTeYJ%JALqQ-<$;pE7*+`;@u9exFLqQ`_Gj<NH*+Q+40^`aRC{^?RJ@>-V^Lg>MsWg7O%?=83ia!{_VqF?~Hgrmx4x^!50tAJhIxd))Q$-S3R+$|Sw(hd#|t2KlkY@r2iR`+uKf1wp=5t+g{=xwCfC*M9BihVS-s!*~0+;k*4DKc?3m`|GZ+<6%9IryKb8EBsqB8RSQA9+vR>?tL=5U15-)D*7(&%cIZPZo`s6e)w3@pI@)LUEdW1`LUtxoblF~eSCRhRdSO-e!SlJgx7bU?{k_J2Kk{CC!G7~V-Na{v)<25U+?FpulIA)*ZaBp?s$OnW%_!)!Yjx7&r8#)#X)|m?4=2>@1B>p=M)C{;VI5IMtyhO^6Q{vkRR*3ClTaFMy3h^^CWL|uE*43|9MZISsdht#@A1HefPY#{a0a-A3d=;?)BZ{)^|-Z(7$9_BFGOPu2&f7zmVzl!#{WVuSdpFrmy2D)7NoSS{}wx>W6gvruR?$|GlSk{Vpx>_lNm+7YF&Nm4}PGzS|!vmJ|m0;X1wIUf*rcth<vzzV+7Ogx7c5S-zwo$d6pz%jplb5BmGnxMRs6KXOKgM4-R^!NMRv{&?JJf6;IL{`P#w;vhfz<qt)H>z5Q3dVTl)*?)*HzaEEFj|IsfKT>x|!t1;53;QY+2Kn(=HJ<PFioN?4`n_IpkRR?;J`v={N3AFf@?(Y5;$C0d8NYo`GRP1AILMdZeGl4wYhjQd8<KMFZ@J-OZ$H=fP1D!+P1D!+P1D!+P4(UR1igP6zFsd@wOfk4*F}8yoZ=uqHey+k*LTNzx11N~TR+r{dwsXwFK$f+`LTPxO$7Ooe%lLz{P4j+&iLW#`-;8&GnSZG9OTExZz>A%t+po%y}tYY`)iZ9*LUYn@+KyO{OHz=i6B4R;$%T!o*SDu_kr@meEllA?w@3kADYoP;q|p&rLLV+801IGu66pun(4lNp4!*DILMC<JyI0p$GYt=49xR&FJFH5JkD8_4DzitGZKORd36he{75}#J}A5--+$e4y_<f7>s@{K_;9_Oew^#w^>x05>)rJAdN+N&-c4Vx_t?qpzUx%yElpqNElpqNElpqNE!B_fe5sD-4PUSK@GbBAulEI8ii7;vs}C0i`Ju`;`h55K*x|c;udnrn*0xLr`O%qwBm(_wHWvi>sk6s0-};&F`VDnjUL53yf7jn7`2A?%r9R&sSC2Y3?)BaF-_ti4<VU|KNd)=_4iyCXseX4l_pus(`mZnUSEjG`E7RBemFesKN`1Fp?pLO-_bb!a`&C*V?pL7=8QXo=3*!^hk1{?<^BJF*ev0u)xL2+1zU!LtiRs4}pQ!JSqZpr<zBOQoFTcBAj89Bo$0w$*;}g@@@riZSZNB}AFrGL4FyndCk29V({TSnU_1){bpEI6M^J`2?1o;uh^J%`0=S%vO`sVjR)7S5VY3uWS(De2DpzG^*PaV%2zB`^be0P54^S-6NJI;S_e{ql>-q)`v$WMLK-RHaGmc{GyeZJOv{ng1JKivMTKtJ@(%7P$2mOmxX*YCDz`SrVP%Pgn;dcV^9w&A<?ZNqo(+xYIhvEH}U*Y@ar+wk4{w(0AA+wk?iZTkAXFU{BA9lbuL)OYWPj7v>l$EBvP<5JVtajE)le`8!~`Z_K(eI1vYzK%=N*4OV)hVOod`tWi8{e*cN(@!yPWBMWHZA?GRyiI)dH2?im--`|3TE%-YzI*?y#Cx&fNA$fI-#u>nUTpa8d$H;3d$Hl`dvV(OeBVi{SAU;8W~u-F$-I#1TW2}*LTUawXI{wkBg_k_?_Mv=3z>eLc_Gt}GB1>thk2p2JbY&{efM`boj3XK=geE0evElb(~mQ6Y5G>enYUEmZ9nstrXOM6()3fzTbh2HdCRo?d>=7={XP=EV!!{oV_w?y<IGE&evEl((+@E(o#yjhBduP(Ys9u6_dW0QcYUU>zw1l$`CXs-?sJOguj%XaH*I~Mzpk(Me|_&TeD}S>@ZI+geD^((`3lq5`3lq5`3m*j_gv-)O+Umuq5AH79P@;(uh%v6&!!(|{@L`c@B&{R_x{Ou2h&gS-NE#ue0OlqqxLubUSs$v{a$1EA^l!s_+kBCW3JEltn@s!ef=<Y*;xPkpyBKI%Jkjw)sPB10<SN_cdswQcdswQcdswg*Xzrym+Q-V@|qpq<FEHO)7Sf(`sV%0^!0va`g*@IeZ60$<=4NrW%%y*+!~#B`1&o+Bh%OCk^1KI#q{<0V*2`gNz23YB`pun7t`10OZ=O@JG|GaJAN>Hcl>~#HXbm1cRXPFIvy~5cRXOOuj2u;Uj4mC-XLE;amQDNuj4E0>yf3tIsP<#cU~0V98a3QJI`tO?mVaA>v%G4ea4ffuj9!`kH<=V^L@ee^?gBobNp}mI{r`d8ULHUj{i+x$Ny<Q<Nx^DX-+%M_dCOP-|z6#-q#G@eP1(t_kGRq-S;(feSKdu^YgwI&6)1_#(Q*{&-2>#jrU^H*Za2VyT6+qywG<)(fJ3{*ZBwa&H02hpZSDv^Mvnucjspe-<_YqPn&Nse4THJ9Qnf6PMu#eeVtzlkNMtzJu;tW`Z}MczBxZ;`Z_<B+FfR+_j=L!M$^~%M)l44L(|v!!*HhycY6D?`(AJO?t49c+We~F>vbAkc*#z0f75ZG>FYR9eRDoJb)wEr@A=hvc+=N;c=gSBb<=mhqg~c#r}up6cM8+j?-c5r-yKZf{q9gW-q%k3&SLudoh6j@gzx;i-<1sC{jP+c_MOP^-Fepyi~Q$ZpD%{*K40+DzM~nwK3^ggm;27Ij@wON$L;Ey-wjhoxB8C1es48>{obm+`Tf-N^}NU5`^kSD>Gx>EcfUvDr+r^Ge7&Do!_VF2ZKr-uH+}t{o;rTsF7NTz-w&9+{(eAx^Y;Lz?~ZfkSKH-1{_gK34B!2|1itzE2W#!kyL`t@=a~&(e>bAO`8$v_pWlI`z8mI04vbe#Uw>DlzWF;D)7Rh0#4Aql?XUih$n^DhMCzNr3kuDc;oD#Ry_4zd@0}uZ-u1O#f8S;L`ui@|H-4{W`ucmVNb3UsdE~v)^!4{_>YKk$i+%Q)uRZ#^JJZ+S-KDx7^B*_fLrq_QH>ke(JHW`}fBDag_}zW~y2`Ij#^gnt+l%ZdXH~TZ5A^)gDq_kX)!=_xWoXm?tAARhQR7B8{Qv#iD&;@Su&lrBD7HiRoJ^<um>n<J5kptQH`&qMj!x*^a3{DgIs(4cjtJ|D4u-qKccY`>7<Cn+AHvPZbraehmU<@A-ifsJF>;M&`Dm62?;_`F_y}cLzJ%>XSHRNdf6+$Kr{TfyXmk$z0^6=ecX{^X2*+3Sf=q`c=Nse@eaDk`4(*yln<ldC9X!!3u++7O`a}=Fb695yS_toAog?TOv}+0LtU&j`M_5PNEm{kf<!5C&IYcYLm#~hkD||U+Y4g{#Mf7J_wyDJWmDomD+VCIR@gM5g!*+#i`!mZ5IfkEcY(Aq7;dU8LAMJtmg>OUeLmz~<+3~#{8{uCmzlE1VzlU2;$8D%LcVF^~j)$k(F_U~V$t8SUhSS%ZqBp?}(H3YsShk(d_Va1$M)Gg4;~DrZ%2!iILsWC$=V{l2<P{#uvS-k#@U`S>f;NPup6{sZEsl+rPuP(Me@FQ?>bMKOk8(#l+S+k1dY6Y=P;S9CcTsmkmN#UXaC5uARJ5ZNdNC|@%(G)0^*uvbB5B9Va31B>)X@=b3*SYKd*Pv!Z{!%YMw`IHS$8rz4xUFF^3V-%Z|WJ2-V3jyjr-6fJdW~Yc%ElHS*LuaqkqA-)2`lVM>t9Sf1xMfTiCbT(bn)n>Rg4s3{RlF3(?82Y%|J^EVwu2QSbzGIQ$CR?L=3>&$7*8bOJnpwq~KX!-qK*RWluxV<7wl+dPG4!8@tzFuD)E!QQ59rqjR5(zk@4V%ulYQSf5VeoSB=giEL+Gt<$-Z~@!AkG=x8q7S!0>%uwIQ{bsjcuj`0Z|l&fV5vjux)haTAgpbApE`F^UdOgM=(DiIDLa0G3n)w5GHG8XxrI-$PFeQxeON-cB3c4}!af{D*TF~OpU@n*gt}$h682NdSCOkedK5mzxoiSUJESbj8)iD|93{7uC4`%xr{GU*z1r5V&}-o{ZN1)(3TQKUgdNw}F&J$GkGJC*mS4j%;bV5L2DY9=8^fY!diZ+EQcrd25^hQPHal9_(Ftu0KW4|3)PE&)3-`67sU1Dg8)0edQ+CXP`%><~I=7)M;05G+4jlnEV%x!RQ_73&m|({XaFnv-zu%52@NJY|r;e5AbMRq1KDOf^dIWxodZwT~;6)sZ1?YHBz7g#22--V~x}^=>&`$7M<a!-l0Iwuh44nl(L;X*p_ro#PS%N+Vzr;4v(I??;b`;q0Ci*tKgl(Ter+BuLx_Y7A;H|WGgQwlX`Rv<P^mTXx>#Rd#@J>5+)2`jLX&Y^oy8ENO;1!<zTS6OOB3F#%F_sDEu<TuQ1zbp*a?o|~a`HWkPKV!R+vVs>a54K==-JOgj)N@Q1#hJ+$NL42x$t7jQqK_Tn$EszIopnT@DR$IXwzzRIV}D6!%U|S3ztxSpLQkC9C$D7dLJ!>Kcek>(PH=z%MPG>;f1vE5i}d#K|OisCU_t9>_8Ln8|=qIbe@NoQ(n%om`B}v$+wqW`^c9=eK{PXO~f0tVH0_!`~k;o5BeeeG5dT3Jpk{fy#;6<ENzW)UKer<qAbhfoaa&J+r%5J{|4JErhYkhJJH=9-bZ;Kb?>H42Uvc9Wx`3e+l+35=Vv<oZWKBJ-b39<bSEs^y~eh}Z&H2@o{zo&@6UAZtskHV;VtA_k8Xyyv%Co11HVVE?dS)v)G^eKIq)dTMQpnTO~S9x);Z{Wcr(k^!>>`!rJjvw5j=zK2B1UXm)ULxItPxk54q@e_#N8yD!LwCiq1q|hNqFQH#z`*m2F=}Ux7E$=6BF7@EYo0g>Hn`($+O-F1(6$mZ9&!%iyJ`w*6(=Iuo8jc{bZTjV^_=SbjU&8=lFssh<6p@?6?98(ju3W!<OYnUtSrKjwP&NBBkd`FV5={5Z=VMxTeJ?wjrC3g1pyay?+jNO(5oezc`0Iu(AHoFmb>@Kkd5gtI6=K+b;X)9}@_^;+~{xFy@&gx(A{BX>)*D||iqnxQ@6YsuLF9SJvp8>0`vGM1HXj-d_Uv3AU`V+cH#a$~l=-gCT!6ZW#>cI0L_{9nqA<=w`PFxml@oRi2a`Vw57{i}oC1iwV?xvZO@e2*Q&$Ty5!V_E(I?GP=O>98z+o*bepVQE`8+9%oz?f~C|4ud<}(Vuli?}zVaJ>_i5FHu(l{Q$m!T&>V<u+;Mi?R|u{P9j$}%d=S~yn~!8;X{;V`HO5Xx*V1^M`@$zH28iv8=Vb5&$cVk9iII-#PJoalIgJIe4QMkZ+r62rd_jX(<3Z<8&7mIyqmg~!}}@EW}O$&IJ|>(4xt&e>qXXCj_!sJv5vG`v?eUe<$Y^ES^=)kI<jtc`lghn&0o<L(POY|Q-Sp>u#K>^;Uw)iNgcb{F3z^cSQh6Pe#)`=lsbgvT9Q6`CwdPoG0=`K@DR#!&3tRediXfyH}O74zlEDqM;G)?_#SfJ36G^bgIrVK^_1&pIDNe_+6r!fHb=v-Y&)0j=hD{o<bBtU>F}GBucD3ysOBC>yQX;BC;R}*rlV8fYsl3IZ2(I>-%!_^92+hFV#ika8_Hd%;|_Qr<@R>8v7--qhliU}Zq7D$P<I2CH(;5tyn~;g>AZ)FR)eLE=j<3mebXr~MT^j_a7*fFkG6sPQ2!Y80r+~3QA@ND{1DqbijIMwqYYcpcj2DY^N^=L;a6$vUbF~)l$=Y^=RC{L&UDrh{*!W7+SL<n4{v3iBKQ}|H?wbD(U$N6>V6en3O`JH7od;AgV=5)+7liLKa4&EFJrsy=&SH7wpoNe4ELk0gV3(<L5@>pj)fcp;m6tLNpukWD%)&__fnR5nlhPA|0+Y@5`L0xXQ3nEMV|e5n0;7AUd!I@BlsZYe71QHT?V(H54T2Z!<(ol-&3FPYZ=bItwo=Nr4Fg91}euuSnBzRy0m>Cv5joI37rK?{9(tBa6V;en??I9atr^#I%U|$_h1R(^U;sskJ*PW(Y5fG@Q>&w_<W9KHPqrbT}iHM&@bUXIG2rJX@`_$nXGdi`XekM+z9;xZf8eFJL=id7QU4bzLOBXhY-Gx5FSPdk0pdB5yJl>geMci;|Ss5gzz9j_+CQzE<(5q(UJZ5C&S_2Z9NZPyo=!T*iYfh2;qy^M)-#eCxpMqa6<Us8BPfQmf?i(X<M%#Pg}~u=Musf62c)uShfq>(IM0M&e{g<ObB-;gzqMVBZTmSgz#uWcp@SE1R?w=Av}f<euxkrNC@{Kgzq4PZy`FcAM*PHVfp5I4!(F7z~``^!nFwD3)n_jzRP|O%QwgrEZ-f!gXNpn30S^u)g@0G%EILd;i`o2rG&6-C+{EaGo5i>Yq%33+>H?KMF{sNgohBq*@W;Tgm9D)o<InXB7}z$!UG85-h}Y&gz(Kod-g-#e}rYsR}NpiDsVaWQ@AD}T!n3fWnB0zEMuV0VHx*)1Ish@7g(OHwaL?(vhdl2aAiWc1|cllT`A|!jymWia2@z!^nCbY_&oF<%i;6j)0U(EhEK!aqx<0R;SUJmchU9myYLirDl9q_o&pacgzrS}g71WHLfgQi*TOf!^$Fpc=%uh|CAcPB5j`8O2%klq?L11XdUBrZxD2fhUj|o0&xNbO=b(RE4xa=6WjXpC{1^N!x)=Ty-a`n#jlKiF4M)*`!J-eqQ8<eb?vCC8cZXY{tzpq?;8yU}gzzP34Op}Sd<lF$S{6PZK9dlZ$MzNWe?oTDLN9`A!55<C;S1q%=zlGT%fWwIj(!9G34e{g4}T5sCWP0b>)^HU<LDEx=wSG9_<lmT8+tq34Q_$9ghj7{TfkQm!qw4>VbSy8>hQT}8TefI3_@7`$n_=H;X~*&c$^(G?U;bhhF96~lpU|2)8Qvswg!HR@(4Sgwqq1J1D-)0$}=fXpsq>i9C(2p&)P8$eGZm;%M|LJLfyhk?RdtHMd&OzPJ6eYOW{SVvjBY--a)<ux(a@UeP4<`1Al18TXwt$Z=k%9I+mde;4i4-Q#1j~JzVbTm!g-$Tc~Fvx(NP&W3dBW1FvGA6YwjPm(hlW=sfs)a(#jBfIlV2K{O6;qyEk4GWa0te1vX+W&K<`O5n|u|6_+-_(#znEQdd0+imDZ&vsJRVss(=2krgE({AC@?Assc7w|8v^CNl?KHF|Xg$$=%q86M>-7lky;g4x+iDy4c$aRqA2U#Zk8_Rw|KZY|hoHqSN+kS)(ldllXg@0n(!)OV7W`?tW85#fE&kUaLr&)fQV{j(NU5@#C=!dY>^D1@avaeDu#(NEY6+S_mK1UD3m(qtXKx@DiGn{svfy%xLSI%(SRT0gAFJ>Pqqi4c(SXL9Q4DX_?Z=$ckXHn-V>XUX0SEZh_&@<q#*pFRkv4;;+KFqNYu1OoJq7~sY*vAu`*PmdCuV}*w@=Cc1*L@}Q0{BYy`Es--T!HplsN}Oa4jVYHyEq0LSaynYeu_GOKtJ^GF3J~h?#@Olc(^L%s?=S9Hq~T#O_m9lVY^=~N9EcQ-cG-J9eoR~#J-n7&xU2Y6x#|PrJRDdqwm2o29|qk74%a0cgxB5Gb;In%d$KZtpv-MS#p&{tH4Fnvl4wB&Scx)*_Sf#5!zaWZijznpN^m@_#|yQj%LDnY!^dU!Uxzc4=sXaY%lw85-kfKvz&H)g8mHeNAuAGa1QyFpfUIpwmpCzfsb=6j-kI(=a=l;XXtVG-?a5h^d$Tl>l{Ll!H3}esJ8t8ZOw=CC>OBJR&+nSoaHZ|OW=H#ZSw5Dl#{fn06he6CFdqIAKuA+Bt82hypMg}iGB&MXW1L*PWXB1pO3x(uO{CLv;cmIHob^$g5MzLYBULNqK+5g<&+D^wZgNXQl3g%r=f4abJ%V!Iv<`*?m6i5@J#Z}Mqh*_-_zuLgEl@*2+u%Qzz?zR2=r<A20Pl@(FpEDc?EUP@Ek8G_p>A0j(gxSl+Uq4{_4wxXf;@JHYcy>t?(rF?=f^P+=+GWLHoh=>}W#1Cgi$-<pXJl=)<rqznL7OU14e4WwcN9a=02?4{ZX=JMy)xE7|~Vz<SC}Dc?$6{m_AMC300oFN39?8)@&2w6!_8nzFnp%Y^%rvnxD^vMle+_M%;2X>%LeDB2co05?TDz&EpPSG2!pKL&ApMJK|N^Dc6T_VncKK)X87rW;w-6HoMRSn3);eWLfl9ayI`dN16cbq1kh;m)kn1swnnVx5WTWLTDuBZt0sX}(FUC;AvHZGMQhh>n0Ku+4q&B+8?x<6d|i<-6JTUUU>J$8ae145bcXxt64l)<NsR64%*L3vNWYx8+<n!_jP5{0Hsm0S~8KnL28rbv!xikyrEvxIH<-aBs>oKO}wq9JDH24y}w{2+Ove*uE2O6>dlFUT6<ElRC<wn)^E17521GxFO5hp<(zea+OER!BWpK>gvI<k#Zlrk?1hE7IoByucLgC9T(Vf1zOv~l_^(do7&V}j^*W8CM@sZk66xoxagy>)FJ;@_Uqwxly5=%qJ7{h)Nv7d0bH9LSHKM^SL7H~LCeF9S+^N_J=~Et^g(;Ub*ZN@dIfwNZH=IP;b!E#1?}irKAv@iM^g^buDa+&a39v`3y-8+lYI-JRp9PjGBT^4@xQ;knSFBEaQWZfOPp){?~nXW#jZJP^w^>NZBBDb|6lv`ZrR_?<^Cnm?p@B5IX=7dWtLw2)n%s4`afS;nMn'

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
