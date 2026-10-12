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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8208ec4c0f204a0f96f41fb4154264ce/part_004.stl', 'relative_path': '8208ec4c0f204a0f96f41fb4154264ce/part_004.stl', 'source_sha256': '90181bf20218c8c7055eee08ef51f7d199733300a1d4dba2044c6dcb2ac312c4', 'input_faces': 790, 'input_vertices': 562, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2451728880405426, -0.4999997019767761, -0.09732457995414734], [-0.007246813271194696, -0.24558725953102112, 0.1355399787425995]]}
GEOMETRY_BASE85 = 'c$}r22Xqu=)c$8flisBXEHw~1h;&%#T{;9JEWOtt(j9tlQVngv5E8nC-m-v*6lo$&kfjJxB-Btu`1aoCnYg?9Kj(kGk8|$1&-<IZciy@4&O7hSZfMphNzyC^{^c`%T(-SW>GFmlmd40p4C_8*Xz#Aw!%GerG{R<NP%i&0Kfh_~Ce1=^#xP@4aJTN^U55l$wg*@3Q8Bo<J-ElfAw!3B9?)svkZ#?D*X`Udyt|i&_v$>TySH7W{3m6L+shR#ZXaX+U;azw?SkXy&ZpzN-t(~5Iq^oS4O46QaHC>X@W{_*3O8~)mD?wL4DPu&N4RHYdgMvj8T{12uf@AYr&4aV>;%4J-vaT@&}7OT!#jdMh*_k0qh6lUJeOyH57<6M^N)Y3+`W4w_~W5-m2W+&+%fV7c-4m*Z*Q;*c|JJ-e&Iag3&n!>aDkiq=V?3HYUR!?HO?zPaQbVBcimiu`07o;hg?%`q+A64VFy3%89qz75#JNM@B`)cG}Dp)LOSfXS#-3v%T7R^C9lAHq}Kj8(vJnduo!%oN9$ue91cDwDfr6)G1{)!7x^2!Iji*^UUi+;E4mBn6C92HL~fg|{W;x1xp`%~A2(mL0^fSbk2`ACQ*Qt0oPYeK3do-#!LOgLMg`EHa!tV#!t{9EzvTtD`tz>GT;+Rng1_Ge-Y`_T{bpw5f9nQc+(@}=X-dSO|H+SgGT!@1`#*I(_Isu)>fGV3a>H2)yl+3Pk1O9s^1;8TA3A)29&g|E%3ZA|Apbo(j%!{dc!{~-%S!rjN1=(D-#oH&9qO@MxyQ2{@y)AZobR2d+`eGFA9pmJt=#>r^?Bd^8^xw!zmGfnaZieg%AM^8D>q~M;CK&?K>oI45KrzXGZ;MCb{y~3*jaiWv$R4T9C1IZf1Pr@=C9lY$Mx)_a`RjU<<93dvER(UA$~(P<>t#zkblT7<iA}F=ke3>h<|V&@ssmtyn9wK_M1NE1@(=?)=Pif87`jG{hl8H9(I4BUUykeC^zSi!+AWgUaxCo?NP*A<E_<PT<_0zD|cs{^o#F#bZ*?N+`c~8Zyt019If2wS^#|Ly4k{ATfX&=zZ9Z%bJubycYb&d$2ENnuJ=CQDECCxIOkhuckE*HvsNqgC--%n-z#&KyP6J0yyLXSJB{hc-_pQ&Y_|>h_k4vqw2DQ2o?<?9><`EBZr_3UOy#uB_7Z)O=Tcd}`O1-@DR@?nD@T_3+RxC&=+EuF7ktm7#U1rS5TC!g?$>VC0pHjNd{AlS&dDWEhj-I)Tw5p4!}u+R{*M{vmnV@g?aKSeW{r1mD2zPT{pEDS`M%st_ZfJ(6B_SKD0tHMdNh`eoA1k=4;p~q?X34HyQ2WOHGXVaG~P8cE6#iVGU(^~;h3Le(_z2WT7ft2i+;XMgFF%Q{p&OT?-LrI_ABsmHBpD~hss?^a)LKauKTqozo*<Nx*GgsVce%~-cs(^_BqbW#AJ(nxoO?MdY95XMw`>hJ)b|~d5_ogYjM*$@8jF~#k)EeMIDwGi1Fi%AL0ITKdW-*y%Wma<9@~X@6+Cods3bAi#JFAi1?U+I{wWTt=Ic<$ErhTaa<EL-Vu5j`(61X^3=YM``zk;%AM{c=zs0b$p0`7@k#F^&#RZpU0>}3&rt}+RWYZ|&z?-XvERFeQO~(8ktb{?^4~ZLo+?7u74Gp{a9r1mYyTae)Y_(bJFUlYm7a+H+zH2djEO=1nMF_^-gi8cB5{7N6!+`DyUR+%k86SXwobUlJ3d;7^HuaD`cv@MB<<hkdDw5<NW|wEiTlpgA>dzT!#uO^<9RiFxpjZx`AXz(qtVYv3pI~3Q)$%US$~|b6jL_padpa%eio>O{D<nqY8|p?S8k7O1m2zNnO|(EfA$3MbOSM;=YM`&>tXeC9LAyRw`<DnZ>r(G)^Qo?F#HhWE8j!^E6l@q2&t#stZ@<X8P{pNIkb*)qgE`AYj%k4*Ll0Da_7Sie%vTo1^m_r$RE~Ox%quD@D`;}|EN-!C)<C7{L5x(yrbGS9S@$LQlOucTOiNuSk2?E_WqdG`S=s`vwse)r#bzJa%a927@yUbYkvFrc;&|BFzmPXH`9H&^Ruep@8dB)=YFKz!S#UA9`{Xq!3)Yg&shInm>)dGS>>+0J$WC=F<IN!PJs70fPTJMtmoGmv0b@6<t1ESGv{bOovAj0zq9#0FPO_?z^(N_o+r4z$jziPQ2z{baG!N8M||6>$Wy5})(Pbz5Fd2~@zLQL?;NuP@qHFx-Np5ZY0gC5z6<`@H;<8R4DysZi~bKyulHH|x)G>nw$<Rg&w3^gMcv;21s+sbpI_`b2P4l@#`F2Yv9UjR-%_Z5^jjR)&pnXm#iFx**Xf&1=;z*<=;zyXvwXR8Rad|MyJ~er{-Fg>&)Q*&wGQ@B)S==v#D`p(8Rx@|m`L<9`o12o(Wfo?lQ%8u+$C1`YsR+5d0*KZd3LPRapExQBagK{oN&XRM{Pm=Wf`&lOi~qjtU6fzA-BiWL7uSqwd$KxMxOAge(Owk(ej9Ia~%0|{h<3b!^<JQLO<lsuu9i&_Wflr{s%-LPx%DoFHsbEuJ%Ws>us_A9~KNg>{sv~PNDv3v!gz}#)A*buE%Az`4H!&SsLuOd_3l>&{Q}t@tY7|`o89IeER{e_wnn&f8u@oVRGcp8Vz2)2kyUS64Y(~62EnnBeQ}0fA;sQr^SswZ=;^+|JLJmM!o$}^SB!#{|Gz}nw4HFH@|2B9#T=SNBe}A%AFzYF+PJz;Q1o&8Rd!hi~DbJ-s>Jyp7>nz^)u~{tKT8yx7MpG4`9DncPn>nFLB<tpYDM>u-`n}wEymDxpn?DlCM>6j2_MBtW<j4c@E7*ey+RBL#Z&{Mo&hb?)AXy*>zrZJ{*HO?9Hm&-5~_?*w$Leldl1;qc*E?e|-BX;#YhF?wB%7>whyl`ZF?u@lz+@_=3PMH3XkKTF<*@?31I~E>;NKhIzwt>Y{S<;aeQnM{Q8&2KkO?|7vBwhT~m``{waO-)ny#_qvYjF~X0#(^dt4b$sQ2a#zc~zT7ov?{CU`+*|XX++BHG4d4Afd!zj^d)|%ljdze6W!KL2jd#RnLwq-^>nv_3H`;$O-#6a=;Nz>xd->-#EMD3_zo-AuUp0R~|1EAD@bACp%(E-XU;Ec5kw^R2$NuOC@SUi$=a+-%&lA>v=|Vqlo~;62?ZnFe<d+8Y_2r(fsIz(c)|&s~#<_~xe~Y`~SmzRtV*K)3yymxaedDe1V-{_@-Z$Q5jjPJ2e`20{sIwW6-%0MB!2I$%>afmd{QLh8_wT>^BI{h;zdniF<6j^9F4mvp-*cc3`v0OP>Y22x&NH6n$x*j`6~K?@o}umOcMt3FEV+yRcbmUV`r~xRf{!|gI<NRUO5;bbR_=QD9(lsT^?vH;xk$NZMJDi>-IcqqO;+x%kOcKyeIi1*QM8kCV{~T3H;x^zb@{0k;;sA^&)ibEeezNCXJ)YW#~Ioj{du1NzOSwB*ZxOk@O;dZxBh0~uKU5@&7Yz_j~bw#!wRDRw=*FAMh1=d1m#12to)l6Ykxemb0bgc=g1Q^6!Y7-ONadWlQ9YM+}H=6Zw=~P(5dguJpFfr-`N0Ov;RbG*IcFCJn{nh_nzCN{l7Osxu@sf=;yX3J2X#@VTb(sZyw*S=P_v?<;H@o7;kSg>2r`Vzol|}{i)!m4(Ygc_pE~WUd&(bC#|!iPZ98yJiihBQ2(k0{EpZBaFp)Xej*L}e<=(2falwkzk6`dx1MJCmwH{eXa1txRq`2*_j!r6e!ONF`uVQpIvsC^Rw;M9Gc=Dobv`^#U5QX`&lrBy@4WX|tlW8iBCoqs(R#cUzXor=1@Q|S=zh(kqmU;{GQ`Jx9jWoxhob)*|3V!)cipSw`FO8`e)V_V+M~ytp(pZm{uz1R-_W|bPPRs#DH+iJW9_zTKUP&c=vU8IVVcK%wiNQ5<h=B8Q?0X6IvD$HPz>=I+F-v|Z@D$T>U_WZpvBGKyC^re^m6?dH`>{|`f_*FWsK)i=c9bN%i`m0lYIAUv`>xxq%E}GH{KJPn%5EDn^`>ZK6q&D2H*I^`{0K;7x~7!CKkl`O6Q;7wD<=9{GJMJa32ilznk1J{rm5EbrSRHcmDNB<WB$kn5&n8@8Wu+mj}ny;M^tUbN|riM7wP)>az*s#~n8OJ74bT&<b^!omS7I!yStF-!ZP-`@=Ne^FbZu&I)ZW>-IE7zg52AQ`BwQVC?td-I0>Vd8C}%_qua$d$J|YhdT>jL7o48hVP*^2cyoM-`quBY(c&AqMtd6VLdi?NtBMyo5_*?%o~iWIu{RUJ^#8K=XZTguCICQnSWO9wyu|p8#Ue)GeNm&&7bE#^5>U&a{aSc*PosyBa}P(+(({u@r(U<LM4pDkS3bPF}AOA<ChCK?_(Qp*6oYBDfcWXi@FUp@V!-?bm+g8zxMI3)aOh%p#Dp~_qG?St?^M$l{;qLL;RB|TYS0a*chDObcgqAeXgZIeDGmDS6<NflkP&#_G{eFcadje`(1im**1ZX;`7lbN4^nmK3u5W_<jw>L*cwwpUj=1+-2qY@q{0D=4prhUKywJs;kJPeag4|f%q2ZwV%fJamwA_H^(?hn|G)7yJK_kO-oSE89#2-<0@B4xe?kE$7>YWq4CG=?Zx@y{UtNs2i~};-1DX<uA}oE^?MD+inGe?(;DIV^s8Gs&RwStD|a>xMf{R<-)SB8Mk2mvbF9-2U)ibsNjg`#<8)i}r}7j$pMEqA`^`QJc`}#R^W}DrML$Ecpr6${;5n;L)4hJ<e2T|i!<S!uspHKt_E)_hd5)JwKf_*Ozv;Isx1UJ^e&Pr8bIYK8+W(<J=uh%E@N&_5UvQUxvd8y&ahy4U{jNKu+;#sZ>OWzJ&JWHj?md3jQS(6>@9eQ3dHRLmy683sc{WEQPqtb(zs1TbH&2d2e7f8iZ)uaq=s29(N4fLcN_Y>JdErK_TbJU>?b+^MRGz2eO64VEc5D0oEsW1Uhw1aCvC*mAld?Jb-};41^B1bF+*JwhGmWVpUH=%7FLvpE*R4IH{Af1Z-!C6j?uy%s=lWWcl{?l>(Q#_e_Y~tN(@wl^&-O;gqnXu#Jo6r4{3I+??q1d#&!K<x?V|h5QA@e&_yE2~+B_)Ehr1hf2VXQx*YmD+hqr6|<<vOu6`tdL+V647&E?5a&u?~W-8^Sqh_|l0EeRvye7SY~F71Q&15s1A`(CH!$=5o+nPn#_Pn>^(zFVUC4~*OHd)+yrI&0h0a4dM!6d3>ghi%e&b^Q`NsszqUBgeOT9mR*E|5krC72U0T)S&IY<I^};?VvAr_I{{&9BKRLcs5h?M?BY2?oOc^Z*gnfnwhU*9M12J{+7>*{PB$uM{Zqr?vg+0b!z7Af$dg(mj8k4dVLr03ny`XO`W6Hqx*0N)UEb=JztIodo_=}Sv%$S0r_wrTzn4WsaJFGT>W(Xm?!4x_;EgOf_|P#hVx$QKE|uraJ%ny=Wb=w<272B#rYi`jQIT<a6N|PMBVOHNBz4`)Ah6CRC@5i$#5TxNTv064M~RnjL3`gxQEXR?`$~U{o@dSsIJcEW~V!PeC~vcxK2|JU#;~Sy&K2<_5yx~GGR@u9#^Gk)b&+3#(CMKQ{sHM@o6XUn(6Vq<dpu%Kemzf$4nNl_3?x^Rqk|TK|fDj*87F=ct6I)`Zc)TU&d&>aczZiS6EfNr>eXcd3HFJdwNgj`}w~+>v%gIiac|Mu|IY7{gTD)Q$7c8SX$SI=G_*EpM>9^m>pK(J?f15;1f*Lzf+9POGZpC?6==X=;!psdOtGCXIE}q!h1QR$-sr`7roW_*gbF)-nVykVBMbowQ{3$NyHnqD{0<a2bG&=zQ%pIbfm6(-TNmfcQx#Zd1Gr*y|1~}byM!hy$!r}E`6?X9r_&W#8$cZ{+7?PEk6d2Z;5&D@no&Pd(~@Qm${$c)A`vfFjLpz7Pr^ijPWosey4A|qvt^U?&;D@9iOfgyAXdn71mMN4rtxn?c0LaFYkAMaSv&>#rJx5q#mN&{=Tttm!|~oUtcdke5W#4hd$Yg@jR)W-ZzcmA?SbL{jq!ME&nxcEgm>-?csNHJ?P0^8S}%SD!T4+&$zDKny(V?`{g$)H|AWz{Pt@p)VFXS#9QluF9zYhzssRKao!$M5$j}f*Tq4Y2lCB{@{PC8o{Vvrb+lfO?lYCJU#?HgCin23wm~+;@7Qw{<2c_|)YYT&x+B*}Tz5HlZP4*h<=iG-Kd76vZfSW!xodR-=Dj=)^gmM)aL)hc_#t>7d+jTHFK68smbJusHPsCrM}hZEiwE8}oh4>(@Xc>581RM0eO3kW0rzF+kJ*)bzKX|jrS#}HH(saO;MboWH+25@+&{A3kK3#0`q^mH5x>(}HXO%$p(W<!0eCOy91?@^)~Y4G=gJn0_qDg&nBS%!+v3aJcOtRQd4cyBX8jy^P8}D5>u!EIJ&(qOIDD@%FAV&Le)>MgSh@@M`6Nehf9aQ?`5kZZy{>(*6aD<FKGxO6=OF&xbj(ZJx?z1g3*U#k_Xndt*$U&nP~;uH#~8Z=-(O4{tMihpS`Vy`N-V{??$0*5K5<3t#`gwS=U_gWaue@iZbjmEYSl*Kdgps2`~Du-fBps-&vR4jICnSPfO_QTy0lt9<<9wwm0R~;BYKd&pLC`90z3zv<BVoAG~TF}OS$XKAzT*|2kH5Cx?kZvWk`CA&uvDWo|lRjlqas+o7VK_3znkJOIPas#SyVbxjAV7=EJ{l>w5s#zMi-)KZ(Wh_G>dr;>|@xk*9Vf#)<t6zV}a`Lb>teCC+a`C)~#yZq)Z)=Js?rFDpvwdpUc-fy$ld%b*VZocbQXC|LmS$@t#V4B4pHxg+j%q;hM$)V(F<of}cg1K<BxJn;QbAh+KCSUm9kkHrJu|5!Zm{g1^1-~U)V@cmC>{{!CtB<?rh{ZC^51K$56?l<85PvUU}y#Gmz4|xCcFYffO&%fUPJZz6T9LmV`Z7STK3fsW>{>PY+AMat>KGSuCqkn$Br!AxJ8;z;IV}0@cdmPt|O;|s;e#847>;B&1E1mbu_=l@?KVOzc{U?RuePFY*%3aoVcP<Zjuj9&%iV?`eb((w0KJYGI@_kD=%&RqLDt8{eg?^szgy+FrO_h5R`1{Fo<F$Xz!a?9E_*^h*jqcYo`OYeB@B9vVY+vAb>Tg!=nf?~>FEi`=Rr{ft%H7uYRz2|k$1$O`a#zd&@ZINiUUHh>>v?lF&W<`v$Nc74vLEmBhRx!6k22LC+w4Mn8IE_+RlH}&xKz0(-oSe7{Xx9%I@cBPJCowP7q+d@{pR`%^MrLh7LCBXx}Z4nyc&W0Z|3OlOkD4$t@OKo&!BE@cMIjtdh-z9F2h(IAGhAG(CybA;kwxL3;LPmsdCeLe;(gj&zHTzO2n5bi{}o<Bdmv}RafqM9E$b-<w?5!H+Pp-p7<U+#h-YeKl=4@ZCmgE)9=B!-0)zz-?&P}`|s6j%AFU}<9^*~t&V3$wL{A7t*)b=%}U_?)w}7)Z@m|K=|&wo4OE`^eMi=^xIZ3j3Eukw@(ha8=VeEW5dZ!ZH#NUI^4K!XXK}78jP(zfYJa*EM19i5Vm*EJx21k{Fh11#uldtA%3ZbJf&Wzn@An?p1-HI$>bFz(>&RD0x!d9!-VE0I-?S;W<_Duyg)e-$=OFppS?K?_$0M|!#T)W>R<Vn9e>Lwe(f$rH@ElQcjef6Wzv996s}1=*Cf*a;XLr}<67z=|82=Y;>vd#5&{ny-E`OgqbWFH@KEq4={Xx#s$aA3eQjISc37+YDjN4;Q%ooGo;rAw!yW{@oTBpBja$dfP-=8*4$=^*4&~=pa5q_8IY!i&*-IZJG<Br&%^QalJALpw;evF4!E%kR>&J0BnKm3laC*A8#>Gx)V-#c48@O$TfaenV?@xbq$1G)9Rv&93ycTUV7@V&Fe1HX4p%oFgvb7G!=@0~3k_`S2m1HX6vH}~&<;P=k|;vWC{1b*-AuJa@M6Y#qWiwFMh;$NJ<yRdlR?=Jqu`MZn6{RaH*!s3CyyGY~#zq_z_;O{OHdBE>3EFSo~3yTN-?jn#|zq?4}0l&NW7mxO@PvGw^T)%7@<2$bOyfpLsYpY9lnogKn$h)HOT1q2}(WA4^pIQl&f0qC6Keg)p@&DJKT2-i2`v3Z;RvT^JsnKf(=zpW$#I|go&h`x2Ci1jFhVjhn(|G+$8?>-A<PXSX+cs+PTYa{P{(zqm_L)t-qce;~UK_!7BQnv=X`)BckD#7pljX5t#4=vu%6aXYx6W6+_B;J`>ffo8*x>)7786~8zPt@uOmrXme$?W(Q1_vZp?^mmL;aLKeGv3h>eNB-8K_fJr}J70Z%j(B?K5Da574Kk78C8JPfIN(`Vf73YBAB@(`Td>6a52yW@<6fKN>L6S-p0gZP6dHE&7B3Ei4P$qBD8zm;omK1ocq^ZP|XrKs$pCc9c9Fw+TCJKnqL5w&+w|J7|E3KTIvxs<dVMego|fY_K@;6x{X!Yb{#XT&a!M7SKz3r%(F|P4r!w=&STQsjpJ+p^2VDKZ{!Y0BZ3Kyw=~R-Jd4BKDo4K(+lh7)9ywSUXMPQx*l~w`VwAC&X^Kp!DI!=a<DBv8Fg~%mj<->1g|CKHqiyClX82!*B%<s^4WNP<|X+<#@wO*gZd8jeXreP`v&9hklmoZMSq`KKKH<<E&c`lD<A!UZSk+EU$gy)Ci+kMKdAp;U;m`N_1b&tc($Lh{hoRLB$I8Q*udXYSF&N7v_G=JL>Hx(?L`?U@q>NZjp+wdi=XMWaO&l3Tie2!V<6k&Bd8-7Z+-5%*DjM^CtFUogL#)zi~a63H@E*z=B7SO{|EJ9>Nxsa)N#}s==V}@pq@s*h<X}zN1Es^v}IoFMYha`tt9V7-J2$QvDbRAy_hEa2l^w_;vZB0K>djRFKY3BQ$M0k;+^MTuq|5r3+51i(I@9cpFW6Q%Dye8UP`{gYu&kRDYf{|X-gTig7KGVvcK14FUVd~OW%Tm&=#GPZP7MrVef5di+=9a2ARP)(Qnw6?YG&!NfRx6AGZmc=e31o;`dYUXN>5s+$OOOw(HPDccyh^OaaEpcANBvOng4-e2fwO*uXZ4y=$QTgeF?J%t3d_Jk-{_<e|PzE$lhlFKD+pKi#61n4C7m$@c8j!YbO(7F~nwoIJl3$-1*$gXiq64d+G1-CMF(UjKw`;jgIQk|$6n@Uz11vYkNvkS6!JYh+i+u2Juz$^CCO*&Z^<E4kh?=R@lE)X#l#J*Qpc*to_V*7(`Q@vw{g*+-kr^De#{^*m~8Y;@yz5MPg4d_j%@t6hLrkmEsoQfeFZ6W#|Ce8x!v$3Oz_TcV|&S6H*_)K7RGu2cWX_FvT3ecG>h-mY`oWt!;U>Eo&6+5XF?{Rd6-E&6-Z_t<_+i|1#pZF}htQXgddu}^yuP4qIF=p(d)j9<xZM_2<n9=XpfU|aM+wnfW5t16lJLDYj7Bf6H?hLBZddk}3d<AzXMOxm+(q6g4KH=wUYy_27r#kTMgG|@R|wYdLeY+Jf2k0YB6_j|d|=knT91MDf+2%>}7&P6S2h^Mqij4Q%zWo*#zjDOle%>9n>($3Fz5$e2bi<foJJKAf0CNJY^bGx*2(?owt6J3**m+@kCZMf&wW*%wxV!I3DYm;^1cI!Sax(R&|>L%23e7*U3`D_nrVcprM9`rS-Yp^Zbb5aYFc{Vp$ZgSDD$Ypz7_P>bjpEaUvleJtjp3``0VGTGYWPL4jo~+$v9;#-;GiL>QY0I-|TWaC*T-la7hFaJ+)WV*!En1!*zaiUAo|?~-yQx!93-fsWIvdzJen#|H<gz`=hPLQV)WVvwU7aTSOIjz!{B0mkw%_#XLS%*bdC_@nXv_9%Y>WP#TA0)$59^bT&&VlgsdyY2s4aGfeHOdJ{zOr)XFsE;tFv8&CVDvSOUAr05GUJzGtl=p^wqijCfmR9SfqWGc9T4xw{J&f4AK8cEhf5P5bU^D7bZJy`-hz*7ZY8C{uH&C=n(od)MBEG2f@yHbxE>wwtv`paxu}R=`T==i7pic6a9;fakfSO%(m#WUMm&^CcXr9(IB*C`)RgC2M0k5`-yGQCuE!ifr$^ME)ayaY?s<f`<M+@fcz-830vZ|RW__0SF!D+7T?o`b*Qx0`oz6qdlh5$^Ru#jA+<1BV|F0xKyGdCz<r4SnEGS39kdS2k&oMi8PvjLy;+K^6uH4%rPwzsZz)=F^5Seuj>2rqI#s;1!^pxIZ*6<bb!%a=+tePeV?%6UA<SdxP`1lbhfs@`&$TBP)}Fp1O>}lzS;l|PIN82}T9}Jk*d?|_zor%zNi9sCS0bq+*^Z{SQHwXI#ariJwD@S&DU!M;{aWfUwnMq!NU~6$zJ#*hg{ftGGq1JuT3@fVW4kZCv>S5!P;&9|es(JLRB~Y(*`7i+mA08|Bek#t)WUwH7Ixoj+sU?*i=NE3wS6*kZf1K5Sv%@>Y&WEzNIjA5`#$Z`G||QACs0pdJ9!XnB0rll2-}2>W1O&LY>U2OgBE5|3;WK7w&=0c!dg%Zt4!U3pEJoyvR&Dye<kV1QCr6^=U|lAMtkjRdTD>*wbj(Z*H8=lmRi_+YGGrjg$<(?)`nVGD{5h_satV>qsT6MhxA^r{c1p8WLx|%)K|D&^d+`MpYz&z>N9Nb<>!8;7Jrsn{Ap_OKT(T6NiF^q^(p4v%l%xSzQBHnF5^9ydAw$)m-a_q%S$ahH?^=_)WUL53(H0=EGxCJ%+$g%QVYvOEi4PQun(z)Wv3RFlR7*5SB7kh_ZT*LZ5vH=tk+6=%`V61wQ*h>>9zhe(fwrpqz|VbNxg|amVPAlNal*AjpIJI&=02{M?H@F8%`75g}xuP)eq4tz1GodbLcx!&!L`5-;H`I^<?@U)RU>F(f6Vj-<NtC^*oyBrSyZTmr`${4Q4&s(^sb-Og)&NuTB$PioO?hDe4k5(Z%U|P#32zM&FIP7<B>qPSgdc^U`;u&P*Rh-;uf_YaK=(L*3nLeY{qbCb}~H5bDa*PMYY6G|_u#qPNmSZ>H}<y_q_izB_d^^$PmWsl~UWUO^o}--bGZdI^17>Lt{xc&zJqyqW1c(66Hwzn(fXeI~D^rw^s?K;41yq4cY$S8>0g{H*vK^lhozvadO4qVv$Vqs~KJnErF>!qma^-Km4Ai_jOPUgNb!URy?Ak9ryPO!@}YGpQHRH=|xey_miwwfNT5i>X)BccorUy@7rZ^#<ziXrg!1M1MsS-GV0iWBRVtA5#~iZ%ti@x*$z-e)^Ww`Kj~KH>1u+ot?e`b$05E^!2FgvA!AUlTl0kBYl|oq%_eD=_9Gde@iXCK6OKC>$9Shc<nQ<HTPO>n&^`B1E@<<e@YWQh9-I!P4q^Z=(Y6Csn=3}L;o4I_$JifP|v4tOg*1^E`4q4xzr2k>ryYIcCijF9<z(wI)3q~=<8C~Wv)~-(HZC)Q)i&gN#BGzCv`6R&!}@ze?*^~dV$v}cx^g;CF<$a6X>f@PoSPeUz2(g^%VMA)Z*(<PobVo-;{bb^>X^&)XS-(Xri~%M1M&WU5zF>guW?t2z564I@H;yKctDyN?(gQD|Ht7n$%gSKcKHd{Q-4y`byN5Sl{F{(bhlFHk#;941MI%c6s_wsLNB&poyMEUx9iSwVYe|O_0ND>1d+u^sS74)?4BS(zl`>Nc}ZU^jMnc5%dn~5!A!zYfy`?N<EBvD1Alhq10c{m!<xKdK7&*>QU6=S%>kg&3N+itfBZ6^yR3_F;@zj=#=yosZ&y?rmsq!nmP?lbXxiv)HPUZ(K0W|c-=|AgL)UeHIMZ){+ZuIS7ZE_{LBvO(KOMW>8nv!<7Ye5M4R+usGBvi1!YO{|N1Yp|M@4+dWPSBpdI*0|DS*PesX{}SK^Psnl(x$<K25Qf^@N2Mphoi{{W>BC%g'

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
