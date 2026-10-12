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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f634e3aae845402ca63e015086c9dbb4/part_009.stl', 'relative_path': 'f634e3aae845402ca63e015086c9dbb4/part_009.stl', 'source_sha256': 'e37bc629a29002ac3bb698f91f16e9b3f24ea0709be8a95af14700c6473d4c06', 'input_faces': 1152, 'input_vertices': 798, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3086753785610199, -0.22661805152893066, -0.34212666749954224], [0.20546478033065796, -0.11042486131191254, 0.34212663769721985]]}
GEOMETRY_BASE85 = 'c$}r3cbL@F8@7`XK|oQ82!b-$kRnJgq8kJhM2aH44ZVo;UPJF)5kz1pB1LHn0#Y`+?6NEiYy(t47^+Cef+Cjhym_CQ-{kQA@m=4?b)D<E_s*L$nM@`*DWgpqJd~|~!T*XI)5qM|+N6PDP<zxUU<~OxU{KG_T?dx!({H$GJmGr!7tRHZnl)_F$~1-;BTIDYI<WJA5;goKYIdtuqKv;px4r`g4d~dXL*D^ix{`mZWAA}ol^@unW52HI@0Y7quU5uiv1A$lX#fA?zg%h&0?p&I;%Hei%_Ee7Z>JoKi}Hb&Qd23NTZ7p*^VSDdeN2=O*BiG7yFOUqt4#Xa{%-qzN~`;&<8guyT~Bho(dG-+8`X;?M%U|JueXjh+%MIKeYoDvn#-@-#rE{Cd%Zrm_IiR;ANJvTt5tvQCzR#sU-x>wQ)Y33R3G+{`Xz6>K2WhhlBZttdcE^Q%LJ)D?8EiJvZc76s+OnT@fYFxBX#z8d@-;0EAMU(%?q->@S0~ibsv7+un&|hpCHwTeYoEF;CzPb7u5IkuY0}TF7jN0R3G-?dVkZ68Pf9WUa!}eU-yyv_q{&6-i%U9GNkoyl=S+@dfq!aL)sp6A6d`v`u3pv$oBtV(+p{Q*1cY@Z_m1qe1A_=%#gm1y4UOV@1yP`%hRZs>-GJK?)7?of1>-yb~U6BFQ>MD(|zRon3#OjeO>H7oryEu{i>Dlpr_B*THMX`!44Na{fE8N{*ddP8)rTKf$az0_-l2FyFA#R>)wuCpC#7sT$?HRz};IJl6UUkNRRg6<qrm)^em5Uq`2OA>sjw|_KxHC`$nedoz-PLKKy>e@5@=_T^@h+%IT6fMq@o{-um;m!;-gscMeJ389g>dte-kE*-hP7&v!ub#)?z>CGYI6lpxkmzZWO@P~3(+(LRvf=J&PwW|GHay*ZCx;{AvIy0hQdDfwXH?QNnzVQ-eaJ-G0C$p>Dayh8H+w?dz|f9uOrb$ma`hsuxd7bEyU?a(KZ57wN#LaZNDczv|Da(u??x%kb2ae}vs+#DEPA6}nEm-D~BLCgE8wq2?96C-$9pOW{h^)Gq)e8qmI-HRh{Yu?yXDM9j1@YH_E)AlKOOKs0$z1sdouf8wQKD-?|t8ONFJl317wnOrkzWnO@D0yd8x1*A$@4MuKYQH3TOYO(R{?&fZ{e1QJrS_AOr~OZ~5AXMEwcnF`<hcK-cYhvI`}1fY-cN?=KI`$(`$Nh5)&4WuNAD*kA6_1-cUOMh6Ek?d^<2r{Q_b6Tb1&rA^LnROlm4P#vaD~6;H`hxe<Jxn-2p2+{+)6Bx@`^&iW7XGdR_PXXn&~nKW$iw<c<HX^7dJSeW2U|_KOy~$3Y9;S-Xfo-;-xDJbu>4ygYrL=i?oGc>mz^%##r9!~Hv@TX9woFaM|fx*gi?iT2@o|Ch^nf2(<C%`$htVN`$cb)$W_|6u#Jyx*wy;POZNaR0ViPIvuOdvHBO`{?!N_EWeEZ-=oXc>OPL>h|ND>dgHNn9KdYeZ)P^8t``UiM;$*$9*h$>*sMFyW8i<2m5i~Z%QYA-E+P8{U+_=el%~4ZsqpljA9?GKbp6n0bAC&{b}Cmzh#~Keoxisehv;i==!&2x!XzD`;%L_-sn5o<E>+jTp#Q+oVP3ZpuL>m*XeObqkXvlK-`fG$@_oGlkVxK=K$ARxyxrr-pO&{sO0UqWrw4^mAgOt3%4?(edK)&yC-^QVRDA#gSV@TKJfS>>5{iIe>*Dn|M)!ba$<ctCvs#--v86C49N!?*Au-R_gk9ejk$S6?`$57?biD_+7IPUmAo<SlVr(TwSU|1@!`+0Mb}ixJ9&zyi1qa@CrjQavL;Eak9#{Y+DF#^{=un|H_Ut~V*R$e$&z<Aev%~Cmu~5K-N<?#H$PSMEAJkZyfq-d=$*zRl0-j!p!>ScN$vCM{-h)NB3m~{`^f&S;ozN~`tbK?>A`r(TNipblJ`%@+Aa2zT5y--jj4sUiT&qqwI$kz*RxfAXT0R?#={-auiv^`^2X|_yCfgj^hd1ZL)V6TmM60Q2QG=1yz$sVNAlM7k-H@y=+tMI=qv4umAt=uth+q6_W1^_n=7JyAgvwm|0|arD*AF|hsH$r6aHL++t<bk-v4UNRg$-xj-4;oKazcn=zZD8h_Czp*!j^uvi@%l^ej*0^Ex+rmE?^(_veW|C8sU=137K!b?saC=SBPfeNVG{mM3x?Y=3Q)<c(|v=Se=a^!PZ*JD(jNC%vxiE9fqdrGKy0=Pr8neUJ8$@zuM7cY5l>>tB7olDC&{Un_a~o=QGArO-CX`_+CR+DE?E>T?vm`rIW?-$%(C>ia8sXH`|t>qfpu?XInoywN}VTFKkpVz)@%skkpz^d0-SuWJbVXUWrX)8nz;LgTY`OP=<_lBfN)Sg($clBeTow2!QRwf~en?Qg|;wSN}t)$vjE>UbLMBj2NIBX>)l_N$V&)qYs=bbOS&rH-fMogW??&q&@<;~%kJjc=oU^f=a2A70ODJR^A;|A_T!yd-)xz7_jX<Kbu@J)V)gW8_PbyrsrVV!ax#iuG!ID|s3ZNBhX<sKz;xcUIh$y*)ow^0peUihfSsG|5|PJWSr!J}){SkvyFTMf>RUk!T-%ei7{>>tCHONS@9wBv0ofk`MKn>{*`Z@xSB^b-o~ZI=_%SoyWP~m(lfjJ)8~l@#4S^zD^Dw-u?rv|K{_Zkq_3#MES_~NY%UkL-zLE$vkdZl6|E+zvcr&Pw;gT_`nx+_`1RMpN7T>KA6&NNOZmR7uH+v_4DHdA3TyZM)Lj*?~jh|$GKtgdOls+(@)qtIl9}DH*UN;*3(bND!e?$YR`)ky!}t{@ox6=t_P#t!|wKPk1W7``gr#|Eqq_V9{!+r*K^IA?%)0qFM8^&8V`E6|N9Hv^A&qVHa-u$jsEX>y%WC9<{$BGOw{rRe&qM%*SwwQx$%;>+H`csIhN*~2^Z$l-@zX2BipV2pnG1d`;gh#^^WHKr~k~5d|>Zb*M~G8{In!r@9L?&?wx>pzU<e$y=L2C$vZs~-1TK?-g>4WZ`ZmX_Z;`9_tS*W`yTK!_`ENu`$0G#(fiNC=OZD_2X6BDi0<t!d_H3I(tH&@AMtD6>dEILmR>)E$H}@6b>eYyK(Buk<7B;lBgV;XCb>ScUmbgbuagv->hXd1Yw>d%nm1m{ktzAmV*~iUrsnOtRo(3&sCj38U3YtM^!kU>4@=(I@P)fQgfwrBD$n2V!dm@vIe7ck{bs)YpnInbUw^PPZ&l#)<$zw_gwL04%?H2Y^JU%p*YNprQ1kW{oG<Ikd6UnVLwY~I@_C%@gO~U`&Ujku{~n*m`898x<nuV=mubA;!2ULLk@wGj%{zs7|Ezl>mG{q<=B*j2?s-<|_FC6R#?>Qg@O|VvULTs=i?6?F-kDg%-A)3Ux0WvC{i){dE4BDIrg@{lpYHW2NAIU7UkB5@?ch4tFPgu|*KPcow<hs*8{G$w@O7Jj<^xai^%-0DmH7HVQ1eDxzCPe+-d~EZ4;TyA@%J6a-@sr#Ui&p4yv4_B-TSBU@!Hb7Q{)}@dV>E}G57vJ`1obxxaR-W>n$AD{0A-9NA9C-xX<ITx8LOY@O_p(eE%q@`&xW|C-`qY*9Tr-$>XB8x4NHW;6L`^agl%0X!rVCU{3>2y-_-wJ1+7MY0S$rX*$>MEaLj0?q^(cU)TRjQ}!5-SyoYpKbNMS*A3Kr!o45u-}8ZI`TdRf{#Q`*!Qc6QR`BcQe81(JFS(y7&$-_V|HkH?_2wijOo{f9_m$Da-Tnjck@Kl$f4kdr5Z+m`3ip#nyZ4U*o8WPO$A8p6*v$?tcsax4rK@kc?<=Tzd)|5X{zx#;!uxsEo}1$F6{m6iYYp6SSD;rb_AS@&>rQUM&ms9*v(Gk)m-FzA!IJlP?LCP84wY!@`COd6_xSmdHEli1WBvOjFHijr-sLP;!CjuvijJQ3X&s4kuj>Y1`EH;4`D0uc-p+&Ny*|918z<(u=hNYFW4PY<-s{8lwo{wWv++ESowAC@hY4P999-qrI~&_4M|=Or+xa<`&0cRT*v|bIk8#ic!p~a<!{g8Az21-IaW>|3*HdKtll=^j12u1z?j-uqA2~B6Z>P@Y=YKY7{Vb}IE_r+S;55k_`I8Qd{d{{gRqUtfvngUf_e=16x_^(yhY$FfJU)ED59aZq?rn?@AE>{@<3n5X{;oVee85-b@uBWR7$53BI26}W_1Epf<3mUDP97c~>OK(5<3lGd7hli7c|`CmpO5I?$j|2^x_6rM`H1fAaeO{vT*~YE$oQn|bsi6B-f3Ql?<Z>B_@hp`<n8ox{5`9k-{V82n(_Ts%^O9>Wk}u`)`rKWdVQPNRLNU;UrQ1F>$wk#9^=mk`hNxYzv_6sjq#`MjrVx`se9{d9)IfI!T3}6{;fRz)O`@+PfPFrHy(fL-nq=<&j<W{9)IdSc!tNH)?e(y<3|5aJpR<Z^-OoM-bldsQ}@$&{Au-m$@Rup&3HRsdz#O8H1AaF!rO`F?ZuB|O5P|nH$(CvJWr^5=i}jNlDC>C@cEA3|Imz7(SKSbMe_EJQU}HQDnpV)Uw;U1Zy#y>>|7Ktc_Vd^BY9`%z}=D$oEf-F?0@ghSjk%#cJlV7zi#fkUrIjM{O&5r2TB_AByUYH$MgFr!Q+DPxVqu$RLR?;8>EQ7+~3Kf$9aVA9h^s4y2p8h?n5|_(7kn(&m(ki6vTOizC4w2pHc6pJ?=B=z9Q~3<}1m^h4A^pP(F{)z4K?5SZ~;T9-(`?FrP;lCE16s4;xJz@%~@)R-F-iJ_sLKZ@u2-aYCI}TpyaymOuA*u4GBx|9dO`zH2`CT7gW-TbCzgNZvSYrAyw~*f~w?=d&MpJgC>-+LJ1I8`m*(Z)6rYDEbkzl0@G*z|S-2e%Z!&$=jF4J7RsUmAfVH&tGqs=%-zb75iy3-Q7Noy4w0L(sZrl198h%Nj}tK(>%%BZ_IL!3r?OG-rjH@!6|nqOY(ukO+{}Me<oA%b{@XY8TQ7vU3hsuJDDZ<z+2r!Z{fO`?(M4cd7S*X_jUdG>ZeQI`mb4<<n8QN4@=%T_jRi1ah*i>M&iQ<qkZIkm8qC6d1uq;G|AhG;|@#Sn14J~^rN0i5&O?9%kNuX&Z(a#iN4u;iK72%Z@lEK;R77WhuS*3qkZIa96m5f@<x{tiDLcIkK;vu`Ey6|ftWsgzMyXpf0W!M`Y(LjBp-<By+!hN(>ZI!ex`O>740MIzrd(nlDDU9jun03_$`tT6uS1M<gNYLSG%vHEl)7H#C*v+d#jC&_L0|p@9bR3hZ?@Z_k&Vv@%Zz25B7%xS&}#Q&E)Spyj`&uj+_0{M8EtHkJC!l_V`fo^I4KN^5^0EfTg@X5L+W%@<x3;2djCz^ouE?$9)h>_lL$NN#4oVCsFc7!<F%3KUL;9k`JDn%-gNz{R2AhlDvI6HCFQ0w_j|LywR@cTG5X=&gZ%M`aJUPJjsWu^>EK~jggIcJGn5F`{~$@#|iLut>L^pFZWD~_ThT}`_p**uhl!b;!`DW+$hBF`-dj3cb1Rvj9YXc9-lby;eJA8cpRd8qvrRAMemg5?c}7_TYIM`N!}^eIZ^WVxef7RKPx9Wk`E?-&ihZjpP3DJN#1$<Y^>z1dGohOKJ;?EwPHV8*WvjwuMhNJJWulW&7*u?nN|9b>v4V3npl)S_nYNhAGuCA=35^BH!Sb*4z52t>npfEG?Sli5AAy|OY;6thV%BbfqnQoZQzTX?saJ^XC>EL*GBTVuu>g9e}oS|e{RgWkR0v9^-hTIHyg3+BiE(-^7Zzx4`25V{^#e{)#^hrd>!7>>aFzKu6MduX1{g}FK4%6N8+M<<T?3#eR+9%c)juafh5sic_~ry_Ryc>#rj9<Ig<BReUg8dtk*wte5dGZw%#Urr^{1Y#QI07uakVJRjj){ZOsRspS(cwmjBvt_jQu0@OFjYLxsjYbu8M4*R#<whL0l$G+(wm?;l>M=Gi`t<<Ic_%JJ1*?|*U~zwU1_S<yc7eBJOKd>n)iZ=cp*oq7K@!Rv!Vm-6p!?p60}KlYP#2TMM*5WfS`>uck8K$`b2+3)^-$AJ%ThsNf1?)7}*Tn*3n*C}6tufxMz1?F)5;kS4{A5+s)@88inGulUfKN5QJnB<*r8uI=bKC+%i{>{HnwQ71^*Dl)8{k@5^^mX>nE#vi2c3gV2kMuutu;`5gHQeu)vCQl3bll(2ytDN}QnZh(hwrlS?|?NQ*xG21<gLHv@;FoTp?@~;_W$=A{JOZGWxUv&_XF_Z^=ypf-+SubDOi(#*BKMTpYO}Fc)Ke4(I>qAz21s@)V+^pwYGS9?(y~z`sE|uufm77bGsZbSJ;O><NH(A{L*QXx8E3<DtYJXA-<0cAAY~q$HfyQAM7`2PqdG`?oW><O5W*Nj`w42y!|*klec+1zIXQYgw4@DydI47CM%<TxPPO_ik*@V6}!y8&(->|%?(3bKiBepPn+=lO<VKUulT**u3Db;Z{+)ruS1?^Z=_<o>b8Q%_k-(rx5G#B@%K*i*6P;0ztX&Yrh2C210%*~NItl&W4h#x6(6KY-rA9uw`a{eH&>=g-s;>jMe@dyUy{Xs>h4Ms{il`qI5<S>=isS$$veB7Ig$^3cW<}oN8a8k`QYg{wn^TfSb>j&nz!rw)=A!(cWb5Otu=)fi2dYRG18rHQXTJhbt;y}$1lI_-40jP;r)LF_JMBO`F%bAJa0dmH~xAjQ}TgJA7)728apsu^g~Oei9TmFcRR5)?~EIkDtUYRloZKZGgFd9e>apQd1G4cMA1L(<NcEEzb@lQ-aqQCJ(71;EZHe}D{<;Jv7c8?@qVeI*9QwNTqpXgHC9SK^j_tUC2xFp-yK)jbL)9uH&C08?+qJxkIMsVXGZ(*^8?}Q&${=Q9K!nztsj5=57Q-Yzwy$MXdmgn-Ro(Rw{p%(mArj*aEe&J{WR}4^!n0iNs>3VKAR}kH@+P&)}M%RB=1~)&fOl2MqVHMHGZe$LuI>elf3g<wk?tmbpK$T*iVjGyx(Z#UC)7ATNXt7$nwnCIm~^38{YNQhdwWIEUt;?zsA*O(UwYf6}psR7&(msMz@Yp|0yn#^e>$9e~PPTrT?q{6j%B3l`H)J{kOPsjWZ47W7X=S5x<Gt41N<FquLv)ZBnfkasjv&xDL_=*8#tcYyzfi41OE@78-GF<XCWRu!Wotw!q8Ox?HJpv1;QDZp7mZZp1awh?miO^l>ggE(TMs1XCkE;p0Y}<l{!X9<}s(>ygXAl=D$T^^{K{=Yy#c-+~(pz6CyxYz%IUb$1+%_yij9ZKMsp4KC>8TmYs<{55hDcoRNjV#+B7Gd1Fk$O&L-#G8;4!IV?M)QC4DX*(j0!FENwIlRsJxDh{v90#UGd<X75@E!1XXvE(m-v?8U2Y(O#1^Eg17jPl<ItP558}K*z4Vb>%V5Xb|rd)*@YQzW75Ak<CZp5D;KLaoHaW2Q-<d>rnzm7&c+2EwtBVMf9G}XQ`Ik%e3)QErZaU;Hsj0IC8zN2!BkMnE%P5x^%;(BPr(+$q8;H`LV;u@;eH;u?YViVZ_OxX}jjd(BILNMiaFy#*LUhr--;$5oEpnW#&1CTM`mEcv#df-*y)vC=@?M>CzAZvlwfWJmoGnpwjz|W%hrrMXt+Tbt2n~>E_X3DkjpV7LYeFgFz@OtnT)#lLpQEd<MUGRR@_Nmqk`2m=+F_^Lum~t1Gaxa)N0Zf?;raS<qj0eZ#^_wBz1yk+>Q|<;+I$+8qFy#*L4!qZ9$alb$Uw|psfhjkGDZc?zZU=A2I&Ows3#Qx%rrZXmj0MNyvu%dl0H*v3Ot}?Ixf)Da4@}!z9sEsM7fks!nDQ+!<?G;j;5X2SYpV8?YA>nwJn|__pRL+^svSW#0UrTpA-@Gv#(}fIKd3fWwWg}2A>Rk5fsZ2(fhmuI=c(30wG3o)a0d80)q<+EQtdplCHOq}ifT(#YopplWNYv_)jFwm8QBi}n`#|Y`vch?{0I1N<mX_@pTK{EP4&I}U1b;5?jZx<d*FYOE5MY0g72!<O||>TuHgG%+R<fKt%t&#$nIcj#CcTaRjr_E{S3}0!IV#cDRYA<bATy(8O)SD!ITTYl(|q(`8b%e0GKjAm@*GI50<kZmi=Qe<s+z}d<;yP4@~(m_+jk$`(eFwML(4D!IXc2DgOggX2ZOc4}mHFMa{qXT>2sZ0aN-=PicZFe?krA4KU@eV9H;>{lJ}(*TL7ZJ$6R615>sIQ+5PXhQO4Uz?9d(ly|_Cx51QG!IT%ll&!&(XTg*gz?46ODQ|%(Z-ObWfGJyoDO16enPAHA!IWpfls|$gzXMY?2U8vfQ>KF{Pk<>;gDFpeDUX9GkAf+WfhkXdDSrS{#(^ml!IUXr%7fs};AUvVbR7OxZ9h9z+k-~D5BUw4@>B3W@IwY?BQWK=V9IyEl&=}g)QHs(&3H=r-YSbAKLk@F_9Od(3#rye@iWMez|@GJLoNhU7B!g*t2RLWT@2YDOpW*j<Wlf!str<H7C8`1jrdiSHB=j-xEyjYc$mtes*Oc10#m+XGE-IrQ&t62RsmC108^F&Qw~O-l%Ikr%b<p`JeaaFn6eU>@>TGwcwb}jUOxd-K8+g67r~UJ!IY)IlrMlOm!coaXW=QI2UC^=Q@#v-8K2u&e3nJQl*Pf6CBT#~fvLTOeIunGOi9~PKWtNvn*ZA$64SA3gyNB^*~l?q%F$rTQD7T97CGGb-!c%>wopQ~LbT41B{1JQllPln`8Yd*cdAxIeNhsT4}+gpnW-`xat=6NWnq>3kq?2hfuBYe20snHf%@w{=1jcCN+dbr4=`;CawT{r<|8hLy8g&1;3=pf&W^fP$o}B|s3CqBbuE#tz^zb2To!fxkS)P2QA6Amb(4|(!2M7&8F?KXk9k%gCxa)WW(C@H)LzHBBQB)!m`Wcq1MH}LN@Y6I1pB~+kWYaNfv=(ds*m{?UL%MkNBlmfO+p62LCi<|3hMeICxIuShBzDQS|Iy^`=W;UA=EWTwg9(44RION^+7fVH%ATed#Ia;>;vwDnu*A(U<dOoM@|G!M9p%vtEjz-bw^xKWtNW*I+QcPaVnowc?9{NkJ$hhMAEc^Xv9CmUGXtzp>`RP9B~s&n}A#fUWWOIOQY^1<OJ{p)DZhn*9`d)_#@O1o2YAyYzA(I8sbu@>y2y-Zj2h@cThJT*&Ey&HRF+2z;T#oDRMk`JZhGrT|w;?tUKZYD$`W{>*HJt-ltlAHSI9+A0IPK`v>#=gJ}iOh<}2+>|;(t?dM2x#Pu<49P)GU=a`SUB<emyjsuTF4Y7f`M#vArAEJi%Ka=YkqP`Kh5o(BEMqMu?xn7v|6SyAgY-BHRFVxt`%iw*OX9>~<+o)NBb{VyovF?cTsXVIkZy)Cl@Ds|Xs{G5xIRm^$wa3-8gUEY6W}0>n^WDR=C(wv5z@7Ior=oTqk{odirVT^R1JA>J#4n<*J8~F!7;1?BHo2}Y>brxxqlWmt$#r#5Pp%H8T>!s;x^75v-7xI}_zl#JMs@>tL(OR9dGH?0vj{mFJQ_8N(9WawJk}j?9+ihw{^{e~0N$<IqiR|L@(&*~P5T4${efwD(1_2$g?!A1P&*$<j`(#<8;YC{o{#y6pGRFs<WTTX)DZt=a$RlIcLaAt4e>pb>)u2?xi>NG9QZlZbw!fvifQM-HBmPT*%jOsHKULr@NUfWDRLBe6ly+23!yfIbw~V|$`qA%eVo(5->Q~dP1}Y1-N#JRe#d;jW7=bA#Ao5o_?S~rI~Pfg_%%!$jGPOei}{F)qb`6P3?7Uc;y+EUtA+XiIDi`BKTNK(P*2Xnw6kD8>bfAwb-}c=;2NkKiR=RIf|`-YGvIGA&zH!N;E|~L6739X&tTmV=Te!h@;4vndhj=@J))*<L;mVxrfI)ozF#pd7aH-8aHoCD$*7%;Bu88s(}o~tgJ)wt;$o=lfE)rIf*RtxCf8L*eFty{)DZt}a$PmlldFblKZ2h{U1ub@&Y1QixDx6{AUlIQqh<v1H253Lvj#Z=JOVXq&`zWFG}aw)PL;7Lb0F7&x2t?c<yPb`KIR<YoJg9M6OH&3+({pEENW*V$q`q?v_Z&O;8~cD_!-o-M-BoHLJje6Cf8L(eS2_w)DZt_a$ObFldFPhr@%!~*9l3k6Q-R4S3uoxWG8SZ)C@<S1aHSYUm%Brhoj~Tw3DbkiFHT3SGBx~zenEpG1HiUI3FBM%ZEmM3GSkg`6y~XLy{wY8`H)jKLdY;`G`xPt|xLVcr0p&|24VpUDWpk_e2fxKPJ~TKs~tzn05*L66$&&$@RdrOW?OqHwM`Q+ygaZkQc#wG0$S;81NX>EJnMC+KX6s#6?veSD7986}XL$|DJ|i4KDBFX#<hdz>i>BJLEuc4oqu{YzKZ7(*_{hf?H$SROA5gPE1>coC>CE7c}iAYF2?)q2?yu4_)6ViYx*y3ciJYsP-1-nF^kYWw?cG3vP?|atk>SJP_;T7IHQC7MNahHP$Jydq2(OduU&SKQwutN&Ccj<VlnHB&NqBn}O-xTyvBAiv>5sewzA9K*odPF+Bm<98CB7dZWK>;O00cP+w=zX973@)6XD#gX!L43zP3FZUTQ~@-do@!TXV?Oy*OVz8~2FO!q5WqQC9n78n;$Ux~>5;Qg4Mh-?X_d!T*L-#6fv7=ut>XVGUOI1$s&BKv^pK5Q$K@4;>X_ceJ;NMpVv<Y|-nG^QsZTY>4`Zfo?n1KbMZQ0nUdG6|f7=?9Rl!F2C<vdQ<29dJLB$HO$<&4~<|%ppuCrko6>dHZ3xlECyDG%qbv2+MW=d;rr!$bMn3=51s0J@9yNf0NH;=v*ZkdCp`$hv~`4HekB9-WL5G0MoR;(bqv_GB_F24<g%w6V$u|&|fl`rqMYX^>rS79t0o6^z+C8V7kZA-sJlk2f^)3-p|v1{17q)oPz0xknO=VFa5pW;6^+U^U}UP1$hB|T)^}cWIHh3Yo2NHz392%wI*LDq3a)yBaeV7Y5L>HnP7T8VT#GmP|N{;Ve)w*o&V)R9t2a;^jyd(V7k{v_ujgj%#?J`?J9V*$@_WQr)Qa*H%#Umn4X2~4t@m3hGUqQ9C3LZOKzfu95LMo9Aolw+yVD6Id6h*qK_WPEN~WHw+E8uC#GxBbgg*~G9TDYlX(t!smb>cDK8-BfazI+EhgVXqnr+=Mojn962XH^9*594<1yq#llda16AwZ^#5A^{d3GQl15;AX4&)XvU4x}-tXECWbd#B~3-~H{1d{GkjzE47rhAKYud$=a*9Pg@-%*qEh{;TixD&D?n3CotrhAvOR1P!wS|weJd;)pJWWIvw#FVqZbp4a&nTdP?Oi48}@i+13Cf`4$Oh?WF&%$yL({(wz?v@96*<_|10;cPGRJRtH2Tad<1WmrbdK5gv<fQ2{ka@tALr_CW_hM%tkAi6%pnVN}{*;Hnl<mP6!Gn;r&l-eG1k*J@y2h7^yks&{4hE-!J0R)Vmk!7u!1P@xhwlO9b(5KL6qwp5d<Q7$KKdNw1u#8lwZ!CStSF~~sS(ruI{{4lV!HlD`|jLG+BfG$4ge28Kg4uRkLH<y%nhcbni<F?V7mYA-j_FVPu}GF@ZW)ln|$Aa?kl93oIjh)KVy0tvNM>zUk~9s_7LVvM@z$ZD-HEskhBcMbnT0d<r|PW!IX6D-hjV}*O>fV8Rc%|WH5bhC-K?QwPM;14r6;r1s?_nkR8C3G%qndW46fT=ga8Y4vn9RAZdJ51lb2njd&6qjl(7(*MZlePhz^JMEy=j76DVz^y$b&V0u<?qsh;#(KQVkr#_9Oap=>?-e79P6X9sQI}y1S>^}d78oHK3{jNto4W^{&>yaD5^xWfWlb?g5b9p*fFO2-rWTxx|rbavgj-HvDfZPD4T#XvKhCuzULly>8()4x6)!>l9_kihn89HC1V`l**9SaK}$AGC3&x505>OABn@Fny~Oy@Dw?^nnIU`m?)6>=T8oSL^Rts7(oa7A!cWEF5#aCKxgaCLBH)yk;$ifXSS%Y$D9S3*_>SH`@RP*3xhR4tEckE@msnID`FTp0N@xG?w`<g?&sz{Qczfs2D*MwSGZ#4@~$*QMpijm!nk4bFkg4$c977?}<HFgPdj5pYiMW2!x&T3&<xcj%mtfgeLn*i+q;_`K-zD}^i#E(LxG`2zSQ@bhTI#gKk*F>n!NQE*YbW)U>vf@s7AkWYYVoJnIx_t`EVUkk{OOaxP|Fq!j%=bD`KJmp;EMes%RNlfEa>X*i<tug-%^hMKepl&pn#w|1+qA?34je&?MJAto&haqV!Gz@tHOwX9nGiO~*&Tc02O*ne)><W0K$<Hd#vj`a`=QWf08m4C;yMigZf$3QYnm-f$kjuohZeTjrXUB0qJ8G|ES~u`@@F*lL_bBAgU>Z}=afrrKlyvMNrVM~DgNGpL7&HWV3{2zD*(Q%g>DdDs*XBji_%$zb1ekI*n4V{#c`}fB!IV^!fxn5jnfxptWhQbqcs7=Un8v+yZ=1%sls}owltaNsz#WnFOkPLiDKK4|rE9No$RA8*%AVlgQ0E}yz;vvkX+NUI0aJbe{t+BL=1^`$egLLMOwVht1~<iY2khW=n<9IHsh)BbvL~3%dFecMA95O)8ZkYa{{i?*ldoseb;?JP--9V>`lHBcU^;iEc`jhyN5Pa-a{;vj!L-ilGYCJwO*|8y-8=aFnlvzd1s?j}kJqM;xwExN1M<9&4F99w4ymoO>wrN$@oP4HPVdj&qUW5g`ilGru1SN3X<x3s7e4oa!TRIrum1zT9Fu4'

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
