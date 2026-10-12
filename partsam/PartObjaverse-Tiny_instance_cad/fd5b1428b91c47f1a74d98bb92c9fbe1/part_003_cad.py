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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fd5b1428b91c47f1a74d98bb92c9fbe1/part_003.stl', 'relative_path': 'fd5b1428b91c47f1a74d98bb92c9fbe1/part_003.stl', 'source_sha256': 'd838ba0c88046f7375bc98785ef36d5eb42be5a6a0f844534822d3f75c50f2f6', 'input_faces': 1258, 'input_vertices': 733, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4957084655761719, -0.5, -0.23664826154708862], [0.4956889748573303, 0.2940065264701843, 0.25399506092071533]]}
GEOMETRY_BASE85 = 'c$}r2cbrYfAF$7Aiy(v`2v@X3i|8#}z4u<iMUW6Bh!&E=28k|ekhnth-pek>VzG<ewU%wTge0UWi6kQB-I;mL{$_6S$NPET<TIb=xnF1Jp7WhKbK0ESu}$VI1uXSnNvp*D5y`ciS(YfdtOC~f!DGg~J!tUQ$|FZl3bFFaxcJZI;`ZIzb?g;ljkn$}_vYZSgT|Dr>nT@%NbPbJJ>`as8Z&OpfRX)2jd^phh&Lbb&e*}}@v(0W7(F=s^UJlWRjcT!_DV(1RL}q8e>ufE>^gkocsiVa{*koCuR9^=Ke*M12U<s-l<^B;M%*5H`k0{a@&q&fa{OueIY%M&IrNdLKl#2R>&yMD`Mpg?pAq!tea2YcbM)6pxm=OouN(DSn`AxSl0O)6&)qNO@>ZEU*Y$e5d6q@Uf3J{Y#H|fKo|5rb6O4MCZ$CRA<29p<xVK|*S&v=!n2cMMcBuF-5psPz^^Y3M`%~u0`mIKLjODGgBXT`G-RBx{r+#BuzrXt&RZsVUYWb8OW&L)a=|<e={2=QI^qFSV<BQp>zIWhwGY{t{M#;Y)_@1h#=4$o5eJxf0Tf@wFmz%Ob1m5js=09sbSx?}-&gObHs;lxdp@X@e2V&*=c;9bn=DFbFbMoJ(G&jE2{vlJij8A*rY_HzY`{n29^^E0xoes$U=`1WM;{mt+un*+&fkh?E{6DTN*WcRp-8FqZ?btCYKfAuYX0-3Pm9ifH{_EHD@Ab|qBm22G^2{~;d#$eyZj|wJN3I$9-xhXOe!jTd_+IbOJ*xgon^is3Z+#!RPyTz-nrlWs{4uwz$Ct9oh&yA#qb0wdt>W>jzgXda9+#i*erUwKgHFr#wSFILZg28yvVQB&er7#!HC4NWbTjK2{ejHCC%4z!-fY=r9;`eK%<a9<Le?KBSlP&@^?oin4tR>ZY~<6)|6qfxw^Sjs{=92s{|Qw2C(X!D*HSX>eeLfweLVv^Q&m5#`%{|HAD*$~dfKmlmu9r1ui>Y1ecE17aq6*`_m=JD>u@H`=>KKcY?AHR@w8FD?QJ2~$L<!Mrnj%%?=87qzTSI{^|z7}VkCzzO*8h#yZKeSOdFAA>=&%3J*T&^z21H6Wq<a~?P+e;OFQNA{?+x&dZuoX{m0r=*39Rrmu1}ER@}@R^#mdxryBkC*S}T$ryrymc`Lb5=EphngNj!qKResY`hDl_rW*U><m-zilh3E>>toM+`@CGQ)N?ZKjSo}fL50<_{{+&aQuVyq1D;X+<a%VPk%zHU=Qb4Wn|YdyTRj)3{+0V}xxZN1CmM0<@GELOEHEHd&zn=ZwrnrEP+xQTlkMgH;=It)Sl$X<^NILg`^8Qw-eaL$-t*{FIi7oqcQm%wJ7J&9kH1uNbN#z}XNh`z6>1xKw)T9#Lb5?YGtUE4WIch#xl@gHeAbcmc$$YA`LwrBll{$U`!q$h%OaJZj)&y_Znyg*#n^ufFH+-q=Z7gqe`p*TChGV0xtU_*Ic2vz&N^?Tr5O8B?w39i%Uc7kr098Y-q@?!eaR$MPx@EL@A+>02D$vwi795DZP_lq)x(T>tj@oye6Ag!;$4@j_F7O#jpw_Xr|5a`4tuKdu&Y^$k>@Ps2g!B}uactY*{bhR-+Q8*xxLA&cF51CJu>ch$FaSkUx|90(<O|2I={rJe4fv5Y_F$Q;q|h;en?K%+tDf9QO50`5@p=(vRsX?`G1q!<@@=(TD}&?&HSHyDcdD<bF!ZQz-)V+i2Do9OE&uRz(wojzn31XmXG^L?RV{7RqI)`ce0V^;j2`8HLt1axx~0sxX^03o~^2=c$XEb{ym%IcxCs`o~&=Lzw^;Oay@;aX8rwcsqxCbkYwcTpK!T8{uw8e^gIXd?A$HCcjk#CW4rRks_}F7ktF?leGT%;<vm|4Q}tgwD91nVx!ZDl@O-(zh<h$(mg9rHaYmA!XZz62owA<I(`DS-NgcP{<6U6$v?RS9z2&RR@AYq=Y}9XM+Yq7hG)C2P@sNr)43*=CFRERV-j4R*v%6%!N~j^@c1(m?J}yq3CtoYA;uk+w{dq`cnK$cJQFD7+&OI#G^T(`7dOLbnt=}TIE6eq(Mn0F6A1LC!=T6DEbLyO`r+v5_H>`pYSM_$ZM=q89#4Z>v<KB*+tA0DMw#rYHxmS(#X;e<07kR4BH0tpVNR$1++otbTy&aw2_YaHpvD)^zs`nEs^Fg`2p7uS|_Z~}B$H~z8@;t$Qv+`BF|M-e6JS6+ikP1fq-q~jl%KFC^FxJy)GHsWvZ(@$CdVjEbbUPs1WyYf`db|6^{37e|EV_0@&!_X~?lKu)c3H;#2XCtSFRoM9FKeAEdb>N@KR&4X&*m#eJ_pp5`LuVfzoNIJ@ArOt<@%f(f5qr;nQzGBbs(*aTK>RomH$n5<@fsjDy-rcKT-YXt$)<{ZTT~a^7Fx4a(UmU`Q-Q$C?Az*wqu30a=9A&WZdKSpRoRNJha-(P1N%oh#BCBxVP*3M%>C#=9uhn-6tgK?d6}9_qeR5?}$WWfBa`~xXjPk#)-y$cdxIk#||r#sOQIyFC_bqJwIQfv42&*86n$cNvK->XsX)YPfDuoU2YlMYel!0=QDxNA77TA&z@B6*e9pjul*0r_<<Vo`r6s}wGp?Ui8(6swdIBxFW5_+=Z8ngxYKd9%%`_cb9H?k5pFE+Yg=4hN1xqf#NGYfcXP545B$DgUBBNMb6IaMyGP^>ndc`R%zA!UB#-ZQNF#H*VnXFO=`C3FvXP%Wea6b=U(BPHZymKoetx<4$%cCTL9sdV^R8;AWV^qVRjrR(f9L{r-Bj`C1pRxhwcXV9PNNG6dV6_hmXqyew>p+!^pk}bWPb~^JCLCFH-Dzs6S5z6*_NQbkMqET-6Lflx^Fa=_f_hw*1!7(V|@aje0W0Tab1GG{&v%jd*r|OUz(uzL#Ieq)j!|)KrQc{zdig(u8%*gt6BdCi&dUybdvFadw%uYUbXy^8s_(os3FHI&u5iXJw>Bszw~}SQ*KvA{L_nays+wro|bu7^HPG|ADoB7<iGpZluR(%cf`7B^6#QAU((mpGku;quTDCANnanUbhB+T{(Ku_d2iSpxxBAj1!H-;dkZ;Uc`B5?q_?BfC6~;<uX6EA`uaGvRxOe7s)a7;dG-t}soJ+*=q0@!?fn&Ge+xAEEnaVTYtRW9_jkAzujj!RdPk1)R=1>hy&mtmB$>BBuh@9K9qqLpWIf)g3*wFK8a7RycloEzkJsDLT_0=Cc(pzW3)Ov%oF`7`aVzg4^*Q#u`rfaaspZdepQ%<4b-lc`o{GE2<=Vf=<Fd7*rdpo~U&g8J`dyBzzJq1d`ndVru>T7YcMg_T^|Vs=Gu-=offLWExO@L3wt%`{5tYOI-U<!m`LqA>1NnXKal|vJp*lam@?)HyA8++0@;KuBx+l))|6@0*{$HVsvAi|m$!fWLwWezMEPn1&%$EHmBW`^>MYhNGIx5d~>c;8q8@O`)h>W)^5vTVbJJ)=*zjw<Pr}sn8z11@Ro~z-pM&8zzlgGQj-IcL=Ke6hjMal2~eua$NPu^Dj;mIU5u4Wk?tM^0aTG$!+z2z#z>ix=FDw~Q|DXQw<=8@yO^Un21Bi^~H9LJsZchvUQdN$U`Tgbd+vRzt#f6?gAuSJ}d+tn-nqR~HFoRaJB#6Gzomn+mu(ixWTgdVp$_mO|^9XUlV?|XLU1><`!janq@t=jy8o`0)gZaE&h@r-=tyRcct*N;DMw96A)=HEKpS;g-~sq^5d`jJMw)6AoCe||huwb$K0V)S-&&TN(Wv>x4yG1jx#soC=L^IKz#{v6UrZGYvdM%?;ix$5T)`p4+|g|o4*I*)DIEk@6?og?cxnYYgM)b-`AR5`wSolP<i{;svu@+Uu6*ID^KSNrwQ=VSDK;@@yc)?-b-6K(X92UTS}u;QqSH#nxwAIfe}=Z#<Nj@I*RXPUEJ?eAgg{>_mzmH%!Z%Kg+jIyGAF55DIf%XSXLb&J-w%ej|3M&|j^3u?RbHB|W=c32&+b38bwx4Uztojfl4uS`B`wC{^~RlD48uddf`s{4#qft@GxxaDc8_Roz4WPkHik5}VU%39<6!QW*68P#5s)i`?eL-oDH?Yh5Tko6YNqxP?+d(Y_o#0qqj`LvHEM(Nw@FAy0m^YDFGl-@3$Z6B&U{5d#EZx_$g`*L~v)$CDvKCL2$WZXAt`f0s>>-N3#vi=`-$@6sQkD)4`w_4fqbKwE%`9So_FIBrASL2==4@ABtm)l!Ojswn&RVVd!_q6*(URPSnrmE|?i~ikm`3hZ68gXwkc|7n<{7fA;_cc4I_kVB16}eydj@D7}{)uw`bGp`%?d8U;FXB~xhs>7kWkr`T>amaJkbmd7eLqs)kG$_4QpcCOchr3~_qa@d@I1UK<Nm%))pbwH-RgWkbe9?z_8n5k$G|VL|2ZY?NWFanwQZIEa^oZQe&~C<hwSJ63L_)+cJa2YB-_PTqpw<@Qun!^eO>k&U(aG{`8Ox2@vY<yb-WvpD^l+#zU#lJ_8n?P>ir~8rN4~Z)8o{Ah@SIRJ-!%qzBKok+MmMSQRDx>2XfrYi09cO$A7Q)AK6}>W!p{|{jF;WRsYG}GVTl;aZTS}eEH8g`u6&AkG?4DX*E>ElNQVI%J*x2M~~Z&3&hKMZ%tDBZ|_#>dD_BP)cW7MGFkG*Sb05U_jy@ew=7wv#%<zOokr?>D{l`uZaXVH5&HT#F$LxR8aN#nZnWe65put?pKBJb=h^Oa>w+H77$<kOmT_;%SHkuE!gnP`-na3td;O^1-@HdVs`KZs>KxVkiT#~djkkY(c0~5W<HhCqf_KJEM~~YPb>#Y4HE*f$>Okwm#{M2QJXU^h|3Zi4-=E8*_M3>dk$T+9|EoN%S>O8Aaq!J&W!!GNUgddo;fZoR+P<ak%chRz`5W!q$#=l`UfVD8;G6yXem$SQk@wX&cJ|}_M&1TpR^#Q>clI0onSSDZx7$7=KRY+c{P<^9+Gpf>OHp+{aLbQ-jXZxgUv95Idt({*&psjVyZF9%UhdbvJ$d%%>+i4nm&}`;b%Gkd+;M4n8+AX5c;M%zYJDDNRmYXQgVgfweWaE-)&2jX9c0|MAzs}NiL9uOXH7zl`kkf4)%jDmZ{_utm94ZoUgyrNjuQi8cj@`}_DEIdu|v+N`$?XFx^AxJm*?Sb+-m5%B=a5-A@?Kyds|gKt4pc-5vc_t^|*blsO)F<S#>?)3!L39>#2D`^#|`~<0Z3vvR%)cw{c$CUcNCWw(0F|H*ToLw};7F^>%m4G?mK-stw$#x4U!kri@$dtID{)LIri4UANWI<JPjyYJV$SSZ&u|k2V|qWd3d0PkcvKZPNRLJ#&{DA9Ci}r1u|tNfXt7LPxIuuYMjF6tzy@US~qRII+C*O{l!i@P0i`wv+#-M<?{SU225-y#EiC&yJ&SAJglpSM1_{#qDv8;`DgNacydA*-wJwmi^v&Bkt};$Nn+uck}OiW}NxG?)k}!VdstSb)T12tRJJ-@12obwbxlsv>vxUzoq(Tud65YxV=`*vvA6Nv`3EzcBy$2PQIt7jpZXYs{Q4+r)P}%X<zHT=c4uX^yhn)=h2_NXRN0?4or@U)R%YL-I~#VkFmW?8ms%+M{kDfao^V+)cw4U<Bscb?~|FTf9_cB81ePrsQvbr?@kzb{<HWJna{W<Cyn@>>+1f(&TLUeylQqe4(6_S##m1)Uhdb{?gSYRbjiK8;eYf)Hy+#%{fQ^#^PJ%R?3pxNJ}(OH|NhB2HZ`>VV}GgmnT!YTU%rtK<n>nY{%9SkwN-w9@P17^c)t#;87kw!<AZ15RT&Q+Pdr~A+tyI)&+ho+jGMV#-(GjT@^+3=@u2a|sk}u!CkYxS-FWag=`9f@<Nq3mi3g9vc9Dy_^gO%cxt;qPwS3U{?|+(Ao<{^9FYL?hWIXuz5{MeCmJd1}dBP_d^|;41Hy(Uk3k=J>N6(vkeDob}s_y3n9Z#KsKkU`}gM0i9yk2FW-hbTVwXa;yeMUdw_--v6zF%*5_k6%_&)ToIyL<i+X#CrLz1`jOjX;k62lVyNI6uie{J?+pbGuj`^*kr&{Ks3kpp5_PJc@Ymd6a)-tHZ|kaz5tSw_4sG3O=uM<NrFZ>sR}zksr<voj&!C8hPe?(w9;$+{iQMpMmHm;d(yZ^H~4c7U4!dIgfRw#)j+pbkBzaok~RL+vT1=+sntO`_Mt>;ch(mJUp<kwc75W^LhXJx72tLbY0-agRcwxBcmOCeKPt9@!<aBE74nxgTdD+54WrFGWfdYy9jlkAn5uiBOY{p<iD<-0|Z}Zc~AXwLeF!?by;}sNMk*@j&t@ERp%)|*L}{SKC0gZT_-xTMnvj)$hfYYJ|R-?Kkjv?Gi6$&(Y{=_+Jkngc+hojpxK>By}!BF%eMEvTK}NyYpZMtb^jpfdOT35j*16e*SqoH>v~V#7Dhc8_Xi$LQOgJ2XUK>L-Dhxat~{yl7w-Lvz&M|}uNidTBO@Mk-@|IPOVt;2|HOYe?6k4JbHBxnXFL~h@59UqjWYV1d*7zV&?vp1xc7OS<};%7dffX$fg*`f`uAqsNAmAEqqnbn-^p3C?~KZ)dH>3d2j9Q)E{s#h;h_6qo;K}OKMJ~^=Ej5Xr#V$8pVj-Jdtc5s_`Y1P;QM%<c17iO1mE}bRq7V4Z?Aiw(2ZxDC%ExKQ=|1fXWVamZidQt(EZ84AG@OUe&XKG^gcc!<H7eoJ=bqX>+O|szw~5*7=3-*`>USaHP!eYbU)Vb?;4|TmwR8=v#MW=zJIy*ft}e?V)XsOy>ILtz0HWb_nAHI?{WQY-k0_@`y)p0CmHv#3v`wJ^k4VG-FVRbaBs-?^G5q}Up+9d#Ra{6Gw#n5557O|44ZYqSWoWrdn!Ir=Y>Jf3*7j>o)_$oyQsIj``p3Wc<-W~XZJaU8+Y5wje8g8i8a=T=N<N(Vlw`(=O%7E=(&j#RzB9~Cp>@g`-a6D{g&r7z7{LgeTbmvJHF;CWA*iSp9lG?g~uBCbe|t(&K9S)Z^rYcUyH{X?Zxvc@3(d0^!9R}XE`^UsO5v7i@EWj=VJck&T&TGc)k``zeg<}^gPb@(T~RR8PD&gKTyjDJ@2!}<%~D_InM{}QTgNb{l$Hr=owO4#e<$d`UjVZH}b~wO1oD*vwog?+FhEfc+hiFf9(k>9`wA`jsNR;YlZpoM*rlwty6wsyq*X5Ij=W+Y`oro+~>khrsQ~|Kl2>fjc4>{H~!bnc)fky=h5CrzZ%QC&#!%Vvt82bch}P&D0oTlKkoB!C+$TU4}P9*CzraU_e1yjyFan~C1ZPeUT>XheM#>p?(=<X)?s6LcRqlBLZY#}JAc62?xh5Md);{mZajD%g44XRj0ewi$cP8cbFiA!NHEr)`4U#O&Ix+^y7ManuXRl@`aknAoFX42=<Vyy-|*yFnxN-7W4=eWb>{cF^Fy+1FzaVNi8sr}1ic;I`6q5X<NTAj6|&ukyYpD=rw5FB+<7n7Z^sh!_I2mU`0k%q@!)wiDUXcxbm!st<FZ`Vw=3g(BPNfG2hab>hzHI8@t-Pk*=S#P9??$kW&L~Ic}KpD9gMg;PszJv%w@g*xbvEv1(S{C-FZ;<_)TU#%$u@@hZ}Kso|QE`Lak@eyexl@fU&$gkIUcfwi##Mm#_UpbGw))=571fj5Dvy)7(ll^20ndPvg);y}jIdYfk-qYWbjfZh_azB<lUsofqenY^>rz^XR-eM<g2kgn4&PmI*Q*JWtQg^nRk=-`sh9o+opRxH}Kfjc3g7CGNkqFHvttcRrz$6s773nwRLtgXbkWTMJ*2%LmPGbY^!|@u2yT_Jj#nj6A#ZC;P3xqUX(>Z|Uo^MaF~YXFBaqT+#FI&gb+sy)5Iw^FMtJuc`Wj=8O8O{d`4lmyG$P<#Jrr+r^!a>M2>^s=og2{8g(!#jAS$-TAJ8=PF;-^Pe$4_RsDz9z37c`$un8f6)9}|C2sO{qB5SH}2N&#_d}(R6W7-es9b%*592c>^l{1Ebq=YcH{q=Z+!feT0UsrvS-h=t9qW@dCs2IS(Ehk&6pRxuxOI8K8z2ZIi+Phc;2;lT1^!Xny2j_*DlG}ADP$f^No@5;CbMIK9h~_b?1%SJ*Foa`ziCx-T1%erFWZ=WbD7pV|O|%H0pQfy<2UUo7?NoldpX=NpD|wUcI+^WRj6j=HUmbolG+JYv%3yDql#_`;R-%-<KyeS#MwWy?{XO?8*A~y6+LV@r?1ujsNzlT0ZD~1nZZY$$I;`?=LukUgr1mzJn)WjEV=nAK{#un`~?^?^F2pZ%WqN*M0xOv-U!=o`3g!4gcyy84rHH!&;e=thcZGK8SyE{uDhA?)xLwxDqKwKHc|C#(Glp{J8I@_(zpX(bwO7pT*y=xr_(D7i0BnA>+aC(RexxRNou)-i_0GSc;KP-qW!fPd3&+<9#3E8U2KKAkS5!9{0T=Pp-5SJ<slYM&2AZ&F$j7B-?tZwkzm8CjZkXM&8`_o~);TP=C;SQom$N)$`!KSLJ<}D^+hV_dP5-xmK!?Pu}P9#Wz>+p!dJL=R2h8+v~nB=8fr;s`hX5{W9xp4;2r3AI&-4C)Mbmyuao<Fu{!T9-O_~HsbDkbN;y}&GqCxJ2#&3y~M3KQK@=9-S_o;pPV!D=Dy$OnRUU~UiW=K&xCuadi%QX4+h3QF!JfXhv<3tajMb2?t6>9i>Ddw!h4RM?q$=AJo8?pQ@3ZDvArzs)ak934|*Td^XiB+BM-d4>3v~onz29fzNeFYukpR^`=No%;c5E%yYG{F{yLLp^mE=zwf{JuX5@kQSgr5BGuNN>apV75&+mRT^TYeIf$M*p`Qbg>jCjy{xc1p{*Yxjo-}CjJu5``Vzc?QGk9e=?>*Ky(?Ah7vnvrMTNA_;%XT;t2m+j@YxjgSd`xebHm*>4{|HrGY>D%SLXKl^&8*%r&Y-`%)Yev7~J#PP$-PiPXao_v4N1rkB;J!cZ#xwFyJTU0GkstRxbgTcj*YtLA-&^-IEP36?Gw;QFtJJ@)*W<oN?|=36>&Ex;-n~=4xv{+ap1%D`%j-sdc(316y7P6TAM*PEUQaJ$`HbHaC^*ch-~IgoU*7R%oZl;Ovdl5-=XVl3S>|5X^Wgrjg75xrBkukVL*VXFV}0D;ZE(JeFqU_J=OOTQl(D?~yAa-Mm&`oyI}&a@<9%V`zJ%LG-2I&jJNA2{9`|=Gd}n_*^TzLB_>Segq1WU7ZiY8J&kcR~jNjQfSjbr3{ap@g`b1-S_jf$3DPd-u-~DjoZao>l2Qqk@vAp~HA#U7V-i>?v9X8jK-yw118S5$H9gSaIsrq{Sl!^5$OOzZ|0c*$r?I%}6Q2giezkhP&?dtzmKe_T+)f%<`|9*2N=l%3`xSC#ag(&`oiz570=m}9Sitx^`72X*i58uPb<MZHhTyPgY4_{9aehOa3PvKYLL;NcKJ<Od+`S<v5(1VL2JcQV5cnF>eR>d>nzlSK6#6=PQ1I&YqB0LE`3Q;bK@Y666KaGC{cjI5-GvIuD2L3*rg1?XVg<bHzczsv}ua6glx$$CnPWZr5o)iDoQoM}+ihmCy@$d1Qa1VYH55V1c0KW%M;P>#yFadvz=Lk`}kBcI_C=~s;C`EWZ_$pox?*lvIeeelzJU#*c2+qUj(RV+h2%kd{z80Rs*W%mZReU>s0Dg}jz|X+n@H2Qc6#Y1w&%$G1CR`NZXQAlFXDPxD!XNO1_zswa@4&x=r|~cGx$rA|F8%?Wfq#HchVSE(@j<XJJ_zpy>*L+<hOijk5U&Pv;??j9Q1s&pd=~x!{2muYctLm*7e)B<Fo269yfD0niz2){e2j}Cyebs^xGF_>16UMqfOm!U@UHkk*ashoPlOZjiTG6b5iU3fpNda{YjMHtxZnX?@C+^(jSI%$f@g8TgSg-hT<}X=a4tTVelrP9#wXK1Cc$oaH~PUOSPid6dryKd;4jdwli>6C^R(Y2SROA=J57QO@CLNUBsdTsNZy5qrk6+Q?VTw^72!Wyins8e@jLJ$eg{v2C-Eda8g9p<@l$XWehS|O7va0`^)L)ykFSL9;VbcF@Ev>^J|Dh`&&OxM-uNth8f=eG!>7PD_!N8sY>Q98C&G^SM0_gjfltLhgg*R3{3G}_{t-S0j>hNUpTf!br}%O>6JL&hmR{DuC2%Ib1h*-|N5IMW2z&q>jSs-P!?*G7cuVNRTjC9154-_h9d^X4<CS1ryb@j>w!zEeufX>BD|kiN8?T7hf^Xur@TTw`yeZxVzK3_g2f{FXAU+B%!bjoL;VOJOz7%f9m*Q*TNqj9H4lm;2cnrLS$KYSXNBGzHFHnpfzwlXjc8c&)6yYUcCcFe*h$8%VOHqt9zf*)igm>_V_zy4%{{g=NqwyQ~HFyfYhR4HQcsza<uE)>fQE(+5g*$K=?%+q^eEcZB7tX@>;yd6pd<VW2PQkb08{q_eBmNbfh<}A|fK%}e_$K%vz6sv~Kf<@*+u$608@>~Mitoht!R7cq{0RIEKY|~#{x=>SqX<8pUe3V%a2>uM-wc=FoADLU##i98DZ<CX5%^eq2poV9!F$5)cu%|)Y>BtR>%#_keY^^+j#t57f|c->@E2iu{6)MVd<8FvKMyP7&*Md5ExagR7B<Dp;&ovcye{4Z4#b<_z2GRk7d{M5$A{sQ;8J`Nz5uSp7vO7PIKBoy0Auh2_&NABeh$A4f5C6#zd<ps{l;hEc__kPf~D}6@ER21bzup-E?x%~!t3C*DZ&dtF(ww^v+!>%#fP}y54hkBT<{t$7>^5{#Ra2qK?fH+iVN<=1$W?rTXDgSxZqc~;09c96E3&~7u<#m?!*Q6;etnS!DG1KY1|znzNHAiP7$64_v2}JGTe+O<B4zuo`|Qw+4#`(c4?Ph+Q8y?8~jCz@INfYr<QV2gr~w3JcasGDZ)R7WATsiF>nYz2Ja7h;{EYXuod13Zv^Y(jqqx)3SJE_2VcU=;f3Ifcp*FwEQsg9v%}}{?06_FiihI4U|BpDUL4lNi{r1sCirW3L)Z&%h<Ap=@Xq*9I0+w$kB1BJ@%TKr2A_w24iDg;;|Jk6{2+cF-p0@4-@xDSZ}2~%7^nW^v+!pr!b`)K@X~m7SOc$)H>L=00_);U@aC`%-W+cUYvV2P78K#H!2<Ye_%l%K&(FZ?xG2K2!8BYH;hAAFE{gCFn23ua{BL3@xZqR#Z@eV?uGoi5QiQjM?eO;aa5xknjxUBw@Wpr}Jc&o*--_+cr1%|0coaN|N8yX$5_}Op1P;ZAGENPl2=4%2#5>?cpcu1?@LBj1itsBi6&L&%zk<(zWAGXHNZ21AiT8z_@V<Bp*a&Zd*MrsYdicw*9R4z11Qx=J;8|fFJS(0VX2&z*AutpV!7Z4}`rm)TGr{6`Cj1%r8vYDk3O2+`;Wc4rye8fn4#ivJZ@}^R8~D3$9{w)=3H%)Y1YZpg;;Zq)@H~DPkA>ghvG|YhPy9zbYlxy4v$9fz=ZB^7{CH(p9j}bP4jbdI<E_)ntn{RhOE04+!h66zcn`ceY=Jk&E5cXsig-cz99|IrGeq&15apr>zXQ|oJNPAd0l$Ptz&&^bz74L!x8YyFW%w8PC-6i36Z}m$7#AFXzlryNt?}06wg*LcPuK((Y>xND-+(RgH}HP21>O(upI*8{FKmGezJ`18O7Iz6FdJS8e+6d7U%|`55WFm228v@t8Ca6ID8k#q_IO+T9XK3+2mcf<#swqsPjQDL{2TZ!{tX_Q>3_$JP>S$3V1N7#d@P)ZkHu%gPw<)eV)!|}82=J(#J|LMz=QY>{17~eAHq+=%lK(L242Bq@OYSv$K#h^Dt-yS0I%W~@Z<0zejMKgkK()Vb#N=b4*wK>hJT8G2xsAfqwo*$cPPTU!5(-wyeVvsH^nQ#ig+db1y~S&0slKhQH()<Q-t4xckp|70=$F^M&JqfakvdXj&Fru;9K#}DZ)R7pWq+k!{D2^U=LidCocE~J`8^s_QT)B$HM;jSbSW_|HhYb6yaki!behs`zXR2K`$;?32%gVg0J9$W${jUM_2|IY>RiqN5gmU(fCsMDK6;XOYv}u@Z0bk{5GCFlcE?qvQvcjhHv1#@iA~LJ_fhpOx(uj!NvGId=>l>UxjagJMazoZg>dajYq)Kcm(di7~H|5U_2g$pMjU~Gk7GtfJfqo;c@&hz6tKaH{pJ`4)^18;ivdqd<y&!7kmewf)Any?*O~u9q`7mDc%?_3oGGe@j~zgyb%6Rh@u!f{-Fr}5#Gap#FJqHp1>H9Oc8zzZpDw`8{p^o27D#_7+;Bp!D09?_Wv-7@ab?YJ{_M1$KliP*>DU#hOuBaMYv57J_7o1A7jA?*a;tjkAfZXj_li`D8d)QrT9|z=Y<sEM=8Q@!rS;wJXa<~v2W+12yY8}<8AT5a11^ep9F1u68;gKhkt}GfUEEY_-eQTUyZMayYcn-P8fmj#P>o6-;3{uQTTrR06c>q!1uvOd>_6A9>%xeYv3k)4ZaBa@kMwToQsFy6W|nFa1cHL??MsY3U<I-;Wc4nye3{8mc@(X1z;h(0B%9CZ@U+(!hd3a{}KNQPl3sJGW&1}MfeH00Y8Cnge&ol_zD<?hq14&pa}mAPQyRL{ctw!$Jam`x7iQZP=qglqwrDeV+-I>d;xxlBK!utiQm9;WKtCSTMmlwy09%?7w-rM;~jAyoP_)E;qW7TI6fXOz{lfL;c9#;J_D}DXW;YUPJBMT1n$L`;LG8Dd^x@X9>7=N%iunI89oPY!RO%9;Tn88J{c~;C*z}G7(N;w2q)lzUGRZ;LyGWfuoYenF9B=fCGf(qI9?df2@Bvk@xMY8E&MO`zxz<^Z}%y}126?oVZRDcgr9>O@pJelxB_3n{<Dc9d?)ndJMn#R4Zeo`VIMq%@558!4LlXkmPt|U57{WfE5o{YW!wup;$FNp^x>`Xc5pb}4(|-d<DKzda4Oyl9{^|I1MnemK0XA03ogOm!bia6_y~L?T!D|o--gTZxA8aO9Q;kZADoW&!@I-Dcz3)#9F4cf+rWXiU_-nOUW_8V2&{$|!SlircwRg!ER1KxGsB#CX8hL>MX^8pN)i45-p3!{cVPez(C_b3grA3-@J;mZ^AzD%;68jGefJ7Qc$Q3xqVHy*2rmjN<3;fop%;G<FAZDcrSX?xJN#w*RoEGS6|W9^;nne4Z~$HluLFnRb?|!dExaE7Ivjz&jyHfK@dkK(_%>c2uMOYCYvVOwKfDHB1$M`);N@U@yd3@#Y=a9H!(YOmhA0-ni_k}f=cQi?&q`kuo|*pmlz#XCe?Z@Q3eV%`=_^lR7V61DpAcS@ejxls+Fp2R+FSU`w6XA4X;<OZX-na?Xg}d~XfxsUXeZ&X(>B5z&>q6;(+0w8lXu}Y$hGh)<X3oNI?tz<ICu_^!%x6t_z8Ru+>Y<Tzk+M=ukfXCA-)u!20y^3;qSs>_`7&d*cI=IH-k;^W_Sfy2CslW5A)&A<9~!GJ_%7Sitw-DE&OXd9>(GE_>uHdPShp(Ahhtj_&=87T}!zr!oP!Y_;>gP7=d5F4?#bE2>${u#J|Aj!uRpH_&E3$J`NuYyWxZJ4zMxa0e>CVz+cBJ!;*Mqyco=j7sGSF+;|Q=3w##Of@g#I@oacbSOU+97l0M;0(j~4(l5QVOD}^c!n;B*-W6{KtK!Y@I<Pcen)>TdguhA=?tvw65B>tokH3IF2cN~C!}G!1cs{%^%!?Ps%fOO&8N4>Ef!D^H!^U`XybtV#_rZt5xA5Wk2k?FT1AH-Dh%d&!gns->{5XujkK>nM9DWJ^3Estj!n3e1ihVK*Mfh_tAO0L(ks|zMSPmDgiNB23g3a(+cvILLZ;JPVZ{fZ0w<*GB!I}6hd^KE!ug15)&G;7lFg$`EVH`V55x$=yJQm)<WAW?o34R^_8H%y>XFdymmT|WX{w!V!Ho;5bjbK;25#9+7!#m+a;RpCo{C&6(e;=O>*W$DBFW`3k3w$#?hHu7?z;pN!{1iNopTf^lgh#_fJQ`0(FDWn$CgN#$5{$!>@K|^PkHy2`9y}c12EW3$;Va=%d?o%doQ8jlzX#vN-^2UDo_JrpC2WSb#LL49czHZOd>+q_KMqk8$M44!;n(2T_%-|@jK?qHd(%tDHX)e`Wd7evyCv?ANUohe$cv)S4-xmF(yu%Rj~VwiZ}A5IrTMzA{+Hv^>&kffw_}^E;@D+nO8;L>=y+wC`1F4OXeMk4'

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
