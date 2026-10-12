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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_008.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_008.stl', 'source_sha256': 'baf38871d53303a51cb1ee8d97e57acfee759e810771cdd54a9975ecf0cc099f', 'input_faces': 900, 'input_vertices': 504, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11118952929973602, 0.1194421648979187, -0.04283895343542099], [0.111179880797863, 0.4999997019767761, 0.2269868552684784]]}
GEOMETRY_BASE85 = 'c$}r21#}cw*#2jM;837A1(qTSMT$FQkN_<dDH5Co5?lg-;IKHsouFCV-3c;SAP~G*u*Kbr7y9MC&$I08mj5~b^L_NZ=lSi^%bh!S-h1cH%x&w{N|-3UhCjKq-bFuWHh$GK6)Cm!T3B$e-ksV7hZgQ0(%+(`5nugr>GV2{{;1c~qJ?P#eS?BS+x7A-XZ5YnzKm}{t8e=ry?Xa*)4g?%UO~aiuimC>XmGqA+ObVYaQtt-l0`}sv=+}_&^p-qzx<P2HRW;Gp8cvVho<lISHG_h-Q;ib?X_1M-}M7KM4NrvrgTvr^=#?5=zG4_w$^U5|E+$n@-F{B<z2`1E>GW8-kB<7mmGJ>sFUiqy=;}OqIZh!H2ZqD6Dz;#@5!-8>d82Bht!|x<`Fq=%v7{1BoF-PmH6$a9guoPB-!C{z7fMZe$O}3XZI-o?R>q;e>*Swj>GS^OFe7Lif<ouPX3;wP<8mdT8i%|xEFrQ(c8qI*Z}=DtcCctL0#dmzI#^cztD7tQft=K;@cDYoRi-t`-^Wcd3LM#K?zPtJs<N)`<?Y>Y&G|r)}_Ks^j}w$&%7G_AKFC9>*?EyZydZW$2AIl*ek~w(Gvda`)JSDeH*2ndlRGnV6;bX^Fe&0v=8dn6T#o|QR>krT-qXjw?T4TN6LzFTx)?J;UDRV>zgG``oUVT$tF4ORi_-+Uh4y{%jA0E>-`?0oeicflXfLchVs6N<+#SC;>)G{dmr(&AqmCTnm<83t)n)2<U>pAto`5d?fI%6HkbdF4_@V6zIS<T&&MO*t;dx=tjBqLI{b_Q$e-bUQeNv_2KDG|#J4qibV&Yvh3D(V&(Q?sTeX89{BWJeb+5U&q10bw7W@Kl(9a(_q5fNT_z9MZZ_QLse8;5QYo$H?hKg_WNC*E?i#1X{Fid>sw()XY{ZyG%a$OqV#C6#ci1Ok2#Miz)LjD}A93kh?_xeh?UX9Ypb+K10xmGmILGkr)UdMh%=SV#tqr}&u5{Pe`SxM@*&5K?v^&~lSP5yqR^s&;OUVX*aYA?So=Qa7=2|2#4F#NUoP=3?~DetJ57xff4E56b78Or<Sgn#uHl)s-t%3G72UnK4P;E?*AKIf#oF>C80^Lc4Oe<DAN%t85u1yFzFWvR!OXVxNfzUkxgE!qDa-@dnIw7I-1-@MCz%R}$-l|LW(uFpJl)#Lcfj^k!3hIU^1Am`<r+#TiTS4a6;zhFKqlm_K%2O*!soN^pJPh|(LS8MofDr25*oLqdP+G(lZk*$*SgSPo>q|{&fFY&dnuTGeKBLcqh(`EGYCx`g@)j3z?eCBV9_3%qa;JS~<C%&`iAo#B%rM#nD9{5#5B0a{-#@>^qT%pc5?sMdW^?Z3LZ+{qw@&gy$kl)K=q&>E<vS@#j8FF0R?<(5ax;V-&OfUK1I9p2QZClMk@b65M@>-1pQeID#Ez&$r9o>qfpZ6z)KXw`B?U>BsI|sa5DDB-e>$>^8^q`mG8^bC}`)$Adj`K}=8UElK;_J>Fm_LSY5#K&ysq~M%|IJvlZ{)9udN%!w^Xj+`<)6||br1gBFqB`mPU_KnYiN&uE0iBO9Q{1tjO2sEuL;`Uy9%zaRujkFUUs3m-?Vo3c1b;v#ZkWfbm@P`la=VVmFpHr{ry|wdL0{jQ0mDUF1``d3-vcHg!^sUFY~2*h8F1mD=EacM&6ijKCZq0Y+0WeRijb<&0t)Y$Hk=mwukG)H=5hgZv_s^c(v_sh4Kkr!M}J}+T%!C82-*f;yW)tK>yVLGEeH!OUB9Xf~{q}WIuKpKIb>9GpE#}j~yYt{SRNM$NDM{#(h!0dFJ*TyNgJ^8CicuJ#UVqeBZ{Hf2Mw!EB)!0NRF%hI6&4{TB&>D+fQ7P^4iT5XlKrw@L$BCp7I!{j<{IywJSs9y4ZYtkZ*^gJ?b%@SHQX=)hv|ndKTlca6`1`*a-N=Zs0!B`8wu}5k27_c#Qi<h(1=-zx7=6`RZF|NS@d})y8oLc9-@T{q|xWi`C(u?Sk>!Y$^POCB!#!_lI945!(MX8OlG#{YZN`W4yHgVM6##aX)fy*n@WNem}?D9&0h1^rtc5iTL*S!MMK9>g*K%P*3rVwoNX}??vyh-W%Fld_8R@<n81Nm<LAugnDZJc|m^nuPo*DPwykl$8~(VioE^0HNsrKp18Q=m34pX2y;F5CWCe%kNi-+(lq4lK|i^_+tRL@E%gt)j`?lF3prnBhW4{P^6hZIX0vZ^a|wAh_5#+uUt7;Mx5pY5vrUeZH8<+Hlo|7RH3Recg*3Cx?X(?Bx6SP9H!fb0-*r03xU)|ED(fj@b}rPj>{sM%+)43uX9bM+C<E)yjvHoq<j<g(C~5!3At*mCAM$*~6RZ<rE2I93B`|)2QenPo<(w(ycjU*sT0TzdvAr!n(|o@6fU0<Y@%0g3`#44V$Cx&7yZrmur!zdR%j^kKkNxX5@%6;@FdoyrNB`9Oce=U#&e~@-<GA<X_iT=Ke&~RHXtYOsy?hUh$J|)YIDI#w{DBaR$Ds*vU+y_ne4}U(=JSog=!YD)rg`++UmdZIUVBh{<6g*3DOYtN=I5DvrkVRetA2Bf^lPII)6D0qNBD_vi>(4bWeoB#Z5^yTzNWx&-#3@~t%1XE|4lM_s?^VQmop%VJcl|{R25%u6@c@q+D-D=nSSpS@q5me{<j7NOFkHj7s79}S@KFR{&Byw_i48&9_M>vj?80@DUHN8mLx}Bah`Op$&7l|4#a)=`B$uG>b8~jg^_9}#`VA-kw2pzP7=S1znqure(K17W|FzzoGaeRag9?uCYjq~OE-9<**8jAr5^kC@Dm>8ee#HJ{IwYU7BF3Wy-k43d-{&kSikvHLOuJYO8bqeJ*9tatMg7WUoYz?|Gj2kdsxz={q{XsCQ3c6I^cXaM$7!8`OFwE^<>yA{cmrYNyfF7IyL-{VOUo*%8LGRtQ{xqEcF%Zx(82iUY~n}oBP2YT3OzEI5XZD<B@N5I?K4Q9`PUJk#CMIQr^1i+(@Zs-WJSPy<#z5>g*O@@30^KtO^)+etsxF`w-gS>?7Nm5akD4Kwe$VhWlD4zY*qk8mUf7UO5`y94_rCR0iu|uHPI{J;m3Ly~g}7Jt@{rn->qmc_qMj)CS^tBygPgTFb1MAD$QW^sD`Zc_3wGu4Db+uS$t|;P1Z3+lx2t;yXD1r)q_9*J+5|qy29$?KAs&^SKx=8Ar-I@4VU6j_aNd^?X`@aW|qe{9@hEpFc$7dA$CYA?E9)56>z6<6LJ9_PAc0XPgBO43y)p>x}hAaGd0W^~|ci;$J$5=dw5*c{^rQnAE>|0-ob){49BBWXU7Go)PO7qxlZWe{Fw?Fpu&6F?PMwAM~b=)U!Db<7n()jMGYO#Mf)R#=JB>G5SBt>E2TQ?E%b(E81Z`EO01P&TDZruJ0CI?$^%fM?Iwc@c~j^+Yp94Pq|Bct;JA`ualE;+$Z^ZnA>Un&_Lz^=fES~#h<zm^T4N5SmzX3)J^<H(>;8BU`RJ}|2tAlz&Pq3-Pzp#M#~GBX9oA|B=x-VLEhdjjQlCpqpZ}^*n$4+eG>D)-(lA(sq(J(Z2vr8w*Nc69``BQT>jg8NU!qWo`1c|C;I2e_k68&4Xp2P$9ekEZSj0M@%|Bydd>!;oMn<{{jT?%-tGBnm+@(<eb}QOE%`{iZz<o|^SG|(&CI)Ic=Q9G@2s=7d6wt%p!VgAhp(TxF6&`io*>V5{`>^%<b(%@diY$gYOQq7@~-u5ie@83Gjy-(Z^|p%FC`4K|7|_<W(mfrQK7!Myfr*neEXB!4a5(dBJ+d&1>S!ei&i!CH|JHrGvvkLa!sXtL`#ed=TqF5Pk*sVKUT6}-W#+5^GW8g4)S~HaLi*1aXpRTIbEgxac8hzT~`A2oUPkkG-kZyr*-&7Jjb0|+C%&d5m>(!`Y7vR`=dc2^1DV8%qR8VBcF3N=_!79ACGmE%Qq^1@R)}kgF?i&=S_(6N6YYiMb=)T9UtR<k!hHRucdt(hw(TB^=z)y3*$Bl<-1yOe>pNkd_6@R`t3oglV;yuWChOm#R-ge>pC1a&ob2GTRGP3>$_rcUwf5O<|W6&e4+BY;VSW+eqYd@0Dtj~cM*85(a)fsEe@3bFdFluvlr&))Vtt^kH<Xu?|95(1GDxPe_JH{f@r7xVlnZJeXBiuNAX(X>#I(q{wXa{f3+F#+doA4r+qN*HNM{4oS*s=UFLIR(_7Tv<IPR;^)gbY?qkk#TU?7x9{$&VF%R>7h;8%lVdi{x6kIOzr1i-3F!OQkQMtr-6gW6c+EHr(u1nRkXn)+v5$5CS2YX}vS*YtsbN%-8`((U0N|qnxQGe~?Qr@~`KKzNZWZc<OFU9+TeOpJ126aN7oV+OGLVISw|C9#r87>t-KG$D4#-rcfrbj*gTk-sTZX)_2?FIC6R|CF*`@U|EJY@Fu%YATN5)Se#pA`2yJ=aWJ-`uZIp7&+j(p@r6t@Xda9}wYjTzj9%;b`vx8K?HXH8I|w?jI+=Bf~MSul<JaR?TwBbG%mVrqttXQW5vBv4zAp21nt3{kbEqOVZ2Y>sQVr->wb!@U=8gkUxu4VqBEEi}HLwX%r8{eJ1GTc=Ppj)VhVd3M)H7%75T`GXHR_2ewU`V7~6gf?uS(_U_IE{O&9L;|#fu{=D;IqWOAhbvGan-%XtCaUJuw-5^?Q@f7hN7e+gGrbGK%uZN$o5azMD1-UMb7T+Ff#d^}w3(tv}ZlZixIpoi;xv>5T{{p{IMm&$N?Su065mQBXB*Al;e?oj`nE1mqX;-yJn3u+6L_Lpur<wcB7&;5@#nbhjhW@#Nc{1_en1AvQo@VYh?c7ayPSNxc@c%xK^=FmR$n)~i;%n<;;O96B|6JH~kN!LxfOSgv3i#L8VBI^UEY`h;{b$JU(8;JL=V*M7i#j5{(Ki_DrPEl4Yb{=iuPw-ed4TWJ^wdG}z0O!s7w@Brp2GW<Je|e2XQ+yGb+b?zUye?L#Q*j_x$i)%dtW<dn)^-5mt3B&?Z%~<=JT@O%Y=Eu=P|w$u4;pIa>dkmACm3mOmlzg{Tj&gl--tKmejwuHpXurJeO&cQj70;9@M8y@$mKSWiftxuEzYiqow%v%8fBU@cGV}E)3-ltVMqop0N$>%QxHHep~-%GA<m&YKd>e#Uh`VSHXH<X(#dZs!K5sgrvdswHJ&q_uIGk+td1pZ~wD5+L?D0+IeXV{5?tWTzoz$?!P`W#MjTv#JW158Ln^W+X#=m9g_>s@A>n|cP%}59Qr3F67!f|aE`}yDUcH1@w=B1-^l1d`Sh5do%5>A@yPSI&Un9Mv&<Er>pe%Wy;zs_O#<KReWn)ryZHL#-dD~2V0SbYU(-6`Jy^~*v1Z?%EEIV-EeqQ7xjV{xy{9z-$H4b`uj@#?bFTS(jrZH7{d(SgsNcUe=7$dLF#oK-jdo@~CF4%}Esf-@ZBO@k;&a_%dzTRRwe!8<Z~PPU*uGb|zdsr<&wO2MWB1B@tN(a>p1D8maf!vZ8TR>7UMq?F+A+M}w)#vL-yS_4?Oag|-$VOunveG6!Z^xQ8rLQ25XyUfM{s7khVp;txPN7h!E<qo=kPy|#eE^dcL%QL->8T0|Lw`|;=J?%3q<+;(;484Jj~Z|fya0`wpZo>N2dYs`QFuecL%QHwTJ~Cc^g<7?=!7y;17R^{IB}}?a%gnfkz&$w&OkX<dh4|$JG}9j(K=zbMal@gIw>OZ1*~duiMjke6O)xd$!QydL2C}?@MiE5=TmXd~Pxl<GYwPI5T{&?`XPD#Yl5I9a%D=p7Wt7@AVzfwrF*v`MCP>q<Ajau`$x)ynbJU?=?Thp!}_mlAo^kWBT!r9>>*(G?4fI&bB!m;^)kU{QRdGo@@7&a+vG4A51IPOMhAgzV~<4@!jC}Zh>`O(~NkZzdlTSW8`VfheK9Kd+cAw<G3F;V_fI1k8z!Bvd3|4Q(kW~`$o_{%n#dMoG|<P?g-qc5^TWyX`PAkH})VuXC*^k6^KCnLG$o_;Lb7B6TAZLdGZ+bSH64D!_Tw|>m0ss*Pow2JuTPZyt*_%p8K4`aW|dAxbydudTh4GDF5jf^p9Rt@>%Qp4CN<p!1qMo)EGy@-+1(c5#AWzYaXSR_sZViyKQgNitm~~wR0u*Bd-I*w`W|0cGkFq`$b>~e6R26)(cZnPtoSMPpu0-X!h-&yW{)#g=`oXPiLb&-unl<{BPg=>HlZ{fS3QD^4|LgT)x--0o(hz@T0n8eu(7znDr+Xd5o76FR%{(snB96H#i*gPkQV(&~Mn_KOcnr47`Z>U+cWsT#ue<67sWf82s#qaUK2FWBpKXsQCK3yO>YrrNnyR$`X_x-XHnK_sq5&+i~10*N|^7$6#Cp9zi`n_r(1F_iD`l^Dn_amlO5(sEYFYoT#S}z6V+TZ{d02!hQHf{ovpEjPa8Co#%N4RFizuD<oJVe&h2V@6)v1xy9FqWW{^(odFmZ*9wYn-*N}<^OH75K40pAdVbxB?-7#^Vcb3M13%e*yeBd8;=DffLp=?4p?vWhIBxD^C_nrZ@^eo~9Jkyll;`u8GpQfyX>keuMC_w*?US*EUKiiB-^RJ>Df*{f_N8d=3FJA~=Z-xV*+-*yN{Mm(`Z?<<CcgcE1^r**B(7t^1>zg`5}^LKY2jB`i+Tzi!+n<TKdr;|VV_RQe~^bW7UQ^e-ol@C9_LkI9p;(KS+KvXY%Gp@_%_-z_Yd*)$uVgE@dN0GO%0agd`@9~&iyUU4kJ;1@CA&Q`NMJC+6Tlpwj4)2b&{a{$8W=rJ%;0Mh(Nv_*em-bUHhZ-CjPQN%6j>b_^$m_TH6D%UbNNsTZMLb?aLZhT72()TzX`yHB!!N-<RG02KH@npP25OM#?+q4_znaz4n#q&t|~)+J|Q3dH~;R-<tOEsl2E0-sk2FEGy5o-uvQ=^)tlx-bZKb-Hq~I`~AFq*FHU$@4es8+xIT-z2EO!d9VF`TAQSJj_1BaBRk%6I`1dL`v9+fjK;IN@UM97drZ?5zSllUYj`?5=Xvj|47m*7YagZ~8`in5eVba@&-kvlD2e#q`#kkqEwI19YhS3nR~z_V`$%nByP|%teW%t9)3<tDckWYlOh1G2-uqg=q{e*jy$?373%(zE?VB~CM#1;qXPdT$toyw8<=R%hhwrtI*M2MU4v+kC?FaVqzwIBU|DXNCF5heau(Ls4_+I;#jZZV-d+l?!S1!8K+;89ZOMCm=FRgX$vCHg#+jsp#x+stKbN{xt@7llZ^1b(md;9+>@3lYN+yAydyk^)QkM?jMyUX|9_x{Z{?|ZN3vHO3G#aO)Ym-rQZd?eG-Ywg>Zw*D(q{c-8{xBho3@&C2;zig2r|JSYmi{sl+QKcV4@fd0eveIDk81it2;%?Li<Zk4?R2#W3c`|h{c`|u9bv}7HIhwkU98G>reMx>z&SZgRvw&47E>EpSE>CVv4JEfG527w44<b*Yt|m_*kD@Ljk0N)c+R5F?wW*EBwaJC3g~^4;KT=bZe<WYhpl39&3dK99Ysovvv#DdqV|XnUpNp^ONqn4SD83gT$KvBge8eymJE`}`_gLP^Q2dPgH~AU)IrTmHIr%B|4f!egCiM~dCiyr+@%i|e6Cd+cUr^7J&yXKdACVuDUs2zXUy<KY-;>{wUsL}kza~GXJ|RCQpQWB7pC!*_D4xeqJcD|YJcB%yp*WU$j~q+BOT9t9OTI!qM!rHm8Xvu>eW}ODeaZc(G2~X%Bh(o35%MLflYEJMo%)P?oqU`6oP3*njrx>)jeL=MlYEhUn0lOinB0<~cmVZ0S?PT80P-UZq4+*^4q1g_XT09fptJc~`Lh{{Pf^d1Pm%9aACm8rUr=9>Uy$EY-;v*vUs7L_Uy>hCACn)DPgBp5Pm?34bIB3pn;Js#E$Te73dOfIgyK8Y8DtfT?@_0c?`qIt{H^?948<p?vE&ovJJh@6JLJpME9A@MXzEdNG`W+-o%fv>iXUhQ#Sb-v;>Xm!WEF~^Q2UWxV?(hD#ZNVa;^!JdaTAt3LT*AnNWDZpNdAj@o%|O$j(VFMN4`b9M!rS9O1((FO1?lnOuj%qL~ThvM2=s!XfHJAGipn+(g9?pYAh)(9v@-xQ8zx+`l&L<&<(PaT8-=^->25q++(mV$7o&F=^C?PJk~Sv3x?u>)Z*lU<dT~DPc=0yi&{TWe<dp|Otw;sQ45ock^3+dH)1GmO#PMInB0n?xCk{1xd=H2LvcE4O0rTvayqhFTGoh<0`XCu`U|-_xhmC<T!rdO^&|U|Q&CfrQ;`$LhlQGynv$H7eUy};IEASnQ!o@~jgO4f>{Kf`J2^MC7&$k&6txez6nT(_v8MDXwGX)uuZ?SLDt3)o#gD0tHTQT|{E*s;{D9h?+KSwsT$EabT$G%XnuDB^oSvchM`}89I$pCMsRhXCsRgM8$OXwYsWr$o$#)rw?=ckLp;p)2bGYK$)T(4x-niy}#p<4Lld4mzkacoisxLV&`3Gt$@(<)h)WqaOWKDDDpX-m}gz=G@>O-}VeaH!@Ny$o6kQ0!TQL~bhkuzxSe9b`piJXC)jrub=8#x!XBw1;3axQWqYF)C@YUD!X{M5?i{N#L8f3ng%<b32b)YRnE?3XkQ#Yw0M$O(A<Nf?TgQ!|h=@H~?<6lbR9BIn{cWTxgPXC|km<|F50o6=H~kdyEjY58~4^7kFy`_+0ujVU!Yic$+|?lGviJ+-Fh9<z!cQ15E)^?+ivMo>D;v}PE_HN`L<Gn#st92#GKT71l4DBeolLf%ULi+YOu7um-G{X|xw_!nw!3s{BXTGRk?EpiuXM{*bPaOw#1aPlPTH1Z_!VCqovU~(IV;<oY8fjW*llst|+lRAw&lRS|+f;^Gjnc9)unOub$K(0dmnVOsYGx-DiO!eIdhT@adQ{<E6jnpmVjpRwxY2-=dF4RzR7jj!_2Xb3-M`~AcNAf6!;<52Df!c%GmE42enc9KenLLCVN)BZ%4q+%>$WXkKx|O_>97p|&97j%LfvUVr!%&=``U^Qfxhl05xhgq`+JziM4x<hyhmi+TCy@t|L#TtvA>;<sHsl86QVhivsBOs=$Q4aFU6G-<a(w(j?L+NA?n9nM9Y>x;UP7HoUP4|#ok(6l?n&)T?n&0ERmeKoO8uE^C4bbQD(^os6rZM^B%da4pl&2@AdjX_B9A5qQM-_X$W5tj$xX@as2$1e$ad-|vYqT;C|*JxOI|`=Y8o?38H$(1#~SK%>ICw1@(5}V@(A)!YG?9LayWGec?ic+I74wHL-8)^PVz4DRcajhDmk46s>W41hT;O${Nw`U>eQ;_>f~T*5ILCKpBhH)PaZ-YNFGA&MGYbMA_r0%kORqOsHMnd$Qc=mGf*p#GmtY=E0QylvrsFOvyii!#$<MeV!!zKmD-H@2e}z}G_?<TG<hX;7I`Ik3v~&33wb?t0eL-n47DeD47ny%C)XtBpjyc}$VsVc+$QC3#TPi1Pm?c@*HJf+*OB{EN0a-L8&ZSF4av2rP06*$EvW6tEyz8oc5+YhT&jaSmwbq!_y~0g`3U(Kbt(B6IflB7978^88uLdPijT*~3F;>58uBLcOzL#<O!7$T2=YksFzQh9F!Fe6I9X{Vc|3VGL-7vkF3tVkUhyUBRn7gLU$OcQpj6EZuI~bh3sDPL+}{xt*QQptxW79n?oJK1xW7{<9!2eMaevoPJcT;M;{Fbzco4Oh#r@qxacgRz#r>T{ad~PPi~GBb;!M<x7Wa1?#jbBXivOl&AgfUPikg|MLh&1F7P1P(Z>ibIDipt?`jJ&Aey_Rb6vZkO{}ZoYHE0q3R(=tN;uh3q<QC+y)Y0Uz<W<y_<W=OY)Gg$#<c-wz<c;KT>KJl3`8R4!@^9pv)EwlT<Yd&O<YeTF8dS|Y7a5AzQ`eE#llxKollzhXq&6h~N&cN$i~KveIkg43IXQ&dlN>^xL!C>WLq147L_SFV$~eU9s`Lo?AM$(ZG0mM1$CxilV>EaE#4x{<9@X6Wc9i+3^tk5E&*RKr*PP|b=M&8L*VJh03C;bTRPl1^Ce8g_Rq<r%OwIirR&ihINX`A-R&h7#FwOm)SMhM_c(T&j<Uiu$xA>^XP~4i@gxs3ko7$b+n>>#iL7qoGOg%t8Oja*;l>SRrp|~iuxCN|2adWDT+?+g;I)OZryn?!xyn?)mx{bVvyn(uzyn#HPI+;A4T!Z>Mxd!<sYA*6m<mA*8<mBWl8uYRTR-t$^bv1c2c>uK+c>p<(`Um+BUdup+;uQ?VtEjEXtH|4^y~*3i`>FHD`^nd+hsoE-U#RN3e&KJ$S$VCClCzSFQJa&Ckt<P0k}HwxP*;%akn2-7k?WJ|Qa6z6lKrXU$^PVm)EeZ1<n+{^$mz)msmaL+$=5Zgx~|t5iessp$+6_^)B)t}<dxJwav-neN`~Uk)K%nFyndgl`^o!xojy~)kd><I@tInTT#Ws$xDxwXaUJ%r;`;1U#dX<_iv8JliVL#86sKn&DNe|K`po``CCBpoKl2<v^Y_&F*c%@c8H%H*77I9voX7$#NlrvAOKndsOYTOEBzGe(rEVuLCGVu}A@3v`)LmqQypOt=ypOzwT93Sj+>n}=+>o4)p*W=l_jjc^sd+8#^?>5vsP!!F^@HMY>SBv~y`gv`b(h7xK2f}ty2s*P&nR9+-EMKOe-w|UMq1qKCB-eM?Je&0mEt1Qk{0)ROtHGRm*ll{-Rl(}q^fK0S`R3mL!GL**AI%-`l30tC3PyfCAkiDBDoHE97FMLY7}`lISKPm<yjJj;&Rlo<Z|R5)NbS+<mJ?*<mKeu)Scwr<O5WLe1N>4x{th{ypFntypG(M+K}9s>`To@_9drfC{9I9NlryRueoznu~N0}JkL<Ph`OG<h}?$SkKBe_f%+%80=XRZcXBy$0JS-}Ij?sBLveX(9ddbcZR$93ZE`b);wjYK<SFDmRFwyN_*-#e=0-VkVsdF}4{~X8SL$+dSF(e;o9rO(pdKLaAn&E_C+{UkQP+{9$jhjW$;-%pQhmvPlJij0lJk&%U?@JPK~s@cC_YP7IdPV`v50(@ynxz<yntMvT7g`jT!vbXT!vhl8bA)<^)Ag&T$Wm!T$Wsk+KgO@+=-!h7Ig}F7TKWgAsgfb%ny|Z2^fk?P)n0bklRtalG~A|$49+dmIUb&{=fcL*X}=RU!&&nKfd<<o1WWb&42T2d|lr*&DN{sBj0)x#Q&on+8(Jh*Zv2`q6gI'

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
