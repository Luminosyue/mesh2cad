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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_000.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_000.stl', 'source_sha256': '5198683a090f303924a964a8da067bb31732ab71d09e0f15a16f26184a4b9c09', 'input_faces': 1122, 'input_vertices': 622, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3866061568260193, -0.4352560341358185, -0.4166320860385895], [0.25989997386932373, 0.41006314754486084, 0.43581926822662354]]}
GEOMETRY_BASE85 = 'c$}r32Xqui_vKq68%#2Y3?smnM9vx1<Y*8%!$^S08H349FwrCdCc~JFK;$Tb8j&O<git_$Fbu&a*<gZg!0F$w>eld@_3qiT%Xi+nzqx8vSG{^w-80kr9Mn2P#(bLm=d1N?_4(k$I+{k2L(8X)A24Rz;C=(fRv0mAqL-Fi`1DWd^0uA74C?Nsjn^jo^&c>{-x$9-4!?S#wfxFC{6a^L88;?)MBkBP`VSz#S@5v211x{+px{vhtk?cEs#GcGs2WhtG1c+^`0o>|3#Q+h8&Q@T->pp})%U-+M(WtMTKIbET;XfYeNzH0asB$8{rGw%<?)?o*^W1gcSxq=_3xgg@#EbEyi!Qb_i5s_IWh2-(4}p!abLUnCdKA2OOd~SF7>8(ow_EG``VH|sodArCJ5ir_N+MG)i*LJkonGDZBx1L3XhiUWGpNCqlXSp=DxB0VG8%1euLBac->RFTo>cL^W$~VPUw2kjw7LEauoB;pI4=D-{|s{Jl<!nJn!iRse#NlR?JJ`zUkNEx-FmIc9p;XuCP$o>OHcZ?QO0FGT)u2Ukdk)g_=D6@mX=a@oH;A6!Y~VV^VB>mD3_$+LlJ?;`PLnvK{zFmMh8JcmKOb9{;+lI9}Vn{Av{Q&Azvjx$p2@nQE&a_v{;DydxW>+Va`hC4V2jC!g^3pzl+7K3&a@rv)-!<<sLgADhDS>H0j+4Os^xWxMs#MgN`EmtNz(>C-)#`>v^>DZJjaTc@uEGGEo3@{PXbQ+PcawSD5Fn6K*D<NqEYkI!>K^v5i<LDZr0jn%D^ZT>?!AD(=cyKz(aD~>1I>U`iQiQM<pIeho}gSK{@y%r}3|LxXfo;Q6!6}kQkFG}X?TF*Qxjr(d{d;GgI?Z=l{5YK(j@$e08sO`MYVVUB@@8A17$+jM6KN90LbN!LT$Lnfc+UBeADqmZBKZ(za>z`e6Ux2ULH*-WJ@Z;5dspHL&@kzG&3I8dX`=0uNuOD2W#K+}$)?AEB|Fv@xpLb`(Ww8$^U(LJnU0<|J;&tf0(C#MpRUIl{Z&z3L|L#OF9#;vc8O8mqg>KmV`n7Gx8=+UuaNqp)O&a&jfVbE9`qgVkT;;x6zslE7{cw%1Uwy$ov7ad4vme4Yez+iyFMd?+XZv=D^<_3)DX&Xa&kEnMYLu+25+U+<>`TrT&r-Rs_9c&BuZ{5a@cMH7%&&V=9CxIQ^v7+I*TXqmMLv{oUW!lQzTP%Kp7+O<az5s4JSC1>o>T50*oPgPL#}gQ?Ze8~-@Z@e<1+G25_!|wyiVlxV{B_6_HA?YD|tP{zOD5gBj!i>YTs7A@#1A7pI=AxofG1GlYW-|(?epsj@7f`xNmg1n!<f;>@#_N{wwjiTql0*{>yje>b*(mg{O(O^>z6{BKOt&8rg@->r1X1@_6?fabM!>JW=#h-@QWk>N@DkabNE9@YQut`Nqo5iM&2tdCJRm1z**t@-_du^7zJo$a&v8EP?yR-wRW?Z+=-v_VdbpdHj(ZVqD7CS}sW8zIHTQBCmh#`47q5SM{%a<Md8B|LxDE@;ra+t2}F^mR_~3i`rvFojGd`6u!}Yh}`#_72^Y$?>gn3!hLsm4Y`h&e=YV0E!k&h)PMNq$#RE89qp`imCvKIxhDE=esUs#AMegKJUr?@d_Aq}VR4?{cL`swHB<I;NQ>Ag?q`+vm&$jX+?2rAh5OQ1avc`=O8B0AzG;zE?tAug<+mIm`-AJ0u|Qtem9MT-$~UK#PvG^ecgiF0CuinP;Ps;i|03%ZzN#PP>#uKK5y#{DWsEW9{tsVWzdZi&t5<lvIbRM<;=Zak<s12;g|Ds`j)`Nhb6;IAl<y4FW&7<b-{kf7v9IdQeKJ6v_r-zhwmN}tOl)xL|KzLsaTRvR_TR_Ier9@<z<qZSc|YRu^Sp}Z^X|ACChwn~J(d19kFWE3``B0YrhM%|mRtXIyz)KA_maNndJ)lRzjz&VH=eIMv)nOxT|b#7+rfUT-DwhI^Kt!EzIOS#?B}BU@;>vk2XWlj4!M%KZ*19O&%@9Q;^(ew>*M))G~<60_31t~N%kMtHAmgZSnjLqn)3CH-QszjJ6GJ6?^DLrmF?qt=T5vO^5FQVyzO|`vK-=g$4X!6V?Q@aPmPG;ezk))xNo$(6UXyrdbNz<zPb-lzWewhc|5LPdW4?DeRcg(zN7I(+wso&pI+j=I$rti8KH4JZ|>e>Wj^7nyeVHF)Fh7Q-`V>}jHp|G|2Uop?ZOf<UXQ>3`VH=DL-NXYww1cU*W<^&T91y%Lznry=u@j+6z$fWe3`E=<4k6G-vwW-FXbD5jk?V1Q1@#uuOIML9V*}4?RS~izq5fuoY#FV<7K{H+>56R-?b)A?BAY!Y*SHj-BG@0AA@gRSSNfVWRhG*B@2sooJpgEZ!W$g>cQ2z_O`(P@Qt;*4v2OZ42reY;nXJ=#QElTm;RdP;&`ob$*uq8>xGWZ7vtR9R`%zkeMb5J%YM?hru5Z)#RS=|@;&zz@Evz@$>TrTSC#+qzWTAR_Ep_`l3X{q?mOaYC2?O}_m!`O4~gM*YrcMcS+p0~NBHWxZ1|Lt_rc1?by@kkmQnhS>NokkeC(@v(f{z4=MBVl2l@ZlSNS)#9J^$zx6j(h<8sav{>S$lF5mvb*NuvDzWn!Z4`jZ!C^3!u?%s86$D4l@TOY-Ib-eP8qhDO&^{f|YEI$W;uj*O(ju+mxeyVwNj=y%1*NJQ4rFibEI#Isi43ozPd?N2>cCR`w@)VsU>-yyexv$0+7x_0YUbw*L*EO`Te4pnVVLM*ywP3Y4Z^A<1t9?(e^^drZRleHyl&|;dA^obq$<L*(gq`EQUc5vy_YL2m3w$08zeusKxwBM|{lWfhPS2FceYHO;U#sCK{enL7bE7)jqh<eYoagz`FU4IF{Rvwyee9FY&F$s;-=kfG@7b>$8P1A!r*%Hh^QOm6mg8;r<{Uq-=Dk<;W7O?)wsC32<^6HTG~v4oXOY*_Un9?QU-S7qnfrRfDB<gc&&&J&{$XbWnQvCZ`!D!L$U5owZ-1SyyN`Xf?zAC`Wc%0;U8@?3Ja~Lumpy*7`L^SYE=$kYd|bbjZ*G_^$8|9HI$zfx`)XZlHzvq_ep^f4R~OlGF_8KCh4duu>ur9G=IhibJ>(?!)jCza@poi2&!_Hc9~H%Xl~0d9c)G29SC*Kg+*j=@-@SL7@ZDou$<LKGy3TXoyzfrpzBX=%@SU$sIo`m+Vjh*R)$WvJ^D9+}=Jl-Y{7vl7TK<Z%{aQP1*TIi{&vkHadD%|>t+wmk$G&I39e7dJsoGE4mOCNZnX&jRuYX5GL2(^&PIKChcQzPzShT<Js>$cq`B%KS&s4seU*)?x?UZ%5M1Buoe)F%WE04dqYZCVzuCgXSuXg<HMlp`(C4}!-Q9|ykZBoy1Upw>W8uyJN`E2bN4F=5>{koUa<n!zLJ4X!n)%+^o(W-V7pD%sjeR)6Q^P5~B*e8wHW~aHY_DSXI8_u2<?R-~QUI$<GT`$IW>C9=Kf7jiOV*hkTMhM^Wu$sJIJz6lD`(~RzuG##Xt8MLTMd!{CzrQZ)X}(?@O^=J~i}KZaQNF8T>?zy0=Km1Keb2by>p_c8@%G(29df<FSM4j`ne&@dJfDu7_2s%w^FPVw%Uu1LsB?!`3E`{#R$nRakCm_XTjlHBGoQ5O!DsIp(O&-FBY8WH72k^2%2(|u-@WHmB(FDT`G3WJrF>Oy%Gc5#MDp_*gN}?Bubc0Tw5_A$FT{O<k#*?_zK*nMS>*l?U#%mLzdP^*Z{JmI++LCYc|RWKbz=B@Bd^o&Rh=l`h)FnZ>*wT7@;*7!c6t2Gfuf&|Da}_2jh}Dxwdd&r#qp0i9OrfG{P&1>?P^x%7;oQ^V@bI9z0ps^{;Kv#^L_tV?yG%L`Fge6M|nHuftD^=Hwj01{b*ZHM~UN&ua5F{ZEW%t>sI+{T`S+n<v1#Tj{C{XqoV_v@425;{>kx2Z24*Lw?oXQU)>{oe)Y@uP0`;j{<h<_n%}Gu`HBAdFh8%JdN7Ln>b%M~GoF<`_D}b~uVZXJ_D|(&Hya)1b>-?)S*&a2tGe>|pOrq$`|tKyD%WS=_(Obtb^Q~$Pp!^$(6&woEIlgv`{S+yJpay$f6ILUzRJJyT}!7P;PYr6%qsS6$L$UWZ0luT1GL-nfNfou%_u+5*_2JTkNwJYJio|&wO=XU4BxZgR{w=Mi1+F4pJv&7vs^o||G27ZHeXA-w?nk+-n);_uUYqLggCx$@?P#66@0gd_FHt0;Q2JCzZBP3cZI4Ewt8;-<bufO{rElN=h&~b7Y*d+0Pxj*rF?C4_i)~hBjJ&lUvu`H9sInmtsUik`KTV-MSIE5<ohqJkle@MYt#Lcxo<wnCGRiVW|QlEb3-wYj$(5+^YOYOO3Hm{!|w07@0@U79A|jX`=0mH__vT;U-^4{Z_D%U(enOwUk8_MzHY6T`EQy*_`1)p@_kVK@#na&MffIjUpxQXCf<(wc{x!(jxtL&*yeqiCg#JrVDJWBhpuJOqR!o`H?FnS=k{Ep&YWSd#rifUl$ZP4wXZ}yE8n>FQxf;}dA+6I?vR|{rhmq8-{l>g#C?}<>S~^UZAggRHzG=h@&0H-v&#F-#5zkvzeZM-*Sk@<<^3Fdy~5ojn|~+6V&P+7a$a5|=0*8xU-J0%{l2x$d*Sn9Kh%ydUC8_6PH7_d6Yq8NZR?^?pcs##U7sh^H&X6bS%WWfU+r%mf5wE_ynb9h-eUhZ#t)v&`>&VnBlmguo_!U*wmJ7y+q_q5y<7DET*0sTx={By%2(^c<4>tL!B(G3a>_cpv23ImZ{6JTes%9DybqGT(<ft+&42r*J+B{UK)T6&RX-j-=tM)FPxs`1Rtw+kk(>LPyLl(kpP<xAfvkRv97W}Q$>Z~SAn*VC&ilmcgJqq8EYI$fIj@M<tG^84$LphpiTzDm?wTZCM;DZzOV0~F&wV5P-8Gx<S~x`<uhwsJ>sao4*01tY9!(R+tNYA38N@!Re9wKR^5^fL9?0rY4_G1g6XVCjGkE{a`={0k|H-|X+}DP@87A`N_+9vF9l2-TI>mjpj+C#Z|2B)CR~ueJ>{r?!>*n!%YSCp+iPs@tFXr>&9%0DOXLE!u<>NJGJvhsKHD2W#MRSD(vidO=W)SZym9OeY`P%Tk%WZk^Nfz(3jLGd+*y<s1>_qW<o4X5Ntqb?(i_ZiyU#$y|KOjZ;s{ZxNCC_tT)xYw!<|o(iJh<{7lJC=>6<cSk!`^+xx-)XP*YkNXp6$OB#e6j{%GVw|+ra0=Ou6S0uQTu5$bF+{l6c>wZ7?_Sde*z2Im>-j&&t<x_mu6WCCL0l<dvV#w|wg2b*{B3D(~;%t2$S{`5^lio(DZWkF5WxH-xXQ7w)bBavz4Tt{2KTr}%BPjo0y3yx-T#O%cB1Up!aXfB!Y^YxD1>aNoEyWE-z5$AdwaxUcHU<NHQ!<L7k@+bQlN^{~C-`k>#9k$H&gBcCT3v1_OBv2SZnTZ?s}e6?>YUpqKz7tgc$JXWi=a2H=M&LdvY+*j*G`9{HayLeq0N6w4uteLlAxNY4%>Mq~s!}qK^_}bynaNd7+|0hSd?|C1g{CWq%WuD~qPP_l|4ENRb&f_=yE1cK4K04P0?yEXizL_2)uVWpL$<JLIwn^l^Yv`>Mo9{n6g0E}yQ8uxEDqpQ@<r|rN#r>V5o45R4DXdc>_s!1hQf&Sw!-TJ`Sty?iJzF-}=I76w!hN&K$bGgtNxLAwr+m3_A72;FJtO3O@5;0L`8=8l^~Ckm)g#A2;qQ4bKR>BhMtpy-d?T-XZbbQp5qOZVQ^%=((cD+-RQV3S{RerSJ72Yt_dmUF3*Y>CmK^W-i}HB}<zM?Wh5N2%Z*A>pE9<Nf{+U9Dc%8c<R*KJ^jNX+G^Y!a4z9WVEYW;fr<feyt-t?}k<>#{@Q-tsNUig5wygxdBLi*32$?va!&5&gC)$<bls$J*4wpKoe=sEuJ=p(#N%*a2la9`Dl@{OsnNBBB2qkVR9-}8Nq^1sV}l-G&dx3K)a)35kZ-i{U<w2J$l{RF=GwBb>nXJ={?x$b{U6TUO*jOf2J>}VSIwP!)8+&Axhb4>W_{N!^Wv$ENIz51gR?rT*K3f~;~Kz<*$?wtG{MEPCzCUakJlXA?quA4VZ=DufL!`H@UIWF@gpDWO6o|E%Gw4u#+R(ma<lj%C-IA1TWNz>xEuhxt5&6$sn^So&-9P)m6^t}_d^;`Om+&?n)i{$m7wLK))JA73S%GXDPM#{V;%kMp3O_2LNe6v_^s?E>vIMP<njT?yiH*>v<<m*L0(leg>YP~35dy)I3oZou#x%UdO@_r4zIq;7Zn_s5LNxok6x)Jg@G5Bg-DBsLF?-b9ED+S-bj$SBySH)fOxytT?<^45$bCP^+N%>~hgR&j<J;>eI@44^!9t6IA@z^OoUq+`;xj$5UXluu4c0%0$DBp9vgRf`rcAD3Tqr{jb?yEXczL_EHG_N<;A7y1eD&{`J>))J_o?!D)|H?PL3J70|m?hU&-%9d17Wkg;-{I>~&15@$8;IvB-NSO+wE3;BC39c<ZuJ?yzVt<_<$V`?wZ4>Z#P5mX^Jug#Eyp$Jjqug=&NZ@wxIgjuxZWvW3(qOu&$+ut$#D%YC!cSJue}?W!hN%Pi13|hYsB%+=fzXF@3}6o=_U4I<$JEnANj`QwJE$ESJ2PG*ZX&t&!g^;e~+PjGv;ox&5tf7K5tO_q}jAcdLZ-FKB;`Y)#9_f4&9q_$-mcFd{Ox7x~VT;B)>OTKCYX}ckhlnYg_N?Il7GLXL)_PniQ4y>F_=K7<_YK>uBDN>x-+RpJv(d!dLr-wzBj!?yG%6`FfF=(#QU<cgdB`eYO89-|^i&d7qwO$~<SElxFkO+a`10DEbub$o<fj(=D$X@YR0k@%v{w$LrHQDnWi<l&|zTz8;+~yUOne#s{C{>&x-DkGxNVuhy6HU1O%5<MZfh9WCE4_&+|!^J$EKDC=Quq4WH_uGkeaPlxNu@1v5_<ln9M553NPb9%32?rU=zo#*RRTQl=2_tiR8z8MfCkH>zlmq@wEeYKx^{1&Ir^Y!I;+$xFtYP~4mh;MblmS_Jy@_Er`$1d2$TPR#UFP!c41)d-CM?5dR``AUEf7j7-H@WY5ZUnyWQ|c10H+QDSN!(ZUrhIc@%}c!Aj1xOjZ9eKv`C5;jmu&s4K1=k|X)L~EtDiM~^1kJfPYlnSD+KccU*%2tW|?*|ynRRV5%JuUqttxa4)znnr)CoO)qbLUWAf@4UO#$CxxSUJ>PPu{qu*nAJvc`ElgNEl56ai(REV{W_enkZoOj{<cE5YL>~FhXm-#w1w#w)Am9N&R$DcDx`nXOxUo@51W#!{KrF^YRt~g#N+JKj7+*fs?e7$_I{Qg$mS7dmS%ze*&h4PE^5cff9|99lbAoB-b?f=Tx-j9yw^X}~R;5zp`*BAJvV_Up!-e)|JpSz5&E#3#H>!7>DcDcUbtLvch&EFqf;q`CcXd&M>z*qIJe62$E1U_Gmj@M;f*QlMq>&+dzPOc01s@^<)hE`X3|Fw6;<bD3Xp*G(g-cH^(y^()Urs~Z(JFA?3_^RGK{y6z}U8;WEX7?2CtNKyCBRwpUkIS5PN48USv(4A0<V=kUvi&t|-RQ$B3s%=OifmdwEi{<@DJ+@vPw9XEDeT~C|5twsTe<T8@880Hve4?oXe&k_i042Tfk~sl-&zrA#V7>v0tE311o34A@fig1H_&gv-++fhM}dcfXG0f&XM;~ePk>K@uR$+^FXP<A&#X9N#Z%~E@Kf-=&<o&y!J3!Ui(rb2XzwE0B7SMbaVvg>9s~ah_VSW?2~0uk4UGX)#Gt(xv_-tZibGZ`h3eo&VDh@)^&u#|?rlY5yjD!w2D%u$9!%akye58b#S1I8LwA4=p-)Gl8^Qab8^QPSn)Da&&(L4c<~_7ax(2+=igs3nThS1_3}bDGu{VUb6u);5$KAv4wZpl7!8o3?bG`uIgWd<<1BXNRgTukgpc}!<z)PVU!0V8w_0S#Q_29+OHQ>eIHqdt9HsHq4hTw+CMPq0qa1SeHS<xLj6Wkp<2)YwI2s{|N3p^Oy13C*_(yGrYR#Zd~*M+tN*9EtS_64^G_kvCY_X3ZGE(VVV&%n7VdCBva1p7hjgZ;qOp&h{0!9md8;2^LQIu`5%Pl3(^PXRB1&H&FqKZ!rHqAcrYS>%SaHMk169kd^~9k?%aHn=Z%B6JOSB6u;*<%jcs1}*@t4lV$$01X0H0JnuY!EM3)p;N&9!E>NXz;nQBp^L$b(NAJ8Z)=aU;;xrex0mFM7T>ot6Z8Rip{3tiF%mioe9Vf&Rvd>O0YA2C^obR3pud3&T0g68MImS%a8WCYS<wI*2>#vrowru}0euIKw0?Hdic`?j;FVTPu;M%D*I-%;RQDC3y}+cS!K1zGHBMR|LEHgB+#5kW7C}4{Is=?$^)=OsPrYOie*(?mC7FV_1hgKw1h^S=7`PdD05k$T0K5o#4ZH}v1)2ih0^SNe2;K?~L!bRI4hrH-@LGX0ftx@>!A-zppkd%Jv_A%8r*W$FLR=Qw3|to68ae>n8r%=M2;2`m8@dHN8@vX(6}$$#7JVqd=A{5~Kw81;!#q|%4oKUA{lTrE{lTrkq0l+tP;eM@EqE>ZL!1fgG$YgtOzV}_+Fj^jFs(gWpU0pJ!L(j!t&N1%2GiPmf^|vy7)<Lm9&7duI1ZWsjsstTz5~C*TD^j`O6&P|Xi+e&Z(5rTpcBBfR%t!2ghqmCebZia3VI(*`Jva|$Pcj_V?T~@A4iTxVT^?^zCy^wZ>a4AtkndJGZhh!wHl9oj5q^+uO5`zsfQpQ1|0<+29AIp0Y`wZLEYeM;1uWsa0-~#PXhY=4od4#?T_z}?_%%*p>zx}X%lcD_-p7GuMhj?*O-Ts;M34C;4$dSY3Ktm{eS$>Te1uY;%o@w&k)3=5X9x6rNQ)Guc{S&p$)*KeZZs!m~=ImbOyM&6=kWmHQBd<I8Q<N`4DB<xk+n6%YtiydqSIodx9rgQH|=ticVHcfrdisfkVN~tSDeb87ust&A`oYj30uyIJ6qLI5+^g3P7F$;8#UdL(Zz99}N(lkU!PeK8PtSm!xZ<Q^0G%6QQBtiQt~lW-LF=kiTXar^;s;<hvZW6tsZ$p*D!AUa~>6LkobjgL6auz<$V4ZUk`=XaKkfxH`*Yb!cC3b#Q0s3~*=gROo8(YUF4tf_NZwBAB!}cp%sxS`h3H&Y^v%-5k&i;2dBtXf|**<i!g?{3$dyI5)=sDT25Jv^uyt##sVETpv0WJQZW85A_Gv2j_w20OvrT@<2ZYe~NPux3yxJ6)h0NUm}QyB8b035O0I70&lfqr4?tPTfn3ynDhpi^Z}UkCOFZGgI3H#-{#>w^WYCd9AxJvjfNfsM}x0J6T#QP4-kns_f;!)TX6tEJQq3*JQv&_K|B&;ABk~~gufCo4LO*GwzeR4BOkkQZWD2p<>m(Zdjr1e|5c3dD*CF%djR>^2L28@m(AT=%;#K;LCr5Q&3OxGFKB;oe~hgcf_OR`|8(eC@O1DV=uPlV<a`fw9(WIUfc9bT2S8hZTj1OSpwq#%tY~jVc?59{1aT08_$vhQeCT*^Rx7OA8_frr1x%VBO!_&Pv<jH?3vjR%Ut7@{eQS;Lw1(dv@ijX)=?duA;1%F;&|vU5a7QaLY4mZdb)RKLC1?|<FSrTVX+<k5CRkA$>I6G+Ol<^lPG}}@POyetX~>fX-y4w$Im?88WI+@{{#0M{BPy|6lGcS*0@nq1gf;<p1doF{S$>?zpA+L$`J8}!&j)`6ZKZvv4PvU78qf;RR^STYqR`sl+Q?B+1aU^F2F?i1%<`BS>I2RUE)4wwTo_y#S_NDMIjW2xZVK%PCJhER1=oSL2G;>s)IQX1MQC|&MX&=}16%`naUh8ELW_cnV*Gg##JQlE!I?46TnOTl(8}P-7(+>D9dJo-F=$0_Mf9l{G%q+W&Oz+5;=C105X74h#ODyiKOl&Igx&#nv!bOHW1(Haq+`IO--Ai_fk`)mCs`3;MF@g844MQE1D}N62A>4SLX*L<;8O_Vy%_smjAJkS^N3`OEg5ayLEOf8Z{yrQB9f4sB=l9~Dgyb7z}QqiCn3j6phKXOz(c?tpdsK6;FgFG<TwO*>52$LzQd50F^H4M{Ym8IdqgbeAr?8>hd70~X^A=RfWDFTgLVUV!yNWQ5HE*r25&~2%b|P0%fXY`+)Rcp0WZP1Cqw&zeXX0khF0W55IYdWI)b<}g18&B3;2=M)?F*Ic}e{VOq$h8GHEF=X=N~JX)yJtJZqb@1++Z41-O<KO|7VDMMng2b7+2Wb8tE6drfjVa8557#1Az&mWLP*>3i^9@K4bE7~fCetZ2U`I4igmv?;h0SdF_f#!?x6EjG3m(2i{E9g&+Z;BL_7;BMf~&~j|<%3(gsVa#fNb7Ic(K{G;gf=MYC8S$F<PnNGgp)`ko;x(}k=Cw4qG{)uwEf4kq=YslzebJ{}(2U@WI1h2UrGHzIf*`(yApQ$MoX1NBadBu~FUdu$$ZbV6XkjpERWNBAFli?+>6c*YPY%{LX&ET_We~)Tt!QaQBP(hkhy$RXg9E_Xp_#$i!LKwK#Q$h=ETp-inK7o^IKD9Sb8umBRcIq{Rd5?<OK=;o8h0m*r4#(dY;0wqHQ3mR^CD^>|1~hq;)npuRRG4R=8l-=Gdsqu=JyrmJO%28z5<i}19pS6uzY1f4O9bX0e=Dg68t5`_60Nt_zUoB%rn&iaXR|+8tMkSaem@rxDhUmATEj^{?|(e@sD0Ih;KrF@{&Bj;(=ClhxP}Pb_0{P0+TiclePxuu;Q`RUQTb>x18ulPWbA^omiclG#&aFoDTj2O6~rE*TlY71Y6PAicVHEgjR$$23G`Ux8hSP9#LID$qT^G8iNDCU7*3>F5pmanX6FbDHQ%dL@;s|jDGY-bVB}AU%Me1vRsljfHnj-0Q*8Kf_=f1kBS(B$`5fm^byPFBjo!g_($lctTsMH%@l?DLCN<+5C=j7zyZinAcD9LG!)zi9K!M#0__eC0e6PB26qNGf;I&=MUEOFh$}&T!K69BmB3}7Il*PX{@x#I*B@FM><_L2EebA*yi`FDw}b|Q12O)V2;#2L5O4^_*%d+D1lkDP2xDjhEdy=>)}j7jfAmR*wgk7tIf&D&`Hi*WA%gfif;a|2yca>d1G*3Vh1FJND?WpM4kpbDCVlHAne-)?^d0z)rI)O@?Irtm8|S$VKNfL`otyM1^b+_eI2C#aoC<!4xPx>5K-UK=E+U9;K?`_Gz6E~mC4;!Qw;X$MjGMFoxH9;2D7E!DUK8hq{s5*RR=IhL{=UUAs{cP=d_SPCYP=Vbj~(E>&|7ToZec!eVGL@1Ut`W6LNj<veGMk1v1LFI7i8lv2>lFP5d1ghm2&(ya(xGU2lM(jg7^)a`!~>s;D_kT8)!lBWGjYP@eP7_5`uUzg19?^xGS^=_<|MjR_uYE2b1mwldc1kE(epY2UCBhv9?JEL8pNSfekChTQS{=J_zE0&<)^$;Hl94;HltM2;vhM%L$C*1pIi!evD~9+B%Qefbng>xpyO`W31EB*L8^TY~0H+mgVpbHnu^~K5XoLkeeRhuF!$tuHf#_sci11Vm_y0%xZpDVa~sSx}dATtB?y9g7^T-*8%7r@B#2f=z8#ajBO)y8h9gkHFPp~GWxU{>H@oP4&p>BqO7=qAijzqK7%0Mi6Gtt-34A?#R@CFg3bq%jsuehgGqaWNkhQYpY5z|(q+)?;AP+uRt&XbxD~Sy#7m)b!Ars0px=YHflUN)IK~o=afHKPf%qO{`W|h~N6f|e=HlGr5W_Ln;pl5HVkjGTPmHA}{1I$y%b>H^*k>U(yTF^EOTnAKJE7ay+-<{rZo`<>{F<2a8_+nY2{w_7I0W%#maomwufUtZ^PnN%5R7debUSz+_$)LLoQOW1g~oy7a1P>{)_&};q8@^{27<T*f;bm~_#ZE+xxqhM@yd#1=rb^B5|}g^OnL}RdJbIDYA>4=nGwWKyrjPHl1xE-1$qyB1$-I$EBG=v0YUtUw;cN?7!T>M7?T5>8+s2+LHrNA7vO)uxzNXKELYi(KhlycpCyswdeHLFlHl^-JkZSGJm6QzGx0O%6Xg3Da+CzU0!{))Lob7)!H1v;;6vbZI2X-v9`ubg3zYmU&}1+L@l$x`z~|8BQz+&ADP9wo^8PS4rJ(h|^>FS|&@AAgRyeH~jvyX_AnuDG?tmZ;f_4O#v!bdM`JrXOr1`+4zj;X}{RK?=JGibD?X2jDzV*a;dct=i+Ocz!HiNbUHv?CI)&*ApXSJf171gXLY{h#osXlmJ4eSH1V?_@u+FH>DS_fPQ$FxBZH;2{&HwV{8uIeLC_2E}V)I!c`p&w-tg^@qi*L-+Qta3^E9Qq#o9Gn%$`e5u?F}4cOIxIhRkiR+@r^;tr<U0u50osGrMi11>5a=Li5AYyxFK8QZ8|0`Lg19}jKDa%&Hp^peXnt^Qa1kigRS~=<{u8zK3-}l0=uZT3A#bUaqe944U2q}rm(ZTzFTsPoKh*AE=y330@G$5Q@DSu>7=pMTv=_J+#@`P?+yYt~TpQzTfgr99rLk3q7J^?0{jQE6?hPFb9*jQqhV}#Z!#R56cYEVC?M1Y&(EdW#R=Q5o^^)!t>AsKd|LDCBy^o>yGxT1b-j~z+bNX!XH9qg7&${Vz>p$_`&18HZQ&N-PE7JFi^lSq?r$Emu(6c)9+zmZ{6V%$vJ70$X-G5^6!#}#0)olO4!H<8_{^wZyH*?n2KKyZ3Q0q+MduMO!fAq&s!SokL+W!E2jN+^'

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
