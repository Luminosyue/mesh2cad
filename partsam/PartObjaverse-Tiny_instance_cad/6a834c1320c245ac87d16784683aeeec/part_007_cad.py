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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6a834c1320c245ac87d16784683aeeec/part_007.stl', 'relative_path': '6a834c1320c245ac87d16784683aeeec/part_007.stl', 'source_sha256': 'a95542640353fbe6016e5f4ffc704bec0e3d1df78bf8e39669a2bc040f69df71', 'input_faces': 685, 'input_vertices': 567, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2149689495563507, -0.13783232867717743, -0.3345775604248047], [0.17720483243465424, 0.03974089026451111, 0.2895438075065613]]}
GEOMETRY_BASE85 = 'c$}r233yD`-^Xu=C907U1i=vd)(}B8l8GfKiP(20G)OJ6)xJz42tw?&g|XAbz6)|iEk%`BYN>W~r?%SHde8a&zIQtJ=KlZB`@FB``SttBCuhz*cRO=u?oFdx<@WSd_+L4t{otUkn}QWZRzbyA85KKxWL)3a5w(U49qXa^keC0oToBbUGP<jWGD;a=`P0}DeTP?WXsI01uR-M+mdgF&hmRZ{Go*L?@K0l<kBAvGB3Aej17e28il3_l*Q;N{5>&N@WuoQ(_^*H%g0*DgnM|4fbN9(qe9!d>lNsHUyghdid3BMxPI_zS5c2Ao7rUu_>h<Z=es)pzzdzYUuk-X@OzkrYaX;f5bNfw|JCOJDWdCc&J><QDzmi^!_~$hF*KMgE>zviJT*ul+?7N-d{xeE%lHRWTLEhRSVkh-e*K4Nq&RVy0-d@LhBl*ai<SqAh?x6PlgHmZc*Upf4=9|myy^5tvZz-0@{d8KmjoJs^X-ea1I*EN!ayqpS8n~La!~Bu#cU0a&?bm0_qUFx$$m4%dmVKEHTim_cDLajPzyn%e%di*U(9a{&)>D5E=WM6-J#wGCTF{TYx~uyd@;C3WKUbE#lHDnp#&hpa?q|&Db(G1TgUH|A#O;riT}}Q?;27y`uQz<d+v{%!EjOeYE!SCfHMj4bMqU}xl$NVbTg3gJ-?fTzLEJ*xKIIa)pO2@eQhJY|?QfqnihcECi>SZg4cpDUGOElD8t0sm-2e7$_9>PWckgN+x0#L~d+Km~`;eRcGtGR3r-P}VvxB&w+i8p4$7A%`c<eVmV?Q`!vHNnB0<qlxqtlDs$LXvRqxTq34v+Czm3HJU-6tI-@4s>e?T6iMc)6vf>ekojweja@kMXO=B6+z1>vY@Gda)JzO}lj4Er-WAEe}H3KP(VKxi|OaOn2|`dI@cp{c+|#rHi>Y_EWd*3e$d;Wvw*rNAu{%5mleOZQ?rKo>yL82y^qw@s;G&s)sLSn)w<7O}*mREZekwLg;R@{vCl+zccgp{vER2y>nPE)oi)yj2^1la_w`Qt7hX@e=Dw<E!Xk3D0%DYR~O8@aXd<$PYzJ~g>7}~WzSW6Fa18|^>%k}t5cKxi))>9+owszd6ZT5b~W{eew0DhF=oqELMnewIeS);uAjPhMw*V_Cuz9p_P5m@K>hE0qdy*e9``Xl9yD(}9^i8v4|cC8YX9?e{dlbN8kvsMx;`=NzxW*e1pG0d&f6oe_2VBnbOHVBH(kHJ-n$otnH`^j*S<7eF3!gs+d=cj?Vz2%#_gc__Xq3u7tYfh%e{VKrRjR5zFTR!+_Gg>g_-T&j7W#+cr<Su54^U0?EQktTXRLx@vjv8irU+@v^c6e-?4o(Z#*Ae?E^c;ntH?h>GFp8Gl$2#m%|(TG0dMXZ<s%Gcw;|?{iWVJ#q&|O=xP7WYsalMI$kw9{*7L1Z=W5mx^HK#z2<G50#q}v_~jbm?rjTeaJ$foJn#9J)_JYH=9L${Hk&P1^Qw1M)yx~0Ybo-cuD#a3=5s8!a-&VW9kT1YZ%?DQHn#J2d)a#<`Q!~V+}j(y)?PW-cD>ntR6Y%!Kz{TyKCdSwUC1=?);B6$=PDt-5j5^{YYtO(YnpB5l_f1UyL(G=?n7qnHScQw<MY`xzK;^t%5>JqL+6WiOF^3Nl)t*r^|7;CA@b^jdF*Qzq4rAQR~M<D;8gZYr!SM~sHdu7?*7M%<i!dersX|9P2S$UBh3T0tkJ5wS8k3VZ>?JV2yLe^x4Hd;b#&dYhE2_+JX@8nf0c;lODWZiS~@>-0sChoQ!?HC^~F4%l7S0!?aTbaJ~~$uUHkHu<usliKI?Vuch*_K+pXtXUHix3<kgqg*Xi1iO(kzH{&>F5du^xBMau8?IdohX{D^(@KQw-8(01N#nlB#5<80r1pU!LB`FW8oI^Xw08ozRT{w|&0IG(&Zx6OW?|8pj{58Rxt^EJOW?`Lm3t(PPImn@xsox$6oQ5x-EYf5MK_Ts$0>Dy;!y89EJw14ft4Vdrl?ac$&S1ZS#pT6tI?GNAP`L;uCo6h%m$n$Do-??G#9`9?`*fWQ8zIRP}UsKM{>8ta%T9LQMwBN7uX^+_-f0^d)?fZQA{cd~o23`Acq2%o$mv-vfzwW`_tJzkaKQfd1dA@d^t{>}WZvVLDZk=!XJ9|smTAlA#kUuA%?N8qi*nLK^?>LIL&zs4UGTppAWDqZR_TvQi_V&EK+)u-bn|1x%?a#jUyX`vfJ%_v_eNUFIpOkd+*0lUbb^ciy`h2UjNLZ=!ulVz}(j#IS?ca7&x&L=d`T8Mf!ND+hKkOLyfAhs2ouBfA`myBynU<?A^<LzD+$xRQt;uxv*glTn!t{P%y-|9R`*~#fw$;~R?!Mn3@{U@UvUJ}67O&5hpH{o~qwQZ?`q+&+Ut=_l-}Z4^{{Em;P4=TaczxUY(Q;kBvmeispA<Sq*&~E~QXSq7SqsVAqo(lnN`(Wu_f2K)eD=ooUwG@~Q<*y7wIR=^Px8}tb$Z{Y>p=Ummh6*C&kJ*F@A6%C>91#QbYcIa_bT^(l+BHnx%Y2r`8Vw^Wye09S7Nth=)88F39r7e@;nv4Wr4f5XQr|5m}|anxe3?UtCdo9{lwPb^JGDx#qQo(r5k&^zi9oawJxz&RNeMb>qYVWQqNE49Zj3_xFe71`f+ZYz&`7qzMlb``FyA{l)mS(wLgBGet+jA`=&qB=NC)Na`wIhcs{`OiKW|i@~S_7pQl96?jrZEGql_{G@fUl(Y#{3-Y|OY`a$!?>kXsV+N(vE^SpIGg0BbP3>j_eLsIDd#pN$e8)4dB^JwpUaFG4Ni&M#Wouc={JF{13*CBuYh_1a_alm$+pSgP~AO8cl>ioD-+|RA3FLYk(|KR*-)ZdOQ_6dvF-`-F2rzP}n_FuP|={`=I@{;|bz?tsLHF|BF)+~kRx!oVkbnoA~){}kuqZ#h&o5N%L*2MgJkMX<wp&`@U$LWYIsQ2jK9^s?+=qHEAa*bYFU!&L7*IwBd>)VF=NmFTkZTbD!$D}4xKgGuKJkg*X`;^ZYkROzn-j}U6da{3YdI|ND&||y1x7Q7uOTPMfI!~;JVz~X$D7r4OA5Eh3+%hSS+rP?B-`Ck&@cF4eKFIAOJ@|dASR1;|Rxcf4zkk<K-F|s<jr-}~v4Z+J6F}b+SUq2I`(F>z_rUhkk7=Bit9ka)de>TY)cyE3di%As40mrlzclZ#@#nc5?G5Lb(dTIYhn272jqMYA@%6i*y?s<`hgo~gYwgv0rP%LO`1|nXrRn$1kpbL)i&pggyKQq2-QTeMP>uba4Rl^OtnW;{qL$G6q_GoC+rz6@-tE?TpVD-FnWH_t*1s~hmTsI{d!=wVd;f3g`wq2E6~0e%ys6$7cuU^dEsA}cD7s!zig)AprG@R;x1PcCMw^I}nPz_R>Ju_;ue<4wAIz(oH_p#4Z=8p>_G16SJCS_(aVO2ZHRa+7ogY+;uaAuVyk~K^ds{*rdF#AbzV5&MJ>OUQhP`s`f}Q-BPP~0IAGn*m<FB)Nf9W&6pYh9-V`kn`=u#Ffx9?!`>Wv9&+|N_nME1(h*-5k?Z|tFdj9%?`jQX)J8N>cn!&&rmVDD@*?|l3B1vBq>(Qm71KS`gY>-?!dr<(Q;?|2rV_bbv8=;zRgEvDYs|Ii+^UOD=QR~wGqZra}1kGBsU|2fvzdqaw8|M35*eU9y;^@HU)`b}s5Wf$6R+I}~B*M4t3m-qV#g}=YqyO{3dSb`Uu&nE`&nol%uoKFniHJ@nSFh3Z*T0KJVjq{JeYvZx6NM&E)`4q}3XHS@UYugdzoo!aLpD^VMI)7Jo;QP(F*Xz7e_>A5+h@|bWcKhh0nYYZ^O8r~*ZDL<Iing0&as}!~8JNy~6kq2!17DN3W$)4-{{=3cH}lG~E_(kkg|F*A$dhU6Z<acu^V;!m>>oZy|2W<h`)G6Du^4&f-Vye7NAdWz`Pt|(KO4O^{v00TSM!}_?|iMFhYenvhn+pn@x1!tARp&XkI?mo5`Tf)j~Pby^|k%tEPq*dUOT_*cHYb@d4lv_>!<TeeLv~P^z*R6yUxceSJ@w|PM=>~^R2;a^R4C9O<phi=?%1A>D}=;>K6MOJ^6F>niG7T^7k*M^Rv-w^N-PM^G}X`F#ou`VSYAxZGLw7tH0Cnrmnnj%*;F1Zp_ko!+f5@8^>dq&y8N2&vUdl_G6gO|MmL$-01&P`yAWTFrVAH{KdY{lR0#p%(#5m%qw0G>2s$e^AY=_?|6RJ=6{3NjyGk*Gt58Dbn~RqYxAVb_c}G*eLP0*jEE-h$p4bBV-rvFeFN>f;`&=|e|I8{Uz<OTUYkFyb3FE$osUMZosW+2JnSty=zYPqzC6#X$@$5v=M)~#Z~OT<pQrhC?X~mQKDre9{A+1G(dMNb9`lm3TG@TN^8)j#(QEUn%NyolqtDUaFc0VOn1`+NE3wD*ur~f29^<#atjWIMIKJLHW8v+#rMAvnCq5_dSlo*Jr$cq;uhDDgueEm+e}7-Q(^s^-f<MytQ1-X&xc%?{q_`hfM(;Y#{d%#-^{3X}=v~L5<_-6uoReeO<9gV&zCm$1udT1O#W41%x6^dT^Oi(Dt{#N4Z+DFEPtHl=_3gB43$K4TKPS^=8+mI*KW-m)ia&QJ-R6EArFcGidxX9xvsZu0{gfO`&y`t!il)!SwsQ)7Pj4C6nA<<{=Ki;Nl2^+lleextK;OfwbMy0kkKj0NzxXAc-}WG1^46#m?A0OlsQ>S)@qK{BQ+4-k)s3~-+vB=tnt8+h<s2UOg>!ggKZg6uE^oZQ?AH+E$*Mx@soe+vEo{I0ezyher2Ve$59jS*e7<GiVBT)W$L!+mf0M2gY<I_TKgRp=4<?YejfmmT125b2^MuPbl6M^KO4qygxO?;5y?td*?%yZ9HT63ojl6R}BKx|P_&Kqj+w|?Rzm(8jJf1lUf3E(%FyCj1J;&{@cHBw+WC-8C7<`Y9lhFa({#sFoyLVa&(s5<4_kh1&`tT`_|L4p6T;=|*G2|oQJEZDAN5fn92dZY?_&M6;Z9aUT8ux!){-<Q!=Vh1o_2v76Xz$qahJAQF$A9x$Kb9Ef0If&ECaU{#)ok`w-);Q-XC;3+zMP$W$XkMvdAr^6nabyXWo|!qEq~sazmeWItht&TaNj;!|Mo4hy7tQ8Q@md^zho8r=B@etD1I<`b!$(0KGwec0H5#C!`P?a<maI74jD@09G%ST)n_9=XFI@ypPOB^k;gMAVn6vyzw!NB+cxsb^C#T@m{0h9&ohI4@ICgwEam3_+x<=6e!LVvud*g}9F5~+U%DTq7R_d#$C2vptxb~2+oK2a_wWCd;`>)uud(0kN#}*y=R@-LKZ_qEe<_6S!zzD-azDSmV1Mi<y3cDJ7{z{rlHtBzG_NeX#pC(lJ$|loM=W_;%YqrazY^$s6*c&C@{W`M_IrQg=Y+>6^Lo9gNAEZG&lC9gN;|>h9FoM}^I!aDo4Z$j?#jOI8Gg>-<s0^EviLgbg3lN3-l-m8KP`jKYqggTfB$!A)e-meS1Ir@-~VZLj^7unj-c<2t!Eqa{h7Ph`2D;2FxsBh_$Y3FX&#@CHSX}|hSw9g{lpOd{&Q?!x?iIHVCVMv_R;l$n)m~M|Gcgg-G|q{H&Z+CyqCk{{nY4P$3MKYWp~xAAD1`wGrqO%Jhi5MNB769_Zri6v$}0OJ%?bad0*$PQ?AkHA?t-YbbnGkT!F@8*|~qMySL9Sf5^-$Ps-8v;f}9wuhaQ`_4qy=+B-jMqwC)>wb({?uk~;ATL0=tZ8qsV`q$b!+B@~*Uszz1yLXKrUb!;+n0tGr(;ND{>x?YI_fbDwN%sexefO-<`8qe)_jy45SjrS<-}C~1uTp;y{p|92-|>8R>LHE8cE2S11H<?}YStF&-{r%;<@evQy{LcN6@T_Y#mHOMHKd<ieotNU&NDTS>3qeWe7!iJ7C)c9!NUHxNPb?W#vWe(oloh$pLTy%dw#>^y~ncOHj|(C2=F*TKfkima_#S5-Kp~!zfz?Zop+AMp6shG<NK(1zSR1u5Bt{Hbp9*03#!gv`HVi-SZ~dy<6HIgWB)@>{(RmhX}->v{fd3yxz4md@0DQx)kL~3Q7_Kq=Z-W#IF0Y4+^9{@5m^qGX7BLe=U(P*%;e*y+zI#nrJNp>qVtEhvOo28S9)Eu%IteT;``5Irt*EXLe>-R+u2_9ZMx1E2+?hSmp>cF^FE#za`|@0*>_y5_eCFb|FgEzdE@fmTX_4Nt}$QN9^2FY+>_7W=i%)CT+Y|?UJ5@yp!o(R`8Y3|rRsd5laKT4UVL5nWlQ#N5A*iPI7#=}T)uGuzR&OXV71QUez%gfovv$~lUuQW)`X9@rZ>`b9{a_9ulxp`$9}Qb-?dNY)xY?>!}H88KcxgMS9?yw<)?LGKeF6Woo|`QpEoAFqWgNz{*mmp>+s#jmeX+<-G;sPoYjH6{63}mZBO}li}c*9^LRc=IeeS{E~Y_StQSAmq#k&~<Jr`Mear#gzh@59ez(l)#lGhR_R%H7rMH(DpgS*=O?~_6{MLi)BgWDFQuX#g_Gi}cekt)6-&cuT&EC3@kB3Uv4~MyXZQk=7$DhY8f5rZ<WbVJq(?dG1J^%d6Fuu-Szm<KLG0XTkKX5QCTK898)xWJ8zrrFu`HS*We3gDNZhzt>rTnL*`JZ^j)%{=niC4V_!T;Ys@p|qd4q;J`QIa1aAAlc$?<1dr?}Psq^$__4`4s#F`~vwBEb|q(ST04GFSbQ_kxNDTirj=O2bLvyC$cJ7mgLRI^5F95Q*vIxD@5iOxlCjpkzXP6fn`bFh4cc;lAMOj56+K1CBG5ta7gY<;WFeYB7V+9z5~mWd=!~G7qcwMDpCQ<lzmDrDR_a%vLY8N^3h;LS&b|MmL+)~vI<z1<Tc2$;Iimba!tW0@=(tuKaMI&Es<-HAA)5`-j1vdmL=JN3<L+FPs#5Ko+q-f$hjg5id={M04z)L4rCFqEXf;?g~5f<r{ofX7m2ipTqv@*$gRlAU|Ev)BCCUCN#2IEfGy}#a#6vlA}feoF0!=9bYuWnmgED-YG7HCw;(HkE1*xwL4ucv3>NvN$T}j|BkO`?N#2jF2bLvyBQh8qj6Nm5CwQjFLLz5~EFf|g(i<#G@@%9JSeE2uWFc@N^eNe2@G6m&M6MKBO5|>2MX)T%2az?vvLx?8RsvT-pOXI(=gSd!N(gsY<XiD`7SbaZvn<J9BR#>gBp*ZO0?U+rN}eQYqNpLr!Qdg_w#aC3l&ChMhKd?5YJ#YE<WTTXw260n%@DMigx^ns8;XnqHy71ZR0OgaI077wHZk~pQ*aZM<i^Nwa5!Eod7P**qCQ8C0FM+kT+~?PXmF6If%14neg>`su8oWX%j^fP4X%ak53U9NP*fmt0J1+g-Geg?*&o~=eMy!j`6~}D$y<<d;5dv=vMkA4J-8%qLJkCP6SYIsrwV6Zg}ITaRto>z3Qlq`e%A->ci}ZM`=Cu9wCRiW+KhFQ8H@D|MAk&cf@^|Xp<=P@SiJsI<Tmifq9R4L#&OaWKg;X_js&+xN$xDF2eKEk3%D1!H?k|ZH`s=1FRG`g?#On?_TYBlPf(IuVx02$?tp9wZizM>kT$Rl%k6;biaz9V9;*C%zJ#KWPmp2AP;g!3N61j{N8kp?aBw|QA=t(rgCntQnK8%^a3y4YWC%C}ebq<5;b<G~_PT4Lu8X>Xl6+O+<3Sz=fyhqaK(IVtvqfDN^_{4*qP`V%3MKhG@;mT%Xn!6h`4Tc4d<pzLO7ay^=R}<mbpd%1d=bCDfXoJeqwu_Q961_%9DEWb`2<SxD3s)3$l>5&;D#v4R+Qux$PwT+$av%ka6EWCatwG3#yuV-S-w|v6V*}FAY?RH=3ww3@MPpf@I>@88729&s1L<?JWy0Has)U?)G$$j$RS{FQH}BY#`s+jeka=$Mq0sbMJ0Ria+0wO$rVJk5Y-Mj8(c<|_=uteAe(~+iCQSCEV3K8ji@A1gOQ8CABYMQ6^)z$4#qn6L{0%u!B{m;#?QS(C5q~eTmWu|G510yf_tM)1!N0w4^i_)HA7AS2Vfn0Am@Xdp-mZNS8#-=iK40?`+&=0n?xWdf~%m-Aml=DRZ)FKO+qdO55_jEitGzsifug!oP?hzi&`eCC^8%zjcq;|xeQzsZ9YJTf#tCxj~Q=dV{koDBSqCg4h7c%*Ft^<t_7}!><6v}u8!;vt`3ew&ICt-qmZ+}QQ+dp*5KmcV#rqDV&D?Uj^GmDlE_ZrlHi8Oao~pFkCEfSAA>t1=Yl(fyCCO*yMPNJ8-WXfeUPDGA8-xi0B{X(O=KLnCb+h!(V{*QH5^$NJRBU4tPQS>*T$p0e0>AtC~yO?FS04v7hD9{1Y86>7P$mG7CZ*|C3p<D5;6u{30x6r16Krpf=mE^0&a=?0^AZj6}bXD6+9i83Z4$`fJ^~*0JlfZ0k;R&M}7{j53YwC36|%XJm11mlI1xm&sTZgE=5U}=e(Q`<h;-aC0WiXa=wxC&IFWXIcLfFOwMZyP?F`GDCbK#Z%#o;P6m&_7(WM(L`fcs90(o?*3NaA{gDH~{lPPl$>5pbS;*PoS>V>l7U0(4R><byR^X1vuHcT~PRMTHPT+CKh2U}E@yJEs@!+}0B=B7DJmd`UJa8jq7`PEQ6ln#Af(IanfCqr%P?F=3!@%)ic}|Z;jzSItj{-MEHU>8ZH$jGjn}C-fmw}gnzeFwte+iC3_65g)ZOA@g8#n<u5u5=20yzQv1$YH=K6nK<6}bSM3Qj>Lf>XeAkW;`iKL_6tbz9Uul;pd}KfyBp0)H*)xTs^uEU-)!d<=XPCHVw06D;!xSmtT)FX9?8pU7LtJYZRpok)MMEXhA3OM_*VMt?H%f#sOXVZ5cVY=2}X*dJUPse(&`Eyyfz7W%ZHPx<=Xq6&&CAnHA&7x+DJIg}S(TN;@U=>_(}>+>P=gY$v&AoGG{dV)PMmOMy*@Q-3!{2(e3nE?Jt)J=tde-poxJXO>b{C*04r*Q&)PC$F@^;&<4c)jFlqNa;V5@i>)T#V%lg=@Ln@gsS=sA9rfM3q362UiePQB)a}<gzHq{-R2WDyhiZ7F;FKhs@Go3%EQ=asbjF?2kSrR~1zSeU}24L{-7-WL5^ttOhO(_D5C2c*`KGqa@crRs$ap+hU!l^+*T!x%k~PQGcK$-$A|r-vR%Ld<y;({2THy_%`wh@-g@c_-~Zt2gs-32jGV&$@h^jz%MYq`zXnGQIhW=pM(EGK0-bRKLY=XlKeaJ4{&}_^8fYcEvm4nBBI_$dV{^uMzRmm3t0f{1<s3-oEw=RoEw}AC0Y9?*%Rpv_5>G176BIo%iC`9xGSpgu@?aLL;8Y!(cTYP80-fwj*?sgCAk<%@&`yC@CV>RNH1_9@O#L-;5^8D$h_cuU~#A_KZ*Zb5%sGF3wf-(Q#c=j-+?_mIA4Ngz6HyY{Jsa5<nqXWz%pNfWxfHQ5tS|Ktf*C@Vnr=Rb_dJ+6ucO`8YOv}2lq7%%by1SKC(Mlrk}^Z<Mi|Rcl?sI_4UK{P~a;gW5JcdcH}Cs9lR2`0lX5t5xF0{5xf_93cMG582KIeF!-D(r>KjfZlNS!L!JYlLwm`;A%8+$!@j?UHdj!RFCb5WFMz*6?gxJZ-h<o#-UD8PTm@c*{kH~fWbPDo61f|>2D}FCcOzGWWgY^{JP6(mK8ZXFJ_*i1W`i@p=aHAe=fRgm{VwXJs2j*j;7e#D`Df%0$jjg#z~3XY!QX?giuwilqo_ZS*O6DjSJD1D@(lPo_*>*b@VDT7$V1?L;I+ur;B`m`ay3}yG>?DZ+hm3yr-8L|F9any7gC<%x$v{(*EsL*gJs?YN4N6G<(vCI{qJl4{U^^cMfX3mHNH~+NQC<<e;0kZ9*~G`l}FBl;*B8}eW80;ew(fQ4;m5Ehy'

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
