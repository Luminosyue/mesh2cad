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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f121301624174b179ca4d50158797b03/part_011.stl', 'relative_path': 'f121301624174b179ca4d50158797b03/part_011.stl', 'source_sha256': '2713e3df105ecaf80c3da59746df252160b02b7e863a65d39d5e326b63af5ab0', 'input_faces': 1010, 'input_vertices': 692, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07343970239162445, -0.22654296457767487, -0.24307981133460999], [0.08167406916618347, 0.158139169216156, 0.25020837783813477]]}
GEOMETRY_BASE85 = 'c$}r32b2_5x3;UBBsoY1p$QTMVGtyTCMQ9n1PMK4kQ{~#4MUCt40(Vi=NyEQ(BvU03KA5d$)Ko%AcBJ2+Izosrs_EVTK~HDTWjC<>4)m-Q>RW<o$9IfHffk7X=X$Im(RF;DJ;3Kx?xbIF)|wwT?Y>C*}3bW5`Fs*cNrPj)BmiT*SKY)CT(0sgfX&km#%|44=h~KQ@C=s@`a0g3U})_aPYwJz8(7w?9!Edo$%g+x|)7akMRCo&DTZBR`{s6r*zTcp3$EF<^NKdO$a_czv~FKWyF&WoO@afIAZrx@3RkHUAw{IcXwVx>DQMJwqqZ{@`37Yo$C)>%kJ>&dhzl`;9fFH@60gg=T<tr+2OH%qcZ&YwBqB-Z{+2tWE|x1Z%b{I<@;`M_)>XzJ;ABk@>R1*`|EXgE<fY<`JB_W<u}|GUmwdih}+4pd)3^{{gbc$Acsdgjr^atcX+hND5QDobB~T{=kVpLPv_T9uMc$i9`CdFpgn=Frn2|vFUajNCRXTR_eQE>+#YX4hRqI-e(>ua+v|@^>Gb_8&EPzNcJ8h#eofvP_T{~Q6x`_;57D1>s%G~X5B|85>^&#`+TrN88@bCIv3slEo@n0cH{(6_fs66%y_F8{VUPV{d1L>wF*1&&Kb7}%6W`J&?Okw|z5lyovj2N8C};PE=Y!dt?N*0z77elw=9ng*8!7#7dE?RVe$G?UZ${>cSkGm@z2AJLN{HY4tL(=v^0~@i`)#6l`CQMs+}rv6OIPpZ&-cjoTHeSXU>~R?$A$7c>h|aSL;68^PX_iOs~=L|-^MvFoY!NF$97r%;)=nXr)9eWmxqWCgbj9#pJrj~{l+5cAD?WO<&9A>(my?9yMo&*^81X8@s91Xyno>n$97rXn`OPDooe|KCmo-w)~}5><uPvk|CZ@o&F-yn`$qHH_*7mSpUV47j7fBRt^I=jR6b~Qx9_in^~~vJ-(SAwp-uMvsK(W+Dy!JfzbXB7_VEFSztED~?|n3vy+2tw@snDtknuGtP|fb|>|4UQy51;0uFL0Q?=AM}X<mP&*HK4oKCrVPdt>XO{k*<oU$5lX+ouFL4_;nV&F(AST*O)Yw`RP)oXf=*={}s_fB5=BT0XR>wRr!^O8j}ZZ!aQmoU1H8TS4Bx{^$|BUCOsgDd+#41)Tm`mc`uODc8T0_rELt?BaQxn<}vP6i6ffV)@m)p5X^pRI~fHk9oVi+v*Q>_+I6BySyWEuXOlr>v{dY#Yg-+u44B~zihk4>kocgX^q3bvxN7HQ55}S`Fdk{zj)X8S?gH-v#`0GC1iO|^4a3!YtMFUm*qn*MsvSaEVI0t-S@xB$93@Y0dvUv$`1-8Hcph+#)<OUel)&lB|ccMHTUQB7t0;qU%Dp0|H1jWJl+~Mm+ddJZ<@XR#+Y*AcZA6}9hjWkqkQaf&QSc<!yJA~-6hh`zc`mqwMmZO_*Y{cepq(tpG6O1oc`A#?9t9Z-MHoKwey(e_4AnJ_4AloUOSJe^=s!b<+bye^4fV!dF?!=yndavymlT_UOSH|ubsyd*5f>n885qu*Un?1UrxrbkLoeizTZP#|6IziZ+BVC`TP-&ALWz0$H$SURJFklU+)$lcfm8GS2}!?$XUGJtF^|H_ut(v{@>fYe*ci$s~x`LJ)EE9_)`8vhXuTyN#fQzmcN`t=25HD^YWqBE5%18mGgVO>(h9gXN?xW$1m5%7Nz985#CFD*x7I%FIOU*-h00VzklA_nf$r!Z^?0Z`yls&@7A~#4xeNQx8HknRfNMgD7lb5K3DlQbNGDXb-g>z;XR|qa{C+R3OM}5sWLzARcbc3bL9#?&wARuJ<t8~?J*v|miMlBBfj77Jpc0L8aqF+_A9ToUwN(l%4_Xceo8HFztJ^qz~Qy_8>JpZ+xtK8TaT3vkN!7K-R1rdc0L<z-@pEmhj{-QqYjD>b>aQ%>r;T&6WkVvPHem>uZ=h5wehCBHr|ZPJ);vlUX<647v;6%MS1Ob3C<}1KkyJQH!SJboGIewCU*P=cK<ksUvGGPn2*Chi}3P+w>!oAmLK79Gdy&L*Yi&y@%nk*^7?t+^7?t+^7?t+^7?sRc{$IA-X50g(dLsp-!YQ*=k^D7_dm=1P`jgCU$yI+^8WZ*JkD^v@MnnUe*Dk8%ktXwRQafqd_DD6iI(f>b-#G+I<7pf<DMa%`8w`N`NK^1+I&NKZN8zrHs4TQn{OB^CW$}ul=q{5@hTY)U1!L+)aFsjYx5}OwRx2C+C0iTt1aIr8%E*syj|^MWPUig)--#+`9GV){T6sQPR6A+FI8Tfms;LGFS(5K`@?v<yb;-_uzy(P1p6XG+53MCO-^+GT3*|~p(`!Lx8B3+_t&2GwcUI3<_+@a<!bf~kE@u^C-Hg@tUJ!HJEdT66zx8N{g6^TKK;v%OFMtQJ)V8Oqr6{?UP&&puM<6vKet>98PD~z@Ou3HI>~iNo6lHYpU+rcpU<e}wfT%%zc!yyUYpM-ugzza*XA?I*O|!U&Hr`FWsc=HHIi|7r07zIpBT&M+t5#KBOU(4LR@z)jCOc!zNEZ%-cw$iM=7t(qm<X?MapaQtAzDy^Q*OQ2P8HQmDk3h5gXT+UvCNUc<`ig%Xv8G$Ucc3FUo7ji_zWHE3xCwXz{(Y8`q0qow>698XLPNdi)k_%GcfhoHs15pEoS8pEoS8oi~ibpS2S2JRd5roe!1Q&WFnD=fe&EO6uol%WLOn<3`F)6Ww2y*Y}s@_3J{Hto3A^X!luBZR*H4abAy%QJ3p*>epGz>(^P!>(^P!>(^P!>(^Q3o!438P;oxK^?9S^^?9S^_2bTXbh00Neg0#4eg0#4eg0#4{eI!q%l_>3`vuGE_Y0QS?-wku&)=fM2C&!WjYjDn;<b6E-<^ISdu_g|yf$AoGFFo9*5=#FYx8a8wfVO4+I(AiZN9C%KHpAzb3&r+vAo_M%j@m2yxtzmYxgh8Ywht5KRA(n{s9LmgA4Y?vA>&slD(g;`!ePA`?7|e#cTI>%4_$7#)Bo35*t^_YvW3JZCoj@kE>tapPcA%VR`+yu)Ka;SYA6WjK5AzN$hy^UwAo{`$hZy(DM5CherC8Gh}}`uY<<z?c%lhiRJbAiRJbAiCSKppQ!a~^AqK@`HAw{{6u+eexkfKe^6eVCn&GY6O`BH0}1QV<^#Dl$#Jir=Pj?F=Pj?F=Pj?F=Pj?F=aqMUZ{~k=QoR2C-q@;9vR&Hs%ktXyg#H{6;`RBq<@Nh1%j@4y#(X7S`@U3p{W@-W?fX)19+zCtwRwf|+Pp$}ZC;_gKCigCSG+zivb;Vovb;Vovb_Gi^r7S8weQ1?YANOVtbgBbdHwr#%WL1a2Y>L2*S^p9-aI!q(fv~5!+D(g{L}LK-w~Fkj%Kg@9YlHU?;y%+<41XY-u2I-1)PUZ^Zl2vN~#OIeD|T!-l(wSGTxW4_kUh!F>l|M+VXdi=<now2p`OmT>9nc+2eL^#BJsE`5zqF;qbMdvG-Pa?;CE{$9I>o&;6RuyTR1|$lt3k=H&YuV{kqmr=c4|<ouUnn)uL3KF+<rjh4Sd7EBS7SU)JQ_rs>EF^TRM%j^5)RrzJoKiYl4=@#Ps$9UWYF16zQ;(c>md{F+LYrJ*sad_>1A^51>^2Ck{<+bBNdF{AR{y%@ONwOlb<68Ou{JjSLKYy=**N*F8{#N3(^NjM^{etotKIiLjuyN--a@@>Xk=TAzUOyjNUcZl68zbJ^YZi~6U6*A1v^gbSKR;VuyT1rNe<R*_HiZ4=$1*;zEtm17U5}L4u1Csi*CXY%>yh%>^(etR?>js*<HYya%-7LSiyQ~JKN{n@SNsYeN51-NWPBDe<UD#OGxwJ-a=e@m9_JVD&nWY~8ohYGc-~zs{#1ThzHePwK6ya=c{$!gYxc4C+^@EZy*5u%UYn;Wug%kx*T27A+ey6s{j=ru@1HHNfB$TGeV)0vr+EGTWoCcz`uF7BCyLj<Z@0XD|5AO4_$6m#ynfS~`^{TsrTCob`MeNnvRr(T4dS)=WH8-6@j;naco!X#@6{fiMgKeRN0is@N0is@N0is@N0is@kCfN%k0!X~K0u%M!vAO93;&;aueH2B@3q#i&wDMe&wDMe&wDMe&wDMe&wDMe&wDMe&wDMe&wJH+ob%q`tHxMf&P)DNez`uM?zP&!--8F9$~YMrE&fy|eqP2mBTD8!ZOh2@Ek>S$GGZsodeU`RV_&~fcrJVYqk&Gp@v4lg_D95@=*08hV4f!OxtSh2*6+hO^e2lKUqGJw3Prq;`=eJcaJ`M<^HQ*R{xiJ3lq2Q-?_!ay{Q9puM;u-s&z9H6v*q>iY<Yb=TVA`rPH2yIe?2`Y{@^EkpXePMF55fyw9J2V%5zq}$mOv|Z2mv@-ImwxyNzz&i;r;0e*E*U%)8p$SZnWpf33Chxt7=O(=D&xr+a@EuivLzUcXPbyndf<dF}k^&-qrqAJU$uvb_F0m60y_I@!P4eZA%N`+Cdk_w|<7zwe5vC0={(D>%EM_=|(&I2>>;j{m*fDDgeY^ZxM6I&qHwy;vlBZ~Q~qzZ;Sr;^l8`k>$1L(3IDnLo@pR!d`za&hq+mams7Y#VM~p7x$*<dih)*e~%KJxro1a^u~v=_vgIB-#>b~HIn;?yX9p0kK*`v3FUckteV|#smJ5qdnTzIr)%2EdJ09#{NQPoAp6!6WcfmcWt?n{<@I>eZWFJ~mz3A$OUi5WCFQmGlJeSoDZxAM--8d2iGTSH&!>Ge-52<CmOgRxgZE7?Ilo1?Ht_c5sV?*QWcTE_E?1Df{ye1e+Vha!TP?&t^U8hP!aMT4(Wy@2^?9k~_2-KY^c4Sdad{5bbxHQumj2>*9O}W_vndO2mv`P6@!GsvdHs1g%WL<u-tZ;jweJo5Emn%x=l^v#Y_N|9-=*|&zACX#eALM4l%b9b`S|kYKg2#bVyWB@)U3kCS1`*7Szf<?vAll&VtM`k#q!$yi}&@n;<e{py<@U%l;g;GU#7fvU#7fvU#7hNcbuG`vj5L>x$ydPxxr_h+3U~!T3&zdS9$IG3gx4Il<$upbm#L!@WL?hURM`xcdl>b{(fn+_+l01yqB)29PdLmZcJ>P7(I8e*PnB?y#Ht{dv$(;*Pnk@UVr}C^4U}I-v@j{WnSTJa#;LOxo&z-u08GW+Wb&?ZN8_x{&&*%eh{xe7ixL^?}-_2iw}(Qala*xmigFsNj6FQ%gXhv=tb^-|Ca3Hwdc~6*Pcr^0(r%ED$MN(r5`NoX;FVuV#mAk`u8D~T8aPrg<KbZUd88me~Av_wdd!JEWO3YMe=>IQMvh7{JwvNi*J8~m-B>`<NI&rbGDM>>gCI5hkw$Np9}WgzaQ!FSL?`gR}DU1?C?8xujh7b>M+{jyU*nQ2~@tf#NoBSn=Ak6Grk^qs-_+9@Y>(gl@H4Eu)YrX-p2BiGD-jMEI!@orT=~3b>;8-{J;Cf-<5feXUQQs?_HTC-uOtyXNL1<xxZI$5`VBPKd<4t@$^fF53K9WzRq3V@5Y!T;(e7nvM=wE=cOC|$X@^bh2{0%UnsBr{z7@}_ZP}*zrQeyWSiMP@3V}T%alW|Qx`nq8_(zG0e$IS9_80PTZ`9zw_<sJd^Pq#b>6`8+V4=5*M5iMZP!t}{`(ip>%V`oy!QJS|6dElzc?r3EoX6gPQ&s`&hWVM_dGs=U*B9KUVE-XdHp$!{RhO~7|Hz>if_#QX7sr$KB6-pzk!z7*!z7yJGRUE{gLw8?~jz%et)FA_WL8{wcj5pul@eWsQXfUuJ!!;3GXjaryV|+tSztq>>N37e3*O-`zg(MoO}0elkchSloYT34$Jb|@34XgYi+TQE2B&!8E*^Ph##4Qk5f;Nnlc}57%5)+U6}Iv@50_+B!0psX~*hFIZr-_6<?x~+`kl^E64SPIPn9X$@u$zEg#px8d<io?{<}+BMwy_&Cf|0`@^?7wimx&Q(pUBn|E`Mt&aBNcW}yUzmM|{pCJBGQh7e>$1MCkp?~``@#*`nw6{n3N4fbt=E*i!p66QN+Qz<kX+CdzW1?g}oV~92QEOygG$BT|YyCv=8RUBHKXZ!5gMZu-@e`8rbJO11N91!qJ|VutQ6B%s7n|4zbAKm(Y(E}Xp7>ERemYj%&c5V6`JGUnF$W!f)m84F(8+D=jpo(2+uIpT7c1NK+c5Fo8oeofE6(%&^~TNIZtn-<$T4Zps#Wa$wcnAybCk_~m~-k5S-#c~{vN}BV5;0FHn_Ci-p}4^d*pLV-NxruX+s&R)1AkOH}wnnZ(8u@wz$Xr78;mr2m4ODWIXrXDbL@vc~|_%8Qc$^4)u7R=7}vR{?U0pE<z7O{9J(Y{tBIVx#4^HbB&cB?XZteU;Plb(-&Pq{QZS;{XIH}zn@XwdykK6|LR}4-+ZoG;#)S|!s|btf!pJ4*-rdH`M$za_DlKPZ#s%Ey^+VQZ(tAEuE?q4`~4&H|G=+basS896aRb!KM&}gcT~<ZP1ictpW~wJ$3-W^4?nPumm4wX6lGxGb@64hbN>W`2DiuK{Zo9zBsq@Ggz@(S!P2kA58BNAA4oD^ws-4W@hLZOI|Ji;o|5(^-^sq`eVK3IKH3wVR{Ug{Zv=dGdHqJZjN+qa^Ks$3Gei8yT;kKn{f=*5B(LAo>kIK0r}6wVSm_n--_Uo5ciQ{YQ!70`9~b=O*iOgzc|J~_qx?F>E;+8}$#rVcX6|Qiz0~4oJd@`lLiuAIeo;?;els+=xzoQaFp}33*JY2xXOQnJ0x#yU556vg<-g_cwR{^V$2z=GkME<sP4_!}`HiEv{n<}B*VAOaJSP}@A-+kYUH0*BWW969;h%)@c7@)YJK*ro*G2N@u6^zF`<L_mPVjzO=lY|v$a966E3x;LUL!v4SKh8b)cjb7zuZ~2>+mtBzZl}}3jTY^xt`E@-mbv9q<gtPCm$4#?;-v7t{-stxMSRY-;7kT4&VBUw7*&QJq{n5!0iwGT~GY;Q@b3;9mbV+?_===i}7}awpNXG_^_2c9)d0VX?`A$2T$(NdmP?7R=(Fdu~mGzlDpZT&dKK)|6KW=TKN`!o^OPr<olgq>(1gkoaW=&b0yDehmSeO&-;f?50UTPD#eQL+>F;BER}Dq!>_~qw!kp{Ucfi|JMmpc%XMe!)h`|Xuf}p6%#v+~!(W!)7aH!!0}g-j2RYBolH)M6BROxkasDE&Kk)0I{SLqMxy;Y|{<h8GtMrq3X1Bbt4*$BejPo7&W&Q7E+>==UD6jR8uUhRriS@toTL1gzwHF^(o7?ZJ5b>qMuNW)8`|LVwhr?Hp@0kPT^Bi#a<PG?|7y79Hj}PDL9f|gj@>>5Wul0}eTL1VLKH8Jm{#9PvzshU-S9$yXZQ}T^Gra5ivd6WOhC!9m$ZT{AxBaIXNYekTO#DC1(6h|{*MFL!R9LC7|J#3?A=Oc{4adwnj0}P)ci8w4Uhe?MAP;~kmw=nN%-e3WVhyPyaBIw5M%!*yI`j1nFct9{EE|jEmf0Mw?;8H?8vZR7|9%6@+`#7$PcrM7S+$V4UBb1^de7v^$mfPI)pNY>Io@Nf<2jb4qV-t+X05L_-cRn8S+~tf=8__ghr0@n2R}yM0zU@-hWramnZzYbNw2fJq*A)X(PyQ0$>&q%v~fwi&Izu8_j>XEl;97Mjlmy+%OY!lYhXRZznh;CGV7&TIn38dUBXmJ@$XcRuv`dy1^FxZ3iu|{?GnBTet~=kOhudxt~fXwxEk_fa5Zovw2|7H3RxYT3S0u&2;2zoCH~p`+#k()Xx0PpQ{>NJs^l*D_XpsA4JqO@sEqI#@j48SvI2^@9GJ2mintV*vLcE&EtoPBiZ}(@Pi_ALMf}!~W$54E;x+LfXg{^_7ZkB!Yqx<SPLHerP7f}PtOqU)u8XV)t_v=M%mgk2&VZ!$Wx#7<mrL6AlabKpKVhFxJ^}v-eu$*^Jw(2Rr(=eWlQ)JGaaNaP4RBU)RV;TO?|TKljr;+88+;Xc7km|b3;7TD7Wgk@W|#0^U^;dwE4vcT1H@ir1F#p|7+Dou740Vu;n=%}BEF8i3BC@#gM0zL1O6LH$KKy~P5iD)vKshZa3y3Ta3yekm$c!v?OZ|p5}C!7aBd-{W0$fDI0v{ovOc&z)=&Hs#_<y*jol}BP3%G$7+(g)aRy{*SHjpUjj>r8W0$y~S#jpuPNNFIQ4uc!Q!Yj(bqg;Br*=!01g8eqMwSQH1~)RRA#I<TwOmrf@4F=%g5L*MKsEw5!g`3uneXjv)*KY^5M&$h5O8l~IJh@>5OOS-a<+|+;x*+~Fn!i`mwZ0uaT{O7>*L_(c<&#0|5ot#$n<XE@4@$x^uGIe|5fl{vpTux@2lqg$E+x@A3PZK1(xdsZjBrWZVmP!XMug-F~}|8G2kHbGB^l+io6GY3Qp&ic2QfmA)kS_fv+HG*(=C<@O{i`XI4+MdVnL4eZW+6@$WsrlTgGvQ2XKb<MlN#<s%gF12E+q6!CR1<wF$lPB7&G6!AQ?k=i~KMLZeH%mYsb4@LW_jr~x>Q*7;?f+F67d<5PD4k6!wL*Q4)hu~M>+sFgp+u*&($>6=<sc2hATc3BtKB4RnZU^p(oC=<b^$^oBL&wQP6!9VCbMPVX?^vcg-Zu{18TmQ5Gq?@1E4U3f92p4?2aiR51s)4Niu@IP6#NJB9k=iwU^;dwslDlu&%ty&(y`YKMcfwY1GfctL5=};0gp!p!Q;WP$fw{~@Dn5*S5NSoIE7o<Fu|2@t|0a!54sZ0EyTx=zk!c|pCM^|&yeZB9Whq=Bd37-gQud1_agUzDMPM=u}6Fx`3ijAyk?y<D~DUMj9WODSs$DAwIOxE5LX612QnA9v{@gSl@poW#-*|B$9O-v_sq(J_vZrVK;{PL#CozJvx2iA-$iBxQ)UJ?HS068TA~`jb)<b}Ry({V-yGQl+#K8%*%90k?`w;7x5K)+;WNk;HLI*y7hRG+x`e5S*C025*MMiDh*u%M1g`?GGixn!7xGK+F7O=`@nhr$@CJPLV-#^sw2|6c6WdS|+g20X(hgM?+g=vi*%nn4ebyBD0kSCg1Mnr6B=yB56!CiG8t{7XO5{xNO7JKY@d)H9@Cfi|<T~(Z@N`>0PDc?>!#bzobEd&tpSu?AT8qB6+PMqcu?zifZ5Qze=uhgGa>x(Bl(bAa<YVw-?2~e~{XyKttWFrG4ZuxM#3N80;Tm8}c0myj!!i@FTt{#><S_6sEZ+_9?QPZ<s7`Ri!|}Qk*lGju94t2s@9zyBiDl;CGv~lfKn?>(nl;0$v1Uy{Mj>Z_Dd&SHW4YPLDDZ4>G;%&T8ay3213Vo(9vKN94<3UY3!aP|YildHX=aT!Yn)lL%$kJP)9~8jd3Zh3tch4|lFiKo&qdAy&jn9KP6PXq(@^8!Mj^+cM#D`+jz&#_Yi5qa7G^a?HU|$g>!ewmk+;C7k>8<+lei^sfvJcyxTT0aZYkotZYkolZYkosSjS25UGNVm;;&J}r%=S3P{i$#!@%vqpP`6bqKI3eh&!N&S0gurSA#dAh<Drih4_Y9ztCs8C0~Q7h&#Kbi2EU{x`nBT2O#T$DeHp=fCr<92O{f%DQkfTg8QS0dm;0Kdx5(mQ-LY}b_sU{``l8*pCf+;Q+^AkB5vW9BF=;y4yGb@Bm06Wdx5El|3ML_gc|^+90{f(&gYgQZid_krXp^I{096D_8&17acd;)KjNWg^)ahE@>6gdq!;-q*b6RzBCdua4oCI@hl6{di2EXkg8PCaP{cz}#DkFC!Gpj(QN$f=?e2hW>)=k<_73Q$4p^oc((6v>LofQ+i*2*|yns7lUl3dSu7EpXpBBLWFMz(tgba5ljE!)NopAJpHI{m~6UG>^H71Fzu}a(v+1H&g&WZaYBft^pJL?!BwvHWQ>sTYUjzQvn$U*Le<CnNIvM0DF`q4V}iQC)yop_B|Yt34RTn}CcUII_cEk-T^F9t6}E&wkCFGVf^FTpyAx0<!xtewc+;GN)&@U+}&<Vx^r@CxKI@Cxu|<VNsDtdn?)Sv$<yh9cetUWI?(0uCUTg9G3g<R)+ocmr}5co)`Byx6?InQqn|<Vx@!@ImAT@Imk{<O=XE@IvHN@Ivqq<Tx;W7JYUkaws?w+zHtf+zH$k@2B;Aiu8d$1=mEj1-Hd}i5Ho*+pK_D5qLcf82|^c%zETk;Pv3;$erNj;3>!j;3;4~axmBr?ucv*?g(y!tO0HV4oCaOqwNvkCdhDbIF={gY}P)rHlm1EAvb|nfoCA+fGH=~cr;#jMvg|cf}{N0#`W-;vWtyd<2B_(8;`<k%9%Ef!fVRa;EmwT$S5$ie=XWeISV`oJQ_L1*8VYQFJ(J$D{wtzeQ-T+Yh-(HYw#%KSnw!t6mm8=3cMNZq;~H`?gQ@yuS0GIZ^nCx>DZZX$gx5>5<C>#6xkBo6kHR_)BCq0_kg#9_ahI2_k*`0cY(Kp=OGt@=YfYKhk%EJn<GC3HwV{6)&$o?n~CXo+-At}NBJfAEAUR_7Vu8+0_0rq0`OquFz{e-V`MXMV{i>*9dHeB6SRlg7mZv5js}lFMu10vTOgZ&n_!*9d$FI_qKIc9XM-unf@gupporTc+k@MIY5dkU=OKm6>%b>2DdHM#$x7fF;7^bh!JmK|Bg4Rr!F7<yz;(cBkV{>{X~0Wdl7+xa!0)4o&lr+t4PnaOV9GDR4b7@<R#s#Ra8__?WD;;{a4Mu5oC=%)nGBo({2nqF_&sn1WO;A}aBt)nVEP+cFGK!@M%fcw7TgO}4z4UXH!>$UH#j{qDL6g&9i#z%2b|I@uUQSuN{-9|P7Zb<Q-V|Cy~HnE(lKX{=Uu{7#LJN@z{|l!ksp95FB`%|!QY{X`yu;-DXW0{fh!}6fh&VcnDsu=gDeKlhb)dP1}+Y+imU>zg3qpsA|8Mu{vLT5OiA1JJzf(RLlFm%E5IwzUjY>H1tj(F1-vG9nN<S$A<_U-(!Ti+uZfG8`4V{(N&Y5^_z3b0_y~9zayfVzxCpW+n3DEc5xge;7De0_*$><g`>8LAxDv7ixDvROZC{o`5f?G505UuBeQ<VgCZq>!?fXn9;&;u;hRlJ?2hIU5ge(p&1TKlJ3N8t*h8zH{1|Ep~9y}0y2}PU-<A%mc9u)BmWB@z^d;)m^d;%Pgr124t*TflZV<;nvxG;*i3W~Tg@<T9X5pZR2DR;s+D}~p@$=y=KF)qoQ;F}m{G00`$7;s@^5ili<r^0wm{0)k@53(<~FUC+G6mdmlDR3!_n~JvaR1rm-2SuC_nH`)FoCcW*oC#wn4T?CeZJZIOMrK83GZL;-#0^ozpCEI9KLIyF76LZ{e}*gx{tVm!Sq<C)JP0`uJP5oLc?rA}d=W+bCz8hKpLk823*&YMI2ZUM<O%Rc;PS|LaCvY|B#qIUcuiafSr|-3O!J!B;6nKKD&RukN~kKBzf{3Eu81rJt_Ti8CI^RslObumCc|sur6}S;$iiSs8n1=$n)ob=xHqy7xDUo+ZxpdLuONO8na4<&hY)8#W;7D!EySsiX~1bP{!-b-C2@5_<_9T|$-ybWNsulu%^_*NNYCjs1Xsr#@)K}%a6=SvBV=Q6W6T#Dp@?fE)3_6!3nEU9r1_%t91*egtPycR<ojSsnkQP%ED^_{h<hQw08^GX66RyX<xs>qk-5M*!AX(Hz)8Ud(hYW_{|uxHT+sZ7zv!59N&W=>6C8&;42}aYKrRF?0Ov#I2j>HyG$c<M!jwJ0C&As3AA`Gt%OJzRWxyXI3xhud7ewX<7X;Iz<>}1I3(gEKh%9Pbz9`m5`H^k?AK~*UyV}~*744-wZfpN>+cpwYe^BPN^-o^(A7!+yKcms#lxJ=Ie-`_P@?YEjBBuRGMO@4+MO@r1Mf?`ao&~=JpF>82&w=Noh&{->;Jnx#4_*_WKoNICb_I7u-*rO~mqrnPfGi4b($MA3oaF!Y|FSXRe|{d&_WuWt`a7LJC$PVBxw$U&<ANp)lhOIcJYd{Bf!ay`$M_#q-w~b'

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
