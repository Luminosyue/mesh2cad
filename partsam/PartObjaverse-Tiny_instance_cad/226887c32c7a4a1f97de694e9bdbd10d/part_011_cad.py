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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/226887c32c7a4a1f97de694e9bdbd10d/part_011.stl', 'relative_path': '226887c32c7a4a1f97de694e9bdbd10d/part_011.stl', 'source_sha256': '099ec03d9f0471208c8e90b9fb53eb84ef661d86f628d0bfd36fcba37ab27401', 'input_faces': 1378, 'input_vertices': 759, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1755390465259552, -0.2473391592502594, -0.39814698696136475], [0.2368929386138916, -0.10921607911586761, -0.26002389192581177]]}
GEOMETRY_BASE85 = 'c$}r2cYG98`?n{6pcE0LD0Km;Qlv>$7Nyw$DJs&I-a&fTl_EuoAVsP{x`JQ>sTq<GdP_*M0mXm_3Rn@uN6|O;o@>^elk>;>d0&2?`*&UWKF8UaGxwa?*(J1nE_;qbj`~x^+4M!A&8C))BbC=F<c#SvV$^_MeMVLv`r7y?=Yeo8e>}e1y5kFNJ4HEToQV~C_Ziu1M8$@_ijDi$uUOSrvG1@Eqek=?+I`rF-hCu*(PQw)J{kGQ{ykpnlksz<dUYFA_0_Ii)i>Gq|M(|&#xD3D7?;o_yfZH*#AN(`xBrPVF`4r8*_95;&(7b!Yq@{@KXKvlElVb5&ZF-s6V9D>UA5e8(IPhd^Pfjlej_cM`)0H{6y8p{Ps;;SyCm3hw?(_~{<vkE>G_0b;^k*w$^KgI_$I6UDYaJ1{h{6A{c)bkk(4<PzH{e5IPcp>&*x1E=l*w(X}P<sq00Ykb2j|n&B}Qwy#4$Ahr@Z}K8cz0;K8R3W#0ctem0O`%l&`%K4{xcdbt7N<Mk)Z(8vF^HhjFn)vi9i<F)YdraL8)GUtH>wZnNZX`Gh3=?B8c<@P(T<>|*Ksrl*9Nju)iJor<?d9Zi2a2~y;%8_uMXIWzAJn&cD@cg*Hj@5Es$EM-=3B2>NKK_ed3AWsqf7n6WcGCM#h_}6NaKWzd{P;$m)^d02J*uC#R8G>yH*6oCpXk+7wLE&@Wp%u{FY9@|55jq{Yd38koY6g0zCEP!cHPu|ZY>#}ALrloiJ5c%k?P_339g#1<<Xa$gy$#tdmk-#%lApJ=BGy;v~9<CV|u*pb)CLP!t)TgeO}9hNe`>}iK(5Wjc+<o_0`O`wcOY4AJr$vf6(&a{C#TPp6sE`ga3)wRloI5Q~82-)%LR`ss4HGQex)Zf1_wPcgJnfa%Wr>HE%`d=;KE{sphT15G{|)n~^(Z#~-w9$5(1@y!Cb8I~`}+&)}7Es^5;(Ptsnu&R8{XW#;R7^E_%@>hq(P`==gN^VzSLHa~$ibF_K$Klb?HaGxwV6P}-7rEe26=jjuRsD7)tRm;73b7s!fa&O+;3q!Qrn>RD}=FQwr^t^fTw$}~bn;2)^&zH)p`FyiMlD0qV$A#y|cW%C(@5rm}FC~A{a;NtRZQdgLUtpd#Z%)^%N5bc~%xTqE>1uzxJea4j>cbzlYI$Vd{PVQjn>T0aP(5GLH^G(%7fv{6+m1JH=If@9ONz7Yr~gm|HJ=R{CTZI#JVDLR!gut%!u{I3MfT_H$?*L6O83_0$3JDhn$I%lR3FZI@0e}gyxg2OFE{7S%guR<<i@;3wr|Xvmz(qE<>tIawr|W^WIM*ZMRH@_BKu>^TV(s@y!EYn+&XXMS>}yA%e;|inKv&t=gr%`Id9}y=8Zhdym{L<=gr%WId5KW&YQPC=Dc~^H|MQvceOvPW07^3+?yZw)Eq6(vi_52S^vH5u#TDA$+G^Fd+S(a{r7Tn{r6s%_1{~^BDuN#d)v8rOke-Wv#kGfr>XgQrJ8#G$@@bu_vRt;KAGH`2Q&9K9dppO9p}W%@H_-7Zqm2Y;<$RhUHXES2R<*M^2h2XY1>~ol;?sudcHPWI1e<wuI1kQ(%^0N{=wa_UiB64i~PB}C1%dO_l;)m{4!kK-v_;}<-saJb$*Yp*7G=5^?#idEsu8dtMk62dQ#@x-PcXMZ>%>%%blNoR(*c`iaM?pKdQd!-CfQ9;f9Hs^I*g7st=cS(el8X0kxmy-q3RY_si7&eEy}rox}@jo|_cWUf11QPW9W-k$S#jyPD@BscQe9xUG&i_uv!Z{XE|`*_OMjPM*!22S*kU=l&<JCfo90!}{8I|5rzkhx0X)Q*60Eb&a+^?v<9|+*$rpiY<39Jf@8g?i_S1d|p23l4{HShhh`8*PS{4XgEJ|G}V>|w{_6RFWsu%Up31cvgSWNsEtoQ9aQVp{5m09?*HN18ErpvcTjzPzDvlKr+19g#z)U@lVBU~<>q+*k+KJE`{QQ29cMeP^a6$AZ1WR+sa~vYo&%qCK43dvzUt>(+j;kL^SlQu%yg}NMQ-+$`)_^M*0)~n^{w+kjuYYi9KAsG=X33nt@(E+wDIncCaV8i-bl9PPR-i-_*>Ui-!^+I#g@BumL+A*{my`J?(6esiY<4JSJ21jpAqioVAp}Ew%lL*i$v|XO05s~v-8sVRBL{|nKs`4)qZvVJzXMX%biWxwDIn@vsItZX%VvJ&W+F+Z9CUrQuph3hJ|do|NCwF_|mNttmAh)bkO#?>H99n+4kSL@o%hc9^Ba_Vy*L;yYT_*d0Ds9wVhut&vJgN_I7Rk<K<cU=aGW0tv@3<{TUonD4YjN-w5|%plZitTkhsKrj3tISgiW?*dNKZ+}&DH8y~p)gvtjjPqF1r{^?1Xb2s_3aNh<N6->3|?#g`H_+XC&wQlE}oodSiRhA@X&eJEQhWplaoscbezAUAUcPn01{d~50$d>!prJd1^>)IN%KJOYHvgOe+Teb1&Te_%z{%)l<KG?NYf-QHqMIE$l-#=n+oNYg&=bnhQ9j~+b!U5a71>%2pZSx<!vX5&!kHMsTuB{)uJWD^^8X9BkH!t`4&A+XdI<8+9pA6@9Urn~<&eI3A@y@Ns!@0jlz7$&?ELu?C{;U+$pL5(4TkhQGmZaqu{Azrsrm40(^8VI)-J1>7`<6EGsn)!5XKlQjt8Tb&o#rh=w%o0)*273Xq_%p$QEXwznirX;k1ujU^=I4IkSz~Z>Z*^A>8n2HIq|DD-hZxff;FF-5^vkSzv^pow*B<p=bOjt+t~krZQk5HJzd-U2eYk;v7X0g)Arl?!OP8lh;CnezpdZA-0QdC*f#2QOVv9S9@nIMvMmobaJBJn@RaJ?8D&yzx%=zgByBq*`i67gjLRvu-1)GPHr`kMaJUbnZx2be<^Cz3BxcV2wLemQIPC9KTkgNFoHjntbe?+u@crzNHE*@}jF$JDsNN^%KNqs)(F2+r<8P_{TylS!Hb054sr!4Mr?fn9s8)h4kFNJ|ylp$aO_k$p`{TY+IM#MtZr?kuZGO^^?uxO_bDIhKt>>%OrhT^a?&aor_x};vYwIg7_xj2|sEc~ti(|w6mfo*NvMqNC?AOQtmPhqx<tiz*+~4L_l9p$WR{d7{w-j6MHm|0Q5A?pP*2$Z1q}p<4`umBQbLVubdcV5AV91*9$*YZb8-1$Q$(idzw%q+?{F%(TfA<pAhpD$iwmh(=l0JT8PIccuSv5`DpGQWk`*lK3E%%M7o?y$}-&V%kw&Q-2H_o;{fo{JZupO6k^q6a#pTMB!V{G&6RL`~FcD~Zv)YxY`?_O@6cX#;9du@H?<z8Po)q1LVYyMWae|)~4$+p}aADvKK^;^5DDYiWQ!p$UYJN-UZ>*4WRDYo4Ep3cjCujE#J+k9H8Eq80LNX(oE+JCFo!#5rZS@TbFY2*DDcB?+jwk2fC-7zE2Xxq85O5K<5`zK_}{lm&=<AZl{tM{3^>ZEDo7mZPUcxQl?NBYpn(+ez*w{6G!e$(8a^gZ7nupO6g=K<F?Kj~9z#n|RKy3e(Jw)5rAD7epd-o4yB@6nqZ?zQ!mmq*sO?L*Z3Y+j`Gp_#j{?9;|O&sJ3HVQjS&TkhZSYf|Pscx_j>f6}+yNwMYLb9W>^Us&ZAW~AD3clpx9%z5N_pXX3B_nxD@-2XtV>bJO0Lbg0OWat^~xISL1`t4ZuG+Q3MwYWAukd{xahZ7oV<0E}oWw@5R_f$);<<aiqc-wZo=WBC++*ub7SdYtlUN+{(->p=PZJwR(N&9T)%O8DbukE~hxq04wu|BO2&D`rNXWay~oxQ77|AgpUBR9vVcd4n?$=Wqitoc8`BxTN>xv}cGCi#CUw%ot=5p8@hUrE)s`_*%wnLE1|C2Fr*@uup-0ltteck=&xM$69}QhnIvi;yk%ml&vx_y4<5^<jy7(`<R5OHqCN?g!L*IIT&VEf4<w&FRd!n`4~%{;SRyZM@f?X6|phDBiYxcllqjw*B-SK7YV=yuK0JUE93*AI=wJn}4TR>^|#xBsb4vV8Z3SwmymEMxO*%=G|-SLofIGFgR|udfnI8X?<(v!RWo(_{ek6b+tcc9zFNxq|CY7`mpM^7JsK$^V;RK@xD`KRX^95lWNO@&%B$c<>UWQ_v?jaL$*9{<?l1v>wbDvt&>lD8M5X6M*Xz$PWp$cZ|~+#v*p2wg|zX}RSK%U^`29V+<oxt)7tCOw{D^FX|~+yy+IrAU;Jo-ZM>J8;{(GM#M}1A*?lM0c3l3ep#!%0N%w7WZS$PII4Z_=zP#K#U+GJB?6dVlBscmY@_c0Uo0psY=CA+H9$P<qd8D83k5=>CZKK}*MsAJ|{M$h9e<P3V4|%Z0G4($7pTARVxjUh(Hs0A@UiJA^=F`ai3l=77+xg*+TDPAq7qaF4>hwRkuiSC9Zg1TcvgOXPKHB(T+b!yI)FFA(Y`HJbgWC8=pC><^X3PC+&!5)jnLhVVpO9wDgE!Y{<GnsN$9uUs-s^vJe<Ig~u|L6Q{)n|5Z~B<j1Gae!ZvW7=&Of<1|NgUo?YEs@FE`Jxle~SOt$)1S?4Lm0B>j3Za<f09$K27c7bExj-`yFb_Vd&x?RqhDbG$pOk;>OTmSW4j{qb@q`gpj{13T`f*mCc9y*%KnsPgycrrL5}+JZ!FJFosvy`RbcNXVLx`Rh#PJoxSjbzSt`9kS+JFJ7MRZdKPy`Fv@%+-YA>8}F=mP+c!`o2A)u=lZ$R+Prz!#S;_LY`MSDI&FO9x-iB^t|Mc7<a#mo$IH$AiCizn@p`#=yuq9)2dwky<;HwE{>`rSe0jNXzP#(m><2G5`yufA)_t~q^K!G_+zzMrTKk#Y>}PlJE$#X;bMJa_dVFKOADOv1-n<`~xwk)FZr+c~+&f+`H}6Mg?yXmm?HKnXGxyd*FE{T;X72SvWIM+F$jrU_k(ZnIBQy8b|HwQW_aig+?k`?$-jB@O9B<x_%-q}`^L}LJ=JA^MDKpP9pT_;m%+2#<-oMP;><9DyW#(qTnfEU<H~ZPVf0=pY{o7kN)$5wiJ4SAf&+@!u<dOR+d6wrLGxy%#l4p6|G4ja!XD>IOcZ@vpyyLyD`MhJ~k>?$69?a(*Bab}qkY{<`G4jasj`zCe^Nx{6o?pnbJntB}IX=ttj**-DljS+c$j#%;@_c0E=6q&(ZZdN7d}Vo_GIFyYvOG_jxzTS~o~Ml5?B^`cQ$`-SALag6<>u#LMjrVbj6BQdU}o-pzCj+m8>fE`X5^92PrTgx9L&fgpM!a?Ykm%9<dM(8yxja8%*Z33gL(77=UwhuK3_8O$md{QZhj7C<dM(8$g_M7X6AP{>*LMO$IRRqpXGBiBhRuwe4b_=ua}$0o8@yhBRA(W%ja)KZl13!pUWA!*$-JhuQPJ9-?DsOXXa)<o1fPidE|O2dEd$Kc8u>k%sk8Z-IcWOJIvhs+}q2Y&U>`)JIp-t_YBF+?>o%g`@X}=&F?$RJo5Jj$<6OO%-sLQkTcqTdf#_U&5>ryz3)3B^T78V{@RVwY`OE#<<nYjd=Fyg{?;FB<IV3!%-kIBeQ#p!kC&VK6Zt;HJYI71c+Kxw%-oz$^ZOSw&vL#d7uUX*F>|vY%<pT=-0U~=dmJ-2``Lf7r2c)Pkw-ocFXvNzdoG}^qium?TkbouUmNdqxvl!VRmBur?tAP`QszAH_1ob*y7G@Hw%p&QmNwqmb}jt(DALD|PqpQd-{181^RGkd`bx?jvgQ8ug|zWbtM%$Ss<tv@%cHYTJEQIA#yRT#6@MdS%l)6%(#A)B=cxCA*~_Nca%c42)7pN1Hd0+jPrsaI%iX$%_3>9~Bv{9jo8tqYe-LlmA1^oe$NjBHob7nM+&o_I_g>BU^m21PgR9TG*7HSfp0D&Bqhf6R;N@BRVSJ7Kwtn++v)=-fUfpNwXD>JV+4siuy|(Mc%f0Kx8P-bm)vDs^dRh5WvMu*7I--pa_KM~2ZQf0`<-QwbwDEym{nT|)cYTUAZ#E$*bDqBaoVxGKES+l2H#^$+=-gM-^>Th$sx9|^&)UoVy?<5LMfE}<TONEik2c=f|F?Qy_vx!4TkcPYKcl_wkge+PbLN^EvgQ8aOSSRt-0tf7TK9R#nx7r0kDt^$!8+c{jq!o1x8rU5<K^c5IA3juvmP(GdAz<2pT*kd)632IjQqa2alX7f%lZ1@uxsmwNN)B+dL!4?Z;{;Sx4@9t7+XJkx!KR@f98*|T`yi9xn8EUQ}dAHym~(B)+O1N2a3gM<AXcLs_QX(krZ3*jJ{7B?+hxW?rWP*rPy-!RGXyCxjS@%`n`ig9a3$1^nhcD+IB7uQlD=me3fd=KYdCYpMI&cx*qfO4%zbHpgm_Y=Yb6`s_QY&Cm~zz{r#E9es;c~esATIOCekCJJeVk?-UrM?o%%pO0(tZzC8N)S@jdF<H^nO{wEK{+xExH&HahK`C^>yc)i>_-eARNVr}#3<>q`kyXqaVo-Z#q&X@nu%C4;+yxi;u@9+7T{pRInzxfWnyx-Q(UY@0&t1j4QyI#CJe7&^Q{*|9oT~6nJsHx*f-RBf?`u525Py9$Ie>~d%iJt*={;&RtpPIGn)&KwdH-2)@&)A1088r_s#^>R4;Uau4J_o*w&%xh@3vuBB{B3+Td<UP6&w?}YS$L2Ve*?abzk!dU#7DvrxUeri67NTecY=Lz;VXD2{CW5sE_@Py9&bX4*Mc>1VR^h3UV#!X1|P<S_v6Lz;xIp69Djfk&k66r?@?_Q_MCVw7=`D;?}gcLVRrmp{60!NH_U+x^WeGh!Z0sh7%xJJ7lrw7;X}Ca5xgi~4nBsL!)w4N@EUkyO8go4EG~Q*e+GXE_Qqerd%@v&FZ?x1d=i|D3uoYy@QLs(d?G#_&cmnU)8JfOI0v7GPla#eQ}HR3_?vJxE}Vr6gZP{HX!r&$9EFd@2T<bu;YeKA5ATn^3OnJ#=kZtZ7hn_o1>6s7;eNa}tbo_X>rmnqVKH1-9IuF%fDhm$@B%O=F3g1&zzf2Aap8S<LHt2Vyb#Qd3k&0g@G`InUIs4<i{ip^cv-wUtbtd@8^OkSBfJ%S1{c1Bx57KZUU)~mCwvX>i4TL5aN$IJ7(M|`$A#1I3HW$Qd>ovL3#Z`Y@Uiesd@Mc&j>d%p@G<y6O1ul~k9Wa4!&h<P3wUR|HT2`H@usjgF06w$#p_bym0(3&SOTwvmxKlIl6Wat5Enj(m%>ZKLU?K12g~3-yc#Tv3#;SR@P@Dv-VkpITj9cvcuTwkCEf$}#CzaF;V@h{0T+(PhvGvh@xgE$E*y&w#s|SMxNsmo2=5BJ;9c=Hurn@fjko3;x1q$Jf_3qy@W(0f%CHh%iE~_;60ZVF;iWj2RVeXCp$~r)uL`T-)i`HWDe(rdCEfsU0XyI=@b<6=-X0IYq4-eFO@I>b4hQ3dnfLCLcsJM;?}oR9ZSXeCX<JJCY4|w)G+qx@#w#;-_28p;J-j}widSV`>cbXzeY`nrk2lBL!2llMINQN)csu+>*cNZgF}z5LH-q)?dhACt*c@-pcEu}ayy3eiqaKC1@JI1#@IJg6UIXUAYv460@qCo{4^gVbuSTg7{|?@VONoCAbK$wzKXEDXi&3h?zll;Mo}ICk@$7iTjCu~f04w7!;BDZecpLmhSPg#>Zx3tW?eUJVCf*T$Iiotk+OQ^GlliJmiRXthclr5Q{5mCmh!Q^tui^*sIQShNhaZ67;s@{;coC1m_rY)QefS<q{A(!l{xv^~M{zDH;!$|{Oy{ONCH_oC4S~bpbNDcPID7#gj*o<G@R9gv_#!?U9}C;#WAX8@BR(FV2w%o0;*&F-<H?lx8yWQ`><l~M^<Z7t3GYN7)P?!+x_AL7eNcd(#eby4kHACt5qu*hz8)UL*W+tp9KIG`0}tS9@b_U1{yx46?!#B%E8re{1-^_D-vz(Mcj4zL@qeN8)4%*IUXC6skC&&1%2DDiGxb?ZN_-F{KA#d_K#9K#hvDzyi{Ws5F}@Uz#FygB;Angqz5<TLSKzDQczhN9KAecZkFSA~@yYbx8cKXECB8mWzpkgmH&WtLDe<nbGw$_tS4zAACH^3+i`S)hAEd;8rl+Nkf2PEb!6W!Fd^6mL&xW($Mtl}N6RyW+;%~vV_*?iixCWnwPl4~_Q}7^Mg$ME1;R<{Oz5Y5SK8X^aK#4DfyYQv>PIw;QiKoGT@ihD{lxyHFKZ}>)x@d`)!JETDcyoLJoR16V;sfx0l=#~jl?0RFTs#?1h4b-LJPj_u)9~}~UHm-$HC&8;jei4|;@{vG;WGRp{w-XAe~W(ySK;5`SK<5kRs09I2LA!S4%gz>@gL!O{73v}xDo#u|23m-!p(3az8Rkmr{dG`?yxH^Y=C#i8&Tqg;e)tPuFt~!EdDDcejFadkK-T0&A4~nen^SGol(Q!P&gYOiVuOa@FDnMI1?X?4}x#ugYW@x8a@E;2dCiu@IEkz_rZI?*YRF>4>$?$fp>=!@a}k5N_-q#ijTt=!=3nI{0o?de}SjMyLc-87nE!MFMbv;olUVhUK)QI4#0)|@Tc)+lz4wid=7jY_tu3u@GL$Dp9fR$dH6dpgujC?q{Po<)R!6cRYvWA=kRlk*+GeaPKkdCQ}9pm?eHvqmi^vNiEpFCKY_{kC-`SD6&I%ApW$Cn;ydAad?&sOevR+K_rP!PJ@`I&5#NW$z;E#w`~dt8KY+)<t9TrK5dMG*uj2>tLzMUt_#=J<KL&rsg}>s*@Dr5ysciqPgQqC*Gw>EJyp5m16Djf2@OS()eiHtM3xB~+;>RiRqZxG={se!)f5JCW;vd4_@DK4V@OOL*{xQ6be~fR1xA3j_NAM;t+>C#O&w$hM8F(*Bya()#3mf4*@Fytohbi%*urMx^`$SQG7Qab}pMb~l6Zl8)L;NFr4tyK;?jLg~@z*Hvj+A%@O1wQBinqtx!6A4%{6#nze-UpB2jOk;)^Gsc8h;-4!=J~Wg?;d6@m8=G-i!N6D@wctCEg5n$D83#!LInzup8`(3&-Kz@bQ%R61W%_et|E+cfeG92Ogrt|Av3zf8)MvigF(k7e0*(o8dmZEG6Co_QzY`1K}K8I1e9)4~FmH!iD%?d?+RU8YR96p2LM-;fwGkl=ubsB`(~J3-{s|@N`Q265Nkp!Y@M?7sle3@hg=0_b?v+9=`??aN%M68h!)*gx|n7z)koDd>Z@^pN79hiO+;v@R|5*_%S{kp9Qz#!jEv_415;e2lm4I;7uv<Ca?!Cd;)KR7l#ky#qnEFibZjutZ}y}@l)^wehS|LKf;A`@GbaU_!>SJ9}YX>!||6gsu64mJK_!T2CxI(0Iv_*<Mr`+upM3xe;mGuKaSUhZSlHzZP*&Gjn{<F<2CUb@L9YDUJbUwtKpBr7WkuhW!Ma_j8}wD;T7>pQU9%#l_>Ellz4O44R4MI;CMWMPlQYGiTHbP2mT)ZB@E$T;^*Ms_&NL^DC^@tuq-Ym?oi^7z!vx;cq=#%7Y@c-;m^XM__O%)@HPB-yfr000xrUZOYl+fJ-7rHUciOv_<Q(rcnM#QuY{NJmH29S1z(Lv!|(BE`~!Fm{{UYHZ{WfW_&R(FoQ6-q1C)4A_!iz1?+s_-z45+qHZGin3;W>0rg&fcDN4K)C0-IX!G*=~Kcf`?fW>j4tZ{!(;%DF~{0zPoZo!3f@vZngI2@mckAN@XBk-4_{#)-}ro<a(R2k@ljc^}c8aBj*4e-)<DN4K~tdEz(OTc<~3A{Lb950R+gLUy@_(QNZ{t#XS*2Ih8g<uW55MB^g!-bFH1@Q+c@%v$A{C+$ytcVLM;d$|Vlz4tv1<#Kcpv0@f=6F@SB@Ey#@t$xZ-V>h;-@_;4%i)*!a(p*DhwsL}g8$$`Ss%qOkY(d%$+J=772qSduoW(R7O#L;g3sfX@G7u1UInj8iMNF#aBr<_ONqCm#K*w*aN%-%3_cF7#D%NzargvEd=iYtC*iNd4{+f+{B=ACr{F=n8w}vx@Wzz*ldvZ)?2SK(`(a<aFKe8i5-$Nu;U)0@MJblVz4h*Ylz1{Fo&^8Eg=g?2{1Zxi8{CR-!{@_!xNrnMA0J7HzXD&zg^lr7@FytovQhu7gW|bhPFM!diQfZ#_&s<ISQ^iPXNRTm?07a<63>Q5!4h~B?!e->ga6|w7Q>~)|Ar6YQsV!EMQ|zcJFpNgC4L(g#HGZ4hY#RV;=jTBaVha%U|w8G{8yL{mlD4T^W#$Dw_pKWO8k!u{^=+_$j_2LNQqa6RdHcUygL32CEgqM#D$ab-uN4o_)54O7w*Pa;(Os&xVMJxrNsAB;^|P<({z3o&%qj70k6PXnS&C~39H~$SSxc<;`dVGxhe7Lur1z}b+bAp{um|R0gl1Pus(L6#9x9F@R#sc;3WJN{8jim{wm%D2Js+kVi!uhA#98{#2<oB;t%1)pda_M_7$VV??fredUuBsPl3t!=kPO_j0=-+;V1ZK_`8(&0=Nwq&c_$vqu@w<6y6EGf_K87giqj4;^kmj+*=3BQR4Sz)D1`RI?RO&bK+9s*Bn*iKfrr%De>=N4qTWWmlD6~s1m;dv*A+W-@zzcO8hc(a4GRiP}a&zlz2M)8&AhC!2jVF@UP$<{44w%yp7*xeLP2rhbZwB_#2*rpM}5Rzpy@@rNomd@l<#dPsP*VE&LYiWEv%Yo)Z7s`ENb_niBtp690=5FC3*P>#Vr2I$jum3_gQDhCc^;<ImxJ;Tw2g{7twLe-mE~_u|6+_-Z_w5_e%b?&6oAtf7}+PCO@T<t4_6Uyf2Geg)>nrNqCFQYD_3|Ghe1oi#KsC0+}5z&o&3)`G9#weULdRlE-VI3->mcEP)_Cf29Ki@=BQBKYr7ip6j#@!L?=!P}JhS(t)*YvNf-{8LJN5&R4nzKbuy$G`=+a1=fU?+iQPopC>W68GcfVL4oQFJ2zc9rfSZmz$r(f6AyNm<Vs+iTG)F9Y2kqgxBzs_z6n<IQ#)Wjvs^H<HD=>G5jbcegs~@kKl*lcewB}ei%=n#N**5JRXmQ>A3I$9*et__<r~mz8~KU&*8!lz8Bw3iGK-G@GtQl@GLG&#&_U5De+w}72k#LfoZt#JiZ6tM~TP4ukjfC0Q?3&m{D;VbrBxG4>0B;C4LwFh2O=CMk&hLDqfiNv?wKB3qFU}!e4-W@fYy^@J+lwJ{7LUSF?srrNlpgF8%=?3oqf9SSw>G@pyOzkH-_>_jm$+m=eE6iQmsUD{JWetfjT^TC9opQ{oT6$MFa7g0Mbb5HAFa;Dzwtq7-FK{EZSnO^GMM+qm#7F8mZv#J5x83*jPsAwCw4!N=lVU}s$D$GhN7De(%hJTA<QSHSa7;y*izvfhb%>)_9n_?e741wWz0KZ8m5XZRPC_~$SY7oNsH$3KN9@lWyXl=wDy0^f#z43Fa<<6Ge|d@H^M9>urdAHgH|NBCxV7~hO<gbDaYd_9cE*W+tpEWQ?B16_O#{yyA~zmKnid+}BH3b-3zfiHt!;>+-*a0k8=e-G}&-@})~UHEc*CESCr#8<<8_-Z^F#^BNT2k-#?0lp5#;p^}X@F2bc-;_}w!b9*NehB{-Uc`lW@o({eDe;G+6lE=bm=do8YvIBd@H%)KN_-&fkN0QI9Y~2!hace6@fno(Iv9(`vd*rf#5ceMd;`7-9>zD}N8vU6D1HOVI(q{?fJ=%01PkH?Sx?2K#D9UZp8i6KpM<CJllaFl5f^U9KgQpI3-NdG(Qqt2mbG#;CH^WU-UK$qo8XVY3b-&2{s?{_l(q6ceir{RquM?fm90?r|Nc>hO<x4sY-*V?=PlLmihF<L?^b54@_j~(8o<A@VE&i-KgW>yzr2#Mt;j#l(Du1|!oMG%E#v>>7q}b9Z$vx)2OM8|^Z'

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
