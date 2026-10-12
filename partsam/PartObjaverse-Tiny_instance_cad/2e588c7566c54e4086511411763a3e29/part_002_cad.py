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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e588c7566c54e4086511411763a3e29/part_002.stl', 'relative_path': '2e588c7566c54e4086511411763a3e29/part_002.stl', 'source_sha256': 'a6f10b2268230dfdcb5feb24fe26772ea235459c6d4feebb59e0ddf129483301', 'input_faces': 914, 'input_vertices': 508, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.08079659938812256, -0.4376412034034729, -0.055697716772556305], [0.12891776859760284, 0.23912185430526733, 0.19903729856014252]]}
GEOMETRY_BASE85 = 'c$}r22Xqz1`}a41C@4)43kVmG-m7#j9RVSLG$~#PEz}U26k+K|@4Z}l7eso?Qj-8lP!LF@T%<`C5k)M#*?B&5+0E;F&U^lU&YAQ5-0yFgot=5+nb}?Zg*Hr`CaWQTavQZ{vlsG|Gz`1EVPrK1b%`7h9@eFQ@jeklLX6DHxBqCJ-MGakp>0BpLB_BGoxAi8i!4ydQ=m%M3I&RK3UuuoIUurQpU?Y7cJ5;PbvyRz-zC}a-@Ri*m*n3C%ayE9)KjKVQO}p2|KXqXb|12B-BCSRyrHQsMJ21RR%A?dhwnEACpvxWd_egg^VW~H?>)4_<y&WFB|3foZ!g3z*<Jab#d(!)9>}uO)<EJ3)s8vqjN2cyJ<;h~8!IW_2z{#R`_4Ca`R2_ri7tPsSNWa-tE8VF|KswlLgy2mzVUT4<@>j{k$#58Myqzidy3y}m}<xRJzuQT_uTm>(dm0C^-;ceaiXg4$uJ_u>HBvsPjvcbx+y!I<8PFI#pUbq5BeEr$oTAPBICBTeyr2CMifeN`hlT->1U^XG7e$uVw}GJ;h{vQ?@wAI{khms{9B#WI2eC#Qoe7GN5<a_i*@?mFIy)$eRIn}=}*T;;x`}Q@;#5fa`|50QE7ku0p$lW43+weqIbID?Our(ryq<r?I$G2eSI}w)%O>OclpNVYl%+Z)9Z>{w^<K~w+5Tl{rb}WA>&-Ay3B9tUrs1L{JC7WXg?YMevf0EzVYE}NlxE0Jk>5&`|s?w)Zf1(zK(x?LYo+uPyB1&8=6!3Mz?yZzVSF?tkXB+OC>pdvqfIHZt*8FU&YTyJAKcq;}e~}=UxeEKdgiD1Jmm(->Okb{7di4{mzy+*S^0^ha{IDQhAqi-5K{r#W;Pv?zHb6SxegKT2|IYgMMn9t+yJA-{8L7*O4-@PT#mU#pQdSh3<03kNIr{S&yf>$#t8amGyY>MYPlRyjYXy^o?h|ce&Pk)3q^9Ke*oUtuZ5%@4Yre#;s<AjPoq<{mYxnIPXYQ_hnw2ApOZ!RN^7~&&So@kDI*9x!%2}Z>l))WLvb$x!wa~kH<KDz23ENo>(b<#PU<B-$S3Sj&k_kvl&h+zh{+I>ORtMl=iQFE%Q~Zpxl@CBTgndeg7*vq<!+a_kQKW>i5b0GXCTT@2JZ$PG9E-?FS|wmU+CAU)s6ZQjLSPDq6;2U;`Pq$vzpkF>zAA##L#*(}HNHZ~nG0(dk=l6QrLXR#D?%KHs}G%HeyTj8Nm?t+aK88lPupq(1q|oO)lz6JO^m?fdecmHOl#PwYWi*W1oZ{nLG9+!Fp#{SSm*bj7C;EBV3dB);Bv%;`(jczUxXNk6~Yp!#q1>Z0b$7;{_Z<={Ap&x)T&eBxV!pCmec&!z{`PR4waPcB=>RQ>r6#lKNY;v`@8HBk=VsP>MGPlb3jK32m&q(1wCnd<c;>U!a6cB^q>|Mk|%D)CS+o$`GXYstE3cSYj--0QoY^KPCfr21o($*6ptZ#|)7Rr|g{@9%c57vs*{qw4o5@paxXCcdV8vut*0r>^XG#)_zDr*EW>N_6_(Y&n$gt=d}hWWL@pF8`S)$?01abBW*M&Pnxqa`*L74&TTSD)V)3!77(ObC-;B$A4EieeaOFYMjmUVSd%G@df36>)u!Gn|Bh{I(?(>SXsaI`>OhZjfG^Kdv=lg8a`6Rn>SA}86WbAr*{uEFGkK%Qvd2Ssh^Zb@?rbxuJJcVw2<{!v6l4H{7vrn{W@!+9KN|fxAedG4AmchnL5(`sr<69{XI_d2EMmPvm~c)K5iiW<XmLTdn|eHd{b$Mebd@@Qr5+Rc5>a4pUb)que?(AH@1WH|BGK`zIM!&_VKL)<6XXYNSKUg))|sd^52Md`hhBU5?y|t?z^4q*Pm&z+*i$TX=ig)iSywxDxS>}y``TcLL?rRey`#|``#SKrT+zvsd4l6ija2Le~lL9RQwwm`^$BUitk(UyP6ks(=fR&eg3IZUyYCd-f+3@yftdRj48w?zK%B|<A!C*j~y%RM6Q?lJ$-Af(>MByZ+>@YgUc^CN!ocF<!Z;c(;&{}mm24at3c06YJ9vG$IHC4KYDv@l>03?N$Nj5Ci$&=y=bRzblQ>V^aI8;x!<sHGH&gc%Q-E2y0p*v)>x1radlyq`0Ov<a|I=DRG;n2SLWMWl^^K4SlYj{O^t*1&j`tr5%_b8O8l=)y<GX;mD2uEpX8t0sU<(-d#1jd<n#mc#5Xg)DfwZlsp8p~FTSxLLj1mIRo?KX-yrR9e)IR<DC>IfR_XtI*+=|yyQnw`JUt}yp7xORe{Cjp9?-s3{hYKvs<-riOstH*e*QY0U$r0jEkWAhoa6cYT{U0k;Iq>IKa0vbx|k!z>3dr>N^<!d66L=B=;eyfps(}cTQ`=d`)GYx?)TqTa$jo_WdB+%zIkGyoQqb5M>~Drq^pTe-}hcX+TYn%uKVzN70*FGZ$32+-o4FMIDIQHUHX&ix$2Lp{T<Sdwe_F1PTyOyPMov8u}yqWx)Bn$-(*tp={azpJeDBy@>i^y_n`k|wB(1YPu0A5t~`)-I9K?x&yw}h>Q{-k9GfK0t3}CqW0CmYO;6SMTRV!zIDOxwF)rVDB)<7@u#8XpB@*ZOmiB9u-Q@I*DIdxBBvfAN^2aTeJb>>DdG3nOz@Q3h9s~XVaphIBKxygE_7`%$oX-QFPEv8``@`6yRPT5DvdKDK`HJ}D$w2sO<r{xyR=)9ItjyQfja2-5@U2nTCH{}BS}Of|OMISFJiF7X>zcQ6OFNf-l6GpYmUAP%Ij*AQ`D_hTKDYkPD}Gg3FTT)0YCU=e7Lax>cbDgpYZIcKexQHmB&YAqR#MvGd~3b&mz=NKl$Lg`Rdwfi{NTAFtmk6Y&mTULc1*9t+mM4B{>!&Md~2Q4xAxDK{NFz7DyMHunJe*Gw8%17{i<_iUuZVUbzS3Zby*kq{+adUx*h6E|Bt8N<nmvgE%h5msrpum`c|_OYn;Ayw}xD|iPR5#*I4RbUd1`QpgdQOZYty4Xr(;QcE9ZMjWib$oxU->xzyLsK{b0yJUnV4<Ggw>`^5zn&z^a$Bn~-Wc?u1YJh`B)^fUCC-0!{RDo#9$eA3RbPsLA|u-fH!|5e6$c%CIr-(3GwoYVLIU+vW2tooIulib(&(z2h%FPHN$eqd<bB&Q$f(1m#3AaSze4;AOyw>mcFxiXf0zn|1+|MmTwTK3bsk*@gnw<|CEe$nB|*ZDBeb)lT+%~4YSd1r~YrtRhYjBmuQlX1wiM)K-_2{O({p2>ciX{+Rad~bi#<y+&XNjseX{XMV9zE)+XT=zy6*E-UEa2<_!eUYrMIdWa{mACH>)xQ7fJZUG#+phg3rLXskps)9rYWWs9{op==Z}puo{cjm1?JRocclzeyj50py2CMxdU@eq(ipjY;kY|F*KSrq)GLJkb`eGYPJjbmS--wWX-1qE+(+`wQm*n&V-PcL|?m1oih4zE_-``jD-w01pU+*LMdLIeaZ@*sdD_5A@*QRPJKYQ?v24BcHY-*tPP49v|a=)LPk@c9dhU%w(eU#MK=f<5rS&u6ZOMglhbL|V-H%f``4IjJN=?C|VA8svj`ewxAIHzx1KPBz_{e#@^f^2HO%<&20&si$x&$(CRJX7ziwC|rP*FD};tvl@-w?33{Xnt4r*(E<IU+?=?&ByA#y!)=pIFQeE-qya(+d4mM-x^yz-szj4-;#OP&p{`S%Kn@0uGG(1LC&{7W{7tBf&4X+oPMDB16LdxpOuy8{c=xS`Pu3@P2~Y^hLFALf3Le*#$j2c8aE%lH^&3HuNli!{_$^4E&jFZvCj2tX<t9@v|h46-B*`%;-9%K^?9yI>Fehp?OO$S-nq2T)lTqv2j80Xy426#%9THZzRsW1%gOn6hWLSpr(}G_&R6Ty_v~%)SN<jAxhs3L%ir>)%MUbsNBqMB<vqr^mM5IP)jxHT)3=(vFMgUQG7db~XkS0q7^AW-RO>or{an6HPT%OTUh<VG^^I1!m9Nj?zJVXB`1GgFC%(>~%RQ2xqf5wj$L*K-9p74>N4_nseEr<yU$|NFRoZegUmMc6o@=xpe6Cr&VxiMFw;L+X%~j%C-9M84|Jv7;R|EK7omcPvrRFQJq>hX;=K=ran<}3D^FEPwI6qj^ugZFC+e+GLlHGOA*M9Jvf3D>sr|<osnXJbj@EeE8b(>a^`OVy2-t*uaFRCOteb2TqS6rD5O3V4AL>C#KhhNG4&X>HTeVwn&gi|Wdco&MV^QzYxqt>Y>N2IjB=Y{xX*UJ07)q}<79BaHI?=h?*BjtYAm6P^4KL>rz&&H&}l7H$?k^YR{=~~x*{NTFoU2wj-?~qw?U+MPA_YdBiY2QeXzr)z*@_C<TZfN9gXGLh7)A!$*?aE6!|5yog#J~EF#PhKJvcB+*e#2b8|C^Q4|2olfU)kk-n)ZY5)4tfPu4`$(#kZ1Yw4ZOSYaLlF2TS|YH%k3l&18P>$~n`*51v1JWRi1KpDi+9?C;jm1bMD3wN2XT_pi)v#C<ux-8&$D?n{y<d9S5?{a(xH)_#H0w|>hM@AL!XkI8laswU6x8Mn*(3VeUXN=Z)Nc>T01j~RJ~%6`!(-W7*Fv!py%cD&$P*G78IMcU^a6<pU1uSowF{4Vptdl>EO_b_ITQVU)Fkk0W=-z@c~^oM=Wo8zd&zxiC|tL6(C=VN=1JAKcSAuiw3FU>yHF6RNg?|Z(+=R9fhzQT*I-(win<=p72kyiPh+7)Hoq8_X9@vX?P&lx}dNeAS;V*Z@c4*A5pE>h0(As_B@&Wk5a2^r`6#iTzoC%V>Y&}Y5t=VI;a=V+7luKnP;zHQA_{pwyu{4-PKJ0IV1v~PaUQr5+H_f&mL*XR3=_C2SoDL-(M@vr<;@*%#}V~ESQZr2pQ_fokpzK>{Me;+YUcAMw&&mNS#5sTlXnQNS_zQ4=+;XTczKKa3#-&>8dKUZtHFU}9a=Pd2>TxN29@KkIo_uDb2#9=SVhhFWIKlS&Bps&A2P~VrM-9Bd=dfzQB>pgXZJ5Kf$llXZ)MEd{pS^hnQyocAmem`$a%dx=eTZae6JAL!wDCrO9d1JGj^Sx=8?sKk3s}Ju#@%8&sz3zO^4@-UaStB6t&9ravo=xwk=9=5mjy@;r_ZaxW_a2;w15@v~<8#-rIjVlMhvMh#D*b%2X06k=9uJZFpKNj0&(${0>3cW-CH0RCmU!d4tq)&+w>3Lgp6m3js?pL8zQ5fY`&B)jqm8`syzK3fS^Q$NWxn{HsD1sN(LC|?Jg0BeC=&1Vt*(XlJL4+&Jqurd|I%?7(0-b6uK2Wu*Hga5KBB*a1bx1nnCuruwXSkq&U?Z4)!OI%wm#Q+UyPOO@*HO#miK!>pZ9_KdChlvrL@EQli>T7g9rCJ=iLk+G+T}HTZd&lQw@^uq{lbA{fwWhd9m<~cTS1Fr;Wr(-wUgqz7?8Q;v`ptIZoee#Y;ZH_vA?0?}`(?<7?mOC*S>boM_)1RW9D?Tg4wpJLI?EcV7J9cVV61@QsW!<DI_0YpMgPKIfU>cR+lT?}qw3<8Se<^7V6s{%)du{hdWWNBC<O7oYdfChrF<{NVcp-ZT4$*OL0YC)Do`jTfsAxYqBHle5&k-(D+zSbv$vhiPUzeQQg{IH&K)zggPv9U}3-{09A1XI=B|t+7MeCqH<1=U(OX&7T&?IO{y1>ld#g^VNvFQTvei?1KjXZo!YQ|DA*0?}C2Z0%_+A`{0mR@i`}3_2fHp(AVFc^||-%Ij+m|vi`1zufGrK=U;ETfZUgU55{*8?FYZV==WO9?-3`GhlB4Q2F^dIe9jg6c|rR+|9JUs9`tz+U}li-o56PU`#ruZ1?%%2O26L=*4N)p^?L(dpYQ%Uk7?gp(J9UuSAP89`+45OYd`qBqt7|IeRH1p>@V84R=tq#3p)Sk`h6o$|JQYOoLgI_xqPef4{`t5PGmKSlb!DCnv)mDJNxPTtk$9bny*09#)tlE-nE}{-hD^g9Qv=gGV%5IXdPEZxh~R9dUxDvKV{sS;StiG6!GuJPq|)<-a`-l*Ln>4Db}NB;%M<x<^g<fiacPQm>_<NJQKjzdB)UvX6sjnob#yX*DQ5UuA3sinc+s1Y9~cL4EibZr`bB2_$l(R_EY9zvtCj0Q{;2s$QsH|xnG#tPqAMZvp!Y6-lvQ%>{Ix9p9=c(!=#@n_D3&%%Kg#5sJGN-U)J-YeJ}g6af11J91-OlXT85$*Cvaf;yhq|y+PV9={{Ek@Kc^EjEER%C*}F1)NN@e#W}~HH<kK#3MtP~miAMeql`S6l&{ZkMzoyMw6D)^+P4a3QGUwvVZeM(+R^_$knz{PK4%8c55+uEKgBsVfS>Z*>zR?qa>X<G%{w-))aSe%%qMNii=X1$Zk($x{ZDcJ548DAeEsi&c)rlSaYUXwv~TVUm;Ue^6wK$^=XpxMU-DcZDDCjvXA;j|?ep9hJTI;MQrb!J9IAaQ#dE9QXS&D7&bOhi|GMB)@0#VUizM$z$t9hU)#%#M@t+phru|3jfB&Zi;bs57{?merrON(q|I>ow_K+l(N9gact?z^gKZ4VTh?a%Z!==#Ha4EPQ`UTt$9)?bbhrzSZ)$lBM9r_Kt4&IJN!`tEG=nwF5_$>Mpd=|cj-i2-b1-=GfM<2u2;T!0$@D2DT`UJiS-$I|lx8R@AKj5F?d+49=J@_H|7yJ-@gg%EK!4J@9@B{ch`a66dzJvY-+j<+m1OJF7!au^N(OCF2Y@vr?3to$EfY-uv(E0EjcoaGo9tC$t`@-Gf+UO^6Z8#U2AI=3oGeiy8*6$5ryV!gJ{Te<2uR_PbtKgAn7kDJx4Q&8-gIl82;g)byv>MzLZh?Lbw}88%o#3wU2y_%Y0$z@8hHX6#FNdQjHeW{{!M56Y;X1!<el0|_6#N=o25kqIfjgqZ;EwP}bQU}ko{O%7=fWG&?eIqUTl6^mEqoL`3m=8QN3X%QUWdPj&!IQqbMSfeCVU>gfZl>Hz!%Y<;frt*dJj&5FQE_NOYjx+5qt#>pby{xd=<S9UxhEDcVJt8gfGMK=xI0}jzTRs3SNb-g;&8d(K+x;_)ByY{3RTQc89~@DrjxE3j8jb3w{@VXo%Wt`yp%m1pE*_hOUB-!Hdz6@M3s0+6^8J_eNX7z2VMiQ@Ar6hPHsi;9h7~xEE}qBVZF=gf54dvxXN@Y(7X)=P~p;Y^%L)1N^r6^$^iA@au3Tv?E*z4o64A;qYj5E<74ufNq2rz?;!;;mz<4^eDUoK7xJ^+j<T@0v|)q!^hwg=mq!$9D`njW8jl$5_}Rqg<gVB!ExvnI1Wxg18@TT9eNf14nBikhHZ_9&%k@oD0mON0$l~KfTy7|;c4(t^h<as+#U^s+r#D2DsXu?1NttU0lsC3+H3C?Yw#F+3qFJ{h7Z9j(9!S;cq-Z(o(c~|JHtcaNHh$NgomKL;34o7)P$$NE73*pBG%YSip>_q<{M}Lw$)x&H~4My+aaQr;J4wLXgFLG?v0Lyd&A?<1@Jg{5xN;(1b>b0fWL<KqDNp`kHLH4o#+X8C%g-dfp@{X(Ub6QcprKS-UshT<KX@90W<+V03SrZgAc-o&@-^Dd*DOxa&!f}9G-$sgQviQ(V_5QxGmZqZVQ)2%fqGNbZ7=R9em9Ywb#Zq*2p3F8hjL80Uw38pi|*3@LY5#JQtpcM#3}U8R!sr20RCy0?&arp)28)tbt7wo1-Z<KR|E5w%T$3fZsNM5F%O={s3->_J$k6{m^l6KX?MV2%Z2hMZboZ!rRcj@LuA38^z|W=q`9GyanA2Z-F<V``}IRdUQX$9$teUfY-n)(Sz_x*pD894-v<Hip^8eDezQy2s#)Z0(U^$!X4mpXlb|{{05p1egnQ~h}yAxlNde<--Kh(EpQCH6P*k1gx8`o;kB?IodNsdHRv384ZH*01aBfncTj9TL$UcO`T(}oj?1U~w)sP1wITc=+zjmpH-r156X5>vSLjmsD|i{Y4c<olEu+}H1l<BJffu8j;KlGlbUnNfo`<f1=fShlmGEqM2I`0X#Mumr&BM_l@Nl>j+5zqaS4PXhmEmmY8*n!G7emyJtzU?-82A_XJ9H=f9ee~`3m<{^pniA{yc=Bu?}iVfJK!C}&|!+rKT>S|7kvubYRApL{I<CSvD6GM0k=W>!)@S!=vVMScrv;SUPgROrr10QT?|ixC!!1CiST%I9y}f%gU*J>z$Q8ao<SU#6q|dXo!}mDEwnOR3(kpVgLA@v7^3#v|3M6V2mb+ILXW_g;0x#;_yU}O?uHZK^XOstFmrsKV)L&Qn=^)p{tMe`&ud1C&DGF0a5cCqIuPy(k3c8GlbOE}6q^U36X8Md0CYS&0FFe*z>#nt)PzmusSm~GMrbX#5u6Xr3Fm`f7^3#vykL$l!7t#)=mq#O{4<&W{|w(o&%@`LgWD9F|DxFJ2@$pDz{6ZrgFW!aXjk}SI0793k6?TwC^mOP2f*Fn&(KKtGq^e02kyf-HmBHJ63qvfgfpS`*kwW=!*;RxZ@i!3zu`a8+wg71=ue8xX+xygTo|>-s4!#oF<cmKiblW@+<#Mw%?;4c;0ADYv^m_I`>al}IX9XKw$;9$-2ArrRrF8zPwwMYip|+6Hh+W`h6~fzkI)A2M{p6eI$WJ=7eQZzU*#G__`5~;eLuNBsgpHpaw&!uL{q~B;Wv}ZPlo6fG&OvMc78zZc7LGQyg#`tLr<ai;ZyJv)V}r;e%qYc(Z9?ToAV@>LTC-N7+eFcix!0I!WGds;fnD4j{AI{-!@-PE(_2N=uhwlcpG{J-Ue?(e}Ff_3(@`XLU_7kyrxrZ9+X@@M<<}m;0f@0^c1`vjzyoqvG5(#9@9Jgw)r`l2eymNX&mF8hGO$8$>kqIv?#v|!A0TvXbreN{3%)&{uB;HE5f00RrGzhDx3wi=OzokZ9eCizjG9urzMwWs1IEL``|w42DlI0AKeD`hX<n@;lc0#bRj$d?u$-``@$X3L2yU7xg!pmQ*5r0T*{&K(a+)fa1V3>+ykD7u7@YWtI=3^HM|$S1Mh|7(C2U*oQT@7lE`nHlh9Y-B;x0y@iLw+Qf!V-E(g%x(0}0H;Jo}jJLd9IY_5mahwH(u&`;r3un!G|eQ*o3D%=9DfM$U!z^PC>=2G$7=6%HBG<Y98&=HpdDK>kPOFpzX+6*oZmq&eYdAJJN2d)CwLi@wD;D+d6xFOsG9RN3h8=-ySMsRJkBU~G<iZ+L<!XKeE;E&)E#>@CFL9sc1a`^x)jFy87!xhl_a0R$A+5>J3cSk3}-QnTrYIrz28{G@fhL@mm@Dg|{nh0-&zeSVaZ{h9eMR+^B4vmM`!Sjum>tsH~=2^+*OY|G`0Q?Pn75xpq3cnX3YOkgDC^mc1daxI6iME1U!aY$R+!OAMwtzdsP0$K(6Sx4H3N8TOGeqsRbdO^5Qgk4^6z+g};SO+F<K=oQOR+gea(NZah~|Sc!dcPca8@`cS{}{`=RvE$dEf$QEw}(&6m19>g-fAL;8JiIv=LkeE{)cPOT)#`s&Fy5Ao>wp5YCI1fb+t+(EM;N_-*6mx_z5sbEf3-8kz<D0L}t?(890>E`nBoi@+7p#&AWrF4`Tg3%5as!)@T6=xn$r`~|uM{sJD0ZiUCflhJSC$?zm}J3I*<hpvOi!Nbt`@G!U^It%UxhZ`@~e>mD24u>mKY>q&`gd^a2=r`~@_%wPIJ`IP2h}!uggkp1X)C(7f8>21Z#&8$3C)@?@g?5H}!Jnf|;LqVYXaTqm{1$5Gi?{e~^GQQ=DSQ$hk9L5^!}ZXza6PyXngcEbXEt8ul*|;H4K$<i@{i4_(5!GO_!TrK{0f{7%>$={-#`n%Z@_P&Md3H$chFMsJMepG8TdUoJ6amf4!@5UgWreWMGM03!f&B@;kV!nXf8MdoF07}P7kL=Gr?)$)W*xalbT|42*u_!XcjmP{5tA^Ux%}yMc{03ZnPqt8!m~~g-gPf&^B--xDMJAt^<FHegS_9e};~QKZDz$li_x7dvp@q9&U?{gWJNb&|z>ZI27#%hr%_{aM;$$a839_ip`&(5%4GQSLi(WD|i=r8r}upMeQ7Pm)|z$ATJe%LmP&q%9{HB^?&*O@{j%g(Qy4AfT#SM?tjkf{F@z;+Y0{U-q41x*zuUWm{X~Nd2ElY@qYm4()Kz'

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
