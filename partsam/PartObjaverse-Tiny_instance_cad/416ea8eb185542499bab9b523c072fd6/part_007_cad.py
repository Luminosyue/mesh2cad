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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/416ea8eb185542499bab9b523c072fd6/part_007.stl', 'relative_path': '416ea8eb185542499bab9b523c072fd6/part_007.stl', 'source_sha256': '3825f1d39ab76ea8eb5fca516a99277b540bc2572848896995aeed0e36ff854d', 'input_faces': 816, 'input_vertices': 480, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24080988764762878, 0.017433255910873413, -0.37717071175575256], [0.24251584708690643, 0.4999842643737793, 0.27548134326934814]]}
GEOMETRY_BASE85 = 'c$}r21#}fx)cxm?;uI)ug~1vm1cC&LWq_c80L3A|3&EifoT3j8P~3gcAjRD$xCRLB52-<sQmA3y+_N{$W7_{(|Mh*Wb=Lm9o%`<GIrq$+c{9^C2=n_SlZJnJwTC&5>YienrXr1&N$cOCci%2i9r^_Ji2lZ<r59iQ`=B$zo78L2!lm`s2K%?~&?l<5e|g=%V#jj+0lI(3p1u3_j_lF4XYckMlwTvVd!G)r-=}kAbO-x$q0;3_1n8v-2k1lf|K-0__7JR_3GoNjSl*W38KQ<ZAf<f%$4?n5zBl2;MfKV9<i;8Chu7Grd~;~JOXA;*haV9rzCI_neBYhMI3<5y)-6u@FJDgD8<{JLudOJwRQ%=1PAIjy7KT45LfU&H>PbJw@7GR>e<O6U^0iujV>^4x!*5eq#_4XcEMC5s=?nPV%IuKO6PBG-pY_`7Psn&4?%yWumz6#&<2)8CzE<MUJn1(>K^c$t-Dvoy%Pg1nC-Ur-_Dct%pAikV%XrfMctqL<_ecA?+Dh54*|knfyVy|pZC=ij{tK4fFYUbs`f0y$tMuRh>}L5K4qrRCRq|s^%WkUA=Ds(_#c%#Z+FOHyW&b=QUy1Lz)kb{7$~sE4#yPbA>9OpW(YE(MnYT{y@cqZFka6@p9CuLi9S1+d>m}0v+S!sPWAZfk@n1-Lk0(m<`H%l|Iq|h!6Hq4?o*fhaRG7?{Cn{L-<}KodU-`Hxd3e}J@}uQl2Y+?=0@>b)8nVCogDCiUFCUa~_fL8b`_&fy;R(lN{M|-NU0LIri|@&Q^?<a$pGNA(v!E*4H+-~F#^YUi@gskHl=Nf1+KT$mRvvz`8`IGK{9yTet8(xYy36>@{qd4F&-h^YxsFNy=7N5bA1!S$_z`F4NPe!ILfswL;eS0<=1Xh0T<X?HkrIBM6I&$ztXpgAoufD|YDnF9T6UAV)#G=-uW?BF)vm6Sx;1VrhkyRbevG@sQTco6DdKzlyKR<stbcF$X!vsr<G4=kl{z%nw}Id6ytLO@=jMw_=s&tT#$QC2d|Ph|p?%&#(vN%YJgHCpQhxZUyKM5U^AEmO?e1RjH_jL><J#ptBJGpLZ1SyhtKT*8wW{gif2ea$0Q{`=WF62J#moE}C-S48BH0g1JFX9&2YKK>TP=C^9z2Wn$DI}ZJPX3QcL({`@})!jof8j9{}bUGweLy(JhuzUI$)H_zDN8USH#y&*Tni$DOBp*JLd@eqi-c|p5JfFyy?sLqo3TFWjtE{D}zJ_Y)1PlJ2AhHyDpG^lE<Qb`4E{G>vfdm-(9M=_|~S!vVLmKlge@9_I48A7`#$^<J*w^>a+V<ZS-$cmie-He7RFqgWoVz#&2d_Cv~n5u7K?>>9*JR_%f&GM*pYkqyN&AyUO1eTZg25hBv!Es@pp;;%g^*?UDRM1xbAxfsNp=c(%*84n0e2!M_wJc{8sUl017GRf7LTS;>#}tghtQiVuLl*H7~4$&wxG^o@cTPhDN=$Edzyn0)VfR<w^hBJJIy*GQh-f2D!%%8Bu_o;}Bt!GAPY#_46<nk!dJp0o+IIA2@jvpa9JsCBNnCENR{;Yr#4^Sa_2odzA3ewlyo%qmz{);z%a_94%=Qo%nIj`L$A)(v;&7nb;GuUo$LX<9$PPq!Dx=d`L)51#8g;OhsZy?Hbf&f~||imxTClyT_&f-j5Tcd__Z{Vy?|_8p}kZ{U3NlWHUSd6gX34Po=p&#zBpUfsW}m3s5$nvC}5H5s>cWac@khvH4qzHlY!M`zudztn@Db~@@KQ(dVm_vzXgPk0ivXFY3UU1&cnQoe5lqYkxEXAX*g`xuUgsB%&do_DeE*RPTM7<C88yqI;Di0@f60O#pK*`-cAGu|GM`TDh*Y}fN;;oUNhp%36^e~$U>S`o+lu)X4I8-v96hWs>J{0oc3x1zV7mhq(CiG2S(8|^C}ljG57J_&hPUJm{5x_e66<-&PN+k6%KJtH}eyEWgU-i}P&C*$9IPsXp88G`!%tAqH)`;C&%f6k|2@I7nh$Z>6z{d|Pz=w@i&c&lvJv#h+V|DN=<#kW$FlzuGMr~Z3E_^)e8d-wg9+hu<*#mV_!3tEMB>T!_dO;554{)YRg%fp7`P4^oHe_0ILCr>>``c0@RzGdZ={;hBRTqFB6J3su>d2k+|{kP1c_G>cnjq?*_+(y67sM~J8W1YTT4?gQtA2?ThEl(!YRg!5qo~=mnt^9w;dBmLsb*Kfp#P{^PFa2l*0x{2H-t3b87c`OlTB#aHooo4?i|>v3?7Z|pHI1kz?{M)w&r#>*ob5QDJnDje{`?7bnQ@o&=W&IKZxt*n+qG^rmiaPA|F~1O(_@XSC+_l-<+yftz71dZ$MG0c5cvzg3O{=|)}t~zaNS;f1N`Rmu`VUIu>Pb75Z|hK5XWQxjxr7{>g5j6XYuHN>+|WdKSiIx-_Pr`WyNqkyni43QZFT+y0;nf-Exok##0mP+KXB8+042He!=9}f4!^hw>~5f`Z?lv(zia{Nq>{N^XQvoyPmY|WFF1ntJ_h}J8-`D`%6A+uQ$RE?uzS!@QYGc#=cVMCv*d@@6C5uH^wCq-?}nZ`q2iV4$UlYwn;ykn_$2E7s>UBS^LdasjrmhF39(*w8Q)-e<8m0^95N4%$92~FB`6lZ(O{K`YhFX7rwttd@b2L<atCO)|oI9?Wev%d*<I;ae?^WR1IXi*1|ZcL#x1<Ez&-!F4mK%U0A=%?-Sn|*BJTF^r?)~>bwko&{=Gk`Ls$bKtC@Jos~QUG?xAitC;xi$j7Mfp@T8MRo~&d@BTXYxhBgx>utJUd~0N`tI|&QT#<G^Z-?Lag^bfE5GLnequ@gEwKtD0OFv^LpO?>Rz7gMub4xwwCof6<^#kG9?yTOjUH9~q?PR>A7H*RMYyBYon?0{$oy#*sd}C4bv%dA_9p44*!_&dfIA7||O5PdmyI#QjMO~8PL~mCDej5$zeEgls^11BkjiU9=iLcMqaa`nlzCrdQs2h&=dEeta)Ap|TR>Xxf(tojYQg8apoZ=f*9-;pS#jyVG+5VmMH#Ha5;d~1uZ|((kzC*spUX*@s1R-y)s)}!XGfC>%v#0S`+21Y2(Ej`<mt?!c)*yegPOTIF;mz~D_3Uo5a;+R^tp>y2enjfQy~HKH=VCG$kGIEJtRt;&u93fwKOybC8zN6*e<zCXxm^ME=^rb3^KMGD2H*Py{+rKny|-@9YSA=Rq#q+g9l37N*KQVH|Ls(Q<a2R0Tptu%D!%(^O38z{=Mb)&Y7ay|Rypa%EO8t4Y!pO4ZPR>I&)UqXvC@7Q)@8HObkuX<G2$C9xLzkSaJ@FLG5o7pG4EZ9;Ce1Bh4}7sV`ZF1(`u3Oy{-3FN&oS$(9is*sQ<q@iEqp)iuI~+I+-tP)>rV~RYCiisB`^fot4s00?tQzOi#(bG5*pD(K5?%-I-=ujO?d3YPsl~M#v}g?2X7OzSsUiDEr%XI@Ya`?Usq(uMXO`eI<EzFFzu`<Bih~alLn~r{uw^mQj2wO8~Z;p{o4evbwxqBHPWDPUgj%WUch4X?>QUjy6et^v9)8w{HybjdC5a{`f75k$yrKFO>c(EWvhLMd5fnx>>I4t>2%EudOdG`)d?%%@Zw@fb;c{Y`6{?cXqC9H@awoZ=INZCW`O<^|h?4+QuBHtCtVtIz?}?UdFFQ<d);r-S-c<?lZcb$M37!&yb(`7iY=wlCGWfuhp6(c`%3U6kj)v;CxXtFOHXDv&DC(_Cx#qejoYfUvtIxOc{O5*Z0<JFXJ(ios_(pv%f_@>(1i5Fn49Nv_CZn{?Q%c>vddGhgyekFrF&U#CJ!`+wSXoOJ<h!L8tFt7y*CM0P)Q=dvRUn*9gAfZ!#YD0&Le~2B80i4HG_UADtcJ8TK0e|1d_j@4cE1{@X(0d!N6<I(+VjnbOb2w%D(~{iGhep;yE=8y=AMMw<bWA3enp@!dE6M88L8kCgFcIt>5Y%LyNCck@E@Z;qGqj@Dz}dDMB~8KM!hq`mdaQQYrr5Hm&kJGBIU|Gc>0wXOmDwEZz(A$z1Ayd#>9mT?9fsGm~}&LGd(J+j>!Nzl*GUvQtp^Ju8F&)ggP+d3oa;k0Ln^takid~?P63G#QZHb}<#^=iy-$1<|N+L6Qkq<xzp^xyJNjK5o(2x)(|0>-&KJI+(3mbR4f9L^!Wx6W47|5w}U%D9#l!+H7Yyz{=kC%P>BsDLZJzSVZ$Z5ij*Q5Qby=fL~B;!n+gO^%=NCf!2*W4p$qQr$!TW1M=nV?#pzW5291Q#>L6m4_K|avkl=oBnnGks<$)XMOs7TwgfnW#iRxA^$Ot?#G?we&WC8{lIAWjymyv`DkXyf7F$pb1?2B8>m~O<`}H!TSkj-2F9TMlM}d~7&cjaZ}k(X;}UcG`TFLja2cn*@JE?1Bl9}6=W*>mJO#)5hHcm`*8%f`f9E*-#ZPcPEye!no7P}lKZIPB<J!3P2mJUZ3BJD8%QaiJH}`WK?}I(~9YWvSlmzuNWGSy_L&f)wU5{}-+lT!v9gg+~Zeg8#U}BwKJR1EwkN0Ea#Me{y#c}<~O{|k0V&Oa16C>lmImrLV>$Cp-4Dp@ox%d5nx$-^7`tKdT0?!*9=L>63+<a;8I3Kxl?_MbVkHdJ(?+5mgzqjhWNYr^=yV*wWzdO%^?qetA{=RqX3asak#>sVykv0|XYnQx){)gnieT9=A@tx;cWAbm}JI~|B(-rdE!g=1;;;YJY6z6q<wWc|quSB-MdOJA<>hR8D@%1*la9(J88P}Pyf1n@7b%?uYs62;oUbk2mx5@Ju=XH*mvFIuppX0j7JP;Nu?H$)w?sswGJFmy|Bc)eMd*^lCv(E6H*Maw&$@RPQI@1g{;XAHlt=Es>JFa{6gTKO`FcW$9yCwDDS=()`sN?$CGkcx*X66!De;%TK%zOvMcV34ZkM5x#$921Tr_?(6d-c?~f3*9)+@G?4CW&v=>4v%uxrpnfo}u4~mfni(_RWqwTx=k|dwU<u@5xc9!#!WDmwp|;M~tMi#drR$(bv@4ApI>ZfbqZnTJq@$c_Y5__mO_Ei#(^%V@Kn9KHp^I`_>uwGjKe5ZeBvYbv!S=^LLs1hbQ8DvlU1Cp~<9f^|&UuzwG#ZXN@!AJAV%ry9VF!`_X8g2KV<JzfX-ORq*`g=lobN$^=T@JwZRicl`eKyhx4b3Xb2)?zCUvIg{h}wKsn;_>SM>?&1~1H*QACc0E%b$$b!gTNv8sT?_wy9PYz}Wx{hx$9)4cO2>Wtn>lfPpZ+cCwoXMnzjWM}@LoA9zFw#a?nkWl;{Iue_vj~fCg!nh0_LSxdOWvu+z+t=GvL0w<Nk>;Ee!1)_gg#x?eJW|d4J|;SG4zJmi5rx`z@X`o|_0iQ!M;mIKGXF-Elw9abL)NAHLr3FRTMMy5N5Jl9jm6<hbvoJv)o`rw8D?vv?Bv|EWEmOE~U#>A4c{dok*|+{ZH_8%dq$W+1LpocG_-M#6X8uQOxX!*|@@GtCkB-F9dn?uW1r^}vPj9rp>1)2rZnQ^;|xPYsj$ap(ONeuJj)Bc|cLrj}QpuQ=~RT9fL*cihi38#aUQxc}+hH%feKbBlQ2`qZ9{hd<~y8Nbov2h_9wHu#SFt9ng5mvY{xbw5}o&xedfOYr=4a9bItci5Nme9IbLL5@eOV{*)MBRu!|*L~w12ho03-*dk8<IZsgzW?fY)(h^(woE1W>z((j&Al^lAK!65+$!`G?H%{k-TqnRd4uylyr*#x{MEIjPR!7^17tgY(|6p@w=_Pth+Km91K;AgLiA<vozE9MW3J%2W5gY4?|GRD_f=w(;5oPB`Gvbv2Ke>*;{N`~W;owWcm+RZf%x7YHBnb9v*EeUtkIaqLObvtNRh&L9_CGY%D3L!i_41d8Re4s^_FXm`#M)@itl{RV&zFL`Eow5ajz%}-|^hXy}S{gOF5ns>HT}ccRW`za(#k)R4*yx)LOQ}bD!PG(a!OFO3RQ2?H$jvjK;a)JDz{(TZ6?nUM0i&c0U>F&F>iccRZ(aXU6*aujhRm?xTOlb3>!S&uBmP6Xd&9h`fKISx@0Ro<F)T=Em<%$MZ^UaY<Z1u8PGxWS=f|rR^+(`I!F@?<G`2eVVQi^wZ+=gE$VhV81huK>L0ncy7h|^j02={x3~9>RX3K>DBnX=y+~x-o1|Y3yNYtE`&*4d1v2)?|A;J$G(7He<{vSIseA{9&HQbeS+X%thcOBYfowMJ&#XgJueX<dDZSWKzqk?YU`KQXzzHgZQg5-_KxS^X2*W;9nZ~;Z65fJ=j{6YXXxLrGS=z3@5f8KGq2D-hlTgYa@B_ZSzeB3?YrstJhvq7<8SH(|6UeZFU`+maDMoFFns6x23=NTT`0N~&)LmPc)uaXUHFdoAH3s#Mn8`CCA1x{(BAQWg)#mu+B@FI@J1xVbIx$gm)R&c>h?)mtk;hBI`oL_XzzFr#H^kl{;u@0ew!cGpF<_#w|F4F_9fOCqh@`cmp*>~#99mA^Zs|sxBiXao56R!$MUuX`l(bo&bR*cpF6;JyeDJ6`~!aIojBim_DoNW<77kEL%wzEPTC*u6FJ`hao382zoV;Mr)v*q$nQkY$P@5$HO2M#`|puI?^F1W_m@12Q{#R>?OeF7|Mhdc2lBxW8!36yKh)ug^f*q+=fQg^scT~Y2G)Qd-A|4S@9|1FzCUdNe{=jE-}*H54(Q+UzLp-{1HR+^E~7^@eCPXMMSH_{ygz0o8;I>z!TU?@pKjwll97YZ-tm6gKfdGrG|!5O=;zwheZI$$CtwcRJKl@ah8=^y>hWIR<H%bI@0U2=yYnPGNB<w*6JtGS^Ha)ol{U7F)SJnAFe_z)?|83If9Mb2@gAV@l>t9s(0<?J!dxE)zx*Jq|6KR1z9->3-aq`ucfNnv^Dp?0_ZZDVc+d1-?>#n84&U*fq!Bp~zT-ViYwl3^j`umu+8f|I-v6{d+YjII9;sIEHtPL%uFnr}yqG(^XzzR<b?ig<y{1choyU=TT_Ic#ef<^Iw--2G^uCdJE<XPieusUi|BSQH{#`q)d#pq2$F#W4IC}%{DRSQRl%K(OynpK%lMl~J2gKv|3hO~{7>V|d_jt8Jec?Oa`_+CM!1qf&eot5nO@aGOj`xbaO)|lEyoc;QlnUob$NS9x_`dHmH~8r7?R#~X54XOsQ(#9*EtA$U(&yD}WvYK4^uJ%-?o#^y>(%XYLBapmSGRw#$8gAw#|*_ss3!Rcc@=dyc@=pK)lD8l?no^|?ntggO-)vsj{Kt?NA38Tq4)%K4fzCl9rauCI`U*{7xH9sH)?HiH*y_n0dfJEM(`s$PTBDjL-9%KX7Wk$M(PamM)EXjFY+{UPih#sC%GmyCs}EBay~n9*b#2W6Fbh?@e4!oY3d&GY4R589P$?ObZUR{baFH`oE%NAMa@CJW5;>U)p^dJ;!Mn87HR?V1v|XVrI-0toQC`O88s(4Ew`1KnvWcBhpOEN)W>AiPdWCHom`XJj$D)6liNPYaa|xEq;4c1Brm5<BQGb9r1m8DWd9?X50#gr+<%pa^3>Yo^5nMEF66f4!PIZbgUJi2Ysd@9`>03BM>z(?$u%5nNvWyHk2oKvn0J-`iqtT2MRI#;FLHbGDC!LIDDn#GX7UQMMLk76#W7f%Up1ebsJqFV$Wy7a$WzIEr~}D;$n~j>$@R&FsKv;I$VsWm$*K-j-F-=|LjIB*Wykk+JhbC5HI96kyqda_yqY|oI+{G5+?g6hj^efyt7A;9gLfE;_fyxA_mdY>CzBVGhf=$dhms?yb;yzA3e>!0rJ2ZSnTs3@#kHtW<XYrt>S!%-ZBaa(x>8GAixjK1O093Fnb(KpIO-Pi7PeRXg!6HZdYF8Uyob7)yoWr8I-Wd-+@JHFk8_|joLq(6ncAP+pWjui)+klehp3y#hsY*%D%m8f^Qx*pb(|KWmeCSxRdIc)TT85M#eJy5$-~)aAI@7A&YjZo<O<|SYFjO_1{A9rQEQ2+xqa0A<bC9Y)Wurjx}<n8btri#`&8`Ju>M-qgJg@mg1THwTtgI(qK?!O*Br&|sqM7HHA-<sYB?=&O;h|CH4RzSn5vs!s87ghJy7dHI)>s()W+mW<c`#VTH^JO;xW`&TH^JR;#Jh$TH^JUVs-uXnEHUan|#(~=gW>ocKl_3erd<&E@*ZaScT$>)UxD?<kr+C<ksY2)Pdw-<ki$g<V75V;@x)auw#ZDf7)aC-HvQ7XjT_kh2oObAaY4^Lu!3;Lvk-_PjWBvOzI5s430tZ5j!k9X4~<~9>X7YWOP9@xxgwE7p4Y~3zKV8!^pMCU8!G_yOO6<XOm}h42oaa+x<<|jtlyk3#>wMeyTq?KRJ|Iha5`oOzlSQOrA`gMOJ#4taKMy%~4v;kJ2>c9h}RP)YD{@!&J<l(oe}2bA5(-j=YQ8J4KBrtNK*+`i7d`1wO~`FQ?8XFDDPCeoY=sZozSU$~jc3lQWS6s1?Wo<S=Rratrnu#(g$j$j1)yOzLp*OmZ)3J6B?TDsD(MT#5CpxFj{7E3y6+XQQSir{z2;R>zq-=5J81l2xu3yD$$Hc{=qQ@^o@nYBN`2-72n4E$>RKbH#<Jd0dIdh2o6VROD2w55;Oei*im?C@w&+F1Y}?2DJ;h2Dt<ETXF~TSn4M7Sn_)2V?A@Sp1xvLcgtL;y;I}`cKmIREr+eIHH6~aE@)|TZt|DZM&vKaO{oLOP053(3&;z&UB&8nQpeR27mhb|+^MxtX<l+xauBsLIfz`J8cD8C?nxa=?n$0OT|!>MG0b3o4s(1;XOWkY2T{9`2a%gn>-g+@9p*-<zfZ3Gnakgp>(7{X<$cD#`IBF8ja2jVH(AYz(){Ec<kHkoa%plS&b7+>E{5XC)B)tl<j&Ma<VNgA@n1Zzre`QFO07sPN>;V3YEISO1%~3))NjeF$-}5!T#4sd#jUAz$#vPk;?tbJlMKZsbtu^+t2IfjA!<!Y!%&=;YLN4iD^uH%E0ZIs!^y+hzhZUltF_=$hGLyso~)BAP@9n}kXul{A-5n8rY?3RuK9}9IpG}j40SR21?%QF>T9xEAJn?Jp1O#<o;;R1(3QBhDDFUQ;!0eL6xX1ZbtSG{iVIM)yAszr#cz0B_LA%3dOLR7ag3q(4D|r{4EYLm7x@bLEOi4}>2dN9J7VmZ%}~6QI*GiL97~-*jwLUnddN!WlE1Q}l^tCfiu+RAko%GcP+OA+ko!>^k(GW;E@(%99R@>jb!rf~I=L>jB)KlR9<?~R9=Qg!2)PD1l==l(X;tz}=661I7kNH;3H1PZiXHPf&+ExMsY}R9*k17<&eJ&RQt~+RL~1NKmh&)?p?Itv-%#gLmywm<iJsCP<gw(5)ZS#J-F^D+&an)lcA$1A=i)pSrdB5xCI{M)+YW!`v?@82T9h10u0bu~Ge;$S=CK6lxdi*JORY|BU`I1MN;4E!rbdt}ldCZlhfrIPL&#;R4autiuIx`~Uve{Y1ly|be9chYj~YSlM;<`!OIEo`$=oPSMfN8brKTq<%}6dvE<w#eE<q0De5tuf!BG4uHIN+0_MdW&)m#r@D2}1_CdZH`F%(ar_8?Cnd#Ihr-`TNU!*Mf(Jde7UJdeDDp?E%Zo0fPyDxOJQOIA7jf;m%Kgq(_;o_SFFT9BbQfSQ3EKn|j2BnOd8G87l5rYEQ8wu*Cqk8%H$o*{21@8#IlJ{)H#K1<z8K1;qrJwsMCs@BsGYHKaAo)uT4wjnERr6nE<iq-K^n)(&B6*;GUE-Ph6W;@E*k;|q2Q)Xxuav-@7H3PX2xfnGwIWzlIT+fauJF42z-i~lPT2ZT!Tag=6E0G(MTT-i%tFlkUeeIZJM-Mxu*wNpP@ziMYc=Bj!ck*cRIBE}a5B8~eg&lErEVSd09V_kFMx9UIM&3xBOWsJ{K%GP0K;BH9N8U`{LtRK-$T28xU`I{nw-mV;wK};N`NJGl=Nx{;Ij%(wBnPsM;*NH-<@|(`t5KVitC1@)nsZK+y2(|^^{Ac5o%neOLvbH!b8;VYZ-(N2)VAb)WDm6?`IsI1IX^4OYEF)FE)P-{k`I!%Q|FPllebXkkmqnNw=fiMrOqeM=XMoOv*SBECQ{dsCz4~ROUX)O$uZ;!c1)$NqsEe_v9JCN#nEivmu;2yAWtC2P`i`6^LsJWiR7cq(G`Z`%hc`U%jAm;#pkJ8$mhuk)UD(M@+HpQHRkRbz5Ud!WHra_IsZyqxf1I^ac^p4veK5W#9C6U>T3u!irSJK?80$UoLY-qoLq!jovgGbxd^$09p$JEs5Qw~n6Eg7;yv8oL)=%T+sK#53Dk`~dE3amD&0U<y4fe^n>i<&xt)vD%j970TP}v;EF6DMj$LVHatU$~Y6fx!ey<3%I9b)Gs?|vh#p9?;$>Yc$)?~%wscT$`Yq;Vm)bGeC?YL*3$C9dC*{Z4iqQ29>DikMB-;xu^m#Oc`m&sSDNnGHo<eSu_<fI&f;?y?ZSJxoayJQuLlTmMzRVenO-XN<`?4n*HE4@xuq4*P9le?g|_*wailQT!3P?M5BA-kwaT#0=q;r3H=+!`YVbDDzVe#d+&eoOTuzvX_srzRn*oLpjFE^%(|GA=SN7dbb#841kGE$;h0#&zcWI`earagB3zjo<q)cQ-h<H`u4*6ZW|7*m2wizRS;9?Z0KSBR@3{IX^j=T8bP@Zcc4NZcZLS9Y!8O-a*|;-a&p!eMZ(ej;v%CKdZlg;X<3I<bp0}8*)K%1a%BKf;^JCmOPTYih0?|+?*iqrLH2cVtd8E+GAK?$8(0_MbxI`MdX&$&&e&xI`tE>PEJNmLQY2ZV@~{-7eD%n?{H3UacpW#Rb0>z7g&YjQPdISQRD;EedGh=o7C&%o8;TnTjX0D!)?}8el77|evUUkYsilg%>4^y4Sm?(=FCTP*3gIij9~sou!cV5a|iRigZ1$t|4*5V24Suwnf(4=|LfAkf9kxeee^#vb$;{X*XDe`dBE=LpO@$wge6t`VNXyJdD&#Qdcvyx5A!1sbp'

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
