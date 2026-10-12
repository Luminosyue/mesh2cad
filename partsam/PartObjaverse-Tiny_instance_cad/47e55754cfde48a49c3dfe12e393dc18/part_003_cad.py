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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/47e55754cfde48a49c3dfe12e393dc18/part_003.stl', 'relative_path': '47e55754cfde48a49c3dfe12e393dc18/part_003.stl', 'source_sha256': '763cad8004849082f940c8b2fbe56dc45bf968e2efaeddcd18c90f246fe10664', 'input_faces': 912, 'input_vertices': 619, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13244006037712097, 0.2869741916656494, -0.12180162966251373], [-0.038562286645174026, 0.4901725947856903, -0.07791472226381302]]}
GEOMETRY_BASE85 = 'c$}r33z&`N{`VJ(9YtHEgJQ*w!e&RCjMK_t90qeV2gA&ogBhog5n-ogFveLFMX~;lrKrfLnZb&k%#1@0A;*=9P?W=r5bwJ0-{+oro_W33^<MAmx_;O9<J;}`+|TbmJcoJaDlDYZJr6tN&(n@6i_hg|2RR%n?sq)w7(HO*s6i<MGMWw>F}8x^LG7zQM(6kL(<>~lf@8E}e8bcM87U(h200tHO?$Cn6KBJ;;Uh<lOd6Ird}QhX<p(DX%@`2yGX^G&7!dgTvn`)*-Nf1AxhBrno&S%2ss_5?E4t#_8c_fB_>&z1>h4r$(^l>Of!{~_&W>Ah#J{9{@1O5#-_fC>_Ps@C#lIe=eV;2$`|hG+w0}$dcI!8)zq^X|(LO|u+o4vD)py=JrhR{#rn<eeXt%U4-hM*&r%To*yT4QWzTorPcNA^czPosf_Pw1N;eRFPb>oN}w@uBBR^NH^H|b|k@#nf-;a2)TSI)QHNcyu`+TVKely2XqIeGG={jIjz_qUh&IEucceJg3-ZVT-<N&B0X#1Fdsxy`@j(!RqLoFo0&NZq>X{<zv7+9>`8^0$!o?Ivj7SGbluU9|6fX}XMK;cBVF&BvslLAUjBy@e~u(@guWwmmkAzm&Qi)W`J(o&MbJpO<+Ov`71%!uP4$OzCIa;Egu_R(HwYu~6no;X>+g$Ck%kIG^+FBJ-i$s*P6Pf3va9<7rbz=2hVg{D-yg4mzpxI18t8+z_cx`#l@&es8IN`y2REB+sp$QlE~MH`)Dg?Rz^k$`OAedAf<;Zkdd4;p?=IlK!~*$~YE`rOwaV>Ti5AUS=Hq1sV7;jANFJW5E#oP&sa=mb#zbf)tJ$C+GFj8d+Zj;rQ{?e~<LPAjEcF?#>B1kAG(y{Qi=s;~81+JO9aXgC$S!9y#vL=kO!tygE<NzGvq%<?`Il5x=(7q2xEcPCdO(f2qfJXARmXNF6#=)p=YytBHR#R=4+u4bBz+KHG7fU1rO8?Yvj^fm>Z=o&=wk{>(YNRr@7>=sb?liaL*b&VjAgJgzSDB+s0!Tdn8o4L&3L$(&8vcV0`B{U>~x&f}l`iR8c4QjXiT=@<In&t5L=Z~a5++$~M}?%DGt|BV9Ke|ntPzGL=y@h=x0*T;>lm#6d38bklD>EpUWYvx*gGk@H{M`avmWr+XhBw3F=dwgm0Z&sJ_>XxaG>zS2E|6h>v?OIRzIV)zX)PI1~En=J0e^#jYH|t6LyG85v&RHSke?and8?Al+%r>0wPT7Zh9FqJq>)QJ1=-E>D(>3!^sar{j?Ej%v^>Ljut4Tkv+|l)ML<Q;kIA&Io_E%q!_K}tIq<zU2spk&e-XArR_LsEpzkE#l&OQ@tzWc@w8JF(srT;T7Y>{yvB>5u>b$@&_ev~{{oZ|P%%oG2V<hhn1^ER@%_B}HWi2vtA8JCdiGXG~3N&d?p>i&58EXcF^<~rz!Y@mJDjBg~*?;Uk}ck~XM@4tLl>Jz=*?q8cL*T?V$xwbsT+r*C=oOd_h5fyCnO@AEJxio+Aw^E0w9{Ahkysp*}KYEMJcb8n3b=3Q^u7h*NR_Z+Bgth<1H~n$;nQrq-`@^_6XXMeJeKy}QV-tD4lH>MSBkODWC({0pCC9~IW%r9ua$ddhKeFX<MHkArPhV~8k2`!`uGM${>0!NJ{6hTYwBJjfJ$Y8&^xwmHmHDTneZ*1id#5jDz73agjJ}*_^_|5l<b1=1(SEVL4$<djeokM=e6DTF<C#96d38|g6MfR|7oV`z!99JBt)IT|Rk>E*S#m+zM@7qgm_EbSA4g2peDS9;E^i;V%^!Sc@fxX5Sl?W$Z|d(e*Nakr?_Kko{&*uU%KVxBhOPdlZjR~WZS&UAd&igJk0HNL#yzHi&hMX=!F+yM`dQ95b@NA8wzn@i&wAOGXZ77Bze@XX*@ykphTH1w44)wLWLmoP=l346??vCpv--~BwNn4E9x@-Mr7-S~(a(DMR=;#Uheg=hyGx3teN=+Xw`qyCI{0Hc>O7ul@%Vf0>YIJu>?fXSG0eApvX8}7%(wccKHlhJTYFO<PxvC4Z_^@e<LC<OE%RYosBIiQy;jL}XIcpPk4yfTmiboSoUbD~H_zT)`tOc7E%RquSLX9a(mpK6=9~JsV*BP>eKU^Uuw<EU(>gH!XUhFR^r1Yf@4PldjvE`DZ}m%`o5DKEJjrfFKhN3cXLbwD>l*vOnLMj+&dba<Uv@KFot@#CHs4#~kmm)iBfjj$%&S_`J~lYt>U)c~%K63)llhk25P$dGee!#_FY;#B=eo8^`XAa<_s5f6*S`OUwYT~1k~{4G>+-C=$zM7Tvuo3zW7IiW_s5<6sIAWa(3ZJY-_+9)Q(fjy_CvPuHS5UuWp!SMU&B@(M_i`Nlk94?adgD?u=(b^+|m2<tbXaZnEfrginPC&cTCrldFaTl#C2pa#~o+$%|7W58!huQ`_5*a|MzgY4~eNI<2&_=_<u~ZT`!F9F1gA+(=^}i-(f$zSgw5)xo&d*R^E3+b;Q54*;+SO+`N37PaWJ5CuJX-dSSE7pSNYch1RqArPq<r=H>j|w*1C7<LC`vLi@8Ex3bi~&$2wLUwU5V{&4D#o2~QBjJs#*DO(=1{}|uoG3&xL^{|}R<=t{W$$B@wv*Z`4f9znJ?=HD*zdlYqV5^%mV!zCvse5g8_QWmAxB2wb+|M|t7TNmgimWC3*wk-q^TEOX;LqA>tG`)a{;WKEJ(*W!el>Y-5H*hDZnB-1E9QxOyD$B5Mpn1AH+j5KY4{s#zMK2=|ILr;%Xxhw`OW*NxOMqf-?aDiS(0}*-xU?Xd3_|~_{R*}Ix6+A)MTF=Ox;%7>SONf%KWP0oBQ5UUyf_;Z+%(IWu9;!?g@P&*Xo=5e6z3mvX)Aoi`(^n;*Oi1Z}rXnbLss<)?((N*-u8=eA7>VAG!Z8^G!c{;4hT?zsIuw$oLxHT(8Y~^kmJq<u6@FS#xaT<&VqBxBJ`d*Ae5hUzv5`&YE%8dF9HQL_O1)53*j2Z_caqIV<Z8`}y|ClKGZ32LE2h_jWm7&dc04I<his^WPiOT;|D?;pNUZ*XBD*uCPC(;SXUPca>{z{G*)LnsWYGsZZQ&n_qsO`=+GW>TK>yjbHw}%KPRy!aF6A>&_gWi}&Eii+{P0{gC@x<Fj7ek#%G~Oo=HsPqy6E_e3Sj^Ujpea`QIluD-c1a!(17^S#=Z>q~=No6op7`fibVGNr3+zIh_f=URO;AH3Y>m-%MBue+=7j~b2N$-b{fHY(@Sf1ZoW`>sB-WgbpxLqEBn4BsO62~%3JP7~xgj{742<QAOoS3Jih<XV06p5NRLm-?Kqhv(BWU;6Kl48m_lp1ro`LF1d}h|=fl$&ID`l?T~ZW&Rt#Y+Sb4{gS_I>#NL{b?1+`P5y@L=kh%3XIzZ$y<DJuS4_=(tM4pcO#hSZd3b(wgpZT`b8`K1`-ANN-pO_C*Jak7XL4=n=e1F`{GQ2=lK*>IkKtK1-|P>i_rsGPDmN}i^X}%G>#2Kk4atACH{&bgZhSL;oDql0`G47-UtE)`N&c%rw*DKx^t#XeMrnKc<23Kh%K7H{?wVYMeh%P1XNlZDOs>Q{sm#2U>zeV)_Pyz}zaz?hyEi;X*2UzTvJbH@nfEQmcV2DG^^tiysYLwC@5wyjx?p@WZ(Xqw`BvYIW9j~kZ|dpfzP-$sy7?kolK%?*_uHORe3LH8zvKO<BYdRIcNcHAT`x-87Z=^tca~hH|Is$z+#mWPZpb{J^rN)D@~gZb2p?_p-B+Ju-e%f;&evQw%lzB6_fein$E2UXC-eS9){%SCVd}q9t|Q#<8Q;9OcQLPw@4niUeP(v9%{Ti-^l923pblrGKCu(>?LN=%Jii#<<T3Y?u1S0It@GB!JS_E#Putd)@lE~B`x)b#`kU*cYf_Qq;eDV#d`+&^H}lYE-k;#RueRd4AU`*8PWndt%b)V|4tc-roV1<%^8DiNGtcgueJO5%+*eQ9O8tE@F1&~FXKo_Te#yf=V0<$_J#nk@ZS9$#<$Y5hH}?-^zU+tQzSNhwf%EMy>w=$~_%c7Sjj!21%luz>4^~y?XXZz&uO}II-uGs%w$<6m^P2I^dj@meF}~@)ng5>5rM7wE<9&<q&3T#YzB_ZVt^WR4c|YLJTxjdRKeD~dlg#<z|1p4{N95T2(&rc6Yn8U=xx*h(oNM#Vx`=5nf6tsj9(liH)}!&w_&VaU?Clv}<2y1Zaom@=UdVmB@%_a|B)|E2+{8C%pT={mtd~-semc31`zMYUy|$1%PvlvB^Sp1~12{9s*y`+LKQHso^8RWK?KAB2ndd=A<`DXsPJgP~d{YN^Y=X@<?>9>K|B306|BrO8JJapHd5$pmU8Vkxa(;^Vyk9cw+W6*t&HD09Otg<9@4LJc<7t1CI>>#LcVdjKKjwbJ_@(PQrjg9^iIKMau9!Obp|(8ce!x93#O9m(&+@*xuQ0xOZZiFJPwdLN7%2M^*B$qSg`$^!J|_K<b?twBjEwW8Gsk58%6jp<o+$PErSDN)=l*N-{fFcAX5ybY^S#ygk3TE>;x8$>y(?jxv>(4ot|w<N>Gr;aqxc)-KION;`nX=^iErF$S(m>JJtpH4B>fzlA??o%CI1$k$2T@z^8Xra%i|c^L9PS8J}>8G=Iz)v^yj+nk2CSI+;6>BU;2OHDX9<d$6T+~ko(gM_i5kHzU_RiisU)>s_u`k|1vqR*Y13&^{1zFen;YIxnCT!UHhK16^@F3QSNs~kJrBQrv_4=#G3M6_0@Q3e=bwEclK*4bsp71``&X|Qiu3rnIEGb`cnFnEq-5~qcg6^_X1~YYTw&`k<R1F*el-!{LuG^o+pXLl7HlK`MLDj$8~#8zi4Scay<T1G9TjW$oY;OB0q0DTUYz;_}j9MUWu3dzc{6R-;>hMSGscCRDE2RyMes_9llk*%lKiq_C4;F+V>1wEZ;|*eDARK6K_b}h7HGGc3A3Gb&J(^oy^g`!(B`Jj$!HYUCGHp?K|Cd<h}XJDe_&ziMO@yO{^^MsbB6S`A_|-eYd;0v>)0~@|>8$ajVOC4Sh(ycRN+x-v6Q1$a7ZupOhv299kmZt(?fDpHE2sA!p?~uTv+q?@G>*{tPLS?{54}WxU)?weK3TUGn@eMUI<TQO<YBCi$-C*yGeq=DG2`Cp?F(^*6rf$G>zQXaAA3-yq)^o!qb6`;(9A_P)WZCC`sFWF7TusoQ%7FBIS3{)qLw9D~Q$&e!zcKWI4l3uIhU&P)D5L&Wz7OMg->;-|}b`9mdt@+ztSphU^<Z!7aEwdq#7-|dKuuhhpgC|>gXFjwlye&rezD)s*%T8^8PApIZISlXYMYMT$G{>iTnTl;BzkH44XVIOb|YAE@SKSTXx9{L8>mhacTd-*#(UJ>#fXMERp8QOP+)sp>aU=^v)5ARAH`VW)-4=mYeJ+8;>!vinKcYG&i+UoC1KPBJ6oy?PYm~z_YJ5Mi_diHB1`(*lI`5vv@zTr;azR_A|XTmBuZu%!1t?SFIJ8#-zX@BwynV-o!WL(nbi+{X1^=V}D&A2!c<vQX?o5OKC$oTf3F2_yFkp7?a+V%(kfFaWU;J<V|y}i=(zUdo~F6|FKqkU)Z1^6lA`=6IO^dBvC7?4Pw*1El~XLH%F2gJztgC{r1ag!Fw`W+A=^*?Z*Zto5~quaX%bd~QS{oy*lFJX_2<A6@&Su5kk`gIOyBlSGxWZcu_d<V1=|N9k(^g1>BQfhtj$oRUFlJV=>d|$$Tsb^|!@ellZQ0AMwpZBCbD*b1FGsktO){y!f_*u92@tp2Tt;RUIZ2Pb)wThfC`>;D9N6ss?67yl3ZJrq4d+IOgKl_q1^^X3|(dX}BtD7VBrhNZ+@|f&bT<?r;_H$4FO!8b1|G;V8e`gdwKT16-dG>#+eQ%ijoX(xHUA|Y{zZGA8F6>IllkZIZF8g{<S*?B7{!ev#cUT>{&q!V_?T@ZMB<Cypq$hcf^k@G{sb}a7xvnQqC4WoyF}Y5;lE+Iw_q{LU6}n%y_a~*}zbk(4MKYh066HHqe-o}FvX6O_Vrc)4oL8>|Ic`!{`m<R4o^@p2CUqds(~>7?n2c9aE2+<^`^8VWA^Txc3+k{;`V(^W3#;!uQdifZ^g5N)O!{-GmeezOo%GXPSH}H#U&eQVtVefk^5;lDyUX{1#&?|jNUrbPpSayMB+veR(!N_u-QMM{B6Z$3SnA(voSd(_lH}i)q<s(L=t(@bLHG09e$qZd-b=d@i?r`JktXw&>!UwmgZ6#<vShw>kC6MSgrys#4owfq_{x2bqkm(`b7+z5GiE>UcWJ#o&R+ik-JjlTq@VHMXy3o*sP<jq@?DCj?|f;0XpPR}PuL;-iLI}F=lA{Oxcz#_eRb@k+V>r(Df?vqakAcHD{0?zC{M0O33A`-i#hd~_ID4{$MtugAoY(qtbNz+<OA0E<Bs`8`|jNn#P2HK(>h{4(Y|wcyyWS<MecW_7i!<P`%O8oE)jB{7yX9z9S7^%`swM@N%HJ^PV#h<?@k?kT1op|Pio&8vQ54(?bBHM-d#bGKUjV*z!UYT_Wg%W$aSG#RjEVN%};fn-MuA$ryDs|-*cdvZtv(X_s`C#3)*)cY$WyX7a{XD@~rp=F3S9&{?5p6wC_LIP3{N!1<ANaZWVw3(Sugs6EQ>k?xO4absaj_ll#$#spN6Xc=fAE`!S!&{NF{M26EkrNdHvU(GuCOXzz?j6#u(HQs?-Ka-Sa_uYGUP{W6Xn7s!22cq{UMBlEmpb?JY23-Sz;`o!;$JYiLAzN;_q!@b3yNS>WiAM?Dkbcgocg`4#GIy$Y(vHJeKf0KQtFYocZTeR=|Zm9G>ZnQk#Ey<Gh`-`M~{88!8l40T(?$-Hzt_E@+_I@4uvtRndbCz@Qj&;^?arIp!&tHpjwC~;j^+DTtEnXt+_tuvB^p*Fh-bK;ccOCdc{5bi3#=R(5`<{YH(w`3J<$C{agLT&V=8Bb{UwGfGCC4q8BlYPZzwh9C=geAt{KEIdZ$DV>tKK=OeaC?#a$d3W9?ZXB$y%xN2hzTs{C<k@eY>a1{u3kbE1V0n)=ED|>GrPn@_PrKx2kL3UocDi?zUAW&%AXX>*E&mmwDSRTJA^Z&DOr>+s;ylSb5*&oi|$h{@si8aeXoJU734c+Q+hf+spcmmY-iZ-fXXZcfqSVzrW3S*~jN@`AGM7U!0t8w7frY%w4B_U%_nYXV7f99?b47?F-!6_p~`A*ST52+IQ@Z(8qN|%g;R>vl@IP>#;<)cSgy3SJ%uvYotG;#ShAo>(jKB+IQ|ABzgJ-^W9_9HP*U$S_e!2vn#K$t~-C^4ZfF{@S)CExLoS_VokZeW+i-Rt%I+1U-|u-tYGbXcYCCsk;VMHxU%-0yXs4SB6slfvK=2tf3l_jt(!~!$vN8h7JecAi^cl7<(ibGednHqI*&U-eoo<?*x&={=OX%9ORo2xI@<T_Y9sq|g#7%`Ibp(Tov(0>)ZxYI(*Fr*tEK*tG7ot^^8cr)_(jL)&t=^o?|+I{$+*Zq=?lFm?_d6NXqC19rf&Z6OIArg-xj}hgpB*xVDWd=lz#TklIz;omfH6eZkP4ax{=&xjIFau*4_K!2c=1#*G{gK^)f-`TO0X(CI6UpE2aH1=1Hc^lQFBb?=LK{_h-zKl`?PNV4h!;c`|zRN;$6`a=tz5$#cr+1lw`FZEMMW|LEQ;rOqoPPtbbl&!`3*_kj2z@}0SV)a@14ewyRDN1a?D_4mv9hUCcoRmKkOy9;xqeUJ4vzx2G?9F^l{Y>_;LOW1$p_xQXS>m*OnZ{qjhej_7G@)Rs&{~5Q@>YIJf)xEb|_cPK~Sl7F=!;Xzs-(UD&+i_hZ6IMvwGG)A6HRXAJWN*&*TWR0Dqr4Y;rTq%q_;#)-_c<dQh+mj1=i7d^?9Z>%S|Q{0xzwkt{C<#sM0NWAj`TB_--mjoGWD4&ey1FH|1#qCav8^UlBdIE>HjOm_+D8@FGb7yixG#G%ebtipS3nweQ#lr<moa@-hU0>qJ3YXPyCL{a<+!qev38g`mDXK#(_fx;y%a2j<h7pudpgp{V{s?Utt~e!vEE;u(p1_`Ty^)uohNuIKB+TH-zGygyLQ37w|6l0Qwz#06s}5J{5?|f%rWTCFrlP(sOVLd<FdlR(b|j`ZIh5zKZ?`EByiff#Y9Azk`*YfR$c@ufjLboA3>|LPgO^6@`^nft6N<E5Hu)Z?FTdNGQICP+S##5UvV8f<6I10@p$R0V{0)*MS?Njp66eCTL?==|5qm&%;gN7U&DG(pGQ_xHZ}qR@wn>4Yxr%!fjv|+8K7i!Gz*&Xm?m?Pq-T#g7$_(;7~$wB-#sB8U{zgeb5M4X&fAjCZKU}0-TJ-!^v<O+8<7X)6qm&=>Rw#9!w}6h$g{GQ{jQ|AT$LY1iR6Gu+kW~FB*-;z)GXwXt)O&4lC^n_kg>go!~C;ON8QfXnVLF{303zzX<;uZ3!#=7yNIy8QKVL2G>Jt!%825l|BvEgPR7TIr=R6H2e%&pHS>XpN5@qT|)6wgyP51hv3KIT7=@7gyI^6;s?-s;RoPqgyQ=H@nj$#3&efsqp;G4VWoeE|EeH*2mL#&v^rd!+=^8wzJ=ZkE4^JoSm~eeE%-Y68+;u;jeZL&-436I4+UaxAc_NVkWl<Rq4+qV_!xQ#J_a8q6z?Y#??Dg2d*B^};;#tB`RH~yAO4(B{4u%-{uo|OC|-uHf|V|Xm9B-AZiJV?tI^GtoSQAj+Du=RZnN}l8~s&UWa)nq=cja^<$U*9>adU6C_Q4S)e&l`^a8B(qNUCkslC$kma#Z*8Kd)zq0+OKF+IyTEB(nb?urkh{t9JtL-AhpD7+UgKzG9h@Ym>n;jdvIp*RoS3g^K&=mt0k{)|xk5&8-I5xjy>>_ykXN<W3Y@DlWY;3e>TgyO~Ma(FSk2>lRN`aZ1mU3d|^7@cRyGmqmaU1&M(Li(a=m20VCuBFboma$M=Oep??P`o7&YtRqST=)ZcJ?evfjK_L32VM`aL_dQ+V+>ZJE8vyzJE#}-a(?fi3*mR*S?D}i=?r)lJP~~ZRyqMz>VYT1Q_;!rRCp#j9i9oliOz=Kgy$2A-$LiWZ^3T|VgWiAodYYK1}n{mm1e<n;YsKeSZO9a34R^@53KZM_;q-EAiAT$=*w_0{36;Hei42aZ3RCIKS(IP>JYsbR-t%5deR}RLh&c)I`|WK9-(+-AT|f$zk&D+-3fmNe}x`|zk&<VU*KN@u_F-Y(L%V8Hs=Y&w+Y3U3B~8ogYY@nkM4y1@Nx9N@NxJ%Lh-lgX82opH<}CYh6@6*ArQL)u^uge3uv>RQ0yfXe~4~|H&e$C3B@bWuizE%r)VKuNF6^V6n{V{_MyMRKKN1~{!u~nG4xkhh2rYydH6izp;(3Dzg3V>T*809441%X(R1)Q#^x+~96ru?oJGHdzoqVH(E_-Dx}PN!??E@fd*D1m@%x10chU9mddBHpLh&p@@dETi_(R5K0ipP9^i%j##^Y^5@iNp0FN5>ZOK?7X(K2Qi`Mcsqf#?~Ce+8l&+6e9jw?+Q}w}qcaAA_HVpF*p{)fwZb2*nQ*ivMIDsPX=jaX$<H3Ev?USF9kRxKafP#f}ORif<5#uM>)|5Q={%6rUj!pCA+;A{6gK_rQCY6Z;6oTL{JfgT4>XMzhfO;VgI(`Y!w~^JWsE_&<c=Y;*y<fccS4D4vNfgJ;6;q51H8@E7Ps_zU<qRLz6m(0{={@ZT>Gif<8$AE2FT{{W%58KF1??Fom#iGdh|y3wAn8;(W0!Le`{+7=FjUqYXUUxFK>Pr*+yM;jB0|4k@<9947lar6$XLa`H7^VLZxej2R=KMg;DI^ZYZM^H7VAK~wc??bP{*O}jnRVc22{tl~9T#R=HE{1<XPryIHMd%^82>u$~2k&DId`&3cNGM)|{ts-{#u`HL!az(zUq@%dufwC!EO<0L0-Xd;V$F;o6b~a5k4LlNY}UzmLh%&zJ$N!Y7kv+&3oj-VuSUOsSHqtZinkMr_oBbSW{vG76#tA~fR)~Ym8v!NGk;fHk9F4!t_OEOL*Nc@G@1yTbr?-3P6@>5KnxDVNHhgbq0LA_@etGvyIHG42*v4W7@Q9GM_+>b!@bbPaAVeIFG6u2LU9}Parkl8WE(<pd-Q3zJ=_v~0&WR6K_7vez;)64;QLs6bqU2aP__1I@OQ<3u^xYd|AK!+i{KyOZRpqV*Q~c~gyJs=#jDUY@EX?GDnju)mUZ|Jq4-Tg@dQHgaP)O}I6M#?4G)Bq(Gl<n)?_lFIE_&JDmoq>&)QS`3OW{@0-LoumQXwnoePhH=c9|^#jMr&gyN6U&taw8;q9!?kI|pukKqG^;`>>jY8~EBD1Hv@06zzJMx)_q)>vmkaU?nzj)db0#UlbS1|3T%ehnQA4`yw@Mksz29SM(Q-M)&Z!>_`xp#9-j;8e61+>7;@N+=#kD2_qfz-?HQF@)mYXiK;^+!1X8cZ8dxb>X_Kz2=1CCsDQbp5*U}??HcrRVY4%w+-ILdOJlZK1L{Bi>`uKvBuUCidUj<!YkpWgyQMw1b8|;hESZ24u{j>M06mW2*;txa5C#qaReGeD2^r+_eay<{;-=+oI)rbg1!oy^*n@7JO~{ND;)>-MTer};GytDbUr*0UW9%Of6V$^L@3@$D87cOwR(-eEB-s{_c{3Qa09e6+?h4mfKc2TjfY#qT?5erO+e$}c-E@o2s8;D0VlzuENgxgp?DlR79PtwABVmQzskBDM<~ufQ{hzBY6hV=jZhqi#=tSG&p1MHINA{ohufje;pVKvc7)<*(0kx#;A*H^d)3fmunNTwRgh48l>fdKUdwtrN+>>pE`|R<PZNs2Arx;ym%^Li<%Ht5(CP47a3(qi&V)x1ic`^aI2BGn6X66n7L9|=dX6O&hoUjC(r8#|e>fEGhq_^<DX`KZ@DSE#KS$ZR?MEo?O(+f_6i1;$;VAfJbRzsRJQZC8E8Pl@MCYMf9cAw-6`OaMiua?}9A)o36<<ZwIydh~6+g(@ZvZ!7J)8Hdil0ThRw#Q1tJu7!RUB+t|K`1};_hey+#T*@*$X-midzJtX&~wc;sru+5ZVF`g1ev*a2GffO@c$=euUxy=qPvqJd990932M_hlipWa0YwFP(pDsp*RYSgX7pQq6oz<v>n`zeZfU2{wG=uuEt*QPeSpdgyO2G+6$_pM_?6-t5hi47Zj^dT)BdT;+g?%7>GKILw)$BL$o%mv=*#F@nN(kT$7xKIp%3t={N9UI0xMX=fF$Q<*?GX;3e=JLa_(UggtNuIttE!2cxO*V7L#O0QZ4=p|P;iP`DS|9qkAAWAErrDDH-az}?^;XcXK74o6>x!{H=!Ds1+VB>t^x_Xe5-C(-5&bRDepdsyj5u+m6aX<PUW_(ilitn^>7(tpEBJHkECZfHkK9XeWS)sea?ZD*--JH|w5SIZc6Wek<ZTgEirGVY2!=xdI$d7{|NCB<rf<)Aar*WelO077vX8V@TChQr{VgyJq}2UuwvSg8x{0(T}9cS3{UPVh@;YxpI&J=zLx54S{LfLp>X(0{^8o5C&N=LyBl(8h2xxC#0!+yrifJ`Fd5pF^L3pMx8s55o=Ne-Mi6p?`<#!A`U~?1by0HQ>5%ee@x?KHLDU1vh}7LLY#YJ_0|3)<GYE>%g_q2jSZAV`w$_QM4*r4OUtit_t6e-UC05K1nF9iQWU(gzrTw!b&T__rmv~72x~eDyRcifBpuCg;c2caHap#|3aqhk4Go4{tso!|4aL4yVifXBao}~Bi^u(dsPhrCs0v8oV}!;;vD}ADqw#q'

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
