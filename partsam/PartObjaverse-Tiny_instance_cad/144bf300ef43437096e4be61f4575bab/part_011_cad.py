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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_011.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_011.stl', 'source_sha256': 'fdc782b4c05b626ea68d825cf3faef9c9a269219184c02b335de1f69609a07e3', 'input_faces': 1028, 'input_vertices': 569, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3070710003376007, -0.2409386932849884, 0.19208496809005737], [-0.1415008008480072, -0.06306395679712296, 0.41052061319351196]]}
GEOMETRY_BASE85 = 'c$}rZ2XxHa_clHWAtVSPM4d<?N+L)Q!Zms)N|0!iD|(6Eq72b%wCIf9MVBCq-n$U)#pqY>f-CZV_IaLJcYgo%f7g1~`}(fE_OqYQo_+S&XP<LEGne%ZYnml%ejWaJ>FyV)xF@Z$PAB53%dZ>WeelrU-MSAcKVaY}2c4VZ<&RA-Xc68#EW$xITo>yX-F-;6!G6{Cel>c8`1$Modc+JKIyh=T*O<Z4-Gy%u)o)05jUUo0YG8NGE?v1wHGh3j8Grp){r}~koLUO{T$^ql)3o`k&o0r1@AdE1(zNk=>J7!Oj5{FOlA0q;cyruI#T#xoB`LmOcku1!gO9zsPkpZb(>sdKJ4W%kxmyk@zF4y24Ojaq-gNkrierAB4RNk^2j6I@;!US4inn%ZgnXi2D&F|GDdN|tt$0hmK$WLy=@P{oONL_Hq29?VujADeZ)#HodG_sjNPVu|CdKRGgW#X?OT{-lLwv)Q3h?joFY-)i4*#pAk!QEHh?8#-;urKrKI1wl-q>Ol_-T5@>s`VWZ*l^!PcNZ(>yQ_F6+a`Vny;l|QN*d%Qsr+x6AnJQAo6_CP5J8{Oh%j<uJF%!Sk>Q9dL8mC?~FVX_bcAo{R8~(WyQQ|RaWbw%U23{4o|<X;`AD*cuTqbi1X^J;tgMiDc+R3Eb4Ozyw#G1{EMG~e+YO>-m%JGf8HPd$)6Q(j-07@gZ~T6>)0E`8*|m!ui~5^g>?)DZ(7@SkBaAPM*dqLBYvKhnAh-n7`N9W_~)pPbt(4pwu+yUhH)RIVqH!;qTdSNK%8cC594_i6~_{P1@moqSovE+Q8(Sg%ZMMEi1-=rkWamfh;t$j;!J|SW$byy>&K5!`I~(Epw2Z<AfGLBRQ{IT*AYMQIQ$K56>nOH{iWNHgmJ%5Reh-IJpy&pA3)uTdaC}nZk>oaXYRwg_?1!XVwrjpc@9WKoFjMkBY*5K%ZZ)vKQKk*Z*d=^>Sm1FhI}>@QU1pAe<IIm8x^lxe-Zn1;W^aVYc2de3m|?n_Lrr<8F@NcRD8pc-pXH>uo`h{4@92ssK2ho3i!WvPEmaL9p$e-v;_GtSfS#WuEi?e@Np6N8p{=Ltvwd`B+X|(H^=!fv>Ebg0^Yd2FV3sfK=6OWBOkAw%3mMRg89sa|I;;!H)bG?E^H3sKR%`AYZ&T`^(qM7TCI-CUw8Br@-a<Ae7CPhRGb`Fz~7vVepvBF@g^O3gAu$gb}I5;P#t-8oPavJy;t+q?ZG)<U0^~!J-exS={rt9o>RvmPTzdk*Z;Ibo*nul&&lD~kFE6R&*(nj9d6+KDcervV_Mf6dEU1w-tycHaa?+0zhu5rye=i5;teZ$AfKG?6mRt{13sz?;&`rA^D@U~pdVg$LY_}tu<u^iMSU_lqW+Hg6mRYsiTbRG1i#Kx@w!Q!;9oKV`MmK1|H4C!Yg*72@f~vEoIkk>^Sa&u^Ii5x)!&j<2ytH2ME(bdp$~UfLVenSH|cYso<Xa@XA6b@{j4}Aoxz*yRmFOF2Od@9U+#hVx>ZI#=MG_gOKryf{TYP#Y3(uYw-Sio2)yocQ}9W};lH*5_(!`GZ=8m8G*=EleNIQ={#yGU{jj|(;;%M>ulNysHt@!Mk?4nw&KUQCAL{w>tIE@$O920GNyPc58qR@5SyY{k9>tN*3?J-AZ=3`Aenn8{9s8BPb;BN22kY<x%pdo@xfSxUym804vr8RCe{D-u^X(7b(&s7aTxlu#A&)Ea+16K$YwY}8`CFdng#U|2%HQhq5bIvb3H<tQD!!@O66J6H?0|g6ZaAjm#Ak!Q_wQ@U-=`Y<XCfcn;-8AQo~j8x>vqNKvwl~+{wLmBOffiDt-Zb~-jv>4?F&=AamYX63*sNDjeWNn{-)&5iZ=|!IvN5)P@mnOz~6m_JYzqjK0n_ge#W9>@XtUU&c6ch>Vt7x^g;Z^;B~%pmA@|T7vi*fsd!_qNab(51zxx5Irud*(a$^f<G#4@1o`~hiSyyf6!d4uyNDlOQtd~5v78w9@eTMl`h;_%PZ;(^vup70J6P>UUCb0UuJQ5})Mu{={0#&8aOfrQ@lzFV9Z?74p1Fwlk7g_0kT(M7<m!{)Gh5+(a#sn|e<pa#d(>aoGXUqn<l~s{#6-l|G8lCj4c?;Pi}SqP4Ago0QSeI+E8hH;d^7OI6K8SG-)Mk*iXB2eC%53-`^&2QO}TfV4#&%Z57~lo`)z}N^~q|z^a%}7pKa?DZ}!PyQR8fhLjL#HV%`0AU|oLkep$Q*ajG=Nd&TpAFm44i`gY%XoZFw_Z_HQ@|ES(7zM;t?_$MvHyk@jV-7;}s8@nyVzId3f^0Z{O#JH|Y;2-`D`G+>gy7yRwy6r2Y;_F=CuUkDI^J@1S@6Vla9vaf;!oNZW?gf7@yf?;>ub+<h|ELhup}=g^Vd8wn>;F9szV0;C`Pg0D7qx@1zg|y4o-Ils&baF6+sbjM!-&)Byw&IA`$>WcaVCZ1J!jrytk<#8sOQ1_xUVyCJ{$LsM4Z}_@IHC}9QNJk5#*y)9W15q-BS6q7>s-lK2z(ZAGrbX_YcH;gK}d(>iw`Tv%nihjYEC9=Ei(icSk<S-pAGR(UlQrUKH|AjllY@eyPSadv-<q{WsAMeX;I_@|{u7YtwPgN8;SGBzJ=U(+et&Ik7O#Rj)|+Cw#<v=5hF&_26}5AE0jJO(i2R-&hCmA-&L7(Jj$e+s-16%ToAzHANi9k65qA&#*6cG{LwR6I4E?+fR^ZvBvP9(-h~%g9GT#vvuJ=81I?p-31VTW^L4StDCBuu0#{$zp@tmvnJ!bU2;{`%`_|&b@;gy=f=E>sN3?Y@PDxg{EKmj-#Qrajrmm^(~^BEj&6A+<XNt?;;nZFt31uq!5ij!V}GR$z<!xgk@=T}zsof4qq5+ad8+&^H_<1Ce|(VV*(5bz{lvDISFAVubFD#tJ~bduC-9c2z8JUVFw`xiDAudI7v6iroKfcs?%-2;W8Ct|YF>uwc`>g*N5t8F8GZgOJL30>RQ`JZdC0RGcwIsm&f68d*E(kdzqB>Z+lxn0w`EQkw|;HB*X{g`dA-Sk_zAOco|tp<e0Bt%vH<ItggB-E2h^dUpUTJjJP!B!>CCIj-<Xc~jaS)GhavA2ulu$J?`efw;M^GUR`JHGqp`1x4#57Z^GflC>?={XLapF`;3?u4s(`wU`G&f=KLNjM0Qx7jEBZX-vEr>Gf-zs8FN(Jo`%Cfqu;D7cHMAT0!T%oOyj+fXHLZ_0pRR(>48ney<%IW^y%&(b>vzn{Jum8+ejeiv*?~N3FGt-fpTxYrN8|h2%+{!LixkD1wjWS&Og(VUo1BlJZf$-dPQ3@{hjxdM&$yxJhmqA#w@3To-}5`})2I)M*H_#E-ZvEa`)^gevH51?|DZ6=tE1=PAG{9!)xV&ghAQaumMbu?O|?%bU1taCUvCle@0^M}4{=}gosIdv-GlQpz8T^loQ3>bi~--=75!6~{MI;iZd-@F#(c9(NBs8FReaO9jyRv6#=*aXzw$TU=e=+s7JT6isOSC!?3a(j5hwaO`ZEIg>l*jNd;_ewXB}3fPYQNLeRlh+`5KRZf&a;ln3u;pyoX2OT-7xOuiI4w=haa&{4cgcoWWI8979V_^huGX$a8=%?uGQG@PE_@aqbnwd)=^q6>m)fuRp&A_f)%I@b6m(^BOx*#n&6-z{eRBZ(jHs>;5Aab#7Pz<3^b<uUMQvy5{9E?){dEw**xOzpWhdANw5pbk0HSi$3738Lcs|dCb#T7I_})gLz%?ME?&c2>(5CsB<d5Usw+pK>qKts5rW~=QmY-X1RgSo{9IjVYn}J5qZE*ERH-Upnohy!CU$s#l7FZ6zZHaH~jk*z`A%JLEmn4K|Xl{@t*HB8~wA&3Hc}PK>T?PvA+g=zM}k2EIfhznu>iC3f_>p75<MiRQ|?l;Ej3qU|#K)@jU;ic+;e2c;D;ef&6olA6*^uJv|fq#pMIy|J@S%ef%pG-_ZQA;`K+v5yv$gaq2x#yft4S>fGZa*5%hd#arB6v5wJAkiTCV_|<OU!zW_@w!Z;>NHX$i`vv39J&!u9Pr&!PF+3mIo<N?-7tx=K79sz27WhvFZ#r8VdB%aa)LMe?YdJe$U3MOWfA2S_TWC4-;ltgSZ@JBiH&0um^0AZwuk+ok;+unZDqi1yJL+)18~V`Q4eL053;ZATMBnCkggO-8jQEwWVtotzz<k$kM4sbI;ytJTCB>UItjB!&p`OO0xR>=Uz?=3xK%5`ZSa+ut$ftA`_^+#jd^RnCe^>|X$15|?KQqBw{@jl9_SJCkQ|2Sjq0TsO@1btSA@dY(Uc4ITz`BDNxAJVn8G&*2Q@Wuap3Q)Np<*hI@k}M0lO9vSPj^TCn>t`#R|g{h*rkZ0|BQTQ^+){Y9nqg{9I@~I=*E7ifpb2*2-dN-5%r&%ggz;?4(r%E0(IEc4s{;B1Lwew4)70cfpe_iC(LVS8}JeA=VmJ~ucBedKg02)ir=Io@69Ig&xP~KwEF_`>0TfCSM8zvjlN^lxVp1-v45vrg8zew@V`_OdET!G|I8-nlOHwU@3#Q+U33!u@gW#D@&(p6G6M6pRzV!ckLc&q=qsILF#H|8PNILxq2COFSoe1ssQ;HM=<~y+;lH~L*CiDDDBTb1wZ)2cd|L^5&h){$44R7gf8GLLzaa9z-$=!=wit|aJHI>Pdz?f)M|Q%x_sR?Y+Z@zCC?DpVo_Sftsni?u8eI|dI`>=ghTL6M9DPDo#CiQq@wytT6mMSUh506ZR=j0<QN-yMkAB$n0dcmB$GW8B{mL@o3C7*K7W;j5UF2^Buk+lF_zPE|{zdO0eq%56;mwm6_uEayn-&M44+mUFUnP_O=Aq(P*MGmE;%vSFzOVz%lX&!@e(rVfPtNdO7>ac%dJW^A{)ls+;5+1V`8@LMh5c^M;f!_3asu;mK8y9L`&*4`SaclzjecNV{w{<16xav;%^RGDPue5SzKzJ|bu{|6wN=H@Pgn#0D<L?a6FVdS(1nV(uGFCp0X{fqrp!V8*KWkT8nr_G+m6G$;u@mg5<@YstYg5Z_XodwAmR*)MVuiHDj(h7%%|>9_)n;c^R4VR^iMhP`V$Ai9~pvm+1nd=7Hf7&J#U!<^L^P<@#g3o=#%%Z@UPMXbui^n{+7JA)wt#vk;rFZU(|Us`q{j&E%=p1mA|#yF3jtDYw-0ODSyl0YUm%=Fw}E@UF0*PD%QoX1@gHTk8{!+_lx;X6XcV9Gu9<J34PVMKH~Sody#p}8O*Cy9mIb-0_(fAB<5AM7W(AiB+P619Tms4xCY`MaYp|8H==*~>ruCu%9yWpAN;Smq5c(TgWqUX<674`A^!Ybh_iuxI3B#^!*%q}yV;o6<zJUno-UKHU+zrByq5h`yd|mH8I}LH&({=R=BwfjIeOv#8iae_^3QAVTQ90{jp_F=Zum>YFXxGUcMJEs>H0J9kuTAo{cd7?(;g^Z?-7jn`3hkjcc&`eI64q<@(x75)jg?rQ@$x`T!Uu|)ITi+amo}qt;VU|5BU^6jCqYLhy7UXJL)!jKjM^(=6g#noCAjwF>c)oI1gR=p>F#&fuCOo`(oN`<X>b3;`hXRrat>U_%~jTd`^r-AD$hIeDcjf-GWc6JgqmnUsv-wI#u!J%!;^=E^S1d5|a_<6z_#)Y3S#GIPeesRUOQRlIW8wV^Qa!X)3-kPo#=(IU1{Y>$E4R+xxA`-&$%U@+s+qeQ|j-&i}|ksL!*ODvo~C59M!c1>V?g=2<mPwtXtT`493(-eSF6Q3vC_D8z}0QgJLhTVUMbM&y5V75s}>u)cS?BLANcaV{lYg1>7d>b(4}>QDXKe=x5qZNRtKiFyv25C2B3Fz)Emr!kMW%3pu2A?iHpjf$h&`?un)I~pMW2SYIK@A0_Dv(!cWYIm?Mway~Xw+7U6>@nP59&6E8ul_*%;J4tzx?q3RtN}jkI?lbTxJRsGgOKOCuc-6DDD>5@0K^{?iFNOsh<aA>N8KW(!@u-b_`CUH9kZ`j^D-VEjQZU5Mm;m4)%xnbWGdcps093%gkoLp=fS?4T^RG7=!x@c^B|0SwGiTL{zt_(v{`^SmkS_&=jrf&-Vk-Wm=}2-NX34SnuLC?<c2tH@&0BtwPv4Z13#m^if^6ng7}x55T{js?4vLEeqnl+aZ%NC++^@Q@qTXc{;qgqW>54<bqB0_&2;$Ze26}&xf%QA_6NmVejBi_)7oO6mVK#sQ#&8j|3P2m>F`|f)}5<Se~)8W-?&HM^>?xEF06B_2a4BaI)Sg_iSugWeZ?Cpk3pPs9@t04(~wVK6_vj!xGMU&#%;`N{Yq75Q?Uxjr}_=dE4m-{<MG)ljxqi!_-dDNj^zqReY#)3xV>j0&ig>rXW&`**RP}ESVpBHpDN%Dp^b2E_%=oT$DGEz+WMhxZ*gB+vz<czZyd0W?cb?5ro1N+{|_hh&xf6;bI%i~bFndMTw~}Y^zHTIm~WwC$kXKt`0vSx)21Kp<?fZyZ|{>3Cw>*q!z(@*x8p&@>;DFCU42H~Yu1a~F|TETr?Fpi;2f^I34Ej7h;!>1*0%t7%ctwOUxF>jzri|;yQ2o~(=r25hjcUizu-N@>|a~)y2~rTZ;itFbL?NttN9$%b3-fibGKiJe{weBC!R+i-u1`27n~0NIDg#NDO2D-X)5^M5r`9a0q1r#@RmDSa4&3Mh5kG`3I5l^(LbKwP>1*-sGHYg%*$&7-UCa5*Y!V&`ajA*oO1&azru6uuZI(Gt{#uUz6jlqd=B}dKKc6~PMN+~-=t0G+nK#F-xuNN|0R16XKz=md&(M|Z-;N9Z|_CG|6~l#c`NQaLkxJsiAeNeVkgvRV|$G2I~M1jxiR>(aO7Wnyy6Yx{zl!dH35IzPu0f|g!c;lySm87xj4qnOjUiQUs3~oJNFjO+g2v@p&=Cc?3%CgvGnl7`7^6J@^=WuzKby;pQ|B=liCUXov}|1BZA={TpsziyNLI+-$9ty(gWy|0$4|DN*Tm49Kil<hCVlq1aFBsf_uMFF7$b<AL4t2o>TrQ=x5y<Z}3T2N7J){d>__hT(_&(FSDMbKG%w3zDx0*ql?*(dunGPjGOH@=JjDT)_rka@O6%2-M9bZIyxc$$9Zs0S`f!H-w}P)Oowrgr=f5AIiPRnc%aX3w@3W`UoWV9<_yPvZ}}PfZuNV`TdFwXe7KAEaNWUI@IR0H-FPev>(ccR_!C*sSE=JL-(P8p*XvC<-xgIteI|i7XKR3da6O21`Ef__#!0h~|AB%yZ~bm5UgzBq@6{(pAWn(1iZ{*Jh;=`g2mL?u4Dvsmi1i&FhdQL6g8!RC=&P}LvG3CMW87Egz`x9fKEJgS<A(1*{ap&f|NIW*AN3Ra_aOGKuHg!dTl^vNU)%$AUO5GEk}D$4UoDaUlnIKrPJ4#)q+L(GkBtStwJgq`c4xt-jKsKG+oEn8(^0om15y87-;vL-j#x*ZzNr6#N2tT{$(UEs-l#*yKJ=j#>u53dM4nYPVBH(9#kjR15WiO$)aOfU)M0N^)UCi^%xj<@;#+GV|0US(hHaA(r&U$NY5fZCMQNzN-lZ(~l6&Caj(zKw5B1zy2=Vt7Lj0S~sKbT&I9H2QfPZXu#Mz#S_nfX#taBFlhfF}<uKT9W2UCC}{2xugeG$11@%#RJ9`zcDb*$@(dJg)iczurrh<|=D*4^p7;*HzCpg$85u}_!0R=lq5G@K_#9l;NJsCes`t=PY=crVg_JBD$;{(*h^;sMt8QwqinxPWn+zQDd1y<PF<B1YU7^M~Rb%RdSEn5N-A{gdy{31bv*>Fuu8(Y&t_>a%|Y@@!F<{2K6eha%7LN~pu>SKO!l;Gff5`RiN#f%C@;yrIodod51);D4?+{5K6joQjLEUb<-Hzo<U?+3_Lje4q{TKZx($h9_;fADg2NW_R%U&tbk>YAN3Ix)J)>WdP2l!~o2<R3z^~)WH<#3BKNC^m+T+7<Z#9^8B3_=SlYOsPp?bIQOfb#yTFHi+SaEsCb=MD(c@4eQx-bqIm0>0Q5udeLRPg6mOhz7w7HXe8_XpR>aBw3V9xPMxJ*oAWq06^vN=OUpC&kiv2L`9=@+k+<jj4Ptau4<y$m<uk|c-QRUhG8peA)1mEYL9=M?96_kQ{Wod@*E0GzBw|qZ@{#%Xv%DlOtif=7-0Pg{VeDOO?>>=fE9Iy@h(5W(i7woUb)vsTLIG^6&`%{fYiZ||wMSXKu#rK%YJ}Qpht0(5^gWpjs>-CDaW^aZ(*DuC>Sl6O>LkX<6e(ZAGtG@jeugh8+{*QJbpPYBWPYcGl9tZII+~qmQbBz<~UgRczC*HOElB!RzBkGpsiQl)H27q_}h(2)dgWr?-cq`uY<1d_Fr*q?b+vHSLH(lP%=z}wOPc+sorSdU(<D4~n1*4u<E}c{Uk#lf9##F_7MAuB@za<X-H=bf%d*W68rWHdmuBj`2Cp&Qp>y;1RZ}p?_{$ebjgg9Yc(D%7g5ocE=)PG(C;^e=B-{T|Np&zEy1HV2QebS?!ny>z5ZN#}g5B14cO7WK5UhuE;H@>g;Uaayl&2dFO7t#^OZ6NA4^()?=;+J843wdK)-6!xDx}gpu7pwUiuDrtchvxV_-n4Tq=JoP9?$P#vxZmdN$G#YJ6MS-3?3c(u<QbQQ_zU+U&h$LU)BPa6zg=vJzB-hG{Svzczn9hSf_gTOK|ak_g3mV)eHHcq>oR*WzGuGZjQ?))0{hg|E&=|3EkvK2PNPqz<9oY4xfu8uAN1Sa{@@2)!G3A(hx(5*q7E|>QU7n(uphI9fd6(4c{cqE^>GWv`@!;um{;^XoDYGO;NSH*`oSgSvWm0W7xi&Ih`L1uqi@abi1TX!_{R${-;=p9uU=)bFGj9M-6p@n?}>F9gAZ<l{&YHz-#d1uBma!=inmnS4c@N;>d+(x^%)tDIDrdrzST^?eyNTBK5BMeh4+QR<&aO`Hu&9Y{xifc;jDPe9{hJ2Yla_xpId#YR@ndeS7E2~-;dc<LE9Oc<k02U^@y_jCt*UWZA1P4|4+ht2mc@aldy^vDuw*N{hP3y0a^}CG>O!trzTxBX(#igu20^^b)|1-@{x92ZA~OzG_i1TcCn-FxB=9{&$Q!2BFKpzN?emzxMsvPDSC3EE85}Wv_+S*!vVAdn5W<>ns{j9sYwlD;hNJH+*XtJ<T?@ySBJLX#>B#vq%GK+Shzg21?M6b&Xu;{9K^27DF?9!u_xEVgZTvz8<>}Yd`~;BJ#*_xJ-`k(rrnq|9>BaJ$kinFrsN`*i?z1l9JF(=);8=x+k?3Z?x9IT9r_}Uw%`fG!p)>Dcp9;ALum^hLM&V}+JajV3s;f0;OfM}m7^`V60vZ#X_sS;mB{7Oq^Kr7lnUfT7bC7rT!A8fe^8epE=p{BR@p9AAwG8}&c}G}#6^gUaZP2No0AvLUlU)(l`+Z_`!Ze`#`h&I#OMCZqdf5+949}0oQd6u-8p7yYJc)JE`+gs`8nJ8A$DAO`udYEZO0X0ykKJC!t7!P+i_yoA{O1j4*Ss-UC$2Zr7gMyaZX|<N(nv}oR!Z-XSc)7w4Ir!U^h*&=<uf$ZTVA{w)`nfTmEFDEq@$o%O3~YI>vJ#&QIHo<7OdOirS4ev2mq1RtR-1J6xD{Vb;Zlv(e7R8rZNSZAaF{h8<`-ur7jSU8N^0lh49uS(vwAS;vB`T~%V?!e|R_K`dMc+JeK0g{wzfa9v{IO3)VUMJ!xS+JbWv3zwa?U>D--%+H0mAhB@$G#RFeNs}?u^U2$|#nki3ts<U9Y+{UAcFz~v#Tm}$F~q{fQjZ~T<Kpecj3tg|?1hXyop=`G&0_rNcHAm{ZZUo1$;ns)>C=TchB$^}&aum-iygOuv8MBL(-~)l9k-Ca@#N>&af29d39)cVcCnY(ab{}akJ)h|v&o6xVu$<F7Cp`mx1=pP$__WBExMB(?n1i@^Ay}&lLneJ(xeZuaN}tUo<S_!RN8{)5(_t&w&2mk!nLL?xDByzp|k~8BNi@*w%|bGAm$fH+<>?d*QNpU>q0z`c?~4L!j7B4+*VMV?eJ*Yqgi(wZbQ2b>u$r<Xjfz1Z8(s2AnR_!4QMxDu7agEMshut6APC_Tkt+&;f~Q3e3)3cEwlx1A{K5OZNZa>g^QvsxHqwIooEaGleiP}`;&Miv2bfN*{;cc$^~+w_Y&VCzCaPbzo<_UZzr}ryJZ(^8=tQy7H%i?Uh+2X9JyPx_mY#?7a2Q+_!Q%vV*C_4?k|4s7Jbi=ld(3?X94kg;`JQ!gk3HR?6{kZmBP=ZFwRXo?jn89kw0O_ZDhO~#KNW9#lB(3iG7Dyw4(#?abn>f5g#YNnw;p}c6cIf(TnWxSlXiJ+2IAW7cfu3%QP9G$tX=$5(~G7w&0`0!X?ude41Fe&9nvYAQo;iZNXEBh3iXOa4%xvy3rPFB<{xijKm{|M{#XNFuw)F8<^Jy@;B|cqs;9l^&LCBgZ2*A-G-;op2E7@a4*`uSa%yX(l)a0Havp%2<9sID%au$vFLPS(b5N3sUMMl#I?Rky@+@b*Yqm2#QmvBR_(K2G@Zi%Sh&2J&Zo&|9rQ~ba9(onX}=^EpF*1G9pF=lpBK9rvFIGcIT%xLnx@ZdazK-N#KIjSzQ<?h$*rR;co(s7Pw4xFpZ`MpH=o(;EBx#e;(M&a2i8DD@GE}i1E0Slw#BzSzeb$KTFN|gGfpwqROC1Pa}x_!LzBvyl+&akv2ayrhmvbZPV7M9vcxt{?4p{uQH$+h#|h5R#{H;+Em*i`<itKp{EYR<?tmIyA^ygC3YO>Jh+R3?-<)4|;$nOzc1iX_cKVhiF3o<)&gZ3xh5N+*`iH$I_!F_{uR8dNEw~&%C%7`PaIe^_vL@GvUorMI#(zmHTovY5nzb#-njfG~8hh^=`_F;%EXo?Wvfc^o%|onV0`XbmE5uh=_tISND$KpIT@FQ=M^TO?_#@ZAf$Q{*aqenzTa(9{yr3;Or{?!u(?2MJuakd3TjT-xTn_Maae&VcaxTP~jGxJP*J%s3XtGt4BbuC{EjW?(5k60}!%JzeCEm(;i2o(VI799s^(AsAi4%#>aNd&7-_)0hZ}ZvT<Zjzx3+;o%mpMPF-y6nxY{xw$Z_7!z0PbVyy=ue(#D1ETr|n11gPhpz#2%C^<o?wGzt+LdLQd?rI$$fYaL;I;C1)jfiS_wTeV_OtpM59yjyRLgzH^=r$;oqP2k_Dlne-7ZKY3fP2o^3E@l*Dg^i(Rba9^o&()TNIIpSQbTRA?z&h>f0^}5U+d_Y@pD)9s6=EwXzh=toqpS4``gY3Q6oacSk{vEkQ_GbcXm`Hq<whdcp=V#uzIA(xd4$fRlXT}$NpPzlr&s&*;r}nIfCIvMqPApuICf=HqqIMz<qRvC@L@YibnpB`q2swYotw1SGzBoTC_?MPPVNJ`AFa;cdg)2c^fX@V%V2|pE-x3SwMc;z_d_mg24tQp>%kZ;a#08j-%sU&!(=JXn;%CId72(``_*s9}t_a5~$Y;Lf`e@QdleU_4Bo?j-?H1%Zk`uc=absc|Cw47O8c~Z~(~c9|Oq05_n~`frPVCym?O2C8tVJ2(O3b|upI0KT$hrD*eszfb`AqC!u5}&q!Nk?s7j^i&I<au_{vdrM?+ii2!Ua*6rC$(nS=KUyx(%_cj}zBK*2{@p2C;B?=p$Sc=2xAy4Q9=M@r--M{t_%)P0q6xYf_Q5wVkIWSVOT(u+Hw}YE#$ccx^aV2(c}PTFj#s;|KFIl{i)zV&OVz(o>Uxn)IeExVa_`H0eqa+?sqn+6{<>52s%YeY%nxORhI{SK_YxoZv7`s%r9wCLL%CHqicq&ke+KKb0rflRid%t^>JY)JAemi4DXZICcc*96^5@4x?RzID&JL+L-v+fp*+5^0u*s8{&XHD*ZK&cnI+{O;*#MMlOMz*k<Ac%4~A+#G`4?CMWh7;%H*w+R?5}E}EQ?b%@ktktQQGnabRa<OgXofp{#RMRK0Q$jS4`<YUN1k{d@H&S#P2!inX3g7lB{OG9Ge%2GF{Z&~8D#Nn)4TjJJSpWa-r2y(3%w+3T3BsZBg9>>~FBUg=UE&f%BtFev~SdZDn!bvYlAG))a2I8vZ4Xk@KpO0hS;T&^_T@I5OdottC=6KN@t0}Q?n>9J8$wo~M6AO1rlhc}Ppk6_Iih3>e3S#lOpvg7*Tp)LxaZmHval3e@`D~IVgEi^wfW8?_E{b?6pA9D0k+$4Hi}-vaKeLhcaXz!zBl+1NN9}uuCY2m9w#;=UWwTwJmBf9BCo$LKtkFSY@%cxS`<mR*<R!6i4`@Fp_mbQLa(Ai!Ccdu8CEAzB2|htvp6?+(LA+g)b+osW+eA+6{=}PDk7U+jB=Hu`Bbm>)5TE0ECG+_?;#96}GM`INN<X>tSu&r?c_V!xXVEF*)x@IB^gBg-hqjrux<F29zk;>zL%fo4SCCsvJdZU?WsT1f-{tysq<?4PNv!1-`tBhXPTpgrzoJ;H#>D-JM-q=@eN&nD1Ll68+&PYaiGEu+&PZb6rf3qU$pTH5(-u6_0q5)}O^#@?Op`>)GCO`I?PbKmTj-ZUpF}%O##qB=iNvGGi``w5R+@BkkiXUrTX1{Y-T1t{9d1Os8F4GlN&JU0Mn7_EsE3m4MckgaA9ESbS`4SZ4R@#Aj(9lz7clk$yK&MSuotD59ulWfZjd{x$zQau5}zgBtI09id&#ZRWE<^me7=|bR&w)+h1*2CKe_qjhH}0;sb>(c;j^9Ob`YoV*-mn2h%J1!lbnTE?(dmg|1reE+3x-$^feRTA-1qScZf&X)wmt;D9RXeat6qK63JSfVU9P5g=@z368~1j%{a%s^j}3Rob-eAQe)PqJ#l~9Haws98Rl)_xM_BI>}3u!=)a1enNKdib{~|`q#(5~u@AM_IUV8WLS2wJAGO$}H7Tk|aq7Ip`KZMXq@O=^abh28u^(~{(u<N$N#-EB3~>N;8M|D)C_ao+k>gdM_9qUY_Giq(j3c@jaarnOcH>o{1n{%vI7TVz3dCipD==mr#u4pCT!h-qZoCjmS$<Z}F$z$ZA}&H*iZQb@j_7Q}xu~<*jaQyhgr6<MF<hw&5a*&Uz?fMWN3<ic6Sbq=c)2OL_*oB*k%QWm*ooSeF>^AGXcuB<Y8Sil94Jowtn^b+j+2A72S1yaob;abhnHPk9mSbGwjLFq-&)W8t4Rh$@DJ*r#G=0wi~dY3`aSUv;&ke7#4j{?%6Ot*6aP#6lOp&N<uzk}CVo$Sn^^Qs;wzeb(Bv{j@IC6c#G)S&i+)Bd`U&wp;(gS+h<~##AE>_&e;|HK5&VYog|VLzKcP-1PG@}tPt;_gCgUlBM^Miq79C40dH}KLzQiMl|D^6he1&ycNWGqTA@MAV;JK9bj6Hz3FZDj+eXLJkuI~Y^?Nj3O)VqmAClQNYOe}g1@p<Cg)HjKf`1vIc=o9IWUlhTg87GN8-|6>@>muv%j`D_U@|k|(^N4=$SO=MZ56WED;2HhivHr98T=H7VahDJ;=4WE*^O$qHO?gc&(*b)Xo$`g;AqVv0KFWG>ExE>jQl^uW?>6!s$D1P9k0LmTSk607+In*3h=YhlSEa6Khbz$*9q9PqJtKB7b!lR6o>7&kOWR?2=1%Qlhy7^#@!YhXqkha;Pur8vit@9inMW{lD#x6&@_dss(RSC$J!ZQL<<7C)Tjd@9yJK=Y{&ycZ*qz;ScFH~-&%Ped`X8W7XD{p~UP_tHeppOAhx$+AImEJ8ZSNLYnXj+oe|K*g$N%ohVvhgaX>N}H-9OnJ|GO(3?aq4_#yrVAHHSINzP(6oB^ICe^b`JHJ`??sSbV<GPx#+_Ci*L}_&lMX@E`b0^ebZV*+oC$uke}ZTg2kimwv)8<TKGniBGbA;<umtM9NY6p5(l{kUv1*1Dv<ur`)HHxksN8XK<fpa*t*ZU*<lQy&2Zj!7+c9|K0xu&VPU8_b=W5_&>z?|9<j+{xb>tPkL0*{r8V1!kRj%zYFWA{ZIZ9l!N?@b>060DGiRF'

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
