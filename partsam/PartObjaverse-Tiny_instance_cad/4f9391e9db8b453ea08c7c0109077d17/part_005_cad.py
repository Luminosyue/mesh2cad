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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4f9391e9db8b453ea08c7c0109077d17/part_005.stl', 'relative_path': '4f9391e9db8b453ea08c7c0109077d17/part_005.stl', 'source_sha256': '74205a1e9826263b892f63f3414d1d5d566b9b26d9e2be3ac55b9cfb2a760ec1', 'input_faces': 790, 'input_vertices': 468, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27875831723213196, 0.07805871963500977, -0.19111678004264832], [-0.05029783397912979, 0.4286614954471588, 0.19933460652828217]]}
GEOMETRY_BASE85 = 'c$}r22Xquw!@nm$L=g}PN|CY@si6r10+K;`Q+h8;2k8Mq6IehxNbhZt-U%cj5MYNSgd`-PTM%_$tXN*a0t%Kd_uglgnPLCu{LlAs&OOhwKZZMZ?%bKZJ9D*to1D1{Y3fgD?ep$8K6Hm`nkad-LR!?|$O*#-4jx}^^w=pOS^=4hKPFeb-KAao9wAzkHm$;-!Q%%;R;cf)&~Qk-3gNB_L&ii-i0nVQ-<ZfjgGJuF|H$!!v-9!8`i~u){kdZ8I`zU`wJL?Xrn~-^fAVBE!BzF+D?ZVdy^oJaWJB+>ZHF&N?wxUckNo@N>+RdG?!Mm_B=^KFJuK+&GhODMoLLFtv$i;VuP;chAMAfnZr`?_tsZS>p0+{rxC%1_jg&U3o<;*yJ$sHG_65mZUq?pEzkjE>%=Nl&8sf8i(P`CwN3I>bFWYYnEh=-PXla>yYR4Uu`L-hVyp#8+{Cq3FZNFywpUP>!YtMtra=+V7CCSg-W*zVa$vu<fj>vv^_2y;kegpmE%&Ff~HeJ;-|E#RXed-l;etc=R++QgqT7Le0nX2c!o+|US#Qni?{l|y0e?0k?sCs;7lC14{DmUA+Wst2N_pyDl-<-MDBw6;eHZc6MZM@~3c-$8xH#RSemHl_Evb`SK^HgrOXMTCr&aiLNWqXeNy~h_M_gsEWj!$jjcb8;6oy%R6^^WN$$D1?PTDF$s&HLi*OSbmsC>`qylKWRSI3f2FnsCWFPTY;dPWXc4+SRHjC8v+J@0a6!DmRb!&0&|U<HWV8{z+eu++U@Ox}I8eweL6XV!Zh5p4r8g>qG9Gl7HW|psgOGga4E-NUq<0bXsoz%lBEbpX(&4aai<6*&b)^-XAKrcmKI1%Q~*yv)@aQ?Wk$bwXk((<bHB4k-2x`<jXSOx8CaulDpG0cgpkCX?~XVym-H;cGedp_nauF?jPscW?9FTC#{Wazcbf*4w3!jSyRTo-*rQG`-0?p{O0|#|58J2_4r-i%l>rcp6DF%cs*C|X3BQXo}v0{Y#Vj|$fI)4fN3)K&(ss;{xUCR+WN;I(=j4ge)aKtGT(hZ(>ks^pQOe4g5<8@U&pKdKA34e@7}MXlVtxa+^6zihN*FQ^3!Cw{kK!>_563T9B<CtJ7bj`Z@NA(({^5>;tgMr+&FvwoUH$^hBDW?rl|4LrSo~YpW61^*xWK%wzI=CnYMBM!CKjV&$(Q-+`V<DY`^|6J;Qdq6WXQ7{=S=J%l#vopZ8gE_q+pFW&7KlUmYwrmQ>#&>%VMd*v3`CB-NhDXKlIb(_5-P?~Ti_jknMx@_y^g{cCos`)x&)oBeDYNIB;VlKbb}NR<0=kIk@Ncm4=N9+xwBFUXYrp#Rle=KlRz^0-_Tcd6^qk-J;nl-Hx)tbxkoGGuPv-=50N`GBj4?YLZ>zL(!?&fNGaM~r0Kdl#+!W|ZkD+waU>Bl@ZKyEA0&j?}Nq&!c`?><f}>lih12pILFycD>Y}rp8IsGF$GNJw~2Kt;cwKJ?8z~nRC2)$heEP<84w+-XEN~F|f6|-!|!MtH(Y1pN+mCxu<)~cKPor7r1CWFZ$xI<^AfZ{9w@ovi`4+rdxA=50{)jxQg3z&&KX@{@_kNly1FF^~+1;eaV@7ifmHj>*&mM>v3rn7oPS7$vyEq&dTjKzMF3Aw;waN`-0?p-kiJT^*XXgy7jvD4@sBf!I|qvK9=LbwI@RDx5#RBTn~mHll6vFO1EC`#&`QJ1j}7DPN?fRv5c*M^c%mac|oC2TRS~(e!bHdEbm)%pWM#}_tUJ`o%UAUR9}!>U(_^BZa*?M%{KnqZ<p<K=GunC>hG(sO|$OTwc0D^tIk}Dy&>nTu9hp)tmE7mJ4E)UwrPUO3%ARV?Rn5z-iNg*_0p{U;9hV$Mt=UKoGsV77MJrSSNU9N)^Xw=eo2lWXRaT+rM?FnX=&DR;ts9u^99NMD|e~y_pBqS*7L4)$erQ~lDjt)x*+${a&xL}T#ddV@3+p}_~)*=-~Q@JwT=gGr8~0!ow*kIfO%{GRBJyNYwOAHUuW*F&`Ey(y1Z>ut>@jC6D2=8bN|ITay+=#R*<<j^0%9Ef7johAphN#FnjycH>vxoBX{?TQ@_t<6iBs>AN_~h>bM-a=e2w4?+@p+?N_fpbD^wn{#|w5L}$p{(|pJTYwjP~>$70Fx5gNI-s9&B)^X@LwoBdTt7qBj*XE8}5Mjy9`klF1znS}Mr^{TQ+cQ&c7dB4b=e_yU?DbUrtDoHO(Nz0>9eJRBa#!3L)&9AI<n`hj-c*g}(wo(OyS0-0b&qYV_M5gr?RQp`9M9gd`Q-e^pSb3NwV#dKM^?%H?zmdjQ=^rvU#k<Q?h|n%E?BP%ukTqkzj`p#)_(o|p_LJq+&o@qZXTDJ8&QL0?s{REn)f#NUEMEV>}x;2pBf(d`FI~&J^sH=c~m>vsP=qc`HIZ@)|S_$ar`xPTzjrxlE*ddo=@(lVO6!?nn`kdJ?4&@FSjd0zZH|Yd%-m|&x|Xo>d)LDbM5}K>i2~=mpU*1IVI~iwr!F1dnbIKVjIt^>Ti($uEd2D+j!1%b)7XgkJtF)x-AckXSR3$n~-9?-n|F6$@_p&<D{(~ePq@mdEH%$x7B0jdZ|$<*6UZh`df6c+%w<>IbZTW&TBg^?cvqUvc0(<pSO>PN}H^CpgsO@TmED`sO|lWez0$!W5aTvB@b**Zmi8x`43;n^Ws^2J5JVf?}W_tpX#XJ@9i5UTXXNMvvPaa<Y(mfh`ZQ6bw4Q9Qf_bL|5sgKFD*Q8z3%+E`^tH*zv^5y&pj8R<~eOr<^5LAKU;18WvH4b&uFH;*CM8>?>+PR)xC{sUhT-;_4X!Ow-0>39N3%e3zB<(jkVPu_#T-zF2xrl_h-$xVBOxl|GWNtWZOP4Z*Tl;s;z!=K2RshUcY&tpE1W)zv1~y_NQy_0((2n-*Hp>+K$UxVt|_eO#L+8x_w}rPnjHR-9GSrG{hAhEO$SwufG4ko22SD=ZB%+ossPr6RGMySybHzF8v^%tN4pIQvGn_8+l#pkCv<X<oY7#ZR5XW>8<kbKQC+>|JrW%W@{c8&#MR8^1ywb?Tww!*tXYvJ68BCd0=}pAGjwu*l}r1cP0lNZ;m`L-pHRCZ;m`L-pHRCZ;m`L-pHRCZ;m`L-pqQO<IRx=#+#Xc@{b&Edi#0yb~?u!`BUSH+&Qj{gPT-67oJn~<ZmJC_g3ku@`OfmzgnJ}>UVbu_58qi)Ks-cyRVM>VXb8AIPu)+vdNkU?*AWmx8;HRKilh5%O+dLp>Zo@i!~37pFhXQ`($8y>hb0oC3DZ5XH<J$T&nt^$kLPQxN@m{>?k$go;qFT?!SMLzf)ZUzE<~Jt&_Ze8vlMObMJ#tb^T_Jm$`o+&wCu-FV5WjesLWcoMgL>N|ak~%>(0~T<@Ur!1eWf1(|#13`nw_U%nr;!QE`z8)a)OvgS|bjg@8Y3Tu{R?Pt&ImGXPsm1QK_+S$3pDr+8SC%Jp9$^++x+*llE&nqR*^jY%2JZDV2$}^57TCaC=KBk>nm1t{cfr_hTeW@!|{Y#6edCTs8^1kXXzR<S4@$j2ja-3Z0VmmHR$0>3iZsvjhA$O1OVrze3`;P7H{d3|>H=iXB9Iqn}^qZNlYpLq__+|ARBl?uOKlvM~dW@gdaoze{e(!rK)l9Tr?}2&#qiXi!>bf*4!jcEt@5lqkYv#AhCaQi~A?E|0%<6Jp?K$eQ_vfnhi)6l|g!(=DPhNFh4F5yTPp%cSZEw!=wb1;k{f^&F`ZswJt=EhB`^%Y|zrQ@K9-gy}ht!?2{r=lmWbXVu=xLfLbNAy(s-5e8SKq&xr_WihqrmUYFQR4c3g4ivuOWY{`On$IGB@vsuBQ3aeR9%vm2*GTCU#Tz=jB^e?)d%d-n&8N{|!^~sNN-1d+X0WXFXo?_q8)Oe_wk)o2>G;<JA2s^i%ns$Qv_S=FZ>s+26zJxZclF^MRiisrO2EJFE6EuQQ+Py7#tF{dw}SI^G8>Wp0F(KW9CU=JOLz(~{?`*ROj`4f*`R-@BOles(;^@PGGMUf=Gw@~G!aGZW<a(Yik}tmj2PA0ofM+^v36d1MuJzVdz~xA)$^V_46-`TR$p`nAkm!^f)Y=yE}I9W~8R``x`v=0?(ws^6-ekhwSaKAC$DAC&L8w3){Y>v;@3*ZOm-VeL<M;f`{9fBhwf^*S}53+bH}7}oP>K3{U?=JO?g*lfdk9?j=+`pd%&YyX?iwfslAtNz(rO+Dwy=qJC|T&JrV*8Vr2H|oEI+xpFXp5_`|)YcyJx!hB^`CP7An5rl4u)J@0*VI?fb!I>GS<j=V=}mcEy9fLxbN#1q_5RNFp=wXgAAQz-HlHhcPcQaa`@wu}=_>i2s%L+MtVf@yj>EHUjH+kJ8QC89_oLN&xywU+wtnV$sWUg9m+BpQsrKLhMqOW<KbGUiz4J|<b)1{eX|?&KRlYT+8n-W;QR8iBNtwIOy{z5~94{%aUw!(2&RWll`Fz;u^M!gZ*QK87x0@fSahP@MtgSz%l$Fn)jjQ`rp8Ey$oP5P6>i*EDzRG(RQ}gF<x69mfw79Jv^SSp^x%u4N<2hsPpTKi<M{Yh>cdeMHet$grLY^1*A-9}2dUEzUW9>KBwd(45e&?>XdIIl3oH_3W{C^fZW4*rgUq-3-M3uu-zAH)H$4aeN`z`sCJU_<zI+<$xWU6%y&32x)op;`MICJxThcWa6nd=FksN-6_Ro!3j%u@NUrPTAWV~<q*BYU5=U8lT%apvax7w_~A>Usa!k*a?xeypz7<h-YC{l<GA{r6mIzaJ&2?~%kKsy$P_Ot5b69(h2GuW2bVf9idcGdJHi<vWsK9S`RFEN5=M&oY|zmbvqNnKL)vmuYc56RhXaXppMDpUU^Jx1aZV&OGp5?<M1uwLiVfFRAe`IKh^?dtO$*U&_a-+`OO1bV{-2&i9qh+<af@DZIy4k0)GL$2+^0%merBuIprb^no>Ox%Z<T>bcF9Wcgm*d_U{Y+d}=$apd|pUDSNz%V?GFe_hSfN=3=%d-~icwZ6dlzSxnQ?~DC!v^r_+|G@j`-nCTy5uxh+#gR#}e%G&e<lmd`wY6~>>b+jfSMk<<@K^E4<1*r-<E{0Z@6(;R`99rvcT2qW{F?9UpUQb(@4weq=H`2UJ++<s9_!yn9S7?KTooIs`|5-@;;rK$u-?Fto9hkyHy@s`?$=zm;A->0mYeGwTyu7uu+_tQ31@Dum+<zjcEWmI0_!mxxw#(0|8F_le$DkB&fHw@q3y_V!gk%Up2QUvV$03-B>vJP<oR)~S8?X%dKIl_kvQvl53GlA<mP%9ckY$3*70xL$ddi8Pg-uvz0JRs&!zo~M#kE%Q`Yl1b8|h9E3Z4&I<5liqntVSH|=psjCH@}dL(CVu17L%PmZyk7jwOnGdI^e`F|Z1V;kqJr*h`zdMf{SAIkM#&h=W(++45aKDpw!ZCr7@Pvz$O^r?%F+uF~1GiPqDH*+uFf6Q8sxt`6Lo9o$(OL>pk#+A7~(3zX-18e>rZMz;>kLS$I^>{|^m(}+k>-vn7In;KJ+*}8!kG_7?I!*%Lcg~#lc!v*A?=xAK=&d_L&d;5BV7=nXkfXM7Vy;(o=H_^7mvF>(z2w-X+L15TmixatrRHhTt=0Owf7QB8&%xblzPF-<%$@5wJvUxCY~8Q9UeuYJ>qWI)GY?tMdtg0=GdI`QHC%a6*2B71*N94Ty{lGYnJqWhyK0d!2W;bw^|a31Tu-a-F!tHDXT7d7m+N)g+g2wxF4l15f>$+7l;^ZU+K~R1rO6@`e@q5nnmoMr|JTywx^L9@zb;K48=`5gvP(0H@RG1RUK0OJQ@pP!7e)9@_%VJH-v&3}+wk|H2Y(+Q4Bhx(yesU8cg35-hIn)QEsF4Z*`)@24K~DI!`r})cpJPsbmQIe8PJ2zz*oZ!_-gzH{20H1--Y+_yLe^#SoC#eitx6u72Xz~3diD8@%h=s3unTy_)L5_Y=#fV>r;dmgeCEU`1hKk7zf`|gntQd;$Pwi;Wqprz6idLFTx|?U_25Z2D{?J@V>A)-WTr--@-fN^(n&3z<PKYyqIMS6{84$DZAu@m0=CMGF}b7hF8Oz!ZvtQ{2kaGe+QoeXW&!t<#08=9KQx{;Mee<;a&V^yhezk7-uyo!aKsYct`wwI2C^%{{YU%Kfrfd#^O$j@V(jPVfKEjXY-G2Uepx-gd+bFR>K8r;-UyILlNEqR>M2sondvnGhP>pcGTsw@OmMt2>+ELJPZDTXW?nulVeDu2tPm(o&o>F1x33v_$>TCusAM?aKEOC@In;fttrCafo1SA9RE8M;ay;7ybC@U*2M?o@4|ZcIQRyvhYN~6dV|lxf1wEfB)e>cpTb}9U+KqBDZ=-{G<+|<2Ohxp;PEg6&!F$(DZ=BRA5VulLKOXY4*I(U6n$NSBD^+5xDH$6I{p?#ct48p(eNF7G(G`#!6)D&;9z_NJ_f#vo9AW>MYt!sBxRQ~*~JG>;y!!_+=TDIx5IV#c6<T!;0y3+a2!4jkAQFBf?`ZW@LBjhitvx%C-_JB8p{}3LlHg`&cbKnJz#&l2i_WX!dv6D;G1|Yye51DuZb6;2!AEJl!Z;;8+a4E1$+~4fp>$Q@NW1Z*dHH+&xNz_x%dva5#PwQv;*$Nci>0i9{eaC1LN^{u8|mu@Z*;2=Qu@pDiqgGDxZbt<eDmh=fumw+ITs<4%G2Fcw_h$-WYER`{7M-Hyn+R=DKoIgfE06@P+tNI0hfX_+ARv;Y;xqa1*`)kA^4lX#6-lgCEBaP=v?ABs>;R$S&t#8cf2|@C(p~U%>al9r!+c7u=5T!k57X_%eJJoQBWBo4^QMP+Z$h_$>Ut6yew5NBDJo1zdx#z^B5Q_*DFD*aLqXZw6cA&G7257G52%0&C(`@Vu}Po)>?fBK$@83jQKqSbK7hC`=JvI=j3M8^E%71H21tf_K6D!4`Nwd^qfe568#DLHKxlF`SDp#`nP;xZqKIAASPH;4$0_PEdqr!c<&PT>qJT79K(oUImuJtKbb`9lRml9X7_h<Go;0ycZq`-ME`;K9VAQB3z13#Am=2_zZkKjK<gF+u(708@>u2z*pfbDZ=-|SbRSo0~7EV{8Y%3`@$(`;HU6Jn2IOjXJHC{7XJ|L#Ra|ihxl4J6JLwJ2Z!VD;XPn|{7o1R>*L}0bFd)(9R9neD1LMPP7!_!eu>}0&%lHD8GI#Ngs;Ts!AN`_J{b<fC*z}GUwkw^5_ZN%;yqz~yeHnCBD^*%gV)Aguo&*bUxqK?FXIKYC%;z<P=t&BE<G1~7UsjB#mmFWczHY=R>Q;b2-p;lz}v!i@V0mqoPtN;OW<;R34R4$!>`~!!k_UU@z+BX#c$fzDZ)F!j(8`0E_@%Ki?4wn;A`;Ra3{VSKM42Y2k~^6f~VtIFcr_jlc9kp<LBWy{5*aMrs0?Hi|_(|5kCa?;fL@&a2LJ@Uk#VxtMPeo7CsMe37g=8;=8{kpN0QK5q=e3$FJf`;R<{yJ_%06C*kej+ju*?5p0Gx!mGmScvZXttb$j-pM!bv=kQSYJRXX_KoK4WU&O=kqOdSt6fXr!<E8LQ+LJj%C5rII*`*Kc0AI&D;Jsi2yca$ScELyCV_-jg3_cAG$EV@*;dp#Lz6vhJ1^3~r@K|^P7tF+C@z0=`H+;rt;aZ4d6<ous!iIQNyb<h<H^O_uUU*Nu4~)bGC*pnZ0dNLB0G|Ta<5TcCa2q}cp9ELolkh0G5|6@XQ-p7Y`|+*#F&Kj%!%xFgxL_iF8jpu(@pybA{16vhi*Ll2!1wSa_z>6wH|GRHD8k!km*(&__$K}uUIB*V74Tf}IXoBsKvNX+h6fbkpTk@D=ePmS;0C@9uEf{jAHaF|2l#9_8J~^62S?-Y;S=CUd;<P1?1{gN4}k6Q0r(J#@ZPXC-W%7U3)k_A@MXLrUJ@3-OX5Xf9=r%%P<t}xC`b{WKf62wHJD3#@<(_M_$;0SFAmG&#qn}595090ff0Beyd`Xlx5UT7D10ow04~87;FsVP{1Sc#{)pef8-yr|c}W9`@ZPW!-Wy*8=i-a-&2SCA89xkn<A?D$co2`nFT-^FGJX|i;aBktn2cxOneaTGiC=@4@N4)LcoDyXpMZz(6ZjFh2S0*ufvfQ?_+mH@UyQebE%7$^51OKwm;68xei>fHFXId0QhXsk4o<?y;jLghycJ#-Hp1)TufnSMt9S`m0WX2)gwNqQ@emlQ1->4o=Y}ufx$$Qx!t=v0JU?C#7S*0y*TRdyQreUIfbf#AlJ?}jA-p1NtUbBU2-meIa~ho@T->*Yz@e}YJ`^7aJKzKH5wI6N0-p#+;S=%ca11^jp981ibMR$wKE4cJ4_D#q@pCX1KZkz-Kf}MkLqinB2@ItOuL!H+74cfI5nc;#0ej*t@V8+f{B67&9DsMj2f-=$Abb>@gO9?8!AbZqd?<{<hvFmQY<wg>FuQbxli_S!a4S9;-vE!{8}Os>G%gsAAH|o$jkw?vd^tWI4#5T6<KywZAy4KsePKJiFWw(^#k+D0{ow|@KRz8E#gEda>2N$go_$Q`-%jWAH`&AH>+JFue2o8v=MGVPHbl87!t=uy@cejTSOhPOmxeC9H2zA6+OKFwGCYqb;|cIIo`4^QNASb=cK9K_9p3`C;#=^Ya5ugakA}zaX#6bn;b-v_cmYqrzlGo7-{SwkfAN3tJRyqDhbR|Ccmen#UH~r!U%_9YZ-w8^uIH=l@;7{h|BdGjQG6yuxhTTJU_LwyFAHDB%i@(_DZCQ?DlCe>ioX=1+9TSR1QYQj{1iNipTZBp{rDl=3pe3jd^22&Z^n0Jm-cN!aumw>|N37{KKUcw{b;uT;iU6l+LwP>|K--~x&n*A+P4W6->caZ*&K3G&|j=H(*6h1OA=!'

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
