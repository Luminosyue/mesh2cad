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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fcc3241662174fbbb146e6cf658293a9/part_009.stl', 'relative_path': 'fcc3241662174fbbb146e6cf658293a9/part_009.stl', 'source_sha256': '5bc6f95063d39086f1e5d9771860db113180ed7e67faf9ff3fca46c39aecda83', 'input_faces': 994, 'input_vertices': 527, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.36183759570121765, 0.010205959901213646, 0.45058006048202515], [-0.3556976318359375, 0.055173397064208984, 0.4666588008403778]]}
GEOMETRY_BASE85 = 'c$}r32ecFAx`rq8UX+ePP!Kqx^m<gH*uVzZP(U`l2}lvUZUpH?q*p`V1qA`6L+IE5DFO-@M5;6?R?wR-|MSnue3^UKUH9&@W_{nh&+k9aOeV=B8P;j~NY-pc9P?MsssHKu+NY{Jjx70{B2NE~efo86-?8tVJzsh);1r7I@@MO~$De+z>2m?6zw<`L4jucp?^Cfsu;N{v>Q$@~tk|hnpMHJX_H5IuPlt|@KiKxgz8zzE-!5%m>KI$ERJ%sqD#4nSs|4Q){vZGH#1x_}D(zn{^;o+F4P!Nud+A}R&K<YKbEjs7v9ca|xNba;^sV3-?|hx<o2NdwDxRmTDj&~-Ex($dIKR!qb^h^eH!}K`c%Hg?b$q+2$DWAip?&4zc}j)d^AoqLbGu!ehh|@1;5XjpcDz%!jM;9+==bC6AC>Xu2U>p+_j|jGCwGs-sWjg__4c*#Jec<;b39wtoe<9h_2PN7S!r{89zQ)laUPx9d2AkO^y31*@iw>PQ-3IF@>QQrNIaf4cSf(A9-rsS9G*ONdY&2a<JGCGcYO7SJddM0f6AaV&-rtk$wO)H#OIGxJ%1=(Uo2tvtL>He@l09p&S6jf*Yfd++qHS*k)xCSa%W)UDT&9^%`;ohNX)}ai<|RpObgHXqjP&c*gTk}Z<^nDo7?fhKZ|kvFOG?O6wcwv_47sN?s<5x$wP;Z4vpsxZuaD<_uM@^e%x-V?a7@*_fCwD-_qGT&(E#Q@qg@FbNq)CHRESZ9ueQ4<&Pcq<mrPZd(MX)Ma*_z8$2Yw-4@wBd8o#w(ed^E=ME+2&Z<wQc+NLF&&q}I$0ahosV9&2cRa^O=l1xx^Oye8cf8Hr$EB#rBU!JEjPLK1j^_A~hsu5uj{B^t=gCtJ?TP2kGtE4?ew_@@zQN2>ZsMrK<Lu_s>Wxo4o;D9ptvNaIdEt(4H#)xE)UrX(_-L^Kp4SJR+vmHRzuqLxcRacK`f$3id0ZOaH#pJ9<|(~;$9+PBa(c!G^XBs$2b+fnulK%>RAc^5PsGoY@EdP=^2q7o;~K{IW1=SyKlr>k{-=4}=wHZe_te8-&-qLq+Ii88uh-T1tSxBHhk_g8&kOrH<L2A1oAZ#@^OS5R4>ry|IdOiQr?wq7H!+VkDPZQgv?2a{56vBaI57|J+&nJvc-lPjUWKWN&(p}*{3btiVvuLQ$b&P}J+D_fx97Rd!<WmY`Hi=^9UtwO*KD`j^E2b)OAYYm*H(F6=Og6KghHOz`S8L#W_*<{<2>g-d2nO?S@GkuXMksX>iex{`;PCrES@|4>YK;qa&B`ThGxu8d|uc*ylqQ74;5@~-rpOTJec*-N%80Zu8E#JdUbsKaSYAAa40cPZE<m4;(pmYRR4R={zg)Bne7%IJUj7uVe^!Whm2=NH%}fKkkk7(s@#1X?fiu{r}>SyxgPIKuaglUzlrDLwwz{v*NmF#IseI>D_6~VIBb$9551OY&WCH0J$dk*YVpT0wdYjtJQsS-PJEuadC4p0@qJ*RXME(|ymR8?k52P$cX&AdxTM~l%af;;S!kYj2ZG-HTC#j@;(6lE^U$Vv9^T&EJJ0t!%slP8dwu5ZHS_%A^$a$Mn)77pbnkfkyx_dmxjnCRuJ_C4&Ijdu^Uxg)eDmmlC;jKS`9<G6-1|NMdGgIP=Xn8++aCwh6VD%;+w&@=`y$^wTxx|UkKQxRa~=kt&S9Pxn|?@7oJZ$&9-Bw{jmq#FZ*x07JT1G)r~ljg{-|>I{gK?cIws9;yv^PB#~-tK_BZ<bN4|Mz)JpSw?3LAQ_t~G*6UXaZj}Ju$WcZD@xg8(=EQ>jAD|&gaV^!{6$C9TWY?<aa-sXCI_{>nx`C#+lz$2c=H|2VO*N5?*$5-d}@v^x-uXLU?e&qrG@#OCLb3ggf!JhXon@1MkpXQf4XMgpcpDIt9U%lSC^AC6_!*3p&+j%0x9g{D}^qwawch3{@&}Y{?kBiO2%e!Ux<-x71GyLYaxt%}Q=I?Lg=fkdz-s7Nh_c)NJ%$S?uH{Ry%^K{<zcpmAn!+TzlhxW|$o>ynD#q;3Kr_%lMl=dm!^G)UM`D61uIWv97lk4%3nKxu6ZZ}kuobyNLp@Pq(B_3y;+v9BW)QNAKd{(+|9{p*pCr^2BoyoJz_sxR?H+VgV=Z+tT)W-At^Sd^Ba);xr=ds6MZ#S}Rbh@9v&9#3h$6C*Mu5*2S!c(_<-;eC^8T4qT?|yBcl<DjF>i$e$Pjc-U`&;PeY4aq{7YZ*-^mJbT%XkI{diGc6b{;n`ekQ|rJh>g88u`;~*Iwt_>pk*d^P2HI-0&mc-2EI)9_i6Jo~OLLz&F?P+dNz-;+>!GL+tZQ=l1#K=IbYz*Wnv8ee+PCHQs#5663Rfj(@&rlP8aU_qpf&UFX4>>%9AApBEiw`{qf<hg=^Acb;-vJbCI%jne&mY_5Im>zLkOH&^=`9QjJR@9`wp$1~J;s^|4n=lbzVxiRcJ-sXCI>fw2w=dXKwcwb98p5*#?+Urt%KHEI$eCGN}Z#U)nZ5h7)<VpVabw-^JHrM{CwMJ(8J-(sVb29xNN2h5d)9>-JdD8ix|5&D<zs-~UXPx)=B-h8s=KA<MYj0WTcl>RxkAJvyEzj#=N=}}4y+29!%k6cD`}*1SSL4%hkLUBa%|oNl#B+Nct8@2zRC1?ZdC%tpo!jetn@65|VZPt|HrMl~zWefgKhKml#nSxtE3&qtd3_ta&^M3#<DK7LKj``Gb$f8leBV6!dBnTF^?IcF?U&8<euchz)!(1*`R#eAb9)}zJpAM=-|f2j%GKU^ZeHMd-PXB&yrL%;n&Wfx9N#?DWwUpG=k4@dcj??-54guO>rr2Sn<pK&D!=<aUiN(<X}`$r>%Yz;-)-^k7kMaimUp}J?@ssgPa)U)>%JeU$JfdJgy(f$=lbzYy`xjQ-|@G(KK_y4x~Ka-zih6~2WMk%?{$>Q-Rmej57(bb=O?-L*PmN;uE*Q=$E4RQ^?v6*UcBz<=c&#0^E7qTakF3Q^}*&zuMg_;p!>M<zLw;3es_l7{@PscZ#46&_qtT&`uICtOJw@ZZ}X({XIte=KTrEUtIu<r>*rCZ+hEUizIz-hrf2${pOMweGJVfOo9ovlJ})GlSLAxXoJNOz_bXES&rH9^JxZSRdfx2Lg}&zlxjrA9#SK00zoEjH%<HZCykK+vc|qsy@9E_F^McOx{QC2PJHPt8pmX<oMVqV73p%&gOKz?{FC^t$Kigb?UeLLHeRlUteO}Oc((zHB7n0`T^McLw=LMZ>AN_eDDOdZeKQHK9A5Z;xLFfAM(yxc^{;KPLo$KSHuN&R%s?P;FPdaba=K^<s)%B<Aude@fuKo4(zw4u}|81_X|8<^pKCA10ohKcCb^WjNr2SRb|E`a^{@1xa&ieX4*y0y+9;(leI(NTUw7L4crgJ+!I`g9OSKqhj+`dn_x%$3E=kE6{$1j-kM}6;SbN#)a&h<R{dq17q>o=S0@BMUczpryW)%Si$Ip6!)Tz~IpbN#)ayIu9YtIplep?16KdqSP-{ng(S>RcaB{XL=UqrUIex%SlGE4rTQdqp=_-z(}|@0X*#SJZjZeyQ&jLsd*3EoJU+iLN>9$?bhF_IF90yTA8U@jkwKe*L|-)Azi|)%W%`*WcSmR-QA*Q~i#hbN6=;a{W7k&fV9ChtB$5_u5?l4&sdd+4KJ5UdO83y^bZ<znkdX{at478FQS~?@cz>zc;z#)$dI@caM+F)$dL2{Ob26oxAS~rA@9s@912QPx}2=<w@h!?{qqMAIEm5&Eu<n$JDud9~Zg)9aHCey#5{2=K6QcXxb@rUR_%1dA=m&Jnw9tLhjxdM6Q4T)w%nAWan4E|LWZR-J#A&&+&JEr%<_jKEHLsY*+n0u5<T$6>|OixX$%>{rkSo-OopMyXyCSox8sq<~i=Uu5*7kB-iJs&h<R{{)FhHW9EEN_u<%F-?w9PeSeP5^*l+>-y=Vo<D>37vbnzRD7qwS=2!P+*<9b3<qSDu_DkJArgQiED{_7Rn9kkrd#iqD=F#^7k|*5<*#Dq8{^~wPoxA6i&DDL3I(P5u$a=u!>i*1>Ci~5KrS2oOxxVkz%}agxKj!XnD6`MAUH5)emAl*RxYryXbsw_M^>}?Bvd&$f`n%2fpzqTr*Y{~hw(c_H)&1u>x5wG$VRiqx&fW1xzxEy<J6`2>d`hD)%=xeG^Vhk1d~B}n^VhjM{)KJkxaoh7K%T1pJwkBaR^P{0=kD_;vMKpIZ0h+}B11<^y|YAB$B`wsQ^e`iHsPO$NGN}{`u`J=uC@MG|3svI{aXLue<Cs`;5hSQODgqU`Zr?BTd`#hbsqgAvE?!NV=(FeitWpF$8f2SG4_jC|CM9-SB#N93(N_aUYM*u5$l@=Ox_&k;5Cp;>XY>1H6K17_AXxUz~6z*!})Re<FL1I{s(WVk26-hzQ+4&#$3lgD_rW=>|b--vQV?qi`M`$sm<ucYc6~)Y#?55!rz3=$N5qCqp){yzJ|BdM;R+#U*i2GWB$Q80GIkD`}ZVnS*Zbf@p_v~YEydgnhl=~lm2zsoAk3;7q2GdO<-^0{3qU0n=n?qKF9lW#$3bsZ}#bLnDotX3sC=Nta!afCbcoWc+G;(g1wE`tMFH0vvGbH{xIxyoPWn#>cfl`ukCnmXUv~C|AF@(FzK7(CS2+tj1{l`FsTpHi&q%$FzhwFUV*;?n}zd3@P}Zp;`|%lQXgWhcx}Ub8)JUQ`B%Jug>A?ALA<5@%Gd$1Wl(JCLQSO~8CyofN5iC_8e78fFiiT{v1I{#0ZjU7v1Jx~7EJn4v1JT=3{3iWW6OK+_h6%NN`<Gw-o<M&nbe8&;x!LG4>ky|On4@2G+v9~i(p~A7Qz?87T`4>J|8v<uPN{;urWAIginOMhu0D^sh`k`*ADm&nDl31ne;nY7q4sqlS@6z81Xs>KL?Y3Cu~0bIo6kwO`+e(`b6BOP?yq+*X;q5N&OeScvTM=F7<YL@v0p#TxxZC@v4Wn)Y|moRVQG09mYs6UNr)S*MObFs|s9d4SI1Bx24o7^x`!MZ>bsd;x!cSp|IQW8U!B%tBzN1cyCy3yxxPq2djtIF!(T79lR#PC&OyslmX9xRl#dLnbgne#cLUS8Eg_>AHzR}4aI9Ad?9QQUW?$1VA6jI8%Do~^$6Ky`cGNUz-=-$LN8ti$fO>k7q1=g9kBIyt%9$DEyHUGd<pDhyjH_k!xrMT6TTC+2(N?igRoC=Is`uii{N#bOzKbc;<X#T8+HJ%4e$-H9eAyQuYs+?Ya@IkYzba_;Co=J@j3!O0^5nxPw<~$2l4ujOzIEx;<XFD3w9W<weYpD-FPj9FNJNuYaM(YYz<!Dz`ucQ#Or(b_pm)U{Q&;~b_B0YWKzGN7q8FYpTWMvYcYH=Y!_Z1!9Rkn#p@IJC$Ob>Er&0Mt;1_Gd^7ADoW6j60s9`WnPgHk>BVa}d^l_qUW4I-VV~jkGW=!OV!VdHhrpyC0b5Q#g!K=}Hq(z_{R`YSQ$M5^uSR52AD|bnd*S!OX5!Tl-Vin%uY2J4zy{+Lf`?!)<8>eWKG+bv?uXwG8-ddU@CRTY;<d~%nbgnd#cP*ixYT9z;&sI_T<R`*@yZU*4r_?lRmX6t*%>Qd-#CU#y-F`$pE`z1{f1tg#O;3Sr}W}A9dD_V=*24??{t{-AHlBBr?W0zi^&(muHf}C{9{;loHO7VjJb-}47_K+zQJh{d=l(ayatm=9Y`-;@5A4RO~-2vd=4xfuQYfX>?6G9!so&k<24pO7WOe-L*PST88{7u4}{IYYXF(lF7)Cx5<U_(7_X`Dsj&C)nhl=~n}gRh_%v7=UZdcnU~}<$7yd46EKXhEU0~8@i7h!D^CvYMeg4=|2wn&#efii@4PFf<ecjk{AN)R;^c7-Db$E4{^aWx|VR&Jf^jTv|E_g0j0i3eIv%#|BRhCR@aeDE(3w{?YCtl6q&0vM_dItUstQua;;mu+9;dM9sZdi4^g76@$Fiyqc#bLSd>Odwng<iad!iU1j;`IUi1K3@7&4kZ{HN$Hhd>rf<yoSMt!KCj93(^l`y*O?`YDaqU${8@3)ExBUl{;X#)SUF<l{a9x)ZFyql|Nv()V%cKl`mkp)co|~l_y}h)O_^fl`CMl)I9X!ByJt4x#-2~DBe<!(~H+$y!XO#;<W|71(qAH74Q|Xym)PeZ-wQ@Yae_cEFWG`codcgr{nPBuv~ckNhbAgdhxmdzW_Um*J=1^*j~I&!cW4s;B^Lm2DSpPi|~uEt$6(f{|mMcr@!HU!=iZQ$YL_7dFaJUUU2@T=Aaj^tMIF^3wWJ_pM#yo>k9k|>?B@+EQU+H!dUUjnZ<Ca0eW!~x4)=4>BTD_-ck$Di&r+hv%#bnuix>OnvJpIbs6u=jJb;QA9()(JBM?2yrurZSn<k_cYekMa4LXz0a#AFa*;{ROD|qo;8|e#aQ+o<saY5+Ugz;X&zRqF{tfTnV3%>uinr9?7%N`6@y^Yd>^SAcJ1;ChUe^L9lll+6c>NMET<SG?@%kBWslU*R*D1VDG3HmC&*FU+b{^+T@Jlf1#p^o!IxH*B|G=eQrx&ju@s@gmUcA1=`&-yGytcu&!G6JOC4439XS}w<x5G~1wI9A8b{4N=@MEw`IGuo>fL+I{9GTQx>BXxwyfo}byo$h!z`n(+FuX8q8(u}>MPV!Px(R+0Y&%}Jz;A)=$LUu1t*~Qwb#hE5wJp7P4R;Ke+KFDg#yf^f9ZoM^A3BCh9ZxS_6CA^(en>A~BOJq}PM{aB&W_<yN6?FtxZOhSOdt2cTWSe<@wx}^dtjaLdJ_I5Y&c%e!k>kW$LlHhQ?L*5Y6x!#n_#`*x4=f=R03WC))}wdWKy%!i`NbC8(`(|ssXP7y9cjE@J6sF@u~^0340c=8{s#?p28~+JP)iPPTAqvVYlFwg-ohLFJAfK`C+;7Di1FYy8*Ad@Vc-XcvXN`fHlIa0K5RKCSF<LSz$Ng<iH)6^zCBj&<nApBK2naaj|7=!0@p!>D$Ma6nF|u`tq@*EW9jC`lGRJ9B~YnT9&cvV*MJ&@HLE)J{nsNIffsCNna5+;ZhGVR=l2tNxgwyyvE=?2KEA8t>CR-V{tACF9}P*`8&L&mSn7Wt-^a1V~*gw5AS`jH8|gZx72-%6|bjZQVY_H*C@P4!K8m4){1@<>*7_Myf~~C&Ij<8TAZ;fa2CH6jQI}dJ>+{}t8gxex70n16|bjYQVY<F*GRla!k)&f1-u1p6wbxq#bD3l{4L&6i!oNbmgBvgF$ZwojrVTY3Y-hzEp<0z#p@ZE)I#*)H5%{Hu&3~932zA-iE{~f30Mo958^Gg1Y^Z(CEhC;^DWMM@!kttj&mWrrS4^{cs&P`dL#Y&IFF`(j&<>BP2L(d8s}2*Qm~dde~-7+Qj8U^)p)OF%t4&@<GmlY66YK7mb#y@;?)KwwG6#@eSr4|u;=h<3vUa1ALk%E2y2b=4|q!rGFH6S;=PtJ-{X83@58XwIG4d&>S4x;S4WuC+vvq>Jl^ABZSd*<?*RJ%=L+x&u(mk=h_}=Vj1{l-c&}&74>%vg`xtC3&bQ$$^%!Htt1C?Eo%G^00q+U0j(By3cZQ9}xe~k*tOL%+@s?VNvGIGN@QyI%N1RXMeG;}F=R5J1dXll?^%6{K1A6hAiuY7lSG>BzyTc~nTn%0g)*0v1cuTFuSn=9~_a??1$N3`O7hw^c8{jSVB4fp?FHGuP^wV*kO5c}t@#;a|12z@sTJT!1?l}L9x71pU6|XILZ()q|mvFvFzlHS%xJfSc5@Y(2i=Xs&vo2mU$Y;R%;?)!06E+>^y70QN9yp)JTWVd#iq}@Ww=(8uoG;^j8MX!IyYZHKnX%&42PXC3^x`!Q?`g1pc)bXJ5jF$on(&&io;aVuTWU?liq~emH#6ou&cERO3v4US|HfPDFN_thUNEWk>BVab-cw+G@ahKd2AhU+Rd`j{i#VUcTWVFtiq}TGH!|i7&KK~$0NadneY~Y!V61p`fl0lCUc4saJrULmuTJnzuqilKhF6Al!}%w?rB-IFcx}LY17l9%d;;$iu#Gt1fw$BXj1{kTFsT*k#cLei<6vFzY7cJ@n}~CHczIYSoR8uywLD|RYaQO}81oa(QM{wD4LDcCTWXZC4Pwh9vE^}U3;Nq(^{J237mY0?;U!_VugrR7=92!7*itXHgs4sFZ-rH%hUn|Fty`&gB=jv<Z^2yB-^BJyQ|r^;3@b=2O<yLq6oVIo*}f?2MVU+bylnqAY8CnbtRnR``hsjLK+T)b*Jr&xb4h<E+b=>bNdE+^6150@lh{%fUKM8hGOU+jF6ncy{eMv_(&vNKqW+7%65Gm0&5_U-WW6ABNnZ+nKeZP91F*-a_tU=+TN=X~!)#xP^-9boeOLCcF|`tXH`oi*#`N7|%hT|uVYY9=dK2c7{<+xlF#KVd^e@7?Q=g{q6<d13d%|qrp7r+3CH>2>r60T>O#1$?UeuoS@5Gk3;cvri{}$_SF_-jpVoPlv|JpqERoQ+W_NNY66Sm(P-Wq26maMmAF6sNmmOk)4u-0t9FZ1;!YmeKT@Hb($e}nZmm`nP9$Ci5?^Zb)ql)g5s47C`&Y`+z}70mYSSZ~K%()W%nFTr1ewPO3dnXfllOWa<EzYeqgYplP<T+%-nTOM-E>z~xh^!LJwQcKdy_Itp4z-<3K>(4Wn^lf6xqwq&zJ=lI5=4(UN4!2j~uflBq3hS>hm-Ju7p2%OumIc)Gg#K&RrKZt0eI$^jNY?-E|9as+e{!$7<M}^g(Ep|PcKpQu^0peze{Rli`bc(popG|n{ue*^ZDsAh0I~eTz5'

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
