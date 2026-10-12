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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_002.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_002.stl', 'source_sha256': '8628b3cbb34fb1b76848a76bc002f35d9a27e25a9339bba9ce7303975ec3b800', 'input_faces': 696, 'input_vertices': 571, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17301487922668457, -0.39099353551864624, -0.141630619764328], [0.13716793060302734, 0.190702885389328, 0.17493638396263123]]}
GEOMETRY_BASE85 = 'c$}qt2XGWexAjOOgNZ_9ykwC@5+W}-2a`-NW&sHU7Dj*!vPoldMu5m^$r*$ZNu;sBfQdrnWEO)B_#?=G$)9=Mea@_Bg#N0(-lOW)IeYrf?b~5ydS+U*Yw4H9U&Fs5+K_jyyBUHtO<ESsUmF%SB(i^>u%Q*ciTKV(%dT|!&&0WHI<;=s)khnqjVKiwHnh)>QZ*f=YWEE(RnAeW@1P-(LwbGFbI_2`FsV1`6+Sdf=tKMUiU<?G1FKc9RL)VQbUDW;$N%zQCYeLG62}e;(0#u@P*48eP;{%p+;e|c`jTNvcg<+AOX>RxDcxDb-;lrcy_vTty+&@O8$(<t<Zs8N>^qbmoCf-uuF&uP9H;dBPmZeiixFR+y<)BWt=&yhy7TS(V^a70z7TP?pMZZh5B&S}-lp{OhSH7tKJcGi;YX!MuY`Z?&WDtLs1yEQEI|B*HGh`B-E)84sr1Nc(7(y4+U0C@9eHLRjyM}`s(OuK$%y~?xA14Xj6C%>sQf#JBA>mvkE-@gibDLyZ4u{kdzFvplbeY1Sp&p*{+G(fQ|}UVzbc6HwGaB)?9T$FpeLnKx?@~t#MkpdABg<5EdQ)h`7HPZ`t&g5S?x}&DzB6YdWH1IZT&X?{Sl>S?g9UX^U)7MZ<OwwTwb-ynSLYu%U*&0vX;tUzmpsJ{FDHl^TD{%W1Gq+awp=SnyCDpkx$nvJ$VuQS+6tu;WbLX5(9l=I<#xW-^l;TWW=eF!N5GJj(XFNf<ODmINlZUmwXQYTI<w2anAdI@jBa1>H2z%uePT$=3(n*@LzrUC*`ld*r@c%4WY-pNKo;Ix81DtdsU#1)Q%|qrXS*u3PSu#7<VJ;0^0Si6#Rp}LqFV^xK8O&S&=`--B~;5W}E)(hRVm-Ru1vAy-iR$`$3yf1NqPT3wp=Js=fO1w20sRK6G<FoV&3}=}%&nuKVCRU<`b)UFl<|DczWmj{W%>^%^<hpB3k$G2kKM97z62>9ug)Im=Fko^(O!h6C3PW8a{yO5c4D{?&hvS9vzwxmmU2_-N>fccAzE1>+u37J8Y&xDII9;Xm$?q4Xp9mF`Ix4*#-?pr1n=Ez5{ys$Snh&=cUVjoq_Y>7j29EB*B!dsUpv`!}lc<k8UQ+*P{!^Y6AR{a#Jz!N^~0Qfsw}GpE5JrI$vYT3gRb=#`-RAKfQ)S7Bp=DnD8V`fSA4oL%QB|H3B@Dt$@ZVbyP8CDy6(!h4`^F;pCV#VB0gVs+>RPwrNFs|AQ(H_#SGJ9Kk`ihnVe&EN6#XI%f6-#?)Au<q#3HRDn5;>!nY`5aq>etx^|fGwZ+yt6T{oX}sPKlKiUmn*$}QCocH%oy}%n;g(XE8@B{{qyxUo&MTq>yUr`m;0^xYl|{OD?Q+M=m}5Mb-`1m9P+=p9{R%JdsKVNPD1?1xzPVxR@LkIwlw-7slC#*DNQgB{2t7(>5W&x&zJhy`nGztj(btQv^w-kk*Z$f%r4wF&ju;oY5b<nYb`hc`D<mM2Oq+D{o(IfO0SR{uj2gOOkIDC_*rXJdBVwfTfG<Wk3VeH*)DBOo5@Nqc@TOo%tP($twl;Nx&`{2bjsgob{YNFrdPZ*e{F2tNy<O21N2f2R6Z_q{qS2Y=mj_rUp-%-{6~h^<3BBlerWJ+pEZuwdcCgv6L&)Iw_nXS&$vsgF+Vp#_t}g2ocL)+<v(BrbiJaQmySlyFm9&avj^gv`oc;3todlgXOC5J<`09unCHv&-<Bx7cR2JWU+h=&w(5*Es=P}co34fI2vz=5vqKNXyw!*OxKQc4FYi@)AIx(-I5*Ds@u#7;iNrVteU13-682i#Yiz!Y^F8l+=nF8PwUtxn9=7Vt$7nkr<8p5)^pkg0|LD{6t+DFnJai6gh3iJZ{Jpk$*r)^a*f~l!4s+i63`74kn+3fZ{PmOFphpcyy<;#gdfPkmZ2FfN7q5P`DfFK>pNnRiuk^Y#ZFzbImq9)eRqS~Vp<cW6UfcP5tK&?ouKy8%_|aeXKb(s0Z1)QHm!uNVwf-2#x!<UDkQQFlmXCI}*$9R10``1rj)9)!Z}$(qjqBd>Og4X`(jU+VXsGvilIl0-_gj!pn*Z*x#aYne2bF*D%RRPwdsl?s_vs#M9PNFceo7BI0(~~-zusd2uG>eK+2bF+=vMf8zAe5n{RVVny3!4IX4KnlfLaG>(+4B|i)K9UZeo5qx9ql_r=DXmxDNNOpmb;M>uO!<y75r0k2F`I-PU}J2|F;KV*+;D&by)C;`&M5%+q7~AIk<k^daJFYcY;ryxXPXe1+?bHavKaiW48d%Q}CY4JP0^Vd}j8d-ch&yR7ZfM(jgAk5=uno!7Vf%}}}?u5{<rK&<z^+JJn14BKTrPc`57)0KZf7o{6@%3%G!>o)rNx7N^mxbeH?9K`W&y32Y#YH>+ehnPCgU#Gb~S@$7M>2tf`d87s7q)Sw~?l%qVy&YH8`bqQM2LG{xvChml7~{2g6ZBKtj@tC9>!Ht>tnzejDh)ll6ZFk(@VoCIU|{_?>$p3Ow3tWTYR1{-;j@46d^EF)&EM!*4gLqp+5ELPm7sSn4SmlDmA}?{HQJk80{N^gsQg`rwySlXHnpg&U0(kOcXp~cf0af2>IU?CiAp!tl*c?A{|e*NY$g0h-cs|>c#|FVHy8u|laHVmK8-l5+U~T@L-+i4$Umfv()C5F)x6a&oWwdbF*p1t!QZ&C3ePX5-VpQFt4|*Cql)uOYpnN-N{CaqHS`;QK%cS}{V=)$^o%{!I^Vss8}#h=cPKp#=83lUEXJ{s2YRVHYW_RweYVf0_uZuOckDN?j?1)qhjrfS%lqQF$<#S-jT({A)6GGgZnaduI6HoUb#&z}&^NVF*9X1hLBxMsdxv$NXxAce{+0`dz6#@ROgMMcrgQ$dG7o_NoIvR2dw}uR)boipCl7S<Ir>6#oG&xe?XZrErsu))+OzwyD$kaERR6f5>LJfVx1d+NjQi%Aw9vOSQo8w^>&!X{@gr+O=kuUrL<NjXzZmsAr!RY;#?>?Mx>}cL?|UfS_^Pvdp4AW4MgG&%D&3iBkeaXh>RyN+7q6b<^;tzQA7T&S{(7}6^lAxe99<)hVxFb(Q@YcqLxL?1b)(B@Tn7%6N4?tNt+w;mRSfHza(lO0``<CQAavsg=zLz*Zq7jbz(}Q=&#mr&+USSrec{jd63%^hQE$hV(D_`fW$1`FkAju1U%Q0olzok$Kk$eC<)3&?JR7d=E83PfTa=!@72Z3w`4s+92cSp)jpva|H*kKr=R#i?rsBK%=10GUjDfxgx*n4W=Tk@z=pXvw_o+3=|3pdX=5xW`$2h-YGD8o>xHx~veo*Owm(+U&^FHPJqF%gB=Q`P|e{mK%pBFrpwyW!)=HD9n(w`B(;uO3$h$;kq>=`v*U7uxxzx%}|%pdfF>s}3Y9nr$CDcxzVA9}7wzg;{9|G43}Zw@<yaSu5Jecm<PA2Tk19up4zWMy@Jx;o84{OA_YxeoD^Z@a^$=jx-b51yHeaNU?32t6lsV^&wRYy7>9nCGsm>UZTm=+6|oW8aU4Rd?6#rgZ1KB?nW}jr0jNe`BB{b${v~`G1#R>7GjVd`#V&PqSZ;=Re=$`L|^q^v}oy=)Rbju6EPZbDGv@g3=xPU!uMD1J!w)QrBy|IbzlI$4`-G%K{0h>KD@;wdz`zjj8&3^%VZDsjE`W$JD*~M2$wh%P>D3zJ53_)^tLDUapFM*7W$)bp29>LsnhOSV8ITUqa(k)3q$cZT_B;53i)=Z|W)ion3!Zx+6tCrtZxrye8W9I-{EB?m6`_pTqNRw4T?F)6H;REPT2F^FJ5f=f91>_5Z{%=sR(K8EZoEp0@Y`=rK6IoK><w_s^zuPmc)n+x;n+S1EL@eH)BRvkZ7&IA8$uRwE6o?&%NR`M5j$qi(DBwR-c)cK;OmNB*74+4D)Ed-DnZPU+tD!%yvTUN0O1o$C!}$;Qx6e~matZmR2ot3`hGJfppDpmgtZ=%w12S3$L*oA;?fHK2Fgy3Xpa-%P}~=<C*5{XJPvLicZ@bn|)H^+yYwr>4&5Wv}im0sYr~c(3U1!t+UOKj`-ltLw1)<Yr#Cx2tuNUa<t;cU5n=)28<xsPga}y@vQ#+pe+Z<7^m%`4IGvdf%z{c#n16&^wri##-nnxSpI;2K6S7gkJIv-^&$2y>a!RFT^_5Q8zd8znY}JW9VJ6u5-jzL_Rk=spl2F1=dUMmHE`VN83;n`bMnx9PJF~;h#dUfOV9!|1pg33zu8zVOW2<y5&ax1q0mH`QZ8Ne5_69{BeJJ6}o%na@+Wxd5!x>h8U$Ar#E6=wR?+xqwakk(Vp4-otYBxyff}O{39kJPR4ZC)bI0+F`rZD&ZXCnSanZsP3i7xAqlDJdi4i3f88hHYHI$b?n>$Z$$_h><zwm&GoR!ZOO@Z~+VBtg^Po+i8jO0YPK{4Z_oVkdWYwJsFL6Cg;cx06`JYWzx--qH_|$Z7K3(eA^7Q&UV;5P+*IlF!#>>5Gk!>8!=Z=UO>V1{-%_#eQgt~*e_j*NLyB&r5UE046T6NE_&>iRI+5A0&8>H%QP*3S^wku^mo>8^!`JAW)e?D*O#eUpx)A`=Rt2e7L&+6}aJ`Mfg@m0D}A{OKO_<)hBzPwd}O|P_x?b>0art1^Cz&~h5jLJL55W9a0-Rr+_wbEUM!tME_)XjXNlGOV!<G>p{M~o<e>yPKC(w$8UD?dl>qR<ol@V>`c9p$+_SRXh$&Qx*C>wx(^l)Cftvp?B%*L}Pn8XL0&^+e%2p!14)4`dX+itp<BaNJ+B*PEt(-zs=Y;e&qozLr=_=?>?z(@K9m3)j8q*HhH*0sg-zY*Pr|>9Qv%U2pGDy7R~-#BsUs-QdAs#Lwfq$*LO{rW{xPqxhZFQyO~7{m`SbZ?)+w|5EvTHuS*tGvc}Wo}ka~qxK`X=k>vLIAZX4>-nV@s?YO_y7~P6pQg|gm*KkspRXO)8za6m^Jo>nUUSTokS#o~Q|Nx4gEqZoL!1}Bv*T0KT^C;2{2kTPrs{9%DgB)dKU_&IAFpoa<Ek{u+Aep*Alx@io$qtJx*j(|VaRheADu~GVqCPy;R;8#!@NrK3ghUA9-`W{GFpw75tRggS23k)^$qAlpQz_a&E0&k@*nhCjiY;AEB5oc2<5jc3iBlEA<l<EN_U17z`WZ2nCHc!L6|>*n1_FD!93Bv8>sv?7ek!Z-J$C%!d1Q9R;l^yj2?mctQA(@Tbz%6#r~90oi<o?BjanFzrk}cubeyjSkGVgxmnO%MI!52=9^(Y51P999`Xw}uWwgJs(I;m0r$0{$Boo<XLyGMtM1Nr2G{4B`;Aofjy>V;`gF9K$4_JI{wa0S-_uFy+ND`3@`3KTILn?-V&MrAU7gcloe)<sRb5-S_lQ;3d;f#;<#e%x)O637qc(r%jf7PF9j2br|320aDf2OPZ$4VZiK<@nJw~l)te=D0PFDKzNW=+$anP!}s2c@h46E)OKM3)c-L&~TsJs2#Hh)*05VUux-QUzx`kT)$dWw8Z-J4HxshQSxX&SF5rfz=6H1(h@(Q3Y$_o-6@F`ucM^V}0U0Q&2*bFK4SPxCGM&D727YSIYk8#cr!KXd&bmKOJ^s5$ekah!WT;Jv8BJ>MF~Gd>;mk2#7iw#M-^c!PXQozFF1J)-Gy)h?dD#?#W<t-9GRukP-x^pD=pq|m+ZL#TiBekO(PecwX;qxUnWf6DhWrhm%!Gbwa$J`YBrUEE*iSo0F^Jsh{7PtJpWE*e0+$O?rOUf9>|DRj@D506-Nm+LX^M~llOq^3J3zOwl{e&3v`zo|P?`0IJrrkanb8)iQJbftgvzJ>Zn?^{yn-uEZeKYHJiLQm=c(fgJZx;GzfrY%qJ`y%%e_<wk*zSp>0HNbbAt2xwnQD@(`_U|~!x0LR>eGl#RnPsG=8`Ya9SatJzoYA~1zNZ-Xl<xTXHuCBFgOQr9UBG*N%}BRW#UH&Pg+FvBb+7;QPn7NmU2V@Zh3?H$>#KBw`_uF>OVQqbOA+6^K3p+y-KxDBy7``e&2i`(u0j7NgPI?nTip>SZ}wHn@2(%;>jj}7?gc2_+_$NHk{SAg5a|4_=iHDNdR#rkxtJUN)5;*e-UNEr+ql1%$`1e2nbm$1^Sh)`WEb=d&9M)~eBK#y7Wub234eYM)k<FBc=c8LER5Lum=EnjQNC~obbjyi6n%nxf^Oh@IM;jn@dEhHHPXGoTCeW#$92`z&F3;xPxCXrTbug>Po*{At3x;UTkd`f-91?CFYxZ4+`1cjmWi9K<EZsoHUZ-`SLu3qHGF@Kor!&P)V=qSg?r&2_eSa7?=l~BweL+Um{siq(u*gm_c?k8&tj|Yy-(GdJqP3Kzr_~++H&aS=0i8X$31tbeTv%arHF5?6OtdGze0CxvG%j`v(Z>LnmX6jUOlqLR$D*REjc(<eRUr6N0z2rZFwd=jX0c&Ze%O~|H$qbzj6EVT)m<Z_A6%Z4}X52augbb?^z>9!GBpH9RDN|`?6ZCgFnBExqIA(|AU?Q?wc+f^4!vVh0=|G5GQ^UzO#hn#q(ajm~Ga6)7lorK7<X=mG1pMn{E{Lbu{u(`&P{NV_v<>W~J+`W}#gH8IWh20DRY6xESY;xj)d<t98M8;@f2GBZ|w1^@sWW?({9p&p(UB+WP-&0QSl3EfZ_)XMIT_=#LsB{>uB<?-5>goQiYu2=p)~_QSjxj{Pu|kH^~1yVs9rtKY#7?e(te9I5=%B-`rMvd(}Wl39(DJ}(OGtsXPern6pc<PeNYc<vpx{=YF2`J1}A4m9<MlF$bxVBPla8Qy2rEx*H-=ZLc76s`%{VaxMDFX)^4AWn_%(GT5wV_e23LSMEC@r#|tKAEY0*uV8IKl~dl$9s^O{?IdQ#dpl*f!JpfSQNTnPx!xhfjF;gKsWb^6+La&&3$5~zUCahcNX?TyMlLO-+O~6@GG8G<*DyKkN&(@57(DO9r<jGMxLD)Lhtwz`xTol!~3kFE1<`v!Tr9(boKsMJCVH8Iv=#K;<)~px_KQArJk-H+IjvQ=388Q?B`t71N!KP*f+cD0_vUKUR}TSQx1GTD0m<JmMI7Fi%ARr)l(KKJz^)?$@lHfJ#(=Sx%0Q!cRQyt+MBc-=TY<#=ozwNUqt#5xW5dWfVk(MVc+%Ofw=x8N2qnH@hBti<F{91o@Qx-@7!w#V88dEa6H%F48w2k+joC`4fmr){jm?;ydQ0Ri1`~e6#DaixNc9(1OM2Wh(GKF+SPau;^$qB_?Jr}pK%@WejxcD#NpqAIKJA0IMWN^`!xTqM8DVu`M+*}eKYQ6SmzxG!2AjN68kK9A9SBB0Do-~{D&mr`}>?;@W1&S@!2kCi}&cyi)nEm<^9P0mit>x{aPRFHz=16=ToNa+;@V0a~>Fu`8K3De)I1{9B*~Bt0dZQ7+vvq8Ewa4+^IYN+vJ!{&srHe+oeByg!AHPBm54Tr`lz-x{BvJPdCKp--&4E-^KWcA&$AfrOrkCokfKK(1WXC-$?mEtE{?l*nxGFsh^w-e{<i(LAE#lLR+3j@&4E+Gkyzn^Y3Ej--Cb6MCj8x;{NDvggo6Bpf3x--({HdoVszX1lM!ai$8{5st5XW^J%-@r^PXw9$gIgmH8bpKY!bZ^E56T>qv7Q@^~874|``qH}78qE3Q1;&h}SirB;=F?I<Fjn8Z_#=CAebW%&~_DawB)rv4{n{j2_e{Rvrcjo|<5pO97b(X>j!UW;5_$<s#gzlp)*dj$3rwu9J<d<XeXVjuE1;+V=lh$k_KT-G7$dP}TA9w#tV*pI~C<nKjUHG%JlRmpb=3=_7S*q2=9Dsz5GtVkX!(B*@6xY&k0j3<w;OzcB0<5goW)tF}}<GI*hF6LQ@@q*b0!EA3Y_Jhnx=KO~JYxZqr`c!7UlE<<gKN91}d$ayZ#46-rY(rmSHF6ho?MVzKUnOjYur<V4<PStn^#uMwtV4cZSY5#%5}o901x5>7O`J)-QrL81D~MCc@5<9#;P1rR<oATt68tw}4f5pzrwDTsr;)qKR}p8B%Uos7_lUK~WgW7v`^38BtC{mk;&gJ^HYfW-Vm<OT?5nlJXmXir4Yp5WP4X3N`*PwG@_IbJ4six~H2ZcYu`YQ{9$%X{oqP)WY8tT?xy)7e#c#xW+P{5Uhdy;!?=+6t3bw@@KXdG6vaXrTr#5r0$9(HC*J$QelX=x-PLgjCHeT2^;zaUiBB$~KlZj=?{}NVC@aMz|<l6;K61J5%fqb*Dal$qde;|J>jtLa_lvsxRiLlawKO&YQ-{2$PkBB8RaV+^J@-4*i<T6*8^Aloea#@G0>n~zC@~zByGjSZbY+D8Phs5&a+t^pziId1>uBF&MiGk!B+4c=YoxD7cFH0OxK8bxhfmn__kjIxHjw9FES7V8#$z?ytoMg_)>|e8Q%hIPT>mAEBY~>i4<7bZD1lBcy`IKSK<(Y4J<~oVF1v0Nd<|O%HVIzh8L>x_?L0Ai6>4?q9(+g`ZEF-Zcd4jMp!VKal@<YN#2-{Emj@(aJV_|8DP07;;Ya+~-*oZt{Sd_4X#P7)uk{>3HBu~ej(-51Gr)6E~iOtCk=6r}af;=PJn1R@W{3rHR0&xtvFLU-IHYVTCw#O5r$XoFEX2g-?V_4rPVsrAwJiaM$1bGze`<~c@JOlf}mzc)Vx6SC&jP-ucHW<v;96xjHMzO9@%%>@HZozz8FxN56tugaz%$y|eFRYEQ0mRS9?+N=&*fru6a?MxMJ_x+!1H4K8v#_JW77-Vc_Yn4lu<FDR@?yeD2+KyyPQFX7)r2i2E+bzq?@7WY5vP!UEi7Ev55%$LQNq3xHi|f!{E4XJv9LG9*W@pRJs0*n@h<s%Ve^CyCk`Y3L|9f~$28z^4g7myBZLhh4ke!_EJoOm#2w`AgncG#An_aWOd@7xVMU2W$YX@f6}F7Hl)SaDR>Hm|Mv|8lR$N#+Vq5YC!Y&A#A?j+a0XGq)E_pxV9ir6l@VKnL;4)5qY7&zyai?o2msp>^vaVLFrxkt7x;HYHjVx=;9KK@x5;to9=H&4~xraXenAa!FO`^w=a}vvwSSGp5t0BuIo*|cct!Lg68?t>euSn({NuTM=Ii7jPv#b?!{*rl1jHj>6>pb&5PoJ-t*DJQ^70W!#=?u%yuuSstBGxQnvo&yu-HBt!yOVz_Y%u-DlS}MC>`vZ+T>6(4R#8|eu@`w-mNg}YlILPsJz`VxiY)6ztVb?w8jqJanLHPdNlPqC-bYvu#_hp4O?k{@wrMikIM`CwfjF4_TgK`@Y)alylYfsVuEE65$-`LImDr42XIVdDSMp{&widA=c~_P-BGw}B$FfeuM&zHftRb<JC6>gh#A@V?SQbL8O5TZOHHabP4Ov!=Si=%aqJvnRJcMQCi4O7_EUQ2)PhO2>#fcTj3yS$$NZ6-7;1X|ZKp%2xl54{9)4w3O#OsVB{jSp_m;OltZV1cg11#VJzCc4+B2j9RuhdX>gqTQvgJtsgmDD7c=3q>Tg~?a)m<7Zn@;kz=GVWEzNo4(n*`~s5V}751%dQjilgqZ<VO#GohUC8r`>(KT#6QV%`=HF9c#S--56S|F{^Zwq>>1(}a(|X(A)X-*;IX-gS;*zFvg`^mm(RbkBpxOvkjvv_*?;JBm^>F_exQ%kKJZvsmO%Vqi6wChaVz<MSazDYh5Q4{&Js_PC$MZQ@htgUnS-zgKHw6QiC4*!$!`er^M(Iga*6NwJDL0)x%3YaK4pYuB4#5m>x;59#7yLcSeAj9hP({RvJo?oOZ(dg$4h)lUWmt(C5DjyA;;1OaV2J89rBo`Y|~TriJztH9pn0u%eMW&w*J9*lKTk!OJGLgKjdkBQI?sQk^H3(%6#dQnOv63V{;I*_=0C<Sx#aOa$lBZC*~xV$I7xS^vUk~Z!C$qiMhygvMhj@n>;(q{D}eNSy+~f=x>Q7u^=%oc>v3b5(|?1v&=y(N}h{ld5I44p`u+wgtaGjBp)Q~8(|T|!Q>I-orxXDJCk=Jeop>1V}%nV$ivCI5<8Q3CGSG)MBc>`uM=ZQ-kryEBX%M0Mm~`EHF;4@zQz{M8N^cLp9;$_tTeF%`Om@(VLuU%lBW}vL0(6R*~v?bKCLLMI<Xpgps)(Uf{9hhKNVJ3SUF-T@?#>`Bf^doPm%v3?0~Sd#M9(?McsLXWg=!JUnOj=utmhh<ZfZ}g)Jm5A)g~+{a4s!!Fy`J2%^*_&q-WDl=>1Lm);j##+gk`;(JTnORPuYZ2HQ&zGOXL(#NcO5OW#CvYyN#2kVzONc%UZ#XcxsOrM<0D;;x_xY&~OdzQavndCCB$t;t2n_TAg5A&8dneCH#O<>*==yQoV&t%>+S@tD!&cnPV&ZMu*YXS3KK%X4U>k-@Zh-HhJ(`}aDW|`#jlZ~IS0Ad<)e_}ymA##7BA2EmJIEgulImiQ8R*0CByo|7X!U_;SAumHLM+_t{L(E4kX*o_}VPZ-00xSz87A8L>?4+=L#J%LFh`$gIk)I--B%ZJwC-ETh1o=Le9U>kizc2dxnVc8IU&-$iuM;nl-zPpJKC~Ps@iOrt`6ZTJBwi*D5@TFbSb1U%@*rYKVlna{VohRY%W)Db5i66IXIU{~CGrBoN(d`XtU_LZn1`63ya2HTF`wl)iA9L{$cwWqKd}h;KGEjA!V-z+$oCP~6Hk)wBkm=xvm7V!1aTdCBFjz^Pmr$@V?0&ZTH-|Vb;LEq)#U4lQ;Bmd$4QJP&LLmRvem?B^7g{|YVyC>0hic?IFh^z`7mM4>EE7QVjE%?@;2nsU;Y!_s?{gfCih`kV`6>s%q(j_Y)tOUvf9K3<kG(2@e+HJXXY_JM2)<^u&)^RE5>QeV|ueqz1ha*ma;a)=H$Z|s|~R+c}rp4G`Tkx*p|Er%jy!H<egd8f>@W_$z!V%>yX!FSun9Wc?*`+BnFeWWmz3!O-n3^m55cygIN|ttVCXuWtE9R<aJn9g;?1VOJWvcHu4~rr6*<~ugtQH#PsA<SeA{Lk$k7H{lX5AOT0k5MSg+&rm*ew-$^d<9PtAAIdbVgT-Z2an~599x3TOzaWnaDmR%&CCm+YM4aAG&(qehM#5nTZJZ2klIJrmI3&wrHIOlmx9NQGfHg30+$u_lX>Er9~_y77YdjI{WtCQ0DANHm^(!MRjdSnw3%ezUVUCXp`-6~EzU-iOkrF@H|{STJw5kU'

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
