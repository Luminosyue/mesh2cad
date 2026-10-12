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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/844fc9a82f46421c9f10804bd8055212/part_005.stl', 'relative_path': '844fc9a82f46421c9f10804bd8055212/part_005.stl', 'source_sha256': '95907eb303d2f3dd5188dca4b9801c63c2ae708beffbc1d7f9dacdce12e34e49', 'input_faces': 1200, 'input_vertices': 664, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.13768801093101501, -0.161630317568779, -0.39531829953193665], [0.16097897291183472, -0.016930758953094482, -0.044286057353019714]]}
GEOMETRY_BASE85 = 'c$}r32b5Gr*LLqTsDL0*l7vQ(Bq|_TghnKzBmpHhAW4D}Br8o60R=%ZYm0#>A}TmDghuiV2nI}uwpq-|3yQw#H>dBe?yfWSul29*!&PhVdTve4?R)B0hnZP+?^2*(8PES$&Fl5mnRjEYJWpCtuZ%Zk_{7PhhYg=}<@h_MXLuzNx%@L+d1LPzy5ExFP4Q;dx^?)ZVH0b$2-a#jqFJqa!CE73pE!Bqknw|WpLpwV$=eSZJ85`cK55jDJBH`=Yd2}qs9x~uI`x8g1^<`-ipZ(F@$~N2axTBlU%M+0kwXt2-<6)fduJjKWj|!+Lzh1%eXrngE04UhD3Qm`__^0(jdT8FuI5kXYJQXJ`6KOjC-U$OoA)Nhb$TWzJ&%2LOCk@?*?riVmzZ-fJ@>W_-Xs0sM;qTv&*QK8x%c`*`>lCeeY87qKD8?xOV1<Zkx+?!>3Qhz$z9TqhE`eQW4Yud%I>ws_kS`w(Vx8A9^cQ;L+f_!vBrNlV4HLPQ+^)P^B-CCiuB{^{9}jxJf_Y+^2uGB6W2{$pAdOaU!T8Ay_h&3b^SvoSJyu_D04&NahW=nJmIb{dA|DU+{{m&ufF8@>TBlF^(D_&U-EqQHS_5Dn(?~6X1uPi8L#VW#_Rf;@w&cdysoc#T)Mty9$jBEkFKv7uj^~ZtNMC(E`GyRUz6+l=F6Gi<hs5l*Y!=#qv~sNU0;*y`X=X5^-Ydf^-Ydf^-Ydf^-Ydf^-Ydf^-Ydf^-Vr5Ro~=1s=mp2RDF}<Reh7=_5Hiy8E1V>p6~wExmiEt!Ds5b=XtfFGY@TyC$4Ykt;Y_#@>r2|*8E<P!-+gxW~DVgUf9p0cfDkf*ZYYXulE!3$l^cVNX%1gs5L%J9-JSy#z*&mlgPuhdt2ip<gw8|TI2KWS7yB4ugv$IxGa%-HFJ+z*M~elW~w#byKinH50=lg#>bYD&$!nbpKm`j<Mn=M9`Bgti9G)7E!OxTd9d>`YkX+oyhI-B+0CARfuDzec-9`T_gj^RpPJ*$gKMYQ^K<{k+w|V+%EP@|JM-jzZm$2{%x$jokMHqweg5938@IWxPvjFn59#ZppD)b$=;sTQ*KhV}VjflBkjYhjW5cT?@}OQnCLe3BpM1|pW*+@~Wa_?S+{=mcSL;8%-OuA{{Rf}v<mc-CibwrCr0%bL&v)iL_4A#{uW$EK;(XNp5Nqq_akW3hvVPl?=<EH5+`G`;e`1dmN#uI}^uF2hqASn${A=dd&%b88+Mh$GcKh=;3RwH6$;0ow>hFhrmmGHGp%&W?T6v9k{C(+<_HU-=A@a}{|J`qmA2`|HXLdb*)EZA7di#le>3O8+<ivd)+1B=$b^hd`aohJ=^Kk#hM&4$PH}_-Yjd9laV5>vhT=Pe-^>aOceA!Kjb?(LN^AD3p)cHp<9!{)7@0@*o!sHQkeY_59{Pm`;f26&iN7VI??44k(A8$bAJ&Aer`!AF0_g^O0@4v|P`>)XE;NHafe=#kVxL?frA&;LO>dd44`zG?(!O6Mld4xPt`sktbJd}BzKmNjTxvo62@VGTT*6v6Dd7*#9!>&Biq=Yrz+nMXHpDCAF<KsL0Ja$QC`+Oq1b|&U&b;ueYB#-r)e$X2K+VlSS`r8h>^4O3i*7#t@sXJZQ%{$f4nFs6jO61|0C39VQq-+Cwo+C~Cd7dnm>&oN*X=II$c|Yt(oacb4*7zuSsBx}!eS$gfCh}nPc6)x4w|v(cAD!DNk;flDXs-wI;MwVRz4~46=fBrEVx8wLejb0UymdXj!YvYc)Z1arA1g$DVxhf$CO7rxx#?nS{s?*a+AHk(-W1uMxXum!YhQnphuhoNr@)j%9?$s6zCPsM@|*1O>|^n}yBu-l;T4Uo+%x-L>x&LM^L_v1y7J)RwufAK^ohn+9yj~vzeNwaa<BC72dwk#a3IU|culS!uXlEPmg{;Zb9Fsq$Ir`h){9)%E8M0)mTNsEbG05qzx<KuT5le?UT>kRf6a8QXOrvo9E^<0bloq>T-`5`PCYVR_oK=6{pg)4km<bN$@Tpntn%IKiR-NQ6Y{9qPeMaJPvjxJUj_C%^QiZbKabiE!{l+jALiWUk5~I`{E(l=)qWdXI>CSatoC!0$JKrwDcIf5)$>J|JgS~ALTz8$ni#L2kI19?`RJb|{&@9#XY#0ez6&0lyw!ExBJ;XfdF+GBoX-o%T<!BZH+46;-nWzE)xMp~)xK(Sy{{(cSNmRa9<}c!bG2XT-0WA$`PDw7b3MP_2lD0m{MCJ$FW1*c-FG_I*I(a9-kDB*US!OU^!l1Svb?`DkG<0?k$X+Qb>^Y|{jA(PpGH@I<<5T|V1M76OZ)R|sh#V}y?6y{d~nkF{yg_q&voX7s@mW8ij9f&5dFJft}72e_{|~f`rPqcA`cz!o$JcI3x2Z3d%0Km^DLN^>&l}=_gmv5t7|86^Lo|fVe-hKBli5}c{8{u*Ohy>Mx1$Q+8*~j+1XYeTT>?6bv`E7=M$V=JlpknO|BoW_t7I+uIp)XeLdrg?$2`7%jCLV!S|bFIoE^9)q05jS|`i3-b}97TfG0-OxJo&=6XF(IhE<UUres=muTi^nXdaT-ui7T4^{5wufuqw9j@GK74+|y8F6PG8am9%qqD#9*X>W`a$R}+*}C@l=J)yIOSa2(<?+bhhpg|r;}U;8XARAD<*{m?+2hUUX}ibdI`d=iS>uEERm*nGZ*o0<q{QYd*ZG@VpMNB$cb4n=m|S0<VA0B1uIq1def{I33uUF(G4@wa=l*PRy$|c$tSgi2eO2dXots?mlR7u|T{2hup3coakj&LSmM>>tGP&Mobgt*u`-aZ-`Rjc^=lc5S`&#Gv`s@2Q)^(s?->v^_cjb}S{M-xQzRnuI_6L9br1x{2dDSsi9$w?;@e4Yxcjdv?SFKIYV=rX;_v6mOxvo4?xrH^qXYwW`H@NcPmbcef=h=R|e?H^u=eqJ>^-}ivxAXJJ?;AEa^MeiT`P&xt*W1q>b6t68^|?dVb-vEe<9`<0=*naJj=f+#F0($*_Q-YR;m3cm<`40{HCnczHGj~&&t13Cnm>MigKXFNn_Qp2M;_PbS@39<>pGiUU*})}KiAhY{Op`8*LpCyUJsGgbGVP}x<`xMnB`ix$y}}5cu_z13fb#6Mjle@)_bs(y?>hPzmlB$C^Bn|f1af>t^3a8(UO_geP?pB@5QSf$#LbuJMOgdP(447?5VQeng4g!TI+nio$Ig9N@sFhxfi?9%46U7dGN)Z>s@)|n#=6@Gurv<xp<jeS00*sr9Hpr=ibZ~8(ev?-E(WKyyzK!9geJ(>&m^lmss=1FZA=+iF-D<^3a!ktohCT6|Zqst}73ZD{WtY^Lf$H7p(cseHZ+-sWpFST|4Lbn_QoNWNka=`G?8%`A0kck>$GnCfC<L-oelFU4Qa?*MCS>mTUc(T(2L`j92R?9`^I7T0g<c4`jL4zsdFb4_ET@s9OKYT&@3T)A`o@n>?Q;^X>b0-el+NB9rUaMLIXn%O=;ai*#<D_f4)}7wO!*u1L<q{hRMRxlcX)xE`M7-;cxh<+yTh>fQGFuk!Qov47XO@_6|#*QV#u;(h(`H-DMq%A?H(+2?tYpNF2Bx!#pWE*)mguU`l1+`LXRd3<_xf1c|9<hb(K`0MTKZ^j?`e7!S2`_~#PU-^}Pzw<eX&dui}CJ(Og^T_7l23H;`vD2Pky^hs+@_tu&@_yIz@VYlyce9U~eZZWL*~iR2V8(Cj>wLT>*N-={wXgH>hRO3i-j?OEUG*}#u2<+9#;bY-O|I&tU+3#wub*g(ud|%%nOv{ucym9`x1P!MdX8_|o8`J6O|I|9AbCXHk0$pj*!QE^pY{G=_Gi8C>Gw4{*ZYrtU!!xqzv=fiI@kMWzV|gp?)1-Je{O7Y{kgHqlb>6X=lk5)jMtwVn_PcxOrGy^V>7@0+}O;cKQ}hH{@hsQ$<K|={Q7famFxNQeQvCCeg67$W1Z{kqdzxRxxW7Se*SWHhO@pVj}*Akndketu*#D^CnAr{tmpsyy3mEWt~_{eQ)_&_p9`D$_0NUL<I{2ydGhlmGr!5r=Syau`7?I79+!R{lDrN#4D(-C<bLPOy#syi$E#kq=-k|Q$@9@acQ)ho&z;Tqt_}V9KiHP*%0mU0+T;10F!IqAxvo6Ct&IJ+)axjnn|&sE-R|CMe;%mw_dm7IN4@USx!L!U>p}k<+>F;h2RGMk{3L(=55LWI=7Ik9_|pyj*G1ROw;wNgwA)Vm{MG9sotx*iWUhanuJYiM=bU-u<T7V&UZ3R4dA*_Y@T*(g=hLdQGf)0}-&}w7Jg#&7c%yxaWV^1X$@TS&oH&%_s#h{s^~(2q0xH+*K|jyxT(39p@WL$DdQRqQJ?rOXo$LF>d~U4oN0aOOG4xN7EZ6;Ra(%z&`@IF7tNld3PSCmDuOg$~_jA1;lI#62-_JWt-XP}8LvKw?<a$3(=4wCB_j?gKSI-yWH%s`x7onbyOs=1g^8H?f%JV(nwg1`qJe%+NH#Ey1-{f-ZeWl4ga`V2@<iU$-`uk7gZ8@$yI$(*Fhl=^RSL(nzS033^&dOtBO8WVIIXSL8TyUCwp5&p4W!Ag$*bO;r)APu*-~9cg$B7(Q9$!4l%A-^LJT|BAdRHDFvDBJBe)S=Le%?pu+`NxSUN>^{J|cPk<mP=uGB-b;HTR3kllP0c&gS#sa!aiF&HKLS+FsWD!MPKh=WlX-{^2<joaY}R*XJL5tF!a^n_ORi&*bX*$B%V(UjOhXmuI`ykID7=iJtUxy?#ut*N=IBs@K2C^R0j0p9b~%Cy%Q2Z=Tom{TRO6&&~blRgL)9t=o^*c$0hNdVHwXxBmHGxhcn$$6tKN$|E)XJa%UFI#=$U4q18dy_5dqn*Dl?GcUE+{=UckJl5jyI#=#3EM?DsFxQ`F;qDw~-g~Z<hY$F9q|YzwTzP24>9y&3{IYF+{?h&&SMGf=)Be6DKUZ+QD~}%d(3(H_`l{`r99JHDWQKixxKCr9im!L&-qY_|^M`9Jbe_M-_4!AuFLa*2$z$sLlly?a{wCMg-|PeW`kQ@2UH{<Z!S3~Aa<zWKlLkB2kID7=iQeDSx&BSA*MI!Jp3e1ea=re;e|B@;kI{48tot$a%3S+(uesmnJ>ci+_uiAa`n~sL9@xDi@wiTR`OwO{_IV)jxWd~%NIZ@aEB##mJvF)h{rTkhs>c%Z2fyl?m_KsnG3PwVT%CV1SLbi?e1A7>#;eDb%x@c>cwE8Tvp=x%^vB!X`s?>MTShv>n&o|qyjIvN<Bb@S{-^KF{9%UfKYbtF=>O|a-y1ZnU;qF1x9>%k2Rv_SUVDfp{xG}`7p}t3&pYSy^4co+5WXbfb1{4fe<0xVekl3<^u-^fi5G<D;RSK?Pdo#jk7wX{(|HBp1@L_Q0{mgP3ODEdFn#f5dF?^C5-!14;w#`{+&oV4d3mjWUb_bl#_z%B!vXkwJOXdVBls+M6Fv){2D{_J$!Xq|zVMDT??_)bHqEc6KNcSaL-;8CR@f334oUOo^o7IH{2Kbh@R6`JJ`x`T+v398)4T(H;iNS0LVprI6?VggGt;~m{h9b|*cb0hEsgh2tL?!IzlOrYxHRzr@DMJ%Igs*w^rea41b5-W?tzqN(-(FPq<kxVY2qE>%ee6RK+0dFFHJlI*WkjIfs{W>Uz&Jx7{#TDUjtX;!q$P5zd&D_cw4v;7j_7wd^3G%;$7ftxHR!@FbkI^-V5%;rHS{2dvRg^K*|qhq-wj8x(Xl0595d6gZP8g)cA7x`|w?GDZUHOhKuk;)YSNV`tzx&@d*70H8nnq{)_k;I1OKeKMN=0lc}lk3G^pWQ{$89uf|`1Q}Gw@jc_Ku5#J1F<Fl!$@p<&;QB&jh(7%V88ec+xC%zXh!}sC`;mV9uZO2eU;qCat_=9jP{vf^_j>ebcOW_E7DZU5}!x!Q6;b43|9)bPw2tEt;#b@EuU@v?cJ{fkyyHP*mUFlE2C&3%>N%&OQ6Q7FDgnjUt_-xn@pN-FhgYZGr&-hUKL#dzf;q;f_%it({8NL#ZNvmyRYA9@qH>G~Yo6sMNkA{u#(fA115FddLgZ1%Y_+WS?J{a#0>*4+JzOXLd7w-jY<Gt{1uqNIO?+R<+HK?EQ%jn;T_k^|Zo_HTv2k(RTgO}s|@Imkjd=NeqUWE_Ehr<T=aC{WJ8o!!a8gHCd+bYyhcq!f#Zvw00P4GtW61)-K5SGKsQ9t9Q>6fN{#!JvILH&#uqhAlN3k&0Q@!Ie_yf$7FX5cmP8t`w=cj09jDfg(SG>;kz3*xo#I<OF42frK^#fwru<HhM;fnNnn;aA}eU|GB@^)p_Peno0&ybApw^{awcr++D46;{KmQ9t9A=~t$H#w*Y-hnI#I<E8Nuuq0jrF9t8fi{XXg1$bfnJXiof56^)AdcF()PV@iL{~MPY3je`{1v63}pq>HhXZ(Enh47-V2woH~4llxs<E3C3ycAv*mdDHD6=5a3B3=as(`wp@8VbAM)$wYuGhPj^3_IeL@d~g#UID)tUXNdlmxR~hCGiVk2)_`&0Jg#}zze{ZcmZ5$C~SdCYe5Z#&2VYWsG+bqF0DB=6kdY|@blrd`1yDd*cvZ_Uj*CW7vW`KTf7Wj9=5~F<CS0syb>OSoziOiHZ>H!i+900!*}q`ct`ja-VtvPkK*m|>*1cXdTygu!VP!`Zv~&mTj4F?lXy$K1$-QDfj5JX;?3~p@G-nOehqvAzXrb+K80V4w}$KS)_5EED&7Wf3*W%o;_cv@csslUJcf6`JHfZpYFH=W*GhN=E=~L$SQi(*m67sG=}Qwo3ajAK#P`6mfmAK`P|xe|ZBWK+gC%j{hK!UKr7unVX;=`KCjKP!aB1R?!#}9Av_Gh=@IUyY_+#*Q{4x9q_%Hqh{uC?_@ck)#J-iSXzM7Hp67+>{WTgCJ`qISTgq3k=;>Tb$T$=dXunvAXwU)m4mGrN`>%w|?UHnp51Fu1?jR)yh!OOz(cv-w8EEP!Avk3JQ2JnKo2mhgN9xk;Kp2h#b{{v6sr>T?iGxUGQ|Al|!|Kd_BVMf4rX&KZ{SU8ZXTXE_nEQeo=SB6#b>RkJ3_~mJ}xSDG(Y>Hor*Mp7ldUy?3AFqK2VNE=UmxmSc@^~p&I;}RPs83P62rP{Y3*klZ0Q_%;?*UwDCHxKl2R{pc!q4KT;dl6H{0#gNKZE}bf5rdCrB=efaB1R&;RR{6EKEI1;KktuxbPypI9?7`z@?^FQO~QWrKxRWYA9@mH^m#lCU_I-XS^Z(`gl!P8?T91gq84$cxhM$FO3(1=i`NNsg>|g>h>pfGX4ww-|(N{5BN{`ckmSc9sVQy9{-+t8ULC7ulQf^9R3$BH4&aieWaa7O@zhpi|`8YlC+u$&HX8?Myr}uPvK>-DqfYZy$oK03v1!E_<G|F=r>?Z7;l`mM!wGQ*Mjg{T$*?j_zf;iydnGwmnL2tet}C9uLM8CrHPk;pW@O!Wi1F#;?hpC7KA786RZQ{AJYE?{{g;_|A3!@$MIA6_wYUZd;Dkk0saB&!T3k?&*8EbgdgL=Vu6%@LSJ}EAmwrT(!^`Q&v9XcK+3<QFKir0`PUh#+Me_L8VdiyrHOw7|HP$<e+B=*rHOw5&*IX=KZF0lrHOwEf5WATpM<~Q(!@`|pKxj7AHpB-L~T9ln#b>OY2wG>w_d8Ar#!z_!tZfu;vc~uacSZo!=G_!;-A1@acSalcp8@`{y98@OB4SR{*Fr%{~Dh2QZ;;+`UyY4KcIHTkJCR+?To)g{}22u%*Au5o$-D2_fb3JG5WvZzrbufo7x$Fjs9!Y&iG68f55+k8}JR(&iI<NS_<EzrsAhKwgwlj$4}wk!%g@mYHj>g`aj}7!z}z~{8zXO-$kvB@1=hlKLc~{9BOU+82w|^+W5O(s^;%eTj7WJ2l#RLK7Jg33%-NDh3CSfcrLyV9>DkEF}NF#;n^?~&&FSaFXOM_FToe_m+%d69lily17E<`;OpU9d_BGiZp1g?ufomvt9TZC9hVyIrzXNT@f`dZd>cQ8zYE_>tJUY!MEEuSA^tx60)HQW2Y!mbgCB(_@T2$vcnCj$?}l&SyYWo84bQ}1hR@?K<1fNz@E7rQ@JW0f{sMdye*s?$pTO7R8(|dRh;N3^;hXW-;nuX833tJr_%3`eZ71~<?!biy@%{Ll@FV<9{B8IN{x<#|{5-AZUs7A)H~8217w{|m3;a{~8U87L0-nTA;D_K5{1E;I+=IV?Z-cMk+wkY%v-tD)Gw^Br8T?83IQ}I5D0~Ee6n_FfhChKv;Zt}Ne-5t3pToDpEncejTdC(xd<Wcu3%BDt@PqI$eh~i%evE&Fe*)w9C-~>^OZ)-q`X#=S{z~d<d<Ffl@Xz3K{4@L{ydOV_AAw8prPS5<V)~1ztMNtjU%{V+3-M?1r{R43Y5Z|G7k?ao1V->j@W<dB{4x9~I1hgcUkw-FtMM)H9()VF9o~y?#}C6L_+k8Gcpv^T9*4{DIQ}JkAg!iTsiANtK9l+xpGJQLz8p@(m*e-tvH1P?QaA!%iZ6yk@x}NeI0#>aFN8Pa3-S4|Cq5sa3%lZT@d)gQNANkY3qA**2YcZ2@CC3hz5u@m4#WpiKjTB_521d>htpqz-v`IwW2m3;3G|oY55TGTC3)?tyjB5TftSx~_3~OpcqLvouhr#vU5<&D%4;?AS{YayFOk=3aJ&Y`#4pNgmva14j)@n|Ye9|&IVLXuPoXLtufj3$3-el4Pku4fXJx#YC%-!CAFswS@sfG%vb<ItR>w={wOSmn#WC@6dF}GNb}_7jSKwNegO}rS4cn3l+u#+shL_N;WUTNy{5rnoDz0mY;~|b+$u)1q@m3tG$F;6aeahl>VN1LvUsIPlwBUFPj@70P%{bnSV>PKm6OK3GSPkmXh~teob}2P#$nl086EBq4DpAiOcokS5ug}+1p_Y~Tx<Ys**Z^<9*Hog;S9APoj)}_}Xw31(921w?%Ni&~tIk+qQ@kl(BQEQrImerGOkCE?H5|W&W8$(_WX+VO)nTmgTKrnRMqJiWYmT?(n7FK=HXLumF>$$%r+fY$ES!bU#HYa-_%wVXoQzMz$HMXWSbPK=h07j0!1MQ1VITZvyeI6A_r$xx&Ujb6BkbU%_Sa6Hzjq3|;XUxaus7Zp9|-&71Mwj+?4|b6k)FRt3diAN@Ck4dJ^`N!r{i*MXLBuucjGhg$#4oj86OYtz{lgG;BELQd>FhHAHlJqa2P%mA4D5QeTMP117JUV0Nw}Qg!jR_!yEDLcxTui?~HeV*QeF81NH2JcY@dB!ghEkyc@g$?}qn=z3|?6e|QVt9}mO9UaI!O;WY7)a4;?$jgQ2~!Q1h1_#}8IJ_(ogA?rcb$6atbKAkb*@;lJ-yX^PE`M5BG3uocNX}EAQF1!O5j>UzeaN(`Ea0o6Oh6_jH!ZEn;c3e0K7f!{6GjZW;TsRM3kk<z0wM8(D3m2yOAo>gOxv(ET7rz_!!SBXrz@E5pN}AtDUpO(%JJX+tkB9B?@%U}<I{Y?#1Z;&1ho*T8`oiI9el7js_-NP$AB~TL?eKB<1lS3mfZqvk!0*JT!ydTst~BpW|1NwEyak_wFMtEnYMYbc*HCx_mnJ?4=HkMBfs`MhFHO7;+>Hx+22#F*zVOCC$}{N;I|ow!3VmVwK+0dDFHQV9xDFS#3Z(pb`qIQ(z-Mr2;@86GaABK3%Gc7DCf*Ki!iAjzDc?e0n)nUybzGWw54ar{_70>xMqirvEpR_B92iJ>PDZM>4^da)Blr<K7p}rrQB&h9=pVp$!~5~w_zt)j-+^bsg?J|Z3Y?3-g1-ds#$UqM!5R2E{CPM9pF&NIPozJQni{{8{&V<RI2~V$Z-RH>oA51g4!#9{9WKBZP*dag(%+89;C*-u-wz+a_v1P6p^Q{*$5BJ!9rz>oDmWfrg|C3O;Vba_;YfTW^)r4e{l)k~I0Rpa&xHf=fz;3VE%fikXTaY0415agf%l+(#&4iM5x*05$GcNM<2TWtj^71u#&4#6#s|=!gD-$#ynC07K$!ynumAOL>Yw~QgJ=DZfc00}e>R!^mH*_;mHZ>h?p@B4zv1%&dH>0a+;j4(*83l$d<+o'

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
