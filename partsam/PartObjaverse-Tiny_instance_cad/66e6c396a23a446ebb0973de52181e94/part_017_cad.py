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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_017.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_017.stl', 'source_sha256': 'a3f3d95f79a9ee97052985f288d954d2fddd242341de142d673abefa88b281c6', 'input_faces': 803, 'input_vertices': 486, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09461160004138947, 0.1688888967037201, -0.027724750339984894], [-0.008277520537376404, 0.2702276408672333, 0.17980335652828217]]}
GEOMETRY_BASE85 = 'c$}r22UJv7^zQEnYE%?^Ni1V5Sg}XN!bB0pf?~x24hq;iVnwfA0TryMsAE9{D=LV6K<ov(*vH;tud)8Q`}@ocZ@stHTknx|*Z1SgW}kibIrrR|fuutlJNv>4zRD`~|LJrjzq6ufmxEGR2@V(;G@x(5DCeQW$LW;(;%i^ObfIULb{)Fwlwf6olYhXdz9XGn^iGWf8#q<dI|U9K88p&wXzyVo{R1@L-EZ)yfJ}c>f4|`Yncr8c+u*Ni`Z|@X=|lAYk6*bnOE8RSkbFqf-%qByW~%v1<Q`2883n{QhYW+CGFp7)V|MZNL3zbjKUd4*t3KPrx5RJXtEusiPrEf=nfwxY(l#cGKD{cwar%q1^79)eOS~oMqWG42-I2fTI`Iw5)5O;gI3n@pY#))Q`zG<ti7^tdteqylK6e!2moAfd!-CGp-`+!fL#_GZTV9@&c(t25>fDlwaXp6blYHiq;;YqsC0@Og4fR|pg#71<o|8Nd6(x^hcrN5={T%V$10|2){JkWJZ#-P`8z#(0{#RF$Z0j+!%p<-z`&seLn{HxWLx1j;e1Wmzo66eBxaLcPkbmqD#0MIYr+Bi|sk(c@KQLT;W5fZeQ;Do8zT#X9^=I=zKMU6o-{RN-{V_&keZ31KPv_HE-`@RXT(x%r@m0%Wi8sCNjd|U7gx{pJ<Tq@5fO-;MC(5`lbBnKZX^j5&u)xnb1pDDsF66g6C%(GS6Z3jk9sRF)P<->PDw0R_Y9ziAx?FtyYz5<bUBb9|mx*s!(ExqB-T?dD6bZkPH|n1oD!y8EF6x=f{xsVN|I$S9Exneao}2yAfA0y1_YFaxSMSDt2oFrO-6w{{FVTPJ?uaj&ANl*$M*WYPWr;Utn~!llOJKgs0x+)eEaG#e?-D<B5XL<eC-LTDC&X9R9mBlt2cVyMR={7iM11}EE9n2CTH+h>PDlU0&qv?NR7d_97vUGuV}Hh165sMM9Q(v;E$XcNai`>OyBl?W{fzuxJ9lEf+i+hzSdRW*PJr*Q3VD16VBBG`$djCb`p;Yz-@I;t_?EiYk*8=`<Z17T`0`(}oG0e4ZIJ&R;tg}l!4GJGc&{huL*1==Y<*L!?AYgpy1>7_eTR%|`ilH<B{1%rSn*AM$KkJ^g7^i?#W$QwJZrl@4Rz;=uk`+g_~<0~rN1XgpD!vne`-9yK6!s#d?h^{=ia#9xF6m3!jC?Q{Kd;)KXloJJfHHU+vZn?H%I*SVmN<39>e|KtGM{T&S8_GIqGlqV!PxCdxrivyutcDy90luQ@ZUwQR=0_H<mmhaXastWgPPX@h!*0#8(Qw5?}ciBfg<~nG@L0B~#?*Rz`_$TvY>oxEGE4XkR$|hs%)vOgV`+TSCM)g<eJeyazFE<UsL%J*O<yilhEmKa4xHro@|Fdr2PUpf~a)ZxY}5vA6gJkItCapXtZt=MTiAeqB?<uYQ7ha=*p6;SI%Ck{nQfsofYiy)?%C<AUT-_T5H&r&7rOq8ZkO&ndP0yKUmvpg-9c`(gMq@eTVwqW+0hQ2+VE;#(>`LY={d;6L7rJl!rxynd`v##IeV#aBO8ko@}8o5&wH8~*FNSeJ;G$Wy5i@}vgApYk4lm&)*WRm}Q2Vf^o?r^*A=S$+k^jVK_#a?TU`r+0RY``f*(k|*8={)s&3L-Uj38}fETpRboep46q{tGUaclzn@DC-%?zNcg|kLf;(2aQ=LpD!$RV7xH^<!1FYF$X47J&oHn07UaKD8F{Xjmi&gqv8m!eEQdM=+(O^FW+Y0!7kcqceUD;X-O(i6zoo>tENg)M*(?QhmUTd$6@4Y%*rSouqqr)VuYW(pzwpO?^Zc?!>YrZ^`6pJzzVd$~zG3Gz%<HF7##QIs6W=uJJl3VhTKG{n#aF%dA;0HrnU`|pB>V!8k!SCNU7}}>A-}x~@=U3Me!fi>U)dN5zvg4~p-e3D)E$L9VF$4voYx@FzA@<YoI~hy;}wWs9)dhkuTbZ#5b-VTS75#uM#A6MAAK0}2Jz7ccZz?qPnLMg!h?u^(iQnr^U69ZAI4$dzV3whoZjN=b$_D|Kii?sR;!TT`Kk0l^{yhmzGrK!*Stg6KV}8~KsU^H&}sB1{mW*_bL*@4rrKUR#J~MseC2g)mim=PZ^Sok^OJhacYk8PP2DNJrQZ(h|Cqp(EPln_IA_*+p&nDL_{Npf(B~n2kmt-|jO(wU4;zXdw)G8;Q&H!Sf6=$+bHq3ME=K;bOR%56OcP(t-yic$DU`)G=bVB54-CM%7axmwhomfhP}=rI{7QSg&QZ^77k^7*)M?il>t3QW`gzw0dHRio{~(9#H}!Q{#3!`GIyQC0Iu<R2c@0`3zB=p}`r!3-llZH*qW<8MsDIN{@zo`#Q0KR^sOQ8f@lD@0VqJ<%Kb*z)n2!B0<_y;HPAc*r8-zT=Phnl`cOn0*ym-C3BXq08w_k$zI&;ytW6gGF@kd-oojy6?4+-65d*7-0XXwvmBm7Zca9{Vb!+am~K%OtnvF@kVVBMd0Lp`QN$UoH|`!iQt@r}EWV87M=7kQivh<}4RO_!QtpR}!oaZ5bFeqI+L^HP@<5?^1V7+!Bj1#FUW-n@#J{N)!SenQPeTVEX<hd$`NFt49a#Wy?5!8+bq&h@<uKja4HHNfMrt^ezNoaN)<-L}47y@YW~cEP&Wy&P}5AM|bS$-1k1SEHVapRwN}`%C@mxh2RGx)Obh`v>d(aTdn)dV%LrQM)vWpV$$3(#v6=&up?$;=|e^e${c*<CTE@u+RhX-!7w`KRaWeAF7|FPV>%bxR1V;LHyxx^e0C-8CNM$SbWQ&ztNvv3$Tvue#S{2`@C8AbFY8JH`l=XGIg#C>WsPzpU*qhH#g41tr_sk9z&foexPqkGV+%>i*c`&JZ$T$FK(dz`r+6QjyuHHUnp}*`c~s8;)`xWo|(_l=dmlWKRYhPxMyqP{bNv(7*UHa;(6X0&J<3N_*dTWYhYacsYlqK<=o)M)RJ-4{u9u*zZ-~ear*=N*8dO5uZ}K<aTDGle{*l?k6QN5Mp?&PSMfT*dqtY9Z^+1j_kBGJZ4<x#74h}MnuxD=%(qs?b-gIQ@xn~x@h^@(_@{|)o`la&)Pxl5!$B$Ht7p0(-Z2O2*Uc2)lvqIKW%gNq*w)WHxMf^Z<vQqFeiiYP@IKo7xv12m77G#IGR%nnOlgYzvpOK&+a3Kkw^}6{<A!-PEdbx;4eGR1L;X#0&YKe>&^He|<f%46@*8HoME>A6u`+Hr-ghfAjFMknaZh~Zsvh+x)<WMNrNQsl4*T}EWl`dPI4J(F&mWYgX6$GCJ>vg&E+zCqAMzxLZ}cpSzEv-HMDo>)Mf|$c*w3*`(9f<>;v43#!E>j~WYm8-0Dh;A=-ak}*bmQpVP2){V?UhPjyiLBq0S#05bwJKd7N5^|KH~umNn=@r#hH#k7}sjWdZi*2q)xmE|1R>I(wr(vrD6%(Va1F`L7Ga&-ZkL<nMV_##I~!%X}5%arg@xp>IzME)-2!Bfi?P27HGfQonk9mH5g(T(2^(Q0KW7h;Kbi@*CgJLqD%Z!N1oN@qLemivJ;8e0^hlKBGLGj{5CqiEsRrAM4_h5B)I=L!E0L;oSS{1N`;_#5d*WhdhtZOcD+ALY~#Z@RN1Eq6<7xe}3GLiu(oBv#bsB#4bU97EQxCZfqgG;q@@Y-?I!CJ=7TUx@>n^>YV;3=KG*J=4EV-{)bjsE%BXos3*B0@_4jaCh<Lg#7Lg~W8kZ`4B`*`EWTk(b*y`_Kv@@c_CJU(=7M;?RhX~iZt=};xsFSg4Y&0Tqb9)5|Jy*Bf6-myD>=(a{Yuq4*bj9#BG0on827?>)Y*NR_?GRBk!SXUUgFQ4j{F-`_&*}YOWvKMv(C$?G?nj942GYrJI?=#6Vc~8ePe9<mbpP1i0{x5b$%KL-!RixzAxv2aqBt5Zyg;b@rEYio4z|?9bHFYUaee^CxP`hID~#qtbjbOX6)PXZxJ6>2Jx2ph#wt4UFu#?68+ifgLQX~M0{K!__<!;d|UD)&DK{ccp^{DH*WI%S$o8Lw1t1J^C0oRzFjZl^zH!vcugbv^;&%6n)dLI#z~*m0?))Z-|*u3{1WrpuvL7^0U!9T;WH#YZ7uS=L*LZBtyKB<r&q)O;fi@>{5)don_jF#p67YOaX&8+-!SV6?$Z}>N3q{#pnmtRlE+Zy1pLyIk-x=NoO{6r_-%$DPk2+*(=ISv{GH9kR|0}CZuH@~^8G$Tmim<+7e~s^r8YsGdDo!-G57d<&x1ak?uPu2-%EZq@Y_1cR~+}3vZ!cZ(V_o}Z#s4e@$M5MWj>=nif_yriuzyQM1K-)i~ry2lZY;DunrmGt2@R>AJm=sWWMT^bol)Yh*#P;%lEfVBmcET^fUY%;=h^^|EdM<Q&a0Bw!Z#tE8dUkJ<#`cs6QzJc`iIbJbit2^jS&!fOEjpgg&fohWX~}F-5f3a@3P23h{FmEReXUsfaHYjeRo22X&qvBEG?8KE`dD8~!st^yk;}Wo8QYtz#$DS?4bNd?|~>uig^zrKX&+?VIA(6!{I<pGwHVBeuTrb8pu9Ug}r+)JFc|Pf<^U9!G5b%r~Zz$8yT<n2a;IBK-1EIF~*I9kKN-&CnlZV`#8wjyG$ip3-jc-@4)c%KK7${Xc#<PtIpUA4)zE-}1nW__^lAGM>v#@s(%Z@Sn`|k~|()*4oyi&YO;U=$l{n;q$1`IPr%b6W?@{`|9S4!QzMS!?;~aBhTsc$g?mR@r~c3KW%5AKPwUupR*m$+ks6aK4CNBhmMzc%h(vqE8Qf%S~%x<i64Jtsnl&Bp0%E2Bc8u`<{*Dn&Uepl+}D*uFyFEPvM&1T4^gLU5c=#r4fU^_l*Ko@bVQ#1zYjQM<D2G;<oz|ex#Vp*0(nmR!!PfHbHk^<_{LQwQGf8)C6Xt$HT(zPG48`f=+AC9%r_(mecL%2{+ULYSI`Tdt7D>M+?(|<Zteqk-7;_->aSN2b#Cj5dOm+2EAdSn5r1GHpBHW&Ty1<cVj}zksd7K6opPXW?;>#Cs%x<>BfhM`JOUAa`dgr=`d)l<LT}9Ll@ID)^#t*$PUyqwk?6y&JBTmX5a+662jo9|4e_T&aGxv;kUE~8MEp5t$)hUWmy7>1MSOj|Pk1itmtx#HTM!?~{ak+8G|B4{4?j8{{oGdw^)!nW-x5;-`3oi^fBz`)4Q-piA6r>`b<%wC|9kz=$7PIszhgY|x9fy+?C?v}bEiN2lG(DnFHjx@Ab&_+oIiEmqYoc?qYvE%;r;cm*Masu#5Z=C#n&g^QxDnr%DAeib7dKsmr|=0{L;4&Uw2ECt#8=T66^Bj-(})=ZHRGw`1;DHV3_#6f5ErQz<SxuK|Mj$k;nNs-q+-P4*&Ugll)xFa_$q)Ir8&wzld+?-v;AWyC>tSUp|R%sFDZu$KOStogRsA4vNIMl^38tO>T*=j@W{6BhKTwymSxzj0G6?hAW=4tCCE%`%o?S4Cmyj^%(c!D&)Twi2ARuLjAsVaBd8W#Pj0w0>sxZi2H8o*)&_<w74PiTlz-Jc-1Ds|HlLV_j%}Z-3h3t)bCh#|F75&jmBcWeu>zhM~X&B+@j8?=XMhOT@UbFi}n)VSh_vlzwaA~JSSXHXV?Su;c^bF`{O#u^STiBVLN-w>s3wU8DAjl{%=@FeEq^s*oVcY;&pYayzpaA;@r;J3G3o(k9qBFCcgeq`6IUefA?2LPVCR?-&Ttsb`^CtAHPui<`>0R2Q)=|o;m1S$1~!a3ngRRi)S(4+ClIKe@A~7yh488KC3bB3R&)7<zY4Pjr{$WA-oLo*p<b&b?;zb9lnxg>zn^_L*H6mMEsoRt0X>G4DyWdMf}D);u~MI%<|k<QiqCfD5qv!uhCB8n<v~tp3t($Gj;z;**{f65Z^o${*5T{Efr7Ua|5?r$n$K0`1%i<5dYL2evUtpr)?;HFX<ACJjXA|J~gB`VL$&?md~Tn(b%WX5^o84htDgV-NiRw9E@>`Bq7fQd-&d7*e5Bk;lKX8LdNZ7htD(9__^ZGx8fT{`Qh{7re@^-T1k90p$I;Iu3Z)J5if8a4BLkIs$1ai4Hn<B>tFQkcTf1&28wTt+>hU5hR#O*iCBMA&*{kTegJ-4vE{b?H($m+S04V9eP`+U9C^O<MEsA+*pH6u#W$bW2j9a1e!n`%-}Nu#agUYz&+xG&@|-V&c>fjR>-$cTcvJjc_!T|jyXC{Y+H`?GxeD^^87Fy+)8689?D^#ppJ+t=RSRR>q*n5}N&mVg>g?DNdG7zU)V4q77x=tX*>zv;8{^eW^7_>norwI^c8PD!<$(P&dJN)I#)@yKumbby@B;BK19AU(<rd%6Wd{7NO~g0dc`CkPe=PF!9wO(ldC5K*S1I}&@zGrt+xE>;*B9}wg~c}o_d$GIYyST6ww#NWXHm%iBQN3yt`uL1T_N#?8buI4J5qd8qBH9EpA5fx2l&~7k;l#zc@Axp^T{$;kv#efFYtRncbr?6_;%>qhDpe?x~uqxo)<B0(kJ+vpUdkkOP~69pHO!T@?>0tZ>S>U>QAggd`Oh|<`ZU#H~&=-{;~1mo38Aa^Vc$T8}c-5gZEWNd(_|h3gX*X<auab_7dlHHYfP!<Ha}q{4BodTQKreoh80;!!+^rzkcr-JV1QqU0<ok<Q|4RXDsr(GWOboIxjbXU+i!M?hCxmGe2pAJe@X)Z)vgxzW<{vzA0BKo=?;MhTkVfd~<$ptoxUE_@4&AZ@38cTpxgOGxCdX(CabZo23vRojPCg7tW15&NUEUdzScy?+Z~+^L&VZ<SM>-&S>!saS8DMtb{yEU(2~^K90ZN_~lz3|ABQ+4MP0A(eot#!}jo7Wx&t<Q{JzrmFl7X77nQA`X;=O*%pZUQ*R*uR&Vhw$;aV4yhfgrZN)bqZ4Q6&O!#i4kZ1ct^z-j#@EdoM&s|JU({b)^IAgZ;4L=H^KgCxgzE?}}mF6w5-v%cjer=k(PBfi<hyIj5gZQo?;v4cfqMsxEc)yeu-)xW9RchD)t}kA1njR*>|MmALzO6zfPwN}-e;))txxDz6Q#Vk5l6w|k-?T9H^XNsWv&STP9ct-#5cO1ChWIK~#n(^tL;X!6;NQMKTgJUM8-06uA9+qshkx*xjBAM93BQkr_@>F55#OOP^6akwKYSxz55*OSKm7JA+x?^NUda8kRDAu6P1sk<R>L=h!Ebd-e9Q6~@RNHYk9!3AlfnMHZ7#m0+#vCd{Cf#yaAEk>>!J^R`yu}2xS5hCWGlv9|CsArTYR<FWaK&KfcW3m%jXm3imN2v)ZnPu*8jCn4Ar9G7j7uNDaaq=rWueY{=0k*YAWb}z8#7{{Lwe!>)YY;8pG>Wh_}BkzIog?8CPF%3gTzFif?e~gE}icf*&{q@BjK{M}L0C!7uJ2zW&W=%(u@I_?v%B%~F49o*OxCh;N8Xl6d2mlZf}-Exz&7eXOHnIi54C;dgJ0`z2yO;xlGV&9d&(=VkHr7w~zpq1Flb4@zR(A{prO>uvDQzEdT>PZ`X&?HjXehb(_he!R$2*YXuJ-vMV{xs<|6pr6g3l53{+^-KTve@Z@}?*G-Fk~gSX=l}Ol$pbQL=&Rip)B)t-<WbcA<Wb}i)IQ`9<RR2S<RRo>>PT`hc|3I-c|3VKbq0AlIgC1=97c|!E+a>g*HG7!*N`_+caS%clc;;iNn|rMm24&-r5-0AC8tv_k<-ansMpC?$QJ5tvW5JFdXM~s{FHi!{FMBH`iT63{D%69{D%C6`j-5K{EhmI{EhsT`jY&W{GIxV{GI%hnoS4(NzSQ*I*@aci&6g|7b91oI+H7q8)jausBTnevK!fh`WM-Q+>!b>xg)t7wF9{u*^k<b>_;9-9ZVid9zh*W9zpKUOXEQ55ON^dpW2t~Pwq+WO72PSL~T#*M0TgPCcBdxQJa$+k?T<FlIxHwQX7*ilB-c&$<@d;sP)J-$d##;$d$=|QcIKnBp0RTCKn~=p#D(6ImjOr=s)BS<cHJ;<cH)8>J4%R`6BfK`6Brw^#u7OIgNUloJQVH-9z3_-bLL>-bLO*O(1U}$5J<wW65i&8^~+P%c-l$%gIZrk>sW1Q0gjjC^>?<f*e7fM_oXkN1jQYMxIF?OC3rcOYTSQN$yAXrgk8ElRc@;$e!fCsZGg$lbcXo$W6!%d1+jiT8CVhT$5UhtZ6lJO>$LgWpY)r6ZKEBrp3vc{y}ykm!uXV>#0Slg~&z84%GZ)2XZcIK5{N{cB&&eJ2^+@Wk=0JbtLB@7o-*=7bKUUmL``Vm!ei6mm-&?RwQd$o?Mn(hL^@gsK1kokn>Utkn@u5slSo!$qH4cSif|fw;eeLH5)kxIXg9{P2X~|ubSqz>2q$IwaCr2(zGyH({eWJsIi_}g{&u6qB@f+k*iZ{ldF?!@Y1**^)Irf^~v?f4XBOC4akkDuH?pK1J#{uAbU`~$R6Y_)E?w6WM67;vM+fsHGn*rJcc@)Jcb-X9YqcytJD!>l{|$yggk{jl^RT*N}fd>Po71dOPx-hOI}P3BQGYKs8M7SIflB197Enl-9+9--c3y+?<OCjn#qUA$EZii$H?cY>E!d|tJEvxtK`R23;8km9rX$M9a+1HG<{0eE{%Vqz94It#(Ai3$l9fGKI#{;c4?fS`i-nz8W*B|C2N<)MX2A&+NJUD)SqPS(zqN|dp%l?m&P@z#mF_uO{f*fO~@^&4aqIZUOMY*Rxe%}d-KxRNOdD?>Ot1DBU#gKWKI3ZnhqsvI)bcef3lJ6O%1fEA&_-x>Tgr0Kj)!oPn&u5<h(WQWYdRE?31SMHhptvUo~xH)8|H92Tkkftm{&T>!xW%opl{6a-B7;rn9blHSP;dYv`=|MB{wa$~x=5(l`(GPn~riYWy3usLr}?HCCuObk=>Yv34J5`oZSD_`v%{(}y<q(L>&6nr7JCcNx4dHN9wapI+pBtm#Rc`}!pBdri}9&Ve+Z6PoU~IXCw6T+wuw%{ilS40VfQJ(n~#QDYVBIi~Sq>RQEm?rA)ix?HiIlN!&WE>*1Os>V~Pp^Eh!)_4jvLb0CP8mrWKiuIh=ID|S=u|5|x9zz|gSf3*r52p50tj`^deW~7x^*N<+7pkXXeXeQjLH%2?J_j{6P@5>$=cdMusSOqDb5`SD&ti@1QR^z!XSc>Rs5Qx&R#mL80W_{obyBRa6Ev<wElK|MT2tfOnfvx?=5>vi#uupP$QQ`RsmI92$*EK`IhDMZnoQnH-a*|?-a(G1ZXm~#*HBlH*N~S{my(x}7f>U}3&>&A+2k<tbgD|8P7a|?Acv60P=m;0$o;4T$^FRPslMdy<aRpkzh#3qrTUValH2goxDRz8xes|5HHbWn988@+4knMMs^szH$<*28$>bT-2=WZ_T<TKtT=F97D)J)o3hD;(3i3MYcJey%CTcQy6L~k)Ox{gCNIgbANKT`kBd3v1QLmCukuOnilP{5PWL|fv52?4w56KqlHL`_#nwQ2$s29jb$SKt0<P`EgYASgjc^7prc^7#Lbq9G1IhGnvjwPF@Yse;Y6m=OniX2H@K#nAbQp3oh<Z0CD<Z0xI)DZGS@<{3!@<?(3wI4Zv+=bem+=bkX+K$|eTwQ0q_p0;KxBxGW?Ws-4_T=KcG_FN$L#{=x&r9PL)IQ`E<j&M#<j!OtYB1S{Jcv4;JcvAsI+;9*JdQepJdQktI+r|!Jd3)BJc~S!x`I59yqLO<yqLU_x{17!yq>z7yq>&`dXT)0oJ36{Cz1D4Pm%YN4^uCZ50g(&Z;(%r&+DxB^LbtxU&*{Os5hy1$v4UOsSnBb$+xH$@-6a3>S^*t@=0DAAD|u~A0Q`EQ^<+r1nNF=0(moa7kM)|j=F^$M~<P!l4HoLsV4Gj@^Wevc{zC@HIlrL98L`-hm&Vgr;%rpCs8MoCy_@}N0LXAds73*y~&=`E@V%#3$+>9g<OSNom_=no?3uho?J5XDnYfQ79eYCPqriLcxmiNEl$?77TJ+pikHS!srAWK$z^$I>_lxrb|TlNb|%**H=z2E8;}juL1Y8DEp-&REx8AE9JvR10Cfs^0C_BR7I`drDs>)tDtQidF?kMoK6NE|K6wdsJ$VT^n!1e~O<qe)BCjQHr0yqgByXi2CT}J0q@Ez}B=4b~C+{I2qFx~%A|KUR&!D5cG(MAgrBkm{GsxG;_oz3?_s9>Z_sI{)cc{0>cgUBi7s;2&XQ?O2XUXZjPO>gd50KB0k5UtD=9S2KYnouwhXnRX)6F)0+swXd8fVkzIIe@HF*fTG!*$biwaq%N<~nP-+-BW1j;1cuS@(&?OQ_*G>%P)>K6R$fx(_v;L!G3v?puwgQb+5o`&{F()ZRMleWCFHs;AC+A8Fi!>Y}sWcN({)R?%7SQ;iMO@;d8%t#JctNuBi^(73kFddB@aH#FAHm9o^r)Dq;v<m^;CvZgxnxy<*RDVf(1UK%G-x04ge>!>Tq>&W5MIplEi1nOw=1hOC1hwMl0O6^GQN^X;RwWPMAb|kkWcju+Ck?KP>l7pzD$wB1V)H&qY<Y?+jax{4>bvt=0`5-lge2{#WdX9XSd^hv@mwKOij(nednR<kLnS70x#;2%><WuBi>N;{Vc_THPypg<!I)S{1Jelf8o=hG{?Mfa<?nZ4x?nZ8HvzD!SY21RB#%{bcZbfZJZbj})?N07Y?!`;vK&p`(NFGKFA`c@^q|PQ!Brl{!lNXZXs9VW#<bBkG<bCAR)U)K%<eSvH<eTKzigkay=B072%zL(s4qA|^`33pC#-AB`pZuBpoO+r3ocxh`jr@_ESBFdE_w-JY-;-}qlgYQpXQ&&=XUGSri^vDa@zlxWc=8hJK=KmuBx*PEB(guXHQArsiQ0nPiQGQ(YD;ZSZ9&%5johJ)E?Z%{|I`1j)cU1;UZZ6BpO^lxKbiGU(`<jzGc(tJf2h`>O?K_~pGvmOf3#nkZP9kQ@;?S93rY'

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
