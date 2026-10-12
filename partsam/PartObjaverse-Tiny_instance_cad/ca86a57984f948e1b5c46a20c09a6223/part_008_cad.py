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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ca86a57984f948e1b5c46a20c09a6223/part_008.stl', 'relative_path': 'ca86a57984f948e1b5c46a20c09a6223/part_008.stl', 'source_sha256': '4276603bf1621c9d4c2cea2b981ecdde8bb67811b7cb164662c5b2bf5152d4f1', 'input_faces': 714, 'input_vertices': 478, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.12227250635623932, -0.11638832092285156, -0.20168930292129517], [0.2546710669994354, 0.15423433482646942, 0.10715997964143753]]}
GEOMETRY_BASE85 = 'c$}r22UJw&*X|Eu#V%kk2OBEZ*icbN!HNY%u|#xGL~Nj-sG&F(6nn*9MzJd@f{54#5XD}iVs}hTFd9wlQ4{^<-OrPI{oi%JwZ3()Ywh*?X3w7e?zf(EW?1@o+vj)E@Xtl7UD|b*PXkR;R!no!B1VQy8a-lUc*Bqh)9kcT;#dFv)fK(^_w*TLr$uOyu7M-NM})by)?Gb<++FMIu0f$;lfnW*hJ}U&j#U260pr3)+Wg_c0TV{rUe{^X(!IXkv~GPpTK|9i=U^+rVCZ?Oy-h7I8>J{UY_FYjO4Zh5l=!u6jm2*%x#Fzyo2SeXzbSuL@oS@YO1vq14dTzVK%Nn960aF{BYx4FWO+ZXI^sJYL%Z&8#cw!<{Dxk);ooUM9?w6|Nc^8~k!R><<at~X@z1}o&ccZQk|FucPwg!d-(~>(<KK$kkX{D<&_d!j4Q4${Dv96d0Ket!M#*oP@SXTA_nhH3EkXX!X5u%`DUNZN)B*KO2^7CRFB19xbUi2e3;lpRG0l-@U;*))uPsGAt6IVT+j->o&PJZ<^Tcm;E`xChdxkt2T@c^29{f%pQ2(%AsOQpT_!rw{NdEf05kL5Lw(=X(i;G`#Nk@G0_fn5xbt&;%)|N#5#Y;*ay=gV^Tiqri&w!>9Z){ovd7j-pB=Od}l3y!bA9+?i62GN#X~|=p)j<5_G2zHR?>*Mrx#7s)szbWGe<~wO>hC@Zc~)N$zp2+O@f*I3MZapUIVztUejEOcG03y;$}xH0<w2(MTf5CioxP7qyp|Lo@fOP}=2?0~H1C=Ctu5Ce&(ep|uHNaI<gwTv5WhauAO7ySXg4+)`Hw#rzjkMh`1Mw4sK0B9v}=6v0`b1^>l@Lo<yAQ9nR-tAhJE`mFW1Y;IBU1hBmUZR>6f<eHR_4GA%3H~{b9*-G7jtQ^G|GdpXArVw9}GjP#)^MoQnL}L$D6tzk~mE5Z2p=nKECN5_XwV&vZxR4_ShG%9jwoHE9<1mvto8&!W<ZPiijv)L0}|@>u8B6~A$TulOxfmZQ%7@Ea!fh5ywk<lpIz{LL?6y??!UT<Tdc0REv^cjlZK$0SdaG2%BrYLO`OSYVq)+PxZ%{2ddKN9!l?mas_iYehn^4n4FJ(yn19>Ri?V<58}Dy2L-8jrgwjkjLpS)KhSy_$@&L_DcH$mY$M&PMZ<GXgBuDcP-?6Fr7(&e_|8V|6rfgW4y3k{HCfs%%YWEWJvzoiKxdL^JRJEFZ;!4Ie<JN;gQn6^?zaCZAyc`%}Mc_a~sO|Yu_KoIP{o`^VZ89=T+!AjGIF&{Psr4Z~5Ue>PhI0ai~8)#=)@aCi+{lcY^4g;#gO;@1xF)-_s;t-M}LffAT%*@f#xXrh=<votwi7W{JN=OIe?~<Cs)wH@;LB_U)=9$?F!3^LbPi#FrlzC2Afl>)*T{e#5wUi8saHz;)-E3;YA;O1p;AHKa~`qMP`22haWDzvPH<{<|UKe_e)lOa6v-^(LrieOu%&Is)TAum$3~FG2io<It{uYs8Oj55FhtdG3Mup(SM>nL;nhdNVxeh<=sGMZY%rqn^rs$P*lkJm;F=demzG^2}-_e#@Bev91~oLBBLN_+#_QKC(6q7Qdx!<t>tb^>7(C!^837H{S?B{Ojh}k559-u2x(8hTP%OU+d8+h#v{RW#U6=S3f=#`7_NpN1Hr4B=x35qn;rL<h-)FRm1q@#3KLNh12D8gLIh}L(F32_bZFI&sT80j$VrVd#j?|mou<#gI8kQiq*q;IX+d|HB{V$c3&+qiU0IgoMYc_Mtnp9t`|;a(<DA)2jWi_m3Yg|T{!>CrDB{jV`gCg9>n;xfnR$yS^TDbu^8v~r^Ro*u^;2m*&$iRA>sn^I5b!;byTy*^=RB>v^%#u#yMg%uBZ0bkw0`N>VMK4`z!7i^6dG1P+s5fB=P#6j}adjC-GYE>ylsl`*)1zoi`G13Mz{8xkIDV((X$SjPrV5+$U6OC4N)t?NySuVI67L(%3`%hUi=SC2zm77|&Op;x~^DKQ5npen|2eOLP*yrN$+RH!kgg^M6BU<k|lV>Nz+Dc^<%T_B$kbEKwJ?OFK`yB2Uh?nbNPX{jvVr`69m5BaB1$RLNubyFdDM++mi)pNz)-&F6<anaQ|+sFEi6txpD_p6iLyU(1ezxZk+xFMe$X@>}kdNB%gY_^m5f!N0i|&ea(~Xm=a-x8=ji!{Wafj`8f-9`h4CRn9kK*Gb58>{pzN9oHfL;1tyJM^Vg+`$o*~50U8aj1y@0RyeMY<z~P??KaNm^NV-L`&DM5{_JPSe=bVeHLRP3I{mw0{{^L{h~F<3b=C@&aWJQ~#k?oZ6Th)Qy0mL3*b?hMXF1066!KeYoIsvdE70!QY0IR(eABSbORh${&xhiE#2Ak{%kM?}SJY$uqpe&o%=1&xFY7j$CzH!nxsGdprD5EP;Cf<7_mX(M{R!l`mYg7;fAv_dzuK5=)IVS-<|V3#)M@E+3H2}d7322yiPWR5zKuMt$Zvg&cx$oz*;3DHf6Qand1+TWQ40RKktf9e@F?<}DJ_1zXd&#suGb{qxTTu-O}=x*Z=4w==YyV5OZ=8B6V`L@0hr&fwUMV+G_M1zCEhf@9^zl>*pJZ`tiw^w#IN0}j{WF#LCza(e{1-wpdQV*M)DY9+KJzqn~C}LI*;`h*AaEL{v}b`dwxm$mc8(6p?Tsrj7)(44gBWu6HtFktXs{cGvd=aV81WU#6Idc6#e?ECf0MrcAQK3$0B~&A;iDEiu3U4c=R`V0>)u}L7dyiqv7}5DE%>C#5rkt3cppWgn1uXLgFpcXQE$8v9hi#sRmqUZ!8tRu^;b?&9RFl&)>_Cr|WLamt};sWBfH9{uygAzgwfx{*8_Bhb_cBrJt1ZMDsVJ-Ta}rF2sLbEbnjF1AkrC>4iL&?1RYToFM0d!KWUskGHeoFWOD^v;Nu{*M$$~kf+)Vtfv9q*uV8IBi`zValSAe_Zts?M1PAMmi(qq$#@<acoXA)biK^4<w!X0D@r~<{vbXdbbW~W$NhwOkC}*%SdaV0&Oamn50`Q747-Et>B~P6-}=h|@t>QF{MtWQKd<IUJ(j!eai3=YMf`>nPY@rs5%*nF;Wzi&g>&P`QH-}kzBAJ9n-jdwn{oZ!4!_0zH`y0jvF}!j-?5DN&3W~uPIHtS#%;Ni_)V*`FwXw2n8#CP#c!zA2<-->V?CtTM*Qwn+2^JiEpQ!~(MbHd-yz)B{`OM*#zRe!$EUd5Cu`#lk7$p16Tjwu1J9>k6{kww2?ND%?Q;P43;%e@xuh)$MSpbz*3TcE#jn2$L;l!xIH!vB!1(u_i8_-z#!8;oLvao_T#oTsmx%j|dk(lBP1^|ns|%R-k7pLj=WA_79@hZu_rASOO21;Zpxp}FQRmv1SihroAbzAb_V42o;x~Jwz#r0^=i4jJ|5fzYB^~>v#Nic^x8XI^v-t$>FSmS_akZ{{ggk9KBHrc6a*0d+4SDSEqW(T13*`NI?~unBg6qLdJ2@YW$BUg6|8wrsxmVYSI#&_D)+`79^ukh)mQ+>zrus|pynoSqlJxt-K*WEEMtswn$g@05{O0|~<^Eqg{CT~^zqx>RYb?b4^-h&~%y|#szkFYwGYu)*v44vc&5?XzGsJIRR}b&|6%)U;*a;aIQ-#a8A3Ik;{92od@_Fmcp%QPbUJrTpSn&CCSCK!ai})?oeC7Gb@}Yn{Kbd2^#cymJm@4_chM|79p2&Z1rF`Bv(LtVP_54A|Q?@_aeKrrz%iqlxzuwOMpuC^cZim!8axLOhry|ds=6Fs|-!Fbcr9iBYO9ggfKV`vx=%`$O4UgZ;bHB0lE#x<!!G8BiPei?W7@tqS;9M#>Qr40A(MR!{<9cBK8k$Rfqko}u^0`^pB#*Iv2dURovy}Kvw{D`{BWB5O%`S`hGHLkUDf{;W(w_@8#cy=#aUA<NUGkXiT8rQ6x<ld(C7y_1>(U*0w0oG}&C77UUFm^5kxTIW@>5ZX*Vp)p->~xq>MU1Q{KhMTkjH!h<N45n>r|Iu)c-6S<Dcpx<F6GRFMdmZGtQqvpHa`E3CO=-tJJAK?k?|}3r-Zj**zHj@>qg)yG({({|V3CnGW*3h|yz?`1Kx{=<mlgv_EG#+AVlN)|K^`6VAm=@o2a2dH5Tz7r*YX1M!gu(62Yoan5%?jDA&HAo0edzQ{8NeoKWPktZrh>bG<{it+j3IQskgiqvB$l7aeLd*iuvsUMyja^Tmk733T=tVr7>?G(vEp2fH>YZvCki{{-y{Pd}~ukBoSm#n*}yQt^;c&W#nY>@U1^WnF8zd)VuQskU4c)r3oOxlfpbtx}?>+kQ7=ghC-*EdbT_oh2Oq5dvrj@uxNTgVrTPi!8(Pq4JEBcBf{bYALzlZbjY;(Rg$mJz?%`xeIGZ2_rMe+s{)Npp$QJ@CDtIn7D@)@D1AC$==c?>tix`R`7EKX;788y{B^zoE-6^lNTAso&792J$b~7Rl$%2k(=*%esl*w6dzyV{ZC4;teg3Ki7bIjt1d;&2tyOvC~Q9Pi_pY=ZX9|FC>rA{;G_Rp_vcrFJDr=k1~JP5bJ#j{HDM^@cMf%iMPI_|LjrD%RiXMmA>#_N|*g>&FU%hZY}R8e*MaI<f*a>^RjpV;tOSM6a6`#>=&!g_vlwjG1*_{A@8IvLrehXr9d;}xz<7QSi%F5=TlSo->-l_9e(}U9PE?8dE+E5brkZKPctjOC2ROr?Dx@_muHExzs!UCq5dvo5ucWh@ppVA`Aq>Ks3)Tp{HE7Zr}1Mr>KR!F=aTsdzvqs?yzE81)%O9$KYJSd2e)BfMyFz5ZivIYIC{Y!mxAxJmn}rQ2NKcWM~+x;wHBklopVr61wYKosio-Gry)D#^AV45KI_X-r~5VRm%i0;K2=zSdRm}eePS7`|M=AyhrHJ4SNG+p=k+@Hi{+am`#kB;9?A0}0qZUKCf5I{RkCi4hjzekoPg`m`cLxwZQ8RB{o2$A?Yb<%?-E51pkEzo<NMNEA?ROR65_{&Nx!V;9^$&NHU<5?w;SU;xFOEHvxiaVnPr&Y*?Ta*iANEi)EIe}=f`zy$#M8ISWn#sn3pgM+BJJ&eFiVYzUiKgenphR^Xb%o)=D0yn`pPU5&3=QNxXHzE%?30Zk2U7aPfBeyytz)OTQ(^pEDf&_I`kN=Ov?G9b9oey8Hz56@>gom)e;3-cOM~!+`lp+>ZI0^A7oA?jld753Z}jJ|q9-@u>6KR;=f&e=rV*_h6h;l5zbiZFfQ5FM9^#Q^OwPJgT7h4MUH?|125nb3<YATZ*q)B6U;^lJiY3Tm*UkM!UvWcBnrKesfk+TxSp5!+I#?D1K}1KUlY8*J52Qset(7kI}D2r?F4FS42HdS8%<UkMq)a2!2c8RK(Z1gL%;^qn_(M@j5jC?@y|N_^5pFS8~QW@u-S=k}9K4trmU<C|3h{JefZu6W8Uan&Q{XeMNtRBgAi9T_1Hmh(`RK>Nv-GG!(xn6!#lu(;qlbYBh%6AqMlcYZCGoX)b<k9_lgcY4AUW-}K`~TrWm>;QRQOo`|3BuvGH4%9QiL*wq{LjOX*D&(c77zl|UKCHvt1dFAi&eTzP82=Y%Kh5COyEc0T`3WUE*1Icf$iTe%fi;)=5h>94ueGgIR(}^7CcCt@Rv${!s(~6m>bJW1u^19`2IcN0An=#IxI!S)xnOyn3NI#m0JbTJxKTaMi`_VY=0M<!7e}6gI9`_Gl4x-M4ji|HaHmvjNC*dDh9rfhClX?t(r{Mq91N*mB2=;IHOw6xiJFJrfskmNWg5SDilH}Jt-SE3&=d-Bu70;0~g|RNqyhgwLcH#ADPmJd;Z_uveAo;#VdpAkuOLHlFQM7*z^sBf9`HMS?-}JGD#Osl}aUXu9#zpLl*H{nFj^X}iP$$G2LQ#L{kFp<4T>}uG+i{`f35vma8yJjsE1G0IXti(1bGG5f2=QAY2gvh`7VaqfUiY3Ne&fYwI3LQV;reoHCgKxkU>sh%;r?@YocQ&5H&D;8SnT)mE70y?Pifb5#~|ZssJR>Qk-ZS#vz)|RlJ=n8kO9cw8NUzfPm<7X{wH|tG91sf|G=+}SdHIV508(Re4A1b|84~O8xuKO;zBYpZZn=PlXhNd82|LsXt#A0oLBW6u^zgf5x==XZCoE~?81GH@viu-rE225DmetdxBEUqyGvcsZqd3jp2n!ZQK#d3`98{ga2d{rmR}IxE)w+zWUQ2SR(wT#)Ca`ZDvxtgFLOzBwy*fD+plAsBCCmCdx7so%@cpddG(8%_$@D7_DFoc4fy@s=R5J6S1!WuR$G6U=V`q~OXOMRA$jy|r*J<x-3xi*l92yd6RgAeJyB1XgZPczR^#{Tw!Ot~NN|vL&DZ|G@9^XL!XI}J-xK{AAlDaj!G6e7hV^)i#Pd#yAN)7VA%C0OxW4=}40WzJiF%g5!1ZXbQT)cvX?QN(oUkAL8G-muU-rp3B(y>ON5-I@-DAYBCqKvd6dVWtwu^YK4_GF3YClhaKcX1Mf5B3WPry{vnN=F~m`-57oQq+<;!#gi1NQZxS>o51T*U7a&h_Mc(C^Jf{Y~28`~BZbV;oAyquu@wrB3tF1Gp}9FvI_H0>;g?HR3BIqQ8Ce5Z^Nj_aR;f#c!S6O1>vDPBLK}`lMohHzweFL+cJ)A3LNWkLe)Bp=BEx2gAE#h);;ey!^BW=brrq)-x6Tt?G>D?v+>2?wEt<@ADsJUaZbHFb>75<NK}ymvG;E_a*Y=o<{wiTW~&<dV@UkbjfdxJ&gOk&tDP$&pyoKd1sstb`>s*e^Yy`=L`7z7vsZT@bB^2EqSJAW8MA@zvb3J`Tj-kg1@7&bm=30t;(-5Zu;R|thbwe;eS>{_N_H>9PZz)`ibB8(TF--hvPZoMG)er*h#!`t&VY<G)DX;x8%JNKO_TxPtiIQbv7P`eub4s{qLqBexN`6&MR>a*O`s@Q;Vd2t78K8%llaLEAmf_=U)8XkXCgr>O9YQcRa^gBIA%}v@hy+tdIMgqRZg7kHhy<S-$A+=as0(+6CY9FE-<x9uklI0dDY@eS`Q7YY|_8c~-T<c~yBE>U=jC-v{OSpq@_K(QfS`sOOdk#<TNYjAv3b=Ieqp`a9wP;?KQA{u@rXK4zt%-NlGECx_#H=He;wTTf%Yj7Q3#{zjR|fBqNb?;eIar{$nueZInfH5ud6?+WXjfbkshr(7Q__j1LrPaKAJX9QtgwR$9evpwU-F2-~Bm?x++WDv%oHNJPz8|T4aB}d|otrwx)lOIt3<N)|rJi~QtYN0C<KNNmFa4z=ss-ohzq&%1PW;}h8=R-00=Xs&s>3OLCQ3>&DUdhPQbq>Gpsw#fNdtbEclppi841P<q$5_uv&G}sEhI(=kuQwZk@myOU@s-cP|9(IERj~>DPivzdcRM`qc)+i<4U_e3Jcj!XZA??~TkB52I;npg_3wh;_|smDe?II-OWBt2&)kCXFN5cFYl;Wztg{QxpZPlBd!!+4#jhK?Ay05?+`nXWLi`N+^Vh_>YSat)XV{~jpKw2GYS0_?pGZP~*H`Cx3%@zf6L~7n=6TW=dD7uGKEH`^@E(XfdmJ#%kMP`NneLA~F^|!&kGNm6OdE>&&z?qpH{7pj4Z@M9{Y}JsIpcm~-!$~=bS2ckt2^#D_QP+PQU!T_<NaHT8SA0kA@r*+_NjT+7UUlmC3Wf%eQ|E5JwX2ZePo=?o*OX!{U0KKC2y?H5__?KJ3T_4_w6O#whmDLz}INE#Lp6M?w1eG3;u7AzmXT_(e)Rs^Ijj3-#-QSCp!L4Q@{TSd8TX?zp+9C-0xj2d{ydd`-fa-&1<)#&fklRUn_SS<L~?k{<%HGuNS?9_~;5p+xz^-Ut>Qgd9(RnE}EvSh~}gP1$^_T*vhH?{j2}?KgAy1?0@v9*e#nh`~Uq@>_N5~JZ;vA+ML{p>`rY;R@#Q_PWGX8AuA0e`;g<PbI3|}ljF!|sprW`e<YtJ-=|v1O8+9?Cx4|n*@3^38``WfwI5A!52_Qn2e}qi<*LQkia#>Hm272AA8CpoQO}bfk*`vBldqC9sdLDg<jvGT@@DcZY8Ub>axhJCKWZCtKXP|!Q*w85Z)$ULZ}KpzCwUloJarIxJb4jy0(lX61x@iJ>L9YxPUK1CQ&e}dQXjGp*Uc&FS@Kz~gHzP6<Wpp4t_d~Y&flyFXPV*~G{pm{{m28!w#}@~q{dMDkz>e#)E?wOa!+b4a!+yzs#-%OsE^3X6#q)!Rr0Uo>(os0b#kiB_D~b3ndD5arv#ef$<$fo$z&rnm>kUYWTYwfqIM^Hk!w+VldDl(sJ+Q9<Yv@i<Yr`l>Ugq0c{X(sc^fr_x`@1p>o0|-_!v!bI&~6x64y;SP4O+7;ty1{Zaz?Jkd-MeXtUPTzSJ7z8eC6(X^Q=+)5!khVKl|lX^P{%S&MNr#q(*3=TT$G^T@F@#p9@f<Z<L+n&J`Ep5zhaJ~YK;sU^rt)fz3!*NT6mDZWj;PQFdPK~sE<no7P#PNON_|IJ$8PgA^;rg#T6fxLsfk*0VobuxJ}*Y{YO;=we<9jRVqFRtm1G{rhiag}fOKoy$eN;JilsV?No<f=5qO{mStO~~KT6t|%IlUtAn(iBHiXOsWkKhZSBW}4y*n_aNk8Jp!$Gsqc?$)PE}L`@+pJx0DnzCukWE4@X&LcU8={F3^CtW@o*mwc_b)Hi#t6iu-=wJ*6Z_n0?z7}=ZL+h#4Pel*3ysl&*_$qT8|$qUKLsd41x<dxL<<oVp6D`|>X&=fDF#*$;XSC`ThPogOfqXv`1$m6La$m7WasC~!-$n~gY$x788uE*DkUu)3Y<k#eT)Ene`<U7=B<U8b>G{q;WX=J7Q$tTH2X^Ib1caoLvARi_lq;4c1B=4e*CGR4esDsHSau7{%H)=<6H*#I7POeL?Nv%SzNv=+<L{?gvT%BBlrr4EQm8`T0*_GUqrnoirJ92As2Wks)2l5E&K=KIkd}=gVshK>VypNhe-bX%1JwrZ6zDT`5zDT}IQ~VS40r`o|UfAq0^(px&-+xSfKz>YqNWDN-nnQj_&ZS-=E4@NidY7C_enx#sR;tdOXMC-=8qXqcay4=tYH#wt=T05!I}Kci{9J?nL4HpDh5Ca0f@AaxP4Umv$K=QC^UpNJdDL8TF8h#2Rdwf4>yVW`XUuc9m&crWe7)8dv)N|Z)QjY7@-6CJ@-6ZWn&LY&#W$%xl5dhvP>+(8n#m`~Td1qaTgdS=#dE2P$V%ss=aPS*n#ezpBd80=5#(9a&E#3++0?b<+2m-N;=we<A=GSg2zfE}7I`sw1N8=Z19`p8CQ>)i6yK)aAm8A)-=-<PPrXULPtK*DAm@@Zs9VSx<OG`HHPm?W8uBvgT=FvV44UF8)E~%G$djoN<jLf4>MU|NIg+M0iaMJdMV?BHCQl{%QU{Zj7AE_W^V#gJZ9lxS*(aLfH`G7LZ^)V*^fOuM-(+Qq^HWvs{A{BzIX}5Obuf7_*G+etVk31i*+`y1-9Vl|4yCRq|GS<-X^KZv$C5{rgQ%m(LF7Ty@5zJ69jP72N?pkv$vU+tStl2u{-c4Fz9qlq928)jVtYH7;xByv4fzYXh#geTK@pnb_SF33{2br*R3o`Pc_?)Pc_?`dHIy96u^U4TB99>lPzR9%$o*-G+fqA{+mdTib+XQ}s7X^?oN7-_vUT%-%@S#f_fprA_mY>}EQC6Rx|TeJ97+u%hm!kJhmiY{dr=3Fdy#uk{m4qcC-)%x(iD%PjwX*HM^R^xl`bVmk=Ia@$ZN>!Xo^=;6UoD=;nYNOIC&y<FL@$)D0Mk`D7oD?<Eyy5%_`WeEwvrF9b?+k6py1$A&(<RP(#TP<S{hGeW-oOeaJnjy~sVuU8z0DUCEtkioL16WN&hR>L_x5@<^KENNN;0k{nN6Lyjk}r>-NfC$FNeCjUEUt7wV?Xo?$YIEvN3{M3Bp{N%#aBILs4lGGAprOxD%<Z{$H<Z|SC)cWLl<ObA6<Obx%)Zt{M;pE0-19c+VKyFVRN^VbXNNq<}T7le<T$Wm%tkj8ImRyEfnyj=SxeU1w)t+34T!3mvw&S=LpeZg&Q|v%fT#Q<nT$tltjHb90wH&z=xgt$*ZE8JoZL$Zo0l5Lk+JkB!dyrdE+ml<7-KY)84LNph)G}l@vLm$+*^ykFT7X=D<D$5(ZQ!cdtSU`$Ih&QSSxK8YQp=GY$rY(p$Q8*h)VgFBa((J|<oe{MG{tRf*2rcpY}SmX*n?^ydyqY;oynf$PSmdCPULn}FLFDwJGBkD4eN2IDQ-@!ORmfDYEDz!idu<0gxZUy*o|6=>_#p`Q~cgGFTZP0JHA$aJHB6)Y)5vWmLr$roH@`G7o(OTD=kkhMlMaQOfF5XK&?%#K(0<x+<@AM+=%nnfTp+!O>q~h2ib%3*M+9I8?_U;6X&cO)t&6lIp{`H>_cru{&zlnXo^SLEY)VmY<7yKILl^7Y-X|9acU0vIQb0q68Q}IJoPg9Joy6k9QgwIEH#UKmVA<WjC_)uMpK+ZO(mz0_frp&_mg+qY^%+-*=!e0@m}g~@@~fOr72FLrjk=RUWyZ`r>UpNr^(l8imy<!$XV?F73yX3Wsc(&n&PX}9C8ll<|<8bCQWfV^$1z%A#ytTFir6R>OS%T@*e6A@*eU|>Q?erj_FRC;_cME<h>lD?KH(3zZplxOQ@@;iR4w}bu`7v)YIf-@->>`d(`XXd*lZ;TWLF6mf37Obt_rvA@X+e5u0V(?6l3YXo@Y=6J!hdIQ0nm2=g4LDNd$tB`1@&P?wRnkeARD&!es+D_uaIN1jfdNuExgO8tR6l{}3aL!L&CrOqWQT}+N8FQh5nK;1<4@wUt7WdGm&7k>ZypZfkt`;Y(7@BjSdfBw12x1U^W%k{th_{7J%fVyw8-GJtko45@13#;~D4QYh8'

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
