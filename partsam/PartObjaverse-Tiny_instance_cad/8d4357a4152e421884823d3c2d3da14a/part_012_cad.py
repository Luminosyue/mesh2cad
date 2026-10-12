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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_012.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_012.stl', 'source_sha256': 'c27d1a4d171453d3722666fd9ac6541eeec40f256106a2ac96bb989dff32e8d7', 'input_faces': 1352, 'input_vertices': 755, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0530075803399086, 0.2717684507369995, 0.00573328509926796], [0.0530075803399086, 0.3049519658088684, 0.04931889846920967]]}
GEOMETRY_BASE85 = 'c$}r23Ajzw|Nr;BrVI(uMBlCylJpgdkQ0g0purHTqZ>t(j8Qn|DaAEp?qrss%tOj4A_;|x2HjMq=F&X)pU?Wd_PKk1?)g2>|M~suc|Y&hd0S_lefC~^?Y-Ap=eBH7pkP@~|EuWzQtHsf&6|0isDxM6>)WYk?=IP$dewNeNB<13l*{Em-zVMH>eiO`WO#kOC#yWzsaJN-D%WOJY0$ZDmFihlIzQI4ch8QG-v3z72RliAW5;g2IwkX74|nX*DfznUHFfG#&#HA<^{jze|I7c1B{w0mx6;xrvMuj_{az#SlU-(s=Z-Dw^2C>4xjfc$w98|yProR6q)CB&@;cK0$C<8ti`|-U|H74z#B*Hv$cPtRp6F4}l~4Tk$qe!6@vfori909j=N_%1<?q;}+tdDv$-z9*>q1vgR)f3dy8P}7T<%R<qxEcUGdY;Y&N<hW&+T%rD<8e4nAZQI`P_YlHE*_0zi)><lY)8dy4qS#rQ)t0Z*zv0|8}5$udJu0yZ2Q;xWsMG{MA~2kBO6md7?mBttWA_t0(s3dd)W#b-8!R4>`fyE8a!Rmw506=YKAAdF+K#T7QKGdR!hEsP$a5R`>t({gZ=v<c>00&xmTe{Y~m?`4Lt0b93st;}{)QNk4biI^7SimzxsGH<fbb<Bu10^+YyR(EQJqTF)sjCzSv5qVAu;PsLqc`^aLK&q=sEc3G8a?tLeAxI9sErylpt8B>CJ?EEbK+{T;TeuylZrTNB(wf^jrZvQ7nbkcg}|D)T#?)u5WJksJ0E&u5`TF*~qwfu$CbbFdVJTaJi^-gHs_RBeLd*<z5<no)Y*YBIzeo`=xRGXmNS+s%szVUXmwfu+k^>Y`kb>BDf-XJZ1(FEPjKDUhx=CK9MT>0oNA1rX~eSUAPXUJIHKZjl(8_H|w_C(8l>dGhX@1*(A#ajODwPS*Ltl)iGzVL8YKK5k?&42t`&+G0#O?95QKJ>Y<=lhHc=CR@pwVu-JTs_e$mo3tE__==W=Jun5dF1tpx__>GbH1ym-Cqk``Nre5{LwB?2lH5sYqk98Cv-c<p3wZxA-bJc@5u?~k@jzC{?JT!yrR3;E)4ExuljxCgL&fWYjpd+tMBU1eR!4DKd_n}_jdJ11@p*#?`i*2X~jJEIhU`{yyHh&{=qsEgL$m;Mf=_7Zd<PX;o9!{xj)U*?Ww(Nd@zsHX{zVx>-*gPiDox<xi|Wdey@fLpL56YWF^h_9@2Uy&3ihSM+*1R{kHrpS5MZVqYK>U_S8JK_V!W1JhrpA+fKh<jqF+Daxdp1ZRa(IjSJ=5SL%Ly?F_dcqK8+wJksqI-OloJbAown%WvBLOE1&?P<n`#zpjS++}IyKyYoHruc!5U+4{MEju{usV>w54|6jIW`@<!_&3EPNoUQx0YVV1`Jodm%E{_cC<E}edHTP@z0<Y?R_;c>)P@dbsm5;C3>CWHi_lsPf*jZ5PU%%6x7x6(?YW>B&)q1iI<^=P^m<n3H*emXH6BSBnzW4<#f62<HgL!0FY26RI2e{8ov>Z0i<>%@7=v`K4TriIfj=J)R`)+mZJof$o%{$$xd71ide`dAosd?Mp+D=|CJtUYXy6Jw7_P=zo+fQA)>F2)xDE;S<A;COxsDtkR!&P1R-0!lr{t}$ObDoO@^T>ey+77$Ev&jAXjd!@*d*U%I-?9JDU>+;mR@;BpFRpxIbrUWB@OCZV<d;FgJaO+b-TuD+EOb7#mgeoR)8oD{Gbfba&`I;=1N6F6{&LN)=%wHH<_*Jwd8EnRy8WFO==T3mP`C4~zFNNaZ^MImq^Dj7vqrSm?Qd8>x4&^|J&qGz8W_rFoYe1IWQX=YyH3n?^}Kyh+sVzpJQK_lJO8WO|JHf#xW_L$;&ShSOEmwqvTL7NZywfqCXCblmiz38V4isHUj1Gl9CG_DQF5K;(KqyaHG6+}FpoX^wC?9f0axB@G+*<#%4mD5d-tSZ9{HxWw*Tq>>h*5_6wTkz>yDQgHaM8a`d_T)-O8)A-+O6*=EJ!!ic}pQ%D>y8`)$Byu6*p@^EI!2yY9Eb-wqGv-jF}_xO5)i`m6Y{vReMCEA_ma{mL`JJh8fuZhxEe+<j53Q-*H;tR-51#jAz}^VsDrUHRPNom~H!xN^x0?sG>M()zC|I5C*V+BDJQHTtHR+P>zxJh8it=B?kz3Ffg&9@qT%pL%@jP1E{U>HUT`zs#s$p4y+?kGOs^-m{OEFY}PrbM!rTUzGJl3(XIFqxFodIx?8Y7C)xn>!q%)U&^|mspeHK(|SJsXHqctS~k+}yJ3a9PUSYZP|FXyTFW=trTzT2-{USHvr9ks;?ZM+d88QU@B5XtA0D*O<=%Sj-y)?Sn;6U^cRs1dt7t9P-g0|P(DJ)<KX^ZXGB%jUHpMjWQ*yRDE|VVCe6^lO-suB5!8~$TbIsr1;_8o=Zl&edYrBdyUi3^bkNk6so)<?vSAYEMBAV~f=Z@TGe{%gpZn@*nyW`$^zss}E`Z1ihIu*`49dNn#MN{3LU&lWi%wuN_V?Y1u?uWfnqc!h)zUG5FP7LN=#_f8%%C>OVDes*dwY;}Iw4HvQSemgfm}hOTr{xcRsO7zVp**qw`%s>{p~CZ_{V?pH%Oitk&2jZic{gqDo%>rT_qz7b{O?yn`^V2?FBjhz%5SQw<=@*L+8#fTeeCTE=8-WE&35^s2etp4QtPQ;o``kQyvv<~g1I-ki}s(5hs8qW&+4k>KfmS4Q2o8TYx$O+4hiOw@k6zI#fd{h_54BpYqtTRe8oo1m;D&3Coyib<~MeEBJ{cKGU$hUgv!UhEu#6(C;Nr+gg%eNqWweL6M3MumM{8E|4{ku_vrrrx5DDk{yD*QXGpJ5o+$o+mao1uTz+O}EkAO4__!2#NRQX)j3uG+YrAXt-ls$L#1;+H>(@u~!g-Iey8ZwBGdxsJ<te&7RW>gSl^-%!%P(IrI8^@Hby|M!-q3bNmTcGZ?;jl<s^`3SwS4>W3qpCFW4fQK-yGVW*mpnc_l=DYZI8G2cdft8j`5*<UxxPoeb1R6+Rx1{)PAG-%!#4$6SFiQe0WSKf2FF+qt87wH<bTUP4mSk!u3yyXg$lPP6?I&y0P|$85826?^XY1?UyPQoe-*Lp7u-L;y<Q`%9qmXY~-x2vqSaYsMpQt;lD%MnTYq)@}s6s4jq?fdVP;Q`gwSJc5D9`TQVc`xsg`Gb^E^>sn?4iI@3NkhWbfAk4=0l)L;3z-|xjIoC@WMVyDxVkCiSN>Tjdd7R+*=Yx*%ixBXbO-@RJi^pk#W`^l{Anwpz_*w1Z09Iv`^X7GEZ`t9<QU2d-nexC2TP<Eu2H`g6Mx7VHA+nZ{6b6xZEeAl%<f1lxUbKUfFd)-Xz`pV_@x}3_*bve3e%Z$)|@Y_R!N?O0UPw;blpOAa<pXsi=xexJkdmoZDXqn6HeU6{o`<!TYOv~H*C~|ur760(#X|5h~pXTTGJ}q)IN6VZ0z1+*2Xm0Ks{oLL+#;4cO+}xM?dA|G7E53ZrmACh|@j05?`($!^pPZXB+U52>+|TWOc<!pFw0?7+@8|YD-<$IGRJY&EbA+GU=ZI*N1)7`Z6hF7mDbeidTHZVd`MG@#iewy|;>w%ntW<8Evl1I#aCyGxIP!eYaYu%0Zk`kU+&(AfHty(h`yA@$_Bk{%y0q3~o^$=&KIeL87InFOUXH)@$7ENJdG7Y}e9zrqZg;tTu21FWxjrklb+Yb<@VJ4W+i`<PwSM}!W?aJ0?YKm|R%b15#ywKG8TW|)-c+~KjH~#0zHyZU)wH}BxAAj3ZW9|?NOLnT<mYx=D0kecNiH|zPJV93oxEkoU2ey<{M?RfMc00)<<0n5;<fGixpth5+>W#5R$iXt>Nn$fes0I{va%m_xg96;b30BL9WrpDwzu$jW8$C6F1O>BsoacP#!4KX;BqrA>gRS`G?u+f%bRgmKeywqkte4<>%OlUzfIiu*)uLT<G_Ay$ANQ4?r^ysXHMm2oH@7s>G5v=m~m`B&o_=eprp&~IJuwOadNL#|EFDfGu|Hm`ipVybIrKDpWAW!+<sq;b-9@r@N+va5F2tpb2IPY=XTy9F?OrwW?sY3?YxHf*KcE7{bt_8&+WWPR-5H6xAQW7Zs%p<7ymlil{fP~ex7gMXUim)=bKj|xARKz8dWqm^HbjSg|r?s&*kTKo+~nW*Qns<`txY1+{~jz`#(P_xS#!bIzP`hPuKcVt;fvwMQh(O(&c8}(9i9>q1WN&5pI8)c}YLF^OCV81&6!xX5Q1!?YyT~sp>Gd{bv3&78^9w)nn#i{oKyO#=bA@ayy@!_@K%Vmz#OvRBq;l<Eu(&Zswg+xtVwN)+~>??KJb(S(n~CSleNE9^B9EJb0vM!9nhOnfY|@RG)#a9y2fR=XPE`Qla-#E;sZ3es1Uey?B);U2fJ7WUVfwxmkzc=XM=J{LL>0xbkK_Lt<_hm)ms_es0%A#GC)x-_>K*UHG|OcM)xHxSz|-`i<y+j`wl(nDrisio1FT%lqp?Vw11$<#My0#H%*3r>n=VKPh~!%k6p<$s47~rJhD<>hY#t->XrY&y7^t)w@xe?Ue7;D9!iEZFsm}uzYGi-1Ms(53~Ez&+Yz<&FkXE^X&2R^L)oEdE6VNIquR<8vPILr%{^rlSsD1MrqoiwA)7iLwjzNradQ;=S8D5=Zl})^Tq2`(A{s^^G?oF_d3n_>t37lH=67RTzS(Ec&kh3{h;YjQn~3*vOcV$x#_P`x#_Q@-*dU?_i~f{q$_9oPd~T)XEfOlyWIA}$$s0tPSc;e{b2g@X!5$?UYqNMpWEw2B6;0$xw#(sxxF6Ab<LHt>sXT4L08_cV<ETK$9VEO>*_Jr-&Ag{zj7USp62@Q>NnSSxleGpUB{BVuLyo_@P5O+w)Y#!`xb47`R`}k`^^1}+!wj>Y3`R?{pNm2?z>!`=6=k*w)bP>wvG+%Xa9cB&-1NgN!~ZQ`t3Rva(h21_oXgRbHD0doBLI{?{%M>=6=}KW7n}H@2g!ob6+j@;Vw^ef9~AepUZu|``k45|L(QD{~xu(J;&!;$KvPa`9hvk+`p%JesT5Nbu7u}Am{cuDEZvv>Nn3*er}(q<hjh1OY^+u+&r&&|5n!fLGwJA%FXj&Jo#MdKHof7Mv~8=?)~QZ)X(knsaIvW=H~g=&+YSXZt^+W<>vX?&+YSdR`U7X<#xRaxqYse@c~zVnsEbH-i#Z>hZfR))Qn5`xgD2?AE@SXJMQ7<`PQra-c-xm^(y3cTt&ubT%Km!#^q+*CR(kZ=4M>T&+WKSB(_zz(~LX$xgB?s@hi98X~wnOYcsAT<72L#G~;I4-ooQ%vC*Y<UdW8s`FXzax+WbpH{*eRZpQ=TM}})|#vA=S-@23yFKC`-Jk!-<#xr9X2Q@e2rK#MEm&&-S%hQa<y7!y$*jSSVTHcKJ%J{I`&NSo3?zI^=j^~Wlb%JIbTgJWJ`_hbuhrTc4;n6F;)beIrJ$HH?T|Z^U=l$G{&&zy)%hSvwxO(k+kL;MPU&y!KW0~e=zQfP$e24eZ7R}e~()pTgdt5&d`{E<bv)^%f^z)0B=y~vi&i|~{`|9Xj5tqw+jVqsK9>;B;na7E}ceUoP?+Ml8=P~b(P#*pGjv1lP?NCPNwZG~X%5&SrbUd@oc<qlbdM{KymCyS%Tu;?$TF-gw!~0?9a?N{g2<?YdzU#fv=ce*sehKH9uZ6ZV{`${44!miL?guk37WwoG-OkE7zZO69$50+=dMcF5yqohh^Ks72d|c$5Q@Wo&+#K4^kw1Ue&o%Rau|I3;bHmX@XutV+Y((LGq5WL2rRG!L2p<<ezr4`CV4hWOq~>OR)6ebvX5w7(-`))EPe1qG*7ANHFF#r9H}kE2Zs%KN-Zpex{CVd>N3{H;CAuGIC-D!y(a)W^RJVtA5?xtF?}G}g47X?U*lXwP3$_33nwp#WWk1h1zdWukzi(I<IxeaFbg9sBiFIf)E7+b>?UUTQ{jAV&N%Xr{b2C5g=XQQP+W9{Hz6V|jwa--koR&|u+i455eluV1=XSn6_lM5fZ<%!kes0$l__<wI;OBN-L8>0Jt{`#$L#(G*7&^YGe9kh>{r-?Vv3gbLxcIsE%9_yr_w!iajp6p}m;dF=ed+Q<;j{Opt0!@0xqazAH&Us5sJ%tU@VRCkm!I2pTz+oXaiz+ebzG_X%{neWx9hl4^_X>BsobpNO66u9SL$=kI<8c1)^VkBvyLmZon{?Zs=QgpmD)dM9am~Q%{s1Bd9#iyRlixsl`3!6apfJy@H(zkZq{+7>M`rMQsvD$u2gxmjw`i)%sQ@AJ!TzODmUx6Qn^{jmHJ$>UMrQGby=z0tjkK}W?fb)H|wub+hf*WrOKQ2RH@@@)>EbSk6BL@y{W4HUdpahBDeis);&F3Zu`|#Zu-?|SIzUSYa-9L{xf@=mbd+Xt*KhxTwhYTxxT~)&C=Xlzx>=@zp_eh*6lafM?bgM$H>NSbbQWSe{(DTr1ebDaj<CfNqS$gvBL8%H`npl_IfV2_XB=z?+2pq+^FTv{fVF3`;$oL11`_Ep6Z<ATHf5JrE+thChMX@+wWhG29(m@!I=Bfc#HCyoBLQl_m=4KO68?n>3D6Lb=vN8?K<sx{j|J!F7We2k-tKDqUR|6+~R+Swnx^PyFAVMb63Azmo;dimN(BkvL4=*PqR+mxp{7qb^ESdn)Upy9=mR;-ZU+r=63|Hym=m!-#fU^OY=Jj=k_`DSXs@@^Q`<X!+DzDYq;&Ozt?zafR;DU-KpHJQ`$d8w=>P}O+w#`=X&|wip$gdp2gK;*C~};r}G|mof5enmyqAx==q!f_c*Q|Gwvb3_i?!yKgn%a!0it^K9kDL_>BB6NxxVA-z&L#&G=7N`O9@2)Qm6rxgB4U-&MKtX?}0za{GI$HBEFo&G?v~+wn2^U6}JUzZY}cXU5;;cV{k7^LsS69cFw_e%GewPyXM#x$QCIhw{5QS1!%(>0Eg`KG|}Z)^Eo@$@8r*s!&STN7&y34!TmupUgO|pWAWT*!PPxH{-qXJ4g3A&F>$zU53Yv<#&`WPxJdq_kO#M=wDBNr)$TzOApcY7iOGXejn=cG`|~l<?ML-o;BL8&A7e%j@6Y*^ZQo!+RO{YPFB+OgJymqlHFX}ot>vx+g*Prm*#i7&dq#>{QlQ@n%@Px*JeINeqZeJG`~A`?=$l?vE6GmH}gS$Zs&udV^3)PX1>YK^ZjnR-CtUdna}cbJD(M)a+zMY&3u`k=Ue}ixL)rI()_O6y*Bf4^80k>W?nD%{!UttnIH7?eCvPa_YQq-YW<I&oB7B1dxI7Q_p?90>F4?8H`~qDddxg&?%e(S-Y7iZ>gRU8RsQ~fdw-h0OW@vb=5upLbkg!>zSz(0d~s~iEFBjy^UjeIJG34%f9>b_{tiR!Bf33i9z3?Gg1bMm^XaMF&ZiHnq`8@|Pvv&~Pm}t3|7GU=<?mf+JIw!gFx+dien9@7hWmH34k7;IdacK-XYg~oo<aV;hs)Fa-4FNLuK(Gb@uJJkx(jcAVa?6@4L`T*H{|b`xbkKlh}Y@@m)rFues0&3WF4!b^_cZ4ex7gr&+)FBn{_Yp_g?h-hu6u(TkH;%Pp$uHeOhz-_hiPFUFzO%*6qmOt8v>GT<6m=^jCPknKZR+Zt~wmMZL0K=Z=9t!IRrai}{}ZPw;f9{r~kRcxu+FbJhRtZ}1d5osoQGPwG@sMKhD9MbiI3!oT8wC-qlS8JWtG6{ozsPxwq;|3g`MuVfkI!i9L90ZUz_VgKI?kc$_FMZ%d#xFlW%7Ow=CgfBwEHSzz#;vHbo{YiC9>MCA$#5?eB7xMZl>a0n26=iD$Ue{t9E+Wh1^}iV^;S#7MW#l_%Qs&}J-7m6FYGmr`|0H!KT!Ysa2g=Cn3iz4u75tme;?;3EW<}vMdF}t(d8h(qs`L6>yeJ%{-s*4-Ubkmk<@H}2zkg{L|I#+({a#Y1;iA0$l`?-Obw2y17LxtkDXD%*J&{zeq|RYmq@JEh@0`>_NnOr%$-nhY>hVnd_XpWl`M3Sak9;?&5AnV5NBBW}FMJ690N)Gm!}s8O;pg$0_+EG#J_FwiPseBBd*Quo-z+>1&w}UR@4|E7_mJ@W_<ndl-|c-Q{0S0164)0<@PqIX_zNWbd0-!Xj(-4u4u6b<4+Qqz0ela90N#y+X9xD_Y<wm>8=i`UCj|EO1bhZO0e%(<PYfJ`iTEsdBK#aa2kw$=Lk}nQ0A3Zo2d{!xg)hM`z^lS%<K^(Ga9O-OUKPF+zYMPmx5KmXs&G}dFB|U)cf%jUyTV;5_ZSlHfrKB$yTD!eo{u8oN09Knf&FqXUIo4vu8f4U0{bfqzW~mH&qBgQ0{gKDUJfn-7evBm1orP4czO5?xD*nu7})O>@yp<fa5W@+U*LG$hiAk7eits4?6a;*stn#37QYcL1D}V4E8s2Q|KPXcE#Pi=SG)z>g7<et!Ve<h`|-wbW47;pB-{ZBw?V>nk#JGG6ui<?UxAl`OYuF0MZzz6D&d#$^WgLNp28yGRh~+CwU@VFgx7fL7w}s03;6e2;S1oKknlr+{V3c6?}>MVyRjd8BH_o8@MHLc@Pq8f$B=M$B>XVm0q(&5eHaNxk?_4p_--Uz2d@j)<v7$q!bOnqIxp`y33tQ0;w#~m9H*{GI2#Ff#9xA6;y86g!tIf88+;YKisRJ=3AaMR_jq~7Rrp?f1HJ}c!!h5$YvFT{@D2D)@J$@o8<6k=Nchn}I}q-OcgB0bJ!l7=k?<o(xC{O`{5b8P3lh#o!uR3b;qJ79`;c&ZB-|R0!cp2sYb1OZ622V?w?e`#@w?%>X*VsAa7`qfffs>`(55nYExZW{_YAZ%;l}uNcsIBk?d&=vTptP7!L#9P+F2bWToVajfwza-)6T9y!c~!QWxN&Kigs2R30FhHR|eXp@HKcR{9gE8+GQssycr3Xr0q(3ElIn*0WJwQK*H_t2jB;2m+g>nCnS7NpdAa>$D80C;f}Q9CP=tB621k01b&2ed<zo383{MVv*B#oaZ@CGJrZt+w};!)jvFH3Ymjhl{4V$|+IMXv{9hz|ITCJ!gm1%J!L4Zbw;|yO60VNdglp37t0Uplo=W&NT+WBrI4^p_ufe^MaI?U9B3uivgg1s8bDmT}!WSXo3V40EKIcgVBz!IsE{oTMYjU2HMZ#wx;i7m|xGLvKQ6yXh375dD!PPiVN+99VNcjA~c_myCkKot9*Kl4%kZ=zq{06=m-po1o2Csz+AmLhg1GoX_RV^fZClYRpcY-@{UbRKScOc=b0_UM{CVnPfAFj`NcqS4qhlJ0^o5RgH56?%!7b4;E_|5RmoQLI+@VQ91G=4pNJ?CL*BzzVUJ_El7zJ~Mg3?y6_348c|Ve!jh@qaz#7x87d<icz5Q~1BIxV--quZ1s0!Zq+lu=s6o4ftv#d?g-%#jC?t!j+KlFP^%b|H7v^&woL}uOs0>cyG8j=lLKc+!6`j;N|rT!VU0C@LI5VCHNBfLL^)czX%qu0GETyAmL*8xv+RyxENdr2^YZ6g2ju%1z--hV-GI^i<j{7{u9nb!Ugftu=x3KLHJB0e1VtOj|g9m*TXBq;t{wW+yV(df%kyL-+-Th-$KHF;nKhSh1Y^b!c~#*wfLQ|cw6{dxET_zhu;B<Uj^5Lt03V&y}W)$c)h2-9G84KekLpuUh1iYm*C}K@$+Gk@FGtoJRiRhzL0)LSS0*{rxKovp9`N$zauOXp698A7vN{XXVLEni-Z??D&fU=VYo1jQP}Tygdf2l$6tiSm%)$2y^!!gFRz~x9-q{Rq&DIM;enLdh@XPRzkxTxUn1e+8S1BCap~iV)7RC2#V>)2!v&FWWxNJlgTAjaekCk^DO?#YgoI1rSHf4)Czima?<;|S3yXxmLc-hdUtsaqVevt*_(*sg{0tI)2p<HCw}i!SfW>cvAA%o6!nfczz<!@A+#SCa2{*wTz~Yy{P2j7L@WuFruy{H6V)#EuxIA747B2>uhtEO6XXAxn@dEJKa7iS52A%<nd+-@>VI=<*$1`E^f^c!T6cRoUKNA+e06q`SLc(>uy#8AFzNDHb)fBG_*QHETydErm6WkQO9|_-y*Mr4dz~WE9;zQs&;ju{gZTtyX{4H4gFIfC1_-*(E60Vq`{ueAR*M^E*Bd&$TtHBlFvPk#}{95>0t{GS0^<eSK;49#>k#H7X4;HTii_0}53;z)o2_Hwoui$^e{<TMV3?4(m{qXg$_;R=({1_5`5MK(5FM%I~J0Rh<_##+*KHL_*8wt0@Ux3Bu!mZ(UNH~hmgT)uXQTPEQ+y!3<i!X-#>rfXY+z@{pZU|qGgm1)q!Qunq8{ylLaA$l3EIuCY4EIOE<M7GwR(uOS8J<kJElBuPd?PIWCHyM91^*P@iXX*4g+Ha-Q6&63F4w%@@q(~O_$dB8@7s!hhkp-$Pr2`SEnJNHD#Mkz78XN=C@=m4@7szW!+(H(pxiND3;%(afW_q+`3L%nvf_u~t@w8QFnpMD+mY}Nd>btO47>y0j!%KN;!opK;3<@Q8VL`;AA-dng$KY-<HO*s_;7p}JdAR~k?_O#EwFz*ei(J9toTrPD?Sb%3J;~+I3(=1bK%bTt+03#FYmk%_Rk~X8}X}P@r%8@^G?`5PlX%e|AEEJdwJ)z@U=*|HhvB)el}bi{x1@)j+cbR&w#7LRgmzdcwtz)ID9F584|96mx9I5gKNN7BjHAP7A#&DZUo<qgzvzc!{YbBcffs+@F@IAcqcv>e-eI@a)XiZU3gPi{C@Z@crgAHyb~XdKLtNUxzR|tFMcO1J{Il^kH#m#JMmrkBzO|#b|K++@V8;{6Yx9mE<6|BiGPjf!nu_D8VUb{%RR?Gcv)B^{5Ad?@7sz0jQ<AzM!BDPEqoF6T>)Rgy~suAY|4xO%KLWWC-Gn5UnzHz*TR3}S+Ka=qx_AIQ&#*lcqjfQ{u%rk<=#ZX3H%k<zrRVKF_ab0fp_Ag@EkaYa-)#2-_C{az+<p@KQHgR5cba_;YRplu=s;s-gzhNpQpk#@D8weTQBdt7WVrA;Y;zmVe!^pUcVvi_cOxP@piCy)XVFag#CU@xHkR(EZ)V->-U7O#T&vqlE-&?QakaPuy`Ea3GYV2`|<hk`}ksfK0Fp5h0llQ^ZrptcqkHn3ZDtjWc!{%!UK@-U?e;n3Gc#pz|At%Z^U=NJNTZ$BH^Z)D&Z#hZg@A}Q&=S2I8!BjeP-T%5xyZ){bOEB{xSc)82%VufrOt8>__1d_&|ItJeK`95D7nlg!|${;i2ruzDT$?67Gc$fCsRDd*OZH{`erg4?GO-hxdW|@cw>CcsLTCi_eB<bKK@4;k`(>MP}Y{6`qMdk2iyxaa^BA!t;>u3wTqwDaZ8%Bs?1lKZiGl8*_Z0L&8&#@Py2~b|Cx=eiMEJd;@LdCSD7FiiB6<E8rEhgOx})2MLc3v>V}x_%rwjcm(a{86-Rg36I2|fS;h<j6}jiknoduZ@4$@<H<m~5uSlh!~4ViX*bi5@GK<!LZF=qFTuy*!{A}GvvEi`hJ>HShr`2ZXHO&H7m@IX_+EG~ZSX^03*U}}Ck5K2@Me4)J`<ivyWEC^cOv24_&j(X?Q%B~-i3s><Fnz}w9D;C_zfid8a@S{Lc4qo32#8cYXj|AcojYxe+GVrc03vh--?94psh>${(^SC68-{Si-f1*IdBf`cq$T}fP|+6+P&}^{AGM1Jdt+)G7?^ngcsps;4!rOMM!ua5`G>Z0uP~mKOboK!tda3;WOYFwEMS^@OC8pHa-iUMZ13+3GYF|9|X=5;aq$bz64&vd9n%#PeQ`u@faNAJQ<IKCnMq2_>1t1oF}W1@aIVQF3u%6f9~Qungrhkk43_30_T<RKKvtmGrXDe>LVn41PLF*cfvb4uZ|(%Z;<dwd>6cn^XeoL{t^j)hQ9&7!Flx=68;1Ue~52@H*j8kh=dOy;dcY)p>P6Ufv<vBaUQNf!XuGzOZ-;&R?g9uycYfn32(yJ!fQDXHzDDLNccH?0z859@Hr&B010o*$UAR^zr>H=Yhdx0;Un-TNcbasIV`>i{s=yRg!kd|VDaZ+|GX8xI#az4{thhu7Az93ov9MO2Hy^E=e!jb316G35^jL+f%kCU3X6oV%Tx(RGV{)J;hQtnkMUaaWBmIn_!#^u5?+c=f+umFFGa$0knl2mGCY~{d>Imc4GAB|KZnKTJU`BB;nqla7(Nyr%XvNw2`@#$n=<qI1>qg|L3|%9{t<i-{t5|yhaZ8(kHO!;KOo_s@NZ!8lkiXQk4X4?{7YE;Gx&S>TO@oO{{$BQ5Izp)BH>T*1F-nJ@Tc(mNO(_XUOytd4qu5UVDT03N_Zg>9)gdA#aqHd;5(7<*BR>4zX*RtKk_va-in0R;|t-1^dsw$@JmQ|9liiwKtHk$3BQ4aPiExxJHpK~)f?eo!s16@k#NIIm2iFh6ZjMQ9bu7hy-byGUHkxifc{3<?{|bJ<5TggVevZfRCpE=j^njq@oV5XJQoSi!LNnI8^Ckm8Avz>zYZ3Uz&Y?3Bs?@Tub&d`pVXkFZo`MdLn(6`E`8Q*__we~_$MU14L=4SqmSE$FNMWlfw#f$BH<1AQg|tS-v)dcEWR1u0KbQX-^7=}%jgr|#E-+`-@$LfKO^C`nd--3ap^0C#fQP-gW<OD03^Hs9|nsrg~d0);>+O$@N^{n621xc`&{8^_%bBC5#IreAA~o;?;+ts_*by_ckm(jb0mBe{{a^N2|fycjf79&Kf>bQ!zbV`knmyrTUh)!d>H;134eg+!s4I8AHe&O@Lv3VSbPt>7v6$|U(U?yuZ71YwJ512_{;Filv#qWgvA%bOW>!G@I-tiEWQvH9|DUHgeSs%knr935Lo<9SX}!0yYU}jk?`+G_z?az{598xL-=}F{B`&c{23D7g0F|gUxHua+OP#rz+2$MNcbSW4i<j{7C#A#e-9soe?!8zWU8Np{cDeKZ~Q4F9K)N#;*H=KJOT-i!W+Wk_2E(QcqIHRUJn+p3;Wk0;q~~d_+(goD*P(^Iud>pp9PD@;Wy#8k?=eCTv&V#{0{sU65fi>fW>p*t?(;Icr`u-79R?)hF?U&^YKBjcz<|4JRAu>iFb$F;H~iPaCgeJLc(|8x546aox6kA!maRPysr)ZBmY(mE=IW@k?>J`8@!F{-%<1~WyMdxZK&@XUY~$lw#djVTOjX`1N>6z(8bN0CEI7S@cLC5NASG9oqG1}!e0xp?+pK0f#5qwChJQ5k%5*i3c0mcnaTfUamNcXGvxh0Da2Le'

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
