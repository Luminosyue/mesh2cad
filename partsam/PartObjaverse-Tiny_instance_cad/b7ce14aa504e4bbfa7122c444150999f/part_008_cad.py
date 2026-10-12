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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_008.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_008.stl', 'source_sha256': 'de490ccfb1a14a348503331c626f4d7f23333d845ed86aae23fc2b05c57b7831', 'input_faces': 758, 'input_vertices': 760, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11855757236480713, -0.1337881088256836, -0.01779695600271225], [0.08339802920818329, 0.26201146841049194, 0.024754181504249573]]}
GEOMETRY_BASE85 = 'c$}r32UJv7^zH{W8f#F{80*-v#uj^Ytg)b?qK4SUf)yJG7ErH>6|omAiHO)c8XM}2C5no@C6)wx5_>GMMc=+>e}^~sp8M8%>;E_FTl?F;v-#%EjKa*Fb4fs}jG26G{HK^LFmq(A`#YOWR}P!6Eh0E{#DLzxVU>mq8|`KD7F_=$>-;tyTL%Pr*&=L_W%>k%^$sml$6lsh-&$oV*vs@C8ag7h=a3#lL;D2lyjjnXuwde0{d*1zrrxh+jmj15)yh_|kG1~~|76pT;bhQ3mtNl#JtXS3=~G=+JhahdOFl6n+>$SEGTf2}Tn}ns#pAQ}wd6j{Cs^{p*^_jh_Rz=j_!W-hS2&Je;W&PU<M<Vh<5xJ2U*R}@?dHJ)dhaN9$|ZQGxM-IZe~>y+<m^gf-YJH8az8Pz@Ne#kd0XRIg1f)FYRFgklAU5cKF@g030q*uSGdf76v{cZ9en>T6yba`FI-97Uw3kE!L{K3M72%LEanxyr@NSsuU?zE)1PyS*5u<cbL2ZRm1Djz$3f40g(KfK_S1gRKW@VH!R?7IE8b~hv^akMXQFrK&%nG@l9*Tc^CU5!mV8+Bnom1JzQU0oAG1UBjt035`3g^5D&}p$Yq|fo&pv)0PxA4bxjg>rahy}36!VWu`1s8n$M0S>kndOF;f8#L%i|C0!n}QzeTL&VbL87vw`G3$_#VM;J)PjP;@!h1i~K?kK2ER6%$vEyyuvrdih1|Cf}HcuIYYj}y}OBd`@}E!ar2vN$X7V>wfgUp`QLSe-J;(3pt-Dg&;C=y-_KkR1$R`mF>jJ8<`uq06Z5vj6N0;o_#5&S?h_#9-C_GUr)5?{zQU2Ol}_NC<#T=(JpY~XE-T)<%T)3Byq?GR>p}qYs3bA3@Q*QK-ZpbM-|ms+%zw+u$8YAykMGh;aP3W3L%zag{_l18c5`3YA?l@dQ7$X~Ax_-iw9V!De$|`J{HO24yuw>-=f|gUHs%$t8}b#7$J62Sp8tOLUS`NwIP%kexh=Rm?yDrhYfO%GS#d3oxWC$pE1YxYx9y_ZN{V@f=W8tHo#m4RceqL!@)eGJ$NL1n-M?=e@)eH!_@&W&yYB+GiQ3CH#%0AHT;k&&7|#6byv!@C811s+6F-|Kj{kLl;F`UsAz$Ihcb{#-IsQcq`3gtAV`yp4iRiXjaQBT-E-RjSyqJ$~UV!<no0|lm6)ENw9=KS{yDz=kEBd41hJ1zZ?aTK!@jml{&kXqrN4{fj8uOd$Hi&9J7U8nuczm1#FA1(yFTwopK4M<sczohtZ)Kh@*^sYrnSU&v`GmU0d^1PBee^Uw&Rp}?GUwN03diH`Za$j%XdmYO4aK~|@%Y65-kEuqjfQ-M<MDTFY0k%)RLYRAaOB&@)#jWEBNIh+bP01=@lG?Qi{oisj&m0MyGrmi<;1+gpYId%&O4toA2pkEZp4Urg(Kg-<E{Alq@Bx}=$WtZ!~`*)*8ErgdA9O$JRk3YAucP9c}MY7=Gi+jcfT9#vf>Rcig|6zTINq48}bz{^T)+8Z`$9OZ{~P>+=a(5&$E3gKQFb!yuxE2^5gk<AoIhkmxx;EYKY5<`xTlYj(>DB=2I?n&a@>WU*X74YhQ=?4_6HN3P-;4avtVY&(7!PcYS}C6(3b5M%>>mnVF{@nJ4P72mM@D+~<3quXCG!-lu*t<SQKcTDFVK$GkM;EBsgkF`stq0P|rXGepf)O3W*K_V42U#xL5!JpYhsqAuvw*JZ`aeIfFl6=Inuo;Ktw9QpPSW0_~#%{i$@M83k2?^xZ7d5Vwtxni5SsF%x%M;4eV{=J8HV6NTg_r3N@JzZ8jUn?>1&Q_Iq+-gI<!jZ3CE6)7cx(LsFg{M>%^J!h*@8W+avHZT;??ro;6|a~<%*R)F#N1gdSnz-$?OawI`Od>9ncJf~dFCq|`L=n<%;T5$_RLo}@-^QD%onWS_xbiJO<h)eV$N9ceBF&^UT+t_e;Zb&k;{q~sW0Z8!<@{wbu#2D9Qp1Rfy^^?G~_EB`PzrN%zyoBmgl^}F>g<;z&ziGIf83->$|M@&LLvn)+;;n#A$|ng(E+{$_IXZoY>ZouW;mR8_qNL&be4{TXb<tp148Wj$_PW=5=z!3GUud$&xp?&d24wl6l09MV|QzN51=yxy(}@EcVP-IP#s}_hTM6;wR3(mEV$gn#cK7x-dT)wnA{nVn0j%&tWm2cAy6H4~-4^3P*l?Y#HVOZ4LPfN50eX1#b6pg5Y!Rwy@+kKh73^f4ptXgF3F_{3rfaTw9o3JkM#Xf8Qzi$ODFah0ne(^5etLGPgH2<eRz7clzyS9_Y75%=<NNZ^gC9KrwHBvzGaPn|a=r(!r9S2odw{*eT2l<TK=(xy;wPjby%Up&?)4$dCW4J@auJ*9-pr&7PLL(HZgh*p4(~?puC?=#Q@GWy$e;+1eIoUS+-^U*X8t{PHnBp2v`{aO7*}-|_p&Wxs9W`}?4e6_<~XW938Um4h~m`H=O&mK=|dt>#JQtq&RU&0OZYGbb~@?J(pk9QlqTtC`=+yiM>XmHJt6?c2Hh_j%qT!L_|Dcs^=&KT967o{z^boO9;9-|Crf<}%;$CYW>PeQU^9IP$fXEjh=rYdb%`?*>|N?OwjQ;&#W>=N#X+JimYcAWL5DYcZdexd8JLn+^G9F7q8}Ir(;<JTl}f9Qp3$Z^Zk5EnBS}p7~}j^KB82m|q^b!!uvu$aiE&VScx~A>YhpzIHvC`JN$$e1*&7@3)xw=*K$+_dXM9#kI8^`1l*fFmGM?XVEwNI?R&48YJfJr~5MRde@L|<}zPf^8=qxDO1vruW;n2^=is|%bZ<;`yL9j<a3sb`S_|en2$ckyk+qbR$RNeQ_MS4eEB%1MjP@Kj(mIEXPndZxFO%nWqw-A$KrgDHY(2^F<)eDxE0s_&N@##?<H^X`J>hyc|P#-2rI7DDlX=o+xBx#m#l_-Gne`9>D!o>Zehqb^Yr|nm3+Ik=k68r?em6P@+oyVzv@Efna(qx7!hv8wTtb=yp|Hi+-I^OU*X7i#P#9hym{1+Z{{-JnWZN4S|gIhykG1{E3PHn<>OB)$2{k5p6~u-q$Pj$LCmLxWai^6G{}%|<}%;W?43BjrrqCQ$X7V>ZEtV!`M7UCKOp)c`ywrQ^O1b~DHoXMX~jITV3Z}FKbs%_?%SE$KkfI-S2*$=l@gdgtZ&FyIPx7YXY>8aGUK4&5u2kdd6u1GKK}G1<~LHAugNvml6Oqy`y14Q`K_^re1#+5UabT3pWTLhg(E-hULC$)G2U*$eb0}z<aoXuu1cIUtTOYKRmWLz?c2Qb1#gv&`N(XBe1*&W79Y0i+<mLOG2g^xzP9Wa!ELWD@cfwh<1BehMLwQ3n+13Dc*#8J<v2@zr77q4?IXC>_lz;$%w_&p{(QUsPmK9yj(qpHf_%T?)*j-2FM~Bp9yd|U+l&0SMI2|w6U^WKs9ACC-crtQu}^UK<dw#JGe^GduVu`i9ya8gxy;wv4C33}Gv=_EyM14?<UhDL|A{~I;>($j`f`F5*VbO;{I9a{?Us!&=9@Y49jVX7`E<t@iwyZ@F7xf#e->P8?|($hw^%>Hifgg<1>)c7hDCzA_YdazyT47a;@b6EV%~nG1E1e-(9D=`;xa!i{2RXA_5BR_W-jyNpJe0P4a|2`%$F(_ZOQxjih0|tN8<AXN1YnXliNjGacyS>&fmM9c|&hwzKP4@w*|!r?k-)~m~Y}T-<>^-a|)l~dHK1siEC}UiFwDyK;{{q@O<o@XiNTMI3NF&+<d!PQw;fLu0;&s=PTmHM)ACi_{)&5@S_v>`FfHfxVCiBFM|8|PPXD&?xlP@E4K;m9>0s{k2INV$$KPm{@#9qJEqQI9$sOx6;IC(Y0LcicAm%Q+6qU${X!AkZs%iyH##`klE1ml#}l2IABW(P%x^xKY{j*v?>Ya+1LE@@Eu@_>-^^ux+tq@*uY?-&O<d-?Q^qh)^*-)7ukes83-#)Z?8Toy)vU^VRM9C`T-#ez%%`m>D!8M54xTTUWr`(7zN48J-)@Nt%zvpl#fr;(_r`PU#qFNG#`CAkO||58mxy_-`yS@CKQPDV=4P%<+s^qBLj~6ySB&{)-fK1Im+j0srC%HKO<dc0K+M}t)Dqm0XKsq<3)h%t#kCye#d$t=q+M`#R1(kQb2o+m(3sB)F1Wf*+-~$tW4?)}=Qnc+?ijGim~ZCDcgIZ=Tx&D<gy0vwr(1EY<r98>YYpVvtscwsLmE!E<Z+ofzjqnVsoT$(Z{q3s8M889J<XVJ<}$z1G4Xk%V?wi&f*<ssVaXjc#k_WFv*23azRZKh&amXO5;^~EAHm&&9mae!?-$4UoBWwy?a6%Y!WmXv+qsSNKjvkgJMSqm-(qi!C7;k%%saOKw?^Erf2%W3`zywhr}h)`X*c#U|Cq~=uW*?kwOnv_|H{UEGe^F*po8GHLGPIRZ<=Yvwd?yi|GT=(FBeP|^AB#!wB%(k^WzixX0>=;ZoD$&n|XSEo@;{J4(B!In>q3w?SAB({1=#i^J=CQ*V^9Ve~+0abIzm}Jb$iKtQFUOe9QS?H)1~Hv@zerwTQ=@f3^hQ?$F1^d^11#nfM&QS^b6hJX<Td;<VuQDzmJ()^xm>cVE23JgbZ6lY7px<ntGE{-?S8d3o+7#(Wc(`SzsI%p><1@)eH!_%B;9&*nTMxcnT!#I>}od^{&BGk-ds=jG=JW?m_U@9(R}Vn2cQI>?Z3=318h{JF})v&@~5hJ1y0yd>tecR%rdg|gMo3NFuMoB4l1;&UO#<|)kQ2QtTbY%|wdhKhOZmv8xYmsa9=d`_WonLnx&=V)y>2cJ_YT;_K=nIL#h?{lKZd0;cQmF&y;S(5~J9JVvZd0;cwhL7X?VgoqmSWcer^Wz*#F7q!12(IlZ%slDmIaXZeJA8aOXWMw@+IMp;xx;&j$UF9arOw?6vpN4vkGYn7mY<k+KHnp_V@;GHU*X8tcCX=_Q%4QQukf;`=UVbg?s--`{r#YM{=|rdmR$b4Gv`eECeCs`Lu-C~<}MXn>k?~xe9Rn=k2_Z}WB#v)=2-H!zs<Gc^8PCGXYS0moX7oDIDY;rIa?dXS<aUY!twvf@3-X7wQCt?SaB_(KR?cMdy3cB=|4BI@5Riu$gceQ@J<N7{*^zMk*{#vFI)aIypL7>+?VqvE|14n=n%i2m9ICJ?w@MOD>dQycE$PipnTmT=gl1R?o}1}{>j%xa-X4@cMRbCQfvA3nta_Q^UYl5k4)m%NAh(YUT-UWz7M}Xd|RIP>B!fU*oUcbydSao*W`T}@^vZl6^?xE^frF|B3}<9U*R%;at!awkgu!p{@2Xq`%^8;XZ-U-zMjAKKH8E$jK%o`Z}I&;{e1!6|C)Jv{`Kkn^F+QM!SR^6oVRWD;?Ftd`yIJ2-Nfbj0e6e4{QXS6Z^Ax&GneNpw10MUj(oq?;8e5~PtV`+lDT}}C(nnNxXgF|*^$4m$oHE=YDZgfdA`NAVIKc{kndYDZ|3rRj=Oz+K2I;-FXMcUnalH0Hs6l?{Y<{^miZ>0e*P!<HouOL=ey+jZ8MkW=R5gee+kZ~U5kpc<i!T@?Uh>1-~Z(KI+<_gGT(ife?G|bfimCBk?&~KR(u~#Ki`=7%@|95^gsT2mvJV4-<9VrLynKJ<d}DC%Dq%ndA?NUn|S)?UxV8)m*-uPuW;l$Cr;;m9`bWZ?DtT(+>du>E${!3pNBdJw6f%w*LMHSTz;<V9oEK@WB;Kuf7V37<>$Hbc+4F6X`k9Lm!AvUdQ`RKcpv9%J&?KlJR19p6ps0{>N}Xr&$VT~nPdN(Ht`g5`FT3>6^{J)tgi)6|6E?~*D~|$!Q$sZ+5q3xB1i5An3LdeS#i8ikFVdEx!hME^UWOR0c<P6SM%e(%aE^dc|87`I7jY_a5ib>vf^^T?vkUNBllxeKH=}O;&OlTgq*y;NABy8`DTuM$L;dGzenyT!Mwte?~dxqT<%M$?CRvQ;@E%gI5~p3+z%5!p|i`1%kxg#4=|VeYGl5d%l-VHE;E<=d1Sts%j4OcW3A}rzMy9dy1A@4UWaHo%QH{kkJP!l%ZmFa^6QG*gPF^HO)}riWqzZX%;ml*%qtxE?sAuz%Y9j&XCL6Q;^zwUdB2z!%;kPCM~IkLIIb^n_o%T>^m1RB%r|qH?+#=x_p`}-Ge^E{NDOniUk>}v6^`p`Y{{#b%YAp)Pp<H)@A&$!Rgaj<{eIX_u5g+EEE7Mza^Ijl9y3S2V|zp9a$jPfB12tP9M?~|KL#<E`yMf`aCtq{{RG@D_Elp4zrtmHwPfaU-=@qrbIfZU^YPz5xi1vgM<^Vx)3k(2%;mn*QTut`%yB)VHe)1nxvv%1cPL!uU!Bcd?wggzW9IUD%<$3t{Z3vNu;40RpJ?Xz9NBhdF>`s{0p=B+@2Hq}Z@9)>Ue|!@85QndYP{&Pzhy43n~?ctj^jytTA06|%Ih);H<{$J;@C%FvsYv;ulwlVRm>|q+e5KW!#Sf3b9r3}@)eGJZC^L$^12n|D;)W0CCBsrLU~=xjJJF}wVC5}puOWP=JL9mtGUH><qCKBi+QJOD|2~W5Aqd`{P?E_`8efuL&#S+^0l((IY(ZX)FnpDE4)^axWA5oo17!Bds?$f%qu*>kN4pm_2QrR^13SID;)XSOK;}#x-H}@9Qp2sWqJRiye@3xqA4ybUNvmAc)o_$VlJ;cd%H!<D?F|d&)@6HTwd4KeH_o5Ir8oKLijl4b#pi#g(F`p8_HZ>m$xfwn#+nG+cru(zd;k2%j^C!E)??$FQ<*-K7o%@URQ{Gg(KhoayxT*-6HZ8j(m6EIlf(aU1W#&=`JfiV}RI47aw_pbL4fGEBA<bg+Hk!=ABP%Ng_vH*NJ?EBVQ}(&0JnLihPA*K5cpx!PBoxU9(YK52WzB?ZrMu+dhZj>DRr!Ji^xxnK|}7I!pHA+m+YVB46Ri*8+$0?aJ$Rk*{#%yH`%<9C=;vyazEZE1v86aB+MW;y6cMcl^gEF|Y8@4Lo0OA9HzKGx8O_Av^Dz4LQNLE3cbIzQX14{QXSu^y{+sjGX1N;y9l80ygpfC;htb%yY!N!hant=AE-j^7|!uT{-d<j(q#il?6|~ZXNjwN4`CWKi{srF1~o3*)A(yr_(TgJiBm?yzYKj``Iol{!=M2AHODwbL4gX$X7V>)2_tu{gS^o0Qm|>zO%qe=JNLvJU=Do6>iHkL_8lYxAAex-+R#Du9#PNYQkV~JUh?xamwGTfP94`-*zvJbL8)BK)%9}Z%g?~y#G)Cy&^R$^7Vyg?!BP1IQ}Q41ed?JMC(>t%$vDw&v|iOn%1i&=g8lSf_#M|-#ssgIezbo%r|q9A7J?HKeL;5ZS;9bdWS*EYV)=A?dkEWe{`t-k=6QF{|u=9|M#nZzNz)U{nbB}GtiGbQZ-U_(l?|Us5RkrUKvcURp6^(y(WBB^tDN~NOe)`z}F*vORA6B0KOLbdhoT;*Ts4R_&Vt4lID=+qt1h0Kw3yzgt{1h0p=E>&V`?k^~Lb>&@Umyk(Qw@h5wQC6KOg83iNU4m%}gdSYL*jWysO}N>V&&6>0)}B55^g4eDC>M9i&5UFosD3Nx#aqx*HFjimMP8_;heZ6<9&-3q@B{U-SJ=r>}0EBprZ+ezC<J5ZD0canZ4?LyrRzYYCP`0eO-V0|}y68b%)WYS*vedza-4v-F_y5RSq-w(eReKOWv@cYmoBDqONP!Gc&CH+D=hI$;{js7V7A&>PVm^p$R-G4>OPb!F70KO2ZFsTS?QTRfbD~$RTd_k-ig)e|UH_4migPI54mz0;35A{oUZ}h(Kxjoi>Fyn(9-4`R-NhMH=!<QtLB9%rh178wzrBI8(m%w@%_~PjONaaao;me_~NUB7t0RJ_5KlByg%X+Mr$4q(T=>7yLg>(w_Bz!9AH0ccLS@=}Uokl(3v3?3Or;wxj^Q3d6i>MdiFOe>juAp9pzl6EVsORA?V*M)o1@ym>ekEN;y#{}Sbd&Tu>L2hoFn1I6H;?t}n7NJ|-QOamk?x@0hQCX?N4k&t0RArK?xEiDSiggrJIK-fU!*@t4^jVye?)prdV=~C{!jFe;Q#Vie~6if$kF|C(lgQv)PLY#l3tNsqy7v34E;;^=N{`XF!KUAy6;JHl6s@|g6~5LCiO+_2j2&C!Kgjqdt<#Hd@u9^Nc~BJPzS<?kOq^6pbmxak3Ix`fXDhE%nU+~?uV0xk-|_z;YX0dNfD?c;fJ9g0Y4ml7}iI^hoT=%8byjk9RnXl8cQ07Iv#!$`Y8C(=p(T{9)1jZjWmfg0e&L-$)qWyX!xlfy#}V?>n7uCreJOoa`b*WX&Na8bq4%QQY>i}>TLL#n2SZ7?y(+&nHc2gz9Gp$YK+<lzA330sR{gd9=!w1fv<0huW5$4#>mlo8!02n3qAw-Or+09nNhRAXTscPs9x|Hv7QA!1NwHP08$6k_V9tEj-*bgo#6w}2g0{Q-vR5L;oGARB7INlg8Bn|S5h}pchny6T`|`UHOOPV3ud|?NB3DtpOdnqW`oZ`%1O$F`UQLr%;iMQ3ZEV8U%+QW--6Vf)C#pFyg#WmsSRpd_~z*S;ahmDx57*-<mmn&Jx%(1i~Xnv;FC%FNPAKDz`M{V!yiPyAM1PI51`*g+D+Pt`ZN3vQW9x9>NfZtm`g(4<*~jKGdq!^`z@rcq)n)s;Wv^tkk+HFgWrg`4X9f@);D2h6LNIFhP0NHh`Jhn6)AzV5;Y!vE&5gPYdqEyF_VZK-Ty>dL0XRbBm6SbQqmICIQSLlm%;z!vA!HL%aNn|MWn@~1*i+*=ac4<=AzDlpO3kDsEa(-7hq-qa&(`Wl!f%ti|Z>d_PNM^qWXo6{YNkEb-e<Ag|Cq_nK73cdAiR;{xi})UR+;zvCl#NKdL!x>_2#Muj>W)3w({7$%MH~$kV<4Z7L(_nHSgRUhMVXQ~RE3b{qS5Ufk<?4*ncpBWE&TE(7v(um91@6ECh$z1U|Z|2gTc7uPpl>~%fG`cr(3oV8)jhCJP$A)O_qqMn97MLJ13ftmt;7X2ysGw4&Xo&tXw{T0$x(k0Z(@E1uJNas<{!Cysx5&jDLOISY#e;NJ1q(`LJ@Q=~|P5O)U5dKf}|Dt~g{~G-xtp5rB82x?H1JYg8d+@hOw@7#3(>(eIU=Q&1xA8T%Fn1R@djC7=57G_PoAB33*GRvi{tEvG`s?t&qrZXmU*T_}KSnz4rGNCn^%wXfq{E~`sBZY<=#Ri3Lw^+OZuno&*C5p-RY&~>z8a}2sS0Xk_?qae!Ph`v9qX0hzd>J`REAU%wG?~_QgKo-R6Beb^d;a+qc4edJA5hhMMy<Sg-{E_7a)B_DhQw7qb~|p6klHeU-K2_3L!`DE0Mk?RY0u>U!GKsR2J0_{%iE*;VYr9fOS9kis+k>z9Th3Z3^F*)QHp&)dBw<`o{3h&^N)l1HLKxe55Z)zNmTOeMosoxlz60eK3~?HJ``2FJ^p^qx<@#2BdnZ-@?}=)gjeJtp(ozeO>ta=<8v<7W}v9i_-VHLZl)#_Jz?GBo!cig_<9}Am$377J)B>_5ARK(U&HbA(cce1z&<x+@_ym<!Xm7gT4fOX^-`im??=I-B%)gO{#!e5xzXB9H}g-AAEVtl|!urUjgfW@D<T_rpG9d)X9r|NAw*??MdxW1K>Mgu03ie_&}@&z;{I7mgG-r1K%2bD^g2R3)JTDZPB-aZ-d?+>&@X?qj!<^lMcckK%Y$7N7{?J2R<2d`%n+U@5lNc_yg#tkfxHNQ76MsB26SsK-J(UVQwPo6!>VYYw(lNk0XsIMWK#`k0gyDjYb^>KOTJ~{5bScSRVyH7JUS1BxwX{ID9B+I4KN%m`6VnY$U!u6kjtOb0d(W_d`fSNg=3%;Rlfhk_MpmhaZZ55d0AIAz1GZKNx*qQa@53)L{7Dq+X<+s80BP=zGKWMc)VOPWWK--AO%2T~WKicOm^i3PSxJz6bg)@ZHgO#rpT~-O$gXe`B*rGf`vVV@NYd(^03v$6#&->MW1-nV6Z09NkYLO(jL6PKKXEnn;>}s=-gf+(gtV9_!JViAIj@$C1X9qEN@eN0P>nMx%~`kHp*<)Nvl`QJ9HBj_xB!BS|Ar!{Nh7p`_uc!{Ea(7m6AIKLYE+;KR`mAq^#kpbmx~L>fpMfZ88^5atG=4)ItI!AuBpbl;cMkJJY>7{0en|FzHbcMR1D-y3tiQ2WC7!MYPZ7=3qA4^mguZtz`5Kahe@zlZOFxgSuw!*|8{_we1&|3rUBSCE#Y{s_N}w3M_2H4c6S`epDxd8{wT%yQ)Del01Hv<7}P`UKKS(kl3P^lQ<tf?tC^5$o~rtI;naEha5MT?jv)G><eFbq@S|%*{hx1it|5bKn=EpGBHYnu!_<A48f!nvOaRJ_d6$P-nr<#QHS&SoEFfIp|CZMC}OQfz+PV4mAM2Gx`qjojle9F%yU!-M1mNCHbSahHph`Nos-G9KIFiTB5e`Sog<_KXP>6jHLgcVVa;eg>Ou1L~4lYfNzYsMySo;n_%4m-xPg)lKvTXJ=AaE>yqk_YNOVIZ-Bloe0`7gdYGw)9NpI-)g)C%{RX}&sS2qYd}WWmCRj~;y<D%3nd->VeLm8cBwy6L@IItGq}-_9@IIK!gPITC7wg{edC@;1JtaLteGLDQ^f&1*)IZ^$qJIeg1pOnd{|WyX{e98{(p}Vh@V7~~NO$1V&_6(b2mU_#yI4<yzlZ*J(jTN7s5jxSldh3|L;V&05A@gJe@A}<>%YR^M1O^Jm2?U9GW<o-1=4xcbMRNuUxdHnv3?0Nmyo0TGo-VmRMgY(r${GBCs0%1&!RsCe+GRj)>Gh5qd!JEPCAPE3;Yq%VbUQ~H~ew*N8pcntRKb9QRL`87kv-<f|LU_Cwz8NHd0p9&*8s7pB+9I`W#sQ96l%dU8LQlov1&<?;s_Swxe!?-+{R#)LkCyJ2A5pIlBKy_u&)i1L}Y9?@8}SZ&BaCe?tEr{v-MiSbqcmANtp%e@QP<U%|g1{X=?=`V9VG^e^CFqkoC@XYjAkZ}HME+q2m=p>BrXKw3}Q2*1vw-wLMJE%2MLz7Bpf`pl#(q)e!v!Dl38AbFwM;4@+_18QcE^-P!vXyui`H{<{7e<AjN|LE^^Y=-}#nE5M>+mAfI@*`!XZ$=7e^_hN7*Or0)(_hpz)L((w{tx0tea!'

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
