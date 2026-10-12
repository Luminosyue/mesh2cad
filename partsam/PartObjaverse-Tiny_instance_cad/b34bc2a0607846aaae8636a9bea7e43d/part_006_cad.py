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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b34bc2a0607846aaae8636a9bea7e43d/part_006.stl', 'relative_path': 'b34bc2a0607846aaae8636a9bea7e43d/part_006.stl', 'source_sha256': '67ee932d4c709c68cd20ac2c0cf639abc6a8c01b3360e3eaed76b997ba346c6f', 'input_faces': 760, 'input_vertices': 471, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.013647042214870453, -0.22168731689453125, -0.09877744317054749], [0.11279917508363724, 0.2180384397506714, 0.13066618144512177]]}
GEOMETRY_BASE85 = 'c$}r22Xs``x5jUP&^rhS5(cFAUZf2uO&~;iXAC7n?*XKEDWQZOI)-EdA%vb@NPwYBlM+Dz<v*YzRVfw}#6NrQ?@s32<gNAAdvWdc{qp7H%(>_6z3-hcOTVr;bCuNOtD;tH?b+PXwKa{RpjJ`~964p$=;0%$)}1hEmX}tPeflzVoo}D+egnL;Ky7xl5hJG#pHl4uOSM*`npdlBsWxijlxb5woiJ?Tlo2Dz@A&DssUzR|Q|+Hl8u|A7>W!N<sBLLfqqb$P<^TAVpVsi|`SPQrPrf<UmNf5+MAm?H!R)^{#=dLOsRUBz6o2;hd3V`&?y8tfYB@P}G5Z&`%lPWa@jOqD!s3^`BlFK_oI>hYkhqZj@q^iSyvU!#^F*Fq!2ZGRGXMV8ydG!1DE76d!`Zj?y}{#Mv!2dpzxampq|Ux$l34@qf6o4j<~&|s9>nX{zdI@ZS94{ackjlr{^l=!hQExruIKA=9zH&g{e~IhH!7OS{@*VHd7TR@h=2b#zFz(N9_(w62gv&S*5K=P{(5&BkI$1s_93zyuiu*dU@H5I{&upzEncoS=Oy;Fo!&Bj??N80-zqX$&gEAbU%fAnx2?P~iT$B6-qq?ZkJnmHnjo*+SJpFY5MQsep4T`YpK^$OTdi=uE`7;6qj~&<A9#L8YC)b~UpU;({zFaX`LPb~kJfce0Q;rnb)7z2WFI101$dr|>;8b0quKa+@W>?AB1cEces+=d#{~1fY4rvV;_>fX=k@3-Z_7D8j~T$@Lte6P3m7KrnNX)X``?_E^#@m$eQ>VyVZV#`wxySN9!<}6^9V`m6B*xlvdq)Gd~NypBiZL2vn8KDx3^>sZY25B^?<C?_gNQS*W-FP-};hQ$F6_Ee%Kb-=UiX&K5NAf^kc1YM6RpP9bS*kcfbJle{qRl&tK}Rgns~kUnYrt>$k=ETr8za+Ijr?47skHjd{GIY?;yQTWuHkx<BiZdeqa${yS2KC1>YbJ{XqB=l1-`7=GQw*W`6uhx0x-KV348$G>=2uItho-UsV7ze()xjOFnbeJHQf`u=M1i=L7F-0+ak#nIJwD$id^#%sk7^LW=!liAnirHgM_Df!>be;Vtn1lgZmRiuvkAD+(R$`+A4{AC31zy9)3Ao~la$~qm<vj3xR&*Yz%KPA_-Nt1jSzh)NuZU2@1^ll>O+vp#i{id=Weg6g-KfmRCS?4|R{Udq*ZG8h4c<#S*{J?~xp1!Fr%)U_<&aN#N^1S{3kooVu;OlZ6f3{GrH;sMgCO_%h4~s71aRaZ&by*+FzP0oUVhuem^Ze~2{kGNpW&C~eedPHiK3~^W>nipO{w(uMxy#q<+O>3*=XF^Ijg>qx`Fi=@@rrNi&)WS9tEDcU$^6BO@p_!0L)Y;5Q9qpL>-;cY`bp2L?CTS*vTt2+FHZ90j*LHeU;L=~(jPhxUduYCiS(0<qCAgvYMl@sUpraGzk@p6+Kqkv&>i-jE!#-nJ6C<Z<Xc0j_gmAXPQ!e~Kd}D1<WWQ{@8`k^>y`Z(yCja!x58}k%UqKAmtT|lAJp6+=VF!l3;ZMb|El)}r5?M?;e0UrTJ%KDD@%Bo%+u8&`QL7+<jH`GGXC?Mvd+!1vJZ{(Y-Hbcg?(3rkJ-1BD=NPBy{xlNS-IXfN$l%?o{)LYJmLAZkkjJ(-w^-1Sv=n2%C(7q-fe=MW4X?}KU(4D?CU9U^1Az5NPa#%C;nvdErB~_{#tj$e<J&4jW{jm8~oR1{&_&C>|4S7>^tVw+`@ibn5=))OxcH*?ZuyQOnmEKlFtz#Ta^54oEj_j>R?}gr|NP3{VQp_e*J9jt*nDO@jRNn4*Slc4a8r%Po4+*-IaQ5&`SJ~t7RX;Y|^jtPu=R7C)S@rxn7+24$AoF!LmOE$MX7ZThEE_e^B-T_hl{mx%hAP%X*UKxyunb@(U$Tl2>q@>Pwr2vVVJ~%o8+E`eY72_Vw*wh(GLKdER@Re;bd_TUq>bz4&@<y{+O;x66J$>>%e@v8VXwPw>8JL3Me&tJY}too&${a=CV9>-WDOot^K{{yO04>&Ez=#geo0opUy%DDxD<`R;qVH#=Y7qs3<Hf4wM9ncwi=<W0!VcT``Qn5`f6?xE~_=jCl_yq~|%5I@Mm`(}B#Q|htr7V!hd$Uaw&m45ZZUgdf%=h__RbKiJS_Wy?^k`I1Yd7aka`^xLO+T1=Obx<qJ)7L`V%6<FSc=4axq^=+QBlUPCJ<Kz&Tniq@@O3OWA^wm+8UJRPyzYq`;@@e=*X1m6T=I6*m~bA~dx+$Dz9I5l(QPXGS~~KobRDVpJj=s9U)NFT9QRed+J2emJz1wU{FL;!TW7@Ioritf<77Tx>)_vHp7ZTwe;z!R=aVm6Iy~#q_Cq}PRXyF8ecd|!1dpqn8pG?_ds4=)Ntga`K>DY({wwiw|9+0go$Dd><th-tzHbFt=d&TQ510Bxc;>n7=Ag*zeEmVkcu(J*|0T{RWam3u_efIa!TDP2j@Xr*uP+$4CtLsewEfxo8`{KV=i81Rk5$%V<bOa$a(2FRZNJoP{j^(LFIuC|6kk8JAf5AN*b>>#yq9_Z^}*ZZeNcFWvJbYd)j7{?!7<_&|3%K_N&(r=$*D3=g=QyNXAF%|{9d^vKOaTOeXzh;Wj(IT7mxDKXFOG3cW<iG(|14Db@SnRan*e;e#sZS9=-8RUXN|TC)<@g9QG&Qk6eCz#s7G`jBgt&efZjn?Q&h?I6pP-za`(2j&1jRU9IRXxxeUlW&DU-r&yCMe7&~QgLd%vXr1TLozvufXbT(rddK1Nx}8tU{b;Jc_yaGVW$jW;>dX6>_(jLcJ_r6T`&{X`%wOjQzpizS7r(CK-xoVP^V|~i&Gzhk<9?CF$NeIUkG^gA?s`GrHv2~3&N3eN7qf5NU$Xe<^X~PS?mK4RxUZRg<9=k@Uy%EO{-ze^r*(6pobQnG(kIHl%lq$)Nsx1#Q!&yrKeg7U`2OPj%QsTFu8c{1zi__kE&kz{)10qfaxQw{9AzHI==UVg7cYqP%qwf-9S2yiFOu=y`h3YhKRAfzvF_L?{-DKYShrS?b-viGu2UN!?*nF}i+|lIc@?};?mP3pkMyhyM`-0(sqeeuueZwn4DKR*phOGK7wzUbo=59aO6s@%2jXw}lgB&j>yporopvg9+A0UvizWW3_`l?reNOP_@s>wLqomHxaX!1+4iG<YarU*J3rKw(DJSpK@AVOXN@=;SRV}4&TZhX$T1VM8ug;RUV^+xc$q{@m`oHbvzTbR9lxLo6i+e?6=NtDCvv2hOEaTC)-M;C*kj2M+A&ZauLKYwQFT;2DbKJkozH$FD`^J4F%Xs5H(lT0nJ&^OwI<d7pzn%J0ou_#|dF~qblk9W7+j5RMpUCq@uh;7M{~Y4`jw8OvE;-lUa$cz;<T)^`^e)f*)Gp`S&-rtw-Y(^ObByKtk;S{e_(Ab}zP2t$WS+oLyFBaE*}Jg3zn=}i!4j#Xy=&xs*3xmx>$+}y!uJ<T$VJt+*O2F>$xU~Ap1aX+&A!pE4By-j&A!nO-SZgF11VwQ+4)94&oUnU-0T~DGRr*ZlUaQ9fA=~~&+TU4=>N7Nla%YSHSW&++<IU)`|kcQeEi;{9=<yd19Ebn*m~bnd|QPy?zgtZFO_+mb>B$;d{JSK=Xh7o$<lB2UVA*xQGd55_dR|4*L#)yN4*%nu@BmajiK53t{~|fX5Wgwk;O;fF#AS-$l{|vWbx4-%)ZfovW!RHa9^*fZ<u|fKez^z-sibL+P>A?A6%!}>{IstO~!7ngS`FrdCp^*)?NBT&?05LHM&37wSIJqGQTw?pWII;+}P)NURuXl^8N_EF~9ZoDeeP~ThkAC)}2;y{g&)}9d%^(-Oo!V-~GH{^4-rH=J`=aS$yL;%J5C~Yxa%$HGFg3nSJ+jmw7z;jBUpe#kcLsz~7lKA5hLQq**lQwSTUI$~nH?AkSkfN*q+`sB8?^ucK!7gP!MT`J_MBuReH~GG6=1dXRtqFhrT(xw9;vqZYh8MmZPMo!NK4|1$Xw<NcS(cfZdv`^Ni0_*vc$ntb>BL1P|c|1T`xn4NF*2eWVV2ea>fpJ?*k&lOW*V?57Gs~Z+|)Wdf_2kt1%=W9E4Ng1zi$iIi@yZx;)-nQsA*R^Hmb7j1>&1$Yw*T=X&U>{r$qPVVIN%DThohRqVOMl*eGgjGW<g?i~>d5UI`!jRly6k+TuFbx2e>D3>U7LNQ?##YX?^(th?<34U>e}$lb!zsFI<>rc6|0=%F|VDx-qPN2N?n8vl0JO$oj7HDk&#@d&gJ!#@s2gs<@qhNNt{x5o4)5dwP^#D@%n<_<?jR2ai2HNW!iDBU#)Ge_-yOW<h$$6@QwAqKYLAfzPnybzHy&5`|dh2`R+P0`R+P0`$iuy`R>2Bn8zFa0lxXZ>GbXpuk7;>`wm`jT7PA{wN#k&jgy1oJ<rj(>?qf-Uive2o~O0AP94n`EAu$ZOqS=vMErY>@qAV8BR)rG!#j#^@hL6O+qY&XDCda!GW(hLP1Vo5Z>oOg{ZaKZ?~m|}^*eqF&d$%g|EhlG{ZaKZ?~kVO?)$IFci(@-&vHLqyE?&h|E({-is0+$v?IauysWv(a-BMC`;>WH#pK^9Y=sXi^JqQia-C}TzEj3qs-(%^@x~TPRL(0QL_R<8R6eia?$2k&%HJPmTu4;T1^MarjeL9g^`h*2qaMw^QIBTds7JGJ)MJ*{MLlNm(KpP#@!XrmNBw5;QNL#2eSh5YZKCJ?>&qKDcwaj`Nc22MZQeAlQ=7Mzq|{NNs&bC--RHjdJlCl!q*0P`j{9@U`#4L0>R-7l&sPmY72h?<$#rU}@_w?CZ#^1rW9?W^^^u3JN3D{Ta|vHMm*;=oK3S>X2&pf_H|MQZsEaa>(Fa@+e(L<_1J1a<if`O!wG)FC->6?#hQG2Nqkf(CG3q?V`_oyI6yN>tO3MNj-{>b!pLvS!e&1Sek@~u*cT41fWY7I~{yaqbLYW)Mp69N;YAT<D%9|raImh6_^7qNPwH4pC?PvM?QtfdmO1@41YYV?lhv|y%98;C^(A9lrigLXd?yuwPdl8hPoEPpRhVMR?&N0jR_cpIn{b%L*b62)Q;VDW!bR5s0`*950ull|LlQ~c3rz-OpeZyAuj5@wD?&F;^l<`L2us(4q<BjKbSI95wJor1CmhiXwx<=m^kT+HF(KlS5l}z=V$9Ue*EtM4C-8W9vQ|2-HhVAE;itoPfe>g;$M?1bj{@t+b+*Hpzah|kG-+30As^rO;mhwL9Y<jBaIcjIUxUTi?N0jldvxVjRhhHk=tw~8-@77mesq<8NwvqkVyUIGPvs`Of1O8C1ON$5(;_EA)|B&MEcs+%$BcuEw<$AR;efaxj4b<`IGtRah6yLayJ16&3<}vz-wfb0f9`qCI?RkoC^b_m)5XCq8iS^?s#dr4;?T|VT`iV2?qOu;NpE$?eQO3KUPr_cP^P`_whvZLFe9I+y&c9P2&9km8MZCGLwf8Efd7iJWc&Pk6HoA&3-slgOo6VH*dalv(IieTVG-dth56;cL>imDm=c!z&1C@2U`-47B_0b>nPOD7gr9apTM=P&u^asneV~Ve%Ke)cQrH)5`aNYYuncwISj{QZ`mDe@?o;Iy!x-yUPcleecDZcyPb8`$;e0P8Na)vU$@m%3py;k*&zo*^Yr~2p*me(oD{La5~%ehCKPFL#vyNmL?e&VY5#{RV1DDUs=E@iwcYG`s>Kjl--W!81pEtTI6eH;0-lG><GJwD=0CVd&2{YRWfH~wFJ#JO41`v2dLIM;c*hQ@EB60|b761W`n9dJ2tVQ4{cVQ>LxE^q;G9%v459<Vo51ABvWL%qPc!TF#$!TG?2p!vatz-6E%!DYY|q3?q$f@?z?fop@CKwE*EfSW<B;QG+kP%F4KxE-_$xE;6~v=_J=cnI`U@DT89=mhX=@Ji?k@Jetr)B%nLr$hIE)4}JU2f^pS7okq@Mer5qN$?f$ZRiQ`ZSZC2Ven<}1?Yb81@LL;F7RpaKIkg&K5+Qku)mF<w=o|Y4i3kd`4~ew2f7MOx(sZGj)5)%la2%1p`)PVz@+|QJ9H@2A51y`Y=;hl4giyO2iu|jpxwcwAA{}CKG2WBq@BQaXm4mIFlk4y9oiS#5lq?{Y=`!Tb_SDn1>2#6p<ThGJ-~M8FlY}j=|Hd@8UP&#CLIB`L&ri#fJw)L?a+D9@nF(mupPP(8Vn{~4YorULsx@IBfxg(QfLI2bSKyj4TA0j2Z6((2f*RrebBR7X8seOhF;P#>xK9N^sbg!U&NQ8KWmxwNPHXmla^V(#8;p$EwkQ<FG9c4GW!GZIp~*KW<McLhwjxf`www6beophuZUMd7ipROjd(V6xR%)uiHAV_w9NiV+zr}6%j~zr?VxS7%>GPF{o6;A{@xJU8r&LV8e$A-187??X&bN)v>vn#n6x?A2U;E498B62>;tU|Z3-r>1NMPhpmo5cmB2pG^3Y0P(sE!QXlZCUFlk}153~fdFqpIe*aun+S^!L%2kZka0?h*^^#=Pui$cA@q`AR9(BjbCVA6bGA809PJ}_w^un+V-Xdy6Z8L$tu0<;X6v?ACCS_N7WOj;Z41FZ(F4JK^@_JP)gHUX110~^mGbrJRPdu`r6JT-e8b)i+krJ(OXtAa~H>p-i5tK#?TAc$Kdh(AUU`yq%wfwlqngtmpY0k^?A+9HUnA&B4gST}JVXl`gJa4D=iH-gw3L7dCuI*D^aOF&D4OX509Ac(6Vh?_!NgInYJn<9w2Ac%(}h({oZhe7?oe%O~`2x1$8c%;WZ5|4uRg7yUW#6I>y5L*$%)uGkE)v%A%5yWK?#Q$iS`%e5=6a5`Z{_oJ-U<%^jGzsDtP;am|_MMo5__-!Q{7lO{C*nt%XbyZ&eh&P+1ULt{41%~av<kQi&Z#njxD|r92eb>g3(l_xg4iEHJPkoS9YGuj9RVJJa}7ig&p;5*gxbJ1oa;;k@hk-KXC8S#JP{fI9R(hRJP1G#_eK!6gId8><Uu<GaSa4<IcQmMS>#1Id{3O$OM>``mYFxi-$TEHJ_bKV-h783zJ(yZ3H=TH8}jBRg7^l4_!{&%_&M_D8iM#+1o1aoW}XpWhdzZq0zX0yKE?OMUI^mS&@$jM$g|Q2;@Sw}me5w<R>-rK2x4CZ@ldEg*dO^f6hS-{LA(?}ybM7c44n?1j=T&;5HCj%uYk?~&p=+TKoGA)5U+yH0?$HTu0jy6Mi8&@$YbKQ(7Diw;EBlNxd`Gh2;#ob-r(NI<Gu*u4-v%mp*6rYkjM2A#P1=9^Fi~1Nhy!>;d|mg5XArS$a~@=&=lzR;O~+5DG1_Z1aT7d7WfwOJ_$jbh#*dY-T>b~-X|c4;}OJZ&~L%tBJa}>#D@^XsUCGg90&axdL4Wnb@DZW_*Vom{gH>1>WA11b)q4NizA3@L2H9+qfTleh(ACOcZd3deNiXf5yV3f#8aSC!K6#UQ@~3Q#9;{Ha0Iafx(rMj40eDc5X9S|%fX~8z}vw)5X6ztm0;3U;7IUJ1aTB}HJEe_I10QAK^*OsS%<{Cp&`(<VA8qZ5b);+;&IS1VA8(eao_<6;ttRc!KC%U9l#9{#6HmXz@+)WKHvff;+LpZs?V3G)Bk{9g6|-Rk9yQCaTqiddIWp~bsLHx{sKX~6`BlAM%`{j5N|;cuY)Fn6H&M85X2z};<eCta6IaEErNJ6f_M}35cm-4b`yelBZ7E?N1YR|hsHwVz;USaSOjqfg7_iySMaas0T1y#@xPh`aWOB^;$YHR;9}tS5yUN^AAm`_gIj>RA&3V<hk!|^fCqyoBZz~bOTeUI;2`ie1aUlqH~~SN2n`35I>3qGBm{9XGy+Vz9h?kKK@g`xcYsMF!KvUw2;wy8PB3W{I1QYRAU+J;1tyIK9|j*m5Iemx`v~!I=pN{9Flh*Q4|pAdSciTNCLIUX!Q&Cc1EB-Jq#eKm!JQDqjiC*}q(0!rU<-n{5VQc8l=?^^d{6urg7`=19q=9WkslGn#}LHZJ^Bu@4*eV&1`b2t`5Zw!7eV|P^b7D8=sTYwh-V>)r$V=Yx1jG#MG#Lx5YL2$fJ4xCW+I4ZAczB@o57pWcLEW_(-Fjzp&P*)(RU^zh^HZlCwcTK;)&2T(DmT;=u>MD#4!lstI!N^2Kv-h1o1Bj;y2KL!KBou-r#%Uq6p%e(D%WlEx<Lw%@M?1q20iwgTY<FpCX7SK_`PrgTRx(ix9-2&~0GScra-km^2m~3jP8?ycHS)COrt=3f_Vs-UK}WCfy6(1m1ukUI5()CS3?#0G^E?wnOKDNk@b2;64cA_RxM{(vQIH!SxWt<)ID0q!qyB!TAxye`=xy!K8m{!W6_mAc&7c?}JItfRBSC5yT6iQDD*~;00hCg4h>25=`0?><j)7LEHk`9!%O2+yYz+L0lGE6Py?NF0>}N2J{1HO>j;8{s#!+j}XM4K-+`cV|||>h({xcmqSN_N8<XIBZzk+h|fc#z){%W^9bSx2;$e!`{4UHzt;%j!d?=@6`_;|6_FPez!kxb5X2p!4ZsbMe;pCT{Sm}tq5Z)9kl$kw#Pblui=lJCb5K8v5yYDj#QUKe!5dMZ`w_%P5yZ!!2fznV|Hlx-ClJJ^pfO<5Snw(EX$0{ZXdIX{9()G;C4%@YGyzPS2tErwhaf%=O#+i9gU^F6Ac!wQQ^2ID;EUj|5X6_Dhrpz1;7j1k2;wWybTH{*@D=b?1aSuR2$<9f&H#UnAin06`P@c)9eNUa989_gd=k75LA)Ni4os?p*MsLHh$leDgGmR1Cx8bbh&w|&fk_*KJA<1bh$}%YVA4Y1O5h?0;#Zm|J<k!7{s?{rzK0+_1w95P-3~ql-tjj4x_ad(ne%`8UnpjN(OziE|4`BVo9f4sJb&}v+qv8yQu6ES&7Zx=@%BG@fNDowQu{ANXc_b'

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
