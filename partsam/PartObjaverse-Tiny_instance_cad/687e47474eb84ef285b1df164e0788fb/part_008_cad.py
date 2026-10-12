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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/687e47474eb84ef285b1df164e0788fb/part_008.stl', 'relative_path': '687e47474eb84ef285b1df164e0788fb/part_008.stl', 'source_sha256': 'b297373ca2f147a7a8922f0285cd8aaa7198a367c8bf44a3ac1115e773151872', 'input_faces': 1056, 'input_vertices': 589, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.044408611953258514, 0.07568427920341492, 0.06793873012065887], [0.09554284065961838, 0.29306358098983765, 0.2672170102596283]]}
GEOMETRY_BASE85 = 'c$}r32T)W=-|i0vR8&O7fC`Qo11JVCGe*p!nB$<LvMPvRPRFdPVh$+kh&e}sVi*h{m{8WR0y<_47*W@Jr~7%_ouTfny7hfq^{?l59@{>BI-Tx5<NNw_$eqVQ!GGlyU9-`)v7U+|qLAXCjQ1ZK8Zg8^#4T{lBrC;E`r^Oey0UYRPCk9Cl<~@xszd!lhK#M+NK>`Rum)9YYN`$k8XG#+FK|%M*rEQyZ{s&A#NXtHjPM)dZ@PA=-=JYlP2FlWHPbZz!~bkdMKBycx#Nr|OGL^EFO%qQbh#kZ7?oT4>dXQs#kJNycY;vOc-?lHK6%n{ajmqkg!B`~Z<Fai9hCVP$NW4e^YinOzVf`<Df#yof0X&?>*Rs|%1h?2DRbw%On?8wR_UMgK|X)}ktpx~BUAe7*7>pW@AvSO_f>jbM0&^T@GEzh`RF@p;b(-z$#ie7%X|!N=SRwX?#9N*d@Cj4zV3eTtu*qvbeeid|Fho~>8FOtavGk8UzC4dwk!Om`(-)x4)4y&@>bBmAK?;f{=Awk=k&5Xb!JIlX*1{?^6MadwbJEiSswS{vOL<irIEgH8Cg!<)dMmgL;BRs((e;0%c;5hBuVPnHt_pL%JQi13MR|)<nFae=D+>~>S3~{^fgmzz;{@JdK+2#vP>Uc9KQd2nZI$`_e(PU!(AIK(!0%+_tiIEAbrK<E6Q0mMy6LiuSLl8gPY6eQtk!H@*Ds5fPeUqOt10Vb4B`fOGsadpDOd$rRk-wO}f89`k@!`Ts!l~avCa}f&Zqm%ty(){E~&g(?$CFxq&htP3!{r&G$-QE!b9;-_S06y(~`=_h^fJe)|sN;QNk~`RKMzgr6CR`uXcR%HPvd`pWQ)Z1)SYKj>^eg-hQrTIQqHd4CS$BLu$f4zzn<DOn!%<CAqL=gKJg_d^!T{PkyzYvq0Iy``@$8G>>?Ke0yoKmSI0*B7#X8czgDU+Lv0^EZ4dhyL@aH~i6ukIDOW+=2X8Dp}2Bz37fgUo+LhSL%;||1tZjg<m#C`r7LDDHeWEqV$yl%`RE^KHl=anq?<0TKEmtNZ*(})gmADLS8&C=bwN5qZRSI#Y<ne@WTd4U)_DfGN1W*QUCp{Ez&D&cio(k=PZ2dj<TN^?qyj%*Ns$+U*C7}7WuCpDEosUAj<N-dn4qyGklG(NU!*BmcE+N(=z`-nR1@gzRG>g!uPa2gYg()QBGB#*C5l|Jh*J(&r6cN8gwwpBA-lKSq{~00LJ4Fw+ZsP?=@Nf%KRkEZ=uU3N&l-4=J`WgWI2uB;^3#Z#JH<`SNdApVw2_dvkmAc0}5O-_tm5w(${QUg??2l9_eGw!#`dq#lpYUU$&#s_JZ^^F|Ux%t_>(>P>A#mi7ltd>nnrMuljeE{Y^V00sfiksOKY1k^h{~snV~wN#?J2D4t;9zxs^+GwT)dUwH}st&?b%Mk%uYD_y=%ld3C*{u%ZQ^{^!WO!@a;XUO{3B>f@tSHFFhzGA&kwxhQ9e%W5S)stt*Kd%xb`<21X74yc!IQYR$QT}&(WxMGd;%Ce2GAq&UA7e59-?=4yW$>2MDA!KePqYVG&XL!bC&+%TKRyrd<ylSVqkS8opYJ#%%dZZ%S|HP>EJ6Lh&XD~<Tcf1()koE3f6zLGqCYeagumn@+Ogb^s}_FC-5A%Ey36!Bt2yw!2cw?1Z$|rG2*-WvWypN=L7%Ug`|8yfm}mIDFx-3#f69BAkMh-kd_Heli1s;&``#Ib_tD8?@W-M)4dv|cyp6y8DRo+YnUA5xHMHX|yG1hn@ouu+4Ra^sxm?_rNPko{*^atuezF}kYc*jqpAKcB(GTs>?rBq(O0Csh*0Zt95cDhS=F3o?%CbJy2p9Oiv*1Vk!2CSI8RhvJ3IFx1DD(Q%r0<76t|I2Q4<n_ooQ{Pb*hJ=|Ex8rrab@M@(zm@O-=~J*%cXB<*hc#56FZErn9Qpdz9vPkf7D^G@ji9k1^<VKOs_w+7w^ZYRQN-dq5pRY#rkK`bNCY)qMmP#PciqE$5B{U<numjk>08U=CR7lWItE>Wg~s>;}~}x?&E#8P`g6<!>Y^n)n;Fj<Hc}mru5Z}tEittt7ZS!4BC(McgM-`qQ9Mnb<V!m@VEDszP8dSjF)<)SIWQtF&)pF^@mJvyxR!=uc<NS{Yu~SqV$z}PvvtND@4nBR_=dTX<iT71-sDC+f`pB{mH}ezFt-w{h_c{`iedp?cU@k-V1NqBmJ7=Xs?T2(l_>*iS#bjWqTR(_mu6TI<G}~b(m~-jm;O?zG{r)YMK7+I*gYHJ>Ktu%cZZDT!itJRU*aQSMu&g`Hwb6|M`3pej3)*`cI2c&bS-!&v+nxu@@Le%e>Y|zv+9l%lbdBS@_Aj<+#(&?TK~H*!J*qu3NhIkiOda73%qQWz?tRNTkoP{!zEAvGBElI<!mM803?49aZft(%Ub^`nk;|yk`qtLHeghqs;3~>r`p2Ot<$7-kUE+Nni8JZ7urAP`r1x2H`#8HU;Uqe%5v`g?cD559xEP_tf{xkbZGH)LX|RxNr0h_?v2AJyUJ2%tsyVyiWSJLeW3#TH$%?)RVqC;0N-rR3GJ;F%JIR6<mk!L;0WYMLs#!r8?h-NPjE=^IlRi@+tKX((k{F_ubo2IevBeis91lxfS*AS_S=KXhZn@o=M;MR|fi_OBd<qTyJZ$h9dp_Etr?Q9%El~EeL*&b@gvw4gZCCc+7a2ziwMP{2c3l&4~BNC&#+|Uq8owMEA~Vy}Zt`Ur^RIlYY*9f!cHs{1zTD=JjuUGz0mJaWmj~r^$Y+9kmzfbL@BY*|(7X+Xu|&6FXx5JpKy4_hgL6bWh|zHP;6D_jB%#tli+}*njE9427R_-&A6*^mFdx)Vu4Ee*ZB!esw<2Fn@+RMVR;V-}}Vhe$M@-c549q9Q#wl>Pzr*>?<|SpW)}&=Ngq<8|C%#EIFU6$&PrBjBK#cB7g2@m9F2BKF2;<e_+)n>F3yYs~JZ4D>AXZAGiwrc2)1q^3N|F!g@O););d8E=KyAqqQ&(j~^m^CHpYyEz=hLwof4Z73p}NY8D{>Ut!2+QDs@b>ePi8cMDD+{Z6AyZ`e=(@9_>PNWcFe){WkS(Y|(1k-o`UoL_vlxoYmK=d;kC{ClDN<s9`gea>@<vDM)3kHd3CUdDOC&Q|b?6vn={#%%bd+Dkv@xyNr`c^)pysr#6Y@pa}8_zR23bf$GT%AY+KzS9ltkG{pAKTkUhKRF(LVpaHqPQq6*q_5n(fc#V9;paG?`PWY@gL9=YU!-rI2>;Po%x@jaU>-hl8GdFRJWq5w=BtV~@Vx!{N?-jw|95lVBCm6t7wP9WgrDQwNeyTvePy~T@2hbML;925kv_+Hl&=2{q>rqL^EZPZ&X*RwhkyGSo-3;1WedM}HqOPozDr-#4T_YS<9y7R`6v7w=V_WttKn;6F)tM=g8Ao<XYe0Bl;u+lQCLT%y^_ANue&_gQ#mjF>u1f9zJc?<QtJo&+cB6YcUM6<Z#r$2zUqu}_^rVD!Nm=JW;E(;u{-9I@Ve4hZ6?b6wbm|pzfWm~^f}HCl?sF4+jPRZ@zC)E3qR_x^fh-2pxws>!S8wk>(ROyc;5Tlao>v7<bCzm#=-a5i}bbUV4rfyh<;l)8vgJn*x$uXljT(ACBV;d{;9@2fM24m>_56Mt1(_SzQTQToTD0S-y?mFb65S_@9<-q$ouN<ce-NX+nq$ceOZWceIwsC>E}4tH7x54KgT(+VP~lHbDkUj>qn>Ke0kg&)Q@)p@@d;i=A+E+i2g9`0esHSsz*W8f66=L^VtUPi78Lf&zpZn`aM1Iz6()N{=Kf-rC+5N){BGd<Gr?hAp9KX-pc#U(pT+E<9)WG5ca1pQ{WFBg7^1;C-TpgCssS8pW|Fz+rVD>%D@F^kN1&ye--Ntf5Q_wUi2HDNZ&BW7x@&rkN3-9C*<EQ0O>=YVO$igh4*QVQ1}mqV7yP<hxJm#B>4W<Fi-yKh;`=lIq<7ZLit{$BK`9d@N;}GP<L4El>WABr_q1bqrFPzlfLSS_k`w$2l{QN3h;+~M}0mVf_e33C-@of<@-;2`x)BhM>6vN*^uMw2cGw=5q|el_)ai281ujgt6kFHbqVJeL8<WnwuaC1H{+Or81Ea)!oU4XmQ%<2)U;{}e{~qne*&8zAFDa=ZzSTrX{%7qu?wZI9xH(T?YtLwzFphkU&)1faNmmc@R?-fb1+%<2W3lr^v^9f;rmX+KI&OPtk-56;s1Pse0ct2@ctxygRw65|LvAw{0%C*Ti$oHPL@+stq0oonYZ+n)Dn2VFLspes~r=9^taq`Uh{Mv##6vHq)%Ib@mV}2$=p}l7r}T)3PX8ZPau8x3!FPBr|_OH@CoT{Kg#~8wD^jA`djajf3I#UoOg^UjQwj!P58+;2hqDG$aXM3c9*^qSP1K)AI`G;x<%dKrwm3tjOilFuOB@Ce%J)mLlG;CuVG>EgS~LyGhx`roY(}vQ99c9@g(%Od`9VOZG({h=^^x^K5vn}X*W5J)W@Sy9;N7B>CgOuahnJ0_TRqRqBz!PW9!R(tzm~d{L()1zUsEqvj1xIgQaiiTOIXqzO<|dHD&?w*DSz$$go_dH-xW*|MMN*Ti(r*E&PG#H|nmX7^hbc;Jz`7u<xBdAN{|=8Ke)!IjmuUg8ppGyHBQHyBPC8*}bSwpMuiYX75A)dE<}$T)dt14Re!F{spCEy=k_Uk-k#p9QLK{w#)Htn9&RQ*HiI+{N#Dj+*cxc<NWdVeA!R*euLr9|Bm(R?lhbiUS0>^>n+yFn<vYBlpg2d+gfuSxF6-;`4{fn3-5c)g`1c^9Ph%9sf7D=O~8Ek?J<1k0kZr$r(~>KGv2^&r^C9s$sT;~sIBam_nXoU=S#&-;J&dnq_5t0liw#aZ>C{ASf~loXDq@wWZmn@=Du1k8~4rI4*Q0bu1G)Hfc<~_Se(b_9S#3QZJEDr*;uU0o=t%7R2}Q~DbZ;Ey-TET2s(y-UiCiudD)drKOOyY`2blS<-snLr%^eXzxIG9+I`a-q|aK9`uwO*H22kdudx5Q^Htv8SmYzp_vnZBSD{pVk7#XoK>E9mVt!s<9pf^(IQ*Tx@t)&;O<T2$^tCRS$FzmFVm{GyMEXv1G0&bTeMI`pyGmazISb`^-x=%w#8L2lo8UQ{bwd8TCm^3fb>%oR*6WY)^)VLry^ik_%Gxie|LKpB{+%!CZ9)Njm#LKZAnGj+_qBg^(%jc}sfhY)UIy#XH8x0Ze@~7JU0O$c$Fa7PzEX4}zHj;2qW|>Oz#mc*^UR2CT%T8#z9DssOmEn<0qc6-u1LSH6wY1W{ld6A-xK#;=!|}K<rmhc_4~um49EO%{{i~Rmtgoo4>A8A(V+abmLPv0Z>&RBoJV`=SHQm*hVmS<M*n%03O}?l#%<&>e3u{aH~iA;u-=N>e%Qj_5P);5QTMQ3xONZaxwjwdxzi7^Zq4%*>A&npzTdcBORzsA{o_|<ztr9so@n70PnY9boB0XrM8}Hom;8hF<^El{QCa%x&UfgCFACs1zOo1W87(kB+bltQu4xQE&kyv^csu#$x_r%%|8#sm&|dD3@q4Bv{E?q9URp23dt+i7_)BkNfBM57=LwOWrLTRq3iW)WhRjDP)*bgvUXFIMFPUWFE3L3jdSXm8_my#ZZpizte<=H#dZ{P;u%%cBOsbJ&;orbMP;>v3EU&&vf9V@M3&?y7MHXV6v)>Q*RSU{;s(fGQ+6Ez?o;-hlI^m+ZuU6@d{x-`U=SdHzB7NczypO#uqaSsj1%IAD_Tj0h2aU%P<nt5X`3!+WWxvub+=%o?eqnxY@EYf)UnAkqd4qls8iW1U=~(!qccFhiYb?vJuXP&!={4AoIXprC>XQJ!R3ki3!AjU46-|PFVH(!w`l3nZzQHR4{h`+;e1HCsiuQfkN!F*%_9xEm_T7S?T?OeQMq}UOly31{ioOcgd%vE-Kj4LZ)}CBR7XG!vDCe4KiRQjx!%*}q>ri};jeX93GF|${9>rumYu9I^o^SU>yJxP!IeoX!@W(F3dNTVR&LIZc$aYZLqTguT7h!)|K?A=|GRFDh!bukX23O3_Pe)p$S8L-uNPk#^bKSHGNS`nY=Xhr~U|u@q3P0Z?%n#j)U$F3N7sYo(+h}=h?9~|l<Tlus9?ysOvRyOykK<9Eb(=AclC&sK+7ek0ni9QnzT2n`=Ciil@xI=281wnw4#?-`4y>d4C&!rkYItYV=f{rtp8S_D@;UA=edVut_+Ak`5c#x!iFQe|L%SP?!Qbj7=QqRJ?|9y>qu_r^#6B&d_IV3`)&a}|Unk-_bMaa5ljq{SdCMWu!tb?Orq|vbjdP=`b5Q=i=WtG#ryb_!@~fq<waUOea4SOgE8U9q$fsWmJlCXp`2N#=Bl1~S5$8U|_n{qg>)9W=V*j?w8~y8KB>ZbPah@JlFu}rK<A{FZ>xy%uB1hqe9Kt-}nt*buvAAzwoGg!?{aN22j`cGX?~f48c?-YdB8=035%?~#+kkvNCgFMC=EuC6dJ*Z*9>uw?qd(SBi!Pyl>|HP~b!!o0?yJcs(XXnmMZ14bK|ap-or>DsMXrBzTi@}y`r|yI@~8xJ-_Xhx`PA!#?@0Z!k^j<9IInPQj`PmTU*LaPjCnQvAH2t#{(^r6-y`)0y5PA!S;_mW{mWy18F>Ti{X2!EZ%{X)p9G)9{7@L>Rf3yhKbC$G<xi-N^h@HAexni3JKYuemtKtbY556Q*ElwY|6nuTa~<L?nEOievFIoB$Km%5$J!!&8or~e<(lHTGJJ5~K6^1vSx()=f$*O<LI3O=jPI+p{f@9-VLhMzD8bxU`?bJ1&rCn`&&XlOr!m&;YQ+Sk>l=W4xSrHs3Pr!V6exXdb~AZj_2?AryFZRcJ|4p`Z`eMS^`jX!75Q{6jeW>;FO2uwGjSj5o#>wiN7Vn)IY>Wo71kTwToWz)op~@Xl*KudF?cER$*@8FdridrIxQ0EIX@U0T*0}%$9DLIA9A0Zg>_EzSokYvpgx<YqCStDg5U8W*5!{Y<Ncd{f%)_Ie9ohB&S8BO<=N(e{u8Ogc}A^U@Z0S|eZI#zy{6AS)Y}UD4ot^!q&j6I{|`Iy-ux>N>-?}U@K5x??{&C7SG>Q&KX4lJ%&L|+2aUDD@8m+ZVSm(p70UCV0P^cG9_Q2t@}V5(9N-6AVV!#a!8vnZX|AH(ZCug+>y?Jzsyz0&x=Sce$;!y5oEGOWFL8dR`BDq%CuZY&!@#omUT~^4{2C+CKl6K|UB<P=K09C}_8oz%qRf3m)^qsFub@1=e3}0~es9`@_Oj~<e_lU}_msA50P@L=^@%YdMP3_Q2c!J_o}y#B8`sT*?^_$|fG3A|UbP<i^E^b;s3Z1wUXe(@ColGop65=R`-UZr(f_Bn#re$VZAkBO1@HIVTQP5Th(iARd*SyG2Uoy9c>;dp87R*;FO;W2D*WY3ux<<*j^As&y9vKrYwU+7<x8;echAE*TsJb>!asKx^Xko__&z@v=O60nu^89m><t$F^6oeX9Fc+b#*a+oGp;n&&r3JscNS4EQ4c(K(v2F1aX0!k^6Bsv=bV><W&hON|A2f7?!x(PsZAJn@ju~jal`s#-zxl$W|9?tzw+k}^n-nwsE4iCC#mlvu@2$<_OIUp-(QXW9>$yd%JaNfZ|uPNqRycR(tDr6{&e<Yl>c&3q<>We=N<iCpSAD{4@CM%yytXt9gvR^=Un;^9{3KdsQ`cP9_-UwhoZjPRfpfGCBA=5Uxsz>V^99hQipL7UIghQ8o{r<75U_Se$3q02E60G81=5qXpKMrSr6&YpFn*&`XZl-c~Q@Qq+uO?Oo#G3yoL9Bp;D*JeI?jkK9}nJ5c@&*N$^+H#(wry2<m6cboigT^LHH$&@OWp!go7``K3SVQ}Zzl_kB?t^P$%+ykFX)e<^=I!TedcC9cQrgx;Hm_C08W-**&>LO%C`vF=(>2>oIjo?8vRfcMc0<${IZAsOcvvtQvn+~XATKhhZUfZGB5UaZtb{;o6*-zDoioVW0+9>M!P?v$*5-NGx#|K&@(x59&PzBuv@{GIsjVCer4{baQf`FxAPdeNyD_Sx1?;n(1PV{LQHtNIUY7e_pA<?vVwfA~hs&(8L;9SlXkz;Bv}elh{=XPosDeygE4$9y$hwu9nd0Ke<{+z981b4#M1cssy9;*0MSzuIv>SOV|8M%ytD=lg|z80(06dgC~Y{;wZX7U?%V#ri7V9p&#<75Q`hpz%+QH}};=ei)B~W@G$j)q}q;74vncHm5B7YCIpYyN-S84o{S4{8H3ICi<&pK?|fWlZO78)Cljf3O?{#uEF~15yqP)tsCBB`KsW#GDc#&t?YsFm)(qUWcM8PpQj)E5(lv_=6*!oJOcU0eaCpP87H4Z={*vD+3G0g0KSjkPeeYhb+BKs#_vZoWoM#1Swk>ygcy*%YXtJqH<$fN(|rN%Gi4ipU+af)`yvy+JF2@Aez5?2R}DCXdV7W6^BKIDzg2DQv&vsU`T}2Y9&zFe+9h`ie16w6Tzq-P+*gL;_u}fCP8bhQ?!xE3Rb7DfoTkVl<TES^^LADj><86M_-h;BeR()P=J|J7$meG~eg{8h?HLPyG=4{}xl<MQP5lSYwYezvM|D@A-l`P9?}rx6#e3haGx}|Q2l(;5vHl(#jQiFp3;*ditQ%9mMOpZZ3ZtL&!}~^aupa-t!7$86Hy2|4rD+5|sx{i{?j-ykC!{^{86SXgHzXYUtQwv0o-b3F->0~*DBK(Q@Z4BwvJ~y*sY5=02jG0E=y&)N@m=fpzD!$t=n->Y`MwzE)ho659rv6qNS|E_?Gl7_o!<E%e2-7qADzcKUSH@6_6M66q5i96qdvQN;r!|2OYECUxZr&^ZX*0N{H{^&%lX}H3VfTlSV#SS-#wcKU(*uh`I?1&mhk}mYD4i{y|9kdy~~T=@o4e=SZVbfeySb(n)7hJcXSBm$3SO{*L<6BuK4yX_mAU{er9p}p5TLZl$VdizxrGC{P{mh9TS?Ofa0JG^E3M=fAS9$<zM~3|C7IfdjDVl<j=i!eUJa$zxlJNXevWtQxstc&P~lr&P}$W<{=9$M7AOqpgNEXkc&~vl8cc`P%DsymLZoQ7pImc3w0(JCzqm@Czm2SQLB)h$Qo*Ove2qz4Y@Mag<P5JNUcT|T8ZpPwxbpy+mZ8AbCdIv6{;24igow<Kf%`2Vq|NwJ+%b61nb3~T8eB>E=hGFmn4^?YRDQsb2*0KqEtt+BcH7(L$D1sKiP(yi>i<nK0_{s;DS_pvOUXJkRjNXT8><f_qL_lkZsBNsJY0wn3v#Vrnq5>hYZ1gnPM090QCm>0C@*Pa5(iCIh;Js6#l08!xWQDv4A>*`UhF)DDn*Qbm}<rbn-mvG4ece9Q7eNj{Jrp_%-z}@@sOc*)yk7w~<rHm#ACFm&g|wf{#!al8=xVQOA-OktdiUz!W1*(T^dxH+3|*H@QD`0=YkVAayKxAh{<)@DS=k@(^+;bqje5pEHypcnozHc?>y(dVm~49#7pt9#0Nr2o9!(lY_~FspH5(N0A4U{iuJC{m6r;{^UXAUZ&_l9ZK~l4<%2eP9jev&sP5HyR#XBmoWsdVF(VR&L9h&P7Wh4rp_ZTCU2z1kvEdBQ{RxUlfP15lfRPRQd7x7FOlDpGpQHIndCbR!Dp#Q$Y;r$sEf#($jhk{$U;Yxmy_pHN0R50RcZiPB~LTO3R5gG#VqO^@+|UX>NN6X@-S)uc^J75wI8_;*_$D_HMKXnHMu3VKe;8j6?GuF6}c_7C%G+I%Mje2I)vPw+?^Uq7CMI9o$NymA^VWKQpc0Kl6|RxWM6V;hTv}0U~)Hd7wTZLP(N}Pa!2YQaz}DIYA<p-a&zUs@!6aqxP>V?PzO+ZkOz=QP=}I7kf%^5lBba8QfHIrl2=iek%g`yuOe?|2#%nJk%cZMN01|_8_AL6qtxr<qvQwFujB{hTvpJxWTBa45rRL{yF>m=e!&o&LOn}PA@8GZBJU&XsmsYi=acp1wN#b7mb{cYjVyEyc`11{bqRSjc|COnc|UbKbp?4lc^yOWpVV38Kgm<6lgU%b!>Pl_!^wTAeaL;uZK&SlHsrbt!L_Na$+gL@)Rtsda!qP0a!qm#YFly*vKv)Pb|cqf2zIBoC%cpDQ@fLe`jG3BJ*i#Ep5%s9Uvfio6KZF26S5aWa5HK*ax-#MY8SH5j^w7~#?*G?#^grS=Hy1?2Gkbh24oNAzd6N&A-JA`t*FpW)DGlMWF2(?Sw{|{jvxn-XHut-XOdS^=aN^FH&9oRg>EKqAn#T%7KHAlZYB$jAnzp~qDGPrk)x?c$wD8HqscF+Vt#o^{Y+nk;M>#}WT7eK+vF(fK5`U!Csj`tx|Y0?yp_6?EOa$_D|rufJ^A;1v4<h}Fm*3^FYDqkLvRc=njFpNjG^8p-{v#KFa#f@?j-MI`3_R|koWL@g4dbqbE_$KQ;(8&lM|__<V5lV>KpO{@^@<9T;T8ILJYwrO`)L{qvj<SBmd;z6M6k)2u`D>lGDiX)T88h@?q*$@?r9JhT!$ob>#KrWu}-;ol9Luo=aXu-A!IaK2A*}A19|%ACMogj?x)||DlTd`iIwoOR)}1l1q`Rn$>AlhTt01V&ocRXR4@EXI=~b#t{5BHI4i?`7|}29M3vE%@Dkgx}Cg_ypg(|ypg<;x{Un0-d8dNs|>-T8G^@9=aR>eCs0?BCy*nk$H@`oE7WvyI_v!kL-1FssQ0hD7F?NaQI%YoT#s6VT#wv<>P&7xE>9J0P@dO<e=r2!q5e(2Lyo1MCZA@#$1()(pl&4ZAg`vbB(G#$uVx6I!w~!jbu{@8au4blau2dEbpqL!+>aVT?nj<Yy+WQ%K1uybK1t4^ih9rDwcuK8i+bc*WG%G;Sxat7El+MqcB6_maO1V$Y_`iCayI!gHI{styo<Vnyo<b?x|+P2b-kP+c$z7OQ-i5<$aB~R!3@D&sXfSD$zD`nvKP5AwI8`Lxg~Wrxg~ih^(1*Hc@H&<yodaWD%#)^uLU<@yJ*Qx$gQX?$*st3sBYvo<hoSR26cHY_!ZmbGWiwx40RXz40#20Ie9tjdIdx9472u_!4Mo`igDCF)Zyel<lfX^axmMbH$!l9su#IAxfZoCxfZ!5wI#VG*^N4s>_+ZP-9zq7UPApuUP69E6>al~*Mhy+UaiPp<hIl{<hJDY)Vk#M<fc^7Hcfdg_$Axx4EZHFhPr~hf^87P5PX0dLOwt~Xx2^#8G@r3f+sNq_oDV8_ae8W_9pjcJGEm7u0yRwu0yUstx2vxcBZ<Koyi(%XR?OejJkx}j69zDh&-PBkSf~gA+H6uVB57Nw;;EpwkNkEcceBYcO*BXigs$oYr&apyBKl|+ar@9_!;#e`5E~IHJbc_{Fxy*fjWsSG>n`;zDC_bzD7P~3U^cVHAOe-JaRYkM26sP)cxdb<P?VB8>Yyho}=z3pCfOe&Lhv`y#=qK4yN`c4<^^6x|2&%OHtj)rN}M}!QRwvWN)%Rbt2iHyqLO;yqJ87nnFHBzRwW+gnEPgg#6a5j@~i^-=&@--zCRUH;{kVQ5-|?UWVXB48eZX!DK&jLux(p?|N*=5M108KNRS9YDuyP!M~`b$RY$6q31#_LaxFP+=}W=ZbjBn{mDA=6zXE~6mlf>6giT7iF%)WiTsfvICn1S6S4@wg{g1JA_TvqcbEK*e3cqUj$?ZW-btNL-AkTN9zk71Uc`19!4RyaHY97wrK!cqrO7{)|JqM*2K6!Z2l)rv@-aj3UFt9LUGhCsJfVK0{vrz%ZTyYbg6-MvRmk>a4{9s22f060N7k{8`!fX3qDGPzQV&rh$&qaDLkz*Us2|Bft#W~Hk?&FSkwpl8Y|__OPzPQMUvN!o6>2`RP%Cm3ayhEFcR6Zq`sLXFT&RV~F64q#(dP>CTJTf$!>i<{<g;e|?<_;`REFRHhTxvm`Q)DDHq;U15$u0$7=oRsrO8fYg(~`-V)b8N{QW}>!S_v(OiiF>kQ2z~sE^5y*)PvA1fQqgBcCT<HtV~W8G>&r;(vn)`i}a9{Elp81^q@AD*CY%LvT5&2e}-%3$;JFKl^AGv%cGfA$W)>0;x->3&~5#QPe}^L+raz)O+M8vVr=TY#?8-`max4U<kfwie&10>TB|Qa+zFE(bvnEje#-@!LFugNNq%|Np3{;pjIJQ;TZ6sx{y7{m8b>DmB@LhqTlD?wcwi^3unnU$qT4c$xWz@s8h*}$n~iK<N%J1`V7Gpscpz@I0h;*1m~tIWTB$3=jOHGXJ+H!8AEUqHG!N&K0`f6K0`jv5FAfEPmU)iQZJJ)a||Rh1m7|nC$|`av#9ULS>!KNF*d&NT5v&*mvZES<Z9F|<Z9#=)FI>+<W6Seq!UAMM~2`~>QZtjIh-0rj^cO-X9(Uzy+GbX)>AK%_2kWFV`ei$@LFmTc`f-*>Ur{?<jK@y<jLe9>K1Ykc_1~6Jdo@|okSMei|j*gN^M6LT8G?}T$NgZT$Nmg>P#*}E<x3hOOPF@&B%`Ay43OHy5s@WhvWg|>r}BfyUuID^|@bbN3Kt9P3=f-P3}N#M(#lNq>BBRC-oUwgy7oL7i1BF9jTwmA_SMng%GSz6UaiZkwpkL(mO^z#y(+W2!2jYB0nd8peB=rz9)Ym+vkFcIoh5f*oo>&b|P0do5uy0rPiS~Bsb)oUWXyro$5h$Cs(6ZB3C2lr{*CG74vm|UJL%q3c7&&7kQ@DfAjcEhG0)q*ih}LO~`iSLexg&LgakZ`edOM$wG6Jg^D>kAFl;J;=G+ienh@VJwv`oK21GNK21Ks5Nx2vlMUpn)I@S3=jf{p!D-YiavC|C`h}cL&SM1?b95etU<Yb7vIDt1wFS96xdycpxdyp9wIjJYxe`NgTWTn|EqN?8oGf$`c`SJpRZkv89!A|v9!4HST}vKB?oR!a+@0KkI+@&o+?pChZcT1L9Y}6Ku1)nJ3vEgkT9sUzT$WmfT$WsnT7q1RY)f?{+mee?>ynF-D^mxME0fz(uan!8k5I*&dxY15i*p`sO)gGuPVGQ$PWGmHl07-MdNTw!raF=vlPgk7kSmglG6dUF6|ybankwd2YwB~d2*CxYAIL(*yjg%D*oNvvwxbrII+2|?Zx%6|Pm3@Fe=+5K+Y0)ND*Ru(7F>a8>yYbkZmqx&T$);qT$-GVnx8CG%%Qn>E%<~LbSC)(c_h`7Jd*5c_1`?}$`G8_6dx7n2b2D-K%Y{D|CHB)pHpqfA_Tvu+L478B8w3GikgosRLr@r7=o`*FOsj2Pf|~lPm*J)C&(u_=f*MwpQ2tRpCVsl2u`P_k<-basM+Lf&byy@EjYgw)PXFtJUKtPFtrA`Fu4G=I=KMZnp%l$P5#GpPoEA}xg2u;zy2?y{`*gS`&2Cc52SMbP0N3FV*WQjnezJgAEEek$SZzdZyJNS<c}HM#V>}H{{y2kWpw'

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
