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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_006.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_006.stl', 'source_sha256': 'f79ec66ed4b4a433412adc5e0c6e6197ccb8313acf58d01cced86ff3d2112aa8', 'input_faces': 1068, 'input_vertices': 643, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2583797574043274, 0.2641400098800659, -0.0652661919593811], [0.04471845179796219, 0.49991488456726074, 0.1555044800043106]]}
GEOMETRY_BASE85 = 'c$}r31#}cyxBaVwdvFhp48dK37w!<;0t5*fAh-q!cP9)M2rj`r0x1Fv?gW<r12ee0{p+5+`|Iwv-dpRx-kY_~+Q00aoVs=Ity{ONi|_Mom>^*W4gclVQZzri`ebEIQ;|~3pbZNcG^BU8fWgK32aU98p5m+j9J;VctH!?VY}znww0HM_!QBRVSG0Rq?&0HI#O~c=z@Q<6y7ccnU{Ln}<=5#FI5@!a2lwg{6kz>apj?^KMeL;u7O@B0|Cj$Ix0;|goPIIJQX~AIi`7({>hIgBe%5l-6W{D!{<8Qbu5J>)V_EUF$KNg~-~1gAE<fighB|w?NxuHrPxAFi3E*cha7Fn>h4E|D&+%0sU69{@`$K%KamZTrvpw**_(ptU<ahO5FZmv&;2(Jp|ImyT>gTYzIpG)m<Er?2^(E4tUoXy!h8{)zvV#q&)BUFS`mLIhuLVyVBY6c@i*Huzf;vwUNF8Hw5c2n3MSf_&P&sam-{-_XcL%<ishLu{-!<`#h7IDx-;i*U`q{ttWbw^;FOa``!yu($(LGS-OE2UnEk0QKPj8ESGZ6Vh@&!u%T|4|6$B}<A(|9>vtyJ(|T!eq@K~JUe6Ca(G^ZVyJ&TGtkL#h8FQ+(sqKgf^E6fAz+Hu%MJUK9Vu`?}(9HQ;Zn0sq6qanhePgT>cxRE2N$Z6^J*=F=HD?)=H{6Z*7}_TPFcz8RDpe#`B1q@C4b#5aEQhkttObeUhFyO4ixzO>WKx_GYCsXY_^mK5UatC!7^zpFF~{>x3QU%i#Iqt+1db*~8cV~X~W@tXVav>f;8d-y>u#!0=TN8yjVDSp_zM)O2Z4HjRIPJ3PQ6P+9)?HW}V`7e-f#4TMY`8O(vuN5wc{LPoAN&OyMPl^AgDg4BpW=Ne^AxFi3+WEHp{iHAJ<o6k8#Y+9-zi!ER#GKnK`FWee&!0>3;}c8>7k{CT_<F)7;%nReC0`p}8u?SJ!4Jt3j(J)H`5nJYePddJt#X`o8IeD}u;d&0{lqsqJvt)!Z)(7g=^=H(E{_#o8x$vXw4>E_$nU=d!|$*{d_8>FcB$_@TzsR;7vx{vD*5)kT~YsSTC{Wh9`WP<^+uhn1<*gK4v4Ss$SJ;A-v{~0dP{w?_ybe?Os8<%b{@OXuQ$clcUO{p{q3r4822;C-}Dvvn~F)kQDhJN@cZJ2c?}fbf5v(f^Q#;BE%@0^(P7KPH)d|ddDU!(I!_Gb4=E$ZHLn_yZ(bgX{8GPBf5l?t|Jf4$i%F=TEn0l7cr(<Q!hX0=3;CgToY#QzIIo6BrM{NN3;8=z;kYrM(f%vPVkG}-W%yyg(4VVA;SVV+$2AMB*)7M}WQeb|7zqE?EAh?9A>x}qE1*uv7joSA?_J<`J%Rj<`W~sjHw)_gPKx>S__x%te@ukqwkeMG4<3a2X}TYF9WUc_QnaUEYxv(ANd5Rf-%EYd^Z6k;Zfq8`r`(l2=$~tcFyC~{lf@OKAIxrN#n+7#828lW_Da2V5%9e`VO$1H65qeraMURpiE*iR&CNF(BtiREHWlB{`--oHltcTE9+vjlZ}fC)k5R`ieprIi@cWKLzjaQwPwMAPjyfK%(N4eHQeXSFDO%cDz7~$#tR&9&N>=f;cfM$6)Jv(OHAx%odR%?D_ikL@-=m~Xj~6$k9aT<BzOnd0lxuyvQ3(C~G**1GU?TKq?QqGrkB@=xw+HQ9Uu(boe&<2)4ZSMzd%i&bO!*!ue()d2?{*RSVVA|%Qq@EMEUda0{Sk=#gtd{M+wTD8Z#(hLleeY)T4QhVwLOhdr*d_i?~%;tAHS;bZ`(0XevOyo8ZYlfNSz70(f`wKpuTR3uW#y&;|{PLl==ai#Mf>nLp%2sl6)ieQsfWBI_$s2kp78ZAA<UA>)`r5+g^?vwyP-e2Vi{dsUJukJ^R6fQa{mIoY%;i2VH$feeLfVs9$g_{C}#UogIElzCG1Q_@`^4or6<If9h|)9gy}!H$p#5=!1DOd#m``haI@@6do5Lzdtx!e4{$n6XW$c^n=;nt&U#m6#C(2Nz@sh7T3|)M3K_Y3mf-K{&Dn!_Bj#e&z?2nYo89`d`q^JeE-Fv@V~b}{+lT2xA>Ax#W!-5M*VEzl5hHU-6!XJ4C{$;_%F0SeIfCU^er&HS@T87?;m)GuRUIkIu-BXxc9E^mHgDWFPl@F;e3;a!9SA@{`QfQZ*MqTeDlc;X}^Cnd$efUiSRSGL;tWp_4BXxNSz|j(a#Azq&?ah6aHu%*I3XM$8EeE{`*|WKayDL$LHF)TiU;HF4n`PZ={Ys<H#<_Z<-M8Om<!T_~SQazi*Ztf%=PM(GO4e%l_S5yBBpHjx(h{jBFdFKf5o+{LElKBJF89YJ(hiD&|T2fm-65gS(2ak6DR+?$^=XUvcif)J^*!R5W>K)TtAT{vVT9^26HvEuRDQhf%nn=IIQ7`zZMNMqqu*bp-9nQCfVn*FqfkO04+tc|+HUe|sb9)V&VB$`J95WmwO{zM_tKH3<1<5=lFa9sM`S?~5c6U;B3|`XO1CSQ&?73Fu$IxMVtk_GEr6pKr{Y^>EzJd1Eop7sD?)2>$+ZsB^ot_<Ex`@TXQ0-}K2ZzA>gX&i86_@r{dlP-nqR^ruz>`@`lx<@1(tekbbmOfLC)*7xG;{yA`7-LlKRP7j(czLo;>-%MT{$6Yl6b$V63C-ptv%l+MdTvPaSvm$@fRLR#Wl|lWw^RfP%X^Z0?N)7)-W%x<wqyEH%sIzGo`twpg@xyvfSuN+awFlaNcr*Gfs;Br`@J(rtp6d(tQQmg(b*?k!$w(Y`(Ty;v)BJ&4kH+H|wDagC@wG|gksq`O`6s5pf0`QeVdzb?Gg~kCqetPm6E4YpB))Vt)PE5pzVR(L?vJ-@$nTALsP&kL@e2BPmH4gGz@K0{D*gHMiugvi1~M-8=drRs(GMO({<Lyv=gP#AuOGj@QqFhP0MzMw676q(RD7-SCOKbo=Qo^h_15B>OFCfwlzD;qR=5oO`u`yRQxUZ1U@q~Ep`Y&II?s#!#?XYwciew}rICCiyl1E!cMST?|4U7@bMGbjysmv3D)sde<;AymSR}sQwm;6R?bTQ}fA)Sku796B*bhvf4gbd_sbjy|0d?Ziq5hGb7~ig);E#!0F8O9b)ZbT4{IKKe#Wz0BLVmmMIA3E1{25trU9|jy^W8ZSb#6RG|C}9x`ahB)e|ml7pUQ^)%#$a}q&+!nAwO;q`e*iL@y#kp(4K^W=%2;u;TJcMUvA-19B0^4sS_84cKU3A|D>__`hwr??YUG~d~?rF%+HY{rQhtGGQ(d`7vnXjpyX>KUg0^%oXN;PHeK#7VT(pBaT~8j`_ONds)%nM|A_tJ%$cZ@KRfCyYK8mt>TTl3w>$Nx)QQZ9`5Dm<?VlP8|Mms6|IsegFE$zexp_F>rKd42TM~$`r`?M7JU)s3{4{N`<VXDtzts--p8n$NF?Z#>%-|EU53%d*kpFNy{4;@azDA+);u|~aVH`b&VPBCUqxk08S(0x*pI+|QVSbN8B!Am_w7>CLv@@V7{3kszKNtLi{t2lkzV@>v>h$R(`vkpZ{e|eyx9I;XO%LKa__aX%T>a6`-Nmq<DLFuVeaGj!^7F6b*e8tbFi+|aScd$Nf|76CZVbO}Wz?^i6ZiLC6~x!Q(ug0wV=49tJCng*_eAO&|K^Z=g%(<PuAEnwW$+gkJtTh7WizFn&x_-{4vay2JX(vdz1%PP@u!j@e{IQWxPHfoZ$G&Gu+$4*K2_>mUxfTAsm0ei1y4c#F`Vy>3(_8=)q{!R&s&K6y$0%REicc*^u?Xg&XZYW-=c+;k>`K<PvnOcdyD#|f5>wzW9J2|+wB{y5`TGH_}{ikzW+~O<p0hdEOo{W$9lMQ{8~}3j`AGQeAPqdkN?Xxi^Z>=Xq40`U`Ic1=(|z;MIS~;|1AH7`8Lv=DgF;%_>D%~#e7bP_Mg2zSn7ApjrLc24!`8`fs+4qG4iini4i}#SfJz|9FO($c*WJ|hn9UM-!nJvFApaEDgKS#y(NEbYpJ8PUWEEhY&|4Dbu8x3y`?Kq=S_FXpI#p0QtvVHJ+gO^^PQg!{a>pD_CK0Up2L~TAKj7s{fFTD7MACQ|GD2~-Y3t^v^VLSh`+A|_8XsWq5b}&t4Mo3G($h^xP;?sg{q2Xc_;O?%i*a1W{j^KuY8F3VcgGXZ)$av^Qm=6eB(wE_{+9;72O?zabMVGgZy0NvG}@Y7K~&2f@{PNTH0OyzQ7Hf@BNy1UKjMUkNm9HMg2};sQ<2XUujR3&EnhF6o#L4wfMSUD)j%dgJ^%QR6*j$gy6cq+jFV-ck{|~V#oEO%}usm^!YqIKc2Wy>g#tKp?<D`!{q0NZQ-Y#3BTto@s0iw7?&K_muk(MjYNMx!{?N*r{OOT6yI!>Tk`#D?uMVI@@T13F$1oP%jt0)b(=m`{FKSi4;dnmACXp`vua}x<8w#gefS<l;lB(({_$DZFMawV&#m>(Pw=@fIGXKAJYMwvVtl@C{~Z2;74Y@n@JFwQpY@9PruPmUckC6^Px5<$)UQ4Tew8Q4AJJ)|_<6BzXs?1W?rYbGujOCD=U3cMrdTpbG@w8FZTjEv%iV$hwF&B!za{I2k$(AP`FTB_t7t`&;eJtW=oI<;N+~d}A{wtpKcotg_J1z}Kdd31`}rl1^~Ri=0P8^i3)qJo`+{{S-(~dYy4JYgE&9C}^FBM);hA^jxu5oXGu8v2KT!W`GI=hlg?cQJ`Xy?h{^1$O-;)o1>MywNZcoK=WA2D=WT}Y!A+7QJInfv7pG%H@cz9_y=B-`kwHa3y`C|v-IqK|UnD61ZUW^^baNM=N@Q?1ob>veX_q(%;#Md|9!h9b8XrHTZde_7KqS{$GFT?vXe9tym$5y<T&v!--pJh^ic22Y>W$-Rn-w3aO{8`^IF5xYfp&xdlABtr_KbM&S|JyoTcY%QsuD)KW1=@3~;TD|l2^{y!Vbr;@AN$_5PjTD?ZQ!3Cfc`0LUoQ2BWW;zK@xr`HTVH(b&|~BupSKD9-Bf)2L=W^^<4N+ITx-)^e8Y?L^Vt@8o^LeYf%@m?<9g4W3HRUk(aT-iZ+INQI{7*Y?hkMC!mr+3t`}o?Rq-9qb<N`wvA#8^4gc$GjMtG55omWi)Om3a<G$#)e4esCc))LWAO6OSVd$R;@IQ6N`A!SLeq-o#_$79ue)DIT4+q!5Z|jNi4fosS=JzXwaj{Lt{r&u3;+w^@;=0bU@Q9ml=lBM#mU(VW`Xs(lr3;SRxd*;C`I=mwbLbDwq5U}%;C`_zi}>26L0AV)`$&BwFc<Ruj$^#G72DwIn>ld*HF|WwIHoF!{68D>d8r@j+%FB^V;b7i_X?hiPN*)v<GGNrWHs`S`=LEEis8PwHB*e6zw{^idBRPs^NYK|zqg9_wVYT-diB9^%T_~wzS+4B*UMzIzh6PrX}SRG%#n@olfT2d9ashT_mS7p&J!Kc|3h`Ov;IBgS3HV#o~$j`v+?3N^1BZgKfdeeNLODgv=aTWHXr6g^gFb3=04Ql^a{tF`xSNK>tH{yd%IkxT3C;jl9#t3u9s{E_I2q;uS7rKIyDxI#&!K@Jo4X<ME|sZBI}^GcN+3Ts-gX1k7eE(1wvQ4UZ<MAC(6}#tcU*m9>J&_gZz!7F%M7g+2`haYnbObPUHKa;~(K?4Z`<^1Jj{D|NJ4o@ht`VzhDhF-^@0T>-<OD2YV%u@i)ieer+EWj_cPaIs6MJ_`S)RBd)%2rW?-J<J)}sIeA*~^(2!qUejx0UTyP&|Ft&8>qBGo&zlPHUv9(s8h0??7S@Fy{}JtX?1vNkq2Btt$p1DC-=mET;yxt{#_L%eK1b9ajyk`6F&{o>L;E`~MgINbn9m)1V?Nt9B0uL{e9qlH;)ttnq-}!sM@_-=@F7v~9qW05@>u8V#-h&Ddgz};d!yZa$3AUk72G!?uc4nWuEP0tjh1<9wEr7EzmL<4r$&2zzJ>3P`>$>;!MYLl8|SsT0mkv}&4aGKnFsrduq-)bA8sT|F6*vQ{W#9ovoD^P4orphnCqvJWF?+M-tvT>>^9c_HCatJKT|`D%d|Q&j>Z@-__IEsez!*G|NRBvXN|}6ld^rdPc9<9zPcy+XNZRT&g)WWXT&u;?`l2({m`}?>Tv&{Wy^~Dv{?c9j`eVFrX!dyHIcuhALhxFDR{nDx(WQzc;2gD^FQM1>sP(d&$ioGH$t1iA9)1z-`Cmh>N~Elu$*PFf4bHIzE66LZ{$PM)z>!s7r$y})GvAz<KDhL`gvnloY&wN=+Eg5kGT3~ijlbQ{Ns)Nm1hs+|Ez&^CP@iAA9xUme11P}3@(WNe-RA7NM+2QY(2TIPC|QlKhkqwKznA-ME#z}Fpgd&kGT5!zXdVh%o?(;>Lr#U|Dr$o$M?~nZhqEem~U?q<377&g<Jn?{+_Z=Gp!X?{O3P0URp-9|MCX3|K=Lh@7xK`T`O)uKVK`teOD)ZU$b@_j=S(W`g3_T%&Qc;Q0M4BsNb|Y&TGhCw|O4Fy+8J^wWCmH!~`6-UOMaxw;x73^B2H%vFdoVtN)*U(e&x~`%JMo?z&m{KJmnS+`oL!!cTY)<NJP_^pDy8F8pbKVH_L$kbM2;Gt}GD9N+VPS&i{J_ZG)3=7ITE-2>-U?jzbcq9m^C-mA?2&ev*%x%pbsl(<eSmOkL>n}2!1f4l_GT~~cUdtN6%KRnte>xmxp8+9HYLpygrk8$-K^VT>~FU-xal?d};erBxOH$3oMf$!UxOKp2xeRJkdwEt5-+!v}RhQH>q`}bezQi-o`@kE{B_t5{NJ+WRc!sktUbcvlfkMyW>E*9rIb_CkjFf-~b#JFqKs$iYjn+@%J^$6pYE*bhihZp=SA2AObrFZj<_Ukbp_`b@2^5^68pq_q|tUvmzd^qmTJE-&g9oCbW!tnQ`=lc9C!qwNp-@<Q~9sA_3WpQ2~F|Xneo-tj0{aRkE1M~M`zICa9{O<g`9Mv2CsmjQoodN4fzOvZ=l+xjA+&50IBl}@<SxwaGI1}@e?~^!uBPb2lu^R2=Ix-W~MV$;~(Eo2Tqy2#mP{*<VY@AWnG5u;|<Tsgu_5=pw`=(TF**_iNN9Mu0u`>Yu^K&=m!-`w`U43)US{(P_1dMx@-l$XkJdRtuHtIhe06%F<tQ%F+Vcs_%jPvq~cKhDn;p^v0VO+`|+2!hM{hpy8I-isKk)C&y+kDpRo;O{6M}6aajTl#7yYmIdP3nd3)BPqPKP(>SHEs*~^RKDM|Gpe`RtMv{E;bYS<ql!o{VU;phQ)K>?+8Ud><`1|j^FcfUia{xgK@4S=4a0k_<bkf`WpBv#?4<CkNvIRDa?n9OW;4o_-fCOVt=)I6^?tZAnJH8M?WNAi~dQF812jwhvN>~0H5zI=pTaiyZL24qyNM0a{n@JZAL$Mj)On>D#kJ6UgY~@9SGw*G#*F7|9TelCwB!|f6V<y(EcJH(9Wmlalg)W9PPjU9sRcN)mB&E%&KAjv>k}gBW*9BJ-P6?+qjZm)&b+lWz<=U_YkzfOR;VjyoUU`%h3O}SbR^h;3nE*=XIL=8a`iqzXPB9Vf%$4rmJs;T}S&17dnLN;~DB7^TBn!tHC-~-;6i_zfCH9Uhe-E{z|;J5Ej`g#?9w`#y@dOH{bDmAnfW=*&piHKX4qIqJKIMm;N_Bf1@92JjVFOC5>|Pcl;0j+P_ez@Dx1ndXNbF&<;h=&hjHLf3kbx^HY{BxLy*?!~U>UHnb}(_9tdiym#U7jbVAwe#gH0lQ;4+)!=(gWldM#NP_#L*=7vZz0QT<&zphcUY&;bKTj5eA2Js0oYykK&A(m~`3FMqo@9wqd=5Gm=ey|aT36q^x*p^8^1F<ezO*d-$g1#f48n5^TLt)svg3OEYn18gJKlTI-fW3+^>rIR2mM_LpS#!9LH^K&=!gEJ@ciwrFY-ID!F;>*`jDG{7QUAM6`mJuZ-evVdy@Xgx}pCwcR>BT*jI#wN8owdi~(qWdF;E)_^?P<-|;!u_>c$JU58=F|BdIyVJ%KzTnY!HJ$yb8*6b0Ur~RCW{9W(yefr~^rmL_2-4*Bi#E$+sKLdW)TwJHe%3$Akb2-i{eFo%L%w)RyX7f^L|E-jmKj}80PVg}FPu)$2Tz#WSFxvlgE$+)X55Vu467~7Lo;f)Z^?f>^&e~bnN6kBf`h#+!&W}@WzE&?c+7s%F>-TgV>NoO2e$}dyua~}wI<@g$sHs23_jGYj;2&&?e)xA{q^ob(@&1_E=QF;qtnv))<mYAoR&n^ev*9J`)XWDz^&f{^eXV7EoL7b3m{+OaB7bEG<PWHge!Kq}KHsy|=CsAQ7t4qB#_oaVB-^&{bMyKBmGQK*++WNYNwIG=Bd|X3Jw5Yh4y>1-LU14Fdv|8iVpuP|a$r9;@h#r>+t&zna$d#v?Bx?7|8##`uP5=Iw%NZIo=a?)g8KC~p}yn!QoTjU@1Gg<2fTLkwOjLWAK6|P&l_j&z;R1@BmbQ*_AS~m)KB>t->36^5A(?j)DJq0<K`HO_7_fy&vPq=-;jO_I*a@Gxs34Z4@bWhFB9SFYcXrko{&!1*QG5fzJ6t$95;Sg0gU6r@~AVloZI`r4qyK`7Ip4K;Jk9wK>em&r9JV324kMQtcUze70{oTb7H*mx4`!Xzxh5!hNgHQ;B!0p{uiW<7PTeH)z=cQbMFWLj>yk90R491-XS-C<$b&taiMm!tM7Op&wer``ro53{50_WbML}?+E)gmPCCAS-mVVzIhBSYe_m5*r+r=e!)|`I4d~CI9kEYXHv)A|ze79uxlbE54*mRcIr`_X7dY;{3GfRiM}FYW!>+!zp*h<BtTFnb&J-LsNgmAS(`yd9`G+dveU%jR(9Rvx;dfk(`I9oUo3HJykL%I%?p`;a?^POii(wqc%|kn@{6atc(etpYueA+8KfE0h;p*%4vS9vf>l@|j8_n9I|IK;$zT@da<mX<1_Usvm^Nn1F<M!{2_V7Kl|M($8(Vw{+;Cjrn674zkPTJ{TFvnpxztaTFt6Lh*YsPB$GrOaHqdD;3uS0vfmPb3El-%#?n`K&|&bQK-SALt2pRo_xGie0ce=HpNneg77eN<2QMR&lD%8U1i^2~{J^XvJe{?#g&hatOBe{CSzc`^4vH^0y<9Jk&H^yh_W^t0oA%MMX)zJ6gG{G0LU&#<HDhXRYF-^}}ku|5nu4L{#~@%1L}qFjA5NgvExt^*F=SiBeS1&!&B^(y=-^4CXTT>7na^L0<W4{xrRjDARe1Ab^*oNv`{INve1QGf3=%zy0(>g<0Ee|S5b*PILo-28w5_@kG?_j-!@+k?^1gPzOhCVk2a_#GCaey5^%4)FRl+P~=y#_QEKJl}5f9`y&@#r1V>-62<BPgk1nacQ_;7yJglTz1sibMug!Kl(2mx7pBxZhn&@Xn)>}=$~&I_Dv@nqJEYgxc`<;0l#_?tOG?ap?;!t;_HDsFpkeEyZOcsPqgRiLaeL(GU9o|^6D6utRr#0aarJRkH-7nd>`AWnghp8atrJEUVqe2lNWw+yr-(oo_)a8H}$gcA8p6|Yeasur(PP&pVYIWTz&n>7aTVr5AGN71yMgI-fz^(&BJ)*tBpFm{~B*^<G%l~A?nO}i1D&##d!VM4*9VsP`~*`tXIAKQQxN$=1Iyc`24=659)YzaJzoZ!2>tA&QI;?zY%Ue-^(@A@5lJo9)UV>-!LwY>xI6StOC~6sFG;UlgaR#rNcT|V+Yz}p9g<lTjcZm6o+pX_eA^oT+56N#c@L(qn#zrVc%GIHGJM*?BAwie9vu%{{i<qZRL85%gTN5?UC^Ft%z{-wc5|%XX=P?xe<eY=v4##&~66S6a6TBzL%?4IE*^!PNV&e@!q3$JP+posB`e!WB&X5KSBTOxsK!38HoB>Lf!pii{U5lg!%LG0sP+w&~LM2P`~wK_%&xDzr&KqYQAp&3VQwApR?zcvU=Q#WLgHTM;DiW0<BCL4(fmZPoR63`TzPS&?QTh^ZCF18|dV(ZJM^*ihWkhwIbSzAnHo;AS;GgF^)QiJb^lcI)|*{Pb=11v4eWXiWAg-8H)dAD1O6Ge3rVFe3rb4`X~8M9&ZzM4tWiAHgyhp4$omWbp&}bwI6i^c?9$NF%-9BDDFlbL>|Px=*CbykfC^(OWzHn&L9sXkD;z5k0CF0>C>guGh|2qDz0ipT`MXv6gOlj?nP}yUP$diZAEUyye<sIIzw@JYE^Po9<MyLI61c!*{#UN$YO;TLvea)HgbA$I%;-uI&wya;>--ixva2T@rM;ft*B*1IdV~Q9){uq48_G5ifdTW-in%5bfnfJ*W>RyG86|=%aH@gU8%Lmwb+iX48@J9e~=rK8&M0B3-kOMF%(y!W+%6_qK_42sa42Tm{XRTo1B~dTb7}?B-M*tl3a$NI6p&iUMuoZb21cXpn8$LIIfB(S+UrPos5%K{AI-v>Ltc4D^6Rn(TZ>@OvW`Uo>=jT`rC>$9@bXEiqzCp<RsKY)Kp}pNy$nRlM|6u&BXlOZyrOj#!&o|UP7`8#Ws3L$w_%U#ouhuU({6ORBX3mr5<DzioZ~klT|#o;<^>bsS#F;x1y~T&8YRs&B!IFZOJ9b)vQ==#ZfCFsTawS<U7=(WTofHuc+^+=gBG_S@GD4XVf?=4q9=*ikXZ9^bhcNaV~i;7>aLD50g((H&73g4>NBAL-BCxOmYJ&T3FGXI-ES5InAj($<4`~sWZu)$y=y#<T#%17KY*&>Lc<a_E8M=Jb4;*B=tPGKXnTAJb5~G74<y%JjZDjbsKpVc>(n(S?PN6Q0i#vda}|;veJ3v(d4PrNb*$j1?nC01@cRqa}K?vz9ZkK#xoRur@kY<W1oI!DE?}5&bhDDII_|g<j>T9s4vJ@saL2k$VzXJm0l)aAxBYfkR5YW@jB{e>M8Ob>M`mmvWi1CT-Oog{nTURW6a-A-9T2loV=erk-CAbbU0aQ3$oGx@<eiXY74T`YGkEt$x8c@yOU>8+me-zCvT<hqK+r4*lWZ3f0{g>x{JJv`SYpG$Vz*V=ac=Y&B%V_BGeM(B4o$COmRMj;=I&q<owh!)N15v?4vT&24tnpZO;3t;*!+PHs?K8vE#n1xFthzAL<se(ipO1?dU@tN$x|g!cg4E=3G-6QK#6Pdkn>nJ&EG3Hs@N?mAcC2+|MWuq%N>I_d<$0+MH`jN9t&sb04L+J#{L%JvoS>crHV6H1z^m=}WR>?TDtvlcUKi8H)EY6yIhjeog&OR{E9fSUX-*{~^C7?`9}oVRNo2E2vk<E69teQRGGBQ8wq=F^amGJc?{E6o=WIYf2dP7&(l5jv7H$dYycZ{GR%ptn>@{JvkZoB5F^PjG;IMH4Qlp_g*O&ic>NaCve%TC7>oECm{c@LDfD?vC=2xALN_VYh<M+`6hWgLvaW-oUC*sIfOi!p?Ee!@fwEWO$^0nsV3QEn;f5E6~D1L_pfiLzsX9~{!;PZ^!}wP|6l4)`byuDPf+hs-;&=l?;b<(N2=O`e&o-JpW2-JRK-evk)M(uP`{ABaIQRHD2}x`_olJb2y!fW8FfEd=|r;9?qsF2$jivFHs}2#mb%NOzT$_})8vQbr_@_yrI%dJQSk@rU*r$uyVR3pr8~)Y$tM_!mrxgzl};irAqO)Qx2E<c>(nmP-sIlQb9^>eypXz+ypwHR$WR<=bAHwerCuV3l2=ntla<aVEA=D$ThYmi0alEq_F^b@JabT7huVqUiGN>*p}0CjacQbAxd_#d>Pz-zp5vbG@6xsb<kjR*m$rsddyyT_K@_XCSFNoT7>a8%6c?fzWToC@r8&r@tmt4x8|q+kMQUX$e5@!)u1wBK^&w{^XJQ))v0a7eRiOHil{O(SqOPDeAva;3;~u1VH?=akGTZ66mnq&y9ZVj~b93B76+7;&ii4<4$?d5%sZGgEnOBoq%I19TqO=CJ6uB6+0JRjk6x&z8rLPN6E8CpUd=%%QX0<t=3n_LyFH&r0DE@<*$>w}Eqcj&a6FD<ABQ+B_6UQtgH3wO#H(6;qa;UY`ueD;U75k}&tvE$J%{XhtCH0j8HIAY90z<J$Jxe~zzc(3*cTo?M5A(RY7>d_W*OHZnlGl*`WGJ3R4IxjaE~JK#LzuUap?CvzD|rL?pi93Tq#h<8B%fg@zUb0-7pbSo7s*$sm&jMhH(dJn1~rbX^bYx^6}PRpYsG!)6DyumUou`<@t*O~if>l@qW)$m{>o7Nf%=jBk$?Yzq4+gJ@juj8<X1fQKMck9s87gG*yei-#kZ)p$+vl)w-}1AGZbH@UL#+i#!;`4uQAUtS8uW(Z}NC|7>Xab^yvfY6Y>M{zYN9iT>AYT^(FZo`8)MJ`91shJ43N%bB>MTUmP37N)y|_Nvud{MRF@rP?ItgC!!`KCnDRZ9%MDvHrBS$SM0$&$J|hyn4vfsH3>NhkC%+0I2A*2YL~XArY0pT^(3dY_JNtKNJq^~&OyyZ%}mbByj%>$MHq_nP_vS~sOhO$$yu3~o|=|ySTW9u@m2&=$5=7SioxVD<bDjrU8#M@HK+m9KIA^k3t%V?VkjO-9Yr3+<Ben}o<JQ>9?v#UU??6<9ZMca9Znrf9?QJp48=njibqflvccnxU??8OP(0M7?}k#xkjJpU6!)Mur}iV)qqd^<BllxJwxYHqw<6c2b|pK;pf0s0S!s20U2;`wO|sHjWTmyqN_BEoa(QZPveL@rLR4>RWpW8>eQITLW&VAAYD02;asz5@a&5LxaTRJQYAtdto=+)iIdUm-K59*JP4<`KY}72&8szNM;?x>sr2%B6ZOO&Se$)W6(jamhYHw-~S?Nf!(gEb&<o?u=WTg|xN=K8G4kGs__oR*{JFXMOjj6uWf#gP1f9gQ8(&1#KeaZgh?$qIAr9;T=s9mT-$Q`JisYA%^shy}p$W5p%s6)t2sokhU$Vx|$l?IZ#k$X``kd+Q2H=}l>4kIfaN_Jf59jVR99m!q{#d$oO*MA;rD{>xk5o%qs(yC;o<vpDD0>!yJoY!G4s<(&p-k~@LLvdjb=k-~bTAy5)+?v{e+?rg;!+9N6qLw08BIl;&Bj+Y(@Niyl8K_yv8OWXt#Th-E*I`C#adJj-F{&TA7`cLn^Lnd5?M<#gu0!olR@#$Xhn(NTd7b2^`jYdLb21d?^>AK4d8z*7yyT+P?&PB6vL4Rsq%5@yxh%OFL$QyC^ZN0jb|(9fOEMIf_HbTTrKz3BrO9O&iVJu+ueSo!7UTkCJ410n59f7QklKx0kX(`4i(HZXhllfe`-9q%tkjEK+S;>Kw4$mNHK}zOzE-rbq7BuL(cOw(R`jI~vSK)O6hm=;YA<qsasahExjX9yFci0^wjj4BH>LWLec9Hg48?V*RmpY8Rj3uoN=uWgkV`QX7orv==cg8=79|&DUO|T9vec^NvSi(*uXSo&vQBP5Z9#58Zsjr_t*CzFR^-mqUgXZ?J}zU{hdPMdhaALEJjP{Q$52O+l^W!(R&=qVBefm51GOc!9a(8(veIVcmgGj%#$=_n$n~f-sI|zIsTHWT$V$tTm6jn_AQz*SCo3&ME=(;zEkQ0qElDjwF2TPqNi9b%Nv=dKPcF~)DXvDXO|3<)Pi;c2MXtquX+mvIZbEKLZA@;=epl>I?M7`!ZpZQKM(siFM(#)LLRK0`9zq>K4J41I4x<K=hf)Vq1IYuZy{UoZKpw9*wJTX^M{;j+Pln=7nsY98qP8S=BDbbCBDW?t)SPp!A+-j%A-Ot3v5)4Qi$2r}WFK;IYB6$gvbW}(bKcYfWN&hQhT=k+b1oL5mLwM<m!ekEoNJomDw=c7RiW0_oNJ(B$C|0Qspg!EO{q;Z=X$HSJ+-aoT&ooaXwEqoK<%bE*LlVLsr@wPJwov)%{jM5QAcRb`-@_Op?I9;oO9!-!^q>vV;PErHRoImrVb_tlSeWX57eA<bRe}iS!qx5XDhx~@s{z_iWgQqqdsCNj%O%-NPS9v%D;ceQ2aOb3;A#IC+bgfS{pPC^(Xl!^AxL4oYIC+oPhe7{F%p7tU~b*dN0U7$ZuTE^9}V8S?Oc)HY@g8vBipYn)=_u*0i0}P2^4d{Z5AB80ubf4EYd4aikRstXO8nJjQG*rdu(II*~eqJe4|=I)l83x|lkHyp%ehI)gleb>~xOlV`IX^BIa)P?wR{Td~oK)zlT_70g*pT}j?dT}53<Udg;w48=<risw=nkQcBWa~X=KQKyrqktewH;{@tN@&xjDhT<tM{X2y^lRSkyhoN}6OTRCtE+#K0uVW|<a~Y2?>U{Ei_MPHQ)GgE%<Q44eEeyrm7>d<=I$_0eEB><L2sMhKIGTE#98Eq%jU~rWk5OaEvCKQhP<)c1_#E{F`2>%5j-mKGL-A3UwjQNMk&lui7>ajL_mMYK_fYqd_c3n|HJZGedVm^Dj^=qDphl7-*{=r}inmiYlDCt?sq4u~SCbvrKsa>|+0mwO>H%^-EB>&;PR&DB>P5Dbb1@WWrDi54v?7rvkJUvJkTt3YH32yR^E?=e6EhU2pe7-wrY5B(Atzy8QffkS7Aw+Ok;w{AD^gjJhM_n))svi@oRXn9JvAdaJvlqolboBHm!UWt)syVWV`pP1&OyyU&Ph#6%|On;ytE9($*9T6z71_284~<Y|CfHw{|p%v*Z+gR|N58i{|v_UFB4mvp#S`%7~h78)L2=A=OH)uOX{w#{XZIdOsD'

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
