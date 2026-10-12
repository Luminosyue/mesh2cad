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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abb0b5c646374beda83954fc2803d968/part_000.stl', 'relative_path': 'abb0b5c646374beda83954fc2803d968/part_000.stl', 'source_sha256': '64187397ec37ee25176d7a2bf57017058cc642dcf46fee920b4c286416be05db', 'input_faces': 1438, 'input_vertices': 851, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13188256323337555, -0.16097430884838104, -0.17967915534973145], [0.08702126890420914, 0.11914972960948944, 0.09587260335683823]]}
GEOMETRY_BASE85 = 'c$}r32b2^=8?I+(5fw#5K%%gKNKTRw*d-%5hzO!Al0nHCg&|7@kqk2AoCJ0W!Y*J!5cEfq{OAfIN)RyrqH_D|da9<oc0A{vdp+kn@6+#oR99D5)%0{%k1d<TX2>2;{}l|xSFSdsQOiI;;^9E{z|d|32lwjIZBUuM{YS(E9(8^BPwU*~ZJV`h9}^fF7*(`uw?SP77Ofsvv_|);MN7pM?cQ(T;DMd{cIr2<Yd7&5bbfVEH^(2;vvdD$&UUe?mCBcjt5CdD+#7NKkN;(Ist`B%o75CX!(-YV5>4p!YKmxTg|w)Cc=1Bl51g)d*v%W<RrxJ*?iWpL`RZQRFSPxjXj(%5eXf6Wrt62Yk6P{K|MQC9&-UqB(YS8{uAf$Vg7Qc7SNZvty4#7*{<+63|E*<i`EmEExqjNLuibx_aB!dNhhKQa%}eZh*!2UiZ&Ch^hkSlQyP#YDgsSb|b+yLY1Mc6qtlsSIr*13P4`j)l?D}6<*y853cvku4e@$}z0S~%<Aaf1Z4^90^`SW+V<s_VW%3scoHg10CoBaO#_4!r#4YDi$@-5}(IjPE7p4DH^4aYZn{m|=Gl6`(sj6Xl`8$RFUYd_1q9qw_rJar(NZ|aX982rl)U;Wd*asAM_A6!47%ym^xh8aHJv>Sfl+i(2)efA}vZ}zMGnqTkm9oOA<KHnS{e!`aHJACc=`0uWt+B?Nx|0(NK{?KGqpADa>@<RiCzS-~7ulanlU&}Z3r<}Mh6W6)<yR*1{+`dKIT^%_@`SY&1^$AxRqx`yw%5QVg_2c@rQ~twE)_Lm_?os7kudnN4`{7f2wny_*7lsbTd;IXh`s=*yVEelMwjWpfvakH`<Z`Yb=$T37uiBvgzWY(--@2OQ%f}Dj|IiMf-{T?Q@y3<^-}b0}@6Ua{ZU;Nx_;$W-|7;6XJLk#hKVQ0>;{kvBoW1Mw&GF_tuKdw=*Lw2<v-j=v`nvwMuj`r4r#`l?+yCGExP?1>_0j#o&ey)3ultFeuYHrh`NCRnzYYI9K>079S?g`*xUq-SezJb<^L2X~pK=nuJhRpP`;ZUUdizhH&hDLFU-zGX^TSt?RQbgYsd74<_Vq*UhZj8I?}yWqeDzFNJYCgi)mq>AO_<Zp=j-#E@M}|_ug`BfpYyBBi7PPO-=0Nc+<L`*KFROb+NF-``=P$$3N_oZ)9dTw`ZquB%Y&+%k6Zcc|5eAWUf<LoKRmLjY6s@?gpoabz8)9GFV)cBp5vFQ^1rU_KkqN!QGQB3UwuMD%kB31x<0nA`?Kxqerx;zIeqPK`+6K1|IPdT?elQWtzO@>4}Q3M(BD4#yyKhpS>I5VlXP{BuYGb1RDRD(Ykd9xLXq8G-}L`~@lC%yes+zo{(1h`;`L4awO{_zHNJk{^KYMT`mOf=OkU$VkM}35{T^BAKd$AEspA^DY>l_y27b!1+w1H8`EP#0tD6}wUHtn!SVir3PB!J281Mhw!4DUC%{SiTZk}50%@3rF+ZoM|YxKi*udmCo^R=(@!>x|0a%vCq*9SkmdyIen8M9%vxBU~JIkw5`o9mOCANYK8ePa8%pO>GK6wSBGH~rtrH{;9l&G^EPyE{{rKeCB`zQqq@E*RC1yY~5xsQ&Bg{Qj0HzV-~g^~TO<ez?Y+?OtEEvz>3+U+2F+VzqDFH5!o=%}-3ZvdQb4@o431U+0IPZ{cg7P`%+hqxo@Df7|Z$b-RU@4cQsZxAS#-+WFc~mrpy}_0hh`FHn88cl?I3c1?=rCyvUo+3TCnBP(C~IzR5+EWU9UI&frHG(X{V%WYm?k2^bG`#L{0<&#z3ei9g!v@4pQu&%!^U-uI`U;8FMY2GT|`Tcs+u4sP3?2s?tw7-?FeVw1sYxXK%e<0uX6TX`0%QyYO%GbWmPrcjC^%GkDbx^g(jg>OKQ=8pc>Gi{Zyz2T1N6)PEo|nLZ8}7Vq`-x}%+3fYr{AuNDU+1URdr$3GUk{8<PLAd$w(hmT>znHYE8onMR=%0vtb8-S;V1l_q<rS*(Aiy4{lswJ4PM{O!&bhThpl`w59|E1b6j7~KcR*zqxy-db2oT>)6XZJ-5t$OoKt3t*Ejv#%GZ9neC9X1K4#vdKB>KWtn~K(z_O2aNAnXOe|C%4*Ztql*S^Wm`^rjh|2O%TpV+0jFJJe6J74=cKjB12RgS)HIWjppnxB~S#0IZ#u4k-#Gw+d~dZNM#S4ZV`?^}i5`*W2$zA6-7;T=bzrMK1iw*17de{J;oW<Ip?&G^#!C4LF}`pJM(Nzweo*UE45`lg>)`KF)f{7ffZKk&r~_kLqy-f4T{J-+D=-=rp`MDY`6Jnt*V^am^7^aq{)-qEo4yoahEOp4|wUU<=$Z{|rW-}DFaQ_GBW{j^FI)jZI+@oM+DHg<A-Juju@-Rj<#wEa-7*VlP{Julh$W*)Qh^?YUL>-kFisU15gpLyxu{7|>C>%6|6m+X8qk6HP8zB2VW7q8lxc`2^e{HT8D)TVV_U(XwMzL{rq{?zKKJx|{};LGowBkUcIX?=!9^+Ut2uk-qPJlgr@x`q7Ekp=I#$GtAI`#BhBcF&zRLTz7j{e-@i)aT}oUz9(-**o5G8aVWRax_0N-*X$hzWIE#^3C|w`Ro2z<{hV@A6F+w^YuKeeRDl*<(u)V^JDie^NrK2Gm@kEiDeG@^36E4^36Ea`8~ES^Nz<r@2Sbr{KQd5eEDYHw(`w5)%nLqE_Kh#<@Ktc$JJRY<0Cv^&Jy={f1BYx_XzE&>7K7}Y!BCu`*MYP9`Zy5<@f5i#CzUDu^W<nzP?YGz1!Yse(0%3)_Q$&Uw40xz0rI--`wxD^3D8U=j;2oR(;I)wern<T`S+*Pqy}J?k8*iZuuqN{vSBBB+2WWd7w(Oz0v$o*}7}JzL^KCd@~Q|{7yyHe)T*syRph|_tRqUc#q3jEUF(W_~u%#Z|;v-`DPx_`4cxR@{ZrMik<gF^AoS+Snu`q__g!RxYqfj1~2lC-?aU;_C)g&&vx+T>+x&nn{lo4GdEu38^2Ya+!NJLo8`+l<JZbJzRn*MzsNU!b-wMFndi$l<JZbJzRs`k>q77N)z@#~PNx@o$8V^^KIMO~Vu5e`HZ7*c$E@iKeEl|4UghV^FyC8#sB<aRpTGHWp0E7j`ILWh!aVPIPt1FEZ!|yDz3dvVZ@#}AKEF4bAIeq2mv6qmSox9b1S?;Ezp(0K<^iiddLFRz^*mtjSI+~+U(j!!Z#>@K>+|(^Pn-W<R6o?O>l&}G$Ge?x<^i4mL5q35@&4J{d!zZGZCic$X1rVZX1weCENkEPj_YviBYUFxp^dH9d3|%g(aJa1=Q_XUq_@4}I{frId!qTFsw;f?=KhtHZ$963{`~{q_Kxegt>gDZ^Fy`I`0~v-y?^YUXuh3q#;KKWuB+{QeSgWSkGUU0e(E<%=X%F)pu!OKJ-y*ubA99YP7mcD`1mdF_ziUG<<>W~@WHoy<2PSN<-al7_0#%oSNXFZR{oH<Ij&~<R(*e2UDEyjk~(MpY~Q%f@~gTZif_j6;A=kLj8og!<58FM>onza|6Gsj)Rdvh-~6TWUl^?Jcketu%l&(~t!ls1zFh6~1G(xX`}~I6RQ~U$x!$<q^G$uuf35rq^_5@arrK|VOlrS{FU<6{TY&;eUf;Cy=Dt4PoR|5deZIMVJ~1ZQ>znhwXO_>`^GsTnulM@$&HeMge11ZaBz3$M!>fJ1e!hI^A76f;LyP2S`R4hul^?mU?%%JO_maNx`+B}&o;2m?>xw5Y?}_GzGCsD>=j-c)3<vi_^F#GJ`t$YYduY|3Xnttvd|$q~Z+||#Cz>C+w#1ij?&n+iW*)Hf_4R{QA2SbF^)c5u*72Ho&pKXn-DS0>nTM_RG@lFBc`=_0eC`-ue@<EF*L+T0%I?cIpR-m!G0)|#er2A&YybKOs^8wYsQPoC-Ku{kZ&&A~RUUu8#n;cvLX)0T^~o|om7n{dDrarW)m}f;yj`--zwn~UuXb7Gm+YhbKIPSZ%Ra603sqKrm3%7y=&$~H>0U-vev!YEeD%M+bcTCe567x`pvi3IXKUp8fsHv;`IAd3|D%tmyUIErGhZdY?D`4KA64a?+(`W&obDZ`x}M=NC*E|=pEdu7tF&-^`|~1vubS)IpD*ECYbUwqHGh})-Ti-&X<NL<w?C)C$#Y!a{#*+;sWs7iz7qQ^SJx*OvMFD$qxkla^4I+{!7X3kcVa%&zPZ0-`+D6=um38)-w(>SuM;fae2(L%yH2otJ3rlZg5{^nx33c{-{i-psCHPIL!I}%`&N7Xbk|pwZ?2c{(_LR#zR5qfK^-sa-$H+6P}hx}#;Ee`>qg5r*Ma!yt{W}i<QMJj`sVXaUx(j%PL&^<L-q6aP1JQoztr)rj^63(C)&6BNoti%uCLeo>Fe;+*!ixn*E8t;lX@&P-rH|O!xyRRmbraYIXmxD=Ott6YOinRhq8H8ey8VMKRjgc5%=F6I_i!i?WewT&Ud`2MQi)>vz%1<_-3Bb*H^bnj`xnE#A)yE_4@Yr0^8T$3sUz#uG&G*x3d#f`Au$&bMvk5FSf5gM^dw$b$#=_DRg|V*Ejcn-u|ERzdq#psgHbkAewJ~kJG;WJ<gP4eUD3Bw^{jVS5$pk-|+eRyr(U{L;qQz>aRbKHr-q8_09Lz7Ypw5`TBbDi}q`LzBTWqJ~K|$M}O|{d0~9LzEqcwZ_bOp-j023oVUM)-*|AJ*EiRPhj01v&2^yd>-C>{zsK4sUw;m=E;@B?9kpNmIs4sWpKm^Awcn|<s?Wi{)wtujBK1~Km7}lQgVon~ee=2S(zhyq|IM-P`Lpg<Xg@8fuJT6(C;9wFh4)4C&FAK>ifX^(&#Cfjckq{kpLpSqy*|Im5!bixt7zYRf6?XRo9{2$&$-q0^*kTx{|nWAH#Je^*L{D2&!1LqUo_v$1H1CmKl`fVn$pEz4u0Ab8U5uPE2GNM-^-pjuj*O!R>-a2nV$ak!B5+E!QVc&&WF7930<7YJoA3YJ1)%pFn*gVXIMXfJ+;5^`d**kWU=d;@2z^=;hXQRTpw!Rd~daV-5+#0IVbv$cUGPWUO%yEYvs4Q&*!I&sk$$kpV;T2eZF$~)em{wIjwtc_4i>_#;Eb!N0q-b=OnM6_{y2RKELdq(XQX*JKF!e`n+t>WpuRqYd>vy8(;m6Z`EJ>iH|+vtA8k^>l<!6TlX77SF^Z&y8DyEY7h5~UwuEb?BQYFab)g)mR&T|-L~($+P=Pzil6SjtL^Ljl)kQ??!K|@>-)g?>FyibzRu6`!4S6``@Xm3oBP=K>F#@5zRACOd$8LM<6m&E&lCISKJ4?C7f|c27d~~w>!-WVZ~5lFJ$}0T{FZO>hkdBZxqpybpTHBj4tsrlJ(*goxT;T<rLLd4_cb>^)V}y(uOIj$pSu5b;u)1+wxP<OGsVr1%UJBN*Vo^h!b57g`Ke{|4|4tc&Lw%<AvNXafo{D|ELPuZIu$wW^J~57`l*Go`+Pl4b$wFX9aVnOg{qu&We)p%>XXpB0rmNHfVZ4*laXrP%Tmzq*Gy4<yJ7v^dhhv<I$ysPP~}{0s(if;ymTey4=d#Qp#>A&`lPifec0=p>xX=`{rS9alGd+|-`CeI?JKEyrNHfe?zWzP&R$pZPyCX8-ume0O4_%dL)pH`pLM6NTfUyhdMs4m54SCKee=2Y)9dQ*CmXtc<nxGm58uphd|nt|&u^A*<~LnVfp=bW&!6=iQ2VAnD|hYn`u1}`?c2`*ZQtZ?Yy7Hv9<1lH#<!lsYTtg|s(t&ps`0Jor`orlpK9NJeroDtKR-SBYah29`?)i|Znw0HEmVGirmnBA!xI;cQGTbDy<N4RYinPh_qvZy_WI^JMEfUK^>TfEU2*pCM4zv(D=go9f84TJ)#qOGUcP#c=s^Ad?CGmdf!q_lzPV1g8te1*b$(jLjlObB|FrVW^@A>d*4-Z7aT>m!iS}>RL!C!`9b0m;*N<Gs;@|tLySra~{k$!~@9XPl?H5?@`jP9&n-jf$<a!c6zK!cgu466VT*u<~`=^_)pByMb`#j&(+i$~5>L@=x-}Aoywri$ZciL%48*l#!Y?$x!?R6Tquh(5@-(II-`zAl-SZlYQ);bg0*Xu^KZ?7}4eUl$Qyp`K7HG}T)2mW~JL$}<NmCanW*UwnKSr3DsZvBkq>-=zh+eYqwm)>~K&HHM{Zg<?Lbg1Xn!&(=YI_CbmZl1MX$oBR6AMM-gg={~PpP1lopMO}jL(E*&4rB7v61CSarQRD|!BuO$Q@B&B=cK;&IxE}P>!!4Cud}j!lV4zYd$$~G{h00R^<dh!*N@r0&JQiW)zNKlYyDfO)1sHex7X=u-(HVrd~3a&?c3$s>*Z|U&bQb5X+Pb1zis(D$9vABem^Mn)`zded(NYNzbSn3wQg>ETI(cjU$1-AzP(P;_D%k_!>(_y^R#`vZd3dAI#1h=<Y({cmSe47wSB!FRr~h(RogfD@!k5wd&Zq!Piy;nJ+1cb^|!XK^F!M*^^5n6$Fz46-SHS6)?%1<9O?DLwy)O@Yu{dPZ2Knv>WE?9^J~68TE1TYtbKdEwC$Vx7ORK(&b!XHe7$~K`}TTo+c)_szYlloX|0F1eKQZ^+w0YB-{hAqG{V=fSPyUedOf`M?e+7vZ}L;(M!MtCdS5{M_WJ_1Z|B?Z3)sHNFWbcR?e{5cU%wxrefxb1+qd)W_bF`O&bQyQuzi!?qQEHcxYO^C*uH*$MEmypCbn<hHz_(a<n90FeH_a-@5|uZ@7LJA$?r5R<n8|^-}24-LHOz353+odKfcpgU%%DwD_OpIUkN|m`%RXg(7un#Z!&0{x1II-R<>{6x5BsI&$4}!e=py7x1Fu`%WPl2FQ$F_{W9A(`4<L^_q9LoyV<^e-%b1W`**f)=iBe!*?ziw>-{_1H~B^HsCrh|qt0*l1?qmz+`JRq`dIHR+P--Y5#N4q(e_P#l@}*?_Zwci`LNHo-p90k{eGqP?e{Tl-{kk}Kf!xm%zLu<_WPvTx8El<zV$w7_`+gU4)=@VswS)B%C_D0Q)7my`)vJIx!398F<-jAnLo|@uzo-C9<K7u{AuN<e{UB*-Fv%!Kl0wL^3%V!>-X*a^zZZfeY-yPd%m`B^5@o@=<O#7x!zLkd93|JUw_c;kDu;6=qeLbzV%+V?VI<k@$L7rZQtat+N#R=a-XWt-8HJ7O@5r{?GK^4+mxT2Ym%>@44bC>TcurJKVMGx>`mpr_<}D#ur;jwkH$^%*54d2zWsiB_{EKHy5(5!%iF$wFJAlhd-S$%@(UlF;+A9m&VcQk-xI*Me}BOCO@70-ruzD`{@!8v30;Qy^6lSYuziz1X5CcZc+~lpZ|B>;BVqe?zWw_Wwr}U#zdK?3CV%IZY3}%Wprm_$ATXp;vit7}KRVree)aEo*uMT95AEB(`(gW${Ax42<>>yVefxJ&LhYK*@bwdZcg6Pg@2+Uy{+$-vH~9@S&ve`2&wi>Me*GlLZHF<1W_r(~{#_c|*S|}nefxKHY(HJT^?N(EZ|B>;!(;n)zWqBqwr}U#zr$nuCcoXVnZEWn=S%ta?<|EzHJRl-F59<%-zl^+ahA88ZQuSKD(&09L#2KDcc@Y)Uz+2Vzx!iV{*KaWz4eNXbKQKsUSiwlYF&Pof8O@yhjy%Y*Ndm-fA3wl{|ru0&+q3BbLZQHHjnJ|`hkCXD*tkv>!&S$N&PNe{tRl}(A2^zzx{CceoEZf%E~VlR(|3&<)6By{8KBV`r*~t-ToW680+pY?W29_dws@+t{<NKxO+Vj*mp0gAMXCohbb+6ze2bu;dIjXbprv32Lssy-8*}Jf>2EPPiyp_AnaA~|LP|Q%U7&W_5bfT2s2f6>QKRnr_oCA({M$!3S1E`jh2H&8^NXFnrKg0v@={2u7SP`i@pTcfS*CD!=k0&XW(LJRk$k0Pz<dI7lVtVrQy=lsW@5#uE9QpI|iM4I8ob)%uZx<;yx$-h*A10nh_SgAC?gQEk=d#|Ii0u3E==C{IC<9oJe${9@-ujjfdmOtw#tyiar28Kz$x1gtMR-;VkeYXl6Jw$NdN)TnBv#eu=u)A%yFq_27E!yDpjq&O*7uSES9H_=OPu7X1$X7CwP~2A_bp5W?FC;hlu=7wC8J7x4G!ukiQqZ|D{HH~1=g621zbB80a(u^IgoJqdpbUq-LMS2+I5gzz_n@XzSC@Xzoi^aOkf{tvnZ{tvu^5MGFGgBQY!3E_9po$wHJBq6*K-3hOR_oH9H`{8rw_wYIRC-gV?C;0wYrB`7I;X8Pz;5+bHC-$N5qNm_foDbn;=puA0tk2&fLU;ioyo3<mj(!Snhd)Oz!<RXipA*8T3E^Al&+sicW319ku!Qh!y#K(r;WOwC_zb+)i7>hp-2w05+zUVML@qgw7^UyVD3%bOfKGxZ!0pi&;r4KOv;tfnet;0pL<najgv+8Y!e!x?&`I!1@SEtn@SE^1RE}pC+rs$>;Q{F5@Bp|UAv}l>&Vx$3<Y8NQD{VCa-U^RH+r#7Fc4&FH9b6iH04@z@AcVgOD9r>*2wx7U5dIp?2ulcm8Bie{<nLwSAY2lC2`&k@Mc;(m!c);*@Kks&Ds8=&ZQ;0}nnOf~p!wi@oC7`Ih%QD4zymlpdcNuxjLc*G=+FH)XG@7ejDs*d9L)m{hx4Oy{_?XeoXj~L2PeZJv>hCR+n}Z4HgIt?16&*qIC034b549j2wz0y?-$Vwa0br5@KGn$JMk&H89s(?L^s20(YMjf@Z0cwLU<v%9$pAfCxlm{N8#1*5&GK^`rr|K-6xOIXOB|9%bt4c{(LMD>F38d-iz=@=tfu{n{GqlLxk{3C#Irrp=;r_9KY~fC+0b^fe_y0#BuavLU<iI4_*f^aN<pLGCB{Q$37+#!jlN$iG=VRbOSsGUPB0ff^LF!T|Xg&(+J^9gz#7B$M9G1c|!Owx(+@JuR<5VtKey#<DW(dzaCJ1Msy+iW+2k9gy*A^;mNd%?vs-Ok-j>K^EHX~dW)FId7cW7Lg&Dv;3?=DcnZA2iB$AMbPc?QHvJGygFl4->%=x^Z0>L(M^I_bpkfK(zJzdpLU=GCoEMdUpO<anolZ<fC!#xG(QWWVc)SzOqhrx+@K|^YD)rmKws3Ch+!xLb4-BenA<+eBU$`&FqpzKW^);37GIVe-axEshj}Tsg4u)62Bhb9?2)F<$ZBc-2;XR)A+CvCWaiWA1_c;+0qx!k%SLl5)k+C2wV<k35o!k4-G&qg1Bz!-)52EsKA0&j!pe10@=ioAMM|282g*ta6ggc-U;fb8r4utRvo^$^KS_*yvE{Dd#u^dA=^g*~B{4`nyE<>H3MmxYA*oW|NCl)&~&xxhzJLqCq^fvqs{1+jtzb^~x@6p2YJ^Nma`hI@biJ?xs?ZhH<2`st{UPkUBLiiT?2Q2z4d<(vT{s!NGZ=$#1+Z@kLLU<uM93D<x7ZSn?&_(bf_PqeT0pFlp;VVwFTy-LAjM8i|imN-3#fchdR#-F}Tm!D<#7Hy&%?2mHIZ)Y04z`7FI<X(!jb4RCufV(EorLgSLijo=^}CK{fhB~038)Y*z~8IG1>pMV5V$@(*oh-(3OWQniXL*}loMY#aTq-WzmIMvgg2pw;7#yGGzCs!UmFSGVQ6)@I_F~;S_>WqkMNwQ5$I-kGy5KaZiEXu-x;eoQ3<ULSAy%IRpEMYWi%gL87_qW6I5IX{>zEO==+55LG&N^AiSFpzK%+{*Vz`%#lEV-x!|&BZMZBPk5+->;WAF-MDwCmV9|oG=-r^=yzt*n96*ntci}_m|IoYe|KI|YA>|ezge#zx;0kbEv>sd+u83BKE5dPTAvg~HlXD~O{-@{M2>;;pi5N$Ja`eAW{OH8rPBe79*-lL1yiDO-O~KdaZZ_w3x)bj?F#|meALj2f2;rINY<MQz9Bl}TN?n?>Et~=U5f=R!mJp6be}ZE<z91^cD=gXs4#G{*>F{*w-4vY(H-(#_&Ee+MqZt|t$FdJ$Y3E}cgJ>H3BP@0Q$cZnV_|S<LoPX0jsP02|gyo)VyP&!k+yhO7d%(TWPH-pwT`xkoC)yqE3BQ8A0E<2ki%Pv-VO#hs>iQ-86?_T(0sevWatZwzz64)J)8NbS74#S^dJ-0uwz$H!a2MLA2i${W?m`H6LwmyA;I8N^u&5kQSGI+};}|c&m#FJ^gz#1L3M?x7zKV8(yHT!iF-O03v~*B~@b851HA47&jQR``JxmCnLcfK-apGJ|<g-ikD0&V)3jc=?{+<y21^osVEgDq(3tW~EF5^Ubv?N*-E(sTRqLdRQg6g=7!G+M`a3Q!LS`-$QdK6?^_-pF+1^fkV@HHWP0sR*KmUh2@7J>^=u5iGaKl3{gB!r(ttHV#iHPAY64Y)p94XzJAgFXR20~dDU184s+j-~`v2;V~s!-dHgmJq%XR3V(3zgL5E!{yLAa5*>utqv!^<<b0bc{mRmfb+mNo&8U9BH4+z2;o%pCM+uXscZ{>hz8-0gGw{7Eq(?<_$l;B_$jy+S_7^HH$dyd4d9ySGjL6~2wE5}0>`2;a4h^0=Sa?<@b}K)WS2QUphEcZ7^U&><8W=XJ6s#?;lyibAGAB%8|{X6hr7Ww(RjEf{1}=YehmJOI!e92BZPMm!bybid+3kwSac>KoPz!cr@(hmIsQ9r3+JOvYQy>9hG-ACA>5M??(1o<zJ%~nLU<k_JRI!<>oy%u2oEKM-zJ1#C4{@8-QaGtbyq_88T2vu8Te6D+WJwpg>TUQyWkt}K2KZAdFbZEYff}=qK6aRo#;>d_a|>G+!yT*i*|+k!mpxT;8)>3=xea(8*m?ZG`bJoN1aEbN$_ZR3_2DbOFhP*ufngg58;ANJmExMCvu~Y6T;ciCt%V1aCSHcA)FJ<2j_(I5W;b^?TfUTXa~4EEN#}@iS|ykL%YG<XuEc3SGXPg0@?w70d9r92#Yp@n^CV;gz%GSJ~$u8_9P)(7<~dR3>QKR!UZ{=LWFP&v>n`zy0##MTcWMtR_wbaS{N=&xh-jDsduh`{I5I%fy_>1apI^mhpuvB4<Wo9eFI(&4|5{P89Q${F$Qf8kAYjGPr|L?Voq#x_IK8aQ|LYT6nqzz+`H(Lu!Qih0Tse={Jl9G2RBCFfE&ZFJFy<!kG=tmCc&al1QqXx3kQ`BgNM;3g$d!#gzyA(6+8i6j~<2B!xstR^Fj5jWP3n8OA-Ad5P7yDd=C8!J_pM)E72k`iY0`Lqb*`0&%%V;prd0V&(4HH=zB4dXKljC=##<7vpHdTb|*SI7<rZ_JRDsej6C}j4x^t0BhLzj_o83Id*L(agRzlk?!vdxtg(@2^uihO9*B)R(-)R!{-V;xdJTZ^Y4j+3l<}a~4+!gZ1;X3W<-y3B1mPv<uwY~jgYZD~33wo!8<jq%@A(UFp&yQki990^9*ee)i9AyfejY6bKM$8eWn7hFTR0Xy3rh&gz4i~$RP-z?x(yax2B*R+&|&ZjSf2BYLWiKk;MQmpbQs(Oehys*KL-y$x4{G8Md&Gb5qtu@3*TiPIY9^?B!q9HGN;^TTR1QCOk+4N+yH$YZUB$+%sZn9;SK0TcmsT#5dO!BAD#YC*@+*}O7IVGMf5?qB3uELGAf`K;fw5Bcs+Am1?IcL{M!o5Yt_-ta2vEY+8OT59M_u=eiK~}zX|U`FT%UvYlLvNSf%IT^NibUgm5u5D_jgNg+2(Ef{UXvj}&KHI6L|YEFt_A-fH+Ocmp~b-T+TTpM)pEHBgy1Yp^Z+Cv)j&_)qu)LU<n`oa)3w&cA)ei4`$Q#aqGOM#C%M<%IBjLbw;&0`3JjL5sjm;DV@pt`uZj_%}XtzJPy&Pomr5lkj3E2BYtw+hNg_u;^6y9e6l83LeFLG2Anc3@3!!I8oM#%1%@xgzKYi;QDX_v^CtCIj8|4Tn>E>E(bS42f&Tsp6DXDCp-f^0iR&rnL!AL2;u$cZFoO?6O}pWCfmX}n3o#FM4lfBC!nKZBF~$IN1_|xk+6RLBK$sjJSK8)O!OLh96rvxrSGQ+|BlLh^gCK97`gu@TpF)3ELsjOhL%Fh!KL7*3E^sJWmxn_xElOBA)Gl@h490UJ{qg^5kmMrRC4Y^e}I2r&b^O3;RbjW;0AC4S{>H&sqk~?i)b78MYs>z8}7|~+J_LHh3<l9!3WT5@Bvt!vB>im(VXZt_!{$WPUhQUa89@kS_&=$$D_q#BhQ9}%c9w1BhQkAbD=V~>Ss^F*O_lO1S8L?gm<G8gOO)j!c)*1@D#WqDsyW?wuS#@zWo6H8~!i45B@KFj1WGFroySr#V6So*3S?`<I!he(TCu8Sk{#XP<amjF#cc6`7)>LXY|7Fpvz+-&+&zqqVr=S_hf|iy&B=3XfL=IbG^RLBis-z7!$b{B%BYGxnAEp628Oye=-oc*Cd>RE)GQQO$pERd>-g~S;GC%esF(S?hVNIaru7U5$yr@Ag3cCTn`-#59YI^9y%Nz&b(g_tqj+LpF+#RqD5fQEbvqCqiAMW^bz<`I4hb9&I%Vm<KQ@sxd0*D5bX$eq^=DK;iBkM@Kfx&D4G?{O1Z*$oby=4iHd}9RkRaa6;4D4!in$zbS*ppUX5lADqaoWLF>a3!rAf0!P()qgz!8<cs?OK9<2|Lha00=;l}V|sMPN<wuRSG=YjA#co5nN9t6LPR)JrJE2DYf%J3sj{4b#NPc#qwC+Fi~yo&I{aArcd5?U3m1Xn{7;c9SabO78L?vJj9`@^fyJMb#_Ix6SpI@`k8IA3kyY;bEQUPWI++rn)*m%=5SV^46R3?W?0iE&Q6;>37DxD#3nu0?()LbwhgToNq-mxSvQ!nFzEc(e>04>u-+%cHg6^6<0hEAX>$FLWH-3!de~`{)659DD#yM#sZ@&<W^xcmkY=c7i+67Q!u^^YxSyO$p&b=-&awh2Y-<N>9VT!=Ir$;LqSC=yG@oJP;iL4}{yIL*ce?Q*<QU6n-8J!_UKm(0AcM@KW>)ycGT%{RjRW{sS!<qxcWFaE#JcaACL^Ivs8X&qNQxGvO2HQ$fWi;95bYA-EPi8C?rchBu+d;Z1NF`d>H=emqv`L$Qh_giE52!6o6+XePKcTmroiR9phifgXb;guljH1Ah%~B!tHV)jCqq5$Kv=WZkLo3iMbovQAZaA9^7eS=TCj7L~f5Wn1_T`dDn_ohIS?@g9neyaOft6Ky7Kr{9?pK8GF;M&7X!-jA*gM&8L1UWtZ+k$1R+N1{&!Bkz0($Dz_!;@B46OaGZ36M5G|cq-Z|Ch~5Ga9gx!Oype>;gYEIb^Y#%a1cEch`g&J{3YJIfylcp!bi|Bd<0&NjtoTJQxKkx4h=-!YY=`N9Ra@%PeYdnBJ10QSD`xsk@fJxhtbo4$ohHV^XT7!$a;I>80I;d`(g;;5@<`f1gzH!i%vsZ!qeaxXjAwzbQanao&`5T3&D-xCs3JlpI}?~r-0JW;Gf|4(IxQv@GNv7JPYoHwhcr+kA$B^n+77EU&7_l=L3<?JK@IYpg`pFQMfm{6z&brMn8vV!yll3z#qUrqcZ3I%(ifT=HX^=e)w5*Cj2Zs8$AKfhCfGT&i$Ni;b)nLC&SOe)6h-uG&mVegOlN#sLZ)H*%r>jJX|t1vc^NWJX$(7vL-}00WA?5SwkXR4$To8S#u(s8<ja%uTc@c!92V%7+KRIoaDq*bP~D|-pIT>i4ZR0nY)XivhKeK+rkH8lum)CFis8-!k?luU_E9&MH>Ybe+t(ODxC^XrA{@`BCx3JL-+@$&*XCWRzQVt&KRY2;hb<C^ewm!JO@1k&w)=1JNszi#9TtSB`SY!iJpNagwGPfbJ4fpxo|zSE?f`Jjpl-L!`C=IIp%AG@E$@qnGimJ-U>vnId6I9kXy_#qS8is&dJG~l#@2nb5tGXusXDnp3~+q=gpzb^c;Aa^DHXu^%>hOIM1SU;70IN`mOX)y+%to#nX>d&^f`#S})-b(7D0LS|ZW6(Yf&3a4WPWEGp-$75%a%{Y<`t%lB#dUM<h-<=K0ofLf0sYb#`pg{+s8wQsTpPS!Na`b1f$C~IG39jmNom9^-yu3Xla%R3A5{(-!QAn%6Admi$>hx{ghyx%YH`OEJx$ZsmhZ!2_gwqJH4i!;{4PTp=OGCA8-oT%!=A5J{x<YjZ>At(Ade_!duD>3o|8&0kh4+Pw0Vs6|YP>+)3Kj)tYGB}aZiTj**+DRDYm_;4!;v~K9@CC=;>ckc&{v-Q{QSq(AA3OSq6KkA!*7-M$oM`AoV<(z8(bS0+PBeF-nG>y@XyrspC&oHu4|QUlw11PBVD{L^kA%cmt~R8R)7TOZ2O|H4+=>tFHgIq+el^7Ym;Rp@@&3z6PFd#1Mp`zxFQaOJpnFq)gS-(J_&*2<W7_'

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
