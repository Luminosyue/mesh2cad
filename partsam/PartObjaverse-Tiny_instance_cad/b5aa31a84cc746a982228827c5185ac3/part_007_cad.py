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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b5aa31a84cc746a982228827c5185ac3/part_007.stl', 'relative_path': 'b5aa31a84cc746a982228827c5185ac3/part_007.stl', 'source_sha256': 'ff7d01256249256f2935958fdd42dd9940aa4da3ef17d3422eb8f76a832d5faa', 'input_faces': 540, 'input_vertices': 629, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.48607316613197327, -0.2509251832962036, -0.05211222544312477], [0.44658318161964417, 0.44777533411979675, 0.08178184926509857]]}
GEOMETRY_BASE85 = 'c$}r22e{S5w#R2573>0{f*?jw4k*~E7J>?bSP%=?Fd(2Py(nNIR_q<bYatd8#NGvzAlLw@qHsjW6|n%8YrU4MZzk)vw%IxRz3+YR9lz!J@88Z&CbRxCljQ6}x2{`kS=Y$VUS{QA6Mh<fxG^raH+9V={f3VmaDKlL2MiuMreJEN-2G_2`=rxP>~?0sTw*S(?Avd|`NJ#Qd6h@>Z&TUatL#5y_{ibC2cI`&c;9}Gcj`TGL_f<%T-bYPKl{3At3%p0_YQ5=+`Gd2KmKfMn-DE;ux^gaH5M*wZ*#J;&vWgw{G`j4yVr5tzl10CJ}coN-1NNVWB1zh7+b=_Bfcxk{Vsc~$#SpewQJMkp51Fn`hLyEq07OpSFO#q(|>R8=i6sF?et!3Qp%e=UzTh8mHTkBPwTXu!SU@%Ip>w<dR|`3qe{0ww$Yj__ilLllXUxGg{5icypoA~l<){1-4d@!&%3Zl>heqX7u#ofm&=!Dc?d7|^O%cDxVA@mT$mx-f4DO3=WzXr)8}Nk|KL?6JeV`Sq&?nc_oe&s;l+OV<5}7NA19<dUjMc9bL|yrKSXe^?V-}2kAGgmqegAY@}!6Kzkk=p5+0n?Q2N<xDCevD={~lE$8S~2dF@+!Mf&-<zfDOqJUXDI^xHRkP0jM4e%rD<>V9ik?p;$SJ#NtL>u1yUDBpZ;%KgLtC49)%vY$InlYVY{$%|PYv~0XE&HIc^c>p(C?KLa?+{{~3?kO)+#_4&^o}F?7Pioz=DBbSDMJZ1P3-_sG)O1xT$5+b3NB{gdZO3_!r|nO+^`!2<ev|SD-<qw(x8cCmvVGI5OU~EKUXXIHSu3gUvF#?8@Vf2Fa_wj3{<61I9=_3HX}Vp9-%@{i@Zj=gAEoWCyP|}9apP549$tBAN&7w8Z?^6w`>)(d#v}gsAMQ}Hz0dZ^6u+cB9_@+Y+MbBxD%bW@<FB78{HTQ~Pwv~f>~X^;3#zg_P`=OoDUb10puU2K_{vvb!99Exs;}UQ5nn~>E8Rc7GU}_w!qrzH{_#$|t19cC82?1Ihg4;K;^C9z?B25frCvHt{Y{%5N<Rlz|M>W!$nj5}tACV7-*v1iSKsi)W^%q~^<12-V*rnCynjhK?hXE{g!{_1zSObEbM-CqCF9ESXw&o(9(4L>b-DJ(t7ok)*Zv5eZ@=<<`$Ofq_9)M{$2)CGNqb@)FQ492(jH&ODO``6=Q@u3i@#5~f$KPm886DUoiXiEuI*HwG`VthIe!*8^Pcjs^<`zxE9rL0>T-VeE*QQ#J04@kqyKgw+s|E{j>mY!(@$i1a@RE_+=ItMr^+~eXllxh?x&gmM*9A+aVbyU5^lcgF)-b}W6zYw$_G69YTC|v2d6wz{>=ODr2V{kn-ZR{R|r@C<axf1%JX#$;Q2Z#*YTqDDssk4HJ+=x@_gNk$Ng=q)ma{IdAji2{9{f&PWqqu$1wjSCkfa2$1tB1IrC4R7q1g^{+ZsYtgpg04a@pOdEO@hJns`<_mlI9r`zXzV&Hk7B&{2k^+^oR*EfO}>q|cu`2{P>@_gNkJXiN3&(&RdzV5~2=IWkod%>#gI5pdFy&e4fqikLL9Xp9nK3n%uwx0v-XSnuHK>sM$aTMtM2G?<v=h~lv&U<j}&qU`p<@9HsYkyYb^k+3rf9ARNr*iMdHF940>jAi455(P<%Dno6@M`m|^4xrD8m*M`%FV0E+?PKpH%{XkPkfXecgZoV`*0n1%A<dnlKKYJ*VO;&!?gXmdL{LQhgvV{qTDd=<$1o2F+5+#BG1)PdA^QCo~vV#=jy0DU&rLast>dN51!vb?yu)vB>g~rL+b0pBkCJbU+?QaA7<+n>2=-poj%Og%TO=x?RFn#>lINK<ytTA+b$^&M&7bA<<u*rUeSuNDUWG?qV4~BRLTSTKcxSCxS>By`-P>P{#5P_?eIbNxDm(o)-@N-{OpZneqIa5KapM^!jnPblStP=xVBTd5BKqjr|pDm`>S!<U*t#MvLfvtuIIfecgpyJN4feY9fXIu`iA|lOSzw`Z@h7!aOxZH`;)Aj`}Rq>p}z4qQb*+>^;I6-7BA1%F?vDj7#;WAvTXmy^nWsS^0I9I$IQdZy}Pd|;W69{V|{$@A-T>`z8~x31DDFY4UeCe`8?M7T#rkAW9sF>1LlW3*Sc5Rp1LbHaIL#f9hDnh?*_~(;i0Z~@UW_;9GCmMWXCJz{!Tf5F!;fPhxoyJJQkn81N;!;hv3)3vaBD1pBl?}AGCRCIX?ssu3wt<LqOe?s~?nmqt98I^@IPS_`zTL+2WMzyxsOFIo~mF3C9l!byx1=2jv0W!w&&|@RZ|+1V2Qh+0TV?U6dTtO!fnh@JX;+h4@6b#}A2)Yj}(wf{7bTxUcI4Jh_zi=z2kYl_zsp7xH}espa|Nab<a+>w@}cm*>-dF|EWu;jdT8{15kPh=1bSCrI7v3J>s)!9M}q$3Om&AILn@d7A78|M=>kKdu*!e<J)7cN!x;-kJ6NYw?NlK-YJ;KY7N2bbIyB8}E)w>vT=a_p<(p@Q=4c!;~jFpHCK_C=c+Das&7APxQk?nP;|Vd;H@)DE=|<5T8W&B-u{5hfgA{J3P|$BFEJy%0u0ct``^0E8*&sY8;<b<M<@c)hEim<kb0T#wP(jN!AGu@kxYFe7KKKlBvuya8I94s!!GmH~Jj%KkH;af1Wr$>mLvQC{NCuCi73L<7Ay0f7tx2ul!oSroM`1?>9f|t7y`hle1iXRpg_m&nxj&EWYw~oBU?V@l}Gaf=g~qxp`B372qG`q0URpKR!IbR|&o{@CaW8?+lUoZItl%0_LT`d&z#_0e(yHn+Ff^Rf2z%d-zIuJd*a~tAM&IkMUJCj<2e5oqz6`Rl<Fpe{$S#zotBT`kgshzxnvhz$5$?;<w~U;p(^O&iOJg!PRdDzj^S)aG!$TjPlOhr@-Tlvr=yKdHA|Y@!|AI!u37{za{^<A>}cC3-DD8_jMhFC$}YOz0Gj0&*zHYOq~;7&-%@@V;!7&aLPUWW)_IAlt=hYc>oXboB2`vmP`>I<F^pM#gDNc{APyWH@J`AOg-_NfqPspnR~@o$^(3u=jub{!K1>}hatXFu0AvqW|eY$sN7eM5A$68raa!S{;TQx_|5z5I`IiS#&5w``Tdt^Cfv*UEo>^><oxEt^L|TCsr_m>UnLuUdZnDN!dl<FlJ%8`e*(DrN_qI(-LI7R>P_ac7K2~T`pWCuO4glmy;2@hcaORUaIJfEG|w^MT6d2+D%ZM4b3ZNJUe`5vc%^WyyGLD$ocrZGS3gway57OPd(V0~J6=4-g>oG)$_-q{i^q5gCkjs(FA?L#Zx}wDZbv_dyWW)ca~M~oJiu25Uxjmodo{&ZKECo^7jE=^4PSY)g(o}lyrq)oDzCwN@%#k;gqwbg#6Mg=Q{QmcA5!k?I;HalJf<I%`|wEDsYbU8--Z3`&-F9?;MEcC>3W1u!rE-F>k)Mi;6~RYxL-?navAH9j$h^dSC()O9_c!j=ekbiIrBrFd#qE+%}yM*lII(YN5AbR*<PRb9y36$OGkfkNBVjCIl@266Z%<s0*}>idrChiV}*zGbM*ZMG9IrM?$Mv#oAf7K`%`&xEytxlBhIVH>CZgZ{#0(RgVUeUoEJ(t{i)o8YkwB`q8fL$&-gP^e}38S?)I5+6x5S(6g7HvV)}XJz3^!1=NPX2uRK`zPRg}j@o#^~b>PCEg)?5l1^dhVd{K>i)7OmCWW9{jV4(1Taq8(f9VR^at4TUe{mb8#bzy|?m~k5EIDPyV`Th%jNVM+o;Ku7pxS1wA(fd~X5W-^}claTiE<Ebb_2GT>#V1d&pVztH+*~E~n!$eXL!xz5jvw+o)cepp*ZWYduX4Q(geN=iEZ>XKdFl28WIz4Jy^!{!&Y!z8f1dxl%xBcyP~Qk{blfT5X}g!w_EYyr>)!1E;nY3Qx;JhmoVrJgZ{+vd!XxUQ^nFl{w=bN!d(=IIhtxf&vqr8P`@A|c-CnQLe&YTS9#VJZ3ET{qx`$oHOC8S_o=|u5gVa6j%YLYPIKQ^|r=RfnDVc}EK|Gg$M`y}<9Wp;CPX@|-65^90$3Myw-9J7t@e3tfeNv6<bsF6ChwF7(jvM9;<?&-5&&>KK#6QXBt7d2YlML!QPW=DI8(IG(n@7ua5nTOK<Q<m3k@Zio!HAEKDa^_G$HzaO*<nuBKOz2!;R*hU@lR3^uKqFjC#Vpv{_*ioaPqrz)BWjn3qDaE;UDE8+`~T+{)v@0=XnMG@w*B4@lS+*LU@FKBK#A<L;MrrALafHJm0`4%42+$=jtov<`lMPUh>or%JEyCtKX_|y$;NCU8gqADB<ci<-y0F%+2~OQosGU&%Crg_{|$4ev9TEKR@OAoB>}cPfoeDgvVograZ!LK7R8*9wi*VB`+Q*etYH$*^fSl!EXWF+nVPvI$u32Jj8EtfBD{y4-fF0r+%y7=-qTXU5|9#f&2I>QD4CWe3k4Gh_7}RZgf3TU%^9s6-<)*g$N$tt3-VQ_wZGoNBAnwV_old<9j0w*j}$E)erDM*ERKna$VQ*T-UW6Pc}|3;lbF$rQh&RqW<Z*`Ms=v%rNnfKk5Ai>F0I5@VMTFYh9EFaIK3uUg{FTL+WB0NnH}<U3;eA2M8O;@BO{|IBq}g_urCw1#qobNWDV1_J2q}E7$&4p6K@Uzu7dSglqp-<GNntxvm#EuKlmv|910&Z2y~?O{88E&smrqryk=`xsFriQLDiVv*XlboO<U^SePBBG2=9BJ~`#4HO~`XlkeBX@PKjZpZu_lyB2W9X~Z~<;J)7X{lW7nc&N{*mVY7Rx@y6qtgn)J+skvL!DlVbo^P^=^M&jA2KU||zn9r^@Zxgk8#TCZak=v~8y=DS|J?cd@Gy723Ea<}ulG6o$(^qc5B2$pp09HHA$Wb0^nZ<7>2_wGj3b}%qC8<7DUaX*<0u{}-=B%$G2_T*9C<a_o^cT~E_`@||6}|gz(f4+<4@&2{;$UIe>IN(^E}4?@h*?a_0j{4rJeZSSO0hHCce@2>uvE#(x9V!{}P|X6U7h8V|=1KT+=P(AwEf#Y$@wk=YhiYK5O!!;`6;n$o}z(!6zX+#wQ*=iQ%5!XPv_LOyEZEv+#*&EIhy`K7J^2e4;!!<B^r==XL%ZC3QDF;MCC^&G!W0T1T_%W2IcLhjU!(TW$Nf-OF;VZ=P#?mHWp{k?om>O}!N*Jm3BRo^OAV=i0A4-~QtEx%L;g&$VB9zWwo{Su3;tG#eU8``>)MJYUgLo>S=j)^PEa>A0TPrYsL?oh9ePb%jU&gmCRQkN!~}(r?Nmc%av%w7<ypx-`c<y)MmfPrp^$UVk5#;}QL)+*~zM+DZR-^iNV_qujUmEInUSQ+PD~{*v=mo<Cm?o<H9r&z-OG{P`BSUWey-?tGQ!&o>@eV^#Kiea<)hbN5x*_WN2dxVGQd{)B6Ls&SoHb6ne#=fSV?dj#KqK-$x{b@_H)-bd!;CG!2!=u5s21NWNB_e(wI)gssHlN^t9z3wnc?jwfvExZ2&p5K3w=k~8WzyI)%p|bzxNjiU;xLNx5FMf+*(hvH)h56sk=ViB#;rZ>&$h)QAzMCcM_#N{1K0Z9q`)<~eaKMDJ+sE+y_HnO!r9D5*l==UwHuAjb*azf#{ZH=4Szki9&pKjQFXFZj{m-2BC4T%{+0S8<rJtE+)St?$`4+C@tLQh~k6tI_dEU41yl>5f*=7A1&#ROAxHy0AA@ip{^w|>bH)6i+zM+H%aDQ3zs_gj&oR@MvU*!Q@&o|KZLieN3^YdJv+vm8RZ@_r;D^IA(o^PP*$oigD+415tUIMs|7lZ$cT%SYcxQ-X);cXXIW&NMb!T)gee>ih%@qd?5RoVWGv_Iq9s>=C1gy(%8%($y;zlAqXsw(H(BG36Y`ThB_{T6PwlRUp@A%8dLZ|;_!m-3)q+p=8yN4bBbeBNur-vc)J^Z6`~_GnX<Cui{YfVC@LkbZ2krljBYlzxkr-6QuW>SxEhmHgH2z9aWvv9!K1F19gsP5<7RKiPHA{b(-#C%Xd<`(ORZZp*_C`v3mP?oPH1t!&gHACInuZb9yjZh>xTV~+~^KN}4Qr~fKQ{;D9_h12WEOVR7lOUSRHm!MxEKZJe-{UG^z^n>W@$ivXrp@))BLJvisMsANj4egVgpnY^Dd3$svdI$0kM)VHoAC2UX(LbWskl#YDLBCCY9{o1@W%3i~m(kCWZ$dwZo=iR;JsEv7`AGE5=&|G@&|}fP$*s}7(LKp6(Jk?V(=}}DYGW6?(a=UCa#M68^cmzs&}X1~klUhrpnH-}NB2bcC!dGzj~-!TBzYkDJai-1J{ygReT=Xs_Pt6Q2is_4qcz&)gU|<~-L`dX>~5nrxjwq3^}y~n8W2tw$R?xf^E$B6+r|)LFzf*vFWb1E{1W<o8;fnMwehEoPta@8?)_73J5ICFi#WGJ*hqWG5jJ{}&&}xJyxzgajyAR;wuIH^JS&MNobxjK-f|loiLZ>XZZ=M_(Su{0f$o8J@3*F%t;naMT{~~2T`u2%zJYc+J>A9x8xzUn(G$@(5aaobo1%BNQO~`$#~5N`7<n-II{V(;Hm)U{zKd{rDlrAt$A0E~8yyJ0LfF1G_OY=WQ4hAGjh!-lS6F0g_L_~EHjcEfD{LG=I9(ubDu^ziHx?xS6TK0gkY}Q2vVW&L+jft((S>k&jE#9Vp0)7|`62W(=m*JT&|~<l)A!l^US;EI^2O+@(F5IaZS=Bn9O3l2<bmjcZ141ZyWiC|s>uIBSE0WrZ(9)kJ$gGEN7>ld^(Eo-KIHAtE^mu=ZFc7{iE#P_8w+hbkA4B|-ao(KzWQW+SdiM?U}G}j^my_J^a!?h`T$$I1Km7f<0RYWb~a8XoIadz`Y;=_ZM<mXb;9YF$WzfSKaRfMh>wR7!(gY_<8`-jj*S5}&PJbucJDXFw+9d{VA~n@Pmmb1g^k_aTwr5Q!h;=Xqmzx}2&XS0E`?ofW3Y{D$V1S3*<;kTu{U`abUPbI**Kis9{rx}$7gLUAU}tG!R~98jhW=7=$Ysx<j>Jd&>L**YCr#n&HpiyH=sALjnkpsW}J-yHV(Dz*x$xs<mTu$cDqAtv?U*kK8JHYn{fIp@*wod_Ve9roJE{jA#5AxZIfPFrTq}l7cTckZ*SvQ+pZldB%J<@aC$XS1$)%)>kb=_5l-Jp+(E6braq2cX!qI0Mn7^#^zk-2+vr3-I-`%}^~3gfvur#<I6a$i`coUn+GC8e(Z|NqHtx6a0J#sk58Ehr+dV~o6a5r=E_oGtF8U+F>F;cOYon$;{?>%kdy^ZZPqlHljXs3aN09eM@6Gm3f0Ws`%i9!0e~Ye3Y{O?<|J-EbM#AY)9Csvo6xzM-`t}0)*X6$G<7{kc;~2u}EeNN-rq5k}uP1LtuSb7PIPE^?`rFl}BjI#&;sDs*HX7P!K<ot@%DOs;JQ)3meeYo#x07$n=!n<*+3lLy*we<vZmzU(5&1;)eRjKl824OW;yfd)oo)MGHax=V8aCds@sy3H38yF67-&Cpv5hmG7i?^8(o3^64D1AZylvfBB%J=iZt$gz?+c=TK)d%}wV!$4#v;P$^)^nlak|?d`82f4T{HSrUe~cv+s1A-j<(UvMpL2#>{jD`hh^6>!s(0112TFXuLqznBwvYk`2w_WqtZqbqCL#%eR=KjQRrK2TyEnE!s-6xei?lkuU+no-rv>R#xcZxoM$u6&oOuX<<_<9iF;rN+c?O`wT#Q1(QcdZZ0D{Ory03UoCcdf9*=fwkjMJt^3G_tR=aCAcfGqC>!Vu}|7Gj^otrbP?ph(aCfRYPzqR=r=e-KaTUChu*y=SlekcEdUR024_%*~QyjQD2vb(>ijs6eseS-eCjSt=2Lw*bW7O&?MPOr4_qm5-Yej=P+PM(W)>&B|W-)o1{ZtZ=B{4RMF`d8bJ|FrQbc_G@Zr=J;FOI==qehs~t{2BUQ8#8Q7BAkAbJO}+GIwr3~$LJ5q-=N>HvBJg&<jv?WY<y|sPx4>rzj*ELXX+K?wYz7lk2d75(5~&j+xX4Knf7%D8%L9yqmM?nAlE@3Lq33TdS`MSbRGKF=`(C}wb6rc`UG+_^a<$w$UC9;L)Rjl{>AS1T^sM&SW8}qcKH|dTJ+Ck_gSaUviVpWXA@3$Bp-<Gh(3s17kv<V7qat;>fiCsp#`ad_Wxl8Vf}6NqYwJgFHXDbG<S`5Q9-Wj4rc$mpbsK<%Cw;qZFKpZOq<W)oX%l?XOjnH&e!P+3*xu0@tn(B7DRu8-imN~PjVx)%WcqmqT7;BLAOPBCyz#VM~@+#zRgB#W2%iggws>Vx1pz?ZzYdLyD_qfapH1CLG)(y7KGD#kQ<_1ZiU_h-I{zdx;45R`4V(D^reK;x7c`;d^7nH^k0n6KN+`9??yO%2>DR7%U#fipgWV#Lw82^A`e3MLJuUIcK5jdAYVfsguVvtp6T4r>ubq_(O*y}SD){A{W*CK+RfoJY&=OgeUFVR$#;`ypj}_RZsRe+={Lw5GWs)K|KjRx;{(F!dE__IE>B0#Lq9<{eOE!|jRnjZE+=T0|BYUU{)KSb%|kBNE{Jw{|H9vMl+*i>Pb~aBk2!q;xo6?;dCzH`8=dY?z5wm=73lux%gJ}4FGt@=o{rwGLe|Tl3zC<ke@3q$meXf0&qcdD4gDs1Ix&s?_vhIC2&XS2--*5qeFu3O+U@^wUQa_i{tEN^JA~7pkk_KuGOvF^IQ<jh^o|9|Zq9ew<!0y|(M`!+(M{3Elg~gOk3OAnx-YpOx*zA+mvDM4`4040^zG!w(Qg-IoIFLIfOgMtUM$FSoi*e|<QLKIS%Q0}a4+HXGsHxg8}BdinV0yS)7`ojD(Y_W-~AJ=fB(4k$&~zquK7=v{u(L!$(QZEioaCq)^#iQ+}%{z|J;L~x$cg_{1;94<wp'

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
