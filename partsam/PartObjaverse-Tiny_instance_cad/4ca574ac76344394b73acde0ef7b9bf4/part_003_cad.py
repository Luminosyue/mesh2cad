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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ca574ac76344394b73acde0ef7b9bf4/part_003.stl', 'relative_path': '4ca574ac76344394b73acde0ef7b9bf4/part_003.stl', 'source_sha256': '2fac9dff11eba91763b998531f21608bec5406b36c2b1b278adc1ed44a3fb252', 'input_faces': 966, 'input_vertices': 503, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12232435494661331, 0.0820416808128357, 0.1344677060842514], [-0.10312346369028091, 0.11490148305892944, 0.37904101610183716]]}
GEOMETRY_BASE85 = 'c$}r22apt1+qQc}L~@oOVaPdWL>O|0B`1X?gGfeD5EuypCUQ<ANs=Iv!@`g=yTk=aL(W;u%FpTNddBXNuj;Sw<E^gydhTjZ-{*8Vr+c>E$hz@fPh-iyY}T~=OFAtrVp(QOVx_SLcJ4Qzd&kcG3-{{tNraWc_RT-l$qky-k8BlT4YY>j>D0M@$9{Rrd-7E1QZ`RPPo6Hl`wi&VzE`{6{W^6vevS4Y_V4`C@87L`pUyAqyrqhkDCjAXub^kB=YRPx(aQ*)C6POJm@HqP-&E<P_||rdt>o~1_j7JGwRe4g+xIuDZTrDT<;5Ra(d9=q9A*2~tXj4o^?PO851gH9w;veO&gJ_Sd}Qw**f7lYt%c=n-~Y~Ydw*|>QZC;c|FpfoZ*~)D=a&M~eoPZ-zfE)756;gi{VKjz+9^;_a@Ni)?R>vW@^2bv``%}1W&ae}x7h8>X)DLAl}h@%>Zly|=veXRCbNA{<_t1!85`Js;7KCs*YJ<!xOa0%`!gPFw~w3l>PEZXQ$zd*cWmD`sIugroXO?;+dh@!cHivwcfDul^v&xoc`C))zO^a2?R)36J}K=TvHhr|E9~Q1y(+~zecw<1P0n#pKX4^Z`ju>=%MZ1mdx71)@Ad)P_jF8c`_|v7#ea9N^tVqUY5(1{l7G@pX@6)>+qXK5aQk<X$@S21rpxzj&M56aeJ<DMt!UZ5`BvG#S$?<QDU0mi_UH+xujkjh_qLrg_|6s?&p*b<_3$FQTqhGYNITQ>%Jn>Wx?FEJeiZ*{r1;C;cKLd~td+%FzSSk4<k|7LohPdNYU$U&(lXA8hsb%n{+;aqq`Kr;;&=J}t|jIAEMMxltz{R<IIkIGpWi^bvawD-n5wMopQ!Q)mp^cUTtAam+WY&y_DjFE|0LJvt)wpBH!ZV_bK^8F-`l;CwEs!rQ?`F~j$9A3D@y*m+hd)+?r&B8%g!HFW~O_59+Zo9`o1((#cwsx-rw`pRM~&;8*=^l2gEx4z>XSnemiWk_xD}?T=Lv_u*umkZ^@C8r*_ND&ih4u-;mwX&X_i~Z;cx+?Z2qG(RqH=kNUZdocELqUHkjzx0CxfRcg1Nd%uj^iL|fwJI|N<_u>%A+3lp9-`YLp{1*S%bzl32Byjnjp~s}1A0Ei{JZ6B5+b><DzjJ?g`QC3o5WoMC6D~jR3As+P#L9Jhp^s~SYxdofPT$wNhm2d{0jFI4$<xwKwQKhNo?<;^JWFif<jfx&-Cc6#zbNetA7>vo_)}+Thxx*LYP9Y9MzxhZ1#U}!7ZtV7yZ2mc*?;3gxt=d|iFNv(MLuaKMH$!rI)4SSdQZ6gGxy{=JY3cGt->v&{omh~@%I*pb^89#9!Y=8=C;Sd8rekpyZB3KKWA~5@6SA1+OJ+u#v!huwEx}^Iq%6MT)wtrHUIOt)3+Lpm-ed;a{Fh0k@1<)|JD9m|Jc62U_BYn5#MZb9#{RqpOZE_@2}AQBmZ#Uclk=Yo=d)dQ8NA~3(I&ud$hs!cjS`$H*W#yZ$uM&e}9%=W1N1}@wRpzf34>(KQQL)t#;1lUG4GoAJ5^Q7gl{D<D4t4`~JGN$MyrCq;%cafhVoyd37wQj8B<U^4#e7wfH#_Nx#Odex)B(>Y!`hjQaQuX=mnsyT4W?kIVNSE-wA*dppLpKkG3oX0nXW(br^rmgKi{1~c7{ar%0`bRPE){4?6lGvSHk89&YKFJI}JH=_>!YWq4b`^t=R`<!>*^4u<8?>q0-`7#ckpQD}kX&_B@m#^zC>#ag^zZ|+B?Yxhy&zrjZP=3}w>gzhtd!~rX_upt`Uk|?dOXU1!xg+iWmcnk|^YlTC)3@d|Wqp-Ja`wL={;^te+;4}=xE;76e#QCrdGv12=<;=)6YPCa&SU0FGH$=bm*c*D#rA{y&Pbk_CFHob)5kjfz>Fz&ek<<i89Qg67->ICPPrdFgJYe(u9rgVJ$&nY61yFpzkGWS+kS9LDj9!Wr-k{UbsfIv^Ays~(sZx(C(M<3Gvk41=Y8$J{zZ(-FP28`)804aeD&TV=WE_Gc@D&HDE-<Uko@I_$vCraRNq%Iv1=Woe$>4T(l6GBq5WC6=sHk+T_1X5V^6t!eV$x8A@ff9Xc>Rj?ZI9rVqAXZY%*@Tp2W9GWR>f1)g_r9cdeKGcmFBZxvpE%{V4laEhsrzAF3ZHnP1w;|Fz6JJC}?9MKQTfau$$vVA}7*|K_G#C&!b;I(>h&GBR$uZVdNzeTeVdR+M?XimRPqsZw&@zpUZfKk#gu<e8r!&d&S6Lb*<^l$HH|&1{decgK7=Zq>u~`3;P!9qaUU-KgtHE6p4kw;EMsd{_tm$7emMzORf|j=Q_>tNr^gTz+tE>uvUN@9wnkJ5To+(*Bmsa{u<+ALH~x>vQHi^#fO{Zgu*>=qb|9^lf&3gW0bhbNW{D4esko_h-H5&DuNG>Fc`A*W#q)+%`^*%R0*2D52b6T}H_M=PTLAjf!3%&%G_fWE@x*1+NZw`GK3i$@TMdpIE2w{q3Uk>r=0s-{eDN+$JxP^BAvMtkVy*bGfg}_f7okm42XtCF6OhpUbx@w3qvFcx$<SIt`M3v7WaQNlx{({cvBO^ZMQ$wYk3>cl``|9HM$`i*fp)bv5tT>WAJJ!rBR~|5w*^`MUmB-;=D59GCZNUC*oUt65*>g>%(izE!W69G7)<u)~Kk{>et#*R6N#-}d$3-`Gv|pEyCz`}tJIoW6dC@x{iAb^7`o@Mfs$^1V~~%YD85maONKbaq{Dq4B{FttU$+v9A;FhWFjiVZJ|DiCfEY7u}ck%k7lsaJ%Nx{=Lz1z10}!^1VxbmFHovkL5aC*I35k#}TrA%iJl}>Ff6m-<zE!XWP2c{>eA(@$oEvdd%gw?jzU3k)PZ?*Qa&1ysI5uZ(HXh<$SHJDSp1b_HjM)|C0MUK{d&LrH351eD0%8-{+Yv_jUPMGXC#*<+@6}$UeVTWEtu2nhMhXnc>ne*466kc?`YR<LmtE%TrC-d83>h_n(Az`@Sz%$@ywiN^+LHEca2B(()X5y|C<mshP~zpOtX=o_K9#{Q17;UzJ<N?Lr+{4+OFuvBxc54%hlBs{gYXryp3JUY^4zuG)D#EwjpTk6u`B@AqTYV=ljGHF-W4P44o&x!cJ2TxcWD&y{b>{$saDzj%LFKXhNSUJC6W_8lM)k=}K`hu+iieJ%HiukRQ5`rhGNJjcEN<wA1(7a0=g^sQada$l$KD}M7duIGt<HwgK(@1309<p+-+lH=~V66^H65gs}3t<s#ebwvu<zfMPKpYI0h>;B$SRqXw}R#M4-uB6Osdy*V>`ud$gzZ<Bp-xC4{Ps)0xSwiubmXdW*0(t)m`Fv;4?*<{CcC2$3<a{lQFW1kobJE{tzshs+p9sl$Fpuj!E9CS2El{I{T(?dB*=FY-HB+t=-c!^MeShG)L}-8gUXk`2`A)L*58Dr9-Xzy;mm)`<zVA#H8MjP#4!ZVVlvSQT<FmW>UwB3C-*oX$yZj8Xavl>cll$fGUnI}_w<IU;W$Nquny*2=<4#}KMOOPCT<vK4fxPSN`NeAd%=Y#BiGFVh_e0-F@b&wNcVJENzkB5N>t&St<<EOE4*62ZbK}{L11^7GN_o%X{a1bceyiVG)c1baO!~Vr#?J4Hye&Bwrg6P*svr73!}k#NbzbwH?ej|CinHW8UwmDB{SL$T7WKowpQx|jPptZz<-Gh6l>M2f{6A0G@A5OmlX0kiImYEPK7qZBVx7M4dIPzBqOZld{6>GuJUegpDVM+Rl3Z7LF3bK6FG|j#5pvzu?YqzE`|7?X*X_NmM_l`#8X)V^sd?miyYQU&8K&F!g(qFUBTnBs@we><E0o^p@{{zGc`)xa`Ofp(Y3Xn7Kji*;v&HUL`TiGm_BefQKPvbBov-peQ-|$(mGA$(>0bN4tA9fJTfVuBC(lpyt;{#&IXN?>JSP_%bLH^_HpMu7&#uSvy-VMh@k76}Fz@`w*Y|FG{q7NZKI3~2+;Km*e?26}<@XwWuea*$m-{hUI(a_pd%F6pAFLNmPdR<xfZwG3HIL<cg@3pBb8pLan<1e+FZiDCu>D}#&tx3>q;UCGx(9MU7Ofxa^aIv9xsUk17xH<3*Z1^rKlI*RXPe~787bExzwfATWg0B|k9*U;&V$d^iO=s5`rhrYwMNFX`Wd<YYuvJ*+rhct%l@f*NWTu;cln|Dz4cIeE<If)=ZoKQ^!?pebBT-(zt`yd^?!VQkDjwYj>~sNf9CD>bJBV;PtI4$D7lXg>~#6wt_NhCc^?V+{4NuEFUHq-!FMi|J?{jn&lbOPw7fs^KC6CUKml2I4a*$s+MnNX^nE<EfBecazdXs~YTx=KL$qBtC}^J-|E%faXWcFLZ=;A9r?2nV`kYih{P&=!N0Y@*-b}{l;I#cN-@9Jg8Q5E%Z`CG<zq!8bug^Vv-_$j7J@C8=_w_jw?(6eJeeXxpB`5FK!5Lr4{>kdNpNC<-KXUJ@{g~!^T|URv=Uce1&(CmQpP!zGV<l(D8m{MUxF5d1=F#I?RY$wp547~kbu#@kxi9qhZoc38?hh5e!*}vMg!fZ#<-u}XzPsvoRP}>BqvZL(cZ1;Fe&U}f9WB>+SGle#^_F(pO_cdd-<R>NK5;Vdj7%)+t|>j-^Vhok$DDp3#~L~A$U!o1-sviSpMi3}^B(P;93|rrJxAJK*F&D46<W#uJ?_Z+l>Xj2v6=V>#>#cVd$IRsBgxbG3u%Y<X!Qf9>)HMFt@~E;ywgC&Q-25Xe=pbD_&T!x)`{{wFVo2Gum5@t$+`MNdC%g#Reh`440*m?Dk0-juBznO-b==3QrV+UU-$RD@s;E(TUPeh_kvqj;+(#JL>qYyEIB9dt)&Y|&XvvO`wZ`)QD5ehcA7Vo`BdLG@pXM3=#~1c(~s(PM8+-8vNKNKceaBZ_iQqIe@`%%w9~nfT<1ND9&!1){%4+5KQOXOwA1&G%ObwM7vJA0@4uHaN*=yD1#kIXzO}QF<e$1%*0Ez#%lPCeAvxQYv&Y|iF}aKb?^F6-W))8&?QbX}=jBOS+xLwAd#l}kWDb5;lJ}9|x!-L+&^DL!x8Gxz?>!xq`H}Y#^>sbqn{`vJ=d%xOU)S5A^*ny)zUcptYyZ&ip<K_tLicPxxaKX%KVYxjj(5Z@X@~cP;CFAvIDKnDLOCw;g8KTqq$lRFe2*;<6#s|B(%<<r_B(xD-|D;&@(ceX=biPl-*-XU@&DtR7sCC}`ZLTAtus%b6~FcCk|$gLeJ-E<^|>1E>+?C>4?UmrpO*1iZMo)`a9`(_a6f9tr@LP1>%0)&&i`;+ou||f^^0|~`o3%l<T;k+k*q)S9g=ofC-}1GkmtjRUD6KoseU&L#%`4Tb6%I@mMnVA<*%qK&wsuzsqb5vL$2p%-Q;_F%t~p0RbhE<3|cFBj(xk;c|Te!+R1mD?DORMWM1$V>f`cteWmLk-=JBt|AXCf9$DvjvQ2i~r}{l1_|bUr4{nw5f473|`wsfVZ`(w2e!BRK)A!}CEzgZwv*mf4WvKXk@3KmL7bo}SC(<wG3+v7Xxli|hBsul>P2S`Dnfl52^qwczRh8l{KX5KW<_mp~!w*h)U;K8x&p3Un$OrQL{5+e?FMWGS&Rf&vI${0|X6!1*)$c-$FUC3jsJIq#UUHw3@z3y{<f(OE+R^usUM=N$wR4nQC;QU5eEq)UU6taj)7SaJn?8x{Tj?7~{;+vLeQ%YoUEjS!`)?j1^Y5dpXPo|j=8>JX<+zW}Nq*it)Yrd13Cw;X^V(ZAWdH8{q+hk39(4I%^_F&+uY)@(x^f2oS}x~3%{$UQzu$%4FFq(E{<e;;=d&+$QE9(QK=x<7t-h6Zwd=j!+pVDZTU$yyAI*~Q9?^LvPl?9z9Mkz1-@3oa^<5&EGMD%|U-SG_U)TAeb#<7p&*yMIw0;iXU)RrJzCQQ<<MZ6}cgZH>!#X+i9V5*5oUXUW>4)A&bbbl*^|>AH>vQ`*`-kUYT^bma)xKY%wq}<5g5Ul1z069UT+aKbvNArbD*_!8%lVqSUas@ex8yoZ`nsH#JH5qcT^-!;*B09^lv~D!^@cz3@3tR!Ym4N0(MIw_Jr`epAAhTh<Vp0<_C3CI8=Ti+;LU5&{_rHyKJ&Z({matMw`Zgs=8>o$&)dE)Z~P6;>&KJetnG)sgXz2(=7;9ZFh4YJhWk2ihPR{hX1K5Orut3Zka>#vQGH$C2Ifwe=V6;u(l4ENF3p#DbM;;sALdi5b$a`}Sgp3p{(L{Qj>pBheEm)sc|zW&UfXE<!G@1zJOgdzy<_ES*`M!b*2AP{oxXlI3lvIh`+;UlZ9n|Gmipn}wLJe!b&Z3!|4hjl`Kh$?B8~X(oRmBZd&>U$y9Uo~f4wel-?Sg;`YZn?^Y3LlP{^{(me5LLb!qST6Mtixf2yzk6aVfd|G)mkzg+3k|JOh9?;K%SAHCeZMVG-we{k?lYNO{~ZY$C4u+dK)JevAbI3ZdJP6&TziSD+9&1QHAIs-Q9cW^YdAC8C+EfgVawnFsD=t%e@cp17CUIy<(&pG-Uq)$fU;5hoDJdb)bTndeZBk7~^Df(x&Q}oH`N_YkwjUI=iVbdq0HRzw&YS1U6bK$x4NBIo(8TzIiq<%<$g78J^ICvhq2wp^glsi&)q>sus=-&<cqr9JbKmAg^Nqv((Dz~G5?dXs4Lh8Bj8T0~tfj%ieq<%(!9>RC2@6sRT71WF1j_3z)N7(eqs0EwN@P70({X0#6l>er_37b9{?N0y9)}1~XT@EjVFQ9ke3-Ckq8T>Q-c?RF7z6-BF*TO5{570jF2e5^vfi2kd$>@3dXSVb7&FEY7?{C=j$!K4=JG>lS2QP>3pby|X@H6yh_&NRg8Gc0li2f*Vq+Sd6K?lGC=$CSK>g@DU`7ZstOTUzJ(7zn?M|mK1Uw9q53Eo71lpj++rccVxsehqA&*3N3Pw0>GX6lXb0Q6({WBQ|<mpVIa`egJz{ku;emGjZReDp{86Y7ERCUhITjs7S<rG84Elz*Xa^m1$ba(f%i3cn54M;pLKzj5$*>Tlpf=wbK}d=<S0UxiPgC*c$DRCF3V6>fw!c4TiwMx!1$E8GBW3O9hqqm$tA@L}`_d>FolUWc#2C(%>zNq8DM9i9d^Mq9xx$kz(aOznZ2qRrr@@Fa9HJPAI69)*vRPx%J*b@&t-3!j3gqch;?a4WP0+>(4P;4IXc;bv%axEVYdodQpWkD|xmqwo#%CVT^qMUTVB$)`M%dIsDAZRyC|gp5YB!CBzuXhXO;JO!NqPl1o2G4L_?CVC6L2_HvK!^h#7=qz|9+!Af#$X<_(M$^IB;D%^jxFI|N{R*A{$Djw`82A=?1-=EJMi0WL;aTWJcoy6Qt>?&Ihm1y3!s+0;Xf3!d{1rM5{t7;T?tu@$SJ2Dw75E^!4?YM_M8AY5!u8NPj_ei5X!H#@C0q-A7p?`5Lr1~m;63Orcn^FTy#!x|_o2Jteejp)82C%L4qDNXy(}4x{$U9leK+D?E<;|kl_8^1A3O@)g+{~C<WoLReF@%;?tpj0W6;mwF>pn+tRs67G8%ng37hQ!xs4Vkuh|Nd(daPP2S=mp;b{0gdKNxQKIIM6JK)dI;qYg0S+s~Fdqy%EJx6Y{og=r=^yD>LdNLaA4-bRaqu;~p;j`#|ct81+S5a?(hoghw;cyW&qa*w8WHlNCpMy<CqkqC?Gu$8jkh~v~Px(9Q@8SJu0NxL;LYKlz$*0_lx))iMe`mZekkizLw^PT!f1(%RKVg&6XcT$P7DYy*e%Mbw<sYekB%ktp>iOhT?m*oOHaR<x+wdXsU4R!+FCwS%Vd{&p$!N3+d8?35`3veV$fvx7dI|ZI$5M|ar*ci|nq*c!MCN7WI|PrU9!XB+<<!f`telIyxyYwHgn9`1lxI`VCZF<P>cQkw&Pkn<%*x9gnLj6^(E;#CcsaTlUJjd#MiY?NYzfF{v<o~0o{jc{XTyWh*6?6BCmLr7=Y&n(II?Q?L1Z-g2|NH^jIM_l!zQEAROB^VDl!^<AMOJ8L*Ik@!L89maBJ9PH2OVx&GtQczbC8VPUIT|cct!1PUUZ@*TW{G(Vt<n8GawFO5UpEQ?5i^iJZ!h$@`dm%Co4yhX<jZ;MU~p1h=7XLr&$dsJ|k!@=w%1!zQEAlH@g8NirHO3Ku1x@>xsjv*c4AO+5?lgtm5Mu1`jzjo?P)Q~sFxV{$4VqdrDv<qYICTLv;3O%10ev+@D*n(Y7?jrM^@!>!T!j_hT~X!Kq9UGgb+rv4Z{hVFoOkXiW`YNM$m{^jS?W_wOXqZ{B2<Wr8Kjv}ja8S1>`D+3pxE<irz_o&|^pYl@brDRsVO#KV|9K8fzBA@aS>J4xd+6rz(M&-PY%xTDIGy|N0e9FzK--DN;li|taQ$9m|hJ4B=s85hjc|7$JxD{F(ZUyH>(>SsxC!^66a0>D%SEsH{KIJjgW5}m`g!%~iln+uLB%ku9)Z^jWXa%?eS(TGJvL_{@(PVHk@+p_3t`3hu2g8HOr@V)H5BZdLQSTz3@<8f=<WnwAU7W1SNgdhWB%{%Ua6<Aa7o;voKIM<72g7^N030Bn@)qh{@IbT&+=G0|xu|oIRryUv_Sea1^bPn8@+oJh&Q3n%Ueq7K0dy<8m3+!SQg4BKpxxjea4s|>oRO@`uRF3^WHkR?gWrI&qaHXr+zb5>?gei}H^Ljqr@V^#N4Oi>0q#IP<+Rip;nz{ikv)QpM&rS+!5%a-oSA&eA5eb?Z$vl48{t*x5AZ6u1KJVpNIvDasNW*1a)cv$d@>qM04E@yat`Vo<WufV{Q<lg-2`uje?V8mKfoQ)E^rs}DZfqqHd&S9JF+JtqtV20V)7{$r7lW7<$lz?;Z5i|cpdqaS5U8pyP)0S?&MR>O`V&p%84A=laSG9DmXD*6pe(7!u`-`a6fn*dK6v<uRzzrE8y;Ed$>EC8_fpih7+Ml9NANn(P(}+6&#87gd^c;Xe>MpK8pSWABESVC*ield$cdy9?pgqhO@y*(3Ef{@}-0;QdcCO@+j(2<Ws&weTRI?1tO$2deZur?~(T&`IN^}k0qaSCF)9KRL(@5hkTjfTGX}3r#y*z68V&0P`@Cba`_0U%ad98HEN?{t$%q6d8d$1xej$5GAiexE=ImQa8v50<WrtUJ&%0KNg||9LO$hc)YZtWoQygdnU&{|cMkcKn@~3)qjE9o667lex1?@KKIMhf3(2RPB0}mE<WsIqU7LK$$*GgUCZo{><Xu2M<rdT}$f#Vxk+}#NjW&Z@!VA&)@O&~WCnaxE@+o_%Ys1OW#Bg%hWHdULymQH?+?cvCS(S@W=ObScxE^&gcs@EEo)4RhMqekd*<L53(RW}koEVJ<$0M`yRPvf_DjAK|g&V^~(0p)C^5uhTP}d-*@<i&1WLEx-+UPqG|8i;anyoY$js9v0$Ae8qqZ8n%a9y+}To=xV=5%DvLPn#N;TrHn^h<am{2TfR{tY%6jTR?wadIj@B=1A=DUYL`0M|slu$QdLSsdBZlhJ5-xIFokKcoH<euUnJAHgQ0(fs7iPiEy?<TcwZG8!EYkAuBvIoJzlLDM_3rzWG((r|hBGjtd{jGW3>sIQP&IX8LDmYdv0gXA?^kc>u$!b8cYT#C9BS(Q^$rz2l#_#NtZ$frDldIb5DuTx(qpK=~@=OMH5Rq|dXpR$kIM?U4U)Md%2oQ^sx`O?AFsH>4r`5WqQ$fx|2`YD-}OOUq&nU$ZA_X+uwzo!10e9Bd*tB_GSD|I3AWrZ71Hz1$#OzN5BQ;r`Yb$s$ESD>yyX5}}jjec$Y%d^Qln|#U*sT-0}xe#?#@)d&Lr+%M&%4?|CkWaZ_gwzGer`(phEt!>zQ5Pe#@;35rBcF0x>b7K5uIk9#j*Le8!|%gu(0%Y4*km+Xj=W|oM@FMv;kIxwv<+MgHW`gxBd^)6k<sWEa9g-4+Rl-ECmD_Ih5N(%(6r>;2b+vWd&A}6uISfrSGW!OIot*|8I5*=&1U!u^ci{0_KdvG$ZGg6^6i8(MM#~Ae9GOZyOB?M0rdj%DQ}_PLQdt?)T_y?Jc4=znUyP38{KLB%YTu%dW7Wr3vN%{o_xx4sOOMRc`x-|@+se@zD+*mpQwK#pYmer#bj3QNnIH>IgM6#WbQ#mqeJ1L<WpWly@q_s_oyT5M!c3L-v9J}_5SZa^E<ue`agaT|1aHtKJNT4Z@z3R^vC3pb>rLLtX_NhKl8G7$K0{j{{!q#488'

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
