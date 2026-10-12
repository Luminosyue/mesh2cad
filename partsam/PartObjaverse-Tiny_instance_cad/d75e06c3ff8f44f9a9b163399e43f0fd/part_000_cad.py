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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d75e06c3ff8f44f9a9b163399e43f0fd/part_000.stl', 'relative_path': 'd75e06c3ff8f44f9a9b163399e43f0fd/part_000.stl', 'source_sha256': 'b7dc35b43a40770946c9494556bf06edabb76a14577efefb0ba9edc8df0c38c9', 'input_faces': 1056, 'input_vertices': 588, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16900861263275146, -0.49960267543792725, -0.1788906455039978], [-0.12147943675518036, -0.4758380949497223, -0.10599715262651443]]}
GEOMETRY_BASE85 = 'c$}r336#{-*0xgxGNVi~2xu`jLNkw|NHGWqGB^N&42=vI6akq9lu{6{$mCT-#i0~M6ctfaga)d+tJ@hx0Rd49R73&24u~Sdm)&_zNOt94>tEl;T6?|Ed6RR_KItTtoFt2Wy^0jAWI6w8S;tN%XU5xFmP8q=k~Mww<f-FEj-JwF!lXMwR=Gl7{uzC!PygQi28FEY*6fT?qo<6VoY6j#amAQ+8JUrcF%u_GojhW~@QIU0jTXP#i1AZK+y0cXBPNZu%MDt$YnK^md1+?k&dC4rUn$9<;<NeNY>D0Z_cw)_UA3^R{ZzZ<Iigty{^RrGb*JP9`H9Ngl0m-p%rAlML>{`_=f~&2;>*WfAK&C-O`h*tKl0V2{2)KRGLiK9rk&WJV>v;-RkcH*pZau+KmRlD<p=qRS!0tye%7q3a)bQHiSH6#KfZjFZ@ljM`0jY?4)TpF`bU0#kRR(lKI!$%xZ;yK=LY$yyu%4!JM^2?XMBE;A3c`uZy!JL!Qq@BKR&K=p&zf=%-2r5Vs?IzpU9Y=^!lb9YgxP8AV2clZ-x11J$JExf6l8~5ah?-teOn+QyrJ*2KiQt<-zTr+_lB)M+epN@3+b~f5+II3jV)Wt4akyeyZ5TNw4qzy<S_E8{|jlJ)Q{i<NH6_;`L2F*6$<pgZy}p?a3fNYho%Vu$}y#j^FuM(zl=FpH~p%N2X^cy}rAjbh;-u$dCQDCK2RE&aB(w_1*0}WNm(+UwuI`$dB&L$PM%#4Hu3p(qL=ScU-R-RuJS{4}G2&<R|KWnH$*71^p61emps1tJjZIIrMd*&wgcm3*WlT*{`DazLE6pR}bG<5ag#;@6Gf2?tWEnS8k9Wtur7I<Xcbn-|F?<JQv@XALLuF?oE1qH~&(*a)SJ<h69}61?zR+-z7fnSbmV7RitY&(BE)NZjhgtn@9xt*6_K7`&D%K!~XsGk*f-V{Mf-Gd4cQi%FXrq?)iM!*hG+@6>qxL>znPCx?y>Kke^leiKN#z+bz1Id~T4Rh*x!v)0rcD<Bc58C<yYS-AW~c{KW0g<p%lj+y#li_J{qk#p|2=6MeVm2l>&XBYpjv{39Rr%nkD6V^fJhe{sjcep9Qu`;M>J=tm2J{M4?;@`C*6!AgO?bzS8|pug$!tzO^S`=;;s)xJ4?V?8?hj?=_P%L;=0_=IQjyuLXeBUhIV^sOT`6G47f*@CTJ-_7Sh&-@@iKKO@Zke@a5-JBpl`o+jXKk-+6-*FL7&MFA<6Vu<$3-YZ_Cvv^Md%XPKG7;okrytwu^-VshEwl22{MhEVl0km7{fV5wcG|Xdt`Gay@a?y;^=I>g{K&!<Nw07A&s5_%xj}xc*t$fJpLOlC&i=gNOrH1nO6?d}5ah?k?aK@D<9&AK2DbCPbDr0JqRI_hy}r9YEPEk8$hX!mOa}U8>*faeSsBH1g8bA4zhxJWW5N4*-t8GR=PTuBne!FCyPeJXO8E(MzEZw>zA`@fxaTY7yXPzAyXPzAyXPzIbH0i+%5jckbHDIwZb6VA?Kv?o$dBFDG0@Li{Kd8)-x|=+=O=O>^j~i%-<+=!dp8&Q?)hr@rh*_p{``!*AU{%}t<QI_H@Y6)7U(}+&F7nZBI_>C5AtJ+{!9k?jW*^4`Kc09oby=LOHQ8VI<woe1wnrF_|m)}KbCv3&v);SZZDGv@>6FIZ}s}_xCRf&5AtINb|nM--FtF^{M69voa3w5QvZ2?^RV{Kd06}AJgj|l9!^`I^RV&Vd^itl-<*fFZ_dMM?QkBpCfw&gPPsnRevIqGG@t83?Wedt)V{esOno%YfBxb6Q2TMN4~_4h&$&L-zBSyrK1^Gm>qFza+kxvt?VIaE?VIaE?VIaE<HyZ@So4#@^RRXD3jcYV`#bGNxxdqXg8Mt|$GN}LzPZ0MzI*-|>fGO@`85_KgZwP+@6vqk?~HH88*lti;dmpxoBGa^sr>x~L4LIJpuE8Kr}Yo?Bj2ss7TC_&p?-hUZ2x&!`Q|*V{lw8-n+x0PlIc6&#%|eJ5adU949yGjQ-}KbeD`{C<%VrReym4tzi;ws-7r7Mk9H{@=to{(ofG88x6KRmBj5bBIk5ecuNV4>AL{td&+hM(^4;Gl<-5OA_~yLr{!VG%{7xC)<Y|7Vl<)pdY2W-#Dc}4~X+OTBdUl|{=)uD65Sw|S|2%K*FO=`zUnt+bzfit=f1!N${sQ0KZ_WLM^4<Fj<-7M6$~X5HY3sLcpB?0<8cZqN4)J~^{pUS152^f=nTJ$<#LPn~Kgv9$@!j+1${Nmm!mP0WcfrihDBpU4`5AooccDD<Gs@30^D}yVGe3jxZf7$;qkMOMM*C)dM)_ubCT;zt{j&r6{bZoC{ns6F&d28b&-|zMt>Vu7XPUp>ng7&&7W1EJ?KA&reD`={{!{x2=0CL`WBxO(9p*pN+8H!HJIGHJ?NqoOva0UL_3l4e%;#%A&V0W16U^sp-%2|3`NlW<p*5u07O(G)i+O(SXED#O{S@>3+D|agpVof4JF|oQNS|iTb~v@c=SO*tqx}TWakL-jIga)tJjY4%n=Hr<?00QF=Xd0$6^?K2r@sBZAjnS*zd0|^A9zimpS9+}ZGr2zpXBr1-(Rjbv~R9A($?pC!)@QJ&-I4(v$)=H+cCd)+;3{%+;3{%+;6(=8=w14?MJxZG`>4u!MvRI&AgoU&AgoU&AgoUBh1Sg-<`K%K41G0=JSp3&L=RRul*SF`Pxq~pYQtSyu|Y<?I(CXrF|>9JU7UX@O&z*eV$Jl-~IjKIi~hgJjc|2jOUozkMbPT-5<<(W>OnpzwYtN^J49%cwVgi2+xbPALV&*+WK1-W(T)Z+jm^YYfbfCS8LyWo}zqnT^-qUN8tHN`{sP5eRICjzByl|`JAuP`sI8T`*KL&?}+xz?}+xz?}+xz?}+jB?}hfw?}hfw?}hfw??qbs{9b6^{9dGrbqTzF(7w5TNb|XV(7w5TFuuM{(7w4&(7w4&NNb1dgtT_JPSC!&PKaKS={qmE*Nw_|uN(2xt{au_UN_>WT^}mny*|{wxjt0Bdwr<aH`j-{U#<@mqwD$iPp;3kZ?4a^Z?4a^Z?4Z%9jf_$7tDQ-_RW2e_RW2e_RW2e@%8<V_Ral{_Ral{_RalH+WOq@Xy3ix*<Q-`du{H2wQuf!wQuf!jj!*2U0>bjYTw-Frup3GYTw-FYTw-Frup3GMyG^**G2BUhw|Nd59Pb_9{6eV9>&-68_IX*H<a(rZz$iL-_Yxu`3>DZ^Bd7|XPxt?ny1pfd)=tlH`k5IH}h1kujZq)@BVHo-~4XIvVV2v+tmD__RajE_RajE_RajE@%21mn$J9;_RTzDn$J98?8l_@`>f`BwQuHojj!i>wQuHojj!i*wQuHiwQuHiweLRn@9~0vdooY1eKSv<<}**OeKSuUU-z{0_gBvsv~Qj-Xx}_v(7t)TV0`@?LHp)8g7(dGgtT_dbA$o&o#pDekM_-TAMKmxKE~J2eT=W4?`YpV-%0a%zN3Bfd?&GgvXhT~9;bYFo>TemJSTqI^Emvp=Wfb(=QFi$<};OV&hya+Zu6gi%zdcx-TP4GyZ52WH_ttdub*#f-<-#+W}|(_wR!HWee>Me`1-lC_RVu=*H_P%wQrs;Yu`Ly*1mbZ9PQZDcO04b1hjA76VSeSPav%w-V-psejh;l=6!%PpZ5W@Z{7#6o+|I#&gT6J?VI;2jIZCX(7t)UBC(~o@A!4!OHsc2UW)SF_fqiF-b=wxd;diF?)xXoci%tJ?Qp(|t^GOSJKoKFzVhAqeEhWcg_Q5k=i{fn7o>c5-d_3cyuI?xb!@cXp@i@FHS<5pcjteU@6P`y-<|)#*Y96x-#y;1{5av=&&_*r+BfgTY2UmTr+xEYobmPhZ`yZ{cYOW+oA%w~eIWDS`h7*^yYDON_09W=_-XGe;-|frsC@UmMEtb(5|wYRPa<#4@ozV-Pqc5|^Gx%(KGD8;&ok0|w(qzw@5gH2ydP_P{eG<W&HJ&&*YCk<-`qzVU%v;defK_k$t2%?Zr(%IzIhK>`{q65w06wACBA;&*!cQ=V{2+B|Ndj%2T;Cw-`n{5eQ)iX_q~m;-|J5Ed9Pdh=DqGT-#qtkU&FsYFps2t^B%tO^?Uf*H}ByaU%zj!ee=G(_RahDY3(qN6sb_ofBs}XS^MUD2ko2h9kg%0cQC&Gu0i|eyM|Qr)7!j%ck_LR_RaSl#@F9>Xy1I_k*d3PoA>WxzJJla`ToWD`ui8{o9|!TcGUMT+Be_7xb3L#U$k$&e~Em!benHGGY_wQ^F5LF&G$swH{TN(Uw=>JuCKl)irjyLZ@ZcAr?hXrpEADweoFi1`>Cv#+WPWzzZX-!`@NX*-S5Se?|v_apZ2|&SzmoGmgrW^*N$0V`-SWG^L^cS{M(Yptrl`<SXN1^k~L<8=hMEz1(xM%@TYy_TK#{0+Sj~U>o)(lZ~IEkv2z$EhZDL09%M%^JLaIn;LdhjYDYh`1>6rFg!Y0Tpx)c)GI$Dg?nVc}m)lXBernT)@P~Hf*l~Wy(IO#-M^fh&v@^VnI&Z@{lrOXEoU!#vv}DNPTc|q)?FZlO8OI>TAY4G(f1@A5uTm!)eE{xa_fg4?9_S_T^Yrtor$6E4mNT{|&|BcY>8o1EQP~E<*`B-}Ag2QANZserDX_%Pc6<xJN?CG~J}yD4k?YT_a|X?Z&%h<gp#c7rG3-H~fcL=PqR+zx^euG@7^jr$(N;rr58R5JE<?}2vb<@?S!WMzOIbp=75X#$iLG^Q{Q|udK5a)kn@fZo?Ev3xM`Jr?pe^7B?8snw2FrvG+U+#4^%&X`mJmLTwu4L1S4Ffl+~1B)cJxKN!4KO}oBnIlx9~VS+S)N3y#juXe4j(d!NXanKiUaS(B4M$Zg>V`ABVPuKeS_+9r^I1l%@SCc02+1r~DIr97H$5-NW`d#EvfL)$nul^8`8^evfUDKp%kbX3QJm8I-4x!yvRT{2OikgeKsFw6Pm~4St#a<LDH4H|uOipMz!nHFkUk$0?V$$5zFTUqX%^4>`P@x-X+oc<M=CBhf){nXr?u6+V}@aHX&_wle5Xuq=~x{$kzTaE9$S4m)`@CO6?V^nDvT68@T8Kl6<9GuqnC^4%;GE)jN?onoD@;fu(r1o{{2?xVd8=o<JGb@!p4!L`HA_$~^c8>etXwnc5U3@qC_pKUJuA!X@jHhryOtWwU#yBD1eOFoC}C>nNnALTCW!<V5Q;b!D@F<Js{MPAL&i{L95Lo2j4+>K?O(N?hJxzvs%Ip0gUKK+zKi^A>br#^Zy{4?W7qS^31_z=8-a%XaAhc<&RW{gGAQ*5iE^id9$_N3gJ<Gwk18QhC8UyXK#8<TGpv>f~)`96v+g{!d6ar*w5zyERi{}4^Wm+`mDKpT6w9p!fP-I$y@v%E9QgfF4qd1!ff3;W#ybQ#>7v0s8_z~@o-hmfPP|NcM-Z$b0n4q@lq+8XTwm!!SZp>ypD*I{{ev^m@;?6g$}Z4FBwbL@DN{uWTKPTi8|CGeNz`X;&sK96OmVOb{Svh))|tHV-ff*mhXe-7o(srMrKCVU}dD2vvC{|-5MeS=E>!k?h8pr6Cf(B3F?0{jiRe~x|$hsgPFwn<6&2xI#e4Z**Y>k+gp{4H&Lfl3=+5Py^J-=5q*C)Zct7b&l&&hzLe@Klx$Mn}O<(#BNJ_=Vpgr}gL;@bk3!B>D=R!<gR*og0tv`;0jUJpw<%vPEbPJb?cDp@U&*Yo;Cd!0RdBLQYxelkg(iya#;;&SISb=u~(nZQkM;r*K_zy%b#pccxx<v>)7oK02cV;C8gv0nLJ?y(YA|h#Z>`!Y$F6u&j5`a;|AFWj!f(v*QLkCZIFmmeg(M*<Ql0+sl5i<3-Ei-zb;1<3hPlKx@L%=1|%dy%(;?_%24f!!uatMf7#JjU7E{uP1E@C&=M-I2>}yvV1meh%SXCw+7@V+8nM4w?TWt?OCrD+=+4nxH;MvzL&mUM-%V`v~eNY0G57kB;Om!btrB1WqDtg^`y<WXjk+DSeD1AFS-zxoNp#a(Q$AmxGy>xo=x4Q=v$s~e8Bb<EgN!J+I*NcL|1y+olIVn$>~Oxt;7?34wk+))1PQQJehT3=qvDBtn&f-7aU`qh3IDZ1J;qeMXQD!mgT2u!`ye7_GBNG^(wM&3QNvkkc;R+xCHIy!xbq@4#&vj7=3J}-Ye8S$g)@1hM%x)KA{g`IhJG}ZH%^oB|6wq7w$$mZaK%ze)I=e{Lk!I0q>_=o<8cLjXiC)p<U4%;L(<Io>+m#;qxqKUoVYb2p31oqt#%kJA?W&$Td#;Pup=Dyn=FwK8mBJ?GB#2y3wxiRV=#=9Ss+ytx{-lSo-;rzE-epq`U_25c(xtmp(G#4wP%yQPqytXr_nDQ!Y=PO!_X)^5QHLmV5BxA?H3^v;urR{Y*!1gXg2`(KT=-`lx|cg{AN7$t{z%q<lWxs1jNVzM6H1px49G$zcupG~A4Su0~tKOUQK_x*i@voAc4>p5>vCvySkulrzYy8CnBgPyfH7hu{cf%Rno^v*>#XIv*ZLzO&FFaFlv|&}MKScp!Q;d_VQxM3=y~Q)ezZ5Wb9Dqi6>FKHI4b+d{U1@CfRRMWgT%>bwbWqb&0@rz~gx5|w>Rcr0~qNBh8YJ>wY27=)9weFA+SewjL((EH&|?8DvAn(!+6dD+vS@I#g}w#U)2@Co{=5^_|wf$%0zUiXtzk~&g%6?!`?anz0j@XM4XH|e7$T7_JXvd$@V6MPCTP7X=<W5%!>eH`8mA3#^ZN&1$$NyaJV+O(B{?uL)@w`>8QqAbg0?lA*CKv_b#1$q?TZfhM|ccBg7f9z;ubFq-4m&0@IXk^DUv>ANA9ramWpJl=+yPZs1kD$$A3E_XxHn8+lp1y>ml&`m=qaD4`uJA*4)S~}d^ey}^J6hW@6m1VnuFu->D*P|XLs{o~v?IKg_TED0!p*2V4Q@^O13Q-3kq57!EbZTJ$K&wzln>KK3VjQ{%D$)TX-6lt2mCDkJdO^93)mK0(fd8^&1JlE$@f+ImK+A6z2X1T)?sujoT9Cr=&SHc^#2rkJG_&1K0=>`W&PE5d<s8B`2u@vmF+kda`cao!yi%iCG>GmJ?U!%IuI@ucJe*r$y>NW*cn?X^e}veb^b(m!u9NBnPDfdOmY)mP2aboBjEky`l)A}pVHP&mhWVlaIvtn>?G^#hpUoPG4xM(5AD5<u7*!icMtk090@z)s~SExPT>Y&XIn(jQm}0AJhr*;2b86sJLqdQV>RV@c5H(0pd1c6IekZNd*Dv&!)?(k;U?r*11$!(Ag?B9Rk%H4Xn{uHt}Kh9E#O>oT#U|x>(bBpXc%roKXuU>@KMH*i*EAp9?E;z7Q#_-XoEI^YcR$zdXjAxrjPSsX;;cEIqsXHZQ-7bxd$4BGs(9ydOj?<uHf&Q%QjfSv35Rx|MSV=58^26AEl0PTmE+S&`b}vq1=YPGs!8+@+ixMYf`TWdI7wd{cb+G1a8XMYohhwBGmmp<f!bw-xI={(LDI_uyby0iFSgE)80R!bL|S(VtF;RDST<zX{#365|%z@+3^Pb&8J+Ay2a6&@LqC#1KkW4Vc9>hER%9+`Z-H()!-MXHy)h@@1Wib=o@fF#!woq1)m5xd3}XS|H2=mYtbF>)3kRpIv)Ot+;^aR;j?Uu6KHYxN5*ylmGy*wCD$L(((nP=+J&BgcflW{CiflWx)y$c@;d6QLO+Hlv;0Q%W_TrSO!kal_-%4phwg$urp_vOE#+;D`R&lT@d&@mn75%n!pm8<5Zwk#-+k=30lty4v^Cw17`%@1SaKPLu7nrTW(<8BUP;@-;K`Jy)8<%o6<mj08=wo}DD|#F`@omeb`-q<ZbN&Qqr>0^w3&&<;7qtVIvtj4S*epkGvTgwTxZ94bQ;{8x@|n$OZYW=+4pw5U^)C>$|dcnDEA3yby(WGiFQTj!Q~lW4fHB_9&Jx!-Pb6$vZDv>^`NcmSiY4!L}fDLzbwClHbfW0l3RW96Kx7thg+dN;C8Hc3EYu#eYh#w8=gmBuc2Gvvb0eVtq)5-1ITv(x!y!uy;<IyWx^Y1b20oLWm$d~^+o>;OU_y3DEcqBBitLE1m8j3#pnjlINoFXik1#JEN%XWHbfuuv^$BsCXv$smOX|i`YbGcy+ePZdGI9GxeHwjZ(yDG&_Ch3Sm)p9JMep~BYBHf4mm8#|Dg?0x!*GF$v!IUm1o}+mYjEyi)aeYqwb$*d028dLLNux;~naxSe|0pTDIYKw#|0>5SC*}_R&UYD_G(RJL<q)DL-X7$IU+Ud-xHS?Lhaz<>;dh+6Zn%n~mV>D37PDQSeigi&)OSUJ|Vc7emXTRbZ(*jr!BbRrprgeiD5Iw&<f6YTCYnyheHQ6Yj#YThUQ)n6^rw#bD`YFMU12wlU@J>{t!&rCf(T8p2mlzQ~TscC<trdbk|ra@1)^-^Ey7jAg=d4}M<AxepgD2TLDQ?YNfyZl!z=x(;0pSD=rJ(8_R2`o9+K0+(SMRX|I?-KjGey%wHI4y(~8;U@Ic-P51&B68h=u7d~D<~`_C&+@aZBm4{HdgRpvy$D{-I_u!?C|}Ij>Y)|jne@E~y$9}3zBAFmu++K6jw|6Nl&^vNqut^AsP_iC2%botJJJ4dTXMY;tp~r$HYgQx^ejA_I%Ci);Wy~(U33d9^E4+dXa5qFeM@)@btj_Nz;}Aa(VsEgNBhU^$c5jf{1SCGqW8fa*@wHL)!}F8=Os^n!Vg-`*d9g4z{lz9!jPk~4TSF_myMqMa;YPApFt<W5<l7T4g3;iX}>x-9;Y8E|HL{c(T(s)ShnLv`V{_%G3-Pig?GZ=pwGZkN9vYCkHfWSt3J9D{)xY3Gx#KBStjc=Lcf6}gqxv1!B^XHjUADY^FFTdwS@3Zgz#uWcp@QuCn0<vA^adA{1_qpA42%wgz#O2@FYTb3?V#(5WbGMhH?C1IsBuoMe)VE04~Zng)bt6FQAU_*On8)pIc4{e`Pr#eAseA_;<^BKlmE9-|zTE2;uVy;cA4i)RX7`y+Y1&)^2cLLU<4%JdzN;jS!wq2;WNxFC~N@C4`p|!V3uDIfU>8LU<G*JeUyfNAzMG^8SIaJaY}>i&qv7Gfv^Egm78v2+MQX{jfZP{0x@oj$gv^OzRLV&$epPPB+TJAwsweAzXzJmU?pk(KF;+=XHg96T$-t;Sq%Jt%UF$gz!8<crhWof)HLp2+t>kXA#2V3E`Uw;Ts9zK15H(A@@JRa?NMqi&q-97^iS$Lbx<_gyp($A1v2EJ7Br)*$c~W>UZ!joG*K_{eHoh->0*1DMI){LRjkc>lF%DD)RsOuc6NUlY3gr_a8;+n*PsDyfweJ+j2ib>DTK#xz4gLZo-8R!>Y+w0oMNj(3YoA'

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
