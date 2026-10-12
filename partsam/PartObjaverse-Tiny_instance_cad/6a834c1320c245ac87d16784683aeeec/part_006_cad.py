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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6a834c1320c245ac87d16784683aeeec/part_006.stl', 'relative_path': '6a834c1320c245ac87d16784683aeeec/part_006.stl', 'source_sha256': '4bfab175c3c10568cca66ccb885d375a849c674e323015a8d05c0997d0943238', 'input_faces': 1146, 'input_vertices': 988, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34352684020996094, -0.16916632652282715, -0.49185895919799805], [0.36573630571365356, -0.012788265943527222, 0.4827936887741089]]}
GEOMETRY_BASE85 = 'c$}r32Xxd%)V5_C5+JltLJMR=4K<;cPz0eQKnT5rw)Eb6jp&5lOK6Mf7%<&bBinRrf{iH#8x{y8bO<HX@XySBN0A0`zW;n5=iKwY`|RDB(adP1m9(aQouFiyH2U|Yw)b-E98YUa<B?j+qz&%We_*!`ody)^-FH}kmR@lFPwL!yO@6H3B0w9gjVREu(|`{B3smqFsMxt&fg+v)o%{43*uP!xwtf0{?8JG^c0C7lVthc?c6~ds*I$({SFVVsWWgeyQJ(+hzf`;p&EK3m#6)jAKa#7q{mZ#kT)0`}*bY1QUSA*KmM^)?H?D>_%kf_@-MDW^@1vaSk5*DSr}rPS=c`=iYjHW8<rGdHf5?UF32V;Sxvyp=(=A`}|MJJhJNhT~Qmma@`SBM8*B|wB<m*BA<LunZfBKAg%My-!b7)X(6*oR<j)Qx46^?Mrw>a|6Et<1EHMYmwxg0Oa^|04x9rcb~O#P^E**_}x++7^w#^ro?kIV5@xHTUX?wyzKxEuH6X>r=MeAz!Lm;DKD&0A%AC71I=<!V1juJ(hvU%bbaez59Q`ayEFA0+n|Y;xMQe5D^OF6W8opo1HQB59tCoapSgsym7A93Z&Xr*)WUXQx9a-MG1H*IBW@-{>#6kytI#p09G5uN7-a<z&gWMQqo$<tN>^-l9Ofotx{&ZWjHYEAfOI*DD{P@*hTt{ZC7Oc(bE?g<IuI{(FZINBIhu<(o$~#M!sYljh(FH*WQt!eu|a$FG%%w{zLgYWeT=|I_sjZuP&ywH;+?d!Mb1vyZ!0ZXfYVBjX(Nr`2j|Pv=vyj{V|!R#C6s>sYL#oHG04?c6$!fSZFN9r>~xbNC@gzBO;bwc0(LeEeQVIdZ?2T;1PQF86np%l%#Da({oXeC&4?FF(k^eSv@e?&zPW4wnzPaM@1Dt$tJT)$MvOKl$hJZd`7c%B^+mR5ihk$NQ-Kx;HPmaXqA?gKJ}(?{>?VTo3OcxVKn7;y;Gbev~v<aC7Oa(?YvF+$idqeUA9!JAxZkLa6*D0iqwg0k?@C+P6z+<QtK1EILQLKzC7&`EDb%XWmvSzj`lGuQ6-@<!9?j`Kh{WaMW9+yWo0@mQ+soO5(wFPrLPx%4PpZuJ(`0W&dcO)ueJdPu?eVetWUKM!xFA*RR+s@(#BW+}yZ5nyY_do`d3b;$Gq>wg|4hEOS6;#vOutN@^#Cjyo#yjj&va;&sC}Cqz5`NTB>%Sq0Zlk2>L)w;L-YxpK@;J$A$i$2>&-dmQ=N(V~L;O1z<dJ8~zniVHXPH%PK`;{#lqRdv5xIg-nKGde5ro{?hym`!UqdBQBg^+Nw7x^Xiqqieo)@GA%RUnFiQ`I5_gt<J0CVjOC=rSjjUb#M*b0QW{dBED!0mD8cR;QFNp#7oz8v|n=n^@5IiB{vmrjJYPbF|Rt+TQ?`Q=UM`_b4O7se_S#L*T6N&_Z+A4^OUFjZ3PAQ|9+IpFEH5A|B~zAhRTblqw=v`D%TZmm_d&ISGgQVU(eaJU3XSF+9SCJF56>_pXuzM=|vn|2iFzui~Y>e9?8ASlXlwMZ<PZsw^v^^^tjvpBDvfzv=4AO|0S3Eg_^JKM=H1WyUyi~iT3nOLF>ts@nYTZ4k{zK8Jk0_C#E?{aDTw~BjWYcJYs#*>fIymF^I=h5bK*U@)oT>S>_xT?NHYrm18|I@=g(4U4P!=$oD7J65I%`EY@M|GUa>k*AUzcYDn`TpbV{JwJT6L1M-M*F+Xig{7zYFPlKCOe)q&gJNJN_-JIN<_3<uyzLvd|qa3|cvm`s0`5)q%!i`aTwu}7lYq)X^+_&%>;_+p6i1Maar+%xSgWCV173I&pFWPDD-4rGIA^7b!k++~wk{j2-_0Sbj_VLn<yRO_iE}WbhWgjn@uX5|WC|MK1eXmAPy;Ytjx^WHM?3X9XJ}$<XOAapk)BFIJ`QDXZL^;NNRFfn-_k4g`;{~p@dM>UP__tIR^IvawlKOwcJ;AlO7JJ0&dwXcSR-WGP);}tj{o_3lzTd6?RW9?*FLF>jCUm0nfi#(~2)^%Q+CSGDv<@r^65Qx^VVk2p5%Ut=xOJY;_v|)DdyubkYd$o7v{lsqGz+aWJ-Uf{{SOia_h%_d?R?mr+B2xqTG#d{+$ujL=UTV+sN7m-ng*{F?HO1=)N7>MCF=D|8zH#1s2Z)SOI8W4Uwt&+Uayg|ge$lD|MO(??Dfigm0RsUT%lDJo|ktPjnAdmB40}}#ml*`R*0BCW~V#E<BN8x;?f?Y*7pOdxYVl;`g1`Q+dMad-#NIP=eokJ{YB+J9uVt^IVIq#(B01k*UI-KUbDJ``^ynG!1Wi&7uwsSEg$aS*8cSYZZ30j&zNW1-SQ=u`R3E0C89l{G*9JrNp6D6e$a-u72I2R0kwa_Fj0;+Hi3Bk%Oc;bP{YA>a6@vV*)oy8HwPW3?v|%^rkN<XUNS_i+s3Q1)Xq$61UFunpzZBk=qlC!H|6hGLdUPa%TYPyr><~}<G#07?A#j14{$Z#Xj+!qzvW+7u7jJye_P?`x9(M`op1N7u#c~~Yp8=;>$bwJ@%;c-^F1x+Y`1gIx8qmY_Y3Ph!831_eZR2Qu{l{ciSpNni|Z<S#Aw=&{PhGkI<FJ^o%Yu-TCYA2+3wiyaz0OV<JLN`?D=-b{)l{)TloV{?iB4Q5=!fL#+_oF_l&$PxG&{Aao%NC-9qcX_EK=|z&BGw`CWQ!sp7)Td|kJS`YyNLCHSk8i)g;K5?os{dAFmT6;>wMxz=X_wKLnzD~|k&Tc{th+;VWMe^8FG>2$bTKd9X5hfj(fa_eW6TkH9`QsTO-w`ywoe*IAsTK~IMqwBS~9t&>fZ9vEU&25Rli==YW)uHcY;Ql>p!`!%UO2{rZZh)I<iF?NQi1)rG_EY2AR1WS1*TH=QP71CSnos+6&!j{<_ZK8?fSWC&9ql)UCOWtWTvxc<E;Zi-m-*hdDI-Mr<BHRMH?eAx8#lrAm-z%YLLX84TRcg$a~<4}yw3N6`!~f>f9@NeWalQhxfgs|vk3e4ni(cLxZGYt;c|Orz8Oi}nkPetIk;KpWSE_6(YvXf%S*yVIY;_9xPGezozL{8cKSw}f@{rB()FJoexdo_Fp|nojG_MQn8U#ha2?!N;jm-7w7%ILTyB@Ha5;`LUw;xy<@ZcM-{XR)AAIAqD3Sk7sA#8tHjRVpZwKzRbM5c`f*aq3P=DTCNbBd|v4VR8=F#~{s(Exi-!9)_(ax43bY1Ia2$g@cl;FmeYob4m6+5XPDxDPEJEkIS?}?wT*txIE3UMB7jA%jY%$+<(#QV5jr?vi;&Z88r@85UH&gJzwHQ&09C-Wy&rE>nxwMo=F_@t8$A4k_AR~EkP%ICkL>z0E%2<~5v>i|3crR#^CJ5jw$s~xa&PqQvm&PGje{p4#0*W(saIdN3J_rP!}XMbfXr)erW-fbF5<(zm!=lPvdIJj(&<eqwCsr*;V=z8hxKw4Kvk9E|mPYa^)eKU=?dOcj>*7a?L8*}QOui}<pbC@gFLYG{0<Hmu)33mS8_ezDU?XmKwG&t{8j!|m7D>qL}z39pV14VnhXXXiR>feXh=Z|OO0%||5OY52PQ~#g4Ah_?-d9<HSX)4x9$@N36_uILD$tx;9$5BW5l3UlqF+Yt#ZyfcS`(MyJ+(O*{LpNHN8q@W5ZI(v&GZ%b8>u`^C#2cm{{&=oq9{O%(7Tn*p6XpN2i?;WC7P|i*I+A$nl+>Q1*{GadIjG*xw$t_e4B3ym?bj-o`>EvWeywtuZ<bqp)NQ`0T+TPi)%l=uYd%a_N%bb~qjB7@g6i$DhT4B;DD9^aONl?+>EL>gNwi-_>~oZ(x7t8FINXsh$Hk~|lG^iCKgv&w`!bta9~0xUdAC?U%{S}mc=t^&!F{)WqV|VxrFD31xZvIqd8prFE+vS1Cq)Ww9!sF(b<#z_efQ1@uK)Ih$T#}l65NPMaO9hlZV2vwbMKhj{wuk<A9+4cFYce4e>I`@%m}7>?`Nj_>Yt^jabK`faI;}S!Tl#%5U;w4^7DR8`Tu03`#9f+&~}+E1^3k*PuFz{tQN-?$^9Ac(tNnIS#V#`8N_kFMoYHtvYmTt+~4ou#ZC+E`K})2Pxy}N)#9n%2C3=zIIWuCo~E~{op~Dyu2-omxK{Q)<(EiL<<zP}{aoN7_0RK#j`BTiQqX<oJu8TRQ;+f|-w@mr|AP9nPWOv~cl%RtBVY%O<99s-_l5o|xV}K6^Ty-@1lPtS6ZfTk*LPDnY5EIp77L~O)!qVh9#Zwx1v~d|N}~Mo(Smy-4+yTOY)a=>T|c7sY!9dV?O8GjuC@DEaJ^<Um0z_mwI@R?m0#vGJr^+J8jWwNIKh3lFHre+T8MJ=9O*CGx%nasorh%nl<Ez+O4~Iz8P!|jz9>gqdX38IT$|ci{+{68X*Y;hT0`s7j52iIRpmaFvpSsm^Y3{gU-vww{2|Gxe*))HJJUa*?dq)4e(`-3I$w%=<!Fz7?-{ix>W!m4`qQV>4^2~@ve&C^UPkrSN`1;+uYO<&m2)|p;O5^8Y2EMyiFqrzJnl%YcbzP_mcAeL^Iw^%-sV%NoTz;?zArLT|IA$F$k#%0Qhwicr|k2`*q1|aBXh}UksnZ&`v2cK=Y@V$T5zN1ZJN(l7YOeCvmE8ODNN&XYrfz{(fY(aC8>Y*ETM98H5A-C^(LLSFJ3|UX&XDr(N``P+^?M%+}Hjnt$VNI#QB5&T7uwm{V@ZHd%t?@$Tv185>NSz@=K?temHoE&O=sKh!I>~52@2Q-p;M-ISRL~hkSs)myhdpM#-l1{8|6Xj(W|SzdN{f9Y*2S^)!Xc>wd<=MGkIV_XGFq^{C$S3#mUZHKqRivLWTKPonL*-I)64Ni(YVLIdibN(Ox|9@2&K)7_=>gcp+?T$XQ+Z%5@f@8Kw4TiS-o&p3~^_ecxM@0d?;&&|bx8;e#5?irbz@^`PG{OPOc`(0`8r7AYAf7@%XoqKC<c9ic+_YJit#|}sNT7jZee(`W>r@THX#}VAR&Iaxeh@}3Bdr9|4X8ByXe<pEH@Cm`K>zNHtQ~6<6sXg~z(0PSFGqq>Y4I1Ao6~zAHd6bd*=jtoU|Ku618*{%PZvIR8Z_CheEjTBYb6*qByJ_X>ZL`k@$^B)W+&|_cdOi-%Gnm_6Q+}!Rf}0sL(f)h!Ic?YRoX-5lA5%Zi$VFT}f0*kj)dy}pKO_0@0z!=<1;zbL?arwycCH7_p!;k~&pEhkk8eaE^~1noj(W`{6UB2xl3V9Fl6NoV$d}LgNUlEr<84vdneWlW^H(aD-?JpQ%2D#I??LnGh<s0@YL0T`b5@e8&tLfh8whT#R~;HUxV0`R+`69JtP$}$4Np7fdBz3w{A*leYL8s6+Qc}xtk<V-YaROlSM%ldWXU}#dppMw-ybD^?|Wsg0W^=kx=-J)yRW8lv>~*;@_PQ5m9)K&hEjXv`P-3R^nF(H?Oz<Q=ljP^q;>{0rSB1Yek0y-ilbgL%~q<n<_v0op*T9OE$>g~)!^pbJfa+b-p!7D*-puQ2}`J)>n%jSr{!9zchV-}^7>odesn&s^2x6q+`2xg<Xc?Hx2{_%+`4Y5lw)zVoS#GK`10(8Gap=6xV)|_%lD>9@w?bAd0o`p>&i{ZbL9}+8<5daj_>PYg3Ifr#>Dv!F0YsB;NA?SiBCF8<2a-_eZN>xU2rqu4Lyfnyq)0Q*Ubd?<^P(l%Y{BluyfCor@QUkf3U6KT6_ZCr_LQr?J3cZ+L=E+J@1jUk;>V!oa&X=GttkITh}usU*Hp5UdOh^D=_$X`~GEYs(VJ%JDRvUPu}AwUvhPxNUqM4_qdX8V7%lwN-oDyj=N{p8Y<_f5W0>U_K>zKSs3w0S!n;A^_2P{CW6Y5*AwLS4m(cuPEAJpb?YT`{_r4y#s$YyJ<DprJss{6ue^?)yZQE7lAW8GQWL**m-ygkj((QMJKdM+jJ-XQYw@vyo5d&7^C{!Q675`j`9OSM*2+c@|KlN*v+4znOM_+fJ)-M7!99tyX?$a*6JMB(o~!M8m7b3{m0I+V`9mJTy(@=O|E&I0aJ|BiSbO`m%K61>?W?h|_V!C|#_f!C-CpxhtlRb)gYP=><#AT>_ns?m5D@29zRJyyLdEtQ)l<f~)~j%tuY0cv?myd~wztmbbUiA=UBP{YQ_%H_&vOf|%}RaNtvxE2<!j?Jo^>5}h0A<1pq*>^D%Z<L(6~JB;$FVOjV1=QXVz+Z{=L~;YUlGp^n5M2)gEwT#u`VyHD2JJkLNnZOFulHo@a00jjp4PUqttRHZP***+1QZ`yi+3zQ>xylpoca_Qylvrk$Jp*U@u2$<NbuwHv|luKlBMtAFa#^Z4?<j6Q3k*v}-luA^3ewMJ~0zE*J0+a{u3&#@JB9(s9Qyz9JDxK(fQ_0*n=S?GIrRCV#(xN&}Cyj%ZEuJ*s4VH4%|y-mlXDy3uWT+6*fa9^*l9o&EC936M+m85!8ZKn2IA4=b+_TD&d=US$QG#<AKY_oGCY6;z!AJCMZzX;qy<<E{3`M!7b+^zm3l*S9!B|M{w#@M-Mo*}sJWFBfyH2rSIdQRirb?X1QVN@@!Kl@YGjdA0~(b~~=F0VhU`I5_g{StAr&3;jicYVcmZruE&>?%9=eSrJ(Hrwr1j^t{-sc>V)0Y^Xk=gbdv@Su|7xake~+ri~^MeSuW@m!bIHNthCNUqKkqyAyy<JO7u8NJr$+wI&}svrHXFlAo44)OgF*YTBH9bc`$QEE?g&P_Bgx2>{s{ksX`eu`Jyzt)ZGAK;!;WyCzu+M|5jH}qEO9_`?`Kj@iTB*vAGI7#!N{4wHxWTE+g?DTFsH>Xyk`TyM^2iHd=BcA*i&9CCeX+Gaep#CqiY>l03%U98Lwym2ST+cddw;Pw&;l2Mv(e~au<2p|)uFMn3)p?>P#?kneuPvT~@+4fN{pjF%DkpEKD90b)(zJ6kWgL~0V}OI}r3;JmOmD|Cq8xMA1?q>_8L2&6<3xM)wF$2CO>%X<8OtwGd;DdnfB#Lf*TFBH+wSO}nTf9BD7iY0lB?q=xhHHS{f=yHp2K$T^M%uSX?J{|o|NP|?vktHZsjjsLF+(b#lv>4&IifW`C#!0^n8o?yc4a@zg(eucZ{U{^ml`vM<05X`e$`BF@D~z-Ap_8j;ct{)i&?p;PSeeo_P_i^L_nP{*ap(SNa{E*5D7~kJHfnxPkjK;KufAVtlnDkLf!14>zelH-16q104>9J2;-hl;unAFIJDfXBE9g_Y(@;rheEOPUAj&+DQlRzK-~j%8?F!YM&^_^L(VpH*?>i{@*{6%FjE*!Hstr1^1=B6K?0;^SgK0$IA?QK)gzII$yc`Cd$tBtObcLJ?!9SfdbC_Y!8X!zP4Q7jC{n6D#YcwYJT*H%Ex_Yx$YU+h#RrQ<$9}fx!&sMp195v$<=vc-X?CQEhftG|2UTB=enoF?-TdFO{Dh65Z4o5IL6o5@`C2ipiYkQHP^m$omY~p^Gb4cUP*3l3U|)i6|XSvrD%I10#Devu__DI>;Lz-gI`NW`H|J=_gxELQ~7wF(BH1tQ9Cz|;5qSrJse!ym9)pswaIT?=dI*Mjlzz3s2l&f&VP$5^IURup6e}w&biH7$<=u)xjJu+H)+qg^^f^9-8r{@mR#*;^IrOMZv82_+MklE{b?j+pmOe~qxQWxBCfj{lXD90FTIYoC-x-qcVALIp7)UZo$1R>yk?|xzXR8z=s6I%f2myVU&cM+*7G69jz-(Le4fPGf9K^nXWvhK$Me&9!nNYm9_2h%a(TY0e}K#LPjg)fDqlI@R=GTXmRvpGR=Jgbj<|ZBEV(=%)<3|l^XKm0()?Vzi@tyD$V~TX(lw+0l+P>feG_5l^7@re;nwqt3O81~-sQ%1aI2gm-6+4&MzQ{Q>#mBnbFKDMx*k>biX-1lx=Z~Qvc!?^Q@HkJcgObn7QKkEb5HBEv<_!J;K<jzz7p;6oXY6PH-G9y>*P;!HaW`al1RtV&A)E3bAQ|R#CHUR+PN{hPPl!$ta?)gQU2<JTOIk$|Dx;dMwduO{+v;QdxNJtxJPeE_p^T099#o86z&bLNad%$>ntDKOsDXk+3EgTpT^F5!Tr6R+_=$EtTUbz*B#rdy*^9p=dpH<eBTrL{gJobXlMJEzoNf0P%PfT&1J;BDnHwh_^m^Z@zt~pbbfyQQ@Rft)7Q~XIlhw1cFOUUT((n=ua%E>%5k(f>XrQ_xtz~(KIjqsh_9PV+k5eLw1Z>2<oFsJ22lHlEfV{ecivYH?giH+pFPO2zZ)fPZgJ!KlqK8j-17l$UB_0+v7Y-?^34x$xo)Uj{{WZwNA$|)wmQoH0GH3htL>Crzgf<aZ+sx%Q1d4YcD85wmIynS?a{!^UPE2iAIa7ANAma9NpN*tvdUN1CCSxw$tqu2m#p?E>ynkPtV>qDvMx!kfqN9Lu2+()>ylNzvMyO%S(mKxm37H#k9vHO+oh~mR=%=cNv^I}Ryp7vg{$kBHIB+UW^rX5v&vD{F)Lp^KFW5gyxlNrXPbNU+=%B72luKxcrxba1maKg((&=9na=&I-+%}^m-~xX;qvbZn3bE;y8YcO8ZZ3)0j*T7t#+;{T>oM&@phlkdBsnO5pLWBHy$n^-mE{}FAk;WZ_Epeoa-dk8S~U)M>%pmF%SJl+a-UGkM%)vUE$hLpJP4uAB>K1<DPKhx;L2m;Xx>^&wXz#b>se9^&I(z(a<$tay8$p<Qo;&V4W#V{ru}FTHms+r*<x(>o&g9Q85mV_05NM%t*b#F^>L*QzGnKj-yZEvR;4wQ#4PKHqpGwke}vHhE$PuZh-3wxBhNJrKPmK9p2(NuKBCe?|dYe$0?P|`K)s5_fz0Tzg@&}AK6=NJ{{jX?RFeD{e>1fxb?fO!cH!ak22q=y4N|+WB;Z7vEY8npA=2y$8U0QAGlBQoCh5JsijNUYUhT^lZQL@Q)|Bfw|*}s=Rdet<u8%n`ZV27$8l3~ufp~1hiSa3<);2TSc&G_*yE0JJpY`Iuya|CCV8$?l#jn-<7v2%_V+fYocr&?#u0XI{XGqp%fI`PX9n?x(ZpZx#&dTo=sYve85$S-9THD)Anos2Vx99G$0Pk+9F>FTF?^?jDL*!z`oH{XaUI6@jJP=>$#s2Dx!m6+*FKOhxlhSg*Atbi<*Vz7%B}MIT%mcmyF2wm(^GVQo9s`=yz-nhBJ5nwD-GQ6-*(J%&%T*d{_(rCU8fVMoYZ-UuYTazPp$b3ZvF1>dYVW(m%nqg<}<kUJ4eYEJ#;;<mfZ6{aH~Dw>Up)~=KsLea^!q79zERZXs3K`N1n%SdqiA5-;!8&^&uCo<tskhl@Faa$&DLh|M0n$uhm<!(v_EZyTO%bE4kZ^o82awu3Y|IP=)&=Hym-}*8OPk_wFx)zjuFM;aXIy)vjFWH;ZS8pXA1kS4$oJ_TTS%LRPwQwcjkR^qbXwrQg)Q8>w=&-`;y(V$5Ue&)*Kx`OGUL+Kqd`^`b9m-X@<)*C(SE6aVrh?bn~}r|0($=Z&;;1Kb~_@aee)_ug3Q;GT)==|0N*Fb9`^U&uQ<Wt1B?6mAxNK<#{c(9uqF(gxxg(#AO21MUMiGQXnoE7J4!{uaaNxcvBy<9O$r^^o|@x0LUBL-z+~kEV4j<{j00`D5ybWf2i}?mrqv+dH(4gX@v4=(&Zqk)aNr@;F@wHlJ*@b1kqQ@znchJ&Dlh`fls|^c+ZwL9{;i{`kD>c!9q+UXrWh1?~m+DEz%~1lPdLc?ws@7yP|(l<f!iDg3?hmF-u?*UDGsvr#)0wMU-!%J2L6(-4=xqmMZlVdwJr;*&gkTEXS<#k2d6gImA9R=7NlsQK3Kufg@H+0NVNoA34;YG+x`dHeqB`==ev=UGLmA1;T|adt&x;(2ONzPiq<T&`E(@2zhNm-%KwUmCA=)9HEdLm~8g(Tn{k|6Z_Tz0%JPr2eVBgpNl^3ADb&4x;wp??T9R&&)QBw(I62x^KF&58dyHo=^1_olN%^`wt@CYnyYsu->ZNY+fnMm17;2TwS+Su9oxOdR{ixQNDE?SGaXN0)OxLrE-~{@jjJ<-*Xuao6&QCN1s#wJReHW_ZDtN&&yqHbU|q2u~bf2Vewp`F}t<kzK|@`&dJ5;dBpNvFF4wX^9q&A^9sq;<EhHU@wC3<ud7G>ydq7xGMdICrItzS+|Kr=)j8z<q`LoU^=_s9zy7p(@#3Y*{NMhzda8f`wj{F%VzDMj(^j)skKleCbOSusweS^LbZ5~S!F?BK5BNQ78~3x=h2TCE!F>pV`wa;0_d)l-?}Ois;C>B@KUw_2;t`7{EFQ49hu}Ve@3SnDSX@VNe-rvA{7v}h2<{(4AHhF{e+GR3{{VGAL-{x1Z=x*jP1e7gS!_aZzn#U20DA8VbQAm)_#_tBpos|XH$peTZ$)`g&`9_w_&*TbUxl84KY{wLBDlW+O@f#0xPiK&;G<A3_eTRYErP`v1oul3+y_IC!Uw}gLC?TP!T-+UIP?Vc4EzcBrU>p^K$pU|fbW3dzB4o!zB7C$1otbTQSdq0wiRSiB!E2E%+PG`JTkJ#4*e89JNy?cvLL?@v<Q45_%B(!V)2&6b7+b{^3UPZAh=HpO%KoYW1Hviy~F2tS?>_szlOeoe+~Z<`W*fx{67fppFnv#p5Qh2sSw<M0!<753H(!*`xnz}Y;E|AMF@-SEEcoyvDn38A&aHZt<YWYTj6&?eegR`&Sq!`{8D@-6uJ}sA#1}W7P*5+^9PZC2<BmNhxuD9axg!I?ZY!Q{%0X5xL*XF4$pNG{3wk+GakYHWCZtfptIm-;d65k+%I4;4>}*Z2!1~N00j4gSd2m4BM{sVXVHjlLq8S`p(EfM!Z$;3KN7+HaA-exu8rV_!<T?Igf9VKl0`9;TLZy;69o4Ip(Ei(qTGQ9?uW4$3>^X;4nG9`-#`lP1Heka2fzm*xK9o(2`}549Kn4`1otTr+?R&dfUkk=;l2oq+AOL=+rd|d{~5u3e+2hGLTkg<Mp-{1xPKi;S{<GT_g}N<jdJ%u`@{Fg=l3AEKfq!iv<~z~_&V@sS=r}N$0w+d*YgSLs|x=Kd|?FlKOneo&7wGq$}E~g+rxXIeWC5)`@*k6a9;*m8NM>gErZ~`AhbDrLHK&M`syLL?+NV--xEF<!Tmu5_lKaX;8&sULkRA}S=5L2L2!RLkhBc^S7=`qXg&CPXh#(U_iYi}uS9Ua8yXBBjJEDZa6cb<2>uY-GvC%$?!Q8P^Pz3w+oHbtD04nu^R<<)qkKKRisL^&4|t689e&<ZfxY)Fi>?UnyCJwQkKn!>v;urN_>Rcud7W6SXXUPCu@Sl%ek1%A1ou0kYvH+u!LQS(ti53Tz14`dcz-Q&xWB^UDvQ5aTw-yVMIwUxTL|uNKrg}HfPaYK{yu{Hi-=38=L-B)Xrirdu1}%Y;J2`T4-MeIdDpaUIJb;|9)gd6Kh9zUi;w{N+!pvy=r;IJ_^l|HzrGIL3g3jy<K`?HBTln8#$q{(NEXeYr{PZ{uNkyCd~=+iHG_7B=h_iIJ*zJRi*zh<vnb3W7xXLmT<|%dpTp;X&%`1t%E$!G0G}SOWjV4Q4>T<_9eg^Jl@`JMXK0W7+%p!bS=(PgKZ57M{TpaHcplvU%k*!2{xLrL4D1H;8Q6Ys4VoIB2lt6gllZw7^B0)@8AzHHuQ|_(;64qMe<lqy5k3)Rra^F@37P?(D{oUK=pXPrxX%pz6Fw`-;{G=l8(AzuY-6#U#R}*S=r;I`_{=8g68KH<TcFF}@9}eYrgx!v;CXQWi0NY%`It{&`ehLLyiopLUg#tENBC@B1oye1IpK4n?p)CO@I1Kx0{Q^{OO(a^RX!h>UV&zT=fV9=rngyq&iqBD*8@p2;x*?P5!`2o^3P<)=d*xkNBQZY>EP3$9qFNdcplt;3cU`09rb^Tdb7j#$2n;~786-aV=)0b1AZ)YDs%??B79~vbOQWnc*FL21Ht`B=u~)K_d*tPQRZm0X%PHi1oy+B2K-QzF$BT=FVJ!DTz`fC1%4oOHvDX~VIZ_0d_S~fAapSNVAMa*){cSDA@G0m?_MlkBDjCf;veWU1ouy&PvGCO(AfCAVOoi40~Sr8{B=nL_eG&i;rVBVG9ARC6pO|z-UX5lfaf|CekeY}{TtN#4jKs0H5okDkKws~1RuvDo<&Xex*Ch`ShRrh*WVzx*P$)ob@(<2?t2AMS^HV+4Wjbv22mYcU!gu8+@A}ia`@+4L3_csg0BS)gAYUbwV*ZOYoeZ7&~xxyQz3_IA$YFe!^iSt2#cSB=sdD4SS<VtXhC=$+!qL<&+yj^pqwp0`)i?&Qs{5q@4sNK@i~_s`!wIT`8vkeD!yj%b)K)~d`(}DV>Lf!f6wAO7C%7i!v6qY8LGoqhOYqq7QO;}IcRzKa`3gGb>M5m{{*c9KZM0V7L%b<;U~iz(DCpF{2=IH_(AYPp(Egj!jFMYf*%9F5IPe6K0B6w!Sr?j1^2lENejd0f-eL;1YZa~9C{*%d^r5^Akqu)$KlUI&%vLEk7v;m+5vhFJ|AmaDHiz=+?R$9gD(v~9Qr%_aQHLO&jQJxfzJ|1njJn1d=6+%_#E(`v-lL60h$xOC@ZrhivkGlOF(<Wmw@jDod@3wel~PB{A~DL(11YlyWq7z(#-H0d?psjpvj?`;q$Q17GseY!Ts0J#_(UmH-V0TZvsCOx)^>W{BO|x@V~(yU=b8Z8VKDF&;N(lHY~b8yTW&Y?*{D--wnP8v?qKI_{GrQ;1|O$fi8t#0>2U(48MxSCKd;v2jLIEM?$0EBjJxjPrx6CKMnmI{xp0%^c;LV{9n*J@ON3<X7LL868;su7C`zAo(K17ps54M^WeTX^c(o%@U5XO;UBQL%i<CI9lYjo3j7g#Ec6I`Ec`L(O88^&tD&>tSHmxW{tCYUemZm%{B-zVpk3g9f$z?uDzq}R3w$-aR|Q%b{vM0JSUiOP6R){Hh}VC@?}diJ?}gt1T?fAdehqXP{2KTr(1q|z;O9W6!Owx844nu+8Gbx;DExT%!O;HjgW>x^+ramQ{~1~Xo~v&2-{CdaO7Q(y^kmTo+Rf%$;WgJ5@MBnvWibvq0e%pRA$WfX-s64+i(nROq3hw7<GrQu!FbK<>Vf*Wc7<<+wzh!wvE}qbp5)vccyF|=oYBY`g1jMUcOPuS1msM>=eeH&KgGtTAZIE*$8{3CkHso%*D7qA+{X3rvJbdFioC;6AN+h4i&)Hr&V^rv_k7Tq@QYB#Tw9%UQO|nhthd#{{T{r}btil@i*Obvq5I$;;JrK0lkhy}A@aEX1-}Q|wi9|7ek%HO5_AguX!P$Os2rOi=<7iN&bh|Nv>L{hYZZ7txA|PD6!71?<({u~vDl6W@X^p?@X_!`p{wDK!molZfL{eaA37a=KKu;mFYq(q4QO|G172<u*Q!vt7CuB@-$QVJ5V{BcAbc2fJ$xAaI_Prvb@0oei{O{RFN98oUkE=9Istwf{6y#w_=)gCq5a^8!uN-^g6|LC2KpU5*BbCMQ1^W3BKV`&=4fcR^z0mEAB#=U5cuC%>}IhTJ`Attu-J|qu6yA5dvlS`{Z_ml%VHRd;Vit+83^vzL5IO}T?;=0It9V~O6Xd6u0HrF(BBX%(e9PV34`u}m)jMB2tyx)A!i?SudQ#m)<SUK2D%rXYisyg(3;TJ@HOE#LifUNgkJ>R1-}UXSEvvESNQ4BweZv7+d_xIw}tNo9Sh$JzBhvVanRxLy`f&H9M6d?Ca@U5;umOt=mhwd&_2)!@O|L>LMOuag>MBN0N)C}r>(x82<{g^x4|!fp9S3jKMOt-dJsMoem-<3{CxO&(Dv~4;D3a+gZ~kJ9)kNF(Dv}{QPvLRaNUC7{s43*{7$s#0CKoaLvX(udJz5~wrw?XxXwm!zXrMiegpbw4RW~lKyW`Ax($9C`g%09KYR~pOQ;<Geps)2LR-P}^>8fK__0_A4Xne#IEDmc{pFtTgM1C*YYtyu_&&VY)`xQ6<lepy&Ova$9l9g%zcq~OKIo1>=l(tqD#uFl&Cvbuo8jg9!@Yf-k>eYNu?j=Z0q8zud_$nJEpi-X`Ktr}TbH?Rg{}_#Z~f&e*H7+OLRSYm*UV{9IbY-)ke^+H_qncDK06b-9)2dgT<5u82VE2BT-#?u<-C)}h@YYT;D3gfYZUkPb*UwS`~J{=@cmGheJ%1r<vJ$kt!(pXw2SK~rOn-;qu{&4dl92h?kIfTe(dW3mHSEq7L8ccXK|Q?$sz{9{SpNCtDuMBSHT~F#=swek4Cv%Pa?QK1&x6}1>XP>gEqyW?nVgiyCAsl23-Z;4ZbUa`(@B0@XO#ELZjhjTN^?f!8byE4WZrOyP*#5J8A4ZmPI=R_pK1zw?uINGmGZXX3!S!Tsy%xgYSUgzN78)ouM7!J0hnuv>kj~jsI;Fw%$WK!*@nbdqg|rwnMwyLR-SOh4(^#hW{C5abK3LkL6jEVbPpLQx@$J+&4sUUme;UzB+s}XnXi(@a<48*R}}mz0mgXUih+z_GnXk)LkCIeFX&f6`|GPE5d(^;Jy*G8GIx7a?p10vaRKy<>AYtzH-ot@D))<Ih0urua{wd@p)F9^>1kwC81^E%d@D&q5^{ZD$ug<W$~FR(BkkFpkE`nFA6OVUxEdHl(`hN9Q?N|Dzm7F;9iH8gD;2A=*a&D?{h5%Um3m}v=qD<q-kSVL_%l4N3od6A_6)V{vyAh!Qv8h8vJDz(^(`y4fr!GM)CVX&?)d|Sxn{kT%e=jFQU8zTe;j%X7MY^_!Z@hLius{tSmPc<xNE!r=p#|pk33kt<$l++&5r-(TGKTXhZluEPAo%3+)ZRjKvBT%b`B_`uJ>bXkYl{$k_(n0pA$))q&QA{}Sqf)`sUf4e*-l5Aa++gZ~V<+`ne=mc<+BzwlgNz;pcv{v6vM;#pjVUV^^`y$QVp&!ZOJ=lY|~*TieCb>X*SySGDkz=yLCze|8dz;DI-rY+CJSoFa-^uZW#f0V^B7Kfon;7_tR#UdIS10R9<jzN#WAI0aQZJ*~pj>TCPXP~k0anK9U^YAgK?<_PHJ{9YWPgtaYri6csG2{L<^0-gM8H;o*K4FnY<3Ea^;661p9eir|w9pjrtSBv;CT<%G%?od0zmKr(|J)a1?|siAqei|KUjM|R9*Ydng76vO(?fH?e}OVSg)fBHxsaC=`W1Y27ByMafPM$hqZ;0?4qp{o7``fe5f+)CnW2T@V^~LIW$XQEXg2r@EY7n?KyZH%8V7$7{%in!hHDHo4*q)<^;rA>{R#ei)KL$b0G}RxlL49${v-C@$1IXVlfidDd7Yp?!FOg+pG8M#ZTJp&zoRXW`vENKuowt!0DqK?{R9@rpmX4lu$ar@FmxjPcowsfI~)1jpJXwPMGSNn{O`z%hK`3X!^WX3i&D_i@TK6ZLu<fShv&x!uD{|~QHlAAEUH1P!k1)Gf*<Fh-@q4TQG~_U&|>ffS$xH!05m_mhed7{UqbW1XT)4e3C#-6w<|BUsVsaxC|_suLC?WwVPl__MQ&&w_}uVyp+Cacg>M3F3eSoX|AL?a@G~(MW1-{V`I?X&>jKw&@Fy{Dr=X|dPr*k+e}_-TK9ii!U+Bm1M=_5M+vXGZIoNxjv&auE06&SnH!q0BkZV<p=QkL?BG6*+`7utpp?TnIV}GavZ6JM}fWS;a|NZD}@8#Gzp4R;DKhYX0|M6=Tnl`vo|AF1`D>U_!&Y!E<KiP(rW&L=qex2mJAK1VIiU*fs`4d&z{{x>VO4a'

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
    if not shape.isValid():
        # Sewing can split near-coincident source edges into sub-tolerance edges
        # after restoring the source scale. Preserve the original planar triangles
        # independently in that case, rather than altering the input geometry.
        shape=cq.Compound.makeCompound(planar_faces).scale(1/construction_scale).translate(tuple(center))
        representation='independent_faces'
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
