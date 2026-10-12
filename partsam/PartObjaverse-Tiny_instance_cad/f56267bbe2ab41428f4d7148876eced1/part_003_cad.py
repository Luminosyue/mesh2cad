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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f56267bbe2ab41428f4d7148876eced1/part_003.stl', 'relative_path': 'f56267bbe2ab41428f4d7148876eced1/part_003.stl', 'source_sha256': '5bd9b211b1dd32247d69c77ec8a5c6d6f643873161b0b13dcdac8083ca4c8910', 'input_faces': 1052, 'input_vertices': 626, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2609211206436157, -0.49930593371391296, -0.05303948372602463], [0.05449708551168442, 0.389529287815094, 0.13005638122558594]]}
GEOMETRY_BASE85 = 'c$}qu1#}e4)^#Vi6WkfxAp}A~f;28cf_oSU1VSKqf`&$d6C}6}uEAX!2=4AMxI6b=oPX-<J?~Eb_5QW~^?kf`*4}5=>C@F!)zvlCop%ER5+%;0;a@&&WV-VoJpDCIS!ykl7SXlefY9Ks{Y!`U8SJK|7hU~xVr-)p4FlV_X%X7cB3-)n5AIjQ&r+mPh;NaSmLeg&`wi&VDZFFveqFjMy>_Rb{kuB!{@pwE>FV%{R`9A&(o(KiNy~7{|L|W*M-_~BTQ44RpxJrka)p*>3ujezpnhS4=tjB*3l-XYldV*`<>E@j2M<XQZ}nUbJ+z+aws$Q>H>cT<Cq)GERKB-D>DtFd(6c5L-BRta=;lv<(QV!-7bw)yoZ2Y)7x_Rx7qkZDsUnqb-1CNBX8Tx$`o7aPrQ17rK`#}EJXwZG9?N1+=>GQka{g@HM7QNB1^se)<j?t9@>>oSg?=+pg7exs7KFYse2!rL_;C{NvHgPht-3_Zb@kl3Ug}>kqv&Q_hNXg6>hu$Q_UF8yfB9HBK1!P>_<j%c?YC`mU72!i6WwzQ^i97+H|9UzD)reM2Yts`(Y2gUMAruO5#8wBBu3&Irw9>!PdCIzR+=t(Z<bgi{eGaP=(e7t*9#t6(GLAq4e{S{EtfoNXU-9f@<sfBnuxDctCd3gpHk3=WQ6`8zO7tG%@oK}EO)Hn)?89gBlWR!5*K=LwbbWr7mTY$J483VOD>i1@wj3qiJ!Uwde)-Lq#oZg%5nPLYRD7)a+T!C^IXQQwk!kUL!)rMG0!K99`f<5w9k^D;gaWi=tPNoc}a9z2QO(Cv*SH48CM&2iEifgF(gk&_-4sdW)<|WiO?TauFH7Vd#^yAhMp?~Yn_*IYWA58J!8gI(k|o1OaJ~y&zwYb&Fz5bM%n4mv%Op?^-UIyc)yy^o1L34=e-gw^>++xT$fL!I62?cS<R$9wan1<_Z#H6BAHuB{%Wa_$A9_)xt_0)n<U@Jl!&i&Y=dhaTdkL8#DCpiuGhT#Xr!Ds`E}8a1K$>lA6ppppS%h2$>OBHocFa67$dsvSDC%y&#FI6+O1Vf=qXR^k^Eb-O8?ulHbI^;mC^1U<AA|mPD^~>i82n1*~2Hx`By%H{(f$VVAgCiWqcMn3q5+vI>{GUaEqL$=rQOM$NhJGU_aE;R!s8SyB~!<W;fyk8X>;ag3}ncF^47ocacTXZoMZ#kBAoCwq!s%sejoK(3b>YUZ^!f@@PJdkU#q)^!wD~!=&7&4&p~7miyPt^-k_5{hOcYMv4O)<+#J|CrbHXALvu#56F4DjvgrOxyKv2mU5HC$6t|n-Omep_5l)aBz?3{aEK@Lw6Vy4X2C>P-B!_ex77PbI~hOLM9)u2e7BV{|7drQNq^asTt4MGek@yh$vmpnIVHNS+6=j0^xIb?-aNe)dGf!O@obx0b)Do(wMKM3!!lF+lE>pDKGjmh7d|QRmU+GsuTNeCJx^NHe|n_o=7kYBZ{)mrxZhXFdG*UZ5dV6&w2yh#N1iW6Gb{8DF`^sii-~T=20?%PkLdd82BKTrl)?2jsUp7Z#gbW4-nJ;}Un7r<2R(S%bZLiW&reF8B$*FN`%E~1>!q%*NM+)_x`c7Q`T*i5r4!$rR&<*9C8vpQX{4Qy{PDwa{`Uh#x8*A?dF}l?w+ogT0R37vJns&CA0p@N8;1NP@=g`ZU0Lp5b89=~zZQR7@<#6IBDk$N^4v&?JbNu`rM^Di(94_{B=wn*L+Ysw%?f?WM!DZD5v}G)-osB$$n`vU&`;`7>&pfyKXOlW%et&`Ub9Dl^p~aPS<!7PHm;R=W^F0s)^c_N@<i6h{Sup6&TCKGANm}xX}I6QWc*mN6-J)4gLjBN_z#}HZE}ll#2&`FA@5#!o?CBcK>Vg0SPzVdZXx>OkH?{>hF&aMo=3L(??pF8`X9tN4wd|N+g-%R{WvD|tUYapTxaN9=w)tok>gg6X)pDEGe~r^>bGEtt1}JjsM4W`uN5Wh9Gm;5nUcS^RdjuHE*Wpywb?RHTfbC9eHwf@B-i<Bx{Ocj?rhL&Cf_gp*Y1?Gv(;Zi{v|<U<a#pt%k$R$^Yby$|4fXOdKDQe>l(Y;Y3Q>$NSu*Xlk2snm?XOM`D<Qy+EnT{B@FRp{>V77oC}{Vc%hx>md>@~<@f;fkKWRP_}DPXZ(Dv(+S__FE#ez`oss;B9$96)b$Agk@$Yh<miQ<S8E;0%E6@-B+$Hf>i^@D?U3ye>i(!*I`i>u1XTGnG_~Mh~{xJuC#dVb{h4|NLF+OK`%k$h4kp=O#sd8T9T?uJVW5U3ra{l;K($40A!!rLH4V#N@=6!_q&!09{!SnT?KYT9hF{9`s8MoGp{-WCo*E=co>+nG8rA@DZ__B48Xa9bwzkaDa&YL4d=6TD=Cvx3di_Fl&KFatsl1^SGdFTFfMEb|aknv*;!n)XOcTaR%xmt2Q+u~$%B`*JJ(Jem@q1`eRmppp^?4p}zBc#2w%h~a~8}jh5=)JEWl|08!%Y0z_y;pSO=cRK}pZ=X?yl5kKiEhhu8twe6h^#jaeZA;<a3+~2t<}Ct9=o|3c?zYH>osHQ$@y(Z=Ha|tA6jz1llxR3JrnxV6<FsS*gs109i4&mUYW8_;%aP=`_!7U4fIYqpto?FA;)FN2t9nAtRHM=W@5da<Ekm+aYkObF1=4h=})sr7tt;E=14!<9v+f*wY~@v-S()ujDK6bt!SU{;?R$dl6E!{r<3Qe_VUvq$-lY4S<xGp!0&^GTlY&l6diP4&bKZ7XgPnP_j@JJ-NkZVBYHO0nUfcbuB9(4^|bkY!#q>)#vY~HM_;@z*Z=tLZdcv%^f>ffZZfWnHM>N&hU~wO^Ss3PEVf;Aeff37ZwtdZtHcuI@$kTP6~Bt-`-YjKn~$D6kn#ejc1rzAO&8sE<f-WPZabwu#>TOt8$ISpetW5Tl3(960{QFg6x~>IV5_TcyfqNtaH_PkzIjlB^V%Nm#(lq~2kJkg4dO>#$NaH1I6-|Z<$B|~D%3=~Rq(>~#&4H-%-pFb$gdTew$)X)6}W<SOL=IYt8Sdwiu!k&i*-w-jA-W#6GXRU9E|Z;IW_Xn%OScsp+D}wDoGNY_dmaDs9VOzA%Ep^(*DLlw*=Q^OZo`)IsA0D)VqH(w8Lft?Ogql=$3iK(GL85XB@dNx*ixR@!F-Oi$y<r19?s_Lj4aWmi2>K^W5$P^{jhyLjwIDZ|L{SE>58TNP+7;S4rj>{n#n!;Sp%hW<^%G>c+Hg&~N|7KF0BVqTBAIM14ZyvCgfx4tb)_pdC)^!hL;e73x1V3fJ2@G47Xo%M-MNu_T%N4%HjPKu;frc8+W{#Z|Wt|9VgIWedl;>+D46%a4n0T{~08zj1Cf>fhzC=$6HQ%kOmk!a(F7w_bGPR5Pq&FSkMct6vn|G-k;<$hguJ@yo6v&-}7jCpT-1cIdts=k0^}-e^$``k?Hh+lJ(lb+p#HB<ktyiTtgfPIuLfV;k>E{O0yjPpwTM)Mr_|=w`%AsgHguAM{s~k-uD7nV*feSuuX@ewTRXI^1ZN9_`<A6s~tiGP#ee4?gUYJZoYlUi&f>zsowl72Q6t5bE<i;{?&I&qUXD<wAYB4wU-a9-l*=3&F_$*-h>jTi5-_)4C+a!{=<Fa^8>~qFc-KW&bAcCHl*SqU+WtxUMPX2Ds{u3zPHe5y_Xk>XvL7QO|2dWnE-{Jr3vX+XQ*Oxes>L&8rnLemdsd;Hq1yK1QC*1!SFN5ATh7)}3-k^!fwFivFPk>SMhOy-6j}t$o{~{sYS0b-gazr^YyMz!21b&rSRe`dk<J%?pyp2skRg3+?@Dp+52FrG50;-wwFydeIof*ZhHftN~S!r}GQUlkq8Konjm4gFFj=;=1l8m;2E&C_n1sTMGTst!qnZuR%F+T`|LOzdP6MLz9YbH131?-19|!ez>DP?b2dC*>$X$9QX6bPKnpfOFf<IUfZuPqFdUel=@hLQp!G!_4ixRwHH&-o;go-ll)PyM7N)siTfp4;U;pNW={}r=3j|*wRTH%eZ<W>uH(%z>b&SSpZpjPjnCB)bU!1y8L}Mh!{@ktw2AzCESTTMK9%|0GJX;Ae+;<mS|8iQ@uFJ`oJRg5Z?O(Z9f|W=&PjbNy9&yEZJE*^@!?%C9>$KAeIRSvP}C<|Y4l64sRIS41|iRzap)JH#`1f@I;|DrS5L?Ft{*G;?dhANo*N9*XZ%We{#vI8BG0%Ph(FY@reKEJh;QkO{Og|$m3E&|9eS0A3F0kt@*<DhE!^+5N{<jfYcBLx#l#r@FYd{FVxQ}Q>%G(h^*Pr~p6`~WXLd;Z7hm)**PoVU@jDW<o1Rqm;jAmyh;G!GiTZfA72Q^34&piA8mC*!bIrbHGW4%#PxD!f?8{k-O%PpAHXHX*Z!KK(;-f^jG?<L>9KULm)O%eN^j|L#-^?!Y_PEZ-lc_G+Eo5i3t8PE=7V~OSH(7t$xB8+!L7&hLMNW^CIB$#S)|H!ZUkt7;`{WkCU)#lx8;tlK^CiFS;C0dM8~P-;ukBUOif&Hsi}9JZsv+g^E1`$XN4x!~Jy_0nY_aIpTpytS6(zc@_DtxzJuwdJZk2sn%ZX{wy=tJI`QzoeW34+D`CrGN9g1(1>#{ZoMm=K#pkG)j`?2=Mb#Prnf8hS@)kx-Z`z3GDwS#}79~afazT)*%$ba~a)W<rkiu{hT-$;!7!I!XJ`dKZ3ZlsPvyS+L*;gE~&oNvuJALRF+wf+5VQhuQ)`aR<!`Q2~ra6@#X@Iu6|4wHCG&_&VpHv`em3;!N1=Xtaix?dK|lSe%;4^y`f{c<NkzdT-s_~VNc==RX?Z5V$CvEE2=4)f24iim$3iR)@pO6D2smn@=dGXfF6eyps2Z2x@UD!R81)+Z5}WPM`!abI+EZngyL0ejRT#NU5|aT{I+&vAE~=(Z$r(3{M_b2I61(e+ZjFb;RrmvyNnRa@loEsycT_Xtki=vNKn=jU(PpRi7DEV?yp2FA(0dXogFl@#5wtqIl%-IBye`*`F>{9X;`t+4^~cIH1@B!1CvT$k?@*`Kpz{V2M1$qlq~ZyoP#<~<PII5QUU+&{D}*@!%oMj(H{Y>a=)dgM8_5_v|?#ru{OV?;M|{D#hX!&1DJ=z6}7Xoo&F{Qh3w0QtMFLHxn{m}g4)i*B!e3*&k7N{P3X&4&D?MxcGZb`agN-`p(v-{mlFv-Ov8Yir;uy0Oa#=N-RzjGV7ganbFkXCn{i6YGV%&@B(JE_$2{`yZD)HsgM|iFOG7D)W-9Nm}R=ra(WvV2!J8d*25Ao3T3HJ6%qR`eZGD{BJK~KD?X=c`mm?eNwL*FYUGZ8}{Eln&Y|Pe+BOm);_`h@}Ts1Zdwmwe_+!#(Jk-#VEjj>!SB$`8=wzMnqdCXx2%Mo=aIC(KDnv%qq%(o@~?}*{gvGh^*LAx`WwtA_PkH!{xT1GV_!SPe4N*Gm*01$SwwWL{&>s}XTqg_^%L)9pIz^=3H`q45cZ$WoW=h8t)zHv4qP={$}g-H-5OaDzmJB7L%%W>@e}9bzNi`^&tLO?3FPPRZgW=_nU{<eAF=NrbLF!1)5O2!KGk2`$NR9yTk%}$mL*F3SEr!!ccN`TZ5b!#+c@MYJ_G%--AnSDtp-6~^;z;;(oDvCifVmCH}-57-TZzP?fkta-dmiSgz>}mhWV>#T!QPJWa%Z><DL|GxL;wqnSDf0@=D&rIoFf6fvse{WTu-fy1i_B)W7UFSuYuLB1P9TTuayvIsBnd9E)+)qlb(uJ!g5*t>tQ=fA<zae6CWW8+DgpJXh!!mq2&Bi2CIGDbGhUS7GS;QlY=*#K?OqJ+BAq$@Q)C`Kwz};{9Ta!Wa*``Y(|@E!;OGXy@3DXy^LBWuMQil<|u4t$nfYs^|ZS_s#9!N&jkDy2$>&S@pZ<_QSg*kN&a*?xXyFt#@sIv-jH?N;mSn!#?7xITEjR{fghwg>ON3zl`~l`{8DhGsshX0s3piu#BP?jTc?7u?y>sZYR)R#SVyWdH4zY1EZ75{HB*&gZR)G+(+pGrQgl6k*I%-JBVL^_co?iALzC(_#MRes=7}@w2wyzj0flYcc*?c4f<=+C3&A<R`i9=eIZ-V^)l}{b^C+oa=p&)5On|IqHCq5V!q|~A$p|(xUK@b(f%GWX#Xl{k$+}QtP?)u#y(ZGZ|hv!-xd}i?<LLZuh+R=m#MGCzD>=0i0A&HW$NU0uDWymU`yXh=3%|ob;J)%gX=2su$!E}_65=PC+9FeH7}W;ow{?LF&7-|FZHQ&7<o>v$8)Mia?@3}O_+`OVfjaS4`bHdi~OCQp`O*#p?~Xd5MA?6iu<cYcI-PD3z28Hhm2>7VZ**_!)eghPeY!vwedYe^U25)xe)VAp60UOqBkCe^Tv%r{a5{w^_U(w6!F(<Vw`MQza)XadMW0C1y^N$)|(7K`*Zzf8@qR|oTo`I<i8S#ek|4t`;$#WL^npf!gcL)!}Fq9N6{_CreQq4pHf|pYtbY@9wTg!>>HRZYoMKHdSQGPJuSa?%+}th5BHfhzlRtPZAzp5hd;}8>7JY9dd&{05dW7S>N#MLyjRhK5@VcjUE$m>(mVdb`@*^DaNeqMwOn;`**>(x&}v=9@AN`+`>6Bi_w{_Q5_}tZa{s{k^QI5>jk{byo(|tIKEsN2mH3c@qU){vFwQ5JoA%#y+YT?8f6Q*XaNZJQkf+9A`JTt@zIm<d{bC!CU)BS9=vvXWUSlvGhHshXs@r=F$GBR08}nO_WeKl$#3%H7&nbMLiuH`Sv7B75F@7BKPb-UYn>+{h`2+eQ|I;WLpVpsuWWUJl(_^h`e`)VF?03~oyB*in@h9HH_YGd_I!-LtiejI<UwhH5_kLntYE)6)v*-gF;k+p(CfJX1>iWKK_<jAMF7|aJy>Q-VyD?5I<z+po56KPv=zgsKcaFsKXjt+D<HWpirmyJ3-4GvJ9pk@Z6&bgB)OUG5X1BjY`>(ruFoDkTY=0ew^_%fjbZx>ajPp954!G)iTCDeUPjA`((MMlIp37CR{+wr#{?en5tZ^L=miPzwj%Hk3LVf9Nyf>LRS9ELjgXs4^J?lvP#OZjy$929Q7J&EXlO~F8>DLzX>Y(Cy?=yKc;u}Wcx@Nb*dx0s#66ANbzdkh_*Ja#B{d-5D-=|rTe`sP{Z(s?$N1NUTc}6}(dv?ZqJUuo5?bbFC_XpD9yO%7r@%_QL(lS1^HS;hp-7152*fB=Nr~TJ`#LrKS{2tiv(hE<JcD645uv+ps-@jz8i2bD{FGaU*YKQR_6D#}qcH14%jYoGdZhacaI@!A7km$O*iS=;L%F>?pRqI5zJfeQeU%q#+Z|aahcV3q@RR(#VY~*Z+`!4(}ei!flEZ+%PH}=4K@5<zwk|&Rw=$5H<CEi$32;W&;dLr+)EhGCPKFwY1AKqGm?;6^5L40ZK2iiAG72Rla6YH+y9`ZZOK4iG)`pNc^$B55?{jpbdp|`&!@wOdzWIxK9>~DDwX)U(-s^mF(68iu%&WLW-50ZF2Ykuql_^lV+(xD5UcTHZ(cT#$j=klIeJ0F2|XwVh+i{Ashe?EN~_3!&#eixhBuZV8Mr4ij86eYi}%?XP|H$OGUcxW6WzsF7gQP9&|#q}PWG)3};dLw_yEmD8&L0;_JR6Z%+9q2!LBmUPEncwX1*W>%9Y_ZqG|EmY~i$;!yo}vS;>-H6CPxF1CoZo1K^V-tJ;(N(BU(qew$3Q<^AJ4lU7Q`RlEA_FwKP&H}%_7M~*Vd#$JLJ3v{l`D}U6^UD)JMDOE#JeKPv1{;y<W@YfElj3esGuMxAlyc@084l6WHH6vP|+A7v4zwnASts|L~u1UE*J-kn1%+&PJZMP0`L7yCP3aW_-739gcQu-W~n;VyNt6SrfIx_*}CQ{Zh4ZsOXR9ApexC*zelqBkMcUYdh+5H&F81BR|SI*Oudm)Za|=LE6(k^-O1}&wPw$y~aU&AJ}_MCy5W3f^jlwrnIv?>v+*E5z){yZp3?mj?eI2$;Y&4x4`6*$2>GTNcyEg(B%Z}ldgv7dWDwg_qzDb$KLHN-v2C^bwl(cuY+;k(y}hrhAkD{=GLc;lrR4<RO<Z;?X1t;hw-z%3BIGe87sQoEd$y=HZn@`Ka7+1F`s@xeHPpl-PvxI2Nm&sRMipkovStXQM6m+1hnU|O`@BHj$^!izli#W)f*|-88sg5(+J;{*vrlk-4^!%?L4P3;?q5b-Z=#0;owf`Uwfg~qHAUB80XpNpuhTe!S@%}rXl~qdgzybW{PebpB3Z0@I&M;lT^NIu%AQwYk5O4-g-5b_j{Jqxo%3iacYuW&#qB;4kU>bT|4>;>x3jfMYp#eF72;}mX!I~JiKTU&c6$J&ZWXSp>Y{`4p^U^6y4@^1@EJ`ZN~fF)b9{qt|RvG(w~uanf>Bm^yB4ZQK<hryl=d+M*2n1KNS1tS$@g$(Dv$tw7-$c6Z4NH2+ylu&oO>B-kmCWtM$P9s6AsbKL47CdFl5?=wtii_jR%-n9o~Y!26}tuO;66xL^wOlJXsyS^pKDr;U?foa_k{-PXUgoY%PYQ@+o!*N;a0g&6c#jm{VkVbevoTr7`vUfdM#aYoKVe0U-B<I>sO|2!|cw!J6TlQULfoFpEDb%bYc$zxVYgzvI)ycAtaw-)U@Bv$q@?4BP*x3`HB-TLU9^p`!bE#9N<U5a>*&3Ip*=bEgiY^TcJz_?o^-@BO~^5Ok<%PyFI=4|XP<H~O<zQg|h4Do*!V;?W}vgk(1UKl_7Psw{sGcYUO=S*CQ=fd8fvL9mZ+a|x8?ME)+`I7XZJRi*z7x8;~Qevs6F({?{ZZ-8MqFXy|MEgHXgWn6~E6e*Rv)~BySGv4dk3AbMy6zK=`{G9S{*wRcZRiz$;6DBOS)SKs&IU4mZEw?~-70u<|Dn0)TDd0}Z$q==JJ`_f81K8j<Gd+~V_w?%P;~t}#-U!A-;LaOi#+*#F;2G4lKn%cZe+@v@VsBYiEh355$)XVH}1QBh4H(#+X&37^#ZU@IDDMwmLZwZzv<IppQ`Om(XBC^(2rhOyGwa7E50``xJmlOR%Di}hwZED%6^_bO)fdFWpi_U@AsfR^r4uC?VVpni~h<gx*o9u^X=VuSvT5!hGQSy>k;PF#t-Cov9;_?>=$bNF#hM|!@6$77txJ!3-BCV*B0Luyu;sPm}%Z%9<H-W*5P)4d`G7DPmkyIgNOjRUp@`Rd#7w4MAx4_ka(*;H$l9yG8o^NX2bV|mP~`uUsimNZ!ho~dcMY}=jy=?B)-Kj=sSy}efFHj_ugSi@OM9}XQN;0jH@nsL<;D4k6y<(nTqdJ-71N0>l=>tY~KjqC;JBCzI3~Ub<5#9nBS-O5#5@(0>=N-+c@v;DCiOAB#-%`5b`(8B>iu%S{mbL^%dFgvIpnDK33^(5^wFl67$38(fHovk)OoduRKQl%n8VoHVN`f3`G2;CD^AqzY62$b5;4>YE7{nc@k?F59d$fdA8yW-Yfc*ME<vXk@s0**~ik{G~~bQf%iv#1q9919WkHJ$M-+>FmHT^8-H2qZ$#9=d-lkR(EWDcIUBQcqN{Gr`~l<N_FLvj>uKztS=NQ29gd8bdCdB;E55Id`i=JQwGHiAbO_=X+`@d7FBR(3bsEn5y9CDhhV0T`R*ws)f1-gn@5gz_?|TpW%%rG)gZeXFbt7p6#zW9!x&Q55-Xed&dl<K~yyd*sfuB*&+3WB;z0*$itL;k@;qQcul8C>%L)IDApt_>lTIR-m^kWz5Z?i(*&;#Q<>L|wB`Yx++KjZh2{yh`!>lZ^rw}0G%=hT#K_<knQBhj_NKc(HQseLhDdw#;-J3XC)@$jTE-b?CVk>_P4+!rhG_c&%tP2M|cYYQU2equcTrt}rvsIVC0ElX#7$GCk2-ctqCK|T8|*ygHRB8p+1tS`rN*FKfsuU*1E`SYsyJ$~v5;)Adb)KC0D{tusU-dO=?&s-a^Uh++Y_XbS{<9frh;JMN<C-mg|v7UMT4*Rb8I^+4g7V8-;Lr(60_QU(t1r0HNE|f?93MWL@nkL5l)@c^5EBFTD4`Kaj=IAcZbu;QA^qT?Dt)CEYdyDT1wUYSV5#1L1((6AWzSc#wLw-B<$9DdOzhlVt0qgm5`7m$h$gvLXlLGfes`c1c^e+tkV-;L)@Jf8Y_fHSeZN2e(!5aDs^(cK;bmIZq+1e=s_J_;g$8)b!9NIs&FWRl@BkX@~d5Cd)^q$O1di`h6eR`u`-nPa5<d4Gmd&F-$&~BYGqraQi!S@%VpJSZ=DvI|SJsOK{%wB_byOtWyvpF5{Ui9Kr$z%8Hf;`KDMb}c4L7tz{XwThY>l3uwt&@1p?LQ5D<4LUZyOu^fq<oI|51-Th+dhE_{@S+EysDWlmen+6DYQ&lNGF#+wN;|}=fwa1r?#Qx|G)m!wydYO*Z=NsZBw3h)3hTFJ4K8qKSh3)c#K@(Ir6jQ*J+C1AYLF>c$54F`8DD#@@wSxiTB9wlfNWBCx1!)g7}R51^GY3zsUa~|4maoi97Iba%GAqCw?VYrg%!?H*#f)ry_nQSD3;bT$$pzh*`;Vk$V#}kb9GtCZ;7<n4i2fc{O5L@@nLP#ERsB<gI9m*B}-oS6Gz126<g#adL$L<aNnA5Id493@7hE9!Bg-9!B1W*qgi$c~4>|@}A^DG{qY^tO&6xu@iY!@|MKj<SofN6Z?{PChtlNC+|vbC3YmYk~b$dByUb$nOKs%GI?QQ4)Vg}nTUzWGm-ys1AcM?SEl$on&OX$56Kl?CVxbJho<;>;z{!J<j0AJ$&ZsCA|4<=M82IkmwY?<P+|x2q2%p}4awV+Hz(F3Z%*Ek*oeF%`EX(<^5Nt=i1WyIkekGV<R<wE;!*Mw<QIu&$S;!Lb=XsfJ#pA=;$8B)jJZubO@5pFD)AKgRq{*3v*Ze|lV2jgLcBq)@EZ9Q@(0BG<PXSS6JL_QCVxeILH>&T2k{^BALNPLfxpR9y93h^m7b2i;u(o*KFvr|JR31Nc{cLg#FXT@$@3CZkt@tao|oL8rnnE$n_OXOav$<?#A@W_$ZHV;$!n1}Beo)MM&6ECgIr-<a)lkp6^4<wBkxA+L*9+N7qKUKFY-`g5P2whdz#`6h>ge_ke6})cdjf$%uHT}JP%PL&qJP!_`wZ48Tl7C;1lvEyf?nk6n{*-O@5o>{xMB)JMj|vC5~x3@d3G={4Mb{`CIZg#8>2R$bS-lkpCo4;|^3~H;wzhV>%5@aSJgWxrMv{F(Y{aa!+D5a)lMhJ;}?{6!#@&BUhN4Twz{vh5qE_iFIg-S0Vb7S0S%N^dYZAt`p0V>*V!_waDv{Hz777Z$jRd*p9p{c^6_g@-F1viM`0XllLHolJ_7FA+{$EArB_DAP**Q!!~K`($0$4Cbl7O!}!{asqNB7idQGLAg@l|l-QoUDS2y};`NCQ$m^4rB9<Xnn1{R+c}`+7@|@&JiR!*eN?-BMyw@I+KjwY%nWp$h;#=~M<nM`Z$lsIyBK{=*MV{UrsO}BL6<WyCljkEAAkRncMf4>1WSe@?6!#-GCHEt*No-Btnr&K>rg#ZrDe_WmyAm|TvlEk&XD4?js`hdxek50>xEt|3`FpmD;>r~FAgZ?TV4LJ4_aHAs^dk4-brzy2UW{0iye6-q7%@9}G4d=#cXD^uDGSkq+=J)H!eg`0Pw$xC)lb&sMCIoqS6I}gEDcR@3oR34EX2yhat>=uo{PS-tTDO5jx@#l6Fa-`a`Zb=8%9*xXmW*<UCJiYlpaG<d<reXVI!$UP*eG8(H~7ef~NF#<n4H@LLY~PIjj_UJ6afHYO$;xF)!nCl9yskKJt7lD@DxhusjaSN}iK3SzU7EWK15$l%THs0z{>iaq-JgtLdUE^dc%ffINV@(%RDxAh)ti`7MZ6a#h})zLmTe%aq@n*o(XuW5Qkh;l#e=ed&jjE9^!LbyzTYclyq<V4Bie(t;dTomvnz#k<f~){rrZx1ryKTxqQwR-1ko`fX@RuSZ^w$11GgFmLkO^qpmOX!RK5&GJIjmG4VayfCp4xxx$%^B^xm-&y9td`0LhUYfqLjEq-22mR9IO3UxC%=Ams&p}Je_#BK$OH5Cmo_<!E;<;&=nadfMoLpf_=1ohUl6n&A%1=R5T4ER9$rZX09aEnCOU!t8mon!+r6nV#B2Px1g?b|T%Cb>cJT?79<W4P}!wOPQM@?CF#%HHrkX&IUVtI!(BTq-)S=NkPVK7mZw<TBD&84gxP3e7z9m)HUt9i5~^Qz-Yk}It`eZ{MgE3G)W(scS&h}l`@yw2j}3X9Q-^SCT5E5>88^W5s1Dzm<A$vaZF&`(FMv^4ac?VW~YNyrnCCt`ml)i74nSWx##25K3oJ9$R>$(cvxP-9q)-x5TBa)0`z$<_Q&lc@aKG=Ii8kEuyrY3d%Wui^ez_kAOWHK5jjy5bG#S0^@PnbWUAYrq^j{YEZzYEM&K&1c=|JGnwNN2+n6=3h0AMvyCQ7=35C;=^f*M-wNJPol4mn@E4EOW8#FiaVd_lNcYvvdN5_;IN@Qb|U#8Vo&mD`pOLILwT(7J26h_P3Swh!nzLYO6*B9s5N(3MV57-Uzb`Fmt#AS4{=x|{eJX2&?0$!Kl<vp=?;scHkN)rYD35kVpsC9^e2!T<TL0ioJ~HKd^&L<`5cGE(qBkEoj8r>o<@I;OIZ{xmNBy!r((vD&vH3Fk~ofB;TVSvAS!<*Z5)qv#yMjKl1CDo6P4bYyft;Dh0t$J?nmy&erry@A~p4%r<%h8$^Cd-Ah{pQE3&*SePuN?jDu>_YcQ@FbrtW)GG$(jQM>?sPjaQHb!1*@P3e2m@-nU|{i-ZizFM31AP=P9lv*HpRhPI?#KGi)>4(sq$BpDMqg>*~)5fsh29rCr!R&{D<RQG~PHYp!ThR9+cb2O);vj0hU9{oU6-JY*-ydpSk(FGbT1S^7)*{bEzcYQM4{|&Z+B$3uQTc7i6$ZGJh0qjlKx@mG2E;1Fx(@Sm@%@NxSf=xsD&z`_5>;$r7r!t~>4k{p$qSJepebICSckkEd2Lz~hXqn=Lamv@Lh09`--M?0VDexdtF&nP!Q>I-3ayL_Cbv@WL!3$8hkP1w7Wp*t>BNcT)5%8=hmnsU??voK-iy2&ZJ@)tQyWMv%wfIh_oF|Mru1>-<9MvnM$sQfzLH#FU&f6i?@K+FxQjfNd>wHQ`8x8o#I59O$>$SSkk2O{PaI4>p1do~(_y8lc~UFuu*~!a)Ayt)Jp*|L9;>v68vG38cjznhV4U(jXiC4wxYgwM$m56$$m7UY5a*JwAYV+JN4}VR5ph2GBJyQ4o5NO7vr${=uyyq3)3?!-zJ`1ak5$@s`fJEHkSkozxHaVKsc$82A>T^Ao4A8~H~AjoX7WAc+lV{Kw~=om?jzqszL$2vVdtq`pmxz=kLd5Ce}SfSJGq_5D(x@&cJhzp3Lh}ePX2)U2clYdf1t1UZ(<s9Ws0YwDX!+W0`#48ozk82VOlrLk!i@4rgFN|PeVT~Ej{DYGDi98Iu!p%RDNQXCuWSZOr!RXrvC3m5c?0~l_@PFk4a3Pk$P6@$}dh-S_v1w1WoCsXxSZBhFW$PExE%|Qcq4TJGC4<COdf!>M4kB<SEGiXt2K>_C<sCH#NoIuuRzt#wdQ1{u^?oU31uR`fuppq$&Lj`57Lov}5#@opsm^@?-R0(7(a>qbyT+lKdF?Y4X!NR^cs&T_(Ro-&uB<$6ca-pZo;*EBcohcZmEI^PHfs^dxT3oyRFZ88wCPd5rR%T;UU9YDdghauu(9XW3WADSSsv=P3U{u40w%Ec-#r<j{VSt8(RkqW_b*6#qnDm1kjGF>-|^U3gXcCCO_#tP*)K@^<u<1u>>7^&q0*u(1wnLEetMolB0fj90kEVI#?x(s!1PWR9gS<(nC^nf`K`;&X@w`Eud{qSA+uE1cp|Hig#T4Qq`lj8Xn9`V$#H#qHnq%M`||xR!2MXAB|lPYYvAYlr!;YzY09v{sB$yaIh6a;4>`Uy!^4eIMrWWtk7TFZCAGm0yJB%f9esx#H<qmWjNeOS~#C#<C*hsTq@wJU{(>tef(a(RcFvj8&S&VHFvhkK96@gqDxTIm`TsdCBwAPeiluxL+Fls~UJ-ml##9?&YhDQT!bJ!{oo{U*&zT^!+S5OuNr{Vn6*YM5XO;@fAPCV^!>S`cAHJ18qN#Q{~@z%n|x3_8aw6)W4A{%<YD<TyEe>`%K@-zwx-7ZqSwXmcElKJV5)*_+9i@lD~C{QRVAcc7XgfV^r)$`cAHJIc*n@TS|W(`9_x*RX(3(%gGloPOTZ2kUQ6vOBuVCd6qI}E%{pdD*hp3){-l{LsNV;Z7t(pGhW4JbAzwe&WgX){`Fro#*1ZY{jGRT7hhp!YHyh@igA(T-Y&iukMrg+%CAm;0(ma_-sCx1=FNODjGI8Na3fKbuX6Dfk7L|Ma)o<{s(h=9ulQ)jtJsC~om}BAS{#q-$rx2WioTO8TuEEV<2o~D6uCcrg_X&Bl8<)#caEq`%tKz8yc&5m#^>R^Q;n9J?NyB!!?<eXd6@SX??2^#=RKN-dPUYl)mP2w6<xT(-n7oVF4e9!H~i+a(T^lXk#D8%jEN-A&3>;=O^uhqEQ=&x$9r}=>-mfGOa<1>`5bD+dZ}lKdRD3D#3DC5Qx}jcoJmt$Jrh?mMwLg?cXEXhv_(8lm2c)TTga6*l^9LFg}%ZW4%<!K!t%}JJ84@Ovy-@irua7EVi!JxzB096G=|zB7hP$~c+6rKu5dqblEe0qkD>1@+ecH{dRh;MO{Ug^n&Kh!l{ICI;*IHtkUKTyH(;6aYY>&DyZBD7Q2j<JL0|D&<R!?P(r-$?3r+F*G{v32YijY>GAt{_dN<{9#d%)!du=b<Za@2F8?{aJ6<<QGwAu6(A4#sXaQcd?^=J^aAnM_a-N{^Q$d|Bu4fz<h;Uu?z*Oxol|7sizpee4#TN{=QAXnIosLDfK{7{<G)p%C-lUj?ad+ND{^}1TC-*wny4ccSsPX2`cWpbt6Cf+5#O#cS`>*Qx${M(E_%XsBKWt=KkzXM-TdqMpvV{h@?>UYsW4f_^~AEm#8zS2*SEA1p>oX43O_BIrcr@xv0PR7Q&lwV=Y75dj`iXSH)C4b2{RsM|prOWXbiO<Lts^9x+FC;L)%{^11|JQ$d?caZ@@3aK}A-4bf$b^4J;(BDbBiDcas3b5TiF!w=xjX)+UcL=hUrK2I2OaK|bp'

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
